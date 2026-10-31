#!/bin/sh
# Monta, renderiza, mezcla, revisa y entrega las piezas que se le pasen. Las rutas salen de motor/config.json.
# Una a una y con 2 workers: con más, el ordenador se quedó sin memoria el 28-10.
#   sh motor/montar.sh 75 76 ...      (SALTAR_MONTAR=1 si p<n>/ ya está montado; SALIDA=<carpeta> para otra salida;
#                                      FORZAR=1 renderiza aunque la puerta del plan falle)
# Solo llega a la carpeta de salida lo que pasa la revisión del fichero; lo demás se queda en el render con su qc.json.
cd "$(dirname "$0")"
cfg() { PYTHONIOENCODING=utf-8 python -c "import rutas; print(rutas.$1)"; }
RENDER="$(cfg RENDER)"; OM="$(cfg OM)"; DEST="${SALIDA:-$(cfg SALIDA)}"
mkdir -p "$RENDER" "$DEST"
slug() { PYTHONIOENCODING=utf-8 python -c "
import json, re, unicodedata, rutas
t = json.load(open(rutas.FICHAS / '$1.json', encoding='utf-8'))['titulo']
t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
print(re.sub(r'[^a-z0-9]+', '-', t).strip('-'))"; }
for n in "$@"; do
  P="$RENDER/p$n"; LOG="$RENDER/p$n.montar.log"
  if [ -z "$SALTAR_MONTAR" ]; then
    PYTHONIOENCODING=utf-8 python montar.py $n > "$LOG" 2>&1 || { echo "$n MONTAR FALLIDO: $(tail -1 "$LOG")"; continue; }
  fi
  PYTHONIOENCODING=utf-8 python puerta_plan.py $n || [ -n "$FORZAR" ] || { echo "$n PARADO EN LA PUERTA DEL PLAN (arregla la ficha o FORZAR=1)"; continue; }
  touch "$P/.marca"; R=""
  for i in 1 2 3; do
    (cd "$P" && sh "$OM" render . --workers 2 --frames jpg -o out/p$n.mp4 > out.log 2>&1)
    R=$(find "$P/out" -name "p$n-v*.mp4" -newer "$P/.marca" | head -1)
    [ -n "$R" ] && break
  done
  [ -z "$R" ] && { echo "$n RENDER FALLIDO (mira $P/out.log)"; continue; }
  PYTHONIOENCODING=utf-8 python mezcla.py $n "$R" "$P/out/p$n-final.mp4" > /dev/null || { echo "$n MEZCLA FALLIDA"; continue; }
  # Huashu guarda cada fotograma de cada render (13-17 GB por pieza): el 28-10 llenó el disco C. Hecha la pieza, sobra.
  rm -rf "$P/.om/cache/frames"
  PYTHONIOENCODING=utf-8 python revisar_export.py $n "$P/out/p$n-final.mp4" || { echo "$n NO SE ENTREGA: mira $P/out/qc.json"; continue; }
  PYTHONIOENCODING=utf-8 python puerta_plan.py $n --anotar > /dev/null || true
  F=$(PYTHONIOENCODING=utf-8 python destino.py "$DEST" $n "$(slug $n)")
  cp "$P/out/p$n-final.mp4" "$F"
  echo "$n HECHO -> $F"
  echo "   para el revisor-montaje: $P/out/hoja.jpg y $P/out/qc.json"
done
