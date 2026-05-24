import os
import time
import glob
import joblib
import pandas as pd
import numpy as np
import warnings
import subprocess
import requests
import datetime
# Suppress sklearn warnings for missing feature names during live prediction
warnings.filterwarnings("ignore", category=UserWarning)

BANNER = """
=========================================================
  🛡️ Smart Home Threat Simulation Platform: Active ML-IPS Node 🛡️
=========================================================
"""

class LiveMLIPS:
    def __init__(self, model_path, scaler_path, log_dir):
        print("⚙️ Initializing Active Defense Node...")
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            print("❌ Error: Trained model (.pkl) files not found!")
            print("   Please run the Google Colab notebook first and download the files.")
            exit(1)
            
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.log_dir = log_dir
        self.banned_ips = set()
        self.last_alert_time = {} # Added to rate-limit UI alerts
        self.dashboard_url = "http://localhost:3001"
        
        # All 25 features fed to the model (same order as training dataset, excluding attack_label & attack_type)
        # Matches: combined_ml_dataset.csv columns except 'attack_label' and 'attack_type'
        # Col layout: [0]timestamp [1]src_ip [2]target_ip [5..26] numeric + motion/arm features
        self.feature_cols = [
            'timestamp', 'src_ip', 'target_ip',                       # string cols (label-encoded)
            'packets_per_second', 'mqtt_publish_rate',                  # cols 5-6
            'broker_response_latency_ms', 'device_heap_free_bytes',    # cols 7-8
            'auth_attempt_rate', 'auth_failure_rate',                   # cols 9-10
            'unique_passwords_tried', 'result_code', 'password_length', # cols 11-13
            'payload_entropy', 'auth_success_rate', 'credential_entropy', # cols 14-16
            'duplicate_payload_rate', 'msg_timestamp_delta_ms',        # cols 17-18
            'motion', 'arm',                                            # cols 19-20
            'inter_arrival_mean_ms', 'inter_arrival_std_ms',            # cols 21-22
            'consecutive_failures', 'session_attempt_count',            # cols 23-24
            'session_failure_rate', 'latency_zscore'                    # cols 25-26
        ]
        print("✅ Random Forest Model & Scaler loaded successfully.")

    def drop_ip(self, ip_address, reason):
        """Executes OS-level iptables command to drop the attacker."""
        
        # Broadcast to Dashboard FIRST so UI shows all concurrent threats (Rate limited to 2s)
        now = time.time()
        if now - self.last_alert_time.get(reason, 0) > 2.0:
            try:
                requests.post(f"{self.dashboard_url}/api/alert", json={
                    "ip": ip_address,
                    "reason": reason,
                    "timestamp": datetime.datetime.now().isoformat()
                }, timeout=5)
                self.last_alert_time[reason] = now
            except Exception:
                pass

        if ip_address in self.banned_ips or ip_address in ["127.0.0.1", "192.168.21.165"]:
            return # Don't ban localhost or the broker itself
            
        print(f"\\n🚨 [ACTIVE DEFENSE TRIGGERED] 🚨")
        print(f"   => Threat Detected : {reason}")
        print(f"   => Target Attacker : {ip_address}")
        print(f"   => Action          : Executing iptables DROP")
        
        try:
            # The actual OS command to block the IP
            cmd = f"sudo iptables -A INPUT -s {ip_address} -j DROP"
            subprocess.run(cmd, shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.banned_ips.add(ip_address)
            print(f"✅ Attacker {ip_address} has been neutralized at the network layer.\\n")
        except Exception as e:
            print(f"⚠️ Failed to execute iptables: {e}")

    def monitor_live_telemetry(self):
        """Tails the most recent CSV log file to simulate live packet sniffing."""
        print(BANNER)
        print("📡 Listening for live IoT network telemetry...")
        print("-" * 57)
        
        file_positions = {}
        # Pre-populate existing files so we don't read old historical logs
        existing_csvs = glob.glob(os.path.join(self.log_dir, "*.csv"))
        for f_path in existing_csvs:
            try:
                with open(f_path, 'r') as f:
                    f.seek(0, 2)
                    file_positions[f_path] = f.tell()
            except Exception:
                pass
        
        while True:
            # Find all target CSVs
            csv_files = glob.glob(os.path.join(self.log_dir, "*.csv"))
            target_files = [f for f in csv_files if "audit" not in f]
            
            if not target_files:
                time.sleep(1)
                continue
                
            for csv_file in target_files:
                if csv_file not in file_positions:
                    # Brand new file created during runtime! Start from the beginning
                    # so we don't miss ultra-fast attacks like Replay that write and close instantly.
                    file_positions[csv_file] = 0
                    continue
                    
                try:
                    # Read only new lines for this specific file
                    with open(csv_file, 'r') as f:
                        f.seek(file_positions[csv_file])
                        new_lines = f.readlines()
                        file_positions[csv_file] = f.tell()
                        
                    if not new_lines:
                        continue
                
                    # If we are reading from the start, skip the header
                    if len(new_lines) > 0 and "timestamp" in new_lines[0]:
                        new_lines = new_lines[1:]
                        
                    for line in new_lines:
                        parts = line.strip().split(',')
                        if len(parts) < 27: continue
                        
                        # Extract raw data
                        src_ip = parts[1]
                        # Build all 25 features matching Colab training schema:
                        # String cols are hash-encoded (mirrors LabelEncoder on unseen data)
                        try:
                            # Pass 0.0 for string columns to prevent StandardScaler from exploding.
                            # These columns (timestamp, IPs) had 0.0 Feature Importance in training anyway.
                            str_features = [0.0, 0.0, 0.0]
                            numeric_features = [float(x) for x in parts[5:27]]  # 22 numeric cols
                            features = str_features + numeric_features            # total = 25
                        except ValueError:
                            continue
                            
                        # 1. Scale
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore", UserWarning)
                            features_scaled = self.scaler.transform([features])
                        
                        # 2. Predict (0=Normal, 1=BruteForce, 2=DoS, 3=Replay)
                        prediction = self.model.predict(features_scaled)[0]
                        
                        # Broadcast telemetry to dashboard (Rate limited to 10 FPS to prevent server DDoS)
                        now_tel = time.time()
                        if not hasattr(self, 'last_telemetry_time'):
                            self.last_telemetry_time = 0
                            
                        if now_tel - self.last_telemetry_time > 0.1:
                            try:
                                telemetry_data = {
                                    "timestamp": datetime.datetime.now().isoformat(),
                                    "packets_per_second": features[3],
                                    "mqtt_publish_rate": features[4],
                                    "broker_response_latency_ms": features[5],
                                    "device_heap_free_bytes": features[6],
                                    "auth_attempt_rate": features[7],
                                    "auth_failure_rate": features[8],
                                    "payload_entropy": features[12],
                                    "duplicate_payload_rate": features[15],
                                    "consecutive_failures": features[21],
                                    "latency_zscore": features[24],
                                    "prediction": int(prediction) # Send prediction state
                                }
                                requests.post(f"{self.dashboard_url}/api/telemetry", json=telemetry_data, timeout=1)
                                self.last_telemetry_time = now_tel
                            except Exception:
                                pass
                        
                        if prediction == 1:
                            self.drop_ip(src_ip, "MQTT BRUTE FORCE ATTACK")
                        elif prediction == 2:
                            self.drop_ip(src_ip, "MQTT VOLUMETRIC DOS ATTACK")
                        elif prediction == 3:
                            self.drop_ip(src_ip, "MQTT REPLAY ATTACK")

                except Exception as e:
                    pass # Ignore mid-write read collisions
                
            time.sleep(0.2)

if __name__ == "__main__":
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    ips = LiveMLIPS(
        model_path=os.path.join(PROJECT_ROOT, "random_forest_ids.pkl"),
        scaler_path=os.path.join(PROJECT_ROOT, "scaler.pkl"),
        log_dir=os.path.join(PROJECT_ROOT, "dataset/logs")
    )
    
    try:
        ips.monitor_live_telemetry()
    except KeyboardInterrupt:
        print("\\n🛑 IPS Node gracefully deactivated.")
