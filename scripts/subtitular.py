# Vídeo FINAL sin CapCut: aplica el corte (tramos.json) y quema los subtítulos con ffmpeg, en 9:16.
#   python subtitular.py <toma-limpia.mp4> [--clave "70,calidad,fuerza"] [--y 1180] [--salida final.mp4]
# Estilo medido (tanda 0710): MAYÚSCULAS, blanco con borde negro, palabra clave en color (config "color_clave"),
# bloques de 1 a 3 palabras y máximo 14 letras. La línea de los subtítulos queda dentro de la zona segura de
# anuncio (y 288-1267). Lee tramos.json de trabajo/<toma>/ (lo escribe cortes.py) y las palabras de turbo (tx2),
# con los huecos rellenados con medium (tx).
import json, os, re, subprocess, sys
import config, cortes

a = sys.argv
if len(a) < 2: raise SystemExit("uso: python subtitular.py <toma-limpia.mp4> [--clave a,b] [--y 1180] [--salida f.mp4]")
op = lambda k, d=None: a[a.index(k) + 1] if k in a else d
toma = os.path.abspath(a[1]); nombre = os.path.splitext(os.path.basename(toma))[0]
D = os.path.join(config.TRABAJO, nombre)
tramos = json.load(open(os.path.join(D, "tramos.json")))
clave = {x.strip().lower() for x in (op("--clave", "") or "").split(",") if x.strip()}
Y = int(op("--y", 1180)); salida = op("--salida", os.path.join(D, "FINAL.mp4"))
if not 288 <= Y <= 1267: print(f"aviso: y={Y} queda fuera de la zona segura de anuncio (288-1267)")

med, tur = cortes.palabras(nombre)
ws = sorted(tur, key=lambda w: w[0])
for w in med:  # huecos de turbo de más de 0,8 s: se rellenan con medium
    if not any(x[0] - 0.4 <= w[0] <= x[1] + 0.4 for x in ws): ws.append(w)
ws.sort(key=lambda w: w[0])

def T(t):  # segundo del original -> segundo del vídeo cortado (None si cae fuera)
    acc = 0.0
    for x, y in tramos:
        if x <= t <= y: return acc + t - x
        acc += y - x
    return None

limpio = lambda w: re.sub(r"[^\wáéíóúüñÁÉÍÓÚÜÑ%]", "", w).strip()
vivas = [(T(i), T(f) if T(f) is not None else T(i) + 0.3, limpio(w)) for i, f, w in ws if T(i) is not None and limpio(w)]
bloques, cur = [], []
for i, (t0, t1, w) in enumerate(vivas):
    if cur and (len(cur) >= 3 or sum(len(x[2]) + 1 for x in cur) + len(w) > 14 or t0 - cur[-1][1] > 0.35 or w.lower() in clave):
        bloques.append(cur); cur = []
    cur.append((t0, t1, w))
    if w.lower() in clave: bloques.append(cur); cur = []
if cur: bloques.append(cur)

def ass_t(s): h = int(s // 3600); m = int(s % 3600 // 60); return f"{h}:{m:02d}:{s % 60:05.2f}"
col = config.COLOR_CLAVE.lstrip("#"); clave_ass = f"&H00{col[4:6]}{col[2:4]}{col[0:2]}&"
fam = os.path.splitext(os.path.basename(config.FUENTE_SUBT))[0].split("-")[0]
ass = os.path.join(D, "subtitulos.ass")
with open(ass, "w", encoding="utf-8") as f:
    f.write(f"[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Outline, Shadow, Alignment, MarginL, MarginR, MarginV\n"
            f"Style: S,{fam},96,&H00FFFFFF,&H00000000,&H80000000,0,7,3,2,60,150,{1920 - Y}\n\n[Events]\n"
            "Format: Layer, Start, End, Style, Text\n")
    for j, bl in enumerate(bloques):
        t0 = bl[0][0]; t1 = bloques[j + 1][0][0] if j + 1 < len(bloques) else bl[-1][1] + 0.4
        if t1 - t0 < 0.12: continue
        txt = " ".join((f"{{\\c{clave_ass}}}{w.upper()}{{\\c&H00FFFFFF&}}" if w.lower() in clave else w.upper()) for _, _, w in bl)
        f.write(f"Dialogue: 0,{ass_t(t0)},{ass_t(t1)},S,{txt}\n")

sel = "+".join(f"between(t,{x:.3f},{y:.3f})" for x, y in tramos)
esc = lambda p: p.replace("\\", "/").replace(":", "\\:")
vf = f"select='{sel}',setpts=N/FRAME_RATE/TB,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,subtitles='{esc(ass)}':fontsdir='{esc(config.FUENTES)}'"
r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", toma, "-vf", vf, "-af", f"aselect='{sel}',asetpts=N/SR/TB",
                    *config.codec_video("alta"), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", salida], capture_output=True, text=True)
if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
print("ok", salida, f"| {len(bloques)} subtítulos | {sum(y - x for x, y in tramos):.1f} s")
