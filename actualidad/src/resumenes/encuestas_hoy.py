"""«Encuestas de hoy» (18-11-2026): las encuestas de las elecciones generales publicadas este día, cada una frente a su
entrega anterior y frente a la mediana de /encuestas/. Una pieza por día, con URL y título fijos.

Encuestas del día: las de carga() (encuestas/src/construir.py: Electográfica y Wikipedia) con fecha de publicación HOY,
más las de EXTRA, publicadas después de la última actualización automática (se comprueban a mano con su fuente).
Mediana: medianas() de /encuestas/, la misma que muestra la página, a la hora de la última actualización (resumen.json).
Uso, desde la raíz: python3 actualidad/src/resumenes/encuestas_hoy.py
"""
import importlib.util
import json
from datetime import date

from comun import BASE, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
HOY = '2026-11-18'
HORA = '15.00'          # hora de Madrid de los datos de esta versión; va también en «actualizado» (dateModified)
SLUG = 'encuestas-elecciones-generales-2026-18-noviembre'
DIA = f'{int(HOY[8:])} de {MES[int(HOY[5:7]) - 1]}'

_spec = importlib.util.spec_from_file_location('enc_construir', RAIZ / 'encuestas/src/construir.py')
enc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enc)
_pub = lambda e: e.get('publicado') or e['fin']
ENCS = enc.carga()
RESUMEN = json.load(open(RAIZ / 'previsiones/datos/encuestas/resumen.json'))

# Publicadas hoy y que aún no recoge la actualización automática de las 7.41 (resumen.json, descargado 06:41 UTC).
# Sondaxe, 4.º tracking: La Voz de Galicia lo subió a su web el martes a las 20.54 y lo publica en su edición del miércoles;
# Electográfica y Wikipedia lo fechan el 18. PP incluye UPN-PP (como en las entregas anteriores de Sondaxe en carga()).
# Sumar = Frente Amplio 5,5 + Compromís 1,5 + Unidad del Pueblo Canario 0,5 (mismo criterio que partidos_encuestas.csv, #630).
EXTRA = [dict(reest=False, casa='Sondaxe', medio='La Voz de Galicia', inicio='2026-11-12', fin='2026-11-16', publicado=HOY, muestra='1000',
              voto={'PP': 29.0, 'PSOE': 27.0, 'VOX': 19.4, 'SUMAR': 7.5, 'PODEMOS': 1.2, 'SALF': 3.1, 'AA': 1.1},
              esc={'PP': '121', 'PSOE': '111', 'VOX': '71', 'SUMAR': '11', 'PODEMOS': '1', 'SALF': '1', 'AA': '3', 'ERC': '11', 'JUNTS': '4',
                   'BILDU': '10', 'PNV': '3', 'BNG': '2', 'CC': '1'},
              url='https://www.lavozdegalicia.es/noticia/espana/2026/11/17/pp-psoe-lanzan-llamada-voto-util-diferencia-estrecha/00031794944189590370512.htm',
              electografica='https://www.electografica.com/2026/11/encuesta-sondaxe-261118.html')]
assert RESUMEN['descargado'][:10] == HOY
for x in EXTRA:
    assert sum(int(v) for v in x['esc'].values()) == 350, x['casa']
    assert not any(enc.clave(e['casa']) == enc.clave(x['casa']) and _pub(e) == HOY for e in ENCS), f'{x["casa"]} ya está en carga(): quítala de EXTRA'

DIA_ENC = [e for e in ENCS if _pub(e) == HOY and not e['reest']] + EXTRA
DIA_ENC.sort(key=lambda e: e['voto']['PP'] - e['voto']['PSOE'])
assert sorted(enc.clave(e['casa']) for e in DIA_ENC) == ['40db', 'sondaxe'], [e['casa'] for e in DIA_ENC]
_val = sorted((e for e in ENCS if not e['reest'] and e['fin'] >= '2023-07-24'), key=_pub, reverse=True)
ANT = {enc.clave(e['casa']): next(x for x in _val if enc.clave(x['casa']) == enc.clave(e['casa']) and _pub(x) < HOY) for e in DIA_ENC}
URL40 = 'https://elpais.com/espana/elecciones-generales/2026-11-18/el-pp-consolida-su-posicion-frente-a-vox.html'
PDF40 = 'https://elpais.com/infografias/encuestas40db/2026/11-tracking-electoral/informe_tracking_dia06.pdf'


def nombre(e):
    return enc.nombre_casa(e['casa'])


def esc_c(e, k):
    """Escaños: el centro si la encuestadora da un intervalo (como el promedio de /encuestas/)."""
    a, b = enc.rango_esc(e['esc'][k])
    return (a + b) / 2


F = []
for e in DIA_ENC:
    a = ANT[enc.clave(e['casa'])]
    v, va = e['voto'], a['voto']
    F.append(dict(casa=nombre(e), medio=e['medio'], ini=e['inicio'], fin=e['fin'], n=int(e['muestra']), PP=v['PP'], PSOE=v['PSOE'], VOX=v['VOX'],
                  SUMAR=v.get('SUMAR'), dif=round(v['PP'] - v['PSOE'], 1), dif_ant=round(va['PP'] - va['PSOE'], 1), ant_pub=_pub(a), ant_fin=a['fin'],
                  dPP=round(v['PP'] - va['PP'], 1), dPSOE=round(v['PSOE'] - va['PSOE'], 1), dVOX=round(v['VOX'] - va['VOX'], 1),
                  escPP=e['esc']['PP'], escPSOE=e['esc']['PSOE'], escVOX=e['esc']['VOX'], pv=esc_c(e, 'PP') + esc_c(e, 'VOX'),
                  pv_ant=esc_c(a, 'PP') + esc_c(a, 'VOX')))
D40, SX = F
assert (D40['casa'], SX['casa']) == ('40dB.', 'Sondaxe') and (D40['dif'], SX['dif']) == (1.5, 2.0), F
assert (SX['dPP'], SX['dPSOE'], SX['dVOX'], SX['pv'], SX['pv_ant']) == (-0.7, 0.3, 1.4, 192, 191), SX
# 40dB. da intervalos: PP 128-139, Vox 51-60 → centro 133,5 + 55,5 = 189; su informe da 131 y 55 (186) como estimación central
ESC40 = {'PP': 131, 'PSOE': 122, 'VOX': 55, 'PP_AYER': 131, 'VOX_AYER': 58}
# Sondaxe: la distancia más corta entre PP y PSOE de esta campaña y la menor desde que hace encuestas de esta legislatura
SX_SERIE = [dict(pub=_pub(e), dif=round(e['voto']['PP'] - e['voto']['PSOE'], 1), VOX=e['voto']['VOX'])
            for e in sorted((x for x in _val if enc.clave(x['casa']) == 'sondaxe'), key=_pub)] + [dict(pub=HOY, dif=SX['dif'], VOX=SX['VOX'])]
SX_MIN = min(s['dif'] for s in SX_SERIE[:-1] if s['pub'] >= '2023-07-24')
assert SX['dif'] < SX_MIN, (SX['dif'], SX_MIN)
SX_VOX_MAX = max(s['VOX'] for s in SX_SERIE[:-1] if s['pub'] >= '2023-07-24')
assert SX['VOX'] > SX_VOX_MAX, SX_VOX_MAX
SX_DESDE = min(s['pub'] for s in SX_SERIE if s['pub'] >= '2023-07-24')

# Mediana de /encuestas/ (la de la página a la hora de su última actualización: aún no incluye la Sondaxe de hoy)
MED = {k: v for k, v in enc.medianas(ENCS, date.fromisoformat(HOY))[-1].items() if k != 'd'}
assert (MED['PP'], MED['PSOE'], MED['VOX']) == (31.4, 26.9, 18.8), MED
MED_DIF = round(MED['PP'] - MED['PSOE'], 1)
ULT = {}
for e in ENCS:
    if (date.fromisoformat(HOY) - date.fromisoformat(e['fin'])).days < enc.VENTANA_MEDIANA and not e['reest'] and enc.clave(e['casa']) not in ULT:
        ULT[enc.clave(e['casa'])] = e
NCASAS = len(ULT)
assert NCASAS == 18
MAS_LEJOS = sum(1 for k, e in ULT.items() if e['voto']['PP'] - e['voto']['PSOE'] > SX['dif'])
assert MAS_LEJOS > NCASAS / 2, MAS_LEJOS   # «más ajustada que la mayoría»


# Margen de la diferencia entre dos encuestas sin entrevistas en común (muestreo aleatorio simple, dos errores típicos)
def margen(p1, n1, p2, n2):
    p1, p2 = p1 / 100, p2 / 100
    return 2 * ((p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2) ** .5) * 100


# Sondaxe frente a su última entrega sin días de campo en común (2 al 4 de noviembre, 1.200 entrevistas)
SX_LIMPIA = next(x for x in _val if enc.clave(x['casa']) == 'sondaxe' and x['fin'] < SX['ini'])
assert (SX_LIMPIA['inicio'], SX_LIMPIA['fin'], SX_LIMPIA['muestra']) == ('2026-11-02', '2026-11-04', '1200'), SX_LIMPIA
SX_dVOX_L = round(SX['VOX'] - SX_LIMPIA['voto']['VOX'], 1)
SX_M_VOX = margen(SX['VOX'], SX['n'], SX_LIMPIA['voto']['VOX'], int(SX_LIMPIA['muestra']))
assert abs(SX_dVOX_L) < SX_M_VOX

CSS_ULTIMO = '<style>' + '\n'.join(l for l in enc.ESTILOS.split('\n') if l.startswith(('.ultimo-graf', '.bu-')) or ('.bu-b i' in l and 'prefers-color-scheme' in l or l.startswith(':root[data-theme="dark"] .bu-b'))) + '</style>'
assert CSS_ULTIMO.count('.bu-') >= 8
_graf = [(e, ANT[enc.clave(e['casa'])], f'{esc(nombre(e))} · {esc(e["medio"] or "El País y SER")} · {enc.dia(HOY)}') for e in DIA_ENC]
g_dia = enc.graficos_ultimo(_graf).replace('Las últimas encuestas, partido a partido', f'Las encuestas de hoy, {DIA}, partido a partido')
assert g_dia.count('class="bu"') == 2


def fecha(s):
    return f'{int(s[8:])} de {MES[int(s[5:7]) - 1]}'


g_med = figura('Las dos de hoy, más ajustadas que la mediana',
               f'Ventaja del PP sobre el PSOE, en puntos: las dos encuestas de hoy y la mediana de las {NCASAS} encuestadoras de las tres últimas semanas',
               barras([(f'{SX["casa"]}', SX['dif'], 'var(--pp)', p(SX['dif'])), (f'{D40["casa"]}', D40['dif'], 'var(--pp)', p(D40['dif'])),
                       ('Mediana', MED_DIF, 'var(--otros)', p(MED_DIF))], 6, 'Ventaja del PP sobre el PSOE en las encuestas de hoy y en la mediana', W=400, ml=90, fmt=p),
               f'Fuente: 40dB. para El País y la SER; Sondaxe para La Voz de Galicia; mediana de <a href="{BASE}encuestas/">mapaelectoral.es/encuestas</a>, sin la Sondaxe de hoy.',
               leyenda=[('Encuestas de hoy', 'var(--pp)'), ('Mediana de las encuestas', 'var(--otros)')],
               tabla=(['', 'PP', 'PSOE', 'Vox', 'Ventaja del PP'], [[SX['casa'], p(SX['PP']), p(SX['PSOE']), p(SX['VOX']), p(SX['dif'])],
                                                                    [D40['casa'], p(D40['PP']), p(D40['PSOE']), p(D40['VOX']), p(D40['dif'])],
                                                                    ['Mediana', p(MED['PP']), p(MED['PSOE']), p(MED['VOX']), p(MED_DIF)]]))

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="dato">Las dos encuestas de las elecciones generales publicadas este miércoles, 18 de noviembre, dejan al PSOE a dos puntos o menos del PP. El <a href="{URL40}">tracking de 40dB. para El País y la SER</a> da al PP el <strong>{p(D40['PP'])} %</strong> y al PSOE el <strong>{p(D40['PSOE'])} %</strong>, {p(D40['dif'])} puntos de distancia; el de <a href="{EXTRA[0]['url']}">Sondaxe para La Voz de Galicia</a>, el <strong>{p(SX['PP'])} %</strong> y el <strong>{p(SX['PSOE'])} %</strong>, {p(SX['dif'])} puntos. Vox va en direcciones opuestas: baja al {p(D40['VOX'])} % en 40dB. y sube al {p(SX['VOX'])} % en Sondaxe. En escaños, PP y Vox suman {ESC40['PP'] + ESC40['VOX']} en 40dB. y {SX['pv']:.0f} en Sondaxe, por encima de la mayoría absoluta de 176.</p>
{CSS_ULTIMO}
{g_dia}
<p data-tipo="dato">En Sondaxe, el PP baja {p(-SX['dPP'])} puntos respecto a su entrega anterior y el PSOE sube {p(SX['dPSOE'])}: la distancia entre los dos pasa de {p(SX['dif_ant'])} a {p(SX['dif'])} puntos, la más corta que ha dado Sondaxe desde las generales de 2023. Vox sube {p(SX['dVOX'])} puntos, hasta su dato más alto en la misma serie. Sondaxe da al PP {SX['escPP']} escaños, al PSOE {SX['escPSOE']} y a Vox {SX['escVOX']}. El trabajo de campo se hizo del 12 al 16 de noviembre, con 1.000 entrevistas por teléfono y en línea, según la <a href="{EXTRA[0]['electografica']}">ficha que recoge Electográfica</a>. La Voz de Galicia lo adelantó en su web el martes por la noche.</p>
<p data-tipo="dato">40dB., con 2.000 entrevistas en línea del 13 al 17 de noviembre, da al PP {ESC40['PP']} escaños, al PSOE {ESC40['PSOE']} y a Vox {ESC40['VOX']}, según su <a href="{PDF40}">informe</a>. Vox baja por quinta entrega seguida y pierde {ESC40['VOX_AYER'] - ESC40['VOX']} diputados en un día. Lo contamos con más detalle en {L("encuesta-40db-vox-17-29n", "la pieza sobre el tracking de 40dB. de hoy")}.</p>
<h2>Frente a la mediana de las encuestas</h2>
<p data-tipo="dato">Las dos ven la carrera más ajustada que la mayoría. La mediana de la última encuesta de cada una de las {NCASAS} encuestadoras de las tres últimas semanas, la que resume <a href="{BASE}encuestas/">nuestra página de encuestas de las elecciones generales 2026</a>, da al PP el {p(MED['PP'])} %, al PSOE el {p(MED['PSOE'])} % y a Vox el {p(MED['VOX'])} %: {p(MED_DIF)} puntos entre PP y PSOE. Esa mediana es la de la última actualización automática de la página, de primera hora de este miércoles, y todavía no incluye la Sondaxe de hoy.</p>
{g_med}
<h2>Lo que estas encuestas no dicen</h2>
<p data-tipo="contexto">Las dos son trackings: cada día suman las entrevistas de los últimos cinco días y cambian la más antigua por la más reciente, así que una entrega comparte casi todas sus entrevistas con la anterior. Frente a su última encuesta sin días de campo en común, la del 2 al 4 de noviembre, Sondaxe da a Vox {p(SX_dVOX_L)} puntos más, dentro del margen de error de la diferencia, de unos ±{p(SX_M_VOX)} puntos. Con 1.000 entrevistas, el margen de cada porcentaje de Sondaxe es de ±3,1 puntos; el de 40dB., de ±2,2.</p>
<p data-tipo="contexto">Esta pieza recoge las encuestas publicadas hasta las {HORA} de este miércoles. Las que salgan esta noche llegarán a <a href="{BASE}encuestas/">la página de encuestas</a> con su actualización automática. La ley prohíbe publicar encuestas desde el martes 24 de noviembre.</p>
'''

preguntas = [
    ('¿Qué encuestas de las elecciones generales se han publicado hoy, 18 de noviembre?',
     f'Dos: el tracking de 40dB. para El País y la SER (PP {p(D40["PP"])} %, PSOE {p(D40["PSOE"])} %, Vox {p(D40["VOX"])} %) y el de Sondaxe para La Voz de Galicia '
     f'(PP {p(SX["PP"])} %, PSOE {p(SX["PSOE"])} %, Vox {p(SX["VOX"])} %), hasta las {HORA}.'),
    ('¿Quién gana las elecciones generales según las encuestas de hoy?',
     f'El PP, en las dos, por {p(D40["dif"])} puntos en 40dB. y por {p(SX["dif"])} en Sondaxe. PP y Vox suman mayoría absoluta en las dos: {ESC40["PP"] + ESC40["VOX"]} y {SX["pv"]:.0f} escaños.'),
    ('¿Qué dice la mediana de las encuestas?',
     f'La mediana de las {NCASAS} encuestadoras de las tres últimas semanas da al PP el {p(MED["PP"])} %, al PSOE el {p(MED["PSOE"])} % y a Vox el {p(MED["VOX"])} %. Está en mapaelectoral.es/encuestas.'),
]
enlaces = (f'<a href="{BASE}encuestas/">Encuestas elecciones generales 2026</a> · {L("encuesta-40db-vox-17-29n", "El tracking de 40dB. de hoy")} · '
           f'{L("cuanto-discrepan-encuestas-29n", "Cuánto discrepan las encuestas")} · {L("encuestas-primera-semana-campana-29n", "Las encuestas, semana a semana")}')
foot = ('Datos: 40dB. para El País y la SER; Sondaxe para La Voz de Galicia; encuestas recogidas por Electográfica y Wikipedia; mediana de mapaelectoral.es/encuestas. '
        'Cálculo: actualidad/src/resumenes/encuestas_hoy.py.')

DATOS = {'F': F, 'ESC40': ESC40, 'MED': MED, 'MED_DIF': MED_DIF, 'NCASAS': NCASAS, 'SX_MIN': SX_MIN, 'SX_VOX_MAX': SX_VOX_MAX, 'SX_DESDE': SX_DESDE,
         'SX_dVOX_L': SX_dVOX_L, 'MAS_LEJOS': MAS_LEJOS, 'SX_M_VOX': round(SX_M_VOX, 1), 'SX_LIMPIA': {k: SX_LIMPIA[k] for k in ('inicio', 'fin', 'muestra')}}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

TITULO = f'Encuestas elecciones generales 2026, hoy {DIA}: el PSOE, a dos puntos o menos del PP'
DEK = (f'40dB. da al PP el {p(D40["PP"])} % y al PSOE el {p(D40["PSOE"])} %; Sondaxe, el {p(SX["PP"])} % y el {p(SX["PSOE"])} %. '
       f'La mediana de las encuestas los separa {p(MED_DIF)} puntos.')
pieza(SLUG, 'Encuestas de hoy', TITULO, DEK, f'18 de noviembre de 2026 · actualizado a las {HORA}', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(TITULO); print(DEK)
print('F', F); print('SX_MIN', SX_MIN, 'SX_VOX_MAX', SX_VOX_MAX, SX_DESDE, 'MARGEN', round(SX_M_VOX, 2), SX_dVOX_L)
