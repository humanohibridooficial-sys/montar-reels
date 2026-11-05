# Buscador de b-roll gratis (spec 2026-11-05-buscador-broll-gratis): una consulta, todas las fuentes libres a la vez.
#   python buscar_broll.py buscar "lo que se ve, en inglés" [--es "palabras de la biblioteca"] [--n 4]
#       -> vistas previas pequeñas en <datos>/candidatos/<consulta>/, una hoja.jpg con todas y candidatos.json
#   python buscar_broll.py bajar <consulta> <ref> [nombre]     (ref = fuente:id de la hoja, p. ej. pixabay:12345)
#       -> el clip bueno a <reutilizables>/b-roll-<fuente>/, apuntado en LICENCIA.txt y en biblioteca.json
# Fuentes: biblioteca propia, Pexels, Pixabay, Mixkit y YouTube con licencia Creative Commons (cita obligatoria).
# Todo puede ir a anuncios: solo licencias que permiten uso comercial. Las claves no se imprimen nunca.
import json, re, subprocess, sys, unicodedata, urllib.parse, urllib.request
from pathlib import Path

from rutas import CONTENIDO, REUTILIZABLES, DATOS, MOTOR
import broll

sys.stdout.reconfigure(encoding='utf-8')
CAND = DATOS / 'candidatos'
UA = {'User-Agent': 'Mozilla/5.0'}
LICENCIAS = {
    'pexels': 'Pexels License: uso comercial libre, sin atribución',
    'pixabay': 'Pixabay Content License: uso comercial libre, sin atribución',
    'mixkit': 'Mixkit Stock Video Free License: uso comercial libre, sin atribución',
    'youtube': 'Creative Commons Attribution (CC BY): uso comercial CITANDO AL AUTOR en el caption',
}
# yt-dlp va con otro Python: si hereda PYTHONHOME (el Python de uv lo fija) falla con "Could not import runpy"
ENV_YT = {k: v for k, v in __import__('os').environ.items() if k != 'PYTHONHOME'}
slug = lambda s: re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()).strip('-')[:50]


def _json(url, headers=None):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **(headers or {})}), timeout=25))


def _bajar(url, out):
    out.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read())


def _usados():
    # los clips de las últimas piezas no se repiten (usados.json del motor guarda los b-roll de cada pieza)
    # usados.json guarda los recursos, no los clips: los ids de b-roll ya usados salen de las fichas de todas las piezas
    f = DATOS / 'usados.json'
    ya = json.dumps(json.load(open(f, encoding='utf-8'))) if f.exists() else ''
    for fi in (DATOS / 'fichas').glob('*.json'):
        ya += ' ' + ' '.join(b.get('file', '') for b in json.load(open(fi, encoding='utf-8')).get('broll', []))
    return ya


def _clave_pixabay():
    for c in (MOTOR / 'config.json', MOTOR.parent / 'config.json'):
        try:
            k = json.load(open(c, encoding='utf-8')).get('pixabay_key')
            if k:
                return k
        except (OSError, ValueError):
            pass
    return None


def pexels(q, n):
    try:
        k = broll.clave()
    except SystemExit:
        return []
    vs = _json('https://api.pexels.com/videos/search?' + urllib.parse.urlencode({'query': q, 'orientation': 'portrait', 'per_page': n * 3}),
               {'Authorization': k}).get('videos', [])
    out = []
    for v in vs:
        fs = sorted(v.get('video_files', []), key=lambda f: f.get('height') or 0)
        prev = next((f['link'] for f in fs if (f.get('height') or 0) >= 500), None)
        full = next((f['link'] for f in fs if 1900 <= (f.get('height') or 0) <= 2200), fs[-1]['link'] if fs else None)
        if prev and v.get('duration', 0) >= 3:
            out.append({'fuente': 'pexels', 'id': str(v['id']), 'prev': prev, 'full': full, 'autor': v.get('user', {}).get('name', ''),
                        'url': v.get('url', ''), 'dur': v.get('duration'), 'vertical': True})
    return out[:n]


def pixabay(q, n):
    k = _clave_pixabay()
    if not k:
        return []
    hs = _json('https://pixabay.com/api/videos/?' + urllib.parse.urlencode({'key': k, 'q': q, 'per_page': max(n * 3, 3), 'safesearch': 'true'})).get('hits', [])
    out = []
    for h in hs:
        v = h['videos']
        out.append({'fuente': 'pixabay', 'id': str(h['id']), 'prev': (v.get('tiny') or v.get('small'))['url'],
                    'full': (v.get('large') or v.get('medium'))['url'], 'autor': h.get('user', ''), 'url': h.get('pageURL', ''),
                    'dur': h.get('duration'), 'vertical': (v['large']['height'] or 0) > (v['large']['width'] or 1), 'tags': h.get('tags', '')})
    out.sort(key=lambda c: not c['vertical'])   # los verticales primero: un recorte de 1080p ampliado 1,8x se ve blando
    return out[:n]


def mixkit(q, n):
    # sin API: las páginas de categoría (/free-stock-video/<palabra>/) listan los clips; el vídeo sale de assets.mixkit.co
    ids = []
    for p in [slug(w) for w in q.split()][:3]:
        try:
            html = urllib.request.urlopen(urllib.request.Request(f'https://mixkit.co/free-stock-video/{p}/', headers=UA), timeout=25).read().decode('utf-8', 'ignore')
        except Exception:
            continue
        for s, i in re.findall(r'/free-stock-video/([a-z0-9-]+)-(\d+)/', html):
            if i not in [x[1] for x in ids]:
                ids.append((s, i))
    return [{'fuente': 'mixkit', 'id': i, 'prev': f'https://assets.mixkit.co/videos/{i}/{i}-360.mp4', 'full': f'https://assets.mixkit.co/videos/{i}/{i}-1080.mp4',
             'autor': 'Mixkit', 'url': f'https://mixkit.co/free-stock-video/{s}-{i}/', 'vertical': False, 'tags': s.replace('-', ' ')} for s, i in ids[:n]]


def youtube(q, n):
    # CC BY: el campo "license" de la ficha de YouTube; la cita del autor es obligatoria. Se busca con el filtro de
    # Creative Commons de YouTube (sp=EgIwAQ): con "ytsearch" normal no salía ni uno (control: Big Buck Bunny sí lo da).
    # OJO: hay canales que marcan CC partidos de la tele que no son suyos: vale solo lo grabado por el propio canal.
    url = 'https://www.youtube.com/results?' + urllib.parse.urlencode({'search_query': q}) + '&sp=EgIwAQ%253D%253D'
    r = subprocess.run(['yt-dlp', '--dump-json', '--skip-download', '--no-warnings', '--playlist-end', str(n * 3), url],
                       capture_output=True, text=True, encoding='utf-8', env=ENV_YT)
    out = []
    for l in r.stdout.splitlines():
        try:
            d = json.loads(l)
        except ValueError:
            continue
        if 'creative commons' in (d.get('license') or '').lower() and (d.get('duration') or 0) <= 1200:
            out.append({'fuente': 'youtube', 'id': d['id'], 'prev': None, 'full': d['webpage_url'], 'autor': d.get('channel') or d.get('uploader', ''),
                        'url': d['webpage_url'], 'dur': d.get('duration'), 'vertical': (d.get('height') or 0) > (d.get('width') or 1), 'tags': d.get('title', '')})
    return out[:n]


def buscar(q, es=None, n=4):
    d = CAND / slug(q)
    d.mkdir(parents=True, exist_ok=True)
    if es:
        print('== biblioteca'); broll.biblioteca(es)
    ya = _usados()
    cands = []
    for f in (pexels, pixabay, mixkit, youtube):
        try:
            cs = [c for c in f(q, n) if c['id'] not in ya]
        except Exception as e:
            print(f'{f.__name__}: no responde ({type(e).__name__})'); cs = []
        print(f'== {f.__name__}: {len(cs)}')
        cands += cs
    hojas = []
    for c in cands:
        ref = f"{c['fuente']}:{c['id']}"
        mp4 = d / f"{c['fuente']}-{c['id']}.mp4"
        try:
            if c['prev']:
                _bajar(c['prev'], mp4)
            else:   # YouTube: solo 20 s en baja calidad para la hoja
                subprocess.run(['yt-dlp', '-q', '--no-warnings', '-f', 'worst[ext=mp4]/worst', '--download-sections', '*0-20', '-o', str(mp4, env=ENV_YT), c['full']], check=True)
            jpg = mp4.with_suffix('.jpg')
            # 5 fotogramas repartidos por el clip (fps según su duración); el rótulo va con PIL: en drawtext los ":" de
            # "fuente:id" son separadores de opciones y el filtro falla
            dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(mp4)],
                                       capture_output=True, text=True).stdout or 10)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(mp4), '-vf', f'fps=5/{max(dur, 1):.2f},scale=-2:200,tile=5x1', '-frames:v', '1', str(jpg)], check=True)
            hojas.append((jpg, f"{ref}  {'vertical' if c['vertical'] else 'horizontal'}  {c['autor']}")); c['hoja'] = jpg.name
        except Exception as e:
            print(f'{ref}: sin vista previa ({type(e).__name__})')
        print(f"{ref}  {'vertical' if c['vertical'] else 'horizontal'}  {c.get('dur', '?')} s  {c['autor']}  {c.get('tags', '')[:60]}")
    if hojas:
        from PIL import Image, ImageDraw
        filas = []
        for jpg, txt in hojas:
            im = Image.open(jpg).convert('RGB'); im = im.resize((1000, max(1, int(im.height * 1000 / im.width))))
            f = Image.new('RGB', (1000, im.height + 36), (0, 0, 0)); f.paste(im, (0, 36))
            ImageDraw.Draw(f).text((8, 8), txt, fill=(255, 255, 255)); filas.append(f)
        h = Image.new('RGB', (1000, sum(f.height for f in filas)))
        y = 0
        for f in filas:
            h.paste(f, (0, y)); y += f.height
        h.save(d / 'hoja.jpg', quality=85)
    json.dump(cands, open(d / 'candidatos.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\nhoja: {d / "hoja.jpg"}\nMÍRALA antes de elegir: juveniles 16-18, césped bueno, acción, sin marcas grandes ni niños pequeños.')


def bajar(q, ref, nombre=None):
    d = CAND / slug(q)
    c = next(x for x in json.load(open(d / 'candidatos.json', encoding='utf-8')) if f"{x['fuente']}:{x['id']}" == ref)
    dest = REUTILIZABLES / f"b-roll-{c['fuente']}"
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / f"{slug(nombre or q)}_{c['fuente']}-{c['id']}.mp4"
    if c['fuente'] == 'youtube':
        subprocess.run(['yt-dlp', '-q', '-f', 'bv*[height<=1920][ext=mp4]+ba/b[ext=mp4]/b', '--merge-output-format', 'mp4', '-o', str(out, env=ENV_YT), c['full']], check=True)
    else:
        _bajar(c['full'], out)
    with open(dest / 'LICENCIA.txt', 'a', encoding='utf-8') as f:
        f.write(f"{out.name} | {LICENCIAS[c['fuente']]} | autor: {c['autor']} | {c['url']}\n")
    bib = DATOS / 'biblioteca.json'
    b = json.load(open(bib, encoding='utf-8')) if bib.exists() else []
    b.append({'file': out.relative_to(CONTENIDO).as_posix(), 'tema': '', 'describe': nombre or q, 'fuente': c['fuente'], 'id': c['id'],
              'url': c['url'], 'autor': c['autor'], 'licencia': LICENCIAS[c['fuente']], 'vertical': c['vertical'], 'dur': c.get('dur')})
    json.dump(b, open(bib, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(out.relative_to(CONTENIDO).as_posix())
    if c['fuente'] == 'youtube':
        print(f"AVISO CC BY: en el caption tiene que ir la cita: vídeo de {c['autor']} ({c['url']})")


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'buscar':
        es = a[a.index('--es') + 1] if '--es' in a else None
        n = int(a[a.index('--n') + 1]) if '--n' in a else 4
        buscar(a[1], es, n)
    elif a[0] == 'bajar':
        bajar(a[1], a[2], a[3] if len(a) > 3 else None)
