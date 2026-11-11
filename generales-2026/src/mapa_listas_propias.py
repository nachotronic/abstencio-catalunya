"""Listas que el mapa sumaba a una familia o a «Otros» y que ganan municipios o secciones: el ganador, lista a lista.

partidos.py agrupa las candidaturas en familias, y las que no tienen familia van a «Otros», que no cuenta para el más
votado (construir.py). Así, en noviembre de 2019 los 40 municipios que ganó ¡Teruel Existe! o los 31 del PRC salían
con el ganador de la familia que quedó segunda, y en 2023 los de Soria ¡Ya!, Por Ávila, la CUP o Nueva Canarias.
Y en Navarra 2023, la familia PP sumaba dos listas que fueron por separado, PP y UPN: Pamplona salía como del PP
(18.561 + 18.185 votos) cuando la ganó el PSN-PSOE (26.296), y lo mismo en otros 80 municipios.

Este script, para las generales de noviembre de 2019 y julio de 2023 (las que usa el mapa por defecto):
  - da código propio (familias añadidas al final de partidos.FAMILIAS, detrás de OTROS) a cada lista sin familia que
    gana o empata en cabeza en algún municipio o sección, y a UPN en 2023;
  - en data/municipios.json, data/e/2019_11.json, data/sec/<provincia>.json, descargas/municipios.csv,
    descargas/secciones.csv y descargas/resultados_secciones_largo.csv, añade su porcentaje (y sus votos donde hay
    columnas de votos), se lo resta a OTROS (o al PP, en el caso de UPN) y vuelve a calcular <elección>_gana lista a
    lista: con las dos listas del espacio de Sumar por separado en 2019 (mapa_listas_separadas.py) y empate (-2,
    «EMPATE») cuando las dos primeras tienen los mismos votos, como mapa_empates.py;
  - en data/meta.json añade las familias, y en data/resumen.json, el porcentaje nacional de cada una (y el del PP
    sin UPN en 2023).
  - y pone sus reglas (partidos.REGLAS_DIRECTO, con la de Coalición Canaria) delante de las de data/meta.json, para que en la noche del 29N el
    directo (app.js) tampoco sume UPN al PP ni mande a «Otros» la CUP, Existe o Soria ¡Ya!.
construir.py lo llama al final, después de mapa_empates.py. El control permanente está en control_ganadores.py (Verificar
piezas): vuelve a calcular el ganador de cada municipio y sección lista a lista desde los votos por mesa.
Los votos salen de los resultados por mesa del Ministerio del Interior (pollspaindata, sin voto exterior), los
mismos de construir.py, y se guardan en descargas/listas_propias.csv (votos por sección de cada lista propia), de
donde se lee al volver a ejecutar. Comprueba que las demás familias coinciden voto a voto con las descargas.

Se puede volver a ejecutar: si una columna ya existe, la recalcula desde el estado original guardado en el propio CSV.
Uso:  python3 generales-2026/src/mapa_listas_propias.py [--desde-mesas DIR]   (DIR: inst/extdata de pollspaindata)
"""
import csv, glob, io, json, os, sys
import numpy as np, pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from partidos import ALIAS, CODIGOS, PROPIAS as _PROPIAS, REGLAS_DIRECTO, SIGLAS_PROPIAS, familia  # noqa: E402
from mapa_listas_separadas import FUSIONES  # noqa: E402

BASE = os.path.join(AQUI, '..')
EMPATE = -2
ELECCIONES = {'2019_11': '10N 2019', '2023_07': '23J 2023'}
SIGLAS = SIGLAS_PROPIAS
DE_PP = {'2023_07': {'UPN'}}   # listas propias que partidos.py suma a la familia PP (UPN sola, 2023)
PROPIAS = [c for c, _, _ in _PROPIAS]
FAM = [k for k in CODIGOS if k != 'OTROS']
assert all(c in PROPIAS for s in SIGLAS.values() for c in s.values())


def desde_mesas(ext, desc=os.path.join(BASE, 'descargas')):
    """Votos por sección de cada lista propia, de los ficheros por mesa (sin voto exterior). Comprueba que el resto de
    las familias coincide voto a voto con resultados_secciones_largo.csv y que ninguna otra lista sin familia gana."""
    lar = pd.read_csv(os.path.join(desc, 'resultados_secciones_largo.csv'), dtype={'tract_code': str, 'mun_code': str})
    out = []
    for y, sig in SIGLAS.items():
        c = pd.read_parquet(os.path.join(ext, f'raw_candidacies_congress_{y}.parquet'))
        c['fam'] = [familia(a, n) for a, n in zip(c.abbrev_candidacies, c.name_candidacies)]
        c['cod'] = [sig.get(a, f) for a, f in zip(c.abbrev_candidacies, c.fam)]
        v = pd.read_parquet(os.path.join(ext, f'raw_candidacies_poll_congress_{y}.parquet'))
        v = v[v.cod_INE_mun != '999'].merge(c[['id_candidacies', 'abbrev_candidacies', 'fam', 'cod']])
        v['tract_code'] = v.cod_INE_prov + v.cod_INE_mun + v.cod_mun_district + v.cod_sec
        f = v.pivot_table(index='tract_code', columns='fam', values='ballots', aggfunc='sum').fillna(0)
        f = f.reindex(columns=sorted(set(f.columns) | set(FAM) | {'OTROS'}), fill_value=0)
        L = lar[lar.eleccion == y].set_index('tract_code')
        assert L.index.isin(f.index).all()
        for k in [k for k in FAM if k in L.columns] + ['OTROS']:
            assert (f.reindex(L.index)[k].fillna(0) - L[k]).abs().max() < .5, (y, k)
        # ninguna lista sin código propio gana o empata en cabeza una sección o un municipio
        v['mun_code'] = v.tract_code.str[:5].replace(FUSIONES)
        for nivel in ('tract_code', 'mun_code'):
            t = v.groupby([nivel, 'abbrev_candidacies', 'cod']).ballots.sum().reset_index()
            mx = t.groupby(nivel).ballots.transform('max')
            top = t[(t.ballots == mx) & (mx > 0)]
            assert not (top.cod == 'OTROS').any(), (y, nivel, top[top.cod == 'OTROS'].abbrev_candidacies.unique())
        p = v[v.cod.isin(set(sig.values()))].pivot_table(index='tract_code', columns='cod', values='ballots', aggfunc='sum')
        p = p.reindex(L.index).fillna(0).astype(int)
        out.append(p.reset_index().melt(id_vars='tract_code', var_name='lista', value_name='votos').assign(eleccion=y))
    o = pd.concat(out)
    o = o[o.votos > 0].sort_values(['eleccion', 'lista', 'tract_code'])
    o[['eleccion', 'tract_code', 'lista', 'votos']].to_csv(os.path.join(desc, 'listas_propias.csv'), index=False)


def leer_csv(f):
    texto = open(f, newline='', encoding='utf-8').read()
    return list(csv.reader(io.StringIO(texto)))


def escribir_csv(f, filas):
    s = io.StringIO()
    csv.writer(s, lineterminator='\n').writerows(filas)
    open(f, 'w', newline='', encoding='utf-8').write(s.getvalue())


def num(x):
    return float(x) if x not in ('', None) else np.nan


def fmt(x, dec=6):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return ''
    return repr(round(float(x), dec)) if dec else repr(float(x))


def ganador(votos, sumar_b=None):
    """Código ganador lista a lista ('EMPATE' si las dos primeras empatan; None si no hay votos)."""
    v = {k: x for k, x in votos.items() if k != 'OTROS' and x and x > 0}
    if sumar_b and 'SUMAR' in v:   # dos listas del espacio de Sumar (noviembre de 2019)
        a, b = v['SUMAR'] - sumar_b, sumar_b
        v['SUMAR'] = max(a, b)
        v['_SUMAR2'] = min(a, b)
    if not v:
        return None
    o = sorted(v.values(), reverse=True)
    if len(o) > 1 and abs(o[0] - o[1]) < 1e-9:
        return 'EMPATE'
    g = max(v, key=v.get)
    return 'SUMAR' if g == '_SUMAR2' else g


class Nivel:
    """Votos por sección o por municipio de cada familia, de cada lista propia y de la segunda lista de Sumar."""

    def __init__(self, y, clave, desc):
        self.y = y
        lar = pd.read_csv(os.path.join(desc, 'resultados_secciones_largo.csv'), dtype={'tract_code': str, 'mun_code': str})
        lar = lar[lar.eleccion == y].set_index('tract_code')
        prop = pd.read_csv(os.path.join(desc, 'listas_propias.csv'), dtype={'tract_code': str})
        prop = prop[prop.eleccion == y].pivot_table(index='tract_code', columns='lista', values='votos', aggfunc='sum').reindex(lar.index).fillna(0)
        self.codigos = list(prop.columns)
        # el estado original de las descargas: PP y OTROS con las listas propias dentro (las restamos aquí)
        base = lar.copy()
        if any(c in base.columns for c in self.codigos):   # ya ejecutado: se reconstruye el original
            for k in self.codigos:
                if k in base.columns:
                    base[k] = base[k].fillna(0)
                    base['PP' if k in DE_PP.get(y, ()) else 'OTROS'] += base[k]
        for k in self.codigos:
            base['PP' if k in DE_PP.get(y, ()) else 'OTROS'] -= prop[k]
            base[k] = prop[k]
        assert (base[['PP', 'OTROS']] >= -0.5).all().all()
        ls = pd.read_csv(os.path.join(desc, 'listas_separadas.csv'), dtype={'tract_code': str})
        base['SUMAR_B'] = ls[ls.eleccion == y].set_index('tract_code').sumar_b.reindex(base.index).fillna(0) if y == '2019_11' else 0
        base['validos'] = base.candidaturas + base.blancos
        cols = [k for k in FAM if k in base.columns] + ['OTROS'] + self.codigos + ['SUMAR_B', 'validos', 'candidaturas']
        if clave == 'mun_code':
            base = base.assign(mun_code=base.mun_code.replace(FUSIONES)).groupby('mun_code')[cols].sum()
        self.t = base[cols]
        self.fams = [k for k in FAM if k in base.columns] + ['OTROS'] + self.codigos
        self.gana = {i: ganador({k: r[k] for k in self.fams}, r['SUMAR_B']) for i, r in self.t.to_dict('index').items()}

    def pct(self, k):
        return (self.t[k] / self.t.validos.where(self.t.validos > 0)).fillna(0)


def familias_meta(meta):
    ya = [f['cod'] for f in meta['familias']]
    for cod, nombre, color in _PROPIAS:
        if cod not in ya:
            meta['familias'].append({'cod': cod, 'nombre': nombre, 'color': color})
    meta.setdefault('alias', {}).update({c: a for c, a in PROPIAS_ALIAS.items()})
    # directo del 29N: las reglas de las listas propias, delante de las de las familias (la primera que casa gana)
    meta['reglas'] = REGLAS_DIRECTO + [r for r in meta.get('reglas', []) if r not in REGLAS_DIRECTO and r[0] not in PROPIAS]


PROPIAS_ALIAS = {c: a for c, a in ALIAS.items() if c in PROPIAS}


def json_web(f, N, cods, idx):
    """Añade los porcentajes de las listas propias, se los resta a OTROS o al PP y rehace el ganador."""
    d = json.load(open(f))
    cambios = 0
    for y, n in N.items():
        if y + '_gana' not in d:
            continue
        arr = d[y + '_gana']
        ok = [i for i, c in enumerate(cods) if c in n.t.index]
        for k in n.codigos:
            col = n.pct(k)
            de = 'PP' if k in DE_PP.get(y, ()) else 'OTROS'
            nuevo = [None] * len(cods)
            for i in ok:
                nuevo[i] = round(float(col[cods[i]]), 3)
            d[f'{y}_{k}'] = nuevo
        for de in ('PP', 'OTROS'):
            if f'{y}_{de}' in d:
                col = n.pct(de)
                for i in ok:
                    if d[f'{y}_{de}'][i] is not None:
                        d[f'{y}_{de}'][i] = round(float(col[cods[i]]), 3)
        for i in ok:
            g = n.gana[cods[i]]
            if arr[i] is None or arr[i] == -1:
                continue
            nv = EMPATE if g == 'EMPATE' else idx[g]
            if nv != arr[i]:
                arr[i], cambios = nv, cambios + 1
    json.dump(d, open(f, 'w'), separators=(',', ':'), ensure_ascii=False)
    return cambios


def csv_desc(f, N, clave, votos):
    """Lo mismo en una descarga CSV: <elección>_<lista> (y <elección>_v<lista>) detrás de los de OTROS, y el ganador."""
    filas = leer_csv(f)
    cab, cuerpo = filas[0], filas[1:]
    ic, cambios = cab.index(clave), 0
    for y, n in N.items():
        if f'{y}_gana' not in cab:
            continue
        for k in n.codigos:
            for pre, dec, val in ((f'{y}_', 6, n.pct(k)), (f'{y}_v', 0, n.t[k])):
                if pre == f'{y}_v' and not votos:
                    continue
                nom = pre + k
                if nom not in cab:
                    j = cab.index(pre + 'OTROS') + 1
                    while j < len(cab) and cab[j][len(pre):] in PROPIAS and cab[j].startswith(pre):
                        j += 1
                    cab.insert(j, nom)
                    for fila in cuerpo:
                        fila.insert(j, '')
                j = cab.index(nom)
                for fila in cuerpo:
                    if fila[ic] in val.index and fila[cab.index(f'{y}_gana')] != '':
                        fila[j] = fmt(val[fila[ic]], dec) if dec else fmt(val[fila[ic]])
        for de in ('PP', 'OTROS'):
            for pre, dec, val in ((f'{y}_', 6, n.pct(de)), (f'{y}_v', 0, n.t[de])):
                if pre + de not in cab or (pre == f'{y}_v' and not votos):
                    continue
                j = cab.index(pre + de)
                for fila in cuerpo:
                    if fila[ic] in val.index and fila[j] != '':
                        fila[j] = fmt(val[fila[ic]], dec) if dec else fmt(val[fila[ic]])
        jg = cab.index(f'{y}_gana')
        for fila in cuerpo:
            if fila[ic] in n.gana and fila[jg] != '':
                g = n.gana[fila[ic]] or fila[jg]
                if g != fila[jg]:
                    fila[jg], cambios = g, cambios + 1
    escribir_csv(f, [cab] + cuerpo)
    return cambios


def largo(f, N):
    """resultados_secciones_largo.csv: votos de cada lista propia, restados de OTROS o del PP."""
    filas = leer_csv(f)
    cab, cuerpo = filas[0], filas[1:]
    it, ie = cab.index('tract_code'), cab.index('eleccion')
    for k in sorted({k for n in N.values() for k in n.codigos}, key=PROPIAS.index):
        if k not in cab:
            j = cab.index('OTROS') + 1
            while cab[j] in PROPIAS:
                j += 1
            cab.insert(j, k)
            for fila in cuerpo:
                fila.insert(j, '')
    for fila in cuerpo:
        y = fila[ie]
        if y not in N:
            continue
        n = N[y]
        t = n.t
        if fila[it] not in t.index:
            continue
        r = t.loc[fila[it]]
        for k in n.codigos + ['PP', 'OTROS']:
            fila[cab.index(k)] = fmt(r[k], 0)
    escribir_csv(f, [cab] + cuerpo)


def main(web=os.path.join(BASE, 'data'), desc=os.path.join(BASE, 'descargas')):
    if '--desde-mesas' in sys.argv:
        desde_mesas(sys.argv[sys.argv.index('--desde-mesas') + 1], desc)
    meta = json.load(open(os.path.join(web, 'meta.json')))
    familias_meta(meta)
    json.dump(meta, open(os.path.join(web, 'meta.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
    idx = {f['cod']: i for i, f in enumerate(meta['familias'])}
    NM = {y: Nivel(y, 'mun_code', desc) for y in ELECCIONES}
    NS = {y: Nivel(y, 'tract_code', desc) for y in ELECCIONES}
    n = {}
    cods = json.load(open(os.path.join(web, 'municipios.json')))['cod']
    n['municipios.json'] = json_web(os.path.join(web, 'municipios.json'), NM, cods, idx)
    for f in sorted(glob.glob(os.path.join(web, 'e', '*.json'))):
        if os.path.basename(f)[:-5] in ELECCIONES:
            n[os.path.basename(f)] = json_web(f, NM, cods, idx)
    n['sec/'] = 0
    for f in sorted(glob.glob(os.path.join(web, 'sec', '[0-9][0-9].json'))):
        sc = json.load(open(f))['cod']
        n['sec/'] += json_web(f, NS, sc, idx)
    n['municipios.csv'] = csv_desc(os.path.join(desc, 'municipios.csv'), NM, 'mun_code', votos=True)
    n['secciones.csv'] = csv_desc(os.path.join(desc, 'secciones.csv'), NS, 'tract_code', votos=False)
    # largo: después de leer los Nivel (que lo usan como estado original)
    largo(os.path.join(desc, 'resultados_secciones_largo.csv'), NS)
    # resumen nacional
    rs = json.load(open(os.path.join(web, 'resumen.json')))
    for y, nom in ELECCIONES.items():
        t = NM[y].t.sum()
        r = rs['nacional'][nom]
        for k in NM[y].codigos + ['PP', 'OTROS']:
            r[k] = float(t[k] / t.validos)
    json.dump(rs, open(os.path.join(web, 'resumen.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
    print('ganadores cambiados', n)
    for y in ELECCIONES:
        g = pd.Series(NM[y].gana).value_counts()
        print(y, 'municipios por lista propia:', {k: int(g.get(k, 0)) for k in NM[y].codigos if g.get(k, 0)})


if __name__ == '__main__':
    main()
