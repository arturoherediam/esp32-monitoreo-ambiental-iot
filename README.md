# ESP32 Monitoreo Ambiental IoT

Monitor de calidad del aire y confort ambiental basado en ESP32 y sensor BME680, con dashboard local en tiempo real vía MQTT (Mosquitto) y Node-RED.

ESP32-based indoor air quality and comfort monitor using a BME680 sensor, with a real-time local dashboard via MQTT (Mosquitto) and Node-RED.

## Problema que resuelve

Detectar en tiempo real cuándo el aire de un espacio cerrado (dormitorio, oficina en casa, salón de estudio) se degrada por acumulación de CO2/VOC, o cuándo la humedad/temperatura salen de un rango de confort — sin depender de la percepción subjetiva.

## Arquitectura

```
Variable física → Sensor (BME680) → ESP32 → Comunicación (WiFi + MQTT) → Servicio IoT (Mosquitto + Node-RED) → Usuario (Dashboard web + pantalla OLED)
```

- **Variable física:** temperatura, humedad relativa, presión atmosférica y calidad de aire (IAQ) — las 4 variables que entrega el BME680.
- **Sensor:** BME680, conectado al ESP32 por I2C (mismo bus que la pantalla OLED).
- **ESP32:** lee el sensor, calcula el índice IAQ (librería BSEC), muestra los valores en la pantalla OLED local, y publica los datos por MQTT en formato JSON.
- **Protocolo:** MQTT sobre WiFi (pub/sub).
- **Servicio IoT:** Mosquitto como broker MQTT local + Node-RED con Dashboard 2.0 para la interfaz web.
- **Usuario:** puede ver los datos en la pantalla OLED del ESP32 (lectura instantánea) o en el dashboard web de Node-RED (histórico y tendencias).

## Estado actual del proyecto

- [x] Broker MQTT (Mosquitto) instalado y probado.
- [x] Node-RED + Dashboard 2.0 instalado y configurado.
- [x] Flujo de dashboard funcional (gauges de temperatura/humedad/IAQ, texto de presión, gráfica de tendencia), validado con datos simulados.
- [ ] Firmware del ESP32 (lectura BME680 + pantalla OLED + publicación MQTT).
- [ ] Integración del hardware real con el dashboard.
- [ ] Seguridad de la conexión MQTT (autenticación y cifrado).

## Estructura del repositorio

```
firmware/   → Código del ESP32 (Arduino/PlatformIO)
node-red/   → Export JSON del flujo de Node-RED (importable directamente)
docs/       → Documentación técnica del proyecto
hardware/   → Esquema de conexiones y lista de materiales
```

## Instalación del Servicio IoT (Mosquitto + Node-RED)

```bash
# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Instalar Mosquitto (broker MQTT)
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto

# Instalar Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Instalar Node-RED
sudo npm install -g --unsafe-perm node-red
node-red
```

Editor de Node-RED: `http://localhost:1880`
Dashboard: `http://localhost:1880/dashboard`

Desde el editor, instalar el paquete `node-red-dashboard` (menú ☰ → Manage palette → Install), e importar el flujo incluido en `node-red/flujo-dashboard.json`.

Documentación técnica completa del Servicio IoT en [`docs/documentacion_servicio_iot.md`](docs/documentacion_servicio_iot.md).

## Materiales (hardware)

- ESP32
- Sensor BME680 (temperatura, humedad, presión, gas/IAQ)
- Pantalla OLED 128x64 (I2C, SSD1306)

## Licencia

MIT — ver [LICENSE](LICENSE).
