#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.hivemq.com";

Servo myServo;
WiFiClient espClient;
PubSubClient client(espClient);

#define RED_LED 25
#define GREEN_LED 26

void callback(char* topic, byte* payload, unsigned int length) {
  String msg = "";
  for (int i = 0; i < length; i++) msg += (char)payload[i];
  
  // DEBUG: This will tell us if the message arrived
  Serial.print("MESSAGE RECEIVED: ");
  Serial.println(msg);

  msg.trim(); // Remove any hidden spaces

  if (msg == "UNLOCK") {
    Serial.println("Action: Unlocking...");
    myServo.write(90);
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);
  } else if (msg == "LOCK") {
    Serial.println("Action: Locking...");
    myServo.write(0);
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RED_LED, HIGH);
  }
}

void setup() {
  Serial.begin(115200);
  myServo.attach(14);
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  digitalWrite(RED_LED, HIGH); // Start Locked

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWiFi Connected!");

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    // Change this ID to something unique like your name
    if (client.connect("shtsp_Unique_Lock_Hub")) { 
      Serial.println("Connected!");
      client.subscribe("shtsp/home/lock/cmd");
    } else {
      Serial.println("Failed, retry in 5s");
      delay(5000);
    }
  }
  client.loop();
}