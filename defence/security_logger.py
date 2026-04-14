import os
import time
import json
import paho.mqtt.client as mqtt
import sys

# Ensure the project root is in the path for forensic_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_utils import DualLogger, get_timestamp, get_iso_now

# Standardized Research Banners
BANNER = """
==================================================
  SOVEREIGNTY RESEARCH: CENTRAL TELEMETRY LOGGER
==================================================
"""

# Configuration
BROKER = "192.168.1.105"
PORT = 1883
TOPICS = "#"
# Absolute pathing for dataset reliability
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset")
RAW_DIR = os.path.join(DATASET_DIR, "raw")
SESSION_DIR = os.path.join(DATASET_DIR, "sessions")

# Ensure directories exist
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)

# Dataset file base names
master_base = "smart_home_security_dataset"

# State variables
current_label = "normal"
last_seq_num = {}
last_timestamp = time.time()

def get_csv_headers():
    return [
        "timestamp", "topic", "client_id", "seq_num", "msg_type", 
        "status", "uptime_ms", "payload_len", "inter_arrival_time", 
        "seq_gap", "label"
    ]

def process_message(msg):
    """Processes an incoming MQTT message into a research-ready record."""
    global last_timestamp, last_seq_num, current_label
    
    now = time.time()
    inter_arrival = now - last_timestamp
    last_timestamp = now
    
    payload_str = msg.payload.decode('utf-8', errors='ignore')
    payload_len = len(payload_str)
    
    try:
        data = json.loads(payload_str)
        seq = data.get("seq", -1)
        msg_type = data.get("type", "UNKNOWN")
        status = data.get("status", "N/A")
        uptime = data.get("uptime", 0)
    except:
        seq = -1
        msg_type = "MALFORMED"
        status = payload_str[:40].replace('\n', ' ')
        uptime = 0

    topic = msg.topic
    seq_gap = 0
    if topic in last_seq_num and seq != -1:
        seq_gap = seq - last_seq_num[topic] - 1
    if seq != -1:
        last_seq_num[topic] = seq

    return {
        "timestamp": get_iso_now(),
        "topic": topic,
        "client_id": "N/A",
        "seq_num": seq,
        "msg_type": msg_type,
        "status": status,
        "uptime_ms": uptime,
        "payload_len": payload_len,
        "inter_arrival_time": round(inter_arrival, 4),
        "seq_gap": max(0, seq_gap),
        "label": current_label
    }

def log_record(record, session_base):
    """Writes a record to the master dataset and the session log in dual formats."""
    # 1. Master Dual Record (RAW)
    DualLogger.append_raw(record, RAW_DIR, master_base, headers=get_csv_headers())
        
    # 2. Session Dual Record (RESEARCH SESSIONS)
    if session_base:
        DualLogger.append_raw(record, SESSION_DIR, session_base, headers=get_csv_headers())

    # Console Output (minimal for performance)
    sys.stdout.write(f"\r📥 [{record['label'].upper()}] Synchronizing: {record['topic']} | Type: {record['msg_type']}")
    sys.stdout.flush()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Secure handshake complete with Broker at {BROKER}")
        client.subscribe(TOPICS)
        print(f"📡 High-Fidelity Intelligence Sync Active | Mode: {current_label.upper()}")
        print("-" * 50)
    else:
        print(f"❌ Handshake failed: {rc}")

def main():
    global current_label
    import argparse
    parser = argparse.ArgumentParser(description="Professional Telemetry Synchronization Engine")
    parser.add_argument("--label", default="normal", help="Metadata label (e.g. baseline, dos, malware)")
    args = parser.parse_args()
    
    current_label = args.label
    print(BANNER)

    # Session-specific base name
    session_ts = get_timestamp()
    session_base = f"session_{args.label}_{session_ts}"
    print(f"📂 Master Sync Active: {os.path.join(RAW_DIR, master_base)}")
    print(f"📊 Session Trace: {session_base} (+.json/+.csv)")
    print("-" * 50)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Sovereignty_Logger_Hub")
    client.on_connect = on_connect
    
    def on_message_handler(client, userdata, msg):
        record = process_message(msg)
        log_record(record, session_base)
        
    client.on_message = on_message_handler

    try:
        client.connect(BROKER, 1883, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n🛑 Telemetry sync terminated safely. All research traces synchronized.")
    except Exception as e:
        print(f"❌ Engine Error: {e}")

if __name__ == "__main__":
    main()
