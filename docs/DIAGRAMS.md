# Master's Thesis: System Diagrams & Visualizations

*Note: These diagrams are written using Mermaid.js syntax. When viewed on GitHub, they will automatically render into high-quality, scalable graphics perfect for our PowerPoint presentation and Thesis Appendices.*

---

## 1. High-Level Smart Home Network Topology
*Visualizes the physical and digital boundaries of the cyber range.*

```mermaid
graph TD
    subgraph "Attacker Workstation (Kali/Linux)"
        A1[Brute Force Script]
        A2[DoS Botnet Script]
        A3[Replay Attack Script]
    end

    subgraph "Local Network (Isolated Cyber Range)"
        MB((Mosquitto MQTT Broker))
        IPS[Live IPS Firewall / iptables]
        DB[React/Node.js Dashboard]
    end

    subgraph "Smart Home IoT Infrastructure"
        ESP[ESP32 Security Hub]
        PIR[PIR Motion Sensor]
        BUZ[Alarm Buzzer]
    end

    A1 -.->|TCP Port 1883| MB
    A2 -.->|Volumetric Flood| MB
    A3 -.->|Duplicate Payloads| MB

    MB <-->|shtsp/home/security/cmd| ESP
    ESP -->|shtsp/home/telemetry| MB
    
    ESP --- PIR
    ESP --- BUZ

    MB -->|Real-time Telemetry| IPS
    MB -->|WebSockets| DB
    
    classDef attacker fill:#ffb3b3,stroke:#cc0000,stroke-width:2px;
    classDef core fill:#e6f3ff,stroke:#0066cc,stroke-width:2px;
    classDef iot fill:#d9f2d9,stroke:#2eb82e,stroke-width:2px;
    
    class A1,A2,A3 attacker;
    class MB,IPS,DB core;
    class ESP,PIR,BUZ iot;
```

---

## 2. Threat Model & Attack Vectors
*Shows how the three different attacks target the core pillars of IoT Security.*

```mermaid
mindmap
  root((Smart Home IoT Threats))
    Authentication Bypass
      (Target: Access Control)
      [Brute Force Attack]
      ::icon(fa fa-unlock-alt)
      (Impact: Unauthorized Control)
    Availability Disruption
      (Target: Broker & Hardware)
      [Denial of Service - DoS]
      ::icon(fa fa-bomb)
      (Impact: CPU Starvation & Buffer Exhaustion)
    Integrity Compromise
      (Target: Message Validity)
      [Replay Attack]
      ::icon(fa fa-history)
      (Impact: Covert Malicious Execution)
```

---

## 3. MQTT Topic & Message Routing Architecture
*Illustrates the Publish/Subscribe architecture of the system.*

```mermaid
flowchart LR
    subgraph "Publishers"
        ESP(ESP32 Device)
        ATT(Attacker Scripts)
        UI(React Dashboard UI)
    end

    subgraph "MQTT Broker Topics"
        CMD[shtsp/home/security/cmd]
        TEL[shtsp/home/telemetry]
        ALR[shtsp/home/alerts]
    end

    subgraph "Subscribers"
        ESP_SUB(ESP32 Device)
        LOG(Data Collector)
        IPS(Live ML IPS)
        DB_SUB(Node.js Backend)
    end

    ESP -- Publishes Audit/Status --> TEL
    ATT -- Publishes Malicious Cmds --> CMD
    UI -- Publishes User Cmds --> CMD
    IPS -- Publishes Threat Flags --> ALR

    CMD --> ESP_SUB
    TEL --> LOG
    TEL --> IPS
    TEL --> DB_SUB
    ALR --> DB_SUB
```

---

## 4. Hardware Logic Flow (ESP32 Security Hub)
*Shows the internal execution loop of the physical smart home device.*

```mermaid
stateDiagram-v2
    [*] --> Connect_WiFi
    Connect_WiFi --> Connect_MQTT
    Connect_MQTT --> Main_Loop
    
    state Main_Loop {
        Poll_PIR --> Check_MQTT_Callback
        
        state Poll_PIR {
            Motion_Detected --> Publish_Telemetry
            Motion_Detected --> Sound_Buzzer : If Armed
        }
        
        state Check_MQTT_Callback {
            Receive_Command --> Process_PIN
            Process_PIN --> Valid_PIN
            Process_PIN --> Invalid_PIN
            
            Valid_PIN --> Change_Arm_State
            Valid_PIN --> Publish_Success_Audit
            
            Invalid_PIN --> Publish_Failure_Audit
        }
    }
    
    Main_Loop --> Reconnect_MQTT : Connection Lost
    Reconnect_MQTT --> Main_Loop
```

---

## 5. Volumetric DoS Attack & Hardware Starvation Sequence
*Visualizes how the DoS attack causes the ESP32 to drop valid physical events.*

```mermaid
sequenceDiagram
    participant Attacker as DoS Botnet (5 Threads)
    participant Broker as Mosquitto Broker
    participant ESP as ESP32 Hardware
    participant PIR as Physical Environment

    Note over Attacker,ESP: Normal Operation
    PIR->>ESP: Motion Detected
    ESP->>Broker: Publish (Motion Event)
    
    Note over Attacker,ESP: DoS Attack Initiated
    loop High Frequency (0ms delay)
        Attacker->>Broker: Publish large junk payload
        Broker->>ESP: Route payload to subscriber
    end
    
    Note over ESP: CPU Maxed Out (150+ PPS)<br/>Heap Memory Exhausted
    
    PIR->>ESP: Motion Detected (CRITICAL)
    Note over ESP: Event Dropped due to CPU Starvation
    ESP--xBroker: Fails to publish motion event
```

---

## 6. Replay Attack Capture & Retransmission Sequence
*Shows the stealthy nature of the Replay attack bypassing traditional security.*

```mermaid
sequenceDiagram
    participant User as Legitimate User
    participant Broker as MQTT Broker
    participant Attacker as Attacker Script
    participant ESP as ESP32 Hub

    Note over Attacker: Listening to network traffic
    Attacker->>Broker: Subscribe (shtsp/home/security/cmd)
    
    User->>Broker: Publish {"type":"PIN", "value":"1234"}
    Broker->>ESP: Route Command
    Broker->>Attacker: Route Command (Intercepted)
    
    Note over ESP: Validates PIN (Success)
    
    Note over Attacker: Modifies and Retransmits Payload
    loop Continuous Injection
        Attacker->>Broker: Publish {"type":"PIN", "value":"1234"}
        Broker->>ESP: Route Command
        Note over ESP: Forced State Change
    end
```

---

## 7. Unified Dataset Engineering Pipeline
*The exact process of turning raw telemetry into the 1.6 Million row ML dataset.*

```mermaid
flowchart TD
    Raw[Raw Fragmented JSON Logs] --> Align{Feature Alignment}
    
    Align --> |Brute Force Logs| Col1[Extract Auth Metrics]
    Align --> |DoS Logs| Col2[Extract Network/Traffic Metrics]
    Align --> |Replay Logs| Col3[Extract Timing/Duplicate Metrics]
    Align --> |Normal Logs| Col4[Extract Baseline Metrics]
    
    Col1 --> ZVI["Zero-Value Imputation<br/>(Fill missing fields with 0)"]
    Col2 --> ZVI
    Col3 --> ZVI
    Col4 --> ZVI
    
    ZVI --> Norm["StandardScaler Normalization"]
    Norm --> Merge[("Master 25-Column CSV Dataset")]
    Merge --> Train[Random Forest Model Training]
```

---

## 8. Machine Learning Benchmarking Workflow
*Demonstrates the scientific rigor used to select Random Forest over deep learning or linear models.*

```mermaid
flowchart LR
    Data[("1.6M Row Dataset")] --> Split["80% Train / 20% Test Split"]
    
    Split --> M1[Random Forest]
    Split --> M2[Linear SVC]
    Split --> M3[Decision Tree]
    Split --> M4[XGBoost]
    Split --> M5[Logistic Regression]
    
    M1 --> Eval{Evaluate Metrics}
    M2 --> Eval
    M3 --> Eval
    M4 --> Eval
    M5 --> Eval
    
    Eval --> Select[Select Best Performing Model]
    Select --> Export[Export random_forest_ids.pkl]
```

---

## 9. Random Forest Feature Importance (Conceptual Model)
*A visual representation of how the algorithm decides on an attack class.*

```mermaid
graph TD
    Root{"Is packets_per_second > 100?"}
    
    Root -->|Yes| DoS["Classify: Denial of Service"]
    Root -->|No| Node2{"Is duplicate_payload_rate > 0.9?"}
    
    Node2 -->|Yes| Replay["Classify: Replay Attack"]
    Node2 -->|No| Node3{"Is auth_failure_rate > 0.5?"}
    
    Node3 -->|Yes| BF[Classify: Brute Force]
    Node3 -->|No| Normal[Classify: Normal Traffic]
```

---

## 10. Active Mitigation (Live IPS) Firewall Mechanism
*Visualizes the real-time defensive mechanism implemented in Section 7.7.*

```mermaid
sequenceDiagram
    participant Attacker
    participant Node as ESP32 Network
    participant Sniffer as Live IPS (Python)
    participant ML as Random Forest Classifier
    participant FW as Linux iptables Firewall

    Attacker->>Node: Malicious Traffic (DoS)
    Node->>Sniffer: MQTT Telemetry Stream
    
    Sniffer->>ML: Extract 25 Features
    ML-->>Sniffer: Prediction: Label 2 (DoS Threat)
    
    Note over Sniffer: Threat Detected!
    Sniffer->>FW: os.system("sudo iptables -A INPUT -s IP -j DROP")
    Note over FW: Attacker IP Blocked Instantly
    
    Attacker-xNode: Traffic Denied by OS Firewall
```

---

## 11. Full-Stack Web 3.0 Dashboard Architecture
*Illustrates the commercial-grade React/Node.js monitoring application.*

```mermaid
graph TD
    subgraph "Frontend (React.js + Vite)"
        UI_Dash[Threat Dashboard]
        UI_Heat[Anomaly Heatmap]
        UI_Ctrl[Attack Simulation Controls]
    end

    subgraph "Backend (Node.js Server)"
        WS[WebSocket Server]
        MQTT_Client[MQTT.js Client]
    end

    subgraph "Core Network"
        Broker((Mosquitto Broker))
    end

    UI_Ctrl -->|HTTP POST| WS
    WS -->|Publishes Command| MQTT_Client
    MQTT_Client -->|shtsp/home/security/cmd| Broker
    
    Broker -->|Real-time Telemetry| MQTT_Client
    MQTT_Client -->|Broadcasts JSON| WS
    WS -->|WebSocket Stream| UI_Dash
    WS -->|WebSocket Stream| UI_Heat
    
    classDef react fill:#61dafb,color:black,stroke:#000,stroke-width:2px;
    classDef node fill:#339933,color:white,stroke:#000,stroke-width:2px;
    
    class UI_Dash,UI_Heat,UI_Ctrl react;
    class WS,MQTT_Client node;
```

---

## 12. Brute Force Authentication Bypass Sequence
*Demonstrates how the Brute Force attack systematically exhausts credentials.*

```mermaid
sequenceDiagram
    participant Attacker as Brute Force Script
    participant Broker as MQTT Broker
    participant ESP as ESP32 Hardware

    Note over Attacker: Loading massive_wordlist.txt
    
    loop High Frequency Authentication Attempts
        Attacker->>Broker: Publish {"type":"PIN", "value":"0000"}
        Broker->>ESP: Route Command
        
        Note over ESP: Validates PIN (Failed)
        ESP->>Broker: Publish Failure Audit
        
        Attacker->>Broker: Publish {"type":"PIN", "value":"1234"}
        Broker->>ESP: Route Command
        
        Note over ESP: Validates PIN (Failed)
        ESP->>Broker: Publish Failure Audit
    end
    
    Note over ESP: auth_failure_rate skyrockets<br/>consecutive_failures spikes
```

---

## 13. Normal Traffic & Authorized Communication Sequence
*Establishes the baseline "Healthy Pulse" of the smart home environment.*

```mermaid
sequenceDiagram
    participant User as Legitimate User
    participant PIR as Physical Environment
    participant Broker as MQTT Broker
    participant ESP as ESP32 Hardware

    PIR->>ESP: Motion Detected (Legitimate)
    ESP->>Broker: Publish Telemetry (Stable PPS, Normal Heap)
    
    User->>Broker: Publish {"type":"PIN", "value":"[CORRECT PIN]"}
    Broker->>ESP: Route Command
    
    Note over ESP: Validates PIN (Success)
    ESP->>Broker: Publish Success Audit
    
    Note over ESP: Arm/Disarm State Changed
    ESP->>Broker: Publish State Update
```
