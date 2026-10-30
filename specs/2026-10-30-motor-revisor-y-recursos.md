# Motor: puertas de calidad, revisor y recursos nuevos (30-10)

## Por qué
La comparativa del 30-10 (toma 75: motor propio, video-use y ChatMonteur) la ganó el motor por estilo.
Luismi: "podemos integrar todo en mi motor, creo que es la mejor edición", "además de meter más elementos
que tomes y copies de ejemplos". De los otros dos se copia cómo se revisan, no su estilo. Los recursos nuevos
salen de `mi-estilo/recursos.md` (referentes medidos el 10-10 y la receta de Carla del 28-10), con la marca
de FF360 (Anton/Inter, dorado `#E0B83C`, azul `#2E6BFF`, marino `#070D16`).

## Qué se construye

### Parte A. Que el motor diga "no" con datos
1. **Puerta del plan** (`motor/puerta_plan.py`, antes del render; sustituye a `revisar_plan.py`).
   Falla si:
   - hay más de 3 s sin un evento visual (reencuadre, b-roll, titular, destello, cifra, tachado, panel, BYN o recurso nuevo);
   - el fotograma 0 no tiene titular;
   - un tramo dura demasiado o demasiado poco (las comprobaciones de `revisar_plan.py`);
   - la pieza repite el mismo gancho y el mismo juego de recursos que alguna de las 3 últimas de `usados.json`.
   Si falla, el render no arranca. `FORZAR=1` lo salta.
2. **Revisión del fichero** (`motor/revisar_export.py`, tras la mezcla), copiada de la puerta de fichero de
   ChatMonteur y de la autoevaluación por corte de video-use. Mide:
   - fotogramas negros;
   - silencios de más de 0,6 s;
   - sonoridad entre −17 y −15 LUFS y pico por debajo de −1 dBTP;
   - duración igual a la de la voz (±0,1 s);
   - en cada empalme de la toma, un clic: salto de nivel de más de 12 dB en 20 ms.

   Escribe `qc.json` (veredicto `ok` o `fallo` y la lista de fallos con su segundo) y una hoja de fotogramas:
   10, 35, 65 y 90 %, más antes y después de cada empalme. Si el veredicto es fallo, `montar.sh` no copia el mp4
   a la carpeta de salida.
3. **Revisor**: `montar.sh` imprime la ruta de la hoja y de `qc.json`. El agente `revisor-montaje` los lee
   primero. El bucle de video-use: si el revisor devuelve fallos de los puntos 1, 3, 4 o 6, se corrige la ficha
   y se vuelve a montar, como mucho 3 veces; después se enseña con los fallos dichos.

### Parte B. Recursos nuevos (cada uno, un campo opcional de la ficha)
Tomados de los referentes y aún sin pintar en el motor:

| Campo | Recurso | Visto en |
|---|---|---|
| `tinte` | Tinte de color sobre el plano (rojo para el error, azul para la idea) | Carla Dd6LU s11, s23 |
| `tuit` | Tarjeta falsa de tuit para citar la objeción | Carla Dd6LU s9-10 |
| `cortinilla` | Banda que barre y deja 2-3 palabras cinéticas sobre color | Carla DeMG s6-8 |
| `contador` | Número fijo arriba en una lista ("1/3") durante su bloque | Carla DeJh s7-35 |
| `marca` | Flecha o círculo sobre un punto del plano | quique Dd7B s8, Carla Dd8pk s43 |
| `congelado` | La imagen se para con una anotación mientras sigue la voz | yassin DcTM |
| `detras` | Palabra gigante detrás de ti (reutiliza `scripts/palabra_detras.py`) | Carla DeMG s32 |

Cada recurso nuevo:
- lleva su efecto en `mezcla.py`;
- cuenta como evento visual en la puerta del plan;
- oculta los subtítulos si se pisan.

Los subtítulos NO se tocan. El "tamaño distinto" del 30-10 es la receta de Carla: blanco pequeño y la clave
dorada grande. "Juegas en una" salía pálido porque el fotograma estaba a mitad de fundido.

## Hecho cuando
- La 75 se monta con `sh motor/montar.sh 75` y la revisión sale `ok`. Solo cambian los reencuadres:
  el forzado pasa de 3,2 a 2,6 s para no dejar huecos.
- **Control positivo** de cada comprobación: una ficha saboteada la hace fallar. Casos:
  - un hueco de 5 s sin evento;
  - un tramo de silencio metido a mano;
  - la música a +6 dB.

  Si el sabotaje no la hace fallar, la comprobación no vale.
- Una pieza de prueba con los 8 recursos nuevos, mirada fotograma a fotograma y pasada por `revisor-montaje`.
- Commits pequeños y PR abierta.

## Fuera
- CapCut/VectCutAPI: se retira del camino principal en otra PR (paso 4 del plan del 30-10).
- Jugadores profesionales con su nombre (riesgo de derechos, nunca en anuncios).

## Bitácora
- 30-10: spec escrito. Rama `feat/motor-revisor-y-recursos`, worktree `montar-reels-motor`.
- 30-10, parte A hecha y verificada:
  - Puerta del plan.
    - Pasó las 6 piezas probadas (75, 27, 33, 40, 56 y m3), después de corregir el reencuadre.
    - Antes, 4 de 5 tenían huecos de 3,1 a 4,5 s. Venían de palabras que whisper estira a 2 s, y ahora el reencuadre entra a mitad de palabra.
    - Controles: un hueco de 10,5 s saboteado la hace fallar. La 33 detrás de la 27 falla por copia: mismo gancho y 100 % de los recursos.
  - Revisión del fichero.
    - Controles con un mp4 saboteado (+6 dB, negro a los 5 s y silencio a los 20 s): detecta los cuatro fallos (sonoridad, pico, negro y silencio). Un clic metido en la voz en el empalme de 15,83 s da 44 dB y falla.
    - Quitados los sabotajes, la 75 vuelve a OK.
  - Camino entero con `montar.sh 75`: puerta OK, render, mezcla, revisión OK (−16,5 LUFS, pico −2,1), entrega y anotación en `usados.json`.
  - Arreglado de paso (fallo de la PR 49): las tomas del móvil (m1-m7) están en la raíz de `edicion`.
  - `revisor-montaje` (repo y `~/.claude/agents`) lee primero `qc.json` y `hoja.jpg`, y el objetivo de volumen pasa a ser −17 a −15 LUFS.
- 30-10, parte B escrita, SIN verificar en vídeo:
  - Los 8 recursos están en `estilo.py` (CSS y animación), `montar.py` (`extras` en la ficha), `mezcla.py` (un efecto por recurso) y `puerta_plan.py` (cuentan como evento; el tuit y el contador fallan si pisan un titular).
  - La 75 sin `extras` sigue pasando la puerta.
  - Prueba con los 8 sobre la 75 (ficha en el scratchpad de la sesión): `montar.py` acabó y generó el congelado, la palabra detrás (`palabra_detras.py`) y el tú delante del clip (`delante_del_clip.py`, escala 0,81).
  - El render lo paró Claude Code por falta de memoria del sistema. La ficha 75 se restauró a mano (md5 igual que la original).
  - MediaPipe se instaló en `montar-reels/.venv` (requirements.txt). `motor/config.json` acepta `scripts` y `python_silueta`.
  - Siguiente paso: relanzar la prueba con la memoria libre, mirar la hoja y los fotogramas de cada recurso, y pasarla por `revisor-montaje`.
- 30-10, parte B verificada en vídeo (`comparativa-75/4-tu-motor-con-recursos-nuevos.mp4`).
  - Primera revisión con `revisor-montaje`: "no se puede enseñar". Del motor se corrigió:
    - el tinte teñía los subtítulos;
    - la flecha cruzaba la cara;
    - la palabra detrás no quedaba detrás;
    - el tuit tapaba la cabeza y quitaba el subtítulo;
    - la cortinilla iba en azul (estilo.md: solo filo), ahora va en marino;
    - el congelado llevaba destello por defecto.
  - Puerta nueva:
    - un rótulo que dice una palabra de la voz entra con ella (±0,25 s);
    - un congelado de más de 1 s falla.

    Control: la ficha vieja da 5 avisos a destiempo y el congelado de 2,3 s.
  - Luismi (30-10): "está muy bien salvo dos cosas". Se quita `delante` ("da mal"). Pendiente: la tarjeta de seguir con su perfil real de Instagram (espera su captura).
  - Visto en la revisión y anterior a esta rama (no se toca sin preguntar): el tachado de la 75 dura 5 s y quita los subtítulos de esa frase; los titulares de arriba quedan a un 11 % de altura.
