# -*- coding: utf-8 -*-
# Biblioteca de rotulos PNG 1080x1920 (colores y fuentes de config.json). Zona util de anuncio: y 288-1267, x <= 930.
#   python rotulos_lib.py <carpeta_salida> '<json: [[nombre, tipo, {args}], ...]>'
import os, sys, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import config
SK = config.FUENTES
ANTON = os.path.join(SK, "Anton-Regular.ttf"); BEBAS = os.path.join(SK, "BebasNeue-Regular.ttf")
W, H = 1080, 1920
AZUL = (30, 58, 95, 242); AZUL_OP = (30, 58, 95); ORO = tuple(int(config.COLOR_CLAVE[i:i + 2], 16) for i in (1, 3, 5)); ROJO = (239, 68, 68); VERDE = (0, 166, 81); BLANCO = (255, 255, 255)
Y0 = 900; CENTRO_X, ANCHO_MAX = 490, 760
f = lambda t, p=ANTON: ImageFont.truetype(p, t)
def medir(d, txt, fo):
    x0, y0, x1, y1 = d.textbbox((0, 0), txt, font=fo); return x1 - x0, y1 - y0, x0, y0

def palabras(texto, destacado=None, tam=104, y=Y0 + 10, ancho_max=760):
    """Solo palabras. Todas las partes sobre la MISMA linea de base (las tildes no las descuadran)
    y siempre al mismo tamano: si no cabe en una linea, pasa a dos (no se encoge)."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    partes = texto.split("|"); fo = f(tam); sep = 24
    asc, desc = fo.getmetrics()
    ancho = lambda t: d.textlength(t, font=fo)
    total = sum(ancho(t) for t in partes) + sep * (len(partes) - 1)
    lineas = [partes] if total <= ancho_max or len(partes) == 1 else [[t] for t in partes]
    base = y + asc
    for linea in lineas:
        tw = sum(ancho(t) for t in linea) + sep * (len(linea) - 1); x = CENTRO_X - tw / 2
        for t in linea:
            c = ORO if destacado and t == destacado else BLANCO
            d.text((x + 7, base + 8), t, font=fo, fill=(0, 0, 0, 210), anchor="ls")
            d.text((x, base), t, font=fo, fill=c, stroke_width=3, stroke_fill=(0, 0, 0, 255), anchor="ls")
            x += ancho(t) + sep
        base += int(asc * 1.02)
    return capa

def dato(numero, etiqueta, fuente_txt=None):
    """Cifra enorme en dorado con su etiqueta debajo y, si hay, la fuente en pequeño."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    fn = f(260); nw, nh, nox, noy = medir(d, numero, fn); x = (W - nw) // 2; y = 700
    d.text((x - nox + 9, y - noy + 11), numero, font=fn, fill=(0, 0, 0, 200))
    d.text((x - nox, y - noy), numero, font=fn, fill=ORO, stroke_width=4, stroke_fill=(0, 0, 0))
    fe = f(64, BEBAS); ew, eh, eox, eoy = medir(d, etiqueta, fe); ye = y + nh + 30
    d.rounded_rectangle([(W - ew) // 2 - 28, ye - 14, (W + ew) // 2 + 28, ye + eh + 20], 14, fill=AZUL)
    d.text(((W - ew) // 2 - eox, ye - eoy), etiqueta, font=fe, fill=BLANCO)
    if fuente_txt:
        fs = f(30, BEBAS); sw, sh, sox, soy = medir(d, fuente_txt, fs)
        d.text(((W - sw) // 2 - sox, ye + eh + 44 - soy), fuente_txt, font=fs, fill=(230, 230, 230, 230))
    return capa

def cartel_cambio(sale, entra, cx=None, escala=1.0):
    """Panel LED del cuarto arbitro: numero rojo que sale y verde que entra."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pw, ph = 400, 500; panel = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(panel)
    d.rounded_rectangle([0, 0, pw - 1, ph - 1], 28, fill=(18, 18, 22, 245), outline=(70, 70, 80), width=6)
    for i, (num, col, flecha) in enumerate([(sale, (255, 45, 45), "▼"), (entra, (40, 230, 90), "▲")]):
        y0 = 34 + i * 228; fo = f(180, BEBAS); nw, nh, nox, noy = medir(d, num, fo)
        # brillo LED
        g = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); ImageDraw.Draw(g).text(((pw - nw) // 2 - nox + 30, y0 - noy), num, font=fo, fill=col + (255,))
        panel.alpha_composite(g.filter(ImageFilter.GaussianBlur(10))); panel.alpha_composite(g)
        fa = f(70); d.text((40, y0 + 55), flecha, font=ImageFont.truetype(r"C:\Windows\Fonts\seguisym.ttf", 70), fill=col)
    panel = panel.rotate(-4, resample=Image.BICUBIC, expand=True)
    if escala != 1.0: panel = panel.resize((int(panel.width * escala), int(panel.height * escala)), Image.LANCZOS)
    s = Image.new("RGBA", (W, H), (0, 0, 0, 0)); x, y = (cx or CENTRO_X) - panel.width // 2, 610
    sh = Image.new("RGBA", panel.size, (0, 0, 0, 0)); sh.putalpha(panel.getchannel("A").point(lambda v: int(v * 0.6)))
    s.alpha_composite(sh, (x + 14, y + 20)); s = s.filter(ImageFilter.GaussianBlur(14)); s.alpha_composite(panel, (x, y))
    return s

def jornada(encendido=None, tachado=None, titulo=None):
    """Tira JUE VIE SAB DOM. encendido = dia en dorado; tachado = dia con aspa roja."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    dias = ["JUE", "VIE", "SÁB", "DOM"]; cw, ch, sep = 180, 130, 14; total = 4 * cw + 3 * sep; x0 = CENTRO_X - total // 2; y = Y0 + 20
    if titulo:
        ft = f(64); tw, th, tox, toy = medir(d, titulo, ft)
        d.text((CENTRO_X - tw // 2 - tox + 5, y - th - 30 - toy + 6), titulo, font=ft, fill=(0, 0, 0, 200))
        d.text((CENTRO_X - tw // 2 - tox, y - th - 30 - toy), titulo, font=ft, fill=BLANCO)
    fd = f(56)
    for i, dia in enumerate(dias):
        cx = x0 + i * (cw + sep); on = dia == encendido
        d.rectangle([cx, y, cx + cw, y + ch], fill=ORO if on else AZUL)
        if dia == "DOM": d.rectangle([cx, y + ch - 9, cx + cw, y + ch], fill=ORO)
        dw, dh, dox, doy = medir(d, dia, fd)
        d.text((cx + (cw - dw) // 2 - dox, y + (ch - dh) // 2 - doy), dia, font=fd, fill=AZUL_OP if on else BLANCO)
        if dia == tachado:
            d.line([cx + 18, y + 14, cx + cw - 18, y + ch - 14], fill=ROJO, width=14); d.line([cx + cw - 18, y + 14, cx + 18, y + ch - 14], fill=ROJO, width=14)
    return capa

_FINA = r"C:\Windows\Fonts\segoeuil.ttf"; _SEGOE = r"C:\Windows\Fonts\segoeui.ttf"; _SEGOE_B = r"C:\Windows\Fonts\segoeuib.ttf"
_existe = lambda p, otra: p if os.path.exists(p) else otra

def tres_pesos(lineas, y=330, alinear="centro"):
    """Gancho de texto arriba con TRES pesos (referencia @carlabalasc): cada línea es [texto, peso] con
    peso "negrita" (pequeña), "fina" (grande y ligera) o "clave" (grande, en el color de la marca).
    Ej.: [["¿Que yo", "negrita"], ["voy a comer", "fina"], ["PASTA", "clave"]]."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    fuentes = {"negrita": f(64), "fina": f(118, _existe(_FINA, BEBAS)), "clave": f(150)}
    for texto, peso in lineas:
        fo = fuentes[peso]; tw, th, ox, oy = medir(d, texto, fo)
        x = 110 if alinear == "izq" else CENTRO_X - tw // 2
        d.text((x - ox + 5, y - oy + 7), texto, font=fo, fill=(0, 0, 0, 170))
        d.text((x - ox, y - oy), texto, font=fo, fill=ORO if peso == "clave" else BLANCO,
               stroke_width=2 if peso != "fina" else 0, stroke_fill=(0, 0, 0))
        y += th + (18 if peso == "negrita" else 26)
    return capa

def tuit(nombre, usuario, texto, y=360):
    """Tarjeta de tuit falsa en blanco para citar "la otra voz" (referencia @carlabalasc). Nunca con el
    nombre ni la foto de una persona real: usuario genérico ("@entrenador_random")."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    fn, fu, ft = f(40, _existe(_SEGOE_B, BEBAS)), f(34, _existe(_SEGOE, BEBAS)), f(44, _existe(_SEGOE, BEBAS))
    ancho = ANCHO_MAX; lineas, actual = [], ""
    for p in texto.split():
        prueba = (actual + " " + p).strip()
        if d.textlength(prueba, font=ft) > ancho - 80: lineas.append(actual); actual = p
        else: actual = prueba
    lineas.append(actual)
    alto = 150 + len(lineas) * 58 + 30; x0 = CENTRO_X - ancho // 2
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sombra).rounded_rectangle([x0 + 10, y + 16, x0 + ancho + 10, y + alto + 16], 34, fill=(0, 0, 0, 120))
    capa.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(16)))
    d.rounded_rectangle([x0, y, x0 + ancho, y + alto], 34, fill=(255, 255, 255, 250))
    d.ellipse([x0 + 36, y + 36, x0 + 120, y + 120], fill=(205, 210, 218))
    d.text((x0 + 140, y + 40), nombre, font=fn, fill=(15, 20, 25))
    d.text((x0 + 140, y + 86), usuario, font=fu, fill=(110, 118, 125))
    for i, l in enumerate(lineas): d.text((x0 + 40, y + 150 + i * 58), l, font=ft, fill=(15, 20, 25))
    return capa

def encajar(img):
    """Ajusta a la zona util: ancho max 760, centrado en x=490 (columna de botones a la derecha)."""
    bb = img.getbbox(); p = img.crop(bb); w, h = p.size
    if w > ANCHO_MAX: k = ANCHO_MAX / w; p = p.resize((int(w * k), int(h * k)), Image.LANCZOS); w, h = p.size
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); out.paste(p, (CENTRO_X - w // 2, bb[1]), p); return out, (CENTRO_X - w // 2, bb[1], CENTRO_X + w // 2, bb[1] + h)

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    TIPOS = {"palabras": palabras, "dato": dato, "cartel": cartel_cambio, "jornada": jornada, "tres_pesos": tres_pesos, "tuit": tuit}
    for nombre, tipo, args in json.loads(sys.argv[2]):
        img0 = TIPOS[tipo](**args)
        img, bb = (img0, img0.getbbox()) if (args.get("cx") or tipo == "palabras") else encajar(img0)
        img.save(os.path.join(out, nombre + ".png"))
        print(f"{nombre}: x {bb[0]}-{bb[2]}, y {bb[1]}-{bb[3]}" + ("  FUERA DE ZONA" if bb[3] > 1267 or bb[1] < 288 else ""))
