# Mide reels ya terminados para aprender un estilo (los tuyos o los de tu cuenta fantasma).
#   python analizar_reels.py mis-reels     -> analiza mi-estilo/mis-reels/*.mp4     y escribe mi-estilo/mis-reels.json
#   python analizar_reels.py referencias   -> analiza mi-estilo/referencias/*.mp4  y escribe mi-estilo/referencias.json
# Por vídeo: duración, cortes de plano (detección de escenas), segundos por plano, volumen (LUFS), palabras por
# segundo y el gancho (lo que se dice en los 3 primeros segundos, con Whisper small), y una hoja de fotogramas
# (uno por segundo de los primeros 12 s) para que Claude MIRE el texto en pantalla y el encuadre.
# Solo mide: las conclusiones (aprendido.md / referencias.md) las escribe Claude a partir de estos números.
import glob, json, os, re, subprocess, sys
import config

modo = sys.argv[1] if len(sys.argv) > 1 else "mis-reels"
CARP = os.path.join(config.RAIZ, "mi-estilo", "mis-reels" if modo == "mis-reels" else "referencias")
dur_de = lambda p: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout or 0)

def cortes_de_plano(p, umbral=0.30):
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", p, "-vf", f"select='gt(scene,{umbral})',showinfo", "-an", "-f", "null", "-"], capture_output=True, text=True)
    return [round(float(x), 2) for x in re.findall(r"pts_time:([\d.]+)", r.stderr)]

def lufs(p):
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", p, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", r.stderr[r.stderr.rfind("Summary:"):]); return float(m.group(1)) if m else None

_whisper = None
def habla(p):
    global _whisper
    try:
        from faster_whisper import WhisperModel
        _whisper = _whisper or WhisperModel("small", device=config.C.get("whisper_dispositivo", "auto"))
        segs, _ = _whisper.transcribe(p, language="es", word_timestamps=True)
        pal = [w for s in segs for w in (s.words or [])]
    except Exception as e:
        return {"error": str(e)[:120]}
    gancho = " ".join(w.word.strip() for w in pal if w.start < 3.0)
    dur_voz = (pal[-1].end - pal[0].start) if pal else 0
    return {"gancho_3s": gancho, "palabras": len(pal), "palabras_por_s": round(len(pal) / dur_voz, 2) if dur_voz else 0,
            "cierre": " ".join(w.word.strip() for w in pal[-12:])}

def hoja(p):
    out = p.rsplit(".", 1)[0] + "-hoja.jpg"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-t", "12", "-i", p, "-vf",
                    "fps=1,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,scale=270:480,tile=6x2:padding=6:color=black",
                    "-frames:v", "1", out], capture_output=True)
    return out

res = []
for p in sorted(glob.glob(os.path.join(CARP, "*.mp4"))):
    d = dur_de(p); cs = cortes_de_plano(p)
    fila = {"video": os.path.basename(p), "duracion_s": round(d, 1), "cortes_de_plano": len(cs),
            "segundos_por_plano": round(d / (len(cs) + 1), 2) if d else None, "lufs": lufs(p), **habla(p), "hoja": os.path.basename(hoja(p))}
    res.append(fila); print(json.dumps(fila, ensure_ascii=False))
if not res: raise SystemExit(f"No hay vídeos .mp4 en {CARP}")
n = len(res); med = lambda k: round(sorted(x[k] for x in res if isinstance(x.get(k), (int, float)))[n // 2], 2) if any(isinstance(x.get(k), (int, float)) for x in res) else None
resumen = {"videos": n, "mediana_duracion_s": med("duracion_s"), "mediana_segundos_por_plano": med("segundos_por_plano"),
           "mediana_palabras_por_s": med("palabras_por_s"), "mediana_lufs": med("lufs")}
json.dump({"resumen": resumen, "videos": res}, open(os.path.join(config.RAIZ, "mi-estilo", f"{modo}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("RESUMEN", json.dumps(resumen, ensure_ascii=False))
