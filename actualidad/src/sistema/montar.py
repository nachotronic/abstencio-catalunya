"""Monta los HTML de trabajo de las piezas de sistema electoral (actualidad/src/<slug>.html) a partir de las
plantillas de esta carpeta, con los datos de cifras.json y simulador.json y las utilidades de comun.js.

Uso, desde la raíz del repositorio:
  python3 actualidad/src/sistema/calcular.py && python3 actualidad/src/sistema/montar.py && python3 actualidad/src/sistema/controles.py
Después, como el resto de Actualidad: python3 actualidad/src/construir.py
"""
import json, pathlib, re

AQUI = pathlib.Path(__file__).resolve().parent
C = json.load(open(AQUI / 'cifras.json'))
SIM = json.load(open(AQUI / 'simulador.json'))
BASE = (AQUI / 'base.css').read_text()
COMUN = (AQUI / 'comun.js').read_text()


def partidos(e, solo_con_escano=True):
    return [{'partido': q['partido'], 'votos': q['votos'], 'esc': q['escanos'], 'vpe': q['votos_por_escano'],
             'sin': q['votos_sin_escano'], 'pct_sin': q['pct_propio_sin_escano']}
            for q in C[e]['partidos'] if q['escanos'] or not solo_con_escano]


def datos_precio():
    prov = sorted(C['2023_07']['provincias'].values(), key=lambda r: r['votos_por_escano'])
    return {'prov': [{'nom': r['nombre'], 'n': r['escanos'], 'vpe': r['votos_por_escano'], 'esc': r['esc']} for r in prov],
            'part': {e: sorted(partidos(e), key=lambda q: q['vpe']) for e in ('2023_07', '2019_11')},
            'sim': SIM}


def datos_sin():
    out = {'part': {}, 'prov': {}, 'filo': {}, 'tot': {}}
    for e in ('2023_07', '2019_11'):
        out['part'][e] = [q for q in partidos(e, False) if q['sin'] >= 20000]
        out['prov'][e] = sorted(({'nom': r['nombre'], 'n': r['escanos'], 'pct': r['pct_sin_escano'], 'votos': r['votos_sin_escano'],
                                  'val': r['validos'], 'per': r['perdidos_por_partido']} for r in C[e]['provincias'].values()),
                                key=lambda r: -r['pct'])
        out['filo'][e] = sorted(({'nom': r['nombre'], 'n': r['escanos'], 'ult': r['ultimo'], 'asp': r['aspirante'], 'falta': r['votos_faltan']}
                                 for r in C[e]['provincias'].values() if r['votos_faltan'] < 1000), key=lambda r: r['falta'])
        out['tot'][e] = {'sin': C[e]['votos_sin_escano'], 'pct': C[e]['pct_sin_escano'], 'val': C[e]['validos']}
    return out


def montar(plantilla, slug, datos):
    t = (AQUI / plantilla).read_text()
    cab, sep, resto = t.partition('<script>')
    t = re.sub(r'(\d) %', r'\1&nbsp;%', cab) + sep + resto   # «12 %» sin partir la línea
    t = t.replace('/*BASE*/', BASE).replace('/*COMUN*/', COMUN)
    t = t.replace('/*DATOS*/', 'const D=' + json.dumps(datos, ensure_ascii=False, separators=(',', ':')) + ';')
    (AQUI.parent / f'{slug}.html').write_text(t)


if __name__ == '__main__':
    montar('precio.html', 'precio-del-escano-29n', datos_precio())
    if (AQUI / 'sinescano.html').exists():
        montar('sinescano.html', 'votos-sin-escano-29n', datos_sin())
