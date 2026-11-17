"""Control de SEO antes de fusionar (reglas de Nacho del 17-11-2026, tras la caída de /encuestas/ por #609).

1. Ningún cambio de título, H1 o descripción en una página con tráfico pierde ninguna de sus 10 búsquedas
   principales de Search Console (últimos 28 días, por impresiones): si la búsqueda estaba tal cual en el texto
   viejo (mismas palabras, seguidas y en el mismo orden; sin contar tildes, mayúsculas ni signos), tiene que
   seguir tal cual en el nuevo. Si se pierde, el PR queda en rojo. Si solo se pierden palabras sueltas, aviso.
2. De uno en uno: si en main hay otro cambio de título o H1 en páginas con tráfico de las últimas 48 h (en
   vigilancia, src/vigilar_seo.py), el PR queda en rojo hasta que acabe la vigilancia.
3. Páginas clave (/, /encuestas/, /elecciones/resultados-elecciones-generales-2026/): rojo salvo que el PR
   lleve la etiqueta «seo-fusiona-nacho», que solo se pone cuando Nacho ha dicho «Fusiona». La etiqueta
   también levanta la regla 2 (por ejemplo, para deshacer un cambio que ha ido mal), nunca la 1.

Sin cambios de título, H1 ni descripción (o solo de cifras, como la actualización diaria de las encuestas),
pasa en verde sin consultar Search Console. Las páginas nuevas no cuentan.

Uso: python3 src/control_seo.py --base REV --cabeza REV [--etiquetas a,b] [--resumen FICHERO]
"""
import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_comun as sc  # noqa: E402

MIN_IMPR = 100       # impresiones en 28 días para que una página cuente como «con tráfico»
MIN_IMPR_BUSQ = 10   # una búsqueda con menos impresiones en 28 días no se exige
TOP = 10
MAX_PAGINAS = 1500   # si hay más páginas con tráfico, se revisan las de más impresiones
VENTANA_H = 48


def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--cabeza", required=True)
    ap.add_argument("--etiquetas", default="")
    ap.add_argument("--resumen")
    ap.add_argument("--ahora", help="ISO, para simulacros (por defecto, ahora)")
    a = ap.parse_args()
    out = []
    p = out.append
    nacho = sc.ETIQUETA_NACHO in {e.strip() for e in a.etiquetas.split(",")}
    ahora = datetime.fromisoformat(a.ahora) if a.ahora else datetime.now(timezone.utc)

    cambios = sc.cambios_seo(a.base, a.cabeza)
    if not cambios:
        p("## Control de SEO: sin cambios de título, H1 ni descripción\n")
        return fin(out, a.resumen, 0)

    p(f"## Control de SEO: {len(cambios)} páginas cambian de título, H1 o descripción\n")
    if not os.environ.get("GSC_CREDENTIALS"):
        p("**Rojo:** no hay acceso a Search Console (secreto GSC_CREDENTIALS) y sin él no se puede comprobar "
          "que no se pierde ninguna búsqueda.\n")
        return fin(out, a.resumen, 1)

    s = sc.sesion()
    hoy = ahora.date()
    ini, fn = (hoy - timedelta(days=28)).isoformat(), hoy.isoformat()
    trafico = {}
    fila = 0
    while True:
        filas = sc.consulta(s, ini, fn, ["page"], 25000, inicio_fila=fila)
        for f in filas:
            trafico[f["keys"][0]] = f["impressions"]
        if len(filas) < 25000:
            break
        fila += 25000
    con = sorted((c for c in cambios if trafico.get(c["url"], 0) >= MIN_IMPR),
                 key=lambda c: -trafico[c["url"]])
    p(f"Con tráfico (≥ {MIN_IMPR} impresiones en 28 días, del {ini} al {fn}): {len(con)}. "
      "Search Console da los datos de los últimos días con retraso; el periodo de 28 días lo compensa.\n")
    fallos, avisos = [], []

    # Regla 3: páginas clave
    clave = [c for c in cambios if c["ruta"] in sc.CLAVE]
    if clave:
        rutas = ", ".join(c["ruta"] for c in clave)
        if nacho:
            p(f"Páginas clave ({rutas}): con la etiqueta «{sc.ETIQUETA_NACHO}» (Nacho ha dicho «Fusiona»).\n")
        else:
            fallos.append(f"Cambia el título, H1 o descripción de una página clave ({rutas}). Necesita el «Fusiona» "
                          f"de Nacho: cuando lo dé, pon al PR la etiqueta «{sc.ETIQUETA_NACHO}».")

    # Regla 2: de uno en uno
    if con:
        desde = (ahora - timedelta(hours=VENTANA_H)).isoformat()
        for c in sc.commits_seo(a.base, desde):
            pags = [x["ruta"] for x in c["cambios"] if trafico.get(x["url"], 0) >= MIN_IMPR]
            if not pags:
                continue
            hasta = datetime.fromisoformat(c["fecha"]) + timedelta(hours=VENTANA_H)
            txt = (f"Otro cambio de SEO sigue en vigilancia hasta el {hora_es(hasta)}: {c['sha'][:7]} «{c['asunto']}» "
                   f"({', '.join(pags[:5])}{'…' if len(pags) > 5 else ''}). Los cambios de SEO van de uno en uno. Si este PR solo corrige un hecho (por ejemplo, un dato equivocado en un titular), el editor puede fusionarlo con este aviso.")
            if nacho:
                avisos.append(txt + f" Se deja pasar por la etiqueta «{sc.ETIQUETA_NACHO}».")
            else:
                fallos.append(txt)

    # Regla 1: las 10 búsquedas principales de cada página, tal cual
    revisar = con[:MAX_PAGINAS]
    if len(con) > MAX_PAGINAS:
        avisos.append(f"Hay {len(con)} páginas con tráfico que cambian; se han revisado las {MAX_PAGINAS} con más "
                      "impresiones. Un cambio así de grande conviene partirlo.")
    filas_tabla = []
    # Búsquedas de cada página: una sola consulta de todo el sitio (búsqueda × página), por tandas de 25.000 filas;
    # una consulta por página tardaba 2 s cada una (13 minutos con las 400 de #609). Si son pocas páginas, una a una.
    por_pagina = {}
    if len(revisar) > 20:
        quiero = {c["url"] for c in revisar}
        fila = 0
        while fila < 250000:
            filas = sc.consulta(s, ini, fn, ["page", "query"], 25000, inicio_fila=fila)
            for f in filas:
                if f["keys"][0] in quiero:
                    por_pagina.setdefault(f["keys"][0], []).append({"keys": [f["keys"][1]], **{
                        k: f[k] for k in ("clicks", "impressions")}})
            if len(filas) < 25000:
                break
            fila += 25000
    for c in revisar:
        busq = (por_pagina.get(c["url"], []) if len(revisar) > 20
                else sc.consulta(s, ini, fn, ["query"], 100, sc.filtro_pagina(c["url"])))
        busq = sorted((b for b in busq if b["impressions"] >= MIN_IMPR_BUSQ), key=lambda b: -b["impressions"])[:TOP]
        for b in busq:
            q = b["keys"][0]
            for campo in c["campos"]:
                viejo, nuevo = c["antes"].get(campo, ""), c["despues"].get(campo, "")
                if sc.contiene_exacta(viejo, q) and not sc.contiene_exacta(nuevo, q):
                    fallos.append(f"{c['ruta']}: {sc.CON_ARTICULO[campo]} pierde la búsqueda exacta «{q}» "
                                  f"({sc.num(b['impressions'])} impresiones en 28 días).")
                    filas_tabla.append((c["ruta"], q, b, campo, "se pierde tal cual"))
                elif sc.contiene_palabras(viejo, q) and not sc.contiene_palabras(nuevo, q):
                    avisos.append(f"{c['ruta']}: {sc.CON_ARTICULO[campo]} deja fuera alguna palabra de «{q}» "
                                  f"({sc.num(b['impressions'])} impresiones en 28 días).")
                    filas_tabla.append((c["ruta"], q, b, campo, "faltan palabras"))

    if fallos:
        p(f"### Rojo ({len(fallos)})\n")
        p("\n".join(f"- {x}" for x in fallos) + "\n")
    if avisos:
        p(f"### Avisos ({len(avisos)})\n")
        p("\n".join(f"- {x}" for x in avisos[:40]) + (f"\n- … y {len(avisos) - 40} más." if len(avisos) > 40 else "")
          + "\n")
    if not fallos:
        p("Ninguna página con tráfico pierde ninguna de sus 10 búsquedas principales.\n")

    p("### Páginas con tráfico que cambian\n")
    p("| Página | Impr. 28 días | Cambia | Antes | Después |\n|---|---:|---|---|---|")
    for c in revisar[:60]:
        for campo in c["campos"]:
            p(f"| {c['ruta']} | {sc.num(trafico[c['url']])} | {sc.NOMBRES[campo]} | "
              f"{celda(c['antes'].get(campo))} | {celda(c['despues'].get(campo))} |")
    if len(revisar) > 60:
        p(f"\n… y {len(revisar) - 60} páginas más.")
    p("")
    return fin(out, a.resumen, 1 if fallos else 0)


def celda(x):
    x = (x or "–").replace("|", "/")
    return x if len(x) <= 160 else x[:157] + "…"


def hora_es(d):
    from zoneinfo import ZoneInfo
    return d.astimezone(ZoneInfo("Europe/Madrid")).strftime("%d-%m a las %H:%M")


def fin(out, resumen, codigo):
    texto = "\n".join(out) + "\n"
    print(texto)
    if resumen:
        with open(resumen, "a", encoding="utf-8") as f:
            f.write(texto)
    return codigo


if __name__ == "__main__":
    sys.exit(principal())
