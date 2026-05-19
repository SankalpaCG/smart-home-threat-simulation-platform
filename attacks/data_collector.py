"""
Data Collector — Replay Attack Session Logger
==============================================
Subscribes to the Security Hub's AUDIT topic and logs telemetry to CSV
for ML training / forensic review.

Labels:
    0 = Normal
    1 = DoS
    2 = Replay
    3 = Brute Force
    4 = MitM / Spoofing

Usage:
    python attacks/data_collector.py
    Edit CURRENT_LABEL and SESSION_NAME before each capture session.
"""

import paho.mqtt.client as mqtt
import json
import csv
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- SESSION SETTINGS ---
# Change these before each capture session to match the attack being recorded
CURRENT_LABEL = 2        # 0:Normal  1:DoS  2:Replay  3:BruteForce  4:Spoof
SESSION_NAME  = "Replay"
BROKER_IP     = os.getenv("MQTT_BROKER_LOCAL", "localhost")
PORT          = int(os.getenv("MQTT_PORT", "1883"))

# Output file (placed next to this script for easy access)
FILE_NAME = os.path.join(os.path.dirname(__file__), f"dataset_{SESSION_NAME}.csv")

# Columns — aligned with the actual AUDIT payload from Security_hub.ino
# ESP32 audit fields: free_heap, wifi_rssi, reconnects, lockdown,
#                     dos_pkts, spoofs, hijacks, timestamp (millis)
HEADERS = [
    "timestamp",       # wall-clock time of this log entry
    "free_heap",       # ESP32 free heap bytes
    "wifi_rssi",       # WiFi signal strength (dBm)
    "reconnects",      # MQTT reconnect counter
    "lockdown",        # bool — hub in lockdown?
    "dos_pkts",        # DoS packet count in current window
    "spoofs",          # spoofing attempt counter
    "hijacks",         # external LOCKDOWN command counter
    "uptime_ms",       # millis() on ESP32
    "seq_num",         # message sequence number (for replay gap detection)
    "label"            # attack label for ML training
]

# Topic the Security Hub publishes AUDIT messages to
AUDIT_TOPIC = os.getenv("MQTT_TOPIC_SECURITY_AUDIT", "shtsp/home/security/audit")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        # Only process AUDIT-type messages from the hub
        if payload.get("type") != "AUDIT":
            return

        row = {
            "timestamp":  time.strftime("%Y-%m-%d %H:%M:%S"),
            "free_heap":  payload.get("free_heap", -1),
            "wifi_rssi":  payload.get("wifi_rssi", 0),
            "reconnects": payload.get("reconnects", 0),
            "lockdown":   int(payload.get("lockdown", False)),
            "dos_pkts":   payload.get("dos_pkts", 0),
            "spoofs":     payload.get("spoofs", 0),
            "hijacks":    payload.get("hijacks", 0),
            "uptime_ms":  payload.get("timestamp", 0),   # ESP32 uses "timestamp" for millis()
            "seq_num":    payload.get("seq", -1),
            "label":      CURRENT_LABEL
        }

        file_exists = os.path.isfile(FILE_NAME)
        with open(FILE_NAME, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

        print(
            f"[{SESSION_NAME.upper()}] heap={row['free_heap']}B  "
            f"rssi={row['wifi_rssi']}dBm  "
            f"dos={row['dos_pkts']}  spoofs={row['spoofs']}  "
            f"hijacks={row['hijacks']}  lock={bool(row['lockdown'])}"
        )

    except json.JSONDecodeError:
        print(f"[WARN] Non-JSON payload on {msg.topic}: {msg.payload[:60]}")
    except Exception as e:
        print(f"[ERROR] {e}")


print(f"[DATA_COLLECTOR] Session: {SESSION_NAME}  Label: {CURRENT_LABEL}")
print(f"[DATA_COLLECTOR] Broker:  {BROKER_IP}:{PORT}")
print(f"[DATA_COLLECTOR] Topic:   {AUDIT_TOPIC}")
print(f"[DATA_COLLECTOR] Output:  {FILE_NAME}")
print("-" * 60)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Data_Collector")
client.on_message = on_message
client.connect(BROKER_IP, PORT)
client.subscribe(AUDIT_TOPIC)
client.loop_forever()