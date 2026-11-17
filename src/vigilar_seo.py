"""Vigilancia de 48 horas tras cada cambio de SEO fusionado en main (regla de Nacho del 17-11-2026, tras #609).

Cada hora (.github/workflows/vigilancia-seo.yml) busca en main los commits de las últimas 48 h que cambian el
título, el H1 o la descripción de páginas con tráfico (sin contar las actualizaciones automáticas del bot ni
los cambios de solo cifras). Para cada uno compara, en Search Console por horas, las impresiones de las páginas
afectadas en las horas posteriores al cambio con las que cabía esperar: el nivel de las 6 horas justo antes del
cambio, con la forma que tuvieron esas mismas horas el día anterior y la semana anterior.

Retraso de Search Console: los datos por horas llegan con varias horas de retraso y las últimas horas salen
incompletas. Por eso solo se cuentan las horas cerradas hace al menos RETRASO_H horas, hace falta un mínimo de
horas y de impresiones, y la caída tiene que darse a la vez con las dos referencias (así un pico de noticias o una
semana con mucho menos tráfico no dan una falsa alarma; comparar a secas con la semana anterior no habría
detectado #609, porque /encuestas/ casi no salía en Google esa semana).

Alarma: una página queda más de un 30 % por debajo de lo esperado (o una de sus búsquedas principales, más de
un 50 %) con las dos referencias. Entonces abre una PR que revierte el commit (git revert) y un issue que avisa a Nacho. La PR de
reversión no se fusiona sola: necesita la revisión del editor. Solo una alarma por commit.
Las páginas que ya han vuelto al texto de antes (por ejemplo, porque otro PR lo ha arreglado) no se vigilan.

Uso: python3 src/vigilar_seo.py [--simulacro SHA] [--ahora ISO] [--resumen FICHERO]
--simulacro: analiza ese commit aunque sea anterior a la vigilancia y no abre PR ni issue.
"""
import argparse
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_comun as sc  # noqa: E402

VENTANA_H = 48
RETRASO_H = 7           # horas más recientes que no se cuentan: el 17-11 a las 10:35 los datos por horas llegaban
                        # hasta las 6:00 (4,5 h de retraso) y las últimas salen incompletas
MIN_HORAS = 3           # horas cerradas después del cambio antes de poder dar la alarma
MIN_BASE = 150          # impresiones mínimas en la referencia (página) para que la comparación valga
MIN_BASE_BUSQ = 100     # ídem para una búsqueda
MIN_REF = 30            # impresiones mínimas en cada tramo de referencia (antes del cambio, día antes, semana antes)
HORAS_ANTES = 6         # horas justo antes del cambio que dan el nivel de partida
CAIDA_PAGINA = 0.30
CAIDA_BUSQ = 0.50
MAX_PAGINAS = 15        # páginas por commit, las de más impresiones
TOP_BUSQ = 10
MIN_IMPR = 100          # impresiones en 7 días para que una página cuente como «con tráfico»
ETIQUETA = "vigilancia-seo"
# Páginas que se vigilan cada hora aunque no cambien, hasta el final del 30-11 (Nacho, 17-11: «con resultados
# será crítico»). Sin commit que revertir: si caen, solo abren un issue (uno al día por página).
SIEMPRE = {"/encuestas/": "2026-11-30T23:59:00+01:00",
           "/elecciones/resultados-elecciones-generales-2026/": "2026-11-30T23:59:00+01:00"}
MADRID = ZoneInfo("Europe/Madrid")
ORIGEN = "HEAD"   # main al empezar (la reversión cambia de rama)


def git(*args, check=True):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=check)


def inicio_vigilancia():
    """Commit que añadió este script: lo anterior no se vigila (#609 lo sigue el hilo de /encuestas/)."""
    r = git("log", "--diff-filter=A", "--format=%H", "--", "src/vigilar_seo.py", check=False)
    shas = r.stdout.split()
    return shas[-1] if shas else None


def es_anterior(sha, limite):
    if not limite:
        return False
    return git("merge-base", "--is-ancestor", sha, limite, check=False).returncode == 0


def hora_es(d):
    return d.astimezone(MADRID).strftime("%d-%m %H:%M")


def serie(s, url, desde, dims):
    """Impresiones por hora (UTC) de una página: {hora: impr} o {(hora, búsqueda): impr}."""
    hasta = datetime.now(timezone.utc) + timedelta(days=1)  # fechas de Search Console en hora del Pacífico
    filas = sc.consulta(s, desde.date().isoformat(), hasta.date().isoformat(), dims, 25000,
                        sc.filtro_pagina(url), estado="hourly_all")
    out = {}
    for f in filas:
        h = datetime.fromisoformat(f["keys"][0]).astimezone(timezone.utc)
        k = h if len(dims) == 1 else (h, f["keys"][1])
        out[k] = out.get(k, 0) + f["impressions"]
    return out


def esperado(ser, antes, horas):
    """Impresiones esperadas después del cambio si nada hubiera cambiado.

    Parte del nivel de las horas justo antes del cambio (mismo día) y le aplica la forma del día: cuánto
    sube o baja ese tramo de horas el día antes y la semana antes. Así no da alarma ni por la hora del día
    ni porque la página venga de un pico de noticias o de una semana con mucho menos tráfico.
    Devuelve {desfase: esperado} solo con las referencias que tienen datos suficientes.
    """
    bt = sum(ser.get(h, 0) for h in antes)
    out = {}
    for d in (24, 168):
        bs = sum(ser.get(h - timedelta(hours=d), 0) for h in antes)
        as_ = sum(ser.get(h - timedelta(hours=d), 0) for h in horas)
        if bs >= MIN_REF and as_ >= MIN_REF:
            out[d] = bt * as_ / bs
    return bt, out


def evalua(ser, antes, horas, minimo, umbral):
    """(después, esperado por referencia, caídas, alarma, motivo si no se puede comparar)."""
    a = sum(ser.get(h, 0) for h in horas)
    bt, esp = esperado(ser, antes, horas)
    if bt < MIN_REF or not esp or min(esp.values()) < minimo:
        return a, esp, {}, False, "poco tráfico para comparar"
    caidas = {d: 1 - a / e for d, e in esp.items()}
    return a, esp, caidas, all(c > umbral for c in caidas.values()), ""


REF = {24: "el día antes", 168: "la semana antes"}


def texto_caidas(caidas):
    return ", ".join(f"{pct_signo(-c)} frente a lo esperado por {REF[d]}" for d, c in caidas.items())


def analiza_pagina(s, c, t0, ahora):
    url = c["url"]
    ultima = (ahora - timedelta(hours=RETRASO_H)).replace(minute=0, second=0, microsecond=0)
    primera = (t0 + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    horas = []
    h = primera
    while h + timedelta(hours=1) <= ultima and h < t0 + timedelta(hours=VENTANA_H):
        horas.append(h)
        h += timedelta(hours=1)
    base0 = t0.replace(minute=0, second=0, microsecond=0)
    antes = [base0 - timedelta(hours=i) for i in range(HORAS_ANTES, 0, -1)]
    res = {"ruta": c["ruta"], "horas": len(horas), "alarma": [], "busq": []}
    if len(horas) < MIN_HORAS:
        res["estado"] = f"esperando datos ({len(horas)} de {MIN_HORAS} horas cerradas)"
        return res
    desde = antes[0] - timedelta(days=8)
    pag = serie(s, url, desde, ["hour"])
    a, esp, caidas, al, motivo = evalua(pag, antes, horas, MIN_BASE, CAIDA_PAGINA)
    res.update(post=a, esp=esp)
    res["estado"] = motivo or texto_caidas(caidas)
    if al:
        res["alarma"].append(f"{c['ruta']}: {sc.num(a)} impresiones en {len(horas)} horas; se esperaban "
                             + " o ".join(f"{sc.num(e)} (por {REF[d]})" for d, e in esp.items())
                             + f" ({texto_caidas(caidas)})")
    # Búsquedas principales de la página antes del cambio
    bq = serie(s, url, desde, ["hour", "query"])
    base_q = {}
    for (h, q), v in bq.items():
        if t0 - timedelta(days=7) <= h < t0:
            base_q[q] = base_q.get(q, 0) + v
    for q in sorted(base_q, key=lambda q: -base_q[q])[:TOP_BUSQ]:
        sq = {h: v for (h, qq), v in bq.items() if qq == q}
        qa, qesp, qc, qal, _ = evalua(sq, antes, horas, MIN_BASE_BUSQ, CAIDA_BUSQ)
        res["busq"].append((q, qa, qesp))
        if qal:
            res["alarma"].append(f"{c['ruta']}, búsqueda «{q}»: {sc.num(qa)} impresiones; se esperaban "
                                 + " o ".join(f"{sc.num(e)} (por {REF[d]})" for d, e in qesp.items())
                                 + f" ({texto_caidas(qc)})")
    return res


def esp_txt(esp, d):
    return sc.num(esp[d]) if d in esp else "–"


def fila(r):
    e = r.get("esp", {})
    return (f"| {r['ruta']} | {r['horas']} | {sc.num(r.get('post', 0))} | {esp_txt(e, 24)} | {esp_txt(e, 168)} | "
            f"{r['estado']} |")


def pct_signo(x):
    return f"{'+' if x >= 0 else '−'}{abs(x) * 100:.0f} %"


def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulacro")
    ap.add_argument("--ahora")
    ap.add_argument("--resumen")
    a = ap.parse_args()
    ahora = datetime.fromisoformat(a.ahora) if a.ahora else datetime.now(timezone.utc)
    global ORIGEN
    ORIGEN = git("rev-parse", "HEAD").stdout.strip()
    out = []
    p = out.append

    if a.simulacro:
        sha = git("rev-parse", a.simulacro).stdout.strip()
        info = git("show", "-s", "--format=%cI%x09%s", sha).stdout.strip().split("\t", 1)
        commits = [{"sha": sha, "fecha": info[0], "asunto": info[1],
                    "cambios": sc.cambios_seo(f"{sha}~1", sha)}]
        p(f"## Vigilancia de SEO: simulacro con {sha[:7]} (no abre PR ni issue)\n")
    else:
        limite = inicio_vigilancia()
        desde = (ahora - timedelta(hours=VENTANA_H)).isoformat()
        commits = [c for c in sc.commits_seo(ORIGEN, desde, sc.CAMPOS) if not es_anterior(c["sha"], limite)]
        fijas = [r for r, h in SIEMPRE.items() if ahora <= datetime.fromisoformat(h)]
        if not commits and not fijas:
            p("## Vigilancia de SEO: ningún cambio de título, H1 ni descripción en las últimas 48 h\n")
            return fin(out, a.resumen)
        p(f"## Vigilancia de SEO: {len(commits)} cambios en las últimas 48 h"
          + (f" y {len(fijas)} páginas clave vigiladas hasta el 30-11" if fijas else "") + "\n")

    p(f"Horas cerradas hasta las {hora_es(ahora - timedelta(hours=RETRASO_H))} (hora de Madrid): Search Console "
      f"tarda horas en dar los datos y las {RETRASO_H} más recientes no se cuentan. Alarma si una página cae más "
      f"de un {CAIDA_PAGINA * 100:.0f} % por debajo de lo esperado (o una búsqueda principal, más de un "
      f"{CAIDA_BUSQ * 100:.0f} %). Lo esperado sale del nivel de las {HORAS_ANTES} horas antes del cambio y de cómo "
      "variaron esas horas el día antes y la semana antes; tiene que caer con las dos referencias.\n")
    s = sc.sesion()
    hoy = ahora.date()
    trafico = {f["keys"][0]: f["impressions"] for f in
               sc.consulta(s, (hoy - timedelta(days=9)).isoformat(), (hoy - timedelta(days=2)).isoformat(),
                           ["page"], 25000)}
    cabeza = {}
    for c in commits:
        t0 = datetime.fromisoformat(c["fecha"]).astimezone(timezone.utc)
        # Las páginas que ya han vuelto al texto de antes no se vigilan
        vivas = []
        for x in c["cambios"]:
            if trafico.get(x["url"], 0) < MIN_IMPR:
                continue
            if not a.simulacro:
                actual = cabeza.get(x["fichero"])
                if actual is None:
                    r = git("show", f"{ORIGEN}:{x['fichero']}", check=False)
                    actual = cabeza[x["fichero"]] = sc.metas(r.stdout)
                if all(sc.sin_cifras(actual.get(k)) == sc.sin_cifras(x["antes"].get(k)) for k in x["campos"]):
                    continue
            vivas.append(x)
        vivas.sort(key=lambda x: -trafico[x["url"]])
        p(f"### {c['sha'][:7]} «{c['asunto']}», fusionado el {hora_es(t0)}\n")
        if not vivas:
            p("Ninguna página con tráfico sigue con el cambio.\n")
            continue
        alarmas, filas = [], []
        for x in vivas[:MAX_PAGINAS]:
            r = analiza_pagina(s, x, t0, ahora)
            alarmas += r["alarma"]
            filas.append(r)
        p("| Página | Horas | Impr. después | Esperadas (día antes) | Esperadas (semana antes) | Estado |\n"
          "|---|---:|---:|---:|---:|---|")
        for r in filas:
            p(fila(r))
        p("")
        for r in filas[:3]:
            if r["busq"]:
                p(f"Búsquedas principales de {r['ruta']}: " + "; ".join(
                    f"«{q}» {sc.num(qa)} / {esp_txt(qe, 24)} / {esp_txt(qe, 168)}" for q, qa, qe in r["busq"][:5])
                  + " (después / esperadas por el día antes / por la semana antes)\n")
        if alarmas:
            p("**Alarma:**\n" + "\n".join(f"- {x}" for x in alarmas) + "\n")
            if a.simulacro:
                p("Simulacro: no se abre PR ni issue.\n")
            else:
                p(alarma(c, alarmas, filas, t0) + "\n")
        else:
            p("Sin alarma.\n")
    if not a.simulacro:
        vigila_fijas(s, ahora, p)
    return fin(out, a.resumen)


def vigila_fijas(s, ahora, p):
    """Últimas 24 horas cerradas de las páginas clave frente al día antes y la semana antes."""
    fijas = [r for r, h in SIEMPRE.items() if ahora <= datetime.fromisoformat(h)]
    if not fijas:
        return
    t0 = ahora - timedelta(hours=RETRASO_H + 25)
    p("### Páginas clave, últimas 24 horas cerradas (vigilancia fija hasta el 30-11)\n")
    p("| Página | Horas | Impr. | Esperadas (día antes) | Esperadas (semana antes) | Estado |\n|---|---:|---:|---:|---:|---|")
    alarmas = []
    for r in fijas:
        x = analiza_pagina(s, {"url": sc.HOST + r, "ruta": r}, t0, ahora)
        p(fila(x))
        alarmas += x["alarma"]
    p("")
    if not alarmas:
        p("Sin alarma.\n")
        return
    p("**Alarma:**\n" + "\n".join(f"- {x}" for x in alarmas) + "\n")
    dia = ahora.astimezone(MADRID).strftime("%d-%m")
    titulo = f"Vigilancia SEO: caída en las páginas clave el {dia}"
    previa = gh("issue", "list", "--label", ETIQUETA, "--state", "all", "--search", f'"{titulo}" in:title',
                "--json", "number")
    if previa.returncode == 0 and previa.stdout.strip() not in ("", "[]"):
        p("Ya hay un aviso de hoy: no se repite.\n")
        return
    gh("label", "create", ETIQUETA, "--color", "B60205", "--description", "Alarma de la vigilancia de SEO", "--force")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    cuerpo = ("@nachotronic La vigilancia de SEO ve una caída en las páginas clave sin un cambio de título que la "
              "explique (no hay nada que revertir):\n\n" + "\n".join(f"- {x}" for x in alarmas)
              + "\n\nSearch Console da los datos por horas con varias horas de retraso: hay que mirarlo hora a hora "
                "antes de sacar conclusiones.\n\n"
                f"Detalle: https://github.com/{repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}")
    iss = gh("issue", "create", "--title", titulo, "--body", cuerpo, "--label", ETIQUETA)
    p(f"Aviso: {iss.stdout.strip() or iss.stderr.strip()[-200:]}\n")


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True)


def alarma(c, alarmas, filas, t0):
    sha7 = c["sha"][:7]
    previa = gh("issue", "list", "--label", ETIQUETA, "--state", "all", "--search", sha7, "--json", "number")
    if previa.returncode == 0 and previa.stdout.strip() not in ("", "[]"):
        return f"Ya hay un aviso abierto para {sha7}: no se repite."
    gh("label", "create", ETIQUETA, "--color", "B60205", "--description", "Alarma de la vigilancia de SEO", "--force")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    rama = f"reversion-seo-{sha7}"
    pr_txt = ""
    git("sparse-checkout", "disable", check=False)
    git("config", "user.name", "github-actions[bot]")
    git("config", "user.email", "41898699+github-actions[bot]@users.noreply.github.com")
    git("checkout", "-B", rama, ORIGEN)
    rev = git("revert", "--no-edit", c["sha"], check=False)
    if rev.returncode != 0:
        git("revert", "--abort", check=False)
        pr_txt = ("No se ha podido preparar la reversión automática (choca con cambios posteriores): "
                  "hay que hacerla a mano.")
    else:
        push = git("push", "-f", "origin", rama, check=False)
        if push.returncode != 0:
            pr_txt = f"No se ha podido subir la rama de reversión: {push.stderr[-300:]}"
        else:
            cuerpo = (f"Reversión automática de {c['sha']} («{c['asunto']}») por la vigilancia de SEO.\n\n"
                      + "\n".join(f"- {x}" for x in alarmas)
                      + "\n\n**No fusionar sin la revisión del editor.** Los datos de Search Console por horas llegan "
                        "con retraso; antes de fusionar, comprobar la caída hora a hora.\n\nLas PR que abre el bot no "
                        "lanzan solas las comprobaciones: lanzar «Verificar piezas» a mano desde Actions.")
            pr = gh("pr", "create", "--base", "main", "--head", rama, "--title",
                    f"Reversión SEO: {c['asunto'][:200]}", "--body", cuerpo, "--label", ETIQUETA)
            pr_txt = (f"PR de reversión: {pr.stdout.strip()}" if pr.returncode == 0 else
                      f"No se ha podido abrir la PR ({pr.stderr.strip()[-200:]}); la rama está lista: "
                      f"https://github.com/{repo}/compare/main...{rama}")
    git("checkout", "-f", "--detach", ORIGEN, check=False)
    cuerpo = (f"@nachotronic La vigilancia de SEO ha detectado una caída tras {c['sha']} («{c['asunto']}»), "
              f"fusionado el {hora_es(t0)} (hora de Madrid).\n\n" + "\n".join(f"- {x}" for x in alarmas)
              + f"\n\n{pr_txt}\n\nLa reversión no se fusiona sin la revisión del editor. Search Console da los datos por "
                "horas con varias horas de retraso: las cifras de las últimas horas pueden subir todavía.\n\n"
                f"Detalle en la ejecución: https://github.com/{repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}")
    iss = gh("issue", "create", "--title", f"Vigilancia SEO: caída tras {sha7} «{c['asunto'][:120]}»",
             "--body", cuerpo, "--label", ETIQUETA)
    return f"{pr_txt} Aviso: {iss.stdout.strip() or iss.stderr.strip()[-200:]}"


def fin(out, resumen):
    texto = "\n".join(out) + "\n"
    print(texto)
    if resumen:
        with open(resumen, "a", encoding="utf-8") as f:
            f.write(texto)
    return 0


if __name__ == "__main__":
    sys.exit(principal())
