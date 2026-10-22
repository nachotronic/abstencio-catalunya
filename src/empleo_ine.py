"""Población ocupada por sector de actividad, por municipio y por sección censal (INE, Censo anual
de población 2021-2023, residentes de 16 y más años). Escribe data/empleo/ (ver LEEME.md allí).
Uso: python3 src/empleo_ine.py [carpeta]   (descarga las tablas a la carpeta si no están ya)"""
import sys
import urllib.request
from pathlib import Path
import pandas as pd

SALIDA = Path(__file__).resolve().parent.parent / 'data' / 'empleo'
URL = 'https://www.ine.es/jaxiT3/files/t/csv_bdsc/{}.csv'
TABLAS = {'secciones': 70005,      # todas las secciones y municipios, 4 sectores
          'mun_500': 69992,        # municipios de 500 hab. o más, secciones A-U de la CNAE-2009
          'situacion': 70006,      # todas las secciones y municipios, cuenta propia / ajena
          'lugar_trabajo': 69987}  # capitales y principales ciudades, por lugar de trabajo

SECTORES = {'Total CNAE': 'ocupados', 'Agricultura, ganadería y pesca': 'agricultura',
            'Industria': 'industria', 'Construcción': 'construccion', 'Servicios': 'servicios',
            'No consta': 'no_consta'}
LUGAR = {'Total': 'ocupados', 'Mismo municipio al de residencia': 'mismo_municipio',
         'Distinto municipio de la misma provincia': 'otro_municipio_provincia',
         'Distinta provincia de la misma comunidad autónoma': 'otra_provincia_ccaa',
         'Otra comunidad autónoma': 'otra_ccaa',
         'Trabaja pero no hay información sobre el lugar de trabajo': 'lugar_no_consta'}


def leer(carpeta, t):
    f = carpeta / f'{t}.csv'
    if not f.exists():
        print('descargando', URL.format(t))
        urllib.request.urlretrieve(URL.format(t), f)
    d = pd.read_csv(f, sep=';', dtype=str, encoding='utf-8-sig')
    d = d[d['Sexo'] == 'Total'] if 'Sexo' in d else d
    # «.» = dato protegido por secreto estadístico (municipios de menos de 50 habitantes y sus secciones)
    d['Total'] = pd.to_numeric(d['Total'].str.replace('.', '', regex=False), errors='coerce')
    d['anyo'] = d['Periodo'].astype(int)
    return d


def ancho(d, clave, col, nombres):
    d = d.assign(v=d[col].map(nombres))
    t = d.pivot_table(index=[clave, 'anyo'], columns='v', values='Total', aggfunc='first')
    return t[[c for c in nombres.values() if c in t]].reset_index()


def cuenta_propia(d, clave):
    """Ocupados por cuenta propia (autónomos, empleadores, miembros de cooperativas…), por sección o municipio."""
    d = d[d['Situación profesional'] == 'Trabajador por cuenta propia']
    d = d[d['Secciones'].notna()] if clave == 'seccion' else d[d['Municipios'].notna() & d['Secciones'].isna()]
    d = d.assign(**{clave: (d['Secciones'].str[:10] if clave == 'seccion' else d['Municipios'].str[:5])})
    return d[[clave, 'anyo', 'Total']].rename(columns={'Total': 'cuenta_propia'})


def secciones(d):
    s = d[d['Secciones'].notna()].assign(seccion=lambda x: x['Secciones'].str[:10])
    t = ancho(s, 'seccion', 'Actividad económica', SECTORES)
    t.insert(1, 'mun_code', t['seccion'].str[:5])
    return t.dropna(subset=['ocupados']).sort_values(['anyo', 'seccion'])


def municipios(d, a_u):
    m = d[d['Municipios'].notna() & d['Secciones'].isna()].assign(mun_code=lambda x: x['Municipios'].str[:5])
    t = ancho(m, 'mun_code', 'Actividad económica', SECTORES)
    t.insert(1, 'municipio', t['mun_code'].map(m.drop_duplicates('mun_code').set_index('mun_code')['Municipios'].str[6:]))
    # secciones A-U de la CNAE (solo municipios de 500 habitantes o más)
    col = 'Municipios de 500 habitantes o más'
    a_u = a_u[a_u['Actividad económica'].str.match(r'^[A-U] ')].assign(
        mun_code=lambda x: x[col].str[:5], letra=lambda x: 'cnae_' + x['Actividad económica'].str[0])
    letras = a_u.pivot_table(index=['mun_code', 'anyo'], columns='letra', values='Total', aggfunc='first').reset_index()
    return t.merge(letras, on=['mun_code', 'anyo'], how='left').sort_values(['anyo', 'mun_code'])


def lugar_trabajo(d):
    col = 'Capitales de provincia y principales ciudades'
    d = d[(d['Actividad económica'] == 'Total CNAE') & (d['Situación profesional'] == 'Total')]
    d = d.assign(mun_code=d[col].str[:5])
    t = ancho(d, 'mun_code', 'Lugar trabajo', LUGAR)
    t.insert(1, 'municipio', t['mun_code'].map(d.drop_duplicates('mun_code').set_index('mun_code')[col].str[6:]))
    return t.sort_values(['anyo', 'mun_code'])


if __name__ == '__main__':
    carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    carpeta.mkdir(parents=True, exist_ok=True)
    SALIDA.mkdir(parents=True, exist_ok=True)
    base = leer(carpeta, TABLAS['secciones'])
    sit = leer(carpeta, TABLAS['situacion'])
    s = secciones(base).merge(cuenta_propia(sit, 'seccion'), on=['seccion', 'anyo'], how='left')
    s.to_csv(SALIDA / 'empleo_sector_secciones.csv.gz', index=False, float_format='%.0f')
    m = municipios(base, leer(carpeta, TABLAS['mun_500']))
    m = m.merge(cuenta_propia(sit, 'mun_code'), on=['mun_code', 'anyo'], how='left')
    m = m[[*m.columns[:9], 'cuenta_propia', *[c for c in m.columns[9:] if c != 'cuenta_propia']]]
    m.to_csv(SALIDA / 'empleo_sector_municipios.csv', index=False, float_format='%.0f')
    lt = lugar_trabajo(leer(carpeta, TABLAS['lugar_trabajo']))
    lt.to_csv(SALIDA / 'lugar_trabajo_ciudades.csv', index=False, float_format='%.0f')
    for y in sorted(s['anyo'].unique()):
        print(y, 'secciones', (s['anyo'] == y).sum(), 'ocupados', int(s.loc[s['anyo'] == y, 'ocupados'].sum()),
              '| municipios con dato', m.loc[m['anyo'] == y, 'ocupados'].notna().sum(),
              'con A-U', m.loc[m['anyo'] == y, 'cnae_A'].notna().sum())
    print('ciudades lugar de trabajo', lt['mun_code'].nunique())
