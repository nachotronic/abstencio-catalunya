"""Municipios de España y ganador por elección (del mapa de generales-2026) para los Shorts de mapa nacional."""
import json, math, os, sys
D = os.path.join(os.path.dirname(__file__), '..', 'generales-2026', 'data')
m = json.load(open(os.path.join(D, 'municipios.json')))
meta = json.load(open(os.path.join(D, 'meta.json')))
k = math.cos(math.radians(40))
polys = []
for parts in m['poly']:
    rings = []
    for f in parts:
        x, y = f[0], f[1]
        pts = [round(x / m['S'] * k, 3), round(-y / m['S'], 3)]
        for i in range(2, len(f), 2):
            x += f[i]; y += f[i + 1]
            q = [round(x / m['S'] * k, 3), round(-y / m['S'], 3)]
            if q != pts[-2:]:
                pts += q
        if len(pts) >= 6:
            rings.append(pts)
    polys.append(rings)
gana = {}
for e in meta['elecciones']:
    if e['tipo'] != 'generales':
        continue
    c = e['cod']
    src = m if c + '_gana' in m else json.load(open(os.path.join(D, 'e', c + '.json')))
    gana[c] = [-1 if g is None else g for g in src[c + '_gana']]
out = {'familias': meta['familias'], 'nombres': {e['cod']: e['nombre'] for e in meta['elecciones']},
       'cod': m['cod'], 'poly': polys, 'gana': gana}
json.dump(out, open(sys.argv[1], 'w'), separators=(',', ':'))
print(len(polys), list(gana))
