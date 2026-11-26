"""Prepara los datos del voto exterior (CERA) para la pieza voto_exterior_loreg.py.

Lee los resultados por mesa del Congreso del Ministerio del Interior en el formato de pollspaindata
(https://github.com/ropenspain/pollspaindata, carpeta inst/extdata), donde el voto de los residentes en el extranjero
de cada provincia es el municipio 999, y escribe:
- datos/voto_exterior_cera_1986_2023.csv: censo, votantes y participación del CERA en cada elección al Congreso.
- datos/voto_exterior_cera_provincias_2023.csv: por provincia en 2023, censo y votantes del CERA, votos válidos del CERA,
  el partido del último escaño, el siguiente aspirante, los votos nuevos que le faltaban a este para quitárselo y si el
  voto exterior cambió el reparto.
Uso, desde la raíz: python3 actualidad/src/resumenes/voto_exterior_preparar.py <carpeta extdata de pollspaindata>
"""
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / 'src'))
import voto_util as V  # noqa: E402

X = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent / 'datos'
COLS = ['census_counting', 'party_ballots', 'blank_ballots', 'invalid_ballots']

filas = []
for f in sorted(X.glob('raw_poll_stations_congress_*.parquet')):
    eleccion = f.stem.split('_', 3)[3]
    m = pd.read_parquet(f, columns=['cod_INE_mun'] + COLS)
    c = m[m.cod_INE_mun == '999']
    if c.empty:
        continue
    votantes = int(c.party_ballots.sum() + c.blank_ballots.sum() + c.invalid_ballots.sum())
    censo = int(c.census_counting.sum())
    filas.append(dict(eleccion=eleccion, censo_cera=censo, votantes_cera=votantes, participacion=round(votantes / censo * 100, 3)))
S = pd.DataFrame(filas)
S.to_csv(OUT / 'voto_exterior_cera_1986_2023.csv', index=False)
print(S.to_string())

m = pd.read_parquet(X / 'raw_poll_stations_congress_2023_07.parquet')
v = pd.read_parquet(X / 'raw_candidacies_poll_congress_2023_07.parquet')
c = pd.read_parquet(X / 'raw_candidacies_congress_2023_07.parquet')
ab = dict(zip(c.id_candidacies, c.abbrev_candidacies))
m['cera'] = m.cod_INE_mun == '999'
v['cera'] = v.cod_INE_mun == '999'
filas = []
for p, g in v.groupby('cod_INE_prov'):
    todo = {ab[k]: int(x) for k, x in g.groupby('id_candidacies').ballots.sum().items() if x > 0}
    sin = {ab[k]: int(x) for k, x in g[~g.cera].groupby('id_candidacies').ballots.sum().items() if x > 0}
    mp = m[m.cod_INE_prov == p]
    bl_todo, bl_sin = int(mp.blank_ballots.sum()), int(mp[~mp.cera].blank_ballots.sum())
    e = V.ESC_2023[p]
    ea, qa = V.reparto(todo, sum(todo.values()) + bl_todo, e)
    es, _ = V.reparto(sin, sum(sin.values()) + bl_sin, e)
    ult = qa[e - 1]
    sig = next(t for t in qa[e:] if t[2] != ult[2])
    pc = mp[mp.cera]
    cambio = '; '.join(f'{k} {es.get(k, 0)}→{ea.get(k, 0)}' for k in sorted(set(ea) | set(es)) if es.get(k, 0) != ea.get(k, 0))
    filas.append(dict(prov=p, escanos=e, censo_cera=int(pc.census_counting.sum()),
                      votantes_cera=int(pc.party_ballots.sum() + pc.blank_ballots.sum() + pc.invalid_ballots.sum()),
                      validos_cera=int(pc.party_ballots.sum() + pc.blank_ballots.sum()),
                      ultimo=ult[2], aspirante=sig[2],
                      votos_nuevos=V.votos_nuevos(todo, sum(todo.values()) + bl_todo, e, sig[2]),
                      cambio_por_cera=cambio))
P = pd.DataFrame(filas)
P.to_csv(OUT / 'voto_exterior_cera_provincias_2023.csv', index=False)
print(P[P.votos_nuevos < P.validos_cera].to_string())
print(P[P.cambio_por_cera != ''].to_string())
