"""Envía a Bing Webmaster (SubmitUrlBatch) las URL del sitemap que aún no se han enviado.

Uso: python3 src/bing_enviar.py [--prueba]  (lo lanza cada día .github/workflows/bing.yml)
- Lee https://mapaelectoral.es/sitemap_index.xml y sus sitemaps.
- Guarda lo enviado en data/seo/bing_enviadas.json.
- Respeta la cuota diaria que devuelve GetUrlSubmissionQuota.
- Prioridad: portada y páginas raíz, /elecciones/, /temas/, /encuestas/, generales-2026, atlas, actualidad,
  /municipio/ (primero provincias y después municipios, en el orden del sitemap).
- Bing permite 100 al día y 1.000 al mes; el script usa la cuota que le quede.
La clave sale de la variable BING_WEBMATER_KEY (así está escrita) o BING_WEBMASTER_KEY.
Nunca imprime la clave.
"""
import json, os, re, sys, time, datetime, urllib.request, urllib.parse

SITE = "https://mapaelectoral.es/"
API = "https://ssl.bing.com/webmaster/api.svc/json/"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESTADO = os.path.join(RAIZ, "data", "seo", "bing_enviadas.json")
KEY = os.environ.get("BING_WEBMATER_KEY") or os.environ.get("BING_WEBMASTER_KEY")
if not KEY:
    sys.exit("Falta la variable BING_WEBMATER_KEY / BING_WEBMASTER_KEY")


def get(url):
    # GitHub Pages devuelve a veces un 503 suelto: tres intentos antes de rendirse
    for intento in range(3):
        try:
            return urllib.request.urlopen(url, timeout=60).read().decode()
        except urllib.error.HTTPError as e:
            if e.code < 500 or intento == 2:
                raise
            time.sleep(10)


def api(metodo, cuerpo=None):
    q = urllib.parse.urlencode({"siteUrl": SITE, "apikey": KEY})
    req = urllib.request.Request(API + metodo + "?" + q)
    if cuerpo is not None:
        req.data = json.dumps(cuerpo).encode()
        req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        return json.loads(urllib.request.urlopen(req, timeout=60).read().decode() or "{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"Error {e.code} en {metodo}: {e.read().decode()[:300]}")


def urls_sitemap():
    urls = []
    for sm in re.findall(r"<loc>(.*?)</loc>", get(SITE + "sitemap_index.xml")):
        for u in re.findall(r"<url>\s*<loc>(.*?)</loc>", get(sm)):
            if u not in urls:
                urls.append(u)
    return urls


def prioridad(u):
    # (grupo, profundidad): dentro de cada grupo, primero las páginas menos profundas; sorted() mantiene el orden del sitemap
    for i, p in enumerate(["/elecciones/", "/temas/", "/encuestas/", "/generales-2026/", "/atlas/", "/actualidad/", "/municipio/"]):
        if p in u:
            return (i + 1, u.count("/"))
    return (0, u.count("/"))


estado = json.load(open(ESTADO)) if os.path.exists(ESTADO) else {"enviadas": {}}
todas = urls_sitemap()
pendientes = sorted((u for u in todas if u not in estado["enviadas"]), key=prioridad)
q = api("GetUrlSubmissionQuota")["d"]
cuota = min(q["DailyQuota"], q["MonthlyQuota"])
lote = pendientes[:cuota]
print(f"URL en el sitemap: {len(todas)} · ya enviadas: {len(todas) - len(pendientes)} · "
      f"pendientes: {len(pendientes)} · cuota hoy: {cuota}")
if "--prueba" in sys.argv or not lote:
    sys.exit(0)
api("SubmitUrlBatch", {"siteUrl": SITE, "urlList": lote})
hoy = datetime.date.today().isoformat()
for u in lote:
    estado["enviadas"][u] = hoy
json.dump(estado, open(ESTADO, "w"), indent=1, ensure_ascii=False)
print(f"Enviadas hoy: {len(lote)} · quedan: {len(pendientes) - len(lote)}")
