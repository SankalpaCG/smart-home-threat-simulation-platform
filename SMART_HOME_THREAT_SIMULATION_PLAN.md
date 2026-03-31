# Smart Home Threat Simulation Platform - Technical Analysis & Plan

## 📁 Project Structure Analysis
**Location:** `/mnt/c/Users/pirat/Desktop/codes/`

### Folder Structure:
```
codes/
├── Climate Hub (ESP32 #2)/
│   ├── sketch.ino          # Temperature/humidity monitoring with relay control
│   ├── diagram.json        # Wokwi circuit diagram
│   ├── libraries.txt       # PubSubClient, DHT sensor library
│   └── wokwi-project.txt   # Wokwi project metadata
├── Security Hub (ESP32 #1)/
│   ├── sketch.ino          # PIR motion detection with buzzer
│   ├── diagram.json        # Wokwi circuit diagram  
│   ├── libraries.txt       # PubSubClient
│   └── wokwi-project.txt   # Wokwi project metadata
├── Smart Lock Hub (ESP32 #3)/
│   ├── sketch.ino          # Servo-controlled smart lock
│   ├── diagram.json        # Wokwi circuit diagram
│   ├── libraries.txt       # PubSubClient, ESP32Servo
│   └── wokwi-project.txt   # Wokwi project metadata
└── Security_hub.ino        # Real-world implementation with actual WiFi credentials
```

## 🔍 Detailed Project Analysis

### **1. Climate Hub (ESP32 #2)**
- **Purpose**: Temperature/humidity monitoring and relay control
- **Components**: ESP32, DHT22 sensor, relay module
- **MQTT Topics**:
  - Publishes: `shtsp/home/climate/data` (temperature JSON)
  - Subscribes: `shtsp/home/climate/relay` (relay control commands)
- **Pins**: GPIO2 (relay), GPIO15 (DHT22)
- **Update Interval**: 5 seconds

### **2. Security Hub (ESP32 #1)**
- **Purpose**: Motion detection security system
- **Components**: ESP32, PIR sensor, buzzer
- **MQTT Topics**: 
  - Publishes: `shtsp/home/security/motion` (motion alerts)
- **Pins**: GPIO13 (PIR), GPIO12 (buzzer)
- **Broker**: Public HiveMQ (`broker.hivemq.com`)

### **3. Smart Lock Hub (ESP32 #3)**
- **Purpose**: Remote-controlled smart lock system
- **Components**: ESP32, servo motor, red/green LEDs
  - **MQTT Topics**:
  - Subscribes: `shtsp/home/lock/cmd` ("LOCK"/"UNLOCK" commands)
- **Pins**: GPIO14 (servo), GPIO25 (red LED), GPIO26 (green LED)
- **State Indicators**: Red = Locked, Green = Unlocked

### **4. Security_hub.ino (Standalone File)**
- **Critical Security Issue**: Contains hardcoded credentials:
  - SSID: "xxxx"
  - Password: "xxxxx"
  - MQTT Broker: `192.168.xx.xx` (local laptop IP)
- **Key Differences**: More robust reconnection logic, local broker

## 🚨 Critical Security & Technical Issues

### **HIGH PRIORITY ISSUES:**
1. **Exposed Credentials**: `Security_hub.ino` contains real WiFi/MQTT credentials
2. **Public MQTT Broker**: Using HiveMQ publicly (no authentication/encryption)
3. **No Error Handling**: Minimal reconnect/error recovery logic
4. **Inconsistent Architecture**: Mixed simulation/real-world implementations
5. **Lack of Security**: No TLS/SSL, no authentication, plaintext communication

### **MEDIUM PRIORITY ISSUES:**
1. **Hardcoded Configuration**: No environment/config management
2. **Limited Scalability**: Direct MQTT topics without namespace hierarchy
3. **No Monitoring**: Missing health checks and system status reporting
4. **Poor Logging**: Basic serial output only

## 💡 Threat Simulation Opportunities

### **Existing Vulnerabilities (Ready for Simulation):**
1. **MQTT Injection**: Unauthenticated public broker allows command injection
2. **Topic Hijacking**: Predictable topic naming allows spoofing
3. **DoS Attacks**: Flood MQTT topics to disrupt operations
4. **Credential Theft**: Hardcoded credentials in source code
5. **Replay Attacks**: Intercept and replay MQTT messages

### **Missing Security Layers to Simulate:**
1. **Authentication Bypass**: Simulate unauthorized access
2. **Firmware Tampering**: Attempt OTA update manipulation
3. **Physical Tampering**: GPIO pin manipulation attacks
4. **Protocol Exploitation**: MQTT protocol vulnerabilities
5. **Side-channel Attacks**: Power analysis, timing attacks

## 🎯 Recommended Architecture for Threat Simulation Platform

### **Phase 1: Foundation (Weeks 1-2)**
```
[ESP32 Devices] → [Local MQTT Broker] → [Threat Simulation Engine] → [Data Collector]
       ↓                  ↓                      ↓                       ↓
[Hardware Layer]  [Communication]      [Attack Simulation]       [Dataset Creation]
```

### **Phase 2: Advanced Simulation (Weeks 3-4)**
```
[Physical Devices] → [Secure Gateway] → [Hybrid Simulation Environment]
       ↓                   ↓                       ↓
[Real Hardware]    [Security Controls]   [Virtualized Devices]
                                     ↓
                             [Unified Data Pipeline]
                                     ↓
                           [Threat Intelligence DB]
```

## 🔧 Technical Recommendations

### **Immediate Actions (Week 1):**
1. **Remove/Encrypt Credentials**: Sanitize `Security_hub.ino`
2. **Local MQTT Broker**: Install Mosquitto on dedicated machine
3. **Network Segmentation**: Isolate test environment
4. **Version Control**: Initialize Git repository with `.gitignore`

### **Short-term Improvements (Week 2):**
1. **Configuration Management**: Use `config.h` with environment variables
2. **Unified Codebase**: Refactor three projects into modular architecture
3. **Security Baseline**: Add basic authentication to MQTT
4. **Monitoring Setup**: Implement Grafana/Prometheus dashboard

### **Long-term Strategy (Weeks 3-6):**
1. **Hybrid Simulation**: Combine Wokwi (virtual) + real hardware
2. **Automated Testing**: CI/CD pipeline for firmware validation
3. **Threat Library**: Catalog of IoT-specific attack vectors
4. **Dataset Schema**: Structured format for attack/benign data

## 📊 Dataset Creation Strategy

### **Data Collection Points:**
1. **MQTT Traffic**: All publish/subscribe messages with metadata
2. **Device Telemetry**: CPU usage, memory, network stats
3. **Sensor Readings**: Temperature, humidity, motion events
4. **Control Actions**: Relay, lock, buzzer activations
5. **Attack Artifacts**: Malformed packets, injection attempts

### **Dataset Structure:**
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "device_id": "esp32_climate_hub_001",
  "data_type": "sensor_reading|control_command|attack_payload",
  "payload": {...},
  "metadata": {
    "source_ip": "192.168.1.100",
    "destination": "shtsp/home/climate/data",
    "protocol": "mqtt",
    "encrypted": false,
    "attack_type": "null|injection|dos|spoofing"
  }
}
```

## 🎓 Academic Value Proposition

### **Research Contributions:**
1. **Real-world IoT Security Dataset**: Publicly available for research
2. **Hybrid Simulation Methodology**: Combining virtual/physical testing
3. **Threat Modeling Framework**: IoT-specific attack taxonomy
4. **Defense Evaluation**: Effectiveness of security controls

### **Expected Outcomes:**
1. **Conference Paper**: IoT security simulation platform
2. **Open Source Toolkit**: Threat simulation tools
3. **Educational Materials**: Lab exercises for cybersecurity courses
4. **Industry Partnerships**: Collaboration with IoT security firms

## 🚀 Next Steps

### **Week 1-2: Foundation**
- [ ] Sanitize existing codebase
- [ ] Set up local development environment
- [ ] Implement basic data collection
- [ ] Design threat simulation scenarios

### **Week 3-4: Simulation Development**
- [ ] Build attack injection framework
- [ ] Create hybrid simulation environment
- [ ] Develop dataset collection pipeline
- [ ] Implement basic analytics

### **Week 5-6: Refinement & Documentation**
- [ ] Validate simulation accuracy
- [ ] Optimize dataset quality
- [ ] Prepare documentation
- [ ] Plan demonstration

---

**Analysis Completed:** March 31, 2026  
**Analyst:** Cline AI Assistant  
**Project Scope:** Smart Home Threat Simulation Platform  
**Target:** College Project with Professional Implementation