# ⚔️ Sovereignty Research: Complete Attack Suite & Dashboard Execution Guide

This comprehensive guide contains the exact, working commands required to execute the IoT threat simulations, launch the React enterprise dashboard, and manage the background AI defense engine for the Master's Capstone project. 

All scripts are specifically engineered to extract the **27 crucial machine learning features** required by our Random Forest classifier.

---

## 🛠️ System Prerequisites & Dependencies

Before running any commands, ensure your environment is fully prepared.

1. **Python Environment (Backend & ML):**
   You must activate the virtual environment and ensure all dependencies are installed.
   ```bash
   cd /home/pirator/smart-home-threat-simulation-platform
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   *Required packages: `paho-mqtt`, `scikit-learn`, `pandas`, `requests`.*

2. **Node.js Environment (Dashboard Backend):**
   The API server that manages the PCAP files and attack subprocesses.
   ```bash
   cd /home/pirator/smart-home-threat-simulation-platform/dashboard
   npm install
   ```

3. **React/Vite Environment (Dashboard UI):**
   The frontend user interface.
   ```bash
   cd /home/pirator/smart-home-threat-simulation-platform/dashboard/ui
   npm install
   ```

---

## 🌐 Launching the Enterprise Dashboard

To run the full Command Center, you need to launch three separate components in **three different terminal windows**.

### Terminal 1: The Active Defense ML-IPS Engine
This is the "Brain" of the platform. It runs continuously, scanning the network and actively updating the dashboard.
```bash
cd /home/pirator/smart-home-threat-simulation-platform
sudo venv/bin/python3 defence/live_ml_ips.py
```
*(Note: `sudo` is strictly required because this script actively modifies Linux OS `iptables` firewall rules to block attackers).*

### Terminal 2: The Node.js API Backend
This server handles the API requests from the UI and spawns the attack scripts in the background.
```bash
cd /home/pirator/smart-home-threat-simulation-platform/dashboard
sudo $(which node) server.js
```
*(Note: `sudo` is required here because the backend uses `tcpdump` to capture secure forensic PCAP network files).*

### Terminal 3: The React/Vite Frontend
This serves the actual web interface.
```bash
cd /home/pirator/smart-home-threat-simulation-platform/dashboard/ui
npm run dev
```
**Access the Dashboard:** Open your browser and navigate to `http://localhost:5173`.

---

## ⚔️ The Attack Suite: Manual Execution

While the Dashboard allows you to click buttons to launch attacks automatically, you can also run these highly advanced scripts manually from the terminal for deep forensic analysis. 

All attack scripts automatically fetch your current WSL IP address, so you do **not** need to hardcode it.

### 1. Baseline Telemetry Collection (Normal Traffic)
Before simulating any attack, collect a baseline of what healthy IoT traffic looks like. The Random Forest model needs this to understand the difference between normal behavior and an attack.

**Command (10 Minute Baseline):**
```bash
cd /home/pirator/smart-home-threat-simulation-platform
python3 attacks/normal_traffic_collector.py --broker 192.168.21.165 --username admin --password "iot@secure99" --duration 600 --phase pre_attack
```
* **Output:** Generates a 27-feature CSV in `dataset/logs/` proving benign behavior.

### 2. Advanced Credential Stuffing (Brute Force)
Simulates a highly aggressive, multi-threaded password spraying attack against the MQTT broker. It calculates payload entropy and credential failure rates.

**Command (10,000 Dictionary Attack - Fast):**
```bash
cd /home/pirator/smart-home-threat-simulation-platform
python3 attacks/bruteforce_attack.py --broker 192.168.21.165 --userlist dataset/userlist_bruteforce.txt --file dataset/wordlist_10k.txt --threads 60
```
* **Output:** Generates `dataset/logs/brute_attempts_*.csv` and a session JSON file for PCAP mapping.

### 3. Volumetric Packet Flooding (DoS Attack)
Simulates a Denial of Service attack by spawning multiple concurrent clients to flood the broker, instantly spiking the `broker_response_latency_ms` feature.

**Command (Aggressive Flood - 1 Minute):**
```bash
cd /home/pirator/smart-home-threat-simulation-platform
python3 attacks/dos_attack_advanced.py --broker 192.168.21.165 --clients 15 --duration 60
```
* **Output:** Generates `dataset/logs/dos_summary_audit.csv`. Watch the Dashboard's blue latency line spike massively!

### 4. Temporal Message Re-injection (Replay Attack)
A stealth attack that records legitimate IoT packets (e.g., "unlock door") and maliciously re-injects them after a delay to bypass standard authentication.

**Command (Record 10s & Replay):**
```bash
cd /home/pirator/smart-home-threat-simulation-platform
python3 attacks/replay_attack.py --broker 192.168.21.165 --capture 10 --delay 2
```
* **Output:** Generates `dataset/logs/replay_attempts_*.csv`.

---

## 🎯 Final Demonstration Strategy for the Panel

To achieve maximum impact during the thesis defense presentation, follow this sequence:

1. Have the **React Dashboard** (`localhost:5173`) open on a large screen. Show the panel the normal blue/green latency lines representing healthy baseline traffic.
2. In a terminal, manually run the **Brute Force** attack command (or click the button in the UI).
3. **The Climax:** Tell the panel to watch the dashboard. They will see the red Authentication Failure graph instantly spike to 100%. Within exactly 2 seconds, the `live_ml_ips.py` engine will detect the 27-feature anomaly, and the **IPS Intervention Log** will flash red, showing the exact IP address of the attacker being neutralized by OS-level `iptables`. The attack will immediately flatline, proving the autonomous defense works.
4. Finally, click the **PCAP** button on the UI to download the forensic network trace as ultimate proof of the engagement.
