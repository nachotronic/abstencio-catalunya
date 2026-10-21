"""Cambio de voto según el perfil, con los microdatos del CIS, y su traslado a cada sección censal.

Idea: no todos los barrios se mueven igual. En una encuesta, para cada partido se compara la intención de voto
(voto + simpatía, VOTOSIMG) con el recuerdo de voto de las anteriores generales (RECUVOTOG) por perfil: edad
(65 años o más), estudios superiores y tamaño del municipio (TAMUNI, 7 tramos). Un modelo log-lineal de Poisson
(intención ~ perfil, con el recuerdo como exposición) da cuánto crece o cae el partido en cada perfil respecto a su
media. Después, cada sección recibe el factor que le toca por su composición (proporción de mayores de 65 entre los
adultos, de titulados superiores y tamaño de su municipio), y el voto nacional se mantiene igual.

Limitaciones: solo tres rasgos, combinados como si fueran independientes dentro de la sección (no hay tablas
cruzadas por sección); el recuerdo de voto del CIS tiene sesgos conocidos; la edad solo distingue 65+.

Uso:  python3 previsiones/src/perfiles.py   (valida 2019 -> 2023 con el CIS 3411 y calcula los factores de 2026)
Lee los .sav del CIS de $CIS_DIR (por defecto ~/cis/s<estudio>/), descargables en
https://www.cis.es/documents/d/cis/MD<estudio>-zip (o MD<estudio> en estudios antiguos).
"""
import glob, json, os, pathlib
import numpy as np
import pandas as pd
import pyreadstat

RAIZ = pathlib.Path(__file__).resolve().parents[2]
CIS = pathlib.Path(os.environ.get('CIS_DIR', os.path.expanduser('~/cis')))
BASE = pathlib.Path(os.environ.get('PREVISIONES_BASE', '/mnt/project-files/previsiones/base'))
# provincia INE -> comunidad en la codificación del CIS (1 Andalucía ... 19 Melilla)
_CC = {1: '04 11 14 18 21 23 29 41', 2: '22 44 50', 3: '33', 4: '07', 5: '35 38', 6: '39', 7: '02 13 16 19 45',
       8: '05 09 24 34 37 40 42 47 49', 9: '08 17 25 43', 10: '03 12 46', 11: '06 10', 12: '15 27 32 36', 13: '28',
       14: '30', 15: '31', 16: '01 20 48', 17: '26', 18: '51', 19: '52'}
PROV_CCAA = {p: c for c, ps in _CC.items() for p in ps.split()}
TRAMOS = [2000, 10000, 50000, 100000, 400000, 1000000]   # cortes de TAMUNI

# códigos CIS -> familia
REC19 = {1: 'PSOE', 2: 'PP', 3: 'VOX', 4: 'SUMAR', 903: 'SUMAR', 1202: 'SUMAR', 7: 'SUMAR', 1001: 'SUMAR', 5: 'CS'}
INT23 = {1: 'PSOE', 2: 'PP', 3: 'VOX', 21: 'SUMAR', 4: 'SUMAR', 8: 'SUMAR', 7: 'SUMAR', 903: 'SUMAR', 1202: 'SUMAR',
         1301: 'SUMAR', 1001: 'SUMAR', 1004: 'SUMAR', 5: 'CS'}
REC23 = {1: 'PSOE', 2: 'PP', 3: 'VOX', 21: 'SUMAR'}
INT26 = {1: 'PSOE', 2: 'PP', 3: 'VOX', 21: 'SUMAR', 8: 'SUMAR', 4: 'SUMAR'}   # espacio Sumar + Podemos junto


def lee(estudio):
    sav = glob.glob(str(CIS / f's{estudio}' / '**' / '*.sav'), recursive=True)[0]
    df, _ = pyreadstat.read_sav(sav, usecols=['EDAD', 'TAMUNI', 'ESTUDIOS', 'PESO', 'RECUVOTOG', 'VOTOSIMG', 'CCAA'])
    df = df[df.TAMUNI.between(1, 7) & df.EDAD.between(18, 110)].copy()
    df['m65'] = (df.EDAD >= 65).astype(int)
    df['sup'] = (df.ESTUDIOS == 6).astype(int)
    df['hab'] = df.TAMUNI.astype(int)
    df['PESO'] = df.PESO.fillna(1)
    df['ccaa'] = df.CCAA.fillna(13).astype(int)
    return df


def ajusta(df, rec, inten, partidos, ccaa=True):
    """Coeficientes log-lineales por partido: {partido: {'m65', 'sup', 'hab': [7], 'ccaa': [19]}} (primer nivel = 0).
    Con ccaa=True se añade la comunidad autónoma (código CIS 1-19) como efecto fijo."""
    df = df.assign(r=df.RECUVOTOG.map(rec), i=df.VOTOSIMG.map(inten))
    claves = ['m65', 'sup', 'hab', 'ccaa']
    celdas = df.groupby(claves).size().index
    X = np.array([[1, a, s] + [int(h == k) for k in range(2, 8)] + ([int(c == k) for k in range(2, 20)] if ccaa else [])
                  for a, s, h, c in celdas], float)
    out = {}
    for p in partidos:
        y = df[df.i == p].groupby(claves).PESO.sum().reindex(celdas, fill_value=0).values
        e = df[df.r == p].groupby(claves).PESO.sum().reindex(celdas, fill_value=0).values + 0.5
        b = np.zeros(X.shape[1]); b[0] = np.log(y.sum() / e.sum())
        for _ in range(50):   # IRLS de Poisson con exposición e
            mu = e * np.exp(X @ b)
            H = X.T @ (X * mu[:, None]) + np.eye(len(b)) * 1.0   # leve contracción hacia 0
            H[0, 0] -= 1.0
            paso = np.linalg.solve(H, X.T @ (y - mu) - np.r_[0, b[1:]])
            b += paso
            if np.abs(paso).max() < 1e-8:
                break
        out[p] = {'m65': float(b[1]), 'sup': float(b[2]), 'hab': [0.0] + [float(v) for v in b[3:9]],
                  'ccaa': [0.0] + [float(v) for v in b[9:]] if ccaa else [0.0] * 19}
    return out


def covariables():
    s = pd.read_csv(RAIZ / 'generales-2026/descargas/secciones.csv', dtype={'tract_code': str, 'mun_code': str},
                    usecols=['tract_code', 'mun_code', 'poblacion', 'menores18', 'mayores65', 'estudios_sup_2021'])
    s['a65'] = (s.mayores65 / (1 - s.menores18)).clip(0, 1)
    s['sup'] = s.estudios_sup_2021.clip(0, 1)
    pob = s.groupby('mun_code').poblacion.sum()
    s['hab'] = np.searchsorted(TRAMOS, s.mun_code.map(pob).values, side='left') + 1
    for c in ('a65', 'sup'):   # secciones sin dato: media de su municipio, y si no, de España
        s[c] = s[c].fillna(s.groupby('mun_code')[c].transform('mean')).fillna(s[c].mean())
    s['ccaa'] = s.tract_code.str[:2].map(PROV_CCAA)
    return s.set_index('tract_code')[['a65', 'sup', 'hab', 'ccaa']]


def factores(coef, cov):
    out = {}
    for p, c in coef.items():
        f = ((1 - cov.a65) + cov.a65 * np.exp(c['m65'])) * ((1 - cov.sup) + cov.sup * np.exp(c['sup']))
        out[p] = f * np.exp(np.array(c['hab'])[cov.hab.values - 1]) * np.exp(np.array(c['ccaa'])[cov.ccaa.values - 1])
    return pd.DataFrame(out, index=cov.index)


def ipf(v, filas, cols, n=30):
    """Ajusta la matriz sección × partido a los totales de cada sección y de cada partido en España."""
    v = v.copy()
    for _ in range(n):
        v = v.mul(cols / v.sum(), axis=1)
        v = v.mul(filas / v.sum(axis=1), axis=0)
    return v


def valida():
    """2019 -> 2023: ¿reparte mejor el voto por sección el cambio por perfil que la subida proporcional uniforme?"""
    g = pd.read_csv(RAIZ / 'generales-2026/descargas/resultados_secciones_largo.csv', dtype={'tract_code': str})
    fam = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS']
    resto = ['ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC', 'OTROS', 'UPYD', 'UCD', 'CDS']
    a = g[g.eleccion == '2019_11'].set_index('tract_code'); b = g[g.eleccion == '2023_07'].set_index('tract_code')
    idx = a.index.intersection(b.index)
    a, b = a.loc[idx], b.loc[idx]
    va = a[fam].assign(RESTO=a[resto].sum(axis=1)); vb = b[fam].assign(RESTO=b[resto].sum(axis=1))
    filas, cols = vb.sum(axis=1), vb.sum()
    cov = covariables().reindex(idx)
    cov = cov.fillna({'a65': cov.a65.mean(), 'sup': cov.sup.mean(), 'hab': 3})
    cov['ccaa'] = pd.Series(idx.str[:2], index=idx).map(PROV_CCAA)
    cov = cov.astype({'hab': int, 'ccaa': int})
    cis = lee('3411')
    ok = filas > 0
    uni = ipf(va[ok] + 0.01, filas[ok], cols)
    real = vb[ok].div(filas[ok], axis=0) * 100
    pruebas = [('uniforme', uni)]
    for nom, cc in (('perfil', False), ('perfil+ccaa', True)):
        coef = ajusta(cis, REC19, INT23, ['PP', 'PSOE', 'VOX', 'SUMAR'], ccaa=cc)   # Cs no se presentó en 2023
        f = factores(coef, cov).assign(CS=1.0, RESTO=1.0)
        pruebas.append((nom, ipf((va[ok] + 0.01) * f[ok], filas[ok], cols)))
    res = {}
    for nom, pr in pruebas:
        e = (pr.div(filas[ok], axis=0) * 100 - real).abs()
        res[nom] = {p: round(float(np.average(e[p], weights=filas[ok])), 2) for p in fam if p != 'CS'}
        res[nom]['media'] = round(float(np.mean(list(res[nom].values()))), 2)
    return coef, res


def main():
    global CON_CCAA
    coef19, res = valida()
    CON_CCAA = res['perfil+ccaa']['media'] < res['perfil']['media']
    print('Validación 2019 -> 2023, error medio por sección (puntos, ponderado por votos):')
    for k, v in res.items():
        print(' ', k, v)
    estudios = ['3570', '3573', '3577', '3578', '3579']   # barómetros más recientes con muestra grande
    df = pd.concat([lee(e) for e in estudios])
    coef26 = ajusta(df, REC23, INT26, ['PP', 'PSOE', 'VOX', 'SUMAR'], ccaa=CON_CCAA)
    f26 = factores(coef26, covariables())
    BASE.mkdir(parents=True, exist_ok=True)
    f26.round(4).reset_index().to_csv(BASE / 'factores_perfil_2026.csv', index=False)
    json.dump({'validacion_2019_2023': res, 'coef_2019_2023_cis3411': coef19,
               'coef_2023_2026': coef26, 'estudios_2026': estudios, 'n_2026': int(len(df))},
              open(BASE / 'perfiles_resumen.json', 'w'), ensure_ascii=False, indent=1)
    print('Coeficientes 2023 -> 2026 (exp: factor multiplicativo):')
    for p, c in coef26.items():
        print(f"  {p}: 65+ x{np.exp(c['m65']):.2f}, superiores x{np.exp(c['sup']):.2f}, municipio >1M frente a <2.000 x{np.exp(c['hab'][6]):.2f}")
    print('factores por sección, percentiles 5-95:', {p: f26[p].quantile([.05, .95]).round(2).tolist() for p in f26})


if __name__ == '__main__':
    main()
