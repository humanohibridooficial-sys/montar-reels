# Cuenta fantasma: descarga los reels de referencia que TÚ pegas en mi-estilo/referencias.txt (un enlace por línea)
# SOLO para analizarlos en tu ordenador. No se republican, no se suben a ningún sitio y nunca se entra en Instagram
# con tu cuenta: si un enlace necesita sesión, se salta.
#   python referencias.py            -> descarga a mi-estilo/referencias/ y lanza analizar_reels.py referencias
import os, subprocess, sys
import config

txt = os.path.join(config.RAIZ, "mi-estilo", "referencias.txt")
out = os.path.join(config.RAIZ, "mi-estilo", "referencias"); os.makedirs(out, exist_ok=True)
enlaces = [l.strip() for l in open(txt, encoding="utf-8") if l.strip().startswith("http")] if os.path.exists(txt) else []
if not enlaces: raise SystemExit(f"Pega enlaces de reels (uno por línea) en {txt}")
for u in enlaces:
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--no-playlist", "-f", "mp4/best", "--restrict-filenames",
                        "-o", os.path.join(out, "%(uploader_id)s_%(id)s.%(ext)s"), u], capture_output=True, text=True)
    print("ok" if not r.returncode else "no se pudo (puede que pida sesión)", u)
subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "analizar_reels.py"), "referencias"])
