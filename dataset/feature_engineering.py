import os
import glob
import pandas as pd
import numpy as np

# Configuration
LOG_DIR = "dataset/logs"
OUTPUT_FILE = "dataset/combined_ml_dataset.csv"

def generate_dataset():
    print("🚀 Starting Feature Engineering & Dataset Aggregation...")
    
    # 1. Find all relevant ML log files (excluding audit logs)
    all_files = glob.glob(os.path.join(LOG_DIR, "*.csv"))
    target_files = [f for f in all_files if "audit" not in f]
    
    if not target_files:
        print("❌ No valid ML log files found in dataset/logs/")
        return

    print(f"📂 Found {len(target_files)} telemetry log files.")
    
    # 2. Load and concatenate datasets
    dfs = []
    for f in target_files:
        try:
            df = pd.read_csv(f)
            dfs.append(df)
            print(f"  + Loaded: {os.path.basename(f)} ({len(df)} rows)")
        except Exception as e:
            print(f"  - Error loading {os.path.basename(f)}: {e}")
            
    if not dfs:
        return
        
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # 3. Data Cleaning and Imputation
    print(f"\n🧹 Cleaning Data (Initial shape: {combined_df.shape})...")
    
    # Fill NaN values with 0 for numeric columns (common in missing sliding windows)
    numeric_cols = combined_df.select_dtypes(include=[np.number]).columns
    combined_df[numeric_cols] = combined_df[numeric_cols].fillna(0)
    
    # 4. Feature Standardization 
    # Drop rows where critical fields are entirely missing
    combined_df = combined_df.dropna(subset=['attack_label', 'timestamp'])
    
    # Sort chronologically
    combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])
    combined_df = combined_df.sort_values(by='timestamp').reset_index(drop=True)
    
    # 5. Label Distribution Analysis
    print("\n📊 Dataset Class Distribution:")
    label_counts = combined_df['attack_label'].value_counts()
    type_counts = combined_df['attack_type'].value_counts()
    
    for label, count in label_counts.items():
        percentage = (count / len(combined_df)) * 100
        print(f"  Label {label}: {count:,} rows ({percentage:.1f}%)")
        
    print("\n📊 Traffic Type Distribution:")
    for type_name, count in type_counts.items():
        print(f"  {type_name}: {count:,} rows")

    # 6. Export
    combined_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Successfully exported unified dataset to: {OUTPUT_FILE}")
    print(f"🔥 The dataset is now ready for Google Colab!")

if __name__ == "__main__":
    generate_dataset()
