# Paso 4: el motor pasa a ser el camino principal y CapCut se archiva (30-10)

## Por qué
Plan de edición del 30-10, paso 4 (Luismi: "ok, hacemos tu orden"; sobre CapCut: "yo no lo veo necesario").
El motor gana la comparativa y ya tiene puertas, revisor y 14 recursos (PR 50, 51 y 52). Pero hoy solo monta las 45
tomas preparadas en lote el 28-10. Para una toma nueva no hay camino de principio a fin. El botón "Montar" de la
Máquina (`puente/puente.py`) y la skill `editor-reels-ff360` siguen mandando a CapCut con `scripts/montar_reel.py`.

## Qué se construye, por fases (cada una con su commit)
1. **Preparar una toma nueva:** `motor/preparar.py <n> <toma.mp4>`.
   - Hace la voz limpia (DeepFilterNet, en el `.venv` del repo).
   - Saca las palabras (faster-whisper, `~/.venvs/fw`) y las añade a `palabras.json`.
   - Deja un borrador de ficha con `video` y `keep` de la toma entera.

   Hecho cuando: con una toma ya conocida (la 75), la voz y las palabras salen equivalentes a las del lote. Control: mismo número de palabras ±3 % y los mismos tramos.
2. **El director escribe la ficha del motor.**
   - `director-montaje` deja de escribir specs de `montar_reel.py` y escribe la ficha: keep y quitar, b-roll, titulares, claves y `extras`.
   - El catálogo de los 14 recursos va con su cuándo y su porqué.
   - La puerta del plan es su comprobación antes de dar la ficha.
3. **Botón "Montar" de la Máquina:** `orden_montar` pasa a preparar, director, `montar.sh` y revisor. Acaba con el mp4 en la carpeta de salida, sin CapCut.
4. **Skill `editor-reels-ff360`, README y docs:**
   - El camino es el motor.
   - CapCut pasa a un apartado "archivado".
   - Los scripts de CapCut se quedan donde están; no se borran, porque `config.py`, `palabra_detras.py` y `transcribir.py` los comparten.
   - Se marca cuáles son solo de CapCut.

## Fuera
- Borrar nada de CapCut o VectCutAPI. Se archiva, no se borra.
- Cambiar la Máquina en Negocio (hh-kpi): solo cambia lo que hace el puente en este PC.

## Bitácora
- 30-10: spec. El entorno de DeepFilterNet del lote del 28-10 no aparece; se reinstala en `montar-reels/.venv`.
