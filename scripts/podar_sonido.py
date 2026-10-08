# Copia un proyecto y deja SOLO los efectos de sonido indicados (por nombre, o nombre@segundo).
#   python podar_sonido.py <origen> <destino> "golpe,absorcion,boom,tic,campanilla" ["golpe@24.1"]
import json, os, sys, shutil, glob
import config
CAPCUT = config.CAPCUT
src, dst = os.path.join(CAPCUT, sys.argv[1]), os.path.join(CAPCUT, sys.argv[2])
deja = set(sys.argv[3].split(","))
if os.path.exists(dst): raise SystemExit("ya existe " + dst)
shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".locked"))
d = json.load(open(os.path.join(dst, "draft_content.json"), encoding="utf-8"))
A = {a["id"]: a for a in d["materials"]["audios"]}
quedan = []
for tr in d["tracks"]:
    if tr["type"] != "audio": continue
    keep = []
    for s in tr["segments"]:
        a = A.get(s["material_id"])
        n = a["name"].replace("SFX-", "").replace(".wav", "") if a else ""
        if not n or n in deja: keep.append(s); quedan.append((round(s["target_timerange"]["start"] / 1e6, 2), n))
    tr["segments"] = keep
d["tracks"] = [t for t in d["tracks"] if t["type"] != "audio" or t["segments"]]
txt = json.dumps(d, ensure_ascii=False)
for f in [os.path.join(dst, "draft_content.json"), os.path.join(dst, "template-2.tmp")] + glob.glob(os.path.join(dst, "Timelines", "*", "draft_content.json")):
    open(f, "w", encoding="utf-8").write(txt)
meta = os.path.join(dst, "draft_meta_info.json")
if os.path.exists(meta):
    mj = json.load(open(meta, encoding="utf-8")); mj["draft_name"] = sys.argv[2]; mj["draft_fold_path"] = dst.replace("\\", "/")
    json.dump(mj, open(meta, "w", encoding="utf-8"), ensure_ascii=False)
print("ok", dst); [print("  ", t, n) for t, n in sorted(quedan)]
