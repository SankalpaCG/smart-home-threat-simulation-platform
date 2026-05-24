import nbformat as nbf
import os

def main():
    nb = nbf.v4.new_notebook()

    title_md = """# Smart Home Threat Simulation: Model Comparison
## Evaluating Multiple Architectures against IoT Threats

This notebook rigorously validates our 100% Random Forest accuracy by comparing it against 4 other architectures (Decision Tree, LinearSVC, XGBoost, and Logistic Regression) on the full 1.6M row dataset.
"""

    imports_code = """!pip install xgboost

import pandas as pd
import numpy as np
import time
import gc

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression

import warnings
warnings.filterwarnings("ignore")
"""

    data_md = """### 1. Data Ingestion
Mount Google Drive and load the dataset."""

    data_code = """from google.colab import drive
drive.mount('/content/drive')

# NOTE: Adjust path if necessary
dataset_path = '/content/drive/MyDrive/combined_ml_dataset.csv'

print(f"Loading dataset from: {dataset_path}")
df = pd.read_csv(dataset_path)
print(f"Dataset Shape: {df.shape}")
"""

    prep_md = """### 2. Preprocessing
We separate the target labels and Label-Encode the non-numeric context columns (IPs, timestamp) exactly as we did in the original baseline training."""

    prep_code = """y = df['attack_label']
X = df.drop(columns=['attack_label', 'attack_type'])

non_numeric_cols = ['timestamp', 'src_ip', 'target_ip']
le = LabelEncoder()
for col in non_numeric_cols:
    X[col] = le.fit_transform(X[col].astype(str))

del df
gc.collect()

print("Splitting data (80% Train, 20% Test)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("Scaling numerical features with StandardScaler...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Training features shape: {X_train_scaled.shape}")
"""

    train_md = """### 3. Model Training & Comparison
Train all 5 models and record their performance metrics. We use `LinearSVC` instead of a standard `SVC` kernel to avoid extreme $O(n^2)$ time complexity on the 1.6 million row dataset."""

    train_code = """models = {
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "LinearSVC": LinearSVC(random_state=42, max_iter=2000, dual=False),
    "XGBoost": XGBClassifier(random_state=42, n_jobs=-1, eval_metric="mlogloss"),
    "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000, n_jobs=-1)
}

results = []

for name, model in models.items():
    print(f"Training [{name}]...")
    start_time = time.time()
    
    # Train
    model.fit(X_train_scaled, y_train)
    
    # Predict
    y_pred = model.predict(X_test_scaled)
    
    train_time = time.time() - start_time
    
    # Metrics
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
    
    print(f"✅ {name} trained in {train_time:.1f}s | Acc: {acc:.4f} | F1: {f1:.4f}\\n")
"""

    eval_md = """### 4. Final Comparison Report"""

    eval_code = """results_df = pd.DataFrame(results)

# Format columns for beautiful output
results_df['Accuracy'] = results_df['Accuracy'].apply(lambda x: f"{x:.4%}")
results_df['Precision'] = results_df['Precision'].apply(lambda x: f"{x:.4%}")
results_df['Recall'] = results_df['Recall'].apply(lambda x: f"{x:.4%}")
results_df['F1-Score'] = results_df['F1-Score'].apply(lambda x: f"{x:.4%}")
results_df['Time (s)'] = results_df['Time (s)'].apply(lambda x: f"{x:.1f}s")

display(results_df)
"""

    nb['cells'] = [
        nbf.v4.new_markdown_cell(title_md),
        nbf.v4.new_code_cell(imports_code),
        nbf.v4.new_markdown_cell(data_md),
        nbf.v4.new_code_cell(data_code),
        nbf.v4.new_markdown_cell(prep_md),
        nbf.v4.new_code_cell(prep_code),
        nbf.v4.new_markdown_cell(train_md),
        nbf.v4.new_code_cell(train_code),
        nbf.v4.new_markdown_cell(eval_md),
        nbf.v4.new_code_cell(eval_code)
    ]

    output_path = '/home/pirator/smart-home-threat-simulation-platform/model_comparison/Model_Comparison_Colab.ipynb'
    with open(output_path, 'w') as f:
        nbf.write(nb, f)
    
    print(f"Successfully generated Google Colab Notebook at: {output_path}")

if __name__ == '__main__':
    main()
