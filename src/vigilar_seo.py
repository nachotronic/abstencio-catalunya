"""Vigilancia de 48 horas tras cada cambio de SEO fusionado en main (regla de Nacho del 17-11-2026, tras #609).

Cada hora (.github/workflows/vigilancia-seo.yml) busca en main los commits de las últimas 48 h que cambian el
título, el H1 o la descripción de páginas con tráfico (sin contar las actualizaciones automáticas del bot ni
los cambios de solo cifras). Para cada uno compara, en Search Console por horas, las impresiones de las páginas
afectadas en las horas posteriores al cambio con las mismas horas del día anterior y de una semana antes.

Retraso de Search Console: los datos por horas llegan con varias horas de retraso y las últimas horas salen
incompletas. Por eso solo se cuentan las horas cerradas hace al menos RETRASO_H horas, hace falta un mínimo de
horas y de impresiones, y la caída tiene que darse a la vez frente al día anterior y frente a la semana anterior
(así un pico de noticias en uno de los dos no da una falsa alarma).

Alarma: una página cae más de un 30 % (o una de sus búsquedas principales, más de un 50 %) frente a las dos
referencias. Entonces abre una PR que revierte el commit (git revert) y un issue que avisa a Nacho. La PR de
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
RETRASO_H = 5           # horas más recientes que no se cuentan: Search Console aún no las tiene completas
MIN_HORAS = 3           # horas cerradas después del cambio antes de poder dar la alarma
MIN_BASE = 150          # impresiones mínimas en la referencia (página) para que la comparación valga
MIN_BASE_BUSQ = 100     # ídem para una búsqueda
CAIDA_PAGINA = 0.30
CAIDA_BUSQ = 0.50
MAX_PAGINAS = 15        # páginas por commit, las de más impresiones
TOP_BUSQ = 10
MIN_IMPR = 100          # impresiones en 7 días para que una página cuente como «con tráfico»
ETIQUETA = "vigilancia-seo"
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


def serie(s, url, desde, hasta, dims):
    """Impresiones por hora (UTC) de una página: {hora: impr} o {(hora, búsqueda): impr}."""
    filas = sc.consulta(s, desde.date().isoformat(), hasta.date().isoformat(), dims, 25000,
                        sc.filtro_pagina(url), estado="hourly_all")
    out = {}
    for f in filas:
        h = datetime.fromisoformat(f["keys"][0]).astimezone(timezone.utc)
        k = h if len(dims) == 1 else (h, f["keys"][1])
        out[k] = out.get(k, 0) + f["impressions"]
    return out


def comparar(post, ref, horas):
    """Suma de las horas post frente a la misma hora desplazada (ref: horas de desfase)."""
    a = sum(post.get(h, 0) for h in horas)
    b = sum(post.get(h - timedelta(hours=ref), 0) for h in horas)
    return a, b


def analiza_pagina(s, c, t0, ahora):
    url = c["url"]
    ultima = (ahora - timedelta(hours=RETRASO_H)).replace(minute=0, second=0, microsecond=0)
    primera = (t0 + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    horas = []
    h = primera
    while h + timedelta(hours=1) <= ultima and h < t0 + timedelta(hours=VENTANA_H):
        horas.append(h)
        h += timedelta(hours=1)
    res = {"ruta": c["ruta"], "horas": len(horas), "desde": primera, "hasta": ultima, "alarma": [], "busq": []}
    if len(horas) < MIN_HORAS:
        res["estado"] = f"esperando datos ({len(horas)} de {MIN_HORAS} horas cerradas)"
        return res
    desde = primera - timedelta(days=8)
    pag = serie(s, url, desde, ahora, ["hour"])
    a, b1 = comparar(pag, 24, horas)
    _, b7 = comparar(pag, 168, horas)
    res.update(post=a, b1=b1, b7=b7)
    caida = lambda x, y: 1 - x / y if y else 0.0  # noqa: E731
    if min(b1, b7) < MIN_BASE:
        res["estado"] = "poco tráfico para comparar"
    else:
        c1, c7 = caida(a, b1), caida(a, b7)
        res["estado"] = f"{pct_signo(-c1)} frente al día antes, {pct_signo(-c7)} frente a la semana antes"
        if c1 > CAIDA_PAGINA and c7 > CAIDA_PAGINA:
            res["alarma"].append(f"{c['ruta']}: impresiones {sc.num(a)} frente a {sc.num(b1)} el día antes "
                                 f"({pct_signo(-c1)}) y {sc.num(b7)} la semana antes ({pct_signo(-c7)})")
    # Búsquedas principales de la página antes del cambio
    bq = serie(s, url, desde, ahora, ["hour", "query"])
    base_q = {}
    for (h, q), v in bq.items():
        if t0 - timedelta(days=7) <= h < t0:
            base_q[q] = base_q.get(q, 0) + v
    for q in sorted(base_q, key=lambda q: -base_q[q])[:TOP_BUSQ]:
        sq = {h: v for (h, qq), v in bq.items() if qq == q}
        qa, q1 = comparar(sq, 24, horas)
        _, q7 = comparar(sq, 168, horas)
        res["busq"].append((q, qa, q1, q7))
        if min(q1, q7) >= MIN_BASE_BUSQ and caida(qa, q1) > CAIDA_BUSQ and caida(qa, q7) > CAIDA_BUSQ:
            res["alarma"].append(f"{c['ruta']}, búsqueda «{q}»: {sc.num(qa)} impresiones frente a {sc.num(q1)} el "
                                 f"día antes y {sc.num(q7)} la semana antes")
    return res


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
        if not commits:
            p("## Vigilancia de SEO: ningún cambio de título, H1 ni descripción en las últimas 48 h\n")
            return fin(out, a.resumen)
        p(f"## Vigilancia de SEO: {len(commits)} cambios en las últimas 48 h\n")

    p(f"Horas cerradas hasta las {hora_es(ahora - timedelta(hours=RETRASO_H))} (hora de Madrid): Search Console "
      f"tarda horas en dar los datos y las {RETRASO_H} más recientes no se cuentan. Alarma si una página cae más "
      f"de un {CAIDA_PAGINA * 100:.0f} % (o una búsqueda principal, más de un {CAIDA_BUSQ * 100:.0f} %) frente al "
      "día antes y frente a la semana antes a la vez.\n")
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
        p("| Página | Horas | Impr. después | Día antes | Semana antes | Estado |\n|---|---:|---:|---:|---:|---|")
        for r in filas:
            p(f"| {r['ruta']} | {r['horas']} | {sc.num(r.get('post', 0))} | {sc.num(r.get('b1', 0))} | "
              f"{sc.num(r.get('b7', 0))} | {r['estado']} |")
        p("")
        for r in filas[:3]:
            if r["busq"]:
                p(f"Búsquedas principales de {r['ruta']}: " + "; ".join(
                    f"«{q}» {sc.num(qa)} / {sc.num(q1)} / {sc.num(q7)}" for q, qa, q1, q7 in r["busq"][:5])
                  + " (después / día antes / semana antes)\n")
        if alarmas:
            p("**Alarma:**\n" + "\n".join(f"- {x}" for x in alarmas) + "\n")
            if a.simulacro:
                p("Simulacro: no se abre PR ni issue.\n")
            else:
                p(alarma(c, alarmas, filas, t0) + "\n")
        else:
            p("Sin alarma.\n")
    return fin(out, a.resumen)


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
