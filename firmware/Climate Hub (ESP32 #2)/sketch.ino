#include <WiFi.h>
#include <PubSubClient.h>
#include <DHTesp.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.hivemq.com";

DHTesp dht;
WiFiClient espClient;
PubSubClient client(espClient);

void callback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (int i=0; i<length; i++) msg += (char)payload[i];
  digitalWrite(2, (msg == "ON") ? HIGH : LOW);
}

void setup() {
  Serial.begin(115200);
  pinMode(2, OUTPUT);
  dht.setup(15, DHTesp::DHT22);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32_Climate_Hub")) {
      Serial.println("Connected!");
      client.subscribe("shtsp/home/climate/relay");
    } else {
      Serial.println("Failed. Retry in 5s");
      delay(5000);
      return;
    }
  }
  client.loop();

  // Read sensors
  TempAndHumidity data = dht.getTempAndHumidity();
  
  // Create JSON string
  String payload = "{\"temp\":" + String(data.temperature) + "}";
  
  // PRINT TO SERIAL MONITOR (So you can see it!)
  Serial.print("Sending Temperature: ");
  Serial.println(data.temperature);

  client.publish("shtsp/home/climate/data", payload.c_str());
  
  delay(5000);
}