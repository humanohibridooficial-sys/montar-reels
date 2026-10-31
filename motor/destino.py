# Dónde deja montar.sh cada pieza terminada (31-10, Luismi: "la pieza original como reel y sus 2 versiones como trial").
# Una carpeta por contenido en la salida: "<n> - <tema>/" con "REEL - ...", "TRIAL A - ..." y "TRIAL B - ...".
# La pieza 41 es el reel; 41a y 41b, sus dos trials (mismo montaje, otro gancho).
#   python destino.py <salida> <n> <slug>   -> imprime la ruta completa del mp4 (y crea la carpeta)
import pathlib, re, sys

salida, n, slug = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
base = re.sub(r'[ab]$', '', n)
tipo = {'a': 'TRIAL A', 'b': 'TRIAL B'}.get(n[len(base):], 'REEL')
carpeta = next(iter(sorted(salida.glob(f'{base} - *'))), salida / f'{base} - {slug}')
carpeta.mkdir(parents=True, exist_ok=True)
print((carpeta / f'{tipo} - {slug}.mp4').as_posix())
