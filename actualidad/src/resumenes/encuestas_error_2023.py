"""«Lo que las encuestas no dicen» (17-11-2026): cuánto se equivocaron las últimas encuestas de 2023 y de noviembre de 2019.

Última encuesta de cada empresa publicada en las dos semanas anteriores a la veda (art. 69.7 de la LOREG: no se publican
en los cinco días anteriores a la votación): del 3 al 17 de julio de 2023 y del 20 de octubre al 3 de noviembre de 2019.
Encuestas: previsiones/datos/encuestas/encuestas_limpias.csv (Electográfica, con la fuente original de cada una).
Resultados: actualidad/src/sistema/simulador.json (Interior, por provincia, con voto exterior; % sobre votos válidos).
Media de hoy: modelo de mapaelectoral.es/encuestas (previsiones/datos/publico/historico, la última versión).
Uso, desde la raíz: python3 actualidad/src/resumenes/encuestas_error_2023.py
"""
import json
import re

import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import COL, grupos, p

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
SLUG = 'encuestas-error-2023-2019-29n'
LOREG = 'https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672#a69'
ELECTO = 'https://www.electografica.com/'

# --- Resultados oficiales (con voto exterior) ---
SIM = json.load(open(RAIZ / 'actualidad/src/sistema/simulador.json'))


def resultado(y):
    tot, val = {}, 0
    for x in SIM['elecciones'][y].values():
        val += x['validos']
        for k, v in x['v'].items():
            tot[k] = tot.get(k, 0) + v
    return {k: v / val * 100 for k, v in tot.items()}, {k: v for k, v in tot.items()}, val


R23, V23, VAL23 = resultado('2023_07')
R19, V19, VAL19 = resultado('2019_11')
RES23 = {'PP': R23['PP'], 'PSOE': R23['PSOE'], 'VOX': R23['Vox'], 'SUMAR': R23['Sumar']}
RES19 = {'PP': R19['PP'], 'PSOE': R19['PSOE'], 'VOX': R19['Vox']}
assert [round(RES23[k], 1) for k in ('PP', 'PSOE', 'VOX', 'SUMAR')] == [33.1, 31.7, 12.4, 12.3], RES23
assert [round(RES19[k], 1) for k in ('PP', 'PSOE', 'VOX')] == [20.8, 28.0, 15.1], RES19
GAP23 = RES23['PP'] - RES23['PSOE']          # con los votos, no con los porcentajes redondeados
GAP19 = RES19['PP'] - RES19['PSOE']

# --- Encuestas ---
e = pd.read_csv(RAIZ / 'previsiones/datos/encuestas/encuestas_limpias.csv')
e = e[e.ambito == 'ESPAÑA']


def orden_url(u):
    """Desempate de encuestas del mismo día y empresa: la ficha de Electográfica …-AAMMDD.html va antes que …-AAMMDD-2.html
    (editor, 17-11-2026: Data10 y Sondaxe publicaron dos el 17-7-2023)."""
    m = re.search(r'(\d{6})(?:-(\d+))?\.html$', str(u))
    return (m.group(1), int(m.group(2) or 1)) if m else ('', 0)


def ultimas(ini, fin):
    f = e[(e.publicado >= ini) & (e.publicado <= fin)].copy()
    f['_ord'] = f.url_agregador.map(orden_url)
    f = f.sort_values(['publicado', '_ord'], kind='stable')
    return f.groupby('encuestadora').tail(1).copy()


U23 = ultimas('2023-07-03', '2023-07-17')
U19 = ultimas('2019-10-20', '2019-11-03')
assert len(U23) == 21 and len(U19) == 15 and U23.encuestadora.is_unique and U19.encuestadora.is_unique
assert U23[['PP', 'PSOE', 'VOX', 'SUMAR']].notna().all().all() and U19[['PP', 'PSOE', 'VOX']].notna().all().all()
M23 = {k: float(U23[k].mean()) for k in ('PP', 'PSOE', 'VOX', 'SUMAR')}
M19 = {k: float(U19[k].mean()) for k in ('PP', 'PSOE', 'VOX')}
ERR23 = {k: M23[k] - RES23[k] for k in M23}
ERR19 = {k: M19[k] - RES19[k] for k in M19}
MGAP23, MGAP19 = M23['PP'] - M23['PSOE'], M19['PP'] - M19['PSOE']
SOBRE23 = MGAP23 - GAP23           # cuánto exageraron la ventaja del PP sobre el PSOE
SOBRE19 = MGAP19 - GAP19
assert GAP19 < 0 and MGAP19 < 0       # en 2019 el PP no tenía ventaja: el texto habla de sobrevalorarlo frente al PSOE
assert round(ERR23['PSOE'], 1) == -3.3 and round(ERR19['VOX'], 1) == -3.1 and SOBRE23 > 4 and 0 < SOBRE19 < 1, (ERR23, ERR19, SOBRE23, SOBRE19)
U23['gap'] = U23.PP - U23.PSOE
U23['nom'] = U23.encuestadora.replace({'Cis': 'CIS', 'SigmaDos': 'Sigma Dos', 'InvyMark': 'Invymark', 'Atlasintel': 'AtlasIntel',
                                      'Yougov': 'YouGov', 'Data10 - Demoscopia y Servicios': 'Data10', 'SocioMétrica': 'SocioMétrica'})
PSOE_POR_DEBAJO = int((U23.PSOE < RES23['PSOE']).sum())
PSOE_ENCIMA = list(U23[U23.PSOE > RES23['PSOE']].nom)
assert PSOE_POR_DEBAJO == 20 and PSOE_ENCIMA == ['CIS'], PSOE_ENCIMA
PP_ENCIMA = int((U23.PP > RES23['PP']).sum())
GAP_MAYOR = int((U23.gap > GAP23).sum())
ATLAS = U23[U23.nom == 'AtlasIntel'].iloc[0]
ATLAS_DIF = float(ATLAS.gap - GAP23)
assert (U23.gap - GAP23).abs().idxmin() == ATLAS.name
PSOE_DELANTE = list(U23[U23.gap < 0].nom)
assert PSOE_DELANTE == ['CIS'] and GAP_MAYOR == 20 and 0 < ATLAS_DIF < 0.1, (ATLAS_DIF, PSOE_DELANTE, GAP_MAYOR)
CIS23 = U23[U23.nom == 'CIS'].iloc[0]
PSOE_MIN, PSOE_MAX = float(U23.PSOE.min()), float(U23.PSOE.max())
VOX19_MAX = float(U19.VOX.max())
assert VOX19_MAX < RES19['VOX']         # ninguna empresa llegó al resultado de Vox en 2019

# --- Hoy ---
HJ = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
MED = json.load(open(HJ))['meta']['media_encuestas']
HOY = MED['PP'] - MED['PSOE']
CON23, CON19 = HOY - SOBRE23, HOY - SOBRE19
assert HOY > 0 and CON23 < 0 < CON19, (HOY, CON23, CON19)
_a, _m, _d, _hm = HJ.stem.split('-')
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de noviembre de {_a}'
NOMBRE = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'SUMAR': 'Sumar'}

# --- Gráficos ---
g_media = figura(f'En 2023, las encuestas se quedaron cortas con el PSOE: {p(M23["PSOE"])} % de media frente al {p(RES23["PSOE"])} % que sacó',
                 'Media de la última encuesta de cada empresa publicada del 3 al 17 de julio de 2023 (barra de arriba) y resultado del 23 de julio (barra de abajo), en % de los votos válidos',
                 grupos([(NOMBRE[k], [(M23[k], COL[k], .45, 'media de las encuestas'), (RES23[k], COL[k], 1, 'resultado')]) for k in ('PP', 'PSOE', 'VOX', 'SUMAR')],
                        40, 'Media de las encuestas y resultado de 2023 por partido', W=400, ml=60),
                 f'Fuente: {len(U23)} encuestas recopiladas por <a href="{ELECTO}">Electográfica</a> (la última de cada empresa) y Ministerio del Interior, resultados con voto exterior. Cálculo propio.',
                 [(NOMBRE[k], COL[k]) for k in ('PP', 'PSOE', 'VOX', 'SUMAR')],
                 (['Partido', 'Media de las encuestas', 'Resultado', 'Diferencia (puntos)'],
                  [[NOMBRE[k], p(M23[k]), p(RES23[k]), ('+' if ERR23[k] > 0 else '−') + p(abs(ERR23[k]))] for k in ('PP', 'PSOE', 'VOX', 'SUMAR')]))

FIL = U23.sort_values('PSOE')
g_psoe = figura(f'De {len(U23)} empresas, solo el CIS dio al PSOE más de lo que sacó en 2023',
                f'Estimación del PSOE en la última encuesta de cada empresa publicada del 3 al 17 de julio de 2023, en %; la línea, su resultado ({p(RES23["PSOE"])} %)',
                barras([(r.nom, float(r.PSOE), COL['PSOE'], p(r.PSOE) + ' %') for r in FIL.itertuples()], 40, 'Estimación del PSOE por empresa en 2023', W=400, ml=118,
                       fmt=p, linea=(RES23['PSOE'], 'Resultado'), separar=True),
                f'Fuente: encuestas recopiladas por <a href="{ELECTO}">Electográfica</a> y Ministerio del Interior. Cálculo propio.',
                [('PSOE', COL['PSOE'])],
                (['Empresa', 'Medio', 'Publicada', 'PP', 'PSOE', 'Ventaja del PP'],
                 [[r.nom, '' if pd.isna(r.cliente) else {'los grupos': 'Henneo y Joly'}.get(str(r.cliente), str(r.cliente)), r.publicado, p(r.PP), p(r.PSOE), ('+' if r.gap > 0 else '−') + p(abs(r.gap))]
                  for r in U23.sort_values('gap').itertuples()]))

ESC = [('La media de hoy', HOY), ('Con el error de 2019', CON19), ('Con el error de 2023', CON23)]
g_hoy = figura('Si las encuestas fallaran como en 2023, el PSOE iría por delante; si fallaran como en 2019, el PP seguiría primero',
               'Ventaja del PP sobre el PSOE en la media de encuestas de hoy, en puntos, y la misma media corregida con lo que las encuestas exageraron esa ventaja en noviembre de 2019 y en julio de 2023 (un cálculo, no una previsión)',
               grupos([(t, [(abs(v), COL['PP'] if v > 0 else COL['PSOE'], 1, 'ventaja del PP' if v > 0 else 'ventaja del PSOE')]) for t, v in ESC], 6,
                      'Ventaja del PP o del PSOE con y sin el error de 2019 y 2023', W=400, ml=140),
               f'Fuente: modelo de <a href="{BASE}encuestas/">mapaelectoral.es/encuestas</a> ({VERSION}), encuestas recopiladas por Electográfica y Ministerio del Interior. Cada barra lleva el color del partido que iría por delante. Cálculo propio.',
               [('Ventaja del PP', COL['PP']), ('Ventaja del PSOE', COL['PSOE'])],
               (['Escenario', 'PP menos PSOE (puntos)'], [[t, ('+' if v > 0 else '−') + p(abs(v))] for t, v in ESC]))

# --- Texto ---
cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Desde el martes 24 de noviembre no se podrá publicar ninguna encuesta de las elecciones generales del 29N: la <a href="{LOREG}">ley electoral</a> lo prohíbe en los cinco días anteriores a la votación. Antes de esa veda, conviene mirar hacia atrás. Las encuestas dicen dónde estaba cada partido cuando se hicieron; lo que no dicen es cuánto se equivocaron la última vez.</p>
<p data-tipo="dato">En julio de 2023, la media de la última encuesta de cada una de las {len(U23)} empresas que publicaron en las dos semanas previas a la veda daba al PP el {p(M23["PP"])} % y al PSOE el {p(M23["PSOE"])} %: una ventaja de <strong>{p(MGAP23)} puntos</strong>. El 23 de julio, el PP sacó el {p(RES23["PP"])} % y el PSOE el {p(RES23["PSOE"])} %. La ventaja real fue de {p(GAP23)} puntos, calculada con los votos y no con los porcentajes redondeados. Las encuestas se quedaron {p(abs(ERR23["PSOE"]))} puntos cortas con el PSOE y dieron al PP {p(ERR23["PP"])} de más.</p>
{g_media}
<p data-tipo="dato">No fue cosa de una empresa. De las {len(U23)}, {PSOE_POR_DEBAJO} dieron al PSOE menos de lo que sacó, con estimaciones de entre el {p(PSOE_MIN)} % y el {p(float(U23[U23.nom != "CIS"].PSOE.max()))} %. Solo el CIS lo puso por encima, con el {p(CIS23.PSOE)} %, y fue también el único que lo situó por delante del PP, al que dio el {p(CIS23.PP)} %. Las otras {GAP_MAYOR} exageraron la ventaja del PP. La que más se acercó fue AtlasIntel: le dio {p(ATLAS.gap)} puntos, a menos de una décima de la ventaja real.</p>
{g_psoe}
<h2>En 2019, el que faltó fue Vox</h2>
<p data-tipo="dato">El error no siempre va en la misma dirección. En noviembre de 2019, la media de las últimas encuestas de {len(U19)} empresas acertó casi con el PSOE ({p(M19["PSOE"])} %, frente al {p(RES19["PSOE"])} % que sacó) y con el PP ({p(M19["PP"])} %, frente al {p(RES19["PP"])} %). El que se escapó fue Vox: las encuestas le daban de media el {p(M19["VOX"])} % y sacó el <strong>{p(RES19["VOX"])} %</strong>, {p(abs(ERR19["VOX"]))} puntos más. Ninguna empresa llegó a ese dato: la que más le daba, un {p(VOX19_MAX)} %.</p>
<h2>Qué pasaría hoy con el mismo error</h2>
<p data-tipo="dato">Con los datos {VERSION}, la media de encuestas de <a href="{BASE}encuestas/">nuestro modelo</a> da al PP el {p(MED["PP"])} % y al PSOE el {p(MED["PSOE"])} %: {p(HOY)} puntos de ventaja para el PP. En 2023, las encuestas exageraron esa ventaja en {p(SOBRE23)} puntos. En 2019, cuando ganó el PSOE, sobrevaloraron al PP frente al PSOE en {p(SOBRE19)} puntos.</p>
{g_hoy}
<p data-tipo="hipotesis">Si las encuestas de hoy fallaran igual que en 2023, el PSOE iría {p(abs(CON23))} puntos por delante del PP. Si fallaran como en 2019, el PP seguiría primero, con {p(CON19)} puntos de ventaja. Es una cuenta, no una previsión: nada dice que el error de esta vez vaya a parecerse al de las anteriores, y las empresas cambian sus métodos después de cada elección.</p>
'''

preguntas = [
    ('¿Acertaron las encuestas en las elecciones generales de 2023?',
     f'No del todo. La media de las últimas encuestas daba al PP {p(MGAP23)} puntos de ventaja sobre el PSOE y la real fue de {p(GAP23)}. Al PSOE le daban el {p(M23["PSOE"])} % y sacó el {p(RES23["PSOE"])} %.'),
    ('¿Qué encuesta acertó más en 2023?',
     f'En la ventaja del PP sobre el PSOE, AtlasIntel, con {p(ATLAS.gap)} puntos. En el voto del PSOE, el CIS fue el único que le dio más de lo que sacó ({p(CIS23.PSOE)} %), pero también el único que lo puso por delante del PP.'),
    ('¿Hasta cuándo se pueden publicar encuestas de las elecciones del 29N?',
     'Hasta el lunes 23 de noviembre. La ley electoral prohíbe publicarlas en los cinco días anteriores a la votación.'),
]
enlaces = f'<a href="{BASE}encuestas/">Las encuestas de las elecciones generales del 29N</a> · {L("cis-preelectoral-29n", "El CIS preelectoral")}'
foot = ('Datos: encuestas recopiladas por Electográfica, con la fuente original de cada una; Ministerio del Interior, resultados de las generales de noviembre de 2019 '
        'y julio de 2023 con voto exterior; modelo de mapaelectoral.es/encuestas. Cálculo: actualidad/src/resumenes/encuestas_error_2023.py.')

DATOS = {'M23': M23, 'M19': M19, 'RES23': RES23, 'RES19': RES19, 'ERR23': ERR23, 'ERR19': ERR19, 'GAP23': GAP23, 'GAP19': GAP19,
         'MGAP23': MGAP23, 'MGAP19': MGAP19, 'SOBRE23': SOBRE23, 'SOBRE19': SOBRE19, 'N23': len(U23), 'N19': len(U19),
         'PSOE_POR_DEBAJO': PSOE_POR_DEBAJO, 'GAP_MAYOR': GAP_MAYOR, 'PSOE_MIN': PSOE_MIN, 'PSOE_MAX_SIN_CIS': float(U23[U23.nom != 'CIS'].PSOE.max()),
         'CIS_PSOE': float(CIS23.PSOE), 'CIS_PP': float(CIS23.PP), 'ATLAS_GAP': float(ATLAS.gap), 'VOX19_MAX': VOX19_MAX,
         'MED': {k: MED[k] for k in ('PP', 'PSOE')}, 'HOY': HOY, 'CON23': CON23, 'CON19': CON19,
         'U23': [{'nom': r.nom, 'PP': float(r.PP), 'PSOE': float(r.PSOE)} for r in U23.itertuples()]}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'Lo que las encuestas no dicen',
      f'En 2023, las últimas encuestas daban al PP {p(MGAP23)} puntos de ventaja sobre el PSOE y ganó por {p(GAP23)}: si hoy fallaran igual, el PSOE iría primero',
      f'Lo que las encuestas de las elecciones generales del 29N no dicen: cuánto se equivocaron la última vez. En 2023 se quedaron {p(abs(ERR23["PSOE"]))} puntos cortas con el PSOE; '
      f'en 2019, {p(abs(ERR19["VOX"]))} con Vox.',
      '17 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('M23', {k: round(v, 2) for k, v in M23.items()}, 'RES23', {k: round(v, 2) for k, v in RES23.items()}, 'MGAP23', round(MGAP23, 2), 'GAP23', round(GAP23, 2),
      'SOBRE', round(SOBRE23, 2), round(SOBRE19, 2), 'ERR19', {k: round(v, 2) for k, v in ERR19.items()}, 'HOY', round(HOY, 2), round(CON23, 2), round(CON19, 2),
      'PSOE<', PSOE_POR_DEBAJO, 'GAPMAYOR', GAP_MAYOR, 'ATLAS', ATLAS.gap, 'VOX19MAX', VOX19_MAX, VERSION)
