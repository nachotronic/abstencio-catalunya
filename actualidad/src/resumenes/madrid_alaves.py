"""«Real Madrid-Alavés en las urnas» (pieza de sábado, 28-11-2026, día del Real Madrid-Alavés en el Bernabéu).

Cifras: secciones (generales-2026/descargas/secciones.csv, con la renta por unidad de consumo del INE) de las generales de
noviembre de 2019 y julio de 2023, con el más votado de cada sección lista a lista (columna _gana); barrios de
data/barrios/secciones_barrio.csv (OpenStreetMap); municipio de generales-2026/descargas/municipios.csv (2004-2023).
Mendizorrotza está en la sección 0105902035 (Vitoria) y el Bernabéu en la 2807905068 (Hispanoamérica, Chamartín), por sus
coordenadas sobre los polígonos de data/barrios/geo. La renta del INE tiene un tope (58.752 €) que alcanzan varias secciones:
no se compara entre ellas, solo el orden. Sin cifras de encuestas: es jornada de reflexión y rige la veda (LOREG 69.7).
Uso, desde la raíz: python3 actualidad/src/resumenes/madrid_alaves.py
"""
import json

import pandas as pd

from comun import BASE, COLOR, RAIZ, barras, figura, n, pieza

A = BASE + 'actualidad/'
VIT, MAD = '01059', '28079'
E, E0 = '2023_07', '2019_11'
P = ['PP', 'PSOE', 'SUMAR', 'VOX', 'BILDU', 'PNV']
ETQ = {'PP': 'PP', 'PSOE': 'PSOE', 'SUMAR': 'Sumar', 'VOX': 'Vox', 'BILDU': 'EH Bildu', 'PNV': 'PNV', 'EMPATE': 'Empate a votos'}
p = lambda v: n(v, 1)
ELEC = [('2004_03', '2004'), ('2008_03', '2008'), ('2011_11', '2011'), ('2015_12', '2015'), ('2016_06', '2016'),
        ('2019_04', 'abr. 2019'), ('2019_11', 'nov. 2019'), ('2023_07', '2023')]
# En 2015 y 2016, la columna SUMAR es Elkarrekin Podemos (Podemos e IU); en 2019, Unidas Podemos; en 2023, Sumar
ETQ_IZQ = {'2004_03': 'IU', '2008_03': 'IU', '2011_11': 'IU', '2015_12': 'Podemos', '2016_06': 'Podemos', '2019_04': 'Podemos', '2019_11': 'Podemos', '2023_07': 'Sumar'}

# --- Los dos municipios, elección a elección ---
mu = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str})


def hist(cod):
    r = mu[mu.mun_code == cod].iloc[0]
    return {e: {**{k: float(r[f'{e}_{k}']) * 100 for k in P if f'{e}_{k}' in r}, 'gana': r[f'{e}_gana'], 'part': float(r[f'{e}_part']) * 100}
            for e, _ in ELEC}, int(r['poblacion'])


HV, POBV = hist(VIT)
HM, POBM = hist(MAD)
assert [HV[e]['gana'] for e, _ in ELEC] == ['PSOE', 'PSOE', 'PP', 'SUMAR', 'SUMAR', 'PSOE', 'PSOE', 'PSOE']
assert [HM[e]['gana'] for e, _ in ELEC] == ['PP', 'PP', 'PP', 'PP', 'PP', 'PSOE', 'PP', 'PP']
assert round(HV[E]['PSOE'], 1) == 29.8 and round(HV[E]['PP'], 1) == 19.9 and round(HV[E]['BILDU'], 1) == 16.7 and round(HV[E]['PNV'], 1) == 14.3
assert round(HV[E0]['PNV'], 1) == 21.2 and round(HV['2011_11']['PP'], 1) == 29.4 and round(HV['2015_12']['SUMAR'], 1) == 31.7
assert round(HM[E]['PP'], 1) == 41.8 and POBV == 255886

# --- Secciones ---
d = pd.read_csv(RAIZ / 'generales-2026/descargas/secciones.csv', dtype={'tract_code': str, 'mun_code': str})
d = d[d.mun_code.isin([VIT, MAD])].dropna(subset=[f'{E}_PP']).copy()
bar = pd.read_csv(RAIZ / 'data/barrios/secciones_barrio.csv', dtype=str)[['tract_code', 'barrio', 'distrito']]
d = d.merge(bar, on='tract_code', how='left')
v = d[d.mun_code == VIT].copy()
m = d[d.mun_code == MAD].copy()
assert int(v.barrio.isna().sum()) == 0 and int(m.barrio.isna().sum()) == 0
G23 = {k: int(c) for k, c in v[f'{E}_gana'].value_counts().items()}
G19 = {k: int(c) for k, c in v[f'{E0}_gana'].value_counts().items()}
assert len(v) == 166 and G23 == {'PSOE': 128, 'PP': 26, 'BILDU': 12} and G19 == {'PSOE': 82, 'PNV': 41, 'PP': 18, 'SUMAR': 18, 'BILDU': 6, 'EMPATE': 1}
MENDI, BERNA = '0105902035', '2807905068'
assert v.loc[v.tract_code == MENDI, 'barrio'].item() == 'Mendizorrotza'
assert m.loc[m.tract_code == BERNA, 'barrio'].item() == 'Hispanoamérica' and m.loc[m.tract_code == BERNA, 'distrito'].item() == 'Chamartín'


def cuota(s, k, e=E):
    return (s[f'{e}_{k}'] * s[f'{e}_votantes']).sum() / s[f'{e}_votantes'].sum() * 100


def part(s, e=E):
    return s[f'{e}_votantes'].sum() / s[f'{e}_censo'].sum() * 100


def resumen(s):
    return {**{k: cuota(s, k) for k in P}, 'part': part(s), 'n': len(s),
            'gana': {k: int(c) for k, c in s[f'{E}_gana'].value_counts().items()},
            'gana0': {k: int(c) for k, c in s[f'{E0}_gana'].value_counts().items()},
            'PP0': cuota(s, 'PP', E0), 'PSOE0': cuota(s, 'PSOE', E0), 'PNV0': cuota(s, 'PNV', E0)}


CIU = resumen(v)
assert round(CIU['part'], 1) == 66.5
B = {k: resumen(s) for k, s in v.groupby('barrio')}
MZ = B['Mendizorrotza']
assert MZ['n'] == 3 and MZ['gana'] == {'PP': 3} and MZ['gana0'] == {'PP': 3}
assert round(MZ['PP'], 1) == 46.5 and round(MZ['PSOE'], 1) == 13.9 and round(MZ['PNV'], 1) == 21.2 and round(MZ['part'], 1) == 73.2 and round(MZ['PP0'], 1) == 39.1
SEG = sorted(B, key=lambda k: -B[k]['PP'])
assert SEG[0] == 'Mendizorrotza' and SEG[1] == 'Ensanche' and round(B['Ensanche']['PP'], 1) == 35.3
SOBRE40 = [k for k in B if B[k]['PP'] > 40]
assert SOBRE40 == ['Mendizorrotza']
# Las tres secciones de Mendizorrotza son las tres de más renta de Vitoria (dos, en el tope del INE)
TOP3 = set(v.sort_values('renta_uc', ascending=False).tract_code.head(3))
assert TOP3 == set(v[v.barrio == 'Mendizorrotza'].tract_code)
CV, ZA, ZB, SA = B['Casco Viejo'], B['Zaramaga'], B['Zabalgana'], B['Salburua']
assert CV['gana'] == {'BILDU': 6} and round(CV['BILDU'], 1) == 31.1
assert ZA['gana'] == {'PSOE': 8} and round(ZA['PSOE'], 1) == 40.1 and round(ZA['part'], 1) == 61.9
assert ZB['gana0'] == {'SUMAR': 8, 'PNV': 5} and ZB['gana'] == {'PSOE': 12, 'BILDU': 1}
assert SA['gana0'] == {'SUMAR': 6, 'PNV': 2, 'PSOE': 1} and SA['gana'] == {'PSOE': 8, 'BILDU': 1}

# Quintiles de renta en Vitoria
q = v.dropna(subset=['renta_uc']).copy()
q['q'] = pd.qcut(q.renta_uc.rank(method='first'), 5, labels=False)
Q = {j: resumen(s) for j, s in q.groupby('q')}
assert Q[0]['gana'] == {'PSOE': 30, 'BILDU': 4} and round(Q[0]['PSOE'], 1) == 35.3 and round(Q[0]['PP'], 1) == 16.2
assert Q[4]['gana'] == {'PP': 22, 'PSOE': 9, 'BILDU': 2} and round(Q[4]['PP'], 1) == 29.4 and round(Q[4]['PSOE'], 1) == 22.2
assert all(Q[j]['gana'].get('PP', 0) == 0 for j in (0, 1, 2))

# Madrid: el Bernabéu
HI = resumen(m[m.barrio == 'Hispanoamérica'])
CH = resumen(m[m.distrito == 'Chamartín'])
MADC = resumen(m)
assert HI['n'] == 21 and HI['gana'] == {'PP': 21} and round(HI['PP'], 1) == 62.1 and round(HI['PSOE'], 1) == 12.8 and round(HI['VOX'], 1) == 16.7
assert CH['n'] == 101 and CH['gana'] == {'PP': 100, 'PSOE': 1} and round(CH['PP'], 1) == 59.0 and round(CH['part'], 1) == 81.0
assert round(MADC['PP'], 1) == 41.8 and round(MADC['PSOE'], 1) == 27.4

# --- Gráficos ---
FUENTE_S = 'Fuente: Ministerio del Interior (generales por sección censal), barrios según OpenStreetMap.'
claro = lambda c: f'color-mix(in srgb, {c} 45%, var(--bg))'
COL_IZQ = COLOR['Sumar']


def fila_h(e, t):
    h = HV[e]
    ks = [('PSOE', COLOR['PSOE'], 'PSOE'), ('PP', COLOR['PP'], 'PP'), ('PNV', COLOR['PNV'], 'PNV'), ('SUMAR', COL_IZQ, ETQ_IZQ[e])]
    if h.get('BILDU', 0) > 0:
        ks.append(('BILDU', COLOR['EH Bildu'], 'EH Bildu'))
    return [(f'{t} · {lab}', h[k], col if h['gana'] == k else claro(col), f'{p(h[k])} %') for k, col, lab in ks]


g_hist = figura('En Vitoria ganaron el PSOE, el PP y Podemos; desde 2019 gana el PSOE',
                '% de voto de los principales partidos en Vitoria-Gasteiz en cada elección general desde 2004. En color fuerte, el más votado',
                barras([f for e, t in ELEC for f in fila_h(e, t)], 45, 'Voto por partido en Vitoria, 2004-2023', W=420, ml=140),
                'Fuente: Ministerio del Interior, resultados por municipio. Izquierda Unida (Ezker Batua) hasta 2011; Podemos con sus aliados en 2015, 2016 y 2019; Sumar en 2023. '
                'EH Bildu se presenta desde 2011 (en 2011, como Amaiur).',
                [('PSOE', COLOR['PSOE']), ('PP', COLOR['PP']), ('PNV', COLOR['PNV']), ('IU / Podemos / Sumar', COL_IZQ), ('EH Bildu', COLOR['EH Bildu'])],
                (['Elección', 'Más votado', 'PSOE (%)', 'PP (%)', 'PNV (%)', 'IU / Podemos / Sumar (%)', 'EH Bildu (%)', 'Participación (%)'],
                 [[t, {'SUMAR': ETQ_IZQ[e]}.get(HV[e]['gana'], ETQ.get(HV[e]['gana'], HV[e]['gana'])), p(HV[e]['PSOE']), p(HV[e]['PP']), p(HV[e]['PNV']),
                   p(HV[e]['SUMAR']), p(HV[e].get('BILDU', 0)), p(HV[e]['part'])] for e, t in ELEC]))

_ord19 = ['PSOE', 'PNV', 'PP', 'SUMAR', 'BILDU']
_col = {'PSOE': COLOR['PSOE'], 'PNV': COLOR['PNV'], 'PP': COLOR['PP'], 'SUMAR': COL_IZQ, 'BILDU': COLOR['EH Bildu']}
_lab = {'PSOE': 'PSOE', 'PNV': 'PNV', 'PP': 'PP', 'SUMAR': 'Podemos / Sumar', 'BILDU': 'EH Bildu'}
g_sec = figura(f'El PSOE pasó de {G19["PSOE"]} a {G23["PSOE"]} secciones; el PNV, de {G19["PNV"]} a ninguna',
               f'Secciones censales de Vitoria según el partido más votado, en noviembre de 2019 y en julio de 2023 (de {len(v)})',
               barras([(f'{_lab[k]} · {a}', G.get(k, 0), c(_col[k]), str(G.get(k, 0)))
                       for k in _ord19 for a, G, c in (('2019', G19, claro), ('2023', G23, lambda x: x))],
                      166, 'Secciones ganadas por cada partido en Vitoria', W=420, ml=150),
               f'Fuente: Ministerio del Interior, más votado de cada sección lista a lista. En 2019, Unidas Podemos; en 2023, Sumar. En 2019 hubo además un empate a votos.',
               [('2019', claro(COLOR['PSOE'])), ('2023', COLOR['PSOE'])],
               (['Partido', 'Secciones en 2019', 'Secciones en 2023'], [[_lab[k], str(G19.get(k, 0)), str(G23.get(k, 0))] for k in _ord19]))

g_bar = figura('Mendizorrotza, el barrio del estadio, es el único de Vitoria donde el PP pasa del 40 %',
               'Voto al PP, en %, en cada barrio de Vitoria en las elecciones generales de 2023. El barrio de Mendizorrotza, en color fuerte',
               barras([(k, B[k]['PP'], COLOR['PP'] if k == 'Mendizorrotza' else claro(COLOR['PP']), f'{p(B[k]["PP"])} %') for k in SEG],
                      50, 'Voto al PP por barrio de Vitoria', W=420, ml=150),
               FUENTE_S + ' Los barrios con una o dos secciones tienen pocos votantes.',
               [('PP', COLOR['PP'])],
               (['Barrio', 'PP', 'PSOE', 'EH Bildu', 'PNV', 'Sumar', 'Vox', 'Participación', 'Secciones', 'Ganadas por el PP', 'Ganadas por el PSOE'],
                [[k, p(B[k]['PP']), p(B[k]['PSOE']), p(B[k]['BILDU']), p(B[k]['PNV']), p(B[k]['SUMAR']), p(B[k]['VOX']), p(B[k]['part']), str(B[k]['n']),
                  str(B[k]['gana'].get('PP', 0)), str(B[k]['gana'].get('PSOE', 0))] for k in SEG]))

QN = ['Más pobre', '2.º', '3.º', '4.º', 'Más rico']
g_q = figura('En Vitoria, el PP solo gana secciones en la mitad más rica',
             'Voto al PSOE y al PP, en %, en las elecciones generales de 2023 según la renta de la sección (quintiles de Vitoria)',
             barras([(f'{QN[j]} · {k}', Q[j][k], COLOR[k], f'{p(Q[j][k])} %') for j in range(5) for k in ('PSOE', 'PP')],
                    40, 'Voto al PSOE y al PP por quintil de renta en Vitoria', W=420, ml=120),
             'Fuente: Ministerio del Interior (generales de 2023, por sección censal) e INE (renta por unidad de consumo). Cada quintil reúne una quinta parte de las secciones de Vitoria, de la más pobre a la más rica.',
             [('PSOE', COLOR['PSOE']), ('PP', COLOR['PP'])],
             (['Quintil', 'PSOE', 'PP', 'EH Bildu', 'PNV', 'Sumar', 'Participación', 'Secciones', 'Ganadas por el PSOE', 'Ganadas por el PP', 'Ganadas por EH Bildu'],
              [[QN[j], p(Q[j]['PSOE']), p(Q[j]['PP']), p(Q[j]['BILDU']), p(Q[j]['PNV']), p(Q[j]['SUMAR']), p(Q[j]['part']), str(Q[j]['n']),
                str(Q[j]['gana'].get('PSOE', 0)), str(Q[j]['gana'].get('PP', 0)), str(Q[j]['gana'].get('BILDU', 0))] for j in range(5)]))

L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
CVIT = f'<a href="{BASE}municipio/alava/vitoria-gasteiz/">Vitoria-Gasteiz</a>'
CMAD = f'<a href="{BASE}municipio/madrid/madrid/">Madrid</a>'
LALIGA = 'https://www.laliga.com/noticias/horarios-de-la-decimocuarta-jornada-de-laliga-ea-sports-2026-27'
VU_ALA = f'{BASE}elecciones/pais-vasco/alava/voto-util-29n/'
VU_MAD = f'{BASE}elecciones/madrid/voto-util-29n/'

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Esta noche, a las 21.00, el Real Madrid recibe al Alavés en el Bernabéu, en la jornada 14 de LaLiga, según el horario oficial de <a href="{LALIGA}">LaLiga</a>. Es la víspera de las elecciones generales del 29N, la jornada de reflexión. El Alavés juega en Mendizorrotza, en el barrio del mismo nombre, al sur de {CVIT}, una ciudad de {n(POBV)} habitantes según el padrón municipal de 2023 (INE). Vitoria y Madrid votan de forma muy distinta. Los barrios de sus dos estadios se parecen bastante más.</p>
<p data-tipo="dato">En las generales de julio de 2023, el PSOE fue el más votado en Vitoria, con el {p(HV[E]['PSOE'])} %. Detrás quedaron el PP, con el {p(HV[E]['PP'])} %, EH Bildu, con el {p(HV[E]['BILDU'])} %, y el PNV, con el {p(HV[E]['PNV'])} %. En {CMAD}, el PP sacó el {p(HM[E]['PP'])} % y el PSOE, el {p(HM[E]['PSOE'])} %.</p>
<p data-tipo="dato">Vitoria ha cambiado de ganador más que Madrid. El PSOE ganó allí en 2004 y 2008, el PP en 2011, con el {p(HV['2011_11']['PP'])} %, y Podemos en 2015 y 2016, con el {p(HV['2015_12']['SUMAR'])} % la primera vez. Desde abril de 2019, el primero es el PSOE. En la ciudad de Madrid, el PP ganó en todas las generales desde 2004 salvo en las de abril de 2019.</p>
{g_hist}

<h2>De 82 secciones a 128</h2>
<p data-tipo="dato">Sección a sección, el cambio de 2019 a 2023 se ve mejor. En noviembre de 2019, el PSOE fue el más votado en {G19['PSOE']} de las {len(v)} secciones de Vitoria, el PNV en {G19['PNV']}, el PP y Unidas Podemos en {G19['PP']} cada uno y EH Bildu en {G19['BILDU']}. En 2023, el PSOE ganó en {G23['PSOE']}, el PP en {G23['PP']} y EH Bildu en {G23['BILDU']}. <strong>El PNV no fue primero en ninguna</strong>: en la ciudad bajó del {p(HV[E0]['PNV'])} % al {p(HV[E]['PNV'])} %.</p>
{g_sec}
<p data-tipo="dato">Donde más se nota es en los barrios nuevos del este y del oeste. En Zabalgana, en 2019 ganaban Unidas Podemos ({ZB['gana0']['SUMAR']} secciones) y el PNV ({ZB['gana0']['PNV']}); en 2023, el PSOE ganó en {ZB['gana']['PSOE']} de las {ZB['n']}. En Salburua, el PSOE pasó de ganar en {SA['gana0']['PSOE']} sección a ganar en {SA['gana']['PSOE']} de {SA['n']}. En el Casco Viejo, EH Bildu ganó las {CV['gana']['BILDU']} secciones, con el {p(CV['BILDU'])} %, y en Zaramaga el PSOE sacó el {p(ZA['PSOE'])} %, con una participación del {p(ZA['part'])} %.</p>

<h2>El barrio de Mendizorrotza</h2>
<p data-tipo="dato">El estadio del Alavés está en el barrio que más vota al PP de Vitoria. En sus {MZ['n']} secciones, el PP fue el más votado en las tres, en 2019 y en 2023, y en 2023 sacó el <strong>{p(MZ['PP'])} %</strong>, frente al {p(MZ['PNV'])} % del PNV y el {p(MZ['PSOE'])} % del PSOE. Es el único barrio de la ciudad donde el PP pasa del 40 %; el siguiente es el Ensanche, con el {p(B['Ensanche']['PP'])} %. Votó el {p(MZ['part'])} %, frente al {p(CIU['part'])} % de toda la ciudad.</p>
<p data-tipo="dato">Las tres secciones de Mendizorrotza son también las tres de más renta de Vitoria, según el Atlas de Distribución de Renta de los Hogares del INE.</p>
{g_bar}

<h2>La renta, sección a sección</h2>
<p data-tipo="patron">Si se ordenan las secciones de Vitoria por renta y se parten en cinco grupos iguales, el PP no es el más votado en ninguna de las tres quintas partes más pobres. En la quinta parte más pobre, el PSOE gana {Q[0]['gana']['PSOE']} de {Q[0]['n']} secciones, con el {p(Q[0]['PSOE'])} %, y el PP saca el {p(Q[0]['PP'])} %. En la más rica, el PP gana {Q[4]['gana']['PP']} de {Q[4]['n']}, con el {p(Q[4]['PP'])} %, frente al {p(Q[4]['PSOE'])} % del PSOE.</p>
{g_q}

<h2>Y el Bernabéu</h2>
<p data-tipo="dato">El Bernabéu está en el barrio de Hispanoamérica, en el distrito de Chamartín. En sus {HI['n']} secciones, el PP fue el más votado en las {HI['gana']['PP']} en 2023, con el {p(HI['PP'])} %, por delante de Vox ({p(HI['VOX'])} %) y del PSOE ({p(HI['PSOE'])} %). En todo Chamartín ganó en {CH['gana']['PP']} de las {CH['n']} secciones, con una participación del {p(CH['part'])} %, como contamos en {L('valencia-madrid-mestalla-barrios-29n', 'Mestalla y el Bernabéu en las urnas')}.</p>
<p data-tipo="dato">Las dos ciudades votan en circunscripciones muy distintas. Álava elige 4 diputados y, con los votos de 2023, su último escaño fue para el PNV; al PSOE le habrían bastado 3.126 votantes, como contamos en <a href="{VU_ALA}">el voto útil en Álava</a>. Madrid elige 38, y su último escaño fue para el PSOE, con el PP a 35.114 votantes, según <a href="{VU_MAD}">el voto útil en Madrid</a>.</p>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">Las cifras de sección son de las generales de 2023 y de 2019. Los quintiles comparan secciones de la misma ciudad: describen dónde se vota qué, no el efecto de la renta. La renta del INE tiene un tope que alcanzan dos de las tres secciones de Mendizorrotza, así que solo decimos que son las de más renta, no cuánto más. Unidas Podemos en 2019 y Sumar en 2023 no son la misma candidatura.</p>
<p data-tipo="hipotesis">Y el fútbol no vota. La afición del Alavés y la del Real Madrid no viven solo junto a sus estadios, y nada de esto dice cómo vota cada una. Lo que muestra el mapa es que los dos estadios están en barrios donde el PP saca mucho más que en el resto de su ciudad, aunque en Vitoria el PSOE ganó en {G23['PSOE']} de las {len(v)} secciones. Las calles de cada sección están en {L('como-voto-tu-calle', 'cómo votó tu calle')}, y lo que hay que saber para mañana, en {L('como-votar-elecciones-generales-29n', 'cómo votar el 29N')} y {L('a-que-hora-resultados-elecciones-generales-29n', 'a qué hora se sabrán los resultados')}.</p>
'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Vitoria?', f'El PSOE, con el {p(HV[E]["PSOE"])} %, por delante del PP ({p(HV[E]["PP"])} %), EH Bildu ({p(HV[E]["BILDU"])} %) y el PNV ({p(HV[E]["PNV"])} %). Fue el más votado en {G23["PSOE"]} de las {len(v)} secciones.'),
    ('¿Cómo vota el barrio de Mendizorrotza?', f'El PP fue el más votado en sus {MZ["n"]} secciones en 2023, con el {p(MZ["PP"])} %: es el único barrio de Vitoria donde pasó del 40 %.'),
    ('¿Cómo vota el barrio del Bernabéu?', f'En Hispanoamérica, el barrio del estadio, el PP ganó en las {HI["n"]} secciones en 2023, con el {p(HI["PP"])} %.'),
]
enlaces = (f'<a href="{BASE}municipio/alava/vitoria-gasteiz/">Elecciones en Vitoria-Gasteiz</a> · <a href="{VU_ALA}">Voto útil en Álava</a> · '
           f'{L("valencia-madrid-mestalla-barrios-29n", "Mestalla y el Bernabéu en las urnas")} · {L("derbi-vasco-bilbao-donostia-29n", "El derbi vasco en las urnas")} · '
           f'{L("getafe-atletico-sur-madrid-29n", "Getafe-Atlético en las urnas")} · {L("euskadi-29n-guia", "Guía del 29N en Euskadi")}')
foot = ('Datos: Ministerio del Interior, generales de 2004 a 2023 por municipio y de noviembre de 2019 y julio de 2023 por sección censal; INE, renta por unidad de consumo '
        'por sección (Atlas de Distribución de Renta de los Hogares) y padrón municipal de 2023; barrios de OpenStreetMap. Cálculo: actualidad/src/resumenes/madrid_alaves.py.')

TIT = (f'Real Madrid-Alavés: en Vitoria, el PSOE ganó en {G23["PSOE"]} de las {len(v)} secciones, pero en Mendizorrotza, el barrio del estadio del Alavés, '
       f'el PP sacó el {p(MZ["PP"])} %')
DEK = (f'El día del Real Madrid-Alavés, Vitoria sección a sección en las elecciones generales. El PNV, primero en {G19["PNV"]} secciones en 2019, no ganó ninguna en 2023; '
       f'el Bernabéu está en un barrio donde el PP ganó las {HI["n"]}.')
r1 = lambda x: round(float(x), 4)


def plano(s):
    return {**{k: r1(s[k]) for k in P + ['PP0', 'PSOE0', 'PNV0']}, 'part': r1(s['part']), 'n': int(s['n']), 'gana': s['gana'], 'gana0': s['gana0']}


DATOS = {'HV': {e: {k: (r1(x) if isinstance(x, float) else x) for k, x in h.items()} for e, h in HV.items()},
         'HM': {e: {k: (r1(x) if isinstance(x, float) else x) for k, x in h.items()} for e, h in HM.items()}, 'POBV': POBV,
         'G23': G23, 'G19': G19, 'NSEC': len(v), 'CIU': plano(CIU), 'BARR': {k: plano(s) for k, s in B.items()},
         'Q': {str(j): plano(s) for j, s in Q.items()}, 'HISP': plano(HI), 'CHAM': plano(CH), 'MADRID': plano(MADC)}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
if __name__ == '__main__':
    print(TIT)
    print(DEK)
    pieza('real-madrid-alaves-chamartin-vitoria-29n', 'Real Madrid-Alavés en las urnas', TIT, DEK, '28 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, datos_js)
