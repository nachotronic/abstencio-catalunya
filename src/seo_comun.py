"""Piezas comunes del control y la vigilancia de cambios de SEO (regla de Nacho, 17-11-2026, tras #609).

#609 cambió el título de /encuestas/ y quitó la búsqueda exacta «últimas encuestas elecciones generales 2026»:
sus impresiones cayeron de unas 830 por hora a unas 40 justo después de fusionarlo. Este módulo:
- detecta qué páginas cambian de título, H1 o descripción entre dos commits (sin contar las cifras: la
  actualización diaria de /encuestas/ cambia «PP 31,5 %» o «18 de 20» y eso no es un cambio de SEO);
- consulta Search Console (GSC_CREDENTIALS, sc-domain:mapaelectoral.es), por días o por horas;
- normaliza textos para comprobar si una búsqueda aparece tal cual en un título.
Lo usan src/control_seo.py (antes de fusionar) y src/vigilar_seo.py (48 h después de fusionar).
"""
import html as html_mod
import json
import os
import re
import subprocess
import unicodedata
from urllib.parse import quote

SITIO = "sc-domain:mapaelectoral.es"
HOST = "https://mapaelectoral.es"
API = "https://searchconsole.googleapis.com/webmasters/v3"
CAMPOS = ("title", "h1", "description")
NOMBRES = {"title": "título", "h1": "H1", "description": "descripción"}
# Páginas clave (regla 3): ningún cambio de SEO en ellas sin el «Fusiona» de Nacho.
CLAVE = {"/", "/encuestas/", "/elecciones/resultados-elecciones-generales-2026/"}
# Etiqueta que se pone en el PR solo cuando Nacho ha dicho «Fusiona» para ese cambio de SEO.
ETIQUETA_NACHO = "seo-fusiona-nacho"


# ---------- Extracción de título, H1 y descripción ----------

def _texto(x):
    x = re.sub(r"<[^>]+>", " ", x)
    return re.sub(r"\s+", " ", html_mod.unescape(x)).strip()


def metas(doc):
    """Título, primer H1 y meta description de una página HTML, y su URL canónica si la tiene."""
    if not doc:
        return {}
    m = {}
    t = re.search(r"<title[^>]*>(.*?)</title>", doc, re.S | re.I)
    m["title"] = _texto(t.group(1)) if t else ""
    h = re.search(r"<h1\b[^>]*>(.*?)</h1>", doc, re.S | re.I)
    m["h1"] = _texto(h.group(1)) if h else ""
    d = (re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)', doc, re.I)
         or re.search(r'<meta\s+content=["\']([^"\']*)["\']\s+name=["\']description["\']', doc, re.I))
    m["description"] = _texto(d.group(1)) if d else ""
    c = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', doc, re.I)
    m["canonical"] = c.group(1) if c else ""
    return m


def sin_cifras(x):
    """Para decidir si un cambio es de SEO: las cifras (porcentajes, fechas, «18 de 20») no cuentan."""
    return re.sub(r"\d+([.,]\d+)*", "#", x or "")


def url_de(fichero, m):
    """URL pública de un fichero HTML: la canónica si la tiene; si no, la que sirve GitHub Pages."""
    if m.get("canonical", "").startswith(HOST):
        return m["canonical"]
    if fichero == "index.html":
        return HOST + "/"
    if fichero.endswith("/index.html"):
        return f"{HOST}/{fichero[:-len('index.html')]}"
    return f"{HOST}/{fichero}"


def ruta(url):
    return url.replace(HOST, "") or "/"


# ---------- Cambios entre commits ----------

def _git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def _contenidos(objetos):
    """Lee muchos blobs de golpe con git cat-file --batch. objetos: lista de «rev:ruta»."""
    if not objetos:
        return {}
    p = subprocess.run(["git", "cat-file", "--batch"], input="\n".join(objetos).encode() + b"\n",
                       capture_output=True, check=True)
    datos, out, i = p.stdout, {}, 0
    for obj in objetos:
        fin = datos.index(b"\n", i)
        cab = datos[i:fin].decode()
        i = fin + 1
        if cab.endswith("missing"):
            out[obj] = ""
            continue
        n = int(cab.split()[2])
        out[obj] = datos[i:i + n].decode("utf-8", "replace")
        i += n + 1
    return out


def cambios_seo(base, cabeza, campos_vale=CAMPOS):
    """Páginas cuyo título, H1 o descripción cambian de base a cabeza (sin contar cifras).

    campos_vale: qué campos cuentan como cambio (por defecto los tres).

    Devuelve una lista de dicts: fichero, url, ruta, antes {campo: texto}, despues {campo: texto},
    campos (los que cambian). Las páginas nuevas no cuentan: no tienen búsquedas que perder.
    """
    salida = _git("diff", "--name-status", "--no-renames", base, cabeza, "--", "*.html")
    ficheros = []
    for linea in salida.splitlines():
        estado, _, f = linea.partition("\t")
        if estado.startswith("M"):
            ficheros.append(f)
    if ficheros:
        # En un clon parcial (filter: blob:none) git diff trae de golpe los ficheros que faltan; cat-file iría uno a uno.
        _git("diff", "--stat", base, cabeza, "--", "*.html")
    objs = [f"{base}:{f}" for f in ficheros] + [f"{cabeza}:{f}" for f in ficheros]
    cont = _contenidos(objs)
    res = []
    for f in ficheros:
        a, d = metas(cont[f"{base}:{f}"]), metas(cont[f"{cabeza}:{f}"])
        campos = [c for c in campos_vale if sin_cifras(a.get(c)) != sin_cifras(d.get(c))]
        if campos:
            u = url_de(f, a)
            res.append({"fichero": f, "url": u, "ruta": ruta(u), "antes": a, "despues": d, "campos": campos})
    return res


# ---------- Búsquedas frente a textos ----------

def normaliza(x):
    """Minúsculas, sin tildes ni signos: así compara Google una búsqueda con un título."""
    x = unicodedata.normalize("NFKD", (x or "").lower())
    x = "".join(c for c in x if not unicodedata.combining(c))
    x = re.sub(r"[^a-z0-9]+", " ", x)
    return " " + re.sub(r"\s+", " ", x).strip() + " "


def contiene_exacta(texto, busqueda):
    """La búsqueda aparece tal cual (palabras seguidas y en el mismo orden) en el texto."""
    b = normaliza(busqueda).strip()
    return bool(b) and f" {b} " in normaliza(texto)


def contiene_palabras(texto, busqueda):
    """Todas las palabras de la búsqueda están en el texto, en cualquier orden."""
    t = set(normaliza(texto).split())
    return all(p in t for p in normaliza(busqueda).split())


# ---------- Search Console ----------

def sesion():
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    cred = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GSC_CREDENTIALS"]),
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    return AuthorizedSession(cred)


def consulta(s, inicio, fin, dims, filas=1000, filtros=None, estado="all", inicio_fila=0):
    cuerpo = {"startDate": inicio, "endDate": fin, "dimensions": dims, "rowLimit": filas,
              "dataState": estado, "startRow": inicio_fila}
    if filtros:
        cuerpo["dimensionFilterGroups"] = [{"filters": filtros}]
    r = s.post(f"{API}/sites/{quote(SITIO, safe='')}/searchAnalytics/query", json=cuerpo)
    r.raise_for_status()
    return r.json().get("rows", [])


def filtro_pagina(url):
    return [{"dimension": "page", "operator": "equals", "expression": url}]


def num(x):
    return f"{x:,.0f}".replace(",", ".")


def pct(x):
    return f"{x * 100:.0f} %"


# ---------- Commits recientes de main que cambian títulos o H1 ----------

BOT = "github-actions[bot]"


def commits_seo(rev, desde_iso, campos_vale=("title", "h1"), excluir=()):
    """Commits de rev (primer padre) desde desde_iso que cambian título o H1 de alguna página.

    No cuentan los del bot (actualizaciones automáticas de datos, como las de /encuestas/): no son
    decisiones de SEO y cambian los textos según las cifras. Devuelve dicts con sha, fecha (ISO, UTC),
    asunto y cambios.
    """
    log = _git("log", "--first-parent", f"--since={desde_iso}", "--format=%H%x09%cI%x09%an%x09%s", rev)
    res = []
    for linea in log.splitlines():
        sha, fecha, autor, asunto = linea.split("\t", 3)
        if autor == BOT or sha in excluir:
            continue
        try:
            c = cambios_seo(f"{sha}~1", sha, campos_vale)
        except subprocess.CalledProcessError:
            continue  # primer commit de un clon superficial: sin padre que comparar
        if c:
            res.append({"sha": sha, "fecha": fecha, "asunto": asunto, "cambios": c})
    return res
