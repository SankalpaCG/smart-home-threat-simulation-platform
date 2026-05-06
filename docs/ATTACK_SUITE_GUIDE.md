# ⚔️ Sovereignty Research: Attack Suite Guide

This guide contains the exact working commands required to execute the IoT threat simulations for the Master's project. All scripts are specifically engineered to extract the 20 crucial machine learning features required by our Random Forest classifier.

**Global Configuration:**
* **Broker IP:** `192.168.21.120` (Change this in the commands if your network IP changes).
* **Port:** `1883`

---

## 1. Baseline Telemetry Collection (Normal Traffic)
Before simulating any attack, you must collect a baseline of what healthy IoT traffic looks like. The Random Forest model needs this to understand the difference between normal behavior and an attack.

**Command (Pre-Attack Baseline - 10 Minutes):**
```bash
python3 attacks/normal_traffic_collector.py --broker 192.168.21.120 --username admin --password "iot@secure99" --duration 600 --phase pre_attack
```

**Command (Post-Attack Cooldown - 3 Minutes):**
Run this *after* an attack finishes to show how the network recovers.
```bash
python3 attacks/normal_traffic_collector.py --broker 192.168.21.120 --username admin --password "iot@secure99" --duration 180 --phase post_attack
```
* **Output:** Generates `dataset/logs/normal_pre_attack_*.csv` and `normal_post_attack_*.csv`.

---

## 2. Advanced Credential Stuffing (Brute Force)
This script simulates a highly aggressive, multi-threaded password spraying attack against the MQTT broker. It tracks exactly how many bad credentials occur per second and measures the payload entropies.

**Command (100k Dictionary Attack):**
Using 10 target usernames against a 10,000-word dictionary.
```bash
python3 attacks/bruteforce_attack.py --broker 192.168.21.120 --userlist dataset/userlist_bruteforce.txt --file dataset/wordlist_10k.txt --threads 10
```

**Command (Full 500k Dictionary Attack):**
Using the massive 50k wordlist for a highly extended overnight simulation.
```bash
python3 attacks/bruteforce_attack.py --broker 192.168.21.120 --userlist dataset/userlist_bruteforce.txt --file dataset/wordlist_50k.txt --threads 15
```
* **Output:** Generates `dataset/logs/brute_attempts_*.csv` containing all ML features, plus a `brute_audit_*.csv` file containing plain-text credential audit logs for the final report.

---

## 3. Volumetric Packet Flooding (DoS Attack)
Simulates a Denial of Service attack by spawning hundreds of malicious MQTT clients that attempt to flood the broker with junk payloads, spiking the `broker_response_latency_ms`.

**Command (Aggressive Flood - 5 Minutes):**
Spawns 50 concurrent flooding clients for 300 seconds.
```bash
python3 attacks/dos_attack_advanced.py --clients 50 --duration 300
```
*(Note: If the broker IP changes, manually edit `BROKER_IP` inside `dos_attack_advanced.py` on line 119).*

---

## 4. Temporal Message Re-injection (Replay Attack)
Simulates an attacker sitting on the network, recording legitimate IoT sensor packets (e.g., a "Door Unlock" command), and re-injecting them later to bypass authentication. 

**Command (Record & Replay):**
Captures packets for 30 seconds, delays for 10 seconds, and then floods the network with exact replicas.
```bash
python3 attacks/replay_attack.py --broker 192.168.21.120 --capture 30 --delay 10
```

---

### What's Next?
Once you have run these simulations and successfully populated your `dataset/logs/` folder with CSVs, proceed to the **[Machine Learning & IPS Guide](MACHINE_LEARNING_IPS_GUIDE.md)** to process the data, train your AI model, and actively defend the network!
