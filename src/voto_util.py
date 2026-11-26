"""Voto útil por provincia: el reparto de los escaños de 2026 con los votos de las generales de julio de 2023.

Los votos salen de generales-2026/data/agregados.json (2023_07, ámbito PR): microdatos de Interior por mesa, con el voto
desde el extranjero (CERA), sumados por agregados_historicos.py. Votos válidos = votos a candidaturas + votos en blanco.
Escaños de 2026: los de 2023 salvo Madrid (38) y Cádiz (8), Real Decreto 806/2026 (como actualidad/src/sistema/calcular.py).
Barrera: 3 % de los votos válidos de la circunscripción (LOREG, art. 163.1.a). Empates de cociente: más votos totales.

Lo usan las 52 páginas elecciones/…/voto-util-29n/ (territorios.py) y la pieza resumen de Actualidad.
Uso suelto, desde la raíz: python3 src/voto_util.py  (imprime el resumen y comprueba contra escanos-en-el-filo-29n)
"""
import functools
import csv
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
AGREGADOS = ROOT / 'generales-2026' / 'data' / 'agregados.json'
OTRAS_2023 = ROOT / 'generales-2026' / 'data' / 'voto_util_otras_2023.csv'   # lo escribe src/voto_util_otras.py

ESC_2023 = {'01': 4, '02': 4, '03': 12, '04': 6, '05': 3, '06': 5, '07': 8, '08': 32, '09': 4, '10': 4, '11': 9, '12': 5,
            '13': 5, '14': 6, '15': 8, '16': 3, '17': 6, '18': 7, '19': 3, '20': 6, '21': 5, '22': 3, '23': 5, '24': 4,
            '25': 4, '26': 4, '27': 4, '28': 37, '29': 11, '30': 10, '31': 5, '32': 4, '33': 7, '34': 3, '35': 8, '36': 7,
            '37': 4, '38': 7, '39': 5, '40': 3, '41': 12, '42': 2, '43': 6, '44': 3, '45': 6, '46': 16, '47': 5, '48': 8,
            '49': 3, '50': 7, '51': 1, '52': 1}
ESC_2026 = {**ESC_2023, '28': 38, '11': 8}
# Escaños de cada circunscripción en las generales anteriores (cuadros de diputados por circunscripción de Wikipedia, 26-11-2026),
# comprobados: con ellos y los votos de agregados.json, el reparto da los diputados oficiales de cada partido (OFICIALES, abajo)
ESC_HIST = {'2015_12': {**ESC_2023, '28': 36, '08': 31, '46': 15, '33': 8, '06': 6, '24': 5},
            '2016_06': {**ESC_2023, '28': 36, '08': 31, '33': 8, '06': 6},
            '2019_04': {**ESC_2023, '46': 15, '06': 6},
            '2019_11': {**ESC_2023, '46': 15, '06': 6},
            '2023_07': dict(ESC_2023)}
HIST = list(ESC_HIST)
ETIQ = {'2015_12': '2015', '2016_06': '2016', '2019_04': 'abril de 2019', '2019_11': 'noviembre de 2019', '2023_07': '2023'}
# Diputados por familia (las de agregados.json) que da el reparto, iguales a los oficiales de Interior: Podemos y sus confluencias,
# IU, Compromís y Más País van juntos en SUMAR; UPN-PP y Navarra Suma, en PP; NC con CC; el PRC en OTROS en abril de 2019
OFICIALES = {'2015_12': {'PP': 123, 'PSOE': 90, 'SUMAR': 71, 'CS': 40, 'ERC': 9, 'JUNTS': 8, 'PNV': 6, 'BILDU': 2, 'CC': 1},
             '2016_06': {'PP': 137, 'PSOE': 85, 'SUMAR': 71, 'CS': 32, 'ERC': 9, 'JUNTS': 8, 'PNV': 5, 'BILDU': 2, 'CC': 1},
             '2019_04': {'PSOE': 123, 'PP': 68, 'CS': 57, 'SUMAR': 43, 'VOX': 24, 'ERC': 15, 'JUNTS': 7, 'PNV': 6, 'BILDU': 4, 'CC': 2, 'OTROS': 1},
             '2019_11': {'PSOE': 120, 'PP': 91, 'VOX': 52, 'SUMAR': 38, 'ERC': 13, 'CS': 10, 'JUNTS': 8, 'PNV': 6, 'BILDU': 5, 'CUP': 2, 'CC': 2,
                         'BNG': 1, 'PRC': 1, 'TE': 1},
             '2023_07': {'PP': 137, 'PSOE': 121, 'VOX': 33, 'SUMAR': 31, 'ERC': 7, 'JUNTS': 7, 'BILDU': 6, 'PNV': 5, 'BNG': 1, 'UPN': 1, 'CC': 1}}

# Nombre corto de cada lista de 2023 en el texto, por familia (las que no están aquí, con sus siglas de Interior)
NOMBRE = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'SUMAR': 'Sumar', 'ERC': 'ERC', 'JUNTS': 'Junts', 'BILDU': 'EH Bildu', 'PNV': 'PNV',
          'BNG': 'BNG', 'CC': 'CC', 'UPN': 'UPN', 'CUP': 'CUP', 'TE': 'Teruel Existe', 'PRC': 'PRC', 'NC': 'NC-BC', 'SY': 'Soria ¡Ya!',
          'UPL': 'UPL', 'FO': 'Frente Obrero', 'CPM': 'Por Mi Región', 'XAV': 'Ávila', 'PACMA': 'PACMA'}
BARRERA = 0.03


def nombre(siglas, fam):
    if siglas == 'PACMA':
        return 'PACMA'
    if siglas == 'ESCAÑOS EN BLANCO':
        return 'Escaños en Blanco'
    return NOMBRE.get(fam, siglas)


_CAT, _VAL, _GAL = {'08', '17', '25', '43'}, {'03', '12', '46'}, {'15', '27', '32', '36'}
_SUMAR = {'2015_12': ('Podemos', 'En Comú Podem', 'Compromís-Podemos', 'En Marea'),
          '2016_06': ('Unidos Podemos', 'En Comú Podem', 'A la valenciana', 'En Marea'),
          '2019_04': ('Unidas Podemos', 'En Comú Podem', 'Unides Podem', 'En Común-Unidas Podemos'),
          '2019_11': ('Unidas Podemos', 'En Comú Podem', 'Unides Podem', 'En Común-Unidas Podemos')}
_SUMAR_2 = {'2015_12': 'IU-Unidad Popular', '2019_04': 'Compromís', '2019_11': 'Más País'}
_OTRAS = {'JUNTS': {'2015_12': 'Democràcia i Llibertat', '2016_06': 'CDC', '2019_04': 'JxCat', '2019_11': 'JxCat'},
          'CS': 'Ciudadanos', 'BILDU': 'EH Bildu', 'CC': 'CC', 'TE': '¡Teruel Existe!', 'CPM': 'Coalición por Melilla'}
_PP = {'UPN-PP': 'UPN-PP', 'NA+': 'Navarra Suma', 'PP-PAR': 'PP-PAR', 'PP-FORO': 'PP-Foro'}


def nombre_hist(y, p, siglas, fam, mayor_sumar):
    """Nombre corto de una lista de 2015 a 2019 (las de 2023, con nombre()). mayor_sumar: la lista de la familia SUMAR más votada
    en esa circunscripción; la otra (IU en 2015, Compromís y Más País en 2019) lleva su nombre."""
    if y == '2023_07':
        return nombre(siglas, fam)
    if fam == 'SUMAR':
        if siglas != mayor_sumar:
            return 'EUPV-Unitat Popular' if (y == '2015_12' and p in _VAL) else ('Més Compromís' if (y == '2019_11' and p in _VAL) else _SUMAR_2.get(y, siglas))
        g, c, v, gl = _SUMAR[y]
        return c if p in _CAT else v if p in _VAL else gl if p in _GAL else g
    if fam == 'PP':
        return _PP.get(siglas, 'PP')
    o = _OTRAS.get(fam)
    if isinstance(o, dict):
        return o.get(y, siglas)
    return o or NOMBRE.get(fam, siglas)


@functools.lru_cache(maxsize=None)
def historia(p):
    """El último escaño de p en cada generales desde 2015, con los votos y los escaños de entonces: quién se lo llevó, quién se quedó
    a las puertas, cuántos votantes que cambiaran de papeleta o votos nuevos le habrían bastado, y los votos que no eligieron a nadie."""
    d = json.loads(AGREGADOS.read_text(encoding='utf-8'))
    out = []
    for y in HIST:
        x = d[y]['PR'][p]
        votos, fam = {}, {}
        for s, v, _, f in x['c']:
            if v > 0:
                votos[s] = votos.get(s, 0) + v
                fam[s] = f
        val, e = sum(votos.values()) + int(x['bl']), ESC_HIST[y][p]
        esc, q = reparto(votos, val, e)
        u = q[e - 1]
        sg = next(t for t in q[e:] if t[2] != u[2])
        su = [l for l in votos if fam[l] == 'SUMAR']
        ms = max(su, key=lambda l: votos[l]) if su else None
        nm = lambda l: nombre_hist(y, p, l, fam[l], ms)
        sin = sum(v for l, v in votos.items() if not esc.get(l))
        out.append({'y': y, 'et': ETIQ[y], 'e': e, 'u': nm(u[2]), 'uf': fam[u[2]], 'uk': u[3], 'uq': u[0],
                    'a': nm(sg[2]), 'af': fam[sg[2]], 'ak': sg[3], 'c': votantes_que_cambian(votos, val, e, u[2], sg[2]),
                    'nv': votos_nuevos(votos, val, e, sg[2]), 'val': val, 'sin': sin, 'sin_pct': 100 * sin / val})
    return out


def comprobar_historia():
    """Los escaños de ESC_HIST y los votos de agregados.json dan los diputados oficiales de cada partido en cada elección."""
    d = json.loads(AGREGADOS.read_text(encoding='utf-8'))
    mal = {}
    for y, E in ESC_HIST.items():
        assert sum(E.values()) == 350, y
        tot = {}
        for p, x in d[y]['PR'].items():
            votos, fam = {}, {}
            for s, v, _, f in x['c']:
                if v > 0:
                    votos[s] = votos.get(s, 0) + v
                    fam[s] = f
            for l, k in reparto(votos, sum(votos.values()) + int(x['bl']), E[p])[0].items():
                tot[fam[l]] = tot.get(fam[l], 0) + k
        if tot != OFICIALES[y]:
            mal[y] = tot
    return mal


def cargar():
    """{prov: {'n': nombre, 'e': escaños 2026, 'val': válidos, 'bl': blancos, 'c': [(nombre, votos, familia, siglas)]}}"""
    d = json.loads(AGREGADOS.read_text(encoding='utf-8'))['2023_07']['PR']
    resto = {}   # la fila «Otras» de agregados.json (listas fuera de las 10 primeras), desglosada en sus candidaturas
    with open(OTRAS_2023, encoding='utf-8') as f_:
        for r in csv.DictReader(f_):
            resto.setdefault(r['prov'], []).append([r['siglas'], int(r['votos']), 0, 'OTROS'])
    out = {}
    for p, x in d.items():
        filas = [r for r in x['c'] if r[0] != 'Otras']
        if len(filas) < len(x['c']):
            assert sum(r[1] for r in resto[p]) == sum(r[1] for r in x['c'] if r[0] == 'Otras'), p
            filas += resto[p]
        c = [(nombre(s, f), int(v), f, s) for s, v, _, f in filas if v > 0]
        c.sort(key=lambda t: -t[1])
        out[p] = {'n': x['n'], 'e': ESC_2026[p], 'bl': int(x['bl']), 'val': sum(t[1] for t in c) + int(x['bl']), 'c': c}
    return out


def reparto(votos, val, e, contra=None):
    """votos {lista: votos}. Devuelve (escaños {lista: n}, cocientes ordenados [(cociente, votos, lista, k)]).
    Empate de cocientes: a la lista con más votos (LOREG 163.1.d). Con contra, esa lista pierde cualquier empate: así se calcula
    lo que le falta para superar a otra, como en las piezas del último escaño."""
    ok = {l: v for l, v in votos.items() if v >= BARRERA * val}
    q = sorted(((v / k, v, l, k) for l, v in ok.items() for k in range(1, e + 1)), key=lambda t: (-t[0], t[2] == contra, -t[1]))
    esc = {}
    for _, _, l, _ in q[:e]:
        esc[l] = esc.get(l, 0) + 1
    return esc, q


def votos_nuevos(votos, val, e, l):
    """Votos nuevos (de quien no votó a nadie) que le harían falta a l para un escaño más; los válidos suben con ellos."""
    base = reparto(votos, val, e)[0].get(l, 0)
    lo, hi = 0, 1
    while True:
        v = dict(votos); v[l] += hi
        if reparto(v, val + hi, e, l)[0].get(l, 0) > base:
            break
        lo, hi = hi, hi * 2
        if hi > 10 ** 8:
            return None
    while lo < hi:   # el mínimo x con un escaño más
        m = (lo + hi) // 2
        v = dict(votos); v[l] += m
        if reparto(v, val + m, e, l)[0].get(l, 0) > base:
            hi = m
        else:
            lo = m + 1
    return lo


def perdida_para_perder(votos, val, e, l, j):
    """Votos que puede perder l (a la abstención: los válidos bajan con ellos) antes de quedarse con menos de j escaños."""
    lo, hi = 0, votos[l]
    v = dict(votos); v[l] -= hi
    if reparto(v, val - hi, e)[0].get(l, 0) >= j:
        return None
    while lo < hi:   # el mínimo x con menos de j escaños
        m = (lo + hi) // 2
        v = dict(votos); v[l] -= m
        if reparto(v, val - m, e)[0].get(l, 0) < j:
            hi = m
        else:
            lo = m + 1
    return lo


# Seguro / probable / en juego: cuánto de su voto de 2023 tendría que perder (o ganar) la lista para que el escaño cambie
EN_JUEGO, PROBABLE = 10.0, 25.0


def categoria(pct):
    return 'juego' if pct < EN_JUEGO else ('probable' if pct < PROBABLE else 'seguro')


def votantes_que_cambian(votos, val, e, de, a):
    """Mínimo de votantes que, pasando de «de» a «a», le darían a «a» un escaño más (los válidos no cambian)."""
    base = reparto(votos, val, e)[0].get(a, 0)
    lo, hi = 0, votos[de]
    v = dict(votos); v[de] -= hi; v[a] += hi
    if reparto(v, val, e, a)[0].get(a, 0) <= base:
        return None
    while lo < hi:
        m = (lo + hi) // 2
        v = dict(votos); v[de] -= m; v[a] += m
        if reparto(v, val, e, a)[0].get(a, 0) > base:
            hi = m
        else:
            lo = m + 1
    return lo


def analizar(p, x):
    votos = {l: v for l, v, _, _ in x['c']}
    fam = {l: f for l, _, f, _ in x['c']}
    val, e = x['val'], x['e']
    esc, q = reparto(votos, val, e)
    orden = q[:e]                                   # [(cociente, votos, lista, k)] en el orden en que se reparten
    ultimo = orden[-1]
    puertas = q[e:e + 3]                            # los tres siguientes cocientes
    sig = next(t for t in q[e:] if t[2] != ultimo[2])   # el primero de otra lista: el que le quitaría el último escaño
    cambian = votantes_que_cambian(votos, val, e, ultimo[2], sig[2])
    nuevos = {l: votos_nuevos(votos, val, e, l) for l in votos}
    barrera = BARRERA * val
    sin = {l: v for l, v in votos.items() if not esc.get(l)}
    escanos = []   # por lista: [(j, categoría, % de su voto)] de los que tiene, y el siguiente si lo tendría con menos de EN_JUEGO % más
    for l, v in votos.items():
        n_ = esc.get(l, 0)
        filas = []
        for j in range(n_, 0, -1):
            x_ = perdida_para_perder(votos, val, e, l, j)
            pc = 100 * x_ / v if x_ is not None else 100.0
            filas.append((j, categoria(pc), pc))
            if pc >= PROBABLE:   # los de abajo aguantan todavía más
                filas += [(i, 'seguro', None) for i in range(j - 1, 0, -1)]
                break
        alcance = []
        if nuevos[l] is not None and 100 * nuevos[l] / v < EN_JUEGO:
            alcance.append((n_ + 1, 100 * nuevos[l] / v))
        escanos.append({'l': l, 'f': fam[l], 'esc': sorted(filas), 'alcance': alcance})
    return {
        'p': p, 'n': x['n'], 'e': e, 'val': val, 'bl': x['bl'], 'barrera': barrera,
        'listas': [{'l': l, 'f': fam[l], 'v': v, 'pct': 100 * v / val, 'esc': esc.get(l, 0), 'nuevos': nuevos[l],
                    'cociente': (v / (esc.get(l, 0) + 1)) if v >= barrera else None, 'barrera': v >= barrera} for l, v in votos.items()],
        'orden': [{'l': l, 'f': fam[l], 'k': k, 'q': c} for c, _, l, k in orden],
        'puertas': [{'l': l, 'f': fam[l], 'k': k, 'q': c} for c, _, l, k in puertas],
        'ultimo': {'l': ultimo[2], 'f': fam[ultimo[2]], 'k': ultimo[3], 'q': ultimo[0]},
        'siguiente': {'l': sig[2], 'f': fam[sig[2]], 'k': sig[3], 'q': sig[0]},
        'cambian': cambian, 'nuevos_sig': nuevos[sig[2]],
        'sin_escano': sum(sin.values()), 'sin_escano_pct': 100 * sum(sin.values()) / val,
        'sin_escano_listas': sorted(sin.items(), key=lambda t: -t[1]),
        'escanos': escanos,
    }


def todas():
    return {p: analizar(p, x) for p, x in sorted(cargar().items())}


def comprobar(A):
    """Contra la pieza «Seis escaños que se decidieron por menos de mil votantes» (objeto F, mismos votos y escaños)."""
    src = (ROOT / 'actualidad' / 'src' / 'escanos-en-el-filo-29n.html').read_text(encoding='utf-8')
    F = json.loads(re.search(r'const F=(\{.*?\});', src, re.S).group(1))
    mal = []
    for p, a in A.items():
        f = F[p]
        if (f['e'], f['un'], f['an'], f['c'], f['f']) != (a['e'], a['ultimo']['k'], a['siguiente']['k'], a['cambian'], a['nuevos_sig']):
            mal.append((p, a['n'], f, (a['e'], a['ultimo']['l'], a['ultimo']['k'], a['siguiente']['l'], a['siguiente']['k'], a['cambian'], a['nuevos_sig'])))
    return mal


if __name__ == '__main__':
    A = todas()
    assert sum(a['e'] for a in A.values()) == 350
    print('escaños por lista:', {l: sum(x['esc'] for a in A.values() for x in a['listas'] if x['l'] == l) for l in ['PP', 'PSOE', 'Vox', 'Sumar']})
    for p, a in A.items():
        print(p, a['n'], a['e'], a['ultimo']['l'], a['ultimo']['k'], '→', a['siguiente']['l'], a['siguiente']['k'], a['cambian'], a['nuevos_sig'],
              f"sin escaño {a['sin_escano']} ({a['sin_escano_pct']:.1f} %)")
    assert not comprobar_historia(), comprobar_historia()
    print('historia: escaños oficiales de 2015 a 2023, bien')
    mal = comprobar(A)
    print('distintos de escanos-en-el-filo:', len(mal))
    for m in mal:
        print(' ', m)
