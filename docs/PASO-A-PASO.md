# Paso a paso: el editor de reels en tu ordenador

Para cualquier persona con **Windows 10 u 11**. No hace falta saber programar. Tiempo: 30-45 minutos la
primera vez (casi todo es esperar descargas).

## Qué vas a tener
Le das a Claude Code un vídeo tuyo hablando a cámara y te devuelve un **proyecto de CapCut ya montado y
editable**: cortes, subtítulos con tus palabras clave, rótulos, recursos visuales y música. Un agente
**director** decide cómo montarlo y un agente **revisor** lo revisa como un editor profesional antes de
dártelo por bueno. Todo con **tu** marca y **tu** estilo.

## Antes de empezar (necesitas)
1. **Claude** con suscripción (Pro o superior): es la IA que dirige el montaje. Sin ella no funciona.
2. **CapCut para ordenador, versión 9** (no la 10: rechaza los proyectos). Instálalo desde su web y ábrelo
   una vez. Si se actualiza solo, desactiva las actualizaciones automáticas en sus ajustes.
3. Unos 5 GB libres.

## Paso 1 · Descargar el editor
1. Abre esta página: https://github.com/humanohibridooficial-sys/montar-reels
2. Botón verde **Code** → **Download ZIP**.
3. Descomprímelo en una carpeta sin tildes ni espacios raros, por ejemplo `C:\editor-reels`.

## Paso 2 · Instalar
1. Abre la carpeta, haz clic en la barra de direcciones de arriba, escribe `powershell` y pulsa Enter.
2. En la ventana azul, copia y pega estas dos líneas (Enter después de cada una):
   ```
   Set-ExecutionPolicy -Scope Process Bypass
   .\instalar.ps1
   ```
3. Espera. Instala lo que falte (Node, Git, Python, FFmpeg, Claude Code) y descarga modelos y fuentes. Si
   te dice "cierra esta ventana y abre otra", hazlo y repite el paso 2.

## Paso 3 · La plantilla de CapCut (la única cosa a mano)
1. Abre CapCut → **Nuevo proyecto** → no añadas nada.
2. Cambia su nombre a **PLANTILLA-REELS** (exactamente así) y cierra CapCut.

## Paso 4 · Comprobar que todo está listo
En la misma ventana azul:
```
.\comprobar.ps1
```
Tiene que terminar en verde con **"Todo listo"**. Si sale algo en rojo, debajo te dice cómo arreglarlo
(casi siempre: volver a lanzar `.\instalar.ps1`). Repite hasta que salga en verde.

## Paso 5 · Tu marca y tu estilo (10 minutos, una vez)
1. Abre `config.json` con el Bloc de notas y cambia `color_clave` (el color de tus palabras destacadas) y
   `color_marca` por los tuyos, en formato `#RRGGBB`.
2. Abre `mi-estilo\estilo.md` y rellena lo que sepas: de qué va tu cuenta, a quién hablas, lo que nunca
   quieres. Lo que no sepas, déjalo en blanco.
3. `mi-estilo\recursos.md` es tu catálogo de recursos de edición. Empieza con uno de ejemplo; crecerá con
   lo que aprendas de tus referencias.

## Paso 6 · Tu primer reel
1. Graba un vídeo vertical hablando a cámara. Si quieres recursos arriba (media pantalla, texto detrás),
   grábate algo más abierto: que tu cabeza empiece hacia la mitad de la pantalla, no arriba del todo.
2. Abre la carpeta del editor en la ventana azul y escribe `claude`. La primera vez te pedirá entrar con tu
   cuenta de Claude.
3. Dile: **"edita este reel: C:\ruta\a\mi-video.mp4"**.
4. Te propondrá cómo montarlo. Cuando esté, abre CapCut: el proyecto sale el primero de la lista.
5. Expórtalo desde CapCut y dile a Claude dónde lo has guardado: el revisor lo mirará y te dirá qué corregir.

## Para que edite como tú (opcional, después)
- **"Aprende de mis reels"**: copia 5-10 reels tuyos terminados a `mi-estilo\mis-reels\`.
- **"Analiza esta cuenta"**: pega enlaces de reels que admires en `mi-estilo\referencias.txt`. Se descargan
  solo en tu ordenador para analizarlos; no se republican.

## Si algo falla
Lanza `.\comprobar.ps1`: te dice qué falta y cómo arreglarlo. El fallo más común es CapCut 10 o la plantilla
con otro nombre.
