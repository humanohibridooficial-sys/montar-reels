# Prueba de la subida del vídeo terminado (spec hh-kpi 2026-10-28-negocio-sencillo-dos-mundos, P3).
#   python puente/prueba_subida.py
# Levanta un Negocio falso en 127.0.0.1 (pedir, PUT, hecho) y sube un fichero de prueba: no toca Negocio de verdad.
import http.server, json, os, sys, tempfile, threading, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import puente  # noqa: E402

fallos = 0


def ok(cond, msg):
    global fallos
    print("  ok   " if cond else "  FALLO", msg)
    fallos += 0 if cond else 1


CLAVE = "x" * 30
ok(puente.clave_negocio(f'OTRA=1\nFANTASMA_SECRET="{CLAVE}"\n') == CLAVE, "lee la clave del .env.local, con comillas")
ok(puente.clave_negocio("FANTASMA_SECRET=corta\n") == "", "una clave corta no vale")
ok(puente.clave_negocio("NADA=1\n") == "", "sin clave: vacío")
ok("hay que subir el límite" in puente.motivo_subida(400, '{"statusCode":"413","error":"Payload too large","message":"The object exceeded the maximum allowed size"}', 148.0),
   "el tope de Supabase se dice claro")
ok(puente.motivo_subida(409, '{"error":"Solo reels"}', 1.0) == "Negocio respondió 409: Solo reels", "otro error: el de Negocio")

P, H = "61498bf9-c466-4c82-9b90-7da97c333c04", "4cc1626f-0000-4000-8000-000000000001"
ok(not puente.lanzar_subida("no-es-uuid", H, __file__), "sin proyecto válido no se lanza")

recibido = {"pasos": [], "bytes": 0, "auth": set()}


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
        recibido["pasos"].append(d["paso"])
        recibido["auth"].add(self.headers.get("Authorization"))
        if d["paso"] == "pedir":
            return self._resp(200, {"url": f"http://127.0.0.1:{srv.server_port}/subir"})
        return self._resp(200 if recibido["bytes"] else 409, {"ok": True} if recibido["bytes"] else {"error": "El vídeo no ha llegado al bucket"})

    def do_PUT(self):
        recibido["bytes"] = len(self.rfile.read(int(self.headers["Content-Length"])))
        recibido["tipo"] = self.headers.get("Content-Type")
        self._resp(200, {"Key": "x"})


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Falso)
threading.Thread(target=srv.serve_forever, daemon=True).start()
puente.NEGOCIO_URL = f"http://127.0.0.1:{srv.server_port}"
os.environ["FANTASMA_SECRET"] = CLAVE

with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
    f.write(os.urandom(3 * 1024 * 1024 + 7))
ok(puente.lanzar_subida(P, H, f.name), "con los dos ids, se lanza")
ok(not puente.lanzar_subida(P, H, f.name), "la misma pieza no se sube dos veces a la vez")
for _ in range(100):
    if puente.SUBIDAS[H]["estado"] != "subiendo":
        break
    time.sleep(0.05)
s = puente.SUBIDAS[H]
ok(s["estado"] == "hecho" and s["mb"] == 3.0, f"sube y queda hecho ({s})")
ok(recibido["pasos"] == ["pedir", "hecho"] and recibido["bytes"] == 3 * 1024 * 1024 + 7 and recibido["tipo"] == "video/mp4",
   "pedir, el fichero entero por PUT como video/mp4, y hecho")
ok(recibido["auth"] == {f"Bearer {CLAVE}"}, "con la clave del PC")
os.remove(f.name)
srv.shutdown()

if fallos:
    print(f"\n{fallos} fallo(s)")
    sys.exit(1)
print("\ntodo ok")
