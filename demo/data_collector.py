import paho.mqtt.client as mqtt
import json
import csv
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LABELED_DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset", "labeled")

# ==========================================
# 1. SESSION CONFIGURATION (Change these!)
# ==========================================
# 0: Normal, 1: DoS, 2: BruteForce, 3: Malformed
CURRENT_LABEL = 1           
SESSION_NAME = "DoS"      # Name of the file: dataset_normal.csv
BROKER_IP = "localhost"
TOPIC = "shtsp/home/telemetry"

os.makedirs(LABELED_DATASET_DIR, exist_ok=True)
FILE_NAME = os.path.join(LABELED_DATASET_DIR, f"dataset_{SESSION_NAME}.csv")

def on_message(client, userdata, msg):
    try:
        # Decode JSON from ESP32
        payload = json.loads(msg.payload.decode())
        
        if payload["type"] == "AUDIT":
            pps = payload["pps"]
            heap = payload["heap"]
            mot = payload["mot"]
            arm = payload["arm"]
            
            # Create file with headers if it doesn't exist
            file_exists = os.path.isfile(FILE_NAME)
            with open(FILE_NAME, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["pps", "heap", "motion", "arm", "label"])
                
                # Save the 4 features + the target label
                writer.writerow([pps, heap, mot, arm, CURRENT_LABEL])
            
            status_text = "NORMAL" if CURRENT_LABEL == 0 else "ATTACK"
            print(f"[{status_text}] Saved -> PPS: {pps} | Heap: {heap} | Mot: {mot} | Arm: {arm}")

    except Exception as e:
        print(f"Error parsing JSON: {e}")

# Setup MQTT Client (Callback Version 1 for compatibility)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Data_Collector_Node")
client.on_message = on_message
client.connect(BROKER_IP, 1883)
client.subscribe(TOPIC)

print(f"📡 COLLECTOR STARTING: Recording session '{SESSION_NAME}' (Label: {CURRENT_LABEL})")
print(f"📂 Saving to: {FILE_NAME}")
client.loop_forever()
