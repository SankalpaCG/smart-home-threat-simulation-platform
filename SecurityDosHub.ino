#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ==========================================
// 1. CONFIGURATION
// ==========================================
const char* ssid = "Crown_Student";             
const char* password = "student123";   
const char* mqtt_server = "192.168.4.22"; // Ensure this matches your ipconfig!

// ==========================================
// 2. HARDWARE PINS
// ==========================================
#define PIR_PIN 13
#define BUZZER_PIN 12

WiFiClient espClient;
PubSubClient client(espClient);

// Variables for ML Features
bool isArmed = true;              
volatile int packet_count = 0;  
int motion_flag = 0;              
unsigned long last_audit = 0;
const int audit_interval = 200;   // 5 times per second

unsigned long buzzer_off_time = 0;
bool buzzer_is_on = false;

// ==========================================
// 3. CALLBACK (Hacker detection)
// ==========================================
void callback(char* topic, byte* payload, unsigned int length) {
  packet_count++; 
}

// ==========================================
// 4. CONNECTION LOGIC
// ==========================================
void setup_wifi() {
  delay(10);
  Serial.println("\nStarting WiFi connection...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi Connected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("Amir_Final_Security_Node")) {
      Serial.println("✅ BROKER CONNECTED!");
      client.subscribe("shtsp/home/security/cmd");
    } else {
      Serial.print("FAILED [rc=");
      Serial.print(client.state());
      Serial.println("] - retrying in 5s");
      delay(5000);
    }
  }
}

// ==========================================
// 5. MAIN SETUP & LOOP
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
  if (!client.connected()) reconnect();
  client.loop(); 

  unsigned long now = millis();

  // --- 1. PHYSICAL MOTION LOGIC ---
  if (digitalRead(PIR_PIN) == HIGH) {
    motion_flag = 1; 
    if (isArmed && !buzzer_is_on) {
      Serial.println("🚨 MOTION! BEEPING...");
      digitalWrite(BUZZER_PIN, HIGH);
      buzzer_off_time = now + 300; 
      buzzer_is_on = true;
      client.publish("shtsp/home/security/alert", "MOTION DETECTED");
    }
  }

  if (buzzer_is_on && now >= buzzer_off_time) {
    digitalWrite(BUZZER_PIN, LOW);
    buzzer_is_on = false;
  }

  // --- 2. TELEMETRY FOR AI ---
  if (now - last_audit > audit_interval) {
    JsonDocument doc;
    doc["type"] = "AUDIT";        
    doc["pps_raw"] = packet_count;
    doc["heap"] = ESP.getFreeHeap();
    doc["mot"] = motion_flag;
    doc["arm"] = isArmed ? 1 : 0;
    doc["ip"] = WiFi.localIP().toString();

    char buffer[256];
    serializeJson(doc, buffer);
    client.publish("shtsp/home/telemetry", buffer);

    // This shows the numbers on your Serial Monitor
    Serial.printf("Audit Sent -> PPS: %d | Heap: %d | Mot: %d\n", packet_count, ESP.getFreeHeap(), motion_flag);

    packet_count = 0; 
    motion_flag = 0; 
    last_audit = now;
  }
}