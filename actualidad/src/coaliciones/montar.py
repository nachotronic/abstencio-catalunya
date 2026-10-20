"""Monta la pieza actualidad/src/mapa-coaliciones-izquierda-29n.html a partir de plantilla.html, datos.json
(calcular.py), mapa.json (provincias, el mismo dibujo que la pieza de los pactos del 29N) y c26.json
(coalición registrada para el 29N en cada provincia, de esa misma pieza).

Uso, desde la raíz del repositorio: python3 actualidad/src/coaliciones/montar.py
"""
import json, pathlib

AQUI = pathlib.Path(__file__).resolve().parent
SALIDA = AQUI.parent / 'mapa-coaliciones-izquierda-29n.html'
IZQ = {'Podemos', 'Unidos Podemos', 'Unidas Podemos', 'En Comú Podem', 'Compromís-Podemos', 'A la valenciana', 'En Marea',
       'IU-Unidad Popular', 'Más País', 'Compromís', 'Sumar'}
LARGO = {'2015_12': 'Diciembre de 2015', '2016_06': 'Junio de 2016', '2019_04': 'Abril de 2019', '2019_11': 'Noviembre de 2019', '2023_07': 'Julio de 2023'}
NOMBRE_LISTA = {'IU-Unidad Popular': 'Unidad Popular-IU', 'A la valenciana': 'Compromís-Podemos-EUPV', 'Más País': 'Más País y Més Compromís'}


def fmt(n):
    return f'{n:,}'.replace(',', '.')


def pct(a, b):
    return f'{100 * a / b:.1f}%'.replace('.', ',')


def main():
    d = json.load(open(AQUI / 'datos.json'))
    out, filas = {}, []
    for e, x in d.items():
        prov = {}
        for c, r in x['provincias'].items():
            prov[c] = {'n': r['prov'], 'e': r['escanos'], 'j': r['esc_juntos'],
                       'l': [[l['marca'], l['nombre'].title() if l['nombre'].isupper() else l['nombre'], l['votos'], l['pct'], l['esc']] for l in r['listas']]}
        marcas = sorted({l['marca'] for r in x['provincias'].values() for l in r['listas']}, key=lambda k: -x['votos'].get(k, 0))
        v = sum(x['votos'].get(k, 0) for k in marcas)
        esc = sum(x['esc_real'].get(k, 0) for k in marcas)
        quien = {}
        for r in x['provincias'].values():
            for k, s in r['cambio'].items():
                quien[k] = quien.get(k, 0) - s
        res = {'v': v, 'pct': round(100 * v / x['validos'], 3), 'esc': esc, 'j': x['esc_juntos'].get('Juntos', 0),
               'n': max(len(r['listas']) for r in x['provincias'].values()),
               'nm': len(marcas), 'p2': sum(1 for r in x['provincias'].values() if len([l for l in r['listas'] if l['pct'] >= 1 or l['esc']]) > 1),
               'quien': dict(sorted(quien.items(), key=lambda q: -q[1]))}
        juntos = {k: s for k, s in x['esc_juntos'].items()}
        out[e] = {'prov': prov, 'real': x['esc_real'], 'juntos': juntos, 'res': res}
        filas.append(f'<tr><td>{LARGO[e]}</td><td>{", ".join(NOMBRE_LISTA.get(k, k) for k in marcas)}</td><td class="n">{fmt(v)}</td>'
                     f'<td class="n">{pct(v, x["validos"])}</td><td class="n">{esc}</td><td class="n">{res["j"]}</td></tr>')
    tabla = ('<table><thead><tr><th>Elección</th><th>Listas del espacio</th><th class="n">Votos</th><th class="n">% válidos</th>'
             '<th class="n">Escaños</th><th class="n">Sumando sus votos</th></tr></thead><tbody>'
             + ''.join(filas) + '</tbody></table>')
    datos = {'el': out, 'MP': json.load(open(AQUI / 'mapa.json')), 'c26': json.load(open(AQUI / 'c26.json'))}
    s = (AQUI / 'plantilla.html').read_text(encoding='utf-8')
    s = s.replace('{{TABLA}}', tabla).replace('/*DATOS*/', json.dumps(datos, ensure_ascii=False, separators=(',', ':')))
    SALIDA.write_text(s, encoding='utf-8')


if __name__ == '__main__':
    main()
