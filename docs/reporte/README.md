# Reporte Técnico LaTeX — Comunicación Bidireccional IoT (ESP32 $\longleftrightarrow$ Node-RED)

**Autores:** Arturo Heredia, Diego López  
**Práctica:** Unidad 2 — Comunicación Bidireccional MQTT con ESP32 y Node-RED  

Este directorio contiene el reporte técnico en **LaTeX** con estructura concisa y directa, preparado para subirse a **Overleaf** y compilar sin errores en `pdfLaTeX`.

---

## 📁 Estructura del Proyecto

```text
docs/reporte/
├── main.tex                    # Documento principal
├── README.md                   # Esta guía
├── reporte_overleaf.zip        # Archivo ZIP listo para subir a Overleaf
├── imagenes/                   # Diagramas y evidencias gráficas
│   ├── diagrama_arquitectura.png           # Arquitectura IoT y tópicos MQTT
│   ├── diagrama_conexiones.png             # Esquemático de conexiones ESP32
│   ├── ciclo_control_closed_loop.png       # Ciclo de control con confirmación
│   ├── dashboard_nodered.png               # Captura del Node-RED Dashboard 2.0
│   └── evidencia_montaje_protoboard.png    # Registro del montaje físico
└── secciones/                  # Secciones modulares y concisas
    ├── 00_portada.tex                      # Portada (Arturo Heredia y Diego López)
    ├── 01_objetivo.tex                     # Objetivo y matriz de los 10 requerimientos
    ├── 02_materiales.tex                   # Materiales (DHT11 vs SHT41, OLED)
    ├── 03_diagrama_conexion.tex            # Pinout, cálculo de LED y bus I2C
    ├── 04_arquitectura_sistema.tex         # 3 capas IoT y red local
    ├── 05_descripcion_funcionamiento.tex   # Flujo, lazo cerrado y LWT
    ├── 06_configuracion_mqtt.tex           # Broker, IP, puerto 1883, usuarios y ACL
    ├── 07_topics_utilizados.tex            # Tópicos, payloads, QoS y retain
    ├── 08_explicacion_codigo.tex           # Firmware ESP32 y flujo Node-RED
    ├── 09_evidencias.tex                   # Montaje, Dashboard y enlace a video
    ├── 10_problemas_solucion.tex           # Tabla de problemas y soluciones
    └── 11_conclusiones.tex                 # Conclusiones y trabajo futuro
```

---

## 🚀 Cómo Subir a Overleaf

1. Descarga el archivo [`reporte_overleaf.zip`](reporte_overleaf.zip).
2. En [Overleaf](https://www.overleaf.com/), presiona **"New Project"** $\to$ **"Upload Project"**.
3. Arrastra y suelta el archivo `reporte_overleaf.zip`.
4. Haz clic en **"Recompile"** (compilador por defecto `pdfLaTeX`).
