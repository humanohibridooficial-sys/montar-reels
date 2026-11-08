# La Fábrica de Atlas (spec hh-kpi 2026-11-08-atlas-negocio-independiente, fase 1).
#   python puente/fabrica_atlas.py            -> rehace ~/.fabrica-atlas/skills desde ~/.claude/skills
#   python puente/fabrica_atlas.py --comprobar -> solo mira la copia que hay, sin tocar nada
# Luismi, 08-11: "atlas es atlas y FF360 son independientes", "salgo yo a cámara". Y el 19-10: "para Atlas montaremos
# íntegra la máquina de Nino, sin versión Kaizen".
# Hermana de nino_puro.py: misma copia limpia (sin el bloque K y con las rutas cambiadas), pero a ~/.fabrica-atlas, con
# las dos skills nuevas de la v1.14 y SIN nada de FF360: ni avatar, ni REGLAS-KAIZEN.md, ni su marca. La config sale de
# config-atlas.json solo la primera vez; después manda la que deje fabrica-init (P2 del spec: la marca es provisional).
import argparse, os, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nino_puro  # noqa: E402

CASA = os.path.expanduser("~")
ORIGEN = nino_puro.ORIGEN
FABRICA = nino_puro.FABRICA
ATLAS = os.path.join(CASA, ".fabrica-atlas")
CARPETA = ".fabrica-atlas"
CONFIG_ATLAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config-atlas.json")
# Las 17 de La Máquina y las dos que trae la v1.14.1. Todas llevan el bloque K en ~/.claude/skills.
SKILLS = nino_puro.SKILLS + ["ads-meta", "director-cinematico"]
PATRON = nino_puro.re_skill(SKILLS)
# Lo de FF360 que no puede aparecer en ~/.fabrica-atlas.
PROHIBIDOS = ("avatar", "REGLAS-KAIZEN.md", "KAIZEN.md")


def restos(raiz: str) -> dict:
    return nino_puro.restos(raiz, PATRON)


def construir(origen=ORIGEN, atlas=ATLAS, config=CONFIG_ATLAS, env_ff360=None) -> dict:
    """Rehace atlas/skills desde cero. Devuelve lo que quedó (restos) y lo que se hizo."""
    faltan = [s for s in SKILLS if not os.path.isdir(os.path.join(origen, s))]
    if faltan:
        raise RuntimeError("Faltan skills en %s: %s" % (origen, ", ".join(faltan)))
    skills = os.path.join(atlas, "skills")
    nueva = skills + ".nueva"
    cambiados = nino_puro.copia_limpia(origen, SKILLS, nueva, CARPETA)
    quedan = restos(nueva)
    if any(quedan.values()):
        shutil.rmtree(nueva, ignore_errors=True)
        raise RuntimeError("La copia no queda limpia: %s" % quedan)
    # Solo al final, ya comprobada: la copia vieja no se pierde si algo falla por el camino.
    shutil.rmtree(skills, ignore_errors=True)
    os.replace(nueva, skills)

    hecho = {"skills": len(SKILLS), "ficheros_reescritos": cambiados, "restos": quedan}
    destino_config = os.path.join(atlas, "config.json")
    if os.path.exists(destino_config):
        hecho["config"] = "la que había (no se pisa)"
    else:
        shutil.copyfile(config, destino_config)
        hecho["config"] = "plantilla de Atlas"
    # Las claves de API son las mismas: enlace duro al .env de ~/.fabrica, sin leerlo ni copiarlo.
    env_ff360 = env_ff360 or os.path.join(FABRICA, ".env")
    env_atlas = os.path.join(atlas, ".env")
    if os.path.isfile(env_ff360) and not os.path.exists(env_atlas):
        os.link(env_ff360, env_atlas)
        hecho["env"] = "enlazado"
    hecho["de_ff360"] = [p for p in PROHIBIDOS if os.path.exists(os.path.join(atlas, p))]
    if hecho["de_ff360"]:
        raise RuntimeError("En %s hay cosas de FF360: %s" % (atlas, ", ".join(hecho["de_ff360"])))
    return hecho


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--comprobar", action="store_true")
    a = ap.parse_args()
    skills = os.path.join(ATLAS, "skills")
    if a.comprobar:
        if not os.path.isdir(skills):
            print("No hay copia en %s" % skills)
            return 2
        quedan = restos(skills)
        print("Restos en la copia: %s" % quedan)
        return 1 if any(quedan.values()) else 0
    try:
        hecho = construir()
    except RuntimeError as e:
        print("No se hizo nada: %s" % e)
        return 1
    print("Fábrica de Atlas en %s: %s" % (skills, hecho))
    # Control positivo: en las originales SÍ tiene que haber bloque K y rutas a ~/.fabrica; si no, el 0 no prueba nada.
    r = {"kaizen": 0, "fabrica_ff360": 0, "skill_con_parche": 0}
    for s in SKILLS:
        for k, v in nino_puro.restos(os.path.join(ORIGEN, s), PATRON).items():
            r[k] += v
    print("En las originales (con bloque K): %s" % r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
