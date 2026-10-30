# Zona segura de arriba y entrada de la tarjeta de "Seguir" (30-10)

## Por qué
El revisor suspendió la 41b (trial reel rehecho con el motor). Dos fallos eran del motor y salen en todas las piezas:
- El titular (210 px) y la tarjeta de Seguir (250 px) caían dentro del 15 % de arriba (288 px), que KAIZEN §1 pide libre.
- La tarjeta de Seguir entraba 1,6 s antes de "sígueme". Si había una cortinilla, la destapaba al salir y se quedaba 3,4 s.

## Qué
- `#tops`, `#follow` y `.tuit` pasan a 300 px. La tarjeta de Seguir baja al 85 %; la escala va dentro de su animación de GSAP, que si no pisaría la de CSS.
- La tarjeta entra 0,8 s antes de "sígueme" y siempre después de que salga una cortinilla, lista, mapa o logo.
- `broll.py` escribe la salida en UTF-8. Con autores como "Oğuzhan", la consola de Windows en cp1252 lo tiraba (lo encontró el director).

## Hecho
- Plan de la 41b: tarjeta en [17,31, 18,11], tras la cortinilla que acaba en 17,19.
- Render de la 41b: titular a unos 320 px; la tarjeta, de unos 317 a 432 px, no toca las gafas. Puerta y revisión del fichero OK (−16,1 LUFS).
- No se toca la pizarra, que a 170 px sigue dentro del 15 %: la decisión del revisor fue ponerla sobre la cabeza.
