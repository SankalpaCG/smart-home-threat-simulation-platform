# Smart Home Threat Simulation Platform

## 🏠 Project Overview

This is a **Capstone Project** focusing on creating an advanced **Smart Home Threat Simulation Platform**. The platform combines real ESP32 hardware with state-of-the-art **Machine Learning Intrusion Prevention Systems (ML-IPS)**. It is designed to act as a comprehensive IoT security environment for generating high-fidelity forensic datasets, training AI classifiers, and actively defending against zero-day IoT threats.

### **Project Vision**
To build a hybrid (virtual + physical) IoT security testing platform that:
1. Simulates real-world smart home attacks (Brute Force, DoS, Replay).
2. Generates pristine, labeled, 20-feature security datasets for research.
3. Employs a Cloud-to-Edge Machine Learning pipeline using Random Forests.
4. Actively defends the network by automatically neutralizing attackers via OS-level firewalls.

---

## 📁 Final Project Structure

```bash
.
├── Security Hub (ESP32 #1)/         # PIR motion detection & Alarm System
├── Security_hub.ino                 # Standard firmware implementation
├── attacks/                         # ⚔️ Sovereignty Research Attack Suite
│   ├── bruteforce_attack.py         # Advanced Credential Stuffing
│   ├── dos_attack_advanced.py       # Volumetric Packet Flooding
│   ├── replay_attack.py             # Temporal Message Re-injection
│   └── normal_traffic_collector.py  # Benign Baseline Telemetry Collector
├── defence/                         # 🛡️ Sovereignty Defence Suite
│   └── live_ml_ips.py               # Active Defense Node (iptables integration)
├── dataset/                         # 📊 ML Research Data & Telemetry
│   ├── logs/                        # Raw CSV/JSON Telemetry
│   ├── feature_engineering.py       # ML Pipeline Aggregation Script
│   ├── combined_ml_dataset.csv      # Merged & Scaled Dataset
│   └── RandomForest_IDS_Training.ipynb # Google Colab Training Notebook
├── docs/                            # 📖 Project Documentation
│   ├── ATTACK_SUITE_GUIDE.md        # How to execute attacks and collect data
│   └── MACHINE_LEARNING_IPS_GUIDE.md# How to train the AI and deploy IPS
├── forensic_utils.py                # 🛠️ Central Forensic Utility 
├── requirements.txt                 # 🐍 Python Dependencies
└── README.md                        # This Project Hub
```

---

## 🏛️ Advanced Research Layer: The Cloud-to-Edge ML-IPS

The platform has transcended standard IDS mechanisms by integrating a **Cloud-to-Edge Machine Learning** pipeline:

1. **Local Data Generation:** Attack scripts simulate zero-day IoT threats against the Mosquitto broker, collecting 20 critical temporal and entropy-based features.
2. **Data Aggregation:** `feature_engineering.py` standardizes the raw logs into a unified dataset.
3. **Cloud Training:** The dataset is processed in **Google Colab** using `RandomForestClassifier`. The model calculates exactly which features identify the threat (e.g., `auth_failure_rate` spikes) and exports `.pkl` model files.
4. **Edge IPS Deployment:** `live_ml_ips.py` runs locally on the gateway. It scales live incoming traffic, predicts the threat category, and automatically executes `iptables DROP` commands to neutralize attackers instantly.

---

## 🎯 Device Specifications

| Device | Purpose | Components | MQTT Topics |
|--------|---------|------------|-------------|
| **Security Hub** | Motion detection & Alarms | ESP32, PIR Sensor, Buzzer | `shtsp/home/security/*` |

*(Note: Peripheral hubs like Climate and Smart Locks were abstracted out to strictly focus the Master's research on the core Authentication & Telemetry pipeline).*

---

## 🚀 Technical Guides

For exact commands and step-by-step instructions for your thesis presentation, please refer to our dedicated documentation guides:

* ⚔️ **[Attack Suite Execution Guide](docs/ATTACK_SUITE_GUIDE.md)**: Contains all Python commands to simulate Brute Force, DoS, and Replay attacks, and collect baseline data.
* 🧠 **[Machine Learning & IPS Guide](docs/MACHINE_LEARNING_IPS_GUIDE.md)**: Details the process of executing `feature_engineering.py`, running the Google Colab training notebook, and activating the Live Active Defense script.

---

## 🤝 Collaboration & Contribution

### **Team Roles (5 Members):**
| Member | Role | Primary Responsibilities |
|--------|------|--------------------------|
| **Sankalpa Ghimire** | **Hardware & Firmware Lead** | ESP32 programming, circuit design, sensor integration, hardware testing. |
| **Deepak Sharma** | **Software & Backend Lead** | MQTT broker setup, API development, data pipeline architecture. |
| **Amir Kumar pachhai** | **Security & Attack Simulation Lead** | Threat modeling, attack vector development, penetration testing. |
| **Sadikshya Dahal** | **Data Science & ML Lead** | Dataset creation, feature engineering, Google Colab Random Forest ML model development. |
| **Shashi Simkhada** | **Frontend & Visualization Lead** | Thesis presentation design, data visualization, real-time alerting UI, documentation. |

---

## 📞 Contact & Support

### **Project Team:**
- **Lead Developer**: Deepak Sharma
- **Advisor**: [Professor Name]
- **Institution**: [Your College/University]

---
**Last Updated**: May 2026  
**Project Status**: **COMPLETE (Active Defense ML-IPS Deployed)**  
*"Building the future of IoT security, one simulation at a time."*