# Video de CORTE para revisar: solo los tramos que se quedan, con el segundo ORIGINAL de la toma
# en una esquina (para decir "corta en el 12,3") y un destello rojo de 2 fotogramas en cada corte.
#   python cortar.py <toma.mp4> '<json [[ini,fin],...]>' <salida.mp4> [etiqueta]
import sys, json, subprocess
import config
toma, tramos, out = sys.argv[1], json.loads(sys.argv[2]), sys.argv[3]
etiq = sys.argv[4] if len(sys.argv) > 4 else ""
sel = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in tramos)
inicios = [a for a, _ in tramos[1:]]
flash = "+".join(f"between(t,{a:.3f},{a + 0.07:.3f})" for a in inicios) or "0"
FONT = "C\\:/Windows/Fonts/arialbd.ttf"
vf = (f"drawbox=x=0:y=0:w=iw:h=14:color=red:t=fill:enable='{flash}',"
      f"drawtext=fontfile='{FONT}':text='{etiq}  %{{pts\\:hms}}':x=40:y=40:fontsize=46:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=12,"
      f"select='{sel}',setpts=N/FRAME_RATE/TB")
af = f"aselect='{sel}',asetpts=N/SR/TB"
r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", toma, "-vf", vf, "-af", af,
                    *config.codec_video(), "-c:a", "aac", "-b:a", "160k", out],
                   capture_output=True, text=True)
if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
print("ok", out, round(sum(b - a for a, b in tramos), 2), "s")
