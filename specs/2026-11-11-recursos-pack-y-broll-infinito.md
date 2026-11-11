# Pack de recursos 2.0 en el motor y b-roll "infinito" con licencia

**Fecha:** 2026-11-11 · **Pedido por:** Luismi · **Rama:** `feat/recursos-pack-y-broll-infinito`

## Qué es, en una frase

La ficha puede pedir overlays, transiciones, elementos (PNG y animaciones) y un LUT del PACK DE RECURSOS 2.0, la
puerta del plan los valida, y el buscador de b-roll consulta más fuentes con licencia comercial (y, como último
recurso, genera el plano con IA marcándolo como tal).

## Por qué

Hoy el motor solo usa 3 SFX del pack. El b-roll se pinta opaco y a pantalla completa, sin modos de fusión. Los
overlays del pack (light leaks, film burn, grano, polvo) son vídeo con fondo negro: sin fusión "screen" tapan el plano.

## Inventario del pack (medido con ffprobe el 11-11)

| Carpeta | Qué hay | Formato | Alfa | Uso en el motor |
|---|---|---|---|---|
| 03_OVERLAYS | 24 clips: light leaks, film burn, polvo, estrellas, grano, vintage, scan | h264 yuv420p, 1080p-4K, 0,3-85 s | no (fondo negro) | `overlay`, fusión `screen` (grano: `overlay`) |
| 06_TRANSICIONES | 13 clips: glitch, film burn, light leak, tech | h264 4K, 0,4-12 s | no (fondo negro) | `transicion` sobre un corte, fusión `screen`, máx. 1,2 s |
| 01_ANIMACIONES | elementos, fuego, dinero, papel, plantas | h264 sin alfa; 3 .mov ProRes 4444 y 1 PNG-mov con alfa | algunos | `elemento` (con alfa) u `overlay` (sin alfa) |
| 07_PNGs | 60 PNG RGBA: flechas, iconos, glow icons, letras | png rgba | sí | `elemento` |
| 09_LUTs | 11 .cube válidos (+ .3DL de Premiere) | cube | n/a | `lut` por pieza (toma y b-roll, nunca los rótulos) |
| 02_BACKGROUNDS | fondos en movimiento | h264 | no | fuera de esta fase (no hay recurso que los use) |

Fuera: todo `ES_*` (Epidemic) y `05_MÚSICA`; `.mogrt` (Premiere), `.webp` animados (ffmpeg no los decodifica),
ficheros `._*` de macOS.

## Cómo va

1. `motor/pack.py inventario` escribe `motor-datos/pack.json` (tipo, fichero, alfa, tamaño, duración, fusión por
   defecto). `pack.py listar <tipo> [palabra]` lo enseña.
2. Ficha: `"pack": [{tipo: overlay|transicion|elemento, nombre, in, out, opacidad, modo, x, y, ancho}]` y
   `"lut": {"nombre": ..., "fuerza": 0-1}`. `montar.py` resuelve las cues y lo deja en `plan.json`.
3. Las capas del pack se pintan con ffmpeg DESPUÉS del render (`motor/capas.py`), no en Chrome: fusión `screen`,
   `overlay` o `addition` en RGB, alfa con `overlay`. Así no dependemos de cómo Huashu trata los `<video>`.
   El LUT se aplica en `montar.py` a la toma y al b-roll, mezclado con el original según `fuerza`.
4. Puerta del plan: un `elemento` no puede caer en la zona de interfaz de Instagram (220 px arriba, 380 abajo),
   ni en la columna de botones (x > 900, y 700-1700), ni sobre la franja del subtítulo mientras esté. Una
   `transicion` cae a menos de 0,3 s de un corte o de una entrada/salida de b-roll y dura <= 1,2 s. Un `overlay`
   no pasa de opacidad 0,7. Los recursos del pack cuentan como cambio en pantalla.
5. Arreglos de paso (marca4r): el `tuit` y el `marcador` ocultan el subtítulo mientras están; el `logo` deja aire
   a la tilde y a la cursiva en su recorte.

## B-roll: fuentes (licencias leídas el 11-11)

| Fuente | Licencia | Anuncios | Atribución | Acceso | Estado |
|---|---|---|---|---|---|
| Biblioteca propia (`biblioteca.json`) | propia o ya licenciada | sí | según la fila | local | busca por `describe`/`tema` |
| 3 RECURSOS local | idem | sí | idem | local | ya existía (`broll.biblioteca`) |
| Canal de Fran (`@fran.entrenador`) | licencia de Luismi para republicar | sí | no | búsqueda en el canal | nuevo |
| Pexels | Pexels License | sí (no gente "enferma o medicándose", no marcas) | no | API con clave | ya existía |
| Pixabay | Pixabay Content License | sí (no marcas/logos) | no | API con clave, caché 24 h | ya existía; clave también por entorno |
| Coverr | Coverr License 2026 | sí | API Demo: citar a Coverr y autor | API con clave (por email) | nuevo, listo sin clave |
| Mixkit | Free License | sí | no | SOLO a mano: sus términos prohíben scripts | se apaga del buscador |
| YouTube CC BY | CC BY | sí, citando | sí | yt-dlp | se apaga por defecto (`--youtube`) |
| Vecteezy | Free: atribución y tope 1.000 $ | limitado | sí (free) | API por planes | no se integra |
| Videezy, Dareful (CC BY), Free Nature Stock (CC0), Life of Vids | varias | ver informe | según | sin API | a mano |
| Videvo, Mazwai | redirigen a Freepik | n/a | n/a | n/a | muertas |
| IA (ApiMart / Higgsfield) | generado | sí | no; se marca `ia` | API con clave / sesión | último recurso, gasta créditos |

Filtros: se descartan por etiqueta los clips con niños pequeños (child, kid, toddler, baby...) y marcas; se
ordenan los verticales primero. Lo descargado se apunta en `biblioteca.json` con fuente, licencia, autor y URL.
Lo generado con IA lleva `"ia": true` en `biblioteca.json` y en la ficha; la puerta falla si la ficha usa un clip
de IA sin marcarlo.

## Criterio de hecho

- `pack.json` generado sin ningún `ES_*` ni `05_MÚSICA`.
- Una ficha copia (`marca4rx`) con un overlay, una transición y un b-roll de Pixabay pasa la puerta, se renderiza,
  y su hoja muestra los tres.
- La puerta tumba un elemento en la columna derecha y una transición fuera de un corte (control positivo).

## Bitácora

- 11-11: spec, inventario y código en la rama.
- 11-11: hecho en la rama. Prueba marca4rx (datos y render aparte): pasa la puerta, capas, mezcla y revisión del fichero (-16,7 LUFS, 13 empalmes). Control positivo: la puerta tumba los cuatro fallos metidos a propósito. Pendiente: clave de Coverr (por email), sesión de Higgsfield, y decidir con Luismi la opacidad por defecto de las transiciones (LightLeak18 a 1,0 lava el plano en su pico).
