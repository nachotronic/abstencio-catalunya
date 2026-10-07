"""Fotos y notas de color de cada pieza (2026-10-07).

fotos.json: una foto de Wikimedia Commons por pieza (archivo en atlas/img/<slug>.webp, autor, licencia y página de Commons).
color.json: notas «Sobre el terreno». Cada nota lleva dos fuentes independientes con la URL, el extracto literal que la
respalda y la fecha de consulta; controles.py comprueba que haya dos y que sean de sitios distintos.
Las notas describen el lugar; no explican el voto.
"""
import json
import pathlib
from urllib.parse import urlparse

SRC = pathlib.Path(__file__).resolve().parent
FOTOS = json.load(open(SRC / 'fotos.json', encoding='utf-8'))
COLOR = json.load(open(SRC / 'color.json', encoding='utf-8'))


def sitio(u):
    h = urlparse(u).netloc.lower()
    return '.'.join(h.split('.')[-2:])


def anadir(piezas):
    for p in piezas:
        f = FOTOS.get(p['slug'])
        if f and not p.get('foto'):
            p['foto'] = dict(src=f'../../img/{p["slug"]}.webp', alt=f['alt'], autor=f['autor'], licencia=f['licencia'], url=f['url'],
                             w=f['w'], h=f['h'])
        notas = COLOR.get(p['slug'])
        if notas and not p.get('color'):
            p['color'] = [(n['texto'], [s['url'] for s in n['fuentes']]) for n in notas]
    return piezas
