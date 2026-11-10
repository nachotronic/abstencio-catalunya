"""«Sánchez promete superar el 70 % de participación» (10-11-2026).

El 9-11-2026, Pedro Sánchez (entrevista con Javier Ruiz en La Séptima) dijo que el 29N «de lejos va a superar el 70 % de
participación que tuvimos en las elecciones de 2023», mientras Santiago Abascal estaba en La Revuelta (La 1). La pieza
mira esa cifra con los datos: participación de los electores residentes en España (sin voto exterior) en cada
generales desde 1977, por provincia en 2019 y 2023, y cuántos votantes harían falta con el censo de 2026.

Datos: generales-2026/descargas/municipios_historico.csv (1977-2000) y municipios.csv (2004-2023), Ministerio del
Interior, votantes / censo de residentes; data/censo/censo_municipios_2023_2026.csv (INE, censo electoral CER 2026).
Uso, desde la raíz: python3 actualidad/src/resumenes/participacion_70.py
"""
import json

import pandas as pd

from comun import BASE, COLOR, RAIZ, esc, figura, n, barras, pares, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
s1 = lambda v: f'{v:+.1f}'.replace('.', ',').replace('-', '−')
mill = lambda v: n(v / 1e6, 1)

h = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios_historico.csv', dtype={'mun_code': str})
m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str})
m['prov'] = m.mun_code.str[:2]
ANOS = ['1977_06', '1979_03', '1982_10', '1986_06', '1989_10', '1993_06', '1996_03', '2000_03',
        '2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
MES = {'03': 'mar.', '06': 'jun.', '10': 'oct.', '11': 'nov.', '12': 'dic.', '04': 'abr.', '07': 'jul.'}
NOMBRE = {y: f'{MES[y[5:]]} {y[:4]}' if y[:4] in ('2019',) else y[:4] for y in ANOS}
PART = {}
for y in ANOS:
    t = h if y < '2004' else m
    PART[y] = {'part': t[f'{y}_votantes'].sum() / t[f'{y}_censo'].sum() * 100, 'votantes': int(t[f'{y}_votantes'].sum()),
               'censo': int(t[f'{y}_censo'].sum())}
P23 = PART['2023_07']['part']
assert 70.3 < P23 < 70.5, P23                          # oficial, sin CERA: 70,40 %
SOBRE = [y for y in ANOS if round(PART[y]['part'], 1) > 70.0]
BAJO = [y for y in ANOS if round(PART[y]['part'], 1) < 70.0]
IGUAL = [y for y in ANOS if round(PART[y]['part'], 1) == 70.0]
assert len(SOBRE) == 11 and IGUAL == ['2000_03'] and BAJO == ['1979_03', '1989_10', '2016_06', '2019_11'], (SOBRE, IGUAL, BAJO)
MAX = max(ANOS, key=lambda y: PART[y]['part'])
assert MAX == '1982_10'

# Provincias
g = m.groupby(['prov', 'provincia'])[['2023_07_votantes', '2023_07_censo', '2019_11_votantes', '2019_11_censo']].sum().reset_index()
g['p23'] = g['2023_07_votantes'] / g['2023_07_censo'] * 100
g['p19'] = g['2019_11_votantes'] / g['2019_11_censo'] * 100
g['nombre'] = g.provincia.str.split('/').str[0]
assert len(g) == 52
BAJO70 = g[g.p23 < 70].sort_values('p23')
N_BAJO70 = len(BAJO70)
CAT = g[g.prov.isin(['08', '17', '25', '43'])].sort_values('p23')
assert set(CAT.prov) <= set(BAJO70.prov)
CAT_TOT = {k: CAT[f'{k}_votantes'].sum() / CAT[f'{k}_censo'].sum() * 100 for k in ('2023_07', '2019_11')}
BCN = g[g.prov == '08'].iloc[0]
GIR = g[g.prov == '17'].iloc[0]
SEG = g.sort_values('p23').iloc[-1]
MEL = g.sort_values('p23').iloc[0]
assert SEG.nombre == 'Segovia' and MEL.nombre == 'Melilla'
SUBEN = int((g.p23 > g.p19).sum())
assert g.sort_values('2023_07_censo').iloc[-2].prov == '08'   # Barcelona, la segunda provincia con más electores
assert set(BAJO70.prov) == {'51', '52', '35', '38', '07', '11', '21', '29', '04', '01', '20', '48', '31', '08', '17', '25', '43'}

# Censo de 2026 (INE, residentes en España)
c = pd.read_csv(RAIZ / 'data/censo/censo_municipios_2023_2026.csv', dtype={'mun_code': str})
CER26 = int(c.cer_2026.sum())
V23 = PART['2023_07']['votantes']
V70, V75 = CER26 * .70, CER26 * .75
MAS70, MAS75 = V70 - V23, V75 - V23
assert 35.9e6 < CER26 < 36.0e6



def pares1(filas, maximo, etiqueta, nombres, W=440, ml=90):
    """Como comun.pares, pero con un decimal."""
    alto, H = 40, 40 * len(filas) + 8
    x = lambda v: ml + v / maximo * (W - ml - 110)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(etiqueta)}">']
    for i, (nom, a, b, col) in enumerate(filas):
        y = 4 + i * alto
        out.append(f'<text x="{ml - 8}" y="{y + 22}" text-anchor="end" class="lab">{esc(nom)}</text>')
        for k, (v, op) in enumerate(((a, .38), (b, 1))):
            yy = y + 4 + k * 16
            out.append(f'<rect x="{ml}" y="{yy}" width="{max(1.5, x(v) - ml):.1f}" height="13" fill="{col}" fill-opacity="{op}" rx="2"><title>{esc(nom)}, {esc(nombres[k])}: {p(v)} %</title></rect>')
            out.append(f'<text x="{x(v) + 6:.1f}" y="{yy + 11}">{p(v)} %{" (" + nombres[k] + ")" if i == 0 else ""}</text>')
    out.append('</svg>')
    return ''.join(out)

# --- Gráficos ---
ACC = 'var(--acc)'
GRIS = 'var(--otros)'
g_hist = figura(f'La participación pasó del 70 % en 11 de las 16 generales',
                'Porcentaje de los electores residentes en España que votó en cada elección general, sin el voto exterior',
                barras([(NOMBRE[y], PART[y]['part'], ACC if round(PART[y]['part'], 1) > 70 else GRIS, f'{p(PART[y]["part"])} %') for y in ANOS], 85,
                       'Participación en cada elección general', W=440, ml=80, alto=22, linea=(70, '70 %'), separar=True),
                'Fuente: Ministerio del Interior, resultados por municipio. Votantes sobre censo de residentes en España (CER). Cálculo propio.',
                [('Más del 70 %', ACC), ('70 % o menos', GRIS)],
                (['Elección', 'Censo de residentes', 'Votantes', 'Participación (%)'],
                 [[NOMBRE[y], n(PART[y]['censo']), n(PART[y]['votantes']), p(PART[y]['part'])] for y in ANOS]))

g_prov = figura(f'Las {N_BAJO70} provincias que no llegaron al 70 % en 2023',
                'Participación en las generales de julio de 2023, sin voto exterior, en las provincias por debajo del 70 %',
                barras([(r.nombre, r.p23, GRIS, f'{p(r.p23)} %') for r in BAJO70.itertuples()], 80,
                       'Participación en 2023 por provincia', W=440, ml=150, alto=22, linea=(P23, f'España: {p(P23)} %'), separar=True),
                'Fuente: Ministerio del Interior. Votantes sobre censo de residentes en España. Cálculo propio. Las 52 provincias, en la tabla.',
                [('Participación en 2023', GRIS)],
                (['Provincia', 'Nov. 2019 (%)', '2023 (%)', 'Diferencia (puntos)'],
                 [[esc(r.provincia), p(r.p19), p(r.p23), s1(r.p23 - r.p19)] for r in g.sort_values('p23').itertuples()]))

g_cat = figura('En Cataluña, la participación cayó en 2023',
               'Participación en las generales de noviembre de 2019 y de julio de 2023, sin voto exterior',
               pares1([(r.nombre, r.p19, r.p23, ACC) for r in CAT.itertuples()] + [('España', PART['2019_11']['part'], P23, GRIS)], 85,
                      'Participación en 2019 y 2023 en las provincias catalanas', ['nov. 2019', '2023'], W=440, ml=90),
               f'Fuente: Ministerio del Interior. Votantes sobre censo de residentes en España. Cálculo propio. La barra clara es noviembre de 2019. Cataluña en conjunto: {p(CAT_TOT["2019_11"])} % y {p(CAT_TOT["2023_07"])} %; España: {p(PART["2019_11"]["part"])} % y {p(P23)} %.',
               [('Provincias catalanas', ACC), ('España', GRIS)],
               (['Territorio', 'Nov. 2019 (%)', '2023 (%)', 'Diferencia (puntos)'],
                [[r.nombre, p(r.p19), p(r.p23), s1(r.p23 - r.p19)] for r in CAT.itertuples()]))

g_votos = figura('Cuántos votantes hacen falta con el censo de 2026',
                 'Millones de votantes residentes en España',
                 barras([('Votaron en 2023', V23 / 1e6, GRIS, f'{mill(V23)} millones'), ('70 % del censo de 2026', V70 / 1e6, ACC, f'{mill(V70)} millones'),
                         ('75 % del censo de 2026', V75 / 1e6, ACC, f'{mill(V75)} millones')], 30,
                        'Votantes en 2023 y votantes necesarios para el 70 % y el 75 % en 2026', W=440, ml=150, separar=True),
                 'Fuente: Ministerio del Interior (2023); INE, censo electoral de residentes en España para el 29N (2026). Cálculo propio.',
                 [('2023', GRIS), ('Con el censo de 2026', ACC)],
                 (['', 'Votantes', 'Diferencia con 2023'],
                  [['Votaron en 2023', n(V23), '–'], ['70 % del censo de 2026', n(V70), '+' + n(MAS70)], ['75 % del censo de 2026', n(V75), '+' + n(MAS75)]]))


# Avances de participación (14 h y 18 h), residentes
av = pd.read_csv(RAIZ / 'data/censo/avances_participacion.csv', dtype={'mun_code': str})
AV = {}
for y, t in av.groupby('eleccion'):
    AV[y] = {'a14': t.a14.sum() / t.censo.sum() * 100, 'a18': t.a18.sum() / t.censo.sum() * 100, 'fin': t.votantes.sum() / t.censo.sum() * 100}
ANOS_AV = [y for y in ANOS if y in AV]
assert len(ANOS_AV) == 8 and abs(AV['2023_07']['fin'] - P23) < .05
A18_MIN = min(ANOS_AV, key=lambda y: AV[y]['a18'])
assert A18_MIN == '2016_06'


def avances(W_=440, ml=72):
    alto, H = 30, 30 * len(ANOS_AV) + 6
    x = lambda v: v / 85 * (W_ - ml - 44)
    tramos = (('a14', 'Hasta las 14 h', .35), ('a18', 'De 14 a 18 h', .65), ('fin', 'De 18 h al cierre', 1))
    out = [f'<svg viewBox="0 0 {W_} {H}" role="img" aria-label="Participación a las 14 h, a las 18 h y al cierre en cada elección">']
    for i, y in enumerate(ANOS_AV):
        yy = 4 + i * alto
        out.append(f'<text x="{ml - 8}" y="{yy + 16}" text-anchor="end" class="lab">{esc(NOMBRE[y])}</text>')
        x0, prev = ml, 0
        for k, nom, op in tramos:
            v = AV[y][k]
            out.append(f'<rect x="{x0:.1f}" y="{yy + 4}" width="{x(v - prev):.1f}" height="17" fill="{ACC}" fill-opacity="{op}"><title>{NOMBRE[y]}, {nom}: {p(v)} % acumulado</title></rect>')
            x0 += x(v - prev)
            prev = v
        out.append(f'<text x="{x0 + 5:.1f}" y="{yy + 17}">{p(AV[y]["fin"])} %</text>')
    out.append('</svg>')
    return ''.join(out)


g_av = figura('A las 18 h, en 2023 había votado el 53,1 %: el cierre lo cambió todo'.replace('53,1', p(AV['2023_07']['a18'])),
              'Participación acumulada de los residentes en España a las 14 h, a las 18 h y al cierre, en las generales desde 2004',
              avances(),
              'Fuente: Ministerio del Interior, avances de participación por municipio (vía pollspaindata). Sin voto exterior. Cálculo propio. El voto por correo se suma al final.',
              [('Hasta las 14 h', 'rgba(162,39,95,.35)'), ('De 14 a 18 h', 'rgba(162,39,95,.65)'), ('De 18 h al cierre', ACC)],
              (['Elección', 'A las 14 h (%)', 'A las 18 h (%)', 'Al cierre (%)'],
               [[NOMBRE[y], p(AV[y]['a14']), p(AV[y]['a18']), p(AV[y]['fin'])] for y in ANOS_AV]))

# Cambio por provincia entre noviembre de 2019 y 2023
g['dif'] = g.p23 - g.p19
CAMBIO = pd.concat([g.sort_values('dif', ascending=False).head(8), g[g.dif < 0].sort_values('dif', ascending=False)])
N_CAEN = int((g.dif < 0).sum())
assert N_CAEN == 52 - SUBEN
assert set(g[g.dif < 0].prov) == {'08', '17', '25', '43', '28', '41', '51', '52', '01', '20', '48'}
GAL = g[g.prov.isin(['15', '27', '32', '36'])]
GAL_TOT = {k: GAL[f'{k}_votantes'].sum() / GAL[f'{k}_censo'].sum() * 100 for k in ('2023_07', '2019_11')}
TOP_SUBE = g.sort_values('dif').iloc[-1]
assert (GAL.p23 > GAL.p19).all()
assert TOP_SUBE.nombre == 'Lugo'


def divergentes(W_=440, ml=120):
    alto, H = 22, 22 * len(CAMBIO) + 8
    k = (W_ - ml - 84) / 17.5
    c0 = ml + 42 + 9 * k
    out = [f'<svg viewBox="0 0 {W_} {H}" role="img" aria-label="Cambio de la participación entre noviembre de 2019 y 2023, por provincia">']
    for i, r in enumerate(CAMBIO.itertuples()):
        y = 4 + i * alto
        x1, x2 = sorted((c0, c0 + r.dif * k))
        col = ACC if r.dif > 0 else GRIS
        out.append(f'<text x="{ml - 8}" y="{y + 14}" text-anchor="end" class="lab">{esc(r.nombre)}</text>')
        out.append(f'<rect x="{x1:.1f}" y="{y + 3}" width="{max(1.5, x2 - x1):.1f}" height="14" fill="{col}" rx="2"><title>{esc(r.nombre)}: {s1(r.dif)} puntos</title></rect>')
        xt = c0 + r.dif * k + (5 if r.dif > 0 else -5)
        out.append(f'<text x="{xt:.1f}" y="{y + 14}"{" text-anchor=\"end\"" if r.dif < 0 else ""}>{s1(r.dif)}</text>')
    out.append(f'<line x1="{c0:.1f}" x2="{c0:.1f}" y1="0" y2="{H}" stroke="var(--fg)" stroke-width=".6"/></svg>')
    return ''.join(out)


g_dif = figura(f'Galicia votó más en 2023; Cataluña, menos',
               f'Diferencia en puntos de participación entre noviembre de 2019 y julio de 2023: las ocho provincias donde más subió y las {N_CAEN} donde bajó',
               divergentes(),
               'Fuente: Ministerio del Interior. Votantes sobre censo de residentes en España. Cálculo propio. Las 52 provincias, en la tabla del gráfico anterior.',
               [('Subió', ACC), ('Bajó', GRIS)],
               (['Provincia', 'Nov. 2019 (%)', '2023 (%)', 'Diferencia (puntos)'],
                [[esc(r.provincia), p(r.p19), p(r.p23), s1(r.dif)] for r in CAMBIO.itertuples()]))

# --- Texto ---
INFOBAE = 'https://www.infobae.com/espana/2026/11/09/elecciones-generales-29-n-en-directo-feijoo-confia-en-que-los-sindicatos-acepten-el-resultado-electoral-si-hay-cambio-de-gobierno/'
EP_ABA = 'https://www.europapress.es/nacional/noticia-abascal-aboga-regular-fondos-buitre-evitar-especulacion-vivienda-20261110000544.html'
EP_ABA2 = 'https://www.europapress.es/epsocial/migracion/noticia-abascal-defiende-termino-cazar-inmigrantes-fue-contexto-invasion-ceuta-roto-convivencia-20261110001207.html'
EP_SAN = 'https://www.europapress.es/nacional/noticia-sanchez-avanza-habra-consejos-ministros-extraordinarios-aprobar-medidas-sociales-antes-generales-20261110001609.html'
VERTELE = 'https://www.eldiario.es/vertele/noticias/pedro-sanchez-sera-entrevistado-javier-ruiz-septima-coincidiendo-visita-abascal-revuelta-rtve_1_13646145.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">El lunes por la noche, a la misma hora, Santiago Abascal se sentaba con David Broncano en La Revuelta, en La 1, y Pedro Sánchez respondía a Javier Ruiz en La Séptima, como había anunciado <a href="{VERTELE}">verTele</a>. Abascal habló de vivienda y de inmigración: según <a href="{EP_ABA}">Europa Press</a>, recalcó que el problema de la vivienda es la inmigración y la falta de construcción de inmuebles: «La oferta y la demanda no casan, no se construye y cada vez entra más gente». Sánchez anunció Consejos de Ministros extraordinarios para aprobar «medidas sociales» antes del 29N, según la <a href="{EP_SAN}">misma agencia</a>, y dio una cifra.</p>
<blockquote class="cita"><p>«De lejos va a superar el 70 % de participación que tuvimos en las elecciones de 2023 y, por tanto, al igual que ocurrió en Estados Unidos, en Brasil y también en España en 2023, volveremos a reeditar una mayoría de progreso en el Parlamento»</p><footer>Pedro Sánchez, en La Séptima, el 9 de noviembre de 2026, según el directo de <a href="{INFOBAE}">Infobae</a></footer></blockquote>
<p data-tipo="dato">El 70 % de 2023 es la participación de los electores que viven en España: votó el {p(P23)} % de ellos, {n(V23)} personas. Si se cuenta el voto exterior, que vota mucho menos, la participación oficial fue del 66,6 %. Con la primera cuenta, la de los residentes, el 70 % se superó en {len(SOBRE)} de las 16 generales desde 1977, y en 2000 se quedó justo en el 70,0 %. Las cuatro veces que no se llegó fueron 1979, 1989, junio de 2016 y noviembre de 2019, la última vez que hubo generales en noviembre: {p(PART["2019_11"]["part"])} %. El récord es de 1982, con el {p(PART["1982_10"]["part"])} %.</p>
{g_hist}
<p data-tipo="dato">En 2023, {52 - N_BAJO70} de las 52 provincias pasaron del 70 %. Las que más votaron fueron Segovia ({p(SEG.p23)} %), Cuenca y Ávila. Las {N_BAJO70} que no llegaron son Ceuta y Melilla, las dos canarias y Baleares, cuatro andaluzas (Cádiz, Huelva, Málaga y Almería), las tres vascas, Navarra y las cuatro catalanas. En Melilla votó el {p(MEL.p23)} %.</p>
{g_prov}
<p data-tipo="patron">Entre noviembre de 2019 y julio de 2023, la participación subió en {SUBEN} de las 52 provincias, pero cayó en las cuatro catalanas: en Barcelona, del {p(BCN.p19)} % al {p(BCN.p23)} %, y en Girona, del {p(GIR.p19)} % al {p(GIR.p23)} %. En el conjunto de Cataluña pasó del {p(CAT_TOT["2019_11"])} % al {p(CAT_TOT["2023_07"])} %. Barcelona es la segunda provincia con más electores, así que lo que pase allí pesa en la cifra de España.</p>
{g_cat}
<p data-tipo="patron">En el otro extremo está Galicia: sus cuatro provincias votaron más en 2023 que en noviembre de 2019, y en Lugo la participación subió {p(TOP_SUBE.dif)} puntos, la mayor subida de España. En el conjunto de Galicia pasó del {p(GAL_TOT["2019_11"])} % al {p(GAL_TOT["2023_07"])} %. En total, la participación bajó en {N_CAEN} provincias: las cuatro catalanas, Madrid, Sevilla, Ceuta, Melilla y las tres vascas.</p>
{g_dif}
<p data-tipo="dato">Los avances que da el Ministerio del Interior durante la jornada no anticipan bien el cierre. En 2023, a las 18 horas había votado el {p(AV["2023_07"]["a18"])} % de los residentes, menos que en noviembre de 2019 ({p(AV["2019_11"]["a18"])} %), y al final la participación fue mayor: {p(P23)} % frente a {p(PART["2019_11"]["part"])} %. Los avances no recogen el voto por correo, que la mesa mete en la urna cuando se cierra la votación, según el <a href="https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672#a88">artículo 88 de la ley electoral</a>. Por eso, la noche del 29N el dato de las 18 horas no bastará para saber si se pasa del 70 %.</p>
{g_av}
<p data-tipo="dato">El censo de residentes para el 29N es más grande que el de 2023: {n(CER26)} electores, según el <a href="https://www.ine.es/oficina_censo/elecgen2026/Elecgral_2026_cc_tab4.xlsx">INE</a>. Para llegar al 70 % harían falta {mill(V70)} millones de votantes, unos {n(round(MAS70, -3))} más que en 2023. Para el 75 %, {mill(V75)} millones: {mill(MAS75)} millones más.</p>
{g_votos}
<p data-tipo="hipotesis">Que suba la participación no dice por sí solo a quién beneficia. En 2023, en la quinta parte del censo de cada provincia que menos votó, el PSOE sacó más que el PP, y en la que más votó, al revés, como contamos en {L("a-quien-beneficia-abstencion-29n", "a quién beneficia la abstención")}. Pero quienes se quedan en casa no votarían necesariamente como sus vecinos, y las encuestas no permiten saber todavía cuánta gente irá a votar el 29N.</p>
<blockquote class="cita"><p>«Yo creo que el Estado tiene que intervenir cuando hay una práctica abusiva en el mercado»</p><footer>Santiago Abascal, sobre los fondos que compran vivienda, en La Revuelta, el 9 de noviembre de 2026, según <a href="{EP_ABA}">Europa Press</a></footer></blockquote>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">Las cifras son de electores residentes en España (CER), sin el voto exterior, que en 2023 bajó la participación oficial al 66,6 %. Una predicción de participación no es un dato: a 19 días de la votación, ninguna encuesta la mide bien. Ver también {L("votar-en-noviembre", "votar en noviembre")}, {L("sanchez-revuelta-broncano-voto-joven-29n", "Sánchez en La Revuelta")} y {L("a-quien-beneficia-abstencion-29n", "a quién beneficia la abstención")}.</p>'''

preguntas = [
    ('¿Cuál fue la participación en las generales de 2023?',
     f'El {p(P23)} % de los electores residentes en España; con el voto exterior, la participación oficial fue del 66,6 %.'),
    ('¿Cuántas veces se ha superado el 70 % de participación?',
     f'Contando a los residentes en España, en {len(SOBRE)} de las 16 generales desde 1977; en 2000 se quedó en el 70,0 %. El máximo fue en 1982, con el {p(PART["1982_10"]["part"])} %.'),
    ('¿Cuántos votantes hacen falta para el 70 % el 29N?',
     f'Con el censo de residentes de 2026 ({n(CER26)} electores), unos {mill(V70)} millones, {n(round(MAS70, -3))} más que en 2023.'),
]
enlaces = (f'{L("votar-en-noviembre", "Votar en noviembre")} · {L("a-quien-beneficia-abstencion-29n", "A quién beneficia la abstención")} · '
           f'{L("sanchez-revuelta-broncano-voto-joven-29n", "Sánchez en La Revuelta")} · <a href="{BASE}encuestas/">Encuestas del 29N</a>')
foot = ('Datos: Ministerio del Interior, generales de 1977 a 2023 por municipio (votantes y censo de residentes); INE, censo electoral '
        'de residentes en España para el 29N. Cálculo: actualidad/src/resumenes/participacion_70.py.')

DATOS = {'PART': PART, 'P23': P23, 'SOBRE': SOBRE, 'BAJO': BAJO, 'N_BAJO70': N_BAJO70, 'SUBEN': SUBEN, 'CAT_TOT': CAT_TOT,
         'CER26': CER26, 'V23': V23, 'V70': V70, 'V75': V75, 'MAS70': MAS70, 'MAS75': MAS75,
         'PROV': {r.nombre: [float(r.p19), float(r.p23)] for r in g.itertuples()}, 'AV': AV, 'GAL_TOT': GAL_TOT, 'N_CAEN': N_CAEN, 'N_CAMBIO_SUBE': 8}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza('sanchez-abascal-septima-revuelta-participacion-29n', 'Sánchez, La Séptima y el 70 %',
      f'Sánchez promete en La Séptima pasar «de lejos» del 70 % de participación: llegar al 75 % exigiría {mill(MAS75)} millones de votantes más que en 2023',
      f'A la misma hora en que Abascal estaba en La Revuelta, Sánchez pronosticó una participación muy por encima de la de 2023, cuando votó el {p(P23)} % de los residentes en España. '
      f'Con el censo de 2026, el 70 % son {mill(V70)} millones de votantes y el 75 %, {mill(V75)} millones. {N_BAJO70} provincias no llegaron al 70 % en 2023.',
      '10 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('P23', P23, 'SOBRE', len(SOBRE), 'BAJO70', N_BAJO70, 'SUBEN', SUBEN, 'CAT', CAT_TOT, 'CER26', CER26, 'MAS70', MAS70, 'MAS75', MAS75)
