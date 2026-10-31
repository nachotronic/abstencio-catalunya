"""«El derbi en las urnas: Bilbao y Donostia» (pieza de domingo, 1-11-2026, día del Athletic-Real Sociedad).

Cifras: municipios (generales-2026/data/municipios.json) y secciones (generales-2026/descargas/secciones.csv, con la renta
por unidad de consumo del INE) de las generales de 2004 a 2023; barrios de data/barrios/secciones_barrio.csv (en Bilbao,
67 secciones no tienen barrio asignado y solo cuentan en los totales). Quintiles de renta dentro de cada ciudad, sin
regresión: es una descripción, no un efecto.
Uso, desde la raíz: python3 actualidad/src/resumenes/derbi.py
"""
import json

import numpy as np
import pandas as pd

from comun import BASE, COLOR, RAIZ, esc, figura, n, pares, pieza

A = BASE + 'actualidad/'
BIL, DON = '48020', '20069'
NOM = {BIL: 'Bilbao', DON: 'Donostia'}
E, E0 = '2023_07', '2019_11'
P = ['PSOE', 'PNV', 'BILDU', 'PP', 'SUMAR', 'VOX']
ETQ = {'PSOE': 'PSOE', 'PNV': 'PNV', 'BILDU': 'EH Bildu', 'PP': 'PP', 'SUMAR': 'Sumar', 'VOX': 'Vox'}
p = lambda v: n(v, 1)

# --- La ciudad, 2004-2023 ---
m = json.load(open(RAIZ / 'generales-2026/data/municipios.json'))
idx = {c: i for i, c in enumerate(m['cod'])}
NUEVAS = ['2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
ciu = {c: {e: {k[8:]: m[k][idx[c]] for k in m if k.startswith(e)} for e in NUEVAS} for c in (BIL, DON)}
FAMS = ['PP', 'PSOE', 'SUMAR', 'PNV', 'BILDU', 'VOX', 'CS']
gan = {c: {e: max(FAMS, key=lambda k: ciu[c][e].get(k, 0)) for e in NUEVAS} for c in ciu}
assert [gan[BIL][e] for e in NUEVAS] == ['PNV', 'PSOE', 'PNV', 'SUMAR', 'PNV', 'PNV', 'PNV', 'PSOE'], gan[BIL]
assert [gan[DON][e] for e in NUEVAS] == ['PSOE', 'PSOE', 'BILDU', 'SUMAR', 'SUMAR', 'PNV', 'PNV', 'PSOE'], gan[DON]
pc = lambda c, e, k: ciu[c][e].get(k, 0) * 100
assert round(pc(BIL, E, 'PSOE'), 1) == 26.5 and round(pc(BIL, E, 'PNV'), 1) == 25.6 and round(pc(BIL, E, 'BILDU'), 1) == 15.6
assert round(pc(DON, E, 'PSOE'), 1) == 25.0 and round(pc(DON, E, 'BILDU'), 1) == 21.8 and round(pc(DON, E, 'PNV'), 1) == 21.3
assert round(pc(BIL, E0, 'PNV'), 1) == 34.5 and round(pc(DON, E0, 'PNV'), 1) == 30.3

# --- Secciones ---
d = pd.read_csv(RAIZ / 'generales-2026/descargas/secciones.csv', dtype={'tract_code': str, 'mun_code': str})
d = d[d.mun_code.isin([BIL, DON])].dropna(subset=[f'{E}_PSOE']).copy()
bar = pd.read_csv(RAIZ / 'data/barrios/secciones_barrio.csv', dtype=str)[['tract_code', 'barrio']]
d = d.merge(bar, on='tract_code', how='left')
NSEC = d.groupby('mun_code').size().to_dict()
assert NSEC == {BIL: 273, DON: 144}, NSEC
d['gana'] = d[[f'{E}_{k}' for k in P]].idxmax(axis=1).str[8:]
GS = {c: g.gana.value_counts().to_dict() for c, g in d.groupby('mun_code')}
assert GS[BIL] == {'PSOE': 147, 'PNV': 93, 'PP': 18, 'BILDU': 15}, GS[BIL]
assert GS[DON] == {'PSOE': 63, 'BILDU': 39, 'PNV': 30, 'PP': 12}, GS[DON]

# Cambio 2019-2023 en las secciones con las dos elecciones
dd = d.dropna(subset=[f'{E0}_PSOE'])
CAMBIO = {c: {k: int((g[f'{E}_{k}'] > g[f'{E0}_{k}']).sum()) for k in ('PSOE', 'PNV', 'BILDU')} for c, g in dd.groupby('mun_code')}
N2 = dd.groupby('mun_code').size().to_dict()
assert N2 == {BIL: 272, DON: 143} and CAMBIO[BIL] == {'PSOE': 270, 'PNV': 1, 'BILDU': 270} and CAMBIO[DON] == {'PSOE': 140, 'PNV': 0, 'BILDU': 140}, (N2, CAMBIO)


def cuota(s, k, e=E):
    return (s[f'{e}_{k}'] * s[f'{e}_votantes']).sum() / s[f'{e}_votantes'].sum() * 100


def part(s, e=E):
    return s[f'{e}_votantes'].sum() / s[f'{e}_censo'].sum() * 100


# Quintiles de renta dentro de cada ciudad (secciones con renta)
Q = {}
for c, g in d.dropna(subset=['renta_uc']).groupby('mun_code'):
    g = g.copy()
    g['q'] = pd.qcut(g.renta_uc.rank(method='first'), 5, labels=False)
    Q[c] = {q: {**{k: cuota(s, k) for k in P}, 'part': part(s), 'renta': s.renta_uc.median()} for q, s in g.groupby('q')}
assert round(Q[BIL][0]['PSOE'], 1) == 35.7 and round(Q[BIL][4]['PSOE'], 1) == 17.1 and round(Q[BIL][4]['PNV'], 1) == 32.1
assert round(Q[BIL][4]['PP'], 1) == 27.1 and round(Q[BIL][0]['part'], 1) == 55.6 and round(Q[BIL][4]['part'], 1) == 73.7
assert round(Q[DON][0]['PSOE'], 1) == 34.9 and round(Q[DON][1]['BILDU'], 1) == 26.1 and round(Q[DON][4]['PNV'], 1) == 28.4
assert round(Q[DON][0]['part'], 1) == 63.6 and round(Q[DON][4]['part'], 1) == 74.2

# Barrios
B = {}
for c, g in d.dropna(subset=['barrio']).groupby('mun_code'):
    B[c] = {b: {**{k: cuota(s, k) for k in P}, 'part': part(s)} for b, s in g.groupby('barrio')}
assert round(B[BIL]['Otxarkoaga']['part'], 1) == 47.3 and round(B[BIL]['Otxarkoaga']['PSOE'], 1) == 42.5
assert round(B[BIL]['Indautxu']['PNV'], 1) == 33.7 and round(B[BIL]['Indautxu']['PP'], 1) == 29.9
assert round(B[BIL]['Bilbao la Vieja']['BILDU'], 1) == 30.9 and round(B[BIL]['Casco Viejo']['BILDU'], 1) == 29.3
assert round(B[DON]['Parte Zaharra']['BILDU'], 1) == 37.4 and round(B[DON]['Egia']['BILDU'], 1) == 31.2
assert round(B[DON]['Altza']['PSOE'], 1) == 39.5 and round(B[DON]['Amaraberri']['PSOE'], 1) == 26.3
assert round(B[DON]['Erdialdea']['PNV'], 1) == 26.6 and round(B[DON]['Berabera']['PP'], 1) == 41.3


# --- Gráficos ---
def lineas(c, W=640, H=250, ml=40, mr=105, mt=12, mb=34):
    x = lambda i: ml + i * (W - ml - mr) / 4
    y = lambda v: mt + (40 - v) / 40 * (H - mt - mb)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc("Voto por quintil de renta en " + NOM[c])}">']
    for v in (0, 10, 20, 30, 40):
        out.append(f'<line x1="{ml}" x2="{W - mr}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--grid)"/><text x="{ml - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{v} %</text>')
    for i, t in enumerate(['Más pobre', '2.º', '3.º', '4.º', 'Más rico']):
        out.append(f'<text x="{x(i):.1f}" y="{H - 10}" text-anchor="middle">{t}</text>')
    for k in ('PSOE', 'PNV', 'BILDU', 'PP'):
        col = COLOR[ETQ[k]]
        pts = ' '.join(f'{x(i):.1f},{y(Q[c][i][k]):.1f}' for i in range(5))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3"/>')
        for i in range(5):
            out.append(f'<circle cx="{x(i):.1f}" cy="{y(Q[c][i][k]):.1f}" r="4" fill="{col}"><title>{ETQ[k]}, quintil {i + 1}: {p(Q[c][i][k])} %</title></circle>')
        out.append(f'<text x="{x(4) + 8:.1f}" y="{y(Q[c][4][k]) + 4:.1f}" class="lab">{ETQ[k]} {p(Q[c][4][k])}</text>')
    out.append('</svg>')
    return ''.join(out)


LEY = [(ETQ[k], COLOR[ETQ[k]]) for k in ('PSOE', 'PNV', 'BILDU', 'PP')]
FUENTE = 'Fuente: Ministerio del Interior (generales del 23 de julio de 2023, por sección censal) e INE (renta por unidad de consumo). Cada quintil reúne una quinta parte de las secciones de la ciudad, de la más pobre a la más rica.'


def tabla_q(c):
    return (['Quintil', 'Renta mediana (€)', 'PSOE', 'PNV', 'EH Bildu', 'PP', 'Participación'],
            [[f'{i + 1}.º', n(Q[c][i]['renta']), p(Q[c][i]['PSOE']), p(Q[c][i]['PNV']), p(Q[c][i]['BILDU']), p(Q[c][i]['PP']), p(Q[c][i]['part'])] for i in range(5)])


g_bil = figura('Bilbao: el PSOE en los barrios pobres, el PNV y el PP en los ricos',
               '% de voto en las generales de 2023 según la renta de la sección', lineas(BIL), FUENTE, LEY, tabla_q(BIL))
g_don = figura('Donostia: EH Bildu, más fuerte en los barrios de renta media',
               '% de voto en las generales de 2023 según la renta de la sección', lineas(DON), FUENTE, LEY, tabla_q(DON))
g_pnv = figura('Lo que cambió entre 2019 y 2023',
               '% de voto en las dos ciudades en las generales de noviembre de 2019 y de julio de 2023',
               pares([(f'{ETQ[k]}, {NOM[c]}', pc(c, E0, k), pc(c, E, k), COLOR[ETQ[k]]) for c in (BIL, DON) for k in ('PNV', 'PSOE', 'BILDU')],
                     40, 'Voto en Bilbao y Donostia en 2019 y 2023', ['2019', '2023'], ml=150),
               'Fuente: Ministerio del Interior, resultados por municipio.')

# Tabla de ganadores
NOMBRE = {'PNV': 'PNV', 'PSOE': 'PSOE', 'BILDU': 'EH Bildu (Amaiur)', 'SUMAR': 'Podemos', 'PP': 'PP'}
FECHA = {'2004_03': '2004', '2008_03': '2008', '2011_11': '2011', '2015_12': '2015', '2016_06': '2016', '2019_04': 'Abril 2019', '2019_11': 'Noviembre 2019', '2023_07': '2023'}
filas = ''.join(f'<tr><td>{FECHA[e]}</td><td>{NOMBRE[gan[BIL][e]]} ({p(pc(BIL, e, gan[BIL][e]))} %)</td><td>{NOMBRE[gan[DON][e]]} ({p(pc(DON, e, gan[DON][e]))} %)</td></tr>' for e in NUEVAS)
g_tab = ('<figure>\n<figcaption><span class="t">Quién ganó en cada ciudad</span><span class="s">Partido más votado en las elecciones generales, de 2004 a 2023</span></figcaption>\n'
         f'<div class="tbl"><table><thead><tr><th>Generales</th><th>Bilbao</th><th>Donostia</th></tr></thead><tbody>{filas}</tbody></table></div>\n'
         '<div class="src">Fuente: Ministerio del Interior. Podemos fue con En Comú y otras marcas en 2015 y como Unidos Podemos en 2016.</div>\n</figure>\n')

L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
M = lambda path, t: f'<a href="{BASE}municipio/{path}/">{t}</a>'
MB = lambda b, t: M('bizkaia/bilbao/' + b, t)
MD = lambda b, t: M('gipuzkoa/donostia-san-sebastian/' + b, t)

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Esta noche, a las nueve, el Athletic recibe a la Real Sociedad en San Mamés. Es el derbi vasco, el que enfrenta a las capitales de Bizkaia y Gipuzkoa. A cuatro semanas del 29N, las urnas también enfrentan a {M('bizkaia/bilbao', 'Bilbao')} y {M('gipuzkoa/donostia-san-sebastian', 'Donostia')}, y no por los colores de la camiseta: en una gana todavía el PNV en los barrios del centro, en la otra EH Bildu ya es primera en una de cada cuatro secciones censales.</p>
<p data-tipo="dato">En las generales de julio de 2023 ganó el mismo en las dos: el PSOE, con el {p(pc(BIL, E, 'PSOE'))} % en Bilbao y el {p(pc(DON, E, 'PSOE'))} % en Donostia. En Bilbao quedó segundo el PNV ({p(pc(BIL, E, 'PNV'))} %); en Donostia, EH Bildu ({p(pc(DON, E, 'BILDU'))} %), con el PNV medio punto por detrás ({p(pc(DON, E, 'PNV'))} %). Desde 2004, el PSOE solo había ganado a la vez en las dos ciudades una vez, en 2008.</p>
{g_tab}
<h2>El PNV bajó en todas partes</h2>
<p data-tipo="dato">Entre las generales de noviembre de 2019 y las de julio de 2023, el PNV pasó del {p(pc(BIL, E0, 'PNV'))} % al {p(pc(BIL, E, 'PNV'))} % en Bilbao y del {p(pc(DON, E0, 'PNV'))} % al {p(pc(DON, E, 'PNV'))} % en Donostia. La caída no se concentró en unos pocos barrios. De las {N2[BIL]} secciones censales de Bilbao que se pueden comparar, el PNV bajó en {N2[BIL] - CAMBIO[BIL]['PNV']}; en Donostia, en las {N2[DON]}. En las dos ciudades, el PSOE y EH Bildu subieron en casi todas: {CAMBIO[BIL]['PSOE']} y {CAMBIO[BIL]['BILDU']} de {N2[BIL]} en Bilbao, {CAMBIO[DON]['PSOE']} y {CAMBIO[DON]['BILDU']} de {N2[DON]} en Donostia.</p>
{g_pnv}
<p data-tipo="contexto">El presidente del PNV, Aitor Esteban, pidió el viernes a los empresarios vascos un partido «fuerte en Madrid». Lo contó <a href="https://cronicavasca.elespanol.com/politica/20261030/esteban-empresarios-pnv-madrid-mantener-concierto-industria/1003742807837_0.html">Crónica Vasca</a>:</p>
<blockquote class="cita"><p>«Es imprescindible una voz vasca en Madrid para defender la industria y cuidar el empleo»</p><footer>Aitor Esteban, presidente del PNV, ante el Círculo de Empresarios Vascos, el 30 de octubre. Recogido por <a href="https://cronicavasca.elespanol.com/politica/20261030/esteban-empresarios-pnv-madrid-mantener-concierto-industria/1003742807837_0.html">Crónica Vasca</a>.</footer></blockquote>
<p data-tipo="contexto">Ese mismo día, el Sociómetro del Gobierno vasco, con 3.485 entrevistas hechas del 20 al 23 de octubre, dejaba al PNV como tercera fuerza en Euskadi, con cerca del 22 %, por detrás de EH Bildu (cerca del 30 %) y del PSE-EE (cerca del 25 %), según <a href="https://www.eldiario.es/euskadi/victoria-eh-bildu-votos-escanos-generales-pse-ee-segundo-pnv-tercero-euskadi-sociometro_1_13626270.html">elDiario.es</a>. En Bizkaia le daba a EH Bildu el 25,9 % y al PNV el 24,7 %; en Gipuzkoa, a EH Bildu el 36,9 %, al PSOE el 22,8 % y al PNV el 20,3 %, según <a href="https://cronicavasca.elespanol.com/politica/20261030/sociometro-batacazo-pnv-generales-bildu-dispararia-euskadi/1003742807610_0.html">Crónica Vasca</a>. Oskar Matute, cabeza de lista de EH Bildu por Bizkaia, lo planteó así en Radio Euskadi:</p>
<blockquote class="cita"><p>«Eso es lo que nos jugamos el 29N. Euskal Herria va a dar la talla y va hacer que nuestros votos pesen»</p><footer>Oskar Matute, EH Bildu, el 30 de octubre en Radio Euskadi. Recogido por <a href="https://www.pressdigital.es/articulo/politica/2026-10-30/6072180-eh-bildu-insta-no-volverse-histericos-pedir-dimisiones-aclarar-hechos-responsabilidades">Press Digital</a>.</footer></blockquote>
<p data-tipo="dato">Nuestro modelo, que reparte la media de las encuestas nacionales por provincia, es más prudente con el PNV en Bizkaia: queda primero en el 36 % de las simulaciones, y EH Bildu en el 33 %, con dos escaños cada uno, dos el PSOE y uno el PP. En Gipuzkoa, EH Bildu queda primero en el 85 %. Las cifras de cada provincia están en las páginas de encuestas de <a href="{BASE}encuestas/bizkaia/">Bizkaia</a> y <a href="{BASE}encuestas/gipuzkoa/">Gipuzkoa</a>.</p>

<h2>Bilbao: la renta ordena el voto</h2>
<p data-tipo="patron">Dentro de Bilbao, el voto sigue a la renta casi como una escalera. En la quinta parte de las secciones más pobres, el PSOE sacó el {p(Q[BIL][0]['PSOE'])} % y el PNV, el {p(Q[BIL][0]['PNV'])} %. En la quinta parte más rica se dan la vuelta: el PNV saca el {p(Q[BIL][4]['PNV'])} %, el PP el {p(Q[BIL][4]['PP'])} % y el PSOE se queda en el {p(Q[BIL][4]['PSOE'])} %.</p>
{g_bil}
<p data-tipo="dato">Los barrios ponen nombre a la escalera. En {MB('indautxu', 'Indautxu')}, en el centro, el PNV sacó el {p(B[BIL]['Indautxu']['PNV'])} % y el PP, el {p(B[BIL]['Indautxu']['PP'])} %. En {MB('otxarkoaga', 'Otxarkoaga')}, el barrio con menos renta de los que tenemos asignados, el PSOE llegó al {p(B[BIL]['Otxarkoaga']['PSOE'])} %. EH Bildu solo ganó en {GS[BIL]['BILDU']} de las {NSEC[BIL]} secciones de la ciudad, casi todas en el Bilbao viejo: el {p(B[BIL]['Bilbao la Vieja']['BILDU'])} % en {MB('bilbao-la-vieja', 'Bilbao la Vieja')} y el {p(B[BIL]['Casco Viejo']['BILDU'])} % en el {MB('casco-viejo', 'Casco Viejo')}. El PSOE ganó en {GS[BIL]['PSOE']} secciones, el PNV en {GS[BIL]['PNV']} y el PP en {GS[BIL]['PP']}.</p>
<p data-tipo="dato">La renta también separa a quien vota de quien no. En las secciones más pobres de Bilbao votó el {p(Q[BIL][0]['part'])} %; en las más ricas, el {p(Q[BIL][4]['part'])} %. En Otxarkoaga, menos de la mitad: el {p(B[BIL]['Otxarkoaga']['part'])} %. Es la misma distancia que vimos esta semana en {L('quien-vota-barrios-renta-edad-inmigracion', 'toda España')}, y que un politólogo de la Universidad de Deusto, en Bilbao, explicaba así:</p>
<blockquote class="cita"><p>«Esto genera una concentración de poder político: si los ricos siempre votan, tendrán más poder en sus manos para que se tengan en cuenta sus intereses»</p><footer>Braulio Gómez, politólogo de la Universidad de Deusto, en <a href="https://www.eldiario.es/politica/barrios-pobres-van-votar-elecciones_1_1162754.html">elDiario.es</a> (7 de abril de 2019).</footer></blockquote>

<h2>Donostia: EH Bildu en el medio</h2>
<p data-tipo="patron">Donostia tiene la misma escalera para el PSOE, el PNV y el PP, pero con EH Bildu mucho más arriba. Su mejor resultado no está en los barrios más pobres, sino en los de renta media: el {p(Q[DON][1]['BILDU'])} % en el segundo quintil, frente al {p(Q[DON][4]['BILDU'])} % en el más rico. En los más pobres manda el PSOE, con el {p(Q[DON][0]['PSOE'])} %.</p>
{g_don}
<p data-tipo="dato">EH Bildu ganó en {GS[DON]['BILDU']} de las {NSEC[DON]} secciones de Donostia, más de una de cada cuatro, frente a {GS[BIL]['BILDU']} de {NSEC[BIL]} en Bilbao. Las más claras están en la {MD('parte-zaharra', 'Parte Vieja')} ({p(B[DON]['Parte Zaharra']['BILDU'])} %) y en {MD('egia', 'Egia')} ({p(B[DON]['Egia']['BILDU'])} %). El PSOE ganó en {MD('altza', 'Altza')}, al este, con el {p(B[DON]['Altza']['PSOE'])} %, y el PNV en el centro, con el {p(B[DON]['Erdialdea']['PNV'])} % en {MD('erdialdea', 'Erdialdea')}. En {MD('amaraberri', 'Amara')}, el barrio del estadio de la Real, ganó el PSOE con el {p(B[DON]['Amaraberri']['PSOE'])} %. El PP solo fue primero en {GS[DON]['PP']} secciones, con su máximo en Berabera ({p(B[DON]['Berabera']['PP'])} %).</p>
<p data-tipo="hipotesis">La diferencia entre las dos ciudades no se explica solo por la renta: Donostia es más rica que Bilbao y aun así EH Bildu saca allí más. Pesan otras cosas que estos datos no miden, como la lengua, la historia de cada barrio o la de la izquierda abertzale en Gipuzkoa. Por eso esta pieza describe dónde se vota qué y no atribuye el voto a ninguna causa.</p>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">Las cifras de sección son de las generales. En las autonómicas, los vascos votan de otra manera: el PNV y EH Bildu sacan allí mucho más que en las generales, y el PSOE bastante menos. Las encuestas del 29N tampoco miden ciudades, solo provincias. En Bilbao, 67 secciones no tienen barrio asignado en nuestro mapa y solo cuentan en los totales de la ciudad. Y los quintiles comparan secciones de la misma ciudad: no es una regresión ni mide efectos de la renta.</p>
<p data-tipo="contexto">El fútbol tampoco dice nada del voto. Esta noche, en San Mamés, se juega otra cosa. El 29N, el derbi de Bilbao y Donostia será entre el PSOE, que ganó en las dos, y un PNV que bajó en {N2[BIL] + N2[DON] - CAMBIO[BIL]['PNV'] - CAMBIO[DON]['PNV']} de las {N2[BIL] + N2[DON]} secciones de las dos ciudades.</p>
'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Bilbao?', f'El PSOE, con el {p(pc(BIL, E, "PSOE"))} % de los votos, por delante del PNV ({p(pc(BIL, E, "PNV"))} %), EH Bildu ({p(pc(BIL, E, "BILDU"))} %) y el PP ({p(pc(BIL, E, "PP"))} %).'),
    ('¿Quién ganó las elecciones generales de 2023 en Donostia-San Sebastián?', f'El PSOE, con el {p(pc(DON, E, "PSOE"))} %, por delante de EH Bildu ({p(pc(DON, E, "BILDU"))} %) y el PNV ({p(pc(DON, E, "PNV"))} %).'),
    ('¿En qué barrios gana EH Bildu en Bilbao y Donostia?', f'En Bilbao, en el Bilbao viejo: Bilbao la Vieja, el Casco Viejo, San Francisco, Atxuri. En Donostia, en {GS[DON]["BILDU"]} de las {NSEC[DON]} secciones, sobre todo en la Parte Vieja y Egia.'),
]
enlaces = (f'<a href="{BASE}municipio/bizkaia/bilbao/">Elecciones en Bilbao</a> · <a href="{BASE}municipio/gipuzkoa/donostia-san-sebastian/">Elecciones en Donostia</a> · '
           f'{L("barcelona-madrid-clasico-del-voto-29n", "El otro Clásico")} · {L("cuatro-semanas-29n-la-semana-en-el-mapa", "La crónica del sábado")} · {L("quien-vota-que-barrios-29n", "Quién vota qué, barrio a barrio")}')
foot = 'Datos: Ministerio del Interior, generales de 2004 a 2023 por municipio y sección censal; INE, renta por unidad de consumo por sección (Atlas de Distribución de Renta de los Hogares); barrios de OpenStreetMap; modelo de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/derbi.py.'

pieza('derbi-vasco-bilbao-donostia-29n', 'El derbi en las urnas: Bilbao y Donostia',
      f'El derbi en las urnas: el PNV bajó en {N2[BIL] + N2[DON] - CAMBIO[BIL]["PNV"] - CAMBIO[DON]["PNV"]} de las {N2[BIL] + N2[DON]} secciones de Bilbao y Donostia, y el PSOE ganó en las dos ciudades',
      f'El día del Athletic-Real Sociedad, las dos ciudades sección a sección. En 2023, el PSOE fue primero en Bilbao ({p(pc(BIL, E, "PSOE"))} %) y en Donostia ({p(pc(DON, E, "PSOE"))} %). En Bilbao manda la renta: el PSOE en los barrios pobres, el PNV y el PP en los ricos. En Donostia, EH Bildu gana en una de cada cuatro secciones.',
      '1 de noviembre de 2026', cuerpo, preguntas, enlaces, foot)
