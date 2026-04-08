# 🌩️ Advanced Threat Simulation Guide

This guide covers the **Advanced Level** attack simulations for the Smart Home Threat Simulation Platform. These tools are designed to demonstrate sophisticated network-level vulnerabilities and generate high-quality security datasets.

---

## 🛠️ Advanced Toolset Overview

| Attack | Script | Advanced Features |
|--------|--------|-------------------|
| **Brute Force** | `bruteforce_attack.py` | Multithreading, JSON Logging, Expanded Wordlist |
| **DoS Flood** | `dos_attack_advanced.py` | High-throughput, Multi-client simulation, Success Metrics |
| **MitM (ARP)** | `mitm_attack_advanced.py` | ARP Spoofing, Packet Interception, Target redirection |

---

## 1. 🔑 Advanced Brute-Force
Located at: `attacks/bruteforce_attack.py`

### What makes it advanced?
- **Multithreading**: Uses concurrent threads to test multiple passwords simultaneously, significantly reducing the attack time.
- **Dataset Integration**: Logs results to `dataset/logs/` in JSON format, capturing metadata for research and machine learning training.

### Usage
```bash
python attacks/bruteforce_attack.py --threads 10 --log
```

---

## 2. 🔥 Advanced DoS (Denial of Service)
Located at: `attacks/dos_attack_advanced.py`

### What makes it advanced?
- **High-Throughput**: Simulates many different "attack clients" at once to stress the MQTT broker beyond a single connection's limit.
- **Customizable Stress**: Tunable message rates per second to fine-tune the impact on the broker.

### Usage
```bash
python attacks/dos_attack_advanced.py --clients 50 --duration 60 --log
```

---

## 3. 🎯 Advanced Man-in-the-Middle (MitM)
Located at: `attacks/mitm_attack_advanced.py`

### What makes it advanced?
- **Network-Level Interception**: Unlike basic MitM simulations, this script performs real **ARP Cache Poisoning**. It tricks the ESP32 into thinking the attacker machine is the gateway/broker.
- **Transparent Interception**: Uses `Scapy` to sniff packets in transit. This allows for observing (and modifying) traffic without the device knowing it's being watched.

### Prerequisites
- **Scapy Library**: `pip install scapy`
- **Root Privileges**: Network-level manipulation requires `sudo`.
- **IP Forwarding**: The script automatically enables forwarding so the device doesn't lose internet/local connectivity.

### Usage
```bash
sudo python attacks/mitm_attack_advanced.py --target 192.168.1.50 --gateway 192.168.1.1
```

---

## 📊 Dataset Creation for Research
All advanced scripts support the `--log` flag. These logs are stored in:
`smart-home-threat-simulation-platform/dataset/logs/`

### Dataset Schema
```json
{
    "timestamp": "2026-04-08T12:59:42Z",
    "attack_type": "dos_flood",
    "target": "192.168.1.100:1883",
    "metrics": {
        "total_messages": 50000,
        "avg_rate": 833.33
    }
}
```

---

## 🛡️ Professional Defense Recommendations
1. **Network Segmentation**: Isolate IoT devices on a dedicated VLAN.
2. **Dynamic ARP Inspection (DAI)**: Prevent ARP spoofing at the switch level.
3. **MQTT TLS (MQTTS)**: Encrypt all traffic to render MitM interception useless.
4. **Intrusion Detection Systems (IDS)**: Use tools like Suricata to monitor for traffic spikes and ARP poisoning attempts.

> [!CAUTION]
> These tools are powerful and should only be used in isolated laboratory environments. Unauthorized use on real networks is illegal and unethical.
