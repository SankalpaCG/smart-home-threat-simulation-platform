# 🛡️ Sovereignty Defence Suite: Intelligence & Mitigation Guide

This document defines the research-grade methodology for network monitoring, anomaly detection, and automated threat mitigation using the **Sovereignty Defence Suite**. These tools provide the foundational ground truth required for academic IoT security validation.

---

## 🏗️ The Defence Stack Architecture

The suite operates as a multi-layer sentinel system, synchronizing network-layer intelligence with application-layer ground truth.

### **1. Sovereignty Network Probe (Layer 3/4 DPI)**
- **Technical Theory**: Performs **Deep Packet Inspection (DPI)** at the transport layer, extracting features such as TCP flags, window size, and payload entropy.
- **Forensic output**: Generates the `network_intelligence.csv/json` master files.
- **Execution**:
  ```bash
  # Must be run with elevated privileges for raw socket access
  sudo ./venv/bin/python3 defence/sovereign_probe.py
  ```

### **2. Central Telemetry Logger (App-Layer Sync)**
- **Technical Theory**: Acts as the "Ground Truth" engine, subscribing to all MQTT topics and calculating inter-arrival times and sequence gaps.
- **Forensic output**: Synchronizes each session into a unique JSON/CSV pair in `dataset/sessions/`.
- **Execution**:
  ```bash
  python3 defence/security_logger.py --label [normal_or_attack_type]
  ```

### **3. Anomaly Detection Engine (IDS)**
- **Technical Theory**: Utilizes an **Isolation Forest** (Unsupervised Learning) model to detect statistical outliers in network traffic patterns.
- **Research Logic**: Evaluates entropy and window size fluctuations to identify potentially malicious deviations from the baseline.
- **Execution**:
  ```bash
  # Requires a baseline in network_intelligence.csv to start
  python3 defence/sovereign_ids.py
  ```

### **4. Sovereign Guard (IPS/Mitigation)**
- **Technical Theory**: An automated response engine that monitors the intelligence trace for critical thresholds (e.g., volumetric DDoS spikes).
- **Mitigation Action**: Dispatches **Lockdown Commands** to the IoT nodes and records a forensic audit of every intervention.
- **Execution**:
  ```bash
  python3 defence/sovereign_guard.py
  ```

---

## 📊 Holistic Forensic Integrity

The Sovereignty Framework is unique in its **Redundant Forensic Capability**. Every tool in the defence stack logs its own audit trail, allowing researchers to correlate the **Trigger** (Probe), the **Detection** (IDS), and the **Reaction** (Guard).

### **Forensic Audit Trails**
| Directory | Audit Log | Primary Research Value |
| :--- | :--- | :--- |
| `dataset/raw/` | `network_intelligence` | Baseline for ML training and model evaluation. |
| `dataset/logs/` | `ids_audit_trail` | Validates model accuracy (False Positives/Negatives). |
| `dataset/logs/` | `guard_mitigation_audit` | Measures responsiveness and mitigation latency. |
| `dataset/sessions/` | `session_audit_*` | Human-readable trace of the entire research event. |

---

> [!IMPORTANT]
> **Academic Integrity**: For valid research, always collect a minimum of 5 minutes of "Normal" baseline data before activating the IDS Anomaly Detection engine. This ensures the Isolation Forest model has a clean representation of legitimate traffic patterns.
