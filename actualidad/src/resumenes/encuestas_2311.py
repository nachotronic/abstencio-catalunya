"""«Encuestas de hoy» (23-11-2026): las encuestas de las elecciones generales publicadas el lunes 23, último día antes de la veda
(LOREG, art. 69.7: no se pueden publicar del 24 al 28). Cada una frente a su entrega anterior y frente a la mediana de /encuestas/.
Una pieza por día, con URL y título fijos (la del 20 es encuestas_2011.py).

Encuestas: las de carga() (encuestas/src/construir.py: Electográfica y Wikipedia) con fecha de publicación 23-11 en la
actualización automática de esta mañana: Target Point, GESOP, Cluster17, 40dB. (la encuesta final, 7.500 entrevistas), NC Report e IMOP.
IMOP: la de hoy entra como «IMOP» y las anteriores como «IMOP Insights»; es la misma casa para El Confidencial (ALIAS_CASA,
#675), también en la mediana.
Uso, desde la raíz: python3 actualidad/src/resumenes/encuestas_2311.py
"""
import importlib.util
import json
from datetime import date

from comun import BASE, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
HOY = '2026-11-23'
HORA = '10.00'           # hora de Madrid de los datos de esta versión; va también en «actualizado» (dateModified)
SLUG = 'encuestas-elecciones-generales-2026-23-noviembre'
DIA = f'{int(HOY[8:])} de {MES[int(HOY[5:7]) - 1]}'

_spec = importlib.util.spec_from_file_location('enc_construir', RAIZ / 'encuestas/src/construir.py')
enc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enc)
_pub = lambda e: e.get('publicado') or e['fin']
RESUMEN = json.load(open(RAIZ / 'previsiones/datos/encuestas/resumen.json'))

ENCS = enc.carga()
# Data10 para OKDiario, campo hasta el 22: carga() la fecha el 22 (fin de campo), pero OKDiario la publica hoy,
# «a seis días del 29-N» (titular y URL de la noticia).
_d10 = lambda e: enc.clave(e['casa']) == 'data10' and e['fin'] == '2026-11-22' and 'seis-dias-del-29-n' in e['url']
HOYS = [e for e in ENCS if (_pub(e) == HOY or _d10(e)) and not e['reest'] and e['voto']]
assert sorted(enc.clave(e['casa']) for e in HOYS) == ['40db', 'cluster17', 'data10', 'gesop', 'imop', 'ncreport', 'targetpoint'], [e['casa'] for e in HOYS]
_val = sorted((e for e in ENCS if not e['reest'] and e['voto'] and e['fin'] >= '2023-07-24'), key=lambda e: (_pub(e), e['fin']), reverse=True)


def anterior(e):
    """La entrega anterior de la misma encuestadora."""
    return next((x for x in _val if enc.clave(x['casa']) == enc.clave(e['casa']) and x is not e and (_pub(x), x['fin']) < (_pub(e), e['fin'])), None)


def nombre(e):
    return 'IMOP Insights' if enc.clave(e['casa']) == 'imop' else enc.nombre_casa(e['casa'])


def margen_dif(p1, p2, n_):
    """Dos errores típicos de la distancia entre dos partidos de una misma encuesta (muestreo aleatorio simple)."""
    p1, p2 = p1 / 100, p2 / 100
    return 2 * ((p1 + p2 - (p1 - p2) ** 2) / n_) ** .5 * 100


F = []
for e in HOYS:
    a = anterior(e)
    v = e['voto']
    f = dict(casa=nombre(e), clave=enc.clave(e['casa']), medio=e['medio'], ini=e['inicio'], fin=e['fin'], n=int(e['muestra']), url=e['url'],
             PP=v['PP'], PSOE=v['PSOE'], VOX=v['VOX'], dif=round(v['PP'] - v['PSOE'], 1), pv=enc.suma_pv(e),
             marg=round(margen_dif(v['PP'], v['PSOE'], int(e['muestra'])), 1), esc=e['esc'])
    va = a['voto']
    f.update(dif_ant=round(va['PP'] - va['PSOE'], 1), dVOX=round(v['VOX'] - va['VOX'], 1), ant_fin=a['fin'], ant_n=int(a['muestra']))
    F.append(f)
F.sort(key=lambda f: -f['dif'])
G = {f['clave']: f for f in F}
TP, GE, CL, D40, NC, IM, D10 = (G[k] for k in ('targetpoint', 'gesop', 'cluster17', '40db', 'ncreport', 'imop', 'data10'))
assert (D10['PP'], D10['PSOE'], D10['pv'], D10['dif_ant']) == (31.7, 27.3, (194, 194), 5.1)
NUM = {6: 'seis', 7: 'siete'}[len(F)]
assert NUM == 'siete'

# PP primero en seis; Cluster17, PSOE por delante, dentro del margen de esa distancia
assert [f['clave'] for f in F if f['dif'] < 0] == ['cluster17'] and CL['dif'] == -2.4 and -CL['dif'] < CL['marg'] == 4.3
assert int(CL['esc']['PSOE']) == 133 and int(CL['esc']['PP']) == 123
# 40dB.: la encuesta final, 7.500 entrevistas del 10 al 21; 0,9 puntos, dentro del margen de ±1,8
assert (D40['n'], D40['ini'], D40['fin'], D40['dif'], D40['marg']) == (7500, '2026-11-10', '2026-11-21', 0.9, 1.8)
assert (D40['ant_fin'], D40['dif_ant']) == ('2026-11-21', 0.3)
# PP y Vox, por encima de 176 en todas, también en el extremo bajo
PVMIN = min(f['pv'][0] for f in F)
assert PVMIN == 178 and PVMIN == D40['pv'][0] and CL['pv'] == (180, 180)
PVMAX = max(f['pv'][1] for f in F)
assert PVMAX == 201 and NC['pv'] == (196, 201)
DMAX = max(f['dif'] for f in F)
assert DMAX == 5.1 and NC['dif'] == DMAX and NC['dif'] > NC['marg']
# PP y PSOE: frente a su entrega anterior, la distancia baja en cinco de las siete y sube en dos
BAJA = sorted(f['casa'] for f in F if f['dif'] < f['dif_ant'])
SUBE = sorted(f['casa'] for f in F if f['dif'] > f['dif_ant'])
assert BAJA == ['Cluster17', 'Data10', 'IMOP Insights', 'NC Report', 'Target Point'] and SUBE == ['40dB.', 'GESOP'], (BAJA, SUBE)

# Mediana de /encuestas/ con IMOP en una sola casa
DESCARGA = RESUMEN['descargado']
MED = {k: v for k, v in enc.medianas(ENCS, date.fromisoformat(HOY))[-1].items() if k != 'd'}
MED_DIF = round(MED['PP'] - MED['PSOE'], 1)
ULT = {}
for e in ENCS:
    if (date.fromisoformat(HOY) - date.fromisoformat(e['fin'])).days < enc.VENTANA_MEDIANA and not e['reest'] and e['voto'] and enc.clave(e['casa']) not in ULT:
        ULT[enc.clave(e['casa'])] = e
NCASAS = len(ULT)
MAS_AJUSTADA = sorted(f['casa'] for f in F if f['dif'] < MED_DIF)

CSS_ULTIMO = '<style>' + '\n'.join(l for l in enc.ESTILOS.split('\n') if l.startswith(('.ultimo-graf', '.bu-')) or ('.bu-b i' in l and 'prefers-color-scheme' in l or l.startswith(':root[data-theme="dark"] .bu-b'))) + '</style>'
assert CSS_ULTIMO.count('.bu-') >= 8
_orden = {f['clave']: i for i, f in enumerate(F)}
_graf = [(e, anterior(e), f'{esc(nombre(e))} · {esc(e["medio"])} · campo hasta el {enc.dia(e["fin"])}') for e in sorted(HOYS, key=lambda e: _orden[enc.clave(e['casa'])])]
g_dia = enc.graficos_ultimo(_graf).replace('Las últimas encuestas, partido a partido', f'Las encuestas de hoy, {DIA}, partido a partido')
import re as _re
_subs = iter(f'Cambio frente a su entrega anterior, con campo hasta el {enc.dia(a["fin"])}' for _, a, _ in _graf)
g_dia = _re.sub(r'Cambio frente a su encuesta del [^<]+', lambda m: next(_subs), g_dia)
assert g_dia.count('Cambio frente a su entrega anterior') == 7 and g_dia.count('class="bu"') == 7

_col = lambda f: 'var(--pp)' if f['dif'] > 0 else 'var(--psoe)'
_txt = lambda f: ('PP +' if f['dif'] > 0 else 'PSOE +') + p(abs(f['dif']))
g_med = figura(f'El PP, por delante en seis de las siete; Cluster17 pone primero al PSOE',
               f'Ventaja del primer partido sobre el segundo, en puntos, en cada encuesta de hoy y en la mediana de las {NCASAS} encuestadoras de las tres últimas semanas',
               barras([(f['casa'], abs(f['dif']), _col(f), _txt(f)) for f in F] + [('Mediana', MED_DIF, 'var(--otros)', 'PP +' + p(MED_DIF))], 6,
                      'Ventaja del primer partido en las encuestas de hoy y en la mediana', W=400, ml=118, fmt=p),
               f'Fuente: las encuestas citadas, recogidas por Electográfica y Wikipedia. Mediana de <a href="{BASE}encuestas/">mapaelectoral.es/encuestas</a>.',
               leyenda=[('PP por delante', 'var(--pp)'), ('PSOE por delante', 'var(--psoe)'), ('Mediana de las encuestas', 'var(--otros)')],
               tabla=(['', 'PP', 'PSOE', 'Vox'], [[f['casa'], p(f['PP']), p(f['PSOE']), p(f['VOX'])] for f in F] + [['Mediana', p(MED['PP']), p(MED['PSOE']), p(MED['VOX'])]]))

pv_txt = lambda f: f'{f["pv"][0]}' if f['pv'][0] == f['pv'][1] else f'entre {f["pv"][0]} y {f["pv"][1]}'
a_ = lambda f, t: f'<a href="{f["url"]}">{t}</a>'
cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="dato">PP y Vox suman mayoría absoluta en las siete encuestas de las elecciones generales publicadas este lunes, el último día en que la ley permite publicarlas: entre <strong>{PVMIN} y {PVMAX} escaños</strong>, por encima de los 176. El PP va primero en seis. La que le da más ventaja es {a_(NC, "NC Report para La Razón")}, {p(NC['dif'])} puntos sobre el PSOE (PP {p(NC['PP'])} %, PSOE {p(NC['PSOE'])} %). Le siguen {a_(D10, "Data10 para OKDiario")}, con {p(D10['dif'])}; {a_(IM, "IMOP Insights para El Confidencial")}, con {p(IM['dif'])}; {a_(GE, "GESOP para Prensa Ibérica")}, con {p(GE['dif'])}, y {a_(TP, "Target Point para El Debate")}, con {p(TP['dif'])}.</p>
<p data-tipo="dato">La encuesta final de {a_(D40, "40dB. para El País y la SER")}, con {n(D40['n'])} entrevistas del 10 al 21 de noviembre, deja la distancia en <strong>{p(D40['dif'])} puntos</strong>: PP {p(D40['PP'])} %, PSOE {p(D40['PSOE'])} %, Vox {p(D40['VOX'])} %. {a_(CL, "Cluster17 para Agenda Pública")} es la única que da más voto al PSOE: {p(CL['PSOE'])} % frente al {p(CL['PP'])} % del PP, y {CL['esc']['PSOE']} escaños frente a {CL['esc']['PP']}. Aun así, PP y Vox suman {pv_txt(CL)} en su reparto.</p>
{CSS_ULTIMO}
{g_dia}
<p data-tipo="dato">Frente a su entrega anterior, la distancia entre PP y PSOE baja en cinco de las siete: en NC Report, de {p(NC['dif_ant'])} a {p(NC['dif'])} puntos; en Data10, de {p(D10['dif_ant'])} a {p(D10['dif'])}; en IMOP Insights, de {p(IM['dif_ant'])} a {p(IM['dif'])}; en Target Point, de {p(TP['dif_ant'])} a {p(TP['dif'])}, y en Cluster17, que en su encuesta anterior, de finales de agosto, daba al PP {p(CL['dif_ant'])} puntos de ventaja. Sube en GESOP, de {p(GE['dif_ant'])} a {p(GE['dif'])}, y en 40dB., de {p(D40['dif_ant'])} en su último tracking a {p(D40['dif'])}. En escaños, PP y Vox suman {pv_txt(NC)} en NC Report, {pv_txt(D10)} en Data10, {pv_txt(IM)} en IMOP Insights, {pv_txt(GE)} en GESOP, {pv_txt(TP)} en Target Point y {pv_txt(D40)} en 40dB., sumando sus horquillas.</p>
<h2>Frente a la mediana de las encuestas</h2>
<p data-tipo="dato">La mediana de la última encuesta de cada una de las {NCASAS} encuestadoras de las tres últimas semanas, la que resume <a href="{BASE}encuestas/">nuestra página de encuestas de las elecciones generales 2026</a>, da al PP el {p(MED['PP'])} %, al PSOE el {p(MED['PSOE'])} % y a Vox el {p(MED['VOX'])} %: {p(MED_DIF)} puntos entre PP y PSOE. 40dB. y Target Point ven la carrera más ajustada que esa mediana, y Cluster17 la da la vuelta; NC Report, Data10, IMOP Insights y GESOP la ven más abierta.</p>
{g_med}
<h2>Lo que estas encuestas no dicen</h2>
<p data-tipo="contexto">Con {n(D40['n'])} entrevistas, los {p(D40['dif'])} puntos de 40dB. quedan dentro del margen de error de esa distancia, de unos ±{p(D40['marg'])} puntos: es un empate técnico. Lo mismo pasa con los {p(abs(CL['dif']))} puntos del PSOE en Cluster17 (±{p(CL['marg'])}), con los {p(TP['dif'])} de Target Point (±{p(TP['marg'])}), con los {p(GE['dif'])} de GESOP (±{p(GE['marg'])}) y con los {p(IM['dif'])} de IMOP Insights (±{p(IM['marg'])}). Solo lo superan la ventaja de Data10, {p(D10['dif'])} puntos con un margen de ±{p(D10['marg'])} por sus {n(D10['n'])} entrevistas, y la de NC Report, {p(NC['dif'])} con ±{p(NC['marg'])}, por poco.</p>
<p data-tipo="contexto">Esta pieza recoge las encuestas publicadas hasta las {HORA} de este lunes. Desde mañana, martes 24, y hasta el cierre de los colegios el domingo 29, la ley prohíbe publicar encuestas: por qué, y qué son las «encuestas de Andorra», en {L("veda-encuestas-29n", "la pieza de la veda de encuestas")}.</p>
'''
assert sorted(MAS_AJUSTADA) == ['40dB.', 'Cluster17', 'Target Point'], MAS_AJUSTADA
assert [f['casa'] for f in F if abs(f['dif']) >= f['marg']] == ['NC Report', 'Data10']
assert sorted(f['casa'] for f in F if f['dif'] > MED_DIF) == ['Data10', 'GESOP', 'IMOP Insights', 'NC Report']

preguntas = [
    (f'¿Qué dicen las encuestas de las elecciones generales hoy, {DIA}?',
     '; '.join(f'{f["casa"]}: PP {p(f["PP"])} %, PSOE {p(f["PSOE"])} %, Vox {p(f["VOX"])} %' for f in F) + '.'),
    ('¿Quién gana las elecciones generales según las encuestas?',
     f'El PP, en seis de las siete publicadas hoy; Cluster17 da más voto al PSOE. La mediana de las {NCASAS} encuestadoras da al PP {p(MED_DIF)} puntos de ventaja.'),
    ('¿Suman mayoría PP y Vox en las encuestas?',
     f'Sí, en las siete de hoy: entre {PVMIN} y {PVMAX} escaños, sumando sus horquillas. La mayoría absoluta está en 176.'),
    ('¿Hasta cuándo se pueden publicar encuestas?',
     'Hasta hoy, lunes 23 de noviembre. La ley electoral prohíbe publicarlas desde el martes 24 hasta el cierre de los colegios el domingo 29.'),
]
enlaces = (f'<a href="{BASE}encuestas/">Encuestas elecciones generales 2026</a> · {L("encuestas-elecciones-generales-2026-20-noviembre", "Las encuestas del 20 de noviembre")} · '
           f'{L("veda-encuestas-29n", "Veda de encuestas")}')
foot = ('Datos: Target Point para El Debate; GESOP para Prensa Ibérica; Cluster17 para Agenda Pública; 40dB. para El País y la SER; NC Report para La Razón; Data10 para OKDiario; '
        'IMOP Insights para El Confidencial; recogidas por Electográfica y Wikipedia; mediana de mapaelectoral.es/encuestas. Cálculo: encuestas_2311.py, en actualidad/src/resumenes.')

DATOS = {'F': F, 'MED': MED, 'MED_DIF': MED_DIF, 'NCASAS': NCASAS, 'PVMIN': PVMIN, 'PVMAX': PVMAX, 'DMAX': DMAX, 'DESCARGA': DESCARGA}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

TITULO = f'Encuestas elecciones generales 2026, hoy {DIA}: PP y Vox suman mayoría absoluta en las siete'
DEK = (f'Es el último día en que se pueden publicar. El PP va primero en seis; Cluster17 da más voto al PSOE. '
       f'La encuesta final de 40dB. deja la distancia en {p(D40["dif"])} puntos.')
pieza(SLUG, 'Encuestas de hoy', TITULO, DEK, f'23 de noviembre de 2026 · actualizado a las {HORA}', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(TITULO); print(DEK); print('MED', MED, NCASAS, DESCARGA, 'MAS_AJUSTADA', MAS_AJUSTADA)
for f in F: print({k: f[k] for k in ('casa', 'fin', 'n', 'PP', 'PSOE', 'VOX', 'dif', 'dif_ant', 'marg', 'pv', 'ant_fin')})
