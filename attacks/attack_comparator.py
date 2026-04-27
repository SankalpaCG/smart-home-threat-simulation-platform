#!/usr/bin/env python3
"""
Attack Type Comparison Tool
Compares Normal, DoS, and Replay Attack characteristics
"""

import csv
import os
from collections import Counter
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LABELED_DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset", "labeled")

class AttackComparator:
    def __init__(self):
        self.datasets = {
            'normal': os.path.join(LABELED_DATASET_DIR, 'dataset_Normal.csv'),
            'dos': os.path.join(LABELED_DATASET_DIR, 'dataset_DoS.csv')
        }
        self.data = {}
    
    def load_all_datasets(self):
        """Load all available datasets"""
        for name, filename in self.datasets.items():
            if os.path.exists(filename):
                self.data[name] = self._load_file(filename)
                print(f"✅ Loaded {filename}")
            else:
                print(f"⚠️  {filename} not found")
    
    def _load_file(self, filename):
        """Load data from CSV"""
        packets = []
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    packets.append({
                        'pps': float(row['pps']),
                        'heap': int(row['heap']),
                        'motion': int(row['motion']),
                        'arm': int(row['arm']),
                        'label': int(row['label'])
                    })
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
        return packets
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
    
    def compare_all_attacks(self):
        """Compare all attack types"""
        self.print_header("🔴 ATTACK TYPE COMPARISON ANALYSIS")
        
        # Define attack characteristics
        attacks = {
            'Normal': {
                'description': 'Legitimate device behavior',
                'characteristics': [
                    '✓ Natural variation in metrics',
                    '✓ Random packet timing',
                    '✓ Realistic sensor readings',
                    '✓ High diversity in values',
                    '✓ No repeated patterns'
                ],
                'detection': 'Baseline - all other attacks deviate'
            },
            'DoS (Denial of Service)': {
                'description': 'Flood the device with traffic',
                'characteristics': [
                    '✗ Extreme packet rate (high PPS)',
                    '✗ Memory exhaustion (low heap)',
                    '✗ Junk/invalid payload',
                    '✗ No meaningful sensor data',
                    '✗ Device becomes unresponsive'
                ],
                'detection': 'High PPS, Low heap, High error rate'
            },
            'Replay': {
                'description': 'Resend captured legitimate packets',
                'characteristics': [
                    '⚠ All packets identical',
                    '⚠ Zero variance in data',
                    '⚠ Looks legitimate but repetitive',
                    '⚠ Same sequence repeating',
                    '⚠ No timestamp validation'
                ],
                'detection': 'Duplicate detection, Pattern matching, Zero variance'
            },
            'BruteForce': {
                'description': 'Try many combinations to guess credentials',
                'characteristics': [
                    '✗ Repeated login attempts',
                    '✗ Invalid/malformed data',
                    '✗ Sequential/predictable changes',
                    '✗ High error/rejection rate',
                    '✗ Automated attack pattern'
                ],
                'detection': 'Failed attempts, Rate limiting, Account lockout'
            },
            'Malformed': {
                'description': 'Send invalid or corrupted data',
                'characteristics': [
                    '✗ Invalid JSON/protocol',
                    '✗ Missing required fields',
                    '✗ Out-of-range values',
                    '✗ Type mismatches',
                    '✗ Parse errors'
                ],
                'detection': 'Input validation, Type checking, Format verification'
            }
        }
        
        for attack_name, details in attacks.items():
            print(f"\n{'─' * 80}")
            print(f"🔹 {attack_name}")
            print(f"{'─' * 80}")
            print(f"Description: {details['description']}")
            print(f"\nCharacteristics:")
            for char in details['characteristics']:
                print(f"  {char}")
            print(f"\nDetection Method: {details['detection']}")
    
    def analyze_dataset_metrics(self):
        """Analyze metrics for each dataset"""
        self.print_header("📊 DATASET METRICS COMPARISON")
        
        for name, packets in self.data.items():
            if not packets:
                continue
            
            print(f"\n{'─' * 80}")
            print(f"Dataset: {name.upper()}")
            print(f"{'─' * 80}")
            
            count = len(packets)
            pps_vals = [p['pps'] for p in packets]
            heap_vals = [p['heap'] for p in packets]
            motion_vals = [p['motion'] for p in packets]
            arm_vals = [p['arm'] for p in packets]
            
            print(f"Total Packets: {count}")
            print(f"\nPPS (Packets Per Second):")
            print(f"  Min: {min(pps_vals):>6} | Max: {max(pps_vals):>6} | Avg: {sum(pps_vals)/count:>7.2f}")
            print(f"  Unique: {len(set(pps_vals))}/{count} | Variance: {self._variance(pps_vals):.2f}")
            
            print(f"\nHeap Memory:")
            print(f"  Min: {min(heap_vals):>6} | Max: {max(heap_vals):>6} | Avg: {sum(heap_vals)/count:>7.2f}")
            print(f"  Unique: {len(set(heap_vals))}/{count} | Variance: {self._variance(heap_vals):.2f}")
            
            print(f"\nMotion Sensor Distribution:")
            motion_dist = Counter(motion_vals)
            for val in sorted(motion_dist.keys()):
                print(f"  Value {val}: {motion_dist[val]:>3} ({motion_dist[val]*100/count:>5.1f}%)")
            
            print(f"\nArm Status Distribution:")
            arm_dist = Counter(arm_vals)
            for val in sorted(arm_dist.keys()):
                print(f"  Value {val}: {arm_dist[val]:>3} ({arm_dist[val]*100/count:>5.1f}%)")
            
            # Detect duplicates
            unique_packets = set()
            duplicates = 0
            for p in packets:
                key = (p['pps'], p['heap'], p['motion'], p['arm'])
                if key in unique_packets:
                    duplicates += 1
                unique_packets.add(key)
            
            print(f"\nDuplicate Analysis:")
            print(f"  Unique packet types: {len(unique_packets)}/{count}")
            print(f"  Duplicate packets: {duplicates} ({duplicates*100/count:.1f}%)")
    
    def _variance(self, values):
        """Calculate variance"""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def detect_attack_type(self, dataset_name):
        """Infer attack type from dataset"""
        if dataset_name not in self.data or not self.data[dataset_name]:
            return "UNKNOWN"
        
        packets = self.data[dataset_name]
        pps_vals = [p['pps'] for p in packets]
        heap_vals = [p['heap'] for p in packets]
        
        # Calculate metrics
        avg_pps = sum(pps_vals) / len(pps_vals)
        avg_heap = sum(heap_vals) / len(heap_vals)
        pps_variance = self._variance(pps_vals)
        heap_variance = self._variance(heap_vals)
        
        # Count unique packets
        unique_packets = len(set((p['pps'], p['heap'], p['motion'], p['arm']) for p in packets))
        uniqueness_ratio = unique_packets / len(packets)
        
        # Decision logic
        if avg_pps > 100:
            return "DoS Attack (High PPS detected)"
        elif uniqueness_ratio < 0.1 and pps_variance < 5:
            return "Replay Attack (Low variance, high duplication)"
        elif avg_heap < 100000:
            return "Possible DoS/Memory Exhaustion"
        elif uniqueness_ratio > 0.9 and pps_variance > 50:
            return "Normal Behavior (High diversity)"
        else:
            return "Mixed/Unknown Pattern"
    
    def generate_full_report(self):
        """Generate comprehensive comparison report"""
        self.load_all_datasets()
        self.compare_all_attacks()
        self.analyze_dataset_metrics()
        
        self.print_header("🎯 ATTACK TYPE CLASSIFICATION")
        
        for name in self.data.keys():
            classification = self.detect_attack_type(name)
            print(f"\n{name.upper():.<40} {classification}")
        
        self.print_header("🛡️ DEFENSE RECOMMENDATIONS")
        print("""
1. TIMESTAMP VALIDATION
   ├─ Add timestamp to every packet
   ├─ Reject packets older than 30 seconds
   └─ Prevents replay attacks by time window

2. SEQUENCE NUMBERING
   ├─ Add sequence number to packets
   ├─ Track expected next sequence
   └─ Reject out-of-order packets

3. RATE LIMITING
   ├─ Set max packets per second
   ├─ Detect DoS attacks
   └─ Reject burst traffic

4. NONCE (Number Used Once)
   ├─ Server generates random nonce
   ├─ Client includes in response
   └─ Each nonce valid only once

5. CRYPTOGRAPHIC SIGNING
   ├─ Use HMAC-SHA256
   ├─ Verify message integrity
   └─ Detect tampering and replay

6. TLS/SSL ENCRYPTION
   ├─ Enable MQTT over TLS
   ├─ Session-based authentication
   └─ Provides confidentiality and integrity

7. ANOMALY DETECTION
   ├─ Monitor for unusual patterns
   ├─ Alert on statistical deviations
   └─ ML-based detection

8. DEVICE FINGERPRINTING
   ├─ Use device-unique identifiers
   ├─ MAC address, hardware serial
   └─ Prevent spoofing attacks
        """)
        
        self.print_header("📈 IMPLEMENTATION PRIORITY")
        print("""
🔴 CRITICAL (Implement First):
  1. Timestamp validation
  2. Rate limiting
  3. Input validation

🟡 IMPORTANT (Implement Second):
  4. Sequence numbering
  5. TLS encryption
  6. HMAC signing

🟢 NICE-TO-HAVE (Implement Third):
  7. Nonce generation
  8. Anomaly detection
  9. Device fingerprinting
        """)


def main():
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "🔐 IoT SECURITY - ATTACK COMPARISON TOOL" + " " * 17 + "║")
    print("╚" + "═" * 78 + "╝")
    
    comparator = AttackComparator()
    comparator.generate_full_report()
    
    print("\n" + "═" * 80)
    print("Report Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("═" * 80 + "\n")


if __name__ == "__main__":
    main()
