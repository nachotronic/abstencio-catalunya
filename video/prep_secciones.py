"""Secciones censales de una provincia (del mapa de generales-2026) con el ganador de 2023, para los Shorts de zoom."""
import json, math, os, sys
D = os.path.join(os.path.dirname(__file__), '..', 'generales-2026', 'data')
prov, dst = sys.argv[1], sys.argv[2]
m = json.load(open(os.path.join(D, 'sec', prov + '.json')))
k = math.cos(math.radians(40))
polys = []
for parts in m['poly']:
    rings = []
    for f in parts:
        x, y = f[0], f[1]
        pts = [round(x / m['S'] * k, 5), round(-y / m['S'], 5)]
        for i in range(2, len(f), 2):
            x += f[i]; y += f[i + 1]
            pts += [round(x / m['S'] * k, 5), round(-y / m['S'], 5)]
        rings.append(pts)
    polys.append(rings)
out = {'cod': m['cod'], 'poly': polys, 'gana': [-1 if g is None else g for g in m['2023_07_gana']],
       'ficha': {c: {'part': m['2023_07_part'][i], 'renta': m['renta_uc'][i], 'edad': m['edad_media'][i],
                     'extranjeros': m['extranjeros'][i], 'censo': m['2023_07_censo'][i]} for i, c in enumerate(m['cod'])}}
json.dump(out, open(dst, 'w'), separators=(',', ':'))
print(len(polys))
