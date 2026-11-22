"""«Getafe-Atlético en las urnas» (pieza de domingo, 22-11-2026, día del Getafe-Atlético en el Coliseum).

Cifras: secciones (generales-2026/descargas/secciones.csv, con la renta por unidad de consumo del INE) de las generales de
noviembre de 2019 y julio de 2023, con el más votado de cada sección lista a lista (columna _gana); barrios de
data/barrios/secciones_barrio.csv (OpenStreetMap); municipio de generales-2026/descargas/municipios.csv (votos de cada
partido, 2011-2023). El Coliseum está en la sección 2806502019 (Getafe Norte) y el Metropolitano en la 2807920067 (Rosas,
San Blas-Canillejas), por sus coordenadas sobre los polígonos de data/barrios/geo. Sumar no se compara con 2019. Quintiles
de renta dentro de la ciudad, sin regresión.
Uso, desde la raíz: python3 actualidad/src/resumenes/getafe_atletico.py
"""
import json

import pandas as pd

from comun import BASE, COLOR, RAIZ, barras, figura, n, pieza

A = BASE + 'actualidad/'
GET, MAD = '28065', '28079'
E, E0 = '2023_07', '2019_11'
P = ['PP', 'PSOE', 'SUMAR', 'VOX']
ETQ = {'PP': 'PP', 'PSOE': 'PSOE', 'SUMAR': 'Sumar', 'VOX': 'Vox', 'EMPATE': 'Empate a votos', 'CS': 'Ciudadanos'}
p = lambda v: n(v, 1)
ELEC = [('2011_11', '2011'), ('2015_12', '2015'), ('2016_06', '2016'), ('2019_04', 'abr. 2019'), ('2019_11', 'nov. 2019'), ('2023_07', '2023')]

# --- El municipio, elección a elección ---
mu = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str})
r = mu[mu.mun_code == GET].iloc[0]
H = {e: {'PP': r[f'{e}_PP'] * 100, 'PSOE': r[f'{e}_PSOE'] * 100, 'vPP': int(r[f'{e}_vPP']), 'vPSOE': int(r[f'{e}_vPSOE']),
         'gana': r[f'{e}_gana'], 'part': r[f'{e}_part'] * 100} for e, _ in ELEC}
assert [H[e]['gana'] for e, _ in ELEC] == ['PP', 'PP', 'PP', 'PSOE', 'PSOE', 'PSOE']
assert round(H[E]['PP'], 1) == 32.2 and round(H[E]['PSOE'], 1) == 34.4 and round(H[E0]['PP'], 1) == 18.2 and round(H[E0]['PSOE'], 1) == 32.1
assert round(H['2011_11']['PP'], 1) == 42.4
DIFV = H[E]['vPSOE'] - H[E]['vPP']
assert (H[E]['vPP'], H[E]['vPSOE'], DIFV) == (32040, 34222, 2182)
POB = int(r['poblacion'])

# --- Secciones ---
d = pd.read_csv(RAIZ / 'generales-2026/descargas/secciones.csv', dtype={'tract_code': str, 'mun_code': str})
d = d[d.mun_code.isin([GET, MAD])].dropna(subset=[f'{E}_PP']).copy()
bar = pd.read_csv(RAIZ / 'data/barrios/secciones_barrio.csv', dtype=str)[['tract_code', 'barrio', 'distrito']]
d = d.merge(bar, on='tract_code', how='left')
g = d[d.mun_code == GET].copy()
G23 = {k: int(c) for k, c in g[f'{E}_gana'].value_counts().items()}
G19 = {k: int(c) for k, c in g[f'{E0}_gana'].value_counts().items()}
assert len(g) == 122 and G23 == {'PSOE': 74, 'PP': 45, 'SUMAR': 2, 'EMPATE': 1} and G19 == {'PSOE': 112, 'PP': 7, 'SUMAR': 2, 'VOX': 1}
SINB = int(g.barrio.isna().sum())
assert SINB == 16
COLI, METRO = '2806502019', '2807920067'
assert g.loc[g.tract_code == COLI, 'barrio'].item() == 'Getafe Norte'
assert d.loc[d.tract_code == METRO, 'barrio'].item() == 'Rosas'


def cuota(s, k, e=E):
    return (s[f'{e}_{k}'] * s[f'{e}_votantes']).sum() / s[f'{e}_votantes'].sum() * 100


def part(s, e=E):
    return s[f'{e}_votantes'].sum() / s[f'{e}_censo'].sum() * 100


def resumen(s):
    return {**{k: cuota(s, k) for k in P}, 'part': part(s), 'renta': float(s.renta_uc.median()), 'n': len(s),
            'gana': {k: int(c) for k, c in s[f'{E}_gana'].value_counts().items()},
            'gana0': {k: int(c) for k, c in s[f'{E0}_gana'].value_counts().items()},
            'PP0': cuota(s, 'PP', E0), 'PSOE0': cuota(s, 'PSOE', E0), 'VOX0': cuota(s, 'VOX', E0)}


CIU = resumen(g)
assert round(CIU['part'], 1) == 75.4 and CIU['renta'] == 21799
B = {k: resumen(s) for k, s in g.groupby('barrio')}
GN, SIII, BER, CEN, JC, LM = B['Getafe Norte'], B['Sector III'], B['El Bercial'], B['Centro'], B['Juan de la Cierva'], B['Las Margaritas']
assert GN['n'] == 9 and GN['gana'] == {'PSOE': 7, 'PP': 2} and GN['gana0'] == {'PSOE': 9}
assert round(GN['PSOE'], 1) == 36.0 and round(GN['PP'], 1) == 31.2 and round(GN['PP0'], 1) == 16.7 and GN['renta'] == 24816
assert SIII['n'] == 20 and SIII['gana'] == {'PP': 13, 'PSOE': 6, 'SUMAR': 1} and round(SIII['PP'], 1) == 33.9 and round(SIII['part'], 1) == 81.0 and SIII['renta'] == 28547
assert BER['gana'] == {'PP': 5, 'PSOE': 4} and BER['gana0'] == {'PSOE': 9} and round(BER['PP'], 1) == 36.1 and round(BER['PP0'], 1) == 17.8
assert CEN['n'] == 19 and CEN['gana'] == {'PP': 13, 'PSOE': 6} and round(CEN['PP'], 1) == 36.8
assert JC['n'] == 21 and JC['gana'] == {'PSOE': 19, 'PP': 2} and round(JC['PSOE'], 1) == 43.1 and round(JC['part'], 1) == 68.1 and JC['renta'] == 17824
assert round(LM['part'], 1) == 68.8 and LM['renta'] == 15133.5
MAXPP = max(B, key=lambda k: B[k]['PP'])
assert MAXPP == 'Centro'

# Quintiles de renta en Getafe
q = g.dropna(subset=['renta_uc']).copy()
q['q'] = pd.qcut(q.renta_uc.rank(method='first'), 5, labels=False)
Q = {j: resumen(s) for j, s in q.groupby('q')}
assert Q[0]['gana'] == {'PSOE': 25} and round(Q[0]['PSOE'], 1) == 43.5 and round(Q[0]['PP'], 1) == 26.8
assert Q[4]['gana'] == {'PP': 21, 'PSOE': 4} and round(Q[4]['PP'], 1) == 36.2 and round(Q[4]['PSOE'], 1) == 29.8
assert round(Q[0]['part'], 1) == 66.0 and round(Q[4]['part'], 1) == 81.7

# Madrid: el Metropolitano
m = d[d.mun_code == MAD]
RO = resumen(m[m.barrio == 'Rosas'])
MADC = resumen(m)
assert RO['n'] == 17 and RO['gana'] == {'PP': 16, 'PSOE': 1} and round(RO['PP'], 1) == 39.3 and round(RO['PSOE'], 1) == 29.7
assert round(MADC['PP'], 1) == 41.8 and round(MADC['PSOE'], 1) == 27.4

# Modelo de encuestas para la provincia de Madrid (mapaelectoral.es/encuestas/madrid/, actualización del 22-11-2026)
MODELO = {'PP': 16, 'PSOE': 10, 'VOX': 8, 'SUMAR': 3, 'PODEMOS': 1, 'pp_primero': 98, 'escanos': 38}
assert sum(v for k, v in MODELO.items() if k in ('PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS')) == MODELO['escanos']

# --- Gráficos ---
FUENTE_S = (f'Fuente: Ministerio del Interior (generales por sección censal) e INE (renta por unidad de consumo). '
            f'Barrios según OpenStreetMap; {SINB} secciones sin barrio asignado solo cuentan en el total de la ciudad.')
g_hist = figura('En Getafe, el PP ganó en 2011, 2015 y 2016; desde 2019 gana el PSOE',
                '% de voto al PP y al PSOE en Getafe en cada elección general desde 2011',
                barras([(f'{t} · {k}', H[e][k], COLOR[k] if H[e]['gana'] == k else f'color-mix(in srgb, {COLOR[k]} 45%, var(--bg))', f'{p(H[e][k])} %')
                        for e, t in ELEC for k in ('PP', 'PSOE')],
                       50, 'Voto al PP y al PSOE en Getafe, 2011-2023', W=420, ml=120),
                f'Fuente: Ministerio del Interior, resultados por municipio. En color fuerte, el más votado de los dos. En 2015, Podemos e IU sumados superaron al PP, pero se presentaron por separado.',
                [('PP', COLOR['PP']), ('PSOE', COLOR['PSOE'])],
                (['Elección', 'PP (%)', 'PSOE (%)', 'Votos PP', 'Votos PSOE', 'Participación (%)'],
                 [[t, p(H[e]['PP']), p(H[e]['PSOE']), n(H[e]['vPP']), n(H[e]['vPSOE']), p(H[e]['part'])] for e, t in ELEC]))

orden = sorted(B, key=lambda k: -(B[k]['PP'] - B[k]['PSOE']))
_d = lambda k: B[k]['PP'] - B[k]['PSOE']
g_bar = figura('El Coliseum está en Getafe Norte, donde el PSOE ganó 7 de las 9 secciones',
               'Ventaja del PP o del PSOE, en puntos, en cada barrio de Getafe en las elecciones generales de 2023. El barrio del estadio, en color fuerte',
               barras([(k, abs(_d(k)), ('var(--pp)' if _d(k) > 0 else 'var(--psoe)') if k == 'Getafe Norte' else
                        f'color-mix(in srgb, {"var(--pp)" if _d(k) > 0 else "var(--psoe)"} 55%, var(--bg))',
                        f'{"PP" if _d(k) > 0 else "PSOE"} +{p(abs(_d(k)))}') for k in orden],
                      16, 'Ventaja del PP o del PSOE por barrio de Getafe', W=420, ml=130, separar=True),
               FUENTE_S, [('Por delante, el PP', 'var(--pp)'), ('Por delante, el PSOE', 'var(--psoe)')],
               (['Barrio', 'PP', 'PSOE', 'Sumar', 'Vox', 'Participación', 'Renta mediana (€)', 'Secciones', 'Ganadas por el PP en 2023', 'Ganadas por el PSOE en 2023', 'Ganadas por el PSOE en 2019'],
                [[k, p(B[k]['PP']), p(B[k]['PSOE']), p(B[k]['SUMAR']), p(B[k]['VOX']), p(B[k]['part']), n(B[k]['renta']), str(B[k]['n']),
                  str(B[k]['gana'].get('PP', 0)), str(B[k]['gana'].get('PSOE', 0)), str(B[k]['gana0'].get('PSOE', 0))] for k in orden]))

g_sec = figura(f'El PSOE pasó de {G19["PSOE"]} a {G23["PSOE"]} secciones; el PP, de {G19["PP"]} a {G23["PP"]}',
               f'Secciones censales de Getafe según el partido más votado, en noviembre de 2019 y en julio de 2023 (de {len(g)})',
               barras([('PSOE · 2019', G19['PSOE'], f'color-mix(in srgb, {COLOR["PSOE"]} 45%, var(--bg))', str(G19['PSOE'])),
                       ('PSOE · 2023', G23['PSOE'], COLOR['PSOE'], str(G23['PSOE'])),
                       ('PP · 2019', G19['PP'], f'color-mix(in srgb, {COLOR["PP"]} 45%, var(--bg))', str(G19['PP'])),
                       ('PP · 2023', G23['PP'], COLOR['PP'], str(G23['PP']))],
                      122, 'Secciones ganadas por el PSOE y el PP en Getafe', W=420, ml=110),
               f'Fuente: Ministerio del Interior, más votado de cada sección lista a lista. El resto: en 2019, Unidas Podemos en {G19["SUMAR"]} y Vox en {G19["VOX"]}; en 2023, Sumar en {G23["SUMAR"]} y un empate a votos.',
               [('2019', f'color-mix(in srgb, {COLOR["PSOE"]} 45%, var(--bg))'), ('2023', COLOR['PSOE'])])


def quint(W=640, H_=250, ml=40, mr=105, mt=12, mb=34):
    x = lambda j: ml + j * (W - ml - mr) / 4
    y = lambda val: mt + (50 - val) / 50 * (H_ - mt - mb)
    out = [f'<svg viewBox="0 0 {W} {H_}" role="img" aria-label="Voto por quintil de renta en Getafe">']
    for val in (0, 10, 20, 30, 40, 50):
        out.append(f'<line x1="{ml}" x2="{W - mr}" y1="{y(val):.1f}" y2="{y(val):.1f}" stroke="var(--grid)"/><text x="{ml - 6}" y="{y(val) + 4:.1f}" text-anchor="end">{val} %</text>')
    for j, t in enumerate(['Más pobre', '2.º', '3.º', '4.º', 'Más rico']):
        out.append(f'<text x="{x(j):.1f}" y="{H_ - 10}" text-anchor="middle">{t}</text>')
    ys, prev = {}, None
    for k in sorted(P, key=lambda k: -Q[4][k]):
        ys[k] = y(Q[4][k]) if prev is None else max(y(Q[4][k]), prev + 15)
        prev = ys[k]
    for k in P:
        col = COLOR[ETQ[k]]
        pts = ' '.join(f'{x(j):.1f},{y(Q[j][k]):.1f}' for j in range(5))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3"/>')
        for j in range(5):
            out.append(f'<circle cx="{x(j):.1f}" cy="{y(Q[j][k]):.1f}" r="4" fill="{col}"><title>{ETQ[k]}, quintil {j + 1}: {p(Q[j][k])} %</title></circle>')
        out.append(f'<text x="{x(4) + 8:.1f}" y="{ys[k] + 4:.1f}" class="lab">{ETQ[k]} {p(Q[4][k])}</text>')
    out.append('</svg>')
    return ''.join(out)


g_q = figura('En Getafe, el PSOE gana todas las secciones más pobres y el PP, casi todas las más ricas',
             '% de voto en las elecciones generales de 2023 según la renta de la sección', quint(),
             'Fuente: Ministerio del Interior (generales de 2023, por sección censal) e INE (renta por unidad de consumo). Cada quintil reúne una quinta parte de las secciones de Getafe, de la más pobre a la más rica.',
             [(ETQ[k], COLOR[ETQ[k]]) for k in P],
             (['Quintil', 'Renta mediana (€)', 'PP', 'PSOE', 'Sumar', 'Vox', 'Participación', 'Secciones', 'Ganadas por el PP', 'Ganadas por el PSOE'],
              [[f'{j + 1}.º', n(Q[j]['renta']), p(Q[j]['PP']), p(Q[j]['PSOE']), p(Q[j]['SUMAR']), p(Q[j]['VOX']), p(Q[j]['part']), str(Q[j]['n']),
                str(Q[j]['gana'].get('PP', 0)), str(Q[j]['gana'].get('PSOE', 0))] for j in range(5)]))

L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
CG = f'<a href="{BASE}municipio/madrid/getafe/">Getafe</a>'
DEBATE = 'https://www.eldebate.com/deportes/futbol/la-liga/20261121/getafe-atletico-madrid-horario-donde-ver-tv-jornada-13-laliga_483606.html'
CIERRE = 'https://www.infobae.com/espana/2023/07/21/el-extasis-se-apodera-del-psoe-en-el-cierre-de-campana-del-23-j-nos-caimos-nos-levantamos-y-pedaleamos-a-contrarreloj/'

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Esta noche, a las 21.00, el Getafe recibe al Atlético de Madrid en el Coliseum, en la jornada 13 de LaLiga, según <a href="{DEBATE}">El Debate</a>. El estadio está en Getafe Norte, uno de los barrios de {CG}, una ciudad del sur de Madrid de {n(POB)} habitantes, según el padrón municipal de 2023 (INE). A siete días de las elecciones generales del 29N, Getafe es uno de los cuatro municipios grandes de la Comunidad de Madrid donde el PSOE fue el más votado en 2023, con Fuenlabrada, Parla y Leganés, como contamos en {L('cinturon-rojo-madrid-29n', 'lo que queda del cinturón rojo')}.</p>
<p data-tipo="dato">En las generales de julio de 2023, el PSOE sacó en Getafe el {p(H[E]['PSOE'])} % y el PP, el {p(H[E]['PP'])} %: {n(H[E]['vPSOE'])} votos frente a {n(H[E]['vPP'])}, una diferencia de <strong>{n(DIFV)} votos</strong>. Cuatro años antes, en noviembre de 2019, el PP se había quedado en el {p(H[E0]['PP'])} %, con Ciudadanos todavía en la papeleta. El PSOE apenas cambió: del {p(H[E0]['PSOE'])} % al {p(H[E]['PSOE'])} %.</p>
<p data-tipo="dato">No siempre ganó el PSOE. En 2011, el PP sacó en Getafe el {p(H['2011_11']['PP'])} %, y volvió a ser el más votado en 2015, cuando Podemos e Izquierda Unida se presentaron por separado, y en 2016. Desde abril de 2019, el primero es el PSOE.</p>
{g_hist}
<h2>De 112 secciones a 74</h2>
<p data-tipo="dato">Donde más se nota el cambio es sección a sección. En noviembre de 2019, el PSOE fue el más votado en {G19['PSOE']} de las {len(g)} secciones censales de Getafe, y el PP, en {G19['PP']}. En 2023, el PSOE ganó en {G23['PSOE']} y el PP, en {G23['PP']}; Sumar fue primero en {G23['SUMAR']} y en otra hubo empate a votos.</p>
{g_sec}
<p data-tipo="contexto">Getafe fue el lugar que eligió el PSOE para cerrar la campaña de 2023. Pedro Sánchez lo hizo en el polideportivo de La Alhóndiga, el 21 de julio, ante unas 4.500 personas, según <a href="{CIERRE}">Infobae</a>:</p>
<blockquote class="cita"><p>«Vamos a ganar las elecciones y las vamos a ganar rotundamente»</p><footer>Pedro Sánchez, en el cierre de campaña del PSOE en Getafe, el 21 de julio de 2023, según <a href="{CIERRE}">Infobae</a>.</footer></blockquote>
<p data-tipo="dato">En las {B['La Alhóndiga']['n']} secciones del barrio de La Alhóndiga, el PSOE ganó en {B['La Alhóndiga']['gana']['PSOE']}, con el {p(B['La Alhóndiga']['PSOE'])} %.</p>

<h2>El barrio del Coliseum</h2>
<p data-tipo="dato">En Getafe Norte, el barrio del estadio, el PSOE ganó en {GN['gana']['PSOE']} de las {GN['n']} secciones en 2023, con el {p(GN['PSOE'])} % frente al {p(GN['PP'])} % del PP. En 2019 había ganado las {GN['gana0']['PSOE']}, y el PP se había quedado en el {p(GN['PP0'])} %. La renta mediana del barrio es de {n(GN['renta'])} € por unidad de consumo, por encima de la de la ciudad ({n(CIU['renta'])} €).</p>
<p data-tipo="dato">Los barrios donde ganó el PP son los de más renta y el centro. En el Sector III, el PP ganó {SIII['gana']['PP']} de las {SIII['n']} secciones, con el {p(SIII['PP'])} %; votó el {p(SIII['part'])} % y la renta mediana es de {n(SIII['renta'])} €. En El Bercial, el PP pasó de no ganar ninguna sección a ganar {BER['gana']['PP']} de {BER['n']}, y del {p(BER['PP0'])} % al {p(BER['PP'])} %. En el Centro, donde más votó al PP, ganó {CEN['gana']['PP']} de {CEN['n']} con el {p(CEN['PP'])} %. Al otro lado, en Juan de la Cierva, el PSOE ganó {JC['gana']['PSOE']} de las {JC['n']} secciones con el {p(JC['PSOE'])} %, y votó el {p(JC['part'])} %.</p>
{g_bar}

<h2>La renta, sección a sección</h2>
<p data-tipo="patron">Si se ordenan las secciones de Getafe por renta y se parten en cinco grupos iguales, el PSOE gana en las {Q[0]['gana']['PSOE']} de la quinta parte más pobre, con el {p(Q[0]['PSOE'])} %, frente al {p(Q[0]['PP'])} % del PP. En la quinta parte más rica, el PP gana en {Q[4]['gana']['PP']} de {Q[4]['n']}, con el {p(Q[4]['PP'])} %, frente al {p(Q[4]['PSOE'])} % del PSOE. La participación va del {p(Q[0]['part'])} % al {p(Q[4]['part'])} %.</p>
{g_q}
<p data-tipo="patron">Es el mismo patrón que en Sevilla, donde se jugó ayer el derbi, pero con distancias más cortas: en la quinta parte más rica de Getafe, el PP saca de media el {p(Q[4]['PP'])} %; en la de Sevilla, sacó casi el 60 %, como contamos en {L('derbi-sevillano-nervion-heliopolis-29n', 'el derbi sevillano en las urnas')}.</p>

<h2>Y el Metropolitano</h2>
<p data-tipo="dato">El estadio del Atlético está en Rosas, en el distrito de San Blas-Canillejas, al este de Madrid. En sus {RO['n']} secciones, el PP ganó en {RO['gana']['PP']} en 2023, con el {p(RO['PP'])} %, frente al {p(RO['PSOE'])} % del PSOE. En toda la ciudad de Madrid, el PP sacó el {p(MADC['PP'])} % y el PSOE, el {p(MADC['PSOE'])} %. Cómo vota el distrito del Metropolitano frente al del viejo Calderón lo contamos en {L('atletico-barca-metropolitano-camp-nou-29n', 'el Atlético-Barça en las urnas')}.</p>
<p data-tipo="dato">Getafe y Madrid votan en la misma circunscripción, la provincia de Madrid, que elige {MODELO['escanos']} diputados. Nuestro modelo, que reparte por provincia la media de las encuestas nacionales, deja al PP primero en el {MODELO['pp_primero']} % de las simulaciones, con un reparto central de {MODELO['PP']} escaños para el PP, {MODELO['PSOE']} para el PSOE, {MODELO['VOX']} para Vox, {MODELO['SUMAR']} para Sumar y {MODELO['PODEMOS']} para Podemos, según la página de <a href="{BASE}encuestas/madrid/">encuestas de Madrid</a>, que se actualiza cada día.</p>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">Las cifras de sección son de las generales de 2023 y de 2019. Las encuestas del 29N no miden ciudades ni barrios, solo provincias, y nuestro modelo no estima el voto dentro de Getafe. En 2019 no comparamos a Sumar, porque Unidas Podemos y Más País fueron por separado. Los quintiles comparan secciones de la misma ciudad: describen dónde se vota qué, no el efecto de la renta. {SINB} secciones no tienen barrio asignado en nuestro mapa y solo cuentan en los totales.</p>
<p data-tipo="hipotesis">Y el fútbol no vota. La afición del Getafe y la del Atlético no viven solo junto a sus estadios, y nada de esto dice cómo vota cada una. Lo que sí muestra el mapa es que el Coliseum está en una ciudad que el PSOE ganó por {n(DIFV)} votos y en un barrio donde el PP subió casi quince puntos. Las calles de cada sección están en {L('como-voto-tu-calle', 'cómo votó tu calle')}.</p>
'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Getafe?', f'El PSOE, con el {p(H[E]["PSOE"])} %, por delante del PP ({p(H[E]["PP"])} %): {n(H[E]["vPSOE"])} votos frente a {n(H[E]["vPP"])}, {n(DIFV)} de diferencia.'),
    ('¿Ha ganado alguna vez el PP en Getafe en unas generales?', f'Sí: en 2011, con el {p(H["2011_11"]["PP"])} %, y en 2015 y 2016. Desde abril de 2019 gana el PSOE.'),
    ('¿Cómo vota el barrio del Coliseum?', f'En Getafe Norte, el PSOE ganó en {GN["gana"]["PSOE"]} de las {GN["n"]} secciones en 2023, con el {p(GN["PSOE"])} % frente al {p(GN["PP"])} % del PP.'),
]
enlaces = (f'<a href="{BASE}municipio/madrid/getafe/">Elecciones en Getafe</a> · <a href="{BASE}encuestas/madrid/">Encuesta de Madrid</a> · '
           f'{L("cinturon-rojo-madrid-29n", "Lo que queda del cinturón rojo")} · {L("atletico-barca-metropolitano-camp-nou-29n", "El Atlético-Barça en las urnas")} · '
           f'{L("derbi-sevillano-nervion-heliopolis-29n", "El derbi sevillano en las urnas")} · {L("valencia-madrid-mestalla-barrios-29n", "Mestalla y el Bernabéu en las urnas")}')
foot = ('Datos: Ministerio del Interior, generales de 2011 a 2023 por municipio y de noviembre de 2019 y julio de 2023 por sección censal; INE, renta por unidad de consumo '
        'por sección (Atlas de Distribución de Renta de los Hogares) y padrón municipal de 2023; barrios de OpenStreetMap; modelo de encuestas de Mapa Electoral. '
        'Cálculo: actualidad/src/resumenes/getafe_atletico.py.')

TIT = (f'Getafe-Atlético: en la ciudad del Coliseum, el PSOE pasó de ganar en {G19["PSOE"]} de las {len(g)} secciones a ganar en {G23["PSOE"]}, '
       f'y el PP se quedó a {n(DIFV)} votos')
DEK = (f'El día del Getafe-Atlético, Getafe sección a sección en las elecciones generales. El PP pasó del {p(H[E0]["PP"])} % al {p(H[E]["PP"])} % entre 2019 y 2023; '
       f'en Getafe Norte, el barrio del estadio, el PSOE ganó en {GN["gana"]["PSOE"]} de {GN["n"]} secciones.')
r1 = lambda x: round(float(x), 4)


def plano(s):
    return {**{k: r1(s[k]) for k in P + ['PP0', 'PSOE0', 'VOX0']}, 'part': r1(s['part']), 'renta': r1(s['renta']), 'n': int(s['n']), 'gana': s['gana'], 'gana0': s['gana0']}


DATOS = {'H': {e: {k: (r1(v) if isinstance(v, float) else v) for k, v in h.items()} for e, h in H.items()}, 'DIFV': DIFV, 'POB': POB,
         'G23': G23, 'G19': G19, 'NSEC': len(g), 'SINBARRIO': SINB, 'CIU': plano(CIU), 'BARR': {k: plano(s) for k, s in B.items()},
         'Q': {str(j): plano(s) for j, s in Q.items()}, 'ROSAS': plano(RO), 'MADRID': plano(MADC), 'MODELO': MODELO}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
if __name__ == '__main__':
    print(TIT)
    print(DEK)
    pieza('getafe-atletico-sur-madrid-29n', 'Getafe-Atlético en las urnas', TIT, DEK, '22 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, datos_js)
