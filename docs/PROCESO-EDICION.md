# Proceso de edición de reels (tanda 0710, 07/08-10-2026)

Datos medidos editando una tanda real de 10 reels (6 orgánicos y 4 anuncios).

## Qué hay aquí
| Fichero | Para qué |
|---|---|
| `scripts/limpiar.py` | Limpieza de audio e imagen de una toma |
| `scripts/transcribir.py` | Transcripción con whisper medium (`tx`) y large-v3-turbo (`tx2`) |
| `scripts/cortes.py` + `scripts/cortar.py` | Corte: tramos que se quedan y vídeo de REVISIÓN (segundo original en pantalla, raya roja en cada corte) |
| `scripts/subtitular.py` | Vídeo final sin CapCut: corte + subtítulos quemados con ffmpeg |
| `scripts/montar_reel.py` | Spec JSON → proyecto de CapCut escritorio (pyJianYingDraft). Molde: `ejemplos/spec_ejemplo.py` |
| `scripts/capas_lib.py`, `scripts/rotulos_lib.py` | Rótulos PNG 1080x1920 (Anton, blanco + color clave, color de marca) |
| `scripts/anadir_musica.py`, `cambiar_clip.py`, `anadir_sonido.py`, `podar_sonido.py` | Retocar un proyecto ya montado sin regenerarlo |
| `scripts/revisar_volumen.py` | Volumen del export y hoja de fotogramas con la zona segura |
| `scripts/analizar_reels.py`, `aprender_corte.py`, `referencias.py` | Personalización: aprender de tus reels y de tu cuenta fantasma |
| `herramientas/` | Pexels (B-roll). Clave desde `.env`, nunca impresa |
| `modelos/` | MediaPipe selfie + manos (los descarga el instalador) |

## Pasos
1. **Limpieza** (ffmpeg): `highpass=f=80,equalizer=f=3200:t=q:w=1.2:g=1.5` + `loudnorm` 2 pasadas (I=-15, TP=-2). Vídeo `hqdn3d=2:1.5:4:3,unsharp=5:5:0.45,eq=contrast=1.04:saturation=1.06`. Sin compresor ni reductor de ruido: subían el ruido.
2. **Transcripción**: faster-whisper medium (conserva repeticiones) + large-v3-turbo (mejor texto). Subtítulos con turbo, huecos rellenados con medium, palabras de más de 1,2 s descartadas (turbo "estira" sobre lo que no oyó).
3. **Corte**: tramos con palabra (−0,10 s / +0,18 s), unidos si el hueco es < 0,55 s. Repeticiones y falsos arranques: a mano, con rangos "fuera". Resultado: vídeo de revisión → el usuario dice "quita de X a Y".
4. **Montaje** en CapCut o, para la web, subtítulos quemados con ffmpeg (CapCut no se puede exportar de forma automática).
5. **Revisión del export**: ebur128 (objetivo ≈ −15 LUFS, pico ≤ −1 dBTP) y hoja de fotogramas con la zona segura.

## Lo que falla o cuesta
- El final de toma cuando la mano va al móvil o al teleprompter: MediaPipe manos y la detección de movimiento de cámara apenas lo ven. Hoy se ajusta a mano.
- Muletillas: no se quitan automáticamente.
- CapCut: proyecto abierto = el autoguardado pisa cambios externos; no ve proyectos nuevos hasta reiniciar; sus botones no son accesibles a la automatización.
- Subtítulos con errores puntuales de la transcripción (tildes, palabras de más): léelos antes de entregar.

## Estilo y zona segura
- Subtítulos: Anton por defecto (ZY Steady, la de CapCut, solo si la tienes instalada), MAYÚSCULAS, blanco con borde negro, clave en dorado; bloques de 1-3 palabras y máximo 14 letras; jerarquía en DOS textos (si se mezclan tamaños en uno, CapCut los descoloca).
- Anuncio Instagram: útil y 288-1267, botones en x > 930. Orgánico: 250 / 420.
- Nada importante detrás de la cabeza: se tapa (pasó con un "90'" y un "70'" gigantes).
- B-roll solo Pexels; música Mixkit / Pixabay (comercial, sin atribución); efectos Mixkit, pocos y con motivo.
