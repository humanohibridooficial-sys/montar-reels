---
name: montar-reels
description: Edita reels verticales 9:16 a partir de tomas grabadas con el móvil (limpiar audio e imagen, transcribir, cortar silencios y repeticiones, subtitular, montar en CapCut y revisar volumen y zona segura) y aprende el estilo de edición del usuario a partir de sus reels terminados y de reels de referencia (cuenta fantasma). Úsala cuando el usuario diga "edita este reel", "monta el reel", "corta esta toma", "ponle subtítulos", "revisa el volumen", "quita de X a Y", "aprende de mis reels", "aprende cómo edito", "analiza esta cuenta", "cuenta fantasma", "quiero editar como este reel" o pase un vídeo .mp4 para editar.
---

# Montar reels

Sistema de edición en `{{REPO}}`. Todos los comandos se lanzan desde `{{REPO}}\scripts` con el Python del
entorno: `{{REPO}}\.venv\Scripts\python.exe`. Las rutas (trabajo, CapCut, fuentes, colores) salen de
`{{REPO}}\config.json`; no escribas rutas a mano en los scripts.

## Antes de editar NADA

1. Lee `{{REPO}}\mi-estilo\estilo.md` (lo que el usuario quiere) y, si existen, `mi-estilo\aprendido.md` (lo que
   se aprendió de sus reels) y `mi-estilo\referencias.md` (lo que se aprendió de su cuenta fantasma).
   Mandan sobre las reglas por defecto de abajo. Si chocan entre sí, manda `estilo.md`.
2. Si `estilo.md` está vacío y es la primera vez, ofrece rellenarlo con 5-6 preguntas cortas (tema, duración,
   subtítulos, color, música). No bloquees: si no quiere, usa los valores por defecto.

## Cómo se trabaja (no negociable)

1. **Uno a uno y con su OK.** Presenta una pieza, espera su export o su "siguiente", corrige y solo entonces pasa a
   la siguiente. Nunca despaches varias de golpe.
2. **Cada pieza pide sus recursos.** El lenguaje es común (colores, tipografía, subtítulos); los recursos (rótulos,
   B-roll, zooms, palabra detrás) se deciden por frase. No repitas el mismo truco en dos piezas seguidas.
3. **Reaprovecha lo que ya gustó.** Si una pieza estaba bien, déjala igual y retócala solo en lo repetido o en lo roto.
4. **Fallo de diseño que veas, avísalo.** No des nada por bueno sin mirar el export.

## Proceso (una toma)

| Paso | Comando | Qué deja |
|---|---|---|
| 1. Limpiar | `python limpiar.py <toma.mp4>` | `<toma>-limpia.mp4` |
| 2. Transcribir | `python transcribir.py <toma>-limpia.mp4` | `trabajo/transcripciones/tx` (medium) y `tx2` (turbo) |
| 3. Cortar | `python cortes.py <toma>-limpia.mp4` | `trabajo/<toma>-limpia/CORTE.mp4`, `CORTE.txt`, `tramos.json` |
| 4. Revisión del corte | el usuario mira `CORTE.mp4` (lleva el segundo ORIGINAL en una esquina) | |
| 5. Corregir | `python cortes.py <toma>-limpia.mp4 --fuera "17-45.5,53-58.6"` | nuevo corte |
| 6a. Final sin CapCut | `python subtitular.py <toma>-limpia.mp4 --clave "palabra1,palabra2"` | `FINAL.mp4` |
| 6b. Proyecto CapCut | `python montar_reel.py spec.json` | proyecto editable en CapCut |
| 7. Música | `python anadir_musica.py <proyecto> <musica.mp3> <vol> <desde_s>` | pista de música bajo la voz |
| 8. Export | lo hace el usuario en CapCut (no se puede automatizar) | |
| 9. Revisar | `python revisar_volumen.py <final.mp4>` | volumen y `<final>-hoja.jpg` con la zona segura |
| 10. Portadas | a partir de un fotograma real (ver abajo) | |

- En el paso 3, lee `CORTE.txt`: lista **posibles repeticiones** (frases dichas dos veces). Propón quitar la
  primera versión con `--fuera`, pero que decida el usuario mirando el vídeo.
- **Con guion es mucho mejor.** Antes de cortar, pregunta si tiene el guion. Si existe `<toma>.guion.txt` al lado
  del vídeo (una frase por línea; si usa un panel de contenido, puede descargarlo desde allí), `CORTE.txt` trae
  "CONTRA EL GUION": las líneas dichas varias veces (propón quedarse con la última toma), las frases que se salen
  del guion (posibles sobrantes o arranques fallidos) y las líneas que no se han dicho. Propónlo, no lo apliques solo.
- "Quita de X a Y" usa siempre segundos del ORIGINAL (los que se ven en la esquina del CORTE), no del vídeo cortado.
- Mira tú la hoja de fotogramas (`Read` sobre el `.jpg`) antes de decir que está bien: nada importante por encima de
  la raya roja de arriba (y 288), por debajo de la de abajo (y 1267) ni a la derecha de la amarilla (x 930).
- Para el spec de `montar_reel.py`, el molde es `{{REPO}}\ejemplos\spec_ejemplo.py` (un reel real con todos
  los recursos y los estilos ORGANICO / ANUNCIO). Claves mínimas: `nombre`, `video`, `fin`, `palabras`, `palabras_subt`, `tramos`
  (o `fuera`) y `piezas_dir`.
- Para retocar un proyecto de CapCut ya montado sin rehacerlo: `anadir_musica.py`, `anadir_sonido.py`,
  `cambiar_clip.py`, `podar_sonido.py`.

## Reglas por defecto (medidas en una tanda real de 10 reels)

- Corte: se conserva desde 0,10 s antes de la primera palabra hasta 0,18 s después de la última; dos tramos se unen
  si el hueco es menor de 0,55 s. Si existe `mi-estilo/aprendido.json`, `cortes.py` usa sus valores.
- Audio: highpass 80 Hz + eq suave a 3,2 kHz + loudnorm en dos pasadas (-15 LUFS, pico -2). Sin compresor ni
  reductor de ruido: suben el ruido de fondo.
- Subtítulos: MAYÚSCULAS, blanco con borde negro, palabra clave en el color `color_clave` de config, bloques de
  1 a 3 palabras y máximo 14 letras.
- Rótulos: PNG 1080x1920, blanco + palabra en el color clave, sombra dura, al **88 %** (que respiren).
- **Rótulo y subtítulo nunca se pisan.** En orgánico el subtítulo baja (`subt_y_bajo` -0,37); en anuncio el rótulo
  sube y el subtítulo baja a -0,255 (sin pasar de y 1267). Si la capa ocupa la parte baja, el subtítulo se oculta.
- Jerarquía (línea pequeña + palabra clave grande) en **dos textos separados**: si se mezclan tamaños en uno, CapCut
  los descoloca.
- Multicámara falso: tramos alternos al 130 % y zooms al 138 % en las frases fuertes.
- Zona segura de anuncio de Instagram: útil y 288-1267, botones a la derecha a partir de x 930. Orgánico: 250 / 420.
  Las tarjetas pequeñas de B-roll van **a la izquierda, a la altura de los ojos** (escala 0,22, x -0,60, y 0,30):
  a la derecha tapan la cara o caen bajo los botones.
- Pocos efectos de sonido y con motivo (golpe en el rótulo, tic en las listas). Más de una docena en un reel sobra.
  Ningún efecto puede pasar del final del vídeo.
- Música libre para promocionar: Pixabay o Mixkit. Volumen 0,06-0,07 con Pixabay y 0,13-0,14 con Mixkit (las de
  Pixabay suenan unos 7 dB más fuerte). **Nada de himnos ni canciones famosas**: Meta bloquea el anuncio.
- B-roll solo de Pexels (`herramientas/pexels_buscar.mjs`, necesita `PEXELS_API_KEY` en `{{REPO}}\.env`).
  Música y efectos de Mixkit o Pixabay. Nunca uses material de otras cuentas en el vídeo final.

## Trampas conocidas

- **CapCut abierto pisa los cambios**: su autoguardado sobrescribe lo que escribe `montar_reel.py`. Pide al usuario
  que cierre CapCut ANTES de montar, y que lo reinicie para ver el proyecto nuevo (no ve proyectos nuevos en caliente).
- **Exportar desde CapCut es manual**: no se puede automatizar. Si el usuario no quiere CapCut, usa `subtitular.py`.
- Nada importante detrás de la cabeza: la tapa. Ponlo delante, a la altura del pecho y grande.
- **Si existe la carpeta del proyecto destino, VectCutAPI la borra**: usa siempre un nombre nuevo (`-v2`, `-v3`).
- Para limpiar proyectos de CapCut: **mueve, no borres**, y solo con CapCut cerrado.
- Los botones de CapCut no son accesibles a la automatización. No hagas clics a ciegas: pide al usuario que abra él
  el proyecto.
- En la revisión del export, mide dónde cae el texto en píxeles: una captura a mitad de animación engaña.
- El final de la toma, cuando la mano va al móvil o al teleprompter, no se detecta bien: revísalo a ojo y corta con `--fin`.
- Las muletillas no se quitan solas. Los subtítulos pueden traer errores de transcripción: léelos antes de entregar.
- La primera transcripción descarga los modelos de Whisper (varios GB): avisa de que tarda.

## Portadas

- Su fotograma real entero, luminoso y con su fondo. **Nunca** la persona recortada y pegada sobre otro fondo ni
  fondos oscuros.
- La frase clave en caja de color con letra del color de marca, una línea en blanco encima y, si acaso, una etiqueta
  pequeña.
- El bloque de texto **debajo de la barbilla** y entero dentro del recorte 3:4 de la rejilla del perfil (y 240-1680).
- Hazlas con Pillow y `rotulos_lib.py` (fuentes y colores de `config.json`). Si se usa IA para mejorar el gesto,
  se entregan las dos versiones y la de IA lleva la etiqueta "Hecha con IA" de Meta.

## Personalización

### A. Su estilo escrito: `mi-estilo/estilo.md`
Plantilla para que el usuario diga cómo quiere sus reels. **Cada vez que el usuario corrija algo** ("no cortes tan
pegado", "la clave siempre en rojo", "más rápido"), añádelo en "Correcciones aprendidas" de `estilo.md` con la fecha,
y aplícalo desde ese momento. Si la corrección es un número (aire, hueco, tamaño, color), cámbialo también en
`aprendido.json` o en `config.json`.

### B. Aprender de sus reels
Cuando diga "aprende de mis reels" o "aprende cómo edito":
1. Pide que copie a `mi-estilo/mis-reels/` entre 3 y 10 reels suyos ya publicados (los `.mp4` exportados).
2. `python analizar_reels.py mis-reels` -> `mi-estilo/mis-reels.json` (duración, segundos por plano, palabras por
   segundo, volumen, gancho de los 3 primeros segundos, cierre) y una hoja de fotogramas por vídeo.
3. **Mira las hojas** (`Read` de cada `*-hoja.jpg`): tamaño, posición y color de los subtítulos, si usa rótulos,
   B-roll, zooms, encuadre.
4. Si tiene proyectos de CapCut donde corrigió a mano un corte automático, compáralos:
   `python aprender_corte.py <toma-limpia.mp4> <proyecto_capcut> [...]` -> `mi-estilo/aprendido.json`
   (aire antes y después de cada corte y huecos que no corta). `cortes.py` lo usa automáticamente.
5. Escribe `mi-estilo/aprendido.md`: lo medido (con los números) y lo visto en las hojas, en reglas concretas
   ("subtítulos a media altura, 2 palabras, amarillo"). No inventes: si algo no se ve, no lo pongas.
6. Enséñale el resumen y pregúntale si se reconoce. Lo que diga que no, se quita.

### C. Cuenta fantasma (reels de referencia)
Cuando diga "analiza esta cuenta", "cuenta fantasma" o "quiero editar como este":
1. Que pegue los enlaces de los reels en `mi-estilo/referencias.txt` (uno por línea).
2. `python referencias.py`: los descarga con yt-dlp a `mi-estilo/referencias/` y lanza el análisis
   (`mi-estilo/referencias.json` + hojas).
3. Mira las hojas y escribe `mi-estilo/referencias.md`: qué hace esa cuenta (ritmo, gancho, subtítulos, rótulos,
   cierre) y **qué de eso choca con `estilo.md`**, para que el usuario elija.
4. Las referencias son un mapa, no una plantilla: se copia la estructura (ritmo, tipo de gancho), nunca el texto,
   la música ni las imágenes de otra cuenta.

Reglas de la cuenta fantasma:
- Los vídeos descargados son solo para analizarlos en este ordenador. No se suben, no se republican y no salen de
  `mi-estilo/referencias/` (está fuera de git).
- **Nunca inicies sesión en Instagram** ni pidas la contraseña del usuario. Si un enlace pide sesión, se salta.
