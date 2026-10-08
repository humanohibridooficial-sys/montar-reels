# Palabra gigante DETRAS de la persona: fondo -> texto -> persona (silueta con MediaPipe).
# uso: python palabra_detras.py <video> <ini_s> <fin_s> <TEXTO> <salida.mp4> [color_hex] [centro_y_px]
import sys, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

video, ini, fin, texto, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
color = sys.argv[6] if len(sys.argv) > 6 else "#FFFFFF"
cy = int(sys.argv[7]) if len(sys.argv) > 7 else 430
BYN = len(sys.argv) > 8 and sys.argv[8] == "byn"  # fondo y persona en blanco y negro
import os, config
MODEL = config.SELFIE
FONT = os.path.join(config.FUENTES, "Anton-Regular.ttf")

cap = cv2.VideoCapture(video)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cap.set(cv2.CAP_PROP_POS_MSEC, ini * 1000)
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=MODEL), running_mode=vision.RunningMode.VIDEO, output_confidence_masks=True))

# texto: lo mas grande que quepa en el 92 % del ancho
rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
size = 600
while True:
    f = ImageFont.truetype(FONT, size)
    l, t, r, b = f.getbbox(texto)
    if r - l <= W * 0.92 or size < 80: break
    size -= 10

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                       *config.codec_video("alta"), "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
n, total = 0, int((fin - ini) * fps)
prev = None
while n < total:
    ok, frame = cap.read()
    if not ok: break
    if BYN: frame = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    ts = int((ini + n / fps) * 1000)
    res = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)), ts)
    m = res.confidence_masks[0].numpy_view().copy()  # probabilidad de persona
    m = cv2.GaussianBlur(np.clip((m - 0.35) / 0.3, 0, 1), (0, 0), 2.0)
    if prev is not None: m = 0.6 * m + 0.4 * prev  # suaviza el parpadeo del borde
    prev = m
    # entrada con rebote: escala 0.7 -> 1.08 -> 1.0 en 0,25 s
    tt = n / fps
    k = 1.0 if tt > 0.25 else (0.7 + 0.38 * (tt / 0.18) if tt < 0.18 else 1.08 - 0.08 * ((tt - 0.18) / 0.07))
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fk = ImageFont.truetype(FONT, max(10, int(size * k)))
    l, t, r, b = fk.getbbox(texto)
    ImageDraw.Draw(capa).text(((W - (r - l)) / 2 - l, cy - (b - t) / 2 - t), texto, font=fk, fill=rgb + (255,))
    a = np.asarray(capa).astype(np.float32)
    alpha = a[..., 3:4] / 255.0
    bg = frame.astype(np.float32)
    con_texto = bg * (1 - alpha) + a[..., [2, 1, 0]] * alpha
    m3 = m[..., None]
    outf = con_texto * (1 - m3) + bg * m3
    ff.stdin.write(outf.astype(np.uint8).tobytes())
    n += 1
ff.stdin.close(); ff.wait()
print("ok", out, n, "fotogramas, fuente", size)
