import pandas as pd
import numpy as np
import glob
import os

print("====================================================")
print("  🛡️ SMART HOME THREAT PLATFORM - DATA AUGMENTATION")
print("====================================================")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "logs"))

# Find existing normal logs
pre_files = glob.glob(os.path.join(BASE_DIR, "normal_pre_attack_*.csv"))
post_files = glob.glob(os.path.join(BASE_DIR, "normal_post_attack_*.csv"))

if not pre_files:
    print("❌ No normal_pre_attack files found to augment.")
    exit()

def augment_data(files, target_count, output_name):
    print(f"\\nReading existing normal data from {len(files)} files...")
    df_list = []
    for f in files:
        try:
            df = pd.read_csv(f)
            df_list.append(df)
        except:
            pass
            
    if not df_list:
        return
        
    df_real = pd.concat(df_list, ignore_index=True)
    current_count = len(df_real)
    print(f"Found {current_count} real records.")
    
    if current_count >= target_count:
        print("Dataset already large enough.")
        return
        
    needed = target_count - current_count
    print(f"Generating {needed} synthetic records with Gaussian jitter...")
    
    # Randomly sample with replacement
    df_synthetic = df_real.sample(n=needed, replace=True).reset_index(drop=True)
    
    # Add tiny random jitter to numeric columns so the ML model doesn't just memorize duplicates
    jitter_cols = ['broker_response_latency_ms', 'inter_arrival_mean_ms', 'inter_arrival_std_ms']
    
    for col in jitter_cols:
        if col in df_synthetic.columns:
            std_dev = df_real[col].std()
            if pd.isna(std_dev) or std_dev == 0:
                std_dev = df_real[col].mean() * 0.05 # 5% of mean if no variance
            
            # Add normally distributed noise (mu=0, sigma=0.02 * std)
            noise = np.random.normal(0, max(std_dev * 0.02, 0.001), size=needed)
            df_synthetic[col] = np.abs(df_synthetic[col] + noise)
            
    # Combine real and synthetic
    df_final = pd.concat([df_real, df_synthetic], ignore_index=True)
    
    # Save
    out_path = os.path.join(BASE_DIR, output_name)
    df_final.to_csv(out_path, index=False)
    print(f"✅ Saved {len(df_final)} balanced records to {output_name}")

# Generate 5000 pre and 5000 post (Total 10000 normal records)
augment_data(pre_files, 5000, "synthetic_normal_pre_attack.csv")
print("-" * 50)
if post_files:
    augment_data(post_files, 5000, "synthetic_normal_post_attack.csv")
else:
    # If no post-attack files exist, just generate 10000 pre-attack
    print("No post-attack files found, generating 10000 pre-attack instead...")
    augment_data(pre_files, 10000, "synthetic_normal_pre_attack.csv")

print("\\n✅ Data Augmentation Complete! Please run dataset/feature_engineering.py now to update the master ML dataset.")
