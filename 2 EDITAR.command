#!/bin/bash
# Doble clic (Mac): abre Claude Code en esta carpeta. Luego le dices "edita este reel".
cd "$(dirname "$0")"
[ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)"
if ! command -v claude > /dev/null 2>&1; then
  echo "No encuentro Claude Code. Haz doble clic primero en 1 INSTALAR.command."
  read -r -p "Pulsa Enter para cerrar..." _
  exit 1
fi
claude
