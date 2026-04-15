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
#define PIR_PIN    13
#define BUZZER_PIN 12

// --- SYSTEM STATE ---
uint32_t seq_num          = 0;
unsigned long last_heartbeat  = 0;
unsigned long last_audit      = 0;
unsigned long last_status_banner = 0;

const unsigned long heartbeat_interval    = 10000;
const unsigned long audit_interval        = 5000;
const unsigned long status_banner_interval = 3000;  // Print status every 3s

bool lockdown_mode = false;
uint32_t reconnect_attempts = 0;

// --- ATTACK DETECTION COUNTERS ---
uint32_t dos_packet_count    = 0;  // Tracks flood volume in rolling window
uint32_t spoof_count         = 0;  // Tracks incoming SAFE packets after an ALARM
uint32_t hijack_events       = 0;  // Tracks LOCKDOWN commands received externally
unsigned long dos_window_start = 0;

// Threshold: >30 messages in 5s = likely DoS flood
const uint32_t DOS_THRESHOLD = 30;
const unsigned long DOS_WINDOW_MS = 5000;

// --- SYSTEM STATUS ENUM ---
enum HubStatus { STATUS_NORMAL, STATUS_ALERT };
HubStatus current_status = STATUS_NORMAL;
String alert_reason = "";

// ============================================================
//  DISPLAY HELPERS - Makes Serial Monitor easy to read
// ============================================================

void printSeparator(char c = '-') {
  for (int i = 0; i < 52; i++) Serial.print(c);
  Serial.println();
}

void printStatusBanner() {
  printSeparator('=');
  if (current_status == STATUS_NORMAL) {
    Serial.println("  ✅ STATUS: NORMAL  |  System Operating Nominally");
    Serial.print  ("     Uptime: "); Serial.print(millis() / 1000); Serial.println("s");
    Serial.print  ("     Heap  : "); Serial.print(ESP.getFreeHeap()); Serial.println(" bytes");
    Serial.print  ("     RSSI  : "); Serial.print(WiFi.RSSI()); Serial.println(" dBm");
  } else {
    Serial.println("  🚨 STATUS: ALERT   |  *** THREAT DETECTED ***");
    Serial.print  ("     Reason: "); Serial.println(alert_reason);
    Serial.print  ("     DoS Pkts (5s window): "); Serial.println(dos_packet_count);
    Serial.print  ("     Spoof Attempts      : "); Serial.println(spoof_count);
    Serial.print  ("     Hijack Events       : "); Serial.println(hijack_events);
  }
  printSeparator('=');
}

void setStatus(HubStatus s, String reason = "") {
  if (current_status != s) {
    current_status = s;
    alert_reason   = reason;
    printStatusBanner();   // Immediate banner on status change
  }
}

// ============================================================
//  WIFI SETUP
// ============================================================

void setup_wifi() {
  delay(10);
  printSeparator('=');
  Serial.println("  SOVEREIGNTY SECURITY HUB  |  Booting...");
  printSeparator('=');
  Serial.print("📡 Connecting to: "); Serial.println(ssid);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("✅ WiFi Connected!");
  Serial.print("📍 IP: "); Serial.println(WiFi.localIP());
}

// ============================================================
//  MQTT CALLBACK — Receives commands & detects attack signals
// ============================================================

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("\n📥 [CMD] Topic: "); Serial.println(topic);

  StaticJsonDocument<256> doc;
  deserializeJson(doc, payload, length);
  const char* action = doc["action"] | "";
  const char* status = doc["status"] | "";

  // --- LOCKDOWN / UNLOCK commands (may be from Guard or from Attacker) ---
  if (strcmp(action, "LOCKDOWN") == 0) {
    hijack_events++;
    lockdown_mode = true;
    setStatus(STATUS_ALERT, "External LOCKDOWN command received");
    Serial.println("🔒 LOCKDOWN MODE ACTIVATED");
    digitalWrite(BUZZER_PIN, HIGH); delay(200); digitalWrite(BUZZER_PIN, LOW);
  } 
  else if (strcmp(action, "UNLOCK") == 0) {
    lockdown_mode = false;
    Serial.println("🔓 LOCKDOWN DEACTIVATED. Systems ONLINE.");
    // Only return to normal if no other threats active
    if (dos_packet_count < DOS_THRESHOLD && spoof_count == 0) {
      setStatus(STATUS_NORMAL);
    }
  }
  else if (strcmp(action, "BEEP") == 0) {
    int duration = doc["duration"] | 500;
    digitalWrite(BUZZER_PIN, HIGH);
    delay(duration);
    digitalWrite(BUZZER_PIN, LOW);
  }

  // --- Detect Spoofed "SAFE" flood following an ALARM ---
  // Attacker sends bursts of SAFE packets to mask real alarms
  if (strcmp(status, "SAFE") == 0 && doc["intelligent_masking"] == true) {
    spoof_count++;
    setStatus(STATUS_ALERT, "Adversarial SPOOFING detected (masking attack)");
    Serial.print("⚠️  [SPOOF] Masking packet #"); Serial.print(spoof_count); Serial.println(" intercepted!");
  }

  // --- DoS Flood Detection ---
  dos_packet_count++;
  unsigned long now = millis();
  if (now - dos_window_start > DOS_WINDOW_MS) {
    if (dos_packet_count > DOS_THRESHOLD) {
      setStatus(STATUS_ALERT, "DoS FLOOD detected (high message rate)");
      Serial.print("🔥 [DoS] Flood detected — "); Serial.print(dos_packet_count);
      Serial.println(" packets in rolling window!");
    } else {
      // Reset window and potentially clear alert if no other threats
      if (current_status == STATUS_ALERT && hijack_events == 0 && spoof_count == 0) {
        setStatus(STATUS_NORMAL);
      }
    }
    dos_packet_count  = 0;
    dos_window_start  = now;
  }
}

// ============================================================
//  MQTT RECONNECT WITH LWT
// ============================================================

void reconnect() {
  while (!client.connected()) {
    reconnect_attempts++;
    printSeparator();
    Serial.print("🔄 [MQTT] Connecting... (Attempt #");
    Serial.print(reconnect_attempts); Serial.println(")");

    String willTopic   = "shtsp/home/security/heartbeat";
    String willMessage = "{\"status\": \"OFFLINE\", \"reason\": \"UNEXPECTED_DISCONNECT\"}";

    if (client.connect("shtsp_Security_Hub_01", NULL, NULL,
                       willTopic.c_str(), 1, true, willMessage.c_str())) {
      Serial.println("✅ [MQTT] Connected.");
      client.subscribe("shtsp/home/security/cmd");
      client.subscribe("shtsp/home/security/motion");  // Subscribe to own topic to detect floods
      send_event("SYSTEM", "SECURE_BOOT");
      setStatus(STATUS_NORMAL);
    } else {
      Serial.print("❌ [MQTT] Failed (rc=");
      Serial.print(client.state());
      Serial.println("). Retrying in 5s...");
      delay(5000);
    }
  }
}

// ============================================================
//  EVENT PUBLISH
// ============================================================

void send_event(const char* type, const char* status) {
  if (lockdown_mode && strcmp(type, "MOTION") == 0) return;

  StaticJsonDocument<200> doc;
  doc["seq"]    = seq_num++;
  doc["type"]   = type;
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

// ============================================================
//  INTERNAL AUDIT (Self-Health Report)
// ============================================================

void send_audit() {
  StaticJsonDocument<256> doc;
  doc["type"]       = "AUDIT";
  doc["free_heap"]  = ESP.getFreeHeap();
  doc["wifi_rssi"]  = WiFi.RSSI();
  doc["reconnects"] = reconnect_attempts;
  doc["lockdown"]   = lockdown_mode;
  doc["dos_pkts"]   = dos_packet_count;
  doc["spoofs"]     = spoof_count;
  doc["hijacks"]    = hijack_events;
  doc["timestamp"]  = millis();

  char buffer[256];
  serializeJson(doc, buffer);
  client.publish("shtsp/home/security/audit", buffer, true);
}

// ============================================================
//  SETUP
// ============================================================

void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  dos_window_start = millis();
}

// ============================================================
//  MAIN LOOP
// ============================================================

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  unsigned long now = millis();

  // --- Periodic heartbeat ---
  if (now - last_heartbeat > heartbeat_interval) {
    last_heartbeat = now;
    send_event("HEARTBEAT", "HEALTHY");
    Serial.print("💓 [HEARTBEAT] Seq: "); Serial.println(seq_num - 1);
  }

  // --- Periodic internal audit ---
  if (now - last_audit > audit_interval) {
    last_audit = now;
    send_audit();
  }

  // --- Periodic status banner (so Serial Monitor stays readable) ---
  if (now - last_status_banner > status_banner_interval) {
    last_status_banner = now;
    printStatusBanner();
  }

  // --- PIR Motion Detection ---
  if (!lockdown_mode && digitalRead(PIR_PIN) == HIGH) {
    printSeparator('!');
    Serial.println("  🚨 [ALARM] REAL MOTION DETECTED BY PIR SENSOR!");
    printSeparator('!');
    setStatus(STATUS_ALERT, "Real PIR motion event");
    digitalWrite(BUZZER_PIN, HIGH);
    send_event("MOTION", "ALARM");
    delay(500);
    digitalWrite(BUZZER_PIN, LOW);
    delay(3000);
    // Auto-clear after delay if no further motion
    if (digitalRead(PIR_PIN) == LOW) {
      setStatus(STATUS_NORMAL);
    }
  }
}