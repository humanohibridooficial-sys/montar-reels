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
- 30-10, fase 1 hecha: `motor/preparar.py <n> <toma>`, con `preparar_voz.py` para una toma suelta y `transcribir_toma.py`.
  - Entornos: DeepFilterNet en `~/.venvs/df`, con Python 3.11 y `soundfile` (en 3.12 no hay paquete para Windows y pide Rust). faster-whisper en `~/.venvs/fw`; el audio se le pasa ya decodificado porque su PyAV es incompatible.
  - Control con la toma 75 preparada como pieza nueva:
    - 97 palabras, 100 % iguales a las del lote;
    - desfase de inicio: mediana 0,01 s y máximo 0,51 s;
    - voz limpia de la misma duración (43,65 s);
    - unos 36 s en total.
  - Restos de la prueba borrados y `palabras.json` restaurado.
- 30-10, fases 2 y 3 hechas:
  - `director-montaje` (repo e instalado en `~/.claude/agents`) escribe la ficha del motor con el catálogo de los 14 `extras` y no la entrega hasta que la puerta dice OK.
  - Botón "Montar" del puente:
    - hace preparar, director, `montar.sh` y revisor, con vuelta al director (como mucho 3 veces);
    - acaba con VIDEO, TONO, VEREDICTO y NO PUDE;
    - permiso solo para `sh <repo>/motor/montar.sh` y carpetas del motor en vez de la de CapCut.
  - Pieza = número de cámara de la DJI o el nombre del fichero.
  - La salida (`edicion/Nuevos 27`) está dentro de la carpeta de tomas del puente, así que "Revisar" y la subida a Negocio siguen igual.
  - Pruebas del puente: las 3 pasan, igual que en main.
- 30-10, fase 4 hecha:
  - La skill `editor-reels-ff360` (en `~/.claude/skills`, fuera del repo) tiene el flujo del motor. Se mantienen sus reglas, estilo, portadas y entrega; CapCut queda en "archivado". Copia de la versión anterior en el scratchpad de la sesión.
  - README: el camino de una pieza y la lista de scripts que solo usa CapCut.
  - `docs/PROCESO-EDICION.md` y `skill/SKILL.md` llevan la nota de archivado.
  - No se mueve ni se borra ningún script de CapCut.
- Sin probar de principio a fin: el botón "Montar" desde Negocio con una toma nueva real, con el director escribiendo la ficha solo. Las piezas están probadas por separado: preparar con la 75, puerta y render con las fichas de prueba, y las pruebas del puente.
- Visto de paso, sin tocar: `config.json` de la raíz apunta `carpeta_trabajo` y `carpeta_piezas` a `Ads y contenido/0710`, que se movió a `edicion`. Solo afecta al camino de CapCut.
