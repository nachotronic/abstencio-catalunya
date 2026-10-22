"""Afiliaciones a la Seguridad Social por municipio y actividad en Cataluña (Idescat), a 31 de diciembre.
Escribe data/empleo/afiliacion_catalunya_municipios.csv (ver data/empleo/LEEME.md).
Uso: python3 src/afiliacion_idescat.py"""
import json
import urllib.request
from pathlib import Path
import pandas as pd

SALIDA = Path(__file__).resolve().parent.parent / 'data' / 'empleo' / 'afiliacion_catalunya_municipios.csv'
API = 'https://api.idescat.cat/taules/v2/{}/mun'
LOTE = 3000   # el API rechaza las peticiones de muchos datos: se pide por lotes de municipios
# (ruta de la tabla, años, enfoque, nivel de actividad)
TABLAS = [('afi/8598/8709', range(2012, 2026), 'residencia', 'sector'),     # todos los municipios
          ('afi/13338/19722', range(2022, 2026), 'residencia', 'seccion'),  # municipios de 5.000 hab. o más
          ('afic/14987/15881', range(2020, 2026), 'trabajo', 'seccion')]    # ídem, solo régimen general


def jsonstat(d):
    """Pasa un dataset JSON-stat 2.0 a tabla larga."""
    ids, size = d['id'], d['size']
    cats = [list(d['dimension'][i]['category']['index']) if isinstance(d['dimension'][i]['category'].get('index'), list)
            else sorted(d['dimension'][i]['category']['index'], key=d['dimension'][i]['category']['index'].get)
            for i in ids]
    valores = d['value']
    if isinstance(valores, dict):
        valores = [valores.get(str(k)) for k in range(int(pd.Series(size).prod()))]
    idx = pd.MultiIndex.from_product(cats, names=ids)
    return pd.DataFrame({'valor': valores}, index=idx).reset_index()


def pedir(url):
    with urllib.request.urlopen(url, timeout=300) as r:
        return json.load(r)


def leer(ruta, anyos):
    meta = pedir(API.format(ruta) + '?lang=es')
    muns = [m for m in meta['dimension']['MUN']['category']['index'] if m not in ('TOTAL', '999999')]
    meses = [f'{a}M12' for a in anyos]
    n = LOTE // (len(meses) * meta['size'][meta['id'].index('MUN') + 1])
    partes = []
    for i in range(0, len(muns), n):
        url = f"{API.format(ruta)}/data?lang=es&MONTH={','.join(meses)}&MUN={','.join(muns[i:i + n])}"
        partes.append(jsonstat(pedir(url)))
    return pd.concat(partes)


if __name__ == '__main__':
    partes = []
    for ruta, anyos, enfoque, nivel in TABLAS:
        d = leer(ruta, anyos)
        act = next(c for c in d.columns if c.startswith(('BRANCHES', 'SEC_ACTIV')))
        d = d.rename(columns={act: 'actividad', 'MUN': 'mun_idescat'})
        d = d.assign(anyo=d['MONTH'].str[:4].astype(int), enfoque=enfoque, nivel=nivel)
        partes.append(d[['mun_idescat', 'anyo', 'enfoque', 'nivel', 'actividad', 'valor']])
        print(ruta, len(d), 'nulos', d['valor'].isna().sum())
    t = pd.concat(partes)
    t['actividad'] = t['actividad'].str.lower()
    t = (t.pivot_table(index=['mun_idescat', 'anyo', 'enfoque', 'nivel'], columns='actividad', values='valor', aggfunc='first')
         .reset_index())
    t.insert(0, 'mun_code', t['mun_idescat'].str[:5])   # el código Idescat de 6 cifras lleva un dígito de control
    t = t.drop(columns='mun_idescat').sort_values(['enfoque', 'nivel', 'anyo', 'mun_code'])
    letras = sorted(c for c in t.columns if len(c) == 1)
    t = t[['mun_code', 'anyo', 'enfoque', 'nivel', *letras, 'b-e', 'g-u', 'total']]
    t.columns.name = None
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(SALIDA, index=False, float_format='%.0f')
    print(len(t), 'filas'); print(t.groupby(['enfoque', 'nivel', 'anyo'])['total'].agg(['count', 'sum']).to_string())
