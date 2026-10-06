"""Participación por sección en las doce elecciones de 2015 a 2024, sobre las secciones de 2023.

Fuente: Transparència Catalunya, dataset irrv-2mfc (nivel «SE», sin residentes en el extranjero).
Una sección de otro año se asigna a la de 2023 con el mismo código solo si su censo está entre 2/3 y 1,5 veces
el del Congreso de 2023 (si se partió o se juntó con otra, el código coincide pero el territorio no).

Uso: python3 src/evolucion.py DIR_CSV tracts.json   (DIR_CSV con sec_<elección>.csv)
Escribe data/evolucion_secciones.csv y src/evo.json (lo que se incrusta en la pieza).
"""
import sys, json, pandas as pd

D, TRACTS = sys.argv[1:3]
EL = ['M20151', 'A20151', 'G20151', 'G20161', 'A20171', 'G20191', 'M20191', 'G20192', 'A20211', 'M20231', 'G20231', 'A20241']
b = pd.read_csv('data/catalunya_secciones_2023.csv', dtype={'tract_code': str}).set_index('tract_code')


def load(c):
    x = pd.read_csv(f'{D}/sec_{c}.csv', dtype={'territori_codi': str})
    x = x[~x.territori_nom.astype(str).str.startswith('Residents')]
    x['tract'] = (x.territori_codi.str.zfill(5) + x.districte.astype(int).astype(str).str.zfill(2)
                  + x.seccio.astype(int).astype(str).str.zfill(3))
    return x.groupby('tract')[['cens_electoral', 'votants']].sum()


ref = load('G20231').cens_electoral
part, cens, cat = {}, {}, {}
for c in EL:
    x = load(c)
    cat[c] = round(x.votants.sum() / x.cens_electoral.sum(), 4)
    x = x[x.index.isin(b.index)]
    r = x.cens_electoral / ref.reindex(x.index)
    x = x[(r > 2 / 3) & (r < 1.5)]
    part[c] = (x.votants / x.cens_electoral).round(4)
    cens[c] = x.cens_electoral
T = pd.DataFrame(part).reindex(b.index)
C = pd.DataFrame(cens).reindex(b.index)
T.to_csv('data/evolucion_secciones.csv')

# participación por quintil de renta de la sección (ponderada por censo)
q = pd.qcut(b.net_income_equiv, 5, labels=False)
quint = []
for c in EL:
    g = pd.DataFrame({'v': T[c] * C[c], 'w': C[c], 'q': q}).dropna().groupby('q').sum()
    quint.append([round(v, 4) for v in (g.v / g.w)])

tracts = json.load(open(TRACTS))
t = [[None if pd.isna(v) else int(round(v * 1000)) for v in T.loc[k]] if k in T.index else [None] * len(EL) for k in tracts]
json.dump({'el': EL, 'cat': [cat[c] for c in EL], 'q': quint, 't': t}, open('src/evo.json', 'w'), separators=(',', ':'))
print('secciones con las 12 elecciones:', int(T.notna().all(axis=1).sum()), 'de', len(T))
print('Cataluña:', cat)
