import pandas as pd
import sys
import os

def validate_dataset(filepath: str, output_path: str):
    print(f"Loading dataset from: {filepath}")
    if not os.path.exists(filepath):
        print(f"Dataset not found at {filepath}")
        sys.exit(1)
        
    df = pd.read_csv(filepath)
    
    with open(output_path, "w") as f:
        f.write("========================================================\n")
        f.write("      SMART HOME IDS - DATASET VALIDATION REPORT        \n")
        f.write("========================================================\n\n")
        
        # 1. Shape & Structure
        f.write("1. DATASET STRUCTURE\n")
        f.write("-" * 50 + "\n")
        f.write(f"Total Records (Rows): {df.shape[0]}\n")
        f.write(f"Total Features (Columns): {df.shape[1]}\n")
        f.write("Feature Schema:\n")
        for col in df.columns:
            f.write(f"  - {col} ({df[col].dtype})\n")
        f.write("\n")
        
        # 2. Missing Values
        f.write("2. MISSING VALUE ANALYSIS (NaN/Null)\n")
        f.write("-" * 50 + "\n")
        null_counts = df.isnull().sum()
        total_nulls = null_counts.sum()
        f.write(f"Total Missing Values Across Dataset: {total_nulls}\n")
        if total_nulls > 0:
            f.write(null_counts[null_counts > 0].to_string() + "\n")
        f.write("\n")
        
        # 3. Class Balance
        f.write("3. CLASS DISTRIBUTION (attack_label)\n")
        f.write("-" * 50 + "\n")
        if "attack_label" in df.columns:
            balance = df["attack_label"].value_counts()
            f.write(balance.to_string() + "\n")
            f.write("\nLabel Mapping:\n")
            f.write("0 = NORMAL\n1 = BRUTE FORCE\n2 = DOS\n3 = REPLAY\n")
        else:
            f.write("ERROR: 'attack_label' column missing.\n")
        f.write("\n")
        
        # 4. Duplicates
        f.write("4. DUPLICATION ANALYSIS\n")
        f.write("-" * 50 + "\n")
        dupes = df.duplicated().sum()
        f.write(f"Total Exact Duplicate Rows: {dupes}\n")
        f.write(f"Duplication Rate: {(dupes / len(df) * 100):.2f}%\n")
        f.write("\n")
        
        # 5. Data Leakage Check
        f.write("5. DATA LEAKAGE PREVENTION CHECK\n")
        f.write("-" * 50 + "\n")
        leakage_cols = ["attack_type", "src_ip", "target_ip"]
        found_leaks = [col for col in leakage_cols if col in df.columns]
        if found_leaks:
            f.write(f"WARNING: Potential leakage features found in training data: {found_leaks}\n")
            f.write("These must be dropped during X/y splitting to prevent model memorization.\n")
        else:
            f.write("PASS: No explicit leakage columns found.\n")
        
        f.write("\n========================================================\n")
        f.write("                  VALIDATION COMPLETE                   \n")
        f.write("========================================================\n")

if __name__ == "__main__":
    dataset_path = "../dataset/combined_ml_dataset.csv"
    output_path = "DATASET_VALIDATION_RESULTS.txt"
    validate_dataset(dataset_path, output_path)
    print(f"Validation complete. Results saved to {output_path}")
