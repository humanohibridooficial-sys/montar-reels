# Catálogo de recursos de edición (ejemplo de partida)

El instalador copia este fichero a `mi-estilo/recursos.md`, que es TUYO y no se sube a git. Ve ampliándolo
con lo que aprendas de tu cuenta fantasma ("analiza esta cuenta" en Claude Code) y de tus propios reels.
Sale de analizar reels y anuncios de coaches de deporte y nutrición con muchas reproducciones (octubre de
2026). Es un mapa, no una receta: se copia la técnica, nunca el texto ni la imagen de nadie.

Tu marca (colores y letras) está en `config.json` (`color_clave`, `color_marca`) y en `mi-estilo/estilo.md`.
Todo recurso se viste con TU marca, nunca con la de la referencia.

## Tono de la pieza (lo primero que se decide)
| Tono | Cuándo | Cómo se monta |
|---|---|---|
| sobria | consejo o dato que debe sonar a experto | pocos recursos, encuadre suave, claves con fundido, sin destellos |
| intensa | problema, reto, urgencia | un recurso cada 3-4 s, zooms marcados, claves de golpe, destellos entre bloques |
| emocional | historia, miedo, frustración | blanco y negro, silencios, desvanecer, claves suaves |
No repitas tono en dos piezas seguidas salvo que el guion lo pida (lo mira el director en `usados.json`).

## Formas por función (rota: que no salgan dos reels seguidos iguales)
| Función | Formas posibles | Script |
|---|---|---|
| Gancho (0-2 s) | nombrar a quién hablas con texto desde el fotograma 0 · imagen real de tu deporte 1-2 s y corte a ti · hablar mientras entrenas · "todo esto NO SIRVE" con objetos · la objeción en blanco y negro y salto a color con tu reacción · texto de tres pesos arriba · palabra gigante detrás de ti · contraste (dos versiones de ti o frase tachada) | `rotulos_lib.py` (`tres_pesos`), `palabra_detras.py`, `byn` en la spec |
| Cuerpo a cámara | cambio de encuadre cada pocos segundos (automático) · tú delante del clip · media pantalla con fundido (solo si hay hueco sobre tu cabeza) · zoom en la frase fuerte | `montar_reel.py`, `delante_del_clip.py`, `composicion.py fundido` |
| Lista | número o rótulo fijo arriba · un clip en media pantalla por punto · puntos que aparecen al nombrarlos · tarjetas | `rotulos_lib.py`, `capas_lib.py`, `tarjetas_v2.py` |
| Dato o resultado | cifra grande · tarjeta de resultado · gráfica detrás de ti | `rotulos_lib.py` (`dato`), `grafica_detras.py` |
| La otra voz / objeción | blanco y negro 1 s · tarjeta de tuit falso (usuario genérico) · tinte de color | `rotulos_lib.py` (`tuit`), `tintes` en la spec |
| Pasar de bloque | destello · corte seco (por defecto) | `destellos` en la spec |
| Subtítulos | 1-3 palabras y la palabra clave "vestida de rótulo": debajo, grande y en tu color, entrando cuando la dices | `subt_rotulo` en la spec |
| Cierre | "sígueme" o "comenta la palabra" en los últimos 1-2 s | rótulo PNG o `cta` |

## Lo que hacen los anuncios que más tiempo llevan activos
Nombran al público en el segundo 0 con texto en pantalla, llevan texto desde el primer fotograma (1-3
palabras, la clave en color) y cambian de plano o de texto cada 1-2 s. Ninguno abre con logo, saludo,
producto o la cara quieta sin texto.

## Para grabar
Si te grabas muy cerca (la cabeza empieza por encima del 30 % de la altura), la media pantalla y el texto
de arriba no caben bien: `montar_reel.py` solo pone media pantalla con un 40 % libre sobre tu cabeza. Si una
pieza va a llevar esos recursos, grábate más abierto.

## Reglas que no se rompen
- Casos, cifras y testimonios: solo reales y con permiso.
- Cada frase con su imagen: nunca más de 3 s de solo cara con subtítulos (una cabeza hablando sin imágenes
  no aguanta). Los adornos (destello, punch-in, transición con efecto), como mucho dos y con motivo.
- Nada tapa tu cara; todo dentro de la zona segura de Instagram.
