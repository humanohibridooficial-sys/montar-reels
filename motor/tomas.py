# Tomas del lote de trial reels (28-10): número de pieza -> fichero en "Ads y contenido".
# Las DJI llevan el número de la cámara; las del móvil del 15-09, m1..m7.
from rutas import CONTENIDO, TOMAS as CARPETA_TOMAS

BR = CONTENIDO
_DJI = {p.name.split('_')[3]: p.name for p in CARPETA_TOMAS.glob('DJI_*_null_video.mp4')}
_MOVIL = {'m1': '151714', 'm2': '152229', 'm3': '152535', 'm4': '152732', 'm5': '152857', 'm6': '153008', 'm7': '153119'}
NUEVAS = ['27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43',
          '47', '48', '49', '50', '56', '57', '59', '60', '61', '62', '63', '64', '65'] + list(_MOVIL)
TOMAS = NUEVAS


def video(n):
    """Lo que va en la ficha: ruta relativa a 'Ads y contenido'."""
    return f'VID_20260915_{_MOVIL[n]}.mp4' if n in _MOVIL else f'Nuevos 27/{_DJI[n]}'


def ruta(n):
    return BR / video(n)
