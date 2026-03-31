#include <WiFi.h>
#include <PubSubClient.h>

// --- UPDATE THESE 3 LINES ---
const char* ssid = "xxxxx";         // Your actual Home WiFi Name
const char* password = "xxxxxxxx"; // Your actual Home WiFi Password
const char* mqtt_server = "192.168.xx.xx";    // Your Laptop's IP (from ipconfig)

WiFiClient espClient;
PubSubClient client(espClient);

#define PIR_PIN 13
#define BUZZER_PIN 12

void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");

  client.setServer(mqtt_server, 1883);
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("shtsp_Security_Pilot")) {
      Serial.println("Connected to Laptop Broker!");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  if (digitalRead(PIR_PIN) == HIGH) {
    Serial.println("🚨 MOTION DETECTED!");
    digitalWrite(BUZZER_PIN, HIGH);
    delay(500);
    digitalWrite(BUZZER_PIN, LOW);
    client.publish("shtsp/home/security/motion", "INTRUDER_ALERT");
    delay(2000); 
  }
}