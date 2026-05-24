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
    
    # Include both logs and sessions directories
    csv_files = glob.glob(os.path.join(LOG_DIR, "*.csv")) + glob.glob("dataset/sessions/*.csv")
    target_files = [f for f in csv_files if "audit" not in f]
    
    if not target_files:
        print("❌ No valid ML log files found.")
        return

    all_dataframes = []

    for file_path in target_files:
        try:
            df = pd.read_csv(file_path)
            
            # Identify missing columns and inject sensible defaults
            missing_cols = set(TARGET_SCHEMA) - set(df.columns)
            for col in missing_cols:
                if col == 'target_ip':
                    df[col] = '192.168.1.100'
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
            
            # --- APPLY USER FIXES DURING ALIGNMENT ---
            # Automatically convert legacy dos_botnet string to 'ddos'
            if 'attack_type' in df.columns:
                df['attack_type'] = df['attack_type'].replace(['dos_botnet', 'dos_standard', 'DoS', 'Distributed_Botnet_DoS'], 'ddos')
            
            # Save back to file
            df.to_csv(file_path, index=False)
            print(f"✅ Aligned and Normalized: {os.path.basename(file_path)} ({len(df)} rows)")
            
            all_dataframes.append(df)
            
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(file_path)}: {e}")

    if all_dataframes:
        print("\n📦 Merging into final Master Dataset...")
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        final_path = "dataset/combined_ml_dataset.csv"
        combined_df.to_csv(final_path, index=False)
        print(f"🎉 SUCCESS! Final dataset created at '{final_path}' with {len(combined_df)} rows and {len(combined_df.columns)} features!")

    print("🎉 All datasets aligned to 27-feature schema!")

if __name__ == "__main__":
    align_all_datasets()
