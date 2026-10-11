# Material con aire: grabar de otra forma y que el motor lo aproveche

**Fecha:** 2026-10-11 · **Estado:** F1 y F6 (medida) hechas; F3-F5 esperan una toma de prueba grabada con la guía

## Por qué

La T42 v2 "está mejor pero a años luz de hacer cosas chulas" (Luismi, 11-10). Comparada con @carlabalasc,
la diferencia está sobre todo en el material: ella graba con aire alrededor, con varias distancias, cámara en
mano y la escena grabada aparte. Luismi graba un solo plano fijo muy cerca (barbilla al 78 % de la altura,
medido en la T42), así que todo acaba encima de su cara. Luismi acepta cambiar cómo graba ("sí, claro").

## Fases

| Fase | Qué | Hecho cuando |
|---|---|---|
| F1 | Guía de grabación `docs/como-grabar.html` (y PDF en su OneDrive) | Hecha 11-10 |
| F2 | ~~Texto detrás de la cabeza~~: **ya existía** (`scripts/palabra_detras.py` y `grafica_detras.py`, spec `palabra_detras`; la T42 v2 lo usa). No se rehace | — |
| F3 | **Dos distancias desde una toma en 4K**: alternar plano medio y primer plano recortado y centrado en la cara, en lugar del zoom al 130 % | Con una toma en 4K, el recorte sale nítido (sin escalar por encima del 100 %) y la cara centrada |
| F4 | **Tomas de cerca aparte**: `tomas_cerca: [ficheros]` emparejadas por la transcripción; el corte entre distancias cae en mitad de frase | Con una toma doble del gancho, el corte no repite ni salta palabras |
| F5 | **Gráficos animados con alfa** (listas que se construyen, flechas que se dibujan) en vez de PNG fijos | Primero comprobar que CapCut 9.5 respeta el alfa de un .mov/.webm; si no, ir por composición previa con ffmpeg como F2 |
| F6 | **Director sabe qué material hay**: `scripts/medir_toma.py` da en qué % de la toma cabe cada recurso y si es 4K; el director lo lanza antes de decidir | Hecha 11-10 (medida). Controles: T42 = rótulo bajo la barbilla en el 33 % y subtítulos sin rozar en el 57 %; Carla (2 reels) = 94-100 % y 100 %. El aire sobre la cabeza es parecido (62 % frente a 65-69 %): lo que separa es el sitio bajo la barbilla. Falta que el revisor lo use |

## Decisiones

- Los efectos se componen fuera de CapCut (ffmpeg + MediaPipe) y entran como material del tramo, como el
  blanco y negro: CapCut 9.5 no aplica bien lo que se le pide por el borrador (saturación, máscaras de persona).
- Texto detrás solo si hay aire: lo alto de la cabeza por debajo del 18 % de la altura. Si no, no se hace y se
  avisa (no se encoge el texto hasta que quepa).
- La marca manda: Anton blanco, la palabra clave en dorado `#E0B83C`.
