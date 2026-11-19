"""«Encuestas de hoy» (19-11-2026): las encuestas de las elecciones generales publicadas desde la pieza del día anterior
(18-11, 15.00) hasta esta mañana, cada una frente a su entrega anterior y frente a la mediana de /encuestas/.
Una pieza por día, con URL y título fijos (memoria noticia-diaria-encuestas; la del 18 es encuestas_hoy.py).

Encuestas: las de carga() (encuestas/src/construir.py: Electográfica y Wikipedia) publicadas después de las 15.00 del 18
(Sondaxe del 13 al 17, Sigma Dos, SW Demoscopia y EM-Analytics), más EXTRA: el tracking de 40dB. de hoy, que aún no recoge
la actualización automática (se comprueba con su informe en PDF).
Mediana: medianas() de /encuestas/, la de la última actualización automática (resumen.json).
Uso, desde la raíz: python3 actualidad/src/resumenes/encuestas_1911.py
"""
import importlib.util
import json
from datetime import date

from comun import BASE, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
HOY, AYER = '2026-11-19', '2026-11-18'
HORA = '8.30'           # hora de Madrid de los datos de esta versión; va también en «actualizado» (dateModified)
SLUG = 'encuestas-elecciones-generales-2026-19-noviembre'
DIA = f'{int(HOY[8:])} de {MES[int(HOY[5:7]) - 1]}'

_spec = importlib.util.spec_from_file_location('enc_construir', RAIZ / 'encuestas/src/construir.py')
enc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enc)
_pub = lambda e: e.get('publicado') or e['fin']
ENCS = enc.carga()
RESUMEN = json.load(open(RAIZ / 'previsiones/datos/encuestas/resumen.json'))

# 40dB., tracking día 7 (informe de El País, págs. 6, 8 y 25): campo del 14 al 18, 2.000 entrevistas en línea.
# Sumar = Frente Amplio 3,7 + otras coaliciones territoriales de izquierda 1,7 (Compromís 1,2, Ara Més 0,2, UPC 0,3).
# Escaños: PP 133 (126-138), PSOE 121 (116-125), Vox 57 (53-61); UPN-PP 2 aparte. Con el criterio de /encuestas/ (UPN-PP en la
# fila del PP, encuestas/src/construir.py), PP 128-140.
PDF40 = 'https://elpais.com/infografias/encuestas40db/2026/11-tracking-electoral/informe_tracking_dia07.pdf'
EXTRA = [dict(reest=False, casa='40dB.', medio='El País / Cadena SER', inicio='2026-11-14', fin='2026-11-18', publicado=HOY, muestra='2000',
              voto={'PP': 32.4, 'PSOE': 30.4, 'VOX': 17.2, 'SUMAR': 5.4, 'PODEMOS': 1.2, 'SALF': 1.7},
              esc={'PP': '128-140', 'PSOE': '116-125', 'VOX': '53-61', 'SUMAR': '8-11', 'PODEMOS': '0-1', 'SALF': '0'},
              url=PDF40, electografica='https://www.electografica.com/2026/11/encuesta-40db-261119.html')]
ESC40 = {'PP': 133, 'UPNPP': 2, 'PSOE': 121, 'VOX': 57, 'VOX_AYER': 55}
for x in EXTRA:
    assert not any(enc.clave(e['casa']) == enc.clave(x['casa']) and _pub(e) == HOY for e in ENCS), f'{x["casa"]} ya está en carga(): quítala de EXTRA'

# Publicadas desde la pieza de ayer: las del 18 que no estaban entonces (Sondaxe del 13 al 17, Sigma Dos, SW, EM-Analytics)
YA = {('40db', '2026-11-17'), ('sondaxe', '2026-11-16')}       # (casa, fin de campo) de las que recogió la pieza del 18
NUEVAS = [e for e in ENCS if _pub(e) == AYER and not e['reest'] and (enc.clave(e['casa']), e['fin']) not in YA] + EXTRA
assert sorted(enc.clave(e['casa']) for e in NUEVAS) == ['40db', 'emanalytics', 'sigmados', 'sondaxe', 'swdemoscopia'], [e['casa'] for e in NUEVAS]
_val = sorted((e for e in ENCS if not e['reest'] and e['fin'] >= '2023-07-24'), key=lambda e: (_pub(e), e['fin']), reverse=True)


def anterior(e):
    """La entrega anterior de la misma encuestadora (la de campo inmediatamente anterior)."""
    return next(x for x in _val if enc.clave(x['casa']) == enc.clave(e['casa']) and x is not e and (_pub(x), x['fin']) < (_pub(e), e['fin']))


def nombre(e):
    return enc.nombre_casa(e['casa'])


F = []
for e in NUEVAS:
    a = anterior(e)
    v, va = e['voto'], a['voto']
    pv = enc.suma_pv(e)
    F.append(dict(casa=nombre(e), clave=enc.clave(e['casa']), medio=e['medio'], ini=e['inicio'], fin=e['fin'], n=int(e['muestra']), url=e['url'],
                  PP=v['PP'], PSOE=v['PSOE'], VOX=v['VOX'], dif=round(v['PP'] - v['PSOE'], 1), dif_ant=round(va['PP'] - va['PSOE'], 1),
                  dPP=round(v['PP'] - va['PP'], 1), dPSOE=round(v['PSOE'] - va['PSOE'], 1), dVOX=round(v['VOX'] - va['VOX'], 1),
                  ant_fin=a['fin'], pv_lo=pv[0], pv_hi=pv[1]))
F.sort(key=lambda f: f['dif'])
G = {f['clave']: f for f in F}
SX, D40, SG, EM, SW = G['sondaxe'], G['40db'], G['sigmados'], G['emanalytics'], G['swdemoscopia']
assert (SX['PP'], SX['PSOE'], SX['dif'], SX['ini'], SX['fin'], SX['ant_fin']) == (28.5, 27.8, 0.7, '2026-11-13', '2026-11-17', '2026-11-16'), SX
assert (D40['dif'], D40['dVOX'], D40['ant_fin']) == (2.0, 0.2, '2026-11-17'), D40
assert SW['dif'] < 0 and all(f['dif'] > 0 for f in F if f is not SW)
# 40dB.: PP + Vox con los escaños centrales del informe, contando UPN-PP como el resto (en la fila del PP)
PV40 = ESC40['PP'] + ESC40['UPNPP'] + ESC40['VOX']
assert PV40 == 192
# Sondaxe: la distancia más corta entre PP y PSOE en sus encuestas desde las generales de 2023
SX_SERIE = [round(x['voto']['PP'] - x['voto']['PSOE'], 1) for x in _val if enc.clave(x['casa']) == 'sondaxe' and x['fin'] < SX['fin']]
assert SX['dif'] < min(SX_SERIE), min(SX_SERIE)
SX_MIN_ANT = min(SX_SERIE)
# Vox en 40dB.: sube tras bajar en cada una de las cinco entregas anteriores (del día 1 al 6)
VOX40 = [x['voto']['VOX'] for x in sorted((x for x in _val if enc.clave(x['casa']) == '40db' and _pub(x) >= '2026-11-13'), key=_pub)]
assert VOX40 == [18.8, 18.5, 18.3, 18.0, 17.5, 17.0], VOX40


# Margen de la distancia entre dos partidos de una misma encuesta (muestreo aleatorio simple, dos errores típicos)
def margen_dif(p1, p2, n_):
    p1, p2 = p1 / 100, p2 / 100
    return 2 * ((p1 + p2 - (p1 - p2) ** 2) / n_) ** .5 * 100


M_SX = margen_dif(SX['PP'], SX['PSOE'], SX['n'])
assert SX['dif'] < M_SX

# Mediana de /encuestas/ (última actualización automática)
DESCARGA = RESUMEN['descargado']
MED = {k: v for k, v in enc.medianas(ENCS, date.fromisoformat(HOY))[-1].items() if k != 'd'}
MED_DIF = round(MED['PP'] - MED['PSOE'], 1)
ULT = {}
for e in ENCS:
    if (date.fromisoformat(HOY) - date.fromisoformat(e['fin'])).days < enc.VENTANA_MEDIANA and not e['reest'] and enc.clave(e['casa']) not in ULT:
        ULT[enc.clave(e['casa'])] = e
NCASAS = len(ULT)
MAS_CERCA = [f['casa'] for f in F if f['dif'] < MED_DIF]

CSS_ULTIMO = '<style>' + '\n'.join(l for l in enc.ESTILOS.split('\n') if l.startswith(('.ultimo-graf', '.bu-')) or ('.bu-b i' in l and 'prefers-color-scheme' in l or l.startswith(':root[data-theme="dark"] .bu-b'))) + '</style>'
assert CSS_ULTIMO.count('.bu-') >= 8
_orden = {f['clave']: i for i, f in enumerate(F)}
_graf = [(e, anterior(e), f'{esc(nombre(e))} · {esc(e["medio"])} · {enc.dia(_pub(e))}') for e in sorted(NUEVAS, key=lambda e: _orden[enc.clave(e['casa'])])]
g_dia = enc.graficos_ultimo(_graf).replace('Las últimas encuestas, partido a partido', f'Las encuestas de hoy, {DIA}, partido a partido')
assert g_dia.count('class="bu"') == 5

_fila = lambda f: (f['casa'], abs(f['dif']), 'var(--pp)' if f['dif'] > 0 else 'var(--psoe)', ('PP +' if f['dif'] > 0 else 'PSOE +') + p(abs(f['dif'])))
g_med = figura('Las cinco, más ajustadas que la mediana',
               f'Ventaja del primero sobre el segundo, en puntos, en cada encuesta y en la mediana de las {NCASAS} encuestadoras de las tres últimas semanas',
               barras([_fila(f) for f in F] + [('Mediana', MED_DIF, 'var(--otros)', 'PP +' + p(MED_DIF))], 6,
                      'Ventaja del PP o del PSOE en las encuestas de hoy y en la mediana', W=400, ml=118, fmt=p),
               f'Fuente: las encuestas citadas, recogidas por Electográfica y Wikipedia; 40dB., <a href="{PDF40}">informe del día 7</a>. '
               f'Mediana de <a href="{BASE}encuestas/">mapaelectoral.es/encuestas</a>, sin la 40dB. de hoy.',
               leyenda=[('PP por delante', 'var(--pp)'), ('PSOE por delante', 'var(--psoe)'), ('Mediana de las encuestas', 'var(--otros)')],
               tabla=(['', 'PP', 'PSOE', 'Vox'], [[f['casa'], p(f['PP']), p(f['PSOE']), p(f['VOX'])] for f in F] + [['Mediana', p(MED['PP']), p(MED['PSOE']), p(MED['VOX'])]]))
assert len(MAS_CERCA) == 5 and max(f['dif'] for f in F) == SG['dif'], (MAS_CERCA, MED_DIF)


def dv(x):
    return 'repite' if x == 0 else (f'sube {p(x)}' if x > 0 else f'baja {p(-x)}')


pv_txt = lambda f: f'{f["pv_lo"]}' if f['pv_lo'] == f['pv_hi'] else f'entre {f["pv_lo"]} y {f["pv_hi"]}'
cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="dato">Sondaxe deja al PSOE a <strong>{p(SX['dif'])} puntos</strong> del PP, la distancia más corta que le ha dado desde las generales de 2023. Su tracking para <a href="{SX['url']}">La Voz de Galicia</a>, con entrevistas del 13 al 17 de noviembre, da al PP el {p(SX['PP'])} % y al PSOE el {p(SX['PSOE'])} %; en la entrega anterior la distancia era de {p(SX['dif_ant'])} puntos. Es una de las cinco encuestas de las elecciones generales publicadas desde ayer por la tarde. El <a href="{PDF40}">tracking de 40dB. para El País y la SER</a> de este jueves deja la distancia en {p(D40['dif'])} puntos (PP {p(D40['PP'])} %, PSOE {p(D40['PSOE'])} %); <a href="{EM['url']}">EM-Analytics para Electomanía</a>, en {p(EM['dif'])}, y <a href="{SG['url']}">Sigma Dos para El Mundo</a>, en {p(SG['dif'])}. <a href="{SW['url']}">SW Demoscopia para La Séptima</a> sigue siendo la única que pone por delante al PSOE, con {p(-SW['dif'])} puntos de ventaja.</p>
{CSS_ULTIMO}
{g_dia}
<p data-tipo="dato">Vox sube en 40dB. por primera vez desde que empezó su tracking: del {p(VOX40[-1])} al <strong>{p(D40['VOX'])} %</strong>, tras bajar en cada una de las cinco entregas anteriores. En Sondaxe {dv(SX['dVOX'])} puntos, hasta el {p(SX['VOX'])} %; en Sigma Dos {dv(SG['dVOX'])}, hasta el {p(SG['VOX'])} %, y en EM-Analytics {dv(EM['dVOX'])}, hasta el {p(EM['VOX'])} %. En SW Demoscopia {dv(SW['dVOX'])}, hasta el {p(SW['VOX'])} %.</p>
<p data-tipo="dato">En escaños, contando los de UPN-PP con el PP en todas, PP y Vox suman {PV40} en 40dB. ({ESC40['PP']} del PP, {ESC40['UPNPP']} de UPN-PP y {ESC40['VOX']} de Vox, según su informe), {pv_txt(SX)} en Sondaxe, {pv_txt(EM)} en EM-Analytics y {pv_txt(SG)} en Sigma Dos: por encima de la mayoría absoluta de 176 en las cuatro. SW Demoscopia les da {pv_txt(SW)}, un intervalo que deja la mayoría en el aire.</p>
<h2>Frente a la mediana de las encuestas</h2>
<p data-tipo="dato">La mediana de la última encuesta de cada una de las {NCASAS} encuestadoras de las tres últimas semanas, la que resume <a href="{BASE}encuestas/">nuestra página de encuestas de las elecciones generales 2026</a>, da al PP el {p(MED['PP'])} %, al PSOE el {p(MED['PSOE'])} % y a Vox el {p(MED['VOX'])} %: {p(MED_DIF)} puntos entre PP y PSOE. Las cinco encuestas de hoy ven la carrera más ajustada; Sigma Dos, con {p(SG['dif'])} puntos a favor del PP, es la que más se acerca a esa mediana. La mediana es la de la última actualización automática de la página y todavía no incluye la 40dB. de esta mañana.</p>
{g_med}
<h2>Lo que estas encuestas no dicen</h2>
<p data-tipo="contexto">Con 1.000 entrevistas, los {p(SX['dif'])} puntos entre PP y PSOE de Sondaxe quedan muy dentro del margen de error de esa distancia, de unos ±{p(M_SX)} puntos: es un empate técnico, no un adelantamiento a punto de producirse. Además, las cinco son trackings o encuestas que acumulan entrevistas de varios días, y cada entrega comparte la mayoría con la anterior, así que los cambios de un día a otro son pequeños por construcción.</p>
<p data-tipo="contexto">Esta pieza recoge las encuestas publicadas hasta las {HORA} de este jueves. La ley prohíbe publicar encuestas desde el martes 24 de noviembre, así que quedan cinco días de encuestas.</p>
'''

preguntas = [
    (f'¿Qué dicen las encuestas de las elecciones generales hoy, {DIA}?',
     'Sondaxe: PP {0} %, PSOE {1} %. 40dB.: PP {2} %, PSOE {3} %. EM-Analytics: PP {4} %, PSOE {5} %. Sigma Dos: PP {6} %, PSOE {7} %. SW Demoscopia: PSOE {8} %, PP {9} %.'.format(
         p(SX['PP']), p(SX['PSOE']), p(D40['PP']), p(D40['PSOE']), p(EM['PP']), p(EM['PSOE']), p(SG['PP']), p(SG['PSOE']), p(SW['PSOE']), p(SW['PP']))),
    ('¿Quién gana las elecciones generales según las encuestas?',
     f'El PP, en cuatro de las cinco publicadas desde ayer, con entre {p(SX["dif"])} y {p(SG["dif"])} puntos de ventaja. SW Demoscopia da ganador al PSOE. '
     f'La mediana de las {NCASAS} encuestadoras da al PP {p(MED_DIF)} puntos de ventaja.'),
    ('¿Hasta cuándo se pueden publicar encuestas?',
     'Hasta el lunes 23 de noviembre. La ley electoral prohíbe publicarlas en los cinco días anteriores a la votación, desde el martes 24 hasta el cierre de los colegios el domingo 29.'),
]
enlaces = (f'<a href="{BASE}encuestas/">Encuestas elecciones generales 2026</a> · {L("encuestas-elecciones-generales-2026-18-noviembre", "Las encuestas de ayer, 18 de noviembre")} · '
           f'{L("cuanto-discrepan-encuestas-29n", "Cuánto discrepan las encuestas")}')
foot = ('Datos: 40dB. para El País y la SER; Sondaxe para La Voz de Galicia; Sigma Dos para El Mundo; EM-Analytics para Electomanía; SW Demoscopia para La Séptima; '
        'recogidas por Electográfica y Wikipedia; mediana de mapaelectoral.es/encuestas. Cálculo: actualidad/src/resumenes/encuestas_1911.py.')

DATOS = {'F': F, 'ESC40': ESC40, 'PV40': PV40, 'MED': MED, 'MED_DIF': MED_DIF, 'NCASAS': NCASAS, 'MAS_CERCA': MAS_CERCA, 'SX_MIN_ANT': SX_MIN_ANT,
         'VOX40': VOX40, 'M_SX': round(M_SX, 1), 'DESCARGA': DESCARGA}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

TITULO = f'Encuestas elecciones generales 2026, hoy {DIA}: Sondaxe deja al PSOE a {p(SX["dif"])} puntos del PP'
DEK = (f'Es su distancia más corta desde 2023. 40dB. la deja en {p(D40["dif"])} puntos y Sigma Dos, en {p(SG["dif"])}; SW Demoscopia pone por delante al PSOE. '
       f'La mediana de las encuestas, en {p(MED_DIF)} a favor del PP.')
pieza(SLUG, 'Encuestas de hoy', TITULO, DEK, f'19 de noviembre de 2026 · actualizado a las {HORA}', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(TITULO); print(DEK); print('MED', MED, NCASAS, DESCARGA, 'MAS_CERCA', MAS_CERCA, 'M_SX', round(M_SX, 2), 'SX_MIN_ANT', SX_MIN_ANT)
for f in F: print(f)
