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
import statistics

import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, barras, pieza

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
# Subidas pequeñas (hasta 1,4 puntos): las tres, el PP primero
SUBE_POCO = [r for r in H if r['dpart'] is not None and 0 < r['dpart'] <= 5]
assert [r['y'] for r in SUBE_POCO] == ['1996_03', '2015_12', '2023_07'] and all(r['gana'] == 'PP' for r in SUBE_POCO)
assert max(r['dpart'] for r in SUBE_POCO) < 1.5
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

ACC, GRIS = 'var(--acc)', 'var(--otros)'
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

R82, R93, R96, R04, R19A, R00, R11, R23 = (P[y] for y in ('1982_10', '1993_06', '1996_03', '2004_03', '2019_04', '2000_03', '2011_11', '2023_07'))
BENEF = 'a-quien-beneficia-abstencion-29n'
cuerpo = f'''
<p data-tipo="dato">Diez encuestadoras han publicado en las tres últimas semanas una estimación de la participación en las elecciones generales del 29N. La mediana de la última de cada una está en el <strong>{p(MED)} %</strong>, {p(SUBE_MED)} puntos más que el {p(P23)} % de los residentes en España que votó en julio de 2023. Ocho de las diez prevén más participación que entonces. La horquilla va del {p(MIN)} % de {esc(CASA_MIN)} al {p(MAX)} % de {esc(CASA_MAX)}. Es el último día en que se pueden publicar encuestas: desde mañana, martes 24, la ley lo prohíbe hasta el cierre de los colegios.</p>
{g_enc}
<h2>Lo que pasó otras veces</h2>
<p data-tipo="patron">En las 16 elecciones generales desde 1977, la participación de los residentes en España ha subido más de cinco puntos frente a la anterior en cuatro ocasiones: 1982 ({s1(R82['dpart'])}), 1993 ({s1(R93['dpart'])}), 2004 ({s1(R04['dpart'])}) y abril de 2019 ({s1(R19A['dpart'])}). Las cuatro veces quedó primero el PSOE. Las tres veces que subió poco, menos de un punto y medio (1996, 2015 y 2023), el más votado fue el PP. Cuando bajó, quedaron primeros uno y otro: el PSOE en {", ".join(BAJA_PSOE[:-1])} y {BAJA_PSOE[-1]}; el PP en {", ".join(BAJA_PP[:-1])} y {BAJA_PP[-1]}, y la UCD en 1979.</p>
{g_cambio}
<p data-tipo="patron">Las dos mayores subidas coincidieron con un cambio de gobierno a favor del PSOE. En 1982, la participación llegó al {p(R82['part'])} %, la más alta de la serie, y el voto al PSOE y a los partidos a su izquierda (la familia del PCE, IU, Podemos y Sumar) subió {p(R82['dizq'])} puntos. En 2004 subió {p(R04['dpart'])} puntos y ese voto, {p(R04['dizq'])}. Al revés, las dos mayorías absolutas del PP llegaron con menos participación: en 2000 bajó {p(-R00['dpart'])} puntos, y en 2011, {p(-R11['dpart'])}; el voto al PSOE y su izquierda cayó {p(-R00['dizq'])} y {p(-R11['dizq'])} puntos.</p>
{g_hist}
<h2>Lo que no dice</h2>
<p data-tipo="contexto">Es una relación entre elecciones, no una ley: son 16 casos y en cada uno pesaron otras cosas. Hay excepciones claras. En 1996 votó el {p(R96['part'])} %, una de las participaciones más altas, y ganó el PP. En 1993 y en abril de 2019, la participación subió más de cinco puntos y el voto conjunto al PSOE y a su izquierda apenas se movió ({s1(R93['dizq'])} y {s1(R19A['dizq'])} puntos): el PSOE quedó primero, pero la subida no se tradujo en más voto para ese bloque. Y la previsión de {p(SUBE_MED)} puntos de subida para el 29N cae entre los dos grupos: más que las subidas pequeñas de 1996, 2015 y 2023, menos que las cuatro grandes.</p>
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
         'MED': round(MED, 3), 'MIN': MIN, 'MAX': MAX, 'SOBRE': SOBRE, 'P23': round(P23, 3), 'SUBE_MED': round(SUBE_MED, 3)}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

TITULO = f'Participación en las elecciones generales del 29N: las encuestas prevén un {p(MED)} %, {p(SUBE_MED)} puntos más que en 2023'
DEK = ('Las cuatro veces que la participación subió más de cinco puntos desde 1977, el PSOE quedó primero; las tres que subió poco, el PP. '
       'Una relación entre elecciones, con excepciones, no una regla.')
pieza(SLUG, 'Participación', TITULO, DEK, '23 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(TITULO); print(DEK)
for r in H: print(r)
print(E[['casa', 'fin', 'valor']].to_string())
