import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

# Configuration
DATASET_PATH = "../dataset/combined_ml_dataset.csv"
OUTPUT_DIR = "graphs"

def setup():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    # Set seaborn style for academic quality
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.size': 12, 'figure.dpi': 300})

def plot_class_distribution(df):
    plt.figure(figsize=(8, 6))
    if 'attack_type' in df.columns:
        ax = sns.countplot(data=df, x='attack_type', palette='viridis')
        plt.title("Class Distribution in Dataset", fontweight='bold')
        plt.xlabel("Attack Type")
        plt.ylabel("Number of Samples")
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', fontweight='bold')
        plt.savefig(os.path.join(OUTPUT_DIR, "class_distribution.png"), bbox_inches='tight')
        plt.close()

def plot_bruteforce_metrics(df):
    brute_df = df[df['attack_label'] == 1].copy() # 1 = BRUTE_FORCE
    if not brute_df.empty and 'auth_failure_rate' in brute_df.columns:
        brute_df = brute_df.reset_index(drop=True)
        # Sample or use head to simulate "over time"
        brute_df = brute_df.head(500)
        
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=brute_df, x=brute_df.index, y='auth_failure_rate', color='red')
        plt.title("Brute Force: Authentication Failure Rate Over Time", fontweight='bold')
        plt.xlabel("Timeline (Samples)")
        plt.ylabel("Auth Failure Rate")
        plt.savefig(os.path.join(OUTPUT_DIR, "bruteforce_auth_failure_rate.png"), bbox_inches='tight')
        plt.close()

        plt.figure(figsize=(10, 5))
        sns.lineplot(data=brute_df, x=brute_df.index, y='consecutive_failures', color='orange')
        plt.title("Brute Force: Consecutive Failures Escalation", fontweight='bold')
        plt.xlabel("Timeline (Samples)")
        plt.ylabel("Consecutive Failures")
        plt.savefig(os.path.join(OUTPUT_DIR, "bruteforce_consecutive_failures.png"), bbox_inches='tight')
        plt.close()

def plot_dos_metrics(df):
    dos_df = df[df['attack_label'] == 2].copy() # 2 = DOS
    if not dos_df.empty and 'packets_per_second' in dos_df.columns:
        dos_df = dos_df.reset_index(drop=True).head(500)
        
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=dos_df, x=dos_df.index, y='packets_per_second', color='darkred')
        plt.title("DoS: Packets Per Second Spike", fontweight='bold')
        plt.xlabel("Timeline (Samples)")
        plt.ylabel("Packets / Sec")
        plt.fill_between(dos_df.index, dos_df['packets_per_second'], color='darkred', alpha=0.3)
        plt.savefig(os.path.join(OUTPUT_DIR, "dos_packets_per_second.png"), bbox_inches='tight')
        plt.close()
        
        if 'broker_response_latency_ms' in dos_df.columns:
            plt.figure(figsize=(10, 5))
            sns.lineplot(data=dos_df, x=dos_df.index, y='broker_response_latency_ms', color='purple')
            plt.title("DoS: Broker Response Latency Degradation", fontweight='bold')
            plt.xlabel("Timeline (Samples)")
            plt.ylabel("Latency (ms)")
            plt.savefig(os.path.join(OUTPUT_DIR, "dos_broker_latency.png"), bbox_inches='tight')
            plt.close()

def plot_replay_metrics(df):
    replay_df = df[df['attack_label'] == 3].copy() # 3 = REPLAY
    if not replay_df.empty and 'duplicate_payload_rate' in replay_df.columns:
        replay_df = replay_df.reset_index(drop=True).head(500)
        
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=replay_df, x=replay_df.index, y='duplicate_payload_rate', color='blue')
        plt.title("Replay Attack: Duplicate Payload Rate Escalation", fontweight='bold')
        plt.xlabel("Timeline (Samples)")
        plt.ylabel("Duplicate Payload Rate")
        plt.savefig(os.path.join(OUTPUT_DIR, "replay_duplicate_payload.png"), bbox_inches='tight')
        plt.close()

def train_and_plot_ml(df):
    print("Training Random Forest to generate Confusion Matrix and Feature Importance...")
    # Drop leakages and non-numeric
    drop_cols = ['attack_label', 'attack_type', 'timestamp', 'src_ip', 'target_ip']
    existing_drops = [c for c in drop_cols if c in df.columns]
    
    X = df.drop(columns=existing_drops)
    y = df['attack_label']
    
    # Fill any NaNs just in case
    X = X.fillna(0)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    rf = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    
    # 1. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    labels = ["Normal", "Brute Force", "DoS", "Replay"]
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.title("IDS Confusion Matrix (Random Forest)", fontweight='bold')
    plt.xlabel("Predicted Class")
    plt.ylabel("Actual Class")
    plt.savefig(os.path.join(OUTPUT_DIR, "ml_confusion_matrix.png"), bbox_inches='tight')
    plt.close()
    
    # 2. Feature Importance
    importances = rf.feature_importances_
    indices = np.argsort(importances)[-10:] # Top 10
    features = X.columns
    
    plt.figure(figsize=(10, 6))
    plt.title('Top 10 Feature Importances (Random Forest)', fontweight='bold')
    plt.barh(range(len(indices)), importances[indices], color='teal', align='center')
    plt.yticks(range(len(indices)), [features[i] for i in indices])
    plt.xlabel('Relative Importance')
    plt.savefig(os.path.join(OUTPUT_DIR, "ml_feature_importance.png"), bbox_inches='tight')
    plt.close()

def main():
    setup()
    print(f"Loading dataset from {DATASET_PATH}...")
    try:
        df = pd.read_csv(DATASET_PATH)
    except FileNotFoundError:
        print("Dataset not found! Ensure it is unzipped or generated.")
        return
        
    print("Generating Class Distribution Graph...")
    plot_class_distribution(df)
    
    print("Generating Brute Force Attack Graphs...")
    plot_bruteforce_metrics(df)
    
    print("Generating DoS Attack Graphs...")
    plot_dos_metrics(df)
    
    print("Generating Replay Attack Graphs...")
    plot_replay_metrics(df)
    
    print("Generating ML Evaluation Graphs...")
    train_and_plot_ml(df)
    
    print(f"All graphs successfully generated in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
