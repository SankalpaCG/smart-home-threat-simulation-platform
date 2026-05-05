import paho.mqtt.client as mqtt
import time
import argparse
import sys
import threading
import json
import os
import csv
import random
import math
import socket
from queue import Queue
from collections import deque
from datetime import datetime

import sys
import os

# Ensure the project root is in the path for forensic_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_utils import DualLogger, get_timestamp, get_iso_now

# ─────────────────────────────────────────────────────────────
BANNER = """
==================================================
 RESEARCH: AUTHENTICATION AUDITOR v2.0 (ML-IDS)
==================================================
"""

BASE_DIR     = "/home/pirator/smart-home-threat-simulation-platform/dataset"
LOG_DIR      = os.path.join(BASE_DIR, "logs")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# ML FEATURE SCHEMA — 20 features
# ─────────────────────────────────────────────────────────────
ML_HEADERS = [
    # ── Identity ──────────────────────────────────────────────
    "timestamp",            # 01 ISO-8601 timestamp of attempt
    "src_ip",               # 02 Attacker machine IP
    "target_ip",            # 03 Broker IP
    "attack_label",         # 04 Integer: 0=Normal 1=BruteForce 2=DoS 3=Replay
    "attack_type",          # 05 String label for the attack

    # ── Per-Attempt Features ───────────────────────────────────
    "broker_response_latency_ms", # 06 CONNACK response time (ms)
    "result_code",          # 07 MQTT rc: 0=OK 4=BadUser 5=BadCreds 98=Timeout 99=ConnFail
    "password_length",      # 08 Character length of password tried
    "payload_entropy",      # 09 Shannon entropy of the password string

    # ── Rolling Window (last 5 seconds) ───────────────────────
    "auth_attempt_rate",    # 10 Attempts per second in last 5s
    "auth_failure_rate",    # 11 Failures per second in last 5s
    "auth_success_rate",    # 12 Successes per second in last 5s
    "unique_passwords_tried", # 13 Distinct passwords tried in last 5s
    "credential_entropy",   # 14 Shannon entropy of password distribution (last 5s)

    # ── Timing Features (last 20 attempts) ────────────────────
    "inter_arrival_mean_ms",# 15 Mean time between consecutive attempts (ms)
    "inter_arrival_std_ms", # 16 Std dev of inter-arrival times (ms)

    # ── Session-Level Cumulative Features ─────────────────────
    "consecutive_failures", # 17 Running count of consecutive BAD_CREDENTIALS
    "session_attempt_count",# 18 Total attempts made this session
    "session_failure_rate", # 19 Cumulative failures / total attempts
    "latency_zscore",       # 20 Z-score of current latency vs session mean
]


def shannon_entropy(s):
    """Compute Shannon entropy of a string."""
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    n = len(s)
    return -sum((f/n) * math.log2(f/n) for f in freq.values())


def get_local_ip():
    """Get the local machine's IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ─────────────────────────────────────────────────────────────
class MLFeatureTracker:
    """
    Thread-safe rolling window tracker for computing all 20 ML features.
    Maintains shared state across all worker threads.
    """
    def __init__(self):
        self.lock = threading.Lock()

        # Rolling window: (timestamp, result_code, password)
        self.window_5s    = deque()         # all events in last 5s
        self.timestamps   = deque(maxlen=20) # last 20 arrival times for IAT
        self.latencies    = deque(maxlen=200)# for z-score computation

        # Session cumulative
        self.total_attempts    = 0
        self.total_failures    = 0
        self.consecutive_fails = 0

    def _prune_window(self, now):
        """Remove events older than 5 seconds from the rolling window."""
        cutoff = now - 5.0
        while self.window_5s and self.window_5s[0][0] < cutoff:
            self.window_5s.popleft()

    def record(self, timestamp, result_code, password, latency_ms):
        """Record a new attempt and return computed feature dict."""
        now = timestamp

        with self.lock:
            # ── Prune 5s window ───────────────────────────────
            self._prune_window(now)

            # ── Add current event ─────────────────────────────
            self.window_5s.append((now, result_code, password))
            self.timestamps.append(now)
            self.latencies.append(latency_ms)

            # ── Session counters ──────────────────────────────
            self.total_attempts += 1
            is_failure = result_code not in (0,)
            if is_failure:
                self.total_failures    += 1
                self.consecutive_fails += 1
            else:
                self.consecutive_fails  = 0

            # ── 5s Window Stats ───────────────────────────────
            window_events = list(self.window_5s)
            window_size   = len(window_events)
            window_span   = max((window_events[-1][0] - window_events[0][0]), 0.001) if window_size > 1 else 1.0

            failures_5s  = sum(1 for _, rc, _ in window_events if rc not in (0,))
            successes_5s = sum(1 for _, rc, _ in window_events if rc == 0)
            passwords_5s = [pwd for _, _, pwd in window_events]
            unique_pwds  = len(set(passwords_5s))

            attempt_rate  = window_size  / window_span
            failure_rate  = failures_5s  / window_span
            success_rate  = successes_5s / window_span

            # Credential entropy over 5s window
            cred_entropy = shannon_entropy("".join(passwords_5s)) if passwords_5s else 0.0

            # ── Inter-Arrival Time ────────────────────────────
            ts_list = list(self.timestamps)
            if len(ts_list) > 1:
                iats = [(ts_list[i] - ts_list[i-1]) * 1000 for i in range(1, len(ts_list))]
                iat_mean = sum(iats) / len(iats)
                iat_std  = math.sqrt(sum((x - iat_mean)**2 for x in iats) / len(iats)) if len(iats) > 1 else 0.0
            else:
                iat_mean = 0.0
                iat_std  = 0.0

            # ── Latency Z-Score ───────────────────────────────
            lat_list = list(self.latencies)
            if len(lat_list) > 1:
                lat_mean = sum(lat_list) / len(lat_list)
                lat_std  = math.sqrt(sum((x - lat_mean)**2 for x in lat_list) / len(lat_list))
                lat_zscore = (latency_ms - lat_mean) / lat_std if lat_std > 0 else 0.0
            else:
                lat_zscore = 0.0

            # ── Session failure rate ──────────────────────────
            session_failure_rate = self.total_failures / self.total_attempts

            return {
                "auth_attempt_rate":       round(attempt_rate,  4),
                "auth_failure_rate":       round(failure_rate,  4),
                "auth_success_rate":       round(success_rate,  4),
                "unique_passwords_tried":  unique_pwds,
                "credential_entropy":      round(cred_entropy,  4),
                "inter_arrival_mean_ms":   round(iat_mean,      4),
                "inter_arrival_std_ms":    round(iat_std,       4),
                "consecutive_failures":    self.consecutive_fails,
                "session_attempt_count":   self.total_attempts,
                "session_failure_rate":    round(session_failure_rate, 4),
                "latency_zscore":          round(lat_zscore,    4),
            }


# ─────────────────────────────────────────────────────────────
class MLAttemptLogger:
    """
    Logs all 20 ML features directly to dataset/logs/brute_attempts_*.csv
    and brute_attempts_*.json — single unified output, no separate ml_features folder.
    """

    def __init__(self, target_ip, src_ip, tracker: MLFeatureTracker):
        self.timestamp = get_timestamp()
        self.target_ip = target_ip
        self.src_ip    = src_ip
        self.tracker   = tracker
        self.base_name = f"brute_attempts_{self.timestamp}"
        self.audit_name = f"brute_audit_{self.timestamp}"
        self.audit_headers = ["timestamp", "target_ip", "username", "password", "result"]

    def log_attempt(self, username, password, rc, latency_ms, result_str, event_time):
        """Compute all 20 ML features and log to both CSV and JSON in dataset/logs/."""

        # ── Compute rolling features ──────────────────────────
        rolling = self.tracker.record(event_time, rc, password, latency_ms)

        # ── Build unified 20-feature record ───────────────────
        record = {
            "timestamp":            get_iso_now(),
            "src_ip":               self.src_ip,
            "target_ip":            self.target_ip,
            "attack_label":         1,
            "attack_type":          "brute_force",

            "broker_response_latency_ms": round(latency_ms, 4),
            "result_code":          rc,
            "password_length":      len(password),
            "payload_entropy":      round(shannon_entropy(password), 4),
            "username_tested":      username,

            "auth_attempt_rate":       rolling["auth_attempt_rate"],
            "auth_failure_rate":       rolling["auth_failure_rate"],
            "auth_success_rate":       rolling["auth_success_rate"],
            "unique_passwords_tried":  rolling["unique_passwords_tried"],
            "credential_entropy":      rolling["credential_entropy"],

            "inter_arrival_mean_ms":   rolling["inter_arrival_mean_ms"],
            "inter_arrival_std_ms":    rolling["inter_arrival_std_ms"],

            "consecutive_failures":    rolling["consecutive_failures"],
            "session_attempt_count":   rolling["session_attempt_count"],
            "session_failure_rate":    rolling["session_failure_rate"],
            "latency_zscore":          rolling["latency_zscore"],
        }

        # Write ML features to dataset/logs/ as both .csv and .json
        DualLogger.append_raw(record, LOG_DIR, self.base_name, headers=ML_HEADERS)

        # Write simple audit log
        audit_record = {
            "timestamp": get_iso_now(),
            "target_ip": self.target_ip,
            "username": username,
            "password": password,
            "result": result_str
        }
        DualLogger.append_raw(audit_record, LOG_DIR, self.audit_name, headers=self.audit_headers)
        return record


# ─────────────────────────────────────────────────────────────
def try_password(broker, port, username, password, logger, results):
    """Attempts a single credential combination and captures all telemetry."""
    # Use newer API if possible, else fallback to standard connect
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,
                             f"audit_{random.getrandbits(16)}")
    except AttributeError:
        client = mqtt.Client(f"audit_{random.getrandbits(16)}")
    client.username_pw_set(username, password)

    auth_event = threading.Event()
    status = {"rc": -1}

    def on_connect(client, userdata, flags, rc):
        status["rc"] = rc
        auth_event.set()

    client.on_connect = on_connect
    start_time = time.time()
    result_str = "ERROR"

    try:
        client.connect(broker, port, 5)
        client.loop_start()

        if auth_event.wait(3):
            rc         = status["rc"]
            latency_ms = (time.time() - start_time) * 1000

            if rc == 0:
                result_str          = "SUCCESS"
                results['success']  = True
                results['password'] = password
                results['username'] = username
            elif rc in (4, 5):
                result_str = "BAD_CREDENTIALS"
            else:
                result_str = f"REFUSED_{rc}"
        else:
            rc         = 98
            latency_ms = (time.time() - start_time) * 1000
            result_str = "AUTH_TIMEOUT"

        client.loop_stop()
        client.disconnect()

    except Exception:
        latency_ms = (time.time() - start_time) * 1000
        result_str = "CONNECTION_FAILED"
        rc         = 99

    logger.log_attempt(username, password, rc, latency_ms, result_str, start_time)
    return rc == 0


def worker(broker, port, queue, logger, results, stop_event, progress):
    while not queue.empty() and not stop_event.is_set():
        username, password = queue.get()
        if try_password(broker, port, username, password, logger, results):
            stop_event.set()
        progress['current'] += 1
        queue.task_done()


def print_progress(current, total, start_time):
    elapsed = time.time() - start_time
    mps     = current / elapsed if elapsed > 0 else 0
    percent = (current / total) * 100
    sys.stdout.write(
        f"\r🔍 Testing: {percent:.1f}% | "
        f"Attempt: {current}/{total} | "
        f"Speed: {mps:.2f} att/s"
    )
    sys.stdout.flush()


# ─────────────────────────────────────────────────────────────
def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="MQTT Brute Force — ML-IDS Dataset Generator")
    parser.add_argument("--broker",   default="192.168.1.107", help="Target Broker IP")
    parser.add_argument("--port",     type=int, default=1883,   help="Broker Port")
    parser.add_argument("--username",                           help="Single Target Username")
    parser.add_argument("--userlist",                           help="Path to username list (.txt)")
    parser.add_argument("--wordlist", nargs="*",                help="Direct password list")
    parser.add_argument("--file",                               help="Path to password list (.txt)")
    parser.add_argument("--threads",  type=int, default=5,      help="Concurrent threads")
    args = parser.parse_args()

    # ── Build username list ───────────────────────────────────
    final_userlist = ["admin"]
    if args.userlist:
        if os.path.exists(args.userlist):
            with open(args.userlist, 'r') as f:
                final_userlist = [l.strip() for l in f if l.strip()]
        else:
            print(f"❌ Error: Username file {args.userlist} not found.")
            return
    elif args.username:
        final_userlist = [args.username]

    # ── Build password list ───────────────────────────────────
    if args.file:
        if os.path.exists(args.file):
            with open(args.file, 'r') as f:
                final_wordlist = [l.strip() for l in f if l.strip()]
        else:
            print(f"❌ Error: Password file {args.file} not found.")
            return
    elif args.wordlist:
        final_wordlist = args.wordlist
    else:
        final_wordlist = ["admin","1234","password","iot123","root",
                          "123456","admin123","smart","home"]

    src_ip  = get_local_ip()
    tracker = MLFeatureTracker()
    logger  = MLAttemptLogger(args.broker, src_ip, tracker)

    print(f"🚀 [ML-IDS AUDIT START]")
    print(f"   Target    : {args.broker}:{args.port}")
    print(f"   Attacker  : {src_ip}")
    print(f"   Usernames : {len(final_userlist):,} users")
    print(f"   Passwords : {len(final_wordlist):,} passwords")
    total_combinations = len(final_userlist) * len(final_wordlist)
    print(f"   Total Comb: {total_combinations:,} combinations")
    print(f"   Log Base  : dataset/logs/{logger.base_name}")
    print("-" * 55)

    credential_queue = Queue()
    for user in final_userlist:
        for pwd in final_wordlist:
            credential_queue.put((user, pwd))

    results    = {'success': False, 'password': None, 'username': None}
    stop_event = threading.Event()
    progress   = {'current': 0}
    threads    = []
    start_time = time.time()

    for _ in range(args.threads):
        t = threading.Thread(
            target=worker,
            args=(args.broker, args.port, credential_queue, logger, results, stop_event, progress)
        )
        t.start()
        threads.append(t)

    total = total_combinations
    while any(t.is_alive() for t in threads):
        print_progress(progress['current'], total, start_time)
        time.sleep(0.5)

    for t in threads:
        t.join()

    duration = time.time() - start_time
    print(f"\n" + "-" * 55)

    if results['success']:
        print(f"✅ CRACKED: [{results['username']}:{results['password']}]")
    else:
        print("❌ AUDIT COMPLETE: No valid credentials found.")

    # ── Session summary ───────────────────────────────────────
    session_ts = get_timestamp()
    summary = {
        "timestamp":       session_ts,
        "attack_type":     "Brute_Force",
        "attack_label":    1,
        "target":          args.broker,
        "src_ip":          src_ip,
        "usernames_tried": len(final_userlist),
        "total_attempts":  progress['current'],
        "success":         results['success'],
        "cracked_password":results.get('password'),
        "duration_sec":    round(duration, 2),
        "speed_att_s":     round(progress['current'] / duration, 2) if duration > 0 else 0,
        "log_base":        logger.base_name,
    }
    json_p, csv_p = DualLogger.log_session(
        summary, SESSIONS_DIR, f"brute_session_{session_ts}"
    )

    print(f"\n📊 ML Feature Log  : dataset/logs/{logger.base_name} (.json/.csv)")
    print(f"   → Both files contain all 20 features")
    print(f"📋 Session Summary : {json_p}")
    print("-" * 55)


if __name__ == "__main__":
    main()
