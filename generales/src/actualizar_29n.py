"""Carga los resultados del 29N en la pieza.

Tres momentos:

1. Noche electoral (en directo). La pieza lee un JSON normalizado (ver FORMATO abajo) que sirve el
   Worker de directo/ y repinta el mapa por municipio cada minuto. Para ensayar sin datos reales:
       python3 actualizar_29n.py --simulacro 0.6      -> web/data/simulacro.json (23J al 60% escrutado)
   y abrir la pieza con ?directo=data/simulacro.json

2. Al acabar la noche, congelar el escrutinio provisional en la pieza (texto, CSV y mapa estático):
       python3 actualizar_29n.py --json resultados.json      (el JSON normalizado del Worker)
   o bien, desde cualquier tabla por municipio:
       python3 actualizar_29n.py --csv municipios.csv
   y después:  python3 construir.py && python3 pagina.py

3. Semanas después, con los resultados por mesa de Interior (fichero 02202611_MESA.zip de
   infoelectoral.interior.gob.es > Área de descargas), para tener el 29N por sección censal:
       python3 actualizar_29n.py --mir 02202611_MESA.zip
       python3 construir.py && python3 pagina.py

FORMATO del JSON normalizado (lo que produce el Worker y lee la pieza):
    {"eleccion": "2026_11", "actualizado": "2026-11-29T22:41:00+01:00",
     "siglas": ["PP", "PSOE", "VOX", ...],
     "mun": {"28079": [censo_total, censo_escrutado, votantes, blancos, nulos, votos_siglas0, votos_siglas1, ...], ...}}
  - claves de "mun": código INE de municipio de 5 dígitos (provincia + municipio).
  - censo_escrutado: censo de las mesas ya escrutadas (si la fuente solo da el %, censo_total × %).

CSV por municipio (--csv): columnas mun_code (5 dígitos), censo, votantes, blancos, nulos y una
columna por candidatura con sus siglas como nombre y los votos como valor.
"""
import argparse, io, json, os, sys, zipfile
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
EXTRA = os.path.join(AQUI, 'datos', 'extra')
Y = '2026_11'


def guardar_largo(filas):
    os.makedirs(EXTRA, exist_ok=True)
    d = pd.DataFrame(filas, columns=['mun_code', 'censo', 'votantes', 'blancos', 'nulos', 'siglas', 'votos'])
    d = d[d.mun_code.str[2:] != '999']          # CERA fuera, como en el resto de elecciones
    f = os.path.join(EXTRA, f'{Y}_municipios.csv')
    d.to_csv(f, index=False)
    print(f'{f}: {d.mun_code.nunique()} municipios, {d.siglas.nunique()} candidaturas, {d.votos.sum():,.0f} votos')


def desde_json(path):
    F = json.load(open(path))
    filas = []
    for c, a in F['mun'].items():
        censo, censo_esc, vot, bl, nu, *v = a
        for s, x in zip(F['siglas'], v):
            if x:
                filas.append([c.zfill(5), censo_esc, vot, bl, nu, s, x])   # participación sobre lo escrutado
    guardar_largo(filas)


def desde_csv(path):
    d = pd.read_csv(path, dtype={'mun_code': str})
    base = ['mun_code', 'censo', 'votantes', 'blancos', 'nulos']
    falta = [c for c in base if c not in d]
    if falta:
        sys.exit(f'Faltan columnas: {falta}')
    filas = []
    for r in d.itertuples(index=False):
        r = r._asdict() if hasattr(r, '_asdict') else dict(zip(d.columns, r))
        for s in d.columns:
            if s not in base and r[s]:
                filas.append([str(r['mun_code']).zfill(5), r['censo'], r['votantes'], r['blancos'], r['nulos'], s, r[s]])
    guardar_largo(filas)


# ---- ficheros de Interior por mesa (formato de registro fijo; posiciones como en pollspaindata)
def _corta(linea, pos):
    return [linea[a - 1:b] for a, b in pos]


def desde_mir(path):
    z = zipfile.ZipFile(path)
    nombres = {n[:2]: n for n in z.namelist() if n.upper().endswith('.DAT')}
    lee = lambda k: io.TextIOWrapper(z.open(nombres[k]), encoding='latin-1').read().splitlines()
    # 03: candidaturas
    pos03 = [(9, 14), (15, 64), (65, 214)]
    cand = pd.DataFrame([[x.strip() for x in _corta(l, pos03)] for l in lee('03') if l.strip()],
                        columns=['id_candidacies', 'abbrev_candidacies', 'name_candidacies'])
    # 09: mesas
    pos09 = [(12, 13), (14, 16), (17, 18), (19, 22), (23, 23), (24, 30), (31, 37), (66, 72), (73, 79), (80, 86)]
    m = pd.DataFrame([[x.strip() for x in _corta(l, pos09)] for l in lee('09') if l.strip()],
                     columns=['cod_INE_prov', 'cod_INE_mun', 'cod_mun_district', 'cod_sec', 'cod_poll_station', 'census_INE',
                              'census_counting', 'blank_ballots', 'invalid_ballots', 'party_ballots'])
    # 10: votos por candidatura y mesa
    pos10 = [(12, 13), (14, 16), (17, 18), (19, 22), (23, 23), (24, 29), (30, 36)]
    v = pd.DataFrame([[x.strip() for x in _corta(l, pos10)] for l in lee('10') if l.strip()],
                     columns=['cod_INE_prov', 'cod_INE_mun', 'cod_mun_district', 'cod_sec', 'cod_poll_station', 'id_candidacies', 'ballots'])
    for d in (m, v):
        d['cod_sec'] = d.cod_sec.str.zfill(4).str[-3:]      # la sección INE tiene 3 dígitos
    for c in ('census_INE', 'census_counting', 'blank_ballots', 'invalid_ballots', 'party_ballots'):
        m[c] = pd.to_numeric(m[c])
    v['ballots'] = pd.to_numeric(v.ballots)
    os.makedirs(EXTRA, exist_ok=True)
    m.to_parquet(os.path.join(EXTRA, f'raw_poll_stations_congress_{Y}.parquet'))
    v.to_parquet(os.path.join(EXTRA, f'raw_candidacies_poll_congress_{Y}.parquet'))
    cand.to_parquet(os.path.join(EXTRA, f'raw_candidacies_congress_{Y}.parquet'))
    print(f'{len(m)} mesas, {len(cand)} candidaturas, {v.ballots.sum():,.0f} votos a candidaturas')


# ---- simulacro con datos del 23J
def simulacro(frac, salida):
    sys.path.insert(0, AQUI)
    from construir import fuentes
    E, _ = fuentes()
    m = pd.read_parquet(f'{E}/raw_poll_stations_congress_2023_07.parquet')
    v = pd.read_parquet(f'{E}/raw_candidacies_poll_congress_2023_07.parquet')
    c = pd.read_parquet(f'{E}/raw_candidacies_congress_2023_07.parquet')
    for d in (m, v):
        d['mun'] = d.cod_INE_prov + d.cod_INE_mun
    m, v = m[m.cod_INE_mun != '999'], v[v.cod_INE_mun != '999']
    # una fracción de mesas escrutadas, al azar pero estable
    m = m.assign(k=m.mun + m.cod_mun_district + m.cod_sec + m.cod_poll_station)
    esc = set(m.sample(frac=frac, random_state=29).k)
    v = v.assign(k=v.mun + v.cod_mun_district + v.cod_sec + v.cod_poll_station)
    tot = m.groupby('mun').census_INE.sum()
    me = m[m.k.isin(esc)].groupby('mun')[['census_INE', 'blank_ballots', 'invalid_ballots', 'party_ballots']].sum()
    ve = v[v.k.isin(esc)].merge(c[['id_candidacies', 'abbrev_candidacies']], on='id_candidacies')
    ve = ve.groupby(['mun', 'abbrev_candidacies']).ballots.sum().unstack(fill_value=0)
    siglas = list(ve.columns)
    out = {'eleccion': Y, 'actualizado': '2026-11-29T22:00:00+01:00', 'simulacro': True, 'siglas': siglas, 'mun': {}}
    for mun, ct in tot.items():
        if mun in me.index:
            r = me.loc[mun]; vv = [int(x) for x in ve.loc[mun]] if mun in ve.index else [0] * len(siglas)
            vot = int(r.blank_ballots + r.invalid_ballots + r.party_ballots)
            out['mun'][mun] = [int(ct), int(r.census_INE), vot, int(r.blank_ballots), int(r.invalid_ballots)] + vv
        else:
            out['mun'][mun] = [int(ct), 0, 0, 0, 0] + [0] * len(siglas)
    json.dump(out, open(salida, 'w'), separators=(',', ':'))
    print(salida, os.path.getsize(salida) // 1024, 'KB')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--json'); g.add_argument('--csv'); g.add_argument('--mir')
    g.add_argument('--simulacro', type=float, metavar='FRACCION')
    ap.add_argument('--salida', default=os.path.join(AQUI, 'web', 'data', 'simulacro.json'))
    a = ap.parse_args()
    if a.json: desde_json(a.json)
    elif a.csv: desde_csv(a.csv)
    elif a.mir: desde_mir(a.mir)
    else: simulacro(a.simulacro, a.salida)
