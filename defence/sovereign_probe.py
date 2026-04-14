import os
import sys
from scapy.all import sniff, IP, TCP

# Ensure the project root is in the path for forensic_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from forensic_utils import DualLogger, get_iso_now

# Standardized Research Banners
BANNER = """
==================================================
  SOVEREIGNTY RESEARCH: NETWORK INTELLIGENCE PROBE
==================================================
"""

# Configuration
INTERFACE = "eth0"
TARGET_PORT = 1883
# Use absolute path for dataset to ensure consistency across subdirectories
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "dataset/raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class NetworkProbe:
    def __init__(self):
        self.base_name = "network_intelligence"
        self.headers = [
            "timestamp", "src_ip", "dst_ip", "tcp_flags", "tcp_window", 
            "payload_len", "payload_entropy", "proto_type"
        ]
        self.packet_count = 0

    def calculate_entropy(self, data):
        """Calculates Shannon entropy of the payload bytes."""
        if not data:
            return 0
        import math
        entropy = 0
        for x in range(256):
            p_x = list(data).count(x) / len(data)
            if p_x > 0:
                entropy += -p_x * math.log(p_x, 2)
        return round(entropy, 4)

    def process_packet(self, pkt):
        if IP in pkt and TCP in pkt:
            self.packet_count += 1
            
            # Extract Network Features
            src_ip = pkt[IP].src
            dst_ip = pkt[IP].dst
            flags = str(pkt[TCP].flags)
            window = pkt[TCP].window
            
            payload = bytes(pkt[TCP].payload)
            payload_len = len(payload)
            entropy = self.calculate_entropy(payload)
            
            # Simple Protocol Identification (MQTT)
            proto = "TCP"
            if pkt[TCP].dport == 1883 or pkt[TCP].sport == 1883:
                proto = "MQTT"

            # Create standard record
            record = {
                "timestamp": get_iso_now(),
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "tcp_flags": flags,
                "tcp_window": window,
                "payload_len": payload_len,
                "payload_entropy": entropy,
                "proto_type": proto
            }

            # Log to Dual Files (Intelligence Raw)
            DualLogger.append_raw(record, OUTPUT_DIR, self.base_name, headers=self.headers)
                
            if self.packet_count % 10 == 0:
                sys.stdout.write(f"\r📡 [Sovereignty Probe] Synchronized {self.packet_count} packets in JSON+CSV...")
                sys.stdout.flush()

    def start(self):
        print(BANNER)
        print(f"🚀 Launching Intelligence Probe on {INTERFACE}...")
        print(f"🕵️  Filtering for Port {TARGET_PORT} (MQTT) | Data Sync: JSON + CSV")
        print("-" * 50)
        try:
            sniff(iface=INTERFACE, prn=self.process_packet, filter=f"tcp port {TARGET_PORT}", store=0)
        except PermissionError:
            print("\n❌ Error: Scapy requires 'sudo' to sniff network interfaces.")
            print("Try running: sudo ../venv/bin/python3 sovereign_probe.py")
        except Exception as e:
            print(f"\n❌ Probe Error: {e}")

if __name__ == "__main__":
    probe = NetworkProbe()
    probe.start()
