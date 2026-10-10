# Presentaciones de b-roll compuestas sobre la toma (control al pixel):
#   partida : b-roll arriba, la persona abajo, filete dorado en medio
#   pip     : b-roll a pantalla completa y la persona hablando en una ventana redondeada
#   fundido : tu toma de fondo, entera; el b-roll encima en la mitad de arriba (o de abajo) y su borde se
#             difumina hacia tu imagen para integrarse, sin línea de corte (Luismi, 10-10)
#   python composicion.py <modo> <toma.mp4> <ini> <dur> <broll.mp4> <salida.mp4> [lado izq|der | arriba|abajo]
import sys, subprocess, json
import config
modo, toma, ini, dur, broll, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5], sys.argv[6]
lado = sys.argv[7] if len(sys.argv) > 7 else "izq"
dB = float(json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", broll], capture_output=True, text=True).stdout)["format"]["duration"])
ss_b = max(0.0, dB / 2 - dur / 2)
ORO = "0xE0B83C"
def cabeza_y(video, t, hombros=False):
    """Altura (px) de la parte alta de la cabeza en el fotograma t, con el detector de silueta."""
    import cv2, numpy as np, mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    M = config.SELFIE
    seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=M), output_confidence_masks=True))
    cap = cv2.VideoCapture(video); cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, fr = cap.read()
    m = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))).confidence_masks[0].numpy_view()
    filas = np.where((m > 0.5).sum(axis=1) > 40)[0]
    if hombros:  # fila en la que la silueta toca un lado del encuadre (por debajo de la barbilla)
        toca = np.where((m[:, :12] > 0.5).any(axis=1) | (m[:, -12:] > 0.5).any(axis=1))[0]
        return int(toca[0]) if len(toca) else 1400
    return int(filas[0]) if len(filas) else 200

if modo == "partida":
    # tu arriba (franja de 960 desde un poco por encima de la cabeza), b-roll abajo: los subtitulos caen sobre el b-roll
    cy = max(0, min(1920 - 960, cabeza_y(toma, ini + dur / 2) - 90))
    fc = (f"[0:v]trim=start={ini}:duration={dur},setpts=PTS-STARTPTS,crop=1080:960:0:{cy}[yo];"
          f"[1:v]trim=start={ss_b}:duration={dur},setpts=PTS-STARTPTS,scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960,fps=30[br];"
          f"[yo][br]vstack=2,drawbox=x=0:y=954:w=1080:h=12:color={ORO}:t=fill,"
          f"fade=t=in:st=0:d=0.12[v]")
elif modo == "pip":
    W, H = 400, 640; x = 50 if lado == "izq" else 1080 - 50 - W; y = 470
    r = 36
    mask = f"if(lte(hypot(max({r}-X,0)+max(X-(W-1-{r}),0),max({r}-Y,0)+max(Y-(H-1-{r}),0)),{r}),255,0)"
    fc = (f"[1:v]trim=start={ss_b}:duration={dur},setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30[br];"
          f"[0:v]trim=start={ini}:duration={dur},setpts=PTS-STARTPTS,crop=1080:1728:0:60,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},format=rgba[yo0];"
          f"color=black:s={W}x{H}:d={dur}:r=30,format=gray,geq=lum='{mask}'[m];[yo0][m]alphamerge[yo];"
          f"color={ORO}:s={W + 12}x{H + 12}:d={dur}:r=30,format=rgba[bo0];color=black:s={W + 12}x{H + 12}:d={dur}:r=30,format=gray,geq=lum='{mask.replace(str(r), str(r + 6))}'[mb];[bo0][mb]alphamerge[bo];"
          f"[br][bo]overlay={x - 6}:{y - 6}[t1];[t1][yo]overlay={x}:{y},fade=t=in:st=0:d=0.12[v]")
elif modo == "fundido":
    # El clip nunca te tapa la cara (Luismi, 10-10): arriba acaba donde empieza tu cabeza; abajo empieza en
    # tus hombros. Los últimos 260 px hacia tu imagen se van difuminando.
    abajo = lado == "abajo"
    DIF = 260
    ALTO = max(500, 1920 - cabeza_y(toma, ini + dur / 2, hombros=True)) if abajo else max(500, cabeza_y(toma, ini + dur / 2) + 60)
    ALTO -= ALTO % 2
    # opaco en el lado del borde de pantalla; en el lado que da a tu imagen, de opaco a transparente
    alfa = f"if(lt(Y,{DIF}),255*Y/{DIF},255)" if abajo else f"if(gt(Y,{ALTO - DIF}),255*({ALTO}-Y)/{DIF},255)"
    fc = (f"[0:v]trim=start={ini}:duration={dur},setpts=PTS-STARTPTS,fps=30[yo];"
          f"[1:v]trim=start={ss_b}:duration={dur},setpts=PTS-STARTPTS,scale=1080:{ALTO}:force_original_aspect_ratio=increase,crop=1080:{ALTO},fps=30,format=rgba[br0];"
          f"color=black:s=1080x{ALTO}:d={dur}:r=30,format=gray,geq=lum='{alfa}'[m];"
          f"[br0][m]alphamerge[br];[yo][br]overlay=0:{1920 - ALTO if abajo else 0},fade=t=in:st=0:d=0.12[v]")
else:
    raise SystemExit("modo: partida | pip | fundido")
r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", toma, "-i", broll, "-filter_complex", fc, "-map", "[v]", "-an",
                    *config.codec_video("alta"), "-pix_fmt", "yuv420p", out], capture_output=True, text=True)
if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
print("ok", out)
