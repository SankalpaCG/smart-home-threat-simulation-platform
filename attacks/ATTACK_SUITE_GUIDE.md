# 🛡️ Sovereignty Research Suite: Advanced IoT Attack Guide

This document defines the professional methodology for evaluating and stressing IoT security frameworks using the **Sovereignty Research Suite**. Every attack vector is designed to mimic high-fidelity adversarial logic, providing rigorous data for Intrusion Detection System (IDS) validation.

---

## 🛠️ Global Framework Pre-requisites

### **1. System Dependencies**
Ensure the host environment is prepared for deep packet inspection and protocol evaluation:
```bash
# Install core capture engine and middleware
sudo apt update
sudo apt install -y libpcap-dev mosquitto mosquitto-clients
```

### **2. Research Context Tools**
For a complete forensic capture, run the **Sovereignty Probe** and **Central Logger** in separate terminals before initiating any simulation:

- **Network Intelligence Probe** (Layer 3/4 Analysis):
  ```bash
  sudo ./venv/bin/python3 defence/sovereign_probe.py
  ```
- **Central Security Logger** (App-Layer Synchronization):
  ```bash
  python3 defence/security_logger.py --label [target_attack_label]
  ```

---

## ⚔️ Multi-Vector Attack Methodologies

### **1. Distributed Denial of Service (DDoS)**
- **Technical Theory**: Exploits the MQTT connection state machine by saturating the broker with high-velocity `PUBLISH` requests, potentially exhausting CPU and memory.
- **Adversarial Logic**: Supports "Stochastic Noise" (randomized payloads) to challenge entropy-based detection.
- **Execution Command**:
  ```bash
  # Stress test with 50 concurrent research nodes
  python3 attacks/dos_attack_advanced.py --clients 50 --duration 60
  ```

### **2. Adversarial Spoofing (Intelligent Mirror)**
- **Technical Theory**: Monitors the broker for legitimate sensor triggers and reacts with a burst of "SAFE" packets to mask a real intrusion in progress.
- **Adversarial Logic**: Context-aware injection is the highest form of reconnaissance-based spoofing.
- **Execution Command**:
  ```bash
  # Mask real alarms with a 100-packet "Safe" burst
  python3 attacks/spoofing_attack.py --mode masking --burst 100
  ```

### **3. Time-Shifted Replay (Gaussian Modeling)**
- **Technical Theory**: Captures a window of valid encrypted telemetry and re-injects it at a later time. 
- **Adversarial Logic**: Uses Gaussian Jitter to mimic human motion variance, making the replayed data statistically similar to the baseline.
- **Execution Command**:
  ```bash
  # Capture for 30s, delay for 15s, then replay
  python3 attacks/replay_attack.py --capture 30 --delay 15
  ```

### **4. Authentication Auditor (Brute Force)**
- **Technical Theory**: Audits the broker's password complexity and lockout policies through high-speed authentication attempts.
- **Execution Command**:
  ```bash
  # Threaded audit against the administrative console
  python3 attacks/bruteforce_attack.py --username admin --threads 10
  ```

### **5. Connectivity Disrupter (Heartbeat Loss)**
- **Technical Theory**: Evaluates the **Last Will and Testament (LWT)** triggers by forcibly hijacking a specific `ClientID` and maintaining silence.
- **Research Impact**: Crucial for testing how the IDS reacts to "Device Offline" or "Silent Malfunction" scenarios.
- **Execution Command**:
  ```bash
  # Perform a 60-second "Silent Hijack" on a Security Hub
  python3 attacks/heartbeat_loss_sim.py --mode silent --duration 60 --target hub_01
  ```

### **6. Identity Recon Probe**
- **Technical Theory**: Rotates through professional identities (e.g., `admin_console`, `root_debug`) to probe for topic leaks and unauthorized wildcard subscriptions (`#`, `$SYS/#`).
- **Execution Command**:
  ```bash
  python3 attacks/rogue_client_attack.py --all
  ```

### **7. Protocol Layer Fuzzer**
- **Technical Theory**: Injects "Poison Payloads" including recursive JSON, integer overflows, and illegal encodings to stress the MQTT broker's parser.
- **Execution Command**:
  ```bash
  python3 attacks/malformed_packet_attack.py
  ```

---

## 📊 Forensic Data Architecture

The platform enforces absolute data traceability by synchronizing every event into synchronized **JSON** (for deep analysis) and **CSV** (for rapid analysis) formats.

| Directory | Data Type | Academic Use |
| :--- | :--- | :--- |
| `dataset/raw/` | Network Telemetry | Primary training data for Anomaly Detection models. |
| `dataset/logs/` | Attack Event Audit | Verification of attack success and timing. |
| `dataset/sessions/` | Structured Reports | High-level summary of research sessions. |

---

> [!IMPORTANT]
> **Adversarial Integrity**: These scripts do not just perform actions—they simulate **strategies**. For a professional research paper, ensure you cross-reference the `raw` network jitter with the `session` summary records.
