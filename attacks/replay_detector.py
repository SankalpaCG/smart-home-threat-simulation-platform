import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LABELED_DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset", "labeled")

# ==========================================
# REPLAY ATTACK DETECTION ANALYSIS
# ==========================================

class ReplayDetector:
    def __init__(self, dataset_file):
        self.dataset_file = dataset_file
        self.packets = []
        self.load_data()
    
    def load_data(self):
        """Load data from CSV file"""
        try:
            with open(self.dataset_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.packets.append({
                        'pps': float(row['pps']),
                        'heap': int(row['heap']),
                        'motion': int(row['motion']),
                        'arm': int(row['arm']),
                        'label': int(row['label'])
                    })
            print(f"✅ Loaded {len(self.packets)} packets from {self.dataset_file}")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
    
    def detect_duplicate_packets(self):
        """Detect identical consecutive packets (strong indicator of replay)"""
        print("\n" + "=" * 60)
        print("🔍 DETECTION #1: DUPLICATE PACKET ANALYSIS")
        print("=" * 60)
        
        duplicates = []
        for i in range(len(self.packets) - 1):
            current = self.packets[i]
            next_pkt = self.packets[i + 1]
            
            # Check if packets are identical
            if (current['pps'] == next_pkt['pps'] and 
                current['heap'] == next_pkt['heap'] and
                current['motion'] == next_pkt['motion'] and
                current['arm'] == next_pkt['arm']):
                duplicates.append((i, current))
        
        if duplicates:
            print(f"⚠️  Found {len(duplicates)} consecutive duplicate packets!")
            print("\nExample duplicates:")
            for idx, pkt in duplicates[:5]:
                print(f"   Packet {idx}: PPS={pkt['pps']}, Heap={pkt['heap']}, Motion={pkt['motion']}, Arm={pkt['arm']}")
            if len(duplicates) > 5:
                print(f"   ... and {len(duplicates) - 5} more")
        else:
            print("✅ No duplicate packets found (low replay risk)")
        
        return len(duplicates) > 0
    
    def detect_pattern_repetition(self):
        """Detect repeated sequences (another replay indicator)"""
        print("\n" + "=" * 60)
        print("🔍 DETECTION #2: PATTERN REPETITION ANALYSIS")
        print("=" * 60)
        
        # Look for sequences of 5 identical packets
        sequence_length = 5
        sequences = defaultdict(int)
        
        for i in range(len(self.packets) - sequence_length):
            seq = tuple([
                (self.packets[i+j]['pps'], 
                 self.packets[i+j]['heap'],
                 self.packets[i+j]['motion'],
                 self.packets[i+j]['arm'])
                for j in range(sequence_length)
            ])
            sequences[seq] += 1
        
        suspicious = {seq: count for seq, count in sequences.items() if count > 1}
        
        if suspicious:
            print(f"⚠️  Found {len(suspicious)} repeated sequences!")
            print("\nMost suspicious sequence patterns:")
            sorted_seq = sorted(suspicious.items(), key=lambda x: x[1], reverse=True)
            for seq, count in sorted_seq[:3]:
                print(f"   Pattern repeated {count} times:")
                print(f"   {seq}")
        else:
            print("✅ No significant pattern repetition detected")
        
        return len(suspicious) > 0
    
    def analyze_statistical_anomalies(self):
        """Detect statistical anomalies that indicate replayed traffic"""
        print("\n" + "=" * 60)
        print("🔍 DETECTION #3: STATISTICAL ANALYSIS")
        print("=" * 60)
        
        pps_values = [p['pps'] for p in self.packets]
        heap_values = [p['heap'] for p in self.packets]
        motion_values = [p['motion'] for p in self.packets]
        arm_values = [p['arm'] for p in self.packets]
        
        # Calculate statistics
        print("\n📊 PACKET STATISTICS:")
        print(f"\nPPS (Packets Per Second):")
        print(f"  Min: {min(pps_values)}, Max: {max(pps_values)}, Avg: {sum(pps_values)/len(pps_values):.2f}")
        print(f"  Unique values: {len(set(pps_values))}/{len(pps_values)}")
        
        print(f"\nHeap Memory:")
        print(f"  Min: {min(heap_values)}, Max: {max(heap_values)}, Avg: {sum(heap_values)/len(heap_values):.2f}")
        print(f"  Unique values: {len(set(heap_values))}/{len(heap_values)}")
        
        print(f"\nMotion Sensor:")
        print(f"  Unique values: {len(set(motion_values))}/{len(motion_values)}")
        print(f"  Distribution: {dict(Counter(motion_values))}")
        
        print(f"\nArm Status:")
        print(f"  Unique values: {len(set(arm_values))}/{len(arm_values)}")
        print(f"  Distribution: {dict(Counter(arm_values))}")
        
        # Low variance = suspicious (replayed traffic often has identical or very similar values)
        pps_variance = self._calculate_variance(pps_values)
        heap_variance = self._calculate_variance(heap_values)
        
        print(f"\n⚠️  VARIANCE ANALYSIS (lower = more suspicious):")
        print(f"  PPS Variance: {pps_variance:.2f}")
        print(f"  Heap Variance: {heap_variance:.2f}")
        
        if pps_variance < 10 and heap_variance < 100:
            print("\n  ⚠️  Low variance detected - potential replay attack!")
            return True
        else:
            print("\n  ✅ Variance appears normal")
            return False
    
    def _calculate_variance(self, values):
        """Calculate variance of values"""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def detect_timing_anomalies(self):
        """Detect timing issues in replayed packets"""
        print("\n" + "=" * 60)
        print("🔍 DETECTION #4: TIMING ANOMALIES")
        print("=" * 60)
        
        print("\n📝 TIMING PATTERNS:")
        print("  In real systems, packets arrive at varying intervals")
        print("  In replay attacks, packets often arrive in bursts or with regular timing")
        print("  Since we don't have timestamps in the CSV, we analyze packet ordering")
        
        # Check for patterns that suggest all data came at once (replay)
        print(f"\n  Total packets: {len(self.packets)}")
        print(f"  If replayed quickly: All packets arrive within milliseconds")
        print(f"  If legitimate: Packets spread over time with natural delays")
        
        # Detect periods of identical values
        identical_streaks = 0
        current_streak = 1
        
        for i in range(len(self.packets) - 1):
            if (self.packets[i]['pps'] == self.packets[i+1]['pps'] and
                self.packets[i]['heap'] == self.packets[i+1]['heap'] and
                self.packets[i]['motion'] == self.packets[i+1]['motion'] and
                self.packets[i]['arm'] == self.packets[i+1]['arm']):
                current_streak += 1
            else:
                if current_streak > 3:
                    identical_streaks += 1
                current_streak = 1
        
        if identical_streaks > 5:
            print(f"\n  ⚠️  Found {identical_streaks} long streaks of identical packets!")
            print("     This is highly suspicious of replay attacks")
            return True
        else:
            print(f"\n  ✅ No suspicious timing patterns detected")
            return False
    
    def generate_detection_report(self):
        """Generate comprehensive detection report"""
        print("\n" + "=" * 80)
        print("🛡️  REPLAY ATTACK DETECTION REPORT")
        print("=" * 80)
        
        findings = []
        findings.append(("Duplicate Packets", self.detect_duplicate_packets()))
        findings.append(("Pattern Repetition", self.detect_pattern_repetition()))
        findings.append(("Statistical Anomalies", self.analyze_statistical_anomalies()))
        findings.append(("Timing Anomalies", self.detect_timing_anomalies()))
        
        print("\n" + "=" * 80)
        print("📋 DETECTION SUMMARY")
        print("=" * 80)
        
        risk_count = sum(1 for _, detected in findings if detected)
        
        for test_name, detected in findings:
            status = "⚠️  SUSPICIOUS" if detected else "✅ NORMAL"
            print(f"{test_name:.<40} {status}")
        
        print("\n" + "=" * 80)
        if risk_count >= 2:
            print(f"🚨 HIGH RISK: Likely replay attack detected! ({risk_count}/4 indicators)")
        elif risk_count == 1:
            print(f"⚠️  MEDIUM RISK: Some suspicious patterns detected ({risk_count}/4 indicators)")
        else:
            print(f"✅ LOW RISK: No replay attack indicators detected")
        print("=" * 80)


def main():
    print("=" * 80)
    print("🛡️  REPLAY ATTACK DETECTION TOOL")
    print("=" * 80)
    
    # Analyze both datasets
    datasets = [
        os.path.join(LABELED_DATASET_DIR, "dataset_Normal.csv"),
        os.path.join(LABELED_DATASET_DIR, "dataset_DoS.csv"),
    ]
    
    for dataset in datasets:
        if os.path.exists(dataset):
            print(f"\n\n{'=' * 80}")
            print(f"Analyzing: {dataset}")
            print(f"{'=' * 80}")
            detector = ReplayDetector(dataset)
            detector.generate_detection_report()
        else:
            print(f"\n⚠️  {dataset} not found")


if __name__ == "__main__":
    main()
