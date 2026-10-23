"""Cifras de la pieza de la provincia de Girona (girona.html y girona-ca.html).

Lee los datos de toda Cataluña que ya usa la pieza catalana, se queda con las 536 secciones de la provincia
de Girona (código 17) y escribe src/girona/resumen.json, que src/girona/construir.py incrusta en las páginas.

Uso: python3 src/girona/datos.py DIR_IRRV SECCIONES_2019_2024
  DIR_IRRV: carpeta con irrv_<elección>.csv de Transparència Catalunya (dataset irrv-2mfc, todos los niveles)
  SECCIONES_2019_2024: secciones_elecciones_2019_2024.csv (municipales 2023 y Parlament 2024 por sección)
Comarcas: src/girona/comarcas.json (Idescat, api.idescat.cat/emex/v1/nodes.json?tipus=com,mun).
Votos nulos y en blanco: raw_poll_stations_congress_<elección>.parquet de pollspaindata (inst/extdata), en la carpeta
de la variable POLLSPAIN (por defecto /tmp/pollspaindata/inst/extdata). Si no está, ese bloque se salta.
"""
import os, sys, json, pathlib
import numpy as np, pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
OUT = ROOT / 'src' / 'girona' / 'resumen.json'
IRRV = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('/mnt/project-files/verificacion/fuentes/transparencia')
ELEC = sys.argv[2] if len(sys.argv) > 2 else '/mnt/project-files/abstencion/municipales_parlament/secciones_elecciones_2019_2024.csv'
EL = ['M20151', 'A20151', 'G20151', 'G20161', 'A20171', 'G20191', 'M20191', 'G20192', 'A20211', 'M20231', 'G20231', 'A20241']
HIST = ['t2015_12', 't2016_06', 't2019_04', 't2019_11', 't2023_07']

cat = pd.read_csv(ROOT / 'data' / 'catalunya_secciones_2023.csv', dtype={'tract_code': str, 'mun_code': str})
cat['prov'] = cat.tract_code.str[:2]
g = cat[cat.prov == '17'].copy()
COM = json.load(open(ROOT / 'src' / 'girona' / 'comarcas.json'))
g['com'] = g.mun_code.map(COM)
popm = g.groupby('mun_code').population.sum()
R = {}


def tot(x):
    return dict(adults=float(x.adults.sum()), electorate=float(x.electorate.sum()), voters=float(x.voters.sum()), sin=float(x.sin_derecho.sum()))


def hist(x):
    return [float((x[c] * x.electorate).sum() / x.dropna(subset=[c]).electorate.sum()) for c in HIST]


def grp(x, name):
    w = x.population
    avg = lambda c: float(np.average(x[c].fillna(x[c].mean()), weights=w))
    return dict(name=name, pop=float(x.population.sum()), turnout=x.voters.sum() / x.electorate.sum(), vota=x.voters.sum() / x.adults.sum(),
                sin=x.sin_derecho.sum() / x.adults.sum(), income=avg('net_income_equiv'), foreign=avg('pct_foreign'), age=avg('mean_age'),
                univ=avg('pct_higher_ed_completed'), hist=hist(x))


# ---- totales: provincia, Cataluña y las cuatro provincias
R['totals'] = tot(g)
R['cat'] = dict(tot(cat), turnout=cat.voters.sum() / cat.electorate.sum(), vota=cat.voters.sum() / cat.adults.sum(), sin=cat.sin_derecho.sum() / cat.adults.sum())
R['provincias'] = {p: dict(turnout=x.voters.sum() / x.electorate.sum(), vota=x.voters.sum() / x.adults.sum(), sin=x.sin_derecho.sum() / x.adults.sum(),
                           hist=hist(x), drop=hist(x)[3] - x.voters.sum() / x.electorate.sum()) for p, x in cat.groupby('prov')}

# ---- tabla de municipios
TOWNS = ['Salt', 'Lloret de Mar', "Castelló d'Empúries", 'Figueres', 'Olot', 'Girona', 'Banyoles']
rural = g[g.mun_code.map(popm) < 2000]
R['compare'] = [grp(g[g.mun_name == m], m) for m in TOWNS] + [grp(rural, 'Pueblos de menos de 2.000 hab.'), grp(g, 'Provincia de Girona')]
R['compare'][len(TOWNS)]['n'] = int(rural.mun_code.nunique())
R['compare'].append(dict(grp(cat, 'Cataluña')))

# ---- municipios: ranking por adultos que votan (más de 10.000 habitantes)
m = g.groupby(['mun_code', 'mun_name']).agg(pop=('population', 'sum'), ad=('adults', 'sum'), el=('electorate', 'sum'), vo=('voters', 'sum'), sin=('sin_derecho', 'sum')).reset_index()
m['vota'] = m.vo / m.ad; m['sinp'] = m.sin / m.ad; m['t'] = m.vo / m.el
R['muni10k'] = m[m['pop'] > 10000].sort_values('vota')[['mun_name', 'pop', 'vota', 'sinp', 't']].to_dict('records')
R['n_mun'] = int(g.mun_code.nunique()); R['n_sec'] = len(g)

# ---- comarcas
R['comarcas'] = {k: dict(pop=float(x.population.sum()), turnout=x.voters.sum() / x.electorate.sum(), vota=x.voters.sum() / x.adults.sum(),
                         sin=x.sin_derecho.sum() / x.adults.sum(), hist=hist(x), drop=hist(x)[3] - x.voters.sum() / x.electorate.sum(),
                         indep19=float(np.average(x.indep_share19.dropna(), weights=x.dropna(subset=['indep_share19']).electorate)))
                 for k, x in g.groupby('com')}


# ---- quintiles por variable
def q(c, n=5):
    out = []
    for _, x in g.groupby(pd.qcut(g[c], n, labels=False)):
        out.append(dict(lo=float(x[c].min()), hi=float(x[c].max()), turnout=x.voters.sum() / x.electorate.sum(), vota=x.voters.sum() / x.adults.sum(),
                        sin=x.sin_derecho.sum() / x.adults.sum(), n=len(x)))
    return out


R['quint'] = {c: q(c) for c in ['net_income_equiv', 'pct_foreign', 'pct_higher_ed_completed', 'unemployment_rate', 'mean_age']}

# ---- modelo: MCO ponderada por censo, variables estandarizadas, IC bootstrap (igual que la pieza catalana)
X = ['pct_higher_ed_completed', 'unemployment_rate', 'mean_age', 'pct_foreign', 'pct_secondary', 'pct_naturalized', 'pct_rented', 'net_income_equiv']
d = g.dropna(subset=X + ['turnout']); Z = (d[X] - d[X].mean()) / d[X].std(); Z.insert(0, 'c', 1); W = np.sqrt(d.electorate.values)
A, y = Z.values * W[:, None], d.turnout.values * W
b, *_ = np.linalg.lstsq(A, y, rcond=None)
rng = np.random.default_rng(1)
bs = [np.linalg.lstsq(A[ix], y[ix], rcond=None)[0] for ix in [rng.integers(0, len(d), len(d)) for _ in range(500)]]
se = np.std(bs, axis=0); pred = Z.values @ b
r2 = 1 - ((d.turnout - pred) ** 2 * d.electorate).sum() / (((d.turnout - np.average(d.turnout, weights=d.electorate)) ** 2) * d.electorate).sum()
order = np.argsort(-np.abs(b[1:]))
R['reg'] = dict(r2=float(r2), n=len(d), coef=[dict(var=X[i], b=float(b[i + 1] * 100), se=float(se[i + 1] * 100), sd=float(d[X[i]].std())) for i in order])
R['corr'] = {v: float(g[[v, 'turnout']].corr().iloc[0, 1]) for v in X}


# ---- comprobación del modelo: efectos fijos de comarca o de municipio y errores agrupados por municipio
def ols_fe(fe):
    D = pd.get_dummies(d[fe], drop_first=True, dtype=float)
    M = np.column_stack([Z.values, D.values]); Aw = M * W[:, None]
    bb, *_ = np.linalg.lstsq(Aw, y, rcond=None)
    u = (d.turnout.values - M @ bb) * W
    inv = np.linalg.pinv(Aw.T @ Aw); cl = pd.factorize(d.mun_code)[0]; G = cl.max() + 1
    S = np.zeros_like(inv)
    for k in range(G):
        sk = Aw[cl == k].T @ u[cl == k]; S += np.outer(sk, sk)
    V = inv @ S @ inv * G / (G - 1) * (len(d) - 1) / (len(d) - M.shape[1])
    return [dict(var=X[i], b=float(bb[i + 1] * 100), se=float(np.sqrt(V[i + 1, i + 1]) * 100)) for i in range(len(X))]
d = d.assign(com=d.mun_code.map(COM))
R['reg_fe'] = {'comarca': ols_fe('com'), 'municipio': ols_fe('mun_code')}

# ---- Girona frente a otras ciudades catalanas: participación del quintil de renta más pobre y más rico
R['ciudades_quint'] = {}
for c in ['Barcelona', 'Girona', 'Lleida', 'Tarragona', 'Reus', 'Sabadell', 'Terrassa']:
    x = cat[cat.mun_name == c].dropna(subset=['net_income_equiv'])
    t = x.groupby(pd.qcut(x.net_income_equiv, 5, labels=False)).apply(lambda z: z.voters.sum() / z.electorate.sum())
    R['ciudades_quint'][c] = dict(q1=float(t.iloc[0]), q5=float(t.iloc[-1]), n=len(x))

# ---- caída 2019 → 2023 por cuartil de voto independentista
R['indep'] = [dict(lo=float(x.indep_share19.min()), hi=float(x.indep_share19.max()), t19=float((x.t2019_11 * x.electorate).sum() / x.dropna(subset=['t2019_11']).electorate.sum()),
                   t23=float(x.voters.sum() / x.electorate.sum())) for _, x in g.dropna(subset=['indep_share19']).groupby(pd.qcut(g.indep_share19, 4, labels=False))]
R['drop_total'] = hist(g)[3] - g.voters.sum() / g.electorate.sum()
# ---- 2019 → 2023: votos nulos y en blanco por cuartil de voto independentista (cuentan como participación)
PS = pathlib.Path(os.environ.get('POLLSPAIN', '/tmp/pollspaindata/inst/extdata'))
if (PS / 'raw_poll_stations_congress_2023_07.parquet').exists():
    gi4 = g.dropna(subset=['indep_share19']).set_index('tract_code')
    q4 = pd.qcut(gi4.indep_share19, 4, labels=False)
    R['nulos'] = {}
    for k in ['2019_11', '2023_07']:
        p = pd.read_parquet(PS / f'raw_poll_stations_congress_{k}.parquet'); p = p[p.cod_INE_prov == '17']
        p['tract_code'] = p.cod_INE_prov + p.cod_INE_mun + p.cod_mun_district + p.cod_sec
        s_ = p.groupby('tract_code')[['blank_ballots', 'invalid_ballots', 'census_counting']].sum().reindex(gi4.index)
        z = pd.DataFrame({'nb': s_.blank_ballots + s_.invalid_ballots, 'c': s_.census_counting, 'q': q4}).dropna().groupby('q').sum()
        R['nulos'][k] = [float(v) for v in z.nb / z.c]

R['indep19'] = float(np.average(g.indep_share19.dropna(), weights=g.dropna(subset=['indep_share19']).electorate))

# ---- historia por tamaño de municipio (generales, secciones con el mismo código)
g['size'] = pd.cut(g.mun_code.map(popm), [0, 2000, 10000, 30000, 1e7], labels=['< 2.000', '2.000–10.000', '10.000–30.000', '> 30.000'])
R['size_hist'] = {str(k): hist(x) for k, x in g.groupby('size', observed=True)}

# ---- secciones con menos participación
R['low'] = g[g.electorate > 300].sort_values('turnout').head(10)[['tract_code', 'mun_name', 'turnout', 'pct_ad_vota', 'pct_ad_sinderecho', 'net_income_equiv',
                                                                  'pct_foreign', 'pct_higher_ed_completed', 'unemployment_rate', 'electorate']].to_dict('records')
# la sección más baja: menores, mayores y en cuántas de las 12 elecciones es la que menos vota de la provincia
ev0 = pd.read_csv(ROOT / 'data' / 'evolucion_secciones.csv', dtype={'tract_code': str}).set_index('tract_code')
ev0 = ev0[ev0.index.str[:2] == '17']
lo = g.set_index('tract_code').loc[R['low'][0]['tract_code']]
R['low_perfil'] = dict(tract_code=lo.name, population=float(lo.population), pct_under18=float(lo.pct_under18), pct_over65=float(lo.pct_over65),
                       rank=[int(ev0[c].rank()[lo.name]) for c in EL], n_elec=len(EL))

# ---- ciudad de Girona: quintiles de renta dentro de la ciudad
gi = g[g.mun_name == 'Girona']
R['girona_quint'] = [dict(lo=float(x.net_income_equiv.min()), hi=float(x.net_income_equiv.max()), turnout=x.voters.sum() / x.electorate.sum(), n=len(x))
                     for _, x in gi.groupby(pd.qcut(gi.net_income_equiv, 5, labels=False))]
R['girona_range'] = dict(min=float(gi.turnout.min()), max=float(gi.turnout.max()), n=len(gi))

# ---- municipales 2023 y Parlament 2024
e = pd.read_csv(ELEC, dtype={'tract_code': str, 'mun_code': str})
e = e[e.tract_code.str[:2] == '17'].copy()
def part(x, k): y = x.dropna(subset=[f'cens_{k}', f'vot_{k}']); return float(y[f'vot_{k}'].sum() / y[f'cens_{k}'].sum())
R['elec'] = {k: part(e, k) for k in ['m2023', 'g2023', 'p2024']}
ec = pd.read_csv(ELEC, dtype={'tract_code': str})
R['elec_cat'] = {k: float(ec[f'vot_{k}'].sum() / ec[f'cens_{k}'].sum()) for k in ['m2023', 'g2023', 'p2024']}
e['ad'] = e.adults
def mstats(x):
    return dict(pop=float(x.population.sum()), m23=part(x, 'm2023'), g23=part(x, 'g2023'), p24=part(x, 'p2024'),
                sin_g=float(np.clip(x.ad - x.cens_g2023, 0, None).sum() / x.ad.sum()), sin_m=float(np.clip(x.ad - x.cens_m2023, 0, None).sum() / x.ad.sum()),
                ue=float(x.ue_censo_mun_aprox.sum()), ue_share=float(x.ue_censo_mun_aprox.sum() / x.cens_m2023.sum()), vota_m=float(x.vot_m2023.sum() / x.ad.sum()))
e['size'] = pd.cut(e.mun_code.map(popm), [0, 2000, 10000, 30000, 1e7], labels=['< 2.000', '2.000–10.000', '10.000–30.000', '> 30.000'])
R['mun_size'] = {str(k): dict(mstats(x), n=int(x.mun_code.nunique())) for k, x in e.groupby('size', observed=True)}
R['mun_towns'] = {t: mstats(e[e.mun_name == t]) for t in TOWNS + ['Roses', "Castell d'Aro, Platja d'Aro i s'Agaró", "Escala, L'", 'Torroella de Montgrí', 'Puigcerdà']}
R['mun_prov'] = mstats(e)
R['perfil_towns'] = {t: dict(under18=float(np.average(x.pct_under18, weights=x.population)), single_hh=float(np.average(x.pct_single_hh, weights=x.population)))
                     for t, x in g[g.mun_name.isin(['Salt', 'Lloret de Mar'])].groupby('mun_name')}
dq = pd.qcut(e.net_income_equiv, 10, labels=False)
R['deciles'] = [dict(d=int(k) + 1, lo=float(x.net_income_equiv.min()), hi=float(x.net_income_equiv.max()), g=round(part(x, 'g2023'), 3),
                     m=round(part(x, 'm2023'), 3), p=round(part(x, 'p2024'), 3)) for k, x in e.groupby(dq)]

# ---- evolución 2015-2024: participación de la provincia en cada elección y por quintil de renta
ev = pd.read_csv(ROOT / 'data' / 'evolucion_secciones.csv', dtype={'tract_code': str}).set_index('tract_code')
ev = ev[ev.index.str[:2] == '17']


def load(c):
    x = pd.read_csv(IRRV / f'irrv_{c}.csv', dtype={'territori_codi': str, 'id_nivell_territorial': str})
    x = x[(x.id_nivell_territorial == 'SE') & ~x.territori_nom.astype(str).str.startswith('Residents')]
    x['tract'] = x.territori_codi.str.zfill(5) + x.districte.astype(int).astype(str).str.zfill(2) + x.seccio.astype(int).astype(str).str.zfill(3)
    return x.groupby('tract')[['cens_electoral', 'votants']].sum()


prov, cens = {}, {}
for c in EL:
    x = load(c); x = x[x.index.str[:2] == '17']
    prov[c] = round(float(x.votants.sum() / x.cens_electoral.sum()), 4)
    cens[c] = x.cens_electoral
C = pd.DataFrame(cens).reindex(ev.index)
qi = pd.qcut(g.set_index('tract_code').net_income_equiv.reindex(ev.index), 5, labels=False)
R['evo_prov'] = [prov[c] for c in EL]
R['evo_q'] = []
for c in EL:
    z = pd.DataFrame({'v': ev[c] * C[c], 'w': C[c], 'q': qi}).dropna().groupby('q').sum()
    R['evo_q'].append([round(float(v), 4) for v in z.v / z.w])
R['evo_drop'] = {}
for a, bb in [('A20151', 'A20241'), ('A20211', 'A20241')]:
    dd = (ev[bb] - ev[a]).dropna(); qq = qi.reindex(dd.index)
    R['evo_drop'][a + '_' + bb] = dict(share_down=float((dd < 0).mean()), share_up=float((dd > 0).mean()), n=len(dd),
                                       med_q1=float(dd[qq == 0].median()), med_q5=float(dd[qq == 4].median()))

json.dump(R, open(OUT, 'w'), ensure_ascii=False, indent=1, default=float)
pr = lambda *a: print(*a)
pr('Girona', {k: round(v, 4) for k, v in R['totals'].items()}, 'vota', round(R['totals']['voters'] / R['totals']['adults'], 4), 'sin', round(R['totals']['sin'] / R['totals']['adults'], 4), 't', round(R['totals']['voters'] / R['totals']['electorate'], 4))
pr('prov', {k: (round(v['vota'], 3), round(v['sin'], 3), round(v['turnout'], 3), round(v['drop'], 3)) for k, v in R['provincias'].items()})
pr('reg', round(R['reg']['r2'], 3), R['reg']['n'], [(c['var'], round(c['b'], 2), round(c['se'], 2)) for c in R['reg']['coef']])
pr('indep', [(round(d['lo'], 3), round(d['hi'], 3), round(d['t19'], 3), round(d['t23'], 3)) for d in R['indep']], 'drop', round(R['drop_total'], 4), 'ind19', round(R['indep19'], 3))
pr('size', {k: [round(v, 3) for v in h] for k, h in R['size_hist'].items()})
pr('girona city quint', [(d['lo'], round(d['turnout'], 3), d['n']) for d in R['girona_quint']], R['girona_range'])
pr('elec', R['elec'], R['elec_cat'])
pr('mun_size', json.dumps(R['mun_size'], ensure_ascii=False))
pr('towns', json.dumps({k: {a: round(b, 3) for a, b in v.items()} for k, v in R['mun_towns'].items()}, ensure_ascii=False))
pr('prov m', {a: round(b, 4) for a, b in R['mun_prov'].items()})
pr('deciles', [(d['d'], d['g'], d['m'], d['p']) for d in R['deciles']])
pr('evo', R['evo_prov']); pr('evo q', R['evo_q']); pr('evo drop', R['evo_drop'])
pr('comarcas', json.dumps({k: {a: (round(b, 3) if not isinstance(b, list) else None) for a, b in v.items()} for k, v in R['comarcas'].items()}, ensure_ascii=False))
pr('muni10k', [(r['mun_name'], round(r['vota'], 3), round(r['sinp'], 3), round(r['t'], 3)) for r in R['muni10k']])
pr('reg_fe', {k: [(c['var'], round(c['b'], 2), round(c['se'], 2)) for c in v] for k, v in R['reg_fe'].items()})
pr('ciudades_quint', {k: (round(v['q1'], 3), round(v['q5'], 3), v['n']) for k, v in R['ciudades_quint'].items()})
pr('low_perfil', R['low_perfil']); pr('perfil_towns', R['perfil_towns']); pr('nulos', R.get('nulos'))
pr('compare', [(c['name'], round(c['vota'], 3), round(c['sin'], 3), round(c['turnout'], 3), round(c['income']), round(c['foreign'], 3), round(c['univ'], 3), [round(h, 3) for h in c['hist']]) for c in R['compare']])
