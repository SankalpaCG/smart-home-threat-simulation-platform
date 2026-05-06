import os
import time
import glob
import joblib
import pandas as pd
import numpy as np
import warnings
import subprocess

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
        
        # Feature columns expected by the model (excluding identifiers)
        self.feature_cols = [
            'broker_response_latency_ms', 'result_code', 'password_length',
            'payload_entropy', 'auth_attempt_rate', 'auth_failure_rate',
            'auth_success_rate', 'unique_passwords_tried', 'credential_entropy',
            'inter_arrival_mean_ms', 'inter_arrival_std_ms', 'consecutive_failures',
            'session_attempt_count', 'session_failure_rate', 'latency_zscore'
        ]
        print("✅ Random Forest Model & Scaler loaded successfully.")

    def drop_ip(self, ip_address, reason):
        """Executes OS-level iptables command to drop the attacker."""
        if ip_address in self.banned_ips or ip_address in ["127.0.0.1", "192.168.21.120"]:
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
        
        last_file = None
        last_position = 0
        
        while True:
            # Find the most recently modified CSV in dataset/logs
            csv_files = glob.glob(os.path.join(self.log_dir, "*.csv"))
            target_files = [f for f in csv_files if "audit" not in f]
            
            if not target_files:
                time.sleep(1)
                continue
                
            latest_csv = max(target_files, key=os.path.getmtime)
            
            if latest_csv != last_file:
                # Switched to a new file (e.g. a new attack started)
                last_file = latest_csv
                last_position = 0
                
            try:
                # Read only new lines
                with open(latest_csv, 'r') as f:
                    f.seek(last_position)
                    new_lines = f.readlines()
                    last_position = f.tell()
                    
                if not new_lines:
                    time.sleep(0.5)
                    continue
                
                # If we are reading from the start, skip the header
                if len(new_lines) > 0 and "timestamp" in new_lines[0]:
                    new_lines = new_lines[1:]
                    
                for line in new_lines:
                    parts = line.strip().split(',')
                    if len(parts) < 20: continue
                    
                    # Extract raw data
                    src_ip = parts[1]
                    if src_ip in self.banned_ips:
                        continue # Already neutralized
                        
                    # Extract the exactly 15 features matching self.feature_cols
                    # Map: latency(5), rc(6), pw_len(7), payload_ent(8), auth_att(9), auth_fail(10), auth_succ(11), 
                    # unique_pw(12), cred_ent(13), iat_mean(14), iat_std(15), consec_fail(16), sess_count(17), 
                    # sess_fail_rate(18), latency_z(19)
                    try:
                        features = [float(x) for x in parts[5:20]]
                    except ValueError:
                        continue
                        
                    # 1. Scale
                    features_scaled = self.scaler.transform([features])
                    
                    # 2. Predict (0=Normal, 1=BruteForce, 2=DoS, 3=Replay)
                    prediction = self.model.predict(features_scaled)[0]
                    
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
