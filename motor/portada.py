# Portada de un trial reel con el molde de las portadas que mejor han funcionado en IG (29-10):
# cara en primer plano, antetítulo dorado, línea 1 en blanco, línea 2 en franja amarilla con letra oscura,
# y opcional una banda azul con los pilares.
# Uso: python portada.py <n> "<linea1>" "<linea2>" [segundo] [antetitulo] [banda]
import subprocess, sys, pathlib
from PIL import Image, ImageDraw, ImageFont

from rutas import RENDER, PLANTILLA
n, l1, l2 = sys.argv[1], sys.argv[2].upper(), sys.argv[3].upper()
seg = float(sys.argv[4]) if len(sys.argv) > 4 else 4.0
kicker = (sys.argv[5] if len(sys.argv) > 5 else 'FUTBOLISTA').upper()
banda = sys.argv[6].upper() if len(sys.argv) > 6 and sys.argv[6] else ''
FUENTE = PLANTILLA / 'fonts/portada.ttf'
DORADO, AMARILLO, OSCURO, AZUL = (224, 184, 60), (240, 196, 48), (16, 24, 40), (14, 30, 66)

tmp = RENDER / f'p{n}/portada-frame.jpg'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(seg), '-i', str(RENDER / f'p{n}/assets/talk.mp4'),
                '-frames:v', '1', '-q:v', '2', str(tmp)], check=True)
im = Image.open(tmp).convert('RGB')
# primer plano: 1,35x, centrado en la cara (tercio de arriba)
z = 1.35
w, h = im.size
cw, ch = int(w / z), int(h / z)
x0, y0 = (w - cw) // 2, int(h * 0.12)
im = im.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.LANCZOS)
d = ImageDraw.Draw(im)

def texto(y, t, size, color, caja=None, pad=(26, 14)):
    f = ImageFont.truetype(str(FUENTE), size)
    while d.textlength(t, font=f) > w * 0.86:
        size -= 4; f = ImageFont.truetype(str(FUENTE), size)
    tw = d.textlength(t, font=f)
    a, b = f.getbbox(t)[1], f.getbbox(t)[3]
    x = (w - tw) / 2
    if caja:
        d.rectangle((x - pad[0], y + a - pad[1], x + tw + pad[0], y + b + pad[1]), fill=caja)
    else:
        d.text((x + 3, y + 3), t, font=f, fill=(0, 0, 0))
    d.text((x, y), t, font=f, fill=color)
    return y + b + pad[1] * 2 + 12

# bloque en la parte baja de la zona 3:4 (la cuadrícula recorta 240 px arriba y abajo), debajo de la cara
y = 1080
y = texto(y, kicker, 52, DORADO)
y = texto(y, l1, 118, (255, 255, 255))
y = texto(y + 6, l2, 118, OSCURO, caja=AMARILLO)
if banda:
    texto(y + 10, banda, 44, (255, 255, 255), caja=AZUL, pad=(22, 12))
out = sys.argv[7] if len(sys.argv) > 7 else str(RENDER / f'p{n}/out/p{n}-portada.jpg')
im.save(out, quality=92)
print(out)
