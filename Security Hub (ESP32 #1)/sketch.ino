#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.hivemq.com";

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

void loop() {
  if (!client.connected()) client.connect("ESP32_Security_Hub");
  client.loop();

  if (digitalRead(PIR_PIN) == HIGH) {
    Serial.println("MOTION DETECTED!");
    client.publish("shtsp/home/security/motion", "INTRUDER_ALERT");
    digitalWrite(BUZZER_PIN, HIGH); delay(500); digitalWrite(BUZZER_PIN, LOW);
  }
  delay(1000);
}