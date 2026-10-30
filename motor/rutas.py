# Todas las rutas del motor salen de aquí, leídas de motor/config.json (local de cada uno, no se sube).
# Si mueves carpetas, cambia config.json y nada más. Ejemplo en config.ejemplo.json.
import json, os, pathlib

MOTOR = pathlib.Path(__file__).parent
_c = json.load(open(MOTOR / 'config.json', encoding='utf-8'))
_r = lambda k: pathlib.Path(os.path.expandvars(os.path.expanduser(_c[k])))

CONTENIDO = _r('carpeta_contenido')      # raíz del material: las rutas de b-roll y tomas de las fichas son relativas a ella
TOMAS = _r('carpeta_tomas')              # donde están las tomas DJI en bruto
REUTILIZABLES = _r('carpeta_reutilizables')  # MUSICA/ y SFX-*.wav
DATOS = _r('carpeta_datos')              # fichas/, palabras.json y voz/ (fuera del repo: llevan lo que dices)
FICHAS = DATOS / 'fichas'
PALABRAS = DATOS / 'palabras.json'
VOZ = DATOS / 'voz'
PERFIL = DATOS / 'perfil'                # perfil.json y foto.jpg de la tarjeta de "Seguir" (fuera del repo, que es público)
RENDER = _r('carpeta_render')            # p<n>/ de cada pieza; disco local, 13-17 GB por pieza mientras renderiza
SALIDA = _r('carpeta_salida')            # donde se deja el vídeo terminado
PLANTILLA = MOTOR / 'plantilla'
OM = _r('om')                            # bin/om de la skill huashu-motion
# Los recursos con tu silueta (palabra detrás de ti, tú delante del clip) usan los scripts del repo y MediaPipe, que va en
# su propio entorno: uv venv .venv && uv pip install --python .venv/Scripts/python.exe -r requirements.txt
SCRIPTS = _r('scripts') if 'scripts' in _c else MOTOR.parent / 'scripts'
PY_SILUETA = _r('python_silueta') if 'python_silueta' in _c else MOTOR.parent / '.venv/Scripts/python.exe'
