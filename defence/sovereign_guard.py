import paho.mqtt.client as mqtt
import time
import sys
import pandas as pd
import os
import json

# Ensure the project root is in the path for forensic_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_utils import DualLogger, get_iso_now, get_timestamp

# Standardized Research Banners
BANNER = """
==================================================
  SOVEREIGNTY RESEARCH: INTRUSION PREVENTION (IPS)
==================================================
"""

# Configuration
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INTELLIGENCE_FILE = os.path.join(PROJECT_ROOT, "dataset/raw/network_intelligence.csv")
LOG_DIR = os.path.join(PROJECT_ROOT, "dataset/logs")

# Thresholds
RISK_THRESHOLD = 85.0
DOS_VOLUME_THRESHOLD = 100 # High-velocity packet trigger

class SovereignGuard:
    def __init__(self, broker="192.168.1.105"):
        self.broker = broker
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Sovereign_Guard")
        self.headers = ["timestamp", "mitigation_action", "reason", "target_topic"]
        self.log_base = "guard_mitigation_audit"

    def record_mitigation(self, action, reason, target="N/A"):
        """Forensic logging of IPS actions."""
        record = {
            "timestamp": get_iso_now(),
            "mitigation_action": action,
            "reason": reason,
            "target_topic": target
        }
        DualLogger.append_raw(record, LOG_DIR, self.log_base, headers=self.headers)

    def trigger_lockdown(self, reason):
        print(f"\n⚠️  [GUARD] CRITICAL THREAT DETECTED: {reason}")
        print("🚨 Sending LOCKDOWN signal to Security Hub...")
        
        payload = {
            "action": "LOCKDOWN",
            "reason": reason,
            "timestamp": time.time()
        }
        topic_cmd = "shtsp/home/security/cmd"
        self.client.publish(topic_cmd, json.dumps(payload))
        self.client.publish("shtsp/guard/alerts", f"MITIGATION_ACTIVE: {reason}")
        
        # Log the forensic trail
        self.record_mitigation("LOCKDOWN", reason, topic_cmd)
        print("✅ Lockdown command dispatched and logged.")

    def run(self):
        print(BANNER)
        print(f"🛡️  IPS active. Monitoring broker: {self.broker}")
        print("-" * 50)
        
        try:
            self.client.connect(self.broker, 1883, 60)
            self.client.loop_start()
            
            last_row_count = 0
            while True:
                if os.path.exists(INTELLIGENCE_FILE):
                    try:
                        df = pd.read_csv(INTELLIGENCE_FILE)
                        if len(df) > last_row_count:
                            new_packets = len(df) - last_row_count
                            # Mitigation Logic: Volume-based DoS Prevention
                            if new_packets > DOS_VOLUME_THRESHOLD:
                                self.trigger_lockdown(f"Volumetric DDoS (Burst: {new_packets} pkts)")
                                time.sleep(10) # Cooldown to prevent flapping
                            
                            last_row_count = len(df)
                    except Exception as e:
                        print(f"⚠️  Data read warning: {e}")
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Guard stopped.")
        except Exception as e:
            print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    guard = SovereignGuard()
    guard.run()
