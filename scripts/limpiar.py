# Limpieza de audio e imagen de una toma (método medido en la tanda 0710).
#   Audio: highpass 80 Hz + eq +1,5 dB a 3,2 kHz + loudnorm en 2 pasadas (I=-15, TP=-2).
#   Vídeo: hqdn3d + unsharp suave + contraste 1,04 / saturación 1,06.
#   Sin compresor ni reductor de ruido: subían el ruido de fondo.
#   python limpiar.py <toma.mp4> [salida.mp4]      (por defecto <toma>-limpia.mp4)
import json, re, subprocess, sys
import config

ENTRADA = sys.argv[1]
SALIDA = sys.argv[2] if len(sys.argv) > 2 else ENTRADA.rsplit(".", 1)[0] + "-limpia.mp4"
PRE = "highpass=f=80,equalizer=f=3200:t=q:w=1.2:g=1.5"
VID = "hqdn3d=2:1.5:4:3,unsharp=5:5:0.45,eq=contrast=1.04:saturation=1.06"

# 1ª pasada: medir
r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", ENTRADA, "-vn", "-af", f"{PRE},loudnorm=I=-15:TP=-2:LRA=11:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True)
m = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr)[-1])
ln = (f"loudnorm=I=-15:TP=-2:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
# 2ª pasada: aplicar
r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", ENTRADA, "-vf", VID, "-af", f"{PRE},{ln}",
                    *config.codec_video("alta"), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", SALIDA],
                   capture_output=True, text=True)
if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
print("ok", SALIDA, f"(volumen de entrada {m['input_i']} LUFS -> -15)")
