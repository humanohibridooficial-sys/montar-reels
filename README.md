# Editor de reels con Claude Code

Convierte las tomas que grabas con el móvil en reels verticales terminados: limpia el audio y la imagen, transcribe,
corta silencios y repeticiones, pone subtítulos, monta el proyecto en CapCut (o saca el vídeo final sin CapCut) y
revisa volumen y zona segura de anuncio. Además **aprende tu forma de editar** a partir de tus reels y de los reels
de una cuenta que quieras imitar (tu "cuenta fantasma").

Tú hablas con Claude Code en español ("edita este reel", "quita del 12 al 15", "aprende de mis reels") y él lanza
los scripts.

## Qué necesitas

- Windows 10 u 11.
- Una suscripción de Claude con **Claude Code** instalado (instrucciones en https://code.claude.com/docs).
- CapCut de escritorio, solo si quieres el proyecto editable. Sin CapCut también sale el vídeo final con subtítulos.

## Instalación (una vez)

1. Descarga este repositorio: botón verde **Code → Download ZIP** y descomprímelo, o
   `git clone https://github.com/humanohibridooficial-sys/montar-reels.git`.
2. Abre **PowerShell** en esa carpeta (en el Explorador: clic derecho en la carpeta → "Abrir en Terminal").
3. Lanza:
   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\instalar.ps1
   ```
   El instalador explica cada paso. Instala Node.js, Git, Python 3.12 y FFmpeg con winget; crea un entorno de Python
   propio en `.venv`; descarga VectCutAPI, los modelos de MediaPipe y las fuentes; crea tu `config.json`; y copia la
   skill `montar-reels` a Claude Code. Si lo vuelves a lanzar, salta lo que ya está.
4. **Paso a mano en CapCut**: abre CapCut, crea un proyecto vacío, llámalo exactamente `PLANTILLA-REELS` y cierra CapCut.
   Todos los reels se montan copiando ese proyecto.
5. (Opcional) Si quieres que busque B-roll en Pexels, pide una clave gratis en la web de Pexels (apartado "API") y ponla en
   el fichero `.env` de esta carpeta: `PEXELS_API_KEY=tu_clave`. Ese fichero no se sube nunca a GitHub.

## Primer uso

Abre Claude Code en esta carpeta (`claude` en la terminal) y dile, por ejemplo:

- "Edita este reel: C:\Videos\toma1.mp4"
- "Quita del 17 al 45,5" (segundos que ves en la esquina del vídeo de revisión)
- "Ponle subtítulos con 'calidad' y 'fuerza' en color"
- "Revisa el volumen y la zona segura del export"

Claude trabaja **una pieza cada vez** y espera tu OK antes de pasar a la siguiente.

## Que edite como tú

- **Tu estilo escrito**: rellena `mi-estilo/estilo.md` (duración, subtítulos, colores, lo que no quieres nunca).
  Claude lo lee antes de cada reel y apunta ahí cada corrección que le hagas.
- **Aprender de tus reels**: copia de 3 a 10 reels tuyos terminados a `mi-estilo/mis-reels/` y dile
  "aprende de mis reels". Mide ritmo, cortes, volumen, gancho y subtítulos, y escribe `mi-estilo/aprendido.md`.
  Si tienes proyectos de CapCut donde corregiste a mano un corte, también aprende cuánto aire dejas en cada corte.
- **Cuenta fantasma**: pega enlaces de reels que quieras imitar en `mi-estilo/referencias.txt` y dile
  "analiza mi cuenta fantasma". Los descarga **solo para analizarlos en tu ordenador** (no se republican ni se
  suben) y escribe `mi-estilo/referencias.md`. Nunca inicia sesión en Instagram.

## Problemas típicos

- **"No reconoce node / git / py / ffmpeg"** después de instalar: cierra PowerShell, abre otra ventana y vuelve a
  lanzar `.\instalar.ps1`.
- **pip falla**: lánzalo a mano con `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` y mira el error.
- **La primera transcripción tarda mucho**: descarga dos modelos de Whisper (varios GB). Solo la primera vez.
- **Mis cambios en CapCut desaparecen**: CapCut abierto sobrescribe lo que escriben los scripts. Ciérralo antes de
  montar y vuelve a abrirlo después (no ve los proyectos nuevos hasta reiniciarse).
- **¿Exporta solo?** No: CapCut no deja exportar de forma automática. Exportas tú, o usas el vídeo final sin CapCut.
- **Va lento al cortar o subtitular**: si tienes tarjeta NVIDIA, pon `"codificador": "nvenc"` en `config.json`.

## Qué hay dentro

| Carpeta | Qué |
|---|---|
| `scripts/` | Los scripts de edición (ver `docs/PROCESO-EDICION.md`) |
| `ejemplos/spec_ejemplo.py` | Un reel real como molde para montar en CapCut |
| `herramientas/` | Búsqueda de B-roll en Pexels |
| `mi-estilo/` | Tu estilo y lo que Claude aprende de ti |
| `skill/` | La skill de Claude Code (el instalador la copia) |
| `plantillas/pared-azul/` | Reel con gráficos de pared azul y cámara 3D hecho con HyperFrames (ver su README) |

No se suben a GitHub: `config.json`, `.env`, `.venv/`, `vendor/`, `modelos/`, `fuentes/`, `trabajo/` ni tus vídeos.

## Licencias de lo que se descarga

- **VectCutAPI** (https://github.com/sun-guannan/VectCutAPI), Apache 2.0, fijado a la versión `cfa4779`.
- **Fuentes** Anton, Bebas Neue y Archivo Black, de Google Fonts, licencia SIL Open Font License (el instalador
  guarda cada `OFL.txt` en `fuentes/`).
- **Modelos de MediaPipe** (selfie_segmenter y hand_landmarker), de Google, Apache 2.0.
- **B-roll**: solo vídeos de Pexels (licencia de Pexels). Música y efectos: Pixabay o Mixkit.

## Lo que NO está probado todavía

Dicho claro para que nadie se lleve una sorpresa:

- El instalador **no se ha lanzado en un ordenador limpio**: se ha comprobado su sintaxis, no una instalación entera.
- `transcribir.py` usa faster-whisper 1.2.1, que **no se ha probado en esta versión del repo**: el sistema original
  se midió con transcripciones hechas aparte. Igual con yt-dlp 2026.8.19 (`referencias.py`).
- `limpiar.py`, `subtitular.py` y `montar_reel.py` **no se han ejecutado de principio a fin** desde este repo; sí se
  comprueba que todos los scripts compilan.
- Las versiones de `requirements.txt` salen del entorno donde se editaron los reels, salvo faster-whisper y yt-dlp.
