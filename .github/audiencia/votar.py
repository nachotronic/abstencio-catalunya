"""Tráfico de las tres guías prácticas (voto por correo, mesa, tarjeta censal): Search Console y Cloudflare."""
import json, os, sys, datetime as dt, requests
sys.path.insert(0, "src")
import seo_comun as sc

P = ["/elecciones/voto-por-correo-29n/", "/elecciones/mesa-electoral-29n/", "/elecciones/tarjeta-censal-29n/"]
hoy = dt.date.today()
ini = (hoy - dt.timedelta(days=28)).isoformat(); fin = hoy.isoformat()
s = sc.sesion()
for p in P:
    url = sc.HOST + p
    tot = sc.consulta(s, ini, fin, [], filtros=sc.filtro_pagina(url))
    print(f"\n## GSC {p} 28 d: {json.dumps(tot)}")
    for r in sc.consulta(s, (hoy - dt.timedelta(days=10)).isoformat(), fin, ["date"], filtros=sc.filtro_pagina(url)):
        print("  dia", r["keys"][0], "clics", r["clicks"], "impr", r["impressions"], "pos", round(r["position"], 1))
    for r in sc.consulta(s, ini, fin, ["query"], filas=10, filtros=sc.filtro_pagina(url)):
        print("  q", r["keys"][0], "clics", r["clicks"], "impr", r["impressions"], "pos", round(r["position"], 1))

tok = [t.strip("'\"") for t in os.environ.get("CF", "").split() if t.strip("'\"").startswith("cfut_")]
if not tok:
    print("sin token Cloudflare"); sys.exit()
ACC = "dee996483598974c337d0777f5ef047c"; SITE = "532b57a6348a4babba29020993949dd7"
q = """query($a:String!,$f:AccountRumPageloadEventsAdaptiveGroupsFilter_InputObject!){viewer{accounts(filter:{accountTag:$a}){
rumPageloadEventsAdaptiveGroups(limit:500,filter:$f,orderBy:[sum_visits_DESC]){sum{visits} count dimensions{requestPath refererHost refererPath}}}}}"""
for d0, d1 in [((hoy - dt.timedelta(days=7)).isoformat(), hoy.isoformat()), ((hoy - dt.timedelta(days=28)).isoformat(), (hoy - dt.timedelta(days=7)).isoformat())]:
    f = {"siteTag": SITE, "date_geq": d0, "date_leq": d1, "requestPath_in": P}
    r = requests.post("https://api.cloudflare.com/client/v4/graphql", headers={"Authorization": "Bearer " + tok[0]},
                      json={"query": q, "variables": {"a": ACC, "f": f}}).json()
    if r.get("errors"):
        print(r["errors"]); continue
    g = r["data"]["viewer"]["accounts"][0]["rumPageloadEventsAdaptiveGroups"]
    print(f"\n## Cloudflare {d0}..{d1}")
    tot = {}
    for x in g:
        dd = x["dimensions"]; tot[dd["requestPath"]] = tot.get(dd["requestPath"], 0) + x["sum"]["visits"]
    print("  visitas por página", tot)
    agg = {}
    for x in g:
        dd = x["dimensions"]; k = (dd["requestPath"], dd["refererHost"], dd["refererPath"] if "mapaelectoral" in dd["refererHost"] else "")
        agg[k] = agg.get(k, [0, 0]); agg[k][0] += x["sum"]["visits"]; agg[k][1] += x["count"]
    for k, v in sorted(agg.items(), key=lambda kv: -kv[1][1])[:40]:
        print("  ", k, "visitas", v[0], "vistas", v[1])
