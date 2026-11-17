#!/usr/bin/env python3
"""Piezas del feed (actualidad/feed.xml del repo) de las últimas 36 horas que aún no tienen vídeo en la release «videos».

Uso: python3 video/pendientes.py <nombres-ya-subidos.txt>   → una línea por pieza: «<ruta> <nombre.mp4>»
Las piezas con <meta name="redes" content="no"> se saltan, igual que en redes/src/publicar.py.
"""
import datetime, os, re, sys, urllib.parse
import xml.etree.ElementTree as ET

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
VENTANA = datetime.timedelta(hours=36)
ADELANTO = datetime.timedelta(hours=12)

subidos = set(open(sys.argv[1]).read().split()) if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else set()
ahora = datetime.datetime.now(datetime.timezone.utc)
for item in ET.parse(os.path.join(RAIZ, 'actualidad', 'feed.xml')).getroot().iter('item'):
    fecha = datetime.datetime.strptime(item.findtext('pubDate'), '%a, %d %b %Y %H:%M:%S %z')
    # El feed fecha cada pieza a las 8.00 UTC de su día, aunque se fusione antes (17-11-2026: la de Gipuzkoa, fusionada a
    # las 7.30 UTC, quedaba «en el futuro» y se saltaba): se aceptan hasta 12 horas por delante
    if not (-ADELANTO <= ahora - fecha <= VENTANA):
        continue
    ruta = urllib.parse.urlparse(item.findtext('link').strip()).path
    if not ruta.endswith('/'):
        ruta += '/'
    pagina = os.path.join(RAIZ, ruta.strip('/'), 'index.html')
    if not os.path.exists(pagina):
        print(f'# {ruta}: no está en el repositorio', file=sys.stderr)
        continue
    if re.search(r'<meta[^>]+name="redes"[^>]+content="no"', open(pagina, encoding='utf-8').read()):
        continue
    nombre = 'x-' + ruta.strip('/').split('/')[-1] + '.mp4'
    if nombre not in subidos:
        print(ruta, nombre)
