# Prueba de La Máquina en el puente (spec hh-kpi 2026-10-28-negocio-sencillo-dos-mundos, P5 M1b).
#   python puente/prueba_maquina.py
# Levanta un Negocio falso en 127.0.0.1 y sube unas ideas y una pieza de prueba: no toca Negocio ni lanza Claude.
import http.server, json, os, sys, tempfile, threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import puente  # noqa: E402

fallos = 0


def ok(cond, msg):
    global fallos
    print("  ok   " if cond else "  FALLO", msg)
    fallos += 0 if cond else 1


P, H = "cc28435c-47cd-42cc-879d-c941f90220a5", "4cc1626f-0000-4000-8000-000000000002"
OTRO = "61498bf9-c466-4c82-9b90-7da97c333c04"
carpeta = tempfile.mkdtemp(prefix="maquina-").replace("\\", "/")

# Lo que puede hacer en cada mitad.
hi = puente.herramientas_maquina("ideas", "reel", carpeta)
ok("WebSearch" in hi and not any(x.startswith(f"Bash({puente.PY_PIL}") for x in hi), "ideas: lee la web y no ejecuta scripts de la skill")
for tipo in puente.TIPOS_MAQUINA:
    hp = puente.herramientas_maquina("pieza", tipo, carpeta)
    ok(not any(x.startswith("Web") for x in hp), f"pieza {tipo}: sin web")
    bash = [x for x in hp if x.startswith("Bash(")]
    ok(bash and all(x.startswith(f"Bash({puente.PY_PIL} {puente.NINO}/skills/") or x == f"Bash({puente.PY_PIL} {carpeta}/montar_pdf.py)" for x in bash),
       f"pieza {tipo}: solo scripts de la copia de Nino")
    ok(all(x in hp for x in (f"Write({carpeta}/**)", f"Edit({carpeta}/**)")) and not any(w.startswith("Write(") and carpeta not in w for w in hp),
       f"pieza {tipo}: escribe solo en su carpeta")
ok(f"Bash({puente.PY_PIL} {carpeta}/montar_pdf.py)" in puente.herramientas_maquina("pieza", "pdf", carpeta)
   and not any("montar_pdf" in x for x in puente.herramientas_maquina("pieza", "carrusel", carpeta)), "el montador del PDF, solo en el PDF")
ok(not any(x in ("Skill", "Task", "Agent", "PowerShell") for a in ("ideas", "pieza") for x in puente.herramientas_maquina(a, "reel", carpeta)),
   "nunca Skill, Task ni Agent")

for a in ("ideas", "pieza"):
    o = puente.orden_maquina(a, "carrusel", carpeta)
    # Cambiado a sabiendas (29-10, Luismi: "avatar y reglas de Kaizen"): de Kaizen, solo el avatar y REGLAS-KAIZEN.md;
    # nunca KAIZEN.md entero (su estructura es la de FF360(K)) ni la config de ~/.fabrica.
    ok(puente.NINO + "/skills" in o and f"{puente.NINO}/REGLAS-KAIZEN.md" in o and f"{puente.NINO}/avatar" in o,
       f"orden de {a}: Nino puro, con el avatar y las reglas fijas de Kaizen")
    ok("/.fabrica/KAIZEN.md" not in o and "/.fabrica/config" not in o, f"orden de {a}: nunca KAIZEN.md entero ni la config de FF360(K)")
    ok('"' not in o, f"orden de {a}: sin comillas dobles (el puente las cambia, pero mejor que no haya)")
ok("investigacion-viral" in puente.orden_maquina("ideas", "pdf", carpeta), "ideas: con investigacion-viral")
ok("pdf-lead-magnet" in puente.orden_maquina("pieza", "pdf", carpeta) and "guia.pdf" in puente.orden_maquina("pieza", "pdf", carpeta), "pieza pdf: su skill y su fichero")

# El pedido de la cola.
idea = {"angulo": "x", "gancho": "y", "prueba": {"url": "https://youtu.be/a", "numero": "1"}}
ok(puente.pedido_maquina("ideas", {"maquina": "reel", "proyectoId": P}) is None, "ideas: vale")
ok(puente.pedido_maquina("pieza", {"maquina": "reel", "proyectoId": P, "idea": idea}) is None, "pieza con idea: vale")
ok(puente.pedido_maquina("pieza", {"maquina": "reel", "proyectoId": P}) is not None, "pieza sin idea: no")
ok(puente.pedido_maquina("version", {"maquina": "reel", "proyectoId": P, "idea": idea}) is not None, "otra acción: no")
ok(puente.pedido_maquina("ideas", {"maquina": "historia", "proyectoId": P}) is not None, "otro tipo: no")
ok(puente.pedido_maquina("ideas", {"maquina": "reel", "proyectoId": "x"}) is not None, "sin proyecto: no")

# La subida, contra un Negocio falso.
recibido = {"posts": [], "puts": [], "auth": set(), "falla": None}


class Falso(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _resp(self, code, d):
        b = json.dumps(d).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        recibido["posts"].append((self.path.rsplit("/", 1)[1], d))
        recibido["auth"].add(self.headers.get("Authorization"))
        if recibido["falla"]:
            return self._resp(400, {"error": recibido["falla"]})
        if self.path.endswith("/ideas"):
            return self._resp(200, {"ok": True, "ideas": len(d["ideas"])})
        if d.get("paso") == "subir":
            return self._resp(200, {"url": f"http://127.0.0.1:{srv.server_port}/bucket/{d['nombre']}"})
        return self._resp(200, {"ok": True, "pasa": d.get("gates", {}).get("pasa")})

    def do_PUT(self):
        n = len(self.rfile.read(int(self.headers["Content-Length"])))
        recibido["puts"].append((self.path.rsplit("/", 1)[1], n, self.headers.get("Content-Type")))
        self._resp(200, {"Key": "x"})


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Falso)
threading.Thread(target=srv.serve_forever, daemon=True).start()
puente.NEGOCIO_URL = f"http://127.0.0.1:{srv.server_port}"
CLAVE = "x" * 30
os.environ["FANTASMA_SECRET"] = CLAVE


def escribir(nombre, d):
    with open(os.path.join(carpeta, nombre), "w", encoding="utf-8") as f:
        json.dump(d, f)


escribir("ideas.json", {"ideas": [idea, idea, idea]})
r = puente.subir_maquina("ideas", P, H, carpeta)
ruta, cuerpo = recibido["posts"][-1]
ok(r == "3 ideas subidas" and ruta == "ideas" and cuerpo["proyectoId"] == P and cuerpo["huecoId"] == H and len(cuerpo["ideas"]) == 3,
   "ideas: a /ideas, con el proyecto Atlas y la pieza")

for n, tam in (("slide-01.png", 1000), ("slide-02.png", 2000)):
    with open(os.path.join(carpeta, n), "wb") as f:
        f.write(os.urandom(tam))
escribir("pieza.json", {"titulo": "t", "caption": "c", "archivos": ["slide-01.png", "slide-02.png"], "gates": {"pasa": True},
                        "proyectoId": OTRO, "huecoId": "otro"})
recibido["posts"].clear()
r = puente.subir_maquina("pieza", P, H, carpeta)
pasos = [(ruta, d.get("paso")) for ruta, d in recibido["posts"]]
ok(pasos == [("maquina", "subir"), ("maquina", "subir"), ("maquina", "pieza")], f"pieza: subir cada fichero y luego la pieza ({pasos})")
ok(recibido["puts"] == [("slide-01.png", 1000, "image/png"), ("slide-02.png", 2000, "image/png")], "los dos ficheros enteros, como PNG")
fin = recibido["posts"][-1][1]
ok(fin["proyectoId"] == P and fin["huecoId"] == H, "los ids de pieza.json no mandan: va a su pieza")
ok("pasa los gates" in r and "no pasa" not in r, f"dice si pasa ({r})")
ok(recibido["auth"] == {f"Bearer {CLAVE}"}, "siempre con la clave del PC")

escribir("pieza.json", {"titulo": "t", "archivos": ["no-esta.png"], "gates": {"pasa": True}})
try:
    puente.subir_maquina("pieza", P, H, carpeta)
    ok(False, "un fichero que no está tendría que parar")
except RuntimeError as e:
    ok("no-esta.png" in str(e), "un fichero que no está: para")
escribir("pieza.json", {"titulo": "t", "archivos": ["../x.png"], "gates": {"pasa": True}})
try:
    puente.subir_maquina("pieza", P, H, carpeta)
    ok(False, "un nombre con ruta tendría que parar")
except RuntimeError:
    ok(True, "un nombre con ruta: para")
escribir("pieza.json", {"titulo": "t", "archivos": [], "gates": {"pasa": True}})
recibido["falla"] = "La cifra 37 no sale en ninguna fuente."
try:
    puente.subir_maquina("pieza", P, H, carpeta)
    ok(False, "un rechazo de Negocio tendría que parar")
except RuntimeError as e:
    ok("37" in str(e), "lo que rechaza Negocio se cuenta tal cual")
srv.shutdown()

if fallos:
    print(f"\n{fallos} fallo(s)")
    sys.exit(1)
print("\ntodo ok")
