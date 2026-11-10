# ¿Vale esta toma o hay que repetirla? Mide CÓMO se dice (spec 2026-11-09-revisar-entrega) y da un veredicto con el
# motivo y el segundo, antes de que la toma pase a montaje.
#   python revisar_entrega.py <toma.mp4> [--guion guion.txt] [--sin-imagen]
# Escribe <toma>.entrega.json al lado de la toma (y <toma>.entrega.tx.json con la transcripción, para no repetirla).
# Umbrales: medición de 59 tomas del 09-11 (/guion §3b) y hallazgos de la sesión de edición. Cada comprobación entró
# solo si un caso conocido la dispara; las que no separaron (cámara baja, contraluz) están en la lista del guion.
import glob, json, os, re, subprocess, sys
import numpy as np

SR = 16000
GIRO = ("necesitas",)                       # palabra sola
GIRO_DOS = {("lo", "que"): ("hago", "trabajo"), ("si", "quieres"): None}
PAUSA_MIN = 0.5      # s antes del giro; el motor la conserva (pausaGiro, PR #76) pero no la crea
MARGEN_INICIO = 0.15  # s de silencio antes de la primera palabra
CTA_MIN_DB = -3.0    # caída de la última palabra de la toma
CAIDA_MIN_DB = -2.5  # mediana de caídas de final de frase
MANOS_MAX = 0.11     # fracción del tramo hablado con manos juntas: positivos 84 0,12, 91 0,14, 66 0,29; negativos 80 0,09, 82 0,06. Margen fino: solo aviso
ACERCA_MAX = 0.15    # cambio de tamaño de la cara en un hueco sin voz


def norm(w):
    return re.sub(r"[^\wáéíóúñü]", "", w.lower())


# ---------- voz: funciones puras (las prueba tests/test_revisar_entrega.py) ----------

def arranque(palabras, guion=None):
    """Fallos del arranque: palabras repetidas, poco margen, o las primeras palabras no son las del guion.
    El reel empieza siempre en su primera palabra entera (Luismi, 09-11), así que el arranque tiene que salir limpio."""
    out = []
    tk = [norm(p["word"]) for p in palabras[:8]]
    for n in (3, 2, 1):
        if len(tk) >= 2 * n and tk[:n] == tk[n:2 * n]:
            out.append(("repetir", palabras[0]["start"], f"repite el arranque: \"{' '.join(tk[:n])}\" dos veces"))
            break
    if guion:
        # Las 5 primeras, en orden. Caso real: la 82 dice "futbolista a minuto 60" y el guion "futbolista, minuto 60".
        g = [w for w in (norm(x) for x in guion[:5]) if w]
        dicho = [w for w in tk[:len(g)] if w]
        if dicho != g:
            k = next((i for i, (a, b) in enumerate(zip(dicho, g)) if a != b), min(len(dicho), len(g)))
            out.append(("repetir", palabras[min(k, len(palabras) - 1)]["start"],
                        f"el arranque no es el del guion: dices \"{' '.join(dicho)}\" y el guion dice \"{' '.join(g)}\""))
    if palabras and palabras[0]["start"] < MARGEN_INICIO:
        out.append(("aviso", 0.0, "la primera palabra empieza nada más grabar: deja medio segundo antes de hablar"))
    return out


def palabras_de_guion(texto):
    """Lo que se dice en un guion de /guion: sin las líneas de notas (empiezan por #) ni las marcas [ENTRE CORCHETES]."""
    lineas = [l for l in texto.splitlines() if not l.lstrip().startswith("#")]
    return re.sub(r"\[[^\]]*\]", " ", "\n".join(lineas)).split()


def giro(palabras):
    """Índice de la palabra del giro (pasado el 35 % del texto) o None."""
    # Por prioridad: "si quieres" suele ser el CTA del final ("si quieres X, empieza a seguirme"), no el giro;
    # solo cuenta si no hay "necesitas" ni "lo que hago".
    tk = [norm(p["word"]) for p in palabras]
    candidatos = [lambda i: tk[i] in GIRO] + [
        (lambda a, b, c: lambda i: i + 1 < len(tk) and tk[i] == a and tk[i + 1] == b
         and (c is None or (i + 2 < len(tk) and tk[i + 2] in c)))(a, b, c) for (a, b), c in GIRO_DOS.items()]
    for es in candidatos:
        for i in range(len(tk)):
            if i > len(tk) * 0.35 and es(i):
                return i
    return None


def silencio_antes(db, t, umbral=-20.0, ventana=1.5):
    """Segundos de silencio seguido que acaban justo antes de t, medidos en el AUDIO (dB por tramo de 20 ms, relativos
    a la voz). Hace falta porque Whisper estira las palabras hasta la siguiente: en la toma 89 hay unos 0,26 s de
    silencio antes de "necesitas" y los tiempos de palabra dan 0,00 (control del 09-11)."""
    fin = min(len(db), int((t + 0.1) / .02))
    ini = max(0, int((t - ventana) / .02))
    mejor = run = 0
    for d in db[ini:fin]:
        run = run + 1 if d < umbral else 0
        mejor = max(mejor, run)
    return mejor * 0.02


def pausa_y_frenada(palabras, db_rel=None):
    i = giro(palabras)
    if i is None or i == 0:
        return [("aviso", None, "no encuentro el giro (\"necesitas\", \"lo que hago\", \"si quieres\"): ¿la toma tiene solución?")], None
    p = palabras
    pausa = p[i]["start"] - p[i - 1]["end"]
    if db_rel is not None:
        pausa = max(pausa, silencio_antes(db_rel, p[i]["start"]))
    ra = i / max(1e-6, (p[i]["start"] - p[0]["start"]) / 60)
    rs = (len(p) - i) / max(1e-6, (p[-1]["end"] - p[i]["start"]) / 60)
    out = []
    if pausa < PAUSA_MIN:
        out.append(("repetir", p[i]["start"], f"sin pausa antes de \"{p[i]['word'].strip()}\" ({pausa:.2f} s; hace falta {PAUSA_MIN} s callado mirando a la lente)"))
    if rs / ra >= 1.0:
        out.append(("aviso", p[i]["start"], f"la solución va igual de rápida o más que el problema ({rs / ra:.2f}): [DESPACIO] desde \"{p[i]['word'].strip()}\""))
    return out, {"palabra": p[i]["word"].strip(), "t": round(p[i]["start"], 2), "pausa_s": round(pausa, 2), "vel_solucion": round(rs / ra, 2)}


def caidas_final(segmentos, db):
    """db: dB por tramo de 20 ms. Caída de la última palabra de cada frase frente a la frase."""
    def tramo(a, b):
        s = db[int(a / .02):int(b / .02)]
        return s[s > -34]
    caidas = []
    for s in segmentos:
        if len(s["words"]) < 4:
            continue
        sd, lw = tramo(s["start"], s["end"]), s["words"][-1]
        ld = tramo(lw["start"], lw["end"])
        if len(sd) > 10 and len(ld) > 2:
            caidas.append((lw["start"], lw["word"].strip(), float(np.median(ld) - np.median(sd))))
    out = []
    if caidas:
        t, w, c = caidas[-1]
        if c < CTA_MIN_DB:
            out.append(("repetir", t, f"la última frase se apaga: \"{w}\" suena {abs(c):.1f} dB más bajo que el resto [ACABA]"))
        med = float(np.median([c for _, _, c in caidas]))
        if med < CAIDA_MIN_DB:
            out.append(("aviso", None, f"los finales de frase caen {abs(med):.1f} dB de media: sostén la última palabra"))
    return out, [round(c, 1) for _, _, c in caidas]


def veredicto(fallos):
    if any(f[0] == "repetir" for f in fallos):
        return "REPETIR"
    return "VALE CON AVISOS" if fallos else "VALE"


# ---------- lo que necesita el modelo o el vídeo ----------

def _dlls_cuda():
    sp = os.path.join(sys.prefix, "Lib", "site-packages", "nvidia")
    for b in glob.glob(os.path.join(sp, "*", "bin")):
        os.add_dll_directory(os.path.abspath(b))
        os.environ["PATH"] = os.path.abspath(b) + os.pathsep + os.environ["PATH"]


def audio(toma):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", toma, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def transcribir(toma, x):
    cache = os.path.splitext(toma)[0] + ".entrega.tx.json"
    if os.path.exists(cache) and os.path.getmtime(cache) > os.path.getmtime(toma):
        return json.load(open(cache, encoding="utf-8"))
    import config
    if os.name == "nt":
        _dlls_cuda()
    from faster_whisper import WhisperModel
    disp = config.C.get("whisper_dispositivo", "auto")
    m = WhisperModel("large-v3-turbo", device=disp, compute_type="default")
    # con VAD: sin él Whisper se inventa colas ("Amén. Amén.") que falsean pausas y velocidad (medido el 09-11)
    segs, _ = m.transcribe(x, language="es", word_timestamps=True, vad_filter=True, condition_on_previous_text=False)
    out = [{"start": s.start, "end": s.end, "text": s.text.strip(),
            "words": [{"word": w.word, "start": w.start, "end": w.end} for w in (s.words or [])]} for s in segs]
    json.dump(out, open(cache, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out


def db_por_tramo(x):
    x = x.astype(np.float64) / (np.abs(x).max() + 1e-9)
    hop, win = int(SR * .02), int(SR * .04)
    return np.array([20 * np.log10(np.sqrt((x[i:i + win] ** 2).mean()) + 1e-9) for i in range(0, len(x) - win, hop)])


def imagen(toma, palabras):
    """4K y sitio para rótulos (medir_toma.py), manos juntas y acercarse sin hablar."""
    import cv2, mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    import config
    out, datos = [], {}
    aqui = os.path.dirname(os.path.abspath(__file__))
    r = subprocess.run([sys.executable, os.path.join(aqui, "medir_toma.py"), toma], capture_output=True, text=True, cwd=aqui)
    enc = os.path.splitext(toma)[0] + ".encuadre.json"
    if r.returncode == 0 and os.path.exists(enc):
        e = json.load(open(enc, encoding="utf-8"))
        datos["encuadre"] = e
        if min(int(v) for v in e["resolucion"].split("x")) < 2160:
            out.append(("aviso", None, f"grabada a {e['resolucion']}: en 4K el montaje puede sacar un segundo plano recortando"))
        if e["caben"]["rotulo_bajo_barbilla"] < 50:
            out.append(("aviso", None, f"barbilla al {e['barbilla_pct']} % de la altura: los rótulos no caben debajo; aléjate o baja la cámara"))
    else:
        # Visto el 09-11: con un vídeo 8K del móvil (HEVC girado 90°), medir_toma.py no encuentra la cara.
        out.append(("aviso", None, "no pude medir el encuadre ni la resolución (medir_toma.py no encontró la cara)"))

    manos = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=config.MANOS), running_mode=vision.RunningMode.VIDEO, num_hands=2,
        min_hand_detection_confidence=0.35, min_tracking_confidence=0.35))
    caras = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(config.MODELOS, "blaze_face_short_range.tflite"))))
    cap = cv2.VideoCapture(toma)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    paso, n, muestras = max(1, round(fps / 4)), 0, []      # 4 por segundo
    while True:
        if n % paso:                                         # grab sin retrieve: no convierte los fotogramas que se saltan
            if not cap.grab():
                break
            n += 1
            continue
        ok, fr = cap.read()
        if not ok:
            break
        h, w = fr.shape[:2]
        s = 1280 / max(w, h)                                 # en 4K la cara se detecta igual y va 4 veces más rápido
        if s < 1:
            fr = cv2.resize(fr, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
        t = n / fps
        hs = manos.detect_for_video(img, int(t * 1000)).hand_landmarks
        juntas = False
        if len(hs) == 2:
            # dos manos a la misma altura, cerca una de otra, por debajo de la barbilla y delante del cuerpo
            # (centradas): así se separan 84, 66 y 91 de 82 y 80 (calibrado el 09-11)
            c = [(np.mean([p.x for p in lm]), np.mean([p.y for p in lm])) for lm in hs]
            juntas = (abs(c[0][0] - c[1][0]) < 0.25 and abs(c[0][1] - c[1][1]) < 0.15
                      and min(c[0][1], c[1][1]) > 0.45 and 0.25 < (c[0][0] + c[1][0]) / 2 < 0.75)
        d = caras.detect(img).detections
        ancho = max(x.bounding_box.width for x in d) / img.width if d else None
        muestras.append((t, juntas, ancho))
        n += 1
    # Todo el tramo hablado, huecos entre frases incluidos: la pirámide sale sobre todo al empezar, entre frases y al
    # acabar (09-11), así que medir solo mientras habla no la ve.
    tramo = [m for m in muestras if palabras[0]["start"] - 1 <= m[0] <= palabras[-1]["end"] + 1]
    frac = sum(m[1] for m in tramo) / max(1, len(tramo))
    datos["manos_juntas_frac"] = round(frac, 2)
    if frac > MANOS_MAX:
        ts = [m[0] for m in tramo if m[1]]
        out.append(("aviso", ts[0], f"manos juntas delante el {round(100 * frac)} % del tiempo (desde el {ts[0]:.1f} s): bájalas entre frases, [PALMAS] en la solución"))
    for a, b in zip(palabras, palabras[1:]):
        if not 0.8 <= b["start"] - a["end"] <= 3:          # más de 3 s es volver a empezar la frase: ahí moverse es normal
            continue
        an = [m[2] for m in muestras if a["end"] <= m[0] <= b["start"] and m[2]]
        if len(an) >= 2 and max(an) / min(an) - 1 > ACERCA_MAX:
            out.append(("aviso", a["end"], f"te mueves hacia la cámara sin hablar entre {a['end']:.1f} y {b['start']:.1f} s: muévete hablando o quieto"))
    return out, datos


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")          # la consola de Windows rompe las tildes si no
    if len(sys.argv) < 2:
        raise SystemExit("uso: python revisar_entrega.py <toma.mp4> [--guion guion.txt] [--sin-imagen]")
    toma = sys.argv[1]
    guion = None
    if "--guion" in sys.argv:
        guion = palabras_de_guion(open(sys.argv[sys.argv.index("--guion") + 1], encoding="utf-8").read())
    x = audio(toma)
    segs = transcribir(toma, x)
    palabras = [w for s in segs for w in s["words"]]
    if len(palabras) < 5:
        raise SystemExit(f"{toma}: casi no hay voz ({len(palabras)} palabras)")
    fallos = arranque(palabras, guion)
    db = db_por_tramo(x)
    f, g = pausa_y_frenada(palabras, db - np.median(db[db > -34]))
    fallos += f
    f, caidas = caidas_final(segs, db)
    fallos += f
    datos = {"giro": g, "caidas_db": caidas}
    if "--sin-imagen" not in sys.argv:
        f, d = imagen(toma, palabras)
        fallos += f
        datos.update(d)
    v = veredicto(fallos)
    res = {"toma": os.path.basename(toma), "veredicto": v,
           "fallos": [{"tipo": a, "segundo": None if t is None else round(t, 1), "que": q} for a, t, q in fallos],
           "texto": " ".join(s["text"] for s in segs), **datos}
    salida = os.path.splitext(toma)[0] + ".entrega.json"
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{res['toma']}: {v}")
    for a, t, q in sorted(fallos, key=lambda z: (z[0] != "repetir", z[1] if z[1] is not None else 1e9)):
        print(f"  {'REPETIR' if a == 'repetir' else 'aviso  '}  {'' if t is None else f'{t:5.1f} s  '}{q}")
    print("->", salida)


if __name__ == "__main__":
    main()
