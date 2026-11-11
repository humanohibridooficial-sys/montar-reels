# Sonido estilo ejemplos (Carla y los otros tres): música real de fondo continuo, ~10 dB bajo la voz y apartándose
# cuando hablas, y un efecto en cada cosa que pasa en pantalla. Sustituye el audio de Huashu en el render.
# Uso: python mezcla.py <n> render.mp4 final.mp4   (la ficha puede fijar musica, musicaDesde y fondoDb)
import json, subprocess, sys, pathlib

from rutas import FICHAS, RENDER, REUTILIZABLES
N = sys.argv[1]; sys.argv = sys.argv[1:]
P = RENDER / f'p{N}'
F = json.load(open(FICHAS / f'{N}.json', encoding='utf-8'))
LIB = REUTILIZABLES
MUSICA = LIB / 'MUSICA' / F.get('musica', 'PX-the_mountain-football-556097.mp3')
MUSICA_DESDE = F.get('musicaDesde', 0.0)
FONDO_DB = F.get('fondoDb', -15)  # 29-10 Luismi: todo sonaba muy alto
SFX_BAJA = F.get('sfxBaja', 10)  # 30-10 Luismi: "música sí o sí, efectos de sonido solo como matiz" (antes 4; sin tic en cada reencuadre ni titular)
# 04-11 Luismi (reel 86): "más efectos que enganchen". La ficha puede subirlos (sfxBaja), poner un golpe en cada palabra
# dorada (golpeClaves) y una subida antes de la tarjeta de Seguir (riserCta). Sin esas claves, todo como antes.
plan = json.load(open(P / 'plan.json', encoding='utf-8'))
LEN = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(P / 'assets/voice.wav')],
                           capture_output=True, text=True).stdout)

# (fichero, segundo, ganancia dB): todo cuadrado a un evento visual del montaje
E = []
E += [('SFX-P-subida.wav', 0.0, -8)]                                                        # arranca con el gancho
E += [('SFX-P-barrido.wav', t0 - 0.12, -6) for k, t0, t1, c in plan['spans'] if c != 'card']  # entra cada b-roll
E += [('SFX-P-latido.wav', plan['byn'][0], -4)] if plan['byn'] else []                       # blanco y negro: tensión
E += [('SFX-brillo.wav', t - 0.2, -6) for t in plan['leaks']]                                # destellos
E += [('SFX-P-golpe.wav', plan['tachado'][1], -5)] if plan['tachado'] else []                # cae la raya roja
E += [('SFX-boom.wav', plan['num'][0], -5)] if plan['num'] else []                           # la cifra gigante
E += [('SFX-P-tic.wav', t + 0.1, -8) for t in plan['panel'][:-1]]                            # cada punto de la lista
E += [('SFX-P-cierre.wav', plan['follow'][1], -5)]                                           # pulsa Seguir
if F.get('golpeClaves'):   # la palabra dorada cae con un golpe (la primera vez que suena cada clave)
    import re
    norm = lambda x: re.sub(r'[^\wáéíóúüñ]', '', x.lower())
    vistas = set()
    for w in json.load(open(P / 'assets/voice.words.json', encoding='utf-8'))['words']:
        k = norm(w['word'])
        if k in plan['claves'] and k not in vistas:
            vistas.add(k); E.append(('SFX-P-golpe.wav', w['start'], F.get('golpeDb', {}).get(k, -6)))   # golpeDb: {"palabra": dB}
if F.get('riserCta'):
    E.append(('SFX-riser.wav', max(plan['follow'][0] - 1.0, 0), -6))                        # sube hacia el CTA
SFX_EXTRA = {   # recursos del 30-10: (fichero, desfase, dB)
    'tinte': ('SFX-P-golpe-grave.wav', 0.0, -7), 'tuit': ('SFX-pop.wav', 0.0, -6), 'cortinilla': ('SFX-whoosh.wav', -0.1, -4),
    'contador': ('SFX-P-tic.wav', 0.0, -6), 'marca': ('SFX-tic.wav', 0.05, -8), 'congelado': ('SFX-P-absorcion.wav', 0.0, -4),
    'detras': ('SFX-boom.wav', 0.0, -9), 'pizarra': ('SFX-whoosh.wav', -0.05, -6), 'barrido': ('SFX-P-barrido.wav', -0.08, -5),
    'logo': ('SFX-brillo.wav', 0.0, -4), 'marcador': ('SFX-P-tic.wav', 0.0, -6)}
SFX_PUNTO = {'lista': ('SFX-P-tic.wav', -8), 'pildora': ('SFX-pop.wav', -8), 'pizarra': ('SFX-pop.wav', -12), 'mapa': ('SFX-tic.wav', -8),
             'tarjetas': ('SFX-P-barrido.wav', -9), 'marcador': ('SFX-P-golpe.wav', -6)}   # uno por cada punto, palabra, jugador o tarjeta
E += [(SFX_EXTRA[x['tipo']][0], x['in'] + SFX_EXTRA[x['tipo']][1], SFX_EXTRA[x['tipo']][2]) for x in plan.get('extras', []) if x['tipo'] in SFX_EXTRA and x.get('color') != 'velo']   # el velo no es un evento
E += [(SFX_PUNTO[x['tipo']][0], t, SFX_PUNTO[x['tipo']][1]) for x in plan.get('extras', []) if x['tipo'] in SFX_PUNTO for t in x.get('items', [])]
# 11-11: las transiciones del pack suenan con un whoosh que llega a tope en el corte; los overlays y elementos, callados
E += [('SFX-whoosh.wav', x['en'] - 0.15, -8) for x in plan.get('pack', []) if x['tipo'] == 'transicion']
E = sorted(E, key=lambda e: e[1])
# un tic que coincide con otro efecto sobra: suena doble
E = [e for i, e in enumerate(E) if not (e[0] == 'SFX-P-tic.wav' and any(abs(e[1] - x[1]) < 0.25 for j, x in enumerate(E) if j != i and (x[0] != 'SFX-P-tic.wav' or j < i)))]
# 10-11 Luismi (reel 92): también suenan los titulares y los punch de la ficha (sonidos del pack 2.0, SFX-V-*).
# Se apagan con sfxTitular / sfxPunch: false. Los reencuadres van callados salvo sfxReencuadre: true (revisor 92: un
# reencuadre es un corte invisible; si suena, delata el truco). Nunca dos efectos a menos de 0,25 s: los de antes ganan
# siempre, y entre los nuevos, titular > punch > reencuadre. (segundo del golpe, fichero, desfase hasta el golpe, dB)
NUEVOS = []
if F.get('sfxTitular', True):
    NUEVOS += [(t[0], 'SFX-V-titular.wav', -0.23, -9) for t in plan['tops']]
if F.get('sfxPunch', True):
    # ni punch pegado a la subida de la tarjeta de Seguir (revisor 92: el de 37,8 s se comía el riser)
    NUEVOS += [(t, 'SFX-V-punch.wav', 0.0, -8) for t in plan.get('punch', []) if t < plan['follow'][0] - 1.0 - 1.5]
if F.get('sfxReencuadre', False):
    NUEVOS += [(t, 'SFX-V-reencuadre.wav', -0.31, -15) for t in plan.get('reencuadres', [])]
# Ningún efecto tapa la voz (revisor 92): si en su golpe y su cola (-0,1 a +0,3 s del golpe real del sonido) hay voz,
# baja SOLO lo necesario para quedar MARGEN dB por debajo de ella en esa ventana; si ya tiene ese margen, no se toca.
# Los nuevos (titular, punch) y el cierre de la tarjeta antes se adelantan, si pueden, a la respiración anterior (hasta 0,3 s).
# La subida del gancho y los de cada punto (pop, tic) marcan una palabra y no se mueven. El golpe y el barrido no entran.
import numpy as np
def _pcm(path):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', '1', '-ar', '8000', '-f', 's16le', '-'],
                                        capture_output=True).stdout, np.int16).astype(np.float32) / 32768
_v = _pcm(P / 'assets/voice.wav')
_db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9) if len(x) else -120.0
def _voz(a, b):   # dB RMS de la voz entre a y b
    return _db(_v[max(0, int(a * 8000)):max(0, int(b * 8000))])
VOZ_HAY, MARGEN = -38, 8   # dB RMS: por encima, está hablando; dB que el efecto queda bajo la voz
_SON = {}
def _son(f):   # (segundo del golpe dentro del fichero, dB RMS del golpe y su cola a ganancia 0)
    if f not in _SON:
        a = _pcm(LIB / f); k = int(np.argmax(np.abs(a))) if len(a) else 0
        _SON[f] = (k / 8000, float(_db(a[max(0, k - 800):k + 2400])))
    return _SON[f]
def _sin_tapar(f, inicio, g, mover):
    pk, nivel = _son(f)
    if mover:
        hueco = next((s for s in np.arange(0, 0.301, 0.05) if _voz(inicio + pk - s - 0.1, inicio + pk - s + 0.3) < VOZ_HAY), None)
        if hueco is not None:
            return (f, inicio - hueco, g)
    voz = _voz(inicio + pk - 0.1, inicio + pk + 0.3)
    if voz < VOZ_HAY:
        return (f, inicio, g)
    return (f, inicio, round(float(min(g, g + (voz - MARGEN) - (nivel + g - SFX_BAJA))), 1))
for t, f, d, g in NUEVOS:   # ya van en orden de importancia
    if all(abs(t - x[1]) >= 0.25 for x in E):
        E.append(_sin_tapar(f, t + d, g, True))
MOVIBLES = {'SFX-P-cierre.wav'}
FIJOS = {'SFX-P-subida.wav', 'SFX-pop.wav', 'SFX-tic.wav', 'SFX-P-tic.wav'}
E = [_sin_tapar(f, t, g, f in MOVIBLES) if f in MOVIBLES | FIJOS else (f, t, g) for f, t, g in E]
E = sorted(E, key=lambda e: e[1])

ins = ['-i', sys.argv[1], '-i', str(P / 'assets/voice.wav'), '-ss', str(MUSICA_DESDE), '-i', str(MUSICA)]
for f, _, _ in E:
    ins += ['-i', str(LIB / f)]
byn = plan['byn'] or [-1, -1]
fc = [
    # música: normalizada, EQ que le quita medios donde vive la voz, ahogada en el blanco y negro, fundido al final
    f'[2:a]atrim=0:{LEN},asetpts=PTS-STARTPTS,loudnorm=I=-14:TP=-2,volume={FONDO_DB}dB,'
    f'equalizer=f=1200:t=o:w=1.4:g=-5,equalizer=f=3000:t=o:w=1.2:g=-3,'
    f"lowpass=f=700:enable='between(t,{byn[0]},{byn[1]})',afade=t=out:st={LEN - 0.8}:d=0.8[mus]",
    '[1:a]asplit=2[voz][sc]',
    '[mus][sc]sidechaincompress=threshold=0.04:ratio=3:attack=20:release=350:makeup=1[musd]',
]
for i, (f, t, g) in enumerate(E):
    fc.append(f'[{3 + i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g - SFX_BAJA}dB,adelay={int(max(t, 0) * 1000)}:all=1[e{i}]')
fc.append('[voz][musd]' + ''.join(f'[e{i}]' for i in range(len(E))) + f'amix=inputs={2 + len(E)}:normalize=0:duration=first,'
          'loudnorm=I=-16:TP=-2:LRA=9[out]')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[out]',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', str(LEN), sys.argv[2]], check=True)
print(len(E), 'efectos:', ', '.join(f'{f[4:-4]}@{t:.1f}' for f, t, _ in E))
