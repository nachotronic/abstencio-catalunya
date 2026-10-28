"""Provincias de España proyectadas, con escaños 2023/2026, ganador de 2023 y censo 2023/2026, para los Shorts de las guías."""
import csv, json, math, os, sys
R = os.path.join(os.path.dirname(__file__), '..')
p = json.load(open(os.path.join(R, 'generales-2026', 'data', 'provincias.json')))
cifras = json.load(open(os.path.join(R, 'actualidad', 'src', 'sistema', 'cifras.json')))['2023_07']['provincias']
sim = json.load(open(os.path.join(R, 'actualidad', 'src', 'sistema', 'simulador.json')))['elecciones']['2023_07']
k = math.cos(math.radians(40))
polys = []
for parts in p['poly']:
    rings = []
    for f in parts:
        x, y = f[0], f[1]
        pts = [round(x / p['S'] * k, 3), round(-y / p['S'], 3)]
        for i in range(2, len(f), 2):
            x += f[i]; y += f[i + 1]
            q = [round(x / p['S'] * k, 3), round(-y / p['S'], 3)]
            if q != pts[-2:]:
                pts += q
        if len(pts) >= 6:
            rings.append(pts)
    polys.append(rings)
censo = {}
for r in csv.DictReader(open(os.path.join(R, 'data', 'censo', 'censo_municipios_2023_2026.csv'))):
    c = censo.setdefault(r['mun_code'][:2], [0, 0, 0, 0])
    for j, col in enumerate(['cer_2023', 'cera_2023', 'cer_2026', 'cera_2026']):
        c[j] += int(float(r[col] or 0))
prov = {}
for cod in p['cod']:
    c = str(cod).zfill(2)
    e23 = cifras[c]['escanos']
    e26 = {'28': 38, '11': 8}.get(c, e23)   # Real Decreto 806/2026
    v = sim[c]['v']
    prov[c] = {'nombre': cifras[c]['nombre'], 'e23': e23, 'e26': e26, 'gana23': max(v, key=v.get), 'censo': censo.get(c)}
out = {'cod': [str(c).zfill(2) for c in p['cod']], 'poly': polys, 'prov': prov}
json.dump(out, open(sys.argv[1], 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(polys), sum(v['e26'] for v in prov.values()), sum(v['e23'] for v in prov.values()))
t = [sum(v['censo'][j] for v in prov.values() if v['censo']) for j in range(4)]
print('censo 2026', t[2] + t[3], 'residentes', t[2], 'cera', t[3], 'dif', t[2] + t[3] - t[0] - t[1])
