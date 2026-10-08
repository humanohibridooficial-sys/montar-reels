# -*- coding: utf-8 -*-
# Capas PNG 1080x1920 que se APILAN (cada una en su pista de CapCut y entra en su segundo):
#   etiqueta : pastilla blanca con texto azul marino y una flecha dorada dibujada que la senala (estilo "PRIMERA")
#   objeto   : objeto recortado (sin fondo) con sombra suave y, si se pide, su palabra dorada debajo
#   python capas_lib.py <carpeta_salida> '<json [[nombre, tipo, {args}], ...]>'
import os, sys, json, math
from PIL import Image, ImageDraw, ImageFilter
from rotulos_lib import f, W, H, ORO, BLANCO

MARINO = (14, 31, 58)

def etiqueta(texto, y, x=70, tam=70, flecha=True):
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    fo = f(tam); asc, desc = fo.getmetrics(); tw = d.textlength(texto, font=fo)
    pad_x, alto = 48, asc + 44; x0 = x + (70 if flecha else 0)
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle([x0 + 8, y + 10, x0 + tw + 2 * pad_x + 8, y + alto + 10], 22, fill=(0, 0, 0, 150))
    capa.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(6))); d = ImageDraw.Draw(capa)
    d.rounded_rectangle([x0, y, x0 + tw + 2 * pad_x, y + alto], 22, fill=BLANCO + (255,))
    d.text((x0 + pad_x, y + alto / 2 + asc * 0.38), texto, font=fo, fill=MARINO, anchor="ls")
    if flecha:  # punto dorado y flecha curva dibujada a mano hacia la pastilla
        cx, cy = x + 10, y - 26
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=ORO + (255,), outline=(0, 0, 0, 255), width=3)
        pts = [(cx + 6 + 52 * t, cy + 6 + 40 * (t ** 2)) for t in [i / 20 for i in range(21)]]
        d.line(pts, fill=BLANCO + (255,), width=7, joint="curve")
        ex, ey = pts[-1]; ang = math.atan2(pts[-1][1] - pts[-3][1], pts[-1][0] - pts[-3][0])
        for da in (2.5, -2.5):
            d.line([(ex, ey), (ex - 22 * math.cos(ang + da / 3), ey - 22 * math.sin(ang + da / 3))], fill=BLANCO + (255,), width=7)
    return capa

def objeto(png, cx, cy, ancho, palabra=None, rot=0, tam=64, palabra_y=None):
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im = Image.open(png).convert("RGBA"); r = ancho / im.width; im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    if rot: im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda a: int(a * 0.55)))
    capa.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (x + 14, y + 22)); capa.alpha_composite(im, (x, y))
    if palabra:
        d = ImageDraw.Draw(capa); fo = f(tam); asc, _ = fo.getmetrics(); by = palabra_y or (y + im.height + 18 + asc)  # palabra_y: misma linea de base para todos
        d.text((cx + 5, by + 6), palabra, font=fo, fill=(0, 0, 0, 210), anchor="ms")
        d.text((cx, by), palabra, font=fo, fill=ORO, stroke_width=3, stroke_fill=(0, 0, 0, 255), anchor="ms")
    return capa

def pastilla(d, cx, y, texto, fondo, color, tam=74):
    fo = f(tam); asc, _ = fo.getmetrics(); tw = d.textlength(texto, font=fo); alto = asc + 46; x0 = cx - tw / 2 - 50
    d.rounded_rectangle([x0 + 8, y + 10, x0 + tw + 100 + 8, y + alto + 10], 24, fill=(0, 0, 0, 140))
    d.rounded_rectangle([x0, y, x0 + tw + 100, y + alto], 26, fill=fondo + (255,))
    d.text((cx, y + alto / 2 + asc * 0.38), texto, font=fo, fill=color, anchor="ms"); return alto

def distinto(arriba, abajo, y=1000, cx=490, igual=False):
    """Dos ideas que NO son lo mismo: pastilla blanca, signo distinto dibujado en rojo, pastilla dorada."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    a = pastilla(d, cx, y, arriba, BLANCO, MARINO)
    sy = y + a + 46; R = (239, 68, 68, 255)
    for k in (0, 34): d.rounded_rectangle([cx - 60, sy + k, cx + 60, sy + k + 16], 6, fill=R, outline=(0, 0, 0, 255), width=3)
    if igual:  # mismo signo en verde, sin tachar: las dos cosas DEBEN ser iguales
        for k in (0, 34): d.rounded_rectangle([cx - 60, sy + k, cx + 60, sy + k + 16], 6, fill=(0, 166, 81, 255), outline=(0, 0, 0, 255), width=3)
    else:
        d.line([(cx + 30, sy - 14), (cx - 30, sy + 64)], fill=(0, 0, 0, 255), width=20); d.line([(cx + 30, sy - 14), (cx - 30, sy + 64)], fill=R, width=12)
    pastilla(d, cx, sy + 112, abajo, ORO, MARINO); return capa

DIAS = ["JUE", "VIE", "SÁB", "DOM"]
def calendario(encendidos=(), titulo=None, tachar_noche=False, y=1040, base=True, dias=None):
    """Tira de jornada. base=True dibuja las 4 casillas oscuras; si no, solo las encendidas (para apilar)."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    dd = dias or DIAS; n = len(dd); cw, ch, g = (160, 140, 30) if n <= 4 else (136, 136, 14); x0 = 490 - (n * cw + (n - 1) * g) / 2; fo = f(66 if n <= 4 else 58)
    for i, dia in enumerate(dd):
        x = x0 + i * (cw + g); on = dia in encendidos
        if not (base or on): continue
        d.rounded_rectangle([x + 6, y + 8, x + cw + 6, y + ch + 8], 16, fill=(0, 0, 0, 150))
        d.rounded_rectangle([x, y, x + cw, y + ch], 16, fill=(ORO if on else (30, 58, 95)) + (255,), outline=(0, 0, 0, 255), width=3)
        d.text((x + cw / 2, y + ch / 2 + 24), dia, font=fo, fill=MARINO if on else BLANCO, anchor="ms")
    if titulo:
        ft = f(58); d.text((493, y - 46 + 4), titulo, font=ft, fill=(0, 0, 0, 200), anchor="ms"); d.text((490, y - 46), titulo, font=ft, fill=BLANCO, stroke_width=3, stroke_fill=(0, 0, 0, 255), anchor="ms")
    if tachar_noche:  # solo la noche de antes (SAB) no basta: aspa roja sobre el sabado
        x = x0 + 2 * (cw + g)
        for a, b in (((x + 10, y + 10), (x + cw - 10, y + ch - 10)), ((x + cw - 10, y + 10), (x + 10, y + ch - 10))):
            d.line([a, b], fill=(0, 0, 0, 255), width=22); d.line([a, b], fill=(239, 68, 68, 255), width=14)
    return capa

def aviso(texto, y, fondo="rojo", cx=490, tam=64):
    """Una sola pastilla (roja de aviso, dorada o blanca)."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    col = {"rojo": ((239, 68, 68), BLANCO), "oro": (ORO, MARINO), "blanco": (BLANCO, MARINO)}[fondo]
    pastilla(d, cx, y, texto, col[0], col[1], tam); return capa

def libreta(titulo, filas, marcada=0, y=360, x=560, ancho=430):
    """Hoja de libreta (lista de cambios del mister) con una fila rodeada en rojo."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fl = 96; alto = 130 + fl * len(filas)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([x + 12, y + 16, x + ancho + 12, y + alto + 16], 18, fill=(0, 0, 0, 160))
    capa.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); d = ImageDraw.Draw(capa)
    d.rounded_rectangle([x, y, x + ancho, y + alto], 18, fill=(250, 248, 240, 255))
    for i in range(len(filas) + 1): d.line([(x + 24, y + 112 + i * fl), (x + ancho - 24, y + 112 + i * fl)], fill=(150, 180, 220, 255), width=3)
    d.line([(x + 70, y + 10), (x + 70, y + alto - 10)], fill=(239, 68, 68, 160), width=3)
    d.text((x + ancho / 2, y + 84), titulo, font=f(64), fill=MARINO, anchor="ms")
    for i, t in enumerate(filas):
        by = y + 112 + i * fl + 72; d.text((x + 92, by), t, font=f(60), fill=(40, 40, 40), anchor="ls")
        if i == marcada: d.ellipse([x + 60, by - 78, x + ancho - 20, by + 18], outline=(239, 68, 68, 255), width=8)
    return capa

def check(texto, y, x=60, tam=66):
    """Item de lista con tic dorado (los tics se apilan, uno por pista)."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    r = 40; cx, cy = x + r, y + r
    d.ellipse([cx - r + 5, cy - r + 7, cx + r + 5, cy + r + 7], fill=(0, 0, 0, 150))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ORO + (255,), outline=(0, 0, 0, 255), width=4)
    d.line([(cx - 20, cy + 2), (cx - 5, cy + 18), (cx + 22, cy - 16)], fill=MARINO, width=11, joint="curve")
    fo = f(tam); asc, _ = fo.getmetrics(); tx = x + 2 * r + 34; tw = d.textlength(texto, font=fo)
    d.rounded_rectangle([tx - 26 + 6, cy - asc / 2 - 20 + 8, tx + tw + 30 + 6, cy + asc / 2 + 20 + 8], 22, fill=(0, 0, 0, 140))
    d.rounded_rectangle([tx - 26, cy - asc / 2 - 20, tx + tw + 30, cy + asc / 2 + 20], 22, fill=BLANCO + (255,))
    d.text((tx, cy + asc * 0.38), texto, font=fo, fill=MARINO, anchor="ls")
    return capa

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for nombre, tipo, kw in json.loads(sys.argv[2]):
        {"etiqueta": etiqueta, "objeto": objeto, "distinto": distinto, "calendario": calendario, "aviso": aviso, "libreta": libreta, "check": check}[tipo](**kw).save(os.path.join(out, nombre + ".png")); print("ok", nombre)
