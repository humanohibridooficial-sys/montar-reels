# Tú RECORTADO DELANTE del clip del que hablas: el b-roll a pantalla completa y tu silueta (MediaPipe)
# encima, abajo, más pequeña. Recurso 3 de mi-estilo/recursos.md (el hilo conductor de los reels largos de
# referencia: comentas la imagen que se ve detrás).
#   python delante_del_clip.py <toma.mp4> <ini_s> <fin_s> <broll.mp4> <salida.mp4> [lado centro|izq|der] [escala 0.62] [broll_ini_s]
# Sale sin audio, como composicion.py: la voz sigue siendo la de la toma en CapCut.
import sys, subprocess, os, numpy as np, cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
import config

toma, ini, fin, broll, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
lado = sys.argv[6] if len(sys.argv) > 6 else "centro"
k = float(sys.argv[7]) if len(sys.argv) > 7 else 0.62
b_ini = float(sys.argv[8]) if len(sys.argv) > 8 else 0.0
W, H = 1080, 1920

cap = cv2.VideoCapture(toma); fps = cap.get(cv2.CAP_PROP_FPS) or 30
cap.set(cv2.CAP_PROP_POS_MSEC, ini * 1000)
cb = cv2.VideoCapture(broll); cb.set(cv2.CAP_PROP_POS_MSEC, b_ini * 1000)
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=config.SELFIE), running_mode=vision.RunningMode.VIDEO, output_confidence_masks=True))

def a_vertical(fr):
    """Escala y recorta al centro a 1080x1920 (cubre la pantalla, como el resto de recursos)."""
    h, w = fr.shape[:2]; s = max(W / w, H / h)
    fr = cv2.resize(fr, (int(w * s + 0.5), int(h * s + 0.5)), interpolation=cv2.INTER_AREA)
    y, x = (fr.shape[0] - H) // 2, (fr.shape[1] - W) // 2
    return fr[y:y + H, x:x + W]

pw, ph = int(W * k), int(H * k)
px = {"izq": 0, "der": W - pw}.get(lado, (W - pw) // 2)
py = H - ph  # pegado abajo: la cabeza queda en el centro de la pantalla
# Degradado desde la mitad de la pantalla: el clip se va oscureciendo hacia abajo, separa tu silueta y
# deja leer los subtítulos (Luismi, 10-10).
grad = np.ones((H, W, 1), np.float32)
g0 = H // 2
grad[g0:] = np.linspace(1.0, 0.35, H - g0)[:, None, None] ** 1.3
NUCLEO = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
# Los hombros llegan al borde del encuadre original: sin esto, a los lados queda un corte vertical recto.
LADOS = np.ones((ph, pw, 1), np.float32)
r = int(pw * 0.18)
LADOS[:, :r] *= np.linspace(0, 1, r)[None, :, None] ** 1.5
LADOS[:, pw - r:] *= np.linspace(1, 0, r)[None, :, None] ** 1.5

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                       *config.codec_video("alta"), "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
n, total, prev, ultimo_b = 0, int((fin - ini) * fps), None, None
while n < total:
    ok, fr = cap.read()
    if not ok: break
    okb, b = cb.read()
    if not okb:  # el clip es más corto que el tramo: vuelve a empezar
        cb.set(cv2.CAP_PROP_POS_MSEC, b_ini * 1000); okb, b = cb.read()
    b = a_vertical(b) if okb else ultimo_b
    ultimo_b = b
    fr = a_vertical(fr)
    res = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)), int((ini + n / fps) * 1000))
    m = res.confidence_masks[0].numpy_view().copy()
    # Sin halo de croma: más exigente con lo que es persona y el borde encogido 2 px, para que no se cuele
    # la pared de detrás (con 0,35 y sin encoger quedaba un halo gris en la cabeza y las orejas).
    m = cv2.erode(np.clip((m - 0.5) / 0.25, 0, 1), NUCLEO)
    m = cv2.GaussianBlur(m, (0, 0), 1.5)
    if prev is not None: m = 0.6 * m + 0.4 * prev  # suaviza el parpadeo del borde
    prev = m
    yo = cv2.resize(fr, (pw, ph), interpolation=cv2.INTER_AREA).astype(np.float32)
    mk = cv2.resize(m, (pw, ph))[..., None] * LADOS * min(1.0, (n / fps) / 0.12)  # entra en 0,12 s
    fondo = b.astype(np.float32) * grad
    zona = fondo[py:py + ph, px:px + pw]
    # Light wrap: en el borde, la luz del clip de detrás se mete un poco en la silueta y la funde con él.
    borde = (4 * mk * (1 - mk)) * 0.55
    luz = cv2.GaussianBlur(zona, (0, 0), 10)
    yo = yo * (1 - borde) + luz * borde
    fondo[py:py + ph, px:px + pw] = zona * (1 - mk) + yo * mk
    ff.stdin.write(np.clip(fondo, 0, 255).astype(np.uint8).tobytes())
    n += 1
ff.stdin.close(); ff.wait()
print("ok", out, n, "fotogramas")
