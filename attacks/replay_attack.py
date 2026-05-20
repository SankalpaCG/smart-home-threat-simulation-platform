import sys
import os
import paho.mqtt.client as mqtt
import json
import time
import argparse
import socket
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

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# Configuration for standardized logging
BASE_DIR = "/home/pirator/smart-home-threat-simulation-platform/dataset"
LOG_DIR = os.path.join(BASE_DIR, "logs")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")

BROKER = "192.168.21.165"
PORT = 1883
TOPICS = ["shtsp/home/security/heartbeat", "shtsp/home/security/motion"]

class AdvancedReplaySimulator:
    def __init__(self, capture_duration, delay, broker=BROKER):
        self.capture_duration = capture_duration
        self.delay = delay
        self.broker = broker
        self.buffer = []
        self.is_capturing = True
        self.ml_log_name = f"replay_attempts_{get_timestamp()}"
        self.packet_count = 0
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Research_Replay")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def log_ml_packet(self, item):
        record = {
            "timestamp":            get_iso_now(),
            "src_ip":               get_local_ip(),
            "target_ip":            self.broker,
            "attack_label":         3,
            "attack_type":          "replay",
            "packets_per_second":   float(random.uniform(5.0, 20.0)),
            "mqtt_publish_rate":    float(random.uniform(5.0, 20.0)),
            "broker_response_latency_ms": float(random.uniform(10.0, 100.0)),
            "device_heap_free_bytes": float(random.randint(200000, 235000)),
            "auth_attempt_rate":    0.0,
            "auth_failure_rate":    0.0,
            "unique_passwords_tried": 0,
            "result_code":          0,
            "password_length":      0,
            "payload_entropy":      float(round(random.uniform(2.0, 4.0), 4)),
            "auth_success_rate":    0.0,
            "credential_entropy":   0.0,
            "duplicate_payload_rate": 0.0,
            "msg_timestamp_delta_ms": float(round(random.uniform(500.0, 5000.0), 4)),
            "motion":               0,
            "arm":                  0,
            "inter_arrival_mean_ms": float(round(random.uniform(10.0, 50.0), 4)),
            "inter_arrival_std_ms":  float(round(random.uniform(5.0, 20.0), 4)),
            "consecutive_failures":  0,
            "session_attempt_count": self.packet_count,
            "session_failure_rate":  0.0,
            "latency_zscore":       float(round(random.uniform(0.1, 1.0), 4)),
        }
        DualLogger.append_raw(record, LOG_DIR, self.ml_log_name)

    def on_connect(self, client, userdata, flags, rc):
        print(f"✅ Replay Simulator connected to {self.broker}")
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
            self.packet_count += 1
            self.log_ml_packet(item)
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
            self.client.connect(self.broker, PORT, 60)
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
    parser.add_argument("--broker", default="192.168.21.165", help="Target Broker IP")
    parser.add_argument("--capture", type=int, default=30, help="Capture phase (seconds)")
    parser.add_argument("--delay", type=int, default=10, help="Delay phase (seconds)")
    
    args = parser.parse_args()

    simulator = AdvancedReplaySimulator(args.capture, args.delay, broker=args.broker)
    simulator.run()
