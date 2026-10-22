"""Malla estadística de 250 m del IECA (Andalucía, datos de 2024) agregada a secciones censales de 2023.
Escribe data/andalucia/malla_ieca_secciones.csv (ver data/andalucia/LEEME.md).
Uso: python3 src/malla_ieca.py <seccionado_2023.zip del INE> [carpeta]
(descarga la malla municipio a municipio a la carpeta si no está ya)"""
import json
import sys
import time
import urllib.request
import zipfile
from pathlib import Path
import geopandas as gpd
import pandas as pd

SALIDA = Path(__file__).resolve().parent.parent / 'data' / 'andalucia' / 'malla_ieca_secciones.csv'
WFS = ('https://www.juntadeandalucia.es/institutodeestadisticaycartografia/geoserver-ieca/grid/wfs?service=WFS'
       '&version=2.0.0&request=GetFeature&typeNames=grid:gridp_250&outputFormat=application/json'
       '&CQL_FILTER=cmun=%27{}%27')
PROVINCIAS = ['04', '11', '14', '18', '21', '23', '29', '41']
# recuentos que se suman tal cual
CONTEOS = ['pob_tot', 'pob_m', 'pob_h', 'edad0015', 'edad1664', 'edad65_',
           'esp', 'ue15', 'mag', 'ams', 'otr', 'muni', 'mund', 'provd', 'ccaad', 'paisd',
           'tr_05', 'tr0610', 'tr1115', 'tr16_', 'ne0', 'ne1', 'ne2', 'ne3', 'ne4',
           'afil_ss', 'afil_ss_m', 'afil_ss_h', 'afil_ss_a', 'afil_ss_p',
           'penc', 'penc_m', 'penc_h', 'pencjub', 'pencviu', 'pencjyv', 'pencinc', 'pencotr',
           'demp', 'demp_m', 'demp_h', 'demp_pr', 'demp_pr_m', 'demp_pr_h']
# importes medios de pensión: media ponderada por el número de pensionistas de cada tipo
MEDIAS = {'pencjub_mi': 'pencjub', 'pencviu_mi': 'pencviu', 'pencjyv_mi': 'pencjyv',
          'pencinc_mi': 'pencinc', 'pencotr_mi': 'pencotr'}


def secciones(zip_ine):
    with zipfile.ZipFile(zip_ine) as z:
        shp = next(n for n in z.namelist() if n.endswith('.shp'))
    s = gpd.read_file(f'zip://{zip_ine}!{shp}')
    s = s[s['CPRO'].isin(PROVINCIAS)][['CUSEC', 'CUMUN', 'geometry']]
    return s.to_crs(25830)


def bajar(carpeta, mun):
    f = carpeta / f'{mun}.json'
    for intento in range(4):
        if f.exists() and f.stat().st_size > 0:
            return json.loads(f.read_text())
        try:
            urllib.request.urlretrieve(WFS.format(mun), f)
        except OSError:
            f.unlink(missing_ok=True)
            time.sleep(2 ** intento)
    raise RuntimeError(f'no se pudo descargar la malla de {mun}')


if __name__ == '__main__':
    zip_ine = Path(sys.argv[1])
    carpeta = Path(sys.argv[2] if len(sys.argv) > 2 else 'malla_ieca')
    carpeta.mkdir(parents=True, exist_ok=True)
    sec = secciones(zip_ine)
    celdas = []
    for mun in sorted(sec['CUMUN'].unique()):
        d = bajar(carpeta, mun)
        if d['features']:
            celdas.append(gpd.GeoDataFrame.from_features(d['features'], crs=25830))
    c = pd.concat(celdas, ignore_index=True)
    c = gpd.GeoDataFrame(c, geometry='geometry', crs=25830)
    # cada celda se reparte entre las secciones de su municipio según la superficie que comparte con
    # ellas (en ciudades muchas secciones son más pequeñas que una celda); la parte de celda que cae
    # fuera de su municipio se reparte entre el resto, y si no toca ninguna sección de su municipio
    # va entera a la más cercana
    c['celda'] = range(len(c))
    i = gpd.overlay(c[['celda', 'cmun', 'geometry']], sec, how='intersection', keep_geom_type=True)
    i = i[i['cmun'] == i['CUMUN']]
    i['peso'] = i.geometry.area
    i['peso'] = i['peso'] / i.groupby('celda')['peso'].transform('sum')
    sueltas = c[~c['celda'].isin(i['celda'])]
    if len(sueltas):
        cerca = gpd.sjoin_nearest(sueltas[['celda', 'geometry']], sec, how='left')
        cerca = cerca[~cerca['celda'].duplicated()].assign(peso=1.0)
        i = pd.concat([i[['celda', 'CUSEC', 'peso']], cerca[['celda', 'CUSEC', 'peso']]])
    print('celdas repartidas', i['celda'].nunique(), 'de', len(c), '; sin sección de su municipio', len(sueltas))
    for m, n in MEDIAS.items():
        c[m + '_x'] = c[m].fillna(0) * c[n].fillna(0)
    v = i[['celda', 'CUSEC', 'peso']].merge(c.drop(columns='geometry'), on='celda')
    cols = CONTEOS + [m + '_x' for m in MEDIAS]
    v[cols] = v[cols].fillna(0).mul(v['peso'], axis=0)
    v['seccion'] = v['CUSEC']
    g = v.groupby('seccion')
    t = g[CONTEOS].sum().round(1)
    for m, n in MEDIAS.items():
        t[m] = (g[m + '_x'].sum() / t[n]).where(t[n] > 0).round(1)
    t.insert(0, 'celdas', g['peso'].sum().round(2))
    t = t.reindex(sorted(sec['CUSEC'])).reset_index().rename(columns={'index': 'seccion', 'CUSEC': 'seccion'})
    t.insert(1, 'mun_code', t['seccion'].str[:5])
    t['celdas'] = t['celdas'].fillna(0)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(SALIDA, index=False, float_format='%.10g')
    print(len(c), 'celdas;', len(t), 'secciones;', (t['celdas'] == 0).sum(), 'sin celdas;',
          'población', round(t['pob_tot'].sum()), 'afiliados', round(t['afil_ss'].sum()))
