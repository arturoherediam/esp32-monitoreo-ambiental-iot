import sys
W, H = 1400, 940
F = "DejaVu Sans, Arial, sans-serif"
M = "DejaVu Sans Mono, Consolas, monospace"
TEL, CTL, STA = "#1c71d8", "#e66100", "#813d9c"
o = []; a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{F}">')
a('<defs>')
for n, c in (("tel", TEL), ("ctl", CTL), ("sta", STA), ("gry", "#555")):
    a(f'<marker id="m{n}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>')
a('</defs>')
a(f'<rect width="{W}" height="{H}" fill="#fff"/>')
a('<text x="40" y="46" font-size="24" font-weight="bold" fill="#1a1a1a">Arquitectura IoT y comunicación MQTT — Práctica U2</text>')
a('<text x="40" y="72" font-size="14" fill="#555">Comunicación bidireccional ESP32 ↔ Mosquitto ↔ Node-RED · red local aislada (hotspot de la laptop)</text>')

def box(x, y, w, h, fill, stroke, dash=False, rx=10):
    d = ' stroke-dasharray="8 6"' if dash else ""
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"{d}/>')
def t(x, y, s, size=13, w="normal", fill="#222", anchor="start", font=None):
    ff = f' font-family="{font}"' if font else ""
    a(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}"{ff}>{s}</text>')
def badge(x, y, n, col):
    a(f'<circle cx="{x}" cy="{y}" r="11" fill="{col}"/>')
    t(x, y+4.5, str(n), 12, "bold", "#fff", "middle")
def arrow(x1, y, x2, col, mk):
    a(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{col}" stroke-width="2.5" marker-end="url(#m{mk})"/>')

# ---------- ESP32 node ----------
ex, ey, ew, eh = 40, 110, 300, 470
box(ex, ey, ew, eh, "#eef3fb", "#1f3a5f")
t(ex+150, ey+30, "Nodo ESP32", 17, "bold", "#1f3a5f", "middle")
t(ex+150, ey+50, "DevKit V1 · firmware PlatformIO", 12, "normal", "#555", "middle")
t(ex+16, ey+76, "Cliente:", 12, "bold"); t(ex+80, ey+76, "esp32-sht41", 12, font=M)
t(ex+16, ey+96, "Usuario:", 12, "bold"); t(ex+80, ey+96, "esp32_user", 12, font=M)
t(ex+16, ey+116, "IP:", 12, "bold"); t(ex+80, ey+116, "10.42.0.x (DHCP)", 12, font=M)
t(ex+16, ey+136, "Keepalive:", 12, "bold"); t(ex+96, ey+136, "15 s", 12, font=M)
def sub(y, h, title, lines, col):
    box(ex+14, y, ew-28, h, "#fff", col, rx=6)
    t(ex+28, y+22, title, 13, "bold", col)
    for i, l in enumerate(lines):
        t(ex+28, y+42+i*17, l, 12, "normal", "#333")
sub(ey+156, 82, "Sensor SHT41 (I²C 0x44)", ["Temperatura y humedad", "lectura cada 2 s"], TEL)
sub(ey+250, 82, "OLED SSD1306 (I²C 0x3C)", ["Valor alterno temp./hum.", "+ estado LED:ON / LED:OFF"], "#333")
sub(ey+344, 106, "LED en GPIO 2 (actuador)", ["Callback MQTT: ON/OFF", "→ digitalWrite(GPIO 2)", "→ confirma el estado real"], CTL)
badge(ex+ew-34, ey+366, 3, CTL)

# ---------- Laptop container ----------
lx, ly, lw, lh = 590, 96, 790, 690
box(lx, ly, lw, lh, "#fafafa", "#888", dash=True, rx=14)
t(lx+18, ly+26, "Laptop Linux", 15, "bold", "#333")
t(lx+130, ly+26, "· hotspot WiFi «ESP32-Proyecto» (WPA2) · wlp3s0 = 10.42.0.1", 12, "normal", "#555")

# ---------- Mosquitto ----------
mx, my, mw, mh = 630, 140, 270, 610
box(mx, my, mw, mh, "#f3eefa", STA)
t(mx+mw/2, my+30, "Broker MQTT", 17, "bold", STA, "middle")
t(mx+mw/2, my+50, "Mosquitto 2.0 · puerto 1883/TCP", 12, "normal", "#555", "middle")
yy = my+80
for s in ["allow_anonymous false", "password_file (usuario/contraseña)", "acl_file (permisos por rol)"]:
    t(mx+16, yy, "• " + s, 12); yy += 19
yy += 10
t(mx+16, yy, "Mensajes retenidos (retain):", 12, "bold"); yy += 19
for s in ["actuador/led/set", "actuador/led/estado", "esp32/status"]:
    t(mx+28, yy, s, 12, font=M); yy += 18
yy += 14
a(f'<line x1="{mx+14}" y1="{yy-12}" x2="{mx+mw-14}" y2="{yy-12}" stroke="#d5c8e8"/>')
t(mx+16, yy+6, "ACL por rol", 13, "bold", STA); yy += 30
def acl(user, rules):
    global yy
    t(mx+16, yy, user, 12, "bold", "#222", font=M); yy += 18
    for rw, topic in rules:
        col = TEL if rw == "W" else "#2e7d32"
        a(f'<rect x="{mx+26}" y="{yy-12}" width="18" height="16" rx="3" fill="{col}"/>')
        t(mx+35, yy+1, rw, 11, "bold", "#fff", "middle")
        t(mx+52, yy, topic, 12, font=M); yy += 18
    yy += 8
acl("esp32_user (ESP32)", [("W", "sensor/sht41/#"), ("W", "actuador/led/estado"), ("W", "esp32/status"), ("R", "actuador/led/set")])
acl("dashboard (Node-RED)", [("R", "sensor/#"), ("R", "actuador/led/estado"), ("R", "esp32/status"), ("W", "actuador/led/set")])
t(mx+16, yy+4, "W = publicar · R = suscribirse", 11, "normal", "#555")
yy += 30
a(f'<line x1="{mx+14}" y1="{yy-8}" x2="{mx+mw-14}" y2="{yy-8}" stroke="#d5c8e8"/>')
t(mx+16, yy+12, "Last Will and Testament (LWT)", 13, "bold", STA); yy += 34
for s_ in ["Si el ESP32 no envía nada en", "1.5 × keepalive (≈ 22 s), el broker", "publica esp32/status = \"offline\".".replace('"','&quot;')]:
    t(mx+16, yy, s_, 12); yy += 18

# ---------- ESP32 <-> broker arrows ----------
rows = [
 ("sensor/sht41/temperatura", '"24.6"  ·  QoS 0  ·  cada 2 s', TEL, "tel", ">"),
 ("sensor/sht41/humedad", '"58.0"  ·  QoS 0  ·  cada 2 s', TEL, "tel", ">"),
 ("sensor/sht41", '{"temp","hum"}  ·  compat. v1.0', TEL, "tel", ">"),
 ("actuador/led/estado", '"ON" / "OFF"  ·  retain', CTL, "ctl", ">"),
 ("esp32/status", '"online" · LWT "offline"  ·  retain', STA, "sta", ">"),
 ("actuador/led/set", '"ON" / "OFF"  ·  QoS 1  ·  retain', CTL, "ctl", "<"),
]
x1, x2 = ex+ew, mx
cx = (x1 + x2) / 2 - 10
y0 = 190
for i, (tp, pl, col, mk, d) in enumerate(rows):
    y = y0 + i*62 + (24 if d == "<" else 0)
    if d == ">": arrow(x1+4, y, x2-4, col, mk)
    else: arrow(x2-4, y, x1+4, col, mk)
    t(cx, y-8, tp, 12.5, "bold", col, "middle", M)
    t(cx, y+17, pl, 11, "normal", "#444", "middle")
# badges on ESP32 side
badge(cx+100, 190 + 3*62 - 13, 4, CTL)
badge(cx+90, 190 + 5*62 + 24 - 13, 2, CTL)
t(cx, 600, "WiFi 2.4 GHz (WPA2)", 12, "bold", "#333", "middle")
t(cx, 617, "TCP 1883 · usuario/contraseña", 11, "normal", "#555", "middle")

# ---------- Node-RED ----------
nx, ny, nw, nh = 1080, 140, 280, 330
box(nx, ny, nw, nh, "#fdf1e6", "#8f3b0b")
t(nx+nw/2, ny+30, "Node-RED", 17, "bold", "#8f3b0b", "middle")
t(nx+nw/2, ny+50, "+ Dashboard 2.0 · usuario: dashboard", 12, "normal", "#555", "middle")
lines = [("mqtt in ×4", "→ gauges, tendencias, textos"),
         ("function", "→ formato de estados (ES)"),
         ("ui-switch", "desacoplado: solo se mueve"),
         ("", "con la confirmación del ESP32"),
         ("mqtt out", "→ actuador/led/set"),
         ("ui-notification", "→ aviso si el ESP32 cae")]
yy = ny+84
for k, v in lines:
    if k:
        t(nx+16, yy, k, 12, "bold", "#222", font=M); yy += 17
    t(nx+28, yy, v, 12, "normal", "#333"); yy += 22

# broker <-> Node-RED
bx1, bx2 = mx+mw, nx
bc = (bx1 + bx2) / 2
arrow(bx1+4, 250, bx2-4, TEL, "tel")
t(bc, 176, "suscribe:", 11, "bold", "#444", "middle")
for i, s in enumerate(["sensor/sht41/temperatura", "sensor/sht41/humedad", "actuador/led/estado", "esp32/status"]):
    pass
t(bc, 194, "sensor/sht41/temperatura", 11, "normal", TEL, "middle", M)
t(bc, 210, "sensor/sht41/humedad", 11, "normal", TEL, "middle", M)
t(bc, 226, "actuador/led/estado", 11, "normal", CTL, "middle", M)
t(bc, 242, "esp32/status", 11, "normal", STA, "middle", M)
badge(bc, 272, 5, CTL)
arrow(bx2-4, 400, bx1+4, CTL, "ctl")
t(bc, 390, "publica:", 11, "bold", "#444", "middle")
t(bc, 422, "actuador/led/set", 11, "normal", CTL, "middle", M)
t(bc, 438, "QoS 1 · retain", 11, "normal", "#444", "middle")
badge(bc, 364, 1, CTL)

# ---------- Browser ----------
wx, wy, ww, wh = 1080, 560, 280, 190
box(wx, wy, ww, wh, "#eef7ee", "#2e7d32")
t(wx+ww/2, wy+28, "Usuario · navegador", 15, "bold", "#2e7d32", "middle")
t(wx+ww/2, wy+47, "localhost:1880/dashboard/practica-u2", 11, "normal", "#555", "middle", M)
for i, s in enumerate(["Gauges de temperatura y humedad", "Tendencias (últimos 10 min)", "Switch del LED (GPIO 2)", "Estado real del LED", "Estado del ESP32 (en línea / LWT)"]):
    t(wx+18, wy+76+i*21, "• " + s, 12)
a(f'<line x1="{nx+nw/2}" y1="{ny+nh+4}" x2="{nx+nw/2}" y2="{wy-4}" stroke="#555" stroke-width="2.5" marker-start="url(#mgry)" marker-end="url(#mgry)"/>')
t(nx+nw/2+12, (ny+nh+wy)/2-4, "HTTP + WebSocket", 12, "bold", "#333")
t(nx+nw/2+12, (ny+nh+wy)/2+13, "puerto 1880", 11, "normal", "#555")

# ---------- Control cycle ----------
cy0 = 812
t(40, cy0, "Ciclo de control con confirmación", 15, "bold", "#1a1a1a")
steps = [
 "El usuario mueve el switch → Node-RED publica \"ON\" en actuador/led/set (QoS 1, retain).",
 "Mosquitto entrega el comando al ESP32, suscrito a actuador/led/set.",
 "El ESP32 enciende GPIO 2 y actualiza la OLED (LED:ON).",
 "El ESP32 confirma publicando \"ON\" en actuador/led/estado (retain).",
 "Node-RED recibe la confirmación: el switch y «Estado del LED» reflejan el estado real.",
]
for i, s in enumerate(steps):
    col_x = 40 if i < 3 else 720
    row = i if i < 3 else i - 3
    y = cy0 + 30 + row*28
    badge(col_x+11, y-4, i+1, CTL)
    t(col_x+30, y+1, s.replace('"', "&quot;"), 12.5)
# legend
ly2 = cy0 + 30 + 2*28
for i, (c, s) in enumerate([(TEL, "Telemetría"), (CTL, "Control del LED"), (STA, "Conexión (LWT)")]):
    x = 760 + i*190
    a(f'<line x1="{x}" y1="{ly2-4}" x2="{x+30}" y2="{ly2-4}" stroke="{c}" stroke-width="3"/>')
    t(x+38, ly2+1, s, 12)
a('</svg>')
open(sys.argv[1], "w").write("\n".join(o))
