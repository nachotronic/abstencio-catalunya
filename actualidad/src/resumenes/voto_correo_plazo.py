"""Voto por correo para el 29N: el plazo acaba el jueves 19 de noviembre (pieza del 17-11-2026).

Solicitudes aceptadas en 2023 por provincia (INE, Oficina del Censo Electoral, tabla 59759) y por fecha de recepción
(tabla 59763, por fecha de recepción), guardadas en actualidad/src/resumenes/datos/ine_5975*_voto_correo_2023_*.json.
Último escaño de 2023: D'Hondt con barrera del 3 % sobre los votos con voto exterior de actualidad/src/sistema/simulador.json
(el mismo cálculo que reproduce los 350 escaños oficiales). Votos que le faltaron a la lista que se quedó más cerca: el cociente
del último escaño por sus escaños más uno, menos sus votos, más uno, sin quitarle votos a nadie.
Uso, desde la raíz: python3 actualidad/src/resumenes/voto_correo_plazo.py
"""
import json
import unicodedata

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import COL, p

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
SLUG = 'voto-correo-plazo-jueves-29n'
DAT = RAIZ / 'actualidad/src/resumenes/datos'
CORREOS26 = 'https://www.correos.com/sala-prensa/la-junta-electoral-central-amplia-el-plazo-para-depositar-el-voto-por-correo-hasta-el-jueves-26-de-noviembre-como-maximo-hasta-las-1400-horas/'
CORREOS = 'https://www.correos.com/en/sala-prensa/el-proximo-jueves-19-de-noviembre-finaliza-el-plazo-para-solicitar-el-voto-por-correo/'
MONCLOA = 'https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/interior/paginas/voto-por-correo-elecciones-generales-29n.aspx'
INE = 'https://www.ine.es/jaxi/Tabla.htm?tpx=59759'
INE_F = 'https://www.ine.es/jaxi/Tabla.htm?tpx=59763'


def clave(t):
    return unicodedata.normalize('NFKD', t.split('/')[0].strip()).encode('ascii', 'ignore').decode().lower()


ALIAS = {'alava': 'araba', 'baleares': 'balears, illes', 'illes balears': 'balears, illes', 'a coruna': 'coruna, a', 'la rioja': 'rioja, la', 'las palmas': 'palmas, las'}
T59 = json.load(open(DAT / 'ine_59759_voto_correo_2023_provincias.json'))
ACEP = {clave(x['Nombre'].rsplit(', ', 1)[0]): x['Data'][0]['Valor'] for x in T59 if x['Nombre'].endswith(', Aceptadas')}
PCT = {clave(x['Nombre'].rsplit(', ', 1)[0]): x['Data'][0]['Valor'] for x in T59 if x['Nombre'].endswith(', Porcentaje sobre electores')}
TOTAL = ACEP.pop('total')
assert TOTAL == 2604386 and abs(sum(ACEP.values()) - TOTAL) < 1, sum(ACEP.values())

T63 = json.load(open(DAT / 'ine_59763_voto_correo_2023_fechas.json'))
FECHAS = {x['Nombre'].split(', ', 1)[1]: x['Data'][0]['Valor'] for x in T63 if x['Nombre'].startswith('Total, ')}
assert FECHAS['TOTAL'] == TOTAL
ULT2 = FECHAS['De 30/06 a 13/07']
POST = FECHAS['Posterior a 13/07/2023']
TRAMOS = [('Hasta el 1 de junio', FECHAS['Hasta el 01/06']), ('Del 2 al 15 de junio', FECHAS['De 02/06 a 15/06']),
          ('Del 16 al 29 de junio', FECHAS['De 16/06 a 29/06']), ('Del 30 de junio al 13 de julio', ULT2), ('Después del 13 de julio', POST)]
assert abs(sum(v for _, v in TRAMOS) - TOTAL) < 1

# --- Último escaño de 2023 ---
# Margen del último escaño con todas las candidaturas y el voto exterior (actualidad/src/sistema/cifras.json, calculado por
# sistema/calcular.py desde los datos de Interior por candidatura): simulador.json agrupa en «Otros» listas que pasaron del 3 %,
# como Teruel Existe, Soria ¡Ya!, Por Ávila o UPL (editor, 17-11-2026).
CIF = json.load(open(RAIZ / 'actualidad/src/sistema/cifras.json'))['2023_07']['provincias']
FILAS = []
for c, x in CIF.items():
    nm = clave(x['nombre'])
    FILAS.append(dict(cod=c, nom=x['nombre'], esc=x['escanos'], ultimo=x['ultimo'], cerca=x['aspirante'], falta=x['votos_faltan'],
                      sol=ACEP[ALIAS.get(nm, nm)], pct=PCT[ALIAS.get(nm, nm)]))
FILAS.sort(key=lambda f: f['falta'])
NPROV = len(FILAS)
MAS = [f for f in FILAS if f['sol'] > f['falta']]
MENOS = [f['nom'] for f in FILAS if f['sol'] <= f['falta']]
assert NPROV == 52 and len(MAS) == 51 and MENOS == ['Melilla'], MENOS
F = {f['nom']: f for f in FILAS}
GIR, CANT = F['Girona'], F['Cantabria']
assert (F['Teruel']['falta'], F['Teruel']['cerca']) == (1946, 'Teruel Existe')
assert (GIR['falta'], GIR['ultimo'], GIR['cerca']) == (285, 'Junts', 'PP') and (CANT['falta'], CANT['ultimo'], CANT['cerca']) == (404, 'Vox', 'PP')
MIL = [f for f in FILAS if f['falta'] < 1000]
DIEZ = FILAS[:12]

# --- Gráficos ---
g_tramos = figura(f'En 2023, una de cada tres solicitudes de voto por correo llegó en las dos últimas semanas del plazo',
                  'Solicitudes de voto por correo aceptadas en las generales de julio de 2023, según su fecha de recepción. El plazo para pedirlo acabó el 13 de julio',
                  barras([(t, v, 'var(--muted)', n(v)) for t, v in TRAMOS], max(v for _, v in TRAMOS) * 1.05,
                         'Solicitudes de voto por correo por fecha en 2023', W=400, ml=150, fmt=n),
                  f'Fuente: <a href="{INE_F}">INE, Oficina del Censo Electoral</a>, solicitudes aceptadas por fecha de recepción. Cálculo propio.',
                  None,
                  (['Fecha de recepción', 'Solicitudes aceptadas', '% del total'], [[t, n(v), p(v / TOTAL * 100)] for t, v in TRAMOS]))

g_escano = figura(f'En Girona, el último escaño de 2023 se decidió por {n(GIR["falta"])} votos; {n(GIR["sol"])} electores habían pedido votar por correo',
                  'Las 12 circunscripciones donde menos votos le faltaron en 2023 a la lista que se quedó más cerca del último escaño, y solicitudes de voto por correo aceptadas en cada una',
                  barras([(f['nom'], f['falta'], 'var(--muted)', f'{n(f["falta"])} · {n(f["sol"])} por correo') for f in DIEZ], max(f['falta'] for f in DIEZ) * 2.1,
                         'Votos que faltaron para el último escaño en 2023', W=400, ml=150, fmt=n, separar=True),
                  'Fuente: Ministerio del Interior, resultados con voto exterior, e INE, solicitudes de voto por correo aceptadas. La barra es la diferencia de votos; la cifra de la derecha, las solicitudes. Cálculo propio.',
                  None,
                  (['Circunscripción', 'Escaños', 'Último escaño', 'Lista más cerca', 'Votos que le faltaron', 'Solicitudes de voto por correo'],
                   [[f['nom'], str(f['esc']), f['ultimo'], f['cerca'], n(f['falta']), n(f['sol'])] for f in FILAS]))

# --- Texto ---
cuerpo = f'''
<p data-tipo="dato">Actualización del 25 de noviembre, a las 12.30. El plazo para pedir el voto por correo acabó el jueves 19. Quien lo pidió puede depositarlo en cualquier oficina de Correos hasta el jueves 26 de noviembre, en su horario habitual y como máximo hasta las 14.00: la Junta Electoral Central amplió un día el plazo, que acababa el miércoles 25, según <a href="{CORREOS26}">Correos</a>.</p>
<p data-tipo="contexto">El voto por correo para las elecciones generales del 29N se puede pedir hasta el jueves 19 de noviembre, incluido, en cualquier oficina de Correos o en su web con certificado digital o DNI electrónico, según <a href="{CORREOS}">Correos</a>. La documentación llega a casa desde el 9 de noviembre y el voto se puede depositar hasta el jueves 26 de noviembre, como máximo a las 14.00. Quien lo pide y se lo aceptan ya no puede votar en su mesa el 29 de noviembre, recuerda el <a href="{MONCLOA}">Ministerio del Interior</a>. Ni Correos ni el Censo Electoral han publicado todavía cuántas solicitudes llevan.</p>
<p data-tipo="dato">En las generales de julio de 2023 se aceptaron {n(TOTAL)} solicitudes de electores residentes en España, según el <a href="{INE}">INE</a>, y buena parte llegó al final: {n(ULT2)}, el {p(ULT2 / TOTAL * 100)} %, se recibieron en las dos últimas semanas del plazo, del 30 de junio al 13 de julio. Otras {n(POST)} constan como recibidas después.</p>
{g_tramos}
<p data-tipo="dato">Hay escaños que se deciden por poco. En 2023, en {len(MAS)} de las {NPROV} circunscripciones hubo más solicitudes de voto por correo que votos le faltaron a la lista que se quedó más cerca del último escaño. En Girona, al PP le faltaron {n(GIR["falta"])} votos para quitarle el último diputado a Junts, y {n(GIR["sol"])} electores de la provincia habían pedido votar por correo. En Cantabria, al PP le faltaron {n(CANT["falta"])} para quitárselo a Vox; las solicitudes fueron {n(CANT["sol"])}. La única excepción fue la ciudad autónoma de Melilla, donde la diferencia fue mayor que las solicitudes. En Teruel, a Teruel Existe le faltaron {n(F["Teruel"]["falta"])} votos para conservar el diputado que tenía desde 2019; hubo {n(F["Teruel"]["sol"])} solicitudes de voto por correo.</p>
{g_escano}
<p data-tipo="contexto">La cuenta no dice que el voto por correo cambiara ningún escaño, porque no se sabe a quién se votó por correo. Dice que en casi todas las circunscripciones el último diputado se decidió por menos votos de los que se pidieron por correo. Hay más datos sobre quién lo pide y dónde en {L("voto-correo-29n", "esta pieza sobre el voto por correo desde 2004")}.</p>
'''

preguntas = [
    ('¿Hasta cuándo se puede pedir el voto por correo para las elecciones generales del 29N?',
     f'Hasta el jueves 19 de noviembre de 2026, incluido, en una oficina de Correos o en su web. El voto se puede depositar en Correos hasta el jueves 26 de noviembre, como máximo a las 14.00, según <a href="{CORREOS}">Correos</a>.'),
    ('Si pido el voto por correo, ¿puedo votar en la mesa el 29N?',
     f'No. Si la solicitud se acepta, ya no se puede votar en persona, según el <a href="{MONCLOA}">Ministerio del Interior</a>.'),
    ('¿Cuánta gente pidió el voto por correo en 2023?',
     f'Se aceptaron {n(TOTAL)} solicitudes de electores residentes en España, según el INE. {n(ULT2)} se recibieron en las dos últimas semanas del plazo.'),
]
enlaces = f'{L("voto-correo-29n", "El voto por correo, provincia a provincia")} · <a href="{BASE}elecciones/votar-29n/">Dónde y cómo votar el 29N</a>'
foot = ('Datos: INE, Oficina del Censo Electoral, solicitudes de voto por correo aceptadas en 2023 por provincia y por fecha de recepción (tablas 59759 y 59763); '
        'Ministerio del Interior, resultados de 2023 con voto exterior. Cálculo: actualidad/src/resumenes/voto_correo_plazo.py.')

DATOS = {'TOTAL': TOTAL, 'ULT2': ULT2, 'POST': POST, 'TRAMOS': TRAMOS, 'NPROV': NPROV, 'MAS': len(MAS), 'MENOS': MENOS,
         'F': {f['nom']: {k: f[k] for k in ('falta', 'sol', 'ultimo', 'cerca', 'esc')} for f in FILAS}}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'Voto por correo',
      'Voto por correo para las elecciones generales del 29N: el plazo para pedirlo acaba el jueves 19; en 2023, una de cada tres solicitudes llegó en las dos últimas semanas',
      f'El voto se puede depositar hasta el jueves 26 de noviembre, como máximo a las 14.00. En 2023, en {len(MAS)} de las {NPROV} circunscripciones hubo más solicitudes que votos le faltaron a la lista más cercana al último escaño. '
      f'En Girona, el último diputado se decidió por {n(GIR["falta"])} votos; {n(GIR["sol"])} electores habían pedido votar por correo.',
      '17 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('TOTAL', TOTAL, 'ULT2', ULT2, round(ULT2 / TOTAL * 100, 1), 'POST', POST, 'MAS', len(MAS), NPROV, MENOS, [(f['nom'], f['falta'], f['sol']) for f in MIL])
