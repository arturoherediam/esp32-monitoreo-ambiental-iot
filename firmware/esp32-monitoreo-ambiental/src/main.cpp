#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include "Adafruit_SHT4x.h"
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "secrets.h" // Credenciales WiFi/MQTT (NO se sube a GitHub, ver secrets.h.example)

// ============================================================================
//  Monitor de confort termico (SHT41 + OLED) con comunicacion bidireccional
//  ESP32 <-> MQTT <-> Node-RED
//
//  - Publica temperatura y humedad (JSON + topics independientes).
//  - Recibe comandos ON/OFF para un LED y confirma el estado real.
//  - Last Will and Testament (LWT) para detectar desconexiones.
//  - Reconexion WiFi/MQTT no bloqueante: el sensor y la OLED siguen
//    funcionando aunque se pierda la red.
// ============================================================================

// ---------- Configuracion MQTT (no sensible) ----------
const int MQTT_PORT = 1883;
const char* MQTT_CLIENT_ID = "esp32-sht41";
const uint16_t MQTT_KEEPALIVE_S = 15;

// Topics de publicacion (ESP32 -> Node-RED)
const char* TOPIC_JSON        = "sensor/sht41";              // {"temp":..,"hum":..} (compatibilidad v1.0)
const char* TOPIC_TEMPERATURA = "sensor/sht41/temperatura";  // "24.6"
const char* TOPIC_HUMEDAD     = "sensor/sht41/humedad";      // "58.0"
const char* TOPIC_LED_ESTADO  = "actuador/led/estado";       // "ON" / "OFF" (retained)
const char* TOPIC_STATUS      = "esp32/status";              // "online" / "offline" (retained, LWT)

// Topic de suscripcion (Node-RED -> ESP32)
const char* TOPIC_LED_SET     = "actuador/led/set";          // "ON" / "OFF"

// ---------- Pines y direcciones I2C ----------
#define SDA_PIN 21
#define SCL_PIN 22
#define LED_PIN 2          // LED externo (220 ohm a GND) + LED azul integrado del DevKit
#define OLED_ADDR 0x3C
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32

// ---------- Intervalos (no bloqueantes) ----------
const unsigned long INTERVALO_PUBLICACION_MS = 2000; // Leer y publicar cada 2 segundos
const unsigned long INTERVALO_OLED_MS = 3000;        // Alternar la OLED cada 3 segundos
const unsigned long INTERVALO_REINTENTO_WIFI_MS = 5000;
const unsigned long INTERVALO_REINTENTO_MQTT_MS = 3000;

Adafruit_SHT4x sht4 = Adafruit_SHT4x();
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

WiFiClient espClient;
PubSubClient mqttClient(espClient);

unsigned long ultimaPublicacion = 0;
unsigned long ultimoCambioOled = 0;
unsigned long ultimoIntentoWiFi = 0;
unsigned long ultimoIntentoMQTT = 0;

bool mostrandoTemperatura = true;
bool wifiReportado = false;  // Para imprimir la IP solo una vez por conexion

float temperaturaActual = 0;
float humedadActual = 0;
bool ledEncendido = false;   // Estado REAL del LED (se refleja en OLED y dashboard)

// ============================================================================
//  OLED
// ============================================================================

// Dibuja la pantalla actual (temperatura o humedad) con el estado del LED
// siempre visible en la esquina superior derecha.
void actualizarOled() {
  const char* etiqueta = mostrandoTemperatura ? "Temperatura" : "Humedad";
  float valor          = mostrandoTemperatura ? temperaturaActual : humedadActual;
  const char* unidad   = mostrandoTemperatura ? "C" : "%";
  const char* textoLed = ledEncendido ? "LED:ON" : "LED:OFF";

  display.clearDisplay();

  // Linea superior (texto pequeno): etiqueta a la izquierda, LED a la derecha
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print(etiqueta);
  int anchoLed = strlen(textoLed) * 6;  // 6 px por caracter en tamano 1
  display.setCursor(SCREEN_WIDTH - anchoLed, 0);
  display.print(textoLed);

  // Valor (texto grande)
  display.setTextSize(2);
  display.setCursor(0, 14);
  display.print(valor, 1);
  display.print(" ");
  display.print(unidad);

  display.display();
}

// ============================================================================
//  LED
// ============================================================================

// Cambia el LED fisico y confirma el estado real a Node-RED y a la OLED.
void aplicarLed(bool encender) {
  ledEncendido = encender;
  digitalWrite(LED_PIN, encender ? HIGH : LOW);

  Serial.print("LED -> ");
  Serial.println(encender ? "ON" : "OFF");

  if (mqttClient.connected()) {
    mqttClient.publish(TOPIC_LED_ESTADO, encender ? "ON" : "OFF", true); // retained
  }
  actualizarOled(); // Reflejar el cambio de inmediato, sin esperar la rotacion
}

// ============================================================================
//  MQTT
// ============================================================================

// Se ejecuta cuando llega un mensaje a un topic suscrito.
void callbackMQTT(char* topic, byte* payload, unsigned int length) {
  // Copiar el payload: PubSubClient reutiliza su buffer al publicar,
  // y aplicarLed() publica el estado dentro de este callback.
  char mensaje[16];
  unsigned int n = length < sizeof(mensaje) - 1 ? length : sizeof(mensaje) - 1;
  for (unsigned int i = 0; i < n; i++) {
    mensaje[i] = toupper((char)payload[i]);
  }
  mensaje[n] = '\0';

  // Quitar espacios/saltos de linea al final (ej. "ON\n")
  while (n > 0 && isspace((unsigned char)mensaje[n - 1])) {
    mensaje[--n] = '\0';
  }

  Serial.print("Mensaje recibido [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(mensaje);

  if (strcmp(topic, TOPIC_LED_SET) == 0) {
    if (strcmp(mensaje, "ON") == 0) {
      aplicarLed(true);
    } else if (strcmp(mensaje, "OFF") == 0) {
      aplicarLed(false);
    } else {
      Serial.println("Comando de LED no valido (se esperaba ON/OFF). Ignorado.");
    }
  }
}

// Intenta UNA conexion al broker (no bloquea). Devuelve true si se conecto.
bool conectarMQTT() {
  Serial.print("Conectando a broker MQTT...");

  // LWT: si el ESP32 se desconecta sin avisar, el broker publica "offline"
  bool ok = mqttClient.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASSWORD,
                               TOPIC_STATUS, 0, true, "offline");
  if (!ok) {
    Serial.print(" fallo, rc=");
    Serial.print(mqttClient.state());
    Serial.println(" (se reintentara)");
    return false;
  }

  Serial.println(" conectado.");
  mqttClient.publish(TOPIC_STATUS, "online", true);
  // Publicar el estado actual antes de suscribirse; si existe un comando
  // retenido en led/set, llegara enseguida y actualizara el estado.
  mqttClient.publish(TOPIC_LED_ESTADO, ledEncendido ? "ON" : "OFF", true);
  mqttClient.subscribe(TOPIC_LED_SET, 1); // QoS 1 para los comandos
  return true;
}

// Mantiene WiFi y MQTT conectados sin bloquear el loop().
void mantenerConexiones(unsigned long ahora) {
  if (WiFi.status() != WL_CONNECTED) {
    wifiReportado = false;
    if (ahora - ultimoIntentoWiFi >= INTERVALO_REINTENTO_WIFI_MS) {
      ultimoIntentoWiFi = ahora;
      Serial.println("WiFi desconectado, reintentando...");
      WiFi.disconnect();
      WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    }
    return; // Sin WiFi no tiene sentido intentar MQTT
  }

  if (!wifiReportado) {
    wifiReportado = true;
    Serial.print("WiFi conectado. IP del ESP32: ");
    Serial.println(WiFi.localIP());
  }

  if (!mqttClient.connected()) {
    if (ahora - ultimoIntentoMQTT >= INTERVALO_REINTENTO_MQTT_MS) {
      ultimoIntentoMQTT = ahora;
      conectarMQTT();
    }
    return;
  }

  mqttClient.loop(); // Procesa mensajes entrantes y mantiene el keepalive
}

// ============================================================================
//  Sensor y publicacion
// ============================================================================

void leerYPublicar() {
  sensors_event_t humedad_evento, temp_evento;
  if (!sht4.getEvent(&humedad_evento, &temp_evento)) {
    Serial.println("Error leyendo el SHT41; se omite esta publicacion.");
    return;
  }

  temperaturaActual = temp_evento.temperature;
  humedadActual = humedad_evento.relative_humidity;

  Serial.println("---- Lectura SHT41 ----");
  Serial.print("Temperatura: "); Serial.print(temperaturaActual); Serial.println(" C");
  Serial.print("Humedad: "); Serial.print(humedadActual); Serial.println(" %");

  if (!mqttClient.connected()) {
    Serial.println("MQTT desconectado; lectura solo local (OLED).");
    return;
  }

  // 1) JSON combinado (compatibilidad con el dashboard v1.0)
  JsonDocument doc;
  doc["temp"] = round(temperaturaActual * 10) / 10.0;
  doc["hum"] = round(humedadActual * 10) / 10.0;
  char buffer[128];
  size_t n = serializeJson(doc, buffer);
  mqttClient.publish(TOPIC_JSON, (const uint8_t*)buffer, n, false);

  // 2) Topics independientes (valor numerico en texto plano)
  char valor[12];
  snprintf(valor, sizeof(valor), "%.1f", temperaturaActual);
  mqttClient.publish(TOPIC_TEMPERATURA, valor);
  snprintf(valor, sizeof(valor), "%.1f", humedadActual);
  mqttClient.publish(TOPIC_HUMEDAD, valor);

  Serial.print("Publicado en MQTT: ");
  Serial.println(buffer);
}

// ============================================================================
//  setup / loop
// ============================================================================

void setup() {
  Serial.begin(115200);
  delay(500);

  // LED: arranca apagado hasta recibir un comando
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

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

  // WiFi (la conexion se completa en segundo plano; ver mantenerConexiones)
  Serial.print("Conectando a WiFi: ");
  Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  ultimoIntentoWiFi = millis();

  // MQTT
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCallback(callbackMQTT);
  mqttClient.setKeepAlive(MQTT_KEEPALIVE_S);

  Serial.println("Sistema listo.");
}

void loop() {
  unsigned long ahora = millis();

  mantenerConexiones(ahora);

  // ---- Lectura y publicacion cada 2 segundos (no bloqueante) ----
  if (ahora - ultimaPublicacion >= INTERVALO_PUBLICACION_MS) {
    ultimaPublicacion = ahora;
    leerYPublicar();
  }

  // ---- Alternar la OLED cada 3 segundos (no bloqueante) ----
  if (ahora - ultimoCambioOled >= INTERVALO_OLED_MS) {
    ultimoCambioOled = ahora;
    mostrandoTemperatura = !mostrandoTemperatura;
    actualizarOled();
  }
}