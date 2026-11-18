"""«La encuesta de El País» (18-11-2026): sexta entrega del tracking de 40dB. para El País y la SER (campo del 13 al 17 de
noviembre, 2.000 entrevistas en línea). Vox baja al 17,0 %, y PP y Vox suman 186 escaños, la cifra más baja del tracking.

Datos de voto: previsiones/datos/encuestas/encuestas_limpias.csv (Action «Encuestas», desde Electográfica y Wikipedia).
Escaños, preferencia de presidente y de gobierno: informe del día 6 de 40dB. publicado por El País (PDF), páginas 6, 8, 9, 12 y 14.
Mediana de /encuestas/: encuestas/src/construir.py, carga() y medianas(), a 18 de noviembre de 2026.
Uso, desde la raíz: python3 actualidad/src/resumenes/tracking_40db.py
"""
import csv
import importlib.util
import json
from datetime import date

from comun import BASE, COLOR, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
PDF = 'https://elpais.com/infografias/encuestas40db/2026/11-tracking-electoral/informe_tracking_dia06.pdf'
PDF_PRE = 'https://ep00.epimg.net/infografias/encuestas40db/2026/11-preelectoral/2026_11_preelectoral_informe.pdf'
ELECTO = 'https://www.electografica.com/2026/11/encuesta-40db-261118.html'
MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
HOY = '2026-11-18'

filas = [r for r in csv.DictReader(open(RAIZ / 'previsiones/datos/encuestas/encuestas_limpias.csv', encoding='utf-8'))
         if r['ambito'] == 'ESPAÑA' and r['encuestadora'] == '40dB.']
filas.sort(key=lambda r: r['publicado'])
f = lambda r, k: float(r[k]) if r[k] else None
S = [dict(pub=r['publicado'], ini=r['campo_inicio'], fin=r['campo_fin'], n=int(r['muestra'] or 0), PP=f(r, 'PP'), PSOE=f(r, 'PSOE'),
          VOX=f(r, 'VOX'), SUMAR=f(r, 'SUMAR'), POD=f(r, 'PODEMOS')) for r in filas]
# preelectoral (9-11) y las seis entregas del tracking (13 a 18 de noviembre)
T = [s for s in S if s['pub'] >= '2026-11-09']
assert [s['pub'] for s in T] == ['2026-11-09', '2026-11-13', '2026-11-14', '2026-11-15', '2026-11-16', '2026-11-17', '2026-11-18'], T
PRE, D1, AYER, D6 = T[0], T[1], T[-2], T[-1]
assert (D6['PP'], D6['PSOE'], D6['VOX'], D6['SUMAR'], D6['POD'], D6['n']) == (32.2, 30.7, 17.0, 5.2, 1.2, 2000), D6
assert (D6['ini'], D6['fin'], AYER['ini'], AYER['fin']) == ('2026-11-13', '2026-11-17', '2026-11-12', '2026-11-16')
for s in S:
    s['dif'] = round(s['PP'] - s['PSOE'], 1)
VOX_TR = [s['VOX'] for s in T[1:]]
assert all(a > b for a, b in zip(VOX_TR, VOX_TR[1:])), VOX_TR   # Vox baja en cada entrega del tracking
VOX_ANT = max((s for s in S[:-1] if s['VOX'] < D6['VOX']), key=lambda s: s['pub'])   # última vez por debajo del 17,0
assert VOX_ANT['pub'] == '2025-10-06' and VOX_ANT['VOX'] == 16.7, VOX_ANT
PSOE_ANT = max((s for s in S[:-1] if s['PSOE'] > D6['PSOE']), key=lambda s: s['pub'])
assert PSOE_ANT['pub'] == '2024-07-01', PSOE_ANT
PP_ANT = max((s for s in S[:-1] if s['PP'] > D6['PP']), key=lambda s: s['pub'])
assert PP_ANT['pub'] == '2026-09-07', PP_ANT
DIF_TR = [s['dif'] for s in T[1:]]


def fecha(s, anio=True):
    a, m, d = s.split('-')
    return f'{int(d)} de {MES[int(m) - 1]}' + (f' de {a}' if anio else '')


def mes(s):
    return f'{MES[int(s[5:7]) - 1]} de {s[:4]}'


# Margen de la diferencia entre dos encuestas sin entrevistas en común (muestreo aleatorio simple, dos errores típicos)
def margen(p1, n1, p2, n2):
    p1, p2 = p1 / 100, p2 / 100
    return 2 * ((p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2) ** .5) * 100


M_VOX_PRE = margen(D6['VOX'], D6['n'], PRE['VOX'], PRE['n'])
M_VOX_D1 = margen(D6['VOX'], D6['n'], D1['VOX'], D1['n'])
assert D1['fin'] < D6['ini'] and PRE['fin'] < D6['ini']    # sin días de campo en común
assert abs(D6['VOX'] - D1['VOX']) < M_VOX_D1 and abs(D6['VOX'] - PRE['VOX']) < M_VOX_PRE

# Informe del día 6, pág. 8 y 9 (escaños; la serie de la pág. 9 da la entrega anterior y la preelectoral)
ESC = {'PP': 131, 'PSOE': 122, 'Vox': 55, 'Frente Amplio': 5, 'Compromís, Ara Més y UPC': 4, 'Podemos': 1, 'Otros': 32}
ESC_AYER = {'PP': 131, 'PSOE': 120, 'Vox': 58, 'Frente Amplio': 5, 'Compromís, Ara Més y UPC': 5, 'Podemos': 0, 'Otros': 31}
PV_SERIE = [('2-4 nov.', 129 + 61), ('10-12', 126 + 64), ('10-13', 126 + 63), ('10-14', 128 + 62), ('10-15', 128 + 62), ('12-16', 131 + 58), ('13-17', 131 + 55)]
RANGO = {'PP': '126-137', 'PSOE': '118-127', 'Vox': '51-60', 'Podemos': '0-1'}
assert sum(ESC.values()) == 350 and sum(ESC_AYER.values()) == 350
PV, PV_AYER = ESC['PP'] + ESC['Vox'], ESC_AYER['PP'] + ESC_AYER['Vox']
assert PV == PV_SERIE[-1][1] == min(v for _, v in PV_SERIE) and PV_AYER == PV_SERIE[-2][1]
# Pág. 12: mejor presidente (población general) y pág. 14: gobierno preferido; entre paréntesis, la preelectoral (2.000 entrevistas)
PRES = [('Pedro Sánchez', 32.4, 30.0), ('Alberto Núñez Feijóo', 22.5, 20.0), ('Santiago Abascal', 16.6, 19.8)]
GOB = [('PP en coalición con Vox', 23.3, 25.4), ('PSOE en coalición con Frente Amplio', 22.2, 23.0), ('PSOE en solitario', 16.6, 13.8),
       ('PP en solitario', 15.2, 14.5)]
SIG = {t: abs(a - b) > margen(a, 2000, b, 2000) for t, a, b in PRES + GOB}
assert [t for t, v in SIG.items() if v] == ['Santiago Abascal', 'PSOE en solitario'], SIG

# ---------- Mediana de /encuestas/ y gráfico de «Lo último» (#517) ----------
_spec = importlib.util.spec_from_file_location('enc_construir', RAIZ / 'encuestas/src/construir.py')
enc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enc)
ENCS = enc.carga()
MED = {k: v for k, v in enc.medianas(ENCS, date(2026, 11, 18))[-1].items() if k != 'd'}
assert (MED['PP'], MED['PSOE'], MED['VOX']) == (31.4, 26.9, 18.8), MED
MED_DIF = round(MED['PP'] - MED['PSOE'], 1)
# última encuesta de cada encuestadora en la ventana de la mediana (como en medianas())
ULT = {}
for e in ENCS:
    if (date(2026, 11, 18) - date.fromisoformat(e['fin'])).days < enc.VENTANA_MEDIANA and not e['reest'] and enc.clave(e['casa']) not in ULT:
        ULT[enc.clave(e['casa'])] = e
NCASAS = len(ULT)
MAS_CERCA = sorted(enc.nombre_casa(e['casa']) for k, e in ULT.items() if k != '40db' and e['voto']['PP'] - e['voto']['PSOE'] < D6['dif'])
assert ULT['40db']['voto']['VOX'] == D6['VOX'] and NCASAS == 18, (ULT['40db'], NCASAS)
assert MAS_CERCA == ['CIS', 'SW Demoscopia'] and all(ULT[k]['voto']['PSOE'] > ULT[k]['voto']['PP'] for k in ('cis', 'swdemoscopia'))
VOX_MENOS = sorted(enc.nombre_casa(e['casa']) for k, e in ULT.items() if k != '40db' and e['voto']['VOX'] < D6['VOX'])

_pub = lambda e: e.get('publicado') or e['fin']
_val = sorted((e for e in ENCS if not e['reest'] and e['fin'] >= '2023-07-24'), key=_pub, reverse=True)
e6 = next(e for e in _val if enc.clave(e['casa']) == '40db' and _pub(e) == HOY)
e5 = next(e for e in _val if enc.clave(e['casa']) == '40db' and _pub(e) < HOY)
assert _pub(e5) == '2026-11-17', e5
CSS_ULTIMO = '<style>' + '\n'.join(l for l in enc.ESTILOS.split('\n') if l.startswith(('.ultimo-graf', '.bu-')) or ('.bu-b i' in l and 'prefers-color-scheme' in l or l.startswith(':root[data-theme="dark"] .bu-b'))) + '</style>'
assert CSS_ULTIMO.count('.bu-') >= 8, CSS_ULTIMO
g_40 = enc.graficos_ultimo([(e6, e5, f'40dB. · El País y SER · {enc.dia(HOY)}')]).replace(
    'Las últimas encuestas, partido a partido', '40dB., partido a partido: hoy frente a ayer')
# la misma encuesta, con la raya en la mediana de /encuestas/ en lugar de la entrega anterior
_med = {'voto': {k: v for k, v in MED.items() if k in e6['voto']}, 'publicado': HOY, 'fin': HOY}
g_med = (enc.graficos_ultimo([(e6, _med, f'40dB. · El País y SER · {enc.dia(HOY)}')])
         .replace('Las últimas encuestas, partido a partido', '40dB. frente a la mediana de las encuestas')
         .replace(f'Cambio frente a su encuesta del {enc.dia(HOY)}', f'Diferencia con la mediana de las {NCASAS} encuestadoras')
         .replace('La raya fina marca lo que daba la encuesta anterior de la misma encuestadora',
                  f'La raya fina marca la mediana de la última encuesta de cada una de las {NCASAS} encuestadoras de las tres últimas semanas'))
assert 'Diferencia con la mediana' in g_med and 'mediana de la última encuesta' in g_med


# ---------- Gráficos ----------
def evolucion():
    """Líneas: PP, PSOE y Vox en la preelectoral y en las seis entregas del tracking."""
    W, H, ml, mr, mt, mb = 400, 250, 30, 44, 12, 40
    lo, hi = 16, 34
    N = len(T)
    x = lambda i: ml + i * (W - ml - mr) / (N - 1)
    y = lambda v: mt + (hi - v) / (hi - lo) * (H - mt - mb)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Estimación de voto de PP, PSOE y Vox en la preelectoral de 40dB. y en las seis entregas de su tracking">']
    for v in range(lo, hi + 1, 2):
        out.append(f'<line x1="{ml}" x2="{W - mr}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--grid)"/>'
                   f'<text x="{ml - 5}" y="{y(v) + 4:.1f}" text-anchor="end">{v}</text>')
    for i, s in enumerate(T):
        et = '2-4 nov.' if i == 0 else f'día {i}'
        out.append(f'<text x="{x(i):.1f}" y="{H - 22}" text-anchor="middle">{et}</text>')
    out.append(f'<text x="{x(0):.1f}" y="{H - 6}" text-anchor="middle">preelectoral</text>'
               f'<text x="{(x(1) + x(N - 1)) / 2:.1f}" y="{H - 6}" text-anchor="middle">tracking de campaña</text>')
    for k, nom, col in (('PP', 'PP', 'var(--pp)'), ('PSOE', 'PSOE', 'var(--psoe)'), ('VOX', 'Vox', 'var(--vox)')):
        pts = ' '.join(f'{x(i):.1f},{y(s[k]):.1f}' for i, s in enumerate(T))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.5"/>')
        for i, s in enumerate(T):
            out.append(f'<circle cx="{x(i):.1f}" cy="{y(s[k]):.1f}" r="{4 if i == N - 1 else 2.5}" fill="{col}">'
                       f'<title>{nom}, {"preelectoral" if i == 0 else f"día {i}"} (campo del {fecha(s["ini"], False)} al {fecha(s["fin"], False)}): {p(s[k])} %</title></circle>')
        dy = {'PP': -4, 'PSOE': 10, 'VOX': 4}[k]
        out.append(f'<text x="{x(N - 1) + 7:.1f}" y="{y(T[-1][k]) + dy:.1f}" class="lab" style="fill:var(--fg)">{p(T[-1][k])}</text>')
    out.append('</svg>')
    return ''.join(out)


g_evo = figura('Vox, a la baja desde el primer día del tracking',
               'Estimación de voto (%) de 40dB. en su encuesta preelectoral y en cada una de las seis entregas del tracking de campaña, que suma varios días de entrevistas',
               evolucion(), f'Fuente: 40dB. para El País y la SER (<a href="{PDF}">informe del día 6</a>), recogidas por Electográfica.',
               leyenda=[('PP', 'var(--pp)'), ('PSOE', 'var(--psoe)'), ('Vox', 'var(--vox)')],
               tabla=(['Entrega', 'Campo', 'PP', 'PSOE', 'Vox'],
                      [['Preelectoral' if i == 0 else f'Día {i}', f'{fecha(s["ini"], False)} a {fecha(s["fin"], False)}', p(s['PP']), p(s['PSOE']), p(s['VOX'])]
                       for i, s in enumerate(T)]))

_col = lambda k: COLOR.get(k, 'var(--sumar)' if k in ('Frente Amplio', 'Compromís, Ara Més y UPC') else 'var(--otros)')
_dif = lambda k: (lambda d: 'igual que ayer' if d == 0 else f'{"+" if d > 0 else "−"}{abs(d)} desde ayer')(ESC[k] - ESC_AYER[k])
g_esc = figura('Los escaños que da 40dB.',
               'Estimación central de escaños de cada partido en la entrega de hoy y cambio frente a la de ayer. La mayoría absoluta está en 176',
               barras([(k.replace('Compromís, Ara Més y UPC', 'Compromís y otros'), ESC[k], _col(k), f'{ESC[k]} ({_dif(k)})') for k in ESC],
                      200, 'Escaños de cada partido según el tracking de 40dB. del 18 de noviembre', W=400, ml=118),
               f'Fuente: 40dB. para El País y la SER, <a href="{PDF}">informe del día 6</a>, págs. 8 y 9. «Compromís y otros»: Compromís 3, Ara Més 1 y Unidad del Pueblo Canario 0. '
               '«Otros»: ERC 10, EH Bildu 7, Junts 4, PNV 3, Adelante Andalucía 3, BNG 2, UPN-PP 2 y Coalición Canaria 1.',
               leyenda=[('PP', 'var(--pp)'), ('PSOE', 'var(--psoe)'), ('Vox', 'var(--vox)'), ('Frente Amplio y socios', 'var(--sumar)'), ('Podemos', 'var(--pod)'), ('Otros', 'var(--otros)')],
               tabla=(['Partido', 'Hoy', 'Ayer'], [[k, str(ESC[k]), str(ESC_AYER[k])] for k in ESC]))

def lista(xs):
    return ', '.join(xs[:-1]) + ' y ' + xs[-1] if len(xs) > 1 else xs[0]


d_vox = round(AYER['VOX'] - D6['VOX'], 1)
cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="dato">Vox baja al <strong>{p(D6['VOX'])} %</strong> en el tracking de 40dB. para El País y la SER publicado este miércoles, {p(d_vox)} puntos menos que ayer. Lleva cinco bajadas seguidas, una en cada entrega desde la primera, cuando tenía el {p(D1['VOX'])} %, y es su dato más bajo en 40dB. desde {mes(VOX_ANT['pub'])}, cuando marcó el {p(VOX_ANT['VOX'])} %. El PP sube al <strong>{p(D6['PP'])} %</strong> y el PSOE, al <strong>{p(D6['PSOE'])} %</strong>: {p(D6['dif'])} puntos de distancia entre los dos, a once días de las elecciones generales del 29 de noviembre. Es el dato más alto del PP en 40dB. desde {mes(PP_ANT['pub'])} y el del PSOE, desde {mes(PSOE_ANT['pub'])}. El trabajo de campo se hizo del 13 al 17 de noviembre, con 2.000 entrevistas en línea y un error muestral de ±2,2 puntos, según el <a href="{PDF}">informe de 40dB.</a></p>
{CSS_ULTIMO}
{g_40}
<p data-tipo="dato">En escaños, 40dB. da al PP <strong>{ESC['PP']}</strong>, al PSOE <strong>{ESC['PSOE']}</strong> y a Vox <strong>{ESC['Vox']}</strong>. PP y Vox suman {PV}, por encima de la mayoría absoluta de 176, pero es la cifra más baja que les ha dado 40dB. en noviembre: ayer eran {PV_AYER} y en la preelectoral, {PV_SERIE[0][1]}. Vox pierde {ESC_AYER['Vox'] - ESC['Vox']} diputados en un día y el PSOE gana {ESC['PSOE'] - ESC_AYER['PSOE']}. Podemos vuelve a sacar un escaño, con un margen de cero a uno.</p>
{g_evo}
{g_esc}
<h2>Más cerca que la mediana de las encuestas</h2>
<p data-tipo="dato">40dB. sigue siendo de las encuestadoras que ven más cerca al PSOE. La mediana de la última encuesta de cada una de las {NCASAS} encuestadoras de las tres últimas semanas, la que resume <a href="{BASE}encuestas/">nuestra página de encuestas de las elecciones generales</a>, da al PP el {p(MED['PP'])} %, al PSOE el {p(MED['PSOE'])} % y a Vox el {p(MED['VOX'])} %: {p(MED_DIF)} puntos entre PP y PSOE, tres más que 40dB. Solo {lista(['el ' + c if c == 'CIS' else c for c in MAS_CERCA])} lo ven mejor: los dos lo ponen por delante del PP en su última encuesta{"; y ninguna da a Vox menos que 40dB." if not VOX_MENOS else f"; solo {lista(VOX_MENOS)} {'da' if len(VOX_MENOS) == 1 else 'dan'} a Vox menos que 40dB."}</p>
{g_med}
<h2>Lo que se mueve y lo que no</h2>
<p data-tipo="contexto">El tracking suma cinco días de entrevistas y cada mañana cambia el más antiguo por el más reciente: la entrega de hoy comparte cuatro días de campo con la de ayer, así que un cambio de un día a otro no es una medida nueva. Las comparaciones limpias son con encuestas sin días en común. Frente a la primera entrega, del 10 al 12 de noviembre, Vox ha perdido {p(D1['VOX'] - D6['VOX'])} puntos; frente a la preelectoral, del 2 al 4, {p(PRE['VOX'] - D6['VOX'])}. Las dos bajadas quedan dentro del margen de error de la diferencia, de unos ±{p(M_VOX_D1)} y ±{p(M_VOX_PRE)} puntos. Lo que sí se repite es la dirección: Vox no ha subido en ninguna entrega desde la primera.</p>
<p data-tipo="dato">El informe pregunta también quién sería el mejor presidente. Pedro Sánchez lo es para el {p(PRES[0][1])} % y Alberto Núñez Feijóo, para el {p(PRES[1][1])} %; los dos suben algo más de dos puntos desde la preelectoral. Santiago Abascal baja del {p(PRES[2][2])} al <strong>{p(PRES[2][1])} %</strong>, el único de los tres cambios que supera el margen de error. En el gobierno preferido, la coalición del PP con Vox, con el {p(GOB[0][1])} % (el {p(GOB[0][2])} % en la preelectoral), y la del PSOE con el Frente Amplio, con el {p(GOB[1][1])} %, están prácticamente empatadas. El cambio que supera el margen es el del gobierno del PSOE en solitario, que pasa del {p(GOB[2][2])} al {p(GOB[2][1])} %.</p>
<p data-tipo="hipotesis">Las dos preguntas van en la línea del voto: Vox y su candidato, algo más abajo que hace dos semanas. Pero una encuesta es una foto con margen de error, y la de 40dB. es una de las {NCASAS}: la mayoría ven todavía al PP con más ventaja. Para seguir todas, con fuente y fecha, está la <a href="{BASE}encuestas/40db/">página de las encuestas de 40dB.</a> La ley prohíbe publicar encuestas desde el martes 24 de noviembre.</p>
'''

preguntas = [
    ('¿Qué dice hoy la encuesta de 40dB. para El País?',
     f'PP {p(D6["PP"])} %, PSOE {p(D6["PSOE"])} %, Vox {p(D6["VOX"])} %, Frente Amplio 3,5 %, SALF 1,7 % y Podemos {p(D6["POD"])} %. En escaños, PP {ESC["PP"]}, PSOE {ESC["PSOE"]} y Vox {ESC["Vox"]}. '
     'Es la sexta entrega de su tracking, con campo del 13 al 17 de noviembre de 2026 y 2.000 entrevistas en línea.'),
    ('¿Suman mayoría absoluta PP y Vox según 40dB.?',
     f'Sí: {PV} escaños, por encima de 176, aunque es la cifra más baja que les ha dado 40dB. en noviembre. Ayer eran {PV_AYER}.'),
    ('¿Qué es un tracking electoral?',
     'Una encuesta que se publica cada día con las entrevistas de los últimos días: cada entrega añade el día más reciente y quita el más antiguo. '
     'Por eso dos entregas seguidas comparten casi todas las entrevistas y un cambio de un día a otro es pequeño por construcción.'),
]
enlaces = (f'{L("encuestas-40db-psoe-podemos-29n", "La encuesta preelectoral de 40dB.")} · {L("cuanto-discrepan-encuestas-29n", "Cuánto discrepan las encuestas")} · '
           f'{L("encuestas-primera-semana-campana-29n", "Las encuestas, semana a semana")} · <a href="{BASE}encuestas/">Encuestas elecciones generales 2026</a>')
foot = ('Datos: 40dB. para El País y la SER, encuesta preelectoral y tracking de campaña de noviembre de 2026; encuestas nacionales recogidas por Electográfica y Wikipedia; '
        'mediana de mapaelectoral.es/encuestas. Cálculo: actualidad/src/resumenes/tracking_40db.py.')

DATOS = {'T': T, 'MED': MED, 'MED_DIF': MED_DIF, 'ESC': ESC, 'ESC_AYER': ESC_AYER, 'PV_SERIE': PV_SERIE, 'PRES': PRES, 'GOB': GOB,
         'VOX_ANT': VOX_ANT, 'PP_ANT': PP_ANT, 'PSOE_ANT': PSOE_ANT, 'NCASAS': NCASAS, 'MAS_CERCA': MAS_CERCA, 'VOX_MENOS': VOX_MENOS,
         'M_VOX_PRE': round(M_VOX_PRE, 1), 'M_VOX_D1': round(M_VOX_D1, 1)}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

TITULO = 'Elecciones generales: Vox baja al 17 % en la encuesta diaria de El País'
DEK = (f'El tracking de 40dB. para El País y la SER deja al PP en el {p(D6["PP"])} % y al PSOE en el {p(D6["PSOE"])} %. '
       f'PP y Vox suman {PV} escaños, su cifra más baja en el tracking.')
pieza('encuesta-40db-vox-17-29n', 'La encuesta de El País', TITULO, DEK, '18 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('DEK', DEK)
print('VOX_ANT', VOX_ANT['pub'], 'PP_ANT', PP_ANT['pub'], 'PSOE_ANT', PSOE_ANT['pub'], 'MED', MED, 'MAS_CERCA', MAS_CERCA, 'VOX_MENOS', VOX_MENOS,
      'M', round(M_VOX_D1, 2), round(M_VOX_PRE, 2), 'DIF_TR', DIF_TR, 'SIG', SIG)
