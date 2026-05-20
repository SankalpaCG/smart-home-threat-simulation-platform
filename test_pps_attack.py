import paho.mqtt.client as mqtt
import time

# --- Configuration ---
BROKER_IP = "localhost"
TARGET_TOPIC = "shtsp/home/security/cmd"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Sensitivity_Tester")
client.connect(BROKER_IP, 1883)
client.loop_start()

print("🧪 AI SENSITIVITY TESTER")
print("-----------------------")

try:
    while True:
        pps_target = input("\nEnter target PPS (e.g., 10, 50, 100) or 'q' to quit: ")
        if pps_target.lower() == 'q':
            break
            
        pps = float(pps_target)
        if pps <= 0: continue
        
        # Calculate sleep time (1 / PPS)
        delay = 1.0 / pps
        
        print(f"🚀 Launching attack at {pps} PPS... Press Ctrl+C to change speed.")
        try:
            while True:
                client.publish(TARGET_TOPIC, "SENSITIVITY_TEST_DATA")
                time.sleep(delay)
        except KeyboardInterrupt:
            print("\nPaused.")
            continue

except Exception as e:
    print(f"Error: {e}")

client.loop_stop()
client.disconnect()