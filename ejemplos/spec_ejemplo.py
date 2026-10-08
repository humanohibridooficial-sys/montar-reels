# EJEMPLO REAL de spec para montar_reel.py: un reel orgánico de 78 s de la tanda con la que se midió este sistema.
# Sirve de molde: copia este fichero, cambia la toma, los tramos y los recursos, y lánzalo.
#   python ejemplos/spec_ejemplo.py            -> escribe trabajo/<nombre>/spec.json y monta el proyecto en CapCut
# Estructura de carpetas que espera (una por pieza dentro de la carpeta de trabajo):
#   trabajo/<carpeta>/piezas/TOMA-<n>-limpia.mp4   la toma limpia
#   trabajo/<carpeta>/piezas/*.png  *.mp4          rótulos y piezas propias
#   trabajo/<carpeta>/b-roll/01_algo.mp4 ...       B-roll de Pexels, numerado
import json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import config

TX, R, PZ = config.TX, config.TRABAJO, config.PIEZAS
# Fuente de CapCut para los subtítulos (recurso de TU CapCut, no se puede compartir). Para usarla, rellena en
# config.json "subt_fuente_capcut": {"path": ".../Fuente.ttf", "id": "<resource_id>"}; si no, None (fuente por defecto).
ZY = config.C.get("subt_fuente_capcut")

def palabras(toma):
    """Palabras de las dos transcripciones (medium y turbo) que deja scripts/transcribir.py."""
    f = lambda d: json.load(open(os.path.join(TX, d, toma + ".json"), encoding="utf-8"))
    w = lambda rows: [[p[0], p[1], p[2]] for r in rows for p in r["palabras"]]
    return w(f("tx")), w(f("tx2"))

def subt_completos(s):
    """Turbo a veces se come frases enteras: los huecos se rellenan con medium.
    Una palabra de más de 1,2 s es turbo "estirando" sobre lo que no transcribió: fuera."""
    tur = [w for w in s["palabras_subt"] if w[1] - w[0] <= 1.2]; med = [w for w in s["palabras"] if w not in s["palabras_subt"]]
    hueco = lambda t: not any(abs(a - t) < 0.03 or a <= t < b - 0.05 for a, b, _ in tur)
    norm = lambda t: t.strip().strip(".,;:!?¿¡").lower()
    igual = lambda w: any(norm(x[2]) == norm(w[2]) and abs(x[0] - w[0]) < 1.0 for x in tur)
    s["palabras_subt"] = sorted(tur + [w for w in med if hueco(w[0]) and not igual(w)]); return s

def base(nombre, toma, carpeta, n, **kw):
    med, tur = palabras(toma); D = os.path.join(R, carpeta)
    s = {"nombre": nombre, "video": os.path.join(D, "piezas", f"TOMA-{n}-limpia.mp4"), "piezas_dir": PZ,
         "palabras": med + tur, "palabras_subt": tur, "fuera": [], "subt_modo": "marca", "subt_size": 12, "subt_y": -0.23,
         "subt_max_letras": 14, "subt_desde": 0, "subt_fuente": ZY, "volumen_voz": 1.0, "sfx_auto": False, "sfx_gain": 1.0,
         "subt_jerarquia": True, "alterna_escala": 1.30, "alterna_y": -0.10, "zoom_escala": 1.38}
    s.update(kw); return subt_completos(s), D

def br(D, pre):
    B = os.path.join(D, "b-roll"); return os.path.join(B, next(x for x in os.listdir(B) if x.startswith(pre + "_")))
png = lambda D, n: os.path.join(D, "piezas", n + ".png")
pz = lambda D, n: os.path.join(D, "piezas", n)
fx = lambda nombre, t, vol=0.45, off=0.0: {"nombre": "P-" + nombre, "ini": t, "off": off, "vol": vol}  # piezas/SFX-<nombre>.wav
# Tarjeta pequeña de B-roll: a la IZQUIERDA y a la altura de los ojos. A la derecha tapa la cara o cae bajo los botones.
TARJ = dict(modo="tarjeta", escala=0.22, x=-0.60, y=0.30, rot=-5)

# Estilos medidos: subtítulo pequeño y la clave menos gigante; si hay rótulo, el subtítulo baja (orgánico) o, en
# anuncio, el rótulo sube y el subtítulo baja sin pasar de y 1267. Rótulos de texto al 88 % ("oxígeno").
AIRE = dict(subt_size=10.5, subt_clave_factor=1.55, subt_jer_sep=[0.062, -0.042], subt_y=-0.24, rotulos_escala=0.88)
ORGANICO = dict(AIRE, subt_y_bajo=-0.37)
ANUNCIO = dict(AIRE, subt_y_bajo=-0.255, rotulos_y=0.09)

# La pieza. Recursos por frase: palabra gigante DETRÁS de la persona al principio, gráfica, pantalla partida,
# un plano en B/N, datos con rótulo, objetos que se suman en una lista y CTA al final.
s, D = base("EJEMPLO-tu-calidad-ya-no-basta", "TOMA-38-limpia", "01-calidad-ya-no-basta", 38,
            tramos=[[0.42, 11.85], [16.85, 70.45], [74.8, 78.0]], fin=78.0,
            zooms=[[53.4, 55.4], [58.5, 61.0], [66.0, 70.4]],                 # frases fuertes al 138 %
            clave=["calidad", "segunda", "cambiado", "fuerte", "físico", "final"],  # palabras que salen en color
            subt_ocultar=[[16.85, 22.1]], **ORGANICO)                         # sin subtítulo mientras va la gráfica
s["palabra_detras"] = [{"clip": pz(D, "CALIDAD-detras.mp4"), "ini": 2.55}, {"clip": pz(D, "GRAFICA-energia.mp4"), "ini": 16.85}]
s["piezas"] = [{"clip": pz(D, "PARTIDA.mp4"), "ini": 22.0, "fin": 26.5},
               {"clip": pz(D, "PLANO-byn.mp4"), "ini": 34.5, "fin": 37.86, "src_ini": 1.0}]
s["broll"] = [{"clip": br(D, "04"), "ini": 46.5, "dur": 7.0, "modo": "pantalla"},
              {"clip": br(D, "02"), "ini": 24.3, "dur": 1.8, **TARJ}]
obj = lambda n, t: {"png": png(D, n), "ini": t, "fin": 66.9, "pista": "capa_" + n[:2], "anim": "pop", "tapa": True}
s["rotulos_png"] = [{"png": png(D, "R2-dato"), "ini": 48.5, "fin": 51.3}, {"png": png(D, "R4-mas-fuerte"), "ini": 53.6, "fin": 55.4},
                    obj("O1-comida", 62.36), obj("O2-fuerza", 64.52), obj("O3-sueno", 65.42),
                    {"png": png(D, "R5-cta"), "ini": 70.0}]
# Pocos efectos y con motivo: golpe en el rótulo, tic en cada elemento de la lista, cierre en la CTA.
s["sfx_extra"] = [fx("golpe-grave", 2.55, 0.55, -0.2), fx("golpe", 48.5, 0.45),
                  fx("tic", 62.36, 0.4), fx("tic", 64.52, 0.4), fx("tic", 65.42, 0.4), fx("cierre", 70.0, 0.35)]

if __name__ == "__main__":
    os.makedirs(D, exist_ok=True); f = os.path.join(D, "spec.json")
    json.dump(s, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    r = subprocess.run([sys.executable, "montar_reel.py", f], capture_output=True, text=True, cwd=os.path.join(config.RAIZ, "scripts"))
    print(s["nombre"], "->", (r.stdout.strip().splitlines() or [""])[-1], r.stderr.strip()[-800:] if r.returncode else "")
