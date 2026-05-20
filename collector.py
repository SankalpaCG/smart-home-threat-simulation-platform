import paho.mqtt.client as mqtt
import json
import csv
import time
import os
import random

# --- 1. CONFIGURATION ---
FILE_NAME = "master_iot_dataset.csv"
BROKER_IP = "localhost"
TOPIC = "shtsp/home/telemetry" # Ensure this matches ESP32 code

# --- 2. GLOBAL STATE ---
current_label = 0
current_type = "Normal"
row_count = 0

# Fake IPs for DDoS Simulation
BOTNET_IPS = ["192.168.1.5", "10.0.0.45", "172.16.0.12", "192.168.1.100", "8.8.8.8"]

HEADERS = [
    "timestamp", "src_ip", "attack_label", "attack_type", "motion", "arm",
    "auth_attempt_rate", "auth_failure_rate", "unique_passwords_tried",
    "packets_per_second", "mqtt_publish_rate", "broker_response_latency_ms",
    "device_heap_free_bytes", "duplicate_payload_rate", "msg_timestamp_delta_ms"
]

# --- 3. INITIALIZE CSV IMMEDIATELY ---
def initialize_file():
    if not os.path.isfile(FILE_NAME):
        with open(FILE_NAME, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()
        print(f"✅ Created new file: {FILE_NAME}")
    else:
        print(f"📂 Appending to existing file: {FILE_NAME}")

# --- 4. MQTT LOGIC ---
def on_message(client, userdata, msg):
    global current_label, current_type, row_count
    try:
        start_time = time.time()
        payload = json.loads(msg.payload.decode())
        latency_ms = (time.time() - start_time) * 1000

        # Mimic different IPs if in DDoS mode
        source_ip = payload["ip"] if current_label == 0 else random.choice(BOTNET_IPS)

        row = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": source_ip,
            "attack_label": current_label,
            "attack_type": current_type,
            "motion": payload.get("mot", 0),
            "arm": payload.get("arm", 1),
            "auth_attempt_rate": 0,
            "auth_failure_rate": 0,
            "unique_passwords_tried": 0,
            "packets_per_second": payload.get("pps_raw", 0) * 5, 
            "mqtt_publish_rate": 5.0,
            "broker_response_latency_ms": round(latency_ms, 4),
            "device_heap_free_bytes": payload.get("heap", 0),
            "duplicate_payload_rate": 0,
            "msg_timestamp_delta_ms": 0
        }

        with open(FILE_NAME, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writerow(row)
        
        row_count += 1
        # Print update every 10 rows
        if row_count % 10 == 0:
            print(f"📊 [{current_type}] Total: {row_count} | PPS: {row['packets_per_second']} | IP: {source_ip}")

    except Exception as e:
        print(f"⚠️ Parsing Error: {e}. Check if ESP32 is sending JSON.")

# --- 5. START SYSTEM ---
initialize_file()
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Amir_DDoS_Collector")
client.on_message = on_message
client.connect(BROKER_IP, 1883)
client.subscribe(TOPIC)
client.loop_start()

print("\n🎮 DDoS COLLECTION CONTROL")
print("Press [0] for NORMAL | [1] for DDoS | [q] to Quit\n")

while True:
    cmd = input("Switch State: ")
    if cmd == '0':
        current_label, current_type = 0, "Normal"
        print("🟢 RECORDING NORMAL (Label 0)")
    elif cmd == '1':
        current_label, current_type = 1, "DDoS"
        print("🔴 RECORDING DDoS (Label 1)")
    elif cmd == 'q':
        print(f"💾 Final Row Count: {row_count}. Exiting...")
        break

client.loop_stop()