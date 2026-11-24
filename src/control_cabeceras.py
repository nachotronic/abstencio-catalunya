"""Control de cabeceras antes de fusionar (Nacho, 18-11-2026: «Eras capaz de perder el posicionamiento que
podamos construir estos días»).

Compara, en todas las páginas publicadas (.html) que toca el PR, el title, la meta description, el H1 y el
canonical antes y después, y comprueba que ninguna página publicada desaparece ni cambia de URL (borrada o
renombrada). Si cambia uno solo, el PR queda en rojo, sea una página con tráfico o no, y aunque solo cambien
cifras. Las páginas nuevas no cuentan.

Solo se levanta con la etiqueta «cabeceras-fusiona-nacho», que se pone únicamente cuando Nacho ha aprobado
expresamente ese cambio de title, description, H1, canonical o URL.

Uso: python3 src/control_cabeceras.py --base REV --cabeza REV [--etiquetas a,b] [--resumen FICHERO]
"""
import argparse
import html
import re
import subprocess
import sys

ETIQUETA = "cabeceras-fusiona-nacho"
CAMPOS = {
    "title": re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I),
    "description": re.compile(r"<meta\s+name=[\"']description[\"']\s+content=[\"']([^\"']*)[\"']", re.I),
    "h1": re.compile(r"<h1[^>]*>(.*?)</h1>", re.S | re.I),
    "canonical": re.compile(r"<link\s+rel=[\"']canonical[\"']\s+href=[\"']([^\"']*)[\"']", re.I),
}


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout


def leer(rev, ruta):
    try:
        return git("show", f"{rev}:{ruta}")
    except subprocess.CalledProcessError:
        return None


def cabeceras(t):
    # title, description y canonical, solo los del <head> (los <title> de los SVG no cuentan)
    fin = re.search(r"</head>", t, re.I)
    cabeza = t[:fin.start()] if fin else t
    r = {}
    for k, rx in CAMPOS.items():
        if k != "h1":
            m = rx.search(cabeza)
            r[k] = [re.sub(r"\s+", " ", html.unescape(m.group(1))).strip()] if m else []
            continue
        # todas las apariciones, por si una página tiene dos (no debería)
        r[k] = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m))).strip() for m in rx.findall(t)]
    return r


def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--cabeza", required=True)
    ap.add_argument("--etiquetas", default="")
    ap.add_argument("--resumen")
    a = ap.parse_args()
    etiquetado = ETIQUETA in [e.strip() for e in a.etiquetas.split(",")]

    fallos = []
    cambios = git("diff", "--name-status", "-M", a.base, a.cabeza, "--", "*.html").splitlines()
    revisadas = 0
    for linea in cambios:
        partes = linea.split("\t")
        est = partes[0]
        if est.startswith("A"):
            continue
        if est.startswith("D"):
            fallos.append(f"{partes[1]}: página publicada borrada (cambia o desaparece su URL)")
            continue
        if est.startswith("R") or est.startswith("C"):
            if est.startswith("R"):
                fallos.append(f"{partes[1]} → {partes[2]}: página publicada renombrada (cambia su URL)")
            continue
        ruta = partes[1]
        antes, despues = leer(a.base, ruta), leer(a.cabeza, ruta)
        if antes is None or despues is None:
            continue
        revisadas += 1
        ca, cd = cabeceras(antes), cabeceras(despues)
        for k in CAMPOS:
            if ca[k] != cd[k]:
                fallos.append(f"{ruta}: cambia {k}\n    antes:   {' | '.join(ca[k]) or '(no hay)'}\n"
                              f"    después: {' | '.join(cd[k]) or '(no hay)'}")

    lineas = [f"Control de cabeceras: {revisadas} páginas publicadas modificadas revisadas."]
    if fallos:
        lineas.append(f"{len(fallos)} cambios de title, description, H1, canonical o URL:")
        lineas += ["  " + f for f in fallos[:300]]
        if len(fallos) > 300:
            lineas.append(f"  … y {len(fallos) - 300} más")
        if etiquetado:
            lineas.append(f"Lleva la etiqueta «{ETIQUETA}» (Nacho ha aprobado el cambio): pasa.")
        else:
            lineas.append(f"No se fusiona: avisa a Nacho. Solo pasa con la etiqueta «{ETIQUETA}», "
                          "tras su aprobación expresa de este cambio.")
    else:
        lineas.append("Ningún title, description, H1, canonical ni URL de página publicada cambia.")
    texto = "\n".join(lineas)
    print(texto)
    if a.resumen:
        with open(a.resumen, "a", encoding="utf-8") as f:
            f.write("## Control de cabeceras\n\n```\n" + texto + "\n```\n")
    return 1 if fallos and not etiquetado else 0


if __name__ == "__main__":
    sys.exit(principal())
