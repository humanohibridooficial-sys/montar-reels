# Plantilla "pared azul"

Reel vertical (1080×1920) con este estilo:

- una **pared azul de yeso** por la que se mueve una **cámara 3D**, con perspectiva, profundidad y barridos con desenfoque;
- fotos y grabados **impresos en tinta blanca** con un marco fino, que **caen** sobre la pared;
- texto que aparece **palabra a palabra**, con las palabras clave en rojo;
- **cortes a vídeo real en blanco y negro**, con una sola palabra en el centro siguiendo la voz.

Está hecha con [HyperFrames](https://github.com/heygen-com/hyperframes) (HTML y GSAP convertidos en MP4, licencia Apache-2.0). El ejemplo es el guion "Cómo se trabaja en FF360", de unos 70 segundos.

## Requisitos

- Node 22 o superior y FFmpeg.
- Python con `pillow`, `numpy` y `requests` (solo para regenerar las imágenes).
- Opcional: el plugin de HyperFrames en Claude Code (`claude plugin marketplace add heygen-com/hyperframes` y `claude plugin install hyperframes@hyperframes`).

## Uso

1. **Clips de vídeo.** Pon en `assets/video/` cuatro clips verticales (`cocina.mp4`, `fuerza.mp4`, `dormir.mp4` y `decide.mp4`). Con `herramientas/pexels_buscar.mjs` de este repositorio los buscas en Pexels. Los tienes que descargar tú: no se incluyen por licencia.
2. **Comprobar**: `npm run check`.
3. **Ver y retocar en el Studio**: `npm run dev`. Haces clic en cualquier elemento para cambiarlo, editas textos y recortas en la línea de tiempo.
4. **Renderizar**: `npm run render`. En un portátil normal tarda bastante: unos 70 s de vídeo llevan del orden de una hora.

Las imágenes ya están procesadas en `assets/img/`. Para regenerarlas o cambiarlas:

```bash
python descargar_imagenes.py          # baja los originales a originales/ y comprueba la licencia
python prep_assets.py originales/     # pared.jpg e imágenes en tinta blanca
```

## Cómo adaptarla a tu guion

Todo está en `index.html`:

- `FRASES`: cada frase con su segundo de inicio y de fin. Si tienes la voz grabada, saca los tiempos de la transcripción (el `transcribir` de este repositorio) y el texto queda sincronizado palabra a palabra.
- `LLENOS`: los tramos a pantalla completa (foto o vídeo), donde va la palabra blanca del centro.
- La pared son **celdas de 1080×1920** en dos columnas (`CEL(columna, fila)`). Cada bloque de contenido vive en su celda con `print(...)` (imagen), `texto(...)` (palabras) o `bloque(...)` (HTML libre).
- La cámara usa `fija` (salta a una celda), `deriva` (movimiento lento) y `barrido` (paso rápido entre celdas, con desenfoque).
- Los tramos de sketch (`sk-ini` y `sk-fin`) son tarjetas provisionales: sustitúyelos por tu toma grabada como un `<video>` más.

## Lo que avisa `check`

Quedan avisos de "texto tapado" porque la pared queda debajo de los vídeos, del sketch y de la viñeta. Es a propósito; revisa siempre con `npx hyperframes snapshot . --at <segundos>`.

Créditos y licencias en [CREDITOS.md](CREDITOS.md).
