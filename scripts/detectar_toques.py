# Detecta cuando se toca el movil/teleprompter: la camara se mueve. Mide el desplazamiento del FONDO
# (franja superior: arboles y cielo, sin la persona) entre fotogramas consecutivos.
#   python detectar_toques.py <video> [umbral_px]
import sys, cv2, numpy as np
video = sys.argv[1]; UMB = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS)
prev, n, filas = None, 0, []
while True:
    ok, fr = cap.read()
    if not ok: break
    g = cv2.cvtColor(cv2.resize(fr, (270, 480)), cv2.COLOR_BGR2GRAY).astype(np.float32)
    banda = np.concatenate([g[10:110, :60], g[10:110, 210:]], axis=1)  # esquinas de arriba: fondo
    if prev is not None:
        (dx, dy), resp = cv2.phaseCorrelate(prev, banda)
        filas.append((n / fps, float(np.hypot(dx, dy)) * 4, resp))  # x4: de 270 px a 1080 px
    prev, n = banda, n + 1
t = np.array([f[0] for f in filas]); m = np.array([f[1] for f in filas])
suave = np.convolve(m, np.ones(3) / 3, mode="same")
mov = t[suave > UMB]
tramos = []
for x in mov:
    if tramos and x - tramos[-1][1] <= 0.25: tramos[-1][1] = x
    else: tramos.append([x, x])
print(f"fotogramas {len(filas)}, movimiento medio {np.median(m):.2f} px, p95 {np.percentile(m, 95):.2f} px")
print("CAMARA MOVIDA (posible toque al movil/teleprompter):")
for a, b in tramos:
    sel = (t >= a) & (t <= b)
    print(f"  {a:6.2f} - {b:6.2f}   pico {m[sel].max():5.1f} px")
