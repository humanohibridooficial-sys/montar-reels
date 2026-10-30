# Motor: segunda tanda de recursos de los referentes (30-10)

## Por qué
Segunda pasada por los 29 vídeos de referencia (16 reels de `mi-estilo/referencias`, 9 anuncios y 4 ejemplos de
Luismi). Lo que salió está en `mi-estilo/recursos.md` ("Segunda pasada"). Luismi eligió estos 7: "ok, mete los 7".
Va sobre la PR 50, que añade el campo `extras` de la ficha.

## Qué se construye (cada uno, un elemento de `extras`)
| tipo | Qué | Visto en |
|---|---|---|
| `lista` | Puntos con bala que aparecen al nombrarlos, sobre el propio plano (sin pantalla clara) | Carla (4), Cosmin |
| `pildora` | Píldora dorada con una palabra que cambia al decir cada una | Riki, MVcoach |
| `pizarra` | Campo en marino que se levanta en perspectiva sobre la cabeza y salen jugadores uno a uno | Cosmin |
| `mapa` | Palabras en zigzag unidas por una línea discontinua que se dibuja al decirlas | Carla DeMG, Dd8pk |
| `tarjetas` | Columna de tarjetas verticales con clips a un lado mientras sigue hablando | FFRJunior, Carla |
| `barrido` | El plano entra con desenfoque de movimiento al cambiar de bloque | Carla, quique |
| `logo` | FF360 gigante que se revela con un borde de luz en el cierre | luissanchez |

Cada uno:
- lleva su efecto en `mezcla.py`;
- cuenta como evento en la puerta del plan, también cada punto o palabra suelto;
- oculta los subtítulos si ocupa su sitio (lista, mapa, logo).

Colores de la marca (`estilo.md`): marino, dorado, y azul solo de filo.

## Hecho cuando
- La 75 sin `extras` sale igual que con la PR 50.
- Una prueba sobre la 75 con los 7 pasa la puerta y la revisión del fichero.
- Se mira fotograma a fotograma y la pasa `revisor-montaje`.
- Commit y PR.

## Bitácora
- 30-10: spec. Rama `feat/motor-recursos-tanda2`, que sale de `feat/motor-revisor-y-recursos` (PR 50 sin mergear).
- 30-10: los 7 escritos y vistos en vídeo (`comparativa-75/5-tu-motor-tanda-2.mp4`, prueba sobre la 75, ficha en el scratchpad).
  - La 75 sin `extras` pasa igual.
  - La prueba pasa la puerta (54 eventos) y la revisión del fichero (−16,4 LUFS, pico −2,0).
  - Visto y corregido:
    - La primera tarjeta entraba a los 12,9 s. Su cue "fuerte" cogía el primer "fuerte" de la pieza, y debía ser "fuerte#2".
    - Puerta nueva: cada punto, palabra o tarjeta cae dentro de su recurso. Control: con la cue mala, falla.
    - La línea del mapa cruzaba la cara. Ahora el mapa va en la franja de arriba (y 250-470) y la puerta lo trata como el titular (no se pueden pisar).
  - Pendiente: pasarlo por `revisor-montaje` y que lo vea Luismi.
