"""Portada del sitio: el mapa de resultados de España en la raíz (index.html).

La pieza se genera en generales-2026/ (generales-2026/src/pagina.py). Este script copia su
index.html a la raíz con las rutas relativas corregidas, la marca como página canónica
(https://mapaelectoral.es/) y deja en generales-2026/index.html una redirección a la portada.
También apunta a la portada los enlaces a generales-2026/ de su llms.txt, su sitemap y su metodología.

En la portada el mapa sube a la primera pantalla: debajo del título, antes de la entradilla.

Uso, cada vez que se actualice la pieza de generales-2026/:  python3 src/portada.py
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
G = ROOT / 'generales-2026'
BASE = 'https://mapaelectoral.es/'
VIEJA = BASE + 'generales-2026/'
CF_ANALYTICS = '''<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "cf0453d1d8f247d4a5dd55aff7b685ae"}'></script><!-- End Cloudflare Web Analytics -->'''
# Datos estructurados del sitio, solo en la portada
SITIO = {'@context': 'https://schema.org', '@type': 'WebSite', '@id': BASE + '#website', 'name': 'Mapa electoral', 'url': BASE,
         'inLanguage': 'es', 'description': 'Periodismo de datos sobre elecciones en España por sección censal.',
         'publisher': {'@id': BASE + '#medio'},
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


# Estilos solo de la portada: cabecera compacta y mapa a la altura de la pantalla.
CSS_PORTADA = """<style id="portada">
header{padding:10px 0 0}
nav.site.col,header.col{max-width:1240px}
header h1{font-size:clamp(22px,2.4vw,32px);margin:2px 0 0}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
#mapa{margin-top:6px}
#mapa .controls{padding:8px 0}
#mapa .mapwrap{height:calc(100svh - 185px);min-height:360px;max-height:900px}
.intro{margin-top:20px}
@media (max-width:760px){
  nav.site{flex-wrap:nowrap;overflow-x:auto;white-space:nowrap;scrollbar-width:none;gap:2px 14px;font-size:13px;padding-top:8px;padding-bottom:6px}
  nav.site::-webkit-scrollbar{display:none}
  .kicker{font-size:11px}
  header h1{font-size:21px;line-height:1.15}
  #mapa .controls{gap:6px 8px;font-size:12px}
  #mapa .controls label{flex:1 1 30%}
  #mapa .controls label.q{flex:1 1 60%}
  #mapa .controls select,#mapa .controls input{font-size:14px;padding:5px 6px}
  #mapa .controls button{font-size:13px;padding:6px 8px}
  /* el mapa a todo el ancho de la pantalla y la leyenda debajo, para que España ocupe todo el ancho */
  #mapa .mapwrap{height:auto;min-height:0;max-height:none;overflow:visible;background:none;border-radius:0;margin:0 -16px}
  #mapa #map{position:relative;height:78vw;max-height:calc(100svh - 230px);background:var(--map-bg)}
  #mapa #legend{position:static;margin:8px 16px 0;max-width:none}
}
</style>
"""


def primera_pantalla(s):
    """Reordena la portada: título, mapa y, debajo, la entradilla y el resto del texto."""
    if 'id="portada"' in s:
        return s
    # la franja con las últimas piezas del Atlas (la rellena atlas/src/paginas.py) va pegada al mapa
    fm = re.search(r'\s*<!--atlas:ultimas-->.*?<!--/atlas:ultimas-->', s, re.S)
    franja = fm.group(0).strip() if fm else ''
    if fm:
        s = s[:fm.start()] + s[fm.end():]
    i, j = s.index('<header class="col">'), s.index('</header>')
    cab = s[i:j]
    k = cab.index('</h1>') + len('</h1>')
    titulo, intro = cab[:k], cab[k:]
    m0 = s.index('<section class="wide" id="mapa"')
    m1 = s.index('</section>', m0) + len('</section>')
    mapa = s[m0:m1].replace('<h2 class="col" id="h-mapa" style="padding:0">', '<h2 class="sr" id="h-mapa">', 1)
    resto = s[j + len('</header>'):m0] + s[m1:]
    resto = resto.replace('<main>', '<main>\n' + mapa + '\n' + franja + '\n<div class="col intro">' + intro + '</div>\n', 1)
    s = s[:i] + titulo + '\n</header>' + resto
    return s.replace('</head>', CSS_PORTADA + '</head>', 1)


def main():
    pieza = (G / 'index.html').read_text(encoding='utf-8')
    if 'http-equiv="refresh"' in pieza:
        print('portada: generales-2026/index.html ya es la redirección; nada que hacer')
        return
    s = re.sub(r'(\s(?:href|src)=")([^"]*)(")', lambda m: m.group(1) + a_raiz(m.group(2)) + m.group(3), pieza)
    s = canonica(s)
    s = s.replace('</head>', '<script type="application/ld+json">' + json.dumps(SITIO, ensure_ascii=False) + '</script>\n</head>', 1)
    s = primera_pantalla(s)
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
