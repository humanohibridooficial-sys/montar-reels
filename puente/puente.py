# Puente local entre Negocio y montar-reels (spec specs/2026-10-12-puente-negocio.md).
# Negocio, abierto en el navegador, llama a http://127.0.0.1:7810 y aquí se lanza Claude Code (`claude -p`)
# con el director o el revisor, en este PC, que es donde están CapCut, las tomas y el catálogo.
#   python puente/puente.py        (instalar.ps1 lo deja arrancando solo con Windows, con pythonw)
# Solo biblioteca estándar. Seguridad: escucha en 127.0.0.1, CORS solo para Negocio, cabecera X-Clave-Puente
# con la clave de config.json (`puente_clave`) y `claude -p` con las herramientas cerradas.
import json, os, re, subprocess, sys, threading, time, uuid, shutil, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import config  # noqa: E402

VERSION = "1"
PUERTO = int(config.C.get("puente_puerto", 7810))
CLAVE = str(config.C.get("puente_clave", ""))
TOMAS = os.path.realpath(config.ruta("carpeta_tomas", config.C.get("carpeta_trabajo", "trabajo")))
ORIGENES = {"https://negocio.humanohibrido.es", "http://localhost:3000"} | set(config.C.get("puente_origenes", []))
VIDEO = re.compile(r"\.(mp4|mov|m4v)$", re.I)
DIAS_TOMAS = 14
MAX_TOMAS = 30  # los más nuevos: en Ads y contenido hay cientos de vídeos (179 en 14 días el 12-10)
PY = sys.executable.replace("pythonw.exe", "python.exe").replace("\\", "/")
DIR_TRABAJOS = os.path.join(RAIZ, "trabajo", "_puente")
os.makedirs(DIR_TRABAJOS, exist_ok=True)
TRABAJOS: dict[str, dict] = {}
CERROJO = threading.Lock()  # comprobar "ya hay uno" y lanzar, de una vez: dos clics seguidos llegan en dos hilos


def dentro_de_tomas(p: str) -> bool:
    """La ruta pedida tiene que estar dentro de la carpeta de tomas (sin salirse con '..')."""
    r = os.path.realpath(p)
    return os.path.commonpath([r, TOMAS]) == TOMAS


def listar_tomas() -> list[dict]:
    limite = time.time() - DIAS_TOMAS * 86400
    out = []
    for raiz, dirs, ficheros in os.walk(TOMAS):
        # Fuera piezas reutilizables (00-...), descartes y compuestos (_...): no son tomas ni exports.
        dirs[:] = [d for d in dirs if not d.startswith(("_", ".", "00-"))]
        for f in ficheros:
            if not VIDEO.search(f):
                continue
            p = os.path.join(raiz, f)
            try:
                st = os.stat(p)
            except OSError:
                continue  # OneDrive bajo demanda: puede no estar en el disco
            if st.st_mtime < limite:
                continue
            enc = os.path.splitext(p)[0] + ".encuadre.json"
            medida = json.load(open(enc, encoding="utf-8")) if os.path.exists(enc) else None
            out.append({"ruta": p, "nombre": f, "carpeta": os.path.relpath(raiz, TOMAS), "modificado": st.st_mtime,
                        "mb": round(st.st_size / 1e6, 1), "encuadre": medida})
    return sorted(out, key=lambda x: -x["modificado"])[:MAX_TOMAS]


def herramientas() -> list[str]:
    """Lo que Claude puede usar sin preguntar. Nada de git, red ni borrar."""
    return ["Read", "Write", "Edit", "Glob", "Grep", "Task", "Agent",
            f"Bash({PY}:*)", "Bash(ffmpeg:*)", "Bash(ffprobe:*)"]


def linea_de_evento(ev: dict) -> list[str]:
    """Un evento de `claude -p --output-format stream-json` en líneas legibles. Sin esto el log se queda vacío
    hasta el final y Negocio parece colgado (13-10: se lanzaron cinco montajes a la vez por eso)."""
    if ev.get("type") == "result":  # repite el último mensaje; solo vale cuando acaba en error
        return str(ev.get("result") or "").splitlines() if ev.get("is_error") else []
    if ev.get("type") != "assistant":
        return []
    out = []
    for b in (ev.get("message") or {}).get("content") or []:
        if b.get("type") == "text" and b.get("text", "").strip():
            out += b["text"].strip().splitlines()
        elif b.get("type") == "tool_use":
            i = b.get("input") or {}
            que = i.get("description") or i.get("subagent_type") or i.get("file_path") or i.get("pattern") or i.get("command") or ""
            out.append(f"· {b.get('name')}: {str(que)[:120]}".rstrip(": "))
    return out


def traducir(proc: subprocess.Popen, f, fin: str):
    for crudo in proc.stdout:
        try:
            lineas = linea_de_evento(json.loads(crudo))
        except ValueError:
            lineas = [crudo.rstrip()]  # errores de arranque, que no vienen en JSON
        for l in lineas:
            f.write(l + "\n")
        f.flush()
    rc = proc.wait()
    f.close()
    open(fin, "w").write(str(rc))


def en_marcha_para(clave: str) -> str | None:
    """El trabajo que ya está montando esta toma: pulsar dos veces no lanza dos directores sobre el mismo proyecto."""
    for tid, t in TRABAJOS.items():
        if t.get("clave") == clave and t["proc"].poll() is None:
            return tid
    return None


def lanzar(tipo: str, orden: str, clave: str) -> str:
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("No encuentro Claude Code (claude) en este PC")
    tid = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    log = os.path.join(DIR_TRABAJOS, f"{tid}.log")
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    # En Windows, Claude Code lanza los comandos por PowerShell y las reglas Bash(...) no lo cubren (medido el
    # 12-10: Python denegado). Sin PowerShell usa Bash y las reglas valen: Python sí, `rm` denegado.
    cmd = [claude, "-p", orden, "--output-format", "stream-json", "--verbose",
           "--permission-mode", "dontAsk", "--allowedTools", *herramientas(),
           "--disallowedTools", "PowerShell", "--add-dir", TOMAS, "--add-dir", config.CAPCUT]
    f = open(log, "w", encoding="utf-8")
    proc = subprocess.Popen(cmd, cwd=RAIZ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                            text=True, encoding="utf-8", errors="replace",
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    threading.Thread(target=traducir, args=(proc, f, log + ".fin"), daemon=True).start()
    TRABAJOS[tid] = {"id": tid, "tipo": tipo, "inicio": time.time(), "proc": proc, "log": log, "clave": clave}
    return tid


def estado_trabajo(tid: str) -> dict | None:
    log = os.path.join(DIR_TRABAJOS, f"{tid}.log")
    t = TRABAJOS.get(tid)
    if not t and not os.path.exists(log):
        return None
    try:
        texto = open(log, encoding="utf-8", errors="replace").read()
    except OSError:
        texto = ""
    lineas = texto.strip().splitlines()[-40:]
    fin = log + ".fin"
    if os.path.exists(fin):  # el hilo ya escribió todo el log
        rc = open(fin).read().strip()
        estado = "hecho" if rc == "0" else "error"
    elif t:
        estado = "en_marcha"
    else:  # el puente se reinició con el trabajo a medias: ya nadie lo sigue
        estado, lineas = "error", lineas + ["El puente se reinició antes de que acabara este trabajo. Lánzalo otra vez."]
    inicio = t["inicio"] if t else os.path.getctime(log)
    return {"id": tid, "tipo": t["tipo"] if t else "montar", "estado": estado,
            "segundos": int(time.time() - inicio), "lineas": lineas}


def orden_montar(d: dict, toma: str) -> str:
    return (
        f"Monta el reel '{d.get('tema') or 'sin tema'}' (pieza {d.get('hueco')}, día {d.get('fecha')}) con la toma {toma}. "
        "Junto a la toma están su guion (.guion.txt), la hoja de montaje de Negocio (.montaje.json) y la medida del "
        "encuadre (.encuadre.json). Primero el agente director-montaje: tono, hoja de montaje y spec. Después monta el "
        f"proyecto de CapCut con `{PY} scripts/montar_reel.py <spec>` (desde la raíz de montar-reels). No esperes al "
        "export: el usuario lo hará en CapCut. Acaba con tres líneas: PROYECTO: <nombre del borrador de CapCut>, "
        "TONO: <tono y por qué> y NO PUDE: <lo que no se pudo hacer, o 'nada'>."
    )


def orden_revisar(d: dict, export: str) -> str:
    toma = d.get("toma") or ""
    return (
        f"Usa el agente revisor-montaje con el vídeo exportado {export}" + (f" (la toma original es {toma})" if toma else "") + ". "
        "Acaba con una línea VEREDICTO: se puede enseñar / no se puede enseñar, y una línea por fallo con este "
        "formato: FALLO: <montaje|grabacion> | <segundo> | <qué se ve y qué haría un editor>."
    )


class Puente(BaseHTTPRequestHandler):
    server_version = "puente-montar-reels/" + VERSION

    def log_message(self, *a):  # sin ruido en consola
        pass

    def _cors(self):
        origen = self.headers.get("Origin", "")
        if origen in ORIGENES:
            self.send_header("Access-Control-Allow-Origin", origen)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Clave-Puente")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            # Chrome lo exige para que una web pública llame a una dirección de la red local.
            self.send_header("Access-Control-Allow-Private-Network", "true")

    def _json(self, codigo: int, datos):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _permitido(self) -> bool:
        origen = self.headers.get("Origin")
        if origen is not None and origen not in ORIGENES:
            self._json(403, {"error": "Origen no permitido"}); return False
        if not CLAVE or self.headers.get("X-Clave-Puente", "") != CLAVE:
            self._json(403, {"error": "Falta la clave del puente o no es la de este PC"}); return False
        return True

    def do_OPTIONS(self):
        self.send_response(204 if self.headers.get("Origin", "") in ORIGENES else 403)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/estado":  # sin clave: solo dice si está vivo, para que Negocio sepa si pedirla
            return self._json(200, {"vivo": True, "version": VERSION, "claude": bool(shutil.which("claude")),
                                    "carpeta_tomas": TOMAS, "con_clave": bool(CLAVE)})
        if not self._permitido():
            return
        if self.path == "/comprobar":
            return self._json(200, {"ok": True})
        if self.path == "/tomas":
            return self._json(200, {"tomas": listar_tomas()})
        m = re.fullmatch(r"/trabajo/([\w-]+)", self.path)
        if m:
            e = estado_trabajo(m.group(1))
            return self._json(200, e) if e else self._json(404, {"error": "No existe ese trabajo"})
        self._json(404, {"error": "No existe"})

    def do_POST(self):
        if not self._permitido():
            return
        try:
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0) or 0)) or b"{}")
        except ValueError:
            return self._json(400, {"error": "JSON mal formado"})
        try:
            with CERROJO:
                return self._post(d)
        except RuntimeError as e:
            return self._json(500, {"error": str(e)})

    def _post(self, d: dict):
        if self.path == "/montar":
            toma = d.get("toma", "")
            if not toma or not dentro_de_tomas(toma) or not os.path.isfile(toma):
                return self._json(400, {"error": "La toma no existe o no está en la carpeta de tomas"})
            ya = en_marcha_para(toma)
            if ya:
                return self._json(200, {"id": ya, "ya_estaba": True})
            base = os.path.splitext(toma)[0]
            if d.get("guion"):
                open(base + ".guion.txt", "w", encoding="utf-8").write(d["guion"])
            if d.get("montaje"):
                json.dump(d["montaje"], open(base + ".montaje.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            subprocess.run([PY, os.path.join(RAIZ, "scripts", "medir_toma.py"), toma], cwd=os.path.join(RAIZ, "scripts"),
                           capture_output=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"),
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            return self._json(200, {"id": lanzar("montar", orden_montar(d, toma), toma)})
        if self.path == "/revisar":
            export = d.get("export", "")
            if not export or not dentro_de_tomas(export) or not os.path.isfile(export):
                return self._json(400, {"error": "El vídeo exportado no existe o no está en la carpeta de tomas"})
            ya = en_marcha_para(export)
            if ya:
                return self._json(200, {"id": ya, "ya_estaba": True})
            return self._json(200, {"id": lanzar("revisar", orden_revisar(d, export), export)})
        self._json(404, {"error": "No existe"})


def main():
    if not CLAVE:
        print("Aviso: no hay puente_clave en config.json; nadie podrá usar el puente hasta que la pongas (instalar.ps1 la crea).")
    # Sin reutilizar el puerto: en Windows SO_REUSEADDR deja a varios puentes escuchar a la vez (12-10: quedaron
    # cuatro vivos). Así el segundo falla al arrancar y solo hay uno.
    ThreadingHTTPServer.allow_reuse_address = False
    srv = ThreadingHTTPServer(("127.0.0.1", PUERTO), Puente)
    print(f"Puente de montar-reels en http://127.0.0.1:{PUERTO} · tomas en {TOMAS}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
