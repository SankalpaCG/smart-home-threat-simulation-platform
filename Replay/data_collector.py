import paho.mqtt.client as mqtt
import json
import csv
import time
import os
import math

BROKER_IP = "192.168.21.64"

CURRENT_LABEL = 3
SESSION_NAME = "Replay"
FILE_NAME = f"dataset_{SESSION_NAME}.csv"

MAX_ROWS = 10000
row_count = 0

latency_values = []

HEADERS = [
    "timestamp",
    "src_ip",
    "target_ip",
    "attack_label",
    "attack_type",
    "broker_response_latency_ms",
    "packets_per_second",
    "mqtt_publish_rate",
    "device_heap_free_bytes",
    "result_code",
    "password_length",
    "payload_entropy",
    "auth_attempt_rate",
    "auth_failure_rate",
    "auth_success_rate",
    "unique_passwords_tried",
    "credential_entropy",
    "inter_arrival_mean_ms",
    "inter_arrival_std_ms",
    "consecutive_failures",
    "session_attempt_count",
    "session_failure_rate",
    "latency_zscore",
    "duplicate_payload_rate",
    "msg_timestamp_delta_ms"
]


def calculate_zscore(value, values):
    if len(values) < 2:
        return 0

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_dev = math.sqrt(variance)

    if std_dev == 0:
        return 0

    return round((value - mean) / std_dev, 4)


def on_message(client, userdata, msg):
    global row_count, latency_values

    try:
        start_time = time.time()
        payload = json.loads(msg.payload.decode())

        if payload.get("type") == "AUDIT":
            latency_ms = round((time.time() - start_time) * 1000, 3)
            latency_values.append(latency_ms)

            row = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "src_ip": payload.get("ip", "unknown"),
                "target_ip": BROKER_IP,

                "attack_label": CURRENT_LABEL,
                "attack_type": "replay",

                "broker_response_latency_ms": latency_ms,
                "packets_per_second": payload.get("pps", 0),
                "mqtt_publish_rate": payload.get("mqtt_publish_rate", payload.get("pps", 0)),
                "device_heap_free_bytes": payload.get("heap", 0),

                # Brute force/auth features are zero for replay
                "result_code": 0,
                "password_length": 0,
                "payload_entropy": 0,
                "auth_attempt_rate": 0,
                "auth_failure_rate": 0,
                "auth_success_rate": 0,
                "unique_passwords_tried": 0,
                "credential_entropy": 0,

                # Timing features from ESP32 packet timing
                "inter_arrival_mean_ms": payload.get("inter_arrival_mean_ms", 0),
                "inter_arrival_std_ms": payload.get("inter_arrival_std_ms", 0),

                # Brute-force session features zeroed for replay
                "consecutive_failures": 0,
                "session_attempt_count": 0,
                "session_failure_rate": 0,

                # Collector-side latency z-score
                "latency_zscore": calculate_zscore(latency_ms, latency_values),

                # Replay-specific features
                "duplicate_payload_rate": payload.get("duplicate_payload_rate", 0),
                "msg_timestamp_delta_ms": payload.get("msg_timestamp_delta_ms", 0)
            }

            file_exists = os.path.isfile(FILE_NAME)

            with open(FILE_NAME, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=HEADERS)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)

            row_count += 1

            print(
                f"[{SESSION_NAME.upper()}] Row {row_count}/{MAX_ROWS} | "
                f"PPS: {row['packets_per_second']} | "
                f"DupRate: {row['duplicate_payload_rate']} | "
                f"Delta: {row['msg_timestamp_delta_ms']} ms"
            )

            if row_count >= MAX_ROWS:
                print("\n✅ 10,000 replay rows collected. Stopping collector.")
                client.disconnect()

    except Exception as e:
        print(f"Error: {e}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Final_Collector")
client.on_message = on_message
client.connect(BROKER_IP, 1883)
client.subscribe("shtsp/home/telemetry")
client.loop_forever()