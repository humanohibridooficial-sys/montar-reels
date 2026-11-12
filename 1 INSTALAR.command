#!/bin/bash
# Doble clic y listo (Mac): instala todo lo que necesita el editor. Se puede repetir; lo que ya está, lo salta.
cd "$(dirname "$0")"
bash ./instalar.sh
echo
echo 'Si arriba pone "Todo listo", ya puedes abrir 2 EDITAR.command.'
echo "Si hay algo en rojo, cierra esta ventana y vuelve a hacer doble clic en 1 INSTALAR.command."
read -r -p "Pulsa Enter para cerrar..." _
