# Paso a paso: el editor de reels en tu ordenador

Para cualquier persona con **Windows 10 u 11** o con **Mac** (chip Apple M1 o posterior, macOS 14 o posterior),
aunque no hayas tocado nunca un ordenador más allá del navegador. No vas a escribir ningún comando: todo es doble
clic y hablarle a Claude en español. Si tienes Mac, sigue los mismos pasos con los cambios de
[**En Mac**](#en-mac), al final.

Tiempo la primera vez: **unos 45 minutos**, casi todo esperando descargas. Necesitas **20 GB libres** en el disco
(el montaje de cada vídeo ocupa mucho mientras se hace y luego se borra).

## Lo único que tienes que tener antes

**Una cuenta de Claude de pago** (Pro o superior), en claude.ai. Es la IA que edita. Sin ella no funciona.

## Paso 1 · Descargar el editor (2 minutos)

1. Abre esta página en el navegador: https://github.com/humanohibridooficial-sys/montar-reels
2. Pulsa el botón verde **Code** y después **Download ZIP**.
3. Ve a tu carpeta de **Descargas**, haz clic derecho en `montar-reels-main.zip` y elige **Extraer todo**.
4. Mueve la carpeta que sale a un sitio fácil, por ejemplo el **Escritorio**.

## Paso 2 · Instalar (40 minutos, casi todo esperar)

1. Abre la carpeta y haz **doble clic en `1 INSTALAR.bat`**.
2. Si Windows dice "Windows protegió su PC": pulsa **Más información** y luego **Ejecutar de todas formas**.
   Es normal con programas que no vienen de una tienda.
3. Se abre una ventana negra que va instalando cosas sola. **No la cierres.** Si te pide permiso de administrador,
   di que **Sí**.
4. Si en algún momento dice **"Cierra esta ventana y abre otra"**: ciérrala y vuelve a hacer doble clic en
   `1 INSTALAR.bat`. Sigue donde lo dejó.
5. Ha terminado cuando la ventana dice **"Todo listo"** en verde. Si hay líneas en rojo, haz doble clic otra vez en
   `1 INSTALAR.bat`: casi siempre se arregla solo a la segunda.

## Paso 3 · Entrar en Claude (1 minuto, solo la primera vez)

1. Haz **doble clic en `2 EDITAR.bat`**.
2. La primera vez se abre el navegador para que entres con tu cuenta de Claude. Entra y vuelve a la ventana negra.
3. Si te pregunta si confías en la carpeta, di que **sí**.

## Paso 4 · Tu primer reel

1. Graba con el móvil un vídeo **vertical** hablando a cámara. Mejor una idea por vídeo que todo seguido.
2. Pásalo al ordenador y déjalo en **Vídeos > Reels > 1 TOMAS EN BRUTO** (la carpeta la crea el instalador).
3. Si tienes el guion de lo que ibas a decir, guárdalo al lado del vídeo: con guion corta mucho mejor.
4. Haz doble clic en `2 EDITAR.bat` y escríbele a Claude, tal cual:

   > edita este reel: el último vídeo de mi carpeta de tomas

5. Te irá contando lo que hace. Tarda unos **10 minutos** por vídeo. Cuando acabe, lo tienes en
   **Vídeos > Reels > 2 PARA SUBIR**, con su portada y el texto para la publicación.
6. Si algo no te gusta, díselo como se lo dirías a una persona: *"quita la parte en la que me equivoco"*,
   *"más rápido"*, *"sin música"*, *"esa palabra que salga en grande"*. Lo rehace y se lo apunta para la próxima.

## Para que edite como tú (cuando ya hayas hecho un par)

- Dile **"aprende de mis reels"** y copia antes 5-10 reels tuyos ya terminados en la carpeta
  `mi-estilo\mis-reels` del editor.
- Dile **"quiero editar como esta cuenta"** y pégale enlaces de reels que te gusten. Los mira en tu ordenador para
  aprender el ritmo y el estilo; no publica nada ni entra en tu Instagram.

## La primera vez: tu perfil

Antes del primer vídeo, Claude te pide **tu usuario de Instagram**, una frase corta para debajo y **una foto de
perfil**. Salen en la tarjeta de "Seguir" del final de cada reel. Sin eso no monta, para que nunca salga un perfil
que no es el tuyo.

## Cómo ordenar las carpetas

Todo vive en **Vídeos > Reels** (en Mac, **Películas > Reels**). El instalador crea esto y el editor lo mantiene:

| Carpeta | Qué va dentro | Quién la llena |
|---|---|---|
| `1 TOMAS EN BRUTO` | Los vídeos tal como salen del móvil. **Una sola copia** de cada uno, con un nombre corto (`01-proteina.mp4`). Si tienes guion, al lado y con el mismo nombre: `01-proteina.guion.txt` | Tú |
| `2 PARA SUBIR` | **Una carpeta por vídeo**: `<número> - <tema>`, con `REEL`, `PORTADA` y `CAPTION`. Si pides pruebas de gancho, también `TRIAL A` y `TRIAL B`: el mismo montaje con otro arranque | El editor |
| `3 RECURSOS` | `MUSICA/`, los efectos `SFX-…wav`, el b-roll en `b-roll-<sitio>/` (cada uno con su `LICENCIA.txt`) y, si compras uno, tu pack de recursos | El editor y tú |
| `motor-datos` | Lo que dices en cada toma, los planes de montaje y tu perfil. **No lo toques** | El editor |

Fuera de esa carpeta, en tu usuario, hay una `reels-render`: es el taller. Cada vídeo ocupa ahí 13-17 GB mientras se
monta. Cuando tengas el vídeo en `2 PARA SUBIR`, Claude puede vaciarla si se lo pides.

Reglas que ahorran líos: no muevas ni renombres nada dentro de `motor-datos` ni mientras un vídeo se está montando,
y no guardes dos copias de la misma toma.

## De dónde sale el b-roll (los planos de recurso)

Claude lo busca solo cuando hace falta. Si quieres uno concreto, díselo: *"pon un plano de un jugador atándose las
botas cuando digo 'antes del partido'"*. Te enseña varios candidatos y elige contigo.

Busca a la vez en:

- **Tu biblioteca**: lo que ya tengas en `3 RECURSOS`. Si tienes clips tuyos (entrenando, en el campo, tu material),
  déjalos ahí: son lo mejor, porque nadie más los tiene.
- **Pexels**, **Pixabay** y **Coverr**: vídeos gratis que se pueden usar en anuncios. Pexels y Pixabay sin citar a
  nadie; Coverr, con su clave gratuita, pide citarle a él y al autor. Hace falta una clave gratis de cada uno. Pídele a Claude *"ayúdame a sacar la clave de Pexels"* y te lleva paso a paso; la
  pega él en el fichero `.env`, que no sale de tu ordenador. Pexels es la importante; Pixabay y Coverr dan más
  variedad (la de Coverr se pide por email).
- **YouTube con licencia Creative Commons**, solo si lo pides: obliga a **citar al autor en el texto** de la
  publicación.
- **Generado con IA**, solo si lo pides y como último recurso: **cuesta dinero** (créditos de un servicio de pago) y
  el vídeo sale marcado como hecho con IA.

Webs como Mixkit o Videezy también son gratis, pero no dejan descargar con programas: si te gusta un clip de ahí,
bájalo tú y déjalo en `3 RECURSOS/b-roll-mixkit/`.

Lo que el buscador descarta siempre: **marcas y logos** (Nike, escudos de clubes…) y **niños pequeños**. Así todo lo
que monta se puede usar también en anuncios.

## El color (LUTs) y el pack de recursos

Un **LUT** es un filtro de color (fichero `.cube`) que da a todos tus vídeos el mismo tono. El editor no trae ninguno:
vienen en los **packs de recursos** que se venden para editores (overlays, transiciones, elementos animados y LUTs).

Si compras uno, déjalo en `3 RECURSOS/PACK DE RECURSOS 2.0/` con estas carpetas dentro: `01_ANIMACIONES`,
`03_OVERLAYS`, `06_TRANSICIONES`, `07_PNGs` y `09_LUTs`. Dile a Claude *"tengo un pack nuevo"*: lo cataloga y
desde ahí puede pedirte *"un LUT cálido"* o *"una transición en el cambio de tema"*. Sin pack, el vídeo sale igual
de completo, sin esos extras.

Antes de comprar uno, mira su licencia: tiene que permitir **uso comercial y anuncios**. Muchos packs traen música o
efectos de terceros que **no** se pueden usar en anuncios. Si lo dice, apártalos.

## El sonido

- **Tu voz**: el editor quita el ruido de fondo solo. No le pongas tú compresor ni reductor de ruido: suben el ruido
  que queda. Lo que más ayuda es grabar con el móvil cerca, en un sitio sin eco y sin viento.
- **Volumen**: todos los vídeos salen al mismo, el que usa Instagram (−16 LUFS). No hace falta tocarlo.
- **Música**: siempre de fondo, bastante más baja que tu voz, y se aparta sola cuando hablas. Trae 9 pistas libres
  de Mixkit; si quieres más, bájalas de **Mixkit** o **Pixabay Music** y déjalas en `3 RECURSOS/MUSICA`. Pídela por
  ambiente: *"música más emotiva"*, *"más energía"*, *"sin música"*.
- ⛔ **Nunca himnos ni cánticos famosos** (la Champions, el "po-po-po"…): tienen derechos y **Meta bloquea el anuncio**.
- **Efectos de sonido**: uno por cada cosa que pasa en pantalla (entra un plano, sale una lista, aparece el botón de
  Seguir). Si te parecen muchos o pocos, díselo: *"menos efectos"*, *"que suene un golpe en la palabra clave"*.

## Programas para cortar: qué usa y qué no

- **El motor del editor** (lo que usa por defecto): corta, subtitula, pone recursos, música y portada, y saca el
  vídeo terminado. Gratis y en tu ordenador. Es el que mejor quedó al compararlo con otras herramientas.
- **CapCut** (solo Windows, versión 9): si quieres retocar a mano, Claude puede montarlo como proyecto de CapCut.
  La exportación final la haces tú desde CapCut.
- **Cualquier otro editor**: el vídeo de `2 PARA SUBIR` es un mp4 normal. Puedes abrirlo en CapCut del móvil, en
  DaVinci Resolve (gratis) o en el que uses, y retocar lo que quieras.
- **Apps de pago que montan solas** (Descript, Submagic, Opus Clip y similares): se descartaron. Dan su estilo, no
  el tuyo, y no aprenden de lo que corriges.

## Grabar para que el montaje salga mejor

- Vertical, con luz de cara y el móvil a la altura de los ojos.
- Si quieres textos o planos encima de ti, deja aire: que tu cabeza quede hacia la mitad de la pantalla, no arriba
  del todo.
- Una idea por vídeo. Si te equivocas, repite la frase entera: el editor te propone quedarse con la última buena.
- Al acabar, quédate un segundo quieto antes de ir a parar el móvil: así el corte no pilla tu mano.

## Si algo falla

Díselo a Claude con tus palabras: *"no me funciona"*, *"me sale un error rojo"*. Él lanza la comprobación, ve qué
falta y lo arregla o te dice qué tocar. Si ni siquiera se abre Claude, haz doble clic otra vez en `1 INSTALAR.bat`.

## Qué instala, por si te lo preguntan

Node.js, Git, Python (3.11 y 3.12), FFmpeg y Google Chrome, todo gratis y con el instalador oficial de Windows
(winget). Dentro de la carpeta del editor deja la limpieza de voz (DeepFilterNet), la transcripción (Whisper) y el
motor de vídeo (huashu-motion). Los efectos de sonido y la música se descargan de Mixkit, que son gratis para usar
en redes y anuncios. Tus vídeos no salen de tu ordenador.

CapCut **no** hace falta. Si alguien quiere el proyecto editable en CapCut, puede pedírselo a Claude, pero
necesita CapCut 9 y una plantilla vacía llamada `PLANTILLA-REELS`.

## En Mac

Funciona en Mac con chip Apple (**M1, M2, M3 o M4**) y **macOS 14 Sonoma o posterior**. Para saberlo: menú Apple
(arriba a la izquierda) > **Acerca de este Mac**. Si pone "Intel", no funciona: la limpieza de voz no tiene versión
para esos Mac.

Los pasos son los mismos, con estos cambios:

1. **Descargar**: al bajar el ZIP, el Mac lo descomprime solo en Descargas. Mueve la carpeta al Escritorio.
2. **Instalar**: doble clic en **`1 INSTALAR.command`** (no en el `.bat`).
   - La primera vez el Mac dice que no puede abrirlo porque "no se ha podido verificar el desarrollador". Ve a
     **Ajustes del Sistema > Privacidad y seguridad**, baja hasta el final y pulsa **Abrir igualmente**. En Mac más
     antiguos vale con clic derecho en el fichero > **Abrir** > **Abrir**.
   - Te pedirá **la contraseña de tu Mac** para instalar Homebrew (el instalador de programas). Al escribirla no se
     ve nada en la pantalla: es normal. Escríbela y pulsa Enter.
   - Puede salir una ventana para instalar las "herramientas de línea de comandos": pulsa **Instalar**.
3. **Entrar**: doble clic en **`2 EDITAR.command`**.
4. **Tu primer reel**: la carpeta está en **Películas > Reels > 1 TOMAS EN BRUTO** (en Mac, la carpeta de vídeos se
   llama Películas). Lo terminado sale en **Películas > Reels > 2 PARA SUBIR**.

En Mac no existe la opción de CapCut: solo el vídeo terminado.
