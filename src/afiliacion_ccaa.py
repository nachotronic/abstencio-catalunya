"""Afiliación a la Seguridad Social (o empleo) por municipio y sector en las comunidades que la publican en
abierto, a partir de sus institutos de estadística: Madrid, Canarias, Galicia, Illes Balears, Región de Murcia,
Comunitat Valenciana y País Vasco. Junta en un fichero común, con un formato que también recoge Cataluña y
Extremadura (de afiliacion_catalunya_municipios.csv y afiliacion_extremadura_municipios.csv).
Escribe data/empleo/afiliacion_ccaa_municipios.csv (ver data/empleo/LEEME.md).
Uso: python3 src/afiliacion_ccaa.py [carpeta]   (descarga las tablas a la carpeta si no están ya)"""
import json
import re
import sys
import time
import unicodedata
import urllib.request
from io import StringIO
from pathlib import Path
import pandas as pd

DATOS = Path(__file__).resolve().parent.parent / 'data' / 'empleo'
SALIDA = DATOS / 'afiliacion_ccaa_municipios.csv'
DESDE = 2021   # primer año que se guarda: diciembre de cada año y el último mes publicado
COLUMNAS = ['mun_code', 'ccaa', 'fecha', 'enfoque', 'medida', 'afiliados', 'agricultura', 'industria',
            'construccion', 'servicios', 'sector_no_consta', 'autonomos']


def abrir(url, datos=None):
    for intento in range(5):
        try:
            req = urllib.request.Request(url, data=datos, headers={'User-Agent': 'Mozilla/5.0',
                                                                   'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.read()
        except OSError:
            if intento == 4:
                raise
            time.sleep(2 ** intento)


def bajar(carpeta, nombre, url, datos=None):
    f = carpeta / nombre
    if not f.exists():
        print('descargando', url)
        f.write_bytes(abrir(url, datos))
    return f


def px(f):
    """Lee un fichero PC-Axis y lo devuelve en formato largo (una columna por variable y `valor`)."""
    s = f.read_bytes().decode('latin-1')
    cab, datos = s.split('DATA=', 1)
    claves = {}
    for m in re.finditer(r'([A-Z-]+)(?:\("([^"]+)"\))?=((?:"[^"]*"|[^;"])*);', cab):
        claves[(m.group(1), m.group(2))] = re.findall(r'"([^"]*)"', m.group(3)) or [m.group(3).strip()]
    variables = claves[('STUB', None)] + claves[('HEADING', None)]
    niveles = [[re.sub(r'\s+', ' ', v) for v in claves[('VALUES', v)]] for v in variables]
    valores = re.findall(r'"[^"]*"|[^\s;]+', datos.split(';')[0])
    valores = pd.to_numeric(pd.Series(valores).str.strip('"'), errors='coerce')   # «....», «.» = secreto
    idx = pd.MultiIndex.from_product(niveles, names=variables)
    return pd.DataFrame({'valor': valores.values}, index=idx).reset_index()


def ancho(d, clave, nombres):
    d = d.assign(col=d[clave].map(nombres)).dropna(subset=['col'])
    t = d.pivot_table(index=['mun_code', 'fecha'], columns='col', values='valor', aggfunc='sum', min_count=1)
    return t.reset_index()


def elegir_fechas(t):
    """Diciembre (o último trimestre) de cada año desde DESDE y el último periodo publicado."""
    f = t['fecha']
    ultima = f.max()
    return t[(f.str[:4].astype(int) >= DESDE) & ((f.str[5:] == '12') | (f == ultima))]


def sin_tildes(s):
    s = unicodedata.normalize('NFKD', str(s).lower()).encode('ascii', 'ignore').decode()
    m = re.match(r'^(.*?)\s*[,(]\s*(el|la|los|las|l\'|les)\s*\)?$', s)   # «Alcázares (Los)», «Alcázares, Los»
    if m:
        s = f'{m.group(2)} {m.group(1)}'
    return re.sub(r'[^a-z0-9]', '', s)


# --- Comunidad de Madrid: datos abiertos, anuales -----------------------------------------------------
MADRID = 'https://datos.comunidad.madrid/api/3/action/package_show?id={}'
RAMAS = {'Total': 'afiliados', 'Agricultura y ganadería': 'agricultura', 'Minería, industria y energía': 'industria',
         'Construcción': 'construccion', 'Servicios de distribución y hostelería': 'servicios',
         'Servicios a empresas y financieros': 'servicios', 'Inmobiliarias': 'servicios', 'Otros servicios': 'servicios',
         'No consta': 'sector_no_consta'}


def madrid_csv(carpeta, conjunto):
    meta = json.loads(abrir(MADRID.format(conjunto)))['result']
    url = next(r['url'] for r in meta['resources'] if r['format'].upper() == 'CSV')
    d = pd.read_csv(bajar(carpeta, f'madrid_{conjunto}.csv', url), sep=';', dtype=str, encoding='latin-1')
    d = d[d['Tipo territorio'] == 'Municipios']
    # código de 4 cifras = municipio INE (3) + dígito de control
    return d.assign(mun_code='28' + d['Código territorio'].str[:3],
                    valor=pd.to_numeric(d['Valor'], errors='coerce'))


def madrid(carpeta):
    # por residencia, a 1 de enero: se fecha en diciembre del año anterior
    r = madrid_csv(carpeta, 'afiliados_por_residencia_y_rama')
    r['fecha'] = (r['Año'].astype(int) - 1).astype(str) + '-12'
    r = ancho(r, 'Rama de actividad', RAMAS).assign(enfoque='residencia')
    # por lugar de trabajo (centro de trabajo), a 31 de diciembre
    w = madrid_csv(carpeta, 'afiliados_por_ubicacion_y_rama').assign(fecha=lambda x: x['Año'] + '-12')
    w = ancho(w, 'Rama de actividad', RAMAS)
    g = madrid_csv(carpeta, 'afiliados_por_ubicacion_y_regimen').assign(fecha=lambda x: x['Año'] + '-12')
    g = ancho(g, 'Régimen', {'Régimen de autónomos': 'autonomos'})
    w = w.merge(g, on=['mun_code', 'fecha'], how='left').assign(enfoque='trabajo')
    return pd.concat([r, w]).assign(ccaa='Madrid', medida='afiliaciones')


# --- Canarias: ISTAC, API de indicadores, mensual --------------------------------------------------------
ISTAC = ('https://datos.canarias.es/api/estadisticas/indicators/v1.0/indicators/{}/data'
         '?granularity=GEOGRAPHICAL%5BMUNICIPALITIES%5D,TIME%5BMONTHLY%5D&fields=-observationsMetadata')
INDICADORES = {'AFILIACIONES': 'afiliados', 'AFILIACIONES_AGRICULTURA': 'agricultura',
               'AFILIACIONES_INDUSTRIA': 'industria', 'AFILIACIONES_CONSTRUCCION': 'construccion',
               'AFILIACIONES_SERVICIOS': 'servicios', 'AFILIACIONES_AUTONOMOS': 'autonomos'}


def canarias(carpeta):
    partes = []
    for ind, col in INDICADORES.items():
        d = json.loads(bajar(carpeta, f'istac_{ind}.json', ISTAC.format(ind)).read_bytes())
        dim = {k: list(d['dimension'][k]['representation']['index']) for k in d['format']}
        idx = pd.MultiIndex.from_product([dim[k] for k in d['format']], names=d['format'])
        t = pd.DataFrame({'valor': pd.to_numeric(pd.Series(d['observation']), errors='coerce').values}, index=idx)
        t = t.xs('ABSOLUTE', level='MEASURE').reset_index()
        partes.append(t.rename(columns={'GEOGRAPHICAL': 'mun_code', 'TIME': 'fecha', 'valor': col})
                      .set_index(['mun_code', 'fecha']))
    t = pd.concat(partes, axis=1).reset_index()
    # domicilio de la cuenta de cotización (o del autónomo): lugar de trabajo
    return t.assign(ccaa='Canarias', enfoque='trabajo', medida='afiliaciones')


# --- Galicia: IGE, API de su banco de datos, mensual ---------------------------------------------------
IGE = 'https://www.ige.gal/igebdt/igeapi/csv/datos/{}'


def ige(carpeta, tabla, col, nombres):
    d = pd.read_csv(bajar(carpeta, f'ige_{tabla}.csv', IGE.format(tabla)), dtype=str, encoding='latin-1')
    d = d[d['CodEspazo'].str.len() == 5]
    d = d.assign(mun_code=d['CodEspazo'], fecha=d['CodTempo'].str[:4] + '-' + d['CodTempo'].str[4:],
                 valor=pd.to_numeric(d['DatoN'], errors='coerce'))
    return ancho(d, col, nombres)


def galicia(carpeta):
    s = ige(carpeta, 10175, 'Sector de actividade', {'Total': 'afiliados', 'Agricultura e pesca': 'agricultura',
                                                    'Industria': 'industria', 'Construción': 'construccion',
                                                    'Servizos': 'servicios'})
    r = ige(carpeta, 4556, 'Réxime', {'Total': 'afiliados_r', 'Réxime especial de autónomos': 'autonomos'})
    t = s.merge(r, on=['mun_code', 'fecha'], how='outer')
    t['afiliados'] = t['afiliados'].fillna(t.pop('afiliados_r'))
    return t.assign(ccaa='Galicia', enfoque='residencia', medida='afiliaciones')


# --- Illes Balears: Ibestat, PC-Axis, trimestral --------------------------------------------------------
IBESTAT = 'https://intranet.caib.es/ibestat-jaxi/tabla.do?typeDownload=0&px={}'
SECTOR_IBESTAT, REGIMEN_IBESTAT = '38c77841-b363-4010-8405-e7259a3692fc', '47cb7053-619a-45d8-a3fc-638a94c51d06'


def ibestat(carpeta, nombre, px_id, col, nombres):
    d = px(bajar(carpeta, f'ibestat_{nombre}.px', IBESTAT.format(px_id)))
    mun = d['Isla y municipio de residencia'].str.extract(r'^(07\d{3}) ')[0]
    d = d.assign(mun_code=mun, fecha=d['Periodo'].str[:4] + '-' + d['Periodo'].str[-1].map(
        {'1': '03', '2': '06', '3': '09', '4': '12'})).dropna(subset=['mun_code'])
    if callable(nombres):   # secciones «(A) AGRICULTURA…»: se agrupan por la letra
        nombres = {v: nombres(v) for v in d[col].unique()}
    return ancho(d, col, nombres)


def baleares(carpeta):
    letras = {**{l: 'servicios' for l in 'GHIJKLMNOPQRSTU'}, 'A': 'agricultura', 'B': 'industria', 'C': 'industria',
              'D': 'industria', 'E': 'industria', 'F': 'construccion'}
    s = ibestat(carpeta, 'sector', SECTOR_IBESTAT, 'Actividad económica',
                lambda v: {'TOTAL': 'afiliados', 'SIN DESCRIPCIÓN': 'sector_no_consta'}.get(v, letras.get(v[1])))
    r = ibestat(carpeta, 'regimen', REGIMEN_IBESTAT, 'Régimen de afiliación',
                {'TOTAL': 'afiliados_r', 'Régimen Especial de Autónomos': 'autonomos'})
    t = s.merge(r, on=['mun_code', 'fecha'], how='outer')
    t['afiliados'] = t['afiliados'].fillna(t.pop('afiliados_r'))
    return t.assign(ccaa='Illes Balears', enfoque='residencia', medida='afiliaciones')


# --- Región de Murcia: CREM, tablas HTML mensuales --------------------------------------------------------
CREM = 'https://econet.carm.es/web/crem/inicio/-/crem/sicrem/PM_Afiliados/{}/sec{}.html'
# periodo -> tablas de régimen y de sector (la numeración cambia de un periodo a otro; se comprueba el título).
# El CREM corta el acceso automatizado con un captcha: los periodos nuevos hay que añadirlos a mano.
PERIODOS_CREM = {'12m2021': (6, 9), '12m2022': (6, 9), '12m2023': (6, 9), '12m2024': (6, 9)}
TITULOS = {'regimen': 'Afiliaciones según municipio de residencia y régimen. Ambos sexos',
           'sector': 'Afiliaciones según municipio de residencia y sector de actividad. Ambos sexos'}


def crem_tabla(carpeta, periodo, clave, n):
    html = bajar(carpeta, f'crem_{periodo}_sec{n}.html', CREM.format(periodo, n)).read_text(encoding='utf-8', errors='replace')
    assert TITULOS[clave] in html, (periodo, clave, n)
    t = [x for x in pd.read_html(StringIO(html), thousands='.', decimal=',') if len(x) and str(x.iloc[0, 0]) == 'Total'][0]
    return t.rename(columns={t.columns[0]: 'municipio'})


def murcia(carpeta, nombres):
    partes = []
    for periodo, (n_regimen, n_sector) in PERIODOS_CREM.items():
        s = crem_tabla(carpeta, periodo, 'sector', n_sector).rename(columns={
            'Total': 'afiliados', 'Agricultura': 'agricultura', 'Industria': 'industria',
            'Construcción': 'construccion', 'Servicios': 'servicios'})
        r = crem_tabla(carpeta, periodo, 'regimen', n_regimen)
        s['autonomos'] = s['municipio'].map(r.set_index('municipio')['Régimen Especial Trabajadores Autónomos'])
        m = re.match(r'(\d+)m(\d{4})', periodo)
        partes.append(s.assign(fecha=f'{m.group(2)}-{int(m.group(1)):02d}'))
    t = pd.concat(partes)
    t['mun_code'] = t['municipio'].replace({'Fuente-Álamo': 'Fuente Álamo de Murcia'}).map(sin_tildes).map(nombres)
    falta = t.loc[t['mun_code'].isna() & ~t['municipio'].isin(['Total', 'Región de Murcia', 'Resto de España', 'Extranjero', 'No consta']),
                  'municipio'].unique()
    assert not len(falta), falta
    t = t.dropna(subset=['mun_code'])
    return t.assign(ccaa='Región de Murcia', enfoque='residencia', medida='afiliaciones')


# --- Comunitat Valenciana: IVE, PC-Axis, trimestral -------------------------------------------------------
IVE = 'https://bdo.gva.es/bdo/res_optimo_static.php?cons=V0200_{}&idioma=cas&form=pcaxis&nperiodo=20'


def ive(carpeta, tabla, col, nombres):
    d = px(bajar(carpeta, f'ive_{tabla}.px', IVE.format(tabla)))
    d = d[(d['Sexo'] == 'Ambos sexos') if 'Sexo' in d else slice(None)]
    tri = d['Trimestre'].str.extract(r'^(\d{4}) - (\d)')
    d = d.assign(mun_code=d['Municipios'].str.extract(r'^(\d{5}) - ')[0],
                 fecha=tri[0] + '-' + tri[1].map({'1': '03', '2': '06', '3': '09', '4': '12'}))
    return ancho(d.dropna(subset=['mun_code']), col, nombres)


def valencia(carpeta):
    s = ive(carpeta, 'C2D0243', 'Sector de actividad', {'Total': 'afiliados', 'Agricultura': 'agricultura',
                                                         'Industria': 'industria', 'Construcción': 'construccion',
                                                         'Servicios': 'servicios', 'Más de una sc': 'sector_no_consta'})
    r = ive(carpeta, 'C2D0242', 'Régimen', {'Total': 'afiliados_r', 'Régimen Especial Trabajadores Autónomos': 'autonomos'})
    t = s.merge(r, on=['mun_code', 'fecha'], how='outer')
    t['afiliados'] = t['afiliados'].fillna(t.pop('afiliados_r'))
    # personas, no afiliaciones: quien está en más de un sector cuenta en «Más de una» (va a sector_no_consta)
    return t.assign(ccaa='Comunitat Valenciana', enfoque='residencia', medida='personas')


# --- País Vasco: Eustat, Directorio de Actividades Económicas, anual --------------------------------------
EUSTAT = 'https://www.eustat.eus/bankupx/api/v1/es/DB/PX_200163_cdirae_est07.px'


def euskadi(carpeta):
    f = bajar(carpeta, 'eustat_est07.json', EUSTAT, json.dumps({'query': [], 'response': {'format': 'json-stat2'}}).encode())
    d = json.loads(f.read_bytes())
    terr, per = (list(d['dimension'][k]['category']['index']) for k in d['id'][1:])
    t = pd.DataFrame({'valor': d['value']}, index=pd.MultiIndex.from_product([terr, per], names=['mun_code', 'anyo']))
    t = t.reset_index()
    t = t[t['mun_code'].str.match(r'^(01|20|48)\d{3}$') & ~t['mun_code'].str.endswith('990')]
    # personas empleadas en establecimientos a 1 de enero: se fecha en diciembre del año anterior
    t = t.assign(fecha=(t['anyo'].astype(int) - 1).astype(str) + '-12', afiliados=t['valor'])
    return t[['mun_code', 'fecha', 'afiliados']].assign(ccaa='País Vasco', enfoque='trabajo', medida='empleados')


# --- Cataluña y Extremadura: ficheros ya en data/empleo --------------------------------------------------
def catalunya():
    d = pd.read_csv(DATOS / 'afiliacion_catalunya_municipios.csv', dtype={'mun_code': str})
    s = d[(d['enfoque'] == 'residencia') & (d['nivel'] == 'sector')].assign(
        agricultura=lambda x: x['a'], industria=lambda x: x['b-e'], construccion=lambda x: x['f'],
        servicios=lambda x: x['g-u'], afiliados=lambda x: x['total'], enfoque='residencia')
    w = d[d['enfoque'] == 'trabajo'].assign(
        agricultura=lambda x: x['a'], industria=lambda x: x[list('bcde')].sum(axis=1, min_count=1),
        construccion=lambda x: x['f'], servicios=lambda x: x[list('ghijklmnopqrstu')].sum(axis=1, min_count=1),
        afiliados=lambda x: x['total'], enfoque='trabajo')
    t = pd.concat([s, w])
    return t.assign(fecha=t['anyo'].astype(str) + '-12', ccaa='Cataluña', medida='afiliaciones')


def extremadura():
    d = pd.read_csv(DATOS / 'afiliacion_extremadura_municipios.csv', dtype={'mun_code': str})
    return d.assign(ccaa='Extremadura', enfoque='residencia', medida='personas')


if __name__ == '__main__':
    carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    carpeta.mkdir(parents=True, exist_ok=True)
    ine = pd.read_csv(DATOS / 'empleo_sector_municipios.csv', dtype={'mun_code': str})
    ine = ine.drop_duplicates('mun_code')
    nombres_murcia = {sin_tildes(n): c for c, n in ine.loc[ine['mun_code'].str[:2] == '30', ['mun_code', 'municipio']].values}
    partes = []
    for nombre, f in [('Madrid', lambda: madrid(carpeta)), ('Canarias', lambda: canarias(carpeta)),
                      ('Galicia', lambda: galicia(carpeta)), ('Illes Balears', lambda: baleares(carpeta)),
                      ('Región de Murcia', lambda: murcia(carpeta, nombres_murcia)),
                      ('Comunitat Valenciana', lambda: valencia(carpeta)), ('País Vasco', lambda: euskadi(carpeta)),
                      ('Cataluña', catalunya), ('Extremadura', extremadura)]:
        t = f()
        t = pd.concat([elegir_fechas(g) for _, g in t.groupby('enfoque')])
        partes.append(t.reindex(columns=COLUMNAS))
        print(nombre, t['mun_code'].nunique(), 'municipios', sorted(t['fecha'].unique()))
    t = pd.concat(partes)
    t = t[t['mun_code'].isin(ine['mun_code'])].sort_values(['ccaa', 'enfoque', 'fecha', 'mun_code'])
    t.to_csv(SALIDA, index=False, float_format='%.0f')
    print(len(t), 'filas')
    print(t.groupby(['ccaa', 'enfoque', 'fecha'])['afiliados'].agg(['count', 'sum']).to_string())
