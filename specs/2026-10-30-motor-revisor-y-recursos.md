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
| `delante` | Tú recortado delante del clip (reutiliza `scripts/delante_del_clip.py`) | quique Dd7B, DeH3 |

Cada recurso nuevo:
- lleva su efecto en `mezcla.py`;
- cuenta como evento visual en la puerta del plan;
- oculta los subtítulos si se pisan.

Además, los subtítulos dejan de salir con tamaños distintos de un bloque a otro (visto en la 75: "Juegas en una",
"con el").

## Hecho cuando
- La 75 se monta con `sh motor/montar.sh 75` igual que antes (control: SSIM ≥ 0,99 contra
  `comparativa-75/1-tu-motor.mp4`) y la revisión sale `ok`.
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
