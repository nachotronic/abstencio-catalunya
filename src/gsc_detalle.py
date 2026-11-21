"""Verificación puntual: /encuestas/ día a día (no fusionar)."""
import json, os
from urllib.parse import quote
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
S = AuthorizedSession(service_account.Credentials.from_service_account_info(
    json.loads(os.environ["GSC_CREDENTIALS"]), scopes=["https://www.googleapis.com/auth/webmasters.readonly"]))
SITIO = "sc-domain:mapaelectoral.es"; H = "https://mapaelectoral.es"
def q(ini, fin, dims, filtros=None, n=25000, estado="all"):
    b = {"startDate": ini, "endDate": fin, "dimensions": dims, "rowLimit": n, "dataState": estado}
    if filtros: b["dimensionFilterGroups"] = [{"filters": filtros}]
    r = S.post(f"https://searchconsole.googleapis.com/webmasters/v3/sites/{quote(SITIO, safe='')}/searchAnalytics/query", json=b)
    r.raise_for_status(); return r.json().get("rows", [])
def l(f): print("  ", " ¦ ".join(k.replace(H, "") for k in f["keys"]), f"{f['clicks']:.0f} {f['impressions']:.0f} {f['ctr']*100:.1f}% pos {f['position']:.1f}")
P = [{"dimension": "page", "operator": "equals", "expression": H + "/encuestas/"}]
Q = [{"dimension": "query", "operator": "equals", "expression": "encuestas elecciones generales 2026"}]
print("# /encuestas/ por dia"); [l(f) for f in sorted(q("2026-11-13", "2026-11-21", ["date"], P), key=lambda f: f["keys"][0])]
print("# consulta principal, todas las paginas, por dia"); [l(f) for f in sorted(q("2026-11-13", "2026-11-21", ["date", "page"], Q), key=lambda f: (f["keys"][0], -f["impressions"])) if f["impressions"] >= 5]
print("# consultas con 'encuesta' en todo el sitio, por dia"); [l(f) for f in sorted(q("2026-11-13", "2026-11-21", ["date"], [{"dimension": "query", "operator": "contains", "expression": "encuesta"}]), key=lambda f: f["keys"][0])]
print("# paginas para consultas con 'encuesta', 19-20 nov"); [l(f) for f in sorted(q("2026-11-19", "2026-11-20", ["page"], [{"dimension": "query", "operator": "contains", "expression": "encuesta"}]), key=lambda f: -f["impressions"])[:12]]
print("# todo el sitio por dia"); [l(f) for f in sorted(q("2026-11-13", "2026-11-21", ["date"]), key=lambda f: f["keys"][0])]
r = S.post("https://searchconsole.googleapis.com/v1/urlInspection/index:inspect", json={"inspectionUrl": H + "/encuestas/", "siteUrl": SITIO, "languageCode": "es"})
print("INSPECT", r.json().get("inspectionResult", {}).get("indexStatusResult", {}).get("lastCrawlTime"))
