"""Crónica del sábado 21-11-2026: «A una semana del 29N», la semana del 15 al 20 de noviembre desde los mapas.

Cada cifra sale de una pieza ya publicada y enlazada (donde se explica el cálculo) o de las encuestas que recoge
mapaelectoral.es/encuestas (carga() y medianas() de encuestas/src/construir.py, con los datos de la última actualización
automática). Las del debate, de las crónicas enlazadas.
Uso, desde la raíz: python3 actualidad/src/resumenes/una_semana.py
"""
import importlib.util
import json
import re
from datetime import date

from comun import BASE, RAIZ, barras, esc, figura, n, pieza

A = BASE + 'actualidad/'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
p = lambda v: n(v, 1)
HOY, SEMANA = date(2026, 11, 21), date(2026, 11, 14)

_spec = importlib.util.spec_from_file_location('enc_construir', RAIZ / 'encuestas/src/construir.py')
enc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enc)
_pub = lambda e: e.get('publicado') or e['fin']
ENCS = enc.carga()

# Mediana de /encuestas/: hoy y hace una semana
SERIE = {r['d']: r for r in enc.medianas(ENCS, HOY)}
MED = {k: v for k, v in SERIE[HOY.isoformat()].items() if k != 'd'}
MED0 = {k: v for k, v in SERIE[SEMANA.isoformat()].items() if k != 'd'}
DIF, DIF0 = round(MED['PP'] - MED['PSOE'], 1), round(MED0['PP'] - MED0['PSOE'], 1)
BAJA = round(DIF0 - DIF, 1)
assert DIF > 0 and BAJA > 0, (DIF, DIF0)
DIAS = [r for d, r in sorted(SERIE.items()) if d >= SEMANA.isoformat()]
assert len(DIAS) == 8
MINDIA = min(DIAS, key=lambda r: round(r['PP'] - r['PSOE'], 1))
MIN_DIF = round(MINDIA['PP'] - MINDIA['PSOE'], 1)

# Encuestas publicadas en la semana (del domingo 15 al sábado 21)
SEM = [e for e in ENCS if '2026-11-15' <= _pub(e) <= '2026-11-20' and not e['reest']]
CASAS_SEM = sorted({enc.nombre_casa(e['casa']) for e in SEM})
# Con entrevistas del viernes 20, el día después del debate
TRAS = [e for e in SEM if e['fin'] >= '2026-11-20']
# Última de cada encuestadora en las tres últimas semanas (la selección de la mediana)
ULT = {}
for e in ENCS:
    if (HOY - date.fromisoformat(e['fin'])).days < enc.VENTANA_MEDIANA and not e['reest'] and enc.clave(e['casa']) not in ULT:
        ULT[enc.clave(e['casa'])] = e
GANA_PP = sum(e['voto']['PP'] > e['voto']['PSOE'] for e in ULT.values())
DELANTE_PSOE = sorted(enc.nombre_casa(e['casa']) for e in ULT.values() if e['voto']['PSOE'] > e['voto']['PP'])
# Escaños de PP y Vox: última de cada encuestadora en los últimos 30 días que los publica (como el titular de /encuestas/)
U30 = {}
for e in ENCS:
    if (HOY - date.fromisoformat(e['fin'])).days < 30 and not e['reest'] and enc.clave(e['casa']) not in U30:
        U30[enc.clave(e['casa'])] = e
PV = {}
for k, e in U30.items():
    try:
        PV[k] = enc.suma_pv(e)
    except (KeyError, ValueError):
        pass
MAYORIA = sum(a >= 176 for a, _ in PV.values())

# Escaños de Sumar / Frente Amplio en el hemiciclo del modelo de /encuestas/ (misma actualización)
_h = open(RAIZ / 'encuestas/index.html').read()
_D = json.JSONDecoder().raw_decode(_h[_h.find('window.__ENC=') + len('window.__ENC='):])[0]
SUMAR_MOD = next(a[1] for a in _D['hemi_modelo'] if a[0] == 'SUMAR')
assert SUMAR_MOD == 11, SUMAR_MOD
D40 = next(e for e in TRAS if enc.clave(e['casa']) == '40db')
D40_DIF = round(D40['voto']['PP'] - D40['voto']['PSOE'], 1)
# la distancia más corta de su tracking de campaña (entregas publicadas desde el 13-11, día 1)
_t40 = [round(e['voto']['PP'] - e['voto']['PSOE'], 1) for e in ENCS if enc.clave(e['casa']) == '40db' and _pub(e) >= '2026-11-13' and not e['reest']]
assert len(_t40) >= 8 and min(_t40) == D40_DIF and _t40.count(D40_DIF) == 1, _t40

print('MED', MED, 'MED0', MED0, DIF, DIF0, 'semana', len(SEM), len(CASAS_SEM), 'tras', [(e['casa'], e['inicio'], e['fin']) for e in TRAS],
      'ult', len(ULT), GANA_PP, DELANTE_PSOE, 'pv', len(PV), MAYORIA, 'min', MINDIA['d'], MIN_DIF, '40dB', D40_DIF)

# Gráfico 1: la mediana, partido a partido, frente a la de hace una semana (raya fina)
CSS_ULTIMO = '<style>' + '\n'.join(l for l in enc.ESTILOS.split('\n') if l.startswith(('.ultimo-graf', '.bu-')) or ('.bu-b i' in l and 'prefers-color-scheme' in l or l.startswith(':root[data-theme="dark"] .bu-b'))) + '</style>'
assert CSS_ULTIMO.count('.bu-') >= 8
g_med = enc.graficos_ultimo([({'casa': 'mediana', 'fin': HOY.isoformat(), 'voto': MED}, {'fin': SEMANA.isoformat(), 'voto': MED0},
                              f'Mediana de las {len(ULT)} encuestadoras · 21 de noviembre')])
g_med = (g_med.replace('Las últimas encuestas, partido a partido', 'La mediana de las encuestas, hoy y hace una semana')
         .replace('La raya fina marca lo que daba la encuesta anterior de la misma encuestadora',
                  'Mediana de la última encuesta de cada encuestadora de las tres últimas semanas. La raya fina marca la mediana del sábado 14')
         .replace(f'Cambio frente a su encuesta del {enc.dia(SEMANA.isoformat())}', 'Cambio frente a la mediana del sábado 14 de noviembre'))
assert 'mediana del sábado 14 de noviembre' in g_med and g_med.count('class="bu"') == 1
g_med = g_med.replace('</figure>', f'<p class="src">Fuente: <a href="{BASE}encuestas/">Encuestas elecciones generales 2026</a> de Mapa Electoral, con Electográfica y Wikipedia. '
                      'Sumar / Frente Amplio suma al Frente Amplio y a sus socios, que algunas encuestadoras publican por separado.</p></figure>')

# Gráfico 2: la distancia entre PP y PSOE en la mediana, día a día
SEMD = ['dom', 'lun', 'mar', 'mié', 'jue', 'vie', 'sáb']
dia_corto = lambda iso: f'{SEMD[(date.fromisoformat(iso).weekday() + 1) % 7]} {int(iso[8:])}'
g_dif = figura(f'La distancia en la mediana, de {p(DIF0)} a {p(DIF)} puntos en una semana',
               'Ventaja del PP sobre el PSOE en la mediana de las encuestas, en puntos, cada día del 14 al 21 de noviembre',
               barras([(dia_corto(r['d']), round(r['PP'] - r['PSOE'], 1), 'var(--pp)', 'PP +' + p(round(r['PP'] - r['PSOE'], 1))) for r in DIAS],
                      6, 'Ventaja del PP en la mediana de las encuestas, día a día', W=400, ml=70, fmt=p),
               f'Fuente: <a href="{BASE}encuestas/">Encuestas elecciones generales 2026</a>, mediana de la última encuesta de cada encuestadora con campo terminado en los 21 días anteriores.',
               leyenda=[('Ventaja del PP', 'var(--pp)')],
               tabla=(['Día', 'PP', 'PSOE', 'Vox', 'Distancia'], [[dia_corto(r['d']), p(r['PP']), p(r['PSOE']), p(r['VOX']), p(round(r['PP'] - r['PSOE'], 1))] for r in DIAS]))

# Gráfico 3: la ventaja en la última encuesta de cada encuestadora
_v = lambda e: round(e['voto']['PP'] - e['voto']['PSOE'], 1)
_ord = sorted(ULT.values(), key=lambda e: -_v(e))
g_ven = figura(f'{GANA_PP} de {len(ULT)} encuestadoras ponen por delante al PP',
               'Ventaja del primero sobre el segundo, PP o PSOE, en puntos, en la última encuesta de cada encuestadora de las tres últimas semanas',
               barras([(enc.nombre_casa(e['casa']), abs(_v(e)), 'var(--pp)' if _v(e) > 0 else 'var(--psoe)',
                        f'{"PP" if _v(e) > 0 else "PSOE"} +{p(abs(_v(e)))}') for e in _ord],
                      8, 'Ventaja del PP o del PSOE en cada encuesta', W=400, ml=118, separar=True),
               f'Fuente: <a href="{BASE}encuestas/">Encuestas elecciones generales 2026</a>, con el enlace a cada encuesta; datos de la actualización de las 4.56 del 21 de noviembre. La de Data10 de esta mañana (PP +5,7) entra en la siguiente.',
               leyenda=[('Por delante, el PP', 'var(--pp)'), ('Por delante, el PSOE', 'var(--psoe)')],
               tabla=(['Encuestadora', 'Medio', 'Fin del campo', 'PP (%)', 'PSOE (%)', 'Vox (%)'],
                      [[enc.nombre_casa(e['casa']), e['medio'] or '–', enc.dia(e['fin']), p(e['voto']['PP']), p(e['voto']['PSOE']), p(e['voto']['VOX'])] for e in _ord]))

# Citas del debate (19-11-2026)
INFOBAE = 'https://www.infobae.com/espana/2026/11/19/los-8-momentos-del-debate-cara-a-cara-entre-sanchez-y-feijoo-del-que-pongan-los-dos-rombos-al-no-me-deja-hablar/'
PAIS40 = 'https://elpais.com/espana/elecciones-generales/2026-11-20/la-distancia-entre-el-pp-y-el-psoe-se-estrecha-al-minimo-pese-a-la-victoria-de-feijoo-en-el-debate.html'
OKD = 'https://okdiario.com/espana/debate-impulsa-pp-hasta-135-escanos-costa-vox-psoe-que-retrocede-4-diputados-21236645'
RTVE = 'https://x.com/rtvenoticias/status/2123546350360961071'
OBJ = 'https://theobjective.com/espana/politica/2026-11-20/debate-sanchez-feijoo-directo/directo/'

nom_tras = ', '.join(f'{enc.nombre_casa(e["casa"])}' for e in TRAS[:-1]) + f' y {enc.nombre_casa(TRAS[-1]["casa"])}'
cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">El jueves por la noche, Pedro Sánchez y Alberto Núñez Feijóo se vieron en el único cara a cara de las elecciones generales del 29N. {L('debate-sanchez-feijoo-29n', 'Lo vieron de media 10.152.000 personas')}, con un 70,8 % de cuota de pantalla, según Barlovento Comunicación: un 72 % más que el de 2023 y el más visto desde 2011. En su último minuto, Feijóo pidió el voto así, según el vídeo que publicó <a href="{RTVE}">RTVE Noticias</a>:</p>
<blockquote class="cita"><p>«No bailo en los mítines y no me gusta la política espectáculo, pero tampoco robo, ni miento, ni me voy de vacaciones cuando se invade nuestro país. Creo en la política como servicio»</p><footer>Alberto Núñez Feijóo, en el minuto final del debate, el 19 de noviembre de 2026, según <a href="{RTVE}">RTVE Noticias</a>.</footer></blockquote>
<p data-tipo="contexto">Sánchez cerró el debate, por sorteo, y pidió el voto para el PSOE a quien duda si ir a votar:</p>
<blockquote class="cita"><p>«Quien pueda votar, que vote. Vota con toda tu alma, vota con toda tu fuerza»</p><footer>Pedro Sánchez, en el minuto final del debate, el 19 de noviembre de 2026, según <a href="{INFOBAE}">Infobae</a> y <a href="{OBJ}">The Objective</a>.</footer></blockquote>
<p data-tipo="contexto">Fue también la semana en que acabó el plazo para pedir el voto por correo, la de los programas electorales y la última con encuestas: la ley prohíbe publicarlas desde el martes 24, así que el lunes 23 es el último día. Del domingo 15 al viernes 20 publicamos 23 piezas en esta sección. Esta es la semana contada desde los mapas.</p>

<h2>Las encuestas: el PP, delante, y la distancia, a la baja</h2>
<p data-tipo="dato">La mediana de la última encuesta de cada una de las {len(ULT)} encuestadoras de las tres últimas semanas, la que resume nuestra página de <a href="{BASE}encuestas/">encuestas de las elecciones generales 2026</a>, da hoy al PP el {p(MED['PP'])} %, al PSOE el {p(MED['PSOE'])} % y a Vox el {p(MED['VOX'])} %: <strong>{p(DIF)} puntos de ventaja para el PP</strong>. El sábado pasado eran {p(DIF0)}. La distancia más corta de la semana fue la del jueves {int(MINDIA['d'][8:])}, {p(MIN_DIF)} puntos.</p>
{CSS_ULTIMO}
{g_med}
<p data-tipo="dato">Del domingo 15 al viernes 20 se publicaron {len(SEM)} encuestas de {len(CASAS_SEM)} encuestadoras, muchas de ellas entregas diarias de un mismo tracking. {GANA_PP} de las {len(ULT)} encuestadoras de la mediana ponen por delante al PP; solo {DELANTE_PSOE[0]} da ganador al PSOE. De las {len(PV)} que publican escaños en el último mes, {MAYORIA} dan a PP y Vox juntos 176 o más, contando el extremo bajo de su horquilla.</p>
{g_dif}
<p data-tipo="dato">Tres de las encuestas del viernes, las de {nom_tras}, incluyen ya entrevistas del día después del debate, aunque mezcladas con otras de días anteriores. La de <a href="{PAIS40}">40dB. para El País y la SER</a> deja al PP en el {p(D40['voto']['PP'])} % y al PSOE en el {p(D40['voto']['PSOE'])} %: {p(D40_DIF)} puntos, la distancia más corta de su tracking de campaña. Esta mañana, <a href="{OKD}">Data10 para OKDiario</a>, con entrevistas del 17 al 20, da al PP el 32,3 % y al PSOE el 26,6 %. El jueves por la mañana, {L('encuestas-elecciones-generales-2026-19-noviembre', 'Sondaxe había dejado al PSOE a 0,7 puntos del PP')}, y el miércoles {L('encuesta-40db-vox-17-29n', 'Vox bajó al 17 % en 40dB.')}</p>
{g_ven}

<h2>Lo que las encuestas no dicen</h2>
<p data-tipo="dato">Una cifra resumen esconde cuánto discrepan las encuestadoras. {L('cuanto-discrepan-encuestas-29n', 'En el PSOE van del 25,5 % al 33,3 %')}; en Vox casi coinciden. Y la última vez fallaron en la misma dirección: {L('encuestas-error-2023-2019-29n', 'en 2023, las últimas encuestas daban al PP 5,7 puntos de ventaja y ganó por 1,4')}. Tras el cara a cara de aquel año, {L('encuestas-tras-el-debate-2023-29n', '10 de 14 encuestadoras ampliaron la ventaja del PP')}, y trece días después la distancia fue mucho menor. Cuánto pesa el debate de este jueves lo dirán las encuestas del fin de semana y del lunes.</p>
<p data-tipo="dato">En la izquierda del PSOE, el jueves {L('frente-amplio-17-provincias-29n', 'el modelo de encuestas daba escaño al Frente Amplio en 5 de las 17 provincias')} donde aspira a sacarlo. Hoy, el modelo da {SUMAR_MOD} diputados a Sumar y el Frente Amplio en toda España; Sumar sacó 31 en 2023, con Podemos dentro.</p>

<h2>Los mapas de la campaña</h2>
<p data-tipo="dato">El lunes, Feijóo hizo campaña con UPN en Pamplona, donde {L('feijoo-pamplona-upn-pp-secciones-29n', 'el PSOE fue el más votado en 77 de las 151 secciones')} en 2023. El martes estuvo en Gipuzkoa, donde {L('feijoo-gipuzkoa-hernani-pp-29n', 'al PP le faltaron 9.793 votos en 2023')} para recuperar el diputado que no saca desde 2011. Y el jueves, el día del debate, Santiago Abascal dio un mitin en Gijón, donde {L('vox-gijon-barrios-abascal-29n', 'Vox sacó su mejor resultado en Somió, el barrio más rico: el 17,0 %')}.</p>
<p data-tipo="patron">El martes publicamos {L('abstencion-mapa-ganador-29n', 'el mapa que nadie enseña antes de unas elecciones')}: el de la abstención. En 2023 no votaron 10,4 millones de residentes, y si la abstención fuera un partido habría quedado por delante del ganador en la mitad de las secciones de España. El miércoles, que {L('secciones-cambian-ganador-29n', 'una de cada tres secciones cambió de ganador entre 2019 y 2023')}: en 5.970 pasó del PSOE al PP, y al revés solo en 100.</p>

<h2>Cómo, cuándo y qué se vota</h2>
<p data-tipo="dato">El plazo para pedir el voto por correo acabó el jueves 19. En 2023 se aceptaron 2.604.386 solicitudes de residentes en España, y {L('voto-correo-plazo-jueves-29n', 'en 51 de las 52 circunscripciones')} hubo más solicitudes que votos le faltaron a la lista que se quedó más cerca del último escaño. El voto por correo se puede depositar hasta el miércoles 25.</p>
<p data-tipo="dato">El domingo 29, {L('como-votar-elecciones-generales-29n', 'los colegios abren de 9.00 a 20.00')}, y basta el DNI, el pasaporte o el carné de conducir. De los electores residentes en España, 1.615.127 {L('generacion-2008-primer-voto-29n', 'votan por primera vez en unas generales')}. Los colegios cierran a las 20.00, pero {L('a-que-hora-resultados-elecciones-generales-29n', 'en 2023 los primeros resultados llegaron a las 21.00')}, al cerrar Canarias.</p>
<p data-tipo="dato">El jueves repasamos {L('programa-electoral-29n', 'los programas de PP, PSOE, Vox y Frente Amplio')}: en vivienda, el PP promete un millón de viviendas; el PSOE, un parque público de 100.000, y el Frente Amplio, 1,5 millones de viviendas públicas en 12 años. Vox no da una cifra.</p>

<h2>Fútbol, historia y fuera de España</h2>
<p data-tipo="dato">El domingo, el día del España-Inglaterra en el Metropolitano, contamos que {L('seleccion-convocados-pueblos-29n', 'de los 25 convocados de De la Fuente nacidos en España, 15 nacieron donde ganó el PSOE en 2023')} y 8 donde ganó el PP. Esta tarde, a las 18.30, se juega el Sevilla-Betis: {L('derbi-sevillano-nervion-heliopolis-29n', 'el derbi sevillano se juega en barrios del PP')}, en una ciudad donde el PSOE ganó en más secciones.</p>
<p data-tipo="dato">En la serie de historia electoral explicamos {L('ley-electoral-segunda-republica', 'la ley electoral de la Segunda República')}: en Jaén, en 1936, ganar por 1,6 puntos valía 10 de los 13 diputados. Y en Cabo Verde, {L('cabo-verde-presidenciales-neves-rosa-mapa', 'José Maria Neves fue reelegido en primera vuelta')} con el 63,8 % de los votos, según los resultados provisionales.</p>

<h2>Lo que viene</h2>
<p data-tipo="contexto">Queda una semana. Las encuestas se pueden publicar hasta el lunes 23; del martes 24 al domingo 29, la ley lo prohíbe, como contamos en {L('veda-encuestas-29n', 'la pieza de la veda')}. La <a href="{BASE}encuestas/">página de encuestas</a> se actualiza hasta entonces. El sábado 28 es la jornada de reflexión, y el domingo 29 los resultados de cada municipio estarán en el mapa en cuanto Interior empiece a darlos, hacia las 21.00. Esta crónica no atribuye a ningún hecho de la semana un efecto en el voto: las encuestas recogen cambios, pero no sus causas.</p>
'''

semana = [('seleccion-convocados-pueblos-29n', 'Los convocados de la selección y sus pueblos'),
          ('generacion-2008-primer-voto-29n', 'La generación de 2008 estrena voto'),
          ('encuestas-primera-semana-campana-29n', 'Las encuestas de la primera semana de campaña'),
          ('feijoo-pamplona-upn-pp-secciones-29n', 'Feijóo en Pamplona: UPN-PP sección a sección'),
          ('feijoo-gipuzkoa-hernani-pp-29n', 'Feijóo en Gipuzkoa y el diputado que el PP no recupera'),
          ('encuestas-error-2023-2019-29n', 'Cuánto se equivocaron las encuestas la última vez'),
          ('abstencion-mapa-ganador-29n', 'El mapa de la abstención'),
          ('voto-correo-plazo-jueves-29n', 'El plazo del voto por correo'),
          ('encuestas-tras-el-debate-2023-29n', 'Qué hicieron las encuestas tras el debate de 2023'),
          ('ley-electoral-segunda-republica', 'La ley electoral de la Segunda República'),
          ('secciones-cambian-ganador-29n', 'Las secciones que cambiaron de ganador'),
          ('cuanto-discrepan-encuestas-29n', 'Cuánto discrepan las encuestas'),
          ('encuesta-40db-vox-17-29n', 'Vox baja al 17 % en 40dB.'),
          ('encuestas-elecciones-generales-2026-18-noviembre', 'Encuestas del 18 de noviembre'),
          ('encuestas-elecciones-generales-2026-19-noviembre', 'Encuestas del 19 de noviembre'),
          ('debate-sanchez-feijoo-29n', 'Debate Sánchez Feijóo'),
          ('frente-amplio-17-provincias-29n', 'El Frente Amplio en sus 17 provincias'),
          ('vox-gijon-barrios-abascal-29n', 'Vox en Gijón, barrio a barrio'),
          ('programa-electoral-29n', 'Los programas electorales'),
          ('encuestas-elecciones-generales-2026-20-noviembre', 'Encuestas del 20 de noviembre'),
          ('veda-encuestas-29n', 'La veda de encuestas'),
          ('como-votar-elecciones-generales-29n', 'Cómo votar el 29N'),
          ('a-que-hora-resultados-elecciones-generales-29n', 'A qué hora se sabrán los resultados')]
assert len(semana) == 23 and len({s for s, _ in semana}) == 23
for s, _ in semana:
    assert (RAIZ / 'actualidad' / s / 'index.html').exists(), s
cuerpo += ('<div class="resumen"><b>La semana, pieza a pieza</b><ul>' + ''.join(f'<li>{L(s, t)}</li>' for s, t in semana) + '</ul></div>\n')

preguntas = [
    ('¿Qué dicen las encuestas a una semana de las elecciones generales del 29N?',
     f'La mediana de las {len(ULT)} encuestadoras de las tres últimas semanas da al PP el {p(MED["PP"])} %, al PSOE el {p(MED["PSOE"])} % y a Vox el {p(MED["VOX"])} %: {p(DIF)} puntos de ventaja para el PP, frente a {p(DIF0)} hace una semana. {GANA_PP} de las {len(ULT)} ponen por delante al PP.'),
    ('¿Cuándo es el último día para publicar encuestas?',
     'El lunes 23 de noviembre. La ley electoral prohíbe publicarlas desde el martes 24 hasta el cierre de los colegios el domingo 29.'),
    ('¿Cuánta gente vio el debate Sánchez Feijóo?',
     'De media, 10.152.000 personas, con un 70,8 % de cuota de pantalla, según Barlovento Comunicación: un 72 % más que el cara a cara de 2023.'),
]
enlaces = (f'{L("dos-semanas-29n-la-semana-en-el-mapa", "La crónica del sábado anterior")} · <a href="{BASE}encuestas/">Encuestas elecciones generales 2026</a> · '
           f'<a href="{BASE}encuestas/provincias.html">Encuestas por provincias</a> · {L("debate-sanchez-feijoo-29n", "Debate Sánchez Feijóo")}')
foot = ('Datos: piezas de Mapa Electoral de la semana del 15 al 20 de noviembre de 2026, enlazadas en cada párrafo, donde se explica cada cálculo; '
        'encuestas recogidas por Electográfica y Wikipedia y mediana de mapaelectoral.es/encuestas a 21 de noviembre de 2026. Cálculo: actualidad/src/resumenes/una_semana.py.')

TIT = (f'A una semana del 29N, la mediana de las encuestas da al PP {p(DIF)} puntos de ventaja, {p(BAJA)} menos que hace siete días; '
       'el lunes 23 es el último día para publicarlas')
DEK = (f'La semana del debate de las elecciones generales: 10,2 millones de personas vieron el cara a cara, {GANA_PP} de {len(ULT)} encuestadoras siguen '
       'dando ganador al PP y la distancia con el PSOE se estrecha. La semana del 15 al 20 de noviembre, contada desde los mapas.')
_r = lambda e: {'casa': enc.nombre_casa(e['casa']), 'fin': e['fin'], 'PP': e['voto']['PP'], 'PSOE': e['voto']['PSOE'], 'VOX': e['voto']['VOX']}
DATOS = {'MED': MED, 'MED0': MED0, 'DIF': DIF, 'DIF0': DIF0, 'BAJA': BAJA, 'DIAS': DIAS, 'MIN_DIF': MIN_DIF, 'NSEM': len(SEM), 'NCASAS_SEM': len(CASAS_SEM),
         'ULT': [_r(e) for e in _ord], 'NULT': len(ULT), 'GANA_PP': GANA_PP, 'NPV': len(PV), 'MAYORIA': MAYORIA, 'TRAS': [_r(e) for e in TRAS],
         'D40': _r(D40), 'SUMAR_MOD': SUMAR_MOD, 'D40_DIF': D40_DIF, 'SEMANA': [s for s, _ in semana]}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
if __name__ == '__main__':
    print(TIT)
    print(DEK)
    pieza('una-semana-29n-la-semana-en-el-mapa', 'A una semana del 29N: la semana en el mapa', TIT, DEK, '21 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, datos_js)
