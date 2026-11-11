# Columna de tarjetas y saltos de línea de los titulares, desde la ficha

**Fecha:** 2026-11-11 · **Rama:** `feat/ficha-tarjetas-y-saltos`

## Qué es, en una frase

Dos arreglos que en la 63r se hicieron a mano sobre `render/p63r/index.html` se piden ahora desde la ficha, para
que no se pierdan si se vuelve a montar la pieza.

## Qué se parcheó a mano (diff de lo que generaba `montar.py` contra el `index.html` parcheado)

Tres líneas de CSS y nada más:

- `#tops .t2`: se le añadió `white-space: pre-line`. La ficha ya traía los `"\n"` en el texto, pero el navegador
  los juntaba en un espacio.
- `.tcol`: `top` de 360 a 326 px, `width` de 190 a 150 px, `gap` de 16 a 12 px.
- `.tcol .tc`: de 190x338 a 150x266 px.

## Cómo se escribe en la ficha

Titulares: un `"\n"` o un `"|"` en `linea1` o `linea2` de `tops` parte la línea ahí.

```json
"tops": [[0, "camino>", "Tu hijo juega en juvenil:", "¿Y si se queda|en el camino?", false]]
```

Tarjetas: campos opcionales en el extra `tarjetas`, en px (`x` también admite `"6%"`).

```json
{"tipo": "tarjetas", "lado": "izq", "in": "verificar", "out": "duerme>",
 "ancho": 150, "alto": 266, "separacion": 12, "y": 326, "x": "6%", "clips": [...]}
```

## Reglas

- Por defecto, lo de siempre: 190x338, separación 16, y 360, x 6 %. Sin saltos en los titulares no se toca el CSS.
  Una pieza que no usa las opciones saca el mismo `index.html` byte a byte.
- Si dos columnas de tarjetas de la misma pieza piden medidas distintas, `montar.py` para (es una sola regla de CSS).
- `montar.py` deja en `plan.json` (no en el HTML) la caja de cada columna, con el borde de 3 px.
- Puerta del plan: la caja no baja de y 1248, no sube de y 220 y no entra en la columna de botones
  (x > 900, y 700-1700). Sustituye a la regla "tarjetas a la derecha", que queda solo para `plan.json` antiguos.

## Criterio de hecho

- 85 (tarjetas sin opciones): `index.html` idéntico con el código de `origin/main` y con el de la rama.
- 63r con las opciones en la ficha: `index.html` generado idéntico al parcheado a mano.
- Control positivo: la 63r sin opciones falla la puerta (caja hasta 1424); una columna a la derecha y otra que sube
  a y 200 también fallan.

## Bitácora

- 11-11: hecho en la rama. Las tres comprobaciones pasan (render y datos de prueba aparte, con `MOTOR_CONFIG`). No
  hizo falta renderizar: el `index.html` sale idéntico. Ficha 63r actualizada con las medidas de las tarjetas.
  La partición con `"|"` no se ha probado de punta a punta (en la 63r los saltos ya iban con `"\n"`).
