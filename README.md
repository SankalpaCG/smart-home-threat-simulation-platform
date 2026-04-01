# Smart Home Threat Simulation Platform

## 🏠 Project Overview

This is a **Capstone project** focusing on creating a **Smart Home Threat Simulation Platform** using ESP32 microcontrollers. The platform combines real hardware with simulation to create a comprehensive IoT security testing environment for generating security datasets and evaluating threat detection mechanisms.

### **Project Vision**
To build a hybrid (virtual + physical) IoT security testing platform that:
1. Simulates real-world smart home attacks
2. Generates labeled security datasets for research
3. Evaluates defense mechanisms
4. Provides educational value for IoT security

---

## 📁 Current Project Structure

```
codes/
├── Climate Hub (ESP32 #2)/          # Temperature/humidity monitoring with relay control
├── Security Hub (ESP32 #1)/         # PIR motion detection with buzzer
├── Smart Lock Hub (ESP32 #3)/       # Servo-controlled smart lock system
├── Security_hub.ino                 # Real-world implementation (with credentials)
├── SMART_HOME_THREAT_SIMULATION_PLAN.md  # Detailed technical analysis & plan
└── README.md                        # This file
```

### **Device Specifications:**

| Device | Purpose | Components | MQTT Topics |
|--------|---------|------------|-------------|
| **Climate Hub** | Environmental monitoring | ESP32, DHT22, Relay | `shtsp/home/climate/*` |
| **Security Hub** | Motion detection | ESP32, PIR Sensor, Buzzer | `shtsp/home/security/*` |
| **Smart Lock Hub** | Access control | ESP32, Servo, LEDs | `shtsp/home/lock/*` |

---

## 🎯 **Hybrid Approach: Wokwi + Real Hardware**

### **Why Hybrid?**
1. **Cost Efficiency**: Virtual simulation reduces hardware costs
2. **Scalability**: Run multiple virtual devices simultaneously
3. **Rapid Prototyping**: Test ideas in Wokwi before hardware implementation
4. **Reproducibility**: Consistent test environments
5. **Safety**: Test dangerous attacks virtually first

### **Proposed Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    HYBRID SIMULATION PLATFORM                │
├──────────────┬──────────────────────┬───────────────────────┤
│  VIRTUAL     │      HYBRID LAYER    │      PHYSICAL         │
│  SIMULATION  │                      │      HARDWARE         │
├──────────────┼──────────────────────┼───────────────────────┤
│ • Wokwi      │ • Unified MQTT Broker│ • ESP32 Devices       │
│ • QEMU       │ • Threat Injection   │ • Real Sensors        │
│ • Containers │ • Data Normalization │ • Actuators           │
│ • Emulators  │ • Protocol Translation│ • Physical Interfaces │
└──────────────┴──────────────────────┴───────────────────────┘
                            │
                    ┌───────┴────────┐
                    │ UNIFIED DATA   │
                    │ PIPELINE       │
                    └───────┬────────┘
                            │
                    ┌───────┴────────┐
                    │ SECURITY       │
                    │ DATASET        │
                    └────────────────┘
```

---

## 🔧 **Professional Tool Stack Recommendation**

### **1. Development & Simulation**
- **Arduino IDE**: Primary development environment for ESP32 programming (recommended)
- **Wokwi**: Virtual IoT simulation (already in use)
- **Visual Studio Code with Arduino Extension**: Alternative IDE option
- **Docker**: Containerized simulation environments
- **QEMU**: Hardware emulation for consistency

### **2. Communication & Middleware**
- **Mosquitto MQTT Broker**: Local, secure MQTT implementation
- **Node-RED**: Visual programming for data flows
- **Apache Kafka**: High-throughput data streaming (advanced)
- **ZeroMQ**: Alternative for high-performance messaging

### **3. Security & Monitoring**
- **Wireshark**: Network traffic analysis
- **Suricata**: Network intrusion detection
- **Elastic Stack**: Log aggregation and analysis
- **Grafana + Prometheus**: Real-time monitoring dashboards

### **4. Data Management**
- **PostgreSQL/TimescaleDB**: Time-series data storage
- **MongoDB**: Flexible document storage for attack patterns
- **MinIO**: Object storage for large datasets
- **Apache Parquet**: Efficient dataset storage format

### **5. Automation & CI/CD**
- **GitHub Actions/GitLab CI**: Automated testing pipelines
- **Terraform**: Infrastructure as Code (IaC)
- **Ansible**: Configuration management
- **Jenkins**: Advanced CI/CD workflows

---

## 📊 **Dataset Creation Methodology**

### **Data Collection Strategy:**
1. **Multi-layer Collection**:
   - Network traffic (PCAP files)
   - MQTT messages (JSON logs)
   - Device telemetry (CPU, memory, network stats)
   - Sensor readings (structured time-series)

2. **Labeling Approach**:
   ```yaml
   attack_types:
     - mqtt_injection
     - topic_hijacking
     - dos_attack
     - credential_theft
     - replay_attack
     - firmware_tampering
     
   labels:
     - benign
     - malicious
     - attack_type: <specific_type>
     - severity: [low, medium, high, critical]
   ```

3. **Dataset Structure**:
   ```
   dataset/
   ├── raw/
   │   ├── network_traffic/
   │   ├── mqtt_logs/
   │   ├── device_telemetry/
   │   └── sensor_data/
   ├── processed/
   │   ├── normalized/
   │   ├── labeled/
   │   └── features/
   ├── splits/
   │   ├── train/
   │   ├── validation/
   │   └── test/
   └── metadata/
       ├── schema.json
       ├── statistics.json
       └── documentation.md
   ```

---

## 🚀 **Implementation Roadmap**

### **Phase 1: Foundation (2 Weeks)**
1. **Environment Setup**:
   - Install Arduino IDE + VS Code/Arduino IDE
   - Set up local Mosquitto broker
   - Create Git repository with proper structure
   - Implement configuration management

2. **Code Sanitization**:
   - Remove hardcoded credentials
   - Standardize code structure
   - Add security baseline
   - Implement proper error handling

### **Phase 2: Hybrid Layer (3 Weeks)**
1. **Unified Communication**:
   - Create abstraction layer for virtual/physical devices
   - Implement protocol translation
   - Build threat injection framework

2. **Data Pipeline**:
   - Set up data collection from all sources
   - Implement real-time processing
   - Create storage infrastructure

### **Phase 3: Simulation Scenarios (2 Weeks)**
1. **Attack Library**:
   - Develop 10+ IoT-specific attack vectors
   - Create reproducible attack scenarios
   - Build defense testing framework

2. **Validation**:
   - Test simulation accuracy
   - Validate dataset quality
   - Performance benchmarking

### **Phase 4: Analysis & Documentation (1 Week)**
1. **Results Analysis**:
   - Generate insights from collected data
   - Create visualizations and reports
   - Prepare academic paper outline

2. **Documentation**:
   - Complete technical documentation
   - Create user/developer guides
   - Prepare demonstration materials

---

## 🎓 **Academic Contributions**

### **Expected Outcomes:**
1. **Research Paper**: "Hybrid IoT Security Simulation Platform"
2. **Open Dataset**: Publicly available labeled IoT security dataset
3. **Toolkit**: Open-source threat simulation framework
4. **Educational Materials**: Lab exercises and tutorials

### **Research Questions:**
1. How effective are current IoT security measures against sophisticated attacks?
2. Can hybrid simulation accurately represent real-world threat scenarios?
3. What are the most critical vulnerabilities in consumer IoT devices?
4. How can machine learning improve IoT threat detection?

### **Innovation Points:**
1. **First hybrid IoT security dataset** combining virtual and physical data
2. **Novel attack simulation framework** for IoT ecosystems
3. **Reproducible testing methodology** for IoT security research
4. **Educational platform** for hands-on IoT security training

---

## 🔐 **Security Considerations**

### **Immediate Actions:**
1. **Remove exposed credentials** from `Security_hub.ino`
2. **Isolate test network** from production systems
3. **Implement basic authentication** for MQTT
4. **Enable TLS encryption** for all communications

### **Long-term Security:**
1. **Secure boot** and **encrypted firmware updates**
2. **Hardware security modules** (optional)
3. **Regular security audits** and penetration testing
4. **Compliance with IoT security standards**

---

## 🤝 **Collaboration & Contribution**

### **Team Roles & Responsibilities (5 Members):**

| Member | Role | Primary Responsibilities | Secondary Responsibilities |
|--------|------|--------------------------|----------------------------|
| **Sankalpa Ghimire** | **Hardware & Firmware Lead** | ESP32 programming, circuit design, sensor integration, hardware testing, power management, physical security | Device provisioning, component sourcing, PCB design (if needed), hardware documentation |
| **Deepak Sharma** | **Software & Backend Lead** | MQTT broker setup, API development, data pipeline architecture, database management, system integration | DevOps, containerization (Docker), CI/CD pipelines, system monitoring, backend documentation |
| **Amir Kumar pachhai** | **Security & Attack Simulation Lead** | Threat modeling, attack vector development, penetration testing, security analysis, defense mechanism testing | Vulnerability assessment, security documentation, compliance checking, risk analysis |
| **Sadikshya Dahal** | **Data Science & ML Lead** | Dataset creation, data preprocessing, feature engineering, ML model development, statistical analysis | Data visualization, model evaluation, algorithm optimization, research paper writing |
| **Shashi Simkhada** | **Frontend & Visualization Lead** | Dashboard development, real-time monitoring UI, data visualization, user interface design, documentation portal | User experience testing, report generation tools, demo preparation, presentation materials |

#### **Detailed Task Distribution:**

**Phase 1: Foundation (2 Weeks) - All Members**
- **Sankalpa Ghimire**: Arduino IDE setup, ESP32 code sanitization, hardware configuration
- **Deepak Sharma**: Mosquitto broker installation, Git repository setup, CI/CD configuration
- **Amir Kumar pachhai**: Security baseline implementation, credential management system
- **Sadikshya Dahal**: Data collection framework design, initial dataset schema
- **Shashi Simkhada**: Project documentation portal, basic monitoring dashboard

**Phase 2: Hybrid Layer (3 Weeks)**
- **Sankalpa Ghimire**: Virtual/physical device abstraction layer, protocol translation
- **Deepak Sharma**: Unified MQTT broker configuration, real-time processing pipeline
- **Amir Kumar pachhai**: Threat injection framework, attack scenario development (5+ vectors)
- **Sadikshya Dahal**: Data storage infrastructure, normalization algorithms
- **Shashi Simkhada**: Hybrid simulation visualization, attack timeline UI

**Phase 3: Simulation Scenarios (2 Weeks)**
- **Sankalpa Ghimire**: Attack hardware integration, physical tampering simulations
- **Deepak Sharma**: Automated testing framework, performance benchmarking
- **Amir Kumar pachhai**: 10+ IoT-specific attack library, defense testing framework
- **Sadikshya Dahal**: Dataset labeling system, quality validation metrics
- **Shashi Simkhada**: Real-time attack visualization, security alert dashboard

**Phase 4: Analysis & Documentation (1 Week)**
- **Sankalpa Ghimire**: Hardware performance report, power consumption analysis
- **Deepak Sharma**: System scalability analysis, bottleneck identification
- **Amir Kumar pachhai**: Security effectiveness report, vulnerability summary
- **Sadikshya Dahal**: Dataset insights, ML model performance, research paper draft
- **Shashi Simkhada**: Final presentation, demo video, user documentation

#### **Cross-functional Collaboration:**
- **Weekly sync meetings** to coordinate between hardware, software, and security teams
- **Pair programming sessions** for critical integrations (e.g., hardware-software interface)
- **Code reviews** with at least 2 members from different specialties
- **Documentation rotation** where each member documents another's work weekly

#### **Success Metrics per Role:**
- **Sankalpa Ghimire (Hardware)**: 100% device reliability, <1% hardware failure rate
- **Deepak Sharma (Software)**: 99.9% system uptime, <100ms processing latency
- **Amir Kumar pachhai (Security)**: 95% attack detection rate, <5 false positives/day
- **Sadikshya Dahal (Data)**: 10,000+ labeled samples, >90% model accuracy
- **Shashi Simkhada (Frontend)**: <3s page load, 100% user task completion rate

### **Getting Started:**
1. Clone the repository
2. Review `SMART_HOME_THREAT_SIMULATION_PLAN.md`
3. Set up development environment
4. Start with Phase 1 tasks

### **Contribution Guidelines:**
1. Follow Git workflow with feature branches
2. Document all changes thoroughly
3. Test changes in both virtual and physical environments
4. Maintain security best practices

---

## 📞 **Contact & Support**

### **Project Team:**
- **Lead Developer**: [Deepak Sharma]
- **Advisor**: [Professor Name]
- **Institution**: [Your College/University]

### **Resources:**
- **Project Repository**: [GitHub URL - To be added]
- **Documentation**: See `SMART_HOME_THREAT_SIMULATION_PLAN.md`
- **Issue Tracker**: [GitHub Issues - To be added]

### **License:**
This project is open-source under the MIT License.

---

**Last Updated**: March 31, 2026  
**Project Status**: Planning Phase  
**Next Milestone**: Environment Setup & Code Sanitization

---
*"Building the future of IoT security, one simulation at a time."*