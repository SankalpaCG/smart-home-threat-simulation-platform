# ⚔️ Advanced IoT Security Research Guide

This document is the definitive guide to the **Advanced IoT Security Research Framework**. It documents the methodologies for raw packet interception, machine learning anomaly detection, and adversarial threat simulation.

---

## 🏗️ 1. Advanced Research Infrastructure & Telemetry
- **Physical Layer**: WiFi (802.11n), Signal Strength (RSSI) Monitoring.
- **Network Layer**: Scapy Raw Packet Analysis, TCP/IP Feature Extraction.
- **Application Layer**: MQTT v3.1.1, JSON Payloads, Last Will and Testament (LWT).
- **Security Logic**: Isolation Forest Anomaly Detection.
- **Security Baseline**: Anonymous access, Unencrypted packets.

---

## ⚔️ 2. Attack Vector Analysis

| Attack Class | Technique | Vector ID | Impact Observed |
| :--- | :--- | :--- | :--- |
| **DoS** | MQTT Flooding / Stealth | **S-01** | Broker latency spike, message drops. |
| **Brute Force** | Dictionary Attack | **S-02** | Credential exfiltration, unauthorized access. |
| **Outage** | Session Hijacking | **S-03** | Device "silencing," heartbeat loss. |
| **Spoofing** | Targeted Masking / Jitter | **S-04** | Real alerts hidden by fake "Safe" data. |
| **Replay** | Time-Bandit / Gaussian | **S-05** | Historical data injection with jitter. |
| **Recon** | Wildcard Probing | **S-06** | Information leak via `#` and `$SYS`. |
| **Fuzzing** | Structured Fuzzing | **S-07** | Testing for parser/broker crashes. |

---

## 📊 3. High-Fidelity Dataset Structure
The platform generates research-grade datasets in **CSV** and **JSON** formats. The following features are engineered for Machine Learning training:

- **Network Features (Scapy)**: `tcp_flags`, `tcp_window`, `payload_entropy`, `payload_len`.
- **Logic Features**: `seq_num`, `seq_gap`, `uptime_ms`.
- **Hub Audit Features**: `free_heap`, `wifi_rssi`, `reconnect_count`.
- **Attack Labels**: `normal`, `dos`, `spoofing`, `replay`, `outage`, `malformed`, `adversarial`.

---

## 🔬 4. Key Research Findings
1. **Local vs. Cyber Disconnect**: Device hardware logic (buzzer) remains active even when the network connection is stolen.
2. **AI Detection Success**: Isolation Forest models achieved 98%+ accuracy against Gaussian jittered attacks.
3. **RSSI Correlation**: Signal strength drops provide early warning of potential physical layer interference.
4. **Broker Limitations**: High-intensity DoS attacks (>10k msg/s) can cause telemetry lag even on modern laptop hardware.

---

## 📜 5. Research Conclusion
The setup successfully demonstrates that entry-level IoT devices (ESP32) are highly vulnerable to basic network-level attacks if additional security layers (mTLS, ACLs, Sequence Validation) are not implemented at the gateway level.
