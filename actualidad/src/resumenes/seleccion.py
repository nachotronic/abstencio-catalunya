"""Domingo 15-11-2026, España-Inglaterra en el Metropolitano: cómo votan los municipios donde nacieron los 27 convocados.

Convocatoria: RFEF, 6-11-2026 (27 jugadores). Lugar de nacimiento: ficha de cada jugador en rfef.es (selecciones/jugadores),
contrastada con una segunda fuente (Wikipedia en español, la ficha de su club o la prensa). Votos: generales de noviembre de 2019
y julio de 2023 por municipio (generales-2026/descargas/municipios.csv, Ministerio del Interior), votos brutos por candidatura.
Uso, desde la raíz: python3 actualidad/src/resumenes/seleccion.py
"""
import json

import pandas as pd

from comun import BASE, COLOR, figura, n, pieza, RAIZ, barras

A = BASE + 'actualidad/'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
RFEF = 'https://rfef.es/es/selecciones/jugadores/'

# (jugador, posición, ficha RFEF, municipio INE, ruta de la ficha municipal, nombre corto del municipio)
J = [('Unai Simón', 'portero', 'unai-simon-absoluta', '01063', 'alava/zuia', 'Zuia (Murgia)'),
     ('David Raya', 'portero', 'david-raya-0', '08019', 'barcelona/barcelona', 'Barcelona'),
     ('Joan Garcia', 'portero', 'joan-garcia-absoluta', '08191', 'barcelona/sallent', 'Sallent'),
     ('Álvaro Valles', 'portero', 'alvaro-valles-absoluta', '41081', 'sevilla/la-rinconada', 'La Rinconada'),
     ('Pedro Porro', 'defensa', 'pedro-porro-sauceda', '06044', 'badajoz/don-benito', 'Don Benito'),
     ('Pau Cubarsí', 'defensa', 'pau-cubarsi-ficha-absoluta', '17020', 'girona/bescano', 'Bescanó (Estanyol)'),
     ('Marc Pubill', 'defensa', 'marc-pubill-absoluta', '08279', 'barcelona/terrassa', 'Terrassa'),
     ('Jacobo Ramón', 'defensa', 'jacobo-ramon-absoluta', '28079', 'madrid/madrid', 'Madrid'),
     ('Marc Cucurella', 'defensa', 'marc-cucurella-ficha-absoluta', '08003', 'barcelona/alella', 'Alella'),
     ('Alejandro Grimaldo', 'defensa', 'alejandro-grimaldo-ficha-absoluta', '46250', 'valencia/valencia', 'València'),
     ('Martín Zubimendi', 'centrocampista', 'martin-zubimendi', '20069', 'gipuzkoa/donostia-san-sebastian', 'Donostia'),
     ('Pedri', 'centrocampista', 'pedri-sub-21', '38046', 'santa-cruz-de-tenerife/tegueste', 'Tegueste'),
     ('Fabián Ruiz', 'centrocampista', 'fabian-ruiz-nueva-ficha-absoluta', '41069', 'sevilla/los-palacios-y-villafranca', 'Los Palacios y Villafranca'),
     ('Mikel Merino', 'centrocampista', 'mikel-merino-ficha-absoluta', '31201', 'navarra/pamplona-iruna', 'Pamplona'),
     ('Fermín López', 'centrocampista', 'fermin-lopez-ficha-absoluta', '21018', 'huelva/el-campillo', 'El Campillo'),
     ('Álex Baena', 'centrocampista', 'alex-baena-absoluta', '04079', 'almeria/roquetas-de-mar', 'Roquetas de Mar'),
     ('Pablo Barrios', 'centrocampista', 'pablo-barrios-ficha-absoluta', '28079', 'madrid/madrid', 'Madrid'),
     ('Marc Roca', 'centrocampista', 'marc-roca-absoluta', '08305', 'barcelona/vilafranca-del-penedes', 'Vilafranca del Penedès'),
     ('Mikel Oyarzabal', 'delantero', 'mikel-oyarzabal', '20030', 'gipuzkoa/eibar', 'Eibar'),
     ('Lamine Yamal', 'delantero', 'lamine-yamal-absoluta', '08077', 'barcelona/esplugues-de-llobregat', 'Esplugues de Llobregat'),
     ('Ferran Torres', 'delantero', 'ferran-torres-garcia-ficha-absoluta', '46126', 'valencia/foios', 'Foios'),
     ('Roberto Fernández', 'delantero', 'roberto-fernandez-ficha-absoluta', '14056', 'cordoba/puente-genil', 'Puente Genil'),
     ('Ander Barrenetxea', 'delantero', 'ander-barrenetxea-absoluta', '20069', 'gipuzkoa/donostia-san-sebastian', 'Donostia'),
     ('Nico Williams', 'delantero', 'nico-williams-absoluta', '31201', 'navarra/pamplona-iruna', 'Pamplona'),
     ('Yeremy Pino', 'delantero', 'yeremy-pino', '35016', 'las-palmas/las-palmas-de-gran-canaria', 'Las Palmas de Gran Canaria')]
FUERA = [('Aymeric Laporte', 'Agen (Francia)', 'aymeric-laporte-0'), ('Dean Huijsen', 'Ámsterdam (Países Bajos)', 'dean-huijsen-absoluta')]
assert len(J) + len(FUERA) == 27
BARRENETXEA = 'https://www.realsociedad.eus/es/team/player/real-sociedad/ander-barrenetxea-muguruza'

NOMBRE = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'SUMAR': 'Sumar', 'ERC': 'ERC', 'JUNTS': 'Junts', 'PNV': 'PNV', 'BILDU': 'EH Bildu'}
COL = {'PP': COLOR['PP'], 'PSOE': COLOR['PSOE'], 'VOX': COLOR['Vox'], 'ERC': COLOR['ERC'], 'JUNTS': COLOR['Junts'], 'PNV': COLOR['PNV'],
       'BILDU': COLOR['EH Bildu'], 'SUMAR': COLOR['Sumar']}

m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str}).set_index('mun_code')
r4 = lambda v: round(float(v), 4)


def eleccion(cod, e):
    """Votos de cada candidatura en el municipio (columnas de votos brutos), ordenados de más a menos."""
    cols = [c for c in m.columns if c.startswith(e + '_v') and c != e + '_votantes']
    v = m.loc[cod, cols].astype(float)
    v.index = [c[len(e) + 2:] for c in v.index]
    return v.sort_values(ascending=False), float(v.sum())


MUN = {}
for _, _, _, cod, ruta, corto in J:
    if cod in MUN:
        continue
    fila = {'nombre': corto, 'ruta': ruta}
    for e, k in (('2019_11', 'n19'), ('2023_07', 'j23')):
        v, tot = eleccion(cod, e)
        fila[k] = dict(gana=v.index[0], segundo=v.index[1], v1=int(v.iloc[0]), v2=int(v.iloc[1]), dif=int(v.iloc[0] - v.iloc[1]),
                       pts=r4(100 * (v.iloc[0] - v.iloc[1]) / tot), pct1=r4(100 * v.iloc[0] / tot),
                       PP=r4(100 * v.get('PP', 0) / tot), PSOE=r4(100 * v.get('PSOE', 0) / tot), VOX=r4(100 * v.get('VOX', 0) / tot))
    MUN[cod] = fila
assert len(MUN) == 22
# En noviembre de 2019, en Pamplona, la candidatura de la familia PP era Navarra Suma (UPN, PP y Ciudadanos)
assert MUN['31201']['n19']['gana'] == 'PP'
nom19 = lambda cod: 'Navarra Suma' if cod == '31201' else NOMBRE[MUN[cod]['n19']['gana']]

g23 = lambda cod: MUN[cod]['j23']['gana']
POR_JUG = {p: sum(g23(c) == p for _, _, _, c, _, _ in J) for p in ('PSOE', 'PP', 'JUNTS', 'BILDU')}
POR_MUN = {p: sum(g23(c) == p for c in MUN) for p in ('PSOE', 'PP', 'JUNTS', 'BILDU')}
CAMBIAN = [c for c in MUN if MUN[c]['n19']['gana'] != g23(c)]
assert (POR_JUG['PSOE'], POR_JUG['PP'], POR_MUN['PSOE'], POR_MUN['PP'], len(CAMBIAN)) == (15, 8, 13, 7, 14)
assert sum(POR_JUG.values()) == 25 and sum(POR_MUN.values()) == 22
PERDIDOS = {}
for c in CAMBIAN:
    PERDIDOS.setdefault(nom19(c), []).append(c)
assert {k: len(v) for k, v in PERDIDOS.items()} == {'PNV': 3, 'ERC': 4, 'PSOE': 5, 'Navarra Suma': 1, 'Vox': 1}

M = lambda cod, t=None: f'<a href="{BASE}municipio/{MUN[cod]["ruta"]}/">{t or MUN[cod]["nombre"]}</a>'
dif = lambda cod: MUN[cod]['j23']['dif']
pts = lambda cod, k='j23': n(MUN[cod][k]['pts'], 1)
pc = lambda cod, p, k='j23': n(MUN[cod][k][p], 1)

# Gráfico 1: un jugador por fila, ganador de 2023 en su municipio y su ventaja en puntos
CORTOJ = {'Álvaro Valles': 'Valles', 'Lamine Yamal': 'Lamine', 'Marc Pubill': 'Pubill', 'Marc Roca': 'Roca', 'David Raya': 'Raya',
          'Joan Garcia': 'Joan Garcia', 'Mikel Oyarzabal': 'Oyarzabal', 'Marc Cucurella': 'Cucurella', 'Mikel Merino': 'Merino',
          'Nico Williams': 'Nico Williams', 'Yeremy Pino': 'Yeremy Pino', 'Martín Zubimendi': 'Zubimendi', 'Ander Barrenetxea': 'Barrenetxea',
          'Ferran Torres': 'Ferran Torres', 'Álex Baena': 'Baena', 'Jacobo Ramón': 'Jacobo Ramón', 'Pablo Barrios': 'Barrios',
          'Fabián Ruiz': 'Fabián', 'Alejandro Grimaldo': 'Grimaldo', 'Pedri': 'Pedri', 'Pedro Porro': 'Porro', 'Roberto Fernández': 'R. Fernández',
          'Pau Cubarsí': 'Cubarsí', 'Unai Simón': 'Unai Simón', 'Fermín López': 'Fermín'}
CORTOM = {'08077': 'Esplugues', '08305': 'Vilafranca', '35016': 'Las Palmas', '41069': 'Los Palacios', '17020': 'Bescanó', '01063': 'Zuia', '41081': 'La Rinconada'}
assert set(CORTOJ) == {r[0] for r in J}
filas = [(f'{CORTOJ[j]} · {CORTOM.get(c, MUN[c]["nombre"])}', MUN[c]['j23']['pts'], COL[g23(c)], f'{NOMBRE[g23(c)]} +{pts(c)}')
         for j, _, _, c, _, _ in sorted(J, key=lambda r: (['PSOE', 'PP', 'JUNTS', 'BILDU'].index(g23(r[3])), -MUN[r[3]]['j23']['pts']))]
g_jug = figura(f'{POR_JUG["PSOE"]} convocados nacieron donde ganó el PSOE en 2023; {POR_JUG["PP"]}, donde ganó el PP',
               'Partido más votado en las generales de julio de 2023 en el municipio de nacimiento de cada convocado nacido en España, y su ventaja en puntos sobre el segundo',
               barras(filas, 30, 'Ganador de 2023 en el municipio de cada convocado', W=420, ml=200, separar=True),
               f'Fuente: Ministerio del Interior, generales de julio de 2023, votos por municipio; lugar de nacimiento, <a href="{RFEF}lamine-yamal-absoluta">fichas de la RFEF</a>. Ventaja sobre el total de votos a candidaturas.',
               [(NOMBRE[p], COL[p]) for p in ('PSOE', 'PP', 'JUNTS', 'BILDU')],
               (['Convocado', 'Municipio', 'Ganador 2019 (nov.)', 'Ganador 2023', 'Ventaja 2023 (votos)'],
                [[j, MUN[c]['nombre'], nom19(c), NOMBRE[g23(c)], n(dif(c))] for j, _, _, c, _, _ in J]))

# Gráfico 2: municipios por ganador, noviembre de 2019 y julio de 2023
ORD = ['PSOE', 'PP', 'Navarra Suma', 'ERC', 'PNV', 'Junts', 'EH Bildu', 'Vox']
cuenta = lambda k: {o: sum((nom19(c) if k == 'n19' else NOMBRE[g23(c)]) == o for c in MUN) for o in ORD}
C19, C23 = cuenta('n19'), cuenta('j23')
COLN = {'PSOE': COL['PSOE'], 'PP': COL['PP'], 'Navarra Suma': COL['PP'], 'ERC': COL['ERC'], 'PNV': COL['PNV'], 'Junts': COL['JUNTS'],
        'EH Bildu': COL['BILDU'], 'Vox': COL['VOX']}
from comun import pares  # noqa: E402
g_mun = figura(f'{len(CAMBIAN)} de los {len(MUN)} municipios cambiaron de ganador entre 2019 y 2023',
               'Municipios de nacimiento de los convocados en los que fue más votado cada partido, en noviembre de 2019 (barra clara) y en julio de 2023',
               pares([(o, C19[o], C23[o], COLN[o]) for o in ORD], 14, 'Municipios por ganador en 2019 y 2023', ['nov. 2019', '2023'], W=420, ml=110),
               'Fuente: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023, votos por municipio. En Pamplona, en 2019, Navarra Suma era la lista conjunta de UPN, PP y Ciudadanos.',
               None,
               (['Partido', 'Noviembre de 2019', 'Julio de 2023'], [[o, str(C19[o]), str(C23[o])] for o in ORD]))

RFEF_LISTA = 'https://rfef.es/es/noticias/esta-es-la-lista-para-cerrar-la-fase-de-grupos-de-la-uefa-nations-lague'
DEBATE_GRIMALDO = 'https://www.eldebate.com/espana/comunidad-valenciana/20260801/restaurante-valencia-visitado-campeon-mundial-2026_446024.html'
FCB_PEDRI = 'https://www.fcbarcelona.es/es/futbol/primer-equipo/jugadores/70486/pedro-gonzalez'
WIKI_PEDRI = 'https://es.wikipedia.org/wiki/Pedri'
WIKI_ROCA = 'https://es.wikipedia.org/wiki/Marc_Roca'
LALIGA_SIMON = 'https://www.laliga.com/jugador/unai-simon'

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">España recibe esta noche a Inglaterra en el Metropolitano, a las 20.45, en el último partido de la fase de grupos de la Liga de Naciones. Luis de la Fuente <a href="{RFEF_LISTA}">convocó a 27 jugadores</a> el 6 de noviembre. Dos nacieron fuera de España: Aymeric Laporte, en Agen (Francia), y Dean Huijsen, en Ámsterdam. Los otros {len(J)} nacieron en {len(MUN)} municipios españoles, según la ficha de cada uno en la web de la RFEF. Esta pieza mira cómo votaron esos {len(MUN)} municipios en las dos últimas elecciones generales.</p>

<h2>Quince del PSOE, ocho del PP</h2>
<p data-tipo="dato">En las generales de julio de 2023, el PSOE fue el más votado en {POR_MUN['PSOE']} de los {len(MUN)} municipios, y el PP, en {POR_MUN['PP']}. Contados por jugadores, {POR_JUG['PSOE']} convocados nacieron en un municipio donde ganó el PSOE y {POR_JUG['PP']} en uno donde ganó el PP. Quedan dos: Pau Cubarsí nació en Estanyol, un pueblo de {M('17020', 'Bescanó')} donde ganó Junts, y Unai Simón, en Murgia, del municipio alavés de {M('01063', 'Zuia')}, donde ganó EH Bildu.</p>
{g_jug}
<p data-tipo="dato">El resultado más amplio es el de {M('21018')}, el pueblo onubense de Fermín López, con unos 2.000 habitantes: el PSOE sacó el {pc('21018', 'PSOE')} % y el PP, el {pc('21018', 'PP')} %. En {M('41081')}, la de Álvaro Valles, el PSOE le sacó {pts('41081')} puntos al PP. Del lado del PP, la mayor ventaja está en {M('04079')}, donde nació Álex Baena: {pts('04079')} puntos, con el {pc('04079', 'PP')} % de los votos. En {M('28079')}, donde nacieron Jacobo Ramón y Pablo Barrios, el PP sacó el {pc('28079', 'PP')} %.</p>

<h2>Cinco pueblos decididos por menos de 110 votos</h2>
<p data-tipo="dato">El más ajustado es {M('14056')}, en Córdoba, el de Roberto Fernández: el PP ganó por {n(dif('14056'))} votos, {n(MUN['14056']['j23']['v1'])} frente a {n(MUN['14056']['j23']['v2'])} del PSOE. En {M('06044')}, donde nació Pedro Porro, el PP ganó por {n(dif('06044'))}. En {M('46126')}, el pueblo de Ferran Torres, fue al revés: el PSOE ganó al PP por {n(dif('46126'))}. Y en {M('38046')}, el de Pedri, el PP ganó por {n(dif('38046'))} votos un año en que Vox no presentó lista al Congreso en Santa Cruz de Tenerife, como contamos en {L('vox-vuelve-tenerife-29n', 'la pieza sobre su vuelta')}.</p>
<p data-tipo="dato">En Zuia, el municipio de Unai Simón, EH Bildu le ganó al PNV por {n(dif('01063'))} votos: {n(MUN['01063']['j23']['v1'])} frente a {n(MUN['01063']['j23']['v2'])}.</p>

<h2>Catorce de veintidós cambiaron de ganador</h2>
<p data-tipo="dato">En noviembre de 2019, el reparto era otro. De los {len(MUN)} municipios, {len(CAMBIAN)} tuvieron un ganador distinto en 2023. ERC perdió los cuatro catalanes que había ganado: {M('08019')}, {M('08191')}, {M('08003')} y {M('08305')}, que pasaron al PSC. El PNV perdió {M('20069')} y {M('20030')}, que fueron al PSOE, y Zuia, que fue a EH Bildu. El PSOE perdió cinco a manos del PP: {M('06044')}, {M('46250')}, {M('38046')}, {M('41069')} y {M('14056')}. {M('31201')} pasó de Navarra Suma al PSOE, y {M('04079')}, donde Vox había sido el más votado en 2019, con el {pc('04079', 'VOX', 'n19')} %, al PP.</p>
{g_mun}
<p data-tipo="dato">Es el mismo movimiento que contamos en la serie {L('mapa-electoral-cataluna-29n', '«El mapa electoral de…»')}: en Cataluña, ERC pasó de ganar en 619 municipios a ganar en 159, y en el {L('mapa-electoral-pais-vasco-29n', 'País Vasco')}, el PNV bajó en 246 de los 251.</p>

<h2>Dónde nacieron y dónde crecieron</h2>
<p data-tipo="contexto">El lugar de nacimiento no siempre es el pueblo del jugador, y las fuentes no siempre coinciden. Esta pieza usa el de la ficha de la RFEF. La RFEF da València para Alejandro Grimaldo, que es natural de La Pobla de Vallbona, según <a href="{DEBATE_GRIMALDO}">El Debate</a>; allí también ganó el PP en 2023. Para Marc Roca, la RFEF da Vilafranca del Penedès y <a href="{WIKI_ROCA}">Wikipedia</a>, La Granada, el pueblo de al lado; en los dos ganó el PSC. La RFEF y la <a href="{FCB_PEDRI}">ficha del Barça</a> dan Tegueste para Pedri, y la ficha de <a href="{WIKI_PEDRI}">Wikipedia</a> también, aunque su biografía dice que nació en Bajamar, en La Laguna, donde ganó el PSOE. Para Unai Simón, la RFEF da Murgia y <a href="{LALIGA_SIMON}">LaLiga</a>, Vitoria, donde también ganó el PSOE. Para Ander Barrenetxea, la ficha de la RFEF y la de <a href="{BARRENETXEA}">la Real Sociedad</a> coinciden: Donostia.</p>
<p data-tipo="contexto">Nada de esto dice a quién votan los jugadores ni sus familias. Es el mapa de los sitios de donde salen: muchos se fueron de niños a las canteras, y cada municipio vota por razones que no tienen que ver con el fútbol.</p>

<h2>El 29N</h2>
<p data-tipo="contexto">Dentro de dos semanas, el 29 de noviembre, esos {len(MUN)} municipios vuelven a votar. La ficha de cada uno, con sus resultados desde 2004, está enlazada en esta pieza, y la <a href="{BASE}encuestas/">página de encuestas</a> recoge lo que dicen las encuestas cada día.</p>
'''

preguntas = [
    ('¿Dónde nacieron los convocados de España para el partido contra Inglaterra?', f'De los 27 convocados por De la Fuente, {len(J)} nacieron en {len(MUN)} municipios españoles, según la RFEF; Laporte nació en Agen (Francia) y Huijsen, en Ámsterdam.'),
    ('¿Quién ganó las elecciones en los pueblos de los jugadores de la selección?', f'En las generales de 2023, el PSOE ganó en {POR_MUN["PSOE"]} de esos {len(MUN)} municipios y el PP, en {POR_MUN["PP"]}; Junts ganó en Bescanó y EH Bildu en Zuia.'),
    ('¿Cuál fue el pueblo más ajustado?', f'Puente Genil (Córdoba), donde nació Roberto Fernández: el PP ganó por {n(dif("14056"))} votos al PSOE en 2023.'),
]
enlaces = (f'{L("atletico-barca-metropolitano-camp-nou-29n", "El Atlético-Barça en las urnas")} · {L("vox-vuelve-tenerife-29n", "Vox vuelve en Tenerife")} · '
           f'{L("dos-semanas-29n-la-semana-en-el-mapa", "A dos semanas del 29N")} · <a href="{BASE}encuestas/">Encuestas del 29N</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023, votos por municipio (descarga de Mapa Electoral); '
        'convocatoria de la RFEF del 6 de noviembre de 2026 y lugar de nacimiento de la ficha de cada jugador en rfef.es. '
        'Porcentajes sobre el total de votos a candidaturas. Cálculo: actualidad/src/resumenes/seleccion.py.')

TIT = (f'De los {len(J)} convocados de De la Fuente nacidos en España, {POR_JUG["PSOE"]} nacieron donde ganó el PSOE en 2023 y {POR_JUG["PP"]} donde ganó el PP; '
       f'en Puente Genil, el PP ganó por {n(dif("14056"))} votos')
DEK = (f'España recibe a Inglaterra en el Metropolitano. Los pueblos de sus convocados votan como el mapa: {len(CAMBIAN)} de los {len(MUN)} cambiaron de ganador '
       'entre 2019 y 2023, ERC perdió los cuatro municipios catalanes que había ganado y el PNV, los tres vascos.')

D = {'J': [[j, c] for j, _, _, c, _, _ in J], 'FUERA': [f[0] for f in FUERA], 'MUN': MUN, 'POR_JUG': POR_JUG, 'POR_MUN': POR_MUN, 'CAMBIAN': CAMBIAN}
datos_js = '<script>const D=' + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
if __name__ == '__main__':
    print(TIT)
    pieza('seleccion-convocados-pueblos-29n', 'Los pueblos de los convocados', TIT, DEK, '15 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, datos_js)
