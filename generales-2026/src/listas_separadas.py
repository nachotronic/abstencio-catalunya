"""Votos de las listas que la familia SUMAR junta y que en 2015 y en noviembre de 2019 fueron por separado.

La familia «Sumar / Podemos / IU» (partidos.py) agrupa a Podemos, IU, Sumar y sus coaliciones para seguir el
espacio a lo largo del tiempo. Pero en dos generales ese espacio fue en dos listas:
  - 20D 2015: Podemos (y sus confluencias: En Comú Podem, Compromís-Podemos, En Marea) e IU-Unidad Popular.
  - 10N 2019: Unidas Podemos (y En Comú Podem) y Más País (Más País-Equo, Més Compromís...).
Sumadas, la familia puede «ganar» donde ninguna de las dos listas ganó. Este script guarda, por sección y
elección, los votos de la segunda lista (IU-UP en 2015, Más País en 2019), para que el ganador se calcule con
cada lista por separado (src/territorios_datos.py).

Fuente: resultados por mesa del Ministerio del Interior, vía dadosdelaplace/pollspaindata, como construir.py.
Uso:  python3 generales-2026/src/listas_separadas.py
Salida: generales-2026/descargas/listas_separadas.csv  (tract_code, eleccion, sumar_b)
"""
import os, re, subprocess, sys
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from partidos import familia  # noqa: E402

CACHE = os.environ.get('GENERALES_CACHE', os.path.expanduser('~/.cache/generales'))
E = os.path.join(CACHE, 'pollspaindata', 'inst', 'extdata')
SALIDA = os.path.join(AQUI, '..', 'descargas', 'listas_separadas.csv')
# la segunda lista de la familia en cada elección (por nombre o siglas de la candidatura)
SEGUNDA = {'2015_12': r'IZQUIERDA UNIDA|ESQUERRA UNIDA|UNIDAD POPULAR|UNITAT POPULAR|^IU|^EUPV|^UPEC',
           '2019_11': r'M[AÁ]S PA[IÍ]S|M[EÉ]S COMPROM|^M PA[IÍ]S'}


def main():
    if not os.path.isdir(E):
        os.makedirs(CACHE, exist_ok=True)
        subprocess.run(['git', 'clone', '-q', '--depth', '1', 'https://github.com/dadosdelaplace/pollspaindata.git',
                        os.path.join(CACHE, 'pollspaindata')], check=True)
    filas = []
    for y, patron in SEGUNDA.items():
        c = pd.read_parquet(f'{E}/raw_candidacies_congress_{y}.parquet')
        c['fam'] = [familia(a, n) for a, n in zip(c.abbrev_candidacies, c.name_candidacies)]
        c['b'] = (c.fam == 'SUMAR') & (c.abbrev_candidacies.str.contains(patron, regex=True, na=False)
                                        | c.name_candidacies.str.contains(patron, regex=True, na=False))
        print(y, 'segunda lista:', '; '.join(sorted(set(c[c.b].name_candidacies.str.strip('" ')))))
        v = pd.read_parquet(f'{E}/raw_candidacies_poll_congress_{y}.parquet')
        v = v[v.cod_INE_mun != '999']          # CERA fuera, como en construir.py
        v['tract_code'] = v.cod_INE_prov + v.cod_INE_mun + v.cod_mun_district + v.cod_sec
        v = v.merge(c[['id_candidacies', 'b']], on='id_candidacies', how='left')
        s = v[v.b == True].groupby('tract_code').ballots.sum().rename('sumar_b').reset_index()  # noqa: E712
        s['eleccion'] = y
        filas.append(s[s.sumar_b > 0])
        print(y, f'{s.sumar_b.sum():,.0f} votos en {len(s)} secciones')
    r = pd.concat(filas)[['tract_code', 'eleccion', 'sumar_b']]
    r['sumar_b'] = r.sumar_b.astype(int)
    r.to_csv(SALIDA, index=False)
    print('Escrito', os.path.relpath(SALIDA))


if __name__ == '__main__':
    main()
