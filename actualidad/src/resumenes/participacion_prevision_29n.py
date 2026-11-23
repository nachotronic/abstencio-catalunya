"""Participación en las elecciones generales del 29N: lo que prevén las encuestas y cómo ha ido la participación con los
resultados desde 1977 (pieza del 23-11-2026, último día en que se pueden publicar encuestas).

- Previsión: participación estimada en la última entrega de cada encuestadora que la publica, con campo terminado desde el
  2-11-2026 (tres semanas), según la tabla de Wikipedia «Opinion polling for the 2026 Spanish general election» (consultada el
  23-11-2026 por la mañana): actualidad/src/resumenes/datos/participacion_encuestas_29n.csv. Ipsos da una horquilla (72-74):
  se usa el punto medio.
- Historia: votantes sobre censo de residentes en España (sin voto exterior) y voto a candidaturas por familia, de
  generales-2026/descargas/municipios_historico.csv (1977-2000) y municipios.csv (2004-2023), Ministerio del Interior.
  «Izquierda» = PSOE + la familia del PCE (PCE, IU, Podemos y sus confluencias, Sumar), columnas PSOE y SUMAR.
Uso, desde la raíz: python3 actualidad/src/resumenes/participacion_prevision_29n.py
"""
import json
import os
import statistics

import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, barras, mapa_provincias, pieza
from mapa_ccaa import NOM, caminos

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
s1 = lambda v: f'{v:+.1f}'.replace('.', ',').replace('-', '−')
SLUG = 'participacion-elecciones-generales-29n-prevision'
WP = 'https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Spanish_general_election'

# ---------- Historia ----------
h = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios_historico.csv', dtype={'mun_code': str})
m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str})
ANOS = ['1977_06', '1979_03', '1982_10', '1986_06', '1989_10', '1993_06', '1996_03', '2000_03',
        '2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
MES = {'04': 'abr.', '11': 'nov.'}
NOMBRE = {y: f'{MES[y[5:]]} {y[:4]}' if y[:4] == '2019' else y[:4] for y in ANOS}
GANA = {'1977_06': 'UCD', '1979_03': 'UCD', '1996_03': 'PP', '2000_03': 'PP', '2011_11': 'PP', '2015_12': 'PP', '2016_06': 'PP', '2023_07': 'PP'}
H = []
for y in ANOS:
    t = h if y < '2004' else m
    cols = [c for c in t.columns if c.startswith(y + '_v') and c != f'{y}_votantes']
    val = t[cols].sum().sum()
    s = lambda k: t[f'{y}_v{k}'].sum() / val * 100 if f'{y}_v{k}' in t else 0.0
    prim = max(('PSOE', 'PP', 'UCD'), key=s)
    H.append(dict(y=y, nombre=NOMBRE[y], part=t[f'{y}_votantes'].sum() / t[f'{y}_censo'].sum() * 100, izq=s('PSOE') + s('SUMAR'), gana=prim))
for i, r in enumerate(H):
    r['dpart'] = r['part'] - H[i - 1]['part'] if i else None
    r['dizq'] = r['izq'] - H[i - 1]['izq'] if i else None
    assert r['gana'] == GANA.get(r['y'], 'PSOE'), r       # el partido con más votos coincide con el ganador conocido
P = {r['y']: r for r in H}
P23 = P['2023_07']['part']
assert 70.3 < P23 < 70.5

# Subidas de más de cinco puntos: las cuatro, el PSOE primero
SUBE5 = [r for r in H if r['dpart'] is not None and r['dpart'] > 5]
assert [r['y'] for r in SUBE5] == ['1982_10', '1993_06', '2004_03', '2019_04'] and all(r['gana'] == 'PSOE' for r in SUBE5)
# Subidas pequeñas (menos de dos puntos): las tres, el PP primero
SUBE_POCO = [r for r in H if r['dpart'] is not None and 0 < r['dpart'] <= 5]
assert [r['y'] for r in SUBE_POCO] == ['1996_03', '2015_12', '2023_07'] and all(r['gana'] == 'PP' for r in SUBE_POCO)
assert max(r['dpart'] for r in SUBE_POCO) < 1.5 < 2  # 2015: +1,4 con los datos por mesa; con el avance de la noche, +1,5: el texto dice «menos de dos»
BAJA = [r for r in H if r['dpart'] is not None and r['dpart'] < 0]
assert len(BAJA) == 8
BAJA_PSOE = [r['nombre'] for r in BAJA if r['gana'] == 'PSOE']
BAJA_PP = [r['nombre'] for r in BAJA if r['gana'] == 'PP']
assert BAJA_PSOE == ['1986', '1989', '2008', 'nov. 2019'] and BAJA_PP == ['2000', '2011', '2016']
# La izquierda: sube mucho en 1982 y 2004; no se mueve en 1993 ni en abril de 2019
IZ = {y: P[y]['dizq'] for y in ('1982_10', '2004_03', '1993_06', '2019_04', '2000_03', '2011_11')}
assert IZ['1982_10'] > 10 and IZ['2004_03'] > 7 and abs(IZ['1993_06']) < .5 and abs(IZ['2019_04']) < .5
assert IZ['2000_03'] < -7 and IZ['2011_11'] < -11
# Por encima del 75 %: siete elecciones, cinco con el PSOE primero
ALTA = [r for r in H if r['part'] > 75]
assert len(ALTA) == 7 and sum(r['gana'] == 'PSOE' for r in ALTA) == 5
ALTA_NO = sorted((r['nombre'], r['gana']) for r in ALTA if r['gana'] != 'PSOE')
assert ALTA_NO == [('1977', 'UCD'), ('1996', 'PP')]

# ---------- Previsión de las encuestas ----------
E = pd.read_csv(RAIZ / 'actualidad/src/resumenes/datos/participacion_encuestas_29n.csv')
E['valor'] = E.participacion.map(lambda v: sum(map(float, v.split('–'))) / len(v.split('–')))
E = E.sort_values('valor', ascending=False).reset_index(drop=True)
assert len(E) == 10 and E.casa.is_unique and (E.fin >= '2026-11-02').all()
MED = statistics.median(E.valor)
MIN, MAX = E.valor.min(), E.valor.max()
assert (round(MED, 1), MIN, MAX) == (73.1, 65.5, 77.3), (MED, MIN, MAX)
SOBRE = int((E.valor > P23).sum())
assert SOBRE == 8
CASA_MIN, CASA_MAX = E.iloc[-1].casa, E.iloc[0].casa
assert (CASA_MIN, CASA_MAX) == ('Celeste-Tel', 'Sigma Dos')
SUBE_MED = MED - P23

ACC, GRIS, BAJA = 'var(--acc)', 'var(--otros)', 'var(--baja)'
COL = {'PSOE': 'var(--psoe)', 'PP': 'var(--pp)', 'UCD': GRIS}
_txt = lambda r: r.participacion.replace('.', ',').replace('–', '-') + ' %'
g_enc = figura(f'La mediana de las encuestas, en el {p(MED)} %',
               'Participación que estima la última encuesta de cada encuestadora que la publica, con campo terminado en las tres últimas semanas, y la de 2023 en España (sin voto exterior)',
               barras([(f'{r.casa}', r.valor, ACC, _txt(r)) for r in E.itertuples()], 85, 'Participación estimada por cada encuestadora',
                      W=400, ml=118, alto=22, linea=(P23, f'2023: {p(P23)} %'), separar=True),
               f'Fuente: las encuestas citadas, recogidas en <a href="{WP}">Wikipedia</a> (CC BY-SA 4.0); 2023, Ministerio del Interior. Ipsos da una horquilla, del 72 al 74 %: la barra marca el centro.',
               [('Participación estimada', ACC)],
               (['Encuestadora', 'Campo hasta el', 'Participación (%)'],
                [[esc(r.firma.replace('/', ' / ')), r.fin[8:].lstrip('0') + ' nov.', _txt(r)[:-2]] for r in E.itertuples()]))

g_hist = figura('Participación en cada elección general y quién quedó primero',
                'Porcentaje de los electores residentes en España que votó, sin el voto exterior. El color, el partido con más votos',
                barras([(r['nombre'], r['part'], COL[r['gana']], f'{p(r["part"])} %') for r in H], 85, 'Participación y partido más votado en cada elección general',
                       W=400, ml=80, alto=22, linea=(MED, f'Encuestas 29N: {p(MED)} %'), separar=True),
                'Fuente: Ministerio del Interior, resultados por municipio. Votantes sobre censo de residentes en España. Cálculo propio. En la tabla, «Cambio» es la diferencia en puntos con la elección anterior y «PSOE e izq.», el voto al PSOE y a la familia del PCE (IU, Podemos, Sumar).',
                [('PSOE', COL['PSOE']), ('PP', COL['PP']), ('UCD', GRIS)],
                (['Elección', 'Votó (%)', 'Cambio', 'PSOE e izq. (%)', 'Primero'],
                 [[r['nombre'], p(r['part']), s1(r['dpart']) if r['dpart'] is not None else '–', p(r['izq']), r['gana']] for r in H]))

_cambios = [r for r in H if r['dpart'] is not None]
g_cambio = figura('Cuando la participación subió más de cinco puntos, el PSOE quedó primero',
                  'Cambio de la participación frente a la elección anterior, en puntos. El color, el partido con más votos',
                  barras([(r['nombre'], abs(r['dpart']), COL[r['gana']], ('sube ' if r['dpart'] > 0 else 'baja ') + p(abs(r['dpart']))) for r in sorted(_cambios, key=lambda r: -r['dpart'])],
                         14, 'Cambio de la participación y partido más votado', W=400, ml=80, alto=22),
                  'Fuente: Ministerio del Interior. Votantes sobre censo de residentes en España. Cálculo propio. Ordenadas de la que más subió a la que más bajó.',
                  [('PSOE', COL['PSOE']), ('PP', COL['PP']), ('UCD', GRIS)])

R82, R93, R96, R04, R19A, R00, R11, R23, R79 = (P[y] for y in ('1982_10', '1993_06', '1996_03', '2004_03', '2019_04', '2000_03', '2011_11', '2023_07', '1979_03'))
BENEF = 'a-quien-beneficia-abstencion-29n'

# ---------- Cambios de ciclo: elecciones tras las que cambió el partido del Gobierno ----------
CICLO = [('1982_10', 'UCD', 'PSOE'), ('1996_03', 'PSOE', 'PP'), ('2004_03', 'PP', 'PSOE'), ('2011_11', 'PSOE', 'PP')]
assert [P[y]['gana'] for y, _, a in CICLO] == [a for _, _, a in CICLO]
assert [round(P[y]['dpart'], 1) for y, _, _ in CICLO] == [12.6, 1.0, 7.2, -3.6]
g_ciclo = figura('Los dos cambios hacia el PSOE llegaron con grandes subidas; los dos hacia el PP, no',
                 'Cambio de la participación frente a la elección anterior en las cuatro elecciones tras las que cambió el partido del Gobierno, en puntos',
                 barras([(f'{P[y]["nombre"]}: {de} → {a}', P[y]['dpart'] if P[y]['dpart'] > 0 else -P[y]['dpart'], COL[a],
                          ('sube ' if P[y]['dpart'] > 0 else 'baja ') + p(abs(P[y]['dpart']))) for y, de, a in CICLO], 14,
                        'Cambio de la participación en los cambios de Gobierno', W=400, ml=150, alto=26),
                 'Fuente: Ministerio del Interior. Votantes sobre censo de residentes en España. Cálculo propio. El color, el partido que llegó al Gobierno.',
                 [('Llega el PSOE', COL['PSOE']), ('Llega el PP', COL['PP'])],
                 (['Elección', 'Del Gobierno sale', 'Llega', 'Participación (%)', 'Cambio (puntos)'],
                  [[P[y]['nombre'], de, a, p(P[y]['part']), s1(P[y]['dpart'])] for y, de, a in CICLO]))


# ---------- Cambio de participación frente a cambio del voto al PSOE y su izquierda ----------
ETIQUETAS = {'1979', '1982', '1986', '2000', '2004', '2011', '2015', '2016'}   # las de cerca del cero se solapan: quedan en el título emergente y la tabla


def dispersion(puntos, W=380, Hh=300):
    ml, mb, mt, mr = 40, 34, 10, 12
    xs, ys = [q[1] for q in puntos], [q[2] for q in puntos]
    x0, x1, y0, y1 = -13, 13, -12, 12
    X = lambda v: ml + (v - x0) / (x1 - x0) * (W - ml - mr)
    Y = lambda v: mt + (y1 - v) / (y1 - y0) * (Hh - mt - mb)
    o = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="Cambio de participación y cambio del voto al PSOE y su izquierda en cada elección">']
    for v in (-10, -5, 0, 5, 10):
        o.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{mt}" y2="{Hh - mb}" stroke="var(--grid)" stroke-width="{1 if v == 0 else .5}"/>')
        o.append(f'<line x1="{ml}" x2="{W - mr}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="var(--grid)" stroke-width="{1 if v == 0 else .5}"/>')
        o.append(f'<text x="{X(v):.1f}" y="{Hh - mb + 14}" text-anchor="middle" class="lab">{s1(v) if v else "0"}</text>')
        o.append(f'<text x="{ml - 6}" y="{Y(v) + 4:.1f}" text-anchor="end" class="lab">{s1(v) if v else "0"}</text>')
    o.append(f'<text x="{(ml + W - mr) / 2:.0f}" y="{Hh - 4}" text-anchor="middle" class="lab">Cambio de participación (puntos)</text>')
    for nom, x, y, col in puntos:
        o.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="5" fill="{col}" fill-opacity=".85"><title>{esc(nom)}: participación {s1(x)}, PSOE y su izquierda {s1(y)}</title></circle>')
        if nom in ETIQUETAS:
            der = x < 9
            o.append(f'<text x="{X(x) + (7 if der else -7):.1f}" y="{Y(y) + 4:.1f}"{"" if der else " text-anchor=\"end\""} style="font-size:11px">{esc(nom)}</text>')
    o.append('</svg>')
    return ''.join(o)


PARES = [(r['nombre'], r['dpart'], r['dizq'], COL[r['gana']]) for r in H if r['dpart'] is not None]
CORR = statistics.correlation([q[1] for q in PARES], [q[2] for q in PARES])
assert 0.55 < CORR < 0.62, CORR
MISMO = sum(1 for _, x, y, _ in PARES if x * y > 0)
assert MISMO == 10 and len(PARES) == 15, MISMO
g_disp = figura('Cuando sube la participación, el voto al PSOE y su izquierda tiende a subir, con excepciones',
                'Cada punto es una elección general: cambio de la participación (horizontal) y del voto al PSOE y a la familia del PCE (vertical) frente a la elección anterior, en puntos. El color, el partido más votado. Las elecciones sin nombre, cerca del centro, están en la tabla',
                dispersion(PARES),
                f'Fuente: Ministerio del Interior. Cálculo propio. Correlación entre los dos cambios, con 15 elecciones: {n(CORR, 2)}.',
                [('PSOE primero', COL['PSOE']), ('PP primero', COL['PP']), ('UCD primero', GRIS)],
                (['Elección', 'Participación (puntos)', 'PSOE y su izquierda (puntos)'], [[q[0], s1(q[1]), s1(q[2])] for q in PARES]))

# ---------- Provincias: 2023 y cambio desde noviembre de 2019 ----------
m = m.copy()
m['prov'] = m.mun_code.str[:2]
G = m.groupby(['prov', 'provincia'])[['2023_07_votantes', '2023_07_censo', '2019_11_votantes', '2019_11_censo']].sum().reset_index()
G['p23'] = G['2023_07_votantes'] / G['2023_07_censo'] * 100
G['p19'] = G['2019_11_votantes'] / G['2019_11_censo'] * 100
G['d'] = G.p23 - G.p19
G['nombre'] = G.provincia.str.split('/').str[0]
assert len(G) == 52
_vc = lambda y: [c for c in m.columns if c.startswith(y + '_v') and c != f'{y}_votantes']
_CAT = {'08', '17', '25', '43'}
_nom = lambda k, prov: 'PSC' if k == 'PSOE' and prov in _CAT else NOM.get(k, k)
for y, col in (('2023_07', 'g23'), ('2019_11', 'g19')):
    V = m.groupby('prov')[_vc(y)].sum()
    G[col] = G.prov.map(lambda c: _nom(V.loc[c].idxmax()[len(y) + 2:], c))
assert dict(zip(G.nombre, G.g23))['Barcelona'] == 'PSC' and dict(zip(G.nombre, G.g23))['Madrid'] == 'PP'
G = G.sort_values('p23').reset_index(drop=True)
TRAMOS = [(0, 65, .3, 'Menos del 65 %'), (65, 70, .5, 'Del 65 al 70 %'), (70, 75, .75, 'Del 70 al 75 %'), (75, 101, 1, 'El 75 % o más')]
op23 = {r.prov: next(o for a, b, o, _ in TRAMOS if a <= r.p23 < b) for r in G.itertuples()}
N_TRAMO = [int(((G.p23 >= a) & (G.p23 < b)).sum()) for a, b, _, _ in TRAMOS]
assert N_TRAMO == [8, 9, 29, 6], N_TRAMO
ALTAS, BAJAS = G.iloc[::-1].head(3), G.head(4)
assert list(ALTAS.nombre) == ['Segovia', 'Cuenca', 'Ávila'] and list(BAJAS.nombre) == ['Melilla', 'Ceuta', 'Lleida', 'Girona']
g_mapa23 = figura(f'Votó más de un 75 % en {N_TRAMO[3]} provincias y menos de un 65 % en {N_TRAMO[0]}',
                  'Participación de los residentes en España en las generales de julio de 2023, por provincia. Cuanto más intenso el color, más participación. Toca o pasa el ratón por una provincia para ver sus datos',
                  mapa_provincias({r.prov: ACC for r in G.itertuples()}, {r.prov: f'{r.nombre}: {p(r.p23)} %' for r in G.itertuples()},
                                  'Participación en 2023 por provincia', op23, claves=True),
                  'Fuente: Ministerio del Interior, resultados por municipio. Votantes sobre censo de residentes en España. Cálculo propio. Ceuta y Melilla no se ven a esta escala: 55,7 % y 49,8 %.'
                  .replace('55,7', p(G[G.prov == '51'].p23.iloc[0])).replace('49,8', p(G[G.prov == '52'].p23.iloc[0])),
                  [(t, f'rgba(162,39,95,{o})') for _, _, o, t in TRAMOS],
                  (['Provincia', '2023 (%)'], [[esc(r.provincia), p(r.p23)] for r in G.iloc[::-1].itertuples()]))
SUBEN = int((G.d > 0).sum())
assert SUBEN == 41
CAT = G[G.prov.isin(['08', '17', '25', '43'])]
assert (CAT.d < -4.9).all()
SUBE_MAS = G.sort_values('d').iloc[::-1].head(4)
assert list(SUBE_MAS.nombre) == ['Lugo', 'A Coruña', 'Soria', 'Ourense']
GAL = G[G.prov.isin(['15', '27', '32', '36'])]
assert (GAL.d > 5.7).all()
opd = {r.prov: min(1, .3 + abs(r.d) / 9) for r in G.itertuples()}
g_mapad = figura(f'Entre 2019 y 2023, la participación subió en {SUBEN} provincias; en Cataluña bajó',
                 'Cambio de la participación entre noviembre de 2019 y julio de 2023, en puntos. Cuanto más intenso el color, mayor el cambio. Toca o pasa el ratón por una provincia para ver sus datos',
                 mapa_provincias({r.prov: (ACC if r.d > 0 else BAJA) for r in G.itertuples()}, {r.prov: f'{r.nombre}: {s1(r.d)} puntos' for r in G.itertuples()},
                                 'Cambio de la participación entre 2019 y 2023 por provincia', opd, claves=True),
                 'Fuente: Ministerio del Interior. Votantes sobre censo de residentes en España. Cálculo propio.',
                 [('Sube', ACC), ('Baja', BAJA)],
                 (['Provincia', 'Nov. 2019 (%)', '2023 (%)', 'Cambio'], [[esc(r.provincia), p(r.p19), p(r.p23), s1(r.d)] for r in G.sort_values('d').iloc[::-1].itertuples()]))

g_mapa23 = g_mapa23.replace('<div class="chart">', '<div class="chart" data-pop="prov">', 1)
g_mapad = g_mapad.replace('<div class="chart">', '<div class="chart" data-pop="prov">', 1)

# ---------- Municipios: tamaño, grandes ciudades y mapa municipal del cambio 2019-2023 ----------
M = m[(m['2023_07_censo'] > 0) & (m['2019_11_censo'] > 0)].copy()
M['p23'] = M['2023_07_votantes'] / M['2023_07_censo'] * 100
M['p19'] = M['2019_11_votantes'] / M['2019_11_censo'] * 100
M['d'] = M.p23 - M.p19
assert len(M) == 8131
TAM = [(0, 1000, 'Menos de 1.000'), (1000, 5000, 'De 1.000 a 5.000'), (5000, 20000, 'De 5.000 a 20.000'),
       (20000, 100000, 'De 20.000 a 100.000'), (100000, 500000, 'De 100.000 a 500.000'), (500000, 10**9, 'Más de 500.000')]
_v23 = _vc('2023_07')
T = []
for a, b, nom in TAM:
    q = M[(M['2023_07_censo'] >= a) & (M['2023_07_censo'] < b)]
    val = q[_v23].sum().sum()
    T.append(dict(nom=nom, n=len(q), censo=q['2023_07_censo'].sum(), p23=q['2023_07_votantes'].sum() / q['2023_07_censo'].sum() * 100,
                  p19=q['2019_11_votantes'].sum() / q['2019_11_censo'].sum() * 100,
                  pp=q['2023_07_vPP'].sum() / val * 100, psoe=q['2023_07_vPSOE'].sum() / val * 100))
for t in T:
    t['d'] = t['p23'] - t['p19']
assert [t['n'] for t in T] == [5302, 1776, 764, 243, 41, 5]
assert all(T[i]['d'] > T[i + 1]['d'] for i in range(3)) and T[-1]['d'] < 0 < T[-2]['d']   # cuanto más pequeño, más subió; en las cinco más grandes, bajó
assert T[0]['p23'] > T[-1]['p23'] > T[3]['p23'] == min(t['p23'] for t in T)
assert all(31.5 < t['pp'] < 35.5 and 29.5 < t['psoe'] < 33.5 for t in T)   # el reparto PP-PSOE apenas cambia con el tamaño
g_tam = figura('Cuanto más pequeño el municipio, más subió la participación entre 2019 y 2023',
               'Cambio de la participación entre noviembre de 2019 y julio de 2023, en puntos, según el número de electores del municipio en 2023',
               barras([(t['nom'], abs(t['d']), ACC if t['d'] > 0 else BAJA, ('sube ' if t['d'] > 0 else 'baja ') + p(abs(t['d']))) for t in T], 4,
                      'Cambio de la participación por tamaño del municipio', W=400, ml=140, alto=24),
               'Fuente: Ministerio del Interior, resultados por municipio. Votantes sobre censo de residentes en España. Cálculo propio. Los cinco de más de 500.000 electores son Madrid, Barcelona, Valencia, Sevilla y Zaragoza.',
               [('Sube', ACC), ('Baja', BAJA)],
               (['Electores del municipio', 'Municipios', 'Nov. 2019 (%)', '2023 (%)', 'Cambio', 'PP 2023 (%)', 'PSOE 2023 (%)'],
                [[t['nom'], n(t['n']), p(t['p19']), p(t['p23']), s1(t['d']), p(t['pp']), p(t['psoe'])] for t in T]))
GR = M[M['2023_07_censo'] > 200000].sort_values('d', ascending=False)
assert len(GR) == 15 and list(GR.municipio[:2]) == ['Gijón', 'Palma'] and GR.municipio.iloc[-1] == 'Barcelona'
GR_SUBE = int((GR.d > 0).sum())
PLANO = list(GR[GR.d.abs() < .1].municipio)
assert GR_SUBE == 8 and sorted(PLANO) == ['Córdoba', 'Málaga', 'Zaragoza'], (GR_SUBE, PLANO)
_ciudad = lambda x: x.split('/')[0] if x != 'Alacant/Alicante' else 'Alicante'
g_ciud = figura(f'En las 15 ciudades con más de 200.000 electores, la participación subió en {GR_SUBE} y bajó en {len(GR) - GR_SUBE}',
                'Cambio de la participación entre noviembre de 2019 y julio de 2023, en puntos',
                barras([(_ciudad(r.municipio), abs(r.d), ACC if r.d > 0 else BAJA, ('sube ' if r.d > 0 else 'baja ') + p(abs(r.d))) for r in GR.itertuples()], 7,
                       'Cambio de la participación en las grandes ciudades', W=400, ml=150, alto=22),
                'Fuente: Ministerio del Interior, resultados por municipio. Votantes sobre censo de residentes en España. Cálculo propio.',
                [('Sube', ACC), ('Baja', BAJA)],
                (['Ciudad', 'Nov. 2019 (%)', '2023 (%)', 'Cambio'], [[_ciudad(r.municipio), p(r.p19), p(r.p23), s1(r.d)] for r in GR.itertuples()]))
GIJ, PAL, BCNm, MADm, VLC = (GR[GR.municipio == x].iloc[0] for x in ('Gijón', 'Palma', 'Barcelona', 'Madrid', 'València'))

# Mapa municipal: un trazado por municipio con data-k, agrupados por color; la ventana emergente lee D.M
PEN = [f'{i:02d}' for i in range(1, 53) if i not in (35, 38, 51, 52)]
_CACHE = os.environ.get('CACHE_CAMINOS')   # el mismo formato que abstencion_mapa.py: caminos() tarda unos 14 minutos con toda España
if _CACHE and os.path.exists(_CACHE):
    CAM, HMAP, CAMC, HMAPC = json.load(open(_CACHE))
else:
    CAM, HMAP = caminos(PEN, W=640, lat=40, umbral=3.5)
    CAMC, HMAPC = caminos(['35', '38'], W=640, lat=28.3, umbral=2)
TRAMOS_M = [(-99, -6, BAJA, 1, 'Baja más de 6'), (-6, -3, BAJA, .65, 'Baja de 3 a 6'), (-3, 0, BAJA, .35, 'Baja hasta 3'),
            (0, 3, ACC, .35, 'Sube hasta 3'), (3, 6, ACC, .65, 'Sube de 3 a 6'), (6, 99, ACC, 1, 'Sube más de 6')]
DM = dict(zip(M.mun_code, M.d))
_tr = lambda k: next(i for i, (a, b, *_ ) in enumerate(TRAMOS_M) if a <= DM[k] < b) if k in DM else None


ORD = []   # códigos de municipio en el orden de los trazados: la ventana emergente busca cada trazado por su posición, sin data-k (unos 120 KB menos)


def mapa_mun(cam, H, etiqueta):
    por = {}
    for k, d in cam.items():
        por.setdefault(_tr(k), []).append((k, f'<path d="{d}"/>'))
    g = ''
    for i, v in por.items():
        ORD.extend(k for k, _ in v)
        g += f'<g fill="{"var(--otros)" if i is None else TRAMOS_M[i][2]}" fill-opacity="{1 if i is None else TRAMOS_M[i][3]}">{"".join(t for _, t in v)}</g>'
    return (f'<svg viewBox="0 0 640 {H}" role="img" aria-label="{esc(etiqueta)}" style="max-width:640px;margin:0 auto;display:block">'
            f'<g stroke="var(--bg)" stroke-width=".3" stroke-linejoin="round">{g}</g></svg>')


SIN_GEO = sorted(set(M.mun_code) - set(CAM) - set(CAMC))
MSUBE = int((M.d > 0).sum())
CENSO_SUBE = M[M.d > 0]['2023_07_censo'].sum() / M['2023_07_censo'].sum() * 100
assert MSUBE == 6150 and 49 < CENSO_SUBE < 60, (MSUBE, CENSO_SUBE)
g_mapam = figura(f'La participación subió en {n(MSUBE)} de los {n(len(M))} municipios entre 2019 y 2023',
                 'Cambio de la participación entre noviembre de 2019 y julio de 2023, en puntos, por municipio. Toca o pasa el ratón por un municipio para ver sus datos',
                 '<div data-pop="mun" style="position:relative">' + mapa_mun(CAM, HMAP, 'Mapa municipal del cambio de la participación entre 2019 y 2023')
                 + '<p style="margin:.8em 0 .2em;font-weight:700;font-size:.95em">Canarias</p>' + mapa_mun(CAMC, HMAPC, 'Canarias') + '</div>',
                 'Fuente: Ministerio del Interior, resultados por municipio (sin voto exterior). Cálculo propio. En los municipios pequeños, unos pocos votantes mueven mucho el porcentaje. Ceuta y Melilla no se dibujan.',
                 [(t, f'color-mix(in srgb, {c} {round(o * 100)}%, transparent)') for _, _, c, o, t in TRAMOS_M])
_gana = lambda k: {'EMPATE': 'empate'}.get(k, NOM.get(k, k)) if isinstance(k, str) else '–'
_MI = M.set_index('mun_code')
GN = sorted({_gana(g) for g in _MI['2023_07_gana']})
# Una cadena: «nombre|participación 2019 ×10|2023 ×10|índice del más votado en GN|provincia», separadas por «;», en el orden de ORD
D_M = ';'.join(f"{_MI.at[k, 'municipio']}|{round(_MI.at[k, 'p19'] * 10)}|{round(_MI.at[k, 'p23'] * 10)}|{GN.index(_gana(_MI.at[k, '2023_07_gana']))}|{k[:2]}"
               if k in _MI.index else '' for k in ORD)
assert ';' not in ''.join(_MI.municipio) and '|' not in ''.join(_MI.municipio)
D_PN = dict(zip(G.prov, G.nombre))
D_PROV = {r.prov: [r.nombre, round(r.p19, 1), round(r.p23, 1), r.g19, r.g23] for r in G.itertuples()}
CENSO23 = M['2023_07_censo'].sum()
MAS_VOT = SUBE_MED / 100 * CENSO23
assert 930000 < MAS_VOT < 970000, MAS_VOT
_t96 = h[[c for c in h.columns if c.startswith('1996_03_v') and c != '1996_03_votantes']].sum()
V96 = (_t96['1996_03_vPP'] - _t96['1996_03_vPSOE']) / _t96.sum() * 100
assert 1.1 < V96 < 1.5, V96   # oficial, sobre voto válido con exterior: 1,2; aquí, residentes y voto a candidaturas: el texto dice «poco más de un punto»
DIF23 = M['2023_07_vPP'].sum() - M['2023_07_vPSOE'].sum()
assert 250000 < DIF23 < MAS_VOT, DIF23
SEATS = {'1982': 202, '1996': 156, '2004': 164, '2011': 186}   # escaños del partido que llegó al Gobierno (Congreso de los Diputados)
_r = lambda nombre: G[G.nombre == nombre].iloc[0]
SEG, MEL, GIR, LUG, LLE, BCN = (_r(x) for x in ('Segovia', 'Melilla', 'Girona', 'Lugo', 'Lleida', 'Barcelona'))

cuerpo = f'''
<p data-tipo="contexto">El domingo 14 de marzo de 2004, tres días después de los atentados de Madrid, fue a votar el {p(R04['part'])} % de los electores residentes en España, {p(R04['dpart'])} puntos más que cuatro años antes. El PSOE, que llegaba desde la oposición, quedó primero y formó gobierno. Veintidós años después, la pregunta vuelve a estar sobre la mesa: cuánta gente irá a votar el 29N y si eso cambia algo.</p>
<h2>Lo que prevén las encuestas</h2>
<p data-tipo="dato">Diez encuestadoras han publicado en las tres últimas semanas una estimación de la participación en las elecciones generales del 29N. La mediana de la última de cada una está en el <strong>{p(MED)} %</strong>, {p(SUBE_MED)} puntos más que el {p(P23)} % de los residentes en España que votó en julio de 2023. Ocho de las diez prevén más participación que entonces. La horquilla es ancha: va del {p(MIN)} % de {esc(CASA_MIN)} al {p(MAX)} % de {esc(CASA_MAX)}. Es el último día en que se pueden publicar encuestas: desde mañana, martes 24, la ley lo prohíbe hasta el cierre de los colegios.</p>
{g_enc}
<p data-tipo="dato">Son pocos puntos, pero mucha gente. Con el censo de residentes de 2023, {n(CENSO23 / 1e6, 1)} millones de electores, cada punto de participación equivale a unos {n(round(CENSO23 / 100, -4))} votantes. Si se cumple la mediana, el 29N votarían unas {n(round(MAS_VOT, -4))} personas más que en julio de 2023. Es más que los {n(round(DIF23, -3))} votos de residentes que separaron al PP del PSOE en 2023, y la cifra no dice a quién votarían.</p>
<h2>Casi medio siglo de participación</h2>
<p data-tipo="dato">Desde 1977 ha habido 16 elecciones generales. La participación más alta fue la de octubre de 1982, con el {p(R82['part'])} %; la más baja, la de 1979, con el {p(R79['part'])} %. En once de las dieciséis pasó del 70 %.</p>
{g_hist}
<p data-tipo="patron">La participación de los residentes ha subido más de cinco puntos frente a la elección anterior en cuatro ocasiones: 1982 ({s1(R82['dpart'])}), 1993 ({s1(R93['dpart'])}), 2004 ({s1(R04['dpart'])}) y abril de 2019 ({s1(R19A['dpart'])}). Las cuatro veces quedó primero el PSOE. Las tres veces que subió poco, menos de dos puntos (1996, 2015 y 2023), el más votado fue el PP. Cuando bajó, quedaron primeros uno y otro: el PSOE en {", ".join(BAJA_PSOE[:-1])} y {BAJA_PSOE[-1]}; el PP en {", ".join(BAJA_PP[:-1])} y {BAJA_PP[-1]}, y la UCD en 1979.</p>
{g_cambio}
<h2>Cuando cambia el ciclo</h2>
<p data-tipo="patron">Cuatro elecciones generales han cambiado el partido del Gobierno, y no todas se parecen. Las dos que llevaron al PSOE al poder llegaron con grandes subidas de la participación: {s1(R82['dpart'])} puntos en 1982, cuando sustituyó a la UCD, y {s1(R04['dpart'])} en 2004. Las dos que llevaron al PP, no. En 1996, cuando José María Aznar sucedió a Felipe González, la participación ya era muy alta ({p(R96['part'])} %), pero solo subió {p(R96['dpart'])} puntos. En 2011, cuando Mariano Rajoy ganó con mayoría absoluta, bajó {p(-R11['dpart'])}.</p>
<p data-tipo="contexto">En octubre de 1982, el PSOE de Felipe González sacó {SEATS['1982']} diputados, la mayor mayoría absoluta de la democracia, con la participación más alta de la serie. En 2004, José Luis Rodríguez Zapatero llegó a {SEATS['2004']} escaños tres días después de los atentados del 11 de marzo. Los dos cambios hacia el PP fueron de otra manera: Aznar ganó en 1996 con {SEATS['1996']} escaños, por poco más de un punto de ventaja sobre el PSOE, y Rajoy llegó a {SEATS['2011']} en 2011, en plena crisis, con {p(R11['part'])} % de participación, {p(-R11['dpart'])} puntos menos que en 2008. Los dos cambios hacia la izquierda coincidieron con mucha más gente votando; los dos hacia la derecha, con una participación parecida o menor que la anterior.</p>
{g_ciclo}
<p data-tipo="contexto">El último cambio de Gobierno no salió de las urnas: en junio de 2018, la moción de censura llevó a Pedro Sánchez a la Moncloa. Las elecciones siguientes, en abril de 2019, fueron de las de gran subida, {s1(R19A['dpart'])} puntos, y el PSOE quedó primero, pero ya gobernaba.</p>
<h2>La participación y los bloques</h2>
<p data-tipo="contexto">La idea viene de lejos. «Históricamente, una participación alta suele beneficiar a la izquierda en unas elecciones generales», resumía <a href="https://maldita.es/malditodato/20210506/participacion-izquierda-derecha-elecciones-madrilenas/">Maldita.es</a> en 2021, con la advertencia de que en las autonómicas de Madrid había pasado lo contrario. El politólogo Pablo Simón lo matizaba en <a href="https://www.eldiario.es/politica/izquierda-gana-baja-abstencion_1_1621061.html">elDiario.es</a> en 2019: «Lo importante no es saber la participación total, sino quién sale a votar».</p>
<p data-tipo="patron">Si se mira el voto del PSOE junto al de los partidos a su izquierda (la familia del PCE, IU, Podemos y Sumar), la relación con la participación es de la misma dirección, pero lejos de ser exacta. En 10 de las 15 elecciones, los dos cambios fueron en el mismo sentido; en las otras cinco, en sentido contrario. Los casos que más pesan son 1982 y 2004, con subidas grandes de las dos cosas, y 2000 y 2011, con bajadas de las dos. En 2015, con la llegada de Podemos, ese voto subió {p(P['2015_12']['dizq'])} puntos con la participación casi igual.</p>
{g_disp}
<h2>El mapa de la participación</h2>
<p data-tipo="dato">En 2023, la participación fue más alta en buena parte de las dos Castillas y más baja en Cataluña, las islas, Ceuta y Melilla. Segovia ({p(SEG.p23)} %), Cuenca y Ávila encabezan la lista; Melilla ({p(MEL.p23)} %), Ceuta, Lleida y Girona la cierran, con Canarias y Baleares también por debajo del 65 %.</p>
{g_mapa23}
<p data-tipo="dato">Frente a noviembre de 2019, la participación subió en {SUBEN} de las 52 provincias. Las mayores subidas fueron gallegas: Lugo ({s1(LUG.d)} puntos), A Coruña, Soria y Ourense. Las mayores bajadas, en Cataluña: Girona ({s1(GIR.d)}), Lleida ({s1(LLE.d)}) y Barcelona ({s1(BCN.d)}), además de Melilla ({s1(MEL.d)}).</p>
{g_mapad}
<h2>Pueblos y ciudades</h2>
<p data-tipo="dato">Quién sale a votar también depende de dónde vive. En julio de 2023, en los {n(T[0]['n'])} municipios con menos de 1.000 electores votó el {p(T[0]['p23'])} %; en los de 20.000 a 100.000, el tramo que menos votó, el {p(T[3]['p23'])} %, y en las cinco ciudades de más de medio millón, el {p(T[-1]['p23'])} %. Y entre 2019 y 2023, cuanto más pequeño era el municipio, más subió la participación: {s1(T[0]['d'])} puntos en los pueblos de menos de 1.000 electores, {s1(T[1]['d'])} en los de 1.000 a 5.000 y {s1(T[3]['d'])} en los de 20.000 a 100.000. En las cinco grandes ciudades, bajó {p(-T[-1]['d'])} puntos.</p>
{g_tam}
<p data-tipo="dato">Lo que cambia con el tamaño es cuánta gente vota, más que a quién. En 2023, el PP sacó entre el {p(min(t['pp'] for t in T))} y el {p(max(t['pp'] for t in T))} % del voto en todos los tramos de tamaño, y el PSOE, entre el {p(min(t['psoe'] for t in T))} y el {p(max(t['psoe'] for t in T))} %.</p>
<p data-tipo="dato">Entre las 15 ciudades con más de 200.000 electores, la participación subió en {GR_SUBE} y bajó en {len(GR) - GR_SUBE}, aunque en Córdoba, Málaga y Zaragoza se movió menos de una décima. Más subió en Gijón ({s1(GIJ.d)} puntos) y en Palma ({s1(PAL.d)}); más bajó en Barcelona ({s1(BCNm.d)}), en línea con el resto de Cataluña. En Madrid, la mayor, se movió poco: del {p(MADm.p19)} al {p(MADm.p23)} %. València fue la que más votó de todas, con el {p(VLC.p23)} %.</p>
{g_ciud}
<p data-tipo="dato">En el mapa por municipios, la subida de 2023 ocupa casi todo el interior y Galicia, y la bajada se concentra en Cataluña. La participación subió en {n(MSUBE)} de los {n(len(M))} municipios, donde vive el {p(CENSO_SUBE)} % de los electores: subió en muchos más pueblos que electores, porque bajó en algunas de las ciudades más grandes.</p>
{g_mapam}
<h2>Lo que no dice</h2>
<p data-tipo="contexto">Es una relación entre elecciones, no una ley: son 16 casos y en cada uno pesaron otras cosas. En 1996 votó el {p(R96['part'])} %, una de las participaciones más altas, y ganó el PP. En 1993 y en abril de 2019, la participación subió más de cinco puntos y el voto conjunto al PSOE y a su izquierda apenas se movió ({s1(R93['dizq'])} y {s1(R19A['dizq'])} puntos). Y la previsión de {p(SUBE_MED)} puntos de subida para el 29N cae entre los dos grupos: más que las subidas pequeñas de 1996, 2015 y 2023, menos que las cuatro grandes.</p>
<p data-tipo="contexto">Dentro de una misma elección, la relación también aparece entre barrios: en 2023, las secciones que menos votaron dieron más voto al PSOE que al PP, y lo contrario las que más, como se cuenta en {L(BENEF, "la pieza sobre a quién beneficia la abstención")}. Pero eso no dice quién se quedará en casa el 29N. Las encuestas tampoco miden bien la participación: no todas dicen si cuentan el voto exterior, y la cifra que da Interior la noche electoral es la de los residentes en España, la que se compara aquí. Los avances de las 14.00 y las 18.00, en {L("a-que-hora-resultados-elecciones-generales-29n", "la guía de horarios de la noche electoral")}, y el mapa de quién no votó en 2023, en {L("abstencion-mapa-ganador-29n", "la abstención como si fuera un partido")}.</p>
'''

preguntas = [
    ('¿Qué participación prevén las encuestas para las elecciones generales del 29N?',
     f'La mediana de las 10 encuestadoras que la publican, en sus últimas entregas, es del {p(MED)} %, con una horquilla del {p(MIN)} al {p(MAX)} %. En 2023 votó el {p(P23)} % de los residentes en España.'),
    ('¿A quién beneficia una participación alta?',
     f'En las generales desde 1977, las cuatro veces que la participación subió más de cinco puntos quedó primero el PSOE, y las tres que subió poco, el PP. Es una relación entre elecciones, no una regla: en 1996, con un {p(R96["part"])} %, ganó el PP.'),
    ('¿Cuál ha sido la participación más alta en unas elecciones generales?',
     f'La de 1982: votó el {p(R82["part"])} % de los residentes en España. La más baja, la de 1979, con el {p(P["1979_03"]["part"])} %.'),
    ('¿Qué participación hubo en las elecciones generales de 2023?',
     f'El {p(P23)} % de los electores residentes en España, sin contar el voto exterior.'),
]
enlaces = (f'{L(BENEF, "A quién beneficia la abstención")} · {L("abstencion-mapa-ganador-29n", "El mapa de la abstención")} · '
           f'{L("sanchez-abascal-septima-revuelta-participacion-29n", "La participación desde 1977, provincia a provincia")} · <a href="{BASE}encuestas/">Encuestas elecciones generales 2026</a>')
foot = ('Datos: Ministerio del Interior, resultados por municipio de las elecciones generales de 1977 a 2023; participación estimada de las encuestas, '
        'recogida en Wikipedia. Cálculo: participacion_prevision_29n.py, en actualidad/src/resumenes.')

DATOS = {'H': [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()} for r in H],
         'E': [{'casa': r.casa, 'fin': r.fin, 'valor': r.valor} for r in E.itertuples()],
         'MED': round(MED, 3), 'MIN': MIN, 'MAX': MAX, 'SOBRE': SOBRE, 'P23': round(P23, 3), 'SUBE_MED': round(SUBE_MED, 3), 'CORR': round(CORR, 4), 'MISMO': MISMO, 'SUBEN': SUBEN, 'N_TRAMO': N_TRAMO,
         'PROV': [{'nombre': r.nombre, 'p23': round(r.p23, 3), 'd': round(r.d, 3)} for r in G.itertuples()]}
DATOS.update({'T': [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in t.items()} for t in T],
              'GR': [{'municipio': r.municipio, 'p19': round(r.p19, 3), 'p23': round(r.p23, 3), 'd': round(r.d, 3)} for r in GR.itertuples()],
              'MSUBE': MSUBE, 'NMUN': len(M), 'CENSO_SUBE': round(CENSO_SUBE, 3), 'CENSO23': int(CENSO23), 'MAS_VOT': round(MAS_VOT), 'DIF23': int(DIF23),
              'V96': round(V96, 3), 'GR_SUBE': GR_SUBE, 'SEATS': SEATS,
              'POP_PROV': D_PROV, 'POP_MUN': D_M, 'POP_GN': GN, 'POP_PN': D_PN})
POPUP = """
(()=>{const f1=v=>v.toFixed(1).replace('.',','),sg=v=>(v>0?'+':v<0?'\u2212':'')+f1(Math.abs(v));
const html={prov:k=>{const r=D.POP_PROV[k];return r&&`<b>${r[0]}</b><br>Votó en 2023: ${f1(r[2])} %<br>En noviembre de 2019: ${f1(r[1])} %<br>Cambio: ${sg(r[2]-r[1])} puntos<br>Más votado en 2023: ${r[4]}<br>En 2019: ${r[3]}`},
 mun:k=>{const r=MU[k];if(!r)return '';const a=r[1]/10,b=r[2]/10;return `<b>${r[0]}</b> (${D.POP_PN[r[4]]||''})<br>Votó en 2023: ${f1(b)} %<br>En noviembre de 2019: ${f1(a)} %<br>Cambio: ${sg(b-a)} puntos<br>Más votado en 2023: ${D.POP_GN[r[3]]}`}};
const MU=D.POP_MUN.split(';').map(x=>x?x.split('|').map((v,i)=>i&&i<4?+v:v):null);
document.querySelectorAll('[data-pop=mun] path').forEach((e,i)=>{e.dataset.k=i});
document.querySelectorAll('[data-pop]').forEach(box=>{box.style.position='relative';const t=document.createElement('div');t.className='tip';t.hidden=true;box.appendChild(t);
 const ver=ev=>{const e=ev.target.closest&&ev.target.closest('[data-k]'),h=e&&html[box.dataset.pop](e.dataset.k);if(!h){t.hidden=true;return}
  const r=box.getBoundingClientRect(),q=ev.touches?ev.touches[0]:ev;t.innerHTML=h;t.hidden=false;const x=q.clientX-r.left,y=q.clientY-r.top,w=t.offsetWidth;
  t.style.left=Math.min(Math.max(x,w/2),box.clientWidth-w/2)+'px';t.style.top=Math.max(y,t.offsetHeight*1.15)+'px'};
 let toque=0;box.addEventListener('mousemove',ver);box.addEventListener('click',ver);box.addEventListener('touchstart',ev=>{toque=Date.now();ver(ev)},{passive:true});box.addEventListener('mouseleave',()=>{if(Date.now()-toque>1000)t.hidden=true})});
document.addEventListener('touchstart',ev=>{if(!ev.target.closest('[data-pop]'))document.querySelectorAll('[data-pop]>.tip').forEach(t=>{t.hidden=true})},{passive:true})})();
"""
ESTILO = ('<style>\n:root{--baja:#1b8fa8}\n@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--baja:#2a9ab4}}\n:root[data-theme="dark"]{--baja:#2a9ab4}\n'
          '.tip{position:absolute;pointer-events:none;background:var(--fg);color:var(--bg);font-family:var(--ui);font-size:.9rem;line-height:1.3;'
          'padding:.35rem .55rem;border-radius:4px;white-space:nowrap;z-index:5;transform:translate(-50%,-115%)}\n[data-pop] [data-k]{cursor:pointer}\n</style>\n')
datos_js = ESTILO + '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';' + POPUP + '</script>\n'

TITULO = f'Participación en las elecciones generales del 29N: las encuestas prevén un {p(MED)} %, {p(SUBE_MED)} puntos más que en 2023'
DEK = ('Las cuatro veces que la participación subió más de cinco puntos desde 1977, el PSOE quedó primero; las tres que subió poco, el PP. '
       'Una relación entre elecciones, con excepciones, no una regla.')
pieza(SLUG, 'Participación', TITULO, DEK, '23 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(TITULO); print(DEK)
for r in H: print(r)
print(E[['casa', 'fin', 'valor']].to_string())
