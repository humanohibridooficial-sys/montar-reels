# Pieza de tres tarjetas estilo @mvcoach_ sobre el fondo de rejilla dorada.
# Laterales inclinadas en 3D, inactivas en blanco y negro, la activa en color con brillo dorado.
# uso: python tarjetas_v2.py <salida.mp4> "COMIDA|DESCANSO|FUERZA" <clip1> <clip2> <clip3> <fondo.mp4> [dur] [act1,act2,act3]
#   act = segundo en que se enciende cada tarjeta (por defecto 0.35,1.45,2.55)
import sys, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

out, etiquetas, c1, c2, c3, fondo = sys.argv[1:7]
DUR = float(sys.argv[7]) if len(sys.argv) > 7 else 4.5
ACT = [float(x) for x in sys.argv[8].split(",")] if len(sys.argv) > 8 else [0.35, 1.45, 2.55]
W, H, FPS = 1080, 1920, 30
ORO = (224, 184, 60)
import os, config
FONT = os.path.join(config.FUENTES, "BebasNeue-Regular.ttf")
labels = etiquetas.split("|")

def lector(p):
    cap = cv2.VideoCapture(p); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, n // 2 - int(DUR * 15)))
    return cap
caps = [lector(c) for c in (c1, c2, c3)]
fcap = cv2.VideoCapture(fondo)

def coeffs(dst, src):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()

def redondear(im, r=26):
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], r, fill=255)
    im = im.convert("RGBA"); im.putalpha(m); return im

def inclinar(im, lado):  # lado -1 = izquierda (borde exterior mas corto), +1 = derecha
    w, h = im.size; k = int(h * 0.14)
    if lado < 0: dst = [(0, k), (w, 0), (w, h), (0, h - k)]
    else:        dst = [(0, 0), (w, k), (w, h - k), (0, h)]
    return im.transform((w, h), Image.PERSPECTIVE, coeffs(dst, [(0, 0), (w, 0), (w, h), (0, h)]), Image.BICUBIC)

# geometria
CARDS = [dict(w=255, h=440, cx=190, cy=680, lado=-1), dict(w=320, h=545, cx=540, cy=660, lado=0), dict(w=255, h=440, cx=890, cy=680, lado=1)]
f_lab = lambda s: ImageFont.truetype(FONT, s)

def texto_espaciado(d, cx, y, txt, font, fill, sp=6):
    ws = [d.textbbox((0, 0), ch, font=font)[2] for ch in txt]; total = sum(ws) + sp * (len(txt) - 1); x = cx - total / 2
    for ch, w in zip(txt, ws): d.text((x, y), ch, font=font, fill=fill); x += w + sp

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       *config.codec_video("alta"), "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
N = int(DUR * FPS)
for f in range(N):
    t = f / FPS
    ok, fb = fcap.read()
    if not ok: fcap.set(cv2.CAP_PROP_POS_FRAMES, 0); ok, fb = fcap.read()
    lienzo = Image.fromarray(cv2.cvtColor(fb, cv2.COLOR_BGR2RGB)).convert("RGBA")
    activa = max([i for i, a in enumerate(ACT) if t >= a], default=-1)
    capa_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for i, (C, cap) in enumerate(zip(CARDS, caps)):
        ok, fr = cap.read()
        if not ok: cap.set(cv2.CAP_PROP_POS_FRAMES, 0); ok, fr = cap.read()
        img = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
        # entrada escalonada: sube 90 px y aparece
        t0 = 0.08 * i; p = min(1.0, max(0.0, (t - t0) / 0.35)); p = 1 - (1 - p) ** 3
        if p <= 0: continue
        on = (i == activa)
        esc = 1.06 if on else 1.0
        w, h = int(C["w"] * esc), int(C["h"] * esc)
        sw, sh = img.size; r = max(w / sw, h / sh)
        img = img.resize((int(sw * r) + 1, int(sh * r) + 1), Image.LANCZOS)
        img = img.crop(((img.width - w) // 2, (img.height - h) // 2, (img.width - w) // 2 + w, (img.height - h) // 2 + h))
        if not on:
            img = ImageEnhance.Brightness(img.convert("L").convert("RGB")).enhance(0.72)
        card = redondear(img)
        if C["lado"]: card = inclinar(card, C["lado"])
        alpha = int(255 * p); card.putalpha(card.getchannel("A").point(lambda v: v * p))
        x, y = C["cx"] - w // 2, int(C["cy"] - h // 2 + 90 * (1 - p))
        if on:  # borde dorado que sigue la forma (inclinada) de la tarjeta
            a = card.getchannel("A")
            borde = Image.new("L", (w + 40, h + 40), 0); borde.paste(a, (20, 20))
            ancho = borde.filter(ImageFilter.MaxFilter(9))
            aro = Image.fromarray(np.clip(np.asarray(ancho, int) - np.asarray(borde, int), 0, 255).astype(np.uint8))
            oro = Image.new("RGBA", aro.size, ORO + (0,)); oro.putalpha(aro)
            halo = Image.new("RGBA", aro.size, ORO + (0,)); halo.putalpha(ancho.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.8)))
            capa_glow.alpha_composite(halo, (x - 20, y - 20)); capa_glow.alpha_composite(oro, (x - 20, y - 20))
        capa.alpha_composite(card, (x, y))
        # etiqueta
        fs = 54 if on else 44
        texto_espaciado(d, C["cx"], C["cy"] + h // 2 + 26 + (0 if on else 6), labels[i], f_lab(fs),
                        ORO + (alpha,) if on else (235, 235, 235, int(alpha * 0.85)), sp=7)
    lienzo.alpha_composite(capa_glow); lienzo.alpha_composite(capa)
    if f == int(3.2 * FPS): lienzo.convert("RGB").save(out.replace(".mp4", ".png"))
    ff.stdin.write(lienzo.convert("RGB").tobytes())
ff.stdin.close(); ff.wait(); print("ok", out)
