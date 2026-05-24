import pandas as pd
import numpy as np
import time
import os
import gc

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Models
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression

# Disable harmless Joblib parallel warning for cleaner output
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.utils.parallel")

def main():
    print("="*60)
    print("  Smart Home ML-IPS: Multi-Model Comparison Engine")
    print("="*60)

    dataset_path = "/home/pirator/smart-home-threat-simulation-platform/dataset/combined_ml_dataset.csv"
    output_dir = "/home/pirator/smart-home-threat-simulation-platform/model_comparison"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load Data
    print(f"Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"Dataset Shape: {df.shape}")
    
    # 2. Preprocess Data (Matching generate_notebook.py)
    print("Preprocessing data...")
    non_numeric_cols = ['timestamp', 'src_ip', 'target_ip']
    df = df.drop(columns=non_numeric_cols)
    
    X = df.drop(columns=['attack_label', 'attack_type'])
    y = df['attack_label']
    
    # Free memory
    del df
    gc.collect()
    
    print("Splitting data (80% Train, 20% Test)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Scaling numerical features with StandardScaler...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Define models
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "LinearSVC": LinearSVC(random_state=42, max_iter=2000, dual=False),
        "XGBoost": XGBClassifier(random_state=42, n_jobs=-1, eval_metric="mlogloss"),
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000, n_jobs=-1)
    }
    
    results = []
    
    print("\n" + "="*60)
    print("Training Phase Initiated")
    print("="*60)
    
    for name, model in models.items():
        print(f"Training [{name}]...")
        start_time = time.time()
        
        # Train
        model.fit(X_train_scaled, y_train)
        
        # Predict
        y_pred = model.predict(X_test_scaled)
        
        train_time = time.time() - start_time
        
        # Metrics
        # Using average='weighted' since it's a multiclass problem (0=Normal, 1=Brute, 2=DoS, 3=Replay)
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        results.append({
            "Model": name,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1,
            "Time (s)": train_time
        })
        
        print(f"✅ {name} trained in {train_time:.1f}s | Acc: {acc:.4f} | F1: {f1:.4f}")
        
    print("\n" + "="*60)
    print("Generating Documentation")
    print("="*60)
    
    # Generate Markdown Report
    md_content = "# Machine Learning Model Comparison\n\n"
    md_content += "This document compares 5 different machine learning architectures on the Smart Home Threat Simulation dataset.\n\n"
    md_content += "> **Note on SVM:** Due to the massive dataset size (1.6M rows), training a standard kernel `SVC` would have taken an unfeasible amount of time (time complexity $O(n^2)$). We explicitly utilized **`LinearSVC`** to test a highly-optimized margin-based classifier capable of handling large-scale tabular data.\n\n"
    
    md_content += "## Performance Metrics\n\n"
    md_content += "| Model | Accuracy | Precision | Recall | F1-Score | Training Time (s) | Comment |\n"
    md_content += "|---|---|---|---|---|---|---|\n"
    
    comments = {
        "Random Forest": "Strong ensemble baseline (Current Prod)",
        "Decision Tree": "Simple, highly interpretable rule-based tree",
        "LinearSVC": "Scalable margin-based classifier (Linear approx)",
        "XGBoost": "State-of-the-art gradient boosting framework",
        "Logistic Regression": "Traditional linear baseline model"
    }
    
    for r in results:
        md_content += f"| **{r['Model']}** | {r['Accuracy']:.4%} | {r['Precision']:.4%} | {r['Recall']:.4%} | {r['F1-Score']:.4%} | {r['Time (s)']:.1f}s | {comments[r['Model']]} |\n"
        
    md_content += "\n## Conclusion\n"
    md_content += "*(Auto-generated results. Review the table above for insights into model selection vs compute trade-offs.)*\n"
    
    out_file = os.path.join(output_dir, "results.md")
    with open(out_file, 'w') as f:
        f.write(md_content)
        
    print(f"Documentation successfully saved to: {out_file}")
    print("Process Complete.")

if __name__ == "__main__":
    main()
