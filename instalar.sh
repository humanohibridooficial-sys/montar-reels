#!/bin/bash
# Instalador del editor de reels para Mac (Apple M1 o posterior, macOS 14 o posterior). Se puede lanzar las veces que
# haga falta: lo que ya está, lo salta. Lo normal es abrirlo con doble clic en "1 INSTALAR.command".
# Es el mismo que instalar.ps1 de Windows, con Homebrew en vez de winget. Sin CapCut ni el puente con Negocio.
set -e
REPO="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO"

paso()  { echo; echo "== $1"; }
ok()    { echo "   ok: $1"; }
aviso() { echo "   aviso: $1"; }
para()  { echo; echo "ERROR: $1"; exit 1; }

# 0. Este Mac vale ---------------------------------------------------------------------------------------------
paso "0/8 Compruebo el Mac"
[ "$(uname -s)" = "Darwin" ] || para "esto es para Mac. En Windows usa 1 INSTALAR.bat"
[ "$(uname -m)" = "arm64" ] || para "hace falta un Mac con chip Apple (M1 o posterior). Los Mac con Intel no pueden con la limpieza de voz"
mac=$(sw_vers -productVersion | cut -d. -f1)
[ "$mac" -ge 14 ] || para "hace falta macOS 14 (Sonoma) o posterior; este tiene $(sw_vers -productVersion). Actualízalo en Ajustes > General > Actualización de software"
libre=$(df -g "$HOME" | awk 'NR==2 {print $4}')
[ "$libre" -ge 20 ] || aviso "solo hay $libre GB libres; hacen falta unos 20"
ok "macOS $(sw_vers -productVersion), chip Apple"

# 1. Programas -------------------------------------------------------------------------------------------------
paso "1/8 Programas: Homebrew, Node.js, Git, Python 3.11 y 3.12, FFmpeg, Chrome y Claude Code"
if ! command -v brew > /dev/null 2>&1 && [ ! -x /opt/homebrew/bin/brew ]; then
    echo "   instalando Homebrew (el instalador de programas de Mac). Te pedirá la contraseña de tu Mac:"
    echo "   escríbela aunque no se vea nada al teclear y pulsa Enter."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
eval "$(/opt/homebrew/bin/brew shellenv)"
for f in node git python@3.11 python@3.12 ffmpeg; do
    if brew list --formula "$f" > /dev/null 2>&1; then ok "$f ya estaba"; else echo "   instalando $f..."; brew install --quiet "$f"; fi
done
if [ -d "/Applications/Google Chrome.app" ]; then ok "Chrome ya estaba"; else echo "   instalando Google Chrome..."; brew install --quiet --cask google-chrome; fi
if command -v claude > /dev/null 2>&1; then ok "Claude Code ya estaba"; else echo "   instalando Claude Code..."; npm install -g @anthropic-ai/claude-code --silent; fi
PY311=/opt/homebrew/opt/python@3.11/bin/python3.11
PY312=/opt/homebrew/opt/python@3.12/bin/python3.12

# 2. Entorno de Python del editor ------------------------------------------------------------------------------
paso "2/8 Entorno de Python propio en .venv (no toca el Python del sistema)"
[ -x .venv/bin/python ] || "$PY312" -m venv .venv
.venv/bin/python -m pip install --upgrade pip --quiet
# uiautomation es solo para manejar CapCut en Windows: en Mac no se instala
grep -v '^uiautomation' requirements.txt > "${TMPDIR:-/tmp}/requisitos-mac.txt"
.venv/bin/python -m pip install --quiet -r "${TMPDIR:-/tmp}/requisitos-mac.txt"
ok "librerías instaladas"

# 3. Modelos y fuentes -----------------------------------------------------------------------------------------
paso "3/8 Modelos de MediaPipe y fuentes libres"
bajar() { [ -f "$2" ] && return 0; curl -fsSL "$1" -o "$2" && ok "$(basename "$2")"; }
mkdir -p modelos fuentes
MP=https://storage.googleapis.com/mediapipe-models
bajar "$MP/image_segmenter/selfie_segmenter/float16/latest/selfie_segmenter.tflite" modelos/selfie_segmenter.tflite
bajar "$MP/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task" modelos/hand_landmarker.task
bajar "$MP/face_detector/blaze_face_short_range/float16/latest/blaze_face_short_range.tflite" modelos/blaze_face_short_range.tflite
GF=https://raw.githubusercontent.com/google/fonts/main/ofl
bajar "$GF/anton/Anton-Regular.ttf" fuentes/Anton-Regular.ttf
bajar "$GF/anton/OFL.txt" fuentes/OFL-Anton.txt
bajar "$GF/bebasneue/BebasNeue-Regular.ttf" fuentes/BebasNeue-Regular.ttf
bajar "$GF/bebasneue/OFL.txt" fuentes/OFL-BebasNeue.txt
bajar "$GF/archivoblack/ArchivoBlack-Regular.ttf" fuentes/ArchivoBlack-Regular.ttf
bajar "$GF/archivoblack/OFL.txt" fuentes/OFL-ArchivoBlack.txt

# 4. Configuración ---------------------------------------------------------------------------------------------
paso "4/8 Tu configuración y tu estilo"
[ -f config.json ] && ok "config.json ya estaba: no lo toco" || { cp config.ejemplo.json config.json; ok "creado config.json"; }
[ -f .env ] && ok ".env ya estaba: no lo toco" || { cp .env.ejemplo .env; ok "creado .env"; }
mkdir -p trabajo/transcripciones trabajo/piezas mi-estilo/referencias
[ -f mi-estilo/estilo.md ] || { cp mi-estilo/estilo.ejemplo.md mi-estilo/estilo.md; ok "creado mi-estilo/estilo.md"; }
[ -f mi-estilo/recursos.md ] || { cp mi-estilo/recursos.ejemplo.md mi-estilo/recursos.md; ok "creado mi-estilo/recursos.md"; }

# 5. El motor --------------------------------------------------------------------------------------------------
paso "5/8 El motor: limpieza de voz, transcripción, render y sonidos (la primera vez tarda 10-20 minutos)"
[ -x .venv-df/bin/python ] || "$PY311" -m venv .venv-df
.venv-df/bin/python -m pip install --upgrade pip --quiet
echo "   librerías de la limpieza de voz (DeepFilterNet, unos 800 MB)..."
.venv-df/bin/python -m pip install --quiet torch==2.5.1 torchaudio==2.5.1 numpy==1.26.4 soundfile==0.14.0 deepfilternet==0.5.6
ok "limpieza de voz"
[ -x .venv-fw/bin/python ] || "$PY312" -m venv .venv-fw
.venv-fw/bin/python -m pip install --upgrade pip --quiet
.venv-fw/bin/python -m pip install --quiet faster-whisper==1.2.1
ok "transcripción (faster-whisper)"
# huashu-motion fijado al commit de la etiqueta v0.3.1 (una etiqueta se puede mover; un commit no)
HM="$REPO/vendor/huashu-motion"; HMCOMMIT=52467f99c602b76ba86d511d37acdfe93fa1e16e
[ -d "$HM/.git" ] || git clone --quiet https://github.com/alchaincyf/huashu-motion.git "$HM"
git -C "$HM" fetch --quiet origin
git -C "$HM" checkout --quiet "$HMCOMMIT"
[ "$(git -C "$HM" rev-parse HEAD)" = "$HMCOMMIT" ] || para "huashu-motion no está en la versión probada. Borra vendor/huashu-motion y vuelve a lanzar"
chmod +x motor/om
ok "render (huashu-motion 0.3.1, ${HMCOMMIT:0:7})"
# Tus carpetas de vídeo, en Películas (así se llama la carpeta de vídeos en Mac)
REELS="$HOME/Movies/Reels"; RECURSOS="$REELS/3 RECURSOS"
mkdir -p "$REELS/1 TOMAS EN BRUTO" "$REELS/2 PARA SUBIR" "$RECURSOS/MUSICA" "$REELS/motor-datos/fichas" "$REELS/motor-datos/voz" "$REELS/motor-datos/perfil"
if [ -f motor/config.json ]; then ok "motor/config.json ya estaba: no lo toco"
else
    "$PY312" - "$REPO" "$REELS" <<'EOF'
import json, sys, pathlib
repo, reels = sys.argv[1], sys.argv[2]
c = {'carpeta_contenido': reels, 'carpeta_tomas': f'{reels}/1 TOMAS EN BRUTO', 'carpeta_reutilizables': f'{reels}/3 RECURSOS',
     'carpeta_datos': f'{reels}/motor-datos', 'carpeta_render': str(pathlib.Path.home() / 'reels-render'),
     'carpeta_salida': f'{reels}/2 PARA SUBIR', 'om': f'{repo}/motor/om',
     'python_df': f'{repo}/.venv-df/bin/python', 'python_fw': f'{repo}/.venv-fw/bin/python'}
json.dump(c, open(f'{repo}/motor/config.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
EOF
    ok "creado motor/config.json (tus vídeos van en Películas > Reels)"
fi
# Efectos y música libres de Mixkit (mixkit.co/license). Se bajan a TU Mac: su licencia no deja repartirlos sueltos.
while read -r nombre id; do
    [ -f "$RECURSOS/$nombre.wav" ] && continue
    if curl -fsSL "https://assets.mixkit.co/active_storage/sfx/$id/$id-preview.mp3" -o "${TMPDIR:-/tmp}/$nombre.mp3"; then
        ffmpeg -v error -y -i "${TMPDIR:-/tmp}/$nombre.mp3" "$RECURSOS/$nombre.wav"; rm -f "${TMPDIR:-/tmp}/$nombre.mp3"
    else aviso "no pude bajar $nombre (el montaje sale igual, sin ese efecto)"; fi
done <<'EOF'
SFX-P-golpe 2180
SFX-P-golpe-grave 1143
SFX-P-barrido 175
SFX-P-absorcion 784
SFX-P-subida 790
SFX-P-latido 498
SFX-P-silbato 615
SFX-P-tic 2568
SFX-P-cierre 951
SFX-P-grada 2111
EOF
while read -r nombre id; do
    [ -f "$RECURSOS/MUSICA/$nombre.mp3" ] && continue
    curl -fsSL "https://assets.mixkit.co/music/$id/$id.mp3" -o "$RECURSOS/MUSICA/$nombre.mp3" || aviso "no pude bajar la música $nombre"
done <<'EOF'
M-la-raiz-indie-rock 1157
M-dare-me-indie-rock 1135
M-a-game-electro 777
M-i-do-edm-optimista 1001
M-karma-dance-pop 1183
M-heartbeat-indie-pop 1000
M-better-times-synthpop 173
M-driving-ambition-emotiva 32
M-dreaming-big-emotiva 31
EOF
ok "efectos y música de Mixkit en $RECURSOS"

# 6. Skill y agentes para Claude Code --------------------------------------------------------------------------
paso "6/8 Skill 'montar-reels' y agentes para Claude Code"
mkdir -p "$HOME/.claude/skills/montar-reels" "$HOME/.claude/agents"
sed "s#{{REPO}}#$REPO#g" skill/SKILL.md > "$HOME/.claude/skills/montar-reels/SKILL.md"
for a in .claude/agents/*.md; do sed "s#{{REPO}}#$REPO#g" "$a" > "$HOME/.claude/agents/$(basename "$a")"; ok "agente $(basename "$a" .md)"; done
ok "skill copiada y apuntando a $REPO"

# 7. Comprobación ----------------------------------------------------------------------------------------------
paso "7/8 Compruebo que cargan"
.venv/bin/python -c "import numpy, PIL, cv2, mediapipe, faster_whisper" && ok "librerías del editor"
.venv-df/bin/python -c "import df.enhance" && ok "limpieza de voz"
.venv-fw/bin/python -c "import faster_whisper" && ok "transcripción"

paso "8/8 Todo"
bash "$REPO/comprobar.sh"
