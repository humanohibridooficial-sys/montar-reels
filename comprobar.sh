#!/bin/bash
# Comprueba que el editor está listo en este Mac. Se puede lanzar cuando quieras; no cambia nada.
REPO="$(cd "$(dirname "$0")" && pwd)"
fallos=0; avisos=0
bien() { echo "  ok     $1"; }
mal()  { echo "  FALTA  $1"; echo "         -> $2"; fallos=$((fallos + 1)); }
ojo()  { echo "  aviso  $1"; avisos=$((avisos + 1)); }
[ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)"
REPITE="haz doble clic otra vez en 1 INSTALAR.command"

echo; echo "Comprobando el editor de reels en $REPO"
for p in ffmpeg ffprobe git node; do command -v $p > /dev/null 2>&1 && bien "$p" || mal "$p" "$REPITE"; done
command -v claude > /dev/null 2>&1 && bien "Claude Code" || mal "Claude Code" "$REPITE"
[ -d "/Applications/Google Chrome.app" ] && bien "Chrome (el motor dibuja con él)" || mal "Google Chrome" "$REPITE"

if [ -x "$REPO/.venv/bin/python" ] && "$REPO/.venv/bin/python" -c "import numpy, PIL, cv2, mediapipe" 2> /dev/null; then bien "librerías del editor"; else mal "librerías del editor (.venv)" "$REPITE"; fi
if [ -x "$REPO/.venv-df/bin/python" ] && "$REPO/.venv-df/bin/python" -c "import df.enhance" 2> /dev/null; then bien "limpieza de voz (DeepFilterNet)"; else mal "limpieza de voz" "$REPITE"; fi
if [ -x "$REPO/.venv-fw/bin/python" ] && "$REPO/.venv-fw/bin/python" -c "import faster_whisper" 2> /dev/null; then bien "transcripción (faster-whisper)"; else mal "transcripción" "$REPITE"; fi
[ -f "$REPO/vendor/huashu-motion/cli/om.js" ] && bien "render (huashu-motion)" || mal "render (vendor/huashu-motion)" "$REPITE"
for f in selfie_segmenter.tflite blaze_face_short_range.tflite; do [ -f "$REPO/modelos/$f" ] && bien "modelo $f" || mal "modelos/$f" "$REPITE"; done
for f in Anton-Regular.ttf BebasNeue-Regular.ttf; do [ -f "$REPO/fuentes/$f" ] && bien "fuente $f" || mal "fuentes/$f" "$REPITE"; done
for f in config.json motor/config.json mi-estilo/estilo.md mi-estilo/recursos.md; do [ -f "$REPO/$f" ] && bien "$f" || mal "$f" "$REPITE"; done

REELS="$HOME/Movies/Reels"
[ -d "$REELS/1 TOMAS EN BRUTO" ] && bien "carpeta de tus tomas: Películas > Reels > 1 TOMAS EN BRUTO" || mal "carpeta de tomas" "$REPITE"
n=$(ls "$REELS/3 RECURSOS"/SFX-*.wav 2> /dev/null | wc -l | tr -d ' ')
[ "$n" -gt 0 ] && bien "$n efectos de sonido" || ojo "no hay efectos de sonido (el vídeo sale igual, sin efectos)"
[ -f "$HOME/.claude/skills/montar-reels/SKILL.md" ] && bien "skill montar-reels" || mal "skill montar-reels" "$REPITE"
for a in director-montaje revisor-montaje; do [ -f "$HOME/.claude/agents/$a.md" ] && bien "agente $a" || mal "agente $a" "$REPITE"; done

echo
if [ "$fallos" -eq 0 ]; then echo "Todo listo ($avisos avisos). Pon tu vídeo en Películas > Reels > 1 TOMAS EN BRUTO, abre 2 EDITAR.command y dile a Claude: 'edita este reel'."
else echo "Faltan $fallos cosas (y $avisos avisos). $REPITE."; exit 1; fi
