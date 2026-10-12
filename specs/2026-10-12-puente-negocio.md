# Puente local: montar el reel desde Negocio con un botón

**Fecha:** 2026-10-12 · **Estado:** spec y maqueta para aprobar

## Por qué

Hoy, en el paso Editar de Negocio (Contenido), Luismi copia una orden y la pega en su Claude Code. Quiere un
solo botón (12-10: "sí, un solo botón"). El editor no puede vivir en el servidor (CapCut, MediaPipe, las tomas
y el catálogo están en su PC), así que hace falta un puente en el PC que reciba la orden.

Respuestas de Luismi (12-10): las tomas llegan solas a **OneDrive (Ads y contenido)**; el puente vale la pena.

## Cómo funciona

```
Negocio (navegador)  --fetch-->  http://127.0.0.1:7810  (puente.py, en el PC)  -->  claude -p  (montar-reels)
```

1. **`puente/puente.py`** (solo biblioteca estándar de Python), escucha en `127.0.0.1:7810`. Arranca con
   Windows (acceso directo en Inicio que crea `instalar.ps1`, con `pythonw` para que no abra ventana).
2. Endpoints:
   - `GET /estado`: vivo, versión, carpeta de tomas, si Claude Code está instalado.
   - `GET /tomas`: los vídeos de la carpeta de tomas de los últimos 14 días, el más nuevo primero, con su
     `.encuadre.json` si ya está medido.
   - `POST /montar` `{hueco, tema, fecha, guion, montaje, toma}`: guarda `<toma>.guion.txt` y
     `<toma>.montaje.json` junto al vídeo, mide la toma (`medir_toma.py`) y lanza `claude -p` con el
     director y `montar_reel.py`. Devuelve un id de trabajo.
   - `POST /revisar` `{hueco, export}`: lanza `claude -p` con el revisor sobre el vídeo exportado.
   - `GET /trabajo/<id>`: estado (en marcha, hecho, error), las últimas líneas y el resumen final.
3. Dos botones, porque entre medias Luismi exporta en CapCut:
   - **Montar en mi PC:** el director decide y monta el borrador de CapCut.
   - **Revisar el export:** el revisor juzga el vídeo exportado y su veredicto sale en Negocio.

## Seguridad

- Solo escucha en `127.0.0.1`: nadie de fuera del PC puede llamarlo.
- CORS solo para `https://negocio.humanohibrido.es` (y `http://localhost:3000` para probar), con
  `Access-Control-Allow-Private-Network: true` (Chrome lo exige para que una web pública llame a localhost).
- **Clave del puente:** `puente_clave` en `config.json` (la genera `instalar.ps1`). Negocio la pide una vez y
  la guarda en el navegador (`localStorage`). Sin la clave, el puente no hace nada: otra web abierta en el mismo
  Chrome no puede lanzar trabajos.
- `claude -p` con `--allowedTools` cerrado: leer y escribir ficheros dentro de montar-reels y de la carpeta de
  tomas, y en Bash solo `python`, `ffmpeg` y `ffprobe`. Nada de git, red ni borrar.
- Rutas: la toma tiene que estar dentro de la carpeta de tomas (sin `..`); el puente lo comprueba.

## Negocio (hh-kpi, paso Editar)

- Si el puente responde: elegir la toma (lista de `/tomas`, la más nueva marcada) y **Montar en mi PC**; luego
  **Revisar el export** con el vídeo exportado. Progreso con las últimas líneas y el veredicto del revisor.
- Si no responde: "El puente no está encendido en tu PC" y el botón de siempre, **Copiar orden**, que no se
  quita.
- La clave se pide una vez, en el mismo paso.

## Hecho cuando

- El puente arranca solo al encender el PC y `GET /estado` responde.
- Desde negocio.humanohibrido.es, con una toma real, el botón monta el borrador en CapCut sin abrir la terminal,
  y el revisor devuelve su veredicto en Negocio.
- Sin clave o desde otro origen, el puente responde 403 (control negativo).
- Con el puente apagado, Negocio lo dice y deja copiar la orden.
