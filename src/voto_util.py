"""Voto útil por provincia: el reparto de los escaños de 2026 con los votos de las generales de julio de 2023.

Los votos salen de generales-2026/data/agregados.json (2023_07, ámbito PR): microdatos de Interior por mesa, con el voto
desde el extranjero (CERA), sumados por agregados_historicos.py. Votos válidos = votos a candidaturas + votos en blanco.
Escaños de 2026: los de 2023 salvo Madrid (38) y Cádiz (8), Real Decreto 806/2026 (como actualidad/src/sistema/calcular.py).
Barrera: 3 % de los votos válidos de la circunscripción (LOREG, art. 163.1.a). Empates de cociente: más votos totales.

Lo usan las 52 páginas elecciones/…/voto-util-29n/ (territorios.py) y la pieza resumen de Actualidad.
Uso suelto, desde la raíz: python3 src/voto_util.py  (imprime el resumen y comprueba contra escanos-en-el-filo-29n)
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
AGREGADOS = ROOT / 'generales-2026' / 'data' / 'agregados.json'

ESC_2023 = {'01': 4, '02': 4, '03': 12, '04': 6, '05': 3, '06': 5, '07': 8, '08': 32, '09': 4, '10': 4, '11': 9, '12': 5,
            '13': 5, '14': 6, '15': 8, '16': 3, '17': 6, '18': 7, '19': 3, '20': 6, '21': 5, '22': 3, '23': 5, '24': 4,
            '25': 4, '26': 4, '27': 4, '28': 37, '29': 11, '30': 10, '31': 5, '32': 4, '33': 7, '34': 3, '35': 8, '36': 7,
            '37': 4, '38': 7, '39': 5, '40': 3, '41': 12, '42': 2, '43': 6, '44': 3, '45': 6, '46': 16, '47': 5, '48': 8,
            '49': 3, '50': 7, '51': 1, '52': 1}
ESC_2026 = {**ESC_2023, '28': 38, '11': 8}

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


def cargar():
    """{prov: {'n': nombre, 'e': escaños 2026, 'val': válidos, 'bl': blancos, 'c': [(nombre, votos, familia, siglas)]}}"""
    d = json.loads(AGREGADOS.read_text(encoding='utf-8'))['2023_07']['PR']
    out = {}
    for p, x in d.items():
        c = [(nombre(s, f), int(v), f, s) for s, v, _, f in x['c'] if v > 0]
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
    mal = comprobar(A)
    print('distintos de escanos-en-el-filo:', len(mal))
    for m in mal:
        print(' ', m)
