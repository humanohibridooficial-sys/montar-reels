# Prepara una toma NUEVA para el motor: voz limpia, palabras y un borrador de ficha. Después el director-montaje
# completa la ficha y `sh motor/montar.sh <n>` monta. Las 45 tomas del lote del 28-10 ya están preparadas.
#   python preparar.py <n> <toma.mp4>        (n: nombre corto de la pieza, p. ej. 80 o m8)
# Voz: DeepFilterNet en su propio entorno (python_df; no hay paquete para Python 3.12 en Windows: va en 3.11).
# Palabras: faster-whisper sobre la toma EN BRUTO (python_fw), así las palabras van en la línea de tiempo de la toma,
# que es la que usan "keep" y "quitar" de la ficha. Formato de palabras.json igual que el del lote.
import json, os, pathlib, subprocess, sys

from rutas import CONTENIDO, TOMAS, FICHAS, PALABRAS, VOZ, PY_DF, PY_FW, MOTOR

N, TOMA = sys.argv[1], pathlib.Path(sys.argv[2]).resolve()
assert TOMA.exists(), f'no existe {TOMA}'
VOZ.mkdir(parents=True, exist_ok=True)

# 1. Voz limpia
limpio = VOZ / f'{N}-limpio.wav'
if not limpio.exists():
    subprocess.run([str(PY_DF), str(MOTOR / 'preparar_voz.py'), N, str(TOMA)], check=True, cwd=MOTOR)
print('voz', limpio.name)

# 2. Palabras (large-v3-turbo: mejor texto; la toma en bruto, misma línea de tiempo)
pal = json.load(open(PALABRAS, encoding='utf-8')) if PALABRAS.exists() else {}
clave = f'{N}-limpio.wav'
if clave not in pal:
    out = subprocess.run([str(PY_FW), str(MOTOR / 'transcribir_toma.py'), str(TOMA)], capture_output=True, text=True, encoding='utf-8',
                         env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, check=True).stdout
    pal[clave] = json.loads(out.strip().splitlines()[-1])
    json.dump(pal, open(PALABRAS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
ws = [w for s in pal[clave] for w in s['words']]
print('palabras', len(ws), '|', ' '.join(w['word'] for w in ws)[:160])

# 3. Borrador de ficha: la toma entera; el director quita lo que sobra y pone los recursos. Una ficha que ya existe no se toca.
ficha = FICHAS / f'{N}.json'
if ficha.exists():
    print('ficha', ficha.name, 'ya existe: no se toca')
else:
    try:
        video = TOMA.relative_to(TOMAS).as_posix() if TOMA.parent == TOMAS else TOMA.relative_to(CONTENIDO).as_posix()
    except ValueError:
        sys.exit(f'la toma tiene que estar dentro de {CONTENIDO}')
    sig = [w for w in ws if w['word'].lower().strip('.,!¡') in ('sígueme', 'sigueme')]
    json.dump({'titulo': '', 'video': video, 'keep': [[max(0, round(ws[0]['start'] - 0.12, 3)), round(ws[-1]['end'] + 0.25, 3)]],
               'tops': [], 'claves': [], 'follow': 'sígueme' if sig else round(ws[-1]['start'], 2), 'subsTop': 1060},
              open(ficha, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('ficha', ficha.name, 'borrador: falta titulo, tops y recursos (director-montaje)')
