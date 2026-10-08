# Revisión del vídeo exportado antes de publicar:
#   1) volumen con ebur128 (objetivo ~ -15 LUFS integrado, pico verdadero <= -1 dBTP)
#   2) hoja de fotogramas (uno cada 2 s) con la zona segura de anuncio dibujada: y 288 y 1267, botones a partir de x 930
#   python revisar_volumen.py <video.mp4>     -> imprime el volumen y deja <video>-hoja.jpg
import re, subprocess, sys

v = sys.argv[1]
r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", v, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
resumen = r.stderr[r.stderr.rfind("Summary:"):]
I = re.search(r"I:\s+(-?[\d.]+) LUFS", resumen); P = re.search(r"Peak:\s+(-?[\d.]+) dBFS", resumen)
li, pk = (float(I.group(1)) if I else None), (float(P.group(1)) if P else None)
print(f"volumen integrado: {li} LUFS (objetivo -15) | pico: {pk} dBTP (máximo -1)")
if li is not None and abs(li + 15) > 1.5: print("  aviso: el volumen se aleja más de 1,5 LU del objetivo")
if pk is not None and pk > -1: print("  aviso: el pico pasa de -1 dBTP: puede saturar en el móvil")

hoja = v.rsplit(".", 1)[0] + "-hoja.jpg"
vf = ("fps=1/2,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
      "drawbox=x=0:y=288:w=1080:h=4:color=red@0.9:t=fill,drawbox=x=0:y=1267:w=1080:h=4:color=red@0.9:t=fill,"
      "drawbox=x=930:y=0:w=4:h=1920:color=yellow@0.9:t=fill,scale=270:480,tile=6x4:padding=6:color=black")
r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", v, "-vf", vf, "-frames:v", "1", hoja], capture_output=True, text=True)
print("hoja de fotogramas:", hoja if not r.returncode else r.stderr[-400:])
