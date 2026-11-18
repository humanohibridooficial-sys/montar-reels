# Acabado final de un reel ya montado (17-11, Luismi: "que se vean una pasada").
# Sobre pN-final.mp4: color común de marca (contraste y saturación algo arriba, sombras frías y luces cálidas,
# como el marino y el dorado), nitidez suave, viñeta y grano fino; acelerón opcional sin cambiar el tono de voz;
# limitador para que el pico no pase de -1 dBTP. Mide sonoridad y pico y copia el resultado a su carpeta de entrega.
#   python acabado.py <n> [velocidad=1.0] [--sin-color]
import json, re, subprocess, sys, unicodedata
import rutas

N = sys.argv[1]
VEL = float(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 1.0
COLOR = '--sin-color' not in sys.argv
P = rutas.RENDER / f'p{N}' / 'out'
ENTRA, SALE = P / f'p{N}-final.mp4', P / f'p{N}-acabado.mp4'

GRADO = ('eq=contrast=1.07:saturation=1.10:gamma=0.97,'
         'colorbalance=rs=-0.03:gs=-0.01:bs=0.04:rh=0.03:gh=0.015:bh=-0.02,'
         'unsharp=5:5:0.35:5:5:0,vignette=angle=PI/6,noise=alls=3:allf=t')
v = [f'setpts=PTS/{VEL}'] if VEL != 1.0 else []
if COLOR:
    v.append(GRADO)
a = ([f'atempo={VEL}'] if VEL != 1.0 else []) + ['alimiter=limit=0.8:level=false']
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(ENTRA), '-filter_complex',
                f"[0:v]{','.join(v) or 'null'},format=yuv420p[v];[0:a]{','.join(a)}[a]",
                '-map', '[v]', '-map', '[a]', '-r', '30', '-c:v', 'libx264', '-crf', '17', '-preset', 'slow',
                '-c:a', 'aac', '-b:a', '192k', str(SALE)], check=True)

err = subprocess.run(['ffmpeg', '-nostats', '-i', str(SALE), '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                     capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
lufs = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', err)[-1])
pico = float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', err)[-1])
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(SALE)],
                           capture_output=True, text=True).stdout)
ok = -17.0 <= lufs <= -15.0 and pico <= -1.0
print(f'{N} acabado {"OK" if ok else "FALLO"} | {dur:.2f} s | {lufs} LUFS | pico {pico} | velocidad {VEL} | color {COLOR}')
if not ok:
    sys.exit(1)

t = json.load(open(rutas.FICHAS / f'{N}.json', encoding='utf-8'))['titulo']
slug = re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()).strip('-')
F = subprocess.run([sys.executable, 'destino.py', str(rutas.SALIDA), N, slug], capture_output=True, text=True,
                   encoding='utf-8').stdout.strip()
import shutil
shutil.copy(SALE, F)
print('entregado ->', F)
