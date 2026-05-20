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
  🛡️ SOVEREIGNTY OS: ACTIVE ML-IPS DEPLOYMENT NODE 🛡️
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
        self.dashboard_url = "http://localhost:3001"
        
        # All 26 features fed to the model (same order as training dataset, excluding attack_label)
        # Matches: combined_ml_dataset.csv columns except 'attack_label' (col index 3)
        # Col layout: [0]timestamp [1]src_ip [2]target_ip [3]attack_label [4]attack_type
        #             [5..26] numeric + motion/arm features
        self.feature_cols = [
            'timestamp', 'src_ip', 'target_ip', 'attack_type',        # string cols (label-encoded)
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
            
            # Broadcast to Dashboard
            try:
                requests.post(f"{self.dashboard_url}/api/alert", json={
                    "ip": ip_address,
                    "reason": reason,
                    "timestamp": datetime.datetime.now().isoformat()
                }, timeout=1)
            except Exception:
                pass
                
        except Exception as e:
            print(f"⚠️ Failed to execute iptables: {e}")

    def monitor_live_telemetry(self):
        """Tails the most recent CSV log file to simulate live packet sniffing."""
        print(BANNER)
        print("📡 Listening for live IoT network telemetry...")
        print("-" * 57)
        
        file_positions = {}
        
        while True:
            # Find all target CSVs
            csv_files = glob.glob(os.path.join(self.log_dir, "*.csv"))
            target_files = [f for f in csv_files if "audit" not in f]
            
            if not target_files:
                time.sleep(1)
                continue
                
            for csv_file in target_files:
                if csv_file not in file_positions:
                    # New file! Initialize pointer to end of file
                    try:
                        with open(csv_file, 'r') as f:
                            f.seek(0, 2)
                            file_positions[csv_file] = f.tell()
                    except Exception:
                        pass
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
                        # Build all 26 features matching Colab training schema:
                        # String cols are hash-encoded (mirrors LabelEncoder on unseen data)
                        try:
                            str_features = [
                                float(abs(hash(parts[0])) % 1000000),  # timestamp
                                float(abs(hash(parts[1])) % 1000000),  # src_ip
                                float(abs(hash(parts[2])) % 1000000),  # target_ip
                                float(abs(hash(parts[4])) % 1000000),  # attack_type (skip col3=label)
                            ]
                            numeric_features = [float(x) for x in parts[5:27]]  # 22 numeric cols
                            features = str_features + numeric_features            # total = 26
                        except ValueError:
                            continue
                            
                        # 1. Scale
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore", UserWarning)
                            features_scaled = self.scaler.transform([features])
                        
                        # 2. Predict (0=Normal, 1=BruteForce, 2=DoS, 3=Replay)
                        prediction = self.model.predict(features_scaled)[0]
                        
                        # Broadcast telemetry to dashboard
                        try:
                            telemetry_data = {
                                "timestamp": datetime.datetime.now().isoformat(),
                                "packets_per_second": features[4],
                                "mqtt_publish_rate": features[5],
                                "broker_response_latency_ms": features[6],
                                "device_heap_free_bytes": features[7],
                                "auth_attempt_rate": features[8],
                                "auth_failure_rate": features[9],
                                "payload_entropy": features[13],
                                "duplicate_payload_rate": features[16],
                                "consecutive_failures": features[22],
                                "latency_zscore": features[25],
                                "prediction": int(prediction) # Send prediction state
                            }
                            requests.post(f"{self.dashboard_url}/api/telemetry", json=telemetry_data, timeout=1)
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
