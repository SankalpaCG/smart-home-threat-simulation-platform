#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// --- WIFI & BROKER CONFIGURATION ---
const char* ssid = "Crown_Student";         
const char* password = "student123"; 
const char* mqtt_server = "192.168.21.89";    

WiFiClient espClient;
PubSubClient client(espClient);

// --- HARDWARE CONFIGURATION ---
#define PIR_PIN 13
#define BUZZER_PIN 12

// --- SYSTEM STATE ---
uint32_t seq_num = 0;
unsigned long last_heartbeat = 0;
unsigned long last_audit = 0;
const unsigned long heartbeat_interval = 10000;
const unsigned long audit_interval = 5000; // Report internal health every 5s
bool lockdown_mode = false;
uint32_t reconnect_attempts = 0;

void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void setup_wifi() {
  delay(10);
  Serial.println("\n--- [SECURITY HUB] BOOTING ---");
  Serial.print("📡 Connecting to: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ WiFi Connected!");
  Serial.print("📍 IP Address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("\n📥 [COMMAND RECEIVED] Topic: ");
  Serial.println(topic);

  StaticJsonDocument<256> doc;
  deserializeJson(doc, payload, length);

  const char* action = doc["action"];

  if (strcmp(action, "LOCKDOWN") == 0) {
    lockdown_mode = true;
    Serial.println("🔒 [SECURITY] LOCKDOWN MODE ACTIVATED. Sensors muted.");
    digitalWrite(BUZZER_PIN, HIGH); delay(200); digitalWrite(BUZZER_PIN, LOW);
  } 
  else if (strcmp(action, "UNLOCK") == 0) {
    lockdown_mode = false;
    Serial.println("🔓 [SECURITY] LOCKDOWN DEACTIVATED. Systems online.");
  }
  else if (strcmp(action, "BEEP") == 0) {
    int duration = doc["duration"] | 500;
    digitalWrite(BUZZER_PIN, HIGH);
    delay(duration);
    digitalWrite(BUZZER_PIN, LOW);
  }
}

void reconnect() {
  while (!client.connected()) {
    reconnect_attempts++;
    Serial.print("🔄 [MQTT] Attempting connection (Try #");
    Serial.print(reconnect_attempts);
    Serial.println(")...");

    // LAST WILL AND TESTAMENT (LWT)
    // Professional way to detect "Silence" attacks or device death
    String willTopic = "shtsp/home/security/heartbeat";
    String willMessage = "{\"status\": \"OFFLINE\", \"reason\": \"UNEXPECTED_DISCONNECT\"}";

    if (client.connect("shtsp_Security_Hub_01", NULL, NULL, willTopic.c_str(), 1, true, willMessage.c_str())) {
      Serial.println("✅ [MQTT] Secure Connection Established.");
      client.subscribe("shtsp/home/security/cmd");
      send_event("SYSTEM", "SECURE_BOOT");
    } else {
      Serial.print("❌ [MQTT] Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void send_event(const char* type, const char* status) {
  if (lockdown_mode && strcmp(type, "MOTION") == 0) return;

  StaticJsonDocument<200> doc;
  doc["seq"] = seq_num++;
  doc["type"] = type;
  doc["status"] = status;
  doc["uptime"] = millis();

  char buffer[200];
  serializeJson(doc, buffer);
  
  if (strcmp(type, "HEARTBEAT") == 0) {
    client.publish("shtsp/home/security/heartbeat", buffer);
  } else {
    client.publish("shtsp/home/security/motion", buffer);
  }
}

void send_audit() {
  // INTERNAL STATE AUDIT - High-Fidelity Forensic Logic
  StaticJsonDocument<256> doc;
  doc["type"] = "AUDIT";
  doc["free_heap"] = ESP.getFreeHeap();
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["reconnects"] = reconnect_attempts;
  doc["lockdown"] = lockdown_mode;
  doc["timestamp"] = millis();

  char buffer[256];
  serializeJson(doc, buffer);
  client.publish("shtsp/home/security/audit", buffer, true);
  
  // Local Forensic Logging (Serial)
  Serial.print("📊 [AUDIT] Heap: "); Serial.print(ESP.getFreeHeap());
  Serial.print(" | RSSI: "); Serial.print(WiFi.RSSI());
  Serial.print(" | Reconnects: "); Serial.println(reconnect_attempts);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  unsigned long now = millis();

  // Heartbeat Logic
  if (now - last_heartbeat > heartbeat_interval) {
    last_heartbeat = now;
    send_event("HEARTBEAT", "HEALTHY");
  }

  // Audit Logic (Self-Monitoring)
  if (now - last_audit > audit_interval) {
    last_audit = now;
    send_audit();
  }

  // Motion Detection Logic
  if (!lockdown_mode && digitalRead(PIR_PIN) == HIGH) {
    Serial.println("🚨 [ALARM] LOCAL MOTION DETECTED!");
    digitalWrite(BUZZER_PIN, HIGH);
    send_event("MOTION", "ALARM");
    delay(500);
    digitalWrite(BUZZER_PIN, LOW);
    delay(3000); 
  }
}