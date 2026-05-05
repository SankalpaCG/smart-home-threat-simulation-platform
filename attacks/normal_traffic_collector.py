"""
normal_traffic_collector.py
─────────────────────────────────────────────────────────────────────────────
Simulates legitimate IoT device behaviour against the MQTT broker.
Logs all 20 ML features with attack_label=0 (NORMAL).

Usage:
  python3 normal_traffic_collector.py --duration 600   # 10 minutes
  python3 normal_traffic_collector.py --duration 180   # 3 minutes (post-attack)
─────────────────────────────────────────────────────────────────────────────
"""
import paho.mqtt.client as mqtt
import time, threading, argparse, csv, math, os, random, socket, sys
from datetime import datetime
from collections import deque

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from forensic_utils import get_timestamp, get_iso_now, DualLogger

# ── Config ────────────────────────────────────────────────────────────────
BASE_DIR = "/home/pirator/smart-home-threat-simulation-platform/dataset"
LOG_DIR  = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

ML_HEADERS = [
    "timestamp", "src_ip", "target_ip", "attack_label", "attack_type",
    "broker_response_latency_ms", "result_code", "password_length", "payload_entropy",
    "auth_attempt_rate", "auth_failure_rate", "auth_success_rate",
    "unique_passwords_tried", "credential_entropy",
    "inter_arrival_mean_ms", "inter_arrival_std_ms",
    "consecutive_failures", "session_attempt_count",
    "session_failure_rate", "latency_zscore",
]

# Realistic IoT device topics
TOPICS   = ["home/sensor/pir", "home/sensor/temp", "home/sensor/humidity",
            "home/device/status", "home/hub/heartbeat"]
PAYLOADS = ["motion_detected", "temp=22.5", "humidity=60", "online",
            "heartbeat=ok", "temp=23.1", "no_motion", "temp=21.8"]

def shannon_entropy(s):
    if not s: return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    n = len(s)
    return -sum((f/n) * math.log2(f/n) for f in freq.values())

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class NormalTrafficCollector:
    def __init__(self, broker, port, username, password, duration, phase):
        self.broker   = broker
        self.port     = port
        self.username = username
        self.password = password
        self.duration = duration
        self.phase    = phase          # "pre_attack" or "post_attack"
        self.src_ip   = get_local_ip()

        ts = get_timestamp()
        self.ml_name     = f"normal_{phase}_{ts}"
        self.ml_path_csv = os.path.join(LOG_DIR, self.ml_name + ".csv")

        # Rolling state
        self.lock        = threading.Lock()
        self.timestamps  = deque(maxlen=20)
        self.latencies   = deque(maxlen=200)
        self.total       = 0
        self.failures    = 0
        self.consec_fail = 0

        # DualLogger creates the file on first append, no need for initialisation


        print(f"\n{'='*55}")
        print(f" NORMAL TRAFFIC COLLECTOR — {phase.upper()}")
        print(f"{'='*55}")
        print(f"  Broker   : {broker}:{port}")
        print(f"  Attacker : {self.src_ip}")
        print(f"  Duration : {duration}s ({duration//60}m {duration%60}s)")
        print(f"  ML Log   : {self.ml_path_csv}")
        print(f"{'='*55}\n")

    def _compute_features(self, latency_ms, rc, password, now):
        with self.lock:
            self.timestamps.append(now)
            self.latencies.append(latency_ms)
            self.total += 1
            if rc != 0:
                self.failures    += 1
                self.consec_fail += 1
            else:
                self.consec_fail  = 0

            # Inter-arrival time
            ts_list = list(self.timestamps)
            if len(ts_list) > 1:
                iats     = [(ts_list[i]-ts_list[i-1])*1000 for i in range(1,len(ts_list))]
                iat_mean = sum(iats)/len(iats)
                iat_std  = math.sqrt(sum((x-iat_mean)**2 for x in iats)/len(iats)) if len(iats)>1 else 0.0
            else:
                iat_mean = iat_std = 0.0

            # Latency z-score
            lat_list = list(self.latencies)
            if len(lat_list) > 1:
                lm  = sum(lat_list)/len(lat_list)
                ls  = math.sqrt(sum((x-lm)**2 for x in lat_list)/len(lat_list))
                zscore = (latency_ms-lm)/ls if ls > 0 else 0.0
            else:
                zscore = 0.0

            sfr = self.failures / self.total

            return {
                "broker_response_latency_ms": round(latency_ms, 4),
                "result_code":          rc,
                "password_length":      len(password),
                "payload_entropy":      round(shannon_entropy(password), 4),
                # Normal traffic: very low auth attempt rate
                "auth_attempt_rate":    round(1.0 / max(iat_mean/1000, 0.001), 4) if iat_mean > 0 else 0,
                "auth_failure_rate":    0.0,
                "auth_success_rate":    round(1.0 / max(iat_mean/1000, 0.001), 4) if iat_mean > 0 else 0,
                "unique_passwords_tried": 1,    # always same real password
                "credential_entropy":   round(shannon_entropy(password), 4),
                "inter_arrival_mean_ms": round(iat_mean, 4),
                "inter_arrival_std_ms":  round(iat_std,  4),
                "consecutive_failures":  self.consec_fail,
                "session_attempt_count": self.total,
                "session_failure_rate":  round(sfr, 4),
                "latency_zscore":        round(zscore, 4),
            }

    def _single_connection(self):
        """Make one legitimate MQTT connection, publish messages, disconnect."""
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION1,
            f"iot_device_{random.getrandbits(12)}"
        )
        client.username_pw_set(self.username, self.password)

        auth_event = threading.Event()
        status     = {"rc": -1}

        def on_connect(c, userdata, flags, rc):
            status["rc"] = rc
            auth_event.set()

        client.on_connect = on_connect
        start = time.time()

        try:
            client.connect(self.broker, self.port, 10)
            client.loop_start()
            connected = auth_event.wait(5)
            latency_ms = (time.time() - start) * 1000
            rc = status["rc"] if connected else 98

            if rc == 0:
                # Publish 1-3 realistic sensor messages
                for _ in range(random.randint(1, 3)):
                    topic   = random.choice(TOPICS)
                    payload = random.choice(PAYLOADS)
                    client.publish(topic, payload, qos=0)
                    time.sleep(random.uniform(0.1, 0.5))

            client.loop_stop()
            client.disconnect()

        except Exception:
            latency_ms = (time.time() - start) * 1000
            rc = 99

        features = self._compute_features(latency_ms, rc, self.password, start)

        record = {
            "timestamp":  get_iso_now(),
            "src_ip":     self.src_ip,
            "target_ip":  self.broker,
            "attack_label": 0,
            "attack_type":  f"normal_{self.phase}",
            **features
        }

        DualLogger.append_raw(record, LOG_DIR, self.ml_name, headers=ML_HEADERS)

        return rc, latency_ms

    def run(self):
        start_time  = time.time()
        count       = 0
        success     = 0

        while time.time() - start_time < self.duration:
            elapsed = time.time() - start_time
            remaining = self.duration - elapsed

            rc, latency = self._single_connection()
            count += 1
            if rc == 0:
                success += 1

            status = "✅" if rc == 0 else "❌"
            sys.stdout.write(
                f"\r{status} Record {count:4d} | "
                f"Latency: {latency:6.1f}ms | "
                f"Elapsed: {int(elapsed)}s / {self.duration}s | "
                f"Remaining: {int(remaining)}s"
            )
            sys.stdout.flush()

            # Realistic IoT reconnect interval: 5–15 seconds
            sleep_time = random.uniform(5, 15)
            if time.time() - start_time + sleep_time > self.duration:
                break
            time.sleep(sleep_time)

        print(f"\n\n✅ Collection complete!")
        print(f"   Records collected : {count}")
        print(f"   Successful conns  : {success}/{count}")
        print(f"   ML dataset saved  : {self.ml_path_csv}")
        return self.ml_path_csv


def main():
    parser = argparse.ArgumentParser(description="Normal MQTT Traffic Collector for ML-IDS")
    parser.add_argument("--broker",   default="192.168.1.107")
    parser.add_argument("--port",     type=int, default=1883)
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="iot@secure99")
    parser.add_argument("--duration", type=int, default=600,  help="Duration in seconds (default: 600 = 10 min)")
    parser.add_argument("--phase",    default="pre_attack",   help="pre_attack or post_attack")
    args = parser.parse_args()

    collector = NormalTrafficCollector(
        args.broker, args.port, args.username,
        args.password, args.duration, args.phase
    )
    collector.run()


if __name__ == "__main__":
    main()
