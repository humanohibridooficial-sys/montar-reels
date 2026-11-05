# Buscador de b-roll gratis

**Fecha:** 2026-11-05 · **Pedido por:** Luismi ("tenemos que buscar un sitio del que se saquen recursos de forma
infinita" / "meter más gastos no, la IA es capaz de hacerlo gratis")
**Rama:** `docs/buscador-broll` (spec) y luego `feat/buscador-broll` (código)

## Qué es, en una frase

Un script al que el director le pasa lo que necesita una frase ("choque hombro con hombro, juvenil, césped") y que
busca en todas las fuentes gratis con licencia comercial, baja los mejores candidatos con su licencia apuntada y
devuelve una hoja de miniaturas para elegir.

## Por qué

En las piezas 84 y 86 (04/05-11) el revisor tumbó una y otra vez planos flojos (campos de tierra, chavales sin
acción, adultos corriendo por un camino, un plato con palillos) porque buscábamos a mano en una o dos fuentes. El
mismo clip de Mixkit acabó en dos reels seguidos. No es falta de material: es que no se busca en todo a la vez.

## Decisiones de Luismi (no reabrir)

- **Sin gasto.** Nada de Envato, Storyblocks ni Artgrid. Generar vídeo con IA tampoco (cuesta créditos).
- Todo puede ir a anuncios: solo fuentes con licencia que permita uso comercial.

## Fuentes, por orden

| Fuente | Cómo | Licencia | Notas |
|---|---|---|---|
| Biblioteca propia (`motor-datos/biblioteca.json`, 189 clips) | búsqueda por `tema`/`describe` | propia o ya licenciada | primero, sin descarga |
| Biblioteca de Fran (canal `@fran.entrenador`, 1.062 vídeos) | por título/ejercicio | licencia de Luismi para republicar (CLAUDE.md, 11-09) | para fuerza, prevención, técnica |
| Pexels | API (la clave que ya use el motor, si existe) | Pexels License, comercial | |
| Pixabay | API con clave gratuita | Pixabay Content License, comercial | ⚠️ la cuenta la crea Luismi; sin clave se salta |
| Mixkit | páginas de categoría (`/free-stock-video/<tema>/`) y `assets.mixkit.co/videos/<id>/<id>-1080.mp4` | Mixkit Free License, comercial | sin API |
| Coverr | API pública | Coverr License, comercial | |
| YouTube Creative Commons | `yt-dlp` con búsqueda y filtro por el campo `license` = "Creative Commons Attribution" | CC BY: comercial **citando al autor** | ⚠️ la cita va en el caption; si Luismi no la quiere, la fuente se apaga con un interruptor |

## Lo que hace

1. **Entrada:** `python motor/buscar_broll.py "<lo que se ve>" [--n 12] [--fuentes ...] [--vertical]`.
2. **Busca** en cada fuente (traduce la frase al inglés para las de stock), descarta lo que ya está en `usados.json`
   de las últimas piezas y lo que ya está en la biblioteca.
3. **Baja vistas previas pequeñas** (360p) de los mejores N, en `motor-datos/candidatos/<consulta>/`, y hace una hoja
   de miniaturas (5 fotogramas por clip, con su id y fuente).
4. **El director mira la hoja** (lo hace él, con visión) y elige. Solo entonces se baja el elegido en 1080p a
   `3 RECURSOS/b-roll-<fuente>/`, se apunta en `biblioteca.json` con `fuente`, `id`, `url`, `licencia`, `autor`
   (obligatorio en CC BY) y `describe`, y se añade a `LICENCIA.txt` de la carpeta.
5. **Filtros fijos** (los del revisor): nada de campos de tierra, niños pequeños, marcas grandes (Barça, Nike…),
   estadios profesionales con escudo. Esto lo juzga el director en la hoja; el script solo los ordena por
   palabras clave negativas.
6. **Si la pieza usa un clip CC BY**, `montar.sh` avisa al final: "cita en el caption: <autor> (<url>)".

## Fuera de esta fase

- Generar vídeo con IA. Grabar banco propio (queda como recomendación para cuando Luismi pueda).
- Recortar automáticamente el encuadre vertical (lo sigue haciendo el director, como en la 84).

## Criterio de hecho

- Las tres consultas que fallaron en la 84 ("choque hombro con hombro juvenil", "salida de sprint en césped",
  "plato casero arroz con pollo") devuelven cada una al menos 5 candidatos que no estén en `usados.json`, con
  licencia apuntada.
- Ningún clip entra en `3 RECURSOS` sin su licencia escrita.
- El director de la próxima pieza lo usa y el revisor no tumba ningún b-roll por "flojo" o "repetido".

## Plan de tareas

1. Script `motor/buscar_broll.py` con las fuentes sin clave (biblioteca, Mixkit, Coverr, YouTube CC) y Pexels.
2. Hoja de miniaturas y descarga del elegido con su registro en `biblioteca.json` y `LICENCIA.txt`.
3. Pixabay cuando Luismi tenga la clave (`config.json`, nunca en el repo).
4. Instrucción al agente `director-montaje`: buscar con el script antes de usar un b-roll que no esté en la
   biblioteca.
5. Prueba con las tres consultas del criterio.

## Bitácora

- 05-11: spec escrito. Pendiente OK de Luismi.
