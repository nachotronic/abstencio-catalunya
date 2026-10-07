"""Atlas de las anomalías electorales: cálculo de las cifras de cada pieza.

Lee las tablas limpias de la pieza de las generales y los ficheros por mesa de Interior (vía pollspaindata) y
escribe atlas/src/cifras.json (todas las cifras que citan las páginas) y un CSV por pieza en atlas/datos/.
Ninguna cifra de las páginas se escribe a mano: paginas.py las lee de cifras.json.

Uso:  python3 atlas/src/construir.py && python3 atlas/src/controles.py && python3 atlas/src/paginas.py
Variables de entorno:
  ATLAS_DATOS      carpeta con municipios.csv y secciones.csv de las generales (por defecto /mnt/project-files/generales/datos)
  GENERALES_CACHE  carpeta con el clon de dadosdelaplace/pollspaindata (por defecto ~/.cache/generales)
"""
import json, os, pathlib, re
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATLAS = ROOT / 'atlas'
DATOS = pathlib.Path(os.environ.get('ATLAS_DATOS', '/mnt/project-files/generales/datos'))
CACHE = pathlib.Path(os.environ.get('GENERALES_CACHE', os.path.expanduser('~/.cache/generales')))
RAW = CACHE / 'pollspaindata' / 'inst' / 'extdata'
OUT_CSV = ATLAS / 'datos'

CONGRESO = ['2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
FAM = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'UPYD', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC', 'OTROS']
# Escaños por provincia: convocatoria de 2023 y de 2026 (Madrid 38, Cádiz 8). Mismos valores que generales-2026/construir.py.
ESCANOS_2023 = {'01': 4, '02': 4, '03': 12, '04': 6, '05': 3, '06': 5, '07': 8, '08': 32, '09': 4, '10': 4, '11': 9, '12': 5,
                '13': 5, '14': 6, '15': 8, '16': 3, '17': 6, '18': 7, '19': 3, '20': 6, '21': 5, '22': 3, '23': 5, '24': 4,
                '25': 4, '26': 4, '27': 4, '28': 37, '29': 11, '30': 10, '31': 5, '32': 4, '33': 7, '34': 3, '35': 8, '36': 7,
                '37': 4, '38': 7, '39': 5, '40': 3, '41': 12, '42': 2, '43': 6, '44': 3, '45': 6, '46': 16, '47': 5, '48': 8,
                '49': 3, '50': 7, '51': 1, '52': 1}
ESCANOS_2026 = {**ESCANOS_2023, '28': 38, '11': 8}
PROVINCIAS = {'01': 'Álava', '02': 'Albacete', '03': 'Alicante', '04': 'Almería', '05': 'Ávila', '06': 'Badajoz', '07': 'Illes Balears',
              '08': 'Barcelona', '09': 'Burgos', '10': 'Cáceres', '11': 'Cádiz', '12': 'Castellón', '13': 'Ciudad Real', '14': 'Córdoba',
              '15': 'A Coruña', '16': 'Cuenca', '17': 'Girona', '18': 'Granada', '19': 'Guadalajara', '20': 'Gipuzkoa', '21': 'Huelva',
              '22': 'Huesca', '23': 'Jaén', '24': 'León', '25': 'Lleida', '26': 'La Rioja', '27': 'Lugo', '28': 'Madrid', '29': 'Málaga',
              '30': 'Murcia', '31': 'Navarra', '32': 'Ourense', '33': 'Asturias', '34': 'Palencia', '35': 'Las Palmas', '36': 'Pontevedra',
              '37': 'Salamanca', '38': 'Santa Cruz de Tenerife', '39': 'Cantabria', '40': 'Segovia', '41': 'Sevilla', '42': 'Soria',
              '43': 'Tarragona', '44': 'Teruel', '45': 'Toledo', '46': 'Valencia', '47': 'Valladolid', '48': 'Bizkaia', '49': 'Zamora',
              '50': 'Zaragoza', '51': 'Ceuta', '52': 'Melilla'}
# Capitales de provincia (código INE de municipio). En Ceuta y Melilla la capital es toda la circunscripción: fuera.
CAPITALES = ['01059', '02003', '03014', '04013', '05019', '06015', '07040', '08019', '09059', '10037', '11012', '12040', '13034',
             '14021', '15030', '16078', '17079', '18087', '19130', '20069', '21041', '22125', '23050', '24089', '25120', '26089',
             '27028', '28079', '29067', '30030', '31201', '32054', '33044', '34120', '35016', '36038', '37274', '38038', '39075',
             '40194', '41091', '42173', '43148', '44216', '45168', '46250', '47186', '48020', '49275', '50297']


def r1(x):
    """Porcentaje con un decimal (0,4321 -> 43.2)."""
    return None if pd.isna(x) else round(float(x) * 100, 1)


def municipios():
    m = pd.read_csv(DATOS / 'municipios.csv', dtype={'mun_code': str}, low_memory=False).copy()
    m['prov'] = m.mun_code.str[:2]
    for e in CONGRESO + ['M2023']:
        m[f'{e}_DER'] = m[f'{e}_PP'] + m[f'{e}_VOX'] + m[f'{e}_CS']
        m[f'{e}_IZQ'] = m[f'{e}_PSOE'] + m[f'{e}_SUMAR']
    return m


def fila(m, nombre):
    x = m[m.municipio == nombre]
    assert len(x) == 1, nombre
    return x.iloc[0]


def agregado(g, e, col):
    """Porcentaje de un grupo de municipios: Σ votos de la familia / Σ voto válido (ponderado, no media de porcentajes)."""
    w = g[f'{e}_votantes']
    return float((g[f'{e}_{col}'] * w).sum() / w.sum())


def modelo(df, y, X, w, efectos='prov'):
    """MCO ponderada por censo con efectos fijos de provincia. Devuelve predicción, R² y coeficientes por desviación típica."""
    Z = (df[X] - df[X].mean()) / df[X].std()
    D = pd.get_dummies(df[efectos], drop_first=True, dtype=float)
    A = np.column_stack([np.ones(len(df)), Z.values, D.values])
    sw = np.sqrt(df[w].values)
    b, *_ = np.linalg.lstsq(A * sw[:, None], df[y].values * sw, rcond=None)
    pred = A @ b
    res = df[y].values - pred
    wv = df[w].values
    r2 = 1 - np.sum(wv * res ** 2) / np.sum(wv * (df[y] - np.average(df[y], weights=wv)) ** 2)
    return pred, float(r2), {k: float(v) for k, v in zip(X, b[1:len(X) + 1])}


# ---------------------------------------------------------------- escaños (D'Hondt con voto CERA)
def dhondt_2023():
    m = pd.read_parquet(RAW / 'raw_poll_stations_congress_2023_07.parquet')
    c = pd.read_parquet(RAW / 'raw_candidacies_congress_2023_07.parquet')
    v = pd.read_parquet(RAW / 'raw_candidacies_poll_congress_2023_07.parquet')
    blancos = m.groupby('cod_INE_prov').blank_ballots.sum()

    def reparto(vv, escanos):
        vot = (vv.groupby(['cod_INE_prov', 'id_candidacies']).ballots.sum().reset_index()
               .merge(c[['id_candidacies', 'abbrev_candidacies']], on='id_candidacies'))
        out = {}
        for p, g in vot.groupby('cod_INE_prov'):
            valido = g.ballots.sum() + blancos.get(p, 0)
            g = g[g.ballots >= 0.03 * valido]                  # barrera del 3 % del voto válido
            n = escanos[p]
            cocientes = sorted([(b / d, a) for a, b in zip(g.abbrev_candidacies, g.ballots) for d in range(1, n + 1)], reverse=True)
            esc = {}
            for _, a in cocientes[:n]:
                esc[a] = esc.get(a, 0) + 1
            ultimo_coc, ultimo = cocientes[n - 1]
            # votos que le faltaban a cada lista para superar el último cociente; el aspirante es la que menos necesitaba
            falta = {a: int(np.floor(ultimo_coc * (esc.get(a, 0) + 1) - b)) + 1 for a, b in zip(g.abbrev_candidacies, g.ballots)
                     if a != ultimo or True}
            falta = {a: f for a, f in falta.items() if f > 0}
            asp = min(falta, key=falta.get)
            out[p] = {'escanos': esc, 'ultimo': ultimo, 'aspirante': asp, 'votos_faltan': falta[asp],
                      'votos': {a: int(b) for a, b in zip(g.abbrev_candidacies, g.ballots)}}
        return out

    con = reparto(v, ESCANOS_2023)
    sin = reparto(v[v.cod_INE_mun != '999'], ESCANOS_2023)
    con26 = reparto(v, ESCANOS_2026)
    cera = (v[(v.cod_INE_mun == '999')].groupby(['cod_INE_prov', 'id_candidacies']).ballots.sum().reset_index()
            .merge(c[['id_candidacies', 'abbrev_candidacies']], on='id_candidacies'))
    return con, sin, con26, cera


def familia_lista(a):
    a = a.upper()
    if a.startswith('PP') or a == 'U.P.N.':
        return 'PP' if a.startswith('PP') else 'UPN'
    if 'PSOE' in a or a.startswith('PSC') or a.startswith('PSE'):
        return 'PSOE'
    if 'SUMAR' in a:
        return 'Sumar'
    return {'VOX': 'Vox', 'ERC': 'ERC', 'JXCAT - JUNTS': 'Junts', 'EH BILDU': 'EH Bildu', 'EAJ-PNV': 'PNV', 'B.N.G.': 'BNG',
            'CCA': 'CC', 'EXISTE': 'Teruel Existe'}.get(a, a)


def main():
    OUT_CSV.mkdir(parents=True, exist_ok=True)
    m = municipios()
    C = {'fuente_datos': {'municipios': str(DATOS / 'municipios.csv'), 'n_municipios': int(len(m))}}

    # ---------------- bisagras
    con, sin, con26, cera = dhondt_2023()
    tot = {}
    for p in con.values():
        for a, k in p['escanos'].items():
            f = familia_lista(a)
            tot[f] = tot.get(f, 0) + k
    C['escanos_2023_con_cera'] = dict(sorted(tot.items(), key=lambda x: -x[1]))
    filas = []
    for p, d in con.items():
        filas.append({'cod_prov': p, 'provincia': PROVINCIAS[p], 'escanos': ESCANOS_2023[p], 'ultimo_escano': familia_lista(d['ultimo']),
                      'aspirante': familia_lista(d['aspirante']), 'votos_que_faltaban': d['votos_faltan']})
    mg = pd.DataFrame(filas).sort_values('votos_que_faltaban')
    mg.to_csv(OUT_CSV / 'escanos-ajustados-2023.csv', index=False)
    C['margenes'] = mg.head(10).to_dict('records')
    C['margenes_menos_1500'] = int((mg.votos_que_faltaban < 1500).sum())
    C['margenes_menos_500'] = int((mg.votos_que_faltaban < 500).sum())
    # Madrid: el voto exterior (CERA) cambió el último escaño
    mad_con, mad_sin = con['28'], sin['28']
    cm = cera[cera.cod_INE_prov == '28'].copy()
    cm['f'] = cm.abbrev_candidacies.map(familia_lista)
    C['madrid'] = {'con_cera': {familia_lista(a): k for a, k in mad_con['escanos'].items()},
                   'sin_cera': {familia_lista(a): k for a, k in mad_sin['escanos'].items()},
                   'cera_pp': int(cm[cm.f == 'PP'].ballots.sum()), 'cera_psoe': int(cm[cm.f == 'PSOE'].ballots.sum()),
                   'cera_total_candidaturas': int(cm.ballots.sum()),
                   'votos_pp': mad_con['votos'].get('PP'), 'votos_psoe': mad_con['votos'].get('PSOE'),
                   'faltaban_psoe_con_cera': mad_con['votos_faltan'] if familia_lista(mad_con['aspirante']) == 'PSOE' else None,
                   'faltaban_pp_sin_cera': mad_sin['votos_faltan'] if familia_lista(mad_sin['aspirante']) == 'PP' else None}
    # 29N: Cádiz pierde uno y Madrid gana uno, con los votos de 2023
    camb = {}
    for p in ('11', '28'):
        a = {familia_lista(k): v for k, v in con[p]['escanos'].items()}
        b = {familia_lista(k): v for k, v in con26[p]['escanos'].items()}
        camb[p] = {'2023': a, '2026': b, 'pierde': [k for k in a if b.get(k, 0) < a[k]], 'gana': [k for k in b if b[k] > a.get(k, 0)]}
    C['escanos_29n'] = camb
    pd.DataFrame([{'provincia': PROVINCIAS[p], 'partido': f, 'escanos_2023': camb[p]['2023'].get(f, 0), 'escanos_con_reparto_2026': camb[p]['2026'].get(f, 0)}
                  for p in camb for f in sorted(set(camb[p]['2023']) | set(camb[p]['2026']))]).to_csv(OUT_CSV / 'cadiz-madrid-29n.csv', index=False)

    # ---------------- modelo municipal 2023 (excepciones)
    X = ['lrenta', 'edad_media', 'extranjeros', 'estudios_sup_2021', 'paro_2021', 'lpob']
    d = m.dropna(subset=['renta_uc', 'edad_media', 'extranjeros', 'estudios_sup_2021', 'paro_2021', '2023_07_DER']).copy()
    d['lrenta'], d['lpob'] = np.log(d.renta_uc), np.log(d.poblacion)
    d['pred_der'], r2, _ = modelo(d, '2023_07_DER', X, '2023_07_censo')
    d['res_der'] = d['2023_07_DER'] - d.pred_der
    C['modelo_municipal'] = {'r2_derecha': round(r2, 3), 'n': int(len(d))}
    big = d[d.poblacion >= 10000].sort_values('res_der')
    C['ranking_residuo_derecha_10k'] = [{'municipio': r.municipio, 'provincia': PROVINCIAS[r.prov], 'real': r1(r['2023_07_DER']),
                                        'previsto': r1(r.pred_der), 'diferencia': r1(r.res_der)} for _, r in big.head(8).iterrows()]
    C['n_municipios_10k'] = int(len(big))
    pr = d[d.municipio == 'Puerto Real'].iloc[0]
    prov = m[m.prov == '11']
    fp = fila(m, 'Puerto Real')
    C['puerto_real'] = {
        'der': r1(pr['2023_07_DER']), 'previsto': r1(pr.pred_der), 'diferencia': r1(pr.res_der),
        'rank': int((big.res_der < pr.res_der).sum()) + 1,
        'psoe': r1(fp['2023_07_PSOE']), 'pp': r1(fp['2023_07_PP']), 'vox': r1(fp['2023_07_VOX']), 'sumar': r1(fp['2023_07_SUMAR']),
        'prov_pp': r1(agregado(prov, '2023_07', 'PP')), 'prov_psoe': r1(agregado(prov, '2023_07', 'PSOE')), 'prov_der': r1(agregado(prov, '2023_07', 'DER')),
        'renta': int(fp.renta_uc), 'edad': float(fp.edad_media), 'paro': r1(fp.paro_2021), 'poblacion': int(fp.poblacion),
        'izq_serie': {e: r1(fp[f'{e}_IZQ']) for e in CONGRESO}, 'izq_prov_serie': {e: r1(agregado(prov, e, 'IZQ')) for e in CONGRESO},
    }
    # lista más votada en las municipales de 2023 (ficheros por mesa de Interior), sobre voto válido
    ex = DATOS / 'extra'
    cm23 = pd.read_parquet(ex / 'raw_candidacies_M2023.parquet')
    vm23 = pd.read_parquet(ex / 'raw_candidacies_poll_M2023.parquet')
    mm23 = pd.read_parquet(ex / 'raw_poll_stations_M2023.parquet')
    sel = lambda t: t[(t.cod_INE_prov == '11') & (t.cod_INE_mun == '028')]
    lv = sel(vm23).groupby('id_candidacies').ballots.sum().sort_values(ascending=False)
    valido = lv.sum() + sel(mm23).blank_ballots.sum()
    C['puerto_real']['m2023_lista'] = cm23.set_index('id_candidacies').name_candidacies[lv.index[0]].strip().title().replace(' De ', ' de ').replace(' La ', ' la ').replace(' Para ', ' para ')
    C['puerto_real']['m2023_lista_pct'] = r1(lv.iloc[0] / valido)
    vec = d[(d.prov == '11') & (d.poblacion >= 20000)].sort_values('res_der')
    vec[['mun_code', 'municipio', 'poblacion', 'renta_uc', 'edad_media', 'paro_2021', '2023_07_DER', 'pred_der', 'res_der', '2023_07_PSOE', '2023_07_PP']].to_csv(OUT_CSV / 'puerto-real.csv', index=False)
    C['puerto_real']['bahia'] = [{'municipio': r.municipio, 'real': r1(r['2023_07_DER']), 'previsto': r1(r.pred_der), 'diferencia': r1(r.res_der),
                                  'renta': int(r.renta_uc)} for _, r in vec.iterrows()]
    big[['mun_code', 'municipio', 'prov', 'poblacion', '2023_07_DER', 'pred_der', 'res_der']].to_csv(OUT_CSV / 'modelo-municipal-2023.csv', index=False)

    # ---------------- A Illa / Vilanova (fronteras)
    a, b = fila(m, 'A Illa de Arousa'), fila(m, 'Vilanova de Arousa')
    C['arousa'] = {k: {'pp': {e: r1(x[f'{e}_PP']) for e in CONGRESO}, 'bng_m2023': r1(x.M2023_BNG), 'pp_m2023': r1(x.M2023_PP),
                       'psoe_2023': r1(x['2023_07_PSOE']), 'bng_2023': r1(x['2023_07_BNG']), 'renta': int(x.renta_uc), 'edad': float(x.edad_media),
                       'paro': r1(x.paro_2021), 'poblacion': int(x.poblacion), 'extranjeros': r1(x.extranjeros)} for k, x in (('illa', a), ('vilanova', b))}
    C['arousa']['brechas'] = {e: round(C['arousa']['vilanova']['pp'][e] - C['arousa']['illa']['pp'][e], 1) for e in CONGRESO}
    pd.DataFrame([{'eleccion': e, 'pp_a_illa': C['arousa']['illa']['pp'][e], 'pp_vilanova': C['arousa']['vilanova']['pp'][e]} for e in CONGRESO]).to_csv(OUT_CSV / 'a-illa-vilanova.csv', index=False)

    # ---------------- Cabra / Montilla (gemelos)
    a, b = fila(m, 'Cabra'), fila(m, 'Montilla')
    C['cabra_montilla'] = {k: {'der': {e: r1(x[f'{e}_DER']) for e in CONGRESO}, 'pp': {e: r1(x[f'{e}_PP']) for e in CONGRESO},
                               'psoe': {e: r1(x[f'{e}_PSOE']) for e in CONGRESO}, 'cs': {e: r1(x[f'{e}_CS']) for e in CONGRESO},
                               'vox': {e: r1(x[f'{e}_VOX']) for e in CONGRESO}, 'gana_2023': x['2023_07_gana'],
                               'renta': int(x.renta_uc), 'edad': float(x.edad_media), 'paro': r1(x.paro_2021), 'extranjeros': r1(x.extranjeros),
                               'estudios': r1(x.estudios_sup_2021), 'poblacion': int(x.poblacion)} for k, x in (('cabra', a), ('montilla', b))}
    pd.DataFrame([{'eleccion': e, **{f'{k}_{v}': C['cabra_montilla'][k][v][e] for k in ('cabra', 'montilla') for v in ('der', 'pp', 'psoe', 'cs', 'vox')}} for e in CONGRESO]).to_csv(OUT_CSV / 'cabra-montilla.csv', index=False)

    # ---------------- capitales frente al resto de su provincia
    filas = []
    for cod in CAPITALES:
        cap = m[m.mun_code == cod].iloc[0]
        resto = m[(m.prov == cod[:2]) & (m.mun_code != cod)]
        filas.append({'capital': cap.municipio, 'provincia': PROVINCIAS[cod[:2]], 'pp_capital': r1(cap['2023_07_PP']),
                      'pp_resto': r1(agregado(resto, '2023_07', 'PP')), 'psoe_capital': r1(cap['2023_07_PSOE']), 'psoe_resto': r1(agregado(resto, '2023_07', 'PSOE'))})
    cp = pd.DataFrame(filas)
    cp['dif_pp'] = (cp.pp_capital - cp.pp_resto).round(1)
    cp['dif_psoe'] = (cp.psoe_capital - cp.psoe_resto).round(1)
    cp = cp.sort_values('dif_pp')
    cp.to_csv(OUT_CSV / 'capitales-2023.csv', index=False)
    C['capitales'] = cp.to_dict('records')
    C['capitales_resumen'] = {'mas_pp': int((cp.dif_pp > 0).sum()), 'menos_pp': int((cp.dif_pp < 0).sum())}

    # ---------------- cinturón sur de Madrid
    mad = m[m.prov == '28']
    sur = ['Parla', 'Fuenlabrada', 'Leganés', 'Getafe', 'Alcorcón', 'Móstoles']
    no = ['Boadilla del Monte', 'Pozuelo de Alarcón', 'Majadahonda', 'Las Rozas de Madrid', 'Villanueva de la Cañada']
    C['madrid_sur'] = {'prov_pp': r1(agregado(mad, '2023_07', 'PP')), 'prov_psoe': r1(agregado(mad, '2023_07', 'PSOE')),
                       'municipios': []}
    for n in sur + no:
        x = fila(m, n)
        C['madrid_sur']['municipios'].append({'municipio': n, 'grupo': 'sur' if n in sur else 'noroeste', 'pp': r1(x['2023_07_PP']), 'psoe': r1(x['2023_07_PSOE']),
                                              'izq_2004': r1(x['2004_03_IZQ']), 'izq_2023': r1(x['2023_07_IZQ']), 'der_2023': r1(x['2023_07_DER']),
                                              'renta': int(x.renta_uc), 'gana': x['2023_07_gana'], 'poblacion': int(x.poblacion)})
    bo = d[d.municipio == 'Boadilla del Monte'].iloc[0]
    C['madrid_sur']['boadilla_previsto'] = r1(bo.pred_der)
    pd.DataFrame(C['madrid_sur']['municipios']).to_csv(OUT_CSV / 'madrid-sur-noroeste.csv', index=False)

    # ---------------- Badalona (voto doble)
    x = fila(m, 'Badalona')
    C['badalona'] = {e: {f: r1(x[f'{e}_{f}']) for f in ('PP', 'PSOE', 'SUMAR', 'CS', 'ERC', 'JUNTS', 'VOX', 'OTROS')} | {'part': r1(x[f'{e}_part'])}
                     for e in ('M2023', '2023_07', 'M2019', '2019_11', 'M2015', '2015_12')}
    pd.DataFrame([{'eleccion': e, **v} for e, v in C['badalona'].items()]).to_csv(OUT_CSV / 'badalona.csv', index=False)
    gap = m[m.poblacion >= 20000].copy()
    gap['dif_pp'] = gap.M2023_PP - gap['2023_07_PP']
    C['badalona']['rank_pp_20k'] = int((gap.dif_pp > gap.loc[gap.municipio == 'Badalona', 'dif_pp'].iloc[0]).sum()) + 1
    C['badalona']['n_20k'] = int(len(gap))
    C['badalona']['top'] = [{'municipio': r.municipio, 'provincia': PROVINCIAS[r.prov], 'pp_m2023': r1(r.M2023_PP), 'pp_g2023': r1(r['2023_07_PP']),
                             'dif': r1(r.dif_pp)} for _, r in gap.sort_values('dif_pp', ascending=False).head(6).iterrows()]

    # ---------------- paro, renta y participación (secciones de toda España)
    s = pd.read_csv(DATOS / 'secciones.csv', dtype={'tract_code': str, 'mun_code': str},
                    usecols=['tract_code', 'mun_code', 'renta_uc', 'edad_media', 'extranjeros', 'estudios_sup_2021', 'paro_2021', '2023_07_part', '2023_07_censo'])
    s = s.dropna().copy()
    s = s[s['2023_07_censo'] > 0]
    s['prov'] = s.tract_code.str[:2]
    s['lrenta'] = np.log(s.renta_uc)
    Xs = ['lrenta', 'paro_2021', 'estudios_sup_2021', 'edad_media', 'extranjeros']
    _, r2s, co = modelo(s, '2023_07_part', Xs, '2023_07_censo')
    _, r2r, co_r = modelo(s, '2023_07_part', ['lrenta'], '2023_07_censo')
    C['paro'] = {'n_secciones': int(len(s)), 'r2': round(r2s, 3), 'coef': {k: round(v * 100, 1) for k, v in co.items()},
                 'solo_renta': round(co_r['lrenta'] * 100, 1), 'r2_solo_renta': round(r2r, 3)}
    for var in ('renta_uc', 'paro_2021'):
        s['dec'] = pd.qcut(s[var], 10, labels=False) + 1
        g = s.groupby('dec').apply(lambda g: pd.Series({'part': g['2023_07_part'].mul(g['2023_07_censo']).sum() / g['2023_07_censo'].sum(),
                                                         'min': g[var].min(), 'max': g[var].max()}))
        C['paro'][f'deciles_{var}'] = [{'decil': int(k), 'part': r1(v.part), 'min': float(v['min']), 'max': float(v['max'])} for k, v in g.iterrows()]
    # a igual renta: participación por terciles de paro dentro de cada quintil de renta
    s['qr'] = pd.qcut(s.renta_uc, 5, labels=False) + 1
    s['tp'] = s.groupby('qr').paro_2021.transform(lambda x: pd.qcut(x, 3, labels=False) + 1)
    t = s.groupby(['qr', 'tp']).apply(lambda g: g['2023_07_part'].mul(g['2023_07_censo']).sum() / g['2023_07_censo'].sum()).unstack()
    C['paro']['quintil_renta_tercil_paro'] = {int(q): {int(k): r1(v) for k, v in row.items()} for q, row in t.iterrows()}
    t.reset_index().to_csv(OUT_CSV / 'participacion-renta-paro.csv', index=False)
    cat = json.load(open('/mnt/project-files/abstencion/municipales_parlament/resumen_hallazgos.json'))['regresion_seccion'] \
        if pathlib.Path('/mnt/project-files/abstencion/municipales_parlament/resumen_hallazgos.json').exists() else None
    if cat:
        C['paro']['cataluna'] = {e: {'paro': cat[e]['unemployment_rate'][0], 'renta': cat[e]['net_income_equiv'][0], 'r2': cat[e]['r2']}
                                 for e in ('g2023', 'm2023', 'p2024')}

    tanda2(m, d, C)
    (ATLAS / 'src' / 'cifras.json').write_text(json.dumps(C, ensure_ascii=False, indent=1, default=str))
    print('cifras.json escrito;', len(list(OUT_CSV.glob('*.csv'))), 'CSV')


# ---------------------------------------------------------------- segunda tanda (2026-10-07)
CENTROIDES = pathlib.Path(os.environ.get('ATLAS_CENTROIDES', '/mnt/project-files/generales/web/data/municipios.json'))


def km(a, b):
    """Distancia en km entre los centroides de dos términos municipales (códigos INE)."""
    j = json.load(open(CENTROIDES))
    c = dict(zip(j['cod'], j['c']))
    (lo1, la1), (lo2, la2) = c[a], c[b]
    x = np.radians(lo2 - lo1) * np.cos(np.radians((la1 + la2) / 2))
    return round(float(6371 * np.hypot(x, np.radians(la2 - la1))), 1)


def lista_ganadora(prov, mun, eleccion='M2023'):
    """Nombre y porcentaje (sobre voto válido) de la lista más votada en unas municipales, desde los ficheros por mesa."""
    ex = DATOS / 'extra'
    cand = pd.read_parquet(ex / f'raw_candidacies_{eleccion}.parquet')
    vot = pd.read_parquet(ex / f'raw_candidacies_poll_{eleccion}.parquet')
    mes = pd.read_parquet(ex / f'raw_poll_stations_{eleccion}.parquet')
    sel = lambda t: t[(t.cod_INE_prov == prov) & (t.cod_INE_mun == mun)]
    lv = sel(vot).groupby('id_candidacies').ballots.sum().sort_values(ascending=False)
    valido = lv.sum() + sel(mes).blank_ballots.sum()
    nombre = cand.set_index('id_candidacies').name_candidacies[lv.index[0]].strip()
    return nombre, r1(lv.iloc[0] / valido)


def perfil(m, d, code, familias=('PP', 'PSOE', 'SUMAR', 'VOX', 'DER', 'IZQ')):
    x = m[m.mun_code == code].iloc[0]
    y = d[d.mun_code == code]
    out = {'municipio': x.municipio, 'provincia': PROVINCIAS[x.prov], 'poblacion': int(x.poblacion), 'renta': int(x.renta_uc),
           'edad': float(x.edad_media), 'paro': r1(x.paro_2021), 'extranjeros': r1(x.extranjeros), 'estudios': r1(x.estudios_sup_2021),
           'gana': x['2023_07_gana'], 'part': r1(x['2023_07_part'])}
    for f in familias:
        out[f.lower()] = {e: r1(x[f'{e}_{f}']) for e in CONGRESO}
    for f in ('PNV', 'BILDU', 'BNG', 'OTROS'):
        out[f.lower() + '_2023'] = r1(x[f'2023_07_{f}'])
    out['m2023'] = {f.lower(): r1(x[f'M2023_{f}']) for f in ('PP', 'PSOE', 'SUMAR', 'VOX', 'PNV', 'BILDU', 'BNG', 'OTROS')} | {'part': r1(x.M2023_part), 'gana': x.M2023_gana}
    if len(y):
        out['previsto'], out['diferencia'] = r1(y.pred_der.iloc[0]), r1(y.res_der.iloc[0])
    return out


def tanda2(m, d, C):
    big = d[d.poblacion >= 10000].sort_values('res_der')
    rango = lambda code: int((big.res_der < big.loc[big.mun_code == code, 'res_der'].iloc[0]).sum()) + 1
    rango_alto = lambda code: int((big.res_der > big.loc[big.mun_code == code, 'res_der'].iloc[0]).sum()) + 1
    prov_serie = lambda p, f: {e: r1(agregado(m[m.prov == p], e, f)) for e in CONGRESO}
    fila_modelo = lambda r: {'municipio': r.municipio, 'real': r1(r['2023_07_DER']), 'previsto': r1(r.pred_der), 'diferencia': r1(r.res_der)}

    # ---- cuencas mineras asturianas
    cuencas = ['33031', '33037', '33060', '33032', '33002']
    C['cuencas'] = {'municipios': [perfil(m, d, c) | {'rango': rango(c) if c in set(big.mun_code) else None}
                                   | dict(zip(('m2023_lista', 'm2023_lista_pct'), lista_ganadora(c[:2], c[2:]))) for c in cuencas],
                    'asturias_der': prov_serie('33', 'DER'), 'asturias_izq': prov_serie('33', 'IZQ'),
                    'asturias_pp': r1(agregado(m[m.prov == '33'], '2023_07', 'PP')), 'asturias_psoe': r1(agregado(m[m.prov == '33'], '2023_07', 'PSOE'))}
    ast = d[(d.prov == '33') & (d.poblacion >= 9000)].sort_values('res_der')
    C['cuencas']['asturias_modelo'] = [fila_modelo(r) for _, r in ast.iterrows()]
    ast[['mun_code', 'municipio', 'poblacion', 'renta_uc', 'paro_2021', '2023_07_DER', 'pred_der', 'res_der', '2023_07_IZQ', '2004_03_IZQ']].to_csv(OUT_CSV / 'cuencas-mineras.csv', index=False)

    # ---- Lalín y Vilanova (excepciones al alza)
    top = big.sort_values('res_der', ascending=False)
    C['lalin'] = {'lalin': perfil(m, d, '36024'), 'vilanova': perfil(m, d, '36061'),
                  'rango_lalin': rango_alto('36024'), 'rango_vilanova': rango_alto('36061'),
                  'top': [fila_modelo(r) | {'provincia': PROVINCIAS[r.prov]} for _, r in top.head(10).iterrows()],
                  'pontevedra_pp': r1(agregado(m[m.prov == '36'], '2023_07', 'PP')),
                  'galicia_pp': r1(agregado(m[m.prov.isin(['15', '27', '32', '36'])], '2023_07', 'PP'))}
    top.head(10)[['mun_code', 'municipio', 'prov', 'poblacion', '2023_07_DER', 'pred_der', 'res_der']].to_csv(OUT_CSV / 'lalin-vilanova.csv', index=False)

    # ---- Cuenca de Pamplona (fronteras)
    cuenca = ['31201', '31076', '31907', '31901', '31060', '31086', '31016', '31258', '31902']
    pam = [perfil(m, d, c) for c in cuenca]
    C['pamplona'] = {'municipios': pam, 'km_cizur_zizur': km('31076', '31907'),
                     'navarra_der': r1(agregado(m[m.prov == '31'], '2023_07', 'DER'))}
    pd.DataFrame([{'municipio': p['municipio'], 'poblacion': p['poblacion'], 'renta': p['renta'], 'pp_upn': p['pp']['2023_07'], 'psoe': p['psoe']['2023_07'],
                   'sumar': p['sumar']['2023_07'], 'bildu': p['bildu_2023'], 'vox': p['vox']['2023_07'], 'derecha': p['der']['2023_07'],
                   'previsto': p.get('previsto'), 'diferencia': p.get('diferencia'), 'gana': p['gana']} for p in pam]).to_csv(OUT_CSV / 'cuenca-de-pamplona.csv', index=False)

    # ---- Getxo y Portugalete (fronteras)
    ria = ['48044', '48054', '48078', '48082', '48084', '48013']
    gx = [perfil(m, d, c) for c in ria]
    C['getxo'] = {'municipios': gx, 'km_getxo_portugalete': km('48044', '48078'),
                  'bizkaia': {f.lower(): r1(agregado(m[m.prov == '48'], '2023_07', f)) for f in ('PP', 'PSOE', 'PNV', 'BILDU', 'SUMAR')}}
    pd.DataFrame([{'municipio': p['municipio'], 'poblacion': p['poblacion'], 'renta': p['renta'], 'pnv': p['pnv_2023'], 'psoe': p['psoe']['2023_07'],
                   'pp': p['pp']['2023_07'], 'bildu': p['bildu_2023'], 'sumar': p['sumar']['2023_07'], 'gana': p['gana']} for p in gx]).to_csv(OUT_CSV / 'getxo-portugalete.csv', index=False)

    # ---- Aranda y Miranda (gemelos)
    C['aranda_miranda'] = {'aranda': perfil(m, d, '09018'), 'miranda': perfil(m, d, '09219'), 'burgos_der': prov_serie('09', 'DER'),
                           'rango_miranda': rango('09219'),
                           'burgos_mayores': m[m.prov == '09'].sort_values('poblacion', ascending=False).municipio.head(3).tolist()}
    pd.DataFrame([{'eleccion': e, **{f'{k}_{v}': C['aranda_miranda'][k][v][e] for k in ('aranda', 'miranda') for v in ('der', 'pp', 'psoe')}} for e in CONGRESO]).to_csv(OUT_CSV / 'aranda-miranda.csv', index=False)

    # ---- Los Palacios y Villafranca (el municipio que cambió)
    lp = perfil(m, d, '41069')
    lp['m2023_lista'], lp['m2023_lista_pct'] = lista_ganadora('41', '069')
    C['los_palacios'] = {'lp': lp, 'sevilla_der': prov_serie('41', 'DER'), 'sevilla_psoe': prov_serie('41', 'PSOE')}
    pd.DataFrame([{'eleccion': e, 'pp': lp['pp'][e], 'psoe': lp['psoe'][e], 'vox': lp['vox'][e], 'derecha': lp['der'][e], 'izquierda': lp['izq'][e],
                   'derecha_provincia': C['los_palacios']['sevilla_der'][e]} for e in CONGRESO]).to_csv(OUT_CSV / 'los-palacios.csv', index=False)

    # ---- Castro-Urdiales (contra su provincia)
    C['castro'] = {'castro': perfil(m, d, '39020'), 'rango': rango('39020'), 'cantabria_der': prov_serie('39', 'DER'),
                   'cantabria_pp': r1(agregado(m[m.prov == '39'], '2023_07', 'PP')), 'cantabria_psoe': r1(agregado(m[m.prov == '39'], '2023_07', 'PSOE')),
                   'km_castro_bizkaia': None}
    pd.DataFrame([{'eleccion': e, 'derecha_castro': C['castro']['castro']['der'][e], 'derecha_cantabria': C['castro']['cantabria_der'][e],
                   'psoe_castro': C['castro']['castro']['psoe'][e], 'pp_castro': C['castro']['castro']['pp'][e]} for e in CONGRESO]).to_csv(OUT_CSV / 'castro-urdiales.csv', index=False)

    # ---- Vigo (contra su provincia)
    gal = m[m.prov.isin(['15', '27', '32', '36'])]
    g20 = gal[gal.poblacion >= 20000]
    C['vigo'] = {'vigo': perfil(m, d, '36057'), 'galicia': {f.lower(): r1(agregado(gal, '2023_07', f)) for f in ('PP', 'PSOE', 'BNG', 'SUMAR')},
                 'n_20k': int(len(g20)), 'psoe_gana_20k': sorted(g20[g20['2023_07_gana'] == 'PSOE'].municipio.tolist()),
                 'ciudades': [{'municipio': r.municipio, 'pp': r1(r['2023_07_PP']), 'psoe': r1(r['2023_07_PSOE']), 'gana': r['2023_07_gana']}
                              for _, r in gal[gal.poblacion >= 60000].sort_values('poblacion', ascending=False).iterrows()]}
    pd.DataFrame(C['vigo']['ciudades']).to_csv(OUT_CSV / 'vigo-galicia.csv', index=False)

    # ---- pueblos pequeños: participación municipal y general por tamaño
    bins = [0, 100, 250, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 10 ** 8]
    etiq = ['<100', '100-249', '250-499', '500-999', '1.000-1.999', '2.000-4.999', '5.000-9.999', '10.000-19.999', '20.000-49.999', '50.000-99.999', '100.000+']
    x = m.dropna(subset=['M2023_part', '2023_07_part']).copy()
    x['tam'] = pd.cut(x.poblacion, bins, right=False, labels=etiq)
    tam = []
    for t, g in x.groupby('tam', observed=True):
        tam.append({'tamano': str(t), 'municipios': int(len(g)), 'part_municipales': r1(g.M2023_votantes.sum() / g.M2023_censo.sum()),
                    'part_generales': r1(g['2023_07_votantes'].sum() / g['2023_07_censo'].sum()),
                    'pct_mas_municipales': r1((g.M2023_part > g['2023_07_part']).mean())})
    C['pequenos'] = {'tamanos': tam, 'n': int(len(x)), 'n_mas_municipales': int((x.M2023_part > x['2023_07_part']).sum()),
                     'n_menos_2000': int((x.poblacion < 2000).sum()),
                     'n_menos_2000_mas_mun': int(((x.poblacion < 2000) & (x.M2023_part > x['2023_07_part'])).sum()),
                     'total_municipales': r1(x.M2023_votantes.sum() / x.M2023_censo.sum()),
                     'total_generales': r1(x['2023_07_votantes'].sum() / x['2023_07_censo'].sum()),
                     'n_mas_20000': int((x.poblacion >= 20000).sum()),
                     'n_mas_20000_mas_mun': int(((x.poblacion >= 20000) & (x.M2023_part > x['2023_07_part'])).sum())}
    pd.DataFrame(tam).to_csv(OUT_CSV / 'participacion-por-tamano.csv', index=False)


if __name__ == '__main__':
    main()
