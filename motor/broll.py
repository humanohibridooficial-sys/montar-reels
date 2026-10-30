# B-roll para una frase: primero la biblioteca (los clips se llaman como la frase que acompañan), y si no hay, Pexels.
#   python broll.py biblioteca "palabra palabra"        -> clips de la biblioteca cuyo nombre lleva esas palabras
#   python broll.py pexels "query en inglés" [nombre]    -> baja hasta 4 vídeos verticales a la biblioteca y una hoja
# Lo bajado va a <carpeta_reutilizables>/b-roll-pexels/<nombre>_pexels-<id>.mp4 con su hoja .jpg (3 fotogramas) para
# MIRAR antes de usarlo: juveniles de 16-18, nunca niños pequeños, sin logos ni marcas, y que se vea lo que dices.
# Solo Pexels (licencia para anuncios). La clave PEXELS_API_KEY sale del .env del repo y no se imprime nunca.
import json, os, re, subprocess, sys, unicodedata, urllib.parse, urllib.request
from pathlib import Path

from rutas import CONTENIDO, REUTILIZABLES, MOTOR
sys.stdout.reconfigure(encoding='utf-8')   # nombres de autor como "Oğuzhan": la consola de Windows usa cp1252

DEST = REUTILIZABLES / 'b-roll-pexels'
sin_tildes = lambda s: unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()


def biblioteca(texto):
    pal = [p for p in re.split(r'\W+', sin_tildes(texto)) if len(p) > 2]
    hits = []
    for raiz, _, fs in os.walk(CONTENIDO):
        if 'b-roll' not in raiz.replace('\\', '/'):
            continue
        for f in fs:
            if f.endswith('.mp4'):
                n = sum(p in sin_tildes(f) for p in pal)
                if n:
                    hits.append((n, os.path.relpath(os.path.join(raiz, f), CONTENIDO).replace('\\', '/')))
    for n, r in sorted(hits, reverse=True)[:15]:
        print(n, r)
    if not hits:
        print('nada en la biblioteca: prueba con pexels')


def clave():
    # el .env del repo; desde una copia de trabajo (worktree), el de la carpeta principal
    for env in (MOTOR.parent / '.env', Path.home() / 'montar-reels' / '.env'):
        for l in (env.read_text(encoding='utf-8').splitlines() if env.exists() else []):
            if l.startswith('PEXELS_API_KEY='):
                return l.split('=', 1)[1].strip()
    sys.exit(f'Falta PEXELS_API_KEY en {MOTOR.parent / ".env"}')


def pexels(query, nombre=None):
    nombre = re.sub(r'[^a-z0-9]+', '-', sin_tildes(nombre or query)).strip('-')[:40]
    req = urllib.request.Request('https://api.pexels.com/videos/search?' + urllib.parse.urlencode(
        {'query': query, 'orientation': 'portrait', 'per_page': 12}), headers={'Authorization': clave(), 'User-Agent': 'montar-reels'})
    vids = json.load(urllib.request.urlopen(req, timeout=20)).get('videos', [])
    DEST.mkdir(parents=True, exist_ok=True)
    bajados = 0
    for v in vids:
        fs = sorted([f for f in v.get('video_files', []) if 1900 <= (f.get('height') or 0) <= 2100 and (f.get('width') or 0) <= 1100],
                    key=lambda f: f['height'])
        if not fs or v.get('duration', 0) < 4:
            continue
        out = DEST / f'{nombre}_pexels-{v["id"]}.mp4'
        if not out.exists():
            # el servidor de vídeos de Pexels da 403 al identificador por defecto de Python
            r = urllib.request.urlopen(urllib.request.Request(fs[0]['link'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=60)
            out.write_bytes(r.read())
        d = v['duration']
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(out), '-vf',
                        f"select='eq(n,1)+eq(n,{int(d * 12)})+eq(n,{int(d * 24)})',scale=240:-1,tile=3x1", '-frames:v', '1',
                        '-vsync', 'vfr', str(out.with_suffix('.jpg'))], check=False)
        print(f'{out.relative_to(CONTENIDO).as_posix()}  ({d} s, {v.get("user", {}).get("name", "")})  hoja: {out.with_suffix(".jpg").name}')
        bajados += 1
        if bajados == 4:
            break
    if not bajados:
        print('Pexels no tiene vídeos verticales para eso: prueba otra query en inglés, más concreta')


if __name__ == '__main__':
    modo, texto = sys.argv[1], sys.argv[2]
    biblioteca(texto) if modo == 'biblioteca' else pexels(texto, sys.argv[3] if len(sys.argv) > 3 else None)
