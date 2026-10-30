# Revisión del fichero final: mide lo que se ve y se oye en el mp4 ya mezclado y dice "ok" o "fallo" con el segundo.
# Copiada de la "file gate" de ChatMonteur (negro, silencio, saturación, duración) y de la autoevaluación por corte
# de video-use (cada empalme, mirado y escuchado). Deja out/qc.json y out/hoja.jpg para el agente revisor-montaje.
#   python revisar_export.py <n> <final.mp4>     (sale con 1 si falla)
import json, re, shutil, subprocess, sys, wave
import numpy as np
from rutas import RENDER

N, MP4 = sys.argv[1], sys.argv[2]
P = RENDER / f'p{N}'
plan = json.load(open(P / 'plan.json', encoding='utf-8'))
LEN = json.load(open(P / 'assets/voice.words.json', encoding='utf-8'))['duration']
LUFS, PICO = (-17.0, -15.0), -1.0   # la mezcla apunta a -16 (Luismi 29-10: "todo sonaba muy alto")
fallos, medidas = [], {}


def ff(*a):
    return subprocess.run(['ffmpeg', '-hide_banner', '-nostats', *a], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr


# 1. Duración: el vídeo dura lo que la voz.
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', MP4],
                           capture_output=True, text=True).stdout)
medidas['duracion'] = round(dur, 2)
if abs(dur - LEN) > 0.1:
    fallos.append({'s': round(min(dur, LEN), 1), 'que': f'dura {dur:.2f} s y la voz {LEN:.2f} s'})

# 2. Fotogramas negros (un tile que no cargó, un corte vacío).
for a, b in re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', ff('-i', MP4, '-vf', 'blackdetect=d=0.08:pix_th=0.10', '-an', '-f', 'null', '-')):
    fallos.append({'s': round(float(a), 1), 'que': f'negro de {float(b) - float(a):.2f} s'})

# 3. Sonoridad y pico de la mezcla.
s = ff('-i', MP4, '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-').split('Summary:')[-1]
lufs, tp = float(re.search(r'I:\s+(-?[\d.]+) LUFS', s).group(1)), float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', s).group(1))
medidas.update(lufs=lufs, pico=tp)
if not LUFS[0] <= lufs <= LUFS[1]:
    fallos.append({'s': 0, 'que': f'sonoridad {lufs} LUFS (va entre {LUFS[0]} y {LUFS[1]})'})
if tp > PICO:
    fallos.append({'s': 0, 'que': f'pico {tp} dBTP (máximo {PICO}): satura'})

# 4. Silencios: en la voz, pausas que el recorte no quitó; en la mezcla, que falte la música.
for pista, umbral, d, que in [(str(P / 'assets/voice.wav'), -38, 0.6, 'pausa sin cortar en la voz'), (MP4, -45, 0.4, 'silencio en la mezcla')]:
    for a, b in re.findall(r'silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)', ff('-i', pista, '-vn', '-af', f'silencedetect=noise={umbral}dB:d={d}', '-f', 'null', '-')):
        if float(a) < LEN - 0.8:   # el final de la voz, tras el "sígueme", no cuenta
            fallos.append({'s': round(float(a), 1), 'que': f'{que} de {float(b) - float(a):.2f} s'})

# 5. Cada empalme: un clic es un salto brusco de la señal. El mayor salto entre muestras en los 5 ms del empalme frente
#    al pico normal (percentil 99) de los 200 ms de alrededor sin contarlo; más de 12 dB por encima, se oye.
with wave.open(str(P / 'assets/voice.wav')) as w:
    sr, ch = w.getframerate(), w.getnchannels()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, ch).mean(axis=1) / 32768
d = np.abs(np.diff(x))
clics = []
for j in plan.get('cortes', []):
    c, v = int(j * sr), sr // 400
    zona = np.concatenate([d[max(0, c - sr // 10):max(0, c - v)], d[c + v:c + sr // 10]])
    db = 20 * np.log10(d[max(0, c - v):c + v].max(initial=0) / (np.percentile(zona, 99) + 1e-6) + 1e-9)
    clics.append(round(float(db), 1))
    if db > 12:
        fallos.append({'s': round(j, 2), 'que': f'clic en el empalme ({db:.0f} dB sobre la voz de alrededor)'})
medidas['empalmes'] = len(clics)
medidas['clic_max_db'] = max(clics, default=None)

# 6. Hoja de fotogramas: 10/35/65/90 % (la muestra de ChatMonteur) y antes/después de cada empalme (la de video-use).
H = P / 'out/hoja'
shutil.rmtree(H, ignore_errors=True); H.mkdir(parents=True)
shutil.copy(P / 'assets/fonts/Inter-Variable.ttf' if (P / 'assets/fonts/Inter-Variable.ttf').exists() else next((P / 'assets/fonts').glob('Inter*')), H / 'f.ttf')
tomas = [(round(LEN * q, 2), f'al {int(q * 100)} pc') for q in (0.10, 0.35, 0.65, 0.90)]
for j in plan.get('cortes', []):
    tomas += [(max(0, round(j - 0.1, 2)), f'empalme {j:.1f} antes'), (round(j + 0.1, 2), f'empalme {j:.1f} despues')]
for i, (t, rot) in enumerate(tomas):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', MP4, '-frames:v', '1',
                    '-vf', f"scale=270:480,drawtext=fontfile=f.ttf:text='{t:.1f} s {rot}':x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6",
                    f'{i:03d}.jpg'], cwd=H, check=True, stderr=subprocess.DEVNULL)   # fontconfig avisa en Windows aunque funcione
cols = 6
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', '%03d.jpg', '-vf', f'tile={cols}x{-(-len(tomas) // cols)}:padding=4', 'hoja.jpg'], cwd=H, check=True)
shutil.move(str(H / 'hoja.jpg'), str(P / 'out/hoja.jpg'))
shutil.rmtree(H)

qc = {'pieza': N, 'fichero': MP4, 'veredicto': 'fallo' if fallos else 'ok', 'medidas': medidas,
      'fallos': sorted(fallos, key=lambda f: f['s']), 'hoja': str(P / 'out/hoja.jpg')}
json.dump(qc, open(P / 'out/qc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(N, qc['veredicto'].upper(), f"| {dur:.2f} s | {lufs} LUFS | pico {tp} | {medidas['empalmes']} empalmes")
for f in qc['fallos']:
    print(f"  - {f['s']} s: {f['que']}")
sys.exit(1 if fallos else 0)
