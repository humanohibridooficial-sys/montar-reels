# Recorre una toma y marca los tramos en que una mano se acerca a la camara o sube hacia el movil/teleprompter.
#   python detectar_manos.py <video> [fps_muestreo]
# Salida: tabla por muestra (t, tamano de la mano, altura) y tramos sospechosos.
import sys, json, cv2, numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

video = sys.argv[1]; FS = float(sys.argv[2]) if len(sys.argv) > 2 else 10
import config
MODEL = config.MANOS
det = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL), running_mode=vision.RunningMode.VIDEO, num_hands=2,
    min_hand_detection_confidence=0.35, min_tracking_confidence=0.35))
cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS); paso = max(1, round(fps / FS))
filas, n = [], 0
while True:
    ok, fr = cap.read()
    if not ok: break
    if n % paso == 0:
        t = n / fps
        r = det.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)), int(t * 1000))
        manos = []
        for lm in r.hand_landmarks:
            xs = [p.x for p in lm]; ys = [p.y for p in lm]
            manos.append({"area": (max(xs) - min(xs)) * (max(ys) - min(ys)), "top": min(ys), "cx": (max(xs) + min(xs)) / 2})
        filas.append({"t": round(t, 2), "manos": manos})
    n += 1
# sospechosa: mano grande (cerca de camara) o mano por encima del pecho (top < 0.55)
sosp = [f["t"] for f in filas if any(m["area"] > 0.03 or m["top"] < 0.55 for m in f["manos"])]
tramos = []
for t in sosp:
    if tramos and t - tramos[-1][1] <= 0.35: tramos[-1][1] = t
    else: tramos.append([t, t])
json.dump(filas, open(video + ".manos.json", "w"), indent=0)
print("muestras", len(filas), "| con mano visible", sum(1 for f in filas if f["manos"]))
print("TRAMOS SOSPECHOSOS (mano cerca o alta):")
for a, b in tramos:
    mx = max((m["area"] for f in filas if a <= f["t"] <= b for m in f["manos"]), default=0)
    tp = min((m["top"] for f in filas if a <= f["t"] <= b for m in f["manos"]), default=1)
    print(f"  {a:6.2f} - {b:6.2f}   area max {mx:.3f}   altura min {tp:.2f}")
