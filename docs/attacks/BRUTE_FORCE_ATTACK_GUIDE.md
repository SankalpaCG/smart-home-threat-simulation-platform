# 🚀 Brute-Force Attack Simulation Guide

In this module, we simulate a **Brute-Force Attack** targeting the MQTT broker of our Smart Home system. This attack aims to gain unauthorized access by guessing the credentials of a legitimate user.

---

## 🧐 What is a Brute-Force Attack?
A brute-force attack involves systematically testing all possible combinations of passwords or using a list of common passwords (a wordlist) to compromise an authentication system. In the context of IoT/MQTT, this allows an attacker to control devices, intercept sensor data, or inject malicious commands.

---

## 🎯 Simulation Objective
The goal is to demonstrate how a weak password for the MQTT broker can be easily compromised using a simple automated script. Once the password is found, the attacker can:
- **Unlock** the Smart Lock Hub.
- **Trigger** the Security Hub's buzzer.
- **Manipulate** Climate Hub data.

---

## 🛠️ Setup & Prerequisites

### 1. Enable MQTT Authentication
By default, some MQTT brokers allow anonymous connections. To simulate this attack, we must first enable authentication:

> [!IMPORTANT]
> This simulation assumes you are using **Mosquitto** as your MQTT broker.

1. Create a password file with a user named `admin`:
   ```bash
   mosquitto_passwd -c password.txt admin
   # Set the password to '1234' (the target of our attack)
   ```
2. Edit your `mosquitto.conf` to disable anonymous access and specify the password file:
   ```ini
   allow_anonymous false
   password_file /path/to/password.txt
   ```
3. Restart the broker:
   ```bash
   sudo systemctl restart mosquitto
   ```

### 2. Install Python Dependencies
The simulation script requires the `paho-mqtt` library:
```bash
pip install paho-mqtt
```

---

## 💻 Running the Attack

Use the `bruteforce_attack.py` script located in the `attacks/` directory.

### Basic Usage
```bash
python attacks/bruteforce_attack.py --broker 192.168.1.100 --username admin
```

### Custom Wordlist
You can provide a list of passwords to try:
```bash
python attacks/bruteforce_attack.py --wordlist "admin" "12345" "abc123" "1234"
```

---

## 📈 Analyzing Results

### What to Record
When you run the attack, pay attention to the following:
- **Success Rate**: How many attempts were needed to find the password?
- **Response Time**: How long does each attempt take?
- **Broker Stability**: Does the broker slow down during the attack?

### Expected Output
```text
Starting Brute Force Attack on 192.168.1.100:1883
Targeting Username: admin
----------------------------------------
[FAILED]  admin
[SUCCESS] Password found: 1234
----------------------------------------
Attack Result: SUCCESS
Time Taken: 2.15 seconds
```

---

## 🛡️ Mitigation Strategies
How can we prevent this in a real Smart Home?
1. **Strong Password Policies**: Use long, complex passwords.
2. **Account Lockout**: Temporarily block an IP address after a certain number of failed attempts.
3. **TLS/SSL Encryption**: Use secure certificates for authentication to prevent credential sniffing.
4. **IP Whitelisting**: Only allow known devices to connect to the MQTT broker.

---

> [!TIP]
> This simulation is for educational purposes only. Always ensure you have permission before testing any system.
