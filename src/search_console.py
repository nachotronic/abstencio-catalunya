"""Informe de Google Search Console para mapaelectoral.es.

Lee la clave de la cuenta de servicio del entorno (GSC_CREDENTIALS, JSON) y
escribe un informe en Markdown por la salida estándar: propiedades accesibles,
totales, días, páginas y búsquedas principales del periodo.
Nunca imprime la clave.
"""
import json
import os
import sys
from datetime import date, timedelta

from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
API = "https://searchconsole.googleapis.com/webmasters/v3"
DIAS = int(os.environ.get("GSC_DIAS", "28"))
FILAS = int(os.environ.get("GSC_FILAS", "25"))


def sesion():
    cred = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GSC_CREDENTIALS"]), scopes=SCOPES)
    return AuthorizedSession(cred)


def consulta(s, sitio, inicio, fin, dims, filas):
    url = f"{API}/sites/{requests_quote(sitio)}/searchAnalytics/query"
    r = s.post(url, json={"startDate": inicio, "endDate": fin,
                          "dimensions": dims, "rowLimit": filas,
                          "dataState": "all"})
    r.raise_for_status()
    return r.json().get("rows", [])


def requests_quote(x):
    from urllib.parse import quote
    return quote(x, safe="")


def pct(x):
    return f"{x * 100:.1f} %".replace(".", ",")


def num(x):
    return f"{x:,.0f}".replace(",", ".")


def pos(x):
    return f"{x:.1f}".replace(".", ",")


def tabla(filas, cabecera, corta=lambda k: k):
    print(f"| {cabecera} | Clics | Impr. | CTR | Pos. |")
    print("|---|---:|---:|---:|---:|")
    for f in filas:
        k = corta(f["keys"][0])
        print(f"| {k} | {num(f['clicks'])} | {num(f['impressions'])} | "
              f"{pct(f['ctr'])} | {pos(f['position'])} |")
    print()


def main():
    s = sesion()
    r = s.get(f"{API}/sites")
    r.raise_for_status()
    sitios = r.json().get("siteEntry", [])
    print("## Propiedades accesibles\n")
    for e in sitios:
        print(f"- {e['siteUrl']} ({e['permissionLevel']})")
    if not sitios:
        print("Ninguna: la cuenta de servicio no tiene acceso a ninguna propiedad.")
        sys.exit(1)
    print()
    pref = [e["siteUrl"] for e in sitios if "mapaelectoral" in e["siteUrl"]]
    sitio = next((u for u in pref if u.startswith("sc-domain:")), pref[0] if pref else sitios[0]["siteUrl"])
    fin = date.today()
    inicio = fin - timedelta(days=DIAS)
    ini, fn = inicio.isoformat(), fin.isoformat()
    print(f"## {sitio}, del {ini} al {fn}\n")

    tot = consulta(s, sitio, ini, fn, [], 1)
    if tot:
        t = tot[0]
        print(f"Total: {num(t['clicks'])} clics, {num(t['impressions'])} impresiones, "
              f"CTR {pct(t['ctr'])}, posición media {pos(t['position'])}\n")

    print("### Por día\n")
    dias = consulta(s, sitio, ini, fn, ["date"], 100)
    tabla(sorted(dias, key=lambda f: f["keys"][0]), "Día")

    host = "https://mapaelectoral.es"
    print("### Páginas principales (por clics)\n")
    tabla(consulta(s, sitio, ini, fn, ["page"], FILAS), "Página",
          lambda u: u.replace(host, "") or "/")

    print("### Búsquedas principales (por clics)\n")
    tabla(consulta(s, sitio, ini, fn, ["query"], FILAS), "Búsqueda")

    print("### Dispositivo\n")
    tabla(consulta(s, sitio, ini, fn, ["device"], 5), "Dispositivo")

    corte = os.environ.get("GSC_CORTE")
    if corte:
        comparar(s, sitio, date.fromisoformat(corte), fin, host)


def comparar(s, sitio, corte, fin, host):
    """Mismo número de días antes y después de un cambio (p. ej. títulos nuevos)."""
    n = max((fin - corte).days, 1)
    a0, a1 = (corte - timedelta(days=n)).isoformat(), (corte - timedelta(days=1)).isoformat()
    d0, d1 = corte.isoformat(), (corte + timedelta(days=n - 1)).isoformat()
    print(f"## Antes ({a0} a {a1}) y después ({d0} a {d1}) del cambio\n")
    for dim, nombre in (("page", "Página"), ("query", "Búsqueda")):
        antes = {f["keys"][0]: f for f in consulta(s, sitio, a0, a1, [dim], 1000)}
        despues = consulta(s, sitio, d0, d1, [dim], 1000)
        despues.sort(key=lambda f: -f["impressions"])
        print(f"| {nombre} | Impr. antes | Impr. después | CTR antes | CTR después | Pos. antes | Pos. después |")
        print("|---|---:|---:|---:|---:|---:|---:|")
        for f in despues[:FILAS]:
            k = f["keys"][0]
            b = antes.get(k)
            print(f"| {k.replace(host, '') or '/'} | {num(b['impressions']) if b else '–'} | "
                  f"{num(f['impressions'])} | {pct(b['ctr']) if b else '–'} | {pct(f['ctr'])} | "
                  f"{pos(b['position']) if b else '–'} | {pos(f['position'])} |")
        print()


if __name__ == "__main__":
    main()
