# La Máquina con Nino puro (spec hh-kpi 2026-10-28-negocio-sencillo-dos-mundos, P5 M1).
#   python puente/nino_puro.py            -> rehace ~/.fabrica-nino/skills desde ~/.claude/skills
#   python puente/nino_puro.py --comprobar -> solo mira la copia que hay, sin tocar nada
# Luismi, 29-10: "para la maquina de nino, manda nino, para la de FF360 cerebro kaizen estructura nino".
# Las skills de ~/.claude/skills llevan el bloque K ("FF360: manda Kaizen", lo pone ~/.fabrica/parches/kaizen_bloque.py)
# y leen ~/.fabrica, que es FF360. Esta copia quita el bloque y lleva todo lo de ~/.fabrica a ~/.fabrica-nino, con su
# historial y su ledger. Las originales no se tocan: FF360(K) sigue igual.
# 08-11: el bloque se quita por texto y no con `git apply -R` de 04-kaizen-manda.diff, que dejó de encajar con la v1.14.1
# de Nino y se retiró. Lo mismo lo usa puente/fabrica_atlas.py (spec hh-kpi 2026-11-08-atlas-negocio-independiente).
# 29-10 (Luismi: La Máquina es "FF360, con mi avatar", con "avatar y reglas de Kaizen"): la marca es la de FF360
# (config-maquina.json), el avatar es el de ~/.fabrica/avatar y las reglas fijas son los apartados 2 (avatar) y 4 (lo que
# nunca se hace) de ~/.fabrica/KAIZEN.md, copiados cada vez a REGLAS-KAIZEN.md. La estructura (apartado 3) es de Nino.
import argparse, os, re, shutil, sys

CASA = os.path.expanduser("~")
ORIGEN = os.path.join(CASA, ".claude", "skills")
FABRICA = os.path.join(CASA, ".fabrica")
NINO = os.path.join(CASA, ".fabrica-nino")
# La primera línea del bloque K. El bloque son las líneas seguidas que empiezan por ">" a partir de ella.
MARCA_K = "FF360: manda Kaizen"
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


def re_skill(skills) -> re.Pattern:
    return re.compile(r"\.claude([/\\]{1,2})skills\1(" + "|".join(map(re.escape, skills)) + r")(?![\w-])")


def reescribir(texto: str, carpeta: str = ".fabrica-nino", patron: re.Pattern = RE_SKILL) -> str:
    texto = patron.sub(lambda m: f"{carpeta}{m.group(1)}skills{m.group(1)}{m.group(2)}", texto)
    return RE_FABRICA.sub(carpeta, texto)


def quitar_bloque_k(texto: str):
    """(texto sin el bloque K, si lo había). Quita sus líneas "> ..." y la línea en blanco que lo precede."""
    lineas = texto.split("\n")
    for i, linea in enumerate(lineas):
        if linea.startswith(">") and MARCA_K in linea:
            fin = i
            while fin < len(lineas) and lineas[fin].startswith(">"):
                fin += 1
            ini = i - 1 if i > 0 and lineas[i - 1].strip() == "" else i
            return "\n".join(lineas[:ini] + lineas[fin:]), True
    return texto, False


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


def restos(raiz: str, patron: re.Pattern = RE_SKILL) -> dict:
    """Lo que no puede quedar en la copia. Todo a 0 = Nino puro."""
    r = {"kaizen": 0, "fabrica_ff360": 0, "skill_con_parche": 0}
    for _, t in textos(raiz):
        r["kaizen"] += len(RE_KAIZEN.findall(t))
        r["fabrica_ff360"] += len(RE_FABRICA.findall(t))
        r["skill_con_parche"] += len(patron.findall(t))
    return r


def copia_limpia(origen: str, skills: list, nueva: str, carpeta: str) -> int:
    """Copia `skills` de origen a `nueva`, sin el bloque K y con las rutas en `carpeta`. Devuelve ficheros cambiados.
    Cada SKILL.md tiene que traer el bloque: si falta, las originales no son las de FF360(K) y mejor parar."""
    shutil.rmtree(nueva, ignore_errors=True)
    for s in skills:
        shutil.copytree(os.path.join(origen, s), os.path.join(nueva, s),
                        ignore=shutil.ignore_patterns(".git", "__pycache__"))
    sin_bloque = []
    for s in skills:
        p = os.path.join(nueva, s, "SKILL.md")
        with open(p, encoding="utf-8", newline="") as fh:
            t, habia = quitar_bloque_k(fh.read())
        if not habia:
            sin_bloque.append(s)
            continue
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(t)
    if sin_bloque:
        shutil.rmtree(nueva, ignore_errors=True)
        raise RuntimeError("Estas skills no traen el bloque K (¿falta python ~/.fabrica/parches/reaplicar.py?): "
                           + ", ".join(sin_bloque))
    patron = re_skill(skills)
    cambiados = 0
    for p, t in textos(nueva):
        n = reescribir(t, carpeta, patron)
        if n != t:
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(n)
            cambiados += 1
    return cambiados


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


def construir(origen=ORIGEN, nino=NINO, config=CONFIG_MAQUINA, env_ff360=None, fabrica=FABRICA) -> dict:
    """Rehace nino/skills desde cero. Devuelve lo que quedó (restos) y lo que se hizo."""
    faltan = [s for s in SKILLS if not os.path.isdir(os.path.join(origen, s))]
    if faltan:
        raise RuntimeError("Faltan skills en %s: %s" % (origen, ", ".join(faltan)))
    avatar = os.path.join(fabrica, "avatar")
    if not os.path.isfile(os.path.join(avatar, "avatar.json")):
        raise RuntimeError("No encuentro el avatar: %s" % os.path.join(avatar, "avatar.json"))
    with open(os.path.join(fabrica, "KAIZEN.md"), encoding="utf-8") as fh:
        reglas = reglas_kaizen(fh.read())

    skills = os.path.join(nino, "skills")
    nueva = skills + ".nueva"
    cambiados = copia_limpia(origen, SKILLS, nueva, ".fabrica-nino")

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
