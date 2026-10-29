# La Máquina con Nino puro (spec hh-kpi 2026-10-28-negocio-sencillo-dos-mundos, P5 M1).
#   python puente/nino_puro.py            -> rehace ~/.fabrica-nino/skills desde ~/.claude/skills
#   python puente/nino_puro.py --comprobar -> solo mira la copia que hay, sin tocar nada
# Luismi, 29-10: "para la maquina de nino, manda nino, para la de FF360 cerebro kaizen estructura nino".
# Las skills de ~/.claude/skills llevan el parche K (~/.fabrica/parches/04-kaizen-manda.diff) y leen ~/.fabrica, que
# es FF360. Esta copia quita el parche con `git apply -R` (no a mano) y lleva todo lo de ~/.fabrica a ~/.fabrica-nino,
# con su historial y su ledger. Las originales no se tocan: FF360(K) sigue igual.
# 29-10 (Luismi: La Máquina es "FF360, con mi avatar", con "avatar y reglas de Kaizen"): la marca es la de FF360
# (config-maquina.json), el avatar es el de ~/.fabrica/avatar y las reglas fijas son los apartados 2 (avatar) y 4 (lo que
# nunca se hace) de ~/.fabrica/KAIZEN.md, copiados cada vez a REGLAS-KAIZEN.md. La estructura (apartado 3) es de Nino.
import argparse, os, re, shutil, subprocess, sys

CASA = os.path.expanduser("~")
ORIGEN = os.path.join(CASA, ".claude", "skills")
FABRICA = os.path.join(CASA, ".fabrica")
NINO = os.path.join(CASA, ".fabrica-nino")
PARCHE_K = os.path.join(FABRICA, "parches", "04-kaizen-manda.diff")
CONFIG_MAQUINA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config-maquina.json")
# Los apartados de KAIZEN.md que valen en La Máquina, por su número de título ("## 2. Avatar...", "## 4. Lo que nunca...").
APARTADOS_KAIZEN = ("2", "4")

# Las 17 que toca el parche K. goated-ads va dentro: guion-viral la usa para los ganchos.
SKILLS = ["carrusel", "edicion-video", "fabrica-core", "fabrica-init", "guion-viral", "investigacion-viral",
          "medicion-ledger", "miniaturas", "multicamara", "pdf-lead-magnet", "produccion-reel", "produccion-youtube",
          "scrollweb", "seo-ia", "ugc", "vsl", "goated-ads"]

# `.fabrica` como carpeta (~/.fabrica, ".fabrica" / "x", ~/.fabrica/config.json), no `.fabrica-nino` ni
# `.fabrica.diaria.plist` (el nombre del lanzador de macOS, que no es una ruta).
RE_FABRICA = re.compile(r"\.fabrica(?![\w.-])")
_NOMBRES = "|".join(map(re.escape, SKILLS))
# `.claude/skills/<una de las 17>`: si no, la copia leería la original con el parche. Las demás (chatgpt-image-ad,
# kie-external-api...) no llevan parche y se quedan donde están.
RE_SKILL = re.compile(r"\.claude([/\\]{1,2})skills\1(" + _NOMBRES + r")(?![\w-])")
RE_KAIZEN = re.compile(r"kaizen", re.I)


def reescribir(texto: str) -> str:
    texto = RE_SKILL.sub(lambda m: f".fabrica-nino{m.group(1)}skills{m.group(1)}{m.group(2)}", texto)
    return RE_FABRICA.sub(".fabrica-nino", texto)


def textos(raiz: str):
    """(ruta, texto) de cada fichero de texto; los binarios (fuentes, imágenes) se saltan."""
    for d, subdirs, ficheros in os.walk(raiz):
        subdirs[:] = [s for s in subdirs if s not in (".git", "__pycache__")]
        for f in ficheros:
            p = os.path.join(d, f)
            try:
                with open(p, encoding="utf-8", newline="") as fh:
                    yield p, fh.read()
            except (UnicodeDecodeError, OSError):
                continue


def restos(raiz: str) -> dict:
    """Lo que no puede quedar en la copia. Todo a 0 = Nino puro."""
    r = {"kaizen": 0, "fabrica_ff360": 0, "skill_con_parche": 0}
    for _, t in textos(raiz):
        r["kaizen"] += len(RE_KAIZEN.findall(t))
        r["fabrica_ff360"] += len(RE_FABRICA.findall(t))
        r["skill_con_parche"] += len(RE_SKILL.findall(t))
    return r


def git_apply(diff: str, cwd: str, *extra) -> tuple[bool, str]:
    # Igual que ~/.fabrica/parches/reaplicar.py: sin subir a un repo de arriba y sin reescribir los finales de línea.
    env = dict(os.environ, GIT_CEILING_DIRECTORIES=os.path.dirname(cwd))
    r = subprocess.run(["git", "-c", "core.autocrlf=false", "apply", *extra, diff], cwd=cwd, env=env,
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or r.stdout).strip()


def reglas_kaizen(texto: str) -> str:
    """Los apartados APARTADOS_KAIZEN de KAIZEN.md, tal cual. Si falta alguno, error: mejor parar que ir sin reglas."""
    trozos = re.split(r"(?m)^(?=## )", texto)
    elegidos = [t for t in trozos if re.match(r"## (\d+)\.", t) and re.match(r"## (\d+)\.", t).group(1) in APARTADOS_KAIZEN]
    numeros = sorted(re.match(r"## (\d+)\.", t).group(1) for t in elegidos)
    if numeros != sorted(APARTADOS_KAIZEN):
        raise RuntimeError("KAIZEN.md no tiene los apartados %s (tiene %s)" % (", ".join(APARTADOS_KAIZEN), ", ".join(numeros) or "ninguno"))
    cabeza = ("# Reglas fijas de Kaizen para La Máquina\n\n"
              "Copiadas de ~/.fabrica/KAIZEN.md por puente/nino_puro.py (no editar aquí). Valen el avatar y lo que nunca "
              "se hace. La estructura, el método y los gates son los de Nino.\n\n")
    return cabeza + "".join(t.rstrip() + "\n\n" for t in elegidos)


def construir(origen=ORIGEN, nino=NINO, parche=PARCHE_K, config=CONFIG_MAQUINA, env_ff360=None, fabrica=FABRICA) -> dict:
    """Rehace nino/skills desde cero. Devuelve lo que quedó (restos) y lo que se hizo."""
    faltan = [s for s in SKILLS if not os.path.isdir(os.path.join(origen, s))]
    if faltan:
        raise RuntimeError("Faltan skills en %s: %s" % (origen, ", ".join(faltan)))
    if not os.path.isfile(parche):
        raise RuntimeError("No encuentro el parche K: %s" % parche)
    avatar = os.path.join(fabrica, "avatar")
    if not os.path.isfile(os.path.join(avatar, "avatar.json")):
        raise RuntimeError("No encuentro el avatar: %s" % os.path.join(avatar, "avatar.json"))
    with open(os.path.join(fabrica, "KAIZEN.md"), encoding="utf-8") as fh:
        reglas = reglas_kaizen(fh.read())

    skills = os.path.join(nino, "skills")
    nueva = skills + ".nueva"
    shutil.rmtree(nueva, ignore_errors=True)
    for s in SKILLS:
        shutil.copytree(os.path.join(origen, s), os.path.join(nueva, s),
                        ignore=shutil.ignore_patterns(".git", "__pycache__"))

    ok, err = git_apply(parche, nueva, "--check", "-R")
    if not ok:
        shutil.rmtree(nueva, ignore_errors=True)
        raise RuntimeError("El parche K no sale limpio de las skills (¿se actualizaron?): " + err)
    ok, err = git_apply(parche, nueva, "-R")
    if not ok:
        shutil.rmtree(nueva, ignore_errors=True)
        raise RuntimeError("No se pudo quitar el parche K: " + err)

    cambiados = 0
    for p, t in textos(nueva):
        n = reescribir(t)
        if n != t:
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(n)
            cambiados += 1

    quedan = restos(nueva)
    if any(quedan.values()):
        shutil.rmtree(nueva, ignore_errors=True)
        raise RuntimeError("La copia no queda pura: %s" % quedan)

    # Solo al final, ya comprobada: la copia vieja no se pierde si algo falla por el camino.
    shutil.rmtree(skills, ignore_errors=True)
    os.replace(nueva, skills)

    hecho = {"skills": len(SKILLS), "ficheros_reescritos": cambiados, "restos": quedan}
    # La marca de FF360, siempre desde la plantilla del repo: así no se queda una vieja (la de Atlas del primer día).
    shutil.copyfile(config, os.path.join(nino, "config.json"))
    # El avatar de FF360 (el de Kaizen), entero salvo los scripts que lo sacan.
    destino_avatar = os.path.join(nino, "avatar")
    shutil.rmtree(destino_avatar, ignore_errors=True)
    shutil.copytree(avatar, destino_avatar, ignore=shutil.ignore_patterns("*.py", "__pycache__"))
    with open(os.path.join(nino, "REGLAS-KAIZEN.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(reglas)
    hecho["avatar"] = sorted(os.listdir(destino_avatar))
    # Las claves de API son las mismas: enlace duro al .env de ~/.fabrica, sin leerlo ni copiarlo.
    env_ff360 = env_ff360 or os.path.join(FABRICA, ".env")
    env_nino = os.path.join(nino, ".env")
    if os.path.isfile(env_ff360) and not os.path.exists(env_nino):
        os.link(env_ff360, env_nino)
        hecho["env"] = "enlazado"
    return hecho


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--comprobar", action="store_true")
    a = ap.parse_args()
    skills = os.path.join(NINO, "skills")
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
    print("Nino puro en %s: %s" % (skills, hecho))
    # Control positivo: en las originales SÍ tiene que haber parche K; si no, la comprobación de arriba no prueba nada.
    print("En las originales (con parche K): %s" % restos_de_originales())
    return 0


def restos_de_originales() -> dict:
    r = {"kaizen": 0, "fabrica_ff360": 0, "skill_con_parche": 0}
    for s in SKILLS:
        for k, v in restos(os.path.join(ORIGEN, s)).items():
            r[k] += v
    return r


if __name__ == "__main__":
    sys.exit(main())
