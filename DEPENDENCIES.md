# 🛠️ Project Dependencies & Installation Guide

This document outlines all software and library requirements for the **IoT Security Research Platform**. Follow these instructions to set up the environment for both the Python-based research framework and the ESP32 firmware.

---

## 🐍 1. Python Analysis Framework (Linux/WSL)

The research framework (Network Probe, IPS, Analysis Engine) requires Python 3.10+ and several high-fidelity libraries.

### **Pre-requisites (System Level)**
If you are on Ubuntu/WSL, install the following required system tools:
```bash
sudo apt update
sudo apt install -y python3-venv python3-pip mosquitto mosquitto-clients libpcap-dev
```

### **Virtual Environment Setup**
It is highly recommended to use a virtual environment to keep your system clean:
```bash
# Create the environment
python3 -m venv venv

# Activate the environment
source venv/bin/activate

# Install all research dependencies
pip install -r requirements.txt
```

---

## 🔌 2. ESP32 Firmware Dependencies (Arduino IDE)

The **Security Hub** firmware requires specific libraries to handle MQTT communication and JSON parsing.

### **Required Libraries**
1.  **PubSubClient** (by Nick O'Leary): Handles MQTT connectivity.
2.  **ArduinoJson** (by Benoit Blanchon): Required for high-fidelity forensic logging.

### **How to Install (Arduino IDE)**
1.  Open **Arduino IDE**.
2.  Navigate to `Sketch` -> `Include Library` -> `Manage Libraries...`
3.  In the search bar, type **"PubSubClient"** and click **Install**.
4.  Search for **"ArduinoJson"** and click **Install** (use the latest version).

### **How to Install (VS Code)**
If you are using **VS Code with the Arduino Extension**:
1.  Press `Ctrl+Shift+P` and type **"Arduino: Board Config"** to verify your ESP32 board.
2.  Open the **Library Manager** view in the sidebar.
3.  Search and install the libraries mentioned above.
4.  Ensure your `c_cpp_properties.json` includes the library paths (usually auto-detected).

---

## 📡 3. Middleware (MQTT Broker)

The platform requires a centralized **Mosquitto** broker to handle intelligence traces.

- **Linux**: Use the command in Section 1.
- **Windows**: Download and install the official [Mosquitto Binary](https://mosquitto.org/download/).
- **Configuration**: Ensure `allow_anonymous true` and `listener 1883 0.0.0.0` are set for research purposes.

---

## 📊 Summary Table
| Dependency | Type | Purpose | Installation Location |
| :--- | :--- | :--- | :--- |
| `scapy` | Python | Raw Packet Sniffing | `venv` |
| `scikit-learn` | Python | Anomaly Detection | `venv` |
| `pandas` | Python | Data Analysis | `venv` |
| `paho-mqtt` | Python | Security Research | `venv` |
| `libpcap-dev` | System (Linux) | Packet Capture Engine | Host OS |
| `PubSubClient` | Arduino | MQTT Signaling | Local IDE |
| `ArduinoJson` | Arduino | Forensic Logging | Local IDE |

---

> [!IMPORTANT]
> **Scapy Permissions**: The `sovereign_probe.py` script requires raw socket access. In Linux, you must run it with `sudo` or grant cap_net_raw privileges to your Python binary.
