# Monta una pieza de Nuevos 27 con el estilo de los ejemplos (Carla y los otros tres), sobre la plantilla talking-head
# de Huashu. Todo lo propio de cada pieza vive en su ficha piezas/<n>.json; esto es común.
#   python montar.py 76        -> deja p76/ listo para "om render" (y p76/plan.json para mezcla.py)
# Ficha: video, keep [[a,b],...] en segundos de la toma, fix {palabra: corregida}, subsTop, origin,
#   broll [{id, file, ss, in: cue, out: cue, modo: ''|'split'}], tops [[cue, cue, linea1, linea2, cursiva]],
#   panel {items: [[cue, h1, h2, bala, broll_id]], fin: cue}, byn [cue, cue], tachado {texto, in, raya, out},
#   num {texto, in, out}, leaks [cue], claves [...], serif [...], follow cue,
#   extras [{tipo, in: cue, out: cue, ...}] (recursos del 30-10, ver el apartado 5).  Una cue es "palabra", "palabra#2"
#   (la segunda vez que sale en el montaje), "palabra#2>" (su final) o un número (segundo del montaje).
import json, subprocess, re, sys, shutil, pathlib, html

N = sys.argv[1]
from rutas import CONTENIDO, TOMAS, FICHAS, PALABRAS, VOZ, RENDER, PLANTILLA, SCRIPTS, PY_SILUETA
from estilo import CSS, JS
F = json.load(open(FICHAS / f'{N}.json', encoding='utf-8'))
P = RENDER / f'p{N}'
# Con carpeta: relativa a carpeta_contenido. Sin ella, en carpeta_tomas (las DJI) o en carpeta_contenido (las del móvil, m1-m7).
SRC = CONTENIDO / F['video'] if '/' in F['video'] or not (TOMAS / F['video']).exists() else TOMAS / F['video']
def run(*a):
    subprocess.run(a, check=True)

# Tramos finales: los de la ficha, menos lo que dice "quitar" (muletillas, repeticiones) y menos las pausas
# de más de 0,35 s que mide la voz limpia, que se dejan en ~0,22 s (ritmo de los ejemplos).
def recortar(keep, quitar, pausas):
    fuera = sorted([list(q) for q in quitar] + [[s + 0.12, e - 0.10] for s, e in pausas if e - s > 0.35])
    out = []
    for a, b in keep:
        cur = a
        for s, e in fuera:
            if e <= cur or s >= b:
                continue
            if s - cur > 0.15:
                out.append([round(cur, 3), round(s, 3)])
            cur = max(cur, e)
        if b - cur > 0.15:
            out.append([round(cur, 3), round(b, 3)])
    return out

_sd = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(VOZ / f'{N}-limpio.wav'), '-af', 'silencedetect=noise=-38dB:d=0.35',
                      '-f', 'null', '-'], capture_output=True, text=True).stderr
PAUSAS = [(float(a), float(b)) for a, b in re.findall(r'silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)', _sd)] if F.get('apretar', True) else []
KEEP = recortar(F['keep'], F.get('quitar', []), PAUSAS)
# El "sígueme" no se puede cortar: el último tramo acaba 0,15 s después de que acabe la voz de verdad.
_sd = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(VOZ / f'{N}-limpio.wav'), '-af', 'silencedetect=noise=-38dB:d=0.3',
                      '-f', 'null', '-'], capture_output=True, text=True).stderr
_b = KEEP[-1][1]
_fin = [float(s) for s, e in re.findall(r'silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)', _sd)
        if float(e) > _b and _b - 0.6 < float(s) < _b + 1.0]
if _fin and not F.get('finExacto'):
    KEEP[-1][1] = round(_fin[0] + 0.15, 3)

if not (P / 'vendor').exists():
    shutil.copytree(PLANTILLA / 'vendor', P / 'vendor')
(P / 'assets/broll').mkdir(parents=True, exist_ok=True)
shutil.copytree(PLANTILLA / 'fonts', P / 'assets/fonts', dirs_exist_ok=True)

def nuevo(t):
    acc = 0.0
    for a, b in KEEP:
        if a <= t <= b:
            return round(acc + t - a, 3)
        acc += b - a
    return None

LEN = round(sum(b - a for a, b in KEEP), 3)

# ---- 1. toma cortada; voz limpia (DeepFilterNet) con la cadena de voz --------------------------------
# Con muchos cortes, un trim por tramo vuelve a decodificar la toma desde el principio cada vez: el vídeo se
# elige por número de fotograma en una sola pasada, y los cortes se ajustan a fotograma para que la voz no se desfase.
FPS = 30
KEEP = [[round(round(a * FPS) / FPS, 4), round(round(b * FPS) / FPS, 4)] for a, b in KEEP]
LEN = round(sum(b - a for a, b in KEEP), 3)
sel = '+'.join(f'between(n,{round(a * FPS)},{round(b * FPS) - 1})' for a, b in KEEP)
parts = f"[0:v]fps={FPS},select='{sel}',setpts=N/{FPS}/TB[v];" + ''.join(
    f'[1:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={round(b - a - 0.015, 3)}:d=0.015[a{i}];'
    for i, (a, b) in enumerate(KEEP))
cat = ''.join(f'[a{i}]' for i in range(len(KEEP))) + f'concat=n={len(KEEP)}:v=0:a=1[a]'
run('ffmpeg', '-v', 'error', '-y', '-i', str(SRC), '-i', str(VOZ / f'{N}-limpio.wav'), '-filter_complex', parts + cat,
    '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', str(P / 'assets/talk.mp4'))
run('ffmpeg', '-v', 'error', '-y', '-i', str(P / 'assets/talk.mp4'), '-vn',
    '-af', 'highpass=f=80,lowpass=f=14000,acompressor=threshold=-20dB:ratio=2:attack=10:release=120,deesser',
    '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', str(P / 'assets/voice.wav'))

# ---- 2. b-roll -----------------------------------------------------------------------------------------
B = list(F.get('broll', [])) + [it for it in F.get('panel', {}).get('broll', [])]
for b in B:
    f = CONTENIDO / b['file']
    trc = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_transfer',
                          '-of', 'csv=p=0', str(f)], capture_output=True, text=True).stdout.strip().strip(',').split(',')[0]
    hdr = 'zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,' \
        if trc in ('arib-std-b67', 'smpte2084') else ''
    run('ffmpeg', '-v', 'error', '-y', '-ss', str(b.get('ss', 0)), '-i', str(f), '-t', '8', '-an',
        '-vf', hdr + 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30',
        '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
        '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(P / f"assets/broll/{b['id']}.mp4"))

# ---- 3. palabras ---------------------------------------------------------------------------------------
FIX = F.get('fix', {})
words = []
for seg in json.load(open(PALABRAS, encoding='utf-8'))[f'{N}-limpio.wav']:
    for w in seg['words']:
        s, e = nuevo(w['start']), nuevo(w['end'])
        if s is None and e is None:
            continue
        if s is None:   # whisper adelanta el inicio a la pausa que se ha quitado: empieza donde arranca el tramo
            s = next(nuevo(a) for a, b in KEEP if a <= w['end'] <= b)
        if e is None:   # whisper alarga la última palabra antes de un silencio: se recorta al final del tramo
            e = next(nuevo(b) for a, b in KEEP if a <= w['start'] <= b)
        words.append({'word': FIX.get(w['word'], w['word']), 'start': s, 'end': e})
norm = lambda x: re.sub(r'[^\wáéíóúüñ]', '', x.lower())

def cue(c):
    if isinstance(c, (int, float)):
        return float(c)
    fin = c.endswith('>')
    c = c.rstrip('>')
    w, _, n = c.partition('#')
    n = int(n or 1)
    hits = [x for x in words if norm(x['word']) == norm(w)]
    if len(hits) < n:
        raise KeyError(f'cue {c!r}: sale {len(hits)} veces')
    return round(hits[n - 1]['end' if fin else 'start'], 3)

side = {'source': 'assets/voice.wav', 'duration': LEN, 'precision': 'asr-python', 'words': words}
json.dump(side, open(P / 'assets/voice.words.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
(P / 'guion.txt').write_text(' '.join(w['word'] for w in words), encoding='utf-8')

# ---- 4. index.html desde la plantilla ------------------------------------------------------------------
s = (PLANTILLA / 'index.html').read_text(encoding='utf-8')
tag = '<script type="application/json" id="om-cues">'
a = s.index(tag) + len(tag); b = s.index('</script>', a)
cues = json.loads(s[a:b]); cues.update(words=words, duration=LEN)
s = s[:a] + json.dumps(cues, ensure_ascii=False) + s[b:]
s = s.replace('data-duration="43.63"', f'data-duration="{LEN}"')
A = "data-composition-variables='"
i = s.index(A) + len(A); j = s.index("'>", i)
vs = json.loads(s[i:j])
nuevos = {'length': LEN, 'subjectTop': 0.29, 'subjectBottom': 0.50, 'cardBottom': 0.70, 'corner': '', 'stats': '[]', 'keywords': '[]'}
for v in vs:
    if v['id'] in nuevos:
        v['default'] = nuevos.pop(v['id'])
assert not nuevos, nuevos
s = s[:i] + json.dumps(vs, ensure_ascii=False, indent=1) + s[j:]
s = s.replace('@font-face { font-family: "Inter";',
              '@font-face { font-family: "Anton"; src: url("assets/fonts/Anton-Regular.ttf") format("truetype"); }\n'
              '@font-face { font-family: "Playfair"; font-style: italic; src: url("assets/fonts/PlayfairDisplay-Italic.ttf") format("truetype"); }\n'
              '@font-face { font-family: "Inter";')

SUBS = F.get('subsTop', 1040)
CSS = CSS.replace('top: 1040px; height: 260px', f'top: {SUBS}px; height: 260px').replace('transform-origin: 50% 42%', f"transform-origin: {F.get('origin', '50% 40%')}")
s = s.replace('  #pack { position: absolute; inset: 0; pointer-events: none; }', CSS + '  #pack { position: absolute; inset: 0; pointer-events: none; }')

spans = [[b['id'], cue(b['in']), round(cue(b['out']) + 0.12, 3), b.get('modo', '')] for b in F.get('broll', [])]
PN = F.get('panel')
panel = []
if PN:
    panel = [cue(it[0]) for it in PN['items']] + [cue(PN['fin'])]
    for k, it in enumerate(PN['items']):
        spans.append([it[4], panel[k], panel[k + 1], 'card'])
# ---- 5. recursos nuevos (30-10), cada uno un elemento de "extras" en la ficha ----------------------------------
# tinte {color: rojo|azul|verde} · tuit {nombre, usuario, texto con **clave**} · cortinilla {texto: 2-3 palabras, la
# última en dorado} · contador {texto, de} · marca {forma: circulo|flecha, x, y (0-1 de la pantalla), texto} ·
# congelado {texto} · detras {texto, color, y} · delante {file, ss, lado}. Todos llevan in y out.
e = html.escape
EXTRAS, XHTML, XTALK = [], [], []
for i, x in enumerate(F.get('extras', [])):
    t0, t1 = cue(x['in']), cue(x['out'])
    tipo = x['tipo']
    EXTRAS.append({**{k: v for k, v in x.items() if k in ('tipo', 'forma', 'color')}, 'in': t0, 'out': t1})
    pista = f'data-start="{t0}" data-duration="{round(t1 - t0, 3)}" data-media-start="0" data-track-index="{40 + i}" muted playsinline'
    if tipo == 'tinte':
        XHTML.append(f'<div class="tinte {x.get("color", "rojo")}" id="x-{i}"></div>')
    elif tipo == 'tuit':
        tx = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', e(x['texto']))
        XHTML.append(f'<div class="tuit" id="x-{i}"><div class="cab"><div class="av">{e(x["nombre"][:1])}</div><div><div class="nm">{e(x["nombre"])}</div>'
                     f'<div class="hn">{e(x["usuario"])}</div></div></div><div class="tx">{tx}</div></div>')
    elif tipo == 'cortinilla':
        ws = x['texto'].split()
        XHTML.append(f'<div class="cort" id="x-{i}"><div class="bd"></div><div class="ws">'
                     + ''.join(f'<span class="w{" k" if k == len(ws) - 1 else ""}">{e(w)}</span>' for k, w in enumerate(ws)) + '</div></div>')
    elif tipo == 'contador':
        XHTML.append(f'<div class="cont" id="x-{i}"><span class="n">{e(str(x["texto"]))}</span><span class="d">/{e(str(x["de"]))}</span></div>')
    elif tipo == 'marca':
        cx, cy = round(x['x'] * 1080), round(x['y'] * 1920)
        if x.get('forma', 'circulo') == 'circulo':
            r = x.get('r', 130)
            dib = f'<ellipse class="tr" pathLength="1" stroke-dasharray="1" cx="{cx}" cy="{cy}" rx="{r}" ry="{round(r * 0.8)}" transform="rotate(-8 {cx} {cy})"/>'
            ox, oy = cx, cy - r - 30
        else:   # la flecha llega en curva desde el lado con más sitio y se para antes del punto
            sx = -1 if cx > 540 else 1
            ox, oy = cx + sx * 300, cy - 300
            ex, ey = cx + sx * 45, cy - 45
            dib = (f'<path class="tr" pathLength="1" stroke-dasharray="1" d="M{ox} {oy} Q{cx + sx * 260} {cy - 40} {ex} {ey}"/>'
                   f'<path class="cb" d="M{ex - sx * 8} {ey + 8} L{ex + sx * 52} {ey - 18} L{ex + sx * 18} {ey - 52} Z"/>')
        if x.get('texto'):
            w_ = 50 + 36 * len(x['texto'])
            dib += (f'<rect class="cb" x="{ox - w_ // 2}" y="{oy - 100}" width="{w_}" height="86" rx="14"/>'
                    f'<text x="{ox}" y="{oy - 33}" text-anchor="middle">{e(x["texto"].upper())}</text>')
        XHTML.append(f'<svg class="marca" id="x-{i}" viewBox="0 0 1080 1920">{dib}</svg>')
    elif tipo == 'congelado':
        run('ffmpeg', '-v', 'error', '-y', '-ss', str(t0), '-i', str(P / 'assets/talk.mp4'), '-frames:v', '1', '-q:v', '2', str(P / f'assets/x-{i}.jpg'))
        XTALK.append(f'<img class="frz" id="xi-{i}" src="assets/x-{i}.jpg">')
        XHTML.append(f'<div class="flash" id="xf-{i}"></div>' + (f'<div class="frzt" id="x-{i}">{e(x["texto"])}</div>' if x.get('texto') else ''))
    elif tipo == 'detras':   # palabra gigante entre el fondo y tu silueta: va dentro del marco de la toma y sigue sus reencuadres
        run(str(PY_SILUETA), str(SCRIPTS / 'palabra_detras.py'), str(P / 'assets/talk.mp4'), str(t0), str(t1), x['texto'].upper(),
            str(P / f'assets/x-{i}.mp4'), x.get('color', '#E0B83C'), str(x.get('y', 430)))
        XTALK.append(f'<div class="tile" id="x-{i}"><video src="assets/x-{i}.mp4" {pista}></video></div>')
    elif tipo == 'delante':   # tú recortado delante del clip del que hablas
        run(str(PY_SILUETA), str(SCRIPTS / 'delante_del_clip.py'), str(P / 'assets/talk.mp4'), str(t0), str(t1), str(CONTENIDO / x['file']),
            str(P / f'assets/x-{i}.mp4'), x.get('lado', 'centro'), 'auto', str(x.get('ss', 0)))
        XHTML.append(f'<div class="tile" id="x-{i}" style="z-index:1"><video src="assets/x-{i}.mp4" {pista}></video></div>')
    else:
        raise KeyError(f'extra {i}: el tipo {tipo!r} no existe')

tiles = '\n'.join(
    f'  <div class="tile {c}" id="t-{k}"><video id="v-{k}" src="assets/broll/{k}.mp4" data-start="{t0}" data-duration="{round(t1 - t0, 3)}" '
    f'data-media-start="0" data-track-index="{2 + n}" muted playsinline></video></div>'
    for n, (k, t0, t1, c) in enumerate(spans))
PANEL_HTML = ''
if PN:
    PANEL_HTML = ('  <div id="panel">' + ''.join(f'<div class="hd"><div class="h1">{it[1]}</div><div class="h2">{it[2]}</div></div>' for it in PN['items'])
                  + '<div class="bl">' + ''.join(f'<div class="b"><i></i>{it[3]}</div>' for it in PN['items']) + '</div></div>')
TC, NU = F.get('tachado'), F.get('num')
s = s.replace('  <video id="talk" class="clip" data-om-id="talk" data-var-src="talk" data-start="0" data-track-index="0" muted playsinline></video>',
              '  <div id="talkwrap"><video id="talk" class="clip" data-om-id="talk" data-var-src="talk" data-start="0" data-track-index="0" muted playsinline></video>' + ''.join(XTALK) + '</div>\n'
              + PANEL_HTML + '\n' + tiles + '\n  ' + '\n  '.join(XHTML) + '\n  <div id="tops"></div>\n  <div id="subs"></div>\n'
              + (f'  <div id="num">{NU["texto"]}</div>\n' if NU else '')
              + (f'  <div id="tachado"><span>{TC["texto"]}<b></b></span></div>\n' if TC else '')
              + '  <div id="follow"><div class="av">FF</div><div><div class="nm">nutretufutbol</div><div class="hn">@nutretufutbol</div></div>'
              '<div class="bt b1">Seguir</div><div class="bt b2">Siguiendo</div></div>\n  <div id="leak"></div>')

# Reencuadres: un tamaño distinto en cada frase nueva (tras punto, coma larga o empalme), como sus cambios de cámara.
ESC = F.get('esc', [1.0, 1.15, 1.05, 1.22])
zoom, k, last = [[0, F.get('zoom0', 1.12)]], 1, 0
joins = [round(sum(b - a for a, b in KEEP[:n]), 3) for n in range(1, len(KEEP))]
for n, w in enumerate(words[1:], 1):
    prev = words[n - 1]
    gap = w['start'] - prev['end']
    nueva = re.search(r'[.,?!]$', prev['word']) or gap > 0.3 or any(abs(w['start'] - j) < 0.2 for j in joins)
    # 2,6 y no 3: salta en la palabra siguiente, y la puerta del plan no deja pasar más de 3 s sin un cambio.
    # Si whisper estira una palabra (un "lo..." de 2 s), la siguiente llega tarde: se cambia a mitad de palabra.
    while w['start'] - last > 3.0:
        last = round(last + 2.6, 3); zoom.append([last, ESC[k % len(ESC)]]); k += 1
    if (nueva and w['start'] - last >= 1.8) or w['start'] - last > 2.6:
        zoom.append([w['start'], ESC[k % len(ESC)]]); k += 1; last = w['start']
fol = cue(F['follow'])
plan = {
    'spans': spans, 'panel': panel, 'zoom': zoom,
    'byn': [cue(F['byn'][0]), cue(F['byn'][1]) + 0.1] if F.get('byn') else None,
    'leaks': [cue(c) for c in F.get('leaks', [])] + ([panel[0], panel[-1]] if panel else []),
    'num': [cue(NU['in']), cue(NU['out']) + 0.3] if NU else None,
    'tachado': [cue(TC['in']), cue(TC['raya']), cue(TC['out'])] if TC else None,
    'follow': [max(fol - 1.6, (panel[-1] + 0.15) if panel else 0), fol],
    'claves': [norm(x) for x in F.get('claves', [])], 'serif': [norm(x) for x in F.get('serif', [])],
    'tops': [[cue(t[0]), cue(t[1]), t[2], t[3], t[4]] for t in F.get('tops', [])],
    'extras': EXTRAS,
    'cortes': joins,   # empalmes de la toma: revisar_export.py busca clics y saltos en cada uno
}
JS = JS.replace('\\\\', '\\')   # en build.py el código va dentro de una cadena de Python: su doble barra es una sola en el HTML
# Lo que es opcional en una ficha se protege; la música la pone mezcla.py.
for a_, b_ in [
    ("  tl.set(tw, { filter: 'grayscale(1) contrast(1.1)' }, PLAN.byn[0]).set(tw, { filter: 'none' }, PLAN.byn[1]);",
     "  if (PLAN.byn) tl.set(tw, { filter: 'grayscale(1) contrast(1.1)' }, PLAN.byn[0]).set(tw, { filter: 'none' }, PLAN.byn[1]);"),
    ("  const [p0, p1, p2, p3] = PLAN.panel, pn = $id('panel');\n  tl.set(pn, { opacity: 1 }, p0).set(pn, { opacity: 0 }, p3);",
     "  const PN = PLAN.panel, pn = $id('panel');\n  if (PN.length) tl.set(pn, { opacity: 1 }, PN[0]).set(pn, { opacity: 0 }, PN[PN.length - 1]);"),
    ("  const hds = pn.querySelectorAll('.hd'), bls = pn.querySelectorAll('.b');\n  [p0, p1, p2].forEach((t, i) => {",
     "  const hds = pn ? pn.querySelectorAll('.hd') : [], bls = pn ? pn.querySelectorAll('.b') : [];\n  PN.slice(0, -1).forEach((t, i) => {"),
    ("    if (i < 2) tl.set(hds[i], { opacity: 0 }, [p1, p2][i]);", "    if (i < PN.length - 2) tl.set(hds[i], { opacity: 0 }, PN[i + 1]);"),
    ("  tl.fromTo(num, { opacity: 0, scale: 0.6 }", "  if (PLAN.num) tl.fromTo(num, { opacity: 0, scale: 0.6 }"),
    ("  OM.sfx('thud', PLAN.num[0] + 0.05, { gain: 0.5 });\n", ""),
    ("  tl.fromTo(tc, { opacity: 0, y: 20 }", "  if (PLAN.tachado) tl.fromTo(tc, { opacity: 0, y: 20 }"),
    ("  const ventanas = [[PLAN.tachado[0], PLAN.tachado[2]], [PLAN.num[0], PLAN.num[1]], [p0, p3]];",
     "  const ventanas = [PLAN.tachado && [PLAN.tachado[0], PLAN.tachado[2]], PLAN.num, PN.length && [PN[0], PN[PN.length - 1]],\n"
     "    ...PLAN.extras.filter((x) => ['tuit', 'cortinilla'].includes(x.tipo)).map((x) => [x.in, x.out])].filter(Boolean);"),
    ("  OM.music({ style: 'cinematic', drop: PLAN.num[0], ending: 'button' });\n", ""),
]:
    assert a_ in JS, a_[:60]
    JS = JS.replace(a_, b_)
JS = re.sub(r"\n\s*OM\.sfx\([^\n]*", '', JS)   # los efectos van en mezcla.py
JS = JS.replace('__PLAN__', json.dumps(plan, ensure_ascii=False))
s = s.replace("  tl.set({}, {}, LEN);                                            // the film is as long as the talk",
              JS + "\n  OM.music({ off: true });\n  tl.set({}, {}, LEN);                                            // the film is as long as the talk")
(P / 'index.html').write_text(s, encoding='utf-8')
json.dump(plan, open(P / 'plan.json', 'w', encoding='utf-8'), ensure_ascii=False)
# La plantilla carga assets/sound.wav; con la música apagada no se genera, así que se deja uno en silencio.
run('ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', str(LEN), str(P / 'assets/sound.wav'))
print('LEN', LEN, '| palabras', len(words), '| zoom', len(zoom), '| b-roll', len(spans))
