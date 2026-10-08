# Dos hojas de puerta (azul marino con filo dorado) que se CIERRAN sobre la persona o se ABREN con luz dorada.
#   python puertas.py <video> <ini> <fin> <salida.mp4> cerrar|abrir <t_accion_rel> [cierre_max 0..0.5]
# cerrar: entran desde los lados y llegan a cierre_max en t_accion (portazo); se retiran al final.
# abrir : empiezan en cierre_max y se abren del todo en t_accion, con un haz de luz dorada.
import sys, subprocess, numpy as np, cv2
import config

video, ini, fin, out, modo = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
TA = float(sys.argv[6]); CMAX = float(sys.argv[7]) if len(sys.argv) > 7 else 0.31
cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS) or 30
W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cap.set(cv2.CAP_PROP_POS_MSEC, ini * 1000)
ORO = np.array([60, 184, 224], np.float32)  # BGR

# textura de la hoja: degradado azul marino -> negro con paneles en relieve
def hoja():
    h = np.zeros((H, W // 2, 3), np.float32)
    g = np.linspace(1.0, 0.35, W // 2)[None, :, None]
    h[:] = np.array([95, 58, 30], np.float32) * g             # #1E3A5F en BGR
    for y0, y1 in ((200, 820), (900, 1700)):                   # dos cuarterones
        h[y0:y0 + 6, 60:W // 2 - 60] += 40; h[y1 - 6:y1, 60:W // 2 - 60] -= 25
        h[y0:y1, 60:66] += 40; h[y0:y1, W // 2 - 66:W // 2 - 60] -= 25
    return np.clip(h, 0, 255)
HOJA = hoja()

def ease(x): x = min(1.0, max(0.0, x)); return 1 - (1 - x) ** 3

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                       *config.codec_video("alta"), "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
n, total = 0, int((fin - ini) * fps); dur = fin - ini
while n < total:
    ok, fr = cap.read()
    if not ok: break
    t = n / fps; f = fr.astype(np.float32)
    if modo == "cerrar":
        if t <= TA: c = CMAX * ease(t / TA)
        elif t <= dur - 0.35: c = CMAX
        else: c = CMAX * (1 - ease((t - (dur - 0.35)) / 0.35))
        luz = 0.0
    else:
        c = CMAX * (1 - ease((t - (TA - 0.45)) / 0.45)) if t > TA - 0.45 else CMAX * ease(t / 0.25)
        luz = max(0.0, 1 - abs(t - TA) / 0.5)                 # destello dorado al abrirse
    w = int(W * c)
    # sombra de las hojas sobre el plano
    if w > 0:
        sombra = np.ones((H, W, 1), np.float32)
        for x in range(min(60, W // 2 - w)):
            k = 0.55 * (1 - x / 60); sombra[:, w + x] *= 1 - k; sombra[:, W - w - 1 - x] *= 1 - k
        f *= sombra
        f[:, :w] = HOJA[:, W // 2 - w:]                        # hoja izquierda (su canto interior se ve)
        f[:, W - w:] = HOJA[:, ::-1][:, :w]                    # hoja derecha, simetrica
        for x0 in (w - 5, W - w):                              # filo dorado con brillo
            f[:, max(0, x0):x0 + 5] = ORO
    if luz > 0:                                                # haz de luz dorada desde el centro
        xs = np.abs(np.arange(W) - W / 2) / (W / 2)
        haz = np.clip(1 - xs * 2.2, 0, 1)[None, :, None] ** 2 * luz
        f = f * (1 - 0.5 * haz) + (ORO * 1.15) * 0.5 * haz + 60 * haz
    ff.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes()); n += 1
ff.stdin.close(); ff.wait(); print("ok", out, n, "fotogramas")
