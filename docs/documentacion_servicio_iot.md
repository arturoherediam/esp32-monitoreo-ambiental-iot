# Documentación — Servicio IoT (Mosquitto + Node-RED + Dashboard)

## 1. Resumen

Esta sección documenta la implementación completa del Servicio IoT del proyecto de monitoreo de confort ambiental: broker MQTT local (Mosquitto, con autenticación), capa de visualización (Node-RED + Dashboard 2.0), y el firmware del ESP32 con el sensor GY-SHT41, publicando datos reales por MQTT.

## 2. Cambio de sensor: de BME680 a SHT41

El proyecto inició con un sensor BME680 (temperatura, humedad, presión, gas/IAQ). Tras cablear el sensor correctamente (confirmado con un escáner I2C) y validar que la calibración de fábrica del chip era válida, se detectó que el canal de temperatura devolvía consistentemente un valor crudo `adc_T = 0` — comprobado mediante lectura directa de registros I2C, sin ninguna librería intermedia y sin el calentador de gas activo. Esto descartó causas de software (se probaron 3 versiones de la librería Adafruit_BME680) y confirmó un defecto de hardware específico de esa unidad.

Se sustituyó por un módulo **GY-SHT41** (sensor Sensirion SHT41), que mide únicamente temperatura y humedad relativa, con mayor precisión que el canal equivalente del BME680. Esto redujo el alcance de variables físicas del proyecto de 4 a 2, y redefinió el planteamiento del problema hacia **confort térmico** exclusivamente (sin calidad de aire/CO2).

## 3. Instalación del entorno (sin cambios respecto al sensor)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto

curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g --unsafe-perm node-red
```

Dashboard: `node-red-dashboard` (Dashboard 2.0 / `@flowfuse/node-red-dashboard`), instalado desde el editor (menú ☰ → Manage palette → Install).

## 4. Red: hotspot local en la laptop

Para no depender de una red doméstica, el ESP32 se conecta a un **hotspot WiFi creado por la propia laptop** (herramienta `nmcli` de NetworkManager), aislando el sistema de cualquier red externa:

```bash
nmcli device wifi hotspot ifname <interfaz_wifi> ssid ESP32-Proyecto password "<contraseña>"
nmcli connection modify Hotspot ipv4.method shared ipv4.addresses 10.42.0.1/24
```

La segunda línea fija la IP del hotspot de forma permanente (`10.42.0.1`), evitando que cambie en cada activación.

## 5. Seguridad de la conexión MQTT

### 5.1 Autenticación obligatoria en Mosquitto

Se creó un usuario dedicado y se desactivó el acceso anónimo:

```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd esp32_user
sudo chown mosquitto:mosquitto /etc/mosquitto/passwd
sudo chmod 640 /etc/mosquitto/passwd
```

Archivo `/etc/mosquitto/conf.d/local.conf`:
```
listener 1883 0.0.0.0
allow_anonymous false
password_file /etc/mosquitto/passwd
```

### 5.2 Firewall restringido a la subred del hotspot

```bash
sudo ufw allow from 10.42.0.0/24 to any port 1883 proto tcp
```

Solo dispositivos conectados al hotspot (`10.42.0.x`) pueden alcanzar el puerto MQTT; en cualquier otra red (ej. WiFi doméstica o institucional), el puerto queda cerrado por la política de firewall por defecto (`deny incoming`).

### 5.3 Auditoría general de puertos expuestos

Se revisaron todos los puertos en escucha (`ss -tlnp`) y se confirmó que, además de Mosquitto, no había otros servicios expuestos a la red (SSH no estaba instalado, se limpió la regla de firewall correspondiente). Se instaló `fail2ban` como protección general del sistema.

### 5.4 Decisiones de alcance en seguridad

- **TLS/cifrado del canal MQTT**: no implementado. El canal ya está protegido por el cifrado WPA2 del hotspot (adecuado para una red aislada y controlada como la de este proyecto). Se documenta como mejora futura si el sistema migra a una red compartida con terceros.
- **Last Will and Testament (LWT)**: no implementado en el firmware actual. Permitiría que el propio broker notifique instantáneamente cuando el ESP32 se desconecta, en vez de depender de un temporizador estimado del lado de Node-RED. Documentado como mejora futura.

## 6. Firmware del ESP32 (SHT41 + OLED + MQTT)

### 6.1 Librerías (platformio.ini)

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
lib_deps =
    adafruit/Adafruit SHT4x Library@^1.0.4
    adafruit/Adafruit SSD1306@^2.5.9
    adafruit/Adafruit GFX Library@^1.11.9
    adafruit/Adafruit BusIO@^1.14.5
    knolleary/PubSubClient@^2.8
    bblanchon/ArduinoJson@^7.1.0
```

### 6.2 Diseño no bloqueante (millis en vez de delay)

El firmware publica por MQTT cada 1 segundo y alterna la pantalla OLED cada 3 segundos, ambos de forma independiente mediante temporizadores basados en `millis()`, evitando el uso de `delay()` bloqueante que impediría que ambas tareas corrieran en paralelo.

### 6.3 Formato de publicación

Tópico: `sensor/sht41`. Payload JSON:
```json
{"temp": 24.3, "hum": 55.8}
```

Autenticado con usuario/contraseña MQTT al conectar (`mqttClient.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASSWORD)`).

## 7. Flujo de Node-RED

### 7.1 Nodo mqtt-in

Configurado con:
- Server: `localhost:1883` (Node-RED corre en la misma laptop que Mosquitto)
- Security: usuario/contraseña `esp32_user`
- Topic: `sensor/sht41`
- Output: "a parsed JSON object" (conversión automática del payload a objeto usable)

### 7.2 Widgets del dashboard

| Widget | Tipo de nodo | Propiedad | Rango | Unidad |
|---|---|---|---|---|
| Temperatura | `gauge` | `payload.temp` | 0–50 | °C |
| Humedad | `gauge` | `payload.hum` | 0–100 | % |
| Tendencia Temperatura | `chart` (Line) | `payload.temp` | 0–50 | °C |
| Tendencia Humedad | `chart` (Line) | `payload.hum` | 0–100 | % |

Los widgets de presión e IAQ del diseño original (BME680) fueron eliminados del flujo al migrar al SHT41.

### 7.3 Mejora pendiente: reinicio a cero por inactividad

Se diseñó un nodo `trigger` entre el `mqtt-in` y los widgets, para resetear los gauges a `{temp:0, hum:0}` si el ESP32 deja de publicar (simulando una desconexión). Durante las pruebas, el nodo no reenviaba correctamente los mensajes intermedios, dejando el dashboard "congelado" en el primer valor. Se retiró temporalmente del flujo (los widgets se alimentan directo del `mqtt-in`) y queda documentado como mejora futura — la alternativa más robusta sería implementar Last Will and Testament (LWT) en el firmware, en vez de un temporizador estimado en Node-RED.

## 8. Validación end-to-end

Con Mosquitto, Node-RED, el hotspot y el ESP32 activos simultáneamente, se confirmó:
- El ESP32 publica un mensaje JSON válido cada 1 segundo, autenticado correctamente.
- Node-RED recibe y parsea los mensajes en tiempo real (confirmado con un nodo `debug`).
- El dashboard (`http://localhost:1880/dashboard`) refleja los valores reales de temperatura y humedad del ambiente, incluyendo cambios al mover el sensor a un espacio climatizado distinto.
