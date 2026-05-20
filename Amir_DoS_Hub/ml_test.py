import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

# 1. LOAD THE DATASET
file_name = "master_iot_dataset.csv"
df = pd.read_csv(file_name)

# 2. SELECT FEATURES
features = ["packets_per_second", "device_heap_free_bytes", "broker_response_latency_ms", "motion", "arm"]
X = df[features].fillna(0)
y_actual = df['attack_label']

# 3. FEATURE SCALING
scaler = StandardScaler()
# We scale based on the whole dataset's range
X_scaled = scaler.fit_transform(X)

# 4. TRAIN ONLY ON NORMAL DATA (The "Clean" Baseline)
# This teaches the AI what a healthy home looks like
X_train = X_scaled[y_actual == 0] 
print(f"🧠 Training AI on {len(X_train)} Normal rows...")

# contamination='auto' lets the model decide the threshold
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X_train)

# 5. PREDICT ON THE WHOLE DATASET
# 1 = Normal, -1 = Anomaly
raw_preds = model.predict(X_scaled)
df['ai_is_attack'] = [1 if p == -1 else 0 for p in raw_preds]

# 6. CALCULATE PERFORMANCE
# How many real attacks (Label 1) did the AI flag as an anomaly?
total_attacks = len(df[df['attack_label'] == 1])
detected_attacks = len(df[(df['attack_label'] == 1) & (df['ai_is_attack'] == 1)])
accuracy = (detected_attacks / total_attacks) * 100

print("\n" + "="*40)
print("🏆 FINAL MACHINE LEARNING RESULTS")
print("="*40)
print(f"✅ Normal Rows Used for Training: {len(X_train)}")
print(f"🚨 Total Attacks tested: {total_attacks}")
print(f"🎯 Attacks Correctly Caught: {detected_attacks}")
print(f"📈 RECALCULATED ACCURACY: {accuracy:.2f}%")
print("="*40)

# 7. SAVE THE BRAIN
joblib.dump(model, "smart_home_ai.pkl")
joblib.dump(scaler, "data_scaler.pkl")
print("💾 AI Brain and Scaler saved successfully.")