"""Ocupación, nivel de estudios y país de nacimiento por municipio y por sección censal (INE, Censo
anual de población). Escribe data/censo/censo_secciones.csv.gz y data/censo/censo_municipios.csv
(ver data/censo/LEEME.md).
Uso: python3 src/censo_secciones.py [carpeta]   (descarga las tablas a la carpeta si no están ya)"""
import sys
import unicodedata
import urllib.request
from pathlib import Path
import pandas as pd

SALIDA = Path(__file__).resolve().parent.parent / 'data' / 'censo'
URL = 'https://www.ine.es/jaxiT3/files/t/csv_bdsc/{}.csv'

OCUPACION = {'Total': 'ocupados',
             'Directores/gerentes y profesionales/técnicos de nivel medio o alto': 'ocup_alta',
             'Trabajadores cualificados y oficiales/operarios de nivel bajo': 'ocup_media',
             'Ocupaciones elementales': 'ocup_elemental',
             'No consta': 'ocup_no_consta'}
ESTUDIOS = {'Total': 'pob15',
            'Educación primaria e inferior': 'est_primaria',
            'Primera etapa de Educación Secundaria y similar': 'est_secundaria1',
            'Segunda etapa de Educación Secundaria y Educación Postsecundaria no Superior': 'est_secundaria2',
            'Educación superior': 'est_superior'}


def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return 'nac_' + '_'.join(s.replace(',', ' ').split())


# tabla: (columna de categorías, nombres de columna; None = generarlos con slug)
TABLAS = {70004: ('Ocupación', OCUPACION),
          66592: ('Nivel de formación alcanzado', ESTUDIOS),
          65035: ('País de nacimiento', None)}


def leer(carpeta, t):
    f = carpeta / f'{t}.csv'
    if not f.exists():
        print('descargando', URL.format(t))
        urllib.request.urlretrieve(URL.format(t), f)
    col, nombres = TABLAS[t]
    trozos = []
    for d in pd.read_csv(f, sep=';', dtype=str, encoding='utf-8-sig', chunksize=2_000_000,
                         usecols=['Municipios', 'Secciones', 'Sexo', col, 'Periodo', 'Total']):
        trozos.append(d[(d['Sexo'] == 'Total') & d['Municipios'].notna()])
    d = pd.concat(trozos)
    # «.» = dato protegido por secreto estadístico (municipios de menos de 50 habitantes y sus secciones)
    d['Total'] = pd.to_numeric(d['Total'].str.replace('.', '', regex=False), errors='coerce')
    d['anyo'] = d['Periodo'].astype(int)
    if nombres is None:
        nombres = {c: ('poblacion' if c == 'Total' else slug(c)) for c in d[col].unique()}
        nombres['España'] = 'nac_espana'
    return d.assign(v=d[col].map(nombres)), list(dict.fromkeys(nombres.values()))


def ancho(d, orden):
    sec = d[d['Secciones'].notna()].assign(clave=lambda x: x['Secciones'].str[:10])
    mun = d[d['Secciones'].isna()].assign(clave=lambda x: x['Municipios'].str[:5])
    out = []
    for x in (sec, mun):
        t = x.pivot_table(index=['clave', 'anyo'], columns='v', values='Total', aggfunc='first')
        out.append(t[[c for c in orden if c in t]])
    return out


def main(carpeta):
    carpeta.mkdir(parents=True, exist_ok=True)
    secs, muns, nombres = [], [], None
    for t in TABLAS:
        d, orden = leer(carpeta, t)
        if t == 65035:
            mm = d['Municipios'].drop_duplicates()
            nombres = pd.Series(mm.str[6:].values, index=mm.str[:5].values)
        s, m = ancho(d, orden)
        secs.append(s)
        muns.append(m)
        print(t, 'secciones', len(s), 'municipios', len(m))
    s = pd.concat(secs, axis=1).reset_index().rename(columns={'clave': 'seccion'})
    s.insert(1, 'mun_code', s['seccion'].str[:5])
    s = s.dropna(subset=[c for c in s.columns[3:]], how='all').sort_values(['anyo', 'seccion'])
    m = pd.concat(muns, axis=1).reset_index().rename(columns={'clave': 'mun_code'})
    m.insert(1, 'municipio', m['mun_code'].map(nombres))
    m = m.sort_values(['anyo', 'mun_code'])
    SALIDA.mkdir(parents=True, exist_ok=True)
    s.to_csv(SALIDA / 'censo_secciones.csv.gz', index=False, float_format='%.0f')
    m.to_csv(SALIDA / 'censo_municipios.csv', index=False, float_format='%.0f')
    print('escrito', len(s), 'filas de sección y', len(m), 'de municipio')


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/censo_ine'))
