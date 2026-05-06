import nbformat as nbf

nb = nbf.v4.new_notebook()

title_md = """# 🛡️ Smart Home Threat Simulation Platform
## Intrusion Detection System (ML-IDS) - Random Forest Classifier

This notebook trains a Random Forest model using the 20-feature dataset generated from our local IoT threat simulations. It is designed to maximize detection accuracy across `BRUTE_FORCE`, `DOS`, `REPLAY`, and `NORMAL` traffic."""

imports_code = """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Set plot style
plt.style.use('dark_background')
sns.set_palette("husl")
"""

data_md = """### 1. Data Ingestion & Exploration
We will mount your Google Drive so the notebook can access the massive datasets without needing to manually upload them every time the session restarts."""

data_code = """# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# NOTE: Make sure you upload 'combined_ml_dataset.csv' to your Google Drive!
# Change this path if you put it inside a specific folder in your Drive.
dataset_path = '/content/drive/MyDrive/Colab Notebooks/combined_ml_dataset.csv'

# Load dataset
df = pd.read_csv(dataset_path)

print(f"Dataset Shape: {df.shape}")
print("\\nClass Distribution:")
print(df['attack_label'].value_counts())
print("\\nTraffic Types:")
print(df['attack_type'].value_counts())

df.head()"""

prep_md = """### 2. Preprocessing
We drop non-numerical identifiers (IPs, timestamp) and scale the features."""

prep_code = """# Drop non-feature columns
drop_cols = ['timestamp', 'src_ip', 'target_ip', 'attack_type']
X = df.drop(columns=drop_cols)
y = df['attack_label']

# Split data (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Feature Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Training features shape: {X_train_scaled.shape}")"""

train_md = """### 3. Model Training
Train the Random Forest Classifier. RF is highly robust to noise and doesn't require massive hyperparameter tuning for tabular IoT data."""

train_code = """# Initialize Random Forest
rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight='balanced')

# Train
print("Training Random Forest model...")
rf_model.fit(X_train_scaled, y_train)
print("Training Complete!")"""

eval_md = """### 4. Evaluation & Visualizations
These graphs are ready to be exported for the Masters Report."""

eval_code = """# Predictions
y_pred = rf_model.predict(X_test_scaled)

# 1. Classification Report
print("Classification Report:\\n")
print(classification_report(y_test, y_pred))

# 2. Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
plt.title('Confusion Matrix', fontsize=16)
plt.ylabel('Actual Label', fontsize=12)
plt.xlabel('Predicted Label', fontsize=12)
plt.show()

# 3. Feature Importance
feature_importances = pd.Series(rf_model.feature_importances_, index=X.columns)
feature_importances = feature_importances.sort_values(ascending=False)

plt.figure(figsize=(10, 8))
sns.barplot(x=feature_importances.values, y=feature_importances.index, palette='viridis')
plt.title('Feature Importance in Attack Detection', fontsize=16)
plt.xlabel('Importance Score', fontsize=12)
plt.ylabel('Features', fontsize=12)
plt.tight_layout()
plt.show()"""

export_md = """### 5. Export Model for Live Deployment
Save the `.pkl` files to deploy into the active IPS `live_ml_ips.py`."""

export_code = """# Save model and scaler directly to Google Drive!
model_export_path = '/content/drive/MyDrive/Colab Notebooks/random_forest_ids.pkl'
scaler_export_path = '/content/drive/MyDrive/Colab Notebooks/scaler.pkl'

joblib.dump(rf_model, model_export_path)
joblib.dump(scaler, scaler_export_path)

print(f"✅ Successfully exported model to: {model_export_path}")
print(f"✅ Successfully exported scaler to: {scaler_export_path}")
print("You can now download these files directly from your Google Drive to deploy locally!")"""

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
    nbf.v4.new_code_cell(eval_code),
    nbf.v4.new_markdown_cell(export_md),
    nbf.v4.new_code_cell(export_code)
]

with open('dataset/RandomForest_IDS_Training.ipynb', 'w') as f:
    nbf.write(nb, f)
    
print("Successfully generated RandomForest_IDS_Training.ipynb")
