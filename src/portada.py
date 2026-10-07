"""Portada del sitio: el mapa de resultados de España en la raíz (index.html).

La pieza se genera en generales-2026/ (generales-2026/src/pagina.py). Este script copia su
index.html a la raíz con las rutas relativas corregidas, la marca como página canónica
(https://mapaelectoral.es/) y deja en generales-2026/index.html una redirección a la portada.
También apunta a la portada los enlaces a generales-2026/ de su llms.txt, su sitemap y su metodología.

Uso, cada vez que se actualice la pieza de generales-2026/:  python3 src/portada.py
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
G = ROOT / 'generales-2026'
BASE = 'https://mapaelectoral.es/'
VIEJA = BASE + 'generales-2026/'
CF_ANALYTICS = '''<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "d27e4ef550c94f82912044da926a3b0f"}'></script><!-- End Cloudflare Web Analytics -->'''
# Datos estructurados del sitio, solo en la portada
SITIO = {'@context': 'https://schema.org', '@type': 'WebSite', '@id': BASE + '#website', 'name': 'Mapa electoral', 'url': BASE,
         'inLanguage': 'es', 'description': 'Periodismo de datos sobre elecciones en España por sección censal.',
         'publisher': {'@type': 'Person', '@id': BASE + 'sobre-mi.html#person', 'name': 'Nacho G. del Álamo', 'url': BASE + 'sobre-mi.html'},
         'hasPart': [{'@type': 'CollectionPage', 'name': 'Atlas de las anomalías electorales', 'url': BASE + 'atlas/'},
                     {'@type': 'NewsArticle', 'name': '¿Quién no vota en Cataluña?', 'url': BASE + 'abstencion.html'}]}
STUB = '''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>El mapa de las generales</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{base}">
<meta http-equiv="refresh" content="0; url=../">
<script>location.replace('../' + location.search + location.hash)</script>
{cf}
</head>
<body style="font-family:system-ui,sans-serif;padding:16px">
<p>El mapa de resultados está en la <a href="../">portada</a>.</p>
</body>
</html>
'''.format(base=BASE, cf=CF_ANALYTICS)


def a_raiz(url):
    """Ruta relativa desde generales-2026/ convertida a ruta desde la raíz."""
    if re.match(r'^(?:[a-z]+:|//|#|/)', url):
        return url
    if url.startswith('../'):
        return url[3:] or './'
    return 'generales-2026/' + url


def canonica(s):
    # La URL de la pieza (no las de sus descargas) pasa a ser la portada.
    return re.sub(re.escape(VIEJA) + r'(?=["\'<)\s])', BASE, s)


def main():
    pieza = (G / 'index.html').read_text(encoding='utf-8')
    if 'http-equiv="refresh"' in pieza:
        print('portada: generales-2026/index.html ya es la redirección; nada que hacer')
        return
    s = re.sub(r'(\s(?:href|src)=")([^"]*)(")', lambda m: m.group(1) + a_raiz(m.group(2)) + m.group(3), pieza)
    s = canonica(s)
    s = s.replace('</head>', '<script type="application/ld+json">' + json.dumps(SITIO, ensure_ascii=False) + '</script>\n</head>', 1)
    (ROOT / 'index.html').write_text(s, encoding='utf-8')
    (G / 'index.html').write_text(STUB, encoding='utf-8')
    for f in ('llms.txt', 'sitemap.xml', 'metodologia.html'):
        p = G / f
        if p.exists():
            t = canonica(p.read_text(encoding='utf-8'))
            if f == 'sitemap.xml':   # la portada ya está en el sitemap de la raíz
                t = re.sub(r'\s*<url><loc>' + re.escape(BASE) + r'</loc>.*?</url>', '', t)
            if f == 'metodologia.html':
                t = t.replace('href="./"', 'href="../"').replace('href="./#', 'href="../#')
            p.write_text(t, encoding='utf-8')
    print('portada: index.html escrito; generales-2026/index.html redirige a la portada')


main()
