# 🛡️ Smart Home Threat Simulation & ML-IPS Platform

[![Status](https://img.shields.io/badge/Status-Pre--Release-blue.svg)]()
[![ML Pipeline](https://img.shields.io/badge/ML_Engine-Random_Forest-orange.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Node.js%20%7C%20React%20%7C%20Python-green.svg)]()

## 📌 Executive Summary

This repository hosts the **Smart Home Threat Simulation Platform**, an advanced Capstone Project focused on securing the next generation of Internet of Things (IoT) infrastructure. By combining real-world hardware (ESP32) with a state-of-the-art **Machine Learning Intrusion Prevention System (ML-IPS)**, this platform serves as a complete hybrid ecosystem. It generates forensic datasets, trains AI threat classifiers, and autonomously defends against zero-day IoT attacks in real-time using OS-level network intervention.

---

## 🏗️ Project Timeline: From Beginning to End

Our project was executed in a structured, multi-phase agile methodology, transforming a simple concept into an enterprise-grade IoT security platform.

### **Phase 1: Hardware Integration & Network Architecture (Weeks 1-3)**
*   **ESP32 Firmware Development:** We began by engineering a physical "Smart Security Hub" using an ESP32 microcontroller, a PIR motion sensor, and an active buzzer alarm.
*   **MQTT Event Mesh:** We established a centralized Mosquitto MQTT broker running on a virtualized Linux (WSL) environment to handle all bi-directional IoT telemetry.
*   **Baseline Establishment:** We developed a `normal_traffic_collector.py` script to simulate benign, everyday smart home network traffic to establish a pristine behavioral baseline.

### **Phase 2: Offensive Security & Threat Modeling (Weeks 4-6)**
*   **Attack Vector Design:** We theorized and mapped out critical vulnerabilities in standard IoT deployments.
*   **Simulation Suite Development:** We engineered custom Python-based offensive tools to attack our own infrastructure:
    *   **Brute Force Script:** Advanced credential stuffing against the MQTT broker using thousands of dictionary passwords.
    *   **Volumetric DoS Script:** A highly concurrent packet flooding tool designed to overwhelm broker response latency.
    *   **Time-Shifted Replay Script:** A stealthy attack that captures legitimate sensor packets and maliciously re-injects them after a temporal delay to bypass standard authentication.

### **Phase 3: Data Science & AI Threat Detection (Weeks 7-9)**
*   **Forensic Telemetry Pipeline:** We realized standard logs were insufficient for AI, so we engineered a deeply complex network sniffer that extracts **27 distinct statistical features** per packet (including latency z-scores, payload entropy, credential entropy, and inter-arrival standard deviations).
*   **Dataset Generation:** We ran our attack suite for hours against the baseline, generating hundreds of thousands of rows of pristine, labeled `.csv` training data.
*   **Cloud AI Training:** We aggregated the data and utilized Google Colab to train a **Random Forest Classifier**. The AI learned the mathematical thresholds of "normal" vs "malicious" traffic and exported highly optimized `.pkl` inference models.

### **Phase 4: Active Defense & Dashboard Engineering (Weeks 10-12)**
*   **The Active ML-IPS Node:** We bridged the gap between AI and infrastructure by building `live_ml_ips.py`. This script runs continuously at the edge, scaling live traffic against our Random Forest model. Upon detecting an anomaly, it executes immediate OS-level `iptables` DROP commands to neutralize the attacker's IP address.
*   **Enterprise React Dashboard:** We developed a stunning, high-performance command center using Node.js and React. It features real-time Threat Matrix Heatmaps, Volumetric Scatter Plots, and Intervention Logs, allowing us to visualize the AI's decision-making process live.
*   **Environment Automation:** We implemented dynamic IP fetching routines to allow the platform to adapt to changing network conditions seamlessly.

### **Phase 5: Project Finalization (Finishing Next Week)**
As we approach our final defense, we are completing the following:
1.  **Performance Benchmarking:** Final latency tests of the ML-IPS pipeline during simultaneous multi-vector attacks.
2.  **Dataset Publication:** Packaging our curated `.csv` datasets for academic peer review.
3.  **Hardware Syncing:** Final physical tests with the ESP32 hardware hub.
4.  **Academic Deliverables:** Finalizing our thesis paper, presentation slide deck, and UI/UX micro-animations for the defense demonstration.

---



## 📁 Final Project Structure

```bash
.
├── Security Hub (ESP32 #1)/         # PIR motion detection & Alarm System
├── Security_hub.ino                 # Standard firmware implementation
├── dashboard/                       # 🌐 Enterprise React Command Center
│   ├── server.js                    # Node.js Backend & Process Manager
│   └── ui/                          # Vite/React Frontend (Heatmaps, PCAPs)
├── attacks/                         # ⚔️ Sovereignty Research Attack Suite
│   ├── bruteforce_attack.py         # Advanced Credential Stuffing
│   ├── dos_attack_advanced.py       # Volumetric Packet Flooding
│   ├── replay_attack.py             # Temporal Message Re-injection
│   └── normal_traffic_collector.py  # Benign Baseline Telemetry Collector
├── defence/                         # 🛡️ Sovereignty Defence Suite
│   └── live_ml_ips.py               # Active Defense Node (iptables integration)
├── dataset/                         # 📊 ML Research Data & Telemetry
│   ├── logs/                        # Raw CSV/JSON Telemetry (27-Feature Schema)
│   ├── feature_engineering.py       # ML Pipeline Aggregation Script
│   ├── combined_ml_dataset.csv      # Merged & Scaled Dataset
│   └── RandomForest_IDS_Training.ipynb # Google Colab Training Notebook
├── docs/                            # 📖 Project Documentation
│   ├── ATTACK_SUITE_GUIDE.md        # Execution guide for attack simulations
│   └── MACHINE_LEARNING_IPS_GUIDE.md# AI training and deployment guide
├── forensic_utils.py                # 🛠️ Central DualLogger & IP Utility
└── README.md                        # This Project Hub
```

---

## 🎯 Device Specifications

| Device | Purpose | Components | MQTT Topics |
|--------|---------|------------|-------------|
| **Security Hub** | Motion detection & Alarms | ESP32, PIR Sensor, Buzzer | `shtsp/home/security/*` |

*(Note: Peripheral hubs like Climate and Smart Locks were abstracted out to strictly focus the final Capstone research on the core Authentication & Telemetry pipeline).*

---

## 📞 Contact & Support

### **Project Team:**
- **Lead Developer**: Deepak Sharma
- **Advisor**: [Professor Name]
- **Institution**: [Your College/University]

---
**Last Updated**: May 2026  
**Project Status**: **FINALIZING (Active Defense ML-IPS Deployed & UI Polished)**  
*"Building the future of IoT security, one simulation at a time."*
