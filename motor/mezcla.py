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
plan = json.load(open(P / 'plan.json', encoding='utf-8'))
LEN = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(P / 'assets/voice.wav')],
                           capture_output=True, text=True).stdout)

zoom = [t for t, _ in plan['zoom']][1:]
# (fichero, segundo, ganancia dB): todo cuadrado a un evento visual del montaje
E = []
E += [('SFX-P-subida.wav', 0.0, -8)]                                                        # arranca con el gancho
E += [('SFX-P-barrido.wav', t0 - 0.12, -6) for k, t0, t1, c in plan['spans'] if c != 'card']  # entra cada b-roll
E += [('SFX-P-tic.wav', t, -14) for t in zoom if not any(abs(t - x) < 0.3 for x in plan['leaks'] + (plan['num'] or [])[:1])]  # cambios de plano
E += [('SFX-P-latido.wav', plan['byn'][0], -4)] if plan['byn'] else []                       # blanco y negro: tensión
E += [('SFX-brillo.wav', t - 0.2, -6) for t in plan['leaks']]                                # destellos
E += [('SFX-P-golpe.wav', plan['tachado'][1], -5)] if plan['tachado'] else []                # cae la raya roja
E += [('SFX-boom.wav', plan['num'][0], -5)] if plan['num'] else []                           # la cifra gigante
E += [('SFX-P-tic.wav', t + 0.1, -8) for t in plan['panel'][:-1]]                            # cada punto de la lista
E += [('SFX-P-tic.wav', t[0], -10) for t in plan['tops'][1:]]                                # titular nuevo arriba
E += [('SFX-P-cierre.wav', plan['follow'][1], -5)]                                           # pulsa Seguir
SFX_EXTRA = {   # recursos del 30-10: (fichero, desfase, dB)
    'tinte': ('SFX-P-golpe-grave.wav', 0.0, -7), 'tuit': ('SFX-pop.wav', 0.0, -6), 'cortinilla': ('SFX-whoosh.wav', -0.1, -4),
    'contador': ('SFX-P-tic.wav', 0.0, -6), 'marca': ('SFX-tic.wav', 0.05, -8), 'congelado': ('SFX-P-absorcion.wav', 0.0, -4),
    'detras': ('SFX-boom.wav', 0.0, -9), 'delante': ('SFX-P-barrido.wav', -0.12, -6)}
E += [(SFX_EXTRA[x['tipo']][0], x['in'] + SFX_EXTRA[x['tipo']][1], SFX_EXTRA[x['tipo']][2]) for x in plan.get('extras', [])]
E = sorted(E, key=lambda e: e[1])
# un tic que coincide con otro efecto sobra: suena doble
E = [e for i, e in enumerate(E) if not (e[0] == 'SFX-P-tic.wav' and any(abs(e[1] - x[1]) < 0.25 for j, x in enumerate(E) if j != i and (x[0] != 'SFX-P-tic.wav' or j < i)))]

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
    fc.append(f'[{3 + i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g - 4}dB,adelay={int(max(t, 0) * 1000)}:all=1[e{i}]')
fc.append('[voz][musd]' + ''.join(f'[e{i}]' for i in range(len(E))) + f'amix=inputs={2 + len(E)}:normalize=0:duration=first,'
          'loudnorm=I=-16:TP=-2:LRA=9[out]')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[out]',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', str(LEN), sys.argv[2]], check=True)
print(len(E), 'efectos:', ', '.join(f'{f[4:-4]}@{t:.1f}' for f, t, _ in E))
