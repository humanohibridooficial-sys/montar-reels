# Monta un reel completo como proyecto de CapCut (editable) a partir de una especificacion JSON.
#   python montar_reel.py spec.json
# El video principal entra en trozos del ORIGINAL (se pueden estirar en CapCut para rehacer un corte).
import json, os, sys, shutil, subprocess, re
import config  # rutas de config.json y VectCutAPI en el path
import pyJianYingDraft as d
from pyJianYingDraft import trange, tim, Keyframe_property as KP
from draft_profiles import get_draft_profile

SPEC = json.load(open(sys.argv[1], encoding="utf-8"))
CAPCUT = config.CAPCUT
PLANTILLA = config.PLANTILLA  # un proyecto (vacío) que tu CapCut ya abrió bien: se copia y se rellena
if not os.path.isdir(PLANTILLA):
    raise SystemExit(f"Falta la plantilla de CapCut: crea en CapCut un proyecto vacío llamado '{os.path.basename(PLANTILLA)}', ciérralo y repite.")

def probe(p):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,codec_type",
                                   "-of", "json", p], capture_output=True, text=True).stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), {})
    return float(j["format"]["duration"]), v.get("width"), v.get("height")

_mats = {}
def vmat(p):
    if p not in _mats:
        dur, w, h = probe(p)
        _mats[p] = d.Video_material("video", path=p, material_name=os.path.basename(p), duration=dur, width=w, height=h)
    return _mats[p]

def amat(p):
    if p not in _mats:
        _mats[p] = d.Audio_material(path=p, material_name=os.path.basename(p), duration=probe(p)[0])
    return _mats[p]

rgb = lambda h: tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))

# ---------- tiempos: tramos que se quedan del original ----------
palabras = SPEC["palabras"]            # [[ini, fin, texto], ...] en segundos del ORIGINAL
fuera = SPEC.get("fuera", [])
forzar = SPEC.get("forzar", [])
FIN = SPEC["fin"]
PRE, POST, GAP = 0.10, 0.18, 0.55
dentro = lambda t: any(a <= t <= b for a, b in fuera)
iv = sorted([[max(0, a - PRE), min(FIN, b + POST)] for a, b, _ in palabras if not dentro(a) and a < FIN] + [list(x) for x in forzar])
partes = []
for a, b in iv:
    segs = [[a, b]]
    for x, y in fuera:  # ningun tramo invade una toma falsa
        segs = [s for p, q in segs for s in ([[p, q]] if q <= x or p >= y else [[p, min(q, x)], [max(p, y), q]]) if s[1] - s[0] > 0.05]
    partes += segs
tramos = []
for a, b in sorted(partes):
    if tramos and a - tramos[-1][1] <= GAP - PRE - POST: tramos[-1][1] = max(tramos[-1][1], b)
    elif tramos and a <= tramos[-1][1]: tramos[-1][1] = max(tramos[-1][1], b)
    else: tramos.append([a, b])
if SPEC.get("tramos"):  # corte ya revisado (cortes.py): manda sobre el calculo automatico
    tramos = [list(x) for x in SPEC["tramos"]]
    dentro = lambda t: not any(a <= t < b for a, b in tramos)
# partir en los zooms
for z0, z1 in SPEC.get("zooms", []) + SPEC.get("byn", []) + SPEC.get("desvanecer", []):
    nuevos = []
    for a, b in tramos:
        cortes = sorted({a, b} | {c for c in (z0, z1) if a < c < b})
        nuevos += [[cortes[i], cortes[i + 1]] for i in range(len(cortes) - 1)]
    tramos = nuevos
def T(t):  # segundo del original -> segundo en el proyecto
    acc = 0.0
    for a, b in tramos:
        if t < a: return acc
        if t <= b: return acc + t - a
        acc += b - a
    return acc
TOTAL = sum(b - a for a, b in tramos)

script = d.Script_file(1080, 1920)
pistas = ["main", "palabra", "broll", "tarjeta", "piezas", "rotulos", "subtitulos", "cta"]
script.add_track(d.Track_type.video, "main")
for i, n in enumerate(["palabra", "broll", "tarjeta", "piezas", "rotulos_img"], 1): script.add_track(d.Track_type.video, n, relative_index=i)
for i, n in enumerate(["rotulos", "subtitulos", "subtitulos_clave", "cta"], 1): script.add_track(d.Track_type.text, n, relative_index=i)

# ---------- 1. tu video ----------
VID = SPEC["video"]; m = vmat(VID); pos = 0.0
zooms = SPEC.get("zooms", [])
for i, (a, b) in enumerate(tramos):
    en_zoom = any(z0 <= a and b <= z1 + 1e-6 for z0, z1 in zooms)
    alterna = SPEC.get("alternar_encuadre", True) and i % 2 == 1
    s = SPEC.get("zoom_escala", 1.15) if en_zoom else (SPEC.get("alterna_escala", 1.06) if alterna else 1.0)
    seg = d.Video_segment(m, trange(f"{pos:.3f}s", f"{b - a:.3f}s"), source_timerange=trange(f"{a:.3f}s", f"{b - a:.3f}s"),
                          volume=SPEC.get("volumen_voz", 1.4), clip_settings=d.Clip_settings(scale_x=s, scale_y=s, transform_y=SPEC.get("alterna_y", -0.06) if en_zoom else (SPEC.get("alterna_y", -0.02) if s > 1 else 0)))
    if any(b0 <= a and b <= b1 + 1e-6 for b0, b1 in SPEC.get("desvanecer", [])):  # se desvanece hasta negro
        seg.add_keyframe(KP.alpha, 0, 1.0); seg.add_keyframe(KP.alpha, tim(f"{b - a:.3f}s"), 0.0)
    if any(b0 <= a and b <= b1 + 1e-6 for b0, b1 in SPEC.get("byn", [])):  # tramo en blanco y negro
        seg.add_keyframe(KP.saturation, 0, -1.0)
    if i == 0 and not SPEC.get("palabra_detras"):  # zoom lento del gancho
        seg.add_keyframe(KP.uniform_scale, 0, 1.0); seg.add_keyframe(KP.uniform_scale, tim(f"{min(3.0, b - a):.3f}s"), 1.07)
    if i == len(tramos) - 1:  # final oscurecido
        dur = b - a; k0 = max(0, dur - 1.6)
        seg.add_keyframe(KP.brightness, tim(f"{k0:.3f}s"), 0.0); seg.add_keyframe(KP.brightness, tim(f"{dur:.3f}s"), -0.35)
    script.add_segment(seg, "main"); pos += b - a

_pistas_sfx = []  # [nombre, fin]
def sfx(nombre, t, vol=0.35):
    p = os.path.join(SPEC["piezas_dir"], f"SFX-{nombre}.wav"); am = amat(p); du = am.duration / 1e6
    t = max(0.0, t)
    du = min(du, TOTAL - t)  # un efecto nunca alarga el video (dejaria el final en negro)
    if du < 0.05: return
    pista = next((ps for ps in _pistas_sfx if ps[1] <= t + 1e-3), None)
    if pista is None:
        nombre_p = f"sfx{len(_pistas_sfx) + 1}"; script.add_track(d.Track_type.audio, nombre_p); pista = [nombre_p, 0.0]; _pistas_sfx.append(pista)
    script.add_segment(d.Audio_segment(am, trange(f"{t:.3f}s", f"{du:.3f}s"), source_timerange=trange("0s", f"{du:.3f}s"), volume=vol * SPEC.get("sfx_gain", 1.0)), pista[0]); pista[1] = t + du

# ---------- 2. palabra gigante detras (clip ya compuesto) ----------
for p in SPEC.get("palabra_detras", []):
    mm = vmat(p["clip"]); t0 = T(p["ini"])
    script.add_segment(d.Video_segment(mm, trange(f"{t0:.3f}s", f"{mm.duration / 1e6 - 0.05:.3f}s"), volume=0), "palabra")
    if SPEC.get("sfx_auto", True): sfx(p.get("sfx", "pop"), t0 + 0.05, p.get("sfx_vol", 0.45))

# ---------- 3. b-roll ----------
for b in SPEC.get("broll", []):
    mm = vmat(b["clip"]); t0 = T(b["ini"]); du = b.get("dur", 2.0)
    src0 = max(0, mm.duration / 1e6 / 2 - du / 2)
    if b["modo"] == "grande":  # tarjeta grande que entra desde abajo, inclinada, tapando medio cuerpo
        cs = d.Clip_settings(scale_x=b.get("escala", 0.62), scale_y=b.get("escala", 0.62), transform_x=b.get("x", 0.0), transform_y=b.get("y", -0.30), rotation=b.get("rot", -3))
        seg = d.Video_segment(mm, trange(f"{t0:.3f}s", f"{du:.3f}s"), source_timerange=trange(f"{src0:.3f}s", f"{du:.3f}s"), volume=0, clip_settings=cs)
        seg.add_mask(script, d.CapCut_Mask_type.Rectangle, size=1.0, rect_width=1.0, round_corner=30)
        seg.add_animation(d.CapCut_Intro_type.Slide_Up, "0.35s"); seg.add_animation(d.CapCut_Outro_type.Fade_Out, "0.15s")
        script.add_segment(seg, "tarjeta")
    elif b["modo"] == "tarjeta":
        cs = d.Clip_settings(scale_x=b.get("escala", 0.36), scale_y=b.get("escala", 0.36), transform_x=b.get("x", 0.52), transform_y=b.get("y", 0.44), rotation=b.get("rot", 5))
        seg = d.Video_segment(mm, trange(f"{t0:.3f}s", f"{du:.3f}s"), source_timerange=trange(f"{src0:.3f}s", f"{du:.3f}s"), volume=0, clip_settings=cs)
        seg.add_mask(script, d.CapCut_Mask_type.Rectangle, size=1.0, rect_width=1.0, round_corner=45)
        seg.add_animation(d.CapCut_Intro_type.Slide_Up, "0.3s")
        script.add_segment(seg, "tarjeta")
    elif b["modo"] == "media":
        # Media pantalla con máscara LINEAL de CapCut (editable): tu toma sigue debajo y el clip se funde con
        # ella en la línea de corte (Luismi, 10-10: "como la máscara de CapCut de media pantalla").
        # "corte" = altura de la línea en pantalla (0 arriba, 1 abajo): por defecto, arriba acaba sobre tu
        # cabeza y abajo empieza en tus hombros (medido en la toma 38). Si en CapCut se ve el lado contrario,
        # cambia "invertir" en la spec.
        arriba = b.get("lado", "arriba") == "arriba"
        corte = b.get("corte", 0.31 if arriba else 0.66)
        seg = d.Video_segment(mm, trange(f"{t0:.3f}s", f"{du:.3f}s"), source_timerange=trange(f"{src0:.3f}s", f"{du:.3f}s"), volume=0)
        seg.add_mask(script, d.CapCut_Mask_type.Split, center_y=(0.5 - corte) * script.height,
                     rotation=0 if arriba else 180, feather=b.get("difuminado", 35), invert=b.get("invertir", False))
        seg.add_animation(d.CapCut_Intro_type.Fade_In, "0.15s"); seg.add_animation(d.CapCut_Outro_type.Fade_Out, "0.15s")
        script.add_segment(seg, "broll")
    else:
        seg = d.Video_segment(mm, trange(f"{t0:.3f}s", f"{du:.3f}s"), source_timerange=trange(f"{src0:.3f}s", f"{du:.3f}s"), volume=0)
        seg.add_animation(d.CapCut_Intro_type.Fade_In, "0.15s"); seg.add_animation(d.CapCut_Outro_type.Fade_Out, "0.15s")
        script.add_segment(seg, "broll")
    if SPEC.get("sfx_auto", True): sfx("whoosh", max(0, t0 - 0.15))

# ---------- 4. piezas (tarjetas) ----------
for p in SPEC.get("piezas", []):
    mm = vmat(p["clip"]); t0 = T(p["ini"]); du = min(T(p["fin"]) - t0 if "fin" in p else p.get("dur", 4.5), mm.duration / 1e6)
    si = p.get("src_ini", 0.0); du = min(du, mm.duration / 1e6 - si)
    sp = d.Video_segment(mm, trange(f"{t0:.3f}s", f"{du:.3f}s"), source_timerange=trange(f"{si:.3f}s", f"{du:.3f}s"), volume=0)
    sp.add_animation(d.CapCut_Intro_type.Fade_In, "0.2s"); sp.add_animation(d.CapCut_Outro_type.Fade_Out, "0.2s")
    script.add_segment(sp, "piezas")
    if SPEC.get("sfx_auto", True): sfx("whoosh", max(0, t0 - 0.15))

# ---------- 5. rotulos ----------
# 5a. diseñados como PNG (sistema de retransmision), entran con deslizamiento y salen con fundido
_pistas_png = []
for r in SPEC.get("rotulos_png", []):
    mm = d.Video_material("photo", path=r["png"], material_name=os.path.basename(r["png"]), width=1080, height=1920)
    t0 = T(r["ini"]); t1 = T(r["fin"]) if "fin" in r else TOTAL
    e = r.get("escala", 1.0 if r.get("pista") else SPEC.get("rotulos_escala", 1.0))  # rotulos de texto algo mas pequenos: respiran
    seg = d.Video_segment(mm, trange(f"{t0:.3f}s", f"{t1 - t0:.3f}s"), clip_settings=d.Clip_settings(scale_x=e, scale_y=e, transform_y=r.get("y", 0.0 if r.get("pista") else SPEC.get("rotulos_y", 0.0))))
    seg.add_animation(d.CapCut_Intro_type.Zoom_In if r.get("anim") == "pop" else d.CapCut_Intro_type.Fade_In, "0.25s")
    if "fin" in r and t1 - t0 > 1.0: seg.add_animation(d.CapCut_Outro_type.Fade_Out, "0.2s")
    pista = r.get("pista", "rotulos_img")  # objetos que se suman: cada uno en su pista para poder solaparse
    if pista not in _pistas_png and pista != "rotulos_img":
        script.add_track(d.Track_type.video, pista, relative_index=6 + len(_pistas_png)); _pistas_png.append(pista)
    script.add_segment(seg, pista)
    if SPEC.get("sfx_auto", True): sfx("whoosh", max(0, t0 - 0.1), 0.25)
# 5c. destellos (pasar de bloque) y tintes de color (la otra voz, "red flag"), como capas PNG de color liso
# en su pista. Variados (Luismi, 10-10: "no sota, caballo y rey"): si la spec no fija el color, se elige al
# azar entre los de la marca, con semilla por pieza para que regenerar dé lo mismo.
import random
from PIL import Image
_azar = random.Random(SPEC.get("nombre", "reel"))
_solidos = os.path.join(config.RAIZ, "trabajo", "_solidos"); os.makedirs(_solidos, exist_ok=True)
def solido(hexcol, alfa):
    p = os.path.join(_solidos, f"{hexcol.strip('#')}-{int(alfa * 100)}.png")
    if not os.path.exists(p): Image.new("RGBA", (1080, 1920), tuple(int(hexcol[i:i + 2], 16) for i in (1, 3, 5)) + (int(255 * alfa),)).save(p)
    return p
# Colores de FF360 (Luismi, 10-10: "mete mi branding, no el de Carla"): dorado del resaltado, azul de la
# marca, marino de los rótulos y el blanco azulado; nada de crema ni verde (el verde es el antiguo).
DESTELLO = ["#E0B83C", "#2E6BFF", "#E6F0FF"]
TINTE = {"rojo": "#C62828", "azul": "#2E6BFF", "marino": "#1E3A5F", "dorado": "#E0B83C"}  # rojo solo para el "red flag"
if SPEC.get("tintes"): script.add_track(d.Track_type.video, "tintes", relative_index=20)
if SPEC.get("destellos"): script.add_track(d.Track_type.video, "efectos", relative_index=21)  # el destello, por encima
for f in SPEC.get("destellos", []):
    f = f if isinstance(f, dict) else {"t": f}
    col = f.get("color") or _azar.choice(DESTELLO); du = f.get("dur", _azar.choice([0.16, 0.2, 0.26]))
    mm = d.Video_material("photo", path=solido(col, 0.9), material_name="destello", width=1080, height=1920)
    t0 = max(0.0, T(f["t"]) - du / 2)
    seg = d.Video_segment(mm, trange(f"{t0:.3f}s", f"{du:.3f}s"))
    seg.add_animation(d.CapCut_Intro_type.Fade_In, f"{du / 2:.3f}s"); seg.add_animation(d.CapCut_Outro_type.Fade_Out, f"{du / 2:.3f}s")
    script.add_segment(seg, "efectos")
for c in SPEC.get("tintes", []):
    col = TINTE.get(c.get("color"), c.get("color")) or _azar.choice(list(TINTE.values()))
    t0, t1 = T(c["ini"]), T(c["fin"])
    mm = d.Video_material("photo", path=solido(col, c.get("fuerza", 0.28)), material_name="tinte", width=1080, height=1920)
    seg = d.Video_segment(mm, trange(f"{t0:.3f}s", f"{t1 - t0:.3f}s"))
    seg.add_animation(d.CapCut_Intro_type.Fade_In, "0.12s"); seg.add_animation(d.CapCut_Outro_type.Fade_Out, "0.12s")
    script.add_segment(seg, "tintes")
# 5b. rotulos de texto de CapCut (sistema antiguo, solo si la spec los pide)
for r in SPEC.get("rotulos", []):
    oro = r.get("oro", False)
    t0, t1 = T(r["ini"]), T(r["fin"])
    seg = d.Text_segment(r["texto"], trange(f"{t0:.3f}s", f"{t1 - t0:.3f}s"), font=d.Font_type.Roboto_BlkCn,
                         style=d.Text_style(size=10, color=rgb("#1E3A5F" if oro else "#FFFFFF"), align=1, bold=True),
                         background=d.Text_background(color="#E0B83C" if oro else "#1E3A5F", alpha=0.95, round_radius=0.3, height=0.2, width=0.18),
                         clip_settings=d.Clip_settings(transform_y=0.62))
    seg.add_animation(d.CapCut_Text_intro.Pop_Up, "0.25s"); seg.add_animation(d.CapCut_Text_outro.Fade_Out, "0.2s")
    script.add_segment(seg, "rotulos")

# ---------- 6. subtitulos palabra a palabra (bloques de 1-3), clave en dorado y mas grande ----------
clave = {w.lower() for w in SPEC.get("clave", [])}
limpio = lambda w: w.strip().strip(".,;:!?¿¡\"'").lower()
vivas = [(a, b, w) for a, b, w in SPEC["palabras_subt"] if not dentro(a) and a < FIN]
UNION = {"y", "que", "de", "el", "la", "lo", "los", "las", "es", "a", "en", "por", "para", "se", "te", "un", "una", "tu", "su", "mi", "del", "al", "con", "no", "si", "pero", "cuando", "como"}
bloques, cur = [], []
for i, (a, b, w) in enumerate(vivas):
    MAXL = SPEC.get("subt_max_letras", 16)
    if SPEC.get("subt_modo") == "marca" and cur and sum(len(x[2].strip()) + 1 for x in cur) + len(w.strip()) > MAXL:
        bloques.append(cur); cur = []          # no cabe: cierra antes de meterla
    cur.append((a, b, w))
    sig = vivas[i + 1] if i + 1 < len(vivas) else None
    chars = sum(len(x[2].strip()) + 1 for x in cur)
    fin_frase = w.rstrip()[-1:] in ".,?!:;"
    pausa = sig and sig[0] - b > 0.35
    llena = len(cur) >= 3 or chars >= SPEC.get("subt_max_letras", 16)
    es_k = SPEC.get("subt_modo") != "marca" and (limpio(w) in clave or (sig and limpio(sig[2]) in clave))
    jer = (SPEC.get("subt_jerarquia") or SPEC.get("subt_rotulo")) and limpio(w) in clave
    if not sig or fin_frase or pausa or es_k or jer or (llena and limpio(w) not in UNION) or len(cur) >= 4:
        bloques.append(cur); cur = []
ESTILO_CLONADO = bool(SPEC.get("subt_estilo_de"))
if ESTILO_CLONADO:  # sus subtitulos: bloques de hasta 6 palabras / 30 letras, en mayusculas, sin puntuacion
    bloques, cur = [], []
    for i, (a, b, w) in enumerate(vivas):
        cur.append((a, b, w))
        sig = vivas[i + 1] if i + 1 < len(vivas) else None
        chars = sum(len(x[2].strip()) + 1 for x in cur)
        fin = w.rstrip()[-1:] in ".?!:;" or (w.rstrip()[-1:] == "," and chars >= 14)
        if not sig or fin or (sig and sig[0] - b > 0.45) or ((len(cur) >= 6 or chars >= 30) and limpio(w) not in UNION) or len(cur) >= 7:
            bloques.append(cur); cur = []
SUBT_INFO = []; MARCA_INFO = []
# tramos en que hay un rotulo/capa en la franja de los subtitulos (los marcados "arriba": True no cuentan)
RIVALES = [(T(r["ini"]), T(r["fin"]) if "fin" in r else TOTAL, bool(r.get("tapa"))) for r in SPEC.get("rotulos_png", []) if not r.get("arriba")]
for j, bl in enumerate(bloques):
    t0 = T(bl[0][0]); t1 = T(bloques[j + 1][0][0]) if j + 1 < len(bloques) else TOTAL
    if t1 - t0 < 0.12: continue
    if ESTILO_CLONADO:
        pal = [re.sub(r"[.,;:!]", "", w.strip()).upper() for _, _, w in bl]
        txt = " ".join(pal)
        SUBT_INFO.append((txt, [(p, int((T(a) - t0) * 1000), int((T(b) - t0) * 1000)) for p, (a, b, _) in zip(pal, bl)]))
        seg = d.Text_segment(txt, trange(f"{t0:.3f}s", f"{t1 - t0:.3f}s"))
        script.add_segment(seg, "subtitulos"); continue
    if t0 < T(SPEC.get("subt_desde", 0)) - 0.01: continue
    if any(T(a) - 0.01 <= t0 < T(b) for a, b in SPEC.get("subt_ocultar", [])): continue
    # un rotulo en pantalla y el subtitulo comparten franja: o baja (subt_y_bajo) o no sale. Nunca se pisan.
    pisa = any(t0 < b and t1 > a for a, b, _ in RIVALES)
    if any(t0 < b and t1 > a for a, b, tapa in RIVALES if tapa): continue  # la capa ocupa tambien la franja baja
    if pisa and SPEC.get("subt_y_bajo") is None: continue
    if SPEC.get("subt_modo") == "marca":
        ROT = SPEC.get("subt_rotulo")  # la palabra clave "vestida de rótulo" (técnica de @carlabalasc, marca FF360)
        mayus = not (ROT and SPEC.get("subt_minusculas"))
        pal = [re.sub(r"[.,;:!]", "", w.strip()).upper() if mayus else re.sub(r"[.,;:]", "", w.strip()) for _, _, w in bl]
        ks = [limpio(w) in clave for _, _, w in bl]
        tam = SPEC.get("subt_size", 16); sy = SPEC["subt_y_bajo"] if pisa else SPEC.get("subt_y", -0.23)
        kf = SPEC.get("subt_clave_factor", 2.5 if ROT else 1.75); ga, gb = SPEC.get("subt_jer_sep", [0.045, -0.035])
        if ROT and any(ks) and not all(ks):
            # La frase pequeña entra con el bloque; la clave, DEBAJO y grande, entra cuando se dice y las dos
            # se quedan juntas como un rótulo hasta el siguiente bloque. La entrada de la clave varía.
            antes = [x for x, k in zip(pal, ks) if not k]; claves = [x.upper() for x, k in zip(pal, ks) if k]
            tk = T(next(a for (a, _, _), k in zip(bl, ks) if k))
            MARCA_INFO.append([(x, False) for x in antes])
            seg = d.Text_segment(" ".join(antes), trange(f"{t0:.3f}s", f"{t1 - t0:.3f}s"),
                                 style=d.Text_style(size=tam * 0.8, color=(1, 1, 1), align=1, bold=True),
                                 border=d.Text_border(color=(0, 0, 0), width=30, alpha=1.0),
                                 shadow=d.Text_shadow(has_shadow=True, alpha=0.7, angle=-60, distance=8, smoothing=0.3),
                                 clip_settings=d.Clip_settings(transform_y=sy + ga))
            seg.add_animation(d.CapCut_Text_intro.Fade_In, "0.12s"); script.add_segment(seg, "subtitulos")
            sk = d.Text_segment(" ".join(claves), trange(f"{tk:.3f}s", f"{max(0.3, t1 - tk):.3f}s"),
                                style=d.Text_style(size=tam * kf, color=(224 / 255, 184 / 255, 60 / 255), align=1, bold=True),
                                border=d.Text_border(color=(0, 0, 0), width=40, alpha=1.0),
                                shadow=d.Text_shadow(has_shadow=True, alpha=0.7, angle=-60, distance=8, smoothing=0.3),
                                clip_settings=d.Clip_settings(transform_y=sy + gb - 0.02))
            entrada = _azar.choice([d.CapCut_Text_intro.Blur, d.CapCut_Text_intro.Zoom_In, d.CapCut_Text_intro.Pop_Up])
            sk.add_animation(entrada, "0.25s"); script.add_segment(sk, "subtitulos_clave"); continue
        if SPEC.get("subt_jerarquia") and any(ks) and not all(ks):
            # jerarquia en DOS textos separados (un tamano por texto: CapCut no descoloca nada)
            antes = [x for x, k in zip(pal, ks) if not k]; claves = [x for x, k in zip(pal, ks) if k]
            MARCA_INFO.append([(x, False) for x in antes])
            seg = d.Text_segment(" ".join(antes), trange(f"{t0:.3f}s", f"{t1 - t0:.3f}s"),
                                 style=d.Text_style(size=tam * 0.85, color=(1, 1, 1), align=1, bold=True),
                                 border=d.Text_border(color=(0, 0, 0), width=40, alpha=1.0),
                                 shadow=d.Text_shadow(has_shadow=True, alpha=0.7, angle=-60, distance=8, smoothing=0.3),
                                 clip_settings=d.Clip_settings(transform_y=sy + ga))
            seg.add_animation(d.CapCut_Text_intro.Pop_Up, "0.18s"); script.add_segment(seg, "subtitulos")
            sk = d.Text_segment(" ".join(claves), trange(f"{t0:.3f}s", f"{t1 - t0:.3f}s"),
                                style=d.Text_style(size=tam * kf, color=(224 / 255, 184 / 255, 60 / 255), align=1, bold=True),
                                border=d.Text_border(color=(0, 0, 0), width=40, alpha=1.0),
                                shadow=d.Text_shadow(has_shadow=True, alpha=0.7, angle=-60, distance=8, smoothing=0.3),
                                clip_settings=d.Clip_settings(transform_y=sy + gb))
            sk.add_animation(d.CapCut_Text_intro.Pop_Up, "0.22s"); script.add_segment(sk, "subtitulos_clave"); continue
        MARCA_INFO.append(list(zip(pal, ks)))
        seg = d.Text_segment(" ".join(pal), trange(f"{t0:.3f}s", f"{t1 - t0:.3f}s"),
                             style=d.Text_style(size=SPEC.get("subt_size", 16), color=(1, 1, 1), align=1, bold=True),
                             border=d.Text_border(color=(0, 0, 0), width=40, alpha=1.0),
                             shadow=d.Text_shadow(has_shadow=True, alpha=0.7, angle=-60, distance=8, smoothing=0.3),
                             clip_settings=d.Clip_settings(transform_y=sy))
        seg.add_animation(d.CapCut_Text_intro.Pop_Up, "0.18s")
        script.add_segment(seg, "subtitulos"); continue
    txt = " ".join(w.strip() for _, _, w in bl).strip()
    es_clave = any(limpio(w) in clave for _, _, w in bl)
    seg = d.Text_segment(txt, trange(f"{t0:.3f}s", f"{t1 - t0:.3f}s"), font=d.Font_type.Inter_Black,
                         style=d.Text_style(size=SPEC.get("subt_size", 18) + (4 if es_clave else 0), color=rgb("#E0B83C" if es_clave else "#FFFFFF"), align=1, bold=True),
                         border=d.Text_border(color=(0, 0, 0), width=30, alpha=0.9),
                         shadow=d.Text_shadow(has_shadow=True, alpha=0.6, angle=-70, distance=6, smoothing=0.45),
                         clip_settings=d.Clip_settings(transform_y=SPEC.get("subt_y", -0.30)))
    seg.add_animation(d.CapCut_Text_intro.Mini_Zoom, "0.15s")
    script.add_segment(seg, "subtitulos")

# ---------- 6b. efectos de sonido sueltos (anclados a un segundo del original) ----------
for e in SPEC.get("sfx_extra", []):
    sfx(e["nombre"], T(e["ini"]) + e.get("off", 0.0), e.get("vol", 0.35))

# ---------- 6c. ambiente de fondo en bucle (opcional) ----------
if SPEC.get("ambiente"):
    am = amat(os.path.join(SPEC["piezas_dir"], f"SFX-{SPEC['ambiente']}.wav")); du = am.duration / 1e6; t = 0.0
    script.add_track(d.Track_type.audio, "ambiente")
    while t < TOTAL - 0.05:
        dd = round(min(du - 0.01, TOTAL - t), 3)
        if dd <= 0.05: break
        script.add_segment(d.Audio_segment(am, trange(f"{t:.3f}s", f"{dd:.3f}s"), volume=SPEC.get("ambiente_vol", 0.5)), "ambiente"); t = round(t + dd + 0.001, 3)

# ---------- 7. CTA (texto; si la spec trae rotulo PNG de cierre, no hace falta) ----------
c = SPEC.get("cta")
if c:
  t0 = T(c["ini"])
  seg = d.Text_segment(c["texto"], trange(f"{t0:.3f}s", f"{TOTAL - t0:.3f}s"), font=d.Font_type.Roboto_BlkCn,
                     style=d.Text_style(size=14, color=(1, 1, 1), align=1, bold=True),
                     background=d.Text_background(color="#2E6BFF", alpha=1.0, round_radius=0.4, height=0.25, width=0.25),
                     clip_settings=d.Clip_settings(transform_y=0.05))
  seg.add_animation(d.CapCut_Text_intro.Pop_Up, "0.3s")
  script.add_segment(seg, "cta")
  if SPEC.get("sfx_auto", True): sfx("pop", t0, 0.45)

# ---------- guardar como proyecto nuevo ----------
destino = os.path.join(CAPCUT, SPEC["nombre"])
if os.path.exists(destino): raise SystemExit(f"ya existe {destino}: cambia el nombre")
shutil.copytree(PLANTILLA, destino, ignore=shutil.ignore_patterns("assets", "*.bak", ".locked"))
contenido = script.dumps(get_draft_profile("capcut_legacy"))


# ---------- subtitulos de marca: fuente de CapCut (p. ej. ZY Steady), blanco y la palabra clave en color ----------
# Solo si la spec trae "subt_fuente" {path, id} de un recurso de TU CapCut; si no, CapCut usa su fuente por defecto.
if MARCA_INFO and SPEC.get("subt_fuente"):
    dj = json.loads(contenido)
    pista = next(tr for tr in dj["tracks"] if tr.get("name") == "subtitulos")
    textos = {t["id"]: t for t in dj["materials"]["texts"]}
    assert len(pista["segments"]) == len(MARCA_INFO)
    ZY = {"path": SPEC["subt_fuente"]["path"], "id": SPEC["subt_fuente"]["id"]}
    for sg, pal in zip(pista["segments"], MARCA_INFO):
        t = textos[sg["material_id"]]; c = json.loads(t["content"]); base = c["styles"][0]
        estilos, pos = [], 0
        jer = False  # la jerarquia va ahora en dos textos separados
        if jer:  # "vas a tener" pequeno arriba / "ANSIEDAD" grande y dorada debajo
            antes = " ".join(w for w, k in pal if not k); clave_txt = " ".join(w for w, k in pal if k)
            c["text"] = antes + chr(10) + clave_txt
            for txt, k, sep in ((antes, False, 1), (clave_txt, True, 0)):
                st = json.loads(json.dumps(base)); st["range"] = [pos, pos + len(txt) + sep]; st["font"] = ZY
                st["size"] = base.get("size", 12) * (1.75 if k else 0.85)
                st["fill"]["content"]["solid"]["color"] = [224 / 255, 184 / 255, 60 / 255] if k else [1, 1, 1]
                estilos.append(st); pos += len(txt) + sep
        else:
            for i, (w, k) in enumerate(pal):
                ln = len(w) + (1 if i < len(pal) - 1 else 0)
                st = json.loads(json.dumps(base)); st["range"] = [pos, pos + ln]; st["font"] = ZY
                st["fill"]["content"]["solid"]["color"] = [224 / 255, 184 / 255, 60 / 255] if k else [1, 1, 1]
                estilos.append(st); pos += ln
        c["styles"] = estilos; t["content"] = json.dumps(c, ensure_ascii=False)
        t["fonts"] = [{"id": "", "resource_id": ZY["id"], "path": ZY["path"], "title": "ZY Steady", "source_platform": 0}]
    pk = next((tr for tr in dj["tracks"] if tr.get("name") == "subtitulos_clave"), None)
    for sg in (pk or {}).get("segments", []):
        t = textos[sg["material_id"]]; c = json.loads(t["content"])
        for st in c["styles"]: st["font"] = ZY
        t["content"] = json.dumps(c, ensure_ascii=False)
        t["fonts"] = [{"id": "", "resource_id": ZY["id"], "path": ZY["path"], "title": "ZY Steady", "source_platform": 0}]
    contenido = json.dumps(dj, ensure_ascii=False, indent=4)
# ---------- estilo de subtitulos clonado de un proyecto tuyo (plantilla de subtitulos de CapCut) ----------
if ESTILO_CLONADO:
    import copy, uuid, time as _t
    ref = json.load(open(os.path.join(CAPCUT, SPEC["subt_estilo_de"], "draft_content.json"), encoding="utf-8"))
    R = {m["id"]: (k, m) for k, lst in ref["materials"].items() if isinstance(lst, list) for m in lst if isinstance(m, dict) and "id" in m}
    rseg = next(sg for tr in ref["tracks"] if tr["type"] == "text" for sg in tr["segments"] if R.get(sg["material_id"], ("",))[0] == "text_templates")
    rtpl = R[rseg["material_id"]][1]
    rinfo = rtpl["text_info_resources"][0]
    rtext = R[rinfo["text_material_id"]][1]
    rstyle = json.loads(rtext["content"])["styles"][0]
    rextra = [R[i] for i in rinfo["extra_material_refs"]]          # efecto + animacion
    nid = lambda: str(uuid.uuid4()).upper()
    dj = json.loads(contenido)
    dj["materials"].setdefault("text_templates", [])
    pista = next(tr for tr in dj["tracks"] if tr.get("name") == "subtitulos")
    assert len(pista["segments"]) == len(SUBT_INFO), (len(pista["segments"]), len(SUBT_INFO))
    textos = {t["id"]: t for t in dj["materials"]["texts"]}
    grupo = f"Auto_{int(_t.time() * 1000)}"
    for sg, (txt, pal) in zip(pista["segments"], SUBT_INFO):
        dur = sg["target_timerange"]["duration"]
        # texto: el del proyecto original con las palabras nuevas (reutilizo el id del material que ya existia)
        tx = textos[sg["material_id"]]; tid = tx["id"]
        nuevo = copy.deepcopy(rtext); nuevo["id"] = tid
        st = copy.deepcopy(rstyle); st["range"] = [0, len(txt)]
        nuevo["content"] = json.dumps({"text": txt, "styles": [st]}, ensure_ascii=False)
        nuevo["recognize_text"] = txt.lower(); nuevo["group_id"] = grupo
        nuevo["words"] = {"start_time": [x for _, x, _ in pal], "end_time": [y for _, _, y in pal], "text": [w for w, _, _ in pal]}
        nuevo["current_words"] = {"start_time": [], "end_time": [], "text": []}
        tx.clear(); tx.update(nuevo)
        # efecto y animacion, copias nuevas
        refs = []
        for k, rm in rextra:
            c = copy.deepcopy(rm); c["id"] = nid()
            if k == "material_animations":
                for an in c["animations"]: an["start"] = 0; an["duration"] = dur
            dj["materials"].setdefault(k, []).append(c); refs.append(c["id"])
        # plantilla
        tpl = copy.deepcopy(rtpl); tpl["id"] = nid()
        info = tpl["text_info_resources"][0]; info["id"] = nid(); info["text_material_id"] = tid
        info["extra_material_refs"] = refs; info["attach_info"]["start_time"] = 0; info["attach_info"]["duration"] = dur
        dj["materials"]["text_templates"].append(tpl)
        sg["material_id"] = tpl["id"]
        sg["extra_material_refs"] = list(reversed(refs)) if [k for k, _ in rextra][0] == "effects" else refs
        sg["clip"] = copy.deepcopy(rseg["clip"])
        sg["render_index"] = rseg.get("render_index", sg.get("render_index"))
    contenido = json.dumps(dj, ensure_ascii=False, indent=4)
for f in ("draft_content.json", "draft_info.json"):
    open(os.path.join(destino, f), "w", encoding="utf-8").write(contenido)
meta = os.path.join(destino, "draft_meta_info.json")
if os.path.exists(meta):
    mj = json.load(open(meta, encoding="utf-8")); mj["draft_name"] = SPEC["nombre"]; mj["draft_fold_path"] = destino.replace("\\", "/")
    json.dump(mj, open(meta, "w", encoding="utf-8"), ensure_ascii=False)
print(f"ok {destino}\n  {len(tramos)} tramos, {TOTAL:.1f} s, {len(bloques)} subtitulos")
