"""Partido más votado del mapa en las cuatro generales en que el espacio de Sumar fue en dos listas.

La familia «Sumar / Podemos / IU» (partidos.py) suma Podemos, IU, Sumar y sus coaliciones. En 2011 y abril de 2019 en
la Comunitat Valenciana (EUPV y Compromís-Q; Unides Podem y Compromís), en 2015 (Podemos e IU-Unidad Popular) y en
noviembre de 2019 (Unidas Podemos y Más País / Més Compromís) ese espacio fue en dos listas. Sumadas, la familia
«ganaba» donde ninguna de las dos ganó: Amurrio en 2015, donde ganó el PNV, por ejemplo. Las fichas de municipio
lo calculan ya lista a lista (#510, src/territorios_datos.py); este script hace lo mismo con el mapa.

Toma los votos de la segunda lista por sección (descargas/listas_separadas.csv, de listas_separadas.py) y:
  - en data/municipios.json, data/e/<elección>.json y data/sec/<provincia>.json, cambia <elección>_gana donde la
    familia ganaba sumando y no gana ninguna de sus dos listas, y añade <elección>_SUMAR_A y <elección>_SUMAR_B, el
    porcentaje de cada lista calculado desde los votos (la ficha del mapa las enseña como dos filas);
  - en descargas/municipios.csv y descargas/secciones.csv, cambia la columna <elección>_gana igual.
Los porcentajes de la familia (<elección>_SUMAR) no cambian: son los de la familia.

Se puede volver a ejecutar: solo toca los ganadores que siguen siendo «SUMAR». construir.py lo llama al final.
Uso:  python3 generales-2026/src/mapa_listas_separadas.py
"""
import csv, glob, io, json, os, sys
import numpy as np, pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from partidos import CODIGOS  # noqa: E402

BASE = os.path.join(AQUI, '..')
SEPARADAS = ('2011_11', '2015_12', '2019_04', '2019_11')
FUSIONES = {'15026': '15902', '15063': '15902', '36011': '36902', '36012': '36902'}   # como en construir.py


def tablas(desc):
    """Por elección: (secciones, municipios), cada una con el ganador lista a lista y el % de la segunda lista."""
    lar = pd.read_csv(os.path.join(desc, 'resultados_secciones_largo.csv'), dtype={'tract_code': str, 'mun_code': str})
    ls = pd.read_csv(os.path.join(BASE, 'descargas', 'listas_separadas.csv'), dtype={'tract_code': str})
    fam = [k for k in CODIGOS if k != 'OTROS' and k in lar.columns]
    out = {}
    for y in SEPARADAS:
        r = lar[lar.eleccion == y].merge(ls[ls.eleccion == y][['tract_code', 'sumar_b']], on='tract_code', how='left')
        r['sumar_b'] = r.sumar_b.fillna(0)
        r['mun_code'] = r.mun_code.replace(FUSIONES)
        m = r.groupby('mun_code')[['candidaturas', 'blancos', 'sumar_b'] + fam].sum()
        res = []
        for t in (r.set_index('tract_code'), m):
            sub = t[fam].copy()
            sub['SUMAR'] = np.maximum(t.SUMAR - t.sumar_b, t.sumar_b)    # la más votada de las dos listas
            g = pd.Series(np.where(t.candidaturas > 0, sub.idxmax(axis=1), None), index=t.index)  # empate: orden de CODIGOS, como construir.py
            val = (t.candidaturas + t.blancos).where(lambda x: x > 0)
            res.append(pd.DataFrame({'gana': g, 'a': ((t.SUMAR - t.sumar_b) / val).round(3), 'b': (t.sumar_b / val).round(3)}))   # desde los votos: sin doble redondeo
        out[y] = res
    return out


def nuevo(viejo, g):
    """El ganador corregido: solo cambia uno que era SUMAR (la familia sumada)."""
    return g if viejo == 'SUMAR' and isinstance(g, str) else viejo


def json_web(f, T, nivel):
    d = json.load(open(f))
    cods, cambios = d.get('cod'), 0
    if cods is None:      # data/e/<elección>.json: mismo orden que municipios.json
        cods = json.load(open(os.path.join(os.path.dirname(f), '..', 'municipios.json')))['cod']
    for y, (ts, tm) in T.items():
        k = f'{y}_gana'
        if k not in d:
            continue
        t = ts if nivel == 'sec' else tm
        g, a, b = t.gana.reindex(cods), t.a.reindex(cods), t.b.reindex(cods)
        arr = []
        for i, (v, n) in enumerate(zip(d[k], g)):
            viejo = CODIGOS[v] if v >= 0 else None
            nv = nuevo(viejo, n)
            cambios += nv != viejo
            arr.append(CODIGOS.index(nv) if nv else (v if v is not None and v < 0 else -1))   # -2: empate (mapa_empates.py)
        d[k] = arr
        fam = d.get(f'{y}_SUMAR')
        for x, s_, v in zip(a, b, fam or []):   # control: las dos listas suman la familia (con el redondeo de cada una)
            assert pd.isna(s_) or s_ == 0 or v is None or abs(x + s_ - v) <= .0016, (f, y, x, s_, v)
        sep = [not pd.isna(x) and x > 0 for x in b]   # solo donde hubo segunda lista
        d[f'{y}_SUMAR_A'] = [float(x) if s and not pd.isna(x) else None for x, s in zip(a, sep)]
        d[f'{y}_SUMAR_B'] = [float(x) if s else None for x, s in zip(b, sep)]
    json.dump(d, open(f, 'w'), separators=(',', ':'), ensure_ascii=False)
    return cambios


def csv_desc(f, T, nivel):
    texto = open(f, newline='', encoding='utf-8').read()
    filas = list(csv.reader(io.StringIO(texto)))
    cab, clave = filas[0], ('tract_code' if nivel == 'sec' else 'mun_code')
    ic, cambios = cab.index(clave), 0
    for y, (ts, tm) in T.items():
        if f'{y}_gana' not in cab:
            continue
        j, g = cab.index(f'{y}_gana'), (ts if nivel == 'sec' else tm).gana.to_dict()
        for fila in filas[1:]:
            nv = nuevo(fila[j] or None, g.get(fila[ic]))
            if (nv or '') != fila[j]:
                fila[j], cambios = nv, cambios + 1
    s = io.StringIO()
    csv.writer(s, lineterminator='\n').writerows(filas)
    open(f, 'w', newline='', encoding='utf-8').write(s.getvalue())
    return cambios


def main(web=os.path.join(BASE, 'data'), desc=os.path.join(BASE, 'descargas')):
    T = tablas(desc)
    n = {'municipios.json': json_web(os.path.join(web, 'municipios.json'), T, 'mun')}
    n['e/'] = sum(json_web(os.path.join(web, 'e', f'{y}.json'), T, 'mun') for y in SEPARADAS
                  if os.path.exists(os.path.join(web, 'e', f'{y}.json')))
    n['sec/'] = sum(json_web(f, T, 'sec') for f in sorted(glob.glob(os.path.join(web, 'sec', '[0-9][0-9].json'))))
    for nom, nivel in (('municipios.csv', 'mun'), ('secciones.csv', 'sec')):
        n[nom] = csv_desc(os.path.join(desc, nom), T, nivel)
    print('listas separadas: ganadores corregidos', n)


if __name__ == '__main__':
    main()
