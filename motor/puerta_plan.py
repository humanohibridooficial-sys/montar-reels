# Puerta del plan: se pasa antes del render y lo para si el montaje va a aburrir o a repetir los últimos reels.
# Sustituye a revisar_plan.py. Copiada de la "plan gate" de ChatMonteur, con el listón de mi-estilo/recursos.md.
#   python puerta_plan.py <n> [--anotar]   (sale con 1 si falla; --anotar guarda la pieza en usados.json si pasa)
import json, re, sys, datetime
from rutas import RENDER, DATOS

HUECO = 3.0          # recursos.md: nunca más de ~3 s en el mismo encuadre sin un cambio
USADOS = DATOS / 'usados.json'
N = sys.argv[1]
P = RENDER / f'p{N}'
p = json.load(open(P / 'plan.json', encoding='utf-8'))
words = json.load(open(P / 'assets/voice.words.json', encoding='utf-8'))
LEN = words['duration']
norm = lambda x: re.sub(r'[^\wáéíóúüñ]', '', x.lower())


def eventos():
    """(segundo, tipo) de todo lo que cambia en pantalla."""
    ev = [(t, 'zoom') for t, _ in p['zoom']]
    ev += [(t0, c or 'broll') for _, t0, _, c in p['spans']]
    ev += [(t[0], 'titular') for t in p['tops']]
    ev += [(t, 'destello') for t in p['leaks']]
    ev += [(t, 'panel') for t in p['panel']]
    ev += [(p['byn'][0], 'byn')] if p['byn'] else []
    ev += [(p['num'][0], 'cifra')] if p['num'] else []
    ev += [(p['tachado'][0], 'tachado')] if p['tachado'] else []
    ev += [(p['follow'][0], 'seguir')]
    ev += [(x['in'], x['tipo']) for x in p.get('extras', [])]
    ev += [(w['start'], 'clave') for w in words['words'] if norm(w['word']) in p['claves']]
    return sorted(ev)


fallos = []
ev = eventos()
ts = [0.0] + [t for t, _ in ev] + [LEN]
for a, b in zip(ts, ts[1:]):
    if b - a > HUECO:
        fallos.append(f'{a:.1f}-{b:.1f} s: {b - a:.1f} s sin ningún cambio en pantalla')
if not any(t[0] == 0 for t in p['tops']):
    fallos.append('0 s: el fotograma 0 no tiene titular de gancho')
# Duraciones (lo que comprobaba revisar_plan.py)
for k, a, b, c in p['spans']:
    if not 0.8 < b - a < 8: fallos.append(f'{a:.1f} s: b-roll {k} dura {b - a:.1f} s (0,8-8)')
for t in p['tops']:
    if not 0.8 < t[1] - t[0] < 9: fallos.append(f'{t[0]:.1f} s: titular "{t[2]}" dura {t[1] - t[0]:.1f} s (0,8-9)')
if p['byn'] and not 0.8 < p['byn'][1] - p['byn'][0] < 8: fallos.append(f"{p['byn'][0]:.1f} s: blanco y negro de {p['byn'][1] - p['byn'][0]:.1f} s")
if p['tachado'] and not p['tachado'][0] < p['tachado'][1] < p['tachado'][2]: fallos.append(f"{p['tachado'][0]:.1f} s: tachado desordenado")
if p['panel'] and p['panel'] != sorted(p['panel']): fallos.append('panel desordenado')
# Dos cosas en la franja de arriba a la vez se pisan: el titular, el tuit y el contador comparten sitio.
for x in p.get('extras', []):
    if x['tipo'] in ('tuit', 'contador'):
        for t in p['tops']:
            if x['in'] < t[1] and t[0] < x['out']:
                fallos.append(f"{max(x['in'], t[0]):.1f} s: el {x['tipo']} se pisa con el titular \"{t[2]}\"")
# Un rótulo que dice una palabra de la voz entra con ella (revisor 30-10: cuatro entraban 0,4-1,2 s antes).
habladas = [(norm(w['word']), w['start']) for w in words['words']]
for x in p.get('extras', []):
    if x['tipo'] == 'congelado' and x['out'] - x['in'] > 1.0:
        fallos.append(f"{x['in']:.1f} s: congelado de {x['out'] - x['in']:.1f} s; con más de 1 s el labio deja de ir con la voz")
    if x['tipo'] == 'tuit':   # el tuit cita a otro: su texto no se dice en voz alta
        continue
    for pal in [norm(t) for t in str(x.get('texto', '')).split()][:3]:
        cerca = [t for w, t in habladas if w == pal and x['in'] - 1.5 < t < x['out']]
        if cerca:
            d = min(cerca, key=lambda t: abs(t - x['in'])) - x['in']
            if abs(d) > 0.25:
                fallos.append(f"{x['in']:.1f} s: {x['tipo']} \"{x['texto']}\" entra {abs(d):.1f} s {'antes' if d > 0 else 'después'} de \"{pal}\"")
            break
for x in p.get('extras', []):
    if not 0.4 < x['out'] - x['in'] < 9: fallos.append(f"{x['in']:.1f} s: {x['tipo']} dura {x['out'] - x['in']:.1f} s (0,4-9)")

# Variedad: "no sota, caballo y rey" (10-10). Falla si gancho y juego de recursos calcan una de las 3 últimas.
gancho = sorted({tipo for t, tipo in ev if t < 2.0 and tipo not in ('zoom', 'clave')})
recursos = sorted({tipo for _, tipo in ev if tipo not in ('zoom', 'clave', 'seguir')})
usados = json.load(open(USADOS, encoding='utf-8')) if USADOS.exists() else []
for u in [u for u in usados if u['pieza'] != N][-3:]:
    r = set(u['recursos'])
    jac = len(r & set(recursos)) / max(1, len(r | set(recursos)))
    if u['gancho'] == gancho and jac >= 0.9:
        fallos.append(f"igual que la pieza {u['pieza']}: mismo gancho ({', '.join(gancho)}) y {jac:.0%} de los recursos")

print(N, 'OK' if not fallos else 'FALLA', f'| {len(ev)} eventos en {LEN:.1f} s | gancho: {", ".join(gancho)} | recursos: {", ".join(recursos)}')
for f in fallos:
    print('  -', f)
if not fallos and '--anotar' in sys.argv:
    usados = [u for u in usados if u['pieza'] != N] + [
        {'pieza': N, 'fecha': datetime.date.today().isoformat(), 'gancho': gancho, 'recursos': recursos}]
    json.dump(usados, open(USADOS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sys.exit(1 if fallos else 0)
