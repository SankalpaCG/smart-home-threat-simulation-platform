import paho.mqtt.client as mqtt
import json
import joblib
import pandas as pd
import numpy as np
import tkinter as tk
from threading import Thread
import warnings

# 1. SETUP & MODEL LOAD
warnings.filterwarnings("ignore")
model = joblib.load("smart_home_ai_27f.pkl")
scaler = joblib.load("scaler_27f.pkl")

# 2. GUI WINDOW SETUP
root = tk.Tk()
root.title("Smart Home AI - Intrusion Detection")
root.geometry("500x350")

status_label = tk.Label(root, text="WAITING FOR DATA", font=("Arial", 22, "bold"), fg="white", bg="gray", width=30, height=4)
status_label.pack(pady=20)

metrics_text = tk.StringVar()
metrics_text.set("PPS: 0 | HEAP: 0")
info_label = tk.Label(root, textvariable=metrics_text, font=("Arial", 14))
info_label.pack(pady=10)

# 3. AI & MQTT LOGIC
FEATURES = ["packets_per_second", "device_heap_free_bytes", "broker_response_latency_ms", "motion", "arm",
            "auth_attempt_rate", "auth_failure_rate", "unique_passwords_tried", "result_code", "password_length",
            "payload_entropy", "auth_success_rate", "credential_entropy", "duplicate_payload_rate", 
            "msg_timestamp_delta_ms", "inter_arrival_mean_ms", "inter_arrival_std_ms", "consecutive_failures", 
            "session_attempt_count", "session_failure_rate", "latency_zscore"]

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        if payload.get("type") == "AUDIT":
            pps = payload["pps_raw"] * 5
            heap = payload["heap"]
            
            # Map features for AI
            data_dict = {f: 0 for f in FEATURES}
            data_dict.update({"packets_per_second": pps, "device_heap_free_bytes": heap, "motion": payload["mot"], "arm": payload["arm"]})
            
            # Predict
            current_df = pd.DataFrame([data_dict], columns=FEATURES)
            scaled = scaler.transform(current_df)
            pred = model.predict(scaled)

            # Update UI
            if pred[0] == -1 and pps > 10:
                status_label.config(text="🚨 DDoS ATTACK DETECTED!", bg="red")
            else:
                status_label.config(text="✅ SYSTEM HEALTHY", bg="green")
            
            metrics_text.set(f"Packet Rate: {pps} PPS | Free RAM: {heap} bytes")
    except: pass

def start_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "GUI_Defender")
    client.on_message = on_message
    client.connect("localhost", 1883)
    client.subscribe("shtsp/home/telemetry")
    client.loop_forever()

# Start MQTT in background so GUI doesn't freeze
Thread(target=start_mqtt, daemon=True).start()
root.mainloop()