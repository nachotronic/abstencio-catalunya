"""Titulares de las listas al Congreso del 29N por provincia y siglas, en su orden, para el directo: con los escaños
provisionales de Interior, los primeros N de cada lista son los que salen (Interior no da los nombres de los diputados).
Lee listas-electorales-29n/candidatos-29n.csv (BOE) y candidatos.json (para el código de provincia).
Escribe generales-2026/data/candidatos-congreso-29n.json: {pp: {siglas: [nombre, ...]}}.
"""
import collections, csv, json, pathlib

RAIZ = pathlib.Path(__file__).resolve().parents[2]
L = RAIZ / 'listas-electorales-29n'
cod = {}
for r in json.loads((L / 'candidatos.json').read_text(encoding='utf-8')):
    cod[(r[0], r[4])] = r[1]
filas = [r for r in csv.DictReader(open(L / 'candidatos-29n.csv', encoding='utf-8')) if r['camara'] == 'congreso' and r['tipo'] == 'titular']
prov = {}
for r in filas:
    c = cod.get((r['nombre'], int(r['puesto'])))
    if c: prov.setdefault(r['provincia'], collections.Counter())[c] += 1
prov = {p: c.most_common(1)[0][0] for p, c in prov.items()}
out = collections.defaultdict(lambda: collections.defaultdict(list))
for r in sorted(filas, key=lambda r: int(r['puesto'])):
    out[prov[r['provincia']]][r['siglas']].append(r['nombre'])
assert len(out) == 52, f'{len(out)} provincias'
(RAIZ / 'generales-2026/data/candidatos-congreso-29n.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':'), sort_keys=True), encoding='utf-8')
print(len(out), 'provincias,', sum(len(v) for v in out.values()), 'listas')
