# Transcribe una toma palabra a palabra con faster-whisper y DOS modelos (método medido en la tanda 0710):
#   medium         -> transcripciones/tx/   conserva repeticiones y tomas falsas (sirve para detectarlas)
#   large-v3-turbo -> transcripciones/tx2/  mejor texto, pero funde repeticiones (sirve para los subtítulos)
#   python transcribir.py <toma.mp4> [--solo medium|turbo] [--idioma es]
# Salida por modelo: <nombre>.json = [{ini, fin, texto, palabras: [[ini, fin, " palabra"], ...]}, ...] y <nombre>.txt legible.
# La primera vez descarga los modelos (varios GB): tarda.
import json, os, sys
import config

def transcribir(video, modelo, carpeta, idioma="es"):
    from faster_whisper import WhisperModel
    disp = config.C.get("whisper_dispositivo", "auto")
    m = WhisperModel(modelo, device=disp, compute_type="default")
    # sin filtro de voz (vad): con él se pierden las tomas repetidas, que es justo lo que medium debe conservar
    segs, _ = m.transcribe(video, language=idioma, word_timestamps=True, vad_filter=False, beam_size=5)
    out = []
    for s in segs:
        out.append({"ini": round(s.start, 2), "fin": round(s.end, 2), "texto": s.text.strip(),
                    "palabras": [[round(w.start, 2), round(w.end, 2), w.word] for w in (s.words or [])]})
    os.makedirs(carpeta, exist_ok=True)
    nombre = os.path.splitext(os.path.basename(video))[0]
    json.dump(out, open(os.path.join(carpeta, nombre + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(carpeta, nombre + ".txt"), "w", encoding="utf-8") as f:
        f.writelines(f"[{s['ini']:6.2f}-{s['fin']:6.2f}] {s['texto']}\n" for s in out)
    return out

if __name__ == "__main__":
    if len(sys.argv) < 2: raise SystemExit(__doc__ or "uso: python transcribir.py <toma.mp4> [--solo medium|turbo]")
    video = sys.argv[1]
    solo = sys.argv[sys.argv.index("--solo") + 1] if "--solo" in sys.argv else None
    idioma = sys.argv[sys.argv.index("--idioma") + 1] if "--idioma" in sys.argv else "es"
    for clave, modelo, sub in (("medium", "medium", "tx"), ("turbo", "large-v3-turbo", "tx2")):
        if solo and solo != clave: continue
        r = transcribir(video, modelo, os.path.join(config.TX, sub), idioma)
        print(f"ok {modelo}: {len(r)} frases, {sum(len(s['palabras']) for s in r)} palabras -> {os.path.join(config.TX, sub)}")
