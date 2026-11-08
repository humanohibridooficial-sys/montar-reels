# Prueba de la Fábrica de Atlas (spec hh-kpi 2026-11-08-atlas-negocio-independiente, fase 1).
#   python puente/prueba_fabrica_atlas.py
# Monta unas skills falsas con el bloque K en una carpeta temporal: no toca ~/.claude, ~/.fabrica ni ~/.fabrica-atlas.
import json, os, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fabrica_atlas  # noqa: E402
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


base = tempfile.mkdtemp(prefix="atlas-")
origen, atlas, fab = (os.path.join(base, x) for x in ("skills", "fabrica-atlas", "fabrica"))
BLOQUE = "\n> **FF360: manda Kaizen (Luismi, 17-10).** Antes de nada, lee entero\n> `~/.fabrica/KAIZEN.md`.\n"
for s in fabrica_atlas.SKILLS:
    escribir(os.path.join(origen, s, "SKILL.md"),
             f"---\nname: {s}\n---\n{BLOQUE}\n# {s}\nLee ~/.fabrica/config.json y ~/.claude/skills/{s}/x.py\n")
escribir(os.path.join(origen, "ads-meta", "scripts", "a.py"),
         'L = Path.home() / ".fabrica" / "ledger.jsonl"\nN = "~/.fabrica-nino/x"\nO = "~/.claude/skills/kie-x/y"\n')
env = os.path.join(fab, ".env")
escribir(env, "NO_SE_LEE=1\n")
config = fabrica_atlas.CONFIG_ATLAS  # la plantilla de verdad del repo

h = fabrica_atlas.construir(origen, atlas, config, env)
cs = os.path.join(atlas, "skills")
ok(h["restos"] == {"kaizen": 0, "fabrica_ff360": 0, "skill_con_parche": 0}, f"la copia queda limpia: {h['restos']}")
ok(sorted(os.listdir(cs)) == sorted(fabrica_atlas.SKILLS), "están las 19, con ads-meta y director-cinematico")
dc = leer(os.path.join(cs, "director-cinematico", "SKILL.md"))
ok("Kaizen" not in dc and "# director-cinematico" in dc, "sin el bloque K y con el resto de la skill")
ok("~/.fabrica-atlas/config.json" in dc, "lee la config de ~/.fabrica-atlas")
ok("~/.fabrica-atlas/skills/director-cinematico/x.py" in dc, "una de las 19 se lee de la copia")
am = leer(os.path.join(cs, "ads-meta", "scripts", "a.py"))
ok('".fabrica-atlas" / "ledger.jsonl"' in am, "el ledger va a ~/.fabrica-atlas, no al de FF360")
ok("~/.fabrica-nino/x" in am, ".fabrica-nino no se confunde con .fabrica")
ok("~/.claude/skills/kie-x/y" in am, "una skill que no es de la Fábrica se queda donde está")
ok("Kaizen" in leer(os.path.join(origen, "carrusel", "SKILL.md")), "las originales siguen con el bloque K")
cfg = json.loads(leer(os.path.join(atlas, "config.json")))
ok(cfg["marca"]["handle"] == "@atlas.training.app" and cfg["rutas"]["output"] == "~/fabrica-output/atlas",
   "config de Atlas puesta: su cuenta y su carpeta de salida")
texto_cfg = leer(os.path.join(atlas, "config.json")).lower()
ok(not any(x in texto_cfg for x in ("kaizen", "nutretufutbol", "futbol", "ff360")), "la config no trae nada de FF360")
ok(not cfg["stack"]["heygen"]["tiene"] and not cfg["stack"]["elevenlabs"]["tiene"], "sin avatar ni voz: sale Luismi")
ok(h["de_ff360"] == [] and not os.path.exists(os.path.join(atlas, "avatar")), "ni avatar ni reglas de Kaizen")
ok(os.path.samefile(env, os.path.join(atlas, ".env")) and h.get("env") == "enlazado", ".env enlazado, no copiado")

# La config que deje fabrica-init no se pisa al rehacer (al revés que La Máquina, que la repone siempre).
escribir(os.path.join(atlas, "config.json"), '{"marca": {"nombre": "Atlas, la de fabrica-init"}}\n')
h2 = fabrica_atlas.construir(origen, atlas, config, env)
ok("la de fabrica-init" in leer(os.path.join(atlas, "config.json")) and h2["config"].startswith("la que"),
   "rehacer no pisa la config de fabrica-init")

# Si se cuela algo de FF360 en la carpeta, para.
escribir(os.path.join(atlas, "REGLAS-KAIZEN.md"), "no\n")
try:
    fabrica_atlas.construir(origen, atlas, config, env)
    ok(False, "con REGLAS-KAIZEN.md dentro tendría que parar")
except RuntimeError as e:
    ok("cosas de FF360" in str(e), "con algo de FF360 dentro, para")
os.remove(os.path.join(atlas, "REGLAS-KAIZEN.md"))

# Una skill sin bloque K: para y la copia buena se queda.
escribir(os.path.join(origen, "ads-meta", "SKILL.md"), "# otra version\n")
try:
    fabrica_atlas.construir(origen, atlas, config, env)
    ok(False, "una skill sin bloque K tendría que parar")
except RuntimeError as e:
    ok("no traen el bloque K" in str(e) and "ads-meta" in str(e), "una skill sin bloque K para y dice cuál")
ok("# ads-meta" in leer(os.path.join(cs, "ads-meta", "SKILL.md")), "y la copia buena de antes sigue")
escribir(os.path.join(origen, "ads-meta", "SKILL.md"), f"---\nname: ads-meta\n---\n{BLOQUE}\n# ads-meta\n")

# Control: sin reescribir rutas, la comprobación TIENE que saltar (si no, el "0 restos" de arriba no prueba nada).
bueno = nino_puro.reescribir
nino_puro.reescribir = lambda t, *a: t
try:
    fabrica_atlas.construir(origen, atlas, config, env)
    ok(False, "sin reescribir tendría que parar")
except RuntimeError as e:
    ok("no queda limpia" in str(e), "sin reescribir rutas, para (control positivo)")
nino_puro.reescribir = bueno

print("fallos:", fallos)
sys.exit(1 if fallos else 0)
