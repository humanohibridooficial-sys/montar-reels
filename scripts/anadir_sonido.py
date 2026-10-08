# Copia un proyecto de CapCut tuyo y le añade diseño de sonido anclado a SUS elementos (respeta sus cambios).
#   python anadir_sonido.py <proyecto_origen> <proyecto_nuevo>
import json, os, sys, shutil, glob, subprocess
import config
import pyJianYingDraft as d
from pyJianYingDraft import trange
from draft_profiles import get_draft_profile

CAPCUT = config.CAPCUT
SFX = config.PIEZAS  # carpeta con los SFX-*.wav (Mixkit), ver README
src, dst = os.path.join(CAPCUT, sys.argv[1]), os.path.join(CAPCUT, sys.argv[2])
if os.path.exists(dst): raise SystemExit(f"ya existe {dst}")
shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".locked"))
d0 = json.load(open(os.path.join(dst, "draft_content.json"), encoding="utf-8"))
DUR = d0["duration"] / 1e6
V = {v["id"]: v for v in d0["materials"]["videos"]}
pista = lambda n: next((t for t in d0["tracks"] if t.get("name") == n), {"segments": []})
ini = lambda s: s["target_timerange"]["start"] / 1e6

eventos = []  # (nombre, segundo, volumen)
# rotulos: golpe; con palabra dorada, golpe + brillo; el CTA, campanilla
for s in pista("rotulos_img")["segments"]:
    n = os.path.basename(V[s["material_id"]]["path"]); t = ini(s)
    if "cta" in n: eventos.append(("campanilla", t, 0.45))
    elif "marcador-tu" in n: eventos.append(("brillo", t + 0.05, 0.40))
    else:
        eventos.append(("golpe", t, 0.55))
        if any(k in n for k in ("gancho", "evitable", "no-sigue", "fuera", "depende")): eventos.append(("brillo", t + 0.06, 0.30))
# zooms de golpe: bombo al entrar en un tramo a 115 %
for s in pista("main")["segments"]:
    if (s.get("clip") or {}).get("scale", {}).get("x", 1) >= 1.14 and ini(s) > 0.2: eventos.append(("bombo", ini(s), 0.55))
# paso a blanco y negro: absorcion justo antes
for s in pista("main")["segments"]:
    if any(k.get("property_type") == "KFTypeSaturation" for k in s.get("common_keyframes", [])): eventos.append(("absorcion", max(0, ini(s) - 0.15), 0.45))
# decisiones de esta pieza: "nombre@segundo" que NO van (cada reel pide lo suyo)
QUITAR = [x.split("@") for x in (sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] else [])]
eventos = [e for e in eventos if not any(e[0] == n and abs(e[1] - float(t)) < 0.2 for n, t in QUITAR)]
eventos = [e for e in eventos if e[1] < DUR - 0.1]

def probe(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)

# generar los segmentos de audio con la libreria y trasplantarlos
sc = d.Script_file(1080, 1920); mats, fines = {}, []
for nombre, t, vol in sorted(eventos, key=lambda e: e[1]):
    p = os.path.join(SFX, f"SFX-{nombre}.wav")
    if p not in mats: mats[p] = d.Audio_material(path=p, material_name=os.path.basename(p), duration=probe(p))
    am = mats[p]; du = min(am.duration / 1e6, DUR - t)
    k = next((i for i, f in enumerate(fines) if f <= t + 1e-3), None)
    if k is None: sc.add_track(d.Track_type.audio, f"sfx_enfasis{len(fines) + 1}"); fines.append(0.0); k = len(fines) - 1
    sc.add_segment(d.Audio_segment(am, trange(f"{t:.3f}s", f"{du:.3f}s"), volume=vol), f"sfx_enfasis{k + 1}"); fines[k] = t + du
nuevo = json.loads(sc.dumps(get_draft_profile("capcut_legacy")))
pistas = [t for t in nuevo["tracks"] if t["type"] == "audio"]
refs = {r for t in pistas for s in t["segments"] for r in [s["material_id"], *s.get("extra_material_refs", [])]}
for k, lst in nuevo["materials"].items():
    if isinstance(lst, list):
        extra = [m for m in lst if isinstance(m, dict) and m.get("id") in refs]
        if extra: d0["materials"].setdefault(k, []).extend(extra)
d0["tracks"].extend(pistas)

txt = json.dumps(d0, ensure_ascii=False)
destinos = [os.path.join(dst, "draft_content.json"), os.path.join(dst, "template-2.tmp")] + glob.glob(os.path.join(dst, "Timelines", "*", "draft_content.json"))
for f in destinos:
    if os.path.exists(f) or f.endswith("draft_content.json"): open(f, "w", encoding="utf-8").write(txt)
meta = os.path.join(dst, "draft_meta_info.json")
if os.path.exists(meta):
    mj = json.load(open(meta, encoding="utf-8")); mj["draft_name"] = sys.argv[2]; mj["draft_fold_path"] = dst.replace("\\", "/")
    json.dump(mj, open(meta, "w", encoding="utf-8"), ensure_ascii=False)
print(f"ok {dst}\n  {len(eventos)} efectos en {len(pistas)} pistas")
for e in sorted(eventos, key=lambda e: e[1]): print(f"   {e[1]:5.2f}s {e[0]}")
