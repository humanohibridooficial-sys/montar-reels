# Catálogo del PACK DE RECURSOS 2.0 (spec 2026-11-11-recursos-pack-y-broll-infinito). Lo compró Luismi: vale para
# anuncios, salvo los ficheros ES_* (Epidemic Sound) y la carpeta 05_MÚSICA, que no entran nunca.
#   python pack.py inventario              -> motor-datos/pack.json (tipo, fichero, alfa, tamaño, duración, fusión)
#   python pack.py listar <tipo> [palabra]  -> lo que hay de un tipo: overlay, transicion, elemento, lut
# La ficha los pide por "nombre" (un trozo del nombre del fichero, sin tildes ni mayúsculas) y montar.py los resuelve aquí.
import json, re, subprocess, sys, unicodedata

from rutas import REUTILIZABLES, DATOS

PACK = REUTILIZABLES / 'PACK DE RECURSOS 2.0'
CATALOGO = DATOS / 'pack.json'
VIDEO = ('.mp4', '.mov', '.gif')
IMAGEN = ('.png',)
# carpeta de arriba -> tipo. 02_BACKGROUNDS (fondos) no tiene recurso que lo use todavía.
TIPO = {'03_OVERLAYS': 'overlay', '06_TRANSICIONES': 'transicion', '01_ANIMACIONES': 'elemento', '07_PNGs': 'elemento', '09_LUTs': 'lut'}
plano = lambda s: unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()


def _fuera(f):
    rel = f.relative_to(PACK).as_posix()
    return f.name.startswith('._') or f.name.upper().startswith('ES_') or rel.startswith('05_M') or rel.startswith('04_SFX')


def _probe(f):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                        'stream=codec_name,pix_fmt,width,height:format=duration', '-of', 'json', str(f)],
                       capture_output=True, text=True, encoding='utf-8')
    try:
        j = json.loads(r.stdout); s = j['streams'][0]
    except (ValueError, KeyError, IndexError):
        return None
    if not s.get('width'):
        return None   # webp animado: ffmpeg no lo decodifica
    return {'codec': s.get('codec_name'), 'alfa': 'a' in (s.get('pix_fmt') or '').replace('gray', ''),
            'w': s['width'], 'h': s['height'], 'dur': round(float(j.get('format', {}).get('duration') or 0), 2)}


def _pico(f):
    r = subprocess.run(['ffmpeg', '-v', 'info', '-i', str(f), '-vf', 'scale=64:-2,signalstats,metadata=print:key=lavfi.signalstats.YAVG',
                        '-an', '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='ignore').stderr
    pts = [float(t) for t in re.findall(r'pts_time:([\d.]+)', r)]
    ys = [float(y) for y in re.findall(r'YAVG=([\d.]+)', r)]
    return round(pts[ys.index(max(ys))], 2) if ys and len(pts) == len(ys) else 0.0


def inventario():
    out = []
    for f in sorted(PACK.rglob('*')):
        if not f.is_file() or _fuera(f):
            continue
        top = f.relative_to(PACK).parts[0]
        tipo = TIPO.get(top)
        if not tipo:
            continue
        rel = f.relative_to(REUTILIZABLES).as_posix()
        if tipo == 'lut':
            if f.suffix.lower() == '.cube':
                out.append({'tipo': 'lut', 'nombre': f.stem, 'file': rel})
            continue
        if f.suffix.lower() not in VIDEO + IMAGEN:
            continue
        p = _probe(f)
        if not p:
            continue
        estatico = f.suffix.lower() in IMAGEN
        if tipo == 'elemento' and not p['alfa'] and not estatico:
            tipo_f = 'overlay'   # una animación sin alfa (fondo negro) solo sirve fundida, como los overlays
        else:
            tipo_f = tipo
        if tipo_f == 'elemento' and not p['alfa']:
            continue   # PNG sin transparencia (fondos de miniatura): taparía el plano
        modo = 'alfa' if p['alfa'] else ('overlay' if 'grain' in plano(rel) else 'screen')
        it = {'tipo': tipo_f, 'nombre': f.stem, 'file': rel, 'modo': modo, 'estatico': estatico, **p}
        if tipo_f in ('transicion', 'overlay') and modo == 'screen' and 0 < p['dur'] <= 15:
            it['pico'] = _pico(f)   # una transición se centra en su fotograma más luminoso, no en el primero (suele ser negro)
        out.append(it)
    CATALOGO.write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding='utf-8')
    n = {}
    for o in out:
        n[o['tipo']] = n.get(o['tipo'], 0) + 1
    print(CATALOGO, n)


def catalogo():
    if not CATALOGO.exists():
        sys.exit(f'Falta {CATALOGO}: python pack.py inventario')
    return json.load(open(CATALOGO, encoding='utf-8'))


def buscar(tipo, nombre):
    """El recurso del pack de ese tipo cuyo nombre (o ruta) contiene "nombre"; si hay varios, el de nombre más corto."""
    q = plano(nombre)
    hits = [c for c in catalogo() if c['tipo'] == tipo and (q in plano(c['nombre']) or q in plano(c['file']))]
    if not hits:
        raise KeyError(f'pack: no hay ningún {tipo} que se llame como {nombre!r} (python pack.py listar {tipo})')
    exacto = [c for c in hits if plano(c['nombre']) == q]
    return (exacto or sorted(hits, key=lambda c: len(c['nombre'])))[0]


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1] == 'inventario':
        inventario()
    elif sys.argv[1] == 'listar':
        q = plano(sys.argv[3]) if len(sys.argv) > 3 else ''
        for c in catalogo():
            if c['tipo'] == sys.argv[2] and q in plano(c['file']):
                print(f"{c['nombre']:<50} {c.get('modo', ''):<8} {c.get('w', '')}x{c.get('h', '')} {c.get('dur', '')} s  {c['file']}")
