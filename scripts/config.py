# Configuración del editor de reels: todas las rutas salen de aquí, nunca escritas en los scripts.
# Lee config.json de la raíz del repo (lo crea instalar.ps1 copiando config.ejemplo.json).
# Importar este módulo también pone VectCutAPI (vendor/VectCutAPI) en el path, para pyJianYingDraft.
import json, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_f = os.path.join(RAIZ, "config.json")
if not os.path.exists(_f):
    _f = os.path.join(RAIZ, "config.ejemplo.json")
C = json.load(open(_f, encoding="utf-8"))

def ruta(clave, defecto=""):
    """Ruta de la config con %VARIABLES% de Windows expandidas y relativa a la raíz del repo si no es absoluta."""
    v = os.path.expandvars(str(C.get(clave, defecto)))
    return v if os.path.isabs(v) or not v else os.path.join(RAIZ, v)

TRABAJO = ruta("carpeta_trabajo", "trabajo")                 # donde van las tomas y los resultados
TX = ruta("carpeta_transcripciones", "trabajo/transcripciones")  # tx/ = medium, tx2/ = large-v3-turbo
CAPCUT = ruta("carpeta_capcut", r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
PLANTILLA = os.path.join(CAPCUT, C.get("plantilla_capcut", "PLANTILLA-REELS"))  # un proyecto vacío que tu CapCut ya abrió
FUENTES = ruta("carpeta_fuentes", "fuentes")
MODELOS = ruta("carpeta_modelos", "modelos")
PIEZAS = ruta("carpeta_piezas", "trabajo/piezas")             # efectos de sonido y piezas reutilizables
VENDOR = os.path.join(RAIZ, "vendor", "VectCutAPI")
FUENTE_SUBT = os.path.join(FUENTES, C.get("fuente_subtitulos", "Anton-Regular.ttf"))
COLOR_CLAVE = C.get("color_clave", "#E0B83C")
COLOR_MARCA = C.get("color_marca", "#0E1F3A")
SELFIE = os.path.join(MODELOS, "selfie_segmenter.tflite")
MANOS = os.path.join(MODELOS, "hand_landmarker.task")

def codec_video(calidad="normal"):
    """Codificador de vídeo: nvenc solo si en config pone "nvenc" (tarjeta NVIDIA); si no, libx264, que va en cualquier PC."""
    if C.get("codificador", "x264") == "nvenc":
        return ["-c:v", "h264_nvenc", "-preset", "p7" if calidad == "alta" else "p5", "-cq", "17" if calidad == "alta" else "23"]
    return ["-c:v", "libx264", "-preset", "medium", "-crf", "18" if calidad == "alta" else "22"]

if os.path.isdir(VENDOR) and VENDOR not in sys.path:
    sys.path.insert(0, VENDOR)
