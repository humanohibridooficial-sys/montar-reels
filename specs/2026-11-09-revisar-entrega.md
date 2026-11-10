# Revisar la entrega de cada toma y guion para grabar

**Fecha:** 2026-11-09 · **Estado:** en curso (rama `feat/revisar-entrega`)

## Por qué

A Luismi le dicen que tiene que comunicar mejor. Se midieron 59 de sus tomas en bruto (del 20-09 al 09-11) con el criterio
del curso de Fernando Miralles (skill `/miralles`). Las correcciones que salieron están en `/guion` §3b, como marcas escritas
en el guion: `[RÁPIDO] [PAUSA] [DESPACIO] [PALMAS] [GESTO] [ACABA]`. Falta cerrar el ciclo:

1. que el guion se lea **en el móvil mientras graba**, con las marcas a la vista;
2. que cada toma en bruto reciba un **veredicto, "vale" o "repetir"**, con el motivo y el segundo, antes de pasar a montaje.

Luismi, 09-11: "la mecánica es que me grabo y se evalúa y se dan las mejoras".

## Qué se construye

| Pieza | Qué hace |
|---|---|
| `scripts/revisar_entrega.py <toma> [--guion g.txt]` | Transcribe la toma (faster-whisper con VAD), mide la voz y la imagen y escribe `<toma>.entrega.json`. Da el veredicto **REPETIR / VALE CON AVISOS / VALE**. |
| `scripts/guion_movil.py <guion.txt>` | Convierte un guion de `/guion`, con sus marcas, en una página HTML para leer en el móvil: letra grande, cada marca en su color y la lista de comprobación antes de grabar. |
| `docs/como-grabar.html` | Una sección nueva con las marcas y el paso "después de grabar, revisa la toma". |

Solo se **leen** `medir_toma.py` (encuadre y 4K) y `detectar_manos.py`; no se modifican. `medir_toma.py` se llama como
subproceso. `motor/montar.py` y `motor/portada.py` no se tocan: son de la PR #76 de la sesión de edición.

## Las comprobaciones

| # | Comprobación | Cómo se mide | REPETIR si | AVISO si |
|---|---|---|---|---|
| 1 | Arranque limpio | primera palabra: si se repite (`a minuto, al minuto`), si empieza con menos de 0,15 s de margen y, con `--guion`, si coincide con la primera palabra del guion | repetida o no coincide con el guion | margen < 0,15 s |
| 2 | Pausa antes del giro | hueco antes de "necesitas", "lo que hago" o "si quieres" (pasado el 35 % del texto) | < 0,5 s (el motor solo conserva lo que se graba: `pausaGiro`, PR #76) | — |
| 3 | Frena en la solución | palabras por minuto de la solución / del problema | — | ≥ 1,0 |
| 4 | El final se oye | dB de la última palabra frente a su frase; con más peso en la última frase (CTA) | CTA < −3 dB | mediana < −2,5 dB |
| 5 | 4K | resolución | — | < 2160 |
| 6 | Sitio para los rótulos | `medir_toma.py`: `rotulo_bajo_barbilla` | — | < 50 % de la toma |
| 7 | Manos en pirámide | HandLandmarker: dos manos juntas delante del cuerpo | — | > 15 % del tiempo hablado |
| 8 | Cámara baja | puntos de la cara (BlazeFace): altura de la nariz entre ojos y boca | calibrado con tomas de móvil conocidas; si no separa, no se incluye | — |
| 9 | Contraluz en el gancho | brillo de la cara frente al fondo en los 3 primeros segundos | — | cara más oscura que el fondo, calibrado con la toma 85 |
| 10 | Se acerca sin hablar | tamaño de la cara en los huecos de más de 0,8 s sin voz | — | cambia más de un 15 % |

**No se mide (va en la lista de comprobación del guion para el móvil):** logos de otras marcas en la ropa (Nike, Joma),
las muletillas (Whisper las borra, control positivo del 09-11: 1 "eh" en 59 tomas) y si suena natural.

## Decisiones

- Los umbrales salen de la medición del 09-11 (memoria `comunicar-mejor-medicion-tomas-09-11`) y de la sesión de edición
  (barbilla, 4K, contraluz en la 85, arranque "a minuto"). **Cada umbral nuevo se calibra con un control**: una toma que se
  sabe que falla tiene que dar el aviso. Si no lo da, la comprobación no entra.
- Una sola toma por llamada: no hace falta procesar lotes.
- El estimador de tono no entra en el veredicto: es casero y solo sirve para ver tendencias.

## Hecho cuando

- [x] `revisar_entrega.py` da REPETIR en un caso conocido de cada tipo y VALE en una toma buena (controles anotados en la bitácora).
- [x] `guion_movil.py` genera una página que se lee a 390 px de ancho.
- [x] La sección de `docs/como-grabar.html` está escrita.
- [x] `python -m unittest discover tests` pasa y `py_compile` pasa en los dos scripts.
- [ ] Commit y push, con PR.

## Bitácora

- 09-11: spec escrito. Worktree `montar-reels-entrega` creado desde `origin/main` (46bc7db).
- 09-11: calibrado con las tomas en bruto de `edicion/1 TOMAS EN BRUTO`:
  - **Pausa:** Whisper estira las palabras hasta la siguiente y esconde los silencios. En la 89 hay unos 0,26 s de
    silencio real antes de "necesitas" y los tiempos de palabra dan 0,00. Ahora la pausa se mide en el audio
    (`silencio_antes`, tramo seguido 20 dB por debajo de la voz). Sobre 20 tomas con giro (60-90): 11 de las 16 que no
    son cortes de toma quedan por debajo de 0,3 s.
  - **Giro:** "si quieres" suele ser el CTA del final. Solo cuenta si no hay "necesitas" ni "lo que hago".
  - **Arranque:** caso real, la 82 ("futbolista a minuto 60" frente a "futbolista, minuto 60" del guion). Con `--guion`
    da REPETIR.
  - **Manos:** midiendo solo mientras habla no separa. Midiendo todo el tramo, con las manos centradas, sí: positivos
    84 0,12, 91 0,14, 66 0,29; negativos 80 0,09, 82 0,06. Umbral 0,11. El margen es fino, así que solo da aviso.
  - **Acercarse sin hablar:** con huecos de cualquier largo saltaba en cada toma, porque al volver a empezar la frase te
    mueves. Ahora solo cuenta en huecos de 0,8 a 3 s.
  - **No entran** (no pasaron el control): la cámara baja (la proporción de la nariz da 0,54-0,57 con el móvil frente a
    0,49-0,62 con la DJI) y el contraluz (la 85 da −20 de brillo cara-fondo, pero las tomas al aire libre dan −50 o
    menos). Van a la lista "Antes de grabar" del guion para el móvil.
  - **Aviso, sin arreglar** (no es de este frente): `medir_toma.py` no encuentra la cara en
    `VID_20261109_143015_8K.mp4`, un 8K HEVC del móvil girado 90°.
- 09-11: `guion_movil.py` comprobado a 390 px con Playwright (scrollWidth 390, sin scroll horizontal). La sección 9-10
  de `como-grabar.html`, también a 390 px. Tests: 16 en verde; con dos sabotajes (PAUSA_MIN = 0 y `silencio_antes` a
  0) fallan los 2 que tienen que fallar.
