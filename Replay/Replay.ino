#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ==========================================
// 1. CONFIGURATION - DO NOT CHANGE
// ==========================================
const char* ssid = "Crown_Student";
const char* password = "student123";
const char* mqtt_server = "192.168.21.64";

// --- SECURITY SETTINGS ---
String correct_pin = "1234";
// ==========================================

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

bool isArmed = true;
volatile int packet_counter = 0;
int motion_flag = 0;

unsigned long last_audit = 0;
const int audit_interval = 100;

// Replay feature variables
int replay_packet_count = 0;
unsigned long total_msg_timestamp_delta_ms = 0;

// Timing feature variables
unsigned long last_packet_time = 0;
float inter_arrival_sum_ms = 0;
float inter_arrival_sq_sum_ms = 0;
int inter_arrival_count = 0;

// ==========================================
// 4. MQTT CALLBACK
// ==========================================
void callback(char* topic, byte* payload, unsigned int length) {
  packet_counter++;

  unsigned long current_packet_time = millis();

  if (last_packet_time > 0) {
    float delta = current_packet_time - last_packet_time;
    inter_arrival_sum_ms += delta;
    inter_arrival_sq_sum_ms += delta * delta;
    inter_arrival_count++;
  }

  last_packet_time = current_packet_time;

  JsonDocument doc;
  DeserializationError error = deserializeJson(doc, payload, length);

  if (!error) {

    // Replay attack detection fields
    if (doc.containsKey("replay_attack")) {
      replay_packet_count++;

      if (doc.containsKey("original_msg_timestamp_ms") && doc.containsKey("replay_msg_timestamp_ms")) {
        unsigned long original_ts = doc["original_msg_timestamp_ms"];
        unsigned long replay_ts = doc["replay_msg_timestamp_ms"];

        if (replay_ts >= original_ts) {
          total_msg_timestamp_delta_ms += (replay_ts - original_ts);
        }
      }
    }

    // PIN command logic
    if (doc.containsKey("pin")) {
      const char* try_pin = doc["pin"];

      if (String(try_pin) == correct_pin) {
        isArmed = false;
        Serial.println("\n🔓 [SECURITY] Correct PIN received! System DISARMED.");
      }
    }

    // Manual ARM command
    if (doc.containsKey("action")) {
      const char* act = doc["action"];

      if (String(act) == "ARM") {
        isArmed = true;
        Serial.println("\n🔒 [SECURITY] System RE-ARMED.");
      }
    }
  }
}

// ==========================================
// 5. SETUP & CONNECTIVITY
// ==========================================
void setup_wifi() {
  delay(10);
  Serial.print("\nConnecting to WiFi...");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ WiFi Connected!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");

    if (client.connect("Amir_Security_Hub_Node")) {
      Serial.println("✅ BROKER CONNECTED!");
      client.subscribe("shtsp/home/security/cmd");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" - Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

// ==========================================
// 6. MAIN EXECUTION
// ==========================================
void setup() {
  Serial.begin(115200);

  pinMode(PIR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  setup_wifi();

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  client.setBufferSize(512);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }

  client.loop();

  unsigned long now = millis();

  // --- PART A: PHYSICAL SENSING ---
  if (digitalRead(PIR_PIN) == HIGH) {
    motion_flag = 1;

    if (isArmed) {
      Serial.println("🚨 MOTION DETECTED! BEEPING...");
      digitalWrite(BUZZER_PIN, HIGH);

      client.publish("shtsp/home/security/telemetry", "{\"type\":\"ALERT\",\"msg\":\"MOTION\"}");

      delay(300);
      digitalWrite(BUZZER_PIN, LOW);
      delay(1000);
    }
  }

  // --- PART B: ML AUDIT GENERATION ---
  if (now - last_audit > audit_interval) {
    float pps = (float)packet_counter / 0.1;
    int current_heap = ESP.getFreeHeap();

    float mqtt_publish_rate = pps;

    float duplicate_payload_rate = 0.0;
    unsigned long avg_msg_timestamp_delta_ms = 0;

    if (packet_counter > 0) {
      duplicate_payload_rate = (float)replay_packet_count / (float)packet_counter;
    }

    if (replay_packet_count > 0) {
      avg_msg_timestamp_delta_ms = total_msg_timestamp_delta_ms / replay_packet_count;
    }

    float inter_arrival_mean_ms = 0.0;
    float inter_arrival_std_ms = 0.0;

    if (inter_arrival_count > 0) {
      inter_arrival_mean_ms = inter_arrival_sum_ms / inter_arrival_count;

      float mean_sq = inter_arrival_sq_sum_ms / inter_arrival_count;
      float variance = mean_sq - (inter_arrival_mean_ms * inter_arrival_mean_ms);

      if (variance > 0) {
        inter_arrival_std_ms = sqrt(variance);
      }
    }

    JsonDocument doc;
    doc["type"] = "AUDIT";
    doc["pps"] = pps;
    doc["mqtt_publish_rate"] = mqtt_publish_rate;
    doc["heap"] = current_heap;
    doc["mot"] = motion_flag;
    doc["arm"] = isArmed ? 1 : 0;
    doc["ip"] = WiFi.localIP().toString();

    doc["duplicate_payload_rate"] = duplicate_payload_rate;
    doc["msg_timestamp_delta_ms"] = avg_msg_timestamp_delta_ms;
    doc["inter_arrival_mean_ms"] = inter_arrival_mean_ms;
    doc["inter_arrival_std_ms"] = inter_arrival_std_ms;
    doc["attack_level"] = 3;

    char buffer[512];
    serializeJson(doc, buffer);

    client.publish("shtsp/home/telemetry", buffer);

    Serial.printf(
      "Audit Sent -> PPS: %.2f | Heap: %d | DupRate: %.2f | Delta: %lu ms | IAT Mean: %.2f | IAT Std: %.2f\n",
      pps,
      current_heap,
      duplicate_payload_rate,
      avg_msg_timestamp_delta_ms,
      inter_arrival_mean_ms,
      inter_arrival_std_ms
    );

    packet_counter = 0;
    motion_flag = 0;
    replay_packet_count = 0;
    total_msg_timestamp_delta_ms = 0;

    inter_arrival_sum_ms = 0;
    inter_arrival_sq_sum_ms = 0;
    inter_arrival_count = 0;

    last_audit = now;
  }
}