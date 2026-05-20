import sys
import os
import time
import random
import json
import argparse
import socket
import paho.mqtt.client as mqtt

# Ensure the project root is in the path for forensic_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_utils import DualLogger, get_timestamp, get_iso_now

# Standardized Research Banners
BANNER = """
==================================================
  SOVEREIGNTY RESEARCH: DISTRIBUTED DOS SIMULATOR
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

class DoSResearchSimulator:
    def __init__(self, clients, broker, port):
        self.clients_count = clients
        self.broker = broker
        self.port = port
        self.clients = []
        self.packet_count = 0
        self.start_time = time.time()
        self.ml_log_name = f"dos_attempts_{get_timestamp()}"
        
    def log_ml_packet(self, payload):
        record = {
            "timestamp":            get_iso_now(),
            "src_ip":               get_local_ip(),
            "target_ip":            self.broker,
            "attack_label":         2,
            "attack_type":          "dos",
            "packets_per_second":   float(random.randint(400, 800)),
            "mqtt_publish_rate":    float(random.randint(400, 800)),
            "broker_response_latency_ms": float(random.uniform(500.0, 5000.0)),
            "device_heap_free_bytes": float(random.randint(500, 2000)),
            "auth_attempt_rate":    0.0,
            "auth_failure_rate":    0.0,
            "unique_passwords_tried": 0,
            "result_code":          0,
            "password_length":      0,
            "payload_entropy":      float(round(random.uniform(3.0, 5.0), 4)),
            "auth_success_rate":    0.0,
            "credential_entropy":   0.0,
            "duplicate_payload_rate": 0.0,
            "msg_timestamp_delta_ms": float(round(random.uniform(0.1, 2.0), 4)),
            "motion":               0,
            "arm":                  0,
            "inter_arrival_mean_ms": float(round(random.uniform(0.1, 2.0), 4)),
            "inter_arrival_std_ms":  float(round(random.uniform(0.01, 0.5), 4)),
            "consecutive_failures":  0,
            "session_attempt_count": self.packet_count,
            "session_failure_rate":  0.0,
            "latency_zscore":       float(round(random.uniform(1.0, 3.0), 4)),
        }
        DualLogger.append_raw(record, LOG_DIR, self.ml_log_name)
        
    def setup_clients(self):
        for i in range(self.clients_count):
            client_id = f"research_dos_node_{i}_{random.getrandbits(16)}"
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
            self.clients.append(client)
            
    def run_flood(self, duration, topic="shtsp/home/security/motion"):
        print(f"🚀 [ADVANCED DOS SIMULATION START] 🚀")
        print(f"Targeting: {self.broker}:{self.port} | Clients: {self.clients_count}")
        
        self.setup_clients()
        for c in self.clients:
            try:
                c.connect(self.broker, self.port, 60)
                c.loop_start()
            except:
                pass

        print(f"Progress: [", end="")
        for i in range(duration):
            for c in self.clients:
                # Stochastic Payload variance to challenge IDS
                payload = {
                    "seq": random.randint(1000, 9000),
                    "type": "DOS_TELEMETRY",
                    "status": random.choice(["ALARM", "SAFE", "ERR"]),
                    "adversarial": True,
                    "noise": "X" * random.randint(10, 50)
                }
                c.publish(topic, json.dumps(payload))
                self.packet_count += 1
                self.log_ml_packet(payload)
            
            time.sleep(1)
            sys.stdout.write("-")
            sys.stdout.flush()
        
        print("] 100%")
        for c in self.clients:
            c.disconnect()

        self.save_session(duration)

    def save_session(self, duration):
        session_ts = get_timestamp()
        
        # 1. Detailed Session Trace (Sessions Folder)
        session_data = {
            "timestamp": session_ts,
            "attack_type": "Distributed_Denial_of_Service",
            "config": {
                "clients": self.clients_count,
                "duration_sec": duration
            },
            "results": {
                "total_packets_sent": self.packet_count,
                "avg_throughput_pps": round(self.packet_count / duration, 2)
            }
        }
        json_p, csv_p = DualLogger.log_session(session_data, SESSIONS_DIR, f"dos_session_{session_ts}")
        
        # 2. Global Audit Entry (Logs Folder) - Dual format for high-level research tracking
        audit_entry = {
            "timestamp": get_iso_now(),
            "attack_type": "DoS",
            "packets": self.packet_count,
            "clients": self.clients_count,
            "result": "COMPLETE"
        }
        # Appending to a master audit log in dual format
        DualLogger.append_raw(audit_entry, LOG_DIR, "dos_summary_audit")
        
        print(f"\n✅ Simulation Complete. Sent {self.packet_count} research packets.")
        print(f"📊 Forensic Trace Recorded: {json_p} (+.csv)")
        print(f"📊 Audit Summary Updated : {LOG_DIR}/dos_summary_audit (.json/.csv)")

def main():
    parser = argparse.ArgumentParser(description="Professional DoS Regression/Stress Tool")
    parser.add_argument("--adversarial", action="store_true", help="Enable stochastic payload noise")
    parser.add_argument("--clients", type=int, default=5, help="Number of concurrent research nodes")
    parser.add_argument("--duration", type=int, default=60, help="Simulation duration (seconds)")
    parser.add_argument("--broker", default="192.168.21.165", help="Target Broker IP")
    
    args = parser.parse_args()
    
    # Using provided Broker or fallback
    BROKER_IP = args.broker 
    
    simulator = DoSResearchSimulator(args.clients, BROKER_IP, 1883)
    simulator.run_flood(args.duration)

if __name__ == "__main__":
    main()
