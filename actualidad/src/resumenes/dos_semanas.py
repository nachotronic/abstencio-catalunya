"""Crónica del sábado 14-11-2026: «A dos semanas del 29N», la semana del 8 al 13 de noviembre desde los mapas.

Cada cifra sale de una pieza ya publicada y enlazada (donde se explica el cálculo) o de la página de encuestas del 14-11-2026
(encuestas/index.html: última encuesta de cada encuestadora con trabajo de campo terminado en los últimos 30 días) y del
modelo publicado a las 00.32 del 14-11-2026 (previsiones/datos/publico/historico/2026-11-14-0032.json).
Uso, desde la raíz: python3 actualidad/src/resumenes/dos_semanas.py
"""
import json

from comun import BASE, barras, figura, n, pieza

A = BASE + 'actualidad/'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'

# Última encuesta de cada encuestadora con trabajo de campo terminado en los últimos 30 días (encuestas/index.html, 14-11-2026).
# (encuestadora · medio, PP %, PSOE %, escaños PP+Vox bajo, alto (None si no publica escaños), publicada)
ENC = [('Sigma Dos · El Mundo', 31.0, 25.4, 188, 201, '13 nov'), ('SW Demoscopia · La Séptima', 28.5, 31.6, 169, 182, '13 nov'),
       ('EM-Analytics · Electomanía', 30.4, 26.1, 190, 190, '13 nov'), ('40dB · El País / SER', 31.5, 29.4, 185, 207, '13 nov'),
       ('Winston · Artículo14', 31.1, 26.4, 198, 198, '13 nov'), ('SocioMétrica · El Español', 32.0, 27.7, 202, 202, '8 nov'),
       ('IMOP · El Confidencial', 29.8, 25.9, 196, 196, '8 nov'), ('DYM · 20minutos', 33.1, 27.3, 198, 205, '10 nov'),
       ('NC Report · La Razón', 32.6, 25.6, 205, 209, '9 nov'), ('GAD3 · Vocento', 31.9, 25.9, 199, 199, '9 nov'),
       ('Ateneo del Dato · elDiario.es', 31.5, 28.6, 184, 202, '8 nov'), ('Sondaxe · La Voz de Galicia', 29.7, 27.3, None, None, '8 nov'),
       ('Data10 · OKDiario', 32.4, 24.7, 203, 203, '9 nov'), ('Celeste-Tel · Onda Cero', 31.4, 25.7, 204, 204, '6 nov'),
       ('Target Point · El Debate', 31.8, 25.5, 199, 207, '2 nov'), ('CIS', 25.5, 33.3, 155, 171, '12 nov'),
       ('Hamalgama · Vozpópuli', 32.0, 26.4, 207, 207, '2 nov'), ('More in Common', 28.3, 27.6, None, None, '3 nov')]
CON_ESC = [e for e in ENC if e[3] is not None]
GANA_PP = sum(e[1] > e[2] for e in ENC)
MAYORIA = sum(e[3] >= 176 for e in CON_ESC)
assert (len(ENC), GANA_PP, len(CON_ESC), MAYORIA) == (18, 16, 16, 14)
assert not any(e[3] >= 210 for e in CON_ESC)

# Modelo de Mapa Electoral publicado el 14-11-2026 a las 00.32 (encuestas hasta el 13-11). Percentiles 10 y 90 del bloque PP + Vox.
MODELO = dict(PP=126, PSOE=109, VOX=67, SUMAR=13, ERC=10, ppvox=193, lo=176, hi=210, p176=91, p210=10,
              media_pp=30.72, media_psoe=27.52, media_pp_ant=30.75, media_psoe_ant=27.13)
VENTAJA = round(MODELO['media_pp'] - MODELO['media_psoe'], 4)
VENTAJA_ANT = round(MODELO['media_pp_ant'] - MODELO['media_psoe_ant'], 4)
assert f'{VENTAJA:.1f}' == '3.2' and f'{VENTAJA_ANT:.1f}' == '3.6'

PP_CLARO = 'color-mix(in srgb, var(--pp) 45%, var(--bg))'
filas = [(e[0], (e[3] + e[4]) / 2, 'var(--pp)' if e[3] >= 176 else PP_CLARO, f'{e[3]}-{e[4]}' if e[3] != e[4] else f'{e[3]}')
         for e in sorted(CON_ESC, key=lambda r: -(r[3] + r[4]))]
g_enc = figura(f'{MAYORIA} de {len(CON_ESC)} encuestas dan a PP y Vox la mayoría absoluta',
               'Escaños de PP y Vox juntos en la última encuesta de cada encuestadora que publica escaños. Si la encuesta da una horquilla, la barra llega a su centro y la cifra es la horquilla',
               barras(filas, 230, 'Escaños de PP y Vox en cada encuesta', ml=200, linea=(176, 'Mayoría: 176'), separar=True),
               f'Fuente: <a href="{BASE}encuestas/">página de encuestas</a> de Mapa Electoral, 14 de noviembre de 2026, con el enlace a cada encuesta. Última encuesta de cada encuestadora con trabajo de campo terminado en los últimos 30 días. Color claro: la horquilla empieza por debajo de 176.',
               None,
               (['Encuestadora y medio', 'PP + Vox', 'Publicada'], [[e[0], f'{e[3]}-{e[4]}' if e[3] != e[4] else str(e[3]), e[5]] for e in CON_ESC]))

dif = lambda e: round(e[1] - e[2], 1)
filas2 = [(e[0], abs(dif(e)), 'var(--pp)' if dif(e) > 0 else 'var(--psoe)', f'{"PP" if dif(e) > 0 else "PSOE"} +{n(abs(dif(e)), 1)}')
          for e in sorted(ENC, key=lambda r: -dif(r))]
g_dif = figura('El CIS y SW Demoscopia, los dos únicos que ponen por delante al PSOE',
               'Ventaja en puntos del primero sobre el segundo, PP o PSOE, en la última encuesta de cada encuestadora',
               barras(filas2, 9, 'Ventaja del PP o del PSOE en cada encuesta', ml=200, separar=True),
               f'Fuente: <a href="{BASE}encuestas/">página de encuestas</a> de Mapa Electoral, 14 de noviembre de 2026. Diferencia entre el voto estimado del PP y el del PSOE en cada encuesta.',
               [('Por delante, el PP', 'var(--pp)'), ('Por delante, el PSOE', 'var(--psoe)')],
               (['Encuestadora y medio', 'PP (%)', 'PSOE (%)', 'Publicada'], [[e[0], n(e[1], 1), n(e[2], 1), e[5]] for e in ENC]))

SANCHEZ_SEPTIMA = 'https://www.infobae.com/espana/2026/11/09/elecciones-generales-29-n-en-directo-feijoo-confia-en-que-los-sindicatos-acepten-el-resultado-electoral-si-hay-cambio-de-gobierno/'
ARNEDO = 'https://actualidadriojabaja.com/sanchez-pide-en-arnedo-una-participacion-del-75-el-29n-para-alcanzar-una-mayoria-progresista/'
FEIJOO_IMV = 'https://www.europapress.es/nacional/noticia-feijoo-reunira-ingreso-minimo-vital-subsidios-renta-activacion-vinculada-busqueda-empleo-20261110143401.html'
MAROTO = 'https://www.europapress.es/madrid/noticia-psoe-asegura-remontada-realidad-avisa-feijoo-le-van-hacer-muy-largas-semanas-20261109111930.html'
CCOO = ('https://industria.ccoo.es/noticia:772073--Huelga_en_la_industria_carnica_del_9_al_13N_Neveras_vacias_hasta_que_las_patronales_entiendan_'
        'que_deben_transformar_sus_beneficios_en_mas_salario_y_en_mejores_condiciones&amp;opc_id=7b0815797cd81939bb3cdca8b4b06f4d')
CIS_NOTA = 'https://www.cis.es/documents/d/guest/3584_estimacion-pdf'

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">La campaña del 29N empezó en la medianoche del jueves al viernes. {L('arranque-campana-sevilla-badalona-colon-vallecas-29n', 'Cada candidato eligió dónde abrirla')}: Pedro Sánchez, en Sevilla; Alberto Núñez Feijóo, en Badalona, con Xavier García Albiol; Santiago Abascal, en la plaza de Colón de Madrid, y Ada Colau, en Puente de Vallecas. El viernes por la mañana, Sánchez fue a Arnedo, en La Rioja, y allí pidió una participación del 75 % para reunir una mayoría progresista de 176 diputados, según <a href="{ARNEDO}">Actualidad Rioja Baja</a>. Cuatro días antes, en La Séptima, había puesto el listón algo más abajo:</p>
<blockquote class="cita"><p>«De lejos va a superar el 70 % de participación que tuvimos en las elecciones de 2023 y, por tanto, al igual que ocurrió en Estados Unidos, en Brasil y también en España en 2023, volveremos a reeditar una mayoría de progreso en el Parlamento»</p><footer>Pedro Sánchez, en La Séptima, el 9 de noviembre de 2026, según el directo de <a href="{SANCHEZ_SEPTIMA}">Infobae</a>.</footer></blockquote>
<p data-tipo="contexto">Fue también la semana del CIS preelectoral, el jueves, y del primer debate de la campaña, el viernes en laSexta. Del domingo 8 al viernes 13 publicamos 32 piezas en esta sección, 18 de ellas en la serie «El mapa electoral de…», una por comunidad. Esta es la semana del 8 al 13 de noviembre contada desde los mapas.</p>

<h2>Las encuestas: el CIS, solo frente a las demás</h2>
<p data-tipo="dato">El jueves, el CIS publicó su preelectoral: <a href="{A}cis-preelectoral-29n/">el PSOE, con el 33,3 %, saca 7,8 puntos al PP</a>, que se queda en el 25,5 %. Ni sumando el máximo de sus horquillas llegan PP y Vox a la mayoría absoluta: se quedan en 171 escaños. Ninguna otra encuesta del último mes da al PSOE tanta ventaja. El viernes contamos que, provincia a provincia, <a href="{A}cis-preelectoral-provincias-29n/">el CIS da al PSOE más escaños que la media de encuestas en 13 provincias</a> y menos en ninguna; en Madrid, entre 12 y 14 frente a 10. El propio CIS avisa de cómo leer esas horquillas:</p>
<blockquote class="cita"><p>«No es un intervalo de confianza ni un error de muestreo»</p><footer>CIS, nota metodológica del reparto de escaños del <a href="{CIS_NOTA}">estudio 3584</a> (12-11-2026).</footer></blockquote>
<p data-tipo="dato">Con la última encuesta de cada una de las {len(ENC)} encuestadoras que han terminado un trabajo de campo en los últimos 30 días, {GANA_PP} dan ganador al PP. Las dos que ponen delante al PSOE son el CIS y SW Demoscopia, que el viernes le daba el 31,6 % frente al 28,5 % del PP. De las {len(CON_ESC)} que publican escaños, {MAYORIA} dan a PP y Vox juntos 176 o más, contando el extremo bajo de su horquilla; ninguna les da los tres quintos, 210.</p>
{g_enc}
<p data-tipo="dato">El lunes, <a href="{A}encuestas-40db-psoe-podemos-29n/">40dB dejó al PSOE a dos puntos del PP</a> en la encuesta de El País y la SER: 29,9 % frente a 31,9 %, su mejor dato en esa serie desde diciembre de 2024. Las otras tres encuestas publicadas ese día veían entre seis y ocho puntos de distancia. La socialista Reyes Maroto lo celebró así:</p>
<blockquote class="cita"><p>«Hoy seguro que en Génova están preocupados, preocupados porque la remontada es una realidad»</p><footer>Reyes Maroto, portavoz del PSOE en el Ayuntamiento de Madrid, el 9 de noviembre, según <a href="{MAROTO}">Europa Press</a>.</footer></blockquote>
{g_dif}
<p data-tipo="dato">La media de encuestas de nuestro modelo, con las publicadas hasta el viernes, da al PP el {n(MODELO['media_pp'], 1)} % y al PSOE el {n(MODELO['media_psoe'], 1)} %: {n(VENTAJA, 1)} puntos de ventaja. Hace una semana eran {n(VENTAJA_ANT, 1)}. En su escenario central, la madrugada del 14 de noviembre, el modelo daba PP {MODELO['PP']}, PSOE {MODELO['PSOE']}, Vox {MODELO['VOX']}, Sumar y el Frente Amplio {MODELO['SUMAR']} y ERC {MODELO['ERC']}. PP y Vox sumarían {MODELO['ppvox']}, entre {MODELO['lo']} y {MODELO['hi']} en ocho de cada diez simulaciones, y llegan a la mayoría absoluta en el {MODELO['p176']} % de ellas; a los tres quintos, en el {MODELO['p210']} %. Las cifras de cada día están en la <a href="{BASE}encuestas/">página de encuestas</a>.</p>

<h2>Cuatro arranques y once pueblos</h2>
<p data-tipo="dato">Feijóo abrió la campaña en una ciudad donde, en las generales de 2023, <a href="{A}arranque-campana-sevilla-badalona-colon-vallecas-29n/">el PP no fue el más votado en ninguna de las 149 secciones censales</a>: el PSC ganó en 146 y le sacó 24,0 puntos. Abascal, en cambio, arrancó entre tres barrios donde el PP sacó entre el 44,4 % y el 67,7 %, y Colau, en un distrito donde Sumar quedó tercera, a 166 votos del PP.</p>
<p data-tipo="dato">El viernes, primer día completo, los candidatos visitaron fuera de Madrid y Barcelona once municipios, y <a href="{A}primer-dia-campana-municipios-29n/">los once cambiaron de ganador entre 2019 y 2023</a>. Arnedo, donde estuvo Sánchez, lo ganó el PSOE por 11,0 puntos en 2019 y lo perdió por 4,4 en 2023. Solo en uno, Pamplona, el partido del candidato que iba de visita fue el más votado en 2023.</p>
<p data-tipo="dato">Por la noche, en el debate de laSexta, <a href="{A}debate-lasexta-cuerpo-bravo-figaredo-bustinduy-29n/">dos de los cuatro participantes no se presentan el 29N</a>: ni Carlos Cuerpo, por el PSOE, ni Pablo Bustinduy, por el Frente Amplio, están en ninguna lista. Juan Bravo encabeza al PP en Sevilla, donde la media de encuestas da cuatro escaños al PP y cuatro al PSOE, y José María Figaredo a Vox en Asturias, donde repetiría su escaño.</p>

<h2>La participación y la abstención</h2>
<p data-tipo="dato">En 2023 votó el 70,4 % de los residentes en España, y <a href="{A}sanchez-abascal-septima-revuelta-participacion-29n/">17 provincias no llegaron al 70 %</a>. Con el censo de 2026, el 75 % que pide Sánchez son 27,0 millones de votantes, 2,2 millones más que en 2023. ¿A quién beneficiaría? El domingo calculamos que <a href="{A}a-quien-beneficia-abstencion-29n/">si los barrios que menos votan fueran a las urnas como la media</a>, cinco escaños de 2023 habrían cambiado de manos, cuatro de ellos hacia el PSOE. En la quinta parte del censo de cada provincia que menos votó, el PSOE sacó el 37,3 % y el PP el 27,4 %.</p>

<h2>La renta de activación y la huelga cárnica</h2>
<p data-tipo="dato">El martes, el PP presentó su programa, con una propuesta para convertir el ingreso mínimo vital en una «renta de activación». <a href="{A}renta-activacion-ingreso-minimo-vital-29n/">En octubre lo cobraban 2.781.679 personas</a>, un 17,7 % más que un año antes: uno de cada 8 habitantes de Jaén y uno de cada 40 de Gipuzkoa. Feijóo lo explicó así:</p>
<blockquote class="cita"><p>«Cada beneficiario firmará un acuerdo de formación y búsqueda de empleo, con seguimiento verificable. Rechazar empleos adecuados de forma reiterada y sin causa justificada supondrá la pérdida graduada de las ayudas»</p><footer>Alberto Núñez Feijóo, presidente del PP, en la presentación del programa electoral, el 10 de noviembre, según <a href="{FEIJOO_IMV}">Europa Press</a>.</footer></blockquote>
<p data-tipo="patron">Del lunes 9 al viernes 13, la industria cárnica estuvo llamada a la huelga. El 11,5 % de los ocupados de España trabaja en la industria; en Guissona, sede de bonÀrea, el 56,3 %. <a href="{A}huelga-carnica-pueblos-industria-29n/">En los municipios donde más pesa la industria</a>, el PP sacó en 2023 1,9 puntos menos que en el resto de su provincia, y el voto a Vox apenas cambia. CCOO convocó así:</p>
<blockquote class="cita"><p>«La huelga de quienes alimentan el país ya está aquí, por más salario y por mejores condiciones laborales»</p><footer>CCOO de Industria, en su <a href="{CCOO}">convocatoria</a> del 6 de noviembre de 2026.</footer></blockquote>

<h2>El mapa electoral de cada comunidad</h2>
<p data-tipo="dato">Del martes al jueves publicamos las 18 piezas de la serie «El mapa electoral de…», una por comunidad y otra para Ceuta y Melilla, con el mapa de cada municipio en 2019 y 2023. En {L('mapa-electoral-andalucia-29n', 'Andalucía')}, el PSOE pasó de ganar en 699 de los 785 municipios a ganar en 466, con el mismo 33,8 % de los votos. En {L('mapa-electoral-cataluna-29n', 'Cataluña')}, ERC pasó de 619 a 159, y el PSC, de 75 a 462. En {L('mapa-electoral-madrid-29n', 'Madrid')}, Vox ganó en 61 municipios en 2019 y en ninguno en 2023, y en la {L('mapa-electoral-murcia-29n', 'Región de Murcia')} los 16 que había ganado pasaron al PP. Y en {L('mapa-electoral-ceuta-melilla-29n', 'Ceuta')}, con la media de encuestas, el PP y Vox están prácticamente empatados: el 32,6 % de los votos para el PP y el 32,3 % para Vox.</p>
<p data-tipo="dato">En Santa Cruz de Tenerife, Vox vuelve a la papeleta tras no presentar lista al Congreso en 2023. <a href="{A}vox-vuelve-tenerife-29n/">Aquel año, el PP subió allí 15,4 puntos</a>, frente a 4,4 en Las Palmas. Con las encuestas, Vox recuperaría entre uno y dos de los siete diputados de la provincia.</p>

<h2>Fuera de España</h2>
<p data-tipo="dato">En Paraguay, <a href="{A}paraguay-pena-destituido-mapa-departamentos/">el Senado destituyó al presidente Santiago Peña</a> con 44 de sus 45 votos, por mal desempeño de funciones. Y este domingo vota Cabo Verde: seis candidatos se disputan la presidencia, entre ellos el presidente, José Maria Neves, que en 2021 <a href="{A}cabo-verde-presidenciales-neves-rosa-mapa/">evitó la segunda vuelta por 3.311 votos</a>. La diáspora es hoy el 18,2 % del censo.</p>

<h2>Lo que viene</h2>
<p data-tipo="contexto">Quedan dos semanas de campaña. A partir del martes 24 no se podrán publicar encuestas: la ley electoral lo prohíbe en los cinco días anteriores a la votación. Hasta entonces, la <a href="{BASE}encuestas/">página de encuestas</a> y las de cada provincia se actualizan cada día. El sábado 28 es la jornada de reflexión. Esta crónica no atribuye a ningún hecho de la semana un efecto en el voto: las encuestas recogen cambios, pero no sus causas.</p>
'''

semana = [('a-quien-beneficia-abstencion-29n', 'A quién beneficia la abstención'),
          ('atletico-barca-metropolitano-camp-nou-29n', 'El Atlético-Barça en las urnas'),
          ('encuestas-40db-psoe-podemos-29n', 'El PSOE, a dos puntos en 40dB'),
          ('huelga-carnica-pueblos-industria-29n', 'La huelga cárnica y los pueblos de la industria'),
          ('vox-vuelve-tenerife-29n', 'Vox vuelve en Tenerife'),
          ('sanchez-abascal-septima-revuelta-participacion-29n', 'Sánchez, Abascal y la participación'),
          ('paraguay-pena-destituido-mapa-departamentos', 'Paraguay destituye a Peña'),
          ('renta-activacion-ingreso-minimo-vital-29n', 'La renta de activación y el ingreso mínimo vital'),
          ('arranque-campana-sevilla-badalona-colon-vallecas-29n', 'Dónde abre cada candidato la campaña'),
          ('cabo-verde-presidenciales-neves-rosa-mapa', 'Cabo Verde elige presidente'),
          ('cis-preelectoral-29n', 'El CIS preelectoral'),
          ('cis-preelectoral-provincias-29n', 'El CIS, provincia a provincia'),
          ('primer-dia-campana-municipios-29n', 'Los once municipios del primer día'),
          ('debate-lasexta-cuerpo-bravo-figaredo-bustinduy-29n', 'El debate de laSexta'),
          ('mapa-electoral-andalucia-29n', 'El mapa electoral de Andalucía'),
          ('mapa-electoral-cataluna-29n', 'El mapa electoral de Cataluña'),
          ('mapa-electoral-madrid-29n', 'El mapa electoral de Madrid'),
          ('mapa-electoral-comunitat-valenciana-29n', 'El mapa electoral de la Comunitat Valenciana'),
          ('mapa-electoral-castilla-y-leon-29n', 'El mapa electoral de Castilla y León'),
          ('mapa-electoral-galicia-29n', 'El mapa electoral de Galicia'),
          ('mapa-electoral-castilla-la-mancha-29n', 'El mapa electoral de Castilla-La Mancha'),
          ('mapa-electoral-pais-vasco-29n', 'El mapa electoral del País Vasco'),
          ('mapa-electoral-canarias-29n', 'El mapa electoral de Canarias'),
          ('mapa-electoral-aragon-29n', 'El mapa electoral de Aragón'),
          ('mapa-electoral-murcia-29n', 'El mapa electoral de la Región de Murcia'),
          ('mapa-electoral-extremadura-29n', 'El mapa electoral de Extremadura'),
          ('mapa-electoral-baleares-29n', 'El mapa electoral de Baleares'),
          ('mapa-electoral-asturias-29n', 'El mapa electoral de Asturias'),
          ('mapa-electoral-navarra-29n', 'El mapa electoral de Navarra'),
          ('mapa-electoral-cantabria-29n', 'El mapa electoral de Cantabria'),
          ('mapa-electoral-la-rioja-29n', 'El mapa electoral de La Rioja'),
          ('mapa-electoral-ceuta-melilla-29n', 'El mapa electoral de Ceuta y Melilla')]
assert len(semana) == 32 and sum(s.startswith('mapa-electoral-') for s, _ in semana) == 18
cuerpo += ('<div class="resumen"><b>La semana, pieza a pieza</b><ul>' + ''.join(f'<li>{L(s, t)}</li>' for s, t in semana) + '</ul></div>\n')

preguntas = [
    ('¿Qué dicen las encuestas a dos semanas del 29N?', f'De las {len(ENC)} encuestadoras con una encuesta en los últimos 30 días, {GANA_PP} dan ganador al PP; el CIS y SW Demoscopia, al PSOE. De las {len(CON_ESC)} que publican escaños, {MAYORIA} dan a PP y Vox 176 o más. Nuestro modelo les da {MODELO["ppvox"]} en el escenario central y la mayoría absoluta en el {MODELO["p176"]} % de las simulaciones.'),
    ('¿Cuándo dejan de publicarse encuestas?', 'El martes 24 de noviembre. La ley electoral prohíbe publicarlas en los cinco días anteriores a la votación, que es el domingo 29.'),
    ('¿Qué participación pide Sánchez?', 'Un 75 %, según lo que dijo en Arnedo el 13 de noviembre. En 2023 votó el 70,4 % de los residentes en España; con el censo de 2026, el 75 % son 27,0 millones de votantes.'),
]
enlaces = (f'{L("tres-semanas-29n-la-semana-en-el-mapa", "La crónica del sábado anterior")} · <a href="{BASE}encuestas/">Encuestas del 29N</a> · '
           f'<a href="{BASE}encuestas/provincias.html">Encuestas por provincias</a> · {L("cis-preelectoral-29n", "El CIS preelectoral")}')
foot = ('Datos: piezas de Mapa Electoral de la semana del 8 al 13 de noviembre de 2026, enlazadas en cada párrafo, donde se explica cada cálculo; '
        'encuestas publicadas y modelo de Mapa Electoral a 14 de noviembre de 2026. Cálculo: actualidad/src/resumenes/dos_semanas.py.')

TIT = (f'A dos semanas del 29N, {MAYORIA} de las {len(CON_ESC)} encuestas con escaños dan mayoría absoluta a PP y Vox; '
       'solo el CIS y SW Demoscopia ponen por delante al PSOE: la primera semana de campaña en el mapa')
DEK = ('Arrancó la campaña, el CIS dio al PSOE 7,8 puntos de ventaja y Sánchez pidió una participación del 75 %. Las demás encuestas, '
       'salvo SW Demoscopia, siguen dando ganador al PP. Esta es la semana del 8 al 13 de noviembre contada desde los mapas.')
datos_js = '<script>const D=' + json.dumps({'SEMANA': [s for s, _ in semana], 'ENC': ENC, 'MODELO': MODELO, 'VENTAJA': VENTAJA, 'VENTAJA_ANT': VENTAJA_ANT},
                                          ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
if __name__ == '__main__':
    print(TIT)
    pieza('dos-semanas-29n-la-semana-en-el-mapa', 'A dos semanas del 29N: la semana en el mapa', TIT, DEK, '14 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, datos_js)
