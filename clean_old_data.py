import os
import glob
import pandas as pd

LOG_DIR = "dataset/logs"
SESSION_DIR = "dataset/sessions"

def clean_old_datasets():
    print("🧹 Starting Dataset Cleanup...")
    
    files = glob.glob(os.path.join(LOG_DIR, "*.csv")) + glob.glob(os.path.join(SESSION_DIR, "*.csv"))
    
    deleted_count = 0
    kept_count = 0
    
    for file_path in files:
        # 1. Remove all audit files automatically
        if "audit" in file_path.lower():
            os.remove(file_path)
            json_file = file_path.replace('.csv', '.json')
            if os.path.exists(json_file):
                os.remove(json_file)
            print(f"🗑️ Deleted Audit file: {file_path}")
            deleted_count += 1
            continue

        try:
            df = pd.read_csv(file_path, low_memory=False)
            
            # 2. Check for padded garbage (attack_type == 0 or '0')
            if 'attack_type' in df.columns:
                unique_types = df['attack_type'].astype(str).unique()
                if '0' in unique_types or '0.0' in unique_types:
                    os.remove(file_path)
                    json_file = file_path.replace('.csv', '.json')
                    if os.path.exists(json_file):
                        os.remove(json_file)
                    print(f"🗑️ Deleted Padded/Corrupt file: {file_path} (Found attack_type=0)")
                    deleted_count += 1
                    continue
                    
            # 3. Delete tiny test files (less than 100 rows)
            if len(df) < 100:
                os.remove(file_path)
                json_file = file_path.replace('.csv', '.json')
                if os.path.exists(json_file):
                    os.remove(json_file)
                print(f"🗑️ Deleted Tiny Test file: {file_path} ({len(df)} rows)")
                deleted_count += 1
                continue
                
            kept_count += 1
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    print(f"\nCleanup Complete! Deleted {deleted_count} unwanted files, Kept {kept_count} perfect files.")

if __name__ == "__main__":
    clean_old_datasets()
