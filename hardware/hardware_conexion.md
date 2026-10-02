# Hardware — Lista de materiales y conexión

## Lista de materiales (BOM)

| # | Componente | Especificación | Cantidad |
|---|---|---|---|
| 1 | Microcontrolador | ESP32 DevKit v1 (WiFi + Bluetooth) | 1 |
| 2 | Sensor ambiental | GY-SHT41 (Sensirion SHT41: temperatura y humedad de alta precisión), módulo I2C | 1 |
| 3 | Pantalla | OLED 128x32, controlador SSD1306, interfaz I2C | 1 |
| 4 | Protoboard | Breadboard estándar (830 puntos) | 1 |
| 5 | Cables | Jumper wires macho-macho | ~8 |
| 6 | Alimentación | Cable USB (datos) para el ESP32 | 1 |

**Nota sobre el cambio de sensor:** el proyecto inició con un módulo BME680, descartado tras un diagnóstico exhaustivo que confirmó un defecto de hardware específico en su canal de temperatura (el chip reportaba consistentemente `adc_T = 0` en el registro crudo, incluso sin librerías ni calentador de gas activo — ver sección de diagnóstico en `docs/documentacion_servicio_iot.md`). Se sustituyó por un GY-SHT41, que solo mide temperatura y humedad (sin presión ni IAQ/gas), lo cual redefinió el alcance del problema hacia confort térmico únicamente.

## Diagrama de conexión (bus I2C compartido)

El ESP32, el SHT41 y la pantalla OLED comparten un mismo bus I2C de 4 líneas.

| Señal | Pin ESP32 | Destino |
|---|---|---|
| Alimentación | `3V3` | VCC del SHT41 y de la OLED |
| Tierra | `GND` | GND del SHT41 y de la OLED |
| Datos I2C | `GPIO21` (SDA) | SDA del SHT41 y de la OLED |
| Reloj I2C | `GPIO22` (SCL) | SCL del SHT41 y de la OLED |

**Direcciones I2C (confirmadas con escáner I2C):**
- SHT41: `0x44` (dirección por defecto)
- OLED SSD1306: `0x3C`

Total de cables físicos necesarios: **4** (compartidos entre ambos módulos, conectados en paralelo sobre el mismo bus).

## Notas de montaje

- No se requirieron resistencias pull-up adicionales — ambos módulos (SHT41 y OLED) traen pull-ups integradas en su breakout.
- El ESP32 opera a lógica de 3.3V; ambos módulos son compatibles nativamente.
