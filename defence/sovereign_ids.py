import pandas as pd
import numpy as np
import time
import os
import sys
from sklearn.ensemble import IsolationForest
import warnings

# Ensure the project root is in the path for forensic_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_utils import DualLogger, get_iso_now, get_timestamp

# Standardized Research Banners
BANNER = """
==================================================
  SOVEREIGNTY RESEARCH: ANOMALY DETECTION ENGINE
==================================================
"""

# Configuration
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INTELLIGENCE_FILE = os.path.join(PROJECT_ROOT, "dataset/raw/network_intelligence.csv")
LOG_DIR = os.path.join(PROJECT_ROOT, "dataset/logs")
SESSION_DIR = os.path.join(PROJECT_ROOT, "dataset/sessions")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)

warnings.filterwarnings("ignore")

class DetectionEngine:
    def __init__(self):
        self.model = IsolationForest(contamination=0.01)
        self.is_trained = False
        self.session_id = f"ids_audit_{get_timestamp()}"
        self.headers = ["timestamp", "packet_index", "risk_score", "prediction", "status"]

    def engineer_features(self, df):
        """Converts raw intelligence into numerical ML features."""
        # Clean data for conversion
        df = df.copy()
        df['flags_encoded'] = df['tcp_flags'].astype('category').cat.codes
        df['proto_encoded'] = df['proto_type'].astype('category').cat.codes
        
        features = ['tcp_window', 'payload_len', 'payload_entropy', 'flags_encoded']
        return df[features]

    def log_detection(self, packet_index, risk, prediction):
        """Records Every detection event for academic auditing."""
        status = "CRITICAL_ALERT" if prediction == -1 else "BENIGN"
        record = {
            "timestamp": get_iso_now(),
            "packet_index": packet_index,
            "risk_score": risk,
            "prediction": prediction,
            "status": status
        }
        # Log to audit trail
        DualLogger.append_raw(record, LOG_DIR, "ids_audit_trail", headers=self.headers)
        # Log to current session
        DualLogger.append_raw(record, SESSION_DIR, self.session_id, headers=self.headers)

    def train_baseline(self):
        print(BANNER)
        print("🧠 [IDS] Analyzing baseline telemetry for anomaly training...")
        if not os.path.exists(INTELLIGENCE_FILE):
            print("❌ Error: No intelligence file found. Please run sovereign_probe.py first.")
            return False
        
        try:
            df = pd.read_csv(INTELLIGENCE_FILE)
            if len(df) < 50: # Reduced for testing, increase for pro baseline
                print(f"⚠️  Insufficient data ({len(df)}/50). Sniffing required...")
                return False

            X = self.engineer_features(df)
            self.model.fit(X)
            self.is_trained = True
            print("✅ Baseline Training Complete. Sovereignty IDS is now operational.")
            return True
        except Exception as e:
            print(f"❌ Training Error: {e}")
            return False

    def run_live_detection(self):
        print("🕵️  [IDS] Initializing Real-Time Anomaly Audit...")
        print("-" * 50)
        
        last_row_count = 0
        try:
            while True:
                if not os.path.exists(INTELLIGENCE_FILE):
                    time.sleep(2)
                    continue

                df = pd.read_csv(INTELLIGENCE_FILE)
                if len(df) > last_row_count:
                    new_data = df.iloc[last_row_count:]
                    start_idx = last_row_count
                    last_row_count = len(df)
                    
                    X_new = self.engineer_features(new_data)
                    scores = self.model.decision_function(X_new) 
                    pred = self.model.predict(X_new) 

                    for i, (score, p) in enumerate(zip(scores, pred)):
                        risk = round((1 - score) * 100, 1)
                        status_str = "🔥 ALERT" if p == -1 else "☘️  SAFE"
                        
                        # Forensic Log
                        self.log_detection(start_idx + i, risk, int(p))
                        
                        sys.stdout.write(f"\r[{status_str}] Pkt {start_idx + i} | Risk: {risk}% | Audit Logged.")
                        sys.stdout.flush()

                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 IDS Audit Stopped.")
            # Final session summary record
            print(f"📊 Forensic trace synchronized to: {self.session_id}")

if __name__ == "__main__":
    ids = DetectionEngine()
    if ids.train_baseline():
        ids.run_live_detection()
    else:
        print("💡 Tip: Populate the baseline by running the network probe while simulating normal activity.")
