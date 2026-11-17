"""Debate Sánchez-Feijóo del 19-11-2026: qué hicieron las encuestas tras el cara a cara de 2023 (10 de julio).

Encuestas: previsiones/datos/encuestas/encuestas_limpias.csv (Electográfica). Para cada empresa, su última encuesta nacional
publicada del 26 de junio al 10 de julio de 2023 (antes del debate, que fue esa noche) y su última del 11 al 17 de julio
(después, hasta la veda). Solo las empresas con encuesta en los dos tramos. Mismo desempate que encuestas_error_2023.py.
Resultado: actualidad/src/sistema/simulador.json (con voto exterior). Hoy: modelo de /encuestas/ (última versión).
Uso, desde la raíz: python3 actualidad/src/resumenes/debate_cara_a_cara.py
"""
import json
import re

import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import COL, grupos, p

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
SLUG = 'debate-sanchez-feijoo-encuestas-29n'
ELDIARIO = 'https://www.eldiario.es/vertele/noticias/debate-cara-a-cara-sanchez-feijoo-sera-jueves-19-noviembre-academia-tv_1_13662406.html'
INFOBAE = 'https://www.infobae.com/espana/2026/11/16/rtve-atresmedia-y-la-septima-emitiran-el-cara-a-cara-de-sanchez-y-feijoo-en-directo-donde-y-cuando-ver-el-debate-electoral/'
AUD23 = 'https://www.eldebate.com/cine-tv-series/20230711/el-debate-entre-feijoo-y-pedro-sanchez-lidera-la-audiencia-pero-es-el-menos-visto-de-la-historia_127320.html'
ELECTO = 'https://www.electografica.com/'

e = pd.read_csv(RAIZ / 'previsiones/datos/encuestas/encuestas_limpias.csv')
e = e[e.ambito == 'ESPAÑA'].copy()
e['gap'] = e.PP - e.PSOE


def orden_url(u):
    m = re.search(r'(\d{6})(?:-(\d+))?\.html$', str(u))
    return (m.group(1), int(m.group(2) or 1)) if m else ('', 0)


e['_ord'] = e.url_agregador.map(orden_url)
e = e.sort_values(['publicado', '_ord'], kind='stable')
NOMS = {'Cis': 'CIS', 'SigmaDos': 'Sigma Dos', 'InvyMark': 'Invymark', 'Atlasintel': 'AtlasIntel', 'Yougov': 'YouGov',
        'Data10 - Demoscopia y Servicios': 'Data10'}
ANT = e[e.publicado.between('2023-06-26', '2023-07-10')].groupby('encuestadora').tail(1).set_index('encuestadora')
DES = e[e.publicado.between('2023-07-11', '2023-07-17')].groupby('encuestadora').tail(1).set_index('encuestadora')
C = ANT.index.intersection(DES.index)
X = pd.DataFrame({'antes': ANT.loc[C, 'gap'], 'despues': DES.loc[C, 'gap'], 'fa': ANT.loc[C, 'publicado'], 'fd': DES.loc[C, 'publicado'],
                  'ppa': ANT.loc[C, 'PP'], 'ppd': DES.loc[C, 'PP'], 'psa': ANT.loc[C, 'PSOE'], 'psd': DES.loc[C, 'PSOE']})
X['d'] = X.despues - X.antes
X['nom'] = [NOMS.get(k, k) for k in X.index]
N, SUBE, BAJA = len(X), int((X.d > 0).sum()), int((X.d < 0).sum())
MA, MD = float(X.antes.mean()), float(X.despues.mean())
DPP, DPS = float((X.ppd - X.ppa).mean()), float((X.psd - X.psa).mean())
assert (N, SUBE, BAJA) == (14, 10, 4), (N, SUBE, BAJA)
# Que no dependa de las encuestas publicadas el 11 y el 12, con parte del campo antes del debate
DES13 = e[e.publicado.between('2023-07-13', '2023-07-17')].groupby('encuestadora').tail(1).set_index('encuestadora')
C13 = ANT.index.intersection(DES13.index)
assert len(C13) == N and int(((DES13.loc[C13, 'gap'] - ANT.loc[C13, 'gap']) > 0).sum()) == SUBE

SIM = json.load(open(RAIZ / 'actualidad/src/sistema/simulador.json'))
tot, val = {}, 0
for x in SIM['elecciones']['2023_07'].values():
    val += x['validos']
    for k, v in x['v'].items():
        tot[k] = tot.get(k, 0) + v
GAP23 = (tot['PP'] - tot['PSOE']) / val * 100
assert round(GAP23, 1) == 1.4

HJ = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
MED = json.load(open(HJ))['meta']['media_encuestas']
HOY = MED['PP'] - MED['PSOE']
_a, _m, _d, _hm = HJ.stem.split('-')
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de noviembre de {_a}'

FIL = X.sort_values('d')
g_cambio = figura(f'Tras el cara a cara de 2023, {SUBE} de {N} empresas ampliaron la ventaja del PP sobre el PSOE',
                  'Cambio en la ventaja del PP sobre el PSOE entre la última encuesta de cada empresa publicada antes del debate del 10 de julio de 2023 y la última publicada después, hasta la veda, en puntos',
                  barras([(r.nom, abs(r.d), COL['PP'] if r.d > 0 else COL['PSOE'], ('+' if r.d > 0 else '−') + p(abs(r.d))) for r in FIL.itertuples()],
                         4, 'Cambio en la ventaja del PP tras el debate de 2023 por empresa', W=400, ml=110, fmt=p),
                  f'Fuente: encuestas recopiladas por <a href="{ELECTO}">Electográfica</a>. Antes: última encuesta publicada del 26 de junio al 10 de julio; después: última del 11 al 17 de julio. Solo las {N} empresas con encuesta en los dos tramos. Cálculo propio.',
                  [('Sube la ventaja del PP', COL['PP']), ('Baja', COL['PSOE'])],
                  (['Empresa', 'Antes (fecha)', 'PP menos PSOE antes', 'Después (fecha)', 'PP menos PSOE después', 'Cambio'],
                   [[r.nom, r.fa, ('+' if r.antes >= 0 else '−') + p(abs(r.antes)), r.fd, ('+' if r.despues >= 0 else '−') + p(abs(r.despues)), ('+' if r.d > 0 else '−') + p(abs(r.d))]
                    for r in FIL.itertuples()]))

ESC = [('Antes del debate', MA), ('Después del debate', MD), ('Resultado del 23 de julio', GAP23)]
g_media = figura(f'La media de esas {N} empresas pasó de {p(MA)} a {p(MD)} puntos de ventaja para el PP; las urnas le dieron {p(GAP23)}',
                 f'Ventaja del PP sobre el PSOE en 2023, en puntos: media de las {N} empresas antes y después del cara a cara, y resultado con voto exterior',
                 grupos([(t, [(v, COL['PP'], 1, 'ventaja del PP')]) for t, v in ESC], 7, 'Ventaja del PP antes y después del debate de 2023 y resultado', W=400, ml=150),
                 f'Fuente: encuestas recopiladas por <a href="{ELECTO}">Electográfica</a> y Ministerio del Interior. Cálculo propio.',
                 None,
                 (['Momento', 'PP menos PSOE (puntos)'], [[t, p(v)] for t, v in ESC]))

cuerpo = f'''
<p data-tipo="contexto">Pedro Sánchez y Alberto Núñez Feijóo se verán en el cara a cara de las elecciones generales del 29N el jueves 19 de noviembre a las 22.00, en un debate organizado por la Academia de Televisión y moderado por su presidenta, María Casado, según <a href="{ELDIARIO}">elDiario.es</a>. RTVE, Atresmedia y La Séptima lo emitirán, según la información de EFE que recoge <a href="{INFOBAE}">Infobae</a>. Quedarán diez días para votar.</p>
<p data-tipo="contexto">El último cara a cara entre los dos fue el 10 de julio de 2023, trece días antes de las elecciones. Lo vieron 5,9 millones de personas, según los datos de Barlovento Comunicación que publicaron <a href="{AUD23}">El Debate y Europa Press</a>: el cara a cara menos visto de los celebrados desde 1993.</p>
<p data-tipo="dato">Las encuestas que se publicaron después se movieron hacia el PP. De las {N} empresas que publicaron encuesta antes y después del debate, {SUBE} ampliaron la ventaja del PP sobre el PSOE y {BAJA} la redujeron. La media de esas {N} pasó de {p(MA)} a {p(MD)} puntos: el PP subió {p(DPP)} puntos de media y el PSOE, {p(DPS)}. El 23 de julio, el PP ganó por {p(GAP23)}.</p>
{g_cambio}
{g_media}
<p data-tipo="contexto">Las encuestas no dicen por qué se movieron, y no es seguro que fuera por el debate: hubo más campaña entre una encuesta y otra, y en las publicadas justo después parte del trabajo de campo pudo ser anterior al 10 de julio. Lo que sí se sabe es cómo acabó: {L("encuestas-error-2023-2019-29n", "las últimas encuestas de 2023 exageraron la ventaja del PP")}.</p>
<p data-tipo="dato">Con los datos {VERSION}, la media de encuestas de <a href="{BASE}encuestas/">nuestro modelo</a> da al PP {p(HOY)} puntos de ventaja sobre el PSOE antes del debate de este jueves.</p>
'''

preguntas = [
    ('¿Cuándo es el debate entre Sánchez y Feijóo?',
     f'El jueves 19 de noviembre de 2026 a las 22.00, organizado por la Academia de Televisión y moderado por María Casado, según <a href="{ELDIARIO}">elDiario.es</a>.'),
    ('¿Qué pasó con las encuestas tras el debate de 2023?',
     f'De las {N} empresas que publicaron antes y después del cara a cara del 10 de julio, {SUBE} ampliaron la ventaja del PP. La media pasó de {p(MA)} a {p(MD)} puntos; el PP ganó por {p(GAP23)}.'),
]
enlaces = f'{L("encuestas-error-2023-2019-29n", "Lo que las encuestas no dicen")} · <a href="{BASE}encuestas/">Las encuestas de las elecciones generales del 29N</a>'
foot = ('Datos: encuestas recopiladas por Electográfica; Ministerio del Interior, resultados de 2023 con voto exterior; modelo de mapaelectoral.es/encuestas. '
        'Cálculo: actualidad/src/resumenes/debate_cara_a_cara.py.')
DATOS = {'N': N, 'SUBE': SUBE, 'BAJA': BAJA, 'MA': MA, 'MD': MD, 'DPP': DPP, 'DPS': DPS, 'GAP23': GAP23, 'HOY': HOY,
         'X': {r.nom: {'antes': float(r.antes), 'despues': float(r.despues)} for r in X.itertuples()}}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'El debate',
      f'Debate Sánchez-Feijóo: tras el cara a cara de 2023, {SUBE} de {N} encuestadoras ampliaron la ventaja del PP; trece días después ganó por {p(GAP23)} puntos',
      f'El debate de las elecciones generales del 29N es este jueves a las 22.00. En 2023, la media de las encuestas pasó de {p(MA)} a {p(MD)} puntos de ventaja para el PP tras el cara a cara; las urnas le dieron {p(GAP23)}.',
      '17 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('N', N, SUBE, BAJA, round(MA, 2), round(MD, 2), round(DPP, 2), round(DPS, 2), round(GAP23, 2), round(HOY, 2))
