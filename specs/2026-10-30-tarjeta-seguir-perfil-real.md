# Tarjeta de "Seguir" con el perfil real de Instagram (30-10)

## Por qué
Luismi, al ver la prueba del motor: "en el perfil de Instagram le puede meter mi perfil". Hasta ahora la tarjeta
ponía un círculo con "FF" y "@nutretufutbol" dos veces.

## Qué
- `motor-datos/perfil/perfil.json`: `usuario` y `nombre` como salen en Instagram.
- `motor-datos/perfil/foto.jpg`: la foto de perfil.
- Las dos cosas van fuera del repo, que es público.
- Si falta la foto, sale el círculo "FF" de siempre.
- La tarjeta pone el usuario en negrita y el nombre debajo, en dos líneas como mucho.

## Hecho cuando
- Una pieza renderizada muestra la tarjeta con la foto y el nombre, sin cortes.
- Sin la carpeta `perfil/`, la pieza sale como antes.

## Bitácora
- 30-10: la captura del perfil trae la burbuja "Nota…" de Instagram encima de la cabeza; no sirve de foto. Se pide a Luismi la foto original.
