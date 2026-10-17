# Qué permite ESTA toma antes de decidir el montaje: dónde quedan la cabeza y la barbilla, si es 4K y, con eso,
# qué recursos caben sin tapar la cara. Lo lee el director (spec 2026-10-11-material-con-aire, F6).
#   python medir_toma.py <toma.mp4> [anuncio]
# Para cada recurso da en qué % de la toma cabe. Escribe <toma>.encuadre.json al lado de la toma y lo resume en pantalla.
import sys, os, json, statistics, cv2, numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
import config

toma = sys.argv[1]; anuncio = len(sys.argv) > 2 and sys.argv[2] == "anuncio"
W, H = 1080, 1920
ZT, ZB = (288, 1267) if anuncio else (H * 0.15, H * 0.65)  # zona segura del formato (orgánico: 35 % abajo, KAIZEN.md §1)

cap = cv2.VideoCapture(toma)
ancho, alto = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS) or 30; dur = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps

def vertical(fr):  # como lo verá el montaje: cubre 1080x1920 recortando al centro
    h, w = fr.shape[:2]; s = max(W / w, H / h)
    fr = cv2.resize(fr, (int(w * s + 0.5), int(h * s + 0.5)), interpolation=cv2.INTER_AREA)
    y, x = (fr.shape[0] - H) // 2, (fr.shape[1] - W) // 2
    return fr[y:y + H, x:x + W]

seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=config.SELFIE), output_confidence_masks=True))
fd = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path=os.path.join(config.MODELOS, "blaze_face_short_range.tflite"))))
tops, barbillas = [], []
N = 24  # repartidos por toda la toma: si mezcla planos (abierto y cerca), cada uno cuenta lo suyo
for i in range(N):
    cap.set(cv2.CAP_PROP_POS_MSEC, dur * (i + 0.5) / N * 1000); ok, fr = cap.read()
    if not ok: continue
    img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(vertical(fr), cv2.COLOR_BGR2RGB))
    m = seg.segment(img).confidence_masks[0].numpy_view() > 0.5
    filas = np.where(m.sum(axis=1) > 40)[0]
    caras = fd.detect(img).detections
    if len(filas) and caras:
        bb = max(caras, key=lambda c: c.bounding_box.width).bounding_box
        tops.append(int(filas[0])); barbillas.append(int(bb.origin_y + bb.height * 1.12))
if not tops: sys.exit(f"no encuentro una cara en {toma}")
top, barbilla = statistics.median(tops), statistics.median(barbillas)
hueco_abajo = ZB - (barbilla + 40)
# Mismos umbrales que montar_reel.py y las referencias medidas. Se cuenta plano a plano: en un reel que mezcla
# distancias, el recurso cabe en los planos abiertos aunque la mediana diga que no (control con Carla, 11-10).
pruebas = {
    "texto_detras_cabeza": lambda t, b: t >= 0.22 * H,         # el texto asoma por encima de la cabeza, en zona segura
    "media_pantalla_arriba": lambda t, b: t >= 0.40 * H,       # umbral de la sección 3 de montar_reel.py
    "rotulo_bajo_barbilla": lambda t, b: ZB - (b + 40) >= 300,  # un rótulo de 2 líneas a tamaño legible
    "subtitulos_sin_rozar": lambda t, b: ZB - 130 - 70 > b + 20,
}
caben = {k: round(100 * sum(f(t, b) for t, b in zip(tops, barbillas)) / len(tops)) for k, f in pruebas.items()}
caben["dos_distancias_por_recorte"] = 100 if min(ancho, alto) >= 2160 else 0  # 4K: el primer plano sale de recortar
r = {"toma": os.path.basename(toma), "resolucion": f"{ancho}x{alto}", "fps": round(fps, 2), "duracion_s": round(dur, 1),
     "cabeza_arriba_pct": round(100 * top / H), "barbilla_pct": round(100 * barbilla / H), "hueco_bajo_barbilla_px": int(hueco_abajo),
     "caben": caben}
salida = os.path.splitext(toma)[0] + ".encuadre.json"
json.dump(r, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{r['toma']}: {r['resolucion']} a {r['fps']} fps; cabeza al {r['cabeza_arriba_pct']} %, barbilla al {r['barbilla_pct']} %")
for k, v in caben.items(): print(f"  {v:3d} % de la toma  {k.replace('_', ' ')}")
print("->", salida)
