# Paso a paso: el editor de reels en tu ordenador

Para cualquier persona con **Windows 10 u 11**, aunque no hayas tocado nunca un ordenador más allá del navegador.
No vas a escribir ningún comando: todo es doble clic y hablarle a Claude en español.

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
