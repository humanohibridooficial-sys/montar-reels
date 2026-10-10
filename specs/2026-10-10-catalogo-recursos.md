# Catálogo de recursos de edición (10-10-2026)

Qué es: que la IA, al editar un reel, elija **qué recurso va en cada momento** (texto detrás de la
persona, rótulo de ejercicio, gancho con imágenes de partido, pantalla partida…) a partir de un
catálogo sacado de los reels que mejor funcionan en la cuenta fantasma, y lo monte con un script.

Primero solo para Luismi. Llevarlo a los compañeros de Kaizen (plugin, otras IA, página propia) es
otra fase y otro spec, cuando esto funcione.

## Lo que ya hay y lo que falta
- Ya hay: `referencias.py` (baja los reels de `mi-estilo/referencias.txt`), `analizar_reels.py`
  (ritmo, volumen, gancho y una hoja con los **12 primeros segundos**), `palabra_detras.py` y
  `grafica_detras.py` (texto o gráfica detrás de la persona con MediaPipe), rótulos, tarjetas,
  subtítulos, música y sonidos. La skill ya dice "cada pieza pide sus recursos".
- Falta:
  1. Ver el reel **entero**: los recursos salen a lo largo de todo el vídeo, no solo en el gancho.
  2. Un **catálogo** escrito: recurso, qué es, cuándo usarlo (qué se está diciendo en ese momento),
     con qué script se hace aquí (o "falta") y una referencia (cuenta, reel, segundo).
  3. Que la skill lo consulte al proponer el montaje de cada pieza.

## Fases (cada una se cierra con el OK de Luismi antes de la siguiente)
1. **Referencias.** Bajar los ~10 reels más vistos de las cuentas que sigue la fantasma (lista
   medida el 10-10). `analizar_reels.py` gana una hoja del reel entero (1 fotograma por segundo).
   Hecho = los 10 bajados y con su hoja.
2. **Catálogo.** Mirar las hojas y escribir `mi-estilo/recursos.md`. Hecho = cada recurso con su
   referencia real (cuenta, reel, segundo); nada sin haberlo visto.
3. **Huecos.** Por cada recurso marcado "falta", un script o una ampliación de uno existente, de uno
   en uno, mirando el resultado sobre un fotograma antes de dar nada por bueno.
4. **La skill elige.** La skill lee `recursos.md` y, en la hoja de montaje de cada pieza, propone el
   recurso por momento con su porqué. Propuesta, no receta: decide lo que dice el reel.
5. **Prueba real.** Un reel de Luismi montado con al menos dos recursos del catálogo y su OK.

## Reglas
- Las referencias son un mapa: se copia la técnica, nunca el texto ni la imagen.
- Los vídeos bajados se quedan en el ordenador (`mi-estilo/referencias/`, fuera de git).
- Gratis: yt-dlp, ffmpeg, MediaPipe, faster-whisper y CapCut por VectCutAPI.

## Bitácora
- 10-10: spec. Comprobado que yt-dlp baja reels sin sesión (el de 479.086 reproducciones, 6 MB).
- 10-10: fases 1 y 2 hechas. 10 reels bajados y con hojas del reel entero (`analizar_reels.py` gana
  `hoja_completa`). Catálogo en `mi-estilo/recursos.md` (fuera de git: nombra las cuentas de la
  fantasma): 4 recursos principales y 11 de apoyo. Faltan scripts para la palabra clave al doble de
  tamaño, tú recortado delante del clip, el reencuadre automático, el congelado con anotación y el destello.
