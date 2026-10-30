# Motor de render directo (ffmpeg + HyperFrames de Huashu) dentro del repo

30-10-2026. Paso 1 del plan de edición acordado con Luismi ("ok, hacemos tu orden").

## Problema

El motor que produce de verdad (Nuevos 27 y los 31 trial reels del 28 y 29-10) vivía en
`~/herramientas/nuevos27`, **sin git**, con `.bak` a mano y dependiendo de dos carpetas sueltas
(`herramientas/prueba-ads05` para `index.html`, `herramientas/reel-mister` para CSS, JS, fuentes y vendor).
Rutas fijas a `OneDrive/Ads y contenido/...`. El 30-10 Luismi movió todo a `Ads y contenido/edicion` y el
motor quedó roto (ni la toma, ni la música, ni el b-roll `0710/...` existen ya en esas rutas).

## Qué se hace

1. `motor/` en el repo con el código: `montar.py`, `mezcla.py`, `portada.py`, `preparar_voz.py`,
   `revisar_plan.py`, `subida_trial.py`, `tomas.py`, `fichas_trial.py`, `fichas_lote.py` y un único
   `montar.sh <n...>` (el antiguo `trial.sh`). Fuera: `lote.sh`, `rehacer.sh`, `optimizar.sh` (lotes de un día
   con listas fijas; `montar.sh` los cubre) y los `.bak`.
2. `motor/plantilla/`: `index.html` (de prueba-ads05), `estilo.py` (el CSS y el JS que se sacaban de
   `reel-mister/build.py`), `fonts/` (OFL, con sus licencias) y `vendor/` (GSAP + om.js, con licencia).
3. Todas las rutas en `motor/rutas.py`, leídas de `motor/config.json` (local, no se sube; ejemplo en
   `config.ejemplo.json`).
4. **Datos fuera del repo** (el repo es público y las fichas y transcripciones llevan lo que dice Luismi en
   tomas no publicadas): `fichas/`, `palabras.json` y `voz/` en `edicion/motor-datos/` (OneDrive, con copia).
   Las fichas pierden el prefijo `0710/`: ahora todo es relativo a la carpeta `edicion`.
5. Las carpetas de render `p<n>/` van a `carpeta_render` (disco local, no OneDrive: 13-17 GB por pieza
   mientras renderiza).

## No se hace aquí

- No se borra `~/herramientas/nuevos27` (76 GB, casi todo caché de fotogramas de `pm2`-`pm7`): se le
  pregunta a Luismi aparte.
- Nada de revisor, video-use ni CapCut: pasos 2-4.

## Hecho cuando

- `sh motor/montar.sh 75` desde el repo, con la config de Luismi, deja la pieza 75 en la carpeta de salida.
- Comparada con la 75 de `Trial reels 29-10`: misma duración (±0,1 s), misma loudness integrada (±0,5 LU) y
  fotogramas equivalentes a 1, 5 y 10 s.
- Commit y PR en `montar-reels`.

## Bitácora

- 30-10: spec escrito.
- 30-10: hecho. `sh motor/montar.sh 75` con la config nueva reproduce la 75 de `Trial reels 29-10`: 30,4 s las
  dos, -16,5 LUFS las dos, SSIM 1,000 a 1, 5 y 10 s (control positivo: fotograma 1 contra 10 = 0,197). El `.om`
  de reel-mister ya no se copia: no hacía falta. `om.js` es de huashu-motion (MIT) y va con su licencia.
  Siguiente: paso 2, montar la toma 75 con ChatMonteur y con video-use para comparar.
