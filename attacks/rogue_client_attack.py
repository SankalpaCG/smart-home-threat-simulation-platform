import sys
import os
import paho.mqtt.client as mqtt
import argparse
import random
import time
import json

# Ensure the project root is in the path for forensic_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_utils import DualLogger, get_timestamp, get_iso_now

# Standardized Research Banners
BANNER = """
==================================================
  SOVEREIGNTY RESEARCH: IDENTITY RECON PROBE
==================================================
"""

# Configuration for standardized logging
BASE_DIR = "/home/pirator/smart-home-threat-simulation-platform/dataset"
LOG_DIR = os.path.join(BASE_DIR, "logs")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")

BROKER = "192.168.1.105"
PORT = 1883

# Advanced Identity Pool for Reconnaissance
PROBE_IDENTITIES = [
    "admin_console_01",
    "root_debug_hub",
    "esp32_gateway_test",
    "security_admin_iot",
    "mqtt_explorer_client",
    "kali_recon_probe"
]

# Wildcards to evaluate exfiltration risk
PROBE_TOPICS = ["#", "$SYS/#", "shtsp/+/+/+"]

class ReconLogger:
    def __init__(self):
        self.timestamp = get_timestamp()
        self.leaked_topics = []
        self.probes = []

    def log_probe(self, identity, status):
        self.probes.append({"identity": identity, "status": status})

    def log_leak(self, topic):
        if topic not in self.leaked_topics:
            self.leaked_topics.append(topic)

    def save_session(self):
        session_data = {
            "timestamp": self.timestamp,
            "attack_type": "Identity_Reconnaissance",
            "probes_executed": self.probes,
            "exfiltration_points": self.leaked_topics,
            "total_leaked_topics": len(self.leaked_topics)
        }
        json_p, csv_p = DualLogger.log_session(session_data, SESSIONS_DIR, f"recon_session_{self.timestamp}")
        print(f"\n📊 Forensic Trace Recorded: {json_p} (+.csv)")

recon_logger = ReconLogger()

def on_connect(client, userdata, flags, rc):
    identity = userdata['id']
    status = "SUCCESS" if rc == 0 else f"REFUSED_{rc}"
    recon_logger.log_probe(identity, status)
    
    if rc == 0:
        print(f"✅ PROBE SUCCESS: Identity accepted as '{identity}'")
        for topic in PROBE_TOPICS:
            print(f"📡 Attempting wildcard subscription to: {topic}")
            client.subscribe(topic)
    else:
        print(f"❌ PROBE REFUSED: Code {rc} for '{identity}'")

def on_message(client, userdata, msg):
    print(f"🔓 EXFILTRATION: Data leaked from {msg.topic}")
    recon_logger.log_leak(msg.topic)

def run_probe(identity):
    print(f"\n🔍 Initializing Recon Probe with ID: '{identity}'")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, identity, userdata={"id": identity})
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(BROKER, PORT, 10)
        client.loop_start()
        time.sleep(5) 
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        recon_logger.log_probe(identity, f"ERROR: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Advanced Broker Identity Reconnaissance Analysis")
    parser.add_argument("--broker", default="192.168.1.105", help="Target Broker IP")
    parser.add_argument("--all", action="store_true", help="Rotate through all identity probes")
    
    args = parser.parse_args()

    print(f"\n🚀 [ADVANCED RECON SIMULATION START] 🚀")
    print(f"Targeting: {args.broker} | Identities: {len(PROBE_IDENTITIES)}")
    print("-" * 50)

    try:
        if args.all:
            for identity in PROBE_IDENTITIES:
                run_probe(identity)
        else:
            run_probe(random.choice(PROBE_IDENTITIES))
    except KeyboardInterrupt:
        pass

    recon_logger.save_session()
    print("-" * 50)
    print("🏁 Recon Probe Sequence Completed.")

if __name__ == "__main__":
    main()
