import os
import glob
import pandas as pd

LOG_DIR = "dataset/logs"

TARGET_SCHEMA = [
    'timestamp', 'src_ip', 'target_ip', 'attack_label', 'attack_type',
    'packets_per_second', 'mqtt_publish_rate', 'broker_response_latency_ms',
    'device_heap_free_bytes', 'auth_attempt_rate', 'auth_failure_rate',
    'unique_passwords_tried', 'result_code', 'password_length', 'payload_entropy',
    'auth_success_rate', 'credential_entropy', 'duplicate_payload_rate',
    'msg_timestamp_delta_ms', 'motion', 'arm', 'inter_arrival_mean_ms',
    'inter_arrival_std_ms', 'consecutive_failures', 'session_attempt_count',
    'session_failure_rate', 'latency_zscore'
]

def align_all_datasets():
    print("🚀 Starting 27-Feature Schema Alignment...")
    
    csv_files = glob.glob(os.path.join(LOG_DIR, "*.csv"))
    target_files = [f for f in csv_files if "audit" not in f]
    
    if not target_files:
        print("❌ No valid ML log files found.")
        return

    for file_path in target_files:
        try:
            df = pd.read_csv(file_path)
            
            # Check if it already matches exactly (to avoid unnecessary rewrites)
            if list(df.columns) == TARGET_SCHEMA:
                print(f"✅ {os.path.basename(file_path)} is already perfectly aligned.")
                continue
                
            print(f"🔄 Aligning {os.path.basename(file_path)} (Original columns: {len(df.columns)})")
            
            # Identify missing columns and inject sensible defaults
            missing_cols = set(TARGET_SCHEMA) - set(df.columns)
            for col in missing_cols:
                if col == 'target_ip':
                    df[col] = '192.168.21.165'
                elif col == 'device_heap_free_bytes':
                    df[col] = 235000
                elif col == 'motion':
                    df[col] = 0   # No motion detected (baseline)
                elif col == 'arm':
                    df[col] = 1   # System armed/active (baseline)
                else:
                    df[col] = 0
                    
            # Reorder to exact target schema (keeps all 27 cols, no drops)
            df = df[TARGET_SCHEMA]
            
            # Save back to file
            df.to_csv(file_path, index=False)
            print(f"  --> Successfully saved with exactly {len(df.columns)} columns.")
            
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(file_path)}: {e}")

    print("🎉 All datasets aligned to 27-feature schema!")

if __name__ == "__main__":
    align_all_datasets()
