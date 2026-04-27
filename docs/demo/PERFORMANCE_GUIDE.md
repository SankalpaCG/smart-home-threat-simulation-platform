# 📊 Performance Monitoring Guide

## Overview

The **replay attack simulator** now includes integrated performance monitoring that automatically tracks metrics during each attack and generates professional reports suitable for demonstrations.

---

## 📈 What Gets Measured

### Timing Metrics
- **Elapsed Time**: Total duration of the attack
- **Start/End Times**: Exact timestamps
- **Throughput**: Packets per second (pps)

### Packet Metrics
- **Total Packets Sent**: Number of replayed packets
- **Successful Packets**: How many sent successfully
- **Failed Packets**: Any transmission failures
- **Success Rate %**: Percentage of successful transmission

### Performance Metrics
- **Average Latency**: Network delay per packet (ms)
- **Throughput (pps)**: Attack intensity rate

### Detection Metrics
- **Detection Rate %**: How effectively the attack was detected
- **False Positive Rate %**: Incorrect attack classifications
- **Detection Methods**: Which detection techniques triggered

---

## 🎯 How to Use

### Run Attack with Performance Monitoring

```powershell
cd "C:\Users\Test\Downloads\Security_hub\Security_hub\Security_hub"
.\replay_attack.bat
```

**Then:**
1. Select attack mode (1-4)
2. Watch the attack execute
3. See the performance report automatically

### Run Detector with Monitoring

```powershell
.\replay_detector.bat
```

- Analyzes datasets
- Shows detection effectiveness
- Generates risk assessment

### Run Comparator with Monitoring

```powershell
.\attack_comparator.bat
```

- Compares attack types
- Shows performance differences
- Provides recommendations

---

## 📊 Output Examples

### Single Replay Attack Report

```
╔══════════════════════════════════════════════════════════╗
║       🎯 REPLAY ATTACK PERFORMANCE REPORT       ║
╚══════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────┐
│ Test Summary                                            │
├─────────────────────────────────────────────────────────┤
│ Test Name:           Replay Attack - Single Cycle       │
│ Duration:               3.90 seconds                     │
│ Status:              ✅ COMPLETED                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Attack Metrics                                          │
├─────────────────────────────────────────────────────────┤
│ Total Packets Sent:       38                            │
│ Successful Packets:       38 (100.0%)                   │
│ Failed Packets:            0                            │
│ Throughput:            9.74 packets/second             │
│ Avg Latency:          10.00 ms                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Detection Results                                       │
├─────────────────────────────────────────────────────────┤
│ Detection Rate:        95.0%                            │
│ False Positive Rate:    0.0%                            │
│ Detection Methods:        3                             │
│   1. Duplicate Packet Analysis                          │
│   2. Pattern Repetition Detection                       │
│   3. Statistical Variance Analysis                      │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Generated Files

After each attack, the following files are generated:

### 1. **replay_attack_report.json**
Raw performance metrics in JSON format
```json
{
  "test_name": "Replay Attack - Single Cycle",
  "packets_sent": 38,
  "successful_packets": 38,
  "success_rate_percent": 100.0,
  "throughput_pps": 9.74,
  "elapsed_time_seconds": 3.90,
  "detection_rate": 95.0,
  "average_latency_ms": 10.0,
  "timestamp": "2026-04-27T13:45:23.123456"
}
```

### 2. **performance_report.html** (Optional)
Beautiful HTML dashboard for presentations
- Visual metrics
- Charts and graphs
- Professional formatting

---

## 🔧 Demo Mode Features

When `DEMO_MODE = True`, the simulator:
✅ Hides debug information  
✅ Shows clean output only  
✅ Displays formatted tables  
✅ Generates professional reports  
✅ Suppresses warnings  
✅ Focuses on key metrics

**To Enable Demo Mode:**
```python
# In replay_attack.py
DEMO_MODE = True  # Professional output
```

**To Enable Verbose Mode:**
```python
# In replay_attack.py
DEMO_MODE = False  # Debug output
```

---

## 📊 Comparison Reports

### Performance by Attack Type

| Metric | Normal | DoS | Replay |
|--------|--------|-----|--------|
| **Packets Sent** | N/A | 100-1000 | 38-50 |
| **Throughput** | N/A | 100+ pps | 10 pps |
| **Detection Rate** | N/A | 99% | 95% |
| **False Positives** | N/A | 1% | 0% |

### Key Insights

**Replay Attack Performance:**
- ✅ Low throughput (stealthy)
- ✅ High detection rate (patterns obvious)
- ✅ Low false positives (accurate detection)
- ⚠️  Time-based attacks easier to detect

**DoS Attack Performance:**
- ⚠️  High throughput (destructive)
- ✅ Very high detection rate
- ⚠️  Can overwhelm system
- ✅ Easy to detect and stop

---

## 🎬 Demo Workflow

### 1. Setup (1 minute)
```powershell
# Navigate to project
cd "C:\Users\Test\Downloads\Security_hub\Security_hub\Security_hub"

# Ensure MQTT broker is running
# mosquitto (separate terminal)
```

### 2. Run Attack (5 minutes)
```powershell
# Run replay attack
.\replay_attack.bat

# Select: 1 (Single replay)
# Shows clean performance output
```

### 3. Analyze Results (2 minutes)
```powershell
# Show generated report
type replay_attack_report.json

# Or run detector
.\replay_detector.bat
```

### 4. Compare Attacks (3 minutes)
```powershell
# Show comparisons
.\attack_comparator.bat
```

**Total Demo Time: ~11 minutes** ✅

---

## 📈 Key Metrics Explained

### Success Rate %
- **Ideal**: 100% (all packets transmitted)
- **Good**: 95%+
- **Poor**: <90%

### Throughput (pps)
- **Replay Attack**: ~10 pps (stealthy)
- **DoS Attack**: 100+ pps (aggressive)
- **Normal**: Variable

### Detection Rate %
- **Excellent**: >95%
- **Good**: 80-95%
- **Fair**: 60-80%
- **Poor**: <60%

### False Positive Rate %
- **Excellent**: 0%
- **Good**: <2%
- **Fair**: 2-5%
- **Poor**: >5%

---

## 🚀 For Presentations

### Export Data
```powershell
# Generate JSON report (automatic)
# File: replay_attack_report.json

# View metrics
Get-Content replay_attack_report.json | ConvertFrom-Json | Format-List
```

### Create Slides
```
Slide 1: Title - "Replay Attack Demo"
Slide 2: Show performance metrics
Slide 3: Detection analysis
Slide 4: Comparison with other attacks
Slide 5: Recommendations
```

### Key Points to Highlight
1. **Low throughput** = Stealthy attack
2. **Identical packets** = Easy to detect
3. **Zero variance** = Statistical signatures
4. **Pattern repetition** = Machine detectable
5. **Defense strategies** = Timestamps + nonces

---

## ⚙️ Customization

### Change Delay Between Packets
```python
# In replay_attack.py
attacker.replay_once(packets, delay=0.05)  # Faster
attacker.replay_once(packets, delay=0.5)   # Slower
```

### Adjust Packet Count
```python
attacker.random_replay(packets, count=100)  # More packets
attacker.random_replay(packets, count=20)   # Fewer packets
```

### Modify Output Format
Edit `performance_monitor.py`:
```python
def print_demo_summary(self):
    # Customize the output here
    # Change formatting, colors, metrics displayed
```

---

## 🔐 Demo Safety

✅ **Safe to Run:**
- Only affects MQTT broker
- No system-wide changes
- Can be stopped anytime (Ctrl+C)
- Non-destructive testing

⚠️ **Prerequisites:**
- MQTT broker must be running
- Python 3.14+
- paho-mqtt library installed
- Dataset files present

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Run attack | `.\replay_attack.bat` |
| Detect attack | `.\replay_detector.bat` |
| Compare types | `.\attack_comparator.bat` |
| View report | `Get-Content replay_attack_report.json` |
| Clean output | Set `DEMO_MODE = True` |
| Verbose output | Set `DEMO_MODE = False` |

---

**Ready for Demo! 🎉**
