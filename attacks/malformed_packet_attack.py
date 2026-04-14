import sys
import os
import paho.mqtt.client as mqtt
import argparse
import json
import time

# Ensure the project root is in the path for forensic_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_utils import DualLogger, get_timestamp, get_iso_now

# Standardized Research Banners
BANNER = """
==================================================
  SOVEREIGNTY RESEARCH: PROTOCOL LAYER FUZZER
==================================================
"""

# Configuration for standardized logging
BASE_DIR = "/home/pirator/smart-home-threat-simulation-platform/dataset"
LOG_DIR = os.path.join(BASE_DIR, "logs")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")

class ForensicFuzzLogger:
    """Logs the impact and response characteristics of malformed payloads."""
    def __init__(self, target_ip):
        self.timestamp = get_timestamp()
        self.base_name = f"fuzz_vectors_{self.timestamp}"
        self.headers = ["timestamp", "payload_identifier", "size_bytes", "latency_ms", "result"]

    def log_fuzz(self, p_name, p_len, latency, result):
        record = {
            "timestamp": get_iso_now(),
            "payload_identifier": p_name,
            "size_bytes": p_len,
            "latency_ms": round(latency * 1000, 2),
            "result": result
        }
        DualLogger.append_raw(record, LOG_DIR, self.base_name, headers=self.headers)

# High-Fidelity Structured Research Payloads
POISON_PAYLOADS = [
    {"name": "RECURSIVE_JSON", "data": json.dumps({"depth": {"d1": {"d2": {"d3": {"d4": "limit_test"}}}}})},
    {"name": "OVERFLOW_INT", "data": json.dumps({"seq": 2**64})},
    {"name": "ILLEGAL_ENCODING", "data": b"\xff\xfe\xfd\x12\x34\x56"},
    {"name": "BUFFER_STRESS", "data": "A" * 5000},
    {"name": "TYPE_AMBIGUITY", "data": json.dumps({"seq": "NAN", "status": 0xDEAD})},
    {"name": "NULL_PAYLOAD", "data": ""},
    {"name": "SCHEMATIC_INJECTION", "data": json.dumps({"$select": "*"})}
]

def main():
    parser = argparse.ArgumentParser(description="Advanced Structured Protocol Analysis (Fuzzing)")
    parser.add_argument("--broker", default="192.168.1.105", help="Target Broker IP")
    parser.add_argument("--topic", default="shtsp/home/security/motion", help="Audit Topic")
    
    args = parser.parse_args()

    print(f"\n🚀 [ADVANCED PROTOCOL ANALYSIS START] 🚀")
    print(f"Targeting: {args.broker} | Topic: {args.topic}")
    print("-" * 50)

    logger = ForensicFuzzLogger(args.broker)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Research_Fuzz_Agent")
    
    try:
        client.connect(args.broker, 1883, 60)
        
        for p in POISON_PAYLOADS:
            print(f"[!] Evaluation Vector: {p['name']} ({len(p['data'])} bytes)")
            
            start_time = time.time()
            client.publish(args.topic, p["data"])
            latency = time.time() - start_time
            
            logger.log_fuzz(p["name"], len(p["data"]), latency, "DISPATCHED")
            time.sleep(2) 
            
        client.disconnect()
        
        # Save session summary
        session_ts = get_timestamp()
        session_data = {
            "timestamp": session_ts,
            "attack_type": "Protocol_Layer_Fuzzing",
            "vectors_tested": [p["name"] for p in POISON_PAYLOADS],
            "audit_trace_base": logger.base_name
        }
        json_p, csv_p = DualLogger.log_session(session_data, SESSIONS_DIR, f"fuzz_session_{session_ts}")

        print("-" * 50)
        print(f"📊 Fuzzing Event Trace: {LOG_DIR}/{logger.base_name} (.json/.csv)")
        print(f"📊 Session Summary    : {json_p} (+.csv)")
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error during session: {e}")

if __name__ == "__main__":
    main()
