# Tú RECORTADO DELANTE del clip del que hablas: el b-roll a pantalla completa y tu silueta (MediaPipe)
# encima, abajo. Recurso 3 de mi-estilo/recursos.md (el hilo conductor de los reels largos de referencia:
# comentas la imagen que se ve detrás).
#   python delante_del_clip.py <toma.mp4> <ini_s> <fin_s> <broll.mp4> <salida.mp4> [lado centro|izq|der] [escala auto|0.8] [broll_ini_s]
# Como en la referencia, el cuerpo SALE por el borde de abajo: nunca se ve dónde acaba el encuadre de tu toma
# (Luismi, 10-10: con los hombros fundidos parecía un fantasma y metido en un recuadro, que flotaba).
# Con escala "auto" el tamaño se calcula para que la cabeza empiece en el 60 % de la altura y la fila en la que
# tus hombros tocan el lado del encuadre caiga justo en el borde de abajo.
# Sale sin audio, como composicion.py: la voz sigue siendo la de la toma en CapCut.
import sys, subprocess, numpy as np, cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
import config

toma, ini, fin, broll, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
lado = sys.argv[6] if len(sys.argv) > 6 else "centro"
escala = sys.argv[7] if len(sys.argv) > 7 else "auto"
b_ini = float(sys.argv[8]) if len(sys.argv) > 8 else 0.0
W, H = 1080, 1920
CABEZA_EN = 0.60  # dónde empieza la cabeza en pantalla (medido en las referencias: ~60-65 % de la altura)

cap = cv2.VideoCapture(toma); fps = cap.get(cv2.CAP_PROP_FPS) or 30
cb = cv2.VideoCapture(broll); cb.set(cv2.CAP_PROP_POS_MSEC, b_ini * 1000)
opciones = lambda modo: vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=config.SELFIE),
                                                      running_mode=modo, output_confidence_masks=True)

def a_vertical(fr):
    """Escala y recorta al centro a 1080x1920 (cubre la pantalla, como el resto de recursos)."""
    h, w = fr.shape[:2]; s = max(W / w, H / h)
    fr = cv2.resize(fr, (int(w * s + 0.5), int(h * s + 0.5)), interpolation=cv2.INTER_AREA)
    y, x = (fr.shape[0] - H) // 2, (fr.shape[1] - W) // 2
    return fr[y:y + H, x:x + W]

# Medidas de la silueta en un fotograma del tramo: dónde empieza la cabeza y dónde tocan los hombros el lado.
cap.set(cv2.CAP_PROP_POS_MSEC, (ini + (fin - ini) / 2) * 1000); _ok, _fr = cap.read()
with vision.ImageSegmenter.create_from_options(opciones(vision.RunningMode.IMAGE)) as s:
    m0 = s.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(a_vertical(_fr), cv2.COLOR_BGR2RGB))).confidence_masks[0].numpy_view() > 0.5
filas = np.where(m0.sum(axis=1) > 40)[0]
cabeza = int(filas[0]) if len(filas) else 200
toca = np.where(m0[:, :12].any(axis=1) | m0[:, -12:].any(axis=1))[0]
hombros = int(toca[0]) if len(toca) else H

k = (H * (1 - CABEZA_EN)) / max(1, hombros - cabeza) if escala == "auto" else float(escala)
pw, ph = int(W * k), int(H * k)
py = H - int(hombros * k)              # la fila de los hombros, en el borde de abajo
cx = {"izq": int(W * 0.30), "der": int(W * 0.70)}.get(lado, W // 2)
px = cx - pw // 2                      # puede salirse por los lados: se recorta
print(f"cabeza en {cabeza}, hombros en {hombros} (fila de la toma) -> escala {k:.2f}, silueta desde y={py}")

# Recorte de la silueta escalada a lo que cabe en pantalla.
sx0, sy0 = max(0, -px), max(0, -py)
dx0, dy0 = max(0, px), max(0, py)
ancho, alto = min(pw - sx0, W - dx0), min(ph - sy0, H - dy0)

# Degradado suave desde la mitad: separa tu silueta del clip y deja leer los subtítulos.
grad = np.ones((H, W, 1), np.float32)
grad[H // 2:] = np.linspace(1.0, 0.6, H - H // 2)[:, None, None]
NUCLEO = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

seg = vision.ImageSegmenter.create_from_options(opciones(vision.RunningMode.VIDEO))
cap.set(cv2.CAP_PROP_POS_MSEC, ini * 1000)
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
    yo = cv2.resize(fr, (pw, ph), interpolation=cv2.INTER_LINEAR)[sy0:sy0 + alto, sx0:sx0 + ancho].astype(np.float32)
    mk = cv2.resize(m, (pw, ph))[sy0:sy0 + alto, sx0:sx0 + ancho, None] * min(1.0, (n / fps) / 0.12)  # entra en 0,12 s
    fondo = b.astype(np.float32) * grad
    zona = fondo[dy0:dy0 + alto, dx0:dx0 + ancho]
    # Light wrap: en el borde, la luz del clip de detrás se mete un poco en la silueta y la funde con él.
    borde = (4 * mk * (1 - mk)) * 0.55
    yo = yo * (1 - borde) + cv2.GaussianBlur(zona, (0, 0), 10) * borde
    fondo[dy0:dy0 + alto, dx0:dx0 + ancho] = zona * (1 - mk) + yo * mk
    ff.stdin.write(np.clip(fondo, 0, 255).astype(np.uint8).tobytes())
    n += 1
ff.stdin.close(); ff.wait()
print("ok", out, n, "fotogramas")
