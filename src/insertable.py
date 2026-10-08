"""Versión insertable del mapa de la portada (insertar/index.html), para que otros medios la pongan en su web con un <iframe>.

Toma de la portada (index.html) los estilos y el bloque del mapa, quita el botón «Insertar en tu web» y añade una firma
con enlace a mapaelectoral.es. Acepta los mismos parámetros que la portada: ?m=<código INE>&e=<elección>.
No se indexa (noindex) y su página canónica es la portada.

Uso, cada vez que cambie la portada (después de src/portada.py):  python3 src/insertable.py
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'https://mapaelectoral.es/'
CF_ANALYTICS = '''<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "cf0453d1d8f247d4a5dd55aff7b685ae"}'></script><!-- End Cloudflare Web Analytics -->'''

# Ocupa todo el marco: controles arriba, mapa en el resto y la firma abajo.
CSS = """<style id="insertable">
html,body{height:100%}
body{margin:0;font-size:16px}
.marco{display:flex;flex-direction:column;height:100svh;padding:0 10px}
#mapa{margin:0;flex:1;display:flex;flex-direction:column;min-height:0}
#mapa .controls{padding:8px 0;gap:6px 8px;font-size:12px}
#mapa .controls label{flex:1 1 28%;gap:2px}
#mapa .controls select,#mapa .controls input{font-size:14px;padding:5px 7px;min-width:0;width:100%}
#mapa .controls button{font-size:13px;padding:6px 10px}
#mapa .mapwrap{flex:1;height:auto;min-height:240px;max-height:none}
.firma{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;font:13px/1.3 var(--sans);color:var(--muted);padding:6px 0 8px}
.firma a{color:var(--ink);font-weight:600}
@media (max-width:760px){
  #mapa .controls label{flex:1 1 40%}
  #mapa .controls label.q{flex:1 1 55%}
  #mapa .mapwrap{height:auto}
}
</style>
"""


def main():
    s = (ROOT / 'index.html').read_text(encoding='utf-8')
    estilos = re.search(r'<style>.*?</style>', s, re.S).group(0)
    m0 = s.index('<section class="wide" id="mapa"')
    mapa = s[m0:s.index('</section>', m0) + len('</section>')]
    mapa = re.sub(r'\s*<button type="button" id="insertar"[^>]*>.*?</button>', '', mapa)
    mapa = re.sub(r'\s*<div class="insertar" id="insertar-caja".*?\n  </div>', '', mapa, flags=re.S)
    mapa = re.sub(r'\s*<p class="hint">.*?</p>', '', mapa, flags=re.S)
    mapa = re.sub(r'\s*<h2[^>]*id="h-mapa"[^>]*>.*?</h2>', '', mapa)
    mapa = mapa.replace('class="wide" ', '', 1).replace('aria-labelledby="h-mapa"', 'aria-label="Mapa electoral"')
    deck = re.search(r'<script src="https://unpkg.com/deck.gl[^"]*"></script>', s).group(0)
    assert 'id="insertar"' not in mapa and 'id="map"' in mapa
    out = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mapa electoral de España por municipio y sección censal</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{BASE}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
{estilos}
{CSS}{CF_ANALYTICS}
</head>
<body>
<div class="marco">
{mapa}
<p class="firma"><span>Datos: Ministerio del Interior e INE · CC BY 4.0</span><a id="firma" href="{BASE}" target="_blank" rel="noopener">Mapa Electoral · Nacho G. del Álamo ↗</a></p>
</div>
{deck}
<script src="../generales-2026/app.js"></script>
<script>document.getElementById('firma').href = '{BASE}' + location.search;</script>
</body>
</html>
"""
    d = ROOT / 'insertar'
    d.mkdir(exist_ok=True)
    (d / 'index.html').write_text(out, encoding='utf-8')
    print('insertable: insertar/index.html')


if __name__ == '__main__':
    main()
