import sys
W, H = 1280, 1020
F = "DejaVu Sans, Arial, sans-serif"
M = "DejaVu Sans Mono, Consolas, monospace"
C = {"3v3": "#d62728", "gnd": "#222222", "sda": "#1c71d8", "scl": "#e5a50a", "gpio2": "#26a269"}
o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{F}">')
a(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
a(f'<text x="40" y="44" font-size="24" font-weight="bold" fill="#1a1a1a">Diagrama de conexiones — ESP32 + SHT41 + OLED + LED</text>')
a(f'<text x="40" y="70" font-size="14" fill="#555">Práctica U2 · Comunicación bidireccional · Bus I²C compartido (GPIO 21/22) y LED de salida en GPIO 2</text>')

# ---- ESP32 board ----
bx, by, bw, bh = 100, 90, 280, 600
a(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="12" fill="#1f3a5f" stroke="#0f2238" stroke-width="2"/>')
# antenna trace
a(f'<path d="M190 104 h20 v14 h20 v-14 h20 v14 h20 v-14 h20" fill="none" stroke="#c9a227" stroke-width="3"/>')
# metal can
a(f'<rect x="185" y="132" width="110" height="250" rx="4" fill="#c0c4c8" stroke="#8a8f94"/>')
a(f'<text x="240" y="250" font-size="10.5" text-anchor="middle" fill="#333" font-weight="bold">ESP-WROOM-32</text>')
a(f'<text x="240" y="430" font-size="15" text-anchor="middle" fill="#fff" font-weight="bold">ESP32 DevKit V1</text>')
a(f'<text x="240" y="450" font-size="12" text-anchor="middle" fill="#cfd8e3">(30 pines)</text>')
# onboard LED
a(f'<circle cx="240" cy="560" r="7" fill="#3584e4" stroke="#fff" stroke-width="1"/>')
a(f'<text x="240" y="584" font-size="10" text-anchor="middle" fill="#cfd8e3">LED azul integrado</text>')
a(f'<text x="240" y="597" font-size="10" text-anchor="middle" fill="#cfd8e3">(también GPIO 2)</text>')
# USB
a(f'<rect x="210" y="{by+bh-4}" width="60" height="22" rx="3" fill="#9aa0a6" stroke="#5f6368"/>')
a(f'<text x="240" y="{by+bh+36}" font-size="11" text-anchor="middle" fill="#555">USB (alimentación + datos)</text>')

left = ["EN","VP","VN","D34","D35","D32","D33","D25","D26","D27","D14","D12","D13","GND","VIN"]
right = ["D23","D22","TX0","RX0","D21","D19","D18","D5","TX2","RX2","D4","D2","D15","GND","3V3"]
used = {"D22": "scl", "D21": "sda", "D2": "gpio2", "GND": "gnd", "3V3": "3v3"}
pin_y = {}
for i, (l, r) in enumerate(zip(left, right)):
    y = 160 + i * 34
    a(f'<circle cx="114" cy="{y}" r="5" fill="#d4af37" stroke="#7a6418"/>')
    a(f'<text x="126" y="{y+4}" font-size="12" fill="#cfd8e3">{l}</text>')
    is_used = r in used and not (r == "GND" and i != 13)
    col = C[used[r]] if is_used else "#d4af37"
    a(f'<circle cx="366" cy="{y}" r="{7 if is_used else 5}" fill="{col}" stroke="#fff" stroke-width="{1.5 if is_used else 0}"/>')
    a(f'<text x="354" y="{y+4}" font-size="12" text-anchor="end" fill="{"#ffffff" if is_used else "#cfd8e3"}" font-weight="{"bold" if is_used else "normal"}">{r}</text>')
    pin_y[r] = y
gp = {"D22": "GPIO 22", "D21": "GPIO 21", "D2": "GPIO 2"}

# ---- buses ----
X = {"3v3": 440, "gnd": 470, "sda": 500, "scl": 530}
SPAN = {"3v3": (120, 636), "gnd": (150, 720), "sda": (210, 400), "scl": (180, 370)}
def crosses(y, x0, x1, exclude):
    xs = []
    for k, x in X.items():
        if k == exclude: continue
        lo, hi = SPAN[k]
        if min(x0, x1) < x < max(x0, x1) and lo < y < hi:
            xs.append(x)
    return sorted(xs)
def hwire(y, x0, x1, col, kind):
    # horizontal wire left->right with hop arcs at crossings
    hops = crosses(y, x0, x1, kind)
    d = f"M{x0} {y}"
    for hx in hops:
        d += f" H{hx-7} a7 7 0 0 1 14 0"
    d += f" H{x1}"
    a(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="3.5" stroke-linecap="round"/>')
def dot(x, y, col):
    a(f'<circle cx="{x}" cy="{y}" r="5.5" fill="{col}"/>')

for k, x in X.items():
    lo, hi = SPAN[k]
    a(f'<line x1="{x}" y1="{lo}" x2="{x}" y2="{hi}" stroke="{C[k]}" stroke-width="3.5" stroke-linecap="round"/>')

# board -> buses
hwire(pin_y["D22"], 366, X["scl"], C["scl"], "scl"); dot(X["scl"], pin_y["D22"], C["scl"])
hwire(pin_y["D21"], 366, X["sda"], C["sda"], "sda"); dot(X["sda"], pin_y["D21"], C["sda"])
hwire(602, 366, X["gnd"], C["gnd"], "gnd"); dot(X["gnd"], 602, C["gnd"])
hwire(636, 366, X["3v3"], C["3v3"], "3v3"); dot(X["3v3"], 636, C["3v3"])

# ---- SHT41 module ----
sx, sy = 700, 90
a(f'<rect x="{sx}" y="{sy}" width="210" height="150" rx="8" fill="#7b2fbe" stroke="#4b1a75" stroke-width="2"/>')
a(f'<rect x="{sx+130}" y="{sy+55}" width="34" height="34" rx="3" fill="#d9d9d9" stroke="#888"/>')
a(f'<text x="{sx+147}" y="{sy+108}" font-size="10" text-anchor="middle" fill="#efe6f7">SHT41</text>')
a(f'<text x="{sx+140}" y="{sy+30}" font-size="15" font-weight="bold" text-anchor="middle" fill="#fff">GY-SHT41</text>')
a(f'<text x="{sx+105}" y="{sy+140}" font-size="12" text-anchor="middle" fill="#efe6f7">Temp./humedad · I²C 0x44</text>')
for name, y, k in [("VIN",120,"3v3"),("GND",150,"gnd"),("SCL",180,"scl"),("SDA",210,"sda")]:
    hwire(y, X[k], sx, C[k], k); dot(X[k], y, C[k])
    a(f'<circle cx="{sx}" cy="{y}" r="5" fill="#d4af37" stroke="#7a6418"/>')
    a(f'<text x="{sx+12}" y="{y+4}" font-size="12" fill="#fff" font-weight="bold">{name}</text>')

# ---- OLED module ----
ox, oy = 700, 280
a(f'<rect x="{ox}" y="{oy}" width="300" height="150" rx="8" fill="#0b3d91" stroke="#06265c" stroke-width="2"/>')
a(f'<rect x="{ox+70}" y="{oy+28}" width="210" height="70" rx="3" fill="#000" stroke="#444"/>')
a(f'<text x="{ox+78}" y="{oy+46}" font-size="12" fill="#9fe7ff" font-family="{M}">Temperatura</text>')
a(f'<text x="{ox+272}" y="{oy+46}" font-size="12" fill="#9fe7ff" font-family="{M}" text-anchor="end">LED:ON</text>')
a(f'<text x="{ox+78}" y="{oy+84}" font-size="26" fill="#9fe7ff" font-family="{M}">24.6 C</text>')
a(f'<text x="{ox+175}" y="{oy+124}" font-size="13" font-weight="bold" text-anchor="middle" fill="#fff">OLED SSD1306 128×32</text>')
a(f'<text x="{ox+175}" y="{oy+141}" font-size="12" text-anchor="middle" fill="#cfe0ff">I²C 0x3C</text>')
for name, y, k in [("GND",310,"gnd"),("VCC",340,"3v3"),("SCL",370,"scl"),("SDA",400,"sda")]:
    hwire(y, X[k], ox, C[k], k); dot(X[k], y, C[k])
    a(f'<circle cx="{ox}" cy="{y}" r="5" fill="#d4af37" stroke="#7a6418"/>')
    a(f'<text x="{ox+12}" y="{y+4}" font-size="12" fill="#fff" font-weight="bold">{name}</text>')

# ---- LED circuit on GPIO 2 ----
ly = pin_y["D2"]
hwire(ly, 366, 610, C["gpio2"], "gpio2")
# resistor zigzag 610..690
zz = f"M610 {ly}"
for i in range(8):
    zz += f" L{615+i*10} {ly + (-9 if i%2==0 else 9)}"
zz += f" L690 {ly}"
a(f'<path d="{zz}" fill="none" stroke="#5e3c1a" stroke-width="3" stroke-linejoin="round"/>')
a(f'<text x="650" y="{ly-20}" font-size="13" font-weight="bold" text-anchor="middle" fill="#333">R1 220 Ω</text>')
a(f'<line x1="690" y1="{ly}" x2="770" y2="{ly}" stroke="{C["gpio2"]}" stroke-width="3.5"/>')
# LED symbol
a(f'<polygon points="770,{ly-20} 770,{ly+20} 808,{ly}" fill="#e01b24" stroke="#7a0b10" stroke-width="2"/>')
a(f'<line x1="808" y1="{ly-20}" x2="808" y2="{ly+20}" stroke="#7a0b10" stroke-width="3"/>')
for dx in (0, 14):
    a(f'<path d="M{786+dx} {ly-26} l12 -14 m0 0 l-7 1 m7 -1 l-1 7" fill="none" stroke="#e01b24" stroke-width="2"/>')
a(f'<text x="789" y="{ly-48}" font-size="13" font-weight="bold" text-anchor="middle" fill="#333">LED1 (rojo, 5 mm)</text>')
a(f'<text x="768" y="{ly+40}" font-size="11" text-anchor="end" fill="#555">Ánodo (+)</text>')
a(f'<text x="768" y="{ly+54}" font-size="11" text-anchor="end" fill="#555">pata larga</text>')
a(f'<text x="814" y="{ly+40}" font-size="11" fill="#555">Cátodo (−)</text>')
a(f'<text x="814" y="{ly+54}" font-size="11" fill="#555">pata corta</text>')
a(f'<path d="M808 {ly} H900 V720 H{X["gnd"]}" fill="none" stroke="{C["gnd"]}" stroke-width="3.5" stroke-linejoin="round"/>')
dot(X["gnd"], 720, C["gnd"])
a(f'<text x="905" y="{ly+90}" font-size="11" fill="#555">al bus GND</text>')

# ---- legend note ----
a(f'<text x="40" y="770" font-size="12" fill="#555">● = unión eléctrica · ⌒ = cruce sin conexión · Todos los módulos operan a 3.3 V. No se requieren pull-ups externas: los módulos SHT41 y OLED las traen integradas.</text>')

# ---- pin table ----
rows = [
 ("3v3", "Alimentación 3.3 V", "3V3", "VIN del SHT41 · VCC de la OLED"),
 ("gnd", "Tierra", "GND", "GND del SHT41 · GND de la OLED · cátodo del LED"),
 ("sda", "Datos I²C (SDA)", "GPIO 21 (D21)", "SDA del SHT41 · SDA de la OLED"),
 ("scl", "Reloj I²C (SCL)", "GPIO 22 (D22)", "SCL del SHT41 · SCL de la OLED"),
 ("gpio2", "Salida digital LED", "GPIO 2 (D2)", "R1 220 Ω → ánodo del LED (actuador/led/set)"),
]
tx, ty, rh = 40, 795, 34
cols = [tx, tx+60, tx+290, tx+480]
a(f'<rect x="{tx}" y="{ty}" width="1200" height="{rh}" fill="#2c3e50"/>')
for x, t in zip(cols, ["Cable", "Señal", "Pin ESP32", "Destino"]):
    a(f'<text x="{x+12}" y="{ty+22}" font-size="13" font-weight="bold" fill="#fff">{t}</text>')
for i, (k, s, p, d) in enumerate(rows):
    y = ty + rh*(i+1)
    a(f'<rect x="{tx}" y="{y}" width="1200" height="{rh}" fill="{"#f4f6f8" if i%2==0 else "#ffffff"}" stroke="#e0e0e0"/>')
    a(f'<line x1="{tx+14}" y1="{y+17}" x2="{tx+48}" y2="{y+17}" stroke="{C[k]}" stroke-width="5" stroke-linecap="round"/>')
    a(f'<text x="{cols[1]+12}" y="{y+22}" font-size="13" fill="#222">{s}</text>')
    a(f'<text x="{cols[2]+12}" y="{y+22}" font-size="13" fill="#222" font-weight="bold">{p}</text>')
    a(f'<text x="{cols[3]+12}" y="{y+22}" font-size="13" fill="#222">{d}</text>')
a('</svg>')
open(sys.argv[1], "w").write("\n".join(o))
