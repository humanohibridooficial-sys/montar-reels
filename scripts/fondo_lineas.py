# Fondo "rejilla dorada" estilo @mvcoach_: degradado radial calido, anillos, estrellas y suelo en perspectiva que avanza.
# uso: python fondo_lineas.py <salida.mp4> [segundos]
import sys, subprocess, numpy as np
import config
from PIL import Image, ImageDraw, ImageFilter

out = sys.argv[1]; DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
W, H, FPS = 1080, 1920, 30
ORO = (224, 184, 60)
HOR = 1080            # linea del horizonte
VX = W // 2           # punto de fuga
rng = np.random.default_rng(7)

# capa fija: degradado + anillos
yy, xx = np.mgrid[0:H, 0:W]
r = np.hypot((xx - VX) / W, (yy - 760) / H * 0.9)
base = np.clip(1 - r * 1.55, 0, 1) ** 1.8
fondo = np.zeros((H, W, 3), np.float32)
for i, c in enumerate((70, 48, 14)): fondo[..., i] = base * c
anillos = (np.sin(r * 95) > 0.985) * np.clip(1 - r * 1.3, 0, 1) * 10
fondo += anillos[..., None] * np.array([1.0, 0.8, 0.35])
fondo = np.clip(fondo, 0, 255)

estrellas = [(int(rng.uniform(0, W)), int(rng.uniform(150, HOR - 40)), rng.uniform(0, 6.28), rng.uniform(1.0, 2.6)) for _ in range(70)]

def suelo(fase):
    capa = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(capa)
    # lineas que fugan al centro
    for k in range(-14, 15):
        xb = VX + k * 150
        d.line([(VX + k * 9, HOR), (VX + (xb - VX) * 3.2, H)], fill=ORO, width=2)
    # lineas horizontales que se acercan (profundidad 1/z)
    for n in range(40):
        z = (n + 1 - fase) * 0.35
        if z <= 0.05: continue
        y = HOR + 260 / z
        if y > H: continue
        a = min(1.0, 0.15 + (y - HOR) / 700)
        d.line([(0, y), (W, y)], fill=tuple(int(c * a) for c in ORO), width=2)
    d.line([(0, HOR), (W, HOR)], fill=ORO, width=3)
    glow = capa.filter(ImageFilter.GaussianBlur(6))
    s = np.asarray(capa, np.float32) * 0.55 + np.asarray(glow, np.float32) * 1.6
    # se desvanece hacia el horizonte y hacia los bordes
    m = np.clip((yy - HOR) / 520, 0, 1) ** 0.8 * np.clip(1 - np.abs(xx - VX) / (W * 0.75), 0, 1)
    m[HOR - 3:HOR + 4] = np.maximum(m[HOR - 3:HOR + 4], 0.35)
    return s * m[..., None]

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       *config.codec_video("alta"), "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
N = int(DUR * FPS)
for f in range(N):
    fase = (f / N) * 1.0          # una celda por bucle: el final enlaza con el principio
    img = fondo + suelo(fase)
    fr = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(fr)
    for x, y, ph, sz in estrellas:
        a = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(ph + f / FPS * 2.2))
        c = tuple(int(v * a) for v in (255, 236, 190)); d.ellipse([x - sz, y - sz, x + sz, y + sz], fill=c)
    if f == 0: fr.save(out.replace(".mp4", ".png"))
    ff.stdin.write(fr.tobytes())
ff.stdin.close(); ff.wait(); print("ok", out)
