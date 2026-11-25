"""Encuestas Andorra 29N: qué son las encuestas prohibidas y qué dice la ley (pieza de servicio del 23-11-2026).

Sin cifras de ninguna encuesta y sin enlaces a encuestas publicadas durante la veda: se publica dentro de ella.
- Ley: LOREG, art. 69.7, 145 y 153.2, texto consolidado del BOE (literal).
- Búsquedas: Google Trends, España, 10 a 25 de julio de 2023, «encuestas andorra», «encuestas prohibidas» y «veda electoral» en la
  misma consulta (índice 0-100 relativo al máximo de las tres), en datos/trends_encuestas_andorra_2023.csv, descargado el 23-11-2026.
- Andorra y Australia: Diario de León / El Periódico (20-12-2015), La Marea (15-12-2015), GESOP (25-7-2023), Diari Més (7-5-2024),
  las mismas fuentes que la pieza de la veda.
- Encuestas encubiertas: El Debate (1-4-2022), resolución de la Junta Electoral Central sobre los «Emojipanel» de Electomanía.
Uso, desde la raíz: python3 actualidad/src/resumenes/encuestas_andorra_29n.py
"""
import json
import pathlib

import pandas as pd

from comun import BASE, barras, figura, n, pieza

AQUI = pathlib.Path(__file__).resolve().parent
SLUG = 'encuestas-andorra-29n'
A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
LOREG = 'https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672'
L69, L145, L153 = LOREG + '#asesentaynueve', LOREG + '#acientocuarentaycinco', LOREG + '#acientocincuentaytres'
LEON = 'https://www.diariodeleon.es/nacional/151219/579930/encuesta-prohibida-elecciones-generales-penultimo-sondeo.html'
MAREA = 'https://www.lamarea.com/?p=79733'
GESOP = 'https://gesop.net/es/2023/07/25/el-sondeo-de-gesop-del-23j-de-los-mas-acertados/'
MES = 'https://www.diarimes.com/es/actualidad/cataluna/240507/primer-sondeo-prohibido-diario-andorra-12-m-votos-escanos_144339.html'
ESTRELLA = 'https://www.estrelladigital.es/espana/cinco-dias-encuestas-que-prohibe-ley-hoy-que-pueden-hacer-medios-donde-seguira-viendo-voto/20261124113128453841.html'
INDAILY = 'https://www.indailysa.com.au/news/archive/2023/07/21/the-adelaide-review-used-to-skirt-spanish-electoral-laws'
CRONICA = 'https://cronicaglobal.elespanol.com/culemania/palco/20190419/oficial-moll-prensa-iberica-el-periodico-sport/392210791_0.html'
DIARI24 = 'https://www.diariandorra.ad/nacional/261124/eleccions-espanya-amb-afluencia-record_209473.html'
DEBATE = 'https://www.eldebate.com/espana/20220401/jec-insiste-sancionar-difusion-sondeos-electorales-encubiertos-fuera-plazo-legal.html'
TRENDS = 'https://trends.google.es/trends/explore?date=2023-07-10%202023-07-25&geo=ES&q=encuestas%20andorra,encuestas%20prohibidas,veda%20electoral'

# ---------- Datos ----------
T = pd.read_csv(AQUI / 'datos/trends_encuestas_andorra_2023.csv', parse_dates=['date']).set_index('date')
AND, PRO = T['encuestas andorra'], T['encuestas prohibidas']
VEDA = T.loc['2023-07-18':'2023-07-22']
assert AND.loc[:'2023-07-17'].sum() == 0 and AND.loc['2023-07-24':].sum() == 0      # nada antes ni después
assert AND.idxmax() == pd.Timestamp('2023-07-22') and AND.max() == 100              # máximo el sábado, jornada de reflexión
RATIO = VEDA['encuestas andorra'].sum() / VEDA['encuestas prohibidas'].sum()
assert RATIO > 3
assert T['veda electoral'].loc['2023-07-18':'2023-07-23'].sum() == 0

DIAS = ['lun', 'mar', 'mié', 'jue', 'vie', 'sáb', 'dom']
filas = [(f'{DIAS[d.weekday()]} {d.day} jul', v, 'var(--acc)', str(v)) for d, v in AND.loc['2023-07-16':'2023-07-24'].items()]
g_tr = figura('En 2023, «encuestas andorra» solo se buscó la semana de la veda',
              'Interés de búsqueda en Google de «encuestas andorra» en España, del 16 al 24 de julio de 2023 (100 = el día con más búsquedas). La veda fue del 18 al 22; las elecciones, el 23',
              barras(filas, 110, 'Búsquedas de encuestas andorra en julio de 2023', W=380, ml=90, alto=22),
              f'Fuente: <a href="{TRENDS}">Google Trends</a>, consulta conjunta de «encuestas andorra», «encuestas prohibidas» y «veda electoral». El índice es relativo, no un número de búsquedas.',
              None,
              (['Día', '«encuestas andorra»', '«encuestas prohibidas»'], [[f'{d.day} de julio de 2023', str(AND[d]), str(PRO[d])] for d in T.index]))

cuerpo = f'''
<p data-tipo="contexto">Las «encuestas de Andorra» son encuestas de las elecciones españolas publicadas por medios de fuera de España durante la veda, los cinco días antes de votar en los que la ley lo prohíbe aquí. Las más conocidas son las de El Periòdic d'Andorra (en castellano, El Periódico de Andorra), que publicó sondeos así en varias elecciones. Para el 29N, la veda empieza el martes 24 de noviembre y dura hasta que cierren los colegios el domingo 29. En mapaelectoral.es no publicamos ninguna encuesta durante la veda, tampoco las de fuera, ni enlazamos a ellas. El domingo, a las 20.00, cuando cierren los colegios de la Península, daremos el sondeo a pie de urna de las televisiones, citando quién lo hace.</p>
<h2>Qué dice la ley</h2>
<p data-tipo="dato">«Durante los cinco días anteriores al de la votación queda prohibida la publicación y difusión o reproducción de sondeos electorales por cualquier medio de comunicación» (<a href="{L69}">artículo 69.7 de la LOREG</a>). Las infracciones en materia de encuestas se castigan con multa «de 3.000 a 30.000 de euros» (<a href="{L153}">artículo 153</a>), y el <a href="{L145}">artículo 145</a> castiga como delito, con «prisión de tres meses a un año», a «quienes infrinjan la normativa vigente en materia de encuestas electorales». La ley prohíbe publicarlas, difundirlas y reproducirlas; no prohíbe hacerlas, y los partidos siguen encargando las suyas. Cómo se aplica al 29N, día a día, en {L("veda-encuestas-29n", "la pieza sobre la veda de encuestas")}.</p>
<h2>De Andorra a Australia</h2>
<p data-tipo="contexto">La ley española no alcanza a los medios de otros países. El Periòdic d'Andorra publicó durante la veda una encuesta diaria del Gabinet d'Estudis Socials i Opinió Pública (GESOP) en las generales de 2008, en las catalanas de 2010, en las municipales de Barcelona de 2015 y en las generales de diciembre de 2015, según El Periódico, en un texto reproducido por <a href="{LEON}">Diario de León</a>, y <a href="{MAREA}">La Marea</a>. En 2023, el destino fue Australia: GESOP cuenta que su sondeo del sábado 22 de julio se publicó «en el portal web australiano The Adelaide Review el mismo día de las elecciones» (<a href="{GESOP}">GESOP</a>). En las autonómicas catalanas de 2024 volvió a Andorra, con una encuesta diaria del Diari d'Andorra, según el <a href="{MES}">Diari Més</a>.</p>
<p data-tipo="dato">Aunque en 2023 la encuesta saliera en Australia, en España se siguió buscando «encuestas andorra». Según <a href="{TRENDS}">Google Trends</a>, esa búsqueda no existió antes del martes 18 de julio, el primer día de veda. Fue creciendo cada día hasta su máximo el sábado 22, la jornada de reflexión, y desapareció el lunes después de las elecciones. Durante la veda se buscó unas {n(RATIO, 1)} veces más que «encuestas prohibidas».</p>
{g_tr}
<h2>Qué se ha publicado fuera esta semana</h2>
<p data-tipo="dato">Actualización del 24 de noviembre, a las 18.45. Para el 29N, el portal australiano The Adelaide Review prevé publicar durante la veda «una actualización diaria» de estimaciones electorales «elaborada a partir de estudios de GESOP», según <a href="{ESTRELLA}">Estrella Digital</a>. En mapaelectoral.es no las reproducimos ni las enlazamos; contaremos aquí cada día, hasta el sábado, qué se publica fuera, sin cifras. En Andorra, lo que cuenta el <a href="{DIARI24}">Diari d'Andorra</a> es que el consulado de España en Andorra recibe «una mitjana d'uns 800 votants diaris, el doble de l'habitual», y que la previsión es doblar la participación de 2023. Las urnas del consulado están abiertas hasta el jueves 26.</p>
<p data-tipo="dato">Actualización del 24 de noviembre, a las 22.30. The Adelaide Review no es un medio cualquiera: es propiedad del editor barcelonés Javier Moll, según el diario australiano <a href="{INDAILY}">InDaily</a>, que añade que El Periódico «is part of the stable of Prensa Ibérica, a publishing company owned by Moll». GESOP, la empresa de sus estimaciones, es la que hace las encuestas de El Periódico (<a href="{GESOP}">GESOP</a>). Prensa Ibérica compró El Periódico al Grupo Zeta en 2019, según <a href="{CRONICA}">Crónica Global</a>.</p>
<p data-tipo="dato">Actualización del 25 de noviembre, a las 8.45. The Adelaide Review actualizará su sondeo «cada 24 horas, desde el martes 24 hasta el sábado 28, jornada de reflexión», con «entre 300 y 400» entrevistas telefónicas nuevas cada día «hasta llegar a las 3.000», según El Correo Gallego, que cita a La Nueva España. No enlazamos esas noticias porque enlazan al portal australiano.</p>
<h2>Las encuestas encubiertas</h2>
<p data-tipo="dato">La Junta Electoral Central también ha actuado contra encuestas disfrazadas. En las autonómicas de Castilla y León de 2022, abrió expediente por los «Emojipanel» de Electomanía, publicados en la recta final con productos gastronómicos en lugar de partidos. La Junta escribió que «con estas prácticas se intenta eludir la prohibición» del artículo 69.7, según <a href="{DEBATE}">El Debate</a>. Para la Junta, que no apareciera el nombre de los partidos no cambiaba nada, porque «quién viese esos paneles de manera sencilla podría asociar su resultado con la intención de voto de cada formación política».</p>
<p data-tipo="contexto">Las encuestas publicadas hasta el lunes 23 siguen en <a href="{BASE}encuestas/">la página de encuestas de las elecciones generales 2026</a>, que no añade ninguna durante la veda. Desde las 21.00 del domingo, cuando cierren los últimos colegios, en Canarias, el mapa irá mostrando el recuento: {L("a-que-hora-resultados-elecciones-generales-29n", "a qué hora llegan los resultados")}.</p>
'''

preguntas = [
    ('¿Qué son las encuestas de Andorra?',
     'Encuestas de las elecciones españolas publicadas durante la veda por medios de fuera de España, a los que no alcanza la ley española. Las más conocidas son las de El Periòdic d\'Andorra, que las publicó en varias elecciones desde 2008.'),
    ('¿Cuándo empieza la veda de encuestas del 29N?',
     f'El martes 24 de noviembre. La ley prohíbe publicar, difundir o reproducir encuestas electorales en España los cinco días anteriores a la votación (<a href="{L69}">artículo 69.7 de la LOREG</a>), y el domingo tampoco se publican hasta que cierran los colegios. En mapaelectoral.es no publicamos ninguna durante la veda; el domingo, a las 20.00, daremos el sondeo a pie de urna de las televisiones.'),
    ('¿Qué multa hay por publicar encuestas prohibidas?',
     f'De 3.000 a 30.000 euros (<a href="{L153}">artículo 153</a>). El <a href="{L145}">artículo 145</a> castiga además como delito, con prisión de tres meses a un año, infringir la normativa de encuestas.'),
    ('¿Se pueden hacer encuestas durante la veda?',
     'Sí. Lo que la ley prohíbe es publicarlas, difundirlas o reproducirlas, no hacerlas.'),
]
enlaces = (f'{L("veda-encuestas-29n", "Veda de encuestas del 29N")} · <a href="{BASE}encuestas/">Encuestas elecciones generales 2026</a> · '
           f'{L("a-que-hora-resultados-elecciones-generales-29n", "A qué hora salen los resultados")}')
foot = ('Datos: LOREG (artículos 69, 145 y 153), BOE; Google Trends, búsquedas en España de julio de 2023; Diario de León, La Marea, GESOP, Diari Més y El Debate. '
        'Sin cifras de ninguna encuesta. Cálculo: encuestas_andorra_29n.py, en actualidad/src/resumenes.')

DATOS = {'RATIO': round(RATIO, 3), 'AND': {d.strftime('%Y-%m-%d'): int(v) for d, v in AND.items()}, 'PRO': {d.strftime('%Y-%m-%d'): int(v) for d, v in PRO.items()}}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

TITULO = 'Encuestas Andorra 29N: qué son las encuestas prohibidas y qué dice la ley'
DEK = ('Son encuestas publicadas fuera de España durante la veda, que va del martes 24 hasta que cierren los colegios el domingo 29. En 2023, «encuestas andorra» solo se buscó la semana de la veda, '
       'con el máximo en la jornada de reflexión.')
pieza(SLUG, 'Encuestas de Andorra', TITULO, DEK, '23 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(TITULO); print(DEK); print(RATIO)
