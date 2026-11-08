"""Avances de participación de las generales (14.00 y 18.00) por municipio, de 2004 a 2023.

Interior publica dos avances durante la jornada: cuántos electores han votado en las mesas a las 14.00 y a las 18.00.
Los ficheros por mesa de Interior traen esas dos cifras (campos «votantes primer avance» y «segundo avance»),
que pollspaindata (github.com/dadosdelaplace/pollspaindata, columnas ballots_1 y ballots_2) recoge ya leídos.

Salida: data/censo/avances_participacion.csv, una fila por municipio y elección, con el censo (residentes, sin CERA),
los votantes de cada avance y los votantes finales en las mesas (blancos + nulos + candidaturas). Los avances solo
cuentan el voto en persona: el voto por correo se suma al final, así que la distancia entre las 18.00 y el cierre
crece cuando hay mucho voto por correo (julio de 2023).

Uso:  python3 src/avances_participacion.py   (clona pollspaindata en ~/.cache/generales si no está, como construir.py)
"""
import os, pathlib, subprocess
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = os.environ.get('GENERALES_CACHE', os.path.expanduser('~/.cache/generales'))
ELECCIONES = ['2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
SALIDA = ROOT / 'data' / 'censo' / 'avances_participacion.csv'


def fuente():
    d = os.path.join(CACHE, 'pollspaindata')
    if not os.path.isdir(d):
        os.makedirs(CACHE, exist_ok=True)
        subprocess.run(['git', 'clone', '-q', '--depth', '1', 'https://github.com/dadosdelaplace/pollspaindata.git', d], check=True)
    return os.path.join(d, 'inst', 'extdata')


def main():
    E = fuente()
    filas = []
    for y in ELECCIONES:
        m = pd.read_parquet(os.path.join(E, f'raw_poll_stations_congress_{y}.parquet'))
        m = m[m.cod_INE_mun != '999']          # CERA fuera, como en el resto del sitio
        m = m.assign(mun_code=m.cod_INE_prov + m.cod_INE_mun, votantes=m.blank_ballots + m.invalid_ballots + m.party_ballots)
        g = m.groupby('mun_code').agg(censo=('census_INE', 'sum'), a14=('ballots_1', 'sum'), a18=('ballots_2', 'sum'),
                                      votantes=('votantes', 'sum'), mesas=('census_INE', 'size')).reset_index()
        g.insert(1, 'eleccion', y)
        filas.append(g)
        print(y, f'{g.a14.sum() / g.censo.sum():.2%} a las 14.00, {g.a18.sum() / g.censo.sum():.2%} a las 18.00, '
                 f'{g.votantes.sum() / g.censo.sum():.2%} al cierre ({len(g)} municipios)')
    d = pd.concat(filas)
    for c in ('censo', 'a14', 'a18', 'votantes', 'mesas'):
        d[c] = d[c].astype(int)
    d.to_csv(SALIDA, index=False)
    print(SALIDA, len(d), 'filas')


if __name__ == '__main__':
    main()
