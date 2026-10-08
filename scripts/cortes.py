# Corte automático de una toma + vídeo de REVISIÓN (segundo original en pantalla, raya roja en cada corte).
#   python cortes.py <toma-limpia.mp4> [--fuera "17-45.5,53-58.6"] [--forzar "0.5-1.5"] [--fin 91.2] [--ini 0] [--capcut PROYECTO]
# Regla medida (tanda 0710): se conservan los tramos con palabra, desde PRE antes hasta POST después, y se unen
# si el hueco es menor que GAP. Si existe mi-estilo/aprendido.json con "pre", "post" o "gap", mandan esos valores.
# --capcut: usa los tramos que TÚ dejaste en ese proyecto de CapCut (tu corte corregido a mano).
# Salida en trabajo/<toma>/: CORTE.mp4 (para mirar), CORTE.txt (tramos y avisos) y tramos.json (para subtitular/montar).
import json, os, re, subprocess, sys, unicodedata
import config

PRE, POST, GAP = 0.10, 0.18, 0.55
_ap = os.path.join(config.RAIZ, "mi-estilo", "aprendido.json")
if os.path.exists(_ap):
    _a = json.load(open(_ap, encoding="utf-8")); PRE, POST, GAP = _a.get("pre", PRE), _a.get("post", POST), _a.get("gap", GAP)

def leer(nombre, sub):
    f = os.path.join(config.TX, sub, nombre + ".json")
    if not os.path.exists(f): return []
    return json.load(open(f, encoding="utf-8"))

def palabras(nombre):
    """Palabras de las dos transcripciones (medium + turbo); se descartan las de más de 1,2 s (turbo 'estira')."""
    w = lambda rows: [[p[0], p[1], p[2]] for r in rows for p in r["palabras"] if p[1] - p[0] <= 1.2]
    return w(leer(nombre, "tx")), w(leer(nombre, "tx2"))

def tramos_auto(nombre, fuera=(), forzar=(), fin=999.0, ini=0.0):
    med, tur = palabras(nombre); ws = med + tur
    if not ws: raise SystemExit(f"No hay transcripción de {nombre}: ejecuta antes  python scripts/transcribir.py <toma>")
    dentro = lambda t: any(a <= t <= b for a, b in fuera)
    iv = sorted([[max(ini, a - PRE), min(fin, b + POST)] for a, b, _ in ws if not dentro(a) and ini <= a < fin] + [list(x) for x in forzar])
    partes = []
    for a, b in iv:
        segs = [[a, b]]
        for x, y in fuera:
            segs = [s for p, q in segs for s in ([[p, q]] if q <= x or p >= y else [[p, min(q, x)], [max(p, y), q]]) if s[1] - s[0] > 0.05]
        partes += segs
    t = []
    for a, b in sorted(partes):
        if t and a - t[-1][1] <= GAP - PRE - POST: t[-1][1] = max(t[-1][1], b)
        elif t and a <= t[-1][1]: t[-1][1] = max(t[-1][1], b)
        else: t.append([a, b])
    return [[round(a, 2), round(b, 2)] for a, b in t]

def tramos_capcut(proyecto, pista_contiene="limpia"):
    """Los tramos de la toma que dejaste en tu proyecto de CapCut (la pista de vídeo con más trozos), unidos si se tocan."""
    j = json.load(open(os.path.join(config.CAPCUT, proyecto, "draft_content.json"), encoding="utf-8"))
    mats = {m["id"]: m.get("path", "") for m in j["materials"]["videos"]}
    best = []
    for tr in j["tracks"]:
        if tr["type"] != "video": continue
        segs = [s for s in tr["segments"] if pista_contiene in os.path.basename(mats.get(s["material_id"], "")) or "TOMA-" in os.path.basename(mats.get(s["material_id"], ""))]
        if len(segs) > len(best): best = segs
    out = []
    for s in sorted(best, key=lambda s: s["target_timerange"]["start"]):
        a = s["source_timerange"]["start"] / 1e6; b = a + s["source_timerange"]["duration"] / 1e6
        if out and abs(a - out[-1][1]) < 0.05: out[-1][1] = b
        else: out.append([a, b])
    return [[round(a, 2), round(b, 2)] for a, b in out if b - a > 0.1]

def _norm(t):
    t = unicodedata.normalize("NFD", t.lower()); t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-z0-9ñ]+", t)

def repeticiones(nombre):
    """Pistas de tomas repetidas o arranques fallidos en la transcripción de medium: una frase cuyas 4 primeras
    palabras vuelven a salir más adelante suele ser una toma que se repitió (se queda la última). Son SOLO
    propuestas: decide el usuario."""
    frases = leer(nombre, "tx"); out = []
    for i, s in enumerate(frases):
        k = _norm(s["texto"])[:4]
        if len(k) < 4: continue
        for t in frases[i + 1:i + 8]:
            if " ".join(k) in " ".join(_norm(t["texto"])):
                out.append((s["ini"], s["fin"], t["ini"], s["texto"][:60])); break
    return out

def _rangos(txt):
    return [[float(a), float(b)] for a, b in (x.split("-") for x in txt.split(",") if x.strip())] if txt else []

if __name__ == "__main__":
    a = sys.argv
    if len(a) < 2: raise SystemExit("uso: python cortes.py <toma-limpia.mp4> [--fuera a-b,...] [--forzar a-b,...] [--fin s] [--capcut PROYECTO]")
    toma = os.path.abspath(a[1]); nombre = os.path.splitext(os.path.basename(toma))[0]
    op = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    if op("--capcut"):
        tr = tramos_capcut(op("--capcut")); origen = f"tu corte en CapCut ({op('--capcut')})"
    else:
        tr = tramos_auto(nombre, _rangos(op("--fuera")), _rangos(op("--forzar")), float(op("--fin", 999)), float(op("--ini", 0)))
        origen = f"automático (aire {PRE}/{POST} s, huecos < {GAP} s)"
    D = os.path.join(config.TRABAJO, nombre); os.makedirs(D, exist_ok=True)
    json.dump(tr, open(os.path.join(D, "tramos.json"), "w"), indent=0)
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "cortar.py"), toma, json.dumps(tr), os.path.join(D, "CORTE.mp4"), nombre[:12]],
                       capture_output=True, text=True)
    rep = repeticiones(nombre)
    with open(os.path.join(D, "CORTE.txt"), "w", encoding="utf-8") as f:
        f.write(f"{nombre} · corte: {origen}\nDura {sum(b - a for a, b in tr):.1f} s. Arriba a la izquierda ves el segundo ORIGINAL de la toma;\n"
                f"la raya roja arriba marca cada corte. Para corregir: 'quita de X a Y', 'devuelve el corte de X'.\n\nTRAMOS QUE SE QUEDAN:\n")
        f.writelines(f"  {x:6.2f} - {y:6.2f}\n" for x, y in tr)
        f.write("\nPOSIBLES TOMAS REPETIDAS (propuesta, no se han quitado):\n" +
                ("".join(f"  {i:6.2f}-{j:6.2f} se repite en {k:6.2f}: \"{t}\"\n" for i, j, k, t in rep) if rep else "  ninguna detectada\n"))
    print(r.stdout.strip() or r.stderr[-600:], f"| {len(tr)} tramos | {len(rep)} posibles repeticiones | {D}")
