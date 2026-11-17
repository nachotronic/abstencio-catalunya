"""Cuánto discrepan las encuestadoras en las elecciones generales del 29N (serie «lo que las encuestas no dicen»).

Encuestas: las mismas que la mediana de /encuestas/, es decir, la última de cada encuestadora con trabajo de campo
terminado en los 21 días anteriores a HOY, sin reestimaciones (encuestas/src/construir.py, carga() y medianas()).
Para cada partido: el mínimo y el máximo entre encuestadoras, y la desviación típica entre ellas frente a la que darían
solo las muestras si todas midieran lo mismo, √(media de p·(1 − p)/n), con n declarado entre 500 y 3.000 entrevistas.
Esa comparación se hace sin el CIS, que tiene un método propio y una muestra mucho mayor.
Uso, desde la raíz: python3 actualidad/src/resumenes/encuestas_discrepan.py
"""
import importlib.util
import statistics
from datetime import date, timedelta
from math import sqrt

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import COL

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
SLUG = 'cuanto-discrepan-encuestas-29n'
HOY = date(2026, 11, 17)
VENTANA = 21

_spec = importlib.util.spec_from_file_location('enc_construir', RAIZ / 'encuestas/src/construir.py')
enc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enc)
assert enc.VENTANA_MEDIANA == VENTANA
TODAS = enc.carga()
ULT = {}
for e in TODAS:   # carga() va de más reciente a más antigua, como en medianas()
    f = date.fromisoformat(e['fin'])
    if HOY - timedelta(days=VENTANA) < f <= HOY and not e['reest'] and enc.clave(e['casa']) not in ULT:
        ULT[enc.clave(e['casa'])] = e
E = list(ULT.values())
nom = lambda e: {'40dB.': '40dB.'}.get(e['casa'], e['casa'].strip())
es_cis = lambda e: enc.clave(e['casa']) == 'cis'
assert sum(map(es_cis, E)) == 1
SIN = [e for e in E if not es_cis(e)]
NE, NS = len(E), len(SIN)
# Control de la corrección de siglas de Sumar (#630): 40dB cuenta Compromís, UPC y Ara Més con Frente Amplio
assert all(e['voto']['SUMAR'] >= 5 for e in E if enc.clave(e['casa']) == '40db'), 'Sumar de 40dB sin coaliciones: falta #630'

PARTIDOS = [('PP', 'PP'), ('PSOE', 'PSOE'), ('VOX', 'Vox'), ('SUMAR', 'Sumar')]
muestra = lambda e: min(max(int(str(e.get('muestra') or 1000).replace('.', '') or 1000), 500), 3000)


def resumen(k, grupo):
    v = [(e['voto'][k], e) for e in grupo if k in e['voto']]
    lo, hi = min(v, key=lambda t: t[0]), max(v, key=lambda t: t[0])
    vals = [x for x, _ in v]
    m = statistics.mean(vals) / 100
    azar = sqrt(statistics.mean(m * (1 - m) / muestra(e) for _, e in v)) * 100
    return dict(min=lo[0], qmin=nom(lo[1]), max=hi[0], qmax=nom(hi[1]), rango=hi[0] - lo[0], sd=statistics.stdev(vals), azar=azar,
                n=len(vals), med=statistics.median(vals))


R = {k: resumen(k, E) for k, _ in PARTIDOS}
RS = {k: resumen(k, SIN) for k, _ in PARTIDOS}
for k in R:
    assert R[k]['n'] == NE and RS[k]['n'] == NS, k
GAP = sorted(((e['voto']['PP'] - e['voto']['PSOE'], nom(e), e) for e in E), key=lambda t: t[0])
G_MIN, G_MAX = GAP[0], GAP[-1]
G_MIN_S = min((g for g in GAP if not es_cis(g[2])), key=lambda t: t[0])
PP_DELANTE = sum(g > 0 for g, *_ in GAP)
RAT = {k: RS[k]['sd'] / RS[k]['azar'] for k in RS}
CIS = next(e for e in E if es_cis(e))

# Cifras que sostienen el texto: si cambian, hay que releerlo
assert R['PSOE']['qmax'] == 'CIS' and R['PP']['qmin'] == 'CIS'
assert RS['PSOE']['rango'] > RS['PP']['rango'] > RS['VOX']['rango']
assert RAT['PSOE'] > 1.3 and RAT['SUMAR'] > 1.3 and RAT['VOX'] < 1 and RAT['PP'] < 1, RAT
assert G_MIN[1] == 'CIS' and G_MIN_S[0] < 0

# ---------- Gráfico 1: cada encuestadora, un punto, en una escala común ----------
X0, X1, W, ML = 4, 36, 400, 64


def puntos():
    alto = 46
    H = alto * len(PARTIDOS) + 26
    x = lambda v: ML + (v - X0) / (X1 - X0) * (W - ML - 12)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Estimación de voto de cada encuestadora por partido">']
    for t in range(5, 36, 5):
        out.append(f'<line x1="{x(t):.1f}" x2="{x(t):.1f}" y1="0" y2="{H - 18}" stroke="var(--grid)"/>'
                   f'<text x="{x(t):.1f}" y="{H - 4}" text-anchor="middle" class="lab">{t}%</text>')
    for i, (k, et) in enumerate(PARTIDOS):
        y = 10 + i * alto
        r = R[k]
        out.append(f'<text x="{ML - 8}" y="{y + 16}" text-anchor="end" class="lab">{esc(et)}</text>')
        out.append(f'<line x1="{x(r["min"]):.1f}" x2="{x(r["max"]):.1f}" y1="{y + 12}" y2="{y + 12}" stroke="var(--muted)" stroke-width="2"/>')
        for e in sorted(E, key=es_cis):
            v = e['voto'][k]
            cis = es_cis(e)
            relleno = 'var(--bg)' if cis else COL[k]
            out.append(f'<circle cx="{x(v):.1f}" cy="{y + 12}" r="{5 if cis else 4}" fill="{relleno}" fill-opacity="{1 if cis else .55}" '
                       f'stroke="{COL[k]}" stroke-width="{2 if cis else 0}"><title>{esc(et)}, {esc(nom(e))}: {p(v)}%</title></circle>')
        out.append(f'<text x="{x(r["min"]):.1f}" y="{y + 34}" text-anchor="middle" class="lab">{p(r["min"])}</text>'
                   f'<text x="{x(r["max"]):.1f}" y="{y + 34}" text-anchor="middle" class="lab">{p(r["max"])}</text>')
    out.append('</svg>')
    return ''.join(out)


tabla1 = (['Encuestadora', 'Medio', 'Fin del campo', 'PP', 'PSOE', 'Vox', 'Sumar'],
          [[nom(e), e.get('medio') or '', e['fin'], *[p(e['voto'][k]) for k, _ in PARTIDOS]]
           for e in sorted(E, key=lambda e: -e['voto']['PP'])])
g_puntos = figura(f'El PSOE va del {p(R["PSOE"]["min"])} al {p(R["PSOE"]["max"])} % según la encuestadora; Vox, del {p(R["VOX"]["min"])} al {p(R["VOX"]["max"])} %',
                  f'Estimación de voto de las {NE} encuestadoras con trabajo de campo en los últimos {VENTANA} días: un punto por encuestadora; el punto hueco es el CIS',
                  puntos(),
                  'Fuente: encuestas publicadas por cada encuestadora, recopiladas por Electográfica y Wikipedia; las mismas que la mediana de nuestra página de encuestas. Cálculo propio.',
                  None, tabla1)

# ---------- Gráfico 2: discrepancia entre encuestadoras frente al azar de las muestras ----------
filas2 = []
for k, et in PARTIDOS:
    filas2.append((f'{et}, azar', RS[k]['azar'], 'var(--muted)', p(RS[k]['azar'])))
    filas2.append((f'{et}, real', RS[k]['sd'], COL[k], p(RS[k]['sd'])))
g_azar = figura(f'En el PSOE y en Sumar las encuestadoras discrepan más de lo que explicaría el tamaño de sus muestras; en el PP y en Vox, no',
                f'Desviación típica entre las {NS} encuestadoras sin el CIS, en puntos: la real y la que darían solo sus muestras si todas midieran lo mismo',
                barras(filas2, max(r['sd'] for r in RS.values()) * 1.25, 'Discrepancia real y por azar entre encuestadoras', W=400, ml=110, fmt=p),
                'Fuente: encuestas recopiladas por Electográfica y Wikipedia. Azar: √(media de p·(1 − p)/n), con n las entrevistas declaradas, entre 500 y 3.000. Cálculo propio.',
                [('Lo que daría el azar', 'var(--muted)')],
                (['Partido', 'Mínimo', 'Máximo', 'Desviación real', 'Por azar', 'Real / azar'],
                 [[et, f'{p(RS[k]["min"])} ({RS[k]["qmin"]})', f'{p(RS[k]["max"])} ({RS[k]["qmax"]})', p(RS[k]['sd']), p(RS[k]['azar']), p(RAT[k])]
                  for k, et in PARTIDOS]))

# ---------- Gráfico 3: ventaja del PP sobre el PSOE en cada encuestadora ----------
sg = lambda v: ('+' if v > 0 else '−' if v < 0 else '') + p(abs(v))
g_gap = figura(f'De {sg(G_MIN[0])} a {sg(G_MAX[0])}: la ventaja del PP sobre el PSOE cambia {p(G_MAX[0] - G_MIN[0])} puntos según quién pregunte',
               'PP menos PSOE en la última encuesta de cada encuestadora, en puntos',
               barras([(nm, abs(g), COL['PP'] if g > 0 else COL['PSOE'], sg(g)) for g, nm, _ in reversed(GAP)],
                      max(abs(G_MIN[0]), G_MAX[0]) * 1.2, 'Ventaja del PP sobre el PSOE por encuestadora', W=400, ml=120, fmt=p),
               'Fuente: encuestas recopiladas por Electográfica y Wikipedia. Cálculo propio.',
               [('Delante, el PP', COL['PP']), ('Delante, el PSOE', COL['PSOE'])])

L_ENC = f'<a href="{BASE}encuestas/">nuestra página de encuestas</a>'

cuerpo = f'''
<p data-tipo="contexto">Las encuestas de las elecciones generales del 29N no dicen lo mismo, y una cifra resumen lo esconde. Hemos tomado las {NE} encuestadoras que han terminado trabajo de campo en los últimos {VENTANA} días, la misma selección que usa la mediana de {L_ENC}, y hemos mirado cuánto se separan entre ellas.</p>
<p data-tipo="dato">Donde más discrepan es en el PSOE: del {p(R["PSOE"]["min"])} % de {R["PSOE"]["qmin"]} al {p(R["PSOE"]["max"])} % del CIS. Sin el CIS, el abanico sigue siendo de {p(RS["PSOE"]["rango"])} puntos, del {p(RS["PSOE"]["min"])} al {p(RS["PSOE"]["max"])} % de {RS["PSOE"]["qmax"]}. En el PP, sin el CIS, van del {p(RS["PP"]["min"])} % de {RS["PP"]["qmin"]} al {p(RS["PP"]["max"])} % de {RS["PP"]["qmax"]}. En Vox casi coinciden: todas lo ponen entre el {p(R["VOX"]["min"])} y el {p(R["VOX"]["max"])} %.</p>
{g_puntos}
<p data-tipo="dato">Eso cambia quién gana. {PP_DELANTE} de las {NE} encuestadoras dan más votos al PP que al PSOE. La ventaja del PP va de {sg(G_MAX[0])} puntos en {G_MAX[1]} a {sg(G_MIN_S[0])} en {G_MIN_S[1]}, que pone delante al PSOE, igual que el CIS ({sg(G_MIN[0])}).</p>
{g_gap}
<p data-tipo="patron">Toda encuesta tiene un margen de error, y dos encuestas bien hechas pueden diferir solo por azar. En el PP y en Vox, sin contar el CIS, las encuestadoras no se separan más de lo que daría ese azar: sus diferencias son {p(RAT["PP"])} y {p(RAT["VOX"])} veces lo que explicaría el tamaño de sus muestras. En el PSOE son {p(RAT["PSOE"])} veces, y en Sumar, {p(RAT["SUMAR"])}. Ahí ya no es solo la muestra.</p>
{g_azar}
<p data-tipo="contexto">Lo que separa a unas de otras no es solo la muestra. Cada encuestadora decide a quién entrevista, por teléfono o por internet, y cómo pasa de las respuestas a una estimación de voto. En Sumar pesa también qué se cuenta: 40dB, por ejemplo, publica aparte a Frente Amplio y a Compromís, Ara Més y Unidad del Pueblo Canario, y aquí se suman, como en las demás.</p>
<p data-tipo="contexto">Una cifra sola no dice cuál acierta. En 2023, {L("encuestas-error-2023-2019-29n", "las últimas encuestas exageraron la ventaja del PP")}. Por eso en {L_ENC} enseñamos la mediana, que no se mueve por una encuesta que se sale del grupo, y la tabla con cada una.</p>
'''

preguntas = [
    ('¿En qué partido discrepan más las encuestas de las elecciones generales?',
     f'En el PSOE: va del {p(R["PSOE"]["min"])} al {p(R["PSOE"]["max"])} % según la encuestadora, y sin el CIS, del {p(RS["PSOE"]["min"])} al {p(RS["PSOE"]["max"])} %. En Vox, todas están entre el {p(R["VOX"]["min"])} y el {p(R["VOX"]["max"])} %.'),
    ('¿Cuántas encuestas dan ganador al PP?',
     f'{PP_DELANTE} de las {NE} encuestadoras con trabajo de campo en los últimos {VENTANA} días dan más votos al PP que al PSOE.'),
]
enlaces = f'{L("encuestas-error-2023-2019-29n", "Lo que las encuestas no dicen")} · <a href="{BASE}encuestas/">Las encuestas de las elecciones generales del 29N</a>'
foot = ('Datos: encuestas publicadas por cada encuestadora, recopiladas por Electográfica y Wikipedia. '
        'Cálculo: actualidad/src/resumenes/encuestas_discrepan.py.')
H1 = (f'Encuestas de las elecciones generales del 29N: según quién pregunte, el PSOE tiene del {p(R["PSOE"]["min"])} al {p(R["PSOE"]["max"])} %; '
      f'en Vox casi coinciden')
DEK = (f'Las {NE} encuestadoras de las últimas tres semanas discrepan en el PSOE y en Sumar más de lo que explicaría el tamaño de sus muestras; en el PP y en Vox, no.')
pieza(SLUG, 'Lo que las encuestas no dicen', H1, DEK, f'{HOY.day} de noviembre de 2026', cuerpo, preguntas, enlaces, foot)
print('NE', NE, 'PSOE', R['PSOE']['min'], R['PSOE']['max'], 'sin CIS', RS['PSOE']['min'], RS['PSOE']['max'], 'PP', RS['PP']['min'], RS['PP']['max'],
      'VOX', R['VOX']['min'], R['VOX']['max'], 'gap', G_MIN[:2], G_MIN_S[:2], G_MAX[:2], 'PPdel', PP_DELANTE, {k: round(v, 2) for k, v in RAT.items()},
      {k: (round(RS[k]['sd'], 2), round(RS[k]['azar'], 2)) for k in RS})
