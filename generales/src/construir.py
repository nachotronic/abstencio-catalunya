"""Construye la base de datos de la pieza de generales (España, Congreso 2004-2023, más municipales y europeas).

Uso:  python3 construir.py            (descarga las fuentes en ~/.cache/generales si faltan)

Fuentes
- Resultados por mesa del Congreso: microdatos del Ministerio del Interior, vía el repositorio
  público dadosdelaplace/pollspaindata (parquet). infoelectoral.interior.gob.es corta las
  conexiones desde este entorno.
- Renta, pobreza, edad y nacionalidad por sección: INE, Atlas de Distribución de Renta de los
  Hogares (ADRH) 2023, vía pablogguz/ineAtlas.data.
- Estudios y paro por sección: INE, Censo 2021, vía pablogguz/ineAtlas.data.
- Geometría: secciones censales INE 2023 (ineAtlas.data).
- Municipales 2007-2023 y europeas 2019-2024: ficheros de Infoelectoral importados con otras_elecciones.py
  (datos/extra/raw_*_M2023.parquet, M2007_municipios.csv...).

Salidas en ./datos (tablas) y ./web/data (lo que carga la pieza).
"""
import glob, json, os, re, subprocess, zipfile
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import Polygon
from shapely.affinity import translate
from partidos import familia, FAMILIAS, CODIGOS, _REGLAS

AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get('GENERALES_CACHE', os.path.expanduser('~/.cache/generales'))
DATOS, WEB = os.path.join(AQUI, 'datos'), os.path.join(AQUI, 'web', 'data')
EXTRA = os.path.join(DATOS, 'extra')   # resultados nuevos que deja actualizar_29n.py
ETIQ = {'2004_03': '14M 2004', '2008_03': '9M 2008', '2011_11': '20N 2011', '2015_12': '20D 2015', '2016_06': '26J 2016', '2019_04': '28A 2019', '2019_11': '10N 2019', '2023_07': '23J 2023',
        '2026_11': '29N 2026'}
TIPO = {'M': 'municipales', 'E': 'europeas'}
etiq = lambda y: ETIQ.get(y) or (TIPO[y[0]].capitalize() + ' ' + y[1:] if y[0] in TIPO else y)
tipo = lambda y: TIPO.get(y[0], 'generales')
# elecciones con resultados por mesa (y por tanto por sección)
GENERALES = ['2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07'] + sorted(
    f.split('_congress_')[1][:7] for f in glob.glob(os.path.join(EXTRA, 'raw_poll_stations_congress_*.parquet')))
# municipales (M2023) y europeas (E2024) por mesa, de otras_elecciones.py
OTRAS = sorted(os.path.basename(f)[18:-8] for f in glob.glob(os.path.join(EXTRA, 'raw_poll_stations_[ME]*.parquet')))
ELECCIONES = GENERALES + OTRAS
# elecciones con resultados solo por municipio (escrutinio provisional de la noche electoral, municipales 2007)
SOLO_MUN = sorted(os.path.basename(f).split('_municipios')[0] for f in glob.glob(os.path.join(EXTRA, '*_municipios.csv'))
                  if os.path.basename(f).split('_municipios')[0] not in ELECCIONES)
TODAS = ELECCIONES + SOLO_MUN
# las que van en municipios.json y sec/<prov>.json; el resto, en ficheros aparte que se cargan al elegirlas
BASE = [y for y in TODAS if tipo(y) == 'generales']
CANARIAS = ('35', '38')
# Escaños por provincia. 2023: los de la convocatoria de 2023. 2026: Madrid gana uno y Cádiz lo pierde (decreto de convocatoria del 6-10-2026).
ESCANOS_2023 = {'01': 4, '02': 4, '03': 12, '04': 6, '05': 3, '06': 5, '07': 8, '08': 32, '09': 4, '10': 4, '11': 9, '12': 5,
                '13': 5, '14': 6, '15': 8, '16': 3, '17': 6, '18': 7, '19': 3, '20': 6, '21': 5, '22': 3, '23': 5, '24': 4,
                '25': 4, '26': 4, '27': 4, '28': 37, '29': 11, '30': 10, '31': 5, '32': 4, '33': 7, '34': 3, '35': 8, '36': 7,
                '37': 4, '38': 7, '39': 5, '40': 3, '41': 12, '42': 2, '43': 6, '44': 3, '45': 6, '46': 16, '47': 5, '48': 8,
                '49': 3, '50': 7, '51': 1, '52': 1}
ESCANOS_2026 = {**ESCANOS_2023, '28': 38, '11': 8}
assert sum(ESCANOS_2023.values()) == 350 and sum(ESCANOS_2026.values()) == 350
DX, DY = 5.6, 6.6   # desplazamiento del recuadro de Canarias en la vista de España (grados)


def fuentes():
    os.makedirs(CACHE, exist_ok=True)
    for repo in ('dadosdelaplace/pollspaindata', 'pablogguz/ineAtlas.data'):
        d = os.path.join(CACHE, repo.split('/')[1])
        if not os.path.isdir(d):
            subprocess.run(['git', 'clone', '-q', '--depth', '1', f'https://github.com/{repo}.git', d], check=True)
    unz = os.path.join(CACHE, 'atlas')
    if not os.path.isdir(unz):
        os.makedirs(unz)
        base = os.path.join(CACHE, 'ineAtlas.data', 'data')
        for f in ['income/income_tract.zip', 'income/income_municipality.zip', 'demographics/demographics_tract.zip',
                  'demographics/demographics_municipality.zip', 'census_2021/census_2021_tract.zip',
                  'census_2021/census_2021_municipality.zip', 'distribution_sex/distribution_sex_tract.zip',
                  'distribution_sex/distribution_sex_municipality.zip', 'geometries/census_tracts_2023.gpkg.zip']:
            sub = os.path.join(unz, os.path.dirname(f) + ('_' + f.split('_')[-1].split('.')[0]))
            with zipfile.ZipFile(os.path.join(base, f)) as z:
                z.extractall(sub)
    return os.path.join(CACHE, 'pollspaindata', 'inst', 'extdata'), unz


def uno(unz, sub):
    fs = [f for f in glob.glob(os.path.join(unz, sub, '*')) if f.endswith(('.csv', '.gpkg'))]
    assert len(fs) == 1, (sub, fs)
    return fs[0]


def bonito(n):
    """'Palmas de Gran Canaria, Las' -> 'Las Palmas de Gran Canaria'; 'Balears, Illes' -> 'Illes Balears'."""
    if not isinstance(n, str):
        return n
    m = re.match(r'^(.*), (La|Las|El|Los|L\'|Les|Els|A|As|O|Os|Illes|Lo)$', n)
    if m:
        art = m.group(2)
        return art + ('' if art.endswith("'") else ' ') + m.group(1)
    return n


# ---------------------------------------------------------------- resultados
def resultados(E):
    """Votos por sección censal (código INE de 10 dígitos) y familia política, por elección."""
    filas = []
    for y in ELECCIONES:
        k = y if y in OTRAS else 'congress_' + y
        src = EXTRA if os.path.exists(f'{EXTRA}/raw_poll_stations_{k}.parquet') else E
        m = pd.read_parquet(f'{src}/raw_poll_stations_{k}.parquet')
        c = pd.read_parquet(f'{src}/raw_candidacies_{k}.parquet')
        v = pd.read_parquet(f'{src}/raw_candidacies_poll_{k}.parquet')
        for d in (m, v):
            d['tract_code'] = d.cod_INE_prov + d.cod_INE_mun + d.cod_mun_district + d.cod_sec
        m = m[m.cod_INE_mun != '999']          # CERA (residentes ausentes) fuera
        # mesas con censo pero sin ningún voto: sin resultado en el origen (no es una abstención del 100%), fuera
        vacia = (m.blank_ballots + m.invalid_ballots + m.party_ballots == 0) & (m.census_INE > 0)
        if vacia.any():
            print(y, 'mesas sin resultado en el origen:', ', '.join(m[vacia].tract_code + '-' + m[vacia].cod_poll_station))
        m = m[~vacia]
        v = v[v.cod_INE_mun != '999']
        c['fam'] = [familia(a, n) for a, n in zip(c.abbrev_candidacies, c.name_candidacies)]
        v = v.merge(c[['id_candidacies', 'fam']], on='id_candidacies', how='left')
        assert v.fam.notna().all()
        pv = v.pivot_table(index='tract_code', columns='fam', values='ballots', aggfunc='sum', fill_value=0)
        pv = pv.reindex(columns=CODIGOS, fill_value=0)
        s = m.groupby('tract_code').agg(censo=('census_INE', 'sum'), blancos=('blank_ballots', 'sum'),
                                        nulos=('invalid_ballots', 'sum'), candidaturas=('party_ballots', 'sum'))
        s = s.join(pv, how='left').fillna(0)
        s['votantes'] = s.blancos + s.nulos + s.candidaturas
        s['eleccion'] = y
        filas.append(s.reset_index())
        tot = s[CODIGOS].sum()
        print(y, f"censo {s.censo.sum():,.0f}  votantes {s.votantes.sum():,.0f}  part {s.votantes.sum()/s.censo.sum():.3f}",
              ' '.join(f"{k}:{tot[k]/s.candidaturas.sum()*100:.1f}" for k in CODIGOS if tot[k] > 0))
    r = pd.concat(filas, ignore_index=True)
    r['mun_code'] = r.tract_code.str[:5]
    return r


def resultados_mun(y):
    """Escrutinio por municipio (formato largo de actualizar_29n.py): mun_code, siglas, votos + totales."""
    d = pd.read_csv(os.path.join(EXTRA, f'{y}_municipios.csv'), dtype={'mun_code': str, 'siglas': str, 'nombre': str},
                    keep_default_na=False)          # hay siglas como "NA"
    d['fam'] = [familia(a, n) for a, n in zip(d.siglas, d.nombre if 'nombre' in d else [''] * len(d))]
    pv = d.pivot_table(index='mun_code', columns='fam', values='votos', aggfunc='sum', fill_value=0).reindex(columns=CODIGOS, fill_value=0)
    t = d.groupby('mun_code')[['censo', 'votantes', 'blancos', 'nulos']].first()
    t = t.join(pv)
    t['candidaturas'] = t[CODIGOS].sum(axis=1)
    return t


def tasas(df, pref=''):
    out = pd.DataFrame(index=df.index)
    out[pref + 'part'] = df.votantes / df.censo.where(df.censo > 0)
    val = (df.candidaturas + df.blancos).where(lambda x: x > 0)
    for k in CODIGOS:
        out[pref + k] = df[k] / val
    sub = df[[k for k in CODIGOS if k != 'OTROS']]
    out[pref + 'gana'] = np.where(df.candidaturas > 0, sub.idxmax(axis=1), None)
    return out


# ---------------------------------------------------------------- covariables
def covariables(unz, nivel):
    key = 'tract_code' if nivel == 'tract' else 'mun_code'
    width = 10 if nivel == 'tract' else 5

    def norm(d):
        d[key] = d[key].astype(str).str.zfill(width)
        return d
    inc = norm(pd.read_csv(uno(unz, f'income_{nivel}'), dtype={key: str}))
    dem = norm(pd.read_csv(uno(unz, f'demographics_{nivel}'), dtype={key: str}))
    dis = norm(pd.read_csv(uno(unz, f'distribution_sex_{nivel}'), dtype={key: str}))
    cen = norm(pd.read_csv(uno(unz, f'census_2021_{nivel}'), dtype={key: str}))
    inc = inc[inc.year == 2023][[key, 'net_income_equiv', 'median_income_equiv', 'net_income_pc']]
    dem = dem[dem.year == 2023][[key, 'population', 'mean_age', 'pct_under18', 'pct_over65', 'pct_spanish']]
    dis = dis[(dis.year == 2023) & (dis.sex == 'total')][[key, 'equivinc_below_60p_median']]
    cen = cen[[key, 'pct_foreign', 'pct_foreign_born', 'pct_higher_ed_completed', 'unemployment_rate', 'pct_over64']]
    d = inc.merge(dem, on=key, how='outer').merge(dis, on=key, how='outer').merge(cen, on=key, how='outer')
    d = d.rename(columns={'net_income_equiv': 'renta_uc', 'median_income_equiv': 'renta_uc_mediana',
                          'net_income_pc': 'renta_pc', 'population': 'poblacion', 'mean_age': 'edad_media',
                          'equivinc_below_60p_median': 'pobreza', 'pct_foreign': 'extranjeros_2021',
                          'pct_foreign_born': 'nacidos_fuera_2021', 'pct_higher_ed_completed': 'estudios_sup_2021',
                          'unemployment_rate': 'paro_2021', 'pct_over64': 'mayores65_2021'})
    for c in ('pct_under18', 'pct_over65', 'pct_spanish', 'pobreza'):
        d[c] = d[c] / 100
    d['extranjeros'] = 1 - d.pct_spanish   # padrón 2023 (ADRH): población sin nacionalidad española
    d = d.rename(columns={'pct_under18': 'menores18', 'pct_over65': 'mayores65'}).drop(columns='pct_spanish')
    d['adultos'] = d.poblacion * (1 - d.menores18)
    return d


# ---------------------------------------------------------------- geometría
def codifica(geom, S=10000):
    out = []
    parts = [geom] if isinstance(geom, Polygon) else list(geom.geoms)
    for p in parts:
        cs = [(round(x * S), round(y * S)) for x, y in p.exterior.coords[:-1]]
        cs = [c for k, c in enumerate(cs) if k == 0 or c != cs[k - 1]]
        if len(cs) < 3:
            continue
        flat = [cs[0][0], cs[0][1]]
        for k in range(1, len(cs)):
            flat += [cs[k][0] - cs[k - 1][0], cs[k][1] - cs[k - 1][1]]
        out.append(flat)
    return out


def a_canarias(g):
    """Mueve Canarias al recuadro junto a la Península (solo para dibujar)."""
    m = g.cod.str[:2].isin(CANARIAS)
    g.loc[m, 'geometry'] = g.loc[m, 'geometry'].apply(lambda x: translate(x, DX, DY))
    return g


def main():
    E, unz = fuentes()
    os.makedirs(DATOS, exist_ok=True); os.makedirs(WEB, exist_ok=True)
    r = resultados(E)
    r.to_csv(os.path.join(DATOS, 'resultados_secciones_largo.csv'), index=False)

    geo = gpd.read_file(uno(unz, 'geometries_2023'))[['tract_code', 'municipality', 'province', 'geometry']]
    geo['tract_code'] = geo.tract_code.astype(str)
    geo['mun_code'] = geo.tract_code.str[:5]
    nombres = geo.groupby('mun_code').agg(municipio=('municipality', 'first'), provincia=('province', 'first'))
    nombres['municipio'] = nombres.municipio.map(bonito)
    nombres['provincia'] = nombres.provincia.map(bonito)

    # --- secciones (código INE 2023): resultados de cada elección solo si la sección conserva el código
    cs = covariables(unz, 'tract')
    sec = geo[['tract_code', 'mun_code']].merge(cs, on='tract_code', how='left')
    for y in ELECCIONES:
        ry = r[r.eleccion == y].set_index('tract_code')
        t = tasas(ry, f'{y}_').join(ry[['censo', 'votantes']].add_prefix(f'{y}_'))
        sec = sec.merge(t, left_on='tract_code', right_index=True, how='left')
        print(y, 'secciones 2023 con resultado:', sec[f'{y}_part'].notna().mean().round(3))
    sec['sin_derecho'] = ((sec.adultos - sec['2023_07_censo']).clip(lower=0) / sec.adultos).where(sec.adultos > 0)
    sec = sec.merge(nombres, left_on='mun_code', right_index=True, how='left')
    sec.round(6).to_csv(os.path.join(DATOS, 'secciones.csv'), index=False)

    # --- municipios: suma de secciones (fronteras municipales estables), así no se pierde nada
    cm = covariables(unz, 'municipality')
    mun = nombres.reset_index().merge(cm, on='mun_code', how='left')
    for y in TODAS:
        if y in ELECCIONES:
            ry = r[r.eleccion == y].groupby('mun_code')[['censo', 'votantes', 'blancos', 'nulos', 'candidaturas'] + CODIGOS].sum()
        else:
            ry = resultados_mun(y)
        t = tasas(ry, f'{y}_').join(ry[['censo', 'votantes'] + CODIGOS].rename(columns={k: 'v' + k for k in CODIGOS}).add_prefix(f'{y}_'))
        mun = mun.merge(t, left_on='mun_code', right_index=True, how='left')
    mun['sin_derecho'] = ((mun.adultos - mun['2023_07_censo']).clip(lower=0) / mun.adultos).where(mun.adultos > 0)
    mun.round(6).to_csv(os.path.join(DATOS, 'municipios.csv'), index=False)

    resumen(sec, r)
    web(geo, sec, mun)


# ---------------------------------------------------------------- análisis para los gráficos
def resumen(sec, r):
    """Voto y participación 23J por decil de cada variable (secciones ponderadas por censo)."""
    y = '2023_07'
    rv = r[r.eleccion == y].set_index('tract_code')
    d = sec.set_index('tract_code').join(rv[['censo', 'votantes', 'candidaturas', 'blancos'] + CODIGOS], how='inner')
    out = {'eleccion': etiq(y), 'variables': {}}
    VARS = {'renta_uc': 'Renta por unidad de consumo (2023)', 'pobreza': 'Población en riesgo de pobreza (2023)',
            'edad_media': 'Edad media (2023)', 'extranjeros': 'Población extranjera (2023)',
            'estudios_sup_2021': 'Adultos con estudios superiores (2021)', 'paro_2021': 'Tasa de paro (2021)'}
    for v, nom in VARS.items():
        x = d[d[v].notna() & (d.censo > 0)].copy()
        x = x.sort_values(v)
        cum = x.censo.cumsum() / x.censo.sum()
        x['dec'] = np.minimum((cum * 10).apply(np.ceil).astype(int), 10)
        g = x.groupby('dec').agg(**{k: (k, 'sum') for k in ['censo', 'votantes', 'candidaturas', 'blancos'] + CODIGOS},
                                 lo=(v, 'min'), hi=(v, 'max'), n=(v, 'size'))
        val = g.candidaturas + g.blancos
        out['variables'][v] = {'nombre': nom, 'deciles': [
            {'d': int(i), 'lo': float(row.lo), 'hi': float(row.hi), 'n': int(row.n),
             'part': float(row.votantes / row.censo),
             **{k: float(row[k] / val[i]) for k in CODIGOS}} for i, row in g.iterrows()]}
    # totales nacionales por elección
    tot = r.groupby('eleccion')[['censo', 'votantes', 'candidaturas', 'blancos'] + CODIGOS].sum()
    for e in SOLO_MUN:
        tot.loc[e] = resultados_mun(e)[['censo', 'votantes', 'candidaturas', 'blancos'] + CODIGOS].sum()
    out['nacional'] = {etiq(e): {'part': float(t.votantes / t.censo),
                                 **{k: float(t[k] / (t.candidaturas + t.blancos)) for k in CODIGOS}}
                       for e, t in tot.iterrows()}
    json.dump(out, open(os.path.join(DATOS, 'resumen.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(out, open(os.path.join(WEB, 'resumen.json'), 'w'), ensure_ascii=False, separators=(',', ':'))


# ---------------------------------------------------------------- datos de la web
COLS = ['part', 'gana'] + CODIGOS
COV = ['renta_uc', 'pobreza', 'edad_media', 'mayores65', 'extranjeros', 'sin_derecho', 'estudios_sup_2021', 'paro_2021', 'poblacion']


def columnas(df, codigo, elecs=None):
    out = {'cod': df[codigo].tolist()} if elecs is None else {}
    for y in (BASE if elecs is None else elecs):
        if f'{y}_part' not in df:
            continue
        for c in COLS:
            k = f'{y}_{c}'
            if c == 'gana':
                out[k] = [CODIGOS.index(v) if isinstance(v, str) else -1 for v in df[k]]
            else:
                out[k] = [None if pd.isna(v) else round(float(v), 3) for v in df[k]]
        out[f'{y}_censo'] = [None if pd.isna(v) else int(v) for v in df[f'{y}_censo']]
    if elecs is not None:
        return out
    for c in COV:
        dig = 0 if c in ('renta_uc', 'poblacion') else (1 if c == 'edad_media' else 3)
        out[c] = [None if pd.isna(v) else (int(round(v)) if dig == 0 else round(float(v), dig)) for v in df[c]]
    return out


def web(geo, sec, mun):
    meta = {'familias': [{'cod': c, 'nombre': n, 'color': col} for c, n, col in FAMILIAS],
            'elecciones': [{'cod': y, 'nombre': etiq(y), 'tipo': tipo(y), 'secciones': y in ELECCIONES, 'aparte': y not in BASE}
                           for y in TODAS], 'canarias': [DX, DY], 'S': 10000,
            'reglas': _REGLAS, 'escanos': {'2023_07': ESCANOS_2023, '2026_11': ESCANOS_2026},
            # URL del Worker de resultados en directo (directo/worker.js). Vacío = sin directo.
            'directo': {'url': os.environ.get('GENERALES_DIRECTO', ''), 'eleccion': '2026_11', 'nombre': '29N 2026'}}
    # municipios: disolver secciones, simplificar más
    gm = geo.dissolve('mun_code').reset_index()[['mun_code', 'geometry']]
    gm['geometry'] = gm.geometry.simplify(200, preserve_topology=True)
    gm = gm.to_crs(4326).rename(columns={'mun_code': 'cod'})
    gm = a_canarias(gm)
    m = mun.set_index('mun_code').loc[gm.cod].reset_index()
    d = columnas(m, 'mun_code')
    d['nombre'] = m.municipio.tolist()
    provs = sorted(m.provincia.dropna().unique())
    d['provs'] = provs
    d['prov'] = [provs.index(p) if isinstance(p, str) else -1 for p in m.provincia]
    d['poly'] = [codifica(x, 2000) for x in gm.geometry]
    d['S'] = 2000
    # centro para el buscador: media de los centroides de sus secciones ponderada por población
    gc = geo[['tract_code', 'mun_code', 'geometry']].copy()
    gc['geometry'] = gc.geometry.centroid
    gc = gc.to_crs(4326).merge(sec[['tract_code', 'poblacion']], on='tract_code', how='left')
    gc['w'] = gc.poblacion.fillna(0) + 1
    gc['x'], gc['y'] = gc.geometry.x * gc.w, gc.geometry.y * gc.w
    gc.loc[gc.mun_code.str[:2].isin(CANARIAS), ['x', 'y']] += gc.loc[gc.mun_code.str[:2].isin(CANARIAS), ['w']].values * [DX, DY]
    cc = gc.groupby('mun_code')[['x', 'y', 'w']].sum()
    cc = cc.loc[gm.cod]
    d['c'] = [[round(x / w, 3), round(y / w, 3)] for x, y, w in zip(cc.x, cc.y, cc.w)]
    json.dump(d, open(os.path.join(WEB, 'municipios.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
    os.makedirs(os.path.join(WEB, 'e'), exist_ok=True)
    for y in TODAS:
        if y not in BASE:
            json.dump(columnas(m, 'mun_code', [y]), open(os.path.join(WEB, 'e', f'{y}.json'), 'w'), separators=(',', ':'))
    # provincias (contorno) para el mapa
    gp = geo.assign(p=geo.tract_code.str[:2]).dissolve('p').reset_index()[['p', 'geometry']]
    gp['geometry'] = gp.geometry.simplify(400, preserve_topology=True)
    gp = gp.to_crs(4326).rename(columns={'p': 'cod'}); gp = a_canarias(gp)
    json.dump({'S': 1000, 'cod': gp.cod.tolist(), 'poly': [codifica(x, 1000) for x in gp.geometry]},
              open(os.path.join(WEB, 'provincias.json'), 'w'), separators=(',', ':'))
    # secciones: un fichero por provincia, cargado al acercarse
    gs = geo[['tract_code', 'geometry']].copy()
    gs['geometry'] = gs.geometry.simplify(12, preserve_topology=True)
    gs = gs.to_crs(4326).rename(columns={'tract_code': 'cod'}); gs = a_canarias(gs)
    os.makedirs(os.path.join(WEB, 'sec'), exist_ok=True)
    s = sec.set_index('tract_code')
    tam = 0
    for p, sub in gs.groupby(gs.cod.str[:2]):
        x = s.loc[sub.cod].reset_index()
        d = columnas(x, 'tract_code')
        d['poly'] = [codifica(g) for g in sub.geometry]
        d['S'] = 10000
        f = os.path.join(WEB, 'sec', f'{p}.json')
        json.dump(d, open(f, 'w'), separators=(',', ':'))
        tam += os.path.getsize(f)
        for y in ELECCIONES:
            if y not in BASE:
                f = os.path.join(WEB, 'sec', f'{p}_{y}.json')
                json.dump(columnas(x, 'tract_code', [y]), open(f, 'w'), separators=(',', ':'))
                tam += os.path.getsize(f)
    json.dump(meta, open(os.path.join(WEB, 'meta.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print('web: municipios', os.path.getsize(os.path.join(WEB, 'municipios.json')) // 1024, 'KB; secciones', tam // 1024, 'KB')


if __name__ == '__main__':
    main()
