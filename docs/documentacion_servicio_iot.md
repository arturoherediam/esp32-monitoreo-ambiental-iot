# Documentación — Servicio IoT (Mosquitto + Node-RED + Dashboard)

## 1. Resumen

Esta sección documenta la implementación del **Servicio IoT** del proyecto de monitoreo ambiental, correspondiente al bloque "Comunicación → Servicio IoT → Usuario" del diagrama de arquitectura. Se instaló y configuró un broker MQTT local (Mosquitto) y una capa de visualización (Node-RED con Dashboard 2.0), validando el flujo completo con datos simulados antes de integrar el hardware real (ESP32 + BME680).

## 2. Instalación del entorno

### 2.1 Actualización del sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### 2.2 Broker MQTT — Mosquitto
```bash
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl status mosquitto        # debe mostrar "active (running)"
sudo systemctl enable --now mosquitto  # si no arrancó solo
```

Prueba de funcionamiento (dos terminales):
```bash
# Terminal 1 (suscriptor)
mosquitto_sub -h localhost -t test/topic

# Terminal 2 (publicador)
mosquitto_pub -h localhost -t test/topic -m "hola"
```

### 2.3 Node.js (requisito de Node-RED)
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node -v
```

### 2.4 Node-RED
```bash
sudo npm install -g --unsafe-perm node-red
node-red
```
Editor visual disponible en: `http://localhost:1880`

### 2.5 Dashboard
Desde el editor: menú ☰ → **Manage palette** → pestaña **Install** → buscar e instalar `node-red-dashboard`.

**Nota importante:** el paquete instalado en este proyecto fue automáticamente la versión moderna **Dashboard 2.0** (`@flowfuse/node-red-dashboard`, v1.31.0), que reemplaza al Dashboard clásico. Esto se confirmó en menú ☰ → Manage palette → pestaña **Nodes**.

**Detalle técnico observado:** en Dashboard 2.0 la ruta del panel (`/dashboard`, no `/ui` como en el Dashboard clásico) no queda activa hasta que exista al menos un nodo `ui-page`/`ui-group` desplegado en algún flujo. Antes de eso, acceder a la URL devuelve error "Cannot GET".

## 3. Diseño del flujo en Node-RED

Para validar el dashboard sin depender del hardware (aún no ensamblado), se optó por **simular las lecturas del BME680** mediante un generador de datos aleatorios, manteniendo el mismo formato JSON que usará el ESP32 en producción. Esto permite tener la capa de visualización terminada y probada de antemano; cuando el ESP32 esté listo, solo se sustituye el origen de datos (inject+function) por un nodo `mqtt-in`, sin modificar el resto del flujo.

### 3.1 Nodos de origen (simulación)

**Nodo `inject`** — "Simular lectura": disparo repetitivo cada 3 segundos.

**Nodo `function`** — "Generar datos simulados":
```javascript
msg.payload = {
  temp: +(20 + Math.random()*10).toFixed(1),
  hum: +(40 + Math.random()*30).toFixed(1),
  pres: +(1000 + Math.random()*30).toFixed(1),
  iaq: Math.floor(Math.random()*150)
};
return msg;
```
Este nodo entrega un único mensaje `msg.payload` en formato JSON con las 4 variables, replicando la estructura que publicará el ESP32 vía MQTT.

### 3.2 Grupo del dashboard

Se creó una página `monitoreo` (`/dashboard/page2`) con un grupo llamado `ambiente`, tamaño `6x2`, donde se alojan todos los widgets.

### 3.3 Widgets configurados

| Widget | Tipo de nodo | Propiedad (Value) | Rango | Unidad |
|---|---|---|---|---|
| Temperatura | `gauge` (Half Gauge, Needle) | `payload.temp` | 0–50 | °C |
| Humedad | `gauge` | `payload.hum` | 0–100 | % |
| Calidad de aire (IAQ) | `gauge` | `payload.iaq` | 0–300 | IAQ |
| Presión | `text` | `payload.pres` | — | hPa |
| Tendencia Temperatura | `chart` (Line) | Y: `payload.temp` / X: `timestamp` | Y: 0–50 | °C |

**Configuración del chart (corrección aplicada):** el campo **Series** debe fijarse como un valor de texto fijo (`string` → `"Temperatura"`), no como `msg.topic`. Usar `msg.topic` como agrupador de series provoca que el chart cree una serie/línea nueva por cada mensaje (al no tener un topic estable), resultando en una gráfica ilegible con un color distinto por punto en vez de una sola línea continua.

### 3.4 Conexión del flujo

El nodo `function` (fuente única de datos) se conecta en abanico (fan-out) a los 5 nodos de dashboard simultáneamente — cada widget extrae únicamente el campo del JSON que necesita (`payload.temp`, `payload.hum`, `payload.pres`, `payload.iaq`).

```
[inject] → [function: generar datos] → [gauge temp]
                                     → [gauge hum]
                                     → [gauge iaq]
                                     → [text presión]
                                     → [chart tendencia]
```

## 4. Validación

Con el flujo desplegado (Deploy) y accediendo a `http://localhost:1880/dashboard`, se confirmó:
- Los 3 gauges responden y se mueven cada 3 segundos con valores dentro de los rangos esperados.
- El texto de presión se actualiza mostrando valores en hPa.
- El chart dibuja una línea de tendencia continua tras la corrección del campo Series.

## 5. Transición al hardware real (pendiente)

Cuando el firmware del ESP32 esté listo y publicando en MQTT:
1. Sustituir el par `inject` + `function` por un nodo `mqtt-in`.
2. Configurar el nodo `mqtt-in` apuntando al broker local (`localhost:1883`) y suscrito al tópico definido en el firmware (ej. `sensor/bme680`).
3. Si el ESP32 publica el payload ya en JSON, mantener el resto del flujo sin cambios (los widgets seguirán leyendo `payload.temp`, `payload.hum`, etc.).
4. Si el payload llega como texto plano, agregar un nodo `json` intermedio para parsearlo antes de los widgets.
