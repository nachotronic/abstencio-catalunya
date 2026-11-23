"""Elecciones generales del 29N en cifras: electores, escaños, candidaturas y mesas de cada provincia (pieza de servicio del 23-11-2026).

- Electores: INE, Oficina del Censo Electoral, censo por municipio para el 29N (data/censo/censo_municipios_2023_2026.csv). Los totales
  coinciden con la guía de Interior en La Moncloa (6-11-2026), de la que salen también los primerizos (1.615.127), los 209 senadores
  elegidos en las urnas y la fecha de las Cortes.
- Escaños por provincia: Real Decreto 806/2026 de convocatoria (BOE del 6-10-2026), en generales-2026/data/meta.json.
- Candidaturas al Congreso: las proclamadas (BOE del 3-11-2026), tal como las da Interior para los medios
  (generales-2026/data/candidatos-congreso-29n.json, de generales-2026/src/candidatos_directo.py).
- Mesas: las de las generales de 2023, de los ficheros por mesa de Interior (data/censo/mesas_congreso_2023.csv). Las del 29N no
  se conocen aún por provincia.
Uso, desde la raíz: python3 actualidad/src/resumenes/cifras_29n.py
"""
import json

import pandas as pd

from comun import BASE, POP_ESTILO, POP_JS, RAIZ, barras, esc, figura, mapa_provincias, n, pieza

SLUG = 'elecciones-generales-29n-cifras'
A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
GUIA = 'https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/interior/paginas/guia-dudas-elecciones-generales-29n.aspx'
RD = 'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742'
BOE_CAND = 'https://www.boe.es/boe/dias/2026/11/03/pdfs/BOE-A-2026-23103.pdf'
INFOEL = 'https://infoelectoral.interior.gob.es/'
CENSO = f'{BASE}elecciones/censo-electoral-2026/'
E29 = f'{BASE}elecciones/elecciones-29n-2026/'

# ---------- Datos ----------
C = pd.read_csv(RAIZ / 'data/censo/censo_municipios_2023_2026.csv', dtype={'mun_code': str})
C['prov'] = C.mun_code.str[:2]
MS = pd.read_csv(RAIZ / 'data/censo/mesas_congreso_2023.csv', dtype={'mun_code': str})
MS['prov'] = MS.mun_code.str.zfill(5).str[:2]
NOMP = (pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str}, usecols=['mun_code', 'provincia'])
        .assign(prov=lambda d: d.mun_code.str[:2]).drop_duplicates('prov').set_index('prov').provincia.str.split('/').str[0].replace({'Araba': 'Álava'}).to_dict())
ESC = json.load(open(RAIZ / 'generales-2026/data/meta.json'))['escanos']
CAND = json.load(open(RAIZ / 'generales-2026/data/candidatos-congreso-29n.json'))

G = C.groupby('prov')[['cer_2026', 'cera_2026', 'cer_2023', 'cera_2023']].sum()
G['electores'] = G.cer_2026 + G.cera_2026
G['electores23'] = G.cer_2023 + G.cera_2023
G['esc'] = pd.Series(ESC['2026_11'])
G['esc23'] = pd.Series(ESC['2023_07'])
G['cand'] = pd.Series({k: len(v) for k, v in CAND.items()})
G['mesas23'] = MS.groupby('prov').mesas.sum()
G['nombre'] = pd.Series(NOMP)
G['por_esc'] = G.electores / G.esc
G = G.reset_index()
assert len(G) == 52 and G.notna().all().all(), G[G.isna().any(axis=1)]

ELEC, RESID, FUERA = int(G.electores.sum()), int(G.cer_2026.sum()), int(G.cera_2026.sum())
assert (ELEC, RESID, FUERA) == (38728356, 35958711, 2769645)           # guía de Interior
ELEC23 = int(G.electores23.sum())
SUBE = ELEC - ELEC23
PRIMER = 1615127                                                           # guía de Interior
assert G.esc.sum() == 350 and G.esc23.sum() == 350
CAMBIA = G[G.esc != G.esc23]
assert sorted(zip(CAMBIA.nombre, CAMBIA.esc - CAMBIA.esc23)) == [('Cádiz', -1), ('Madrid', 1)]
MAD, CAD = (G[G.prov == k].iloc[0] for k in ('28', '11'))
NCAND = int(G.cand.sum())
assert NCAND == 534
CMAX = G[G.cand == G.cand.max()].nombre.tolist()
CMIN = G[G.cand == G.cand.min()].iloc[0]
assert sorted(CMAX) == ['Las Palmas', 'Madrid', 'Álava'] and (CMIN.nombre, CMIN.cand) == ('Melilla', 5), (CMAX, CMIN.nombre)
MESAS23 = int(G.mesas23.sum())
assert MESAS23 == 60314
SECC23 = int(MS.secciones.sum())
PEN = G[~G.prov.isin(['51', '52'])]
CARO, BARATO = PEN.loc[PEN.por_esc.idxmax()], PEN.loc[PEN.por_esc.idxmin()]
assert (CARO.nombre, BARATO.nombre) == ('Madrid', 'Teruel'), (CARO.nombre, BARATO.nombre)
RAT = CARO.por_esc / BARATO.por_esc
MEDIA = ELEC / 350
SENADO = 209
assert G.loc[G.electores.idxmax()].nombre == 'Madrid' and PEN.loc[PEN.electores.idxmin()].nombre == 'Soria'
assert G.cera_2026.sum() / G.cera_2023.sum() > G.cer_2026.sum() / G.cer_2023.sum()

# ---------- Gráficos ----------
ACC = 'var(--acc)'
G = G.sort_values('por_esc', ascending=False).reset_index(drop=True)
g_esc = figura(f'En Madrid hacen falta {p(RAT)} veces más electores por diputado que en Teruel',
               'Electores (residentes en España y en el extranjero) por cada diputado que elige la provincia el 29N. Las 10 provincias con más y las 10 con menos',
               barras([(r.nombre, r.por_esc / 1000, ACC, f'{n(round(r.por_esc, -3))}') for r in pd.concat([G.head(10), G[~G.prov.isin(['51', '52'])].tail(10)]).itertuples()],
                      140, 'Electores por diputado en cada provincia', W=400, ml=130, alto=22),
               f'Fuente: INE, censo electoral para el 29N; escaños, <a href="{RD}">Real Decreto 806/2026</a>. Cálculo propio. Ceuta y Melilla, que eligen un diputado cada una, no están en el gráfico: {n(round(G[G.prov == "51"].iloc[0].por_esc, -3))} y {n(round(G[G.prov == "52"].iloc[0].por_esc, -3))} electores.',
               None,
               (['Provincia', 'Electores', 'Diputados', 'Electores por diputado', 'Candidaturas al Congreso', 'Mesas en 2023'],
                [[esc(r.nombre), n(r.electores), str(r.esc), n(round(r.por_esc)), str(r.cand), n(r.mesas23)] for r in G.sort_values('electores', ascending=False).itertuples()]))
TR = [(0, 4, .3, 'Menos de 4 diputados'), (4, 6, .5, 'De 4 a 5'), (6, 10, .75, 'De 6 a 9'), (10, 99, 1, '10 o más')]
op = {r.prov: next(o for a, b, o, _ in TR if a <= r.esc < b) for r in G.itertuples()}
g_mapa = figura('Los diputados que elige cada provincia el 29N',
                'Toca o pasa el ratón por una provincia para ver sus electores, sus diputados, sus candidaturas al Congreso y sus mesas',
                '<div data-pop="prov">' + mapa_provincias({r.prov: ACC for r in G.itertuples()}, {}, 'Diputados por provincia', op, claves=True) + '</div>',
                f'Fuente: <a href="{RD}">Real Decreto 806/2026</a>; INE; candidaturas proclamadas (<a href="{BOE_CAND}">BOE del 3 de noviembre</a>); mesas de 2023, Ministerio del Interior.',
                [(t, f'color-mix(in srgb, {ACC} {round(o * 100)}%, transparent)') for _, _, o, t in TR])
POP = {r.prov: (f'<b>{esc(r.nombre)}</b><br>Electores: {n(r.electores)}<br>Diputados: {r.esc}'
                + (f' ({"+" if r.esc > r.esc23 else "−"}1 frente a 2023)' if r.esc != r.esc23 else '')
                + f'<br>Electores por diputado: {n(round(r.por_esc, -2))}<br>Candidaturas al Congreso: {r.cand}<br>Mesas en 2023: {n(r.mesas23)}') for r in G.itertuples()}

cuerpo = f'''
<p data-tipo="dato">El domingo 29 de noviembre pueden votar en las elecciones generales {n(ELEC)} personas: {n(RESID)} viven en España y {n(FUERA)}, en el extranjero. Son {n(SUBE)} más que en julio de 2023. De los residentes en España, {n(PRIMER)} votarán por primera vez en unas generales, porque han cumplido 18 años desde entonces, según la <a href="{GUIA}">guía de Interior para el 29N</a>. Eligen 350 diputados y {SENADO} senadores; el resto del Senado lo designan los parlamentos autonómicos.</p>
<h2>Electores</h2>
<p data-tipo="dato">Madrid es la provincia con más electores, {n(MAD.electores)}, y Soria la que menos entre las provincias, {n(G[G.nombre == "Soria"].iloc[0].electores)}. El censo de cada provincia, municipio a municipio, está en <a href="{CENSO}">el censo electoral de 2026</a>. El de los que viven fuera ha crecido más que el de los residentes: es una de las claves del escrutinio, como se cuenta en {L("escrutinio-elecciones-generales-29n", "la pieza sobre el escrutinio")}.</p>
<h2>Escaños</h2>
<p data-tipo="dato">Cada provincia elige al menos dos diputados, Ceuta y Melilla uno cada una, y los 248 restantes se reparten según la población. Para el 29N, el <a href="{RD}">decreto de convocatoria</a> da un diputado más a Madrid, que pasa a {MAD.esc}, y uno menos a Cádiz, que se queda en {CAD.esc}. El resto, igual que en 2023.</p>
<p data-tipo="dato">Como el mínimo es igual para todas, el voto no pesa lo mismo en todas partes. Contando también a los que viven fuera, en Madrid hay {n(round(CARO.por_esc, -3))} electores por cada diputado; en Teruel, {n(round(BARATO.por_esc, -3))}: {p(RAT)} veces menos. La media de España es de {n(round(MEDIA, -3))}. Cuánto cuesta un escaño a cada partido, en <a href="{BASE}elecciones/como-se-vota/">cómo se vota</a>.</p>
{g_esc}
{g_mapa}
<h2>Candidaturas</h2>
<p data-tipo="dato">Se presentan {NCAND} candidaturas al Congreso en las 52 circunscripciones, las que proclamaron las juntas electorales en el <a href="{BOE_CAND}">BOE del 3 de noviembre</a>. Álava, Las Palmas y Madrid son las que más tienen, {int(G.cand.max())} cada una; Melilla, la que menos, {CMIN.cand}. Quién va en cada lista, provincia a provincia, en <a href="{BASE}listas-electorales-29n/">las listas del 29N</a>.</p>
<h2>Mesas</h2>
<p data-tipo="dato">En las generales de julio de 2023 hubo {n(MESAS23)} mesas electorales en {n(SECC23)} secciones censales, según los ficheros por mesa de Interior. Cada mesa tiene un presidente y dos vocales elegidos por sorteo entre los vecinos de la sección. Las del 29N se sortearon entre el 31 de octubre y el 4 de noviembre; qué hacer si te ha tocado, en {L("me-ha-tocado-mesa-electoral-29n", "la pieza sobre las mesas")}.</p>
<h2>Fechas</h2>
<p data-tipo="contexto">Los colegios abren a las 9.00 y cierran a las 20.00 del domingo 29. El escrutinio definitivo es del 4 al 7 de diciembre y las nuevas Cortes se constituyen el miércoles 23 de diciembre a las 10.00, según la <a href="{GUIA}">guía de Interior</a>. Cómo votar y qué llevar, en {L("como-votar-elecciones-generales-29n", "la guía para votar el 29N")}.</p>
'''

preguntas = [
    ('¿Cuántos electores hay en las elecciones generales del 29N?',
     f'{n(ELEC)}: {n(RESID)} residentes en España y {n(FUERA)} en el extranjero, según el INE y la <a href="{GUIA}">guía de Interior</a>.'),
    ('¿Cuántos diputados y senadores se eligen el 29N?',
     f'350 diputados y {SENADO} senadores. Los parlamentos autonómicos designan después a otros senadores, uno por comunidad y otro por cada millón de habitantes.'),
    ('¿Qué provincias ganan o pierden escaños el 29N?',
     f'Madrid gana uno y pasa a {MAD.esc}; Cádiz pierde uno y se queda en {CAD.esc} (<a href="{RD}">Real Decreto 806/2026</a>).'),
    ('¿Cuántas candidaturas se presentan al Congreso?',
     f'{NCAND} en las 52 circunscripciones, según las candidaturas proclamadas en el <a href="{BOE_CAND}">BOE del 3 de noviembre</a>.'),
    ('¿Cuántas mesas electorales hay?',
     f'En las generales de 2023 hubo {n(MESAS23)}. Interior no ha dado aún la cifra del 29N por provincia.'),
]
enlaces = (f'<a href="{E29}">Elecciones 29N 2026</a> · <a href="{CENSO}">Censo electoral 2026</a> · {L("escrutinio-elecciones-generales-29n", "Escrutinio del 29N")} · '
           f'{L("como-votar-elecciones-generales-29n", "Cómo votar el 29N")}')
foot = ('Datos: INE, censo electoral por municipio para el 29N y para 2023; Real Decreto 806/2026 de convocatoria; candidaturas proclamadas (BOE del 3-11-2026); '
        'Ministerio del Interior, mesas de las generales de 2023 y guía de las elecciones del 29N. Cálculo: cifras_29n.py, en actualidad/src/resumenes.')

DATOS = {'ELEC': ELEC, 'RESID': RESID, 'FUERA': FUERA, 'ELEC23': ELEC23, 'SUBE': SUBE, 'NCAND': NCAND, 'MESAS23': MESAS23, 'SECC23': SECC23,
         'RAT': round(RAT, 3), 'MEDIA': round(MEDIA), 'SENADO': SENADO, 'PRIMER': PRIMER,
         'PROV': [{'prov': r.prov, 'nombre': r.nombre, 'electores': int(r.electores), 'esc': int(r.esc), 'esc23': int(r.esc23), 'cand': int(r.cand),
                   'mesas23': int(r.mesas23), 'por_esc': round(r.por_esc)} for r in G.itertuples()],
         'POP': {'prov': POP}}
datos_js = POP_ESTILO + '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';' + POP_JS + '</script>\n'

TITULO = 'Elecciones generales del 29N en cifras: electores, escaños, candidaturas y mesas de cada provincia'
DEK = (f'Pueden votar {n(ELEC)} personas, {n(SUBE)} más que en 2023. Madrid gana un diputado y Cádiz lo pierde. '
       f'En Madrid hacen falta {p(RAT)} veces más electores por escaño que en Teruel.')
pieza(SLUG, 'El 29N en cifras', TITULO, DEK, '23 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(TITULO); print(DEK); print(G[['nombre', 'electores', 'esc', 'por_esc', 'cand', 'mesas23']].head(6).to_string())
