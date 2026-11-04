"""«Quién no vota en Madrid» (4-11-2026): participación en las generales por renta, sección a sección y municipio a municipio.

Cifras: generales-2026/descargas/secciones.csv (2023, secciones INE 2023) y municipios*.csv (1977-2023). Participación =
votantes (candidaturas, blancos y nulos) entre censo de residentes en España, sin CERA, como en el resto del mapa: sale más
alta que la oficial con el voto exterior. Renta neta por unidad de consumo del Atlas de Distribución de Renta (INE, ADRH 2023),
la misma para todos los años: los grupos de municipios se forman con la renta de hoy.
Deciles: secciones ordenadas por renta y cortadas en diez grupos con el mismo censo electoral de 2023 (como los grupos de renta
de las páginas de municipio).
Uso, desde la raíz: python3 actualidad/src/resumenes/participacion_madrid.py
"""
import json

import numpy as np
import pandas as pd

from comun import BASE, COLOR, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
E = '2023_07'
EL = ['1977_06', '1979_03', '1982_10', '1986_06', '1989_10', '1993_06', '1996_03', '2000_03', '2004_03', '2008_03',
      '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
ANIO = {'2019_04': '2019-A', '2019_11': '2019-N'}
an = lambda e: ANIO.get(e, e[:4])
C_POBRE, C_RICO = '#c2581b', '#2f6f8f'   # no son colores de partido: la participación no es de nadie

s = pd.read_csv(RAIZ / 'generales-2026/descargas/secciones.csv', dtype={'tract_code': str, 'mun_code': str},
                usecols=['tract_code', 'mun_code', 'renta_uc', 'extranjeros', 'poblacion', 'edad_media', f'{E}_censo', f'{E}_votantes'])
s = s[s.mun_code.str[:2] == '28']
assert len(s) == 4479
SIN_RENTA = int(s.renta_uc.isna().sum())
assert SIN_RENTA == 6
s = s.dropna(subset=['renta_uc']).sort_values('renta_uc')
cum = s[f'{E}_censo'].cumsum() / s[f'{E}_censo'].sum()
s['dec'] = np.minimum((cum * 10).astype(int), 9) + 1
DEC = {}
for d, g in s.groupby('dec'):
    DEC[int(d)] = {'part': round(float(g[f'{E}_votantes'].sum() / g[f'{E}_censo'].sum() * 100), 2),
                   'rmin': int(g.renta_uc.min()), 'rmax': int(g.renta_uc.max()), 'secs': int(len(g)),
                   'ext': round(float((g.extranjeros * g.poblacion).sum() / g.poblacion.sum() * 100), 1),
                   'censo': int(g[f'{E}_censo'].sum())}
assert round(DEC[1]['part'], 1) == 60.9 and round(DEC[10]['part'], 1) == 83.1, DEC
assert all(DEC[i]['part'] < DEC[i + 1]['part'] for i in range(1, 10))   # sube en cada escalón
PART_CAM = round(float(s[f'{E}_votantes'].sum() / s[f'{E}_censo'].sum() * 100), 2)
CORR = round(float(s[['renta_uc', f'{E}_votantes', f'{E}_censo']].assign(pt=lambda d: d[f'{E}_votantes'] / d[f'{E}_censo'])[['renta_uc', 'pt']].corr().iloc[0, 1]), 2)
assert CORR == 0.75, CORR

# Municipios
h = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios_historico.csv', dtype={'mun_code': str})
m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str})
h, m = h[h.mun_code.str[:2] == '28'], m[m.mun_code.str[:2] == '28']
big = m[m.poblacion >= 50000].sort_values('renta_uc')
assert len(big) == 24
POBRES, RICOS = list(big.mun_code[:6]), list(big.mun_code[-6:])
NPOB, NRIC = list(big.municipio[:6]), list(big.municipio[-6:])
assert NPOB == ['Parla', 'Fuenlabrada', 'Móstoles', 'Arganda del Rey', 'Aranjuez', 'Leganés']
assert NRIC == ['Alcobendas', 'Tres Cantos', 'Majadahonda', 'Las Rozas de Madrid', 'Boadilla del Monte', 'Pozuelo de Alarcón']
SERIE = {}
for e in EL:
    d = h if e < '2004' else m
    f = lambda cs: float(d[d.mun_code.isin(cs)][f'{e}_votantes'].sum() / d[d.mun_code.isin(cs)][f'{e}_censo'].sum() * 100)
    SERIE[an(e)] = {'pobres': round(f(POBRES), 2), 'ricos': round(f(RICOS), 2)}
r1 = lambda v: round(v + 1e-9, 1)
BRECHA = {k: round(r1(v['ricos']) - r1(v['pobres']), 1) for k, v in SERIE.items()}   # de las cifras redondeadas que da el texto, para que cuadren a la vista
assert max(BRECHA, key=BRECHA.get) == '2023' and round(BRECHA['2023'], 1) == 7.5
assert max(v for k, v in BRECHA.items() if k != '2023') == BRECHA['2016']
assert BRECHA['2016'] > BRECHA['2015'] and BRECHA['2019-N'] > BRECHA['2019-A']
MAX_ANT = max(v for k, v in BRECHA.items() if k < '2016')
assert MAX_ANT == BRECHA['2000']
assert SERIE['2023']['ricos'] > SERIE['2019-N']['ricos'] and SERIE['2023']['pobres'] < SERIE['2019-N']['pobres']
BIG = {r.municipio: {'part': round(r[f'{E}_part'] * 100, 2), 'renta': int(r.renta_uc), 'pob': int(r.poblacion)} for _, r in big.iterrows()}
MAXB, MINB = max(BIG, key=lambda k: BIG[k]['part']), min(BIG, key=lambda k: BIG[k]['part'])
assert MAXB == 'Boadilla del Monte' and MINB == 'Parla'
RENTA_RATIO = BIG['Boadilla del Monte']['renta'] / BIG['Parla']['renta']
M1000 = m[m.poblacion >= 1000]
CORR_M = round(float(M1000[[f'{E}_part', 'renta_uc']].corr().iloc[0, 1]), 2)
assert len(M1000) == 135 and CORR_M == 0.69, (len(M1000), CORR_M)


# --- gráficos ---
def lineas(W=640, H=250, ml=40, mr=110, mt=12, mb=34, lo=65, hi=90):
    xs = list(SERIE)
    x = lambda i: ml + i * (W - ml - mr) / (len(xs) - 1)
    y = lambda v: mt + (hi - v) / (hi - lo) * (H - mt - mb)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Participación en los seis grandes municipios más ricos y en los seis más pobres de Madrid, 1977-2023">']
    for v in range(lo, hi + 1, 5):
        out.append(f'<line x1="{ml}" x2="{W - mr}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--grid)"/><text x="{ml - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{v} %</text>')
    for i, t in enumerate(xs):
        if t in ('1977', '1986', '1996', '2004', '2011', '2016', '2023'):
            out.append(f'<text x="{x(i):.1f}" y="{H - 10}" text-anchor="middle">{t}</text>')
    for k, col, et in (('ricos', C_RICO, 'Los 6 más ricos'), ('pobres', C_POBRE, 'Los 6 más pobres')):
        pts = ' '.join(f'{x(i):.1f},{y(SERIE[t][k]):.1f}' for i, t in enumerate(xs))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.6"/>')
        for i, t in enumerate(xs):
            out.append(f'<circle cx="{x(i):.1f}" cy="{y(SERIE[t][k]):.1f}" r="3" fill="{col}"><title>{et}, {t}: {p(SERIE[t][k])} %</title></circle>')
        out.append(f'<text x="{x(len(xs) - 1) + 8:.1f}" y="{y(SERIE["2023"][k]) + 4:.1f}" class="lab">{p(SERIE["2023"][k])} %</text>')
    out.append('</svg>')
    return ''.join(out)


SIN_CERA = 'Participación: votantes entre censo de residentes en España, sin voto exterior (CERA).'
g_dec = figura('Cuanta más renta, más participación, escalón a escalón',
               'Participación en las generales de 2023 en las secciones censales de la Comunidad de Madrid, por decil de renta (diez grupos con el mismo censo)',
               barras([(f'{i}.º ({n(DEC[i]["rmin"] / 1000)}-{n(DEC[i]["rmax"] / 1000)} mil €)' if i not in (1, 10) else
                        ('1.º, el más pobre' if i == 1 else '10.º, el más rico'), DEC[i]['part'],
                        C_POBRE if i <= 5 else C_RICO, f'{p(DEC[i]["part"])} %') for i in range(1, 11)], 100,
                      'Participación por decil de renta', ml=190, alto=26),
               'Fuente: Ministerio del Interior (resultados por mesa) e INE, Atlas de Distribución de Renta de los Hogares 2023 (renta neta por unidad de consumo). ' + SIN_CERA, None,
               (['Decil', 'Renta por unidad de consumo', 'Secciones', 'Participación', 'Población extranjera'],
                [[f'{i}.º', f'{n(DEC[i]["rmin"])}-{n(DEC[i]["rmax"])} €', str(DEC[i]['secs']), f'{p(DEC[i]["part"])} %', f'{p(DEC[i]["ext"])} %'] for i in range(1, 11)]))
g_serie = figura('La brecha de 2023 es la mayor desde 1977',
                 'Participación en las generales en los seis municipios de más de 50.000 habitantes con más renta y en los seis con menos',
                 lineas(), 'Fuente: Ministerio del Interior; renta, INE (ADRH 2023), la misma para todos los años. Más ricos: ' + ', '.join(NRIC) +
                 ' (Tres Cantos, desde 1993: se segregó de Colmenar Viejo en 1991). Más pobres: ' + ', '.join(NPOB) + '. ' + SIN_CERA,
                 [('Los 6 más ricos', C_RICO), ('Los 6 más pobres', C_POBRE)],
                 (['Elección', 'Más ricos', 'Más pobres', 'Diferencia (puntos)'], [[t, p(v['ricos']), p(v['pobres']), p(BRECHA[t])] for t, v in SERIE.items()]))
ORDB = sorted(BIG, key=lambda k: -BIG[k]['part'])
g_big = figura('Los 24 grandes municipios, de más a menos participación', 'Participación en las generales de 2023 y renta neta por unidad de consumo',
               barras([(k.replace(' de Madrid', '').replace('San Sebastián de los Reyes', 'S. S. de los Reyes'), BIG[k]['part'],
                        C_RICO if k in NRIC else (C_POBRE if k in NPOB else 'var(--otros)'), f'{p(BIG[k]["part"])} % · {n(BIG[k]["renta"])} €') for k in ORDB],
                      100, 'Participación en los 24 grandes municipios', ml=170, alto=22),
               'Fuente: Ministerio del Interior e INE (ADRH 2023). En azul, los seis con más renta; en naranja, los seis con menos. ' + SIN_CERA, None,
               (['Municipio', 'Participación', 'Renta por u. c.', 'Habitantes'], [[k, p(BIG[k]['part']), n(BIG[k]['renta']), n(BIG[k]['pob'])] for k in ORDB]))

SALTO = 'https://www.elsaltodiario.com/elecciones-autonomicas/el-circulo-vicioso-de-la-abstencion-andalucia'
MU = lambda path, t: f'<a href="{BASE}municipio/madrid/{path}/">{t}</a>'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
DATOS = {'DEC': DEC, 'SERIE': SERIE, 'BRECHA': BRECHA, 'BIG': BIG, 'PART_CAM': PART_CAM, 'CORR': CORR, 'CORR_M': CORR_M, 'SIN_RENTA': SIN_RENTA}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
B, P = BIG['Boadilla del Monte'], BIG['Parla']
d1, d10 = DEC[1], DEC[10]

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="dato">En las generales de julio de 2023, en la décima parte más pobre de la Comunidad de Madrid votó el {p(d1["part"])} % del censo. En la décima parte más rica, el {p(d10["part"])} %. Son {p(r1(d10["part"]) - r1(d1["part"]))} puntos de diferencia entre secciones censales de una misma región. La participación sube con la renta en cada uno de los diez escalones, sin excepción.</p>
{g_dec}
<p data-tipo="dato">Entre los grandes municipios pasa lo mismo. {MU("boadilla-del-monte", "Boadilla del Monte")}, con una renta por unidad de consumo de {n(B["renta"])} euros, fue el que más votó: el {p(B["part"])} %. {MU("parla", "Parla")}, con {n(P["renta"])} euros, menos de la mitad, el que menos: el {p(P["part"])} %. En los {len(M1000)} municipios de más de 1.000 habitantes, la correlación entre renta y participación es de {n(CORR_M, 2)}; entre las secciones, de {n(CORR, 2)}. Es una relación fuerte, pero es una correlación: no dice que la renta, por sí sola, haga votar más.</p>
{g_big}

<h2>Una brecha que se ha ensanchado</h2>
<p data-tipo="dato">La diferencia no es nueva, pero nunca había sido tan grande. En los seis grandes municipios con más renta ({", ".join(NRIC[:-1])} y {NRIC[-1]}) votó en 2023 el {p(SERIE["2023"]["ricos"])} %; en los seis con menos ({", ".join(NPOB[:-1])} y {NPOB[-1]}), el {p(SERIE["2023"]["pobres"])} %. Son {p(BRECHA["2023"])} puntos, la mayor distancia en las 16 generales desde 1977. Hasta 2015, su máximo eran los {p(MAX_ANT)} puntos de 2000. Las dos repeticiones electorales la ensancharon: {p(BRECHA["2016"])} puntos en 2016 y {p(BRECHA["2019-N"])} en noviembre de 2019, frente a {p(BRECHA["2015"])} y {p(BRECHA["2019-A"])} en las elecciones que se repetían.</p>
{g_serie}
<p data-tipo="patron">Cuando la participación cae, cae más en los municipios con menos renta. En la repetición de noviembre de 2019 bajó {p(r1(SERIE["2019-A"]["ricos"]) - r1(SERIE["2019-N"]["ricos"]))} puntos en los seis más ricos y {p(r1(SERIE["2019-A"]["pobres"]) - r1(SERIE["2019-N"]["pobres"]))} en los seis más pobres. En 2023, los ricos subieron un poco, al {p(SERIE["2023"]["ricos"])} %, y los pobres siguieron bajando, al {p(SERIE["2023"]["pobres"])} %.</p>
<p data-tipo="contexto">La población extranjera no explica la diferencia por sí misma. En la décima parte más pobre, el {p(d1["ext"])} % de los vecinos es extranjero, frente al {p(d10["ext"])} % en la más rica. Pero en las generales solo votan los españoles, y el censo con el que se calcula la participación solo los incluye a ellos: un vecino extranjero no cuenta como abstención.</p>
<p data-tipo="hipotesis">Hay varias explicaciones posibles, y los datos agregados no permiten elegir entre ellas: la que relaciona votar con el nivel de estudios, la del desencanto de quienes sienten que la política no cambia su vida y la de la movilización, porque los partidos hacen más campaña donde la participación es alta. Los datos por sección describen dónde se vota menos, no por qué.</p>
<blockquote class="cita"><p>«Existe el tipo de votante que no se siente capacitado o cree que no entiende el lenguaje de la política institucional».</p><footer>Jean-Baptiste Harguindéguy, politólogo de la Universidad Pablo de Olavide, sobre la abstención en los barrios con menos renta de las ciudades andaluzas, en <a href="{SALTO}">El Salto</a> (2019)</footer></blockquote>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">La participación de esta pieza es la de los residentes en España, sin el voto exterior, que vota muy poco; por eso sale más alta que la oficial. La renta es la del Atlas del INE de 2023 y se aplica a todas las elecciones: los municipios más ricos y más pobres de hoy no son necesariamente los de 1977. Las secciones son las de 2023. Y una sección o un municipio no es una persona: que en las secciones pobres se vote menos no dice que cada vecino con poca renta se abstenga.</p>'''

preguntas = [
    ('¿Qué municipio de Madrid vota más?', f'Entre los de más de 50.000 habitantes, Boadilla del Monte: el {p(B["part"])} % en las generales de 2023, sin contar el voto exterior. El que menos, Parla, con el {p(P["part"])} %.'),
    ('¿Votan menos los barrios con menos renta?', f'En la Comunidad de Madrid, sí: en 2023 votó el {p(d1["part"])} % en la décima parte de secciones con menos renta y el {p(d10["part"])} % en la décima parte con más. Es una correlación, no una causa demostrada.'),
    ('¿Cuenta como abstención un vecino extranjero?', 'No. En las generales solo votan los españoles, y la participación se calcula sobre el censo electoral, que solo los incluye a ellos.'),
]
enlaces = (f'<a href="{BASE}elecciones/participacion-electoral-por-barrio/">Participación electoral por barrio en toda España</a> · '
           f'<a href="{BASE}municipio/madrid/">Los municipios de Madrid</a> · <a href="{BASE}encuestas/madrid/">Encuesta de Madrid</a> · '
           f'{L("cinturon-rojo-madrid-29n", "El cinturón rojo de Madrid")} · {L("madrid-barrio-a-barrio-29n", "Madrid capital, barrio a barrio")}')
foot = ('Datos: Ministerio del Interior, generales de 1977 a 2023 por mesa y por municipio; INE, Atlas de Distribución de Renta de los Hogares 2023. '
        'Cálculo: actualidad/src/resumenes/participacion_madrid.py.')

pieza('participacion-renta-municipios-madrid-29n', 'Quién no vota en Madrid',
      f'En la Madrid más pobre votó el {n(d1["part"])} %; en la más rica, el {n(d10["part"])} %: entre los grandes municipios, la brecha es la mayor desde 1977',
      f'La participación sube con la renta en cada escalón. Boadilla del Monte votó un {p(B["part"])} % y Parla un {p(P["part"])} %. Entre los seis grandes municipios '
      f'más ricos y los seis más pobres, la diferencia es hoy de {p(BRECHA["2023"])} puntos, la mayor desde 1977.',
      '4 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
