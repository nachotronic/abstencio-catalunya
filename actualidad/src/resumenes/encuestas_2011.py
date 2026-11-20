"""«Encuestas de hoy» (20-11-2026): las encuestas de las elecciones generales publicadas desde la pieza del día anterior
(19-11, 8.30) hasta esta mañana, cada una frente a su entrega anterior y frente a la mediana de /encuestas/.
Una pieza por día, con URL y título fijos (la del 19 es encuestas_1911.py).

Encuestas: las de carga() (encuestas/src/construir.py: Electográfica y Wikipedia) publicadas el 19 que no recogió la pieza
del 19: 40dB. (día 8, publicado el 19 por la noche), Sigma Dos, EM-Analytics, Data10 y Public First para Politico.
Fuera: la fila «Metroscopia 19-11» de Wikipedia, que no es una encuesta (un ejemplo hipotético de Ignacio Urquizu en laSexta),
y la copia «PF Global» de la encuesta de Public First (la misma encuesta, recogida dos veces).
Todas las de hoy se hicieron antes del debate del 19 por la noche.
Mediana: medianas() de /encuestas/, la de la última actualización automática (resumen.json).
Uso, desde la raíz: python3 actualidad/src/resumenes/encuestas_2011.py
"""
import importlib.util
import json
from datetime import date

from comun import BASE, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
HOY, AYER = '2026-11-20', '2026-11-19'
HORA = '8.30'           # hora de Madrid de los datos de esta versión; va también en «actualizado» (dateModified)
SLUG = 'encuestas-elecciones-generales-2026-20-noviembre'
DIA = f'{int(HOY[8:])} de {MES[int(HOY[5:7]) - 1]}'

_spec = importlib.util.spec_from_file_location('enc_construir', RAIZ / 'encuestas/src/construir.py')
enc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enc)
_pub = lambda e: e.get('publicado') or e['fin']
RESUMEN = json.load(open(RAIZ / 'previsiones/datos/encuestas/resumen.json'))


def _fuera(e):
    k = enc.clave(e['casa'])
    return (k == 'metroscopia' and e['fin'] == '2026-11-19' and 'lasexta.com' in e.get('url', '')) or (k == 'pfglobal' and e['fin'] == '2026-11-17')


_todas = enc.carga()
FUERA = [e for e in _todas if _fuera(e)]
ENCS = [e for e in _todas if not _fuera(e)]

# 40dB., tracking día 8 (informe de El País, pág. 8): campo del 15 al 19, 2.000 entrevistas en línea.
# Escaños centrales: PP 132 (125-137), PSOE 120 (115-123), Vox 58 (56-62); UPN-PP 2 entre «Otros».
PDF40 = 'https://elpais.com/infografias/encuestas40db/2026/11-tracking-electoral/informe_tracking_dia08.pdf'
ESC40 = {'PP': 132, 'UPNPP': 2, 'PSOE': 120, 'VOX': 58}
PV40 = ESC40['PP'] + ESC40['UPNPP'] + ESC40['VOX']
assert PV40 == 192
PV40_AYER = 192         # día 7: PP 133 + UPN-PP 2 + Vox 57 (pieza del 19)

# Publicadas desde la pieza de ayer: las del 19 que no estaban entonces
YA = {('40db', '2026-11-18'), ('sondaxe', '2026-11-17')}       # (casa, fin de campo) de las que recogió la pieza del 19
NUEVAS = [e for e in ENCS if _pub(e) == AYER and not e['reest'] and (enc.clave(e['casa']), e['fin']) not in YA]
assert sorted(enc.clave(e['casa']) for e in NUEVAS) == ['40db', 'data10', 'emanalytics', 'publicfirst', 'sigmados'], [e['casa'] for e in NUEVAS]
assert all(e['fin'] <= '2026-11-19' for e in NUEVAS)            # todas, de antes del debate
_val = sorted((e for e in ENCS if not e['reest'] and e['fin'] >= '2023-07-24'), key=lambda e: (_pub(e), e['fin']), reverse=True)


def anterior(e):
    """La entrega anterior de la misma encuestadora (la de campo inmediatamente anterior), o None si es la primera."""
    return next((x for x in _val if enc.clave(x['casa']) == enc.clave(e['casa']) and x is not e and (_pub(x), x['fin']) < (_pub(e), e['fin'])), None)


def nombre(e):
    return enc.nombre_casa(e['casa'])


F = []
for e in NUEVAS:
    a = anterior(e)
    v = e['voto']
    try:
        pv = enc.suma_pv(e)
    except KeyError:
        pv = None
    f = dict(casa=nombre(e), clave=enc.clave(e['casa']), medio=e['medio'], ini=e['inicio'], fin=e['fin'], n=int(e['muestra']), url=e['url'],
             PP=v['PP'], PSOE=v['PSOE'], VOX=v['VOX'], dif=round(v['PP'] - v['PSOE'], 1), pv=pv, primera=a is None)
    if a:
        va = a['voto']
        f.update(dif_ant=round(va['PP'] - va['PSOE'], 1), dPP=round(v['PP'] - va['PP'], 1), dPSOE=round(v['PSOE'] - va['PSOE'], 1),
                 dVOX=round(v['VOX'] - va['VOX'], 1), ant_fin=a['fin'])
    F.append(f)
F.sort(key=lambda f: f['dif'])
G = {f['clave']: f for f in F}
D40, PF, EM, SG, D10 = G['40db'], G['publicfirst'], G['emanalytics'], G['sigmados'], G['data10']
assert all(f['dif'] > 0 for f in F)
DMIN, DMAX = min(f['dif'] for f in F), max(f['dif'] for f in F)
assert (DMIN, DMAX) == (2.0, 4.6) and D40['dif'] == DMIN and D10['dif'] == DMAX, (DMIN, DMAX)
assert PF['primera'] and not any(f['primera'] for f in F if f is not PF)
# EM-Analytics: la que más recorta, un punto
assert (EM['dif'], EM['dif_ant']) == (2.8, 3.8) and min(f['dif'] - f['dif_ant'] for f in F if not f['primera']) == EM['dif'] - EM['dif_ant']
RECORTE_EM = round(EM['dif_ant'] - EM['dif'], 1)
BAJAN = [f['casa'] for f in F if not f['primera'] and f['dif'] < f['dif_ant']]
IGUAL = [f['casa'] for f in F if not f['primera'] and f['dif'] == f['dif_ant']]
assert sorted(BAJAN) == ['Data10', 'EM-Analytics', 'Sigma Dos'] and IGUAL == ['40dB.'], (BAJAN, IGUAL)
# Vox en 40dB.: sube por segunda entrega seguida, tras bajar en las cinco anteriores
VOX40 = [x['voto']['VOX'] for x in sorted((x for x in _val if enc.clave(x['casa']) == '40db' and _pub(x) >= '2026-11-13'), key=lambda x: x['fin'])]
assert VOX40 == [18.8, 18.5, 18.3, 18.0, 17.5, 17.0, 17.2, 17.6], VOX40


# Margen de la distancia entre dos partidos de una misma encuesta (muestreo aleatorio simple, dos errores típicos)
def margen_dif(p1, p2, n_):
    p1, p2 = p1 / 100, p2 / 100
    return 2 * ((p1 + p2 - (p1 - p2) ** 2) / n_) ** .5 * 100


M40 = margen_dif(D40['PP'], D40['PSOE'], D40['n'])
assert D40['dif'] < M40

# Mediana de /encuestas/ (última actualización automática)
DESCARGA = RESUMEN['descargado']
MED = {k: v for k, v in enc.medianas(ENCS, date.fromisoformat(HOY))[-1].items() if k != 'd'}
MED_DIF = round(MED['PP'] - MED['PSOE'], 1)
MED_PUB = {k: v for k, v in enc.medianas(_todas, date.fromisoformat(HOY))[-1].items() if k != 'd'}   # la que publica la página si aún no se ha corregido
ULT = {}
for e in ENCS:
    if (date.fromisoformat(HOY) - date.fromisoformat(e['fin'])).days < enc.VENTANA_MEDIANA and not e['reest'] and enc.clave(e['casa']) not in ULT:
        ULT[enc.clave(e['casa'])] = e
NCASAS = len(ULT)
MAS_CERCA = [f['casa'] for f in F if f['dif'] < MED_DIF]

CSS_ULTIMO = '<style>' + '\n'.join(l for l in enc.ESTILOS.split('\n') if l.startswith(('.ultimo-graf', '.bu-')) or ('.bu-b i' in l and 'prefers-color-scheme' in l or l.startswith(':root[data-theme="dark"] .bu-b'))) + '</style>'
assert CSS_ULTIMO.count('.bu-') >= 8
_orden = {f['clave']: i for i, f in enumerate(F)}
_con_ant = [e for e in NUEVAS if anterior(e)]
_graf = [(e, anterior(e), f'{esc(nombre(e))} · {esc(e["medio"])} · campo hasta el {enc.dia(e["fin"])}') for e in sorted(_con_ant, key=lambda e: _orden[enc.clave(e['casa'])])]
g_dia = enc.graficos_ultimo(_graf).replace('Las últimas encuestas, partido a partido', f'Las encuestas de hoy, {DIA}, partido a partido')
# 40dB. publica dos entregas con la misma fecha (19): el subtítulo de cada tarjeta compara por fin de campo, no por publicación
import re as _re
_subs = iter(f'Cambio frente a su entrega anterior, con campo hasta el {enc.dia(a["fin"])}' for _, a, _ in _graf)
g_dia = _re.sub(r'Cambio frente a su encuesta del [^<]+', lambda m: next(_subs), g_dia)
assert g_dia.count('Cambio frente a su entrega anterior') == 4
assert g_dia.count('class="bu"') == 4

_fila = lambda f: (f['casa'], f['dif'], 'var(--pp)', 'PP +' + p(f['dif']))
g_med = figura(f'El PP, por delante en las cinco: entre {p(DMIN)} y {p(DMAX)} puntos',
               f'Ventaja del PP sobre el PSOE, en puntos, en cada encuesta y en la mediana de las {NCASAS} encuestadoras de las tres últimas semanas',
               barras([_fila(f) for f in F] + [('Mediana', MED_DIF, 'var(--otros)', 'PP +' + p(MED_DIF))], 6,
                      'Ventaja del PP en las encuestas de hoy y en la mediana', W=400, ml=118, fmt=p),
               f'Fuente: las encuestas citadas, recogidas por Electográfica y Wikipedia; 40dB., <a href="{PDF40}">informe del día 8</a>. '
               f'Mediana de <a href="{BASE}encuestas/">mapaelectoral.es/encuestas</a>.',
               leyenda=[('Encuestas de hoy', 'var(--pp)'), ('Mediana de las encuestas', 'var(--otros)')],
               tabla=(['', 'PP', 'PSOE', 'Vox'], [[f['casa'], p(f['PP']), p(f['PSOE']), p(f['VOX'])] for f in F] + [['Mediana', p(MED['PP']), p(MED['PSOE']), p(MED['VOX'])]]))


def dv(x):
    return 'repite' if x == 0 else (f'sube {p(x)}' if x > 0 else f'baja {p(-x)}')


pv_txt = lambda f: f'{f["pv"][0]}' if f['pv'][0] == f['pv'][1] else f'entre {f["pv"][0]} y {f["pv"][1]}'
assert EM['pv'] == (187, 187) and SG['pv'] == (184, 195), (EM['pv'], SG['pv'])
cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="dato">Las cinco encuestas de las elecciones generales publicadas desde ayer por la mañana dan ganador al PP, con entre <strong>{p(DMIN)} y {p(DMAX)} puntos</strong> de ventaja sobre el PSOE. Todas se hicieron antes del debate de anoche entre Pedro Sánchez y Alberto Núñez Feijóo. La que más recorta la distancia es <a href="{EM['url']}">EM-Analytics para Electomanía</a>: de {p(EM['dif_ant'])} a {p(EM['dif'])} puntos (PP {p(EM['PP'])} %, PSOE {p(EM['PSOE'])} %). El <a href="{PDF40}">tracking de 40dB. para El País y la SER</a> la mantiene en {p(D40['dif'])} (PP {p(D40['PP'])} %, PSOE {p(D40['PSOE'])} %); <a href="{SG['url']}">Sigma Dos para El Mundo</a> la deja en {p(SG['dif'])}, y <a href="{D10['url']}">Data10 para OKDiario</a>, en {p(D10['dif'])}, la más amplia de las cinco.</p>
<p data-tipo="dato">La quinta es la primera encuesta de <a href="{PF['url']}">Public First para Politico</a> en esta campaña, con entrevistas del 15 al 17 de noviembre: PP {p(PF['PP'])} %, PSOE {p(PF['PSOE'])} % y Vox {p(PF['VOX'])} %, {p(PF['dif'])} puntos entre los dos primeros.</p>
{CSS_ULTIMO}
{g_dia}
<p data-tipo="dato">Vox sube en 40dB. por segunda entrega seguida, del {p(VOX40[-2])} al <strong>{p(D40['VOX'])} %</strong>, después de bajar en las cinco anteriores. En Sigma Dos {dv(SG['dVOX'])} puntos, hasta el {p(SG['VOX'])} %; en EM-Analytics {dv(EM['dVOX'])}, hasta el {p(EM['VOX'])} %, y en Data10 {dv(D10['dVOX'])}, en el {p(D10['VOX'])} %.</p>
<p data-tipo="dato">En escaños, contando los de UPN-PP con el PP, PP y Vox suman {PV40} en 40dB. ({ESC40['PP']} del PP, {ESC40['UPNPP']} de UPN-PP y {ESC40['VOX']} de Vox, según su informe), los mismos que ayer; {pv_txt(EM)} en EM-Analytics y {pv_txt(SG)} en Sigma Dos, sumando sus horquillas. Las tres, por encima de la mayoría absoluta de 176.</p>
<h2>Frente a la mediana de las encuestas</h2>
<p data-tipo="dato">La mediana de la última encuesta de cada una de las {NCASAS} encuestadoras de las tres últimas semanas, la que resume <a href="{BASE}encuestas/">nuestra página de encuestas de las elecciones generales 2026</a>, da al PP el {p(MED['PP'])} %, al PSOE el {p(MED['PSOE'])} % y a Vox el {p(MED['VOX'])} %: {p(MED_DIF)} puntos entre PP y PSOE. Cuatro de las cinco encuestas de hoy ven la carrera más ajustada que esa mediana; solo Data10 la ve más abierta.</p>
{g_med}
<h2>Lo que estas encuestas no dicen</h2>
<p data-tipo="contexto">Ninguna mide todavía el efecto del debate: la de campo más reciente, la de 40dB., cerró sus entrevistas el jueves 19. Con 2.000 entrevistas, sus {p(D40['dif'])} puntos entre PP y PSOE quedan dentro del margen de error de esa distancia, de unos ±{p(M40)} puntos: es un empate técnico, aunque el PP vaya por delante. Electográfica, que recoge la de Public First, califica también de empate estadístico sus {p(PF['dif'])} puntos.</p>
<p data-tipo="contexto">Esta pieza recoge las encuestas publicadas hasta las {HORA} de este viernes. La ley prohíbe publicar encuestas desde el martes 24 de noviembre, así que el lunes 23 es el último día. Quién ganó el debate según los sondeos se cuenta en {L("debate-sanchez-feijoo-29n", "la pieza del debate Sánchez Feijóo")}.</p>
'''

preguntas = [
    (f'¿Qué dicen las encuestas de las elecciones generales hoy, {DIA}?',
     'Data10: PP {0} %, PSOE {1} %. Sigma Dos: PP {2} %, PSOE {3} %. EM-Analytics: PP {4} %, PSOE {5} %. Public First: PP {6} %, PSOE {7} %. 40dB.: PP {8} %, PSOE {9} %.'.format(
         p(D10['PP']), p(D10['PSOE']), p(SG['PP']), p(SG['PSOE']), p(EM['PP']), p(EM['PSOE']), p(PF['PP']), p(PF['PSOE']), p(D40['PP']), p(D40['PSOE']))),
    ('¿Quién gana las elecciones generales según las encuestas?',
     f'El PP, en las cinco publicadas desde ayer, con entre {p(DMIN)} y {p(DMAX)} puntos de ventaja. La mediana de las {NCASAS} encuestadoras le da {p(MED_DIF)} puntos de ventaja.'),
    ('¿Las encuestas de hoy recogen el efecto del debate?',
     'No. Todas se hicieron antes del debate del jueves 19 por la noche.'),
    ('¿Hasta cuándo se pueden publicar encuestas?',
     'Hasta el lunes 23 de noviembre. La ley electoral prohíbe publicarlas en los cinco días anteriores a la votación, desde el martes 24 hasta el cierre de los colegios el domingo 29.'),
]
enlaces = (f'<a href="{BASE}encuestas/">Encuestas elecciones generales 2026</a> · {L("encuestas-elecciones-generales-2026-19-noviembre", "Las encuestas de ayer, 19 de noviembre")} · '
           f'{L("debate-sanchez-feijoo-29n", "Debate Sánchez Feijóo")}')
foot = ('Datos: 40dB. para El País y la SER; Sigma Dos para El Mundo; EM-Analytics para Electomanía; Data10 para OKDiario; Public First para Politico; '
        'recogidas por Electográfica y Wikipedia; mediana de mapaelectoral.es/encuestas. Cálculo: encuestas_2011.py, en actualidad/src/resumenes.')

DATOS = {'F': F, 'ESC40': ESC40, 'PV40': PV40, 'MED': MED, 'MED_DIF': MED_DIF, 'NCASAS': NCASAS, 'MAS_CERCA': MAS_CERCA, 'DMIN': DMIN, 'DMAX': DMAX,
         'RECORTE_EM': RECORTE_EM, 'VOX40': VOX40, 'M40': round(M40, 1), 'DESCARGA': DESCARGA}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

TITULO = f'Encuestas elecciones generales 2026, hoy {DIA}: el PP gana en las cinco, por entre {p(DMIN)} y {p(DMAX)} puntos'
DEK = (f'Todas son de antes del debate. EM-Analytics recorta un punto la distancia y 40dB. la mantiene en {p(D40["dif"])}. '
       f'La mediana de las encuestas, en {p(MED_DIF)} a favor del PP.')
pieza(SLUG, 'Encuestas de hoy', TITULO, DEK, f'20 de noviembre de 2026 · actualizado a las {HORA}', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(TITULO); print(DEK); print('MED', MED, 'MED_PUB', MED_PUB, NCASAS, DESCARGA, 'MAS_CERCA', MAS_CERCA, 'M40', round(M40, 2), 'FUERA', [(e['casa'], e['fin']) for e in FUERA])
for f in F: print(f)
