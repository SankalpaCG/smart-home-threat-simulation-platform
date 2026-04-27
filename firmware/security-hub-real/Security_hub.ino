#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ==========================================
// 1. CONFIGURATION - UPDATE THESE!
// ==========================================
const char* ssid = "Khagendra's iPhone";         
const char* password = "987654321"; 
const char* mqtt_server = "172.20.10.3"; // Your Laptop IP

// ==========================================
// 2. HARDWARE PINS
// ==========================================
#define PIR_PIN 13
#define BUZZER_PIN 12

// ==========================================
// 3. SYSTEM STATE & ML VARIABLES
// ==========================================
WiFiClient espClient;
PubSubClient client(espClient);

bool isArmed = true;              // 1 = Armed, 0 = Disarmed
String correct_pin = "8822";      // The hacker's target
volatile int packet_counter = 0;  // Counts incoming packets (PPS)
int motion_flag = 0;              // 1 if motion happened in this window
unsigned long last_audit = 0;
const int audit_interval = 2000;  // Audit every 2 seconds
const float dos_pps_threshold = 50.0; // Beep when command traffic is attack-like
const unsigned long alarm_beep_ms = 700;
unsigned long attack_alarm_until = 0;

void triggerAttackAlarm(const char* reason) {
  Serial.print("[ATTACK] ");
  Serial.println(reason);
  attack_alarm_until = millis() + alarm_beep_ms;
  digitalWrite(BUZZER_PIN, HIGH);
}

// ==========================================
// 4. MQTT CALLBACK (The Attack Surface)
// ==========================================
void callback(char* topic, byte* payload, unsigned int length) {
  // ML Feature: Count every packet for DoS detection
  packet_counter++; 

  // Parse JSON Commands (Brute Force or System Reset)
  JsonDocument doc; 
  DeserializationError error = deserializeJson(doc, payload, length);

  if (!error) {
    // Check for PIN (Brute Force Simulation)
    if (doc.containsKey("pin")) {
      const char* try_pin = doc["pin"];
      if (String(try_pin) == correct_pin) {
        isArmed = false; 
        Serial.println("🔓 [SECURITY] System Disarmed via PIN.");
      }
    }
    // Check for Manual ARM command
    if (doc.containsKey("action")) {
      const char* act = doc["action"];
      if (String(act) == "ALERT" || String(act) == "BEEP") {
        triggerAttackAlarm("Remote attack alert received");
        return;
      }
      if (String(act) == "ARM") {
        isArmed = true;
        Serial.println("🔒 [SECURITY] System Re-Armed.");
      }
    }
  } else if (length > 128) {
    triggerAttackAlarm("Malformed or oversized command payload");
  }
}

// ==========================================
// 5. SETUP FUNCTIONS
// ==========================================
void setup_wifi() {
  delay(10);
  Serial.print("\nConnecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\n✅ WiFi Connected!");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to Broker...");
    if (client.connect("Amir_Security_Node_Final")) {
      Serial.println("Connected!");
      client.subscribe("shtsp/home/security/cmd");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

// ==========================================
// 6. MAIN EXECUTION LOOP
// ==========================================
void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  client.setBufferSize(512); // Buffer to handle large attack packets
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop(); 

  if (attack_alarm_until > 0 && millis() > attack_alarm_until) {
    digitalWrite(BUZZER_PIN, LOW);
    attack_alarm_until = 0;
  }

  unsigned long now = millis();

  // --- PART A: PHYSICAL SENSING ---
  // If sensor is HIGH (Motion detected)
  if (digitalRead(PIR_PIN) == HIGH) {
    motion_flag = 1; // Mark motion occurred for the next Audit log
    
    if (isArmed) {
      Serial.println("🚨 MOTION DETECTED! BEEPING...");
      digitalWrite(BUZZER_PIN, HIGH);
      
      // Notify Gateway immediately
      client.publish("shtsp/home/security/telemetry", "{\"type\":\"ALERT\",\"msg\":\"MOTION\"}");
      
      delay(300); // Beep duration
      digitalWrite(BUZZER_PIN, LOW);
      delay(1000); // Cooldown
    }
  }

  // --- PART B: ML AUDIT GENERATION (Every 2 seconds) ---
  if (now - last_audit > audit_interval) {
    float pps = (float)packet_counter / (audit_interval / 1000);
    int current_heap = ESP.getFreeHeap();

    if (pps >= dos_pps_threshold) {
      triggerAttackAlarm("DoS packet rate threshold exceeded");
      client.publish("shtsp/home/security/telemetry", "{\"type\":\"ALERT\",\"msg\":\"DOS_DETECTED\"}");
    }

    // Create JSON Telemetry for the AI Dataset
    JsonDocument auditDoc;
    auditDoc["type"] = "AUDIT";
    auditDoc["pps"] = pps;           // AI Feature 1: Packet Volume
    auditDoc["heap"] = current_heap; // AI Feature 2: Memory Health
    auditDoc["mot"] = motion_flag;   // AI Feature 3: Physical activity
    auditDoc["arm"] = isArmed ? 1 : 0; // AI Feature 4: Security State

    char buffer[256];
    serializeJson(auditDoc, buffer);
    client.publish("shtsp/home/telemetry", buffer);
    
    // Serial Monitor display for debugging
    Serial.printf("LOG -> PPS: %.2f | Heap: %d | Mot: %d | Arm: %d\n", 
                  pps, current_heap, motion_flag, isArmed);

    // RESET flags for the next 2-second window
    packet_counter = 0;
    motion_flag = 0; 
    last_audit = now;
  }
}
