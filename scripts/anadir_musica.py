# Anade musica de fondo (y opcionalmente un ambiente de grada al principio) a un proyecto de CapCut YA montado,
# sin tocar nada mas: una pista de audio nueva, volumen bajo bajo la voz, entrada y salida con fundido.
#   python anadir_musica.py <proyecto> <musica.mp3> [volumen 0-1] [inicio_en_la_cancion_s] [grada.wav] [grada_seg]
import json, os, sys, subprocess, copy
import config
import pyJianYingDraft as d
from pyJianYingDraft import trange
from draft_profiles import get_draft_profile

CAPCUT = config.CAPCUT
proy, musica = sys.argv[1], sys.argv[2]
vol = float(sys.argv[3]) if len(sys.argv) > 3 else 0.13
ss = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
grada = sys.argv[5] if len(sys.argv) > 5 else None
grada_s = float(sys.argv[6]) if len(sys.argv) > 6 else 3.0
dur_de = lambda p: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)

carpeta = os.path.join(CAPCUT, proy)
dj = json.load(open(os.path.join(carpeta, "draft_content.json"), encoding="utf-8"))
if any(t.get("name") == "musica" for t in dj["tracks"]): raise SystemExit("ese proyecto ya tiene musica")
TOTAL = dj["duration"] / 1e6

# los segmentos los construye pyJianYingDraft (formato correcto) y se injertan en el proyecto
sc = d.Script_file(1080, 1920); sc.add_track(d.Track_type.audio, "musica")
am = d.Audio_material(path=musica, material_name=os.path.basename(musica), duration=dur_de(musica))
du = min(TOTAL, am.duration / 1e6 - ss)
seg = d.Audio_segment(am, trange("0s", f"{du:.3f}s"), source_timerange=trange(f"{ss:.3f}s", f"{du:.3f}s"), volume=vol)
seg.add_fade("0.6s", "1.2s"); sc.add_segment(seg, "musica")
if grada:
    sc.add_track(d.Track_type.audio, "grada")
    ag = d.Audio_material(path=grada, material_name=os.path.basename(grada), duration=dur_de(grada))
    gs = d.Audio_segment(ag, trange("0s", f"{min(grada_s, ag.duration / 1e6):.3f}s"), volume=0.30)
    gs.add_fade("0.1s", "1.0s"); sc.add_segment(gs, "grada")
nuevo = json.loads(sc.dumps(get_draft_profile("capcut_legacy")))

for nombre in ("draft_content.json", "draft_info.json"):
    f = os.path.join(carpeta, nombre)
    if not os.path.exists(f): continue
    j = json.load(open(f, encoding="utf-8"))
    for k, lista in nuevo["materials"].items():
        if isinstance(lista, list) and lista: j["materials"].setdefault(k, []).extend(copy.deepcopy(lista))
    j["tracks"].extend(copy.deepcopy([t for t in nuevo["tracks"] if t["segments"]]))
    json.dump(j, open(f, "w", encoding="utf-8"), ensure_ascii=False)
print("ok", proy, "|", os.path.basename(musica), f"vol {vol}", f"desde {ss}s", "| grada" if grada else "")
