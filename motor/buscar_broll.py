# Buscador de b-roll (specs 2026-11-05-buscador-broll-gratis y 2026-11-11-recursos-pack-y-broll-infinito): una consulta,
# todas las fuentes con licencia comercial a la vez, y la IA solo como último recurso.
#   python buscar_broll.py buscar "lo que se ve, en inglés" [--es "palabras de la biblioteca"] [--n 4] [--youtube]
#       -> vistas previas pequeñas en <datos>/candidatos/<consulta>/, una hoja.jpg con todas y candidatos.json
#   python buscar_broll.py bajar <consulta> <ref> [nombre]     (ref = fuente:id de la hoja, p. ej. pixabay:12345)
#       -> el clip bueno a <reutilizables>/b-roll-<fuente>/, apuntado en LICENCIA.txt y en biblioteca.json
#   python buscar_broll.py generar "plano que no existe, en inglés" <nombre> --si-gastar [--motor apimart|higgsfield]
#       -> un clip vertical generado con IA a <reutilizables>/b-roll-ia/, marcado "ia": true en biblioteca.json.
#          GASTA CRÉDITOS: sin --si-gastar no envía nada. En la ficha, su b-roll lleva "ia": true (la puerta lo exige).
# Fuentes automáticas (API oficial o licencia propia): biblioteca propia, canal de Fran, Pexels, Pixabay, Coverr.
# YouTube CC BY solo con --youtube (obliga a citar al autor en el caption). Mixkit, Videezy, Dareful, Free Nature
# Stock y Life of Vids NO se consultan desde aquí: sus términos solo permiten la descarga a mano (Mixkit prohíbe
# expresamente scripts y bots) o no tienen API. Todo puede ir a anuncios. Las claves no se imprimen nunca.
import json, os, re, subprocess, sys, time, unicodedata, urllib.parse, urllib.request
from pathlib import Path

from rutas import CONTENIDO, REUTILIZABLES, DATOS, MOTOR
import broll

sys.stdout.reconfigure(encoding='utf-8')
CAND = DATOS / 'candidatos'
UA = {'User-Agent': 'Mozilla/5.0'}
LICENCIAS = {
    'pexels': 'Pexels License: uso comercial libre, sin atribución (no gente enferma o medicándose, no marcas)',
    'pixabay': 'Pixabay Content License: uso comercial libre, sin atribución (no marcas ni logos)',
    'coverr': 'Coverr License: uso comercial y anuncios; con la clave Demo de la API hay que citar a Coverr y al autor',
    'mixkit': 'Mixkit Stock Video Free License: uso comercial libre, sin atribución (bajado a mano)',
    'youtube': 'Creative Commons Attribution (CC BY): uso comercial CITANDO AL AUTOR en el caption',
    'fran': 'Canal de Fran (@fran.entrenador): licencia de Luismi para republicar bajo su marca (11-09)',
    'ia': 'Generado con IA: sin derechos de terceros; se marca como IA en la ficha',
}
FRAN = 'https://www.youtube.com/@fran.entrenador'
# Filtros fijos (los del revisor): nunca niños pequeños ni marcas. Se descartan por etiqueta o título; lo que pase,
# lo juzga el director en la hoja (juveniles 16-18 o sin personas).
NO = re.compile(r'\b(child|children|kid|kids|toddler|baby|babies|little (boy|girl)|schoolboy|schoolgirl|niñ[oa]s?|bebé|'
                r'nike|adidas|puma|barcelona|real madrid|logo|brand)\b', re.I)
# yt-dlp va con otro Python: si hereda PYTHONHOME (el Python de uv lo fija) falla con "Could not import runpy"
ENV_YT = {k: v for k, v in os.environ.items() if k != 'PYTHONHOME'}
slug = lambda s: re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()).strip('-')[:50]


def _json(url, headers=None, data=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})}, data=data)
    return json.load(urllib.request.urlopen(req, timeout=30))


def _bajar(url, out):
    out.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180).read())


def _usados():
    # los ids de b-roll ya usados salen de usados.json y de las fichas de todas las piezas
    f = DATOS / 'usados.json'
    ya = json.dumps(json.load(open(f, encoding='utf-8'))) if f.exists() else ''
    for fi in (DATOS / 'fichas').glob('*.json'):
        try:
            ya += ' ' + ' '.join(b.get('file', '') for b in json.load(open(fi, encoding='utf-8')).get('broll', []))
        except ValueError:
            pass
    return ya


def clave(nombre, en_config=None, ficheros=()):
    """Clave de API: variable de entorno, .env del repo (o del checkout principal) o config.json. Nunca se imprime.
    Los ficheros van antes que el entorno cuando se pasan: en Windows hay una APIMART_API_KEY de usuario caducada que
    tapa la buena (memoria apimart-401)."""
    def de_fichero():
        for env in list(ficheros) + [MOTOR.parent / '.env', Path.home() / 'montar-reels' / '.env']:
            for l in (env.read_text(encoding='utf-8', errors='ignore').splitlines() if env.exists() else []):
                if l.startswith(nombre + '='):
                    return l.split('=', 1)[1].strip().strip('"\'')
        for c in (MOTOR / 'config.json', MOTOR.parent / 'config.json', Path.home() / 'montar-reels' / 'config.json'):
            try:
                k = json.load(open(c, encoding='utf-8')).get(en_config or '')
                if k:
                    return k
            except (OSError, ValueError):
                pass
    if ficheros:
        return de_fichero() or os.environ.get(nombre)
    return os.environ.get(nombre) or de_fichero()


def propia(q, n):
    # biblioteca.json: lo ya licenciado y descrito a mano (tema, subtema, describe). Sin descarga.
    pal = [p for p in re.split(r'\W+', broll.sin_tildes(q)) if len(p) > 2]
    bib = json.load(open(DATOS / 'biblioteca.json', encoding='utf-8')) if (DATOS / 'biblioteca.json').exists() else []
    hits = []
    for b in bib:
        txt = broll.sin_tildes(' '.join(str(b.get(k, '')) for k in ('tema', 'subtema', 'describe', 'file')))
        s = sum(p in txt for p in pal)
        if s:
            hits.append((s, b))
    for s, b in sorted(hits, key=lambda h: -h[0])[:n * 2]:
        print(f"  {s} {b['file']}  ({b.get('fuente', 'propia')}{', IA' if b.get('ia') else ''}) {b.get('describe', '')[:60]}")
    return []   # ya está en local: no hace falta hoja


def pexels(q, n):
    k = clave('PEXELS_API_KEY')
    if not k:
        print('  sin PEXELS_API_KEY'); return []
    vs = _json('https://api.pexels.com/videos/search?' + urllib.parse.urlencode({'query': q, 'orientation': 'portrait', 'per_page': n * 3}),
               {'Authorization': k}).get('videos', [])
    out = []
    for v in vs:
        fs = sorted(v.get('video_files', []), key=lambda f: f.get('height') or 0)
        prev = next((f['link'] for f in fs if (f.get('height') or 0) >= 500), None)
        full = next((f['link'] for f in fs if 1900 <= (f.get('height') or 0) <= 2200), fs[-1]['link'] if fs else None)
        if prev and v.get('duration', 0) >= 3:
            out.append({'fuente': 'pexels', 'id': str(v['id']), 'prev': prev, 'full': full, 'autor': v.get('user', {}).get('name', ''),
                        'url': v.get('url', ''), 'dur': v.get('duration'), 'vertical': True, 'tags': v.get('url', '').rsplit('/', 2)[-2]})
    return out[:n]


def pixabay(q, n):
    k = clave('PIXABAY_API_KEY', 'pixabay_key')
    if not k:
        print('  sin clave de Pixabay (PIXABAY_API_KEY o pixabay_key en config.json)'); return []
    # sin filtro de orientación en la API de vídeo: se piden de sobra y se ordenan los verticales primero
    hs = _json('https://pixabay.com/api/videos/?' + urllib.parse.urlencode({'key': k, 'q': q, 'per_page': max(n * 4, 3), 'safesearch': 'true'})).get('hits', [])
    out = []
    for h in hs:
        v = h['videos']
        big = v.get('large') if (v.get('large') or {}).get('url') else v.get('medium')
        out.append({'fuente': 'pixabay', 'id': str(h['id']), 'prev': (v.get('tiny') or v.get('small'))['url'],
                    'full': big['url'], 'autor': h.get('user', ''), 'url': h.get('pageURL', ''),
                    'dur': h.get('duration'), 'vertical': (big.get('height') or 0) > (big.get('width') or 1), 'tags': h.get('tags', '')})
    out.sort(key=lambda c: not c['vertical'])   # los verticales primero: un recorte de 1080p ampliado 1,8x se ve blando
    return out[:n]


def coverr(q, n):
    # API oficial (api.coverr.co). La clave se pide por email a Coverr; sin ella la fuente se salta.
    k = clave('COVERR_API_KEY', 'coverr_key')
    if not k:
        print('  sin COVERR_API_KEY (se pide a Coverr por email): se salta'); return []
    hs = _json('https://api.coverr.co/videos?' + urllib.parse.urlencode({'query': q, 'page': 0, 'page_size': n * 3, 'urls': 'true'}),
               {'x-api-key': k}).get('hits', [])
    out = []
    for h in hs:
        u = h.get('urls') or {}
        if not u.get('mp4'):
            continue
        out.append({'fuente': 'coverr', 'id': str(h['id']), 'prev': u.get('mp4_preview') or u['mp4'], 'full': u.get('mp4_download') or u['mp4'],
                    'autor': 'Coverr', 'url': f"https://api.coverr.co/videos/{h['id']}", 'dur': h.get('duration'),
                    'vertical': bool(h.get('is_vertical')), 'tags': h.get('title', '')})
    out.sort(key=lambda c: not c['vertical'])
    return out[:n]


def _yt(url, n):
    r = subprocess.run(['yt-dlp', '--dump-json', '--skip-download', '--no-warnings', '--playlist-end', str(n * 3), url],
                       capture_output=True, text=True, encoding='utf-8', env=ENV_YT)
    return [json.loads(l) for l in r.stdout.splitlines() if l.startswith('{')]


def fran(q, n):
    # Canal de Fran: ejercicios de fuerza, prevención y técnica con licencia de Luismi. Se busca dentro del canal.
    out = []
    for d in _yt(f'{FRAN}/search?' + urllib.parse.urlencode({'query': q}), n):
        if (d.get('channel_id') or '') != 'UCjf9ozK5uCZUPvUMoBNR24w':
            continue
        out.append({'fuente': 'fran', 'id': d['id'], 'prev': None, 'full': d['webpage_url'], 'autor': 'Fran (@fran.entrenador)',
                    'url': d['webpage_url'], 'dur': d.get('duration'), 'vertical': (d.get('height') or 0) > (d.get('width') or 1),
                    'tags': d.get('title', '')})
    return out[:n]


def youtube(q, n):
    # CC BY con el filtro de Creative Commons de YouTube (sp=EgIwAQ). Vale solo lo grabado por el propio canal.
    url = 'https://www.youtube.com/results?' + urllib.parse.urlencode({'search_query': q}) + '&sp=EgIwAQ%253D%253D'
    return [{'fuente': 'youtube', 'id': d['id'], 'prev': None, 'full': d['webpage_url'], 'autor': d.get('channel') or d.get('uploader', ''),
             'url': d['webpage_url'], 'dur': d.get('duration'), 'vertical': (d.get('height') or 0) > (d.get('width') or 1), 'tags': d.get('title', '')}
            for d in _yt(url, n) if 'creative commons' in (d.get('license') or '').lower() and (d.get('duration') or 0) <= 1200][:n]


def buscar(q, es=None, n=4, con_youtube=False):
    d = CAND / slug(q)
    d.mkdir(parents=True, exist_ok=True)
    print('== biblioteca propia (biblioteca.json)'); propia(es or q, n)
    if es:
        print('== 3 RECURSOS (nombres de fichero)'); broll.biblioteca(es)
    ya = _usados()
    cands = []
    # El canal de Fran es licencia de Luismi, no de quien se instala el editor: los instaladores ponen "fran": false
    import rutas
    con_fran = rutas._c.get('fran', True)
    for f in ((fran,) if con_fran else ()) + (pexels, pixabay, coverr) + ((youtube,) if con_youtube else ()):
        try:
            cs = f(es or q, n) if f is fran else f(q, n)   # los títulos de Fran están en español
        except Exception as e:
            print(f'{f.__name__}: no responde ({type(e).__name__})'); cs = []
        fuera = [c for c in cs if NO.search(f"{c.get('tags', '')} {c['url']}")]
        cs = [c for c in cs if c['id'] not in ya and c not in fuera]
        print(f'== {f.__name__}: {len(cs)}' + (f' ({len(fuera)} fuera por niños o marcas)' if fuera else ''))
        cands += cs
    hojas = []
    for c in cands:
        ref = f"{c['fuente']}:{c['id']}"
        mp4 = d / f"{c['fuente']}-{c['id']}.mp4"
        try:
            if c['prev']:
                _bajar(c['prev'], mp4)
            else:   # YouTube: solo 20 s en baja calidad para la hoja
                subprocess.run(['yt-dlp', '-q', '--no-warnings', '-f', 'worst[ext=mp4]/worst', '--download-sections', '*0-20', '-o', str(mp4), c['full']],
                               check=True, env=ENV_YT)
            jpg = mp4.with_suffix('.jpg')
            # 5 fotogramas repartidos por el clip; el rótulo va con PIL (en drawtext los ":" de "fuente:id" son separadores)
            dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(mp4)],
                                       capture_output=True, text=True).stdout or 10)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(mp4), '-vf', f'fps=5/{max(dur, 1):.2f},scale=-2:200,tile=5x1', '-frames:v', '1', str(jpg)], check=True)
            hojas.append((jpg, f"{ref}  {'vertical' if c['vertical'] else 'horizontal'}  {c['autor']}")); c['hoja'] = jpg.name
        except Exception as e:
            print(f'{ref}: sin vista previa ({type(e).__name__})')
        print(f"{ref}  {'vertical' if c['vertical'] else 'horizontal'}  {c.get('dur', '?')} s  {c['autor']}  {str(c.get('tags', ''))[:60]}")
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
    print(f'\nhoja: {d / "hoja.jpg"}\nMÍRALA antes de elegir: juveniles 16-18 o sin personas, nunca niños pequeños, césped bueno, sin marcas.'
          '\nSi no hay nada: Mixkit, Videezy, Dareful o Free Nature Stock a mano, o "generar" (IA, gasta créditos).')


def _apuntar(out, entrada):
    # índice único del b-roll con licencia y origen (spec 11-11): biblioteca.json
    bib = DATOS / 'biblioteca.json'
    b = json.load(open(bib, encoding='utf-8')) if bib.exists() else []
    b = [x for x in b if x.get('file') != entrada['file']] + [entrada]
    json.dump(b, open(bib, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(out.parent / 'LICENCIA.txt', 'a', encoding='utf-8') as f:
        f.write(f"{out.name} | {entrada['licencia']} | autor: {entrada.get('autor', '')} | {entrada.get('url', '')}\n")


def bajar(q, ref, nombre=None):
    d = CAND / slug(q)
    c = next(x for x in json.load(open(d / 'candidatos.json', encoding='utf-8')) if f"{x['fuente']}:{x['id']}" == ref)
    dest = REUTILIZABLES / f"b-roll-{c['fuente']}"
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / f"{slug(nombre or q)}_{c['fuente']}-{c['id']}.mp4"
    if c['fuente'] in ('youtube', 'fran'):
        subprocess.run(['yt-dlp', '-q', '-f', 'bv*[height<=1920][ext=mp4]+ba/b[ext=mp4]/b', '--merge-output-format', 'mp4', '-o', str(out), c['full']],
                       check=True, env=ENV_YT)
    else:
        _bajar(c['full'], out)
        if c['fuente'] == 'coverr':   # la API pide avisar de cada descarga
            try:
                urllib.request.urlopen(urllib.request.Request(f"https://api.coverr.co/videos/{c['id']}/stats/downloads", method='PATCH',
                                                              headers={**UA, 'x-api-key': clave('COVERR_API_KEY', 'coverr_key')}), timeout=15)
            except Exception:
                print('aviso: Coverr no confirmó la descarga en sus estadísticas')
    _apuntar(out, {'file': out.relative_to(CONTENIDO).as_posix(), 'tema': '', 'describe': nombre or q, 'fuente': c['fuente'], 'id': c['id'],
                   'url': c['url'], 'autor': c['autor'], 'licencia': LICENCIAS[c['fuente']], 'vertical': c['vertical'], 'dur': c.get('dur'),
                   'bajado': time.strftime('%Y-%m-%d')})
    print(out.relative_to(CONTENIDO).as_posix())
    if c['fuente'] == 'youtube':
        print(f"AVISO CC BY: en el caption tiene que ir la cita: vídeo de {c['autor']} ({c['url']})")


# ---- IA: último recurso, para planos que no existen en stock (p. ej. padres en la grada con su hijo de 16-18) ----------
REGLAS_IA = ('Vertical 9:16 smartphone-style documentary footage, natural light, realistic. Any young people are teenagers aged 16 to 18, '
             'never small children. No logos, no brand names, no text, no watermarks, no club crests. No dialogue.')


def _apimart(prompt, dur):
    k = clave('APIMART_API_KEY', 'apimart_key', ficheros=[Path.home() / 'HH-DIETAS' / '.env.local'])
    if not k:
        sys.exit('Falta APIMART_API_KEY (.env del repo o HH-DIETAS/.env.local)')
    h = {'Authorization': f'Bearer {k}', 'Content-Type': 'application/json'}
    # contrato verificado en HH-DIETAS/lib/contenido/apimart.ts: POST devuelve data[0].task_id, se sondea /v1/tasks/<id>
    modelo = os.environ.get('APIMART_MODELO_VIDEO', 'gemini-omni-1.1-flash-ext')
    r = _json('https://api.apimart.ai/v1/videos/generations', h,
              json.dumps({'model': modelo, 'prompt': prompt, 'duration': dur, 'resolution': '720p', 'size': '9:16'}).encode())
    tid = r['data'][0]['task_id']
    for _ in range(120):
        time.sleep(10)
        t = _json(f'https://api.apimart.ai/v1/tasks/{tid}?language=en', h)['data']
        if t.get('status') == 'completed':
            v = (t.get('result') or {}).get('videos') or []
            u = v[0]['url'] if v else None
            return (u[0] if isinstance(u, list) else u), modelo   # la URL caduca a las 24 h: se baja ya
        if t.get('status') in ('failed', 'cancelled'):
            sys.exit(f"ApiMart: la tarea {tid} acabó en {t.get('status')}")
    sys.exit(f'ApiMart: la tarea {tid} no acabó en 20 min')


def _higgsfield(prompt, dur):
    # CLI de Higgsfield con sesión iniciada ("higgsfield auth login", lo hace Luismi). Seedance 2.5 por defecto.
    r = subprocess.run(['higgsfield', 'generate', 'create', 'seedance_2_5', '--prompt', prompt, '--mode', 't2v', '--aspect_ratio', '9:16',
                        '--duration', str(dur), '--resolution', '1080p', '--wait', '--json'], capture_output=True, text=True, encoding='utf-8')
    u = re.findall(r'https://[^"\s]+\.mp4[^"\s]*', r.stdout)
    if r.returncode or not u:
        sys.exit('Higgsfield no devolvió vídeo: ' + (r.stderr or r.stdout)[-300:])
    return u[0], 'seedance_2_5'


def generar(prompt, nombre, motor='apimart', dur=5):
    prompt_final = f'{prompt}. {REGLAS_IA}'
    url, modelo = (_higgsfield if motor == 'higgsfield' else _apimart)(prompt_final, dur)
    dest = REUTILIZABLES / 'b-roll-ia'
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / f"{slug(nombre)}_ia-{time.strftime('%Y%m%d-%H%M%S')}.mp4"
    _bajar(url, out)
    _apuntar(out, {'file': out.relative_to(CONTENIDO).as_posix(), 'tema': '', 'describe': nombre, 'fuente': 'ia', 'ia': True,
                   'motor': motor, 'modelo': modelo, 'prompt': prompt_final, 'licencia': LICENCIAS['ia'], 'autor': f'IA ({motor}/{modelo})',
                   'url': '', 'vertical': True, 'dur': dur, 'bajado': time.strftime('%Y-%m-%d')})
    print(out.relative_to(CONTENIDO).as_posix())
    print('Generado con IA: en la ficha, este b-roll lleva "ia": true. MÍRALO: nada de niños pequeños, manos raras ni texto.')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'buscar':
        es = a[a.index('--es') + 1] if '--es' in a else None
        n = int(a[a.index('--n') + 1]) if '--n' in a else 4
        buscar(a[1], es, n, '--youtube' in a)
    elif a[0] == 'bajar':
        bajar(a[1], a[2], a[3] if len(a) > 3 and not a[3].startswith('--') else None)
    elif a[0] == 'generar':
        if '--si-gastar' not in a:
            sys.exit('generar gasta créditos de IA: vuelve a lanzarlo con --si-gastar si de verdad no hay plano en stock')
        generar(a[1], a[2], a[a.index('--motor') + 1] if '--motor' in a else 'apimart',
                int(a[a.index('--dur') + 1]) if '--dur' in a else 5)
