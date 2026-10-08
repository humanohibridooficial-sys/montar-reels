# Copia un proyecto de CapCut (tuyo, ya aprobado) con otro nombre y cambia SOLO un clip por otro.
# No toca cortes, sonidos ni textos: lo que ya dejaste bien se queda igual.
#   python cambiar_clip.py <proyecto_origen> <proyecto_nuevo> <trozo_nombre_clip_viejo> <ruta_clip_nuevo>
import json, os, sys, shutil, subprocess
import config
CAPCUT = config.CAPCUT
orig, nuevo, viejo, clip = sys.argv[1:5]
src, dst = os.path.join(CAPCUT, orig), os.path.join(CAPCUT, nuevo)
if os.path.exists(dst): raise SystemExit(f"ya existe {dst}")
shutil.copytree(src, dst, ignore=shutil.ignore_patterns("*.bak", ".locked"))
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", clip], capture_output=True, text=True).stdout)
cambiados = 0
for nombre in ("draft_content.json", "draft_info.json"):
    f = os.path.join(dst, nombre)
    if not os.path.exists(f): continue
    j = json.load(open(f, encoding="utf-8"))
    ids = set()
    for m in j["materials"]["videos"]:
        if viejo in os.path.basename(m.get("path", "")):
            ids.add(m["id"])
            m["path"] = clip.replace("\\", "/"); m["material_name"] = os.path.basename(clip); m["duration"] = int(dur * 1e6); cambiados += 1
    for t in j["tracks"]:  # que ningun trozo pida mas segundos de los que tiene el clip nuevo
        for s in t["segments"]:
            st = s.get("source_timerange")
            if s.get("material_id") in ids and st and st["start"] + st["duration"] > dur * 1e6: st["start"] = max(0, int(dur * 1e6) - st["duration"])
    if "name" in j: j["name"] = nuevo
    json.dump(j, open(f, "w", encoding="utf-8"), ensure_ascii=False)
mi = os.path.join(dst, "draft_meta_info.json")
if os.path.exists(mi):
    j = json.load(open(mi, encoding="utf-8")); j["draft_name"] = nuevo; j["draft_fold_path"] = dst.replace("\\", "/")
    json.dump(j, open(mi, "w", encoding="utf-8"), ensure_ascii=False)
print("ok", nuevo, "| materiales cambiados:", cambiados)
