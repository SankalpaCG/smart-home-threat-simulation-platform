# 🔐 Replay Attack Simulation & Detection Guide

## Overview

This directory now contains **replay attack simulation and detection tools** for your IoT security lab. These scripts complement your existing DoS attack simulator.

---

## 📋 What is a Replay Attack?

A **replay attack** is when an attacker:
1. **Captures** legitimate network traffic or data packets
2. **Records** the captured packets
3. **Replays** them later to trick the system into:
   - Accepting fraudulent transactions
   - Triggering unintended actions
   - Bypassing authentication
   - Causing unauthorized state changes

### Example Scenario
- Attacker captures legitimate unlock command: `{"arm": 0, "action": "unlock"}`
- Attacker sends it multiple times at different times
- System doesn't validate timestamps/freshness
- Doors unlock repeatedly without authorization

---

## 🎯 New Files Created

### 1. `replay_attack.py` - Attack Simulator
Simulates a replay attack by reading legitimate traffic from CSV and replaying it back.

**Features:**
- Loads captured packets from CSV dataset
- Multiple attack modes:
  - **Single Replay**: One-time replay of all packets
  - **Continuous Replay**: Multiple cycles of replay
  - **Random Replay**: Scattered replay to look legitimate
  - **Sequential Mode**: All attacks in order

**How it works:**
```
1. Reads dataset_Normal.csv
2. Extracts packets: [pps, heap, motion, arm]
3. Publishes them back to MQTT topic
4. System receives seemingly legitimate traffic
```

**Usage:**
```bash
python replay_attack.py
```

Then select attack mode 1-4 and watch the packets get replayed!

---

### 2. `replay_detector.py` - Detection Tool
Analyzes datasets to detect if replay attacks have occurred.

**Detection Methods:**

#### Detection #1: Duplicate Packet Analysis
- Looks for identical consecutive packets
- Replay attacks often have many duplicates
- Legitimate systems have variation

**What it detects:**
```
Example: 
PPS=0, Heap=234188, Motion=0, Arm=1  (Packet 1)
PPS=0, Heap=234188, Motion=0, Arm=1  (Packet 2) ← IDENTICAL!
PPS=0, Heap=234188, Motion=0, Arm=1  (Packet 3) ← SUSPICIOUS!
```

#### Detection #2: Pattern Repetition
- Finds sequences of packets that repeat
- Looks for 5-packet patterns that appear multiple times
- Real systems have variable patterns

#### Detection #3: Statistical Analysis
- Calculates variance in PPS and heap values
- **Low variance = replay attack** (all values identical)
- **High variance = legitimate** (values change naturally)

**Example:**
```
Normal System:
  PPS: Min=0, Max=50, Avg=15.2, Variance=120
  → Natural variation

Replay Attack:
  PPS: Min=0, Max=0, Avg=0, Variance=0
  → All identical (obviously replayed!)
```

#### Detection #4: Timing Anomalies
- Detects suspicious packet timing patterns
- Replayed packets often arrive in bursts
- Legitimate packets have natural delays

**Usage:**
```bash
python replay_detector.py
```

Will analyze both `dataset_Normal.csv` and `dataset_DoS.csv`

---

## 📊 Analysis of Current Datasets

Your current `dataset_Normal.csv` has:
```
pps,heap,motion,arm,label
0,234188,0,1,0
0,234188,0,1,0
0,234188,0,1,0
```

**Detection Analysis:**
- ✅ Perfect duplicate detection: **EVERY packet is identical**
- ✅ Pattern repetition: Yes (same pattern repeats)
- ✅ Statistical variance: **ZERO** (suspicious!)
- ⚠️ All indicators suggest possible replay scenario

---

## 🔄 Workflow: Attack → Detect → Defend

### Step 1: Run Legitimate Collector
```bash
# Run ESP32 or simulator
# Collects normal data into dataset_Normal.csv
python data_collector.py
```

### Step 2: Perform Replay Attack
```bash
python replay_attack.py
# Select option 1: Single Replay
# Watch collector window for spike in packets
```

### Step 3: Detect the Attack
```bash
python replay_detector.py
# Should show high risk indicators
```

### Step 4: Compare with Other Attacks
```bash
# After DoS attack:
python dos_attack.py &
# Let collector run
# Then analyze:
python replay_detector.py
```

---

## 🛡️ Defense Strategies

### 1. **Timestamps & Freshness**
```python
# Add timestamp verification
if current_time - packet_timestamp > 30_seconds:
    reject_packet()  # Too old, likely replay
```

### 2. **Sequence Numbers**
```python
# Track expected sequence
expected_seq = last_seq + 1
if packet_seq != expected_seq:
    reject_packet()  # Out of order, likely replay
```

### 3. **Nonce (Number Used Once)**
```python
# Server sends random value
# Client must include in response
# Each nonce only valid once
seen_nonces = set()
if nonce in seen_nonces:
    reject_packet()  # Already used, replay!
seen_nonces.add(nonce)
```

### 4. **Message Authentication Code (MAC)**
```python
# HMAC prevents modification AND replay
import hmac
correct_mac = hmac.new(secret_key, packet_data, hashlib.sha256)
if mac != correct_mac:
    reject_packet()  # Corrupted or replayed
```

### 5. **TLS/SSL with Session IDs**
- MQTT can use TLS
- Session IDs prevent replay attacks
- Each session has unique ID

---

## 🔧 Integration with Your Project

### Add to `data_collector.py`:
```python
# Add timestamp tracking
import time
from collections import deque

recent_packets = deque(maxlen=100)

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    current_packet = (payload["pps"], payload["heap"], payload["mot"], payload["arm"])
    
    # Check for replay (identical to recent packet)
    if current_packet in recent_packets:
        print(f"🚨 REPLAY DETECTED: {current_packet}")
        # Could mark as attack instead of normal
    
    recent_packets.append(current_packet)
    # ... rest of code
```

### Add to `Security_hub.ino`:
```cpp
// ESP32 code: Add sequence number
int expected_sequence = 0;

void handle_message(JsonDocument msg) {
    if (msg["seq"] != expected_sequence) {
        Serial.println("REPLAY ATTACK DETECTED!");
        return;  // Reject
    }
    expected_sequence++;
    // Process legitimate message
}
```

---

## 📈 Attack Scenarios to Test

### Scenario 1: Basic Replay
```bash
python replay_attack.py
# Select option 1 (Single Replay)
# Result: All captured packets sent again
```

### Scenario 2: Continuous Replay (More Stealthy)
```bash
python replay_attack.py
# Select option 2 (Continuous, 3 cycles)
# Result: Repeated cycles might fool weak detection
```

### Scenario 3: Random Replay (Very Stealthy)
```bash
python replay_attack.py
# Select option 3 (Random Replay)
# Result: Packets sent randomly, harder to detect
```

### Scenario 4: Combined Attack
```bash
# Run DOS attack
python dos_attack.py &

# Simultaneously run replay attack
python replay_attack.py
# Select option 4 (All attacks)

# Detection becomes harder with combined attacks!
```

---

## 🧪 Detection Testing

### Test Detection on Normal Data:
```bash
python replay_detector.py
# Analyzes dataset_Normal.csv
# Should show: LOW RISK (if truly normal)
```

### Test Detection on DoS Data:
```bash
python replay_detector.py
# Analyzes dataset_DoS.csv
# Should show: MEDIUM RISK (different pattern)
```

### Test Detection on Replayed Data:
```bash
# 1. Run replay attack and collect data
python replay_attack.py &
python data_collector.py  # With CURRENT_LABEL = 3 (Replay)

# 2. Analyze the collected data
python replay_detector.py
# Should show: HIGH RISK
```

---

## 🔬 Comparison: All Attack Types

| Attack Type | Method | Detection | Impact |
|------------|--------|-----------|--------|
| **Normal** | Natural device behavior | Varied patterns, High variance | Baseline |
| **DoS** | Flood with junk packets | High PPS, Low heap, Large payload | Crashes device |
| **Replay** | Resend captured legitimate packets | Duplicate patterns, Zero variance | Unauthorized actions |
| **Brute Force** | Try many combinations | High error rate, Failed attempts | Account lockout |
| **Malformed** | Send invalid JSON/data | Parse errors, Invalid format | Input validation bypass |

---

## 📝 MQTT Topics Used

- **Telemetry (Normal)**: `shtsp/home/telemetry`
  - Legitimate sensor data
  - Normal device reporting

- **Command (Attack)**: `shtsp/home/security/cmd`
  - DoS attack targets this
  - Replay could target this too

- **Audit**: `shtsp/home/telemetry` (type: AUDIT)
  - System monitoring
  - Both attacks recorded here

---

## 🚀 Quick Start

```bash
# Install MQTT (if not already)
# Windows: Download from https://mosquitto.org
# Or: choco install mosquitto

# Terminal 1: Start MQTT Broker
mosquitto

# Terminal 2: Start data collector (Normal mode)
python data_collector.py

# Terminal 3: Run replay attack
python replay_attack.py
# Choose option: 1 (Single Replay)

# Terminal 4: Analyze results
python replay_detector.py

# Results will show detection analysis
```

---

## 📚 References

- OWASP Replay Attack: https://owasp.org/www-community/attacks/Replay_attack
- MQTT Security: https://mosquitto.org/man/mqtt-7.html
- Timestamp Validation: https://en.wikipedia.org/wiki/Freshness_(cryptography)
- Nonce: https://en.wikipedia.org/wiki/Cryptographic_nonce

---

## ⚠️ Educational Note

These tools are for **security research and education only**. They demonstrate:
- How attacks work
- How to detect them
- How to defend against them

Use responsibly in authorized environments only!

---

Created: 2026-04-27
Security Hub Project - IoT Attack Simulation & Detection Lab
