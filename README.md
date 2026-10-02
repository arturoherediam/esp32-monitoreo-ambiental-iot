# ESP32 Monitoreo Ambiental IoT

Monitor de confort térmico basado en ESP32 y sensor SHT41, con dashboard local en tiempo real vía MQTT (Mosquitto) y Node-RED.

ESP32-based thermal comfort monitor using a Sensirion SHT41 sensor, with a real-time local dashboard via MQTT (Mosquitto) and Node-RED.

## Problema que resuelve

Monitoreo de confort térmico en un espacio cerrado de uso personal (dormitorio, oficina en casa, salón de estudio), para saber en tiempo real cuándo la temperatura o la humedad relativa salen de un rango de confort — sin depender de la percepción subjetiva, que suele notar el malestar hasta que ya es incómodo.

## Arquitectura

```
Variable física → Sensor (SHT41) → ESP32 → Comunicación (WiFi + MQTT) → Servicio IoT (Mosquitto + Node-RED) → Usuario (Dashboard web + pantalla OLED)
```

- **Variable física:** temperatura y humedad relativa — medidas por el sensor SHT41.
- **Sensor:** SHT41 (Sensirion), conectado al ESP32 por I2C (mismo bus que la pantalla OLED).
- **ESP32:** lee el sensor cada 1 segundo, muestra los valores en la pantalla OLED local (alternando cada 3s), y publica los datos por MQTT en formato JSON, autenticado con usuario/contraseña.
- **Protocolo:** MQTT sobre WiFi (pub/sub), sobre un hotspot local creado por la laptop (red aislada, sin depender de internet).
- **Servicio IoT:** Mosquitto (con autenticación y firewall restringido) como broker MQTT local + Node-RED con Dashboard 2.0 para la interfaz web.
- **Usuario:** puede ver los datos en la pantalla OLED del ESP32 (lectura instantánea) o en el dashboard web de Node-RED (histórico y tendencias).

> **Nota:** el proyecto inició con un sensor BME680 (4 variables: temp/humedad/presión/IAQ), descartado tras confirmar un defecto de hardware en su canal de temperatura. Ver `docs/documentacion_servicio_iot.md` para el detalle del diagnóstico.

## Estado actual del proyecto

- [x] Broker MQTT (Mosquitto) instalado, con autenticación y firewall restringido.
- [x] Node-RED + Dashboard 2.0 instalado y configurado.
- [x] Firmware del ESP32: lectura SHT41 + pantalla OLED + publicación MQTT autenticada, cada 1 segundo, sin bloqueos (millis).
- [x] Flujo de dashboard funcional (gauges de temperatura/humedad, gráficas de tendencia), validado con datos reales del sensor.
- [x] Auditoría y refuerzo de seguridad general (puertos expuestos, fail2ban, políticas de firewall).

**Versión final (v1.0).**

### Limitaciones conocidas

- Si el ESP32 se desconecta, los gauges conservan el último valor recibido en lugar de volver a cero. La solución prevista es implementar Last Will and Testament (LWT) en el firmware (ver *Trabajo futuro*).

## Estructura del repositorio

```
firmware/esp32-monitoreo-ambiental/   → Código del ESP32 (PlatformIO)
node-red/   → Export JSON del flujo de Node-RED (importable directamente)
docs/       → Documentación técnica del proyecto
hardware/   → Esquema de conexiones y lista de materiales
```

## Instalación del Servicio IoT (Mosquitto + Node-RED)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto

curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g --unsafe-perm node-red
node-red
```

Editor de Node-RED: `http://localhost:1880`
Dashboard: `http://localhost:1880/dashboard`

Documentación técnica completa (incluye configuración de seguridad y firmware) en [`docs/documentacion_servicio_iot.md`](docs/documentacion_servicio_iot.md).

## Materiales (hardware)

- ESP32
- Sensor GY-SHT41 (temperatura y humedad, Sensirion SHT41)
- Pantalla OLED 128x32 (I2C, SSD1306)

Detalle completo en [`hardware/hardware_conexion.md`](hardware/hardware_conexion.md).

## Trabajo futuro / Escalabilidad

Este proyecto está diseñado pensando en una posible evolución hacia un sistema multi-nodo:

- **Nodo central dedicado:** migrar el broker/dashboard de la laptop a una placa siempre encendida (ej. Orange Pi Zero 3), colocada estratégicamente en el hogar. La Orange Pi Zero 3 cuenta con WiFi y Ethernet (RJ45) simultáneos: WiFi en modo Access Point (`hostapd` + `dnsmasq`) para que los nodos ESP32 se conecten localmente, y Ethernet como salida hacia el router doméstico (o conexión directa a una laptop para pruebas sin router). El dashboard sería accesible tanto desde la red WiFi del nodo como desde la red Ethernet/router.
- **Múltiples nodos sensores/actuadores:** convención de tópicos por dispositivo/habitación (ej. `casa/<habitacion>/<tipo>`), permitiendo escalar de un sensor a varios sin cambiar la arquitectura base (mismo broker, mismo patrón pub/sub).
- **Actuadores:** un ESP32 con relé/servo se suscribiría a un tópico de comando; la lógica de decisión (ej. "si temp > 28°C, activa el ventilador") viviría centralizada en Node-RED, no en cada MCU.
- **Acceso remoto seguro:** VPN personal (Tailscale o WireGuard) para administrar el nodo central y ver el dashboard desde fuera de casa, sin exponer puertos directamente a internet.
- **Mejoras de seguridad pendientes:** cifrado TLS en MQTT (si el sistema sale de una red controlada), Last Will and Testament (LWT) en el firmware para detección instantánea de desconexión.

## Licencia

MIT — ver [LICENSE](LICENSE).
