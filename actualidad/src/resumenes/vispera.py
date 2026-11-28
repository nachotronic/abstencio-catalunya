"""Crónica del sábado 28-11-2026, jornada de reflexión: «La víspera del 29N», la semana del 22 al 28 de noviembre desde los mapas.

Cada cifra sale de una pieza o página ya publicada y enlazada, donde se explica el cálculo. Los dos gráficos leen sus datos de
esas páginas (el voto útil de las 52 provincias y los pueblos que siempre aciertan), para que no se separen de ellas.
Sin cifras de encuestas: rige la veda (LOREG 69.7) hasta que cierren los colegios el domingo 29.
Uso, desde la raíz: python3 actualidad/src/resumenes/vispera.py
"""
import html as _html
import json
import re

from comun import BASE, COLOR, RAIZ, barras, figura, n, pieza

A = BASE + 'actualidad/'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
p = lambda v: n(v, 1)


def texto(ruta):
    s = open(RAIZ / ruta / 'index.html').read()
    s = s[s.find('<main'):] if '<main' in s else s
    return re.sub(r'\s+', ' ', _html.unescape(re.sub(r'<[^>]+>', ' ', s)))


# Voto útil: los escaños más ajustados de 2023 con el reparto de 2026 (elecciones/voto-util-29n/)
VU = texto('elecciones/voto-util-29n')
_m = re.search(r'Con los votos de las generales de 2023 y el reparto de 2026, (\d+) de los 350 escaños se habrían perdido si su partido hubiera perdido menos del 10 % de sus votos\. '
               r'Los más ajustados: (.*?)\.', VU)
N_JUEGO = int(_m.group(1))
ORD = {'primero': '1.º', 'segundo': '2.º', 'tercero': '3.º', 'cuarto': '4.º', 'quinto': '5.º', 'sexto': '6.º', 'séptimo': '7.º', 'octavo': '8.º'}
AJ = [(ORD[o], partido, prov, float(pct.replace(',', '.')))
      for o, partido, prov, pct in re.findall(r'el (\w+) del? (Vox|PP|PSOE|Sumar|Junts|ERC|PNV|EH Bildu|BNG|CC|UPN) en ([^(;]+?) \((\d+,\d) %\)', _m.group(2))]
assert N_JUEGO == 37 and len(AJ) == 8, (N_JUEGO, AJ)
assert AJ[0] == ('1.º', 'Vox', 'Cantabria', 0.3) and AJ[2] == ('5.º', 'PP', 'Málaga', 1.0)
COLP = {'Vox': COLOR['Vox'], 'PP': COLOR['PP'], 'PSOE': COLOR['PSOE'], 'Sumar': COLOR['Sumar'], 'Junts': COLOR['Junts'], 'ERC': COLOR['ERC'],
        'PNV': COLOR['PNV'], 'EH Bildu': COLOR['EH Bildu'], 'BNG': COLOR['BNG'], 'CC': COLOR['CC']}

# Pueblos que siempre aciertan: ventaja del PP en 2023 en los seis más ajustados
PQ = texto('actualidad/pueblos-que-siempre-aciertan-29n')
_m = re.search(r'En seis de los 24, la ventaja del PP sobre el PSOE en 2023 fue de menos de tres puntos: (.*?)\. En el conjunto de España, sin el voto exterior, fue de (\d,\d) puntos', PQ)
PUEB = [(nom.strip(), float(v.replace(',', '.'))) for nom, v in re.findall(r'([A-ZÁÉÍÓÚ][^,(]*?)(?:, en [^(]+)? \((\d,\d)\)', _m.group(1))]
ESP_DIF = float(_m.group(2).replace(',', '.'))
assert [x for x, _ in PUEB] == ['Ayerbe', 'Jaca', 'Los Navalmorales', 'Biescas', 'Villaquilambre', 'Plasencia'], PUEB
assert PUEB[0][1] == 0.3 and PUEB[-1][1] == 2.9 and ESP_DIF == 1.4

# Cifras del censo y del calendario, comprobadas contra su pieza
CIF = texto('actualidad/elecciones-generales-29n-cifras')
for frase in ('pueden votar en las elecciones generales 38.728.356 personas', '1.261.924 más que en julio de 2023', '1.615.127 votarán por primera vez',
              'Se presentan 534 candidaturas al Congreso'):
    assert frase in CIF, frase
assert 'son 2.769.645 electores' in texto('actualidad/voto-exterior-cera-loreg-29n').lower() or '2.769.645 electores' in texto('actualidad/voto-exterior-cera-loreg-29n')
assert 'el miércoles 23 de diciembre a las 10.00' in texto('actualidad/despues-elecciones-generales-29n-investidura')
VER = texto('actualidad/verificacion-debate-a-cuatro-datos-29n')
assert 'De las cinco, solo una es exacta' in VER and '22.852.600 ocupados' in VER
assert 'solo 24 han votado siempre' in PQ and 'el PP ganó en Ayerbe (Huesca) por 2 votos' in PQ

g_aj = figura(f'{N_JUEGO} escaños de 2023 cambiaban de manos con menos de un 10 % de votos; estos son los ocho más ajustados',
              'Porcentaje de sus votos que habría tenido que perder cada partido para quedarse sin ese escaño, con los votos de 2023 y el reparto de 2026',
              barras([(f'{prov} · {o} de {par}', v, COLP.get(par, COLOR['Otros']), f'{p(v)} %') for o, par, prov, v in AJ],
                     4, 'Los escaños más ajustados de 2023', W=420, ml=190),
              f'Fuente: <a href="{BASE}elecciones/voto-util-29n/">Voto útil el 29N en cada provincia</a>, de Mapa Electoral, con los resultados de las generales de 2023 (Ministerio del Interior) y los escaños de cada provincia en 2026.',
              None,
              (['Provincia', 'Escaño', 'Partido', 'Votos que bastaba perder (%)'], [[prov, o, par, p(v)] for o, par, prov, v in AJ]))

g_pq = figura('Seis de los pueblos que siempre aciertan dieron al PP menos de tres puntos de ventaja en 2023',
              'Ventaja del PP sobre el PSOE, en puntos, en las generales de 2023. Con la de España, sin el voto exterior',
              barras([(x, v, COLOR['PP'], f'+{p(v)}') for x, v in PUEB] + [('España', ESP_DIF, 'color-mix(in srgb, var(--pp) 45%, var(--bg))', f'+{p(ESP_DIF)}')],
                     3.5, 'Ventaja del PP en los pueblos que siempre aciertan', W=420, ml=140),
              f'Fuente: {L("pueblos-que-siempre-aciertan-29n", "Los pueblos que siempre aciertan")}, de Mapa Electoral, con los resultados del Ministerio del Interior. '
              f'Son 6 de los 24 municipios que votaron al ganador en las 16 generales desde 1977. En toda España, sin el voto exterior, la ventaja del PP fue de {p(ESP_DIF)} puntos.',
              [('PP', COLOR['PP'])],
              (['Municipio', 'Ventaja del PP en 2023 (puntos)'], [[x, p(v)] for x, v in PUEB]))

VU_URL = f'{BASE}elecciones/voto-util-29n/'
cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Hoy es la jornada de reflexión. La campaña de las elecciones generales del 29N terminó anoche a medianoche, y mañana, domingo, los colegios abren a las 9.00 y cierran a las 20.00. Rige la veda de encuestas, que la ley mantiene hasta el cierre de los colegios, así que esta crónica no lleva ninguna, como explicamos en {L('veda-encuestas-29n', 'la pieza de la veda')}. Del domingo 22 a hoy publicamos en esta sección más de una docena de piezas y las páginas de voto útil de las 52 provincias. Esta es la semana contada desde los mapas.</p>

<h2>Quién vota y qué se elige</h2>
<p data-tipo="dato">Mañana pueden votar 38.728.356 personas, 1.261.924 más que en julio de 2023, según contamos en {L('elecciones-generales-29n-cifras', 'el 29N en cifras')}. De las que viven en España, 1.615.127 votan por primera vez en unas generales. Se presentan 534 candidaturas al Congreso en las 52 circunscripciones, y Madrid elige un diputado más que en 2023, 38, y Cádiz uno menos, 8. Otros 2.769.645 electores viven fuera: su urna en los consulados cerró el jueves 26 y sus votos no se cuentan hasta el viernes 4 de diciembre, como explicamos en {L('voto-exterior-cera-loreg-29n', 'votar desde el extranjero, ley en mano')}.</p>
<p data-tipo="dato">Las elecciones eligen a las Cortes, no al presidente. Las nuevas Cortes se constituyen el miércoles 23 de diciembre a las 10.00, y para la investidura no hay fecha, solo un plazo de dos meses desde la primera votación, como contamos en {L('despues-elecciones-generales-29n-investidura', 'qué pasa después del 29N')}. Y el voto en blanco cuenta como válido y el nulo no, la única diferencia que importa para el reparto, según {L('voto-blanco-nulo-elecciones-generales-29n', 'la pieza del voto en blanco y el nulo')}.</p>

<h2>El voto útil, provincia a provincia</h2>
<p data-tipo="dato">El jueves abrimos <a href="{VU_URL}">una página de voto útil para cada provincia</a>: un cuadrado por escaño, con los votos de 2023 y los escaños de 2026. Con esos votos, <strong>{N_JUEGO} de los 350 escaños se habrían perdido si su partido hubiera perdido menos del 10 % de sus votos</strong>. El más ajustado fue el primero de Vox en Cantabria, que se habría ido con un {p(AJ[0][3])} % menos; después, el segundo de Junts en Girona ({p(AJ[1][3])} %) y el quinto del PP en Málaga ({p(AJ[2][3])} %).</p>
{g_aj}
<p data-tipo="dato">En Álava, por ejemplo, el último de sus 4 escaños fue para el PNV, y al PSOE le habrían bastado 3.126 votantes, según <a href="{BASE}elecciones/pais-vasco/alava/voto-util-29n/">el voto útil en Álava</a>. En Madrid, el último fue para el PSOE, con el PP a 35.114, según <a href="{BASE}elecciones/madrid/voto-util-29n/">el de Madrid</a>.</p>

<h2>El debate a cuatro, con datos</h2>
<p data-tipo="dato">El jueves por la noche, Pedro Sánchez, Alberto Núñez Feijóo, Santiago Abascal y Ada Colau se vieron en {L('debate-a-cuatro-sanchez-feijoo-abascal-colau-29n', 'el último debate de la campaña')}. Al día siguiente comprobamos cinco de sus frases con datos oficiales, al menos una de cada candidato, y {L('verificacion-debate-a-cuatro-datos-29n', 'solo una era exacta')}: la de Sánchez sobre el empleo. En el tercer trimestre de 2026 había 22.852.600 ocupados, el máximo de la Encuesta de Población Activa, que empieza en 2002.</p>

<h2>Los pueblos que siempre aciertan</h2>
<p data-tipo="dato">De los municipios con resultados en las 16 generales desde 1977, {L('pueblos-que-siempre-aciertan-29n', 'solo 24 han votado siempre al ganador')}. Mañana votan por decimoséptima vez, y en varios la racha depende de muy pocos votos: en 2023, el PP ganó en Ayerbe (Huesca) por 2 votos. En seis de los 24, la ventaja del PP fue de menos de tres puntos, cuando en toda España, sin el voto exterior, fue de {p(ESP_DIF)}.</p>
{g_pq}
<p data-tipo="dato">El mismo día contamos lo que las encuestas no dicen: {L('encuestas-fallos-elecciones-espana-29n', 'en 15 de las 30 elecciones analizadas desde 2015 fallaron por más de tres puntos')} con algún partido. Es una pieza sobre elecciones pasadas: no da ninguna cifra de las encuestas de este 29N.</p>

<h2>El fútbol, desde el mapa</h2>
<p data-tipo="dato">El domingo pasado, el día del Getafe-Atlético, contamos que en Getafe {L('getafe-atletico-sur-madrid-29n', 'el PSOE pasó de ganar en 112 de las 122 secciones a ganar en 74')}. Esta noche juegan el Real Madrid y el Alavés en el Bernabéu, y en Vitoria {L('real-madrid-alaves-chamartin-vitoria-29n', 'el PSOE ganó en 128 de las 166 secciones, pero en Mendizorrotza, el barrio del estadio del Alavés, el PP sacó el 46,5 %')}.</p>

<h2>Mañana</h2>
<p data-tipo="contexto">Los colegios abren a las 9.00 y cierran a las 20.00. Para votar basta el DNI, el pasaporte o el carné de conducir, y quien no sepa dónde le toca puede consultarlo, como contamos en {L('como-votar-elecciones-generales-29n', 'cómo votar el 29N')}. Interior da dos avances de participación durante el día, y en 2023 los primeros resultados llegaron a las 21.00, al cerrar Canarias, según {L('a-que-hora-resultados-elecciones-generales-29n', 'a qué hora se sabrán los resultados')}. Los de cada municipio estarán en <a href="{BASE}elecciones/resultados-elecciones-generales-2026/">los resultados de las elecciones generales 2026</a> en cuanto Interior empiece a darlos. Esta crónica no atribuye a ningún hecho de la campaña un efecto en el voto.</p>
'''

semana = [('getafe-atletico-sur-madrid-29n', 'Getafe-Atlético en las urnas'),
          ('una-semana-29n-la-semana-en-el-mapa', 'La crónica de la semana pasada'),
          ('elecciones-generales-29n-cifras', 'El 29N en cifras'),
          ('voto-blanco-nulo-elecciones-generales-29n', 'Voto en blanco y voto nulo'),
          ('despues-elecciones-generales-29n-investidura', 'Después del 29N: Cortes e investidura'),
          ('veda-encuestas-29n', 'La veda de encuestas'),
          ('debate-a-cuatro-sanchez-feijoo-abascal-colau-29n', 'El debate a cuatro'),
          ('pueblos-que-siempre-aciertan-29n', 'Los pueblos que siempre aciertan'),
          ('encuestas-fallos-elecciones-espana-29n', 'Cuánto fallan las encuestas'),
          ('voto-exterior-cera-loreg-29n', 'Votar desde el extranjero'),
          ('verificacion-debate-a-cuatro-datos-29n', 'El debate a cuatro, comprobado con datos'),
          ('real-madrid-alaves-chamartin-vitoria-29n', 'Real Madrid-Alavés en las urnas'),
          ('como-votar-elecciones-generales-29n', 'Cómo votar el 29N'),
          ('a-que-hora-resultados-elecciones-generales-29n', 'A qué hora se sabrán los resultados')]
assert len({s for s, _ in semana}) == len(semana)
for s, _ in semana:
    assert (RAIZ / 'actualidad' / s / 'index.html').exists() or s == 'real-madrid-alaves-chamartin-vitoria-29n', s
cuerpo += ('<div class="resumen"><b>La semana, pieza a pieza</b><ul>' + ''.join(f'<li>{L(s, t)}</li>' for s, t in semana)
           + f'<li><a href="{VU_URL}">Voto útil en cada provincia</a></li></ul></div>\n')

preguntas = [
    ('¿Cuántas personas pueden votar en las elecciones generales del 29N?',
     'Pueden votar 38.728.356 personas, 1.261.924 más que en 2023: 35.958.711 viven en España y 2.769.645 en el extranjero.'),
    ('¿A qué hora abren y cierran los colegios el 29N?', 'Abren a las 9.00 y cierran a las 20.00. En 2023, los primeros resultados llegaron a las 21.00, al cerrar Canarias.'),
    ('¿Cuántos escaños estaban en juego en 2023?',
     f'Con los votos de 2023 y los escaños de 2026, {N_JUEGO} de los 350 escaños se habrían perdido si su partido hubiera perdido menos del 10 % de sus votos.'),
]
enlaces = (f'{L("una-semana-29n-la-semana-en-el-mapa", "La crónica del sábado anterior")} · <a href="{VU_URL}">Voto útil en cada provincia</a> · '
           f'{L("como-votar-elecciones-generales-29n", "Cómo votar el 29N")} · {L("a-que-hora-resultados-elecciones-generales-29n", "A qué hora se sabrán los resultados")}')
foot = ('Datos: piezas y páginas de Mapa Electoral de la semana del 22 al 28 de noviembre de 2026, enlazadas en cada párrafo, donde se explica cada cálculo. '
        'Sin cifras de encuestas, por la veda. Cálculo: actualidad/src/resumenes/vispera.py.')

TIT = (f'La víspera del 29N: pueden votar 38.728.356 personas y {N_JUEGO} de los 350 escaños de 2023 cambiaban de manos con menos de un 10 % de votos')
DEK = ('La semana del debate a cuatro y del voto útil, contada desde los mapas en la jornada de reflexión de las elecciones generales: qué se elige mañana, '
       'qué escaños estuvieron más ajustados y qué pueblos se juegan la racha.')
DATOS = {'N_JUEGO': N_JUEGO, 'AJ': [{'escano': o, 'partido': par, 'prov': prov, 'pct': v} for o, par, prov, v in AJ],
         'PUEB': [{'mun': x, 'dif': v} for x, v in PUEB], 'ESP_DIF': ESP_DIF, 'SEMANA': [s for s, _ in semana]}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
if __name__ == '__main__':
    print(TIT)
    print(DEK)
    pieza('vispera-29n-la-semana-en-el-mapa', 'La víspera del 29N: la semana en el mapa', TIT, DEK, '28 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, datos_js)
