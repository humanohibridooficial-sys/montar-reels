# Compartir el editor con gente que no sabe nada de ordenadores

2026-11-12. Luismi: "y como se le envio a compañeros", "version gente que no tiene ni puta idea".

## Problema (medido el 12-11 contra `origin/main` d7a4d03)

Lo que se instala hoy un compañero es el camino viejo de CapCut, no el motor:

- `skill/SKILL.md` es `montar-reels` con CapCut. El flujo del motor solo vive en la skill local de Luismi.
- `instalar.ps1` no crea los entornos que pide `motor/preparar.py`: DeepFilterNet (Python 3.11) y faster-whisper.
- El motor necesita `om` de huashu-motion. En el PC de Luismi es la 0.3.1; en npm solo hay 0.1.x y 0.4.0, así que
  `npx huashu-motion` instalaría una versión nunca probada.
- `motor/config.json` no lo crea nadie y su ejemplo usa las carpetas de OneDrive de Luismi.
- `mezcla.py` falla si falta un efecto o la música: esos ficheros están en el OneDrive de Luismi, no en el repo.
  Son de Mixkit, cuya licencia no deja redistribuirlos sueltos: no se pueden subir al repo público.
- `comprobar.ps1` da FALLO sin CapCut y su plantilla, aunque CapCut está archivado.
- Hay que abrir PowerShell y escribir comandos: para alguien que no sabe, eso ya es un muro.

## Qué se hace

1. **Doble clic**: `1 INSTALAR.bat` (lanza `instalar.ps1` sin tocar la política) y `2 EDITAR.bat` (abre Claude Code
   en la carpeta). Nadie escribe comandos.
2. **`instalar.ps1`, paso nuevo "Motor"**:
   - Python 3.11 y Chrome por winget si faltan.
   - `.venv-df` (3.11): `torch==2.5.1+cpu torchaudio==2.5.1+cpu deepfilternet==0.5.6 numpy==1.26.4 soundfile==0.14.0`,
     las mismas versiones que el entorno con el que se montaron los reels.
   - `.venv-fw` (3.12): `faster-whisper==1.2.1`.
   - huashu-motion clonado en `vendor/huashu-motion` en la etiqueta `v0.3.1` (la que usa Luismi), y `motor/om`
     que lo lanza.
   - `motor/config.json` con carpetas en `Vídeos\Reels\` (1 TOMAS EN BRUTO, 2 PARA SUBIR, 3 RECURSOS, motor-datos)
     y el render en `%USERPROFILE%\reels-render` (13-17 GB por pieza mientras renderiza).
   - Efectos y música de Mixkit descargados a `3 RECURSOS` en el PC de cada uno (no se redistribuyen), con los ids
     de `SFX-P-LICENCIA.txt` y `LICENCIA-MUSICA.txt` de Luismi.
3. **`mezcla.py` aguanta lo que falte**: un efecto que no existe se salta con aviso; sin la música de la ficha usa la
   primera de `MUSICA/`, y sin ninguna monta sin música. Con todos los ficheros (el PC de Luismi) sale igual que antes.
4. **`comprobar.ps1`**: CapCut pasa a aviso; comprueba los dos entornos, `om`, Chrome y `motor/config.json`.
5. **`skill/SKILL.md`**: el flujo del motor (preparar, director, montar, revisor), sin las reglas de FF360.
6. **README y `docs/PASO-A-PASO.md`** reescritos para alguien que no ha abierto una terminal nunca.
7. **La guía web** (https://claude.ai/artifact/1V1yqxndfSsYgpJYmBuqce) al día con lo mismo.

## Qué NO se hace

- No se toca el PC de Luismi: sus `~/.venvs/df` y `~/.venvs/fw` siguen siendo los suyos; los nuevos van dentro del repo.
- No se suben efectos, música ni el PACK DE RECURSOS 2.0 (comprado, no redistribuible).

## Cómo se verifica

- Sintaxis de `instalar.ps1` y `comprobar.ps1` con el parser de PowerShell.
- `mezcla.py`: un efecto que no existe se salta (control positivo: con el fichero, entra).
- ⛔ Falta lo importante: **instalarlo en un Windows limpio** (otro usuario de Windows o el PC de un compañero).
  Hasta entonces no está probado que un novato llegue al final.

## Bitácora

- 12-11: spec y rama `feat/compartir-para-novatos` (PR #81).
- 12-11: #81 y #82 mergeadas. Rama `feat/guia-recursos`: sin `perfil.json` el montaje para (antes salía la tarjeta de @nutretufutbol); el buscador de b-roll no usa el canal de Fran con `"fran": false` (lo ponen los instaladores; en el PC de Luismi sigue igual); el director usa la marca del perfil, no FF360; guía de carpetas, b-roll, LUTs, sonido y programas. Medido: `montar.py 74x` da index.html y plan.json idénticos a main con el perfil de Luismi, y sin perfil para con el aviso.
- 12-11: Mac, rama `feat/editor-en-mac`. Luismi: "si hazlo para mac tambien". `instalar.sh`/`comprobar.sh` con
  Homebrew y doble clic en `.command`. Solo Apple M1+ y macOS 14+: medido en PyPI que torch 2.5.1, DeepFilterLib
  0.5.6, mediapipe 1.1.0, ctranslate2 4.8.3 y av 19.0.1 tienen rueda `macosx arm64`, y onnxruntime 1.30 y av piden
  macOS 14. `rutas.py` elige `bin/python` fuera de Windows. `montar.sh` usa el Python del editor si el `python` del
  sistema no tiene numpy y PIL (eso fallaba también en un Windows recién instalado; en el PC de Luismi no cambia
  nada, su `python` las tiene). Sin probar en ningún Mac.
