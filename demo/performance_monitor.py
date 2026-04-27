#!/usr/bin/env python3
"""
Replay Attack Performance Monitor
Tracks and displays metrics for replay attack demonstrations
"""

import time
import json
import os
from datetime import datetime
from collections import defaultdict

class PerformanceMonitor:
    def __init__(self, output_file="performance_report.json"):
        self.output_file = output_file
        self.metrics = {
            'test_name': '',
            'start_time': None,
            'end_time': None,
            'packets_sent': 0,
            'packets_received': 0,
            'successful_packets': 0,
            'failed_packets': 0,
            'average_latency_ms': 0,
            'throughput_pps': 0,  # Packets Per Second
            'detection_rate': 0,
            'false_positive_rate': 0,
            'elapsed_time_seconds': 0,
            'success_rate_percent': 0,
            'detection_methods_triggered': []
        }
        self.latencies = []
    
    def start_test(self, test_name):
        """Start timing a test"""
        self.metrics['test_name'] = test_name
        self.metrics['start_time'] = time.time()
        print(f"\n{'=' * 70}")
        print(f"📊 PERFORMANCE TEST: {test_name}")
        print(f"{'=' * 70}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 70}\n")
    
    def end_test(self):
        """End timing the test"""
        self.metrics['end_time'] = time.time()
        self.metrics['elapsed_time_seconds'] = self.metrics['end_time'] - self.metrics['start_time']
        
        # Calculate derived metrics
        if self.metrics['packets_sent'] > 0:
            self.metrics['success_rate_percent'] = (self.metrics['successful_packets'] / self.metrics['packets_sent']) * 100
            self.metrics['throughput_pps'] = self.metrics['packets_sent'] / self.metrics['elapsed_time_seconds']
        
        if len(self.latencies) > 0:
            self.metrics['average_latency_ms'] = sum(self.latencies) / len(self.latencies)
    
    def add_packet_sent(self, success=True, latency_ms=0):
        """Record a sent packet"""
        self.metrics['packets_sent'] += 1
        if success:
            self.metrics['successful_packets'] += 1
            if latency_ms > 0:
                self.latencies.append(latency_ms)
        else:
            self.metrics['failed_packets'] += 1
    
    def add_detection(self, method_name):
        """Record a detection method triggered"""
        if method_name not in self.metrics['detection_methods_triggered']:
            self.metrics['detection_methods_triggered'].append(method_name)
    
    def set_detection_rate(self, rate):
        """Set detection rate (0-100)"""
        self.metrics['detection_rate'] = rate
    
    def set_false_positive_rate(self, rate):
        """Set false positive rate (0-100)"""
        self.metrics['false_positive_rate'] = rate
    
    def print_summary(self):
        """Print performance summary"""
        self.end_test()
        
        print("\n" + "=" * 70)
        print("📈 PERFORMANCE METRICS")
        print("=" * 70)
        
        print(f"\n⏱️  TIMING METRICS:")
        print(f"  Elapsed Time:        {self.metrics['elapsed_time_seconds']:.2f} seconds")
        print(f"  Start Time:          {datetime.fromtimestamp(self.metrics['start_time']).strftime('%H:%M:%S')}")
        print(f"  End Time:            {datetime.fromtimestamp(self.metrics['end_time']).strftime('%H:%M:%S')}")
        
        print(f"\n📦 PACKET METRICS:")
        print(f"  Packets Sent:        {self.metrics['packets_sent']:>6}")
        print(f"  Successful:          {self.metrics['successful_packets']:>6}")
        print(f"  Failed:              {self.metrics['failed_packets']:>6}")
        print(f"  Success Rate:        {self.metrics['success_rate_percent']:>6.1f}%")
        
        print(f"\n🚀 THROUGHPUT:")
        print(f"  Packets/Second:      {self.metrics['throughput_pps']:>6.2f} pps")
        print(f"  Avg Latency:         {self.metrics['average_latency_ms']:>6.2f} ms")
        
        print(f"\n🛡️  DETECTION METRICS:")
        print(f"  Detection Rate:      {self.metrics['detection_rate']:>6.1f}%")
        print(f"  False Positives:     {self.metrics['false_positive_rate']:>6.1f}%")
        if self.metrics['detection_methods_triggered']:
            print(f"  Methods Triggered:")
            for method in self.metrics['detection_methods_triggered']:
                print(f"    ✓ {method}")
        
        print("\n" + "=" * 70)
        self.save_report()
    
    def save_report(self):
        """Save metrics to JSON file"""
        self.metrics['timestamp'] = datetime.now().isoformat()
        try:
            with open(self.output_file, 'w') as f:
                json.dump(self.metrics, f, indent=2, default=str)
            print(f"📄 Report saved to: {self.output_file}\n")
        except Exception as e:
            print(f"❌ Error saving report: {e}\n")
    
    def print_demo_summary(self):
        """Print clean summary for demo purposes"""
        self.end_test()
        
        print("\n" + "╔" + "═" * 68 + "╗")
        print("║" + " " * 20 + "🎯 REPLAY ATTACK PERFORMANCE REPORT" + " " * 14 + "║")
        print("╚" + "═" * 68 + "╝")
        
        print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│ Test Summary                                                        │
├─────────────────────────────────────────────────────────────────────┤
│ Test Name:           {self.metrics['test_name']:<45} │
│ Duration:            {self.metrics['elapsed_time_seconds']:>6.2f} seconds{'':<37} │
│ Status:              {'✅ COMPLETED' if self.metrics['success_rate_percent'] > 80 else '⚠️  PARTIAL':<45} │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ Attack Metrics                                                      │
├─────────────────────────────────────────────────────────────────────┤
│ Total Packets Sent:  {self.metrics['packets_sent']:>6}{'':<40} │
│ Successful Packets:  {self.metrics['successful_packets']:>6} ({self.metrics['success_rate_percent']:>5.1f}%){'':<29} │
│ Failed Packets:      {self.metrics['failed_packets']:>6}{'':<40} │
│ Throughput:          {self.metrics['throughput_pps']:>6.2f} packets/second{'':<25} │
│ Avg Latency:         {self.metrics['average_latency_ms']:>6.2f} ms{'':<40} │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ Detection Results                                                   │
├─────────────────────────────────────────────────────────────────────┤
│ Detection Rate:      {self.metrics['detection_rate']:>6.1f}%{'':<40} │
│ False Positive Rate: {self.metrics['false_positive_rate']:>6.1f}%{'':<40} │
│ Detection Methods:   {len(self.metrics['detection_methods_triggered'])}{'':<45} │
""")
        
        if self.metrics['detection_methods_triggered']:
            for i, method in enumerate(self.metrics['detection_methods_triggered'], 1):
                print(f"│   {i}. {method:<60} │")
        
        print("└─────────────────────────────────────────────────────────────────────┘")
        print()
        self.save_report()


def generate_demo_report(test_results):
    """Generate a demo-ready HTML report"""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Replay Attack Performance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        h1 {{ color: #c41e3a; text-align: center; }}
        .metrics {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
        .metric-box {{ background: #f9f9f9; padding: 15px; border-left: 4px solid #c41e3a; }}
        .metric-label {{ font-weight: bold; color: #333; }}
        .metric-value {{ font-size: 24px; color: #c41e3a; margin-top: 5px; }}
        .success {{ color: #22c55e; }}
        .warning {{ color: #f59e0b; }}
        .error {{ color: #c41e3a; }}
        .timestamp {{ text-align: center; color: #999; margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f3f4f6; font-weight: bold; }}
        tr:hover {{ background: #f9fafb; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Replay Attack Performance Report</h1>
        
        <div class="metrics">
            <div class="metric-box">
                <div class="metric-label">Total Packets Sent</div>
                <div class="metric-value">{test_results.metrics['packets_sent']}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value success">{test_results.metrics['success_rate_percent']:.1f}%</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Throughput</div>
                <div class="metric-value">{test_results.metrics['throughput_pps']:.2f} pps</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Detection Rate</div>
                <div class="metric-value warning">{test_results.metrics['detection_rate']:.1f}%</div>
            </div>
        </div>
        
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Elapsed Time</td>
                <td>{test_results.metrics['elapsed_time_seconds']:.2f} seconds</td>
            </tr>
            <tr>
                <td>Successful Packets</td>
                <td>{test_results.metrics['successful_packets']}</td>
            </tr>
            <tr>
                <td>Failed Packets</td>
                <td>{test_results.metrics['failed_packets']}</td>
            </tr>
            <tr>
                <td>Average Latency</td>
                <td>{test_results.metrics['average_latency_ms']:.2f} ms</td>
            </tr>
            <tr>
                <td>False Positive Rate</td>
                <td>{test_results.metrics['false_positive_rate']:.1f}%</td>
            </tr>
        </table>
        
        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
    return html_content


if __name__ == "__main__":
    # Example usage
    monitor = PerformanceMonitor()
    monitor.start_test("Replay Attack - Single Cycle")
    
    # Simulate some packet sends
    for i in range(38):
        monitor.add_packet_sent(success=True, latency_ms=10 + (i % 5))
        time.sleep(0.1)
    
    # Add detection results
    monitor.set_detection_rate(95.0)
    monitor.set_false_positive_rate(0.0)
    monitor.add_detection("Duplicate Packet Analysis")
    monitor.add_detection("Pattern Repetition Detection")
    monitor.add_detection("Statistical Variance Analysis")
    
    monitor.print_demo_summary()
