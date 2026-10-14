"""Avisa a Bing, Yandex y el resto de buscadores de IndexNow de las páginas que han cambiado.

Bing alimenta la búsqueda de ChatGPT, Copilot y DuckDuckGo, así que una página avisada aparece antes
en esos asistentes. Lo lanza .github/workflows/indexnow.yml en cada push a main, con las páginas HTML
que cambian en ese push; también se puede ejecutar a mano con rutas:

    python3 src/indexnow.py elecciones/madrid/index.html actualidad/index.html

Solo envía páginas indexables (con canonical y sin noindex), por su URL canónica.
La clave es el fichero 7076dc68fb935de114542a0876378fae.txt de la raíz.
"""
import json, pathlib, re, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'https://mapaelectoral.es/'
CLAVE = '7076dc68fb935de114542a0876378fae'


def url_canonica(ruta):
    f = ROOT / ruta
    if f.suffix != '.html' or not f.exists() or '/src/' in '/' + ruta:
        return None
    t = f.read_text(encoding='utf-8', errors='ignore')
    cab = t[:t.find('</head>')]
    if 'noindex' in cab or 'http-equiv="refresh"' in cab:
        return None
    m = re.search(r'<link rel="canonical" href="([^"]+)"', cab)
    return m.group(1) if m and m.group(1).startswith(BASE) else None


def main(rutas):
    urls = sorted({u for u in map(url_canonica, rutas) if u})[:10000]
    if not urls:
        print('indexnow: ninguna página indexable que avisar')
        return
    cuerpo = json.dumps({'host': 'mapaelectoral.es', 'key': CLAVE, 'keyLocation': BASE + CLAVE + '.txt', 'urlList': urls}).encode()
    req = urllib.request.Request('https://api.indexnow.org/indexnow', data=cuerpo,
                                 headers={'Content-Type': 'application/json; charset=utf-8'})
    with urllib.request.urlopen(req, timeout=60) as r:
        print(f'indexnow: {len(urls)} URL enviadas, respuesta {r.status}')


if __name__ == '__main__':
    main(sys.argv[1:])
