"""Empates en el partido más votado del mapa: un municipio o una sección donde los dos primeros tienen los mismos votos.

construir.py elige el ganador con idxmax, que en un empate se queda con el primero en el orden de CODIGOS (el PP antes
que el PSOE, el PSOE antes que ERC…). Así, Albesa (Lleida, 2023: PSOE 172, ERC 172) salía como del PSOE y Bayarque
(Almería, noviembre de 2019: PP y PSOE con los mismos votos) como del PP. Este script los marca como empate:

  - en data/municipios.json, data/e/<elección>.json, data/sec/<provincia>.json y data/sec/<provincia>_<elección>.json,
    <elección>_gana = -2 (el mapa los pinta en gris, con «Empate» en la leyenda y en la ficha: EMPATE en app.js);
  - en descargas/municipios.csv, municipios_historico.csv, secciones.csv y secciones_municipales_europeas.csv,
    <elección>_gana = EMPATE.

Los votos salen de las mismas tablas que construir.py: por municipio, las columnas <elección>_v<familia> de
municipios.csv y municipios_historico.csv; por sección, resultados_secciones_largo*.csv. En las cuatro generales en que
el espacio de Sumar fue en dos listas (mapa_listas_separadas.py) se compara lista a lista. OTROS no cuenta, como en
construir.py. La Segunda República (listas abiertas) queda fuera.

Solo toca ganadores que ya existían (no inventa ganador donde no hay datos) y se puede volver a ejecutar.
construir.py lo llama al final, después de mapa_listas_separadas.py.
Uso:  python3 generales-2026/src/mapa_empates.py
"""
import csv, glob, io, json, os, re, sys
import numpy as np, pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from partidos import CODIGOS  # noqa: E402
from mapa_listas_separadas import FUSIONES, SEPARADAS  # noqa: E402

BASE = os.path.join(AQUI, '..')
EMPATE = -2
FAM = [k for k in CODIGOS if k != 'OTROS']


def empatados(t, b=None):
    """Índice de las filas en que los dos primeros (lista a lista) tienen los mismos votos, y más de cero."""
    cols = [k for k in FAM if k in t.columns]
    v = t[cols].astype(float)
    if b is not None:   # dos listas en el espacio de Sumar: cada una por su lado
        b = b.reindex(t.index).fillna(0)
        v = v.assign(SUMAR=v.SUMAR - b, SUMAR_B=b)
    x = v.to_numpy()
    ok = ~np.isnan(x).any(axis=1)
    s = -np.sort(-np.nan_to_num(x, nan=-1), axis=1)
    return set(t.index[ok & (s[:, 0] > 0) & (s[:, 0] == s[:, 1])])


def tablas(desc):
    """{elección: (secciones empatadas, municipios empatados)}."""
    ls = pd.read_csv(os.path.join(desc, 'listas_separadas.csv'), dtype={'tract_code': str})
    out = {}
    # municipios: las columnas de votos de las descargas por municipio
    for f in ('municipios.csv', 'municipios_historico.csv'):
        if not os.path.exists(os.path.join(desc, f)):
            continue
        m = pd.read_csv(os.path.join(desc, f), dtype={'mun_code': str}).set_index('mun_code')
        for y in sorted({c[:-5] for c in m.columns if c.endswith('_gana')}):
            cols = {c[len(y) + 2:]: c for c in m.columns if re.fullmatch(re.escape(y) + r'_v[A-Z]+', c)}
            if not cols:
                continue
            t = m[list(cols.values())].rename(columns={v: k for k, v in cols.items()})
            b = None
            if y in SEPARADAS:
                x = ls[ls.eleccion == y].assign(mun_code=lambda d: d.tract_code.str[:5].replace(FUSIONES))
                b = x.groupby('mun_code').sumar_b.sum()
            out.setdefault(y, [set(), set()])[1] = empatados(t, b)
    # secciones
    for f in ('resultados_secciones_largo.csv', 'resultados_secciones_largo_municipales_europeas.csv'):
        if not os.path.exists(os.path.join(desc, f)):
            continue
        lar = pd.read_csv(os.path.join(desc, f), dtype={'tract_code': str, 'mun_code': str, 'eleccion': str})
        for y, t in lar.groupby('eleccion'):
            t = t.set_index('tract_code')
            b = ls[ls.eleccion == y].set_index('tract_code').sumar_b if y in SEPARADAS else None
            out.setdefault(y, [set(), set()])[0] = empatados(t, b)
    return out


def json_web(f, T, cods):
    d = json.load(open(f))
    cambios = 0
    for k in [k for k in d if k.endswith('_gana')]:
        y = k[:-5]
        if y not in T:
            continue
        emp = T[y]
        arr = d[k]
        for i, c in enumerate(cods):
            if c in emp and arr[i] is not None and arr[i] >= 0:
                arr[i], cambios = EMPATE, cambios + 1
    if cambios:
        json.dump(d, open(f, 'w'), separators=(',', ':'), ensure_ascii=False)
    return cambios


def csv_desc(f, T, clave):
    texto = open(f, newline='', encoding='utf-8').read()
    filas = list(csv.reader(io.StringIO(texto)))
    cab = filas[0]
    ic, cambios = cab.index(clave), 0
    for j, k in enumerate(cab):
        if not k.endswith('_gana') or k[:-5] not in T:
            continue
        emp = T[k[:-5]]
        for fila in filas[1:]:
            if fila[ic] in emp and fila[j] and fila[j] != 'EMPATE':
                fila[j], cambios = 'EMPATE', cambios + 1
    if cambios:
        s = io.StringIO()
        csv.writer(s, lineterminator='\n').writerows(filas)
        open(f, 'w', newline='', encoding='utf-8').write(s.getvalue())
    return cambios


def main(web=os.path.join(BASE, 'data'), desc=os.path.join(BASE, 'descargas')):
    E = tablas(desc)
    TS = {y: s for y, (s, m) in E.items()}
    TM = {y: m for y, (s, m) in E.items()}
    n = {}
    cods = json.load(open(os.path.join(web, 'municipios.json')))['cod']
    n['municipios.json'] = json_web(os.path.join(web, 'municipios.json'), TM, cods)
    n['e/'] = sum(json_web(f, TM, cods) for f in sorted(glob.glob(os.path.join(web, 'e', '*.json'))))
    n['sec/'] = 0
    for f in sorted(glob.glob(os.path.join(web, 'sec', '[0-9][0-9].json'))):
        sc = json.load(open(f))['cod']
        n['sec/'] += json_web(f, TS, sc)
        n['sec/'] += sum(json_web(g, TS, sc) for g in sorted(glob.glob(f[:-5] + '_*.json')))
    for nom, clave, T in (('municipios.csv', 'mun_code', TM), ('municipios_historico.csv', 'mun_code', TM),
                          ('secciones.csv', 'tract_code', TS), ('secciones_municipales_europeas.csv', 'tract_code', TS)):
        if os.path.exists(os.path.join(desc, nom)):
            n[nom] = csv_desc(os.path.join(desc, nom), T, clave)
    print('empates marcados', n, {y: (len(s), len(m)) for y, (s, m) in sorted(E.items())})


if __name__ == '__main__':
    main()
