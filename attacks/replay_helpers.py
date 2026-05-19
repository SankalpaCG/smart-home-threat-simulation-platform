import csv
import os
import time

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Load environment variables once for all replay modules
load_dotenv()


def load_replay_config():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_root = os.path.join(project_root, "app", "dataset")

    return {
        "broker_ip": os.getenv("MQTT_BROKER_LOCAL", "localhost"),
        "cmd_topic": os.getenv("MQTT_TOPIC_SECURITY_CMD", "shtsp/home/security/cmd"),
        "audit_topic": os.getenv("MQTT_TOPIC_SECURITY_AUDIT", "shtsp/home/security/audit"),
        "port": int(os.getenv("MQTT_PORT", "1883")),
        "project_root": project_root,
        "dataset_root": dataset_root,
    }


def create_mqtt_client(client_id, on_message=None):
    client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    if on_message is not None:
        client.on_message = on_message
    return client


def connect_and_start(client, host, port):
    client.connect(host, port)
    client.loop_start()


def stop_and_disconnect(client):
    client.loop_stop()
    client.disconnect()


def publish_payloads(client, topic, payloads, delay=0.5):
    for i, payload in enumerate(payloads, start=1):
        client.publish(topic, payload)
        print(f"[{i}] Published payload: {payload}")
        time.sleep(delay)


def resolve_dataset_path(dataset_name, dataset_root):
    if os.path.isabs(dataset_name):
        return dataset_name
    return os.path.join(dataset_root, dataset_name)


def load_dataset(dataset_name, dataset_root, payload_column):
    dataset_path = resolve_dataset_path(dataset_name, dataset_root)
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    with open(dataset_path, newline="", encoding="utf-8", errors="replace") as file:
        reader = csv.DictReader(file)
        if payload_column not in reader.fieldnames:
            raise ValueError(
                f"Column '{payload_column}' not found in dataset. Available columns: {reader.fieldnames}"
            )
        return [row[payload_column] for row in reader if row.get(payload_column)]
