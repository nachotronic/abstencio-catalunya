"""Debate a cuatro del 26-11-2026 (Sánchez, Feijóo, Abascal y Colau): hora, dónde verlo, turnos y peso de cada atril en 2023.

Pieza de servicio aprobada por Nacho el 26-11 («todas»). Título fijo desde la publicación; después del debate solo se
actualiza el contenido (audiencia, con actualización fechada).
Veda (LOREG 69.7): sin cifras de encuestas ni enlaces a piezas que las den.
Audiencias: tabla de Barlovento Comunicación (datos de Kantar), análisis del 19-7-2023: debates de generales entre los
candidatos de los partidos mayoritarios. Aquí, los que tuvieron tres o más candidatos.
Escaños y votos de 2023: actualidad/src/sistema/cifras.json (Interior, con CERA).
Uso, desde la raíz: python3 actualidad/src/resumenes/debate_cuatro.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import COL, p

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
SLUG = 'debate-a-cuatro-sanchez-feijoo-abascal-colau-29n'

MUNDIARIO = 'https://www.mundiario.com/politica/debate-cuatro-29-n-horarios-turnos-bloques-duelo-entre-sanchez-feijoo-abascal-colau/20261126081720455042.html'
ELDEBATE = 'https://www.eldebate.com/cine-tv-series/20261125/debate-4-abascal-izquierda-colau-derecha-sanchez-abrira-minuto-oro-feijoo-cerrara_485161.html'
INFOBAE = 'https://www.infobae.com/espana/2026/11/26/el-debate-a-cuatro-definitivo-en-directo-ultima-hora-de-las-elecciones-generales-29-n-y-la-campana-electoral/'
BARLOVENTO = 'https://barloventocomunicacion.es/wp-content/uploads/2023/07/Analisis-Audiencia-23J-EL-DEBATE-FINAL_19-julio-2023.pdf'
ESP26 = 'https://www.elespanol.com/espana/politica/20261120/cara-sanchez-feijoo-arrasa-parrilla-audiencia-media-espectadores/1003744465708_0.html'

BLOQUES = ['Vivienda', 'Economía y fiscalidad', 'Política social y servicios públicos',
           'Lucha contra la corrupción y regeneración democrática', 'Migración y política exterior']
CADENAS = ['La 1, el Canal 24 Horas y TVE Internacional, y en internet RTVE.es y RTVE Play', 'Antena 3', 'laSexta',
           'Telecinco', 'Cuatro', 'La Séptima',
           'Varias televisiones autonómicas, entre ellas RTVA, CMM, CARTV, CVMC, RTRM, IB3, RTPA y RTVM']

# Barlovento (Kantar): debates de generales con tres o más candidatos; audiencia media en miles y cuota en %
VARIOS = [('Sánchez, Iglesias, Sáenz de Santamaría y Rivera', '7-12-2015', 9233, 48.2),
          ('Rajoy, Sánchez, Iglesias y Rivera', '13-6-2016', 10496, 57.0),
          ('Sánchez, Casado, Iglesias y Rivera (1.º)', '22-4-2019', 8886, 43.8),
          ('Sánchez, Casado, Iglesias y Rivera (2.º)', '23-4-2019', 9477, 48.7),
          ('Sánchez, Casado, Iglesias, Rivera y Abascal', '4-11-2019', 8632, 52.7),
          ('Sánchez, Abascal y Díaz', '19-7-2023', 4155, 34.6)]
ULT = VARIOS[-1]
MAXV = max(VARIOS, key=lambda c: c[2])
assert MAXV[1] == '13-6-2016' and min(VARIOS, key=lambda c: c[2]) is ULT
CAIDA = round((1 - ULT[2] / MAXV[2]) * 100)
CARA26 = 10152  # cara a cara del 19-11-2026, Barlovento (Europa Press)

# Escaños y votos de 2023
C23 = json.load(open(RAIZ / 'actualidad/src/sistema/cifras.json'))['2023_07']
P23 = {x['partido']: x for x in C23['partidos']}
ATRIL = [('Sánchez', 'PSOE', 'PSOE'), ('Feijóo', 'PP', 'PP'), ('Abascal', 'Vox', 'VOX'), ('Colau', 'Sumar', 'SUMAR')]
ESC = {k: P23[k]['escanos'] for _, k, _ in ATRIL}
VOT = {k: P23[k]['votos'] for _, k, _ in ATRIL}
assert ESC == {'PSOE': 121, 'PP': 137, 'Vox': 33, 'Sumar': 31}
SUMA = sum(ESC.values())
VSUMA = sum(VOT.values())
VPCT = 100 * VSUMA / C23['validos']
DER = ESC['PP'] + ESC['Vox']
IZQ = ESC['PSOE'] + ESC['Sumar']
RESTO = 350 - SUMA
assert (SUMA, DER, IZQ, RESTO) == (322, 170, 152, 28)

g_esc = figura(f'Los cuatro partidos de los atriles sumaron {SUMA} de los 350 escaños en 2023',
               'Diputados que sacó en las elecciones generales de 2023 el partido de cada candidato del debate',
               barras([(f'{k} ({c})', ESC[k], COL[col], str(ESC[k])) for c, k, col in sorted(ATRIL, key=lambda a: -ESC[a[1]])],
                      150, 'Escaños de 2023 de los partidos del debate a cuatro', W=400, ml=150, fmt=str),
               'Fuente: Ministerio del Interior, elecciones generales del 23 de julio de 2023. En 2023, Sumar incluía a Podemos, que el 29N se presenta por separado del Frente Amplio de Colau.',
               None,
               (['Candidato', 'Partido en 2023', 'Votos', 'Escaños'],
                [[c, k, n(VOT[k]), str(ESC[k])] for c, k, _ in ATRIL]))

g_aud = figura(f'El último debate a varios, el de 2023, lo vieron {p(ULT[2] / 1000)} millones: el menos visto',
               'Audiencia media de los debates de las elecciones generales con tres o más candidatos a la presidencia, en millones de espectadores',
               barras([(c[1], c[2] / 1000, 'var(--muted)', p(c[2] / 1000)) for c in VARIOS], MAXV[2] / 1000 * 1.12,
                      'Audiencia de los debates de generales con tres o más candidatos desde 2015', W=400, ml=95, fmt=p),
               f'Fuente: <a href="{BARLOVENTO}">Barlovento Comunicación, con datos de Kantar</a>. Solo televisión.',
               None,
               (['Fecha', 'Candidatos', 'Espectadores (millones)', 'Cuota de pantalla (%)'],
                [[c[1], c[0], p(c[2] / 1000), p(c[3])] for c in VARIOS]))

lis = lambda xs: '<ul>' + ''.join(f'<li>{esc(x)}</li>' for x in xs) + '</ul>'
cuerpo = f'''
<h2>A qué hora es el debate a cuatro</h2>
<p data-tipo="contexto">El debate a cuatro de las elecciones generales del 29N es este jueves 26 de noviembre, a las <strong>22.00</strong>, y durará casi dos horas, hasta las 0.00 aproximadamente, según <a href="{ELDEBATE}">El Debate</a>. Participan Pedro Sánchez (PSOE), Alberto Núñez Feijóo (PP), Santiago Abascal (Vox) y Ada Colau (Frente Amplio). Lo organiza la Academia de Televisión y lo modera su presidenta, María Casado, según <a href="{MUNDIARIO}">Mundiario</a>.</p>
<p data-tipo="contexto">Es el último debate de la campaña, según <a href="{INFOBAE}">Infobae</a>. La campaña acaba el viernes 27 a medianoche, el sábado es la jornada de reflexión y el domingo se vota.</p>
<h2>Dónde ver el debate</h2>
<p data-tipo="contexto">La Academia da la señal a las cadenas que quieran emitirlo. Lo darán en directo, según <a href="{MUNDIARIO}">Mundiario</a>:</p>
{lis(CADENAS)}
<p data-tipo="contexto">También lo emitirá la cadena portuguesa CNN Portugal.</p>
<h2>En qué orden hablan</h2>
<p data-tipo="contexto">El sorteo decidió los atriles y los turnos. De izquierda a derecha, en pantalla, estarán Abascal, Sánchez, Feijóo y Colau. Abre Colau, con una valoración de la legislatura de un minuto y medio, y le siguen Sánchez, Feijóo y Abascal. En el minuto de oro final el orden cambia: empieza Sánchez, siguen Abascal y Colau, y cierra Feijóo, según <a href="{ELDEBATE}">El Debate</a> y <a href="{MUNDIARIO}">Mundiario</a>.</p>
<p data-tipo="contexto">El debate tiene cinco bloques de 20 minutos, con cinco minutos para cada candidato en cada uno, en este orden:</p>
{lis(BLOQUES)}
<p data-tipo="contexto">Habrá dos pausas publicitarias de tres minutos, después del segundo y del cuarto bloque. Los candidatos no pueden llevar dispositivos electrónicos, y los tiempos los controlan árbitros de la Federación Española de Baloncesto, según las dos mismas fuentes.</p>
<h2>Cuánto pesaba cada atril en 2023</h2>
<p data-tipo="dato">Los partidos de los cuatro candidatos sacaron <strong>{SUMA} de los 350 diputados</strong> en las elecciones generales de 2023, y {n(VSUMA)} votos, el {p(VPCT)} % de los válidos. El PP y Vox sumaron {DER}; el PSOE y Sumar, {IZQ}. Ninguno de los dos pares llegó a los 176 de la mayoría absoluta: los {RESTO} escaños restantes eran de ERC, Junts, EH Bildu, el PNV, el BNG, Coalición Canaria y UPN.</p>
{g_esc}
<p data-tipo="contexto">La comparación de Colau con Sumar es aproximada: en 2023 Sumar llevaba dentro a Podemos, que esta vez se presenta por su cuenta, fuera del Frente Amplio.</p>
<h2>Cuánta gente ve un debate a varios</h2>
<p data-tipo="dato">El último debate con más de dos candidatos a la presidencia, el de Sánchez, Abascal y Yolanda Díaz del 19 de julio de 2023, lo vieron de media <strong>{p(ULT[2] / 1000)} millones de personas</strong>, con un {p(ULT[3])} % de cuota: el menos visto de los seis desde 2015 y un {CAIDA} % menos que el de 2016, el que más audiencia tuvo, según los datos de Kantar que recopila <a href="{BARLOVENTO}">Barlovento Comunicación</a>.</p>
{g_aud}
<p data-tipo="contexto">El cara a cara entre Sánchez y Feijóo del jueves pasado lo vieron {p(CARA26 / 1000)} millones, según el informe de Barlovento que recoge <a href="{ESP26}">Europa Press</a>.</p>
'''

preguntas = [
    ('¿A qué hora es el debate a cuatro?',
     'El jueves 26 de noviembre de 2026, a las 22.00. Está previsto que acabe hacia las 0.00.'),
    ('¿Dónde se puede ver el debate a cuatro?',
     'En La 1, el Canal 24 Horas, Antena 3, laSexta, Telecinco, Cuatro y La Séptima, en varias televisiones autonómicas y en RTVE Play.'),
    ('¿Quién participa en el debate a cuatro?',
     'Pedro Sánchez (PSOE), Alberto Núñez Feijóo (PP), Santiago Abascal (Vox) y Ada Colau (Frente Amplio). Modera María Casado.'),
    ('¿Quién abre y quién cierra el debate?',
     'Abre Colau. En el minuto de oro final empieza Sánchez y cierra Feijóo.'),
    ('¿Cuántos escaños sacaron en 2023 los partidos del debate?',
     f'{SUMA} de 350: PP {ESC["PP"]}, PSOE {ESC["PSOE"]}, Vox {ESC["Vox"]} y Sumar {ESC["Sumar"]}, que entonces incluía a Podemos.'),
]
enlaces = (f'<a href="{BASE}elecciones/resultados-elecciones-generales-2026/">Resultados de las elecciones generales 2026</a> · '
           f'{L("despues-elecciones-generales-29n-investidura", "Qué pasa después del 29N")}')
foot = ('Datos: Barlovento Comunicación con datos de Kantar (audiencias hasta 2023) y su informe de 2026 (Europa Press); Ministerio del Interior (escaños y votos de 2023). '
        'Cálculo: actualidad/src/resumenes/debate_cuatro.py.')
DATOS = {'VARIOS': VARIOS, 'CAIDA': CAIDA, 'ESC': ESC, 'VOT': VOT, 'SUMA': SUMA, 'VPCT': VPCT, 'DER': DER, 'IZQ': IZQ, 'CARA26': CARA26}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'El debate a cuatro',
      'Debate a cuatro: hora, dónde verlo y en qué orden hablan Sánchez, Feijóo, Abascal y Colau',
      f'Es este jueves a las 22.00, en La 1, Antena 3, laSexta, Telecinco, Cuatro y La Séptima. El último debate a varios, en 2023, fue el menos visto desde 2015: {p(ULT[2] / 1000)} millones.',
      '26 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(SUMA, DER, IZQ, round(VPCT, 1), CAIDA)
