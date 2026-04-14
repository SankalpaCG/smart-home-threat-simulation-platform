# 📓 Smart Home Security Lab Notes

## 🧪 Simulation Observations

### 1. Local Survivability vs. Network Outage
**Observation**: During a "Session Hijacking" or "Heartbeat Loss" attack, the ESP32 remained physically active (beeping/detecting motion) even though no data appeared on the MQTT broker.
-   **Why?**: The device's internal logic (`loop()`) is independent of its network status.
-   **Security Impact**: This highlights that a network-level attack affects **Information Availability**, but may not stop the local hardware from functioning as an alarm.
-   **Detection Key**: Differentiating between a "True Device Power-Off" (no beeps) and a "Cyber Silence" (beeping but no MQTT).

### 2. Session Hijacking (Connection Stealing)
**Technique**: Using the same `ClientID` as a legitimate device to force the broker to disconnect the original client.
-   **MQTT Behavior**: Per the MQTT spec, the broker (Mosquitto) must disconnect the existing connection once a new one arrives with the same ID.
-   **Detection Key**: Frequent "Duplicate Client ID" warnings in Mosquitto logs or sudden "Sequence Gaps" in our `security_logger.py`.

### 3. Data Collection Strategies
-   **Fidelity**: High message rates (e.g., 10k messages/sec) are necessary to test the "breaking point" of detection algorithms.
-   **Labeling**: Each dataset session must be accurately labeled (`normal`, `dos`, `spoofing`, etc.) at the moment of collection to ensure ML models can learn correctly.


While standard IoT security benchmarks rely solely on application-layer telemetry, this project implements a Multi-Layer Forensic Framework. It correlates Raw Network Intelligence (Layer 4) with Physical-Layer Telemetry (RSSI) and Heap Memory Analysis to provide a 360-degree defense posture, significantly exceeding the detection capabilities of traditional signature-based systems.
---

## 🛠️ Lab Setup Summary
-   **Broker**: Eclipse Mosquitto (Windows)
-   **Hub**: ESP32 DevKit V1 (PIR Sensor)
-   **Gateway IP**: 192.168.1.105
-   **Protocol**: MQTT (Unencrypted for research)
