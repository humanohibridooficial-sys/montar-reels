# Pinta los recursos del PACK DE RECURSOS 2.0 sobre el render (spec 2026-11-11-recursos-pack-y-broll-infinito).
# Va entre el render de Huashu y mezcla.py, con ffmpeg: los overlays y transiciones del pack son vídeo con fondo negro
# y se funden en RGB (screen / overlay / addition); los elementos con alfa (PNG, ProRes 4444, gif) van encima en su caja.
#   python capas.py <n> render.mp4 salida.mp4      (sin "pack" en plan.json, copia el render tal cual)
import json, shutil, subprocess, sys

from rutas import RENDER

N, ENTRA, SALE = sys.argv[1:4]
P = RENDER / f'p{N}'
plan = json.load(open(P / 'plan.json', encoding='utf-8'))
CAPAS = plan.get('pack') or []
if not CAPAS:
    shutil.copy(ENTRA, SALE); print('sin capas del pack'); sys.exit(0)

ins, fc, base = ['-i', ENTRA], [], '[0:v]'
fc.append('[0:v]format=gbrp[b0]'); base = '[b0]'
for k, c in enumerate(CAPAS, 1):
    t0, t1 = c['in'], c['out']
    dur = round(t1 - t0 + 0.1, 3)
    if c.get('estatico'):
        ins += ['-loop', '1', '-t', str(dur), '-i', c['file']]
    else:   # un overlay más corto que su tramo vuelve a empezar
        ins += ['-stream_loop', '-1', '-ss', str(c.get('desde', 0)), '-t', str(dur), '-i', c['file']]
    entre = f"enable='between(t,{t0},{t1})'"
    if c['modo'] == 'alfa':
        x0, y0 = c['caja'][0], c['caja'][1]
        fc.append(f"[{k}:v]fps=30,scale={c['ancho']}:-2,format=rgba,colorchannelmixer=aa={c['opacidad']},"
                  f"tpad=start_duration={t0}:color=black@0,fade=t=in:st={t0}:d=0.12:alpha=1,fade=t=out:st={round(t1 - 0.12, 3)}:d=0.12:alpha=1[l{k}]")
        fc.append(f"{base}[l{k}]overlay=x={x0}:y={y0}:format=gbrp:eof_action=pass:{entre}[b{k}]")
    else:
        # a pantalla completa como el b-roll (cubre y recorta al centro); en screen el negro no cambia nada, y los
        # fundidos van a negro para que la capa no entre de golpe (el grano, en modo overlay, entra sin fundido)
        fd = '' if c['modo'] == 'overlay' else (f",fade=t=in:st={t0}:d={min(0.15, (t1 - t0) / 4):.3f}"
                                                 f",fade=t=out:st={round(t1 - min(0.15, (t1 - t0) / 4), 3)}:d={min(0.15, (t1 - t0) / 4):.3f}")
        fc.append(f"[{k}:v]fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=gbrp,"
                  f"tpad=start_duration={t0}:color=black{fd}[l{k}]")
        fc.append(f"{base}[l{k}]blend=all_mode={ {'screen': 'screen', 'overlay': 'overlay', 'suma': 'addition'}.get(c['modo'], c['modo']) }"
                  f":all_opacity={c['opacidad']}:shortest=0:repeatlast=0:{entre}[b{k}]")
    base = f'[b{k}]'
fc.append(f'{base}format=yuv420p[v]')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '0:a?',
                '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'copy', SALE], check=True)
print(len(CAPAS), 'capas del pack:', ', '.join(f"{c['tipo']} {c['nombre']}@{c['in']:.1f}" for c in CAPAS))
