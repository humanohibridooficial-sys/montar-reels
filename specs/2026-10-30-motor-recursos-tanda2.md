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
- 30-10, primera revisión con `revisor-montaje`: "no se puede enseñar". Corregido y visto en vídeo:
  - El FF360 tapaba la boca. Ahora va en el pecho, en el sitio del subtítulo, y dura 0,8 s o más.
  - Las tarjetas estaban en la columna de botones de IG y pisaban el subtítulo. Ahora van a la izquierda, a 190 px, por encima del subtítulo.
  - La pizarra se apoyaba en el cráneo y un jugador salía volando (GSAP escala SVG desde 0,0). Ahora es más pequeña, va por encima de la cabeza y los jugadores crecen desde su centro.
  - La píldora duplicaba el subtítulo en dorado. Ahora ocupa su sitio y el subtítulo se oculta.
  - El mapa se leía mal sobre el cielo y la línea llegaba antes que la palabra. Ahora va en caja marino y la línea sale tras la palabra.
  - La lista sube a 64 px con sombra dura.
  - El destello del motor baja de 0,95 a 0,3 (estilo.md: "flojos y muy cortos"). Lo de 0,3 no se ha renderizado; a 0,5 aún lavaba.
  - Puerta nueva: tarjetas a la derecha y logo de menos de 0,8 s. Control: la ficha vieja falla en las dos y la corregida pasa.
  - No se tocan los subtítulos en mayúsculas de estilo.md: esa regla es de la letra de CapCut (11-10) y el motor sigue el estilo de Carla (28-10).
