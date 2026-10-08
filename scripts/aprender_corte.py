# Aprende TU forma de cortar comparando el corte automático con el que dejaste corregido en CapCut.
#   python aprender_corte.py <toma-limpia.mp4> <proyecto_capcut_corregido> [<toma2> <proyecto2> ...]
# Mide, sobre las palabras de la transcripción: cuánto aire dejas antes de la primera palabra de cada tramo (pre),
# después de la última (post) y qué huecos sin voz no cortas (gap). Escribe la mediana en mi-estilo/aprendido.json,
# que cortes.py usa a partir de entonces en lugar de 0,10 / 0,18 / 0,55.
import json, os, sys
import config, cortes

pares = list(zip(sys.argv[1::2], sys.argv[2::2]))
if not pares: raise SystemExit("uso: python aprender_corte.py <toma-limpia.mp4> <proyecto_capcut> [...]")
pre, post, huecos = [], [], []
for toma, proyecto in pares:
    nombre = os.path.splitext(os.path.basename(toma))[0]
    med, tur = cortes.palabras(nombre); ws = sorted(med + tur)
    tr = cortes.tramos_capcut(proyecto)
    for a, b in tr:
        dentro = [w for w in ws if a - 0.05 <= w[0] and w[1] <= b + 0.05]
        if not dentro: continue
        pre.append(round(dentro[0][0] - a, 3)); post.append(round(b - dentro[-1][1], 3))
        # huecos sin voz que dejaste DENTRO del tramo (no los cortaste)
        huecos += [round(y[0] - x[1], 3) for x, y in zip(dentro, dentro[1:]) if y[0] - x[1] > 0.2]
    print(f"{nombre}: {len(tr)} tramos tuyos")
mediana = lambda l: round(sorted(l)[len(l) // 2], 2) if l else None
ap = os.path.join(config.RAIZ, "mi-estilo", "aprendido.json")
prev = json.load(open(ap, encoding="utf-8")) if os.path.exists(ap) else {}
nuevo = {"pre": max(0.0, mediana(pre) or 0.10), "post": max(0.0, mediana(post) or 0.18),
         "gap": max(0.3, round((sorted(huecos)[int(len(huecos) * 0.9)] if huecos else 0.55), 2)),
         "muestras": len(pre), "tomas": [os.path.basename(t) for t, _ in pares]}
prev.update(nuevo)
json.dump(prev, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("aprendido:", json.dumps(nuevo, ensure_ascii=False), "->", ap)
