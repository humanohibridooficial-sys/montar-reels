# El guion de /guion, con sus marcas, en una página para leer en el móvil mientras grabas (spec 2026-11-09-revisar-entrega).
#   python guion_movil.py <guion.txt>     -> <guion>.html al lado (déjalo en OneDrive y ábrelo en el móvil)
# Formato del guion: texto plano. Las líneas que empiezan por # son notas (la primera, el título). Las marcas van entre
# corchetes, como las escribe /guion §3b: [RÁPIDO] [PAUSA] [DESPACIO] [PALMAS] [GESTO: ...] [ACABA].
import html, os, re, sys

MARCAS = {  # marca -> (color, qué hacer, en una línea)
    "RÁPIDO": ("#E0623C", "más rápido y con energía"),
    "PAUSA": ("#E0B83C", "1 segundo callado, mirando a la lente"),
    "DESPACIO": ("#4C8DE0", "más lento y tranquilo, sin bajar el volumen"),
    "ACABA": ("#3FB37F", "la última palabra igual de fuerte que la primera"),
    "PALMAS": ("#A77BE0", "palmas abiertas hacia arriba"),
    "GESTO": ("#A77BE0", "el gesto que se indica"),
}
ANTES = [  # lo que el comprobador no puede medir o que se arregla antes de empezar
    "En 4K.",
    "Cámara a la altura de los ojos. Con el móvil en la mano, súbelo; no mires la pantalla, mira la lente.",
    "Deja aire debajo de la barbilla: la cara en la mitad de arriba de la pantalla.",
    "Luz de frente o de lado, nunca detrás de ti.",
    "Ropa sin logos de otras marcas.",
    "Medio segundo callado y empiezas por la primera palabra del guion, entera.",
    "Entre frases, manos abajo y quieto: muévete solo mientras hablas.",
]


def marca(m):
    nombre = m.split(":", 1)[0].strip().upper().replace("RAPIDO", "RÁPIDO")
    color, _ = MARCAS.get(nombre, ("#888888", ""))
    return f'<span class="m" style="--c:{color}">{html.escape(m.strip())}</span>'


def linea(texto):
    if re.fullmatch(r"\s*\[\s*PAUSA\s*\]\s*", texto, re.I):
        return '<p class="pausa">PAUSA &middot; 1 segundo mirando a la lente</p>'
    partes = re.split(r"(\[[^\]]*\])", texto)
    cuerpo = "".join(marca(p[1:-1]) if p.startswith("[") else html.escape(p) for p in partes)
    return f"<p>{cuerpo}</p>"


def pagina(texto):
    lineas = [l for l in texto.splitlines() if l.strip()]
    notas = [l.lstrip("# ").strip() for l in lineas if l.lstrip().startswith("#")]
    titulo = notas[0] if notas else "Guion"
    cuerpo = "\n".join(linea(l) for l in lineas if not l.lstrip().startswith("#"))
    leyenda = "".join(f'<li><span class="m" style="--c:{c}">{n}</span> {html.escape(q)}</li>' for n, (c, q) in MARCAS.items())
    antes = "".join(f"<li>{html.escape(a)}</li>" for a in ANTES)
    extra = "".join(f"<p class='nota'>{html.escape(n)}</p>" for n in notas[1:])
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titulo)}</title>
<style>
:root {{ --fondo:#0B0F14; --texto:#F2F2F2; --suave:#9AA4AF; }}
body {{ margin:0; background:var(--fondo); color:var(--texto); font-family:system-ui,-apple-system,"Segoe UI",sans-serif; }}
main {{ max-width:680px; margin:0 auto; padding:24px 16px 120px; }}
h1 {{ font-size:20px; color:var(--suave); font-weight:600; margin:0 0 12px; }}
details {{ background:#141A22; border-radius:10px; padding:10px 14px; margin-bottom:12px; font-size:16px; color:var(--suave); }}
summary {{ cursor:pointer; color:var(--texto); font-weight:600; }}
details ul {{ margin:8px 0 4px; padding-left:20px; line-height:1.5; }}
.guion p {{ font-size:30px; line-height:1.4; margin:0 0 22px; }}
.m {{ display:inline-block; font-size:15px; font-weight:700; letter-spacing:.04em; color:var(--fondo); background:var(--c);
      border-radius:6px; padding:2px 8px; margin-right:8px; vertical-align:middle; }}
.pausa {{ font-size:18px !important; font-weight:700; color:#E0B83C; border-top:2px dashed #E0B83C; border-bottom:2px dashed #E0B83C;
          padding:14px 0; text-align:center; }}
.nota {{ font-size:15px !important; color:var(--suave); }}
</style></head><body><main>
<h1>{html.escape(titulo)}</h1>
<details open><summary>Antes de grabar</summary><ul>{antes}</ul></details>
<details><summary>Qué significa cada marca</summary><ul>{leyenda}</ul></details>
{extra}
<section class="guion">
{cuerpo}
</section>
</main></body></html>
"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("uso: python guion_movil.py <guion.txt>")
    origen = sys.argv[1]
    destino = os.path.splitext(origen)[0] + ".html"
    open(destino, "w", encoding="utf-8").write(pagina(open(origen, encoding="utf-8").read()))
    print("->", destino)
