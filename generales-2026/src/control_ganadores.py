"""Control permanente del ganador del mapa (Verificar piezas, 11-11-2026): el más votado, lista a lista, desde las mesas.

El mapa elegía el ganador sumando familias: UPN iba dentro del PP en Navarra 2023 (Pamplona salía del PP y la ganó el
PSN-PSOE) y las listas sin familia (¡Teruel Existe!, el PRC, la CUP, Soria ¡Ya!…) iban a «Otros», que no cuenta, de modo
que sus municipios salían con la familia que quedó segunda. Este control lo vuelve a calcular sin familias:

  1. Lee los votos de cada candidatura en cada sección, sumados desde los resultados por mesa del Ministerio del Interior
     (control/votos_secciones_<elección>.csv.gz y control/candidaturas_<elección>.csv, sin voto exterior; sacados de
     los ficheros por mesa que publica pollspaindata, los mismos de construir.py).
  2. En cada sección y en cada municipio (las secciones sumadas, con los municipios fusionados como en construir.py),
     el ganador es la candidatura con más votos; si las dos primeras tienen los mismos votos, «EMPATE».
  3. Traduce esa candidatura al código del mapa (partidos.familia y, para las listas con código propio,
     partidos.SIGLAS_PROPIAS). Si gana una candidatura que en el mapa sería «Otros», es error: no tendría color propio.
  4. Lo compara con <elección>_gana de descargas/municipios.csv y descargas/secciones.csv, y con el índice del ganador
     en data/municipios.json, data/municipios-ligero.json, data/e/<elección>.json y data/sec/<provincia>.json; y,
     por provincia, con el que dan las fichas (la suma de los votos de cada código del mapa en municipios.csv).

Cualquier diferencia hace fallar Verificar piezas (no hay excepciones: los empates salen de los mismos votos).
Elecciones comprobadas: noviembre de 2019 y julio de 2023 (las que corrigió mapa_listas_propias.py); las demás se
añadirán a ELECCIONES cuando se corrijan. Solo usa la biblioteca estándar de Python (no hace falta instalar nada).
Uso:  python3 generales-2026/src/control_ganadores.py [--resumen FICHERO]
"""
import csv, glob, gzip, io, json, os, sys
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from partidos import SIGLAS_PROPIAS, familia  # noqa: E402

BASE = os.path.dirname(AQUI)
ELECCIONES = ['2019_11', '2023_07']
FUSIONES = {'15026': '15902', '15063': '15902', '36011': '36902', '36012': '36902'}   # como en construir.py
EMPATE = -2
try:   # la misma tabla que construir.py y mapa_listas_separadas.py (si pandas está instalado, se comprueba)
    from mapa_listas_separadas import FUSIONES as _F
    assert _F == FUSIONES, 'FUSIONES no coincide con mapa_listas_separadas.py'
except ImportError:
    pass


def mesas(y):
    """{sección: {candidatura: votos}} y {candidatura: código del mapa}."""
    cand = {}
    with open(os.path.join(BASE, 'control', f'candidaturas_{y}.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            cand[r['candidatura']] = SIGLAS_PROPIAS.get(y, {}).get(r['siglas']) or familia(r['siglas'], r['nombre'])
    sec = defaultdict(dict)
    with gzip.open(os.path.join(BASE, 'control', f'votos_secciones_{y}.csv.gz'), 'rt', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            sec[r['tract_code']][r['candidatura']] = int(r['votos'])
    return sec, cand


def ganador(votos, cand):
    """Código del mapa de la candidatura más votada, 'EMPATE' o None (sin votos). La lista, no la familia."""
    o = sorted(((v, c) for c, v in votos.items() if v > 0), reverse=True)
    if not o:
        return None
    if len(o) > 1 and o[0][0] == o[1][0]:
        return 'EMPATE'
    return cand[o[0][1]]


def esperados(y):
    sec, cand = mesas(y)
    mun = defaultdict(lambda: defaultdict(int))
    for t, vs in sec.items():
        m = FUSIONES.get(t[:5], t[:5])
        for c, v in vs.items():
            mun[m][c] += v
    prov = defaultdict(lambda: defaultdict(int))
    for m, vs in mun.items():
        for c, v in vs.items():
            prov[m[:2]][c] += v
    return ({t: ganador(v, cand) for t, v in sec.items()}, {m: ganador(v, cand) for m, v in mun.items()},
            {p: ganador(v, cand) for p, v in prov.items()})


def provincias_site():
    """El ganador de cada provincia como lo calculan las fichas (src/territorios_datos.py): la suma de los votos de cada
    código del mapa en descargas/municipios.csv, sin «Otros», con las dos listas del espacio de Sumar por separado
    en noviembre de 2019 (descargas/listas_separadas.csv)."""
    b = defaultdict(float)
    with open(os.path.join(BASE, 'descargas', 'listas_separadas.csv'), newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['eleccion'] in ELECCIONES:
                b[r['eleccion'], r['tract_code'][:2]] += float(r['sumar_b'] or 0)
    tot = {y: defaultdict(lambda: defaultdict(float)) for y in ELECCIONES}
    with open(os.path.join(BASE, 'descargas', 'municipios.csv'), newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            for y in ELECCIONES:
                for k, x in r.items():
                    if k.startswith(f'{y}_v') and k not in (f'{y}_votantes', f'{y}_vOTROS') and x:
                        tot[y][r['mun_code'][:2]][k[len(y) + 2:]] += float(x)
    out = {}
    for y in ELECCIONES:
        out[y] = {}
        for p, v in tot[y].items():
            v = dict(v)
            if b[y, p] and 'SUMAR' in v:
                v['SUMAR'], v['_SUMAR2'] = max(v['SUMAR'] - b[y, p], b[y, p]), min(v['SUMAR'] - b[y, p], b[y, p])
            o = sorted(((x, k) for k, x in v.items() if x > 0), reverse=True)
            g = 'EMPATE' if len(o) > 1 and o[0][0] == o[1][0] else o[0][1]
            out[y][p] = 'SUMAR' if g == '_SUMAR2' else g
    return out


class Informe:
    def __init__(self):
        self.errores, self.vistos = defaultdict(list), defaultdict(int)

    def compara(self, fichero, y, clave, actual, esperado):
        self.vistos[fichero] += 1
        if esperado == 'OTROS':
            self.errores[fichero].append(f'{y} {clave}: gana una candidatura sin código propio (saldría en «Otros»)')
        elif actual != esperado:
            self.errores[fichero].append(f'{y} {clave}: el mapa dice {actual}, lista a lista gana {esperado}')

    def total(self):
        return sum(len(v) for v in self.errores.values())


def csv_gana(inf, nombre, clave, E):
    with open(os.path.join(BASE, 'descargas', nombre), newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            for y in ELECCIONES:
                a, e = r.get(f'{y}_gana', ''), E[y].get(r[clave])
                if a == '' and e is None:
                    continue
                inf.compara(nombre, y, r[clave], a or None, e)


def json_gana(inf, ruta, E, cods_de):
    d = json.load(open(ruta))
    cods = d.get('cod') or cods_de
    nombre = os.path.relpath(ruta, BASE)
    y_fich = os.path.basename(ruta)[:-5]
    for y in ELECCIONES:
        arr = d.get(f'{y}_gana') if y + '_gana' in d else (d.get('gana') if y_fich == y else None)
        if arr is None:
            continue
        for c, g in zip(cods, arr):
            e = E[y].get(c)
            if g in (None, -1) and e is None:
                continue
            a = 'EMPATE' if g == EMPATE else (FAMILIAS[g] if isinstance(g, int) and 0 <= g < len(FAMILIAS) else g)
            inf.compara(nombre, y, c, a, e)


def main():
    global FAMILIAS
    FAMILIAS = [f['cod'] for f in json.load(open(os.path.join(BASE, 'data', 'meta.json')))['familias']]
    S, M, P = {}, {}, {}
    for y in ELECCIONES:
        S[y], M[y], P[y] = esperados(y)
    inf = Informe()
    ps = provincias_site()
    for y in ELECCIONES:
        for p in sorted(P[y]):
            inf.compara('provincias (fichas)', y, p, ps[y].get(p), P[y][p])
    csv_gana(inf, 'municipios.csv', 'mun_code', M)
    csv_gana(inf, 'secciones.csv', 'tract_code', S)
    cods = json.load(open(os.path.join(BASE, 'data', 'municipios.json')))['cod']
    for f in ['municipios.json', 'municipios-ligero.json'] + [f'e/{y}.json' for y in ELECCIONES]:
        if os.path.exists(os.path.join(BASE, 'data', f)):
            json_gana(inf, os.path.join(BASE, 'data', f), M, cods)
    for f in sorted(glob.glob(os.path.join(BASE, 'data', 'sec', '[0-9][0-9].json'))):
        json_gana(inf, f, S, None)
    lineas = ['## Ganador del mapa, lista a lista (control_ganadores.py)', '']
    for f, n in sorted(inf.vistos.items()):
        e = inf.errores.get(f, [])
        lineas.append(f'- {f}: {n} ganadores comprobados, {len(e)} diferencias')
        lineas += [f'  - {x}' for x in e[:15]] + ([f'  - … y {len(e) - 15} más'] if len(e) > 15 else [])
    txt = '\n'.join(lineas)
    print(txt)
    if '--resumen' in sys.argv:
        open(sys.argv[sys.argv.index('--resumen') + 1], 'a', encoding='utf-8').write(txt + '\n')
    if inf.total():
        print(f'\nERROR: {inf.total()} ganadores del mapa no son la candidatura más votada.')
        sys.exit(1)
    print('\nOK: en todos, el ganador del mapa es la candidatura más votada (o empate).')


if __name__ == '__main__':
    main()
