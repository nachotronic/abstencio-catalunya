"""Debate Sánchez Feijóo del 19-11-2026: hora, dónde verlo y quién gana el cara a cara (pieza de servicio).

Título fijo desde la publicación (plan de SEO, /mnt/project-files/audiencia/plan-debate-y-resultados.md): no se cambia
después del debate; solo se actualiza el contenido.
Audiencias de los cara a cara: tabla de Barlovento Comunicación (datos de Kantar), en su análisis del 19-7-2023, que recoge
los debates de generales con los candidatos de los partidos mayoritarios. Aquí, solo los cara a cara PSOE-PP (dos candidatos).
Encuestas de hoy: mediana de /encuestas/ (medianas() de encuestas/src/construir.py), no la media del modelo.
Uso, desde la raíz: python3 actualidad/src/resumenes/debate_servicio.py
"""
import importlib.util
import json
from datetime import date

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import COL, p

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
SLUG = 'debate-sanchez-feijoo-29n'
HOY = '2026-11-19'

FTV_ACADEMIA = 'https://www.formulatv.com/noticias/sanchez-feijoo-debate-19-noviembre-academia-tv-138759/'
FTV_CADENAS = 'https://www.formulatv.com/noticias/donde-ver-debate-pedro-sanchez-feijoo-2026-138774/'
PLURAL = 'https://www.elplural.com/politica/espana/todo-sabemos-cara-cara-entre-sanchez-feijoo-temas-tiempos-perspectivas_804551102'
INFOBAE = 'https://www.infobae.com/espana/2026/11/16/rtve-atresmedia-y-la-septima-emitiran-el-cara-a-cara-de-sanchez-y-feijoo-en-directo-donde-y-cuando-ver-el-debate-electoral/'
BARLOVENTO = 'https://barloventocomunicacion.es/wp-content/uploads/2023/07/Analisis-Audiencia-23J-EL-DEBATE-FINAL_19-julio-2023.pdf'
VOZ23 = 'https://www.vozpopuli.com/espana/elecciones-generales-2023/cara-a-cara-sanchez-catapulta-feijoo-sondeos.html'

BLOQUES = ['Vivienda', 'Economía y fiscalidad', 'Política social y servicios públicos',
           'Lucha contra la corrupción y regeneración democrática', 'Migración y política exterior']
CADENAS = ['La 1, con el Canal 24 Horas y TVE Internacional', 'Antena 3', 'Telecinco', 'Cuatro', 'laSexta', 'La Séptima']

# Barlovento (Kantar): cara a cara entre los candidatos del PSOE y del PP; audiencia media en miles y cuota en %
CARAS = [('Aznar-González', '24-5-1993', 9625, 61.8), ('Aznar-González', '31-5-1993', 10526, 75.3),
         ('Zapatero-Rajoy', '25-2-2008', 13043, 59.1), ('Zapatero-Rajoy', '3-3-2008', 11952, 56.3),
         ('Rubalcaba-Rajoy', '7-11-2011', 12005, 54.2), ('Sánchez-Rajoy', '14-12-2015', 9728, 48.7),
         ('Sánchez-Feijóo', '10-7-2023', 5911, 46.5)]
MIN = min(CARAS, key=lambda c: c[2])
MAX = max(CARAS, key=lambda c: c[2])
assert MIN[0] == 'Sánchez-Feijóo' and MAX[1] == '25-2-2008'
M23 = MIN[2] / 1000
MMAX = MAX[2] / 1000
CAIDA = MAX[2] / MIN[2]
assert 2 < CAIDA < 3  # «más del doble»

# Encuestas de 2023 sobre quién ganó el debate (Vozpópuli, con EFE)
NC_F, NC_S = 57, 39
SIGMA_F = 54.2

# Mediana de /encuestas/ hoy
_spec = importlib.util.spec_from_file_location('enc_construir', RAIZ / 'encuestas/src/construir.py')
enc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enc)
ENCS = enc.carga()
MED = {k: v for k, v in enc.medianas(ENCS, date.fromisoformat(HOY))[-1].items() if k != 'd'}
MED_DIF = round(MED['PP'] - MED['PSOE'], 1)

_anios = [c[1].rsplit('-', 1)[1] for c in CARAS]


def etq(c):
    a = c[1].rsplit('-', 1)[1]
    if _anios.count(a) == 1:
        return f'{c[0]} {a}'
    return f'{c[0]} {a} ({[x for x in CARAS if x[1].endswith(a)].index(c) + 1}.º)'


g_aud = figura(f'El último cara a cara, el de 2023, fue el menos visto: {p(M23)} millones de espectadores',
               'Audiencia media de los cara a cara entre los candidatos del PSOE y del PP en las elecciones generales, en millones de espectadores',
               barras([(etq(c), c[2] / 1000, 'var(--muted)', p(c[2] / 1000)) for c in CARAS], MMAX * 1.12,
                      'Audiencia de los cara a cara PSOE-PP desde 1993', W=400, ml=165, fmt=p),
               f'Fuente: <a href="{BARLOVENTO}">Barlovento Comunicación, con datos de Kantar</a>. Solo televisión. Sin los debates a cuatro o más.',
               None,
               (['Debate', 'Fecha', 'Espectadores (millones)', 'Cuota de pantalla (%)'],
                [[c[0], c[1], p(c[2] / 1000), p(c[3])] for c in CARAS]))

lis = lambda xs: '<ul>' + ''.join(f'<li>{esc(x)}</li>' for x in xs) + '</ul>'
cuerpo = f'''
<h2>A qué hora es el debate</h2>
<p data-tipo="contexto">El debate entre Pedro Sánchez y Alberto Núñez Feijóo de las elecciones generales del 29N es este jueves, 19 de noviembre, a las <strong>22.00</strong>, según <a href="{FTV_CADENAS}">FormulaTV</a>. Durará unas dos horas y está previsto que acabe hacia la medianoche, con dos pausas publicitarias de tres minutos, según <a href="{PLURAL}">El Plural</a>. Lo organiza la Academia de Televisión y lo modera su presidenta, María Casado, en el plató A de Madrid Content City, en Tres Cantos (Madrid).</p>
<p data-tipo="contexto">Feijóo abrirá el debate y Sánchez lo cerrará, según el sorteo que hicieron los dos partidos, informó <a href="{FTV_ACADEMIA}">FormulaTV</a>. Quedarán diez días para votar.</p>
<h2>Dónde ver el debate</h2>
<p data-tipo="contexto">La Academia reparte la señal para que la emita cualquier cadena. Lo darán en directo, según <a href="{FTV_CADENAS}">FormulaTV</a> y la información de EFE que recoge <a href="{INFOBAE}">Infobae</a>:</p>
{lis(CADENAS)}
<h2>De qué van a hablar</h2>
<p data-tipo="contexto">El debate tiene cinco bloques, en este orden. Son grandes temas, no una lista cerrada de preguntas, según <a href="{PLURAL}">El Plural</a>:</p>
{lis(BLOQUES)}
<h2>Cuánta gente ve un cara a cara</h2>
<p data-tipo="dato">El último cara a cara entre los candidatos del PSOE y del PP, el de Sánchez y Feijóo del 10 de julio de 2023, lo vieron de media <strong>{p(M23)} millones de personas</strong>: el menos visto de los siete celebrados desde 1993. El más visto fue el primero entre Zapatero y Rajoy, el 25 de febrero de 2008, con {p(MMAX)} millones, más del doble que el de 2023, según los datos de Kantar que recopila <a href="{BARLOVENTO}">Barlovento Comunicación</a>.</p>
{g_aud}
<h2>Quién gana el debate</h2>
<p data-tipo="contexto">En 2023, las encuestas publicadas tras el debate dieron ganador a Feijóo. Para NC Report y La Razón, el {NC_F} % de los encuestados le vio ganador, frente al {NC_S} % que eligió a Sánchez; en la de Sigma Dos para El Mundo, el {p(SIGMA_F)} % creía que Feijóo se impuso. 40dB. para El País y la SER no vio un ganador claro, según recogió <a href="{VOZ23}">Vozpópuli con información de EFE</a>.</p>
<p data-tipo="contexto">Ganar el debate no fue ganar por mucho: tras aquel cara a cara, {L("encuestas-tras-el-debate-2023-29n", "las encuestas ampliaron la ventaja del PP")}, pero las urnas se la dejaron en 1,4 puntos.</p>
<p data-tipo="dato">Hoy, antes del debate, la mediana de las encuestas de <a href="{BASE}encuestas/">las elecciones generales</a> da al PP {p(MED['PP'])} % y al PSOE {p(MED['PSOE'])} %: <strong>{p(MED_DIF)} puntos</strong> de diferencia.</p>
'''

preguntas = [
    ('¿A qué hora es el debate entre Sánchez y Feijóo?',
     'Este jueves, 19 de noviembre, a las 22.00. Está previsto que acabe hacia la medianoche.'),
    ('¿Dónde se puede ver el debate?',
     'En La 1 (y el Canal 24 Horas y TVE Internacional), Antena 3, Telecinco, Cuatro, laSexta y La Séptima, con la señal de la Academia de Televisión.'),
    ('¿Quién modera el debate?',
     'María Casado, presidenta de la Academia de Televisión, que organiza el cara a cara.'),
    ('¿Quién ganó el debate de 2023?',
     f'Las encuestas publicadas después dieron ganador a Feijóo: el {NC_F} % frente al {NC_S} % en la de NC Report para La Razón. El PP ganó las elecciones por 1,4 puntos.'),
]
enlaces = f'{L("encuestas-tras-el-debate-2023-29n", "Encuestas y debate")} · <a href="{BASE}encuestas/">Las encuestas de las elecciones generales del 29N</a>'
foot = ('Datos: Barlovento Comunicación con datos de Kantar (audiencias); mediana de las encuestas de mapaelectoral.es/encuestas. '
        'Cálculo: actualidad/src/resumenes/debate_servicio.py.')
DATOS = {'M23': M23, 'MMAX': MMAX, 'CAIDA': CAIDA, 'MED': MED, 'MED_DIF': MED_DIF, 'NC_F': NC_F, 'NC_S': NC_S, 'SIGMA_F': SIGMA_F,
         'CARAS': CARAS}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'Debate Sánchez Feijóo',
      'Debate Sánchez Feijóo: hora, dónde verlo y quién gana el cara a cara',
      f'Es este jueves a las 22.00, en La 1, Antena 3, Telecinco, Cuatro, laSexta y La Séptima. El último, en 2023, fue el menos visto desde 1993: {p(M23)} millones.',
      '19 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(MED, MED_DIF, round(CAIDA, 1))
