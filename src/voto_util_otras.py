"""Desglosa la fila «Otras» de agregados.json (2023_07, PR) en sus candidaturas, para las páginas de voto útil.

agregados.json guarda las 10 listas más votadas de cada provincia y suma el resto en «Otras». Este script lee los votos por mesa
de Interior (formato de pollspaindata, https://github.com/ropenspain/pollspaindata, carpeta inst/extdata; con el voto CERA,
municipio 999) y escribe generales-2026/data/voto_util_otras_2023.csv con cada candidatura que agregados.json no nombra,
comprobando que en cada provincia suman exactamente lo que dice su fila «Otras».
Uso, desde la raíz: python3 src/voto_util_otras.py <carpeta extdata de pollspaindata>
"""
import csv
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
X = Path(sys.argv[1])
A = json.loads((ROOT / 'generales-2026/data/agregados.json').read_text(encoding='utf-8'))['2023_07']['PR']
v = pd.read_parquet(X / 'raw_candidacies_poll_congress_2023_07.parquet')
c = pd.read_parquet(X / 'raw_candidacies_congress_2023_07.parquet')
ab = dict(zip(c.id_candidacies, c.abbrev_candidacies))
filas = []
for p, x in sorted(A.items()):
    otras = [r for r in x['c'] if r[0] == 'Otras']
    if not otras:
        continue
    assert len(otras) == 1, p
    nombradas = {r[0] for r in x['c'] if r[0] != 'Otras'}
    g = v[v.cod_INE_prov == p].groupby('id_candidacies').ballots.sum()
    todas = {}
    for k, n in g.items():
        if n > 0:
            todas[ab[k]] = todas.get(ab[k], 0) + int(n)
    assert nombradas <= set(todas), (p, nombradas - set(todas))
    assert all(todas[s] == r[1] for r in x['c'] if r[0] != 'Otras' for s in [r[0]]), p
    resto = sorted(((s, n) for s, n in todas.items() if s not in nombradas), key=lambda t: -t[1])
    assert sum(n for _, n in resto) == otras[0][1], (p, sum(n for _, n in resto), otras[0][1])
    filas += [(p, s, n) for s, n in resto]
with open(ROOT / 'generales-2026/data/voto_util_otras_2023.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['prov', 'siglas', 'votos'])
    w.writerows(filas)
print(len(filas), 'candidaturas en', len({p for p, _, _ in filas}), 'provincias')
