# Grafica de ENERGIA (minuto 0-90) dibujandose DETRAS de la persona, con el fondo tenido (estilo reel de referencia).
#   python grafica_detras.py <video> <ini> <fin> <salida.mp4> [titulo] [minuto_marca]
import sys, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

video, ini, fin, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
TITULO = sys.argv[5] if len(sys.argv) > 5 else "TU ENERGÍA"
MARCA = int(sys.argv[6]) if len(sys.argv) > 6 else 60
import os, config
MODEL = config.SELFIE
ANTON = os.path.join(config.FUENTES, "Anton-Regular.ttf")
BEBAS = os.path.join(config.FUENTES, "BebasNeue-Regular.ttf")
ORO, ROJO = (224, 184, 60), (239, 68, 68)
TINTE = np.array([28, 22, 70], np.float32)   # BGR: granate oscuro

cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS) or 30
W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cap.set(cv2.CAP_PROP_POS_MSEC, ini * 1000)
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=MODEL), running_mode=vision.RunningMode.VIDEO, output_confidence_masks=True))

# curva: rinde arriba hasta el 45', cae a partir del 55' (con zigzag de partido)
pts_min = [0, 8, 15, 22, 30, 38, 45, 52, 58, 62, 68, 75, 82, 90]
pts_val = [0.85, 0.92, 0.86, 0.94, 0.88, 0.92, 0.85, 0.74, 0.5, 0.28, 0.2, 0.14, 0.1, 0.06]
X0, X1, Y0, Y1 = 110, 870, 1065, 1228     # franja libre bajo la barbilla (por encima del limite 1267)
DELANTE = True
px = lambda m: X0 + (X1 - X0) * m / 90
py = lambda v: Y1 - (Y1 - Y0) * v

def capa_grafica(p):  # p: 0..1 de la curva dibujada
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    fb = ImageFont.truetype(BEBAS, 34); ft = ImageFont.truetype(ANTON, 44)
    d.rounded_rectangle([X0 - 40, Y0 - 80, X1 + 50, Y1 + 62], 22, fill=(14, 10, 24, 200))
    d.text((X0 - 10, Y0 - 72), TITULO, font=ft, fill=(255, 255, 255, 240))
    for m in (0, 45, 90):
        d.line([(px(m), Y1 + 6), (px(m), Y1 + 22)], fill=(255, 255, 255, 160), width=3)
        d.text((px(m) - 12, Y1 + 22), f"{m}'", font=fb, fill=(255, 255, 255, 200))
    d.line([(X0, Y1), (X1, Y1)], fill=(255, 255, 255, 110), width=3)
    # curva hasta p
    mmax = 90 * p; xs, ys = [], []
    for i in range(len(pts_min) - 1):
        a, b = pts_min[i], pts_min[i + 1]
        if a > mmax: break
        b2 = min(b, mmax); t = (b2 - a) / (b - a)
        v2 = pts_val[i] + (pts_val[i + 1] - pts_val[i]) * t
        if not xs: xs.append(px(a)); ys.append(py(pts_val[i]))
        xs.append(px(b2)); ys.append(py(v2))
    if len(xs) > 1:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).line(list(zip(xs, ys)), fill=ORO + (255,), width=18, joint="curve")
        c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
        d = ImageDraw.Draw(c); d.line(list(zip(xs, ys)), fill=ORO + (255,), width=8, joint="curve")
        d.ellipse([xs[-1] - 11, ys[-1] - 11, xs[-1] + 11, ys[-1] + 11], fill=(255, 255, 255, 255))
    if mmax >= MARCA:   # marca del minuto en rojo
        x = px(MARCA); d.line([(x, Y0 - 20), (x, Y1)], fill=ROJO + (230,), width=5)
        d.text((x + 12, Y0 - 78), f"{MARCA}'", font=ImageFont.truetype(ANTON, 52), fill=ROJO + (255,))
    return c

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                       *config.codec_video("alta"), "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
n, total, prev = 0, int((fin - ini) * fps), None
while n < total:
    ok, frame = cap.read()
    if not ok: break
    t = n / fps
    res = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)), int((ini + t) * 1000))
    m = cv2.GaussianBlur(np.clip((res.confidence_masks[0].numpy_view() - 0.35) / 0.3, 0, 1), (0, 0), 2.0)
    if prev is not None: m = 0.6 * m + 0.4 * prev
    prev = m
    k = min(1.0, t / 0.35)                                  # el tinte entra en 0,35 s
    fondo = frame.astype(np.float32); gris = fondo.mean(axis=2, keepdims=True)
    tenido = fondo * (1 - 0.75 * k) + (gris * 0.35 + TINTE) * 0.75 * k
    g = capa_grafica(min(1.0, max(0.0, (t - 0.25) / 2.6)))  # la curva se dibuja en 2,6 s
    ga = np.asarray(g).astype(np.float32); a = ga[..., 3:4] / 255.0
    m3 = m[..., None]; base = tenido * (1 - m3) + frame.astype(np.float32) * m3
    outf = base * (1 - a) + ga[..., [2, 1, 0]] * a
    ff.stdin.write(np.clip(outf, 0, 255).astype(np.uint8).tobytes()); n += 1
ff.stdin.close(); ff.wait(); print("ok", out, n, "fotogramas")
