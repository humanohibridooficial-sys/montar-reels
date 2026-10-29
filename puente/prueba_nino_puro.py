# Prueba de la copia de Nino puro (spec hh-kpi 2026-10-28-negocio-sencillo-dos-mundos, P5 M1).
#   python puente/prueba_nino_puro.py
# Monta unas skills falsas con un parche K falso en una carpeta temporal: no toca ~/.claude ni ~/.fabrica.
import difflib, os, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nino_puro  # noqa: E402

fallos = 0


def ok(cond, msg):
    global fallos
    print("  ok   " if cond else "  FALLO", msg)
    fallos += 0 if cond else 1


def leer(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def escribir(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


base = tempfile.mkdtemp(prefix="nino-")
origen, nino, fab = (os.path.join(base, x) for x in ("skills", "fabrica-nino", "fabrica"))
LIMPIO = "---\nname: carrusel\n---\n\n# CARRUSEL\r\nLee ~/.fabrica/config.json antes de nada.\r\n"
BLOQUE = "\n> **FF360: manda Kaizen.** Lee `~/.fabrica/KAIZEN.md`.\n"
CON_K = LIMPIO.replace("---\n\n#", "---\n" + BLOQUE + "\n#")
for s in nino_puro.SKILLS:
    escribir(os.path.join(origen, s, "SKILL.md"), CON_K if s == "carrusel" else f"# {s}\nnada\n")
escribir(os.path.join(origen, "guion-viral", "scripts", "qa.py"),
         'CFG = Path.home() / ".fabrica" / "config.json"\nA = "~/.claude/skills/goated-ads/SKILL.md"\n'
         'B = "~/.claude/skills/chatgpt-image-ad/x.py"\nC = "~/.claude/skills/carrusel-ff360/x"\n'
         'D = "com.luismi.fabrica.diaria.plist"\nE = r"C:\\Users\\x\\.claude\\skills\\ugc\\a"\n')
with open(os.path.join(origen, "carrusel", "fuente.ttf"), "wb") as f:
    f.write(b"\x00\xff.fabrica\xfe")
diff = "".join(difflib.unified_diff(LIMPIO.splitlines(True), CON_K.splitlines(True),
                                    "a/carrusel/SKILL.md", "b/carrusel/SKILL.md"))
parche = os.path.join(base, "04.diff")
escribir(parche, diff)
config = os.path.join(base, "config-maquina.json")
escribir(config, '{"marca": {"nombre": "FF360"}}\n')
env = os.path.join(fab, ".env")
escribir(env, "NO_SE_LEE=1\n")
# El avatar y KAIZEN.md de ~/.fabrica (29-10: La Máquina es FF360 con su avatar y las reglas fijas de Kaizen).
escribir(os.path.join(fab, "avatar", "avatar.json"), '{"problemas": []}\n')
escribir(os.path.join(fab, "avatar", "1 - Mi Avatar.txt"), "el futbolista\n")
escribir(os.path.join(fab, "avatar", "sacar.py"), "print('no va')\n")
escribir(os.path.join(fab, "KAIZEN.md"), "# K\n## 0. Como se decide\ncero\n## 2. Avatar\nel avatar\n## 3. Voz y guiones\n"
         "la estructura de Kaizen\n## 4. Lo que nunca se hace\nnunca el precio\n## 5. Colores\n")

h = nino_puro.construir(origen, nino, parche, config, env, fab)
cs = os.path.join(nino, "skills")
ok(h["restos"] == {"kaizen": 0, "fabrica_ff360": 0, "skill_con_parche": 0}, f"la copia queda pura: {h['restos']}")
car = leer(os.path.join(cs, "carrusel", "SKILL.md"))
ok("Kaizen" not in car and "# CARRUSEL" in car, "sin el bloque de Kaizen y con el resto de la skill")
ok("~/.fabrica-nino/config.json" in car, "lee la config de ~/.fabrica-nino")
ok("\r\n" in car, "respeta los finales de línea (CRLF)")
qa = leer(os.path.join(cs, "guion-viral", "scripts", "qa.py"))
ok('".fabrica-nino" / "config.json"' in qa, "Path.home() / '.fabrica' pasa a .fabrica-nino")
ok("~/.fabrica-nino/skills/goated-ads/SKILL.md" in qa, "una de las 17 se lee de la copia")
ok("~/.claude/skills/chatgpt-image-ad/x.py" in qa, "una skill sin parche se queda donde está")
ok("~/.claude/skills/carrusel-ff360/x" in qa, "carrusel-ff360 no se confunde con carrusel")
ok("fabrica.diaria.plist" in qa, "el nombre del lanzador de macOS no se toca")
ok(".fabrica-nino\\skills\\ugc\\a" in qa, "también con barras de Windows")
with open(os.path.join(cs, "carrusel", "fuente.ttf"), "rb") as f:
    ok(f.read() == b"\x00\xff.fabrica\xfe", "los binarios se copian sin tocar")
ok("Kaizen" in leer(os.path.join(origen, "carrusel", "SKILL.md")), "las originales siguen con el parche K")
ok(leer(os.path.join(nino, "config.json")).count("FF360") == 1, "config de FF360 puesta")
ok(h.get("avatar") == ["1 - Mi Avatar.txt", "avatar.json"], f"el avatar copiado, sin el script que lo saca ({h.get('avatar')})")
rk = leer(os.path.join(nino, "REGLAS-KAIZEN.md"))
ok("el avatar" in rk and "nunca el precio" in rk, "las reglas fijas: avatar y lo que nunca se hace")
ok("la estructura de Kaizen" not in rk and "cero" not in rk and "Colores" not in rk, "sin la estructura de Kaizen ni lo demás")
ok(os.path.samefile(env, os.path.join(nino, ".env")) and h.get("env") == "enlazado", ".env enlazado, no copiado")

# Cambiado a sabiendas (29-10): antes la config no se pisaba; ahora sale siempre de la plantilla del repo, para que no se
# quede una vieja (la de Atlas del primer día).
escribir(os.path.join(nino, "config.json"), '{"marca": {"nombre": "Atlas"}}\n')
h2 = nino_puro.construir(origen, nino, parche, config, env, fab)
ok("Atlas" not in leer(os.path.join(nino, "config.json")), "una config vieja se cambia por la de la plantilla")
ok(os.path.isfile(os.path.join(cs, "vsl", "SKILL.md")), "la segunda vez rehace la copia entera")

# Si las skills se actualizan y el parche ya no encaja, no se hace nada y la copia buena se queda.
escribir(os.path.join(origen, "carrusel", "SKILL.md"), "# otra version\n")
try:
    nino_puro.construir(origen, nino, parche, config, env, fab)
    ok(False, "un parche que no encaja tendría que parar")
except RuntimeError as e:
    ok("no sale limpio" in str(e), "un parche que no encaja para")
ok("# CARRUSEL" in leer(os.path.join(cs, "carrusel", "SKILL.md")), "y la copia buena de antes sigue")
escribir(os.path.join(origen, "carrusel", "SKILL.md"), CON_K)

# Control: sin reescribir rutas, la comprobación TIENE que saltar (si no, el "0 restos" de arriba no prueba nada).
bueno = nino_puro.reescribir
nino_puro.reescribir = lambda t: t
try:
    nino_puro.construir(origen, nino, parche, config, env, fab)
    ok(False, "sin reescribir tendría que parar")
except RuntimeError as e:
    ok("no queda pura" in str(e), "sin reescribir rutas, para (control positivo)")
nino_puro.reescribir = bueno

print("fallos:", fallos)
sys.exit(1 if fallos else 0)
