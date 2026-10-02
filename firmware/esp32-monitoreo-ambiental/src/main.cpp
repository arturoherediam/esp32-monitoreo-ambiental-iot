#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include "Adafruit_SHT4x.h"
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "secrets.h" // Credenciales WiFi/MQTT (NO se sube a GitHub, ver secrets.h.example)
 
// ---------- Configuracion MQTT (no sensible) ----------
const int MQTT_PORT = 1883;
const char* MQTT_TOPIC = "sensor/sht41";
const char* MQTT_CLIENT_ID = "esp32-sht41";
 
// ---------- Pines y direcciones I2C ----------
#define SDA_PIN 21
#define SCL_PIN 22
#define OLED_ADDR 0x3C
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
 
// ---------- Intervalos (no bloqueantes) ----------
const unsigned long INTERVALO_PUBLICACION_MS = 1000; // Publicar cada 1 segundo
const unsigned long INTERVALO_OLED_MS = 3000;         // Alternar la OLED cada 3 segundos
 
Adafruit_SHT4x sht4 = Adafruit_SHT4x();
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
 
WiFiClient espClient;
PubSubClient mqttClient(espClient);
 
unsigned long ultimaPublicacion = 0;
unsigned long ultimoCambioOled = 0;
bool mostrandoTemperatura = true;
 
float temperaturaActual = 0;
float humedadActual = 0;
 
void conectarWiFi() {
  Serial.print("Conectando a WiFi: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("WiFi conectado. IP del ESP32: ");
  Serial.println(WiFi.localIP());
}
 
void conectarMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("Conectando a broker MQTT...");
    if (mqttClient.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASSWORD)) {
      Serial.println(" conectado.");
    } else {
      Serial.print(" fallo, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" reintentando en 3s...");
      delay(3000);
    }
  }
}
 
void mostrarValor(const char* etiqueta, float valor, const char* unidad) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println(etiqueta);
 
  display.setTextSize(2);
  display.setCursor(0, 14);
  display.print(valor, 1);
  display.print(" ");
  display.print(unidad);
 
  display.display();
}
 
void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); }
  delay(500);
 
  Wire.begin(SDA_PIN, SCL_PIN);
 
  // OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("Error: no se pudo inicializar la pantalla OLED.");
    while (1) delay(10);
  }
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("Iniciando...");
  display.display();
 
  // SHT41
  if (!sht4.begin()) {
    Serial.println("Error: no se pudo inicializar el SHT41.");
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Error: SHT41");
    display.display();
    while (1) delay(10);
  }
  sht4.setPrecision(SHT4X_HIGH_PRECISION);
  sht4.setHeater(SHT4X_NO_HEATER);
 
  // WiFi y MQTT
  conectarWiFi();
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
 
  Serial.println("Sistema listo.");
}
 
void loop() {
  if (!mqttClient.connected()) {
    conectarMQTT();
  }
  mqttClient.loop();
 
  unsigned long ahora = millis();
 
  // ---- Publicacion MQTT cada 1 segundo (no bloqueante) ----
  if (ahora - ultimaPublicacion >= INTERVALO_PUBLICACION_MS) {
    ultimaPublicacion = ahora;
 
    sensors_event_t humedad_evento, temp_evento;
    sht4.getEvent(&humedad_evento, &temp_evento);
 
    temperaturaActual = temp_evento.temperature;
    humedadActual = humedad_evento.relative_humidity;
 
    Serial.println("---- Lectura SHT41 ----");
    Serial.print("Temperatura: "); Serial.print(temperaturaActual); Serial.println(" C");
    Serial.print("Humedad: "); Serial.print(humedadActual); Serial.println(" %");
 
    JsonDocument doc;
    doc["temp"] = round(temperaturaActual * 10) / 10.0;
    doc["hum"] = round(humedadActual * 10) / 10.0;
 
    char buffer[128];
    size_t n = serializeJson(doc, buffer);
    mqttClient.publish(MQTT_TOPIC, buffer, n);
 
    Serial.print("Publicado en MQTT: ");
    Serial.println(buffer);
  }
 
  // ---- Alternar la OLED cada 3 segundos (no bloqueante) ----
  if (ahora - ultimoCambioOled >= INTERVALO_OLED_MS) {
    ultimoCambioOled = ahora;
    mostrandoTemperatura = !mostrandoTemperatura;
 
    if (mostrandoTemperatura) {
      mostrarValor("Temperatura", temperaturaActual, "C");
    } else {
      mostrarValor("Humedad", humedadActual, "%");
    }
  }
}
