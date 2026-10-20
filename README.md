# ESP32 Monitoreo Ambiental IoT

Monitor de confort térmico basado en ESP32 y sensor SHT41, con dashboard local en tiempo real vía MQTT (Mosquitto) y Node-RED, y **comunicación bidireccional**: el dashboard también controla un LED en el ESP32 y muestra su estado real.

ESP32-based thermal comfort monitor using a Sensirion SHT41 sensor, with a real-time local dashboard via MQTT (Mosquitto) and Node-RED, plus **bidirectional communication**: the dashboard controls an LED on the ESP32 and shows its confirmed state.

## Problema que resuelve

Monitoreo de confort térmico en un espacio cerrado de uso personal (dormitorio, oficina en casa, salón de estudio), para saber en tiempo real cuándo la temperatura o la humedad relativa salen de un rango de confort — sin depender de la percepción subjetiva, que suele notar el malestar hasta que ya es incómodo.

## Arquitectura

```
Variable física → Sensor (SHT41) → ESP32 ⇄ Comunicación (WiFi + MQTT) ⇄ Servicio IoT (Mosquitto + Node-RED) ⇄ Usuario (Dashboard web + pantalla OLED)
```

![Arquitectura IoT y comunicación MQTT](docs/diagrama_arquitectura.png)

- **Variable física:** temperatura y humedad relativa — medidas por el sensor SHT41.
- **Sensor:** SHT41 (Sensirion), conectado al ESP32 por I2C (mismo bus que la pantalla OLED).
- **Actuador:** LED en `GPIO 2` (con resistencia de 220 Ω), controlado desde el dashboard.
- **ESP32:** lee el sensor cada 2 segundos y publica por MQTT (autenticado). Recibe comandos ON/OFF para el LED, los aplica y **confirma el estado real**. La pantalla OLED alterna temperatura/humedad cada 3 s y muestra siempre el estado del LED (`LED:ON` / `LED:OFF`).
- **Protocolo:** MQTT sobre WiFi (pub/sub), sobre un hotspot local creado por la laptop (red aislada, sin depender de internet).
- **Servicio IoT:** Mosquitto (autenticación, ACL por rol y firewall restringido) como broker MQTT local + Node-RED con Dashboard 2.0 para la interfaz web.
- **Usuario:** ve los datos en la OLED (lectura instantánea) o en el dashboard web (gauges, tendencias, control del LED y estado de conexión del ESP32).

### Tópicos MQTT

| Tópico | Dirección | Payload | QoS / Retain |
|---|---|---|---|
| `sensor/sht41/temperatura` | ESP32 → Node-RED | `"24.6"` (°C) | 0 / no |
| `sensor/sht41/humedad` | ESP32 → Node-RED | `"58.0"` (%) | 0 / no |
| `sensor/sht41` | ESP32 → Node-RED | `{"temp":24.6,"hum":58.0}` (compatibilidad v1.0) | 0 / no |
| `actuador/led/set` | Node-RED → ESP32 | `ON` / `OFF` | 1 / sí |
| `actuador/led/estado` | ESP32 → Node-RED | `ON` / `OFF` (confirmación) | 0 / sí |
| `esp32/status` | ESP32 / broker → Node-RED | `online` / `offline` (LWT) | 0 / sí |

**Control con confirmación:** el switch del dashboard publica en `actuador/led/set`; el ESP32 cambia el LED y publica el estado real en `actuador/led/estado`. El switch está desacoplado: solo cambia de posición cuando llega esa confirmación, así el dashboard nunca muestra un estado que el LED no tiene.

**Last Will and Testament (LWT):** al conectarse, el ESP32 registra en el broker el mensaje `esp32/status = offline`. Si deja de comunicarse (corte de energía o de WiFi), el broker lo publica automáticamente y el dashboard muestra "Desconectado" con un aviso.

> **Nota:** el proyecto inició con un sensor BME680 (4 variables: temp/humedad/presión/IAQ), descartado tras confirmar un defecto de hardware en su canal de temperatura. Ver `docs/documentacion_servicio_iot.md` para el detalle del diagnóstico.

## Estado actual del proyecto

**v1.0 — Monitoreo (unidireccional)**
- [x] Broker MQTT (Mosquitto) instalado, con autenticación y firewall restringido.
- [x] Node-RED + Dashboard 2.0 instalado y configurado.
- [x] Firmware del ESP32: lectura SHT41 + pantalla OLED + publicación MQTT autenticada, sin bloqueos (`millis()`).
- [x] Auditoría y refuerzo de seguridad general (puertos expuestos, fail2ban, políticas de firewall).

**Práctica Unidad 2 — Comunicación bidireccional**
- [x] Control de un LED desde el dashboard (`actuador/led/set`) con confirmación del estado real (`actuador/led/estado`).
- [x] Tópicos separados para temperatura y humedad (se mantiene el JSON de v1.0 por compatibilidad).
- [x] LWT (`esp32/status`): detección de desconexión del ESP32 en el dashboard.
- [x] Estado del LED siempre visible en la OLED.
- [x] Reconexión WiFi/MQTT no bloqueante: el sensor y la OLED siguen funcionando sin red.
- [x] ACL en Mosquitto con un usuario por rol (`esp32_user` para el dispositivo, `dashboard` para Node-RED).
- [x] Nuevo flujo de Node-RED (Dashboard 2.0) y diagramas de conexión y arquitectura.

## Estructura del repositorio

```
firmware/esp32-monitoreo-ambiental/   → Código del ESP32 (PlatformIO)
firmware/esp32-scanner-i2c/           → Escáner I2C de diagnóstico (verifica 0x44 y 0x3C)
node-red/dashboard.json               → Flujo de Node-RED (importable directamente)
docs/                                 → Documentación técnica y diagrama de arquitectura
docs/diagramas/                       → Scripts que generan los diagramas (SVG)
hardware/                             → Lista de materiales, conexiones y diagrama de conexión
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

- Editor de Node-RED: `http://localhost:1880`
- Dashboard: `http://localhost:1880/dashboard/practica-u2`

Después de importar `node-red/dashboard.json`, captura el usuario y la contraseña MQTT en el nodo de configuración "Mosquitto local" (pestaña *Security*): los flujos exportados nunca incluyen credenciales.

Documentación técnica completa (seguridad, ACL, firmware, flujo y solución de problemas) en [`docs/documentacion_servicio_iot.md`](docs/documentacion_servicio_iot.md).

## Materiales (hardware)

- ESP32 DevKit V1 (30 pines)
- Sensor GY-SHT41 (temperatura y humedad, Sensirion SHT41)
- Pantalla OLED 128x32 (I2C, SSD1306)
- LED de 5 mm + resistencia de 220 Ω

Detalle completo y diagrama en [`hardware/hardware_conexion.md`](hardware/hardware_conexion.md).

## Trabajo futuro / Escalabilidad

Este proyecto está diseñado pensando en una posible evolución hacia un sistema multi-nodo:

- **Nodo central dedicado:** migrar el broker/dashboard de la laptop a una placa siempre encendida (ej. Orange Pi Zero 3), colocada estratégicamente en el hogar. La Orange Pi Zero 3 cuenta con WiFi y Ethernet (RJ45) simultáneos: WiFi en modo Access Point (`hostapd` + `dnsmasq`) para que los nodos ESP32 se conecten localmente, y Ethernet como salida hacia el router doméstico (o conexión directa a una laptop para pruebas sin router). El dashboard sería accesible tanto desde la red WiFi del nodo como desde la red Ethernet/router.
- **Múltiples nodos sensores/actuadores:** convención de tópicos por dispositivo/habitación (ej. `casa/<habitacion>/<tipo>`), permitiendo escalar de un sensor a varios sin cambiar la arquitectura base (mismo broker, mismo patrón pub/sub).
- **Actuadores reales:** el control con confirmación ya está implementado con un LED; el siguiente paso es un relé/ventilador. La lógica de decisión (ej. "si temp > 28°C, activa el ventilador") viviría centralizada en Node-RED, no en cada MCU.
- **Acceso remoto seguro:** VPN personal (Tailscale o WireGuard) para administrar el nodo central y ver el dashboard desde fuera de casa, sin exponer puertos directamente a internet.
- **Mejoras de seguridad pendientes:** cifrado TLS en MQTT (si el sistema sale de una red controlada).

## Licencia

MIT — ver [LICENSE](LICENSE).
