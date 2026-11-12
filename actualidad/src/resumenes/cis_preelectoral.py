"""«El CIS preelectoral» (12-11-2026): estudio 3584, preelectoral de las generales de 2026 (45.074 entrevistas
del 7 al 30 de octubre), frente a la última encuesta de cada empresa y a los anteriores barómetros del CIS.

Estimación de voto y de escaños del CIS: PDF «3584_estimacion» de cis.es (tabla del total nacional), copiada abajo.
Encuestas de las demás empresas y barómetros anteriores del CIS: previsiones/datos/encuestas/encuestas_limpias.csv
(lo actualiza la Action «Encuestas» desde Electográfica y Wikipedia). Media de las encuestas: la del modelo de
/encuestas/ de las 14.11 del 12 de noviembre (previsiones/datos/publico/historico/2026-11-12-1411.json), que todavía
no incluye este estudio. Hemeroteca del CIS en 2019 y 2023: pieza cis-tezanos-estimacion-29n (estudios 3242, 3263,
3411 y 3415 del CIS frente a los resultados de Interior).
Uso, desde la raíz: python3 actualidad/src/resumenes/cis_preelectoral.py
"""
import csv
import importlib.util
import json

from comun import BASE, RAIZ, esc, figura, n, pieza

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
PDF = 'https://www.cis.es/documents/d/guest/3584_estimacion-pdf'
AVANCE = 'https://www.cis.es/es/w/avance-de-resultados-del-estudio-3584-preelectoral-elecciones-generales-2026-'
MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

# ---------- CIS 3584, total nacional (PDF de estimación) ----------
# (partido, voto directo % censo, estimación % voto válido, escaños mín., escaños máx., color)
CIS = [('PSOE', 28.7, 33.3, 134, 143, 'var(--psoe)'), ('PP', 17.2, 25.5, 98, 106, 'var(--pp)'), ('Vox', 15.0, 18.4, 57, 65, 'var(--vox)'),
       ('Frente Amplio', 3.3, 4.7, 7, 11, 'var(--sumar)'), ('ERC-Podemos', 2.4, 3.1, 10, 14, 'var(--erc)'), ('EH Bildu', 1.3, 1.8, 7, 10, 'var(--bildu)'),
       ('Compromís', 1.2, 1.6, 4, 6, '#e0802a'), ('Adelante Andalucía', 1.1, 1.5, 3, 4, '#1fb07a'), ('Junts', 0.7, 1.2, 2, 4, 'var(--junts)'),
       ('Podemos', 0.8, 1.1, 0, 1, 'var(--pod)'), ('BNG', 0.7, 1.0, 2, 3, 'var(--bng)'), ('PNV', 0.4, 0.7, 2, 4, 'var(--pnv)'),
       ('UPC', 0.3, 0.4, 0, 2, 'var(--sumar)'), ('Ara Més-Front Ampli', 0.2, 0.2, 0, 1, 'var(--sumar)'), ('SALF', 1.3, 1.4, None, None, '#785a46'),
       ('CC', 0.2, 0.2, None, None, 'var(--cc)')]
E = {c[0]: c for c in CIS}
N_CIS = 45074
NS = 15.8   # «No sabe», voto directo (% censo)
assert round(sum(c[2] for c in CIS) + 0.5 + 3.4, 1) == 100.0   # más blanco (0,5) y otros (3,4): suma 100
MIN_SUM = sum(c[3] for c in CIS if c[3] is not None)
MAX_SUM = sum(c[4] for c in CIS if c[4] is not None)
assert MIN_SUM <= 350 <= MAX_SUM, (MIN_SUM, MAX_SUM)
DIF = round(E['PSOE'][2] - E['PP'][2], 1)
assert DIF == 7.8
PPVOX_MIN, PPVOX_MAX = E['PP'][3] + E['Vox'][3], E['PP'][4] + E['Vox'][4]
assert (PPVOX_MIN, PPVOX_MAX) == (155, 171)
DIR_DIF = round(E['PSOE'][1] - E['PP'][1], 1)   # en voto directo
FA_ESPACIO = round(E['Frente Amplio'][2] + E['Compromís'][2] + E['UPC'][2] + E['Ara Més-Front Ampli'][2], 1)

# ---------- Encuestas publicadas ----------
filas = [r for r in csv.DictReader(open(RAIZ / 'previsiones/datos/encuestas/encuestas_limpias.csv', encoding='utf-8')) if r['ambito'] == 'ESPAÑA']
f = lambda r, k: float(r[k]) if r[k] else None
# barómetros del CIS de 2026 en la tabla
SERIE = [(r['publicado'], f(r, 'PP'), f(r, 'PSOE')) for r in sorted(filas, key=lambda r: r['publicado'])
         if r['encuestadora'] == 'CIS' and r['publicado'] >= '2026-01-01']
assert SERIE[-1] == ('2026-10-14', 22.2, 34.0), SERIE[-1]
SERIE.append(('2026-11-12', E['PP'][2], E['PSOE'][2]))
OCT_DIF = round(SERIE[-2][2] - SERIE[-2][1], 1)

# última encuesta de cada empresa (sin el CIS) publicada en el último mes, desde el 13 de octubre
ult = {}
for r in sorted((r for r in filas if r['publicado'] >= '2026-10-13' and r['encuestadora'] != 'CIS'), key=lambda r: (r['publicado'], r['campo_fin'])):
    ult[r['encuestadora']] = r
CASAS = [[k.rstrip('.'), r['cliente'] if r['cliente'] != 'n/a' else '', r['publicado'], f(r, 'PP'), f(r, 'PSOE'), round(f(r, 'PSOE') - f(r, 'PP'), 1)]
         for k, r in ult.items() if f(r, 'PP') and f(r, 'PSOE')]
CASAS.append(['CIS', '', '2026-11-12', E['PP'][2], E['PSOE'][2], DIF])
CASAS.sort(key=lambda c: -c[5])
NCASAS = len(CASAS) - 1
PSOE_DELANTE = [c[0] for c in CASAS if c[0] != 'CIS' and c[5] > 0]
SEGUNDO = CASAS[1] if CASAS[0][0] == 'CIS' else CASAS[0]
assert CASAS[0][0] == 'CIS', CASAS[:2]
assert PSOE_DELANTE == [SEGUNDO[0]] and SEGUNDO[5] * 2 < DIF and all(c[5] < 0 for c in CASAS[2:]), CASAS
URL = {k.rstrip('.'): r['url_agregador'] if 'licdn.com' in r['fuente_original'] else r['fuente_original'] for k, r in ult.items()}

MED = json.load(open(RAIZ / 'previsiones/datos/publico/historico/2026-11-12-1411.json'))['meta']['media_encuestas']
MED_DIF = round(MED['PP'] - MED['PSOE'], 1)

# Hemeroteca (pieza cis-tezanos-estimacion-29n): ventaja del PSOE sobre el PP estimada por el CIS y real
HIST = [('Abril de 2019 (preelectoral)', 13.0, 12.0), ('Noviembre de 2019 (macrobarómetro de octubre)', 14.1, 7.2),
        ('Julio de 2023 (preelectoral)', -0.2, -1.4), ('Julio de 2023 (encuesta flash)', 1.4, -1.4)]
for _, est, real in HIST:
    assert est > real

# ---------- Gráfico de «Lo último» de /encuestas/ (#517), con el preelectoral frente al barómetro de octubre ----------
_spec = importlib.util.spec_from_file_location('enc_construir', RAIZ / 'encuestas/src/construir.py')
enc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enc)
_oct = next(e for e in enc.carga() if e['casa'] == 'CIS' and not e['reest'] and (e.get('publicado') or e['fin']) == '2026-10-14')
_pre = dict(casa='CIS', medio='', publicado='2026-11-12', fin='2026-10-30', reest=False,
            voto={'PP': E['PP'][2], 'PSOE': E['PSOE'][2], 'VOX': E['Vox'][2], 'SALF': E['SALF'][2], 'AA': E['Adelante Andalucía'][2]})
_oct_sin = dict(_oct, voto={k: v for k, v in _oct['voto'].items() if k in ('PP', 'PSOE', 'VOX', 'SALF')})
CSS_ULTIMO = '<style>' + '\n'.join(l for l in enc.ESTILOS.split('\n') if l.startswith(('.ultimo-graf', '.bu-')) or ('.bu-b i' in l and 'prefers-color-scheme' in l or l.startswith(':root[data-theme="dark"] .bu-b'))) + '</style>'
assert CSS_ULTIMO.count('.bu-') >= 8, CSS_ULTIMO
g_ult = (enc.graficos_ultimo([(_pre, _oct_sin, 'CIS · preelectoral · 12 nov')])
         .replace('Las últimas encuestas, partido a partido', 'El preelectoral del CIS frente a su barómetro de octubre'))


def fecha(s):
    a, m, d = s.split('-')
    return f'{int(d)} {MES[int(m) - 1]} {a}'


def casas():
    """Barras divergentes: ventaja del PSOE (a la derecha, rojo) o del PP (a la izquierda, azul)."""
    W, alto, ml = 360, 24, 122
    lo, hi = -10, 10
    H = alto * len(CASAS) + 30
    x = lambda v: ml + (v - lo) / (hi - lo) * (W - ml - 34)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Ventaja del PSOE o del PP en el preelectoral del CIS y en la última encuesta de cada empresa">']
    for v in range(-10, 11, 5):
        out.append(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="0" y2="{H - 22}" stroke="{"var(--muted)" if v == 0 else "var(--grid)"}"/>'
                   f'<text x="{x(v):.1f}" y="{H - 6}" text-anchor="middle">{abs(v)}</text>')
    for i, c in enumerate(CASAS):
        yy = i * alto
        es = c[0] == 'CIS'
        col = 'var(--psoe)' if c[5] > 0 else 'var(--pp)'
        out.append(f'<text x="{ml - 6}" y="{yy + 16}" text-anchor="end" class="{"lab" if es else ""}" style="fill:var(--fg);font-size:12px">{esc(c[0])}</text>')
        x0, x1 = sorted((x(0), x(c[5])))
        out.append(f'<rect x="{x0:.1f}" y="{yy + 5}" width="{max(1.5, x1 - x0):.1f}" height="{alto - 9}" rx="2" fill="{col}" fill-opacity="{1 if es else .6}">'
                   f'<title>{esc(c[0])}, {esc(fecha(c[2]))}: PSOE {p(c[4])} %, PP {p(c[3])} %</title></rect>')
        if c[5] >= 0:
            out.append(f'<text x="{x(c[5]) + 6:.1f}" y="{yy + 17}" class="{"lab" if es else ""}">{p(c[5])}</text>')
        elif x(0) - x(c[5]) > 30:   # dentro de la barra, para no pisar el nombre
            out.append(f'<text x="{x(c[5]) + 4:.1f}" y="{yy + 16}" style="fill:#fff;font-weight:600;font-size:12px">{p(-c[5])}</text>')
        else:   # barra corta: la cifra, a la derecha del cero
            out.append(f'<text x="{x(0) + 4:.1f}" y="{yy + 16}" style="font-size:12px">{p(-c[5])}</text>')
    out.append('</svg>')
    return ''.join(out)


def horquillas():
    """Horquilla de escaños de cada partido según el CIS."""
    fs = [c for c in CIS if c[3] is not None]
    W, alto, ml = 360, 22, 118
    hi = 150
    H = alto * len(fs) + 28
    x = lambda v: ml + v / hi * (W - ml - 58)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Horquilla de escaños de cada partido según el preelectoral del CIS">']
    for v in range(0, hi + 1, 50):
        out.append(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="0" y2="{H - 22}" stroke="var(--grid)"/><text x="{x(v):.1f}" y="{H - 6}" text-anchor="middle">{v}</text>')
    for i, c in enumerate(fs):
        yy = i * alto
        out.append(f'<text x="{ml - 6}" y="{yy + 15}" text-anchor="end" style="fill:var(--fg);font-size:12px">{esc("Ara Més" if c[0].startswith("Ara") else c[0])}</text>')
        out.append(f'<rect x="{x(c[3]):.1f}" y="{yy + 5}" width="{max(3, x(c[4]) - x(c[3])):.1f}" height="{alto - 9}" rx="2" fill="{c[5]}">'
                   f'<title>{esc(c[0])}: de {c[3]} a {c[4]} escaños</title></rect>'
                   f'<text x="{x(c[4]) + 5:.1f}" y="{yy + 15}" style="font-size:12px">{c[3]}–{c[4]}</text>')
    out.append('</svg>')
    return ''.join(out)


def serie():
    """Ventaja del PSOE sobre el PP en cada estimación del CIS de 2026."""
    W, H, ml, mt, mb = 360, 200, 24, 18, 34
    N = len(SERIE)
    bw = (W - ml - 4) / N
    hi = 14
    y = lambda v: mt + (1 - v / hi) * (H - mt - mb)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Ventaja del PSOE sobre el PP en cada estimación del CIS de 2026">']
    for v in range(0, hi + 1, 4):
        out.append(f'<line x1="{ml}" x2="{W}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--grid)"/><text x="{ml - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{v}</text>')
    for i, (pub, pp, ps) in enumerate(SERIE):
        d = round(ps - pp, 1)
        xx = ml + i * bw
        ult = i == N - 1
        out.append(f'<rect x="{xx + 4:.1f}" y="{y(d):.1f}" width="{bw - 8:.1f}" height="{y(0) - y(d):.1f}" rx="2" fill="var(--psoe)" fill-opacity="{1 if ult else .55}">'
                   f'<title>{esc(fecha(pub))}: PSOE {p(ps)} %, PP {p(pp)} %</title></rect>'
                   f'<text x="{xx + bw / 2:.1f}" y="{y(d) - 5:.1f}" text-anchor="middle" class="{"lab" if ult else ""}">{p(d)}</text>'
                   f'<text x="{xx + bw / 2:.1f}" y="{H - 18}" text-anchor="middle">{"nov." if ult else MES[int(pub[5:7]) - 1]}</text>')
    out.append(f'<text x="{W - 2}" y="{H - 2}" text-anchor="end" style="font-size:12px">preelectoral</text></svg>')
    return ''.join(out)


def hist():
    """Ventaja del PSOE estimada por el CIS y real, en las generales desde 2019."""
    W, alto, ml = 360, 46, 122
    lo, hi = -2, 15
    H = alto * len(HIST) + 28
    x = lambda v: ml + (v - lo) / (hi - lo) * (W - ml - 62)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Ventaja del PSOE sobre el PP estimada por el CIS y resultado real">']
    for v in range(0, hi + 1, 5):
        out.append(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="0" y2="{H - 22}" stroke="{"var(--muted)" if v == 0 else "var(--grid)"}"/><text x="{x(v):.1f}" y="{H - 6}" text-anchor="middle">{v}</text>')
    for i, (t, est, real) in enumerate(HIST):
        yy = i * alto
        partes = t.split(' (')
        corto = {'Abril de 2019': 'Abril 2019', 'Noviembre de 2019': 'Noviembre 2019', 'Julio de 2023': 'Julio 2023'}[partes[0]]
        sub = {'preelectoral)': 'preelectoral', 'macrobarómetro de octubre)': 'barómetro oct.', 'encuesta flash)': 'encuesta flash'}[partes[1]]
        out.append(f'<text x="{ml - 6}" y="{yy + 15}" text-anchor="end" style="fill:var(--fg);font-size:12px">{esc(corto)}</text>'
                   f'<text x="{ml - 6}" y="{yy + 30}" text-anchor="end" style="font-size:11px">{esc(sub)}</text>')
        for j, (v, op) in enumerate(((est, 1), (real, .45))):
            x0, x1 = sorted((x(0), x(v)))
            out.append(f'<rect x="{x0:.1f}" y="{yy + 4 + j * 17}" width="{max(1.5, x1 - x0):.1f}" height="14" rx="2" fill="{"var(--psoe)" if v > 0 else "var(--pp)"}" fill-opacity="{op}">'
                       f'<title>{esc(t)}: {"CIS" if j == 0 else "resultado"} {p(v)}</title></rect>'
                       f'<text x="{max(x0, x1) + 4:.1f}" y="{yy + 15 + j * 17}" style="font-size:11px">{("CIS " if j == 0 else "real ")}{p(v)}</text>')
    out.append('</svg>')
    return ''.join(out)


FUENTE_CIS = f'Fuente: CIS, estudio 3584, <a href="{PDF}">estimación de voto</a> (12-11-2026).'
g_casas = figura(f'El CIS es la única encuesta del último mes que da al PSOE más de {p(SEGUNDO[5])} puntos de ventaja',
                 f'Ventaja del PSOE (a la derecha) o del PP (a la izquierda), en puntos, en el preelectoral del CIS y en la última encuesta de cada una de las {NCASAS} empresas que han publicado una desde el 13 de octubre',
                 casas(), FUENTE_CIS + ' Resto: encuestas publicadas, recogidas por Electográfica y Wikipedia. Cálculo propio.',
                 leyenda=[('PSOE por delante', 'var(--psoe)'), ('PP por delante', 'var(--pp)')],
                 tabla=(['Empresa', 'Publicada', 'PSOE', 'PP', 'Ventaja'],
                        [[c[0] + (f' ({c[1]})' if c[1] else ''), fecha(c[2]), p(c[4]), p(c[3]), ('PSOE +' if c[5] > 0 else 'PP +') + p(abs(c[5]))] for c in CASAS]))
g_esc = figura(f'Ni con el máximo de sus horquillas suman PP y Vox 176 escaños: {PPVOX_MAX}',
               'Horquilla de escaños de cada partido según el CIS (mínimo y máximo). El CIS no da escaños a SALF ni a Coalición Canaria',
               horquillas(), FUENTE_CIS,
               leyenda=[(c[0], c[5]) for c in CIS if c[3] is not None and c[0] not in ('UPC', 'Ara Més-Front Ampli')],
               tabla=(['Partido', 'Estimación (%)', 'Voto directo (% censo)', 'Escaños'],
                      [[c[0], p(c[2]), p(c[1]), f'{c[3]}–{c[4]}' if c[3] is not None else '–'] for c in CIS]))
g_serie = figura(f'En octubre, el CIS daba al PSOE {p(OCT_DIF)} puntos de ventaja; ahora, {p(DIF)}',
                 'Ventaja del PSOE sobre el PP, en puntos, en cada estimación del CIS publicada en 2026 que recoge nuestra tabla de encuestas; la última, la del preelectoral',
                 serie(), FUENTE_CIS + ' Barómetros anteriores: CIS, recogidos por Electográfica.',
                 leyenda=[('Ventaja del PSOE sobre el PP', 'var(--psoe)')],
                 tabla=(['Publicada', 'PSOE', 'PP', 'Ventaja del PSOE'], [[fecha(s[0]), p(s[2]), p(s[1]), p(round(s[2] - s[1], 1))] for s in reversed(SERIE)]))
g_hist = figura('En 2019 y 2023, el CIS dio al PSOE más ventaja de la que tuvo',
                'Ventaja del PSOE sobre el PP, en puntos, en el último gran estudio del CIS antes de cada elección y en el resultado (negativo: ventaja del PP)',
                hist(), 'Fuente: CIS, estudios 3242, 3263, 3411 y 3415; resultados del Ministerio del Interior. Recopilado en '
                + L('cis-tezanos-estimacion-29n', 'esta pieza del 16 de octubre') + '.',
                leyenda=[('Estimación del CIS', 'var(--psoe)'), ('Resultado', 'color-mix(in srgb, var(--psoe) 45%, transparent)')],
                tabla=(['Elección', 'CIS', 'Resultado', 'Desvío'], [[t, p(e_), p(r), p(round(e_ - r, 1))] for t, e_, r in HIST]))

cuerpo0 = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="dato">El CIS da al PSOE el <strong>{p(E['PSOE'][2])} %</strong> de los votos y al PP el <strong>{p(E['PP'][2])} %</strong> en su encuesta preelectoral de las generales del 29N, publicada este jueves, la víspera del inicio de la campaña: {p(DIF)} puntos de ventaja socialista. Vox queda en el {p(E['Vox'][2])} % y el Frente Amplio, en el {p(E['Frente Amplio'][2])} %. Es el estudio 3584, con {n(N_CIS)} entrevistas hechas entre el 7 y el 30 de octubre, según el <a href="{AVANCE}">avance de resultados</a> y la <a href="{PDF}">estimación de voto</a> que publica el propio CIS.</p>
{CSS_ULTIMO}
{g_ult}
<p data-tipo="dato">En escaños, el CIS da al PSOE entre {E['PSOE'][3]} y {E['PSOE'][4]}; al PP, entre {E['PP'][3]} y {E['PP'][4]}, y a Vox, entre {E['Vox'][3]} y {E['Vox'][4]}. Ni sumando el máximo de las horquillas de los dos, {E['PP'][4]} y {E['Vox'][4]}, PP y Vox llegan a los 176 de la mayoría absoluta: se quedan en {PPVOX_MAX}.</p>
<p data-tipo="contexto">Cada horquilla deja fuera el 5 % de los escenarios más bajos y el 5 % de los más altos del modelo del CIS, que advierte en su nota metodológica:</p>
<blockquote class="cita"><p>«No es un intervalo de confianza ni un error de muestreo»</p><footer>CIS, nota metodológica del reparto de escaños del <a href="{PDF}">estudio 3584</a> (12-11-2026).</footer></blockquote>
{g_esc}
<h2>Ninguna otra encuesta lo ve así</h2>
<p data-tipo="dato">De las {NCASAS} empresas que han publicado una encuesta desde el 13 de octubre, solo una pone por delante al PSOE: {PSOE_DELANTE[0]}, con {p(SEGUNDO[5])} puntos de ventaja, menos de la mitad que el CIS. Las demás dan ganador al PP. La media de las encuestas que usa <a href="{BASE}encuestas/">nuestro modelo</a>, con los datos de las 14.11 de este jueves y todavía sin este estudio, deja al PP {p(MED_DIF)} puntos por delante: PP {p(MED['PP'])} %, PSOE {p(MED['PSOE'])} %.</p>
{g_casas}
<p data-tipo="dato">Frente a su propio barómetro de octubre, el CIS acerca al PP: entonces daba al PSOE {p(OCT_DIF)} puntos de ventaja, con el PP en el {p(SERIE[-2][1])} %. En el preelectoral, el PP sube {p(E['PP'][2] - SERIE[-2][1])} puntos y el PSOE baja {p(SERIE[-2][2] - E['PSOE'][2])}.</p>
{g_serie}
<p data-tipo="contexto">El CIS no publica cómo pasa de las respuestas a la estimación. En voto directo, lo que contestan los entrevistados sobre todo el censo, el PSOE tiene el {p(E['PSOE'][1])} % y el PP, el {p(E['PP'][1])} %; el {p(NS)} % dice que no sabe a quién votará.</p>
<h2>Lo que pasó en 2019 y 2023</h2>
<p data-tipo="dato">En las tres generales celebradas desde que José Félix Tezanos preside el CIS, el último gran estudio del organismo dio al PSOE más ventaja sobre el PP de la que salió de las urnas, como contamos en {L('cis-tezanos-estimacion-29n', 'esta pieza')}. El desvío fue de {p(HIST[0][1] - HIST[0][2])} puntos en abril de 2019, de {p(HIST[1][1] - HIST[1][2])} en noviembre de 2019 y de {p(HIST[3][1] - HIST[3][2])} en la encuesta flash de julio de 2023.</p>
{g_hist}
<p data-tipo="hipotesis">Tres elecciones son pocas para hablar de un sesgo fijo, y el CIS sostiene que su estimación describe el momento de la encuesta, no el resultado. Si el desvío de este año fuera como el de 2019 o 2023, la ventaja socialista de {p(DIF)} puntos quedaría entre {p(DIF - (HIST[1][1] - HIST[1][2]))} y {p(DIF - (HIST[0][1] - HIST[0][2]))}; no hay forma de saber si lo será.</p>
<h2>El resto del mapa</h2>
<p data-tipo="dato">El CIS mide por separado al Frente Amplio ({p(E['Frente Amplio'][2])} %), a Compromís ({p(E['Compromís'][2])} %), a la Unidad del Pueblo Canario ({p(E['UPC'][2])} %) y a Ara Més-Front Ampli ({p(E['Ara Més-Front Ampli'][2])} %): juntos, el {p(FA_ESPACIO)} %. A ERC y Podemos los cuenta juntos en Cataluña, donde hacen campaña conjunta aunque no van en coalición: {p(E['ERC-Podemos'][2])} % y entre {E['ERC-Podemos'][3]} y {E['ERC-Podemos'][4]} escaños. Aparte, Podemos tiene el {p(E['Podemos'][2])} % y entre {E['Podemos'][3]} y {E['Podemos'][4]} escaños. Por eso, el gráfico del principio no compara a Podemos ni al Frente Amplio con octubre.</p>
<p data-tipo="contexto">La ley prohíbe publicar encuestas desde el martes 24 de noviembre, cinco días antes de la votación. Desde la noche del jueves, este estudio ya está en la tabla y en la media de <a href="{BASE}encuestas/">/encuestas/</a>; la media que se cita más arriba es la de antes de incluirlo.</p>
'''

cuerpo = cuerpo0.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')
preguntas = [
    ('¿Qué dice el CIS preelectoral del 29N?',
     f'PSOE {p(E["PSOE"][2])} %, PP {p(E["PP"][2])} %, Vox {p(E["Vox"][2])} %, Frente Amplio {p(E["Frente Amplio"][2])} %. En escaños, PSOE {E["PSOE"][3]}–{E["PSOE"][4]}, PP {E["PP"][3]}–{E["PP"][4]} y Vox {E["Vox"][3]}–{E["Vox"][4]}. Estudio 3584, {n(N_CIS)} entrevistas del 7 al 30 de octubre de 2026.'),
    ('¿Suman mayoría absoluta PP y Vox según el CIS?', f'No: con el máximo de sus horquillas ({E["PP"][4]} y {E["Vox"][4]}) suman {PPVOX_MAX}, por debajo de 176.'),
    ('¿Coincide el CIS con las demás encuestas?',
     f'No. Es la única del último mes que da al PSOE más de {p(SEGUNDO[5])} puntos de ventaja; la media de las encuestas pone al PP {p(MED_DIF)} puntos por delante.'),
]
enlaces = (f'{L("cis-tezanos-estimacion-29n", "El CIS frente a los resultados")} · {L("encuestas-40db-psoe-podemos-29n", "La encuesta de El País")} · '
           f'<a href="{BASE}encuestas/">Todas las encuestas del 29N</a> · <a href="{BASE}encuestas/cis/">Las encuestas del CIS</a>')
foot = ('Datos: CIS, estudio 3584 (estimación de voto, total nacional); encuestas nacionales publicadas desde el 13 de octubre de 2026, recogidas por '
        'Electográfica y Wikipedia; media de encuestas de mapaelectoral.es/encuestas; estudios del CIS de 2019 y 2023 y resultados de Interior. '
        'Cálculo: actualidad/src/resumenes/cis_preelectoral.py.')
DATOS = {'CIS': {c[0]: {'directo': c[1], 'est': c[2], 'min': c[3], 'max': c[4]} for c in CIS}, 'DIF': DIF, 'PPVOX': [PPVOX_MIN, PPVOX_MAX], 'OCT_DIF': OCT_DIF,
         'SERIE': SERIE, 'CASAS': CASAS, 'NCASAS': NCASAS, 'PSOE_DELANTE': PSOE_DELANTE, 'SEGUNDO': SEGUNDO, 'MED': MED, 'MED_DIF': MED_DIF,
         'HIST': HIST, 'FA_ESPACIO': FA_ESPACIO, 'N': N_CIS, 'NS': NS}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
if __name__ == '__main__':
    pieza('cis-preelectoral-29n', 'El CIS preelectoral',
          f'El CIS preelectoral da al PSOE {p(DIF)} puntos de ventaja; la media de las demás encuestas, {p(MED_DIF)} al PP',
          f'Ni con el máximo de sus horquillas suman PP y Vox mayoría absoluta: {PPVOX_MAX} escaños. Ninguna otra encuesta del último mes da al PSOE tanta ventaja. '
          f'En las tres generales desde 2019, el CIS sobrestimó la del PSOE.',
          '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
    print('DIF', DIF, 'OCT', OCT_DIF, 'MED_DIF', MED_DIF, 'PSOE_DELANTE', PSOE_DELANTE, 'SEGUNDO', SEGUNDO, 'NCASAS', NCASAS, 'FA', FA_ESPACIO, 'SERIE', SERIE)
