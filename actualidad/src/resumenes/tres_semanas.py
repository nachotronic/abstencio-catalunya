"""Crónica del sábado 7-11-2026: «A tres semanas del 29N», la semana del 1 al 6 de noviembre desde los mapas.

Cada cifra sale de una pieza ya publicada y enlazada (donde se explica el cálculo) o de la página de encuestas del 7-11-2026
(encuestas/index.html: última encuesta de cada encuestadora en los últimos 30 días y escenario central del modelo).
Uso, desde la raíz: python3 actualidad/src/resumenes/tres_semanas.py
"""
from comun import BASE, barras, figura, n, pieza

A = BASE + 'actualidad/'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
M = lambda path, t: f'<a href="{BASE}municipio/{path}/">{t}</a>'

# PP + Vox en la última encuesta de cada encuestadora con escaños (encuestas/index.html, 7-11-2026).
# (encuestadora y medio, extremo bajo, extremo alto, fecha de publicación)
ENC = [('NC Report · La Razón', 206, 210, '2 nov'), ('Hamalgama · Vozpópuli', 207, 207, '2 nov'), ('Celeste-Tel · Onda Cero', 204, 204, '6 nov'),
       ('SocioMétrica · El Español', 203, 203, '1 nov'), ('Target Point · El Debate', 199, 207, '2 nov'), ('Sigma Dos · El Mundo', 196, 208, '1 nov'),
       ('EM-Analytics · Electomanía', 197, 197, '30 oct'), ('Ateneo del Dato · elDiario.es', 183, 211, '25 oct'), ('IMOP · El Confidencial', 195, 195, '23 oct'),
       ('Winston · Artículo14', 191, 191, '26 oct'), ('SW Demoscopia · La Séptima', 172, 185, '6 nov')]
assert len(ENC) == 11 and sum(lo >= 176 for _, lo, _, _ in ENC) == 10
MODELO = dict(PP=127, PSOE=108, VOX=68, SUMAR=13, ERC=11, ppvox=195, p176=91, p210=14, lo=176, hi=212)
assert MODELO['PP'] + MODELO['VOX'] == MODELO['ppvox']

filas = [(f'{e}', (lo + hi) / 2, 'var(--pp)' if lo >= 176 else 'color-mix(in srgb, var(--pp) 45%, var(--bg))',
          f'{lo}-{hi}' if lo != hi else f'{lo}') for e, lo, hi, _ in sorted(ENC, key=lambda r: -(r[1] + r[2]))]
g_enc = figura('Diez de once encuestas dan a PP y Vox la mayoría absoluta',
               'Escaños de PP y Vox juntos en la última encuesta de cada encuestadora del último mes. Si la encuesta da una horquilla, la barra llega a su centro y la cifra es la horquilla',
               barras(filas, 230, 'Escaños de PP y Vox en cada encuesta', ml=200, linea=(176, 'Mayoría: 176'), separar=True),
               f'Fuente: <a href="{BASE}encuestas/">página de encuestas</a> de Mapa Electoral, 7 de noviembre de 2026, con el enlace a cada encuesta. Color claro: la horquilla de la encuestadora empieza por debajo de 176.',
               None,
               (['Encuestadora y medio', 'PP + Vox', 'Publicada'], [[e, f'{lo}-{hi}' if lo != hi else str(lo), f] for e, lo, hi, f in ENC]))

PUENTE = 'https://www.europapress.es/economia/transportes-00343/noticia-puente-avanza-dimision-tragedia-urda-decision-empatia-victimas-20261103211310.html'
INFOBAE = 'https://www.infobae.com/espana/2026/11/06/elecciones-generales-29-n-en-directo-ultima-hora-del-reinicio-de-la-campana-el-accidente-de-urda-o-el-caso-koldo/'
ABALOS = 'https://www.elidealgallego.com/actualidad/espana/2026-11-06/abalos-subraya-la-coincidencia-entre-el-registro-en-su-casa-y-las-declaraciones-de-koldo-889554.html'
UCO = 'https://www.infobae.com/espana/agencias/2026/11/05/la-uco-registra-la-casa-de-abalos-y-pide-informacion-a-adif-sobre-contratos-amanados/'
SOL = 'https://www.eldiario.es/madrid/somos/policia-desaloja-madrugada-acampada-sol-marcha-principales-organizaciones_1_13632746.html'
FEIJOO = 'https://www.europapress.es/nacional/noticia-feijoo-lamenta-muerte-fatima-banez-accidente-urda-era-mujer-incansable-leal-amiga-20261029150620.html'

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">El martes 3, al final de su comparecencia en la Diputación Permanente del Congreso por el accidente de Urda, el ministro de Transportes, Óscar Puente, anunció que dimitía y que no iría en las listas del PSOE el 29N. El 28 de octubre, el día del choque, había descartado irse. Esta vez lo explicó así:</p>
<blockquote class="cita"><p>«Un ministro de transportes de un país como España no puede continuar en su cargo con dos accidentes de esta gravedad en menos de un año. Por muy distintos que sean, y tenga o no responsabilidad directa en ellos, es una cuestión de dignidad política, de coherencia y de empatía con las víctimas»</p><footer>Óscar Puente, en la Diputación Permanente, el 3 de noviembre. Recogido por <a href="{PUENTE}">Europa Press</a>.</footer></blockquote>
<p data-tipo="contexto">El jueves 5, la UCO registró la casa de José Luis Ábalos en València, en una nueva pieza separada del caso Koldo, según <a href="{UCO}">EFE</a>. El viernes, Pedro Sánchez reabrió la precampaña del PSOE precisamente en València, y habló de Puente:</p>
<blockquote class="cita"><p>«El ejemplo de dignidad y ejemplaridad que ha ejercido Óscar Puente ellos jamás lo practicarán durante ninguna crisis»</p><footer>Pedro Sánchez, en el mitin del PSOE en València, el 6 de noviembre. Recogido por <a href="{INFOBAE}">Infobae</a>.</footer></blockquote>
<p data-tipo="contexto">Fue la semana en que los partidos volvieron a la precampaña tras el luto por Urda, y la última antes de la campaña, que empieza el viernes 13. Del domingo 1 al viernes 6 publicamos 19 piezas en esta sección. Esta es la semana del 1 al 6 de noviembre contada desde los mapas.</p>

<h2>Las encuestas: el PSOE baja tras Urda y PP y Vox siguen por encima de 176</h2>
<p data-tipo="dato">Las cuatro primeras encuestas hechas después del accidente coincidieron en una cosa: <a href="{A}encuestas-antes-despues-urda-29n/">el PSOE bajaba en todas</a> respecto a la anterior de la misma empresa, entre cuatro décimas y punto y medio. En las de antes del 28 de octubre subía. Hoy, de las 13 encuestadoras con una encuesta en los últimos 30 días, 12 dan ganador al PP. La excepción es SW Demoscopia, que el viernes daba al PSOE el 31,0 % y al PP el 28,5 %.</p>
{g_enc}
<p data-tipo="dato">De las 11 encuestadoras que publican escaños, 10 dan a PP y Vox juntos 176 o más, contando el extremo bajo de su horquilla. Nuestro modelo, que junta las encuestas y simula el reparto provincia a provincia, daba la mañana del 7 de noviembre en su escenario central PP {MODELO['PP']}, PSOE {MODELO['PSOE']}, Vox {MODELO['VOX']}, Sumar y el Frente Amplio {MODELO['SUMAR']} y ERC {MODELO['ERC']}. PP y Vox sumarían {MODELO['ppvox']}, entre {MODELO['lo']} y {MODELO['hi']} en ocho de cada diez simulaciones, y llegan a la mayoría absoluta en el {MODELO['p176']} % de ellas. A los tres quintos, 210, en el {MODELO['p210']} %. Las cifras de cada día están en la <a href="{BASE}encuestas/">página de encuestas</a>.</p>
<p data-tipo="contexto">El lunes contamos también la trayectoria de una de las víctimas de Urda, la exministra Fátima Báñez. <a href="{A}banez-huelva-pp-29n/">Encabezó seis veces la lista del PP en Huelva</a>, de 2000 a 2016: ganó la provincia una vez, en 2011, y nunca en San Juan del Puerto, su pueblo. Feijóo la despidió así:</p>
<blockquote class="cita"><p>«Era una mujer incansable, leal amiga y siempre comprometida con mejorar la vida de los españoles»</p><footer>Alberto Núñez Feijóo, presidente del PP, el 29 de octubre. Recogido por <a href="{FEIJOO}">Europa Press</a>.</footer></blockquote>

<h2>Valladolid y Valencia: el escaño de Puente y la lista de Ábalos</h2>
<p data-tipo="dato">Puente ya no será diputado, pero su nombre seguirá en la papeleta: las candidaturas estaban proclamadas cuando dimitió, así que sigue como número uno del PSOE en {M('valladolid/valladolid', 'Valladolid')}, y si saca escaño pasa a los siguientes de la lista. Con las encuestas hasta el 3 de noviembre, <a href="{A}puente-valladolid-segundo-escano-29n/">el segundo escaño socialista</a>, ahora el de José Domingo Castaño, sale en el 47,5 % de las simulaciones. La semana anterior salía en el 54 %.</p>
<p data-tipo="dato">Ábalos fue el número dos de la lista del PSOE por Valencia en 2023, detrás de Diana Morant. <a href="{A}psoe-valencia-abalos-municipios-29n/">Esa lista sacó el 32,3 %</a>, el mejor resultado del PSOE en la provincia desde 2008, y fue la más votada en 134 de sus 266 municipios. Para el 29N, con Pilar Bernabé al frente y encuestas anteriores al registro, el modelo le da los mismos cinco escaños. Ábalos, que está en prisión, contestó el viernes en X:</p>
<blockquote class="cita"><p>«No voy a atribuir intenciones que desconozco, pero tampoco voy a fingir que no llama poderosamente la atención»</p><footer>José Luis Ábalos, el 6 de noviembre, sobre la coincidencia del registro con las declaraciones de Koldo García. Recogido por EFE en <a href="{ABALOS}">El Ideal Gallego</a>.</footer></blockquote>
<p data-tipo="dato">En el conjunto de la Comunitat Valenciana, <a href="{A}comunitat-valenciana-escanos-29n/">PP y Vox pasarían de 18 a 20 de los 33 escaños</a> con la media de encuestas del 3 de noviembre. En Castellón, el segundo escaño del PSOE sale en el 45,5 % de las simulaciones y el cabeza de lista de Compromís, en el 40,6 %. Y hoy, día del Valencia-Real Madrid, contamos que <a href="{A}valencia-madrid-mestalla-barrios-29n/">el distrito de Mestalla vota como el del Bernabéu</a>: el PP ganó en sus 23 secciones censales en 2023.</p>

<h2>Las listas y las mesas</h2>
<p data-tipo="dato">El martes, el BOE publicó las candidaturas proclamadas. <a href="{A}listas-proclamadas-29n/">Las juntas electorales dejaron fuera 32 listas</a>: 21 al Congreso y 11 al Senado. PACMA pierde siete provincias, y en León la junta envió a la Fiscalía la copia del DNI de una suplente de Podemos, que se queda sin candidatos al Senado en la provincia.</p>
<p data-tipo="dato">Hasta el miércoles, los ayuntamientos sortearon a las 549.297 personas que formarán las mesas el 29N. <a href="{A}me-ha-tocado-mesa-electoral-29n/">En los pueblos de menos de 100 electores</a>, la mesa necesita a uno de cada seis vecinos; en las ciudades, a uno de cada setenta. Quien recibe la carta tiene siete días para presentar una excusa.</p>

<h2>Madrid: el cinturón rojo, la renta y la acampada</h2>
<p data-tipo="dato">En las generales de 2023, el PP ganó {M('madrid/coslada', 'Coslada')} por siete votos. Es el ejemplo más ajustado de <a href="{A}cinturon-rojo-madrid-29n/">lo que pasó en el cinturón rojo</a>: el PSOE pasó de ganar en 16 de los 24 grandes municipios de la Comunidad de Madrid en 2019 a ganar en 4, aunque subió en todos. En esos 16 municipios, el PSOE subió del 31,1 % al 33,0 %, y el PP, del 19,6 % al 35,3 %, tras la desaparición de Ciudadanos.</p>
<p data-tipo="patron">En Madrid, además, <a href="{A}participacion-renta-municipios-madrid-29n/">la participación sube con la renta</a> en cada escalón. En la décima parte de las secciones censales con menos renta de la Comunidad votó el 60,9 % del censo en 2023; en la décima parte más rica, el 83,1 %. Entre los seis grandes municipios más ricos y los seis más pobres, la distancia es hoy de 7,5 puntos, la mayor desde 1977.</p>
<p data-tipo="dato">El martes, la Policía desalojó de madrugada a 334 personas de la acampada por la vivienda de la Puerta del Sol, 38 días después de que empezara. <a href="{A}acampada-sol-alquiler-madrid-distritos-29n/">El alquiler sube más deprisa en el sur de Madrid</a>: un 22,7 % en Villaverde desde 2019, frente al 15,9 % de Centro, según el índice del Ministerio de Vivienda. Los acampados se despidieron con un manifiesto:</p>
<blockquote class="cita"><p>«Somos la fuerza que tiene la mayoría social si trabaja unida, y no nos vamos a conformar con migajas»</p><footer>Manifiesto de despedida de la acampada, leído horas antes del desalojo. Recogido por <a href="{SOL}">elDiario.es</a>.</footer></blockquote>

<h2>Euskadi y Navarra: un empate a tres</h2>
<p data-tipo="dato">El País Vasco elige 18 diputados, y con la media de encuestas <a href="{A}euskadi-29n-guia/">EH Bildu sacaría siete</a>. Lo que está en el aire es Bizkaia, que elige ocho. <a href="{A}bizkaia-pnv-bildu-encuestas-29n/">El PNV ganó allí en 92 municipios en 2019 y en 55 en 2023</a>: EH Bildu le quitó 27 y el PSOE, 10, Bilbao incluido. La media de encuestas del 3 de noviembre dejaba al PNV, EH Bildu y el PSOE entre el 22,2 % y el 22,4 %. El domingo, día del derbi, contamos que <a href="{A}derbi-vasco-bilbao-donostia-29n/">el PNV bajó en 414 de las 415 secciones</a> de Bilbao y Donostia entre 2019 y 2023.</p>
<p data-tipo="patron">En Navarra, <a href="{A}participacion-navarra-municipios-29n/">la participación va más ligada al voto a EH Bildu que a la renta</a>. Donde EH Bildu pasa del 40 %, votó el 64 %; donde no llega al 15 %, el 71 %. Fontellas votó un 80,9 % y Olazti un 59,9 %.</p>

<h2>Andalucía: el PP de Moreno y el de Feijóo</h2>
<p data-tipo="dato">El PP de Juanma Moreno sacó en las autonómicas de mayo <a href="{A}pp-andalucia-autonomicas-generales-29n/">150.000 votos más</a> que el PP de Feijóo en las generales de 2023, con 194.000 votantes menos. Ganó votos en 603 de los 785 municipios andaluces y en todas las provincias salvo Almería. Para el 29N, el modelo le da en cada provincia menos que en 2023.</p>

<h2>Fuera de España</h2>
<p data-tipo="dato">En Estados Unidos, <a href="{A}eeuu-resultados-medio-mandato-2026/">los demócratas ganaron las dos cámaras del Congreso</a> en las elecciones de medio mandato del martes. Con el recuento de esta mañana tienen 252 escaños en la Cámara de Representantes, frente a 161 republicanos y con 22 por decidir, y 51 de los 100 del Senado. En Bulgaria, Iliana Yotova, la candidata más cercana a Rusia, <a href="{A}bulgaria-yotova-gyurov-mapa-municipios/">ganó la segunda vuelta de las presidenciales</a> con el 57,6 %. Y hoy ha votado Nueva Zelanda, donde el primer ministro, Christopher Luxon, llegaba <a href="{A}nueva-zelanda-elecciones-mapa-circunscripciones/">casi empatado con los laboristas</a>: en el recuento provisional, <a href="{A}nueva-zelanda-resultados-mapa/">los laboristas ganan por muy poco el voto de partido, pero la coalición de Luxon suma la mayoría de escaños</a>.</p>

<h2>Lo que viene</h2>
<p data-tipo="contexto">La campaña empieza en la medianoche del jueves 12 al viernes 13. A partir del martes 24 no se podrán publicar encuestas: la ley electoral lo prohíbe en los cinco días anteriores a la votación. Hasta entonces, la <a href="{BASE}encuestas/">página de encuestas</a> y las de cada provincia se actualizan cada día. Esta crónica no atribuye a ningún hecho de la semana un efecto en el voto: las encuestas recogen cambios, pero no sus causas.</p>
'''

semana = [('encuestas-antes-despues-urda-29n', 'Cuatro de cuatro: el PSOE baja en todas las encuestas hechas tras Urda'),
          ('banez-huelva-pp-29n', 'Fátima Báñez, seis veces cabeza de lista en Huelva'),
          ('me-ha-tocado-mesa-electoral-29n', 'Me ha tocado ir a una mesa electoral'),
          ('listas-proclamadas-29n', 'Las 32 listas que se quedan fuera'),
          ('acampada-sol-alquiler-madrid-distritos-29n', 'La acampada de Sol y el alquiler por distritos'),
          ('euskadi-29n-guia', 'Guía del 29N en Euskadi'),
          ('bizkaia-pnv-bildu-encuestas-29n', 'Bizkaia, el feudo del PNV, en empate a tres'),
          ('cinturon-rojo-madrid-29n', 'Lo que queda del cinturón rojo'),
          ('participacion-renta-municipios-madrid-29n', 'Quién no vota en Madrid'),
          ('participacion-navarra-municipios-29n', 'La participación en Navarra, pueblo a pueblo'),
          ('comunitat-valenciana-escanos-29n', 'Los 33 escaños valencianos'),
          ('psoe-valencia-abalos-municipios-29n', 'El PSOE de Valencia tras el registro a Ábalos'),
          ('pp-andalucia-autonomicas-generales-29n', 'El PP de Moreno y el de Feijóo'),
          ('puente-valladolid-segundo-escano-29n', 'Puente dimite: el segundo escaño de Valladolid'),
          ('derbi-vasco-bilbao-donostia-29n', 'El derbi en las urnas'),
          ('eeuu-resultados-medio-mandato-2026', 'Estados Unidos: los resultados'),
          ('eeuu-noche-electoral-guia-horarios', 'La noche electoral de EE. UU., hora a hora'),
          ('bulgaria-yotova-gyurov-mapa-municipios', 'Bulgaria, municipio a municipio'),
          ('nueva-zelanda-elecciones-mapa-circunscripciones', 'Nueva Zelanda, circunscripción a circunscripción')]
assert len(semana) == 19
cuerpo += ('<div class="resumen"><b>La semana, pieza a pieza</b><ul>' + ''.join(f'<li>{L(s, t)}</li>' for s, t in semana) + '</ul></div>\n')

preguntas = [
    ('¿Cuándo empieza la campaña de las elecciones generales del 29N?', 'El viernes 13 de noviembre a medianoche. Dura quince días y acaba el viernes 27; el sábado 28 es la jornada de reflexión.'),
    ('¿Qué dicen las encuestas a tres semanas del 29N?', f'De las 13 encuestadoras con una encuesta en los últimos 30 días, 12 dan ganador al PP. De las 11 que publican escaños, 10 dan a PP y Vox 176 o más. Nuestro modelo les da {MODELO["ppvox"]} en el escenario central y la mayoría absoluta en el {MODELO["p176"]} % de las simulaciones.'),
    ('¿Por qué Óscar Puente seguirá en la papeleta si ha dimitido?', 'Porque las candidaturas ya estaban proclamadas cuando renunció. Su nombre sigue como número uno del PSOE en Valladolid, y si la lista saca escaño, pasa a los siguientes.'),
]
enlaces = (f'{L("cuatro-semanas-29n-la-semana-en-el-mapa", "La crónica del sábado anterior")} · <a href="{BASE}encuestas/">Encuestas del 29N</a> · '
           f'<a href="{BASE}encuestas/provincias.html">Encuestas por provincias</a> · {L("valencia-madrid-mestalla-barrios-29n", "Mestalla vota como el Bernabéu")}')
foot = 'Datos: piezas de Mapa Electoral de la semana del 1 al 6 de noviembre de 2026, enlazadas en cada párrafo, donde se explica cada cálculo; encuestas publicadas y modelo de Mapa Electoral a 7 de noviembre de 2026. Cálculo: actualidad/src/resumenes/tres_semanas.py.'

TIT = f'A tres semanas del 29N, PP y Vox llegan a la mayoría absoluta en el {MODELO["p176"]} % de nuestras simulaciones: la semana en que dimitió Puente y la UCO registró la casa de Ábalos'
DEK = 'Puente se fue del Gobierno y de la lista, la UCO registró la casa de Ábalos en València y los partidos volvieron a la precampaña tras el luto por Urda. Diez de once encuestas con escaños dan mayoría a PP y Vox. Esta es la semana del 1 al 6 de noviembre contada desde los mapas.'
import json
datos_js = '<script>const D=' + json.dumps({'SEMANA': [s for s, _ in semana], 'ENC': ENC, 'MODELO': MODELO}, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
if __name__ == '__main__':
    print(TIT)
    pieza('tres-semanas-29n-la-semana-en-el-mapa', 'A tres semanas del 29N: la semana en el mapa', TIT, DEK, '7 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, datos_js)
