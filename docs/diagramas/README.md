# Generadores de diagramas

Scripts en Python (sin dependencias externas) que generan los diagramas del proyecto como SVG.

| Script | Salida | Ubicación en el repo |
|---|---|---|
| `diagrama_conexiones.py` | Diagrama de conexiones (ESP32 + SHT41 + OLED + LED) | `hardware/diagrama_conexiones.svg` |
| `diagrama_arquitectura.py` | Arquitectura IoT y tópicos MQTT | `docs/diagrama_arquitectura.svg` |

## Regenerar

Desde la raíz del repositorio:

```bash
python3 docs/diagramas/diagrama_conexiones.py hardware/diagrama_conexiones.svg
python3 docs/diagramas/diagrama_arquitectura.py docs/diagrama_arquitectura.svg
```

## Exportar a PNG

Cualquier convertidor de SVG sirve, por ejemplo:

```bash
# librsvg (sudo apt install librsvg2-bin), a doble resolución
rsvg-convert -z 2 hardware/diagrama_conexiones.svg -o hardware/diagrama_conexiones.png
rsvg-convert -z 2 docs/diagrama_arquitectura.svg -o docs/diagrama_arquitectura.png
```

También se puede abrir el SVG en Inkscape o en el navegador y exportar desde ahí. Las fuentes usadas son DejaVu Sans / DejaVu Sans Mono.
