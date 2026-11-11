"""Auditoría del partido más votado: el ganador lista a lista, desde los votos oficiales, frente al que da el site.

El site guarda el ganador por familia política (generales-2026/src/partidos.py) en la columna <elección>_gana de
generales-2026/descargas/municipios.csv y secciones.csv; de ahí salen el mapa de la portada, las fichas y muchas piezas.
Agrupar en familias da ganadores falsos cuando:
  - dos listas de la misma familia fueron por separado (Podemos e IU en 2015, UPN y PP en Navarra en 2023...);
  - ganó una lista que la familia mete en «otros» (Teruel Existe, PRC, Soria ¡Ya!...), que no puede ganar;
  - las dos primeras listas empatan a votos.
Este script recalcula el ganador sin agrupar: cada candidatura (id_candidacies de Interior) por separado, con los
votos por mesa de pollspaindata, sin el voto exterior (CERA), como construir.py. Y lo compara con el site.

Una discrepancia es una unidad (municipio o sección) en la que:
  - la lista ganadora es de una familia distinta de la que da el site, o
  - las dos primeras listas empatan y el site no dice EMPATE, o el site dice EMPATE y no hay empate.
Si la lista ganadora es de «otros», el site debería no darle la victoria a ninguna familia: cuenta como discrepancia.

Uso:
  python3 src/auditoria_ganadores.py --csv salida.csv   discrepancias con su causa (necesita pollspaindata)
  python3 src/auditoria_ganadores.py --referencia       rehace descargas/ganador_lista.csv.gz (necesita pollspaindata)
  python3 src/auditoria_ganadores.py --comprobar        descargas frente a la referencia, en segundos (para «verificar»)
Sale con código 1 si hay alguna discrepancia.
"""
import argparse, csv, gzip, os, sys

try:
    import pandas as pd   # solo para --csv y --referencia; --comprobar va sin pandas (en la CI no está)
except ImportError:
    pd = None

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'generales-2026', 'src'))
from partidos import familia  # noqa: E402

CACHE = os.environ.get('GENERALES_CACHE', os.path.expanduser('~/.cache/generales'))
E = os.path.join(CACHE, 'pollspaindata', 'inst', 'extdata')
DESC = os.path.join(RAIZ, 'generales-2026', 'descargas')
FUSIONES = {'15026': '15902', '15063': '15902', '36011': '36902', '36012': '36902'}   # como en construir.py
TODAS = ['2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']


def votos_lista(y):
    """Votos por (sección, candidatura), sin CERA, con la familia y las siglas de cada candidatura."""
    c = pd.read_parquet(f'{E}/raw_candidacies_congress_{y}.parquet')
    c['fam'] = [familia(a, n) for a, n in zip(c.abbrev_candidacies, c.name_candidacies)]
    v = pd.read_parquet(f'{E}/raw_candidacies_poll_congress_{y}.parquet')
    v = v[v.cod_INE_mun != '999']
    v['tract_code'] = v.cod_INE_prov + v.cod_INE_mun + v.cod_mun_district + v.cod_sec
    v = v.groupby(['tract_code', 'id_candidacies'], as_index=False).ballots.sum()
    v = v.merge(c[['id_candidacies', 'abbrev_candidacies', 'name_candidacies', 'fam']], on='id_candidacies', how='left')
    v['mun_code'] = v.tract_code.str[:5].replace(FUSIONES)
    return v


def ganadores(v, clave):
    """Por unidad: la lista más votada, la segunda, y si empatan."""
    t = v.groupby([clave, 'id_candidacies', 'abbrev_candidacies', 'name_candidacies', 'fam'], as_index=False).ballots.sum()
    t = t[t.ballots > 0].sort_values([clave, 'ballots'], ascending=[True, False])
    top = t.groupby(clave).head(2).copy()
    top['n'] = top.groupby(clave).cumcount()
    a = top[top.n == 0].set_index(clave)
    b = top[top.n == 1].set_index(clave).reindex(a.index)
    # votos de la familia del ganador del site, sumando sus listas, para explicar las sumas de familia
    fam = t.groupby([clave, 'fam']).agg(votos=('ballots', 'sum'), listas=('id_candidacies', 'nunique'))
    return pd.DataFrame({'lista': a.abbrev_candidacies, 'nombre': a.name_candidacies, 'fam_lista': a.fam, 'votos': a.ballots,
                         'segunda': b.abbrev_candidacies, 'fam_segunda': b.fam, 'votos_2': b.ballots,
                         'empate': a.ballots == b.ballots}), fam


def causa(r, fam):
    if r.empate and r.site != 'EMPATE':
        return 'empate a votos sin marcar'
    if r.site == 'EMPATE' and not r.empate:
        return 'EMPATE marcado sin empate'
    if r.fam_lista == 'OTROS':
        return 'gana una lista de «otros»'
    try:
        x = fam.loc[(r.name, r.site)]
        if x.listas > 1 and x.votos > r.votos:
            return 'suma de listas de la misma familia'
    except KeyError:
        pass
    return 'otra'


def audita(elecciones):
    sites = {n: pd.read_csv(os.path.join(DESC, f'{n}.csv'), dtype=str,
                            usecols=lambda c, k=k: c == k or c.endswith('_gana')).set_index(k)
             for n, k in (('municipios', 'mun_code'), ('secciones', 'tract_code'))}
    filas = []
    for y in elecciones:
        v = votos_lista(y)
        for nivel, clave in (('municipios', 'mun_code'), ('secciones', 'tract_code')):
            g, fam = ganadores(v, clave)
            col = f'{y}_gana'
            if col not in sites[nivel]:
                continue
            g['site'] = sites[nivel][col].reindex(g.index)
            g = g[g.site.notna()]          # secciones que han cambiado de código desde entonces: el site no da dato
            mal = g[((g.fam_lista != g.site) & ~(g.empate & (g.site == 'EMPATE'))) | (g.empate & (g.site != 'EMPATE'))].copy()
            mal['causa'] = [causa(r, fam) for _, r in mal.iterrows()]
            mal['eleccion'], mal['nivel'] = y, nivel
            filas.append(mal.reset_index().rename(columns={clave: 'codigo'}))
            print(f'{y} {nivel}: {len(g)} unidades, {len(mal)} discrepancias', dict(mal.causa.value_counts()))
    return pd.concat(filas, ignore_index=True) if filas else pd.DataFrame()


REF = os.path.join(DESC, 'ganador_lista.csv.gz')


def referencia(elecciones):
    """Escribe descargas/ganador_lista.csv.gz: la lista más votada de cada municipio y sección, con sus siglas y su nombre
    oficiales, sus votos, los de la segunda y si empatan. Es lo que necesita --comprobar, sin pollspaindata."""
    filas = []
    for y in elecciones:
        v = votos_lista(y)
        for nivel, clave in (('municipios', 'mun_code'), ('secciones', 'tract_code')):
            g, _ = ganadores(v, clave)
            g = g.reset_index().rename(columns={clave: 'codigo'})
            g['eleccion'], g['nivel'] = y, nivel
            filas.append(g[['eleccion', 'nivel', 'codigo', 'lista', 'nombre', 'votos', 'votos_2', 'empate']])
    d = pd.concat(filas, ignore_index=True)
    d['votos_2'] = d.votos_2.fillna(0)
    d[['votos', 'votos_2']] = d[['votos', 'votos_2']].astype(int)
    d['empate'] = d.empate.astype(int)
    d.to_csv(REF, index=False, compression={'method': 'gzip', 'mtime': 0})   # mtime 0: mismo fichero si no cambia nada
    print('Escrito', os.path.relpath(REF, RAIZ), len(d), 'filas')


def comprobar():
    """Compara la columna <elección>_gana de las descargas con descargas/ganador_lista.csv.gz. La familia de la lista
    ganadora se calcula ahora con partidos.familia(), así que sigue a partidos.py si cambia. Solo con la biblioteca
    estándar y en segundos: para «verificar»."""
    ref = {}
    with gzip.open(REF, 'rt', encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            ref[(r['nivel'], r['eleccion'], r['codigo'])] = r
    fams = {}
    n = 0
    for nivel, clave in (('municipios', 'mun_code'), ('secciones', 'tract_code')):
        with open(os.path.join(DESC, f'{nivel}.csv'), encoding='utf-8', newline='') as f:
            rd = csv.DictReader(f)
            cols = [c for c in rd.fieldnames if c.endswith('_gana')]
            mal = {}
            for fila in rd:
                for col in cols:
                    y, site = col[:-5], fila[col]
                    r = ref.get((nivel, y, fila[clave]))
                    if not site or r is None:
                        continue      # sin dato en el site (sección con otro código entonces) o sin votos
                    k = (r['lista'], r['nombre'])
                    if k not in fams:
                        fams[k] = familia(*k)
                    esperado = 'EMPATE' if r['empate'] == '1' else fams[k]
                    if site != esperado or esperado == 'OTROS':
                        mal.setdefault(y, []).append((fila[clave], site, r))
        for y, m in sorted(mal.items()):
            n += len(m)
            print(f'{y} {nivel}: {len(m)} con otro ganador. Ejemplos:', '; '.join(
                f"{c} da {si} y ganó {r['lista']} ({r['votos']} votos, la segunda {r['votos_2']}{', empate' if r['empate'] == '1' else ''})"
                for c, si, r in m[:3]))
    print('auditoría de ganadores:', 'todo cuadra' if not n else f'{n} unidades con un ganador distinto del oficial lista a lista')
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--elecciones', nargs='*', default=TODAS)
    ap.add_argument('--csv', help='con pollspaindata: discrepancias con su causa, a este fichero')
    ap.add_argument('--referencia', action='store_true', help='con pollspaindata: rehace descargas/ganador_lista.csv.gz')
    ap.add_argument('--comprobar', action='store_true', help='sin pollspaindata: compara las descargas con la referencia')
    a = ap.parse_args()
    if a.referencia:
        referencia(a.elecciones)
        return
    if a.comprobar:
        sys.exit(1 if comprobar() else 0)
    d = audita(a.elecciones)
    if a.csv:
        d.to_csv(a.csv, index=False)
    sys.exit(1 if len(d) else 0)


if __name__ == '__main__':
    main()
