# Prepara los recursos del reel "Cómo se trabaja en FF360" (estilo pared azul):
#  - assets/img/pared.jpg   textura de yeso azul (a media resolución; el CSS la escala)
#  - assets/img/<n>.png      fotos y grabados "impresos en blanco" sobre transparente
# Fuentes de las imágenes: Wikimedia Commons, CC0 / dominio público (ver CREDITOS.txt).
# Uso: python prep_assets.py <carpeta-de-imagenes-originales>
import sys
import numpy as np
from PIL import Image, ImageOps

ORIG = sys.argv[1]
OUT = 'assets/img/'
np.random.seed(7)

# Pared: mundo de 3500 x 9300 px; la textura va a la mitad y el navegador la escala.
w2, h2 = 1750, 4650
ruido = np.zeros((h2, w2), np.float32)
for esc, peso in [(2, 0.12), (8, 0.2), (32, 0.35), (128, 0.5), (400, 0.45)]:
    n = np.random.rand(h2 // esc + 2, w2 // esc + 2).astype(np.float32)
    n = np.array(Image.fromarray((n * 255).astype(np.uint8)).resize((w2, h2), Image.BICUBIC), np.float32) / 255
    ruido += (n - 0.5) * peso
gy, gx = np.gradient(ruido)
v = ruido * 34 + (-gx - gy) * 70
pared = np.stack([29 + v, 62 + v, 122 + v], -1)
Image.fromarray(np.clip(pared, 0, 255).astype(np.uint8)).save(OUT + 'pared.jpg', quality=90)

def impreso(src, dst, ancho, dibujo=False, alto=None, recorte=None):
    """Lo claro de una foto (o la línea de un dibujo) se vuelve tinta blanca; el resto, transparente."""
    im = Image.open(ORIG + src).convert('L')
    if recorte: im = im.crop(recorte)
    im = ImageOps.autocontrast(im, cutoff=2)
    if alto: im = ImageOps.fit(im, (ancho, alto), Image.LANCZOS)
    else: im = im.resize((ancho, int(im.height * ancho / im.width)), Image.LANCZOS)
    a = np.array(im, np.float32) / 255
    if dibujo: a = 1 - a
    a = np.clip((a - 0.12) / 0.8, 0, 1) ** 1.1
    a = np.clip(a + (np.random.rand(*a.shape) - 0.5) * 0.16, 0, 1)  # grano de serigrafía
    out = np.zeros((*a.shape, 4), np.uint8)
    out[..., :3] = (236, 242, 255); out[..., 3] = (a * 245).astype(np.uint8)
    Image.fromarray(out).save(OUT + dst + '.png', optimize=True)
    print(dst, out.shape[1], 'x', out.shape[0])

impreso('penalti.jpg', 'penalti', 1000, alto=1500)
impreso('michels.jpg', 'michels', 900, alto=640)
impreso('keeper.jpg', 'keeper', 900, alto=600)
impreso('comida.jpg', 'comida', 440, alto=330)
impreso('kopbal.jpg', 'kopbal', 440, alto=330)
impreso('masaje.jpg', 'masaje', 440, alto=330)
impreso('keeper.jpg', 'keeper-mini', 440, alto=330)
impreso('kopbal.jpg', 'kopbal-grande', 820, alto=620)
impreso('masaje.jpg', 'masaje-grande', 820, alto=620)
impreso('carrera.jpg', 'carrera', 760, alto=300, recorte=(314, 230, 968, 546))
