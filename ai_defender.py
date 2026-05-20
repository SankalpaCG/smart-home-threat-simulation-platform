import paho.mqtt.client as mqtt
import json
import joblib
import pandas as pd
import numpy as np
import time
import os

# 1. LOAD THE TRAINED BRAIN
try:
    model = joblib.load("smart_home_ai_27f.pkl")
    scaler = joblib.load("scaler_27f.pkl")
    print("🛡️ AI INTRUSION DETECTION SYSTEM ACTIVE")
    print("Monitoring live IoT traffic for DDoS anomalies...")
except Exception as e:
    print(f"❌ ERROR: Ensure .pkl files are in the folder! {e}")
    exit()

# The 22 features the AI expects (excluding text columns)
FEATURES = [
    "packets_per_second", "mqtt_publish_rate", "broker_response_latency_ms", "device_heap_free_bytes",
    "auth_attempt_rate", "auth_failure_rate", "unique_passwords_tried", 
    "result_code", "password_length", "payload_entropy", "auth_success_rate", "credential_entropy",
    "duplicate_payload_rate", "msg_timestamp_delta_ms", "motion", "arm",
    "inter_arrival_mean_ms", "inter_arrival_std_ms", "consecutive_failures", 
    "session_attempt_count", "session_failure_rate", "latency_zscore"
]

def on_message(client, userdata, msg):
    try:
        start_time = time.time()
        payload = json.loads(msg.payload.decode())
        
        if payload.get("type") == "AUDIT":
            # Map incoming data to our 22 behavioral features
            pps = payload["pps_raw"] * 5
            heap = payload["heap"]
            mot = payload["mot"]
            arm = payload["arm"]
            latency = (time.time() - start_time) * 1000

            # Create a row with all 22 features (fill missing with 0)
            data_dict = {f: 0 for f in FEATURES}
            data_dict.update({
                "packets_per_second": pps,
                "device_heap_free_bytes": heap,
                "motion": mot,
                "arm": arm,
                "broker_response_latency_ms": latency
            })
            
            # AI Prediction
            current_df = pd.DataFrame([data_dict], columns=FEATURES)
            scaled_data = scaler.transform(current_df)
            prediction = model.predict(scaled_data)

            # --- RESULT ---
            if prediction[0] == -1 and pps > 10: # Alert if Anomaly AND traffic is high
                print(f"🚨 [ALERT] DDoS ATTACK DETECTED! | PPS: {pps} | HEAP: {heap}")
            else:
                print(f"✅ [SAFE] SYSTEM HEALTHY | PPS: {pps} | HEAP: {heap}")

    except Exception as e:
        pass

# 2. MQTT SETUP
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Live_AI_Monitor")
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("shtsp/home/telemetry")
client.loop_forever()