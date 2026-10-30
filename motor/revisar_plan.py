# Avisa de tramos al revés o demasiado cortos/largos en el plan de una pieza
import json, sys
from rutas import RENDER
for n in sys.argv[1:]:
    p = json.load(open(RENDER / f'p{n}/plan.json', encoding='utf-8'))
    bad = []
    for k, a, b, c in p['spans']:
        if not 0.8 < b - a < 8: bad.append(('span', k, a, b))
    for t in p['tops']:
        if not 0.8 < t[1] - t[0] < 9: bad.append(('top', t[2], t[0], t[1]))
    if p['byn'] and not 0.8 < p['byn'][1] - p['byn'][0] < 8: bad.append(('byn', *p['byn']))
    if p['tachado'] and not p['tachado'][0] < p['tachado'][1] < p['tachado'][2]: bad.append(('tachado', *p['tachado']))
    if p['panel'] and p['panel'] != sorted(p['panel']): bad.append(('panel', p['panel']))
    print(n, 'OK' if not bad else bad, '| panel', p['panel'], '| follow', p['follow'])
