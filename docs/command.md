# Execution Commands

This document contains the exact terminal commands required to launch the various attack simulations and defense mechanisms from your terminal layer.

> [!WARNING]
> **CRITICAL RULE:** You must execute these commands from the **ROOT** project folder (`/home/pirator/smart-home-threat-simulation-platform`), **NOT** from inside the `/dashboard` folder! If you are in `/dashboard`, type `cd ..` before running these.

Ensure you are in the root project directory before executing these commands:
```bash
cd /home/pirator/smart-home-threat-simulation-platform
```

Make sure your virtual environment is active (if applicable), or use the Python interpreter inside the `venv`:
```bash
source venv/bin/activate
```

---

## 1. Launch MQTT Bruteforce Attack
This command launches the high-concurrency dictionary attack against the target broker.

**Basic Command (Default Settings):**
```bash
python3 attacks/bruteforce_attack.py --username admin --file dataset/wordlist_10k.txt --broker 192.168.1.100
```

**Advanced Command (Custom Threads):**
*Adjust `--threads` based on your hardware limits.*
```bash
python3 attacks/bruteforce_attack.py --username admin --file dataset/wordlist_10k.txt --broker 192.168.1.100 --threads 20
```

**Full Dictionary Attack (Bruteforce Usernames AND Passwords):**
*Uses a text file for usernames instead of a single target.*
```bash
python3 attacks/bruteforce_attack.py --userlist dataset/userlist_bruteforce.txt --file dataset/wordlist_10k.txt --broker 192.168.1.100 --threads 20
```

---

## 2. Launch Volumetric DoS Attack
This command unleashes the simulated botnet against the MQTT broker.

**Basic Command (10 Botnet Nodes, 60 Seconds):**
```bash
python3 attacks/dos_attack_advanced.py --clients 10 --duration 60 --broker 192.168.1.100
```

**Heavy Stress Command (50 Botnet Nodes, 120 Seconds):**
*WARNING: This may crash the target router/broker.*
```bash
python3 attacks/dos_attack_advanced.py --clients 50 --duration 120 --broker 192.168.1.100
```

---

## 3. Launch Replay Attack
This command sniffs the network, captures a valid payload, and replays it at high velocity to poison the state of the Smart Home.

**Basic Command:**
```bash
python3 attacks/replay_attack.py --broker 192.168.1.100 --delay 2
```

---

## 4. Launch Normal Traffic Generator
This command acts as the baseline control group, generating standard, benign Smart Home telemetry.

**Basic Command:**
```bash
python3 attacks/normal_traffic_collector.py --broker 192.168.1.100
```

---

## 5. Train the Machine Learning Models
This command reads the massive `.csv` dataset, engineers the features, and trains the 5 different AI architectures.

**Execution Command:**
```bash
python3 model_comparison/train_compare_models.py
```

---

## 6. Generate Google Colab Jupyter Notebook
This command programmatically builds the `.ipynb` file used to bridge your local dataset to the GPU clusters on Google Colab for advanced training and visual metric generation.

**Execution Command:**
```bash
python3 generate_notebook.py
```

---

## 7. Forensic Telemetry Logger (`forensic_utils.py`)
> [!NOTE]
> **No Execution Command Needed.**
> The `forensic_utils.py` script is a **library class module**. It is not meant to be run directly from the terminal. Instead, it is automatically imported by the `bruteforce_attack.py`, `dos_attack_advanced.py`, and `normal_traffic_collector.py` scripts to safely log JSON and CSV data using thread-safe `threading.Lock()` queues.

---

## 8. Launch the Live Intrusion Prevention System (IPS)
This command boots the AI edge-firewall. It will actively sniff the telemetry streams and execute `sudo iptables` blocks against any IP that triggers the Random Forest prediction logic.

**Execution Command:**
```bash
sudo /home/pirator/smart-home-threat-simulation-platform/venv/bin/python3 defence/live_ml_ips.py
```
*(Note: `sudo` is strictly required so the Python script has Kernel permission to alter `iptables`)*

---

## 9. Launch the Visualization Dashboard (Full Stack)
To run the React UI and the Node.js backend simultaneously, you need two terminal windows.

**Terminal 1 (Node.js Backend):**
```bash
cd dashboard
node server.js
```

**Terminal 2 (React Frontend):**
```bash
cd dashboard/ui
npm run dev
```

---

## 10. Execute the Academic Validation & Testing Suite
This script systematically validates the 1.6 Million row dataset for structural integrity, leakage, and missing values, while simultaneously rendering high-resolution mathematical graphs (.png) of your Machine Learning evaluation metrics and attack simulations.

**Execution Command:**
```bash
cd testing
./run_tests.sh
```
