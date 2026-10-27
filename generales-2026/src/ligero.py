"""Versión ligera de municipios.json para la carga inicial del mapa (data/municipios-ligero.json).

Uso:  python3 ligero.py      (tras construir.py o republica.py; también lo llama construir.py al final)

municipios.json lleva las ocho generales con secciones (2004-2023), y los scripts de Python que lo leen las necesitan.
El mapa solo pinta una al abrirse, la última, así que carga esta copia sin las anteriores y pide cada una en
data/e/<elección>.json al elegirla, igual que las de antes de 2004 (ver asegura() en app.js). Así la descarga inicial
baja a la mitad, que es lo que más tarda en el móvil.
"""
import json
import os
import re

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def main():
    d = json.load(open(os.path.join(DATA, 'municipios.json')))
    elecciones = sorted({k[:7] for k in d if re.match(r'\d{4}_\d\d_', k)})
    ultima, anteriores = elecciones[-1], elecciones[:-1]
    for y in anteriores:
        cols = {k: v for k, v in d.items() if k.startswith(y + '_')}
        json.dump(cols, open(os.path.join(DATA, 'e', f'{y}.json'), 'w'), separators=(',', ':'))
    lig = {k: v for k, v in d.items() if not re.match(r'\d{4}_\d\d_', k) or k.startswith(ultima + '_')}
    f = os.path.join(DATA, 'municipios-ligero.json')
    json.dump(lig, open(f, 'w'), separators=(',', ':'), ensure_ascii=False)
    print('municipios-ligero.json', os.path.getsize(f) // 1024, 'KB (con', ultima + ');', len(anteriores), 'elecciones a e/')


if __name__ == '__main__':
    main()
