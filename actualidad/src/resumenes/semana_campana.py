"""«Las encuestas, semana a semana» (16-11-2026): la primera semana de campaña, del viernes 13 al lunes 16 de noviembre.

Cada encuesta publicada desde el arranque de la campaña frente a la anterior de la misma empresa, publicada antes del 13;
los cuatro trackings diarios; el recuento de encuestas que dan ganador al PP y mayoría absoluta a PP y Vox, y la media
de encuestas del modelo de /encuestas/ al empezar la campaña (00.38 del 13 de noviembre) y hoy (08.13 del 16).

Datos: encuestas/src/construir.py, carga() (Electográfica y Wikipedia, las mismas filas que la tabla de /encuestas/).
Modelo: previsiones/datos/publico/historico/2026-11-13-0038.json y 2026-11-16-0813.json.
Uso, desde la raíz: python3 actualidad/src/resumenes/semana_campana.py
"""
import importlib.util
import json
from datetime import date, timedelta
from math import sqrt

from comun import BASE, RAIZ, esc, figura, n, pieza

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
LOPEZ = 'https://www.infobae.com/espana/agencias/2026/11/14/patxi-lopez-psoe-todas-las-encuestan-marcan-el-alza-del-psoe-y-descenso-del-pp/'
FEIJOO = 'https://www.infobae.com/america/agencias/2026/11/16/feijoo-asegura-que-el-partido-de-las-elecciones-lo-va-ganando-el-pp-aunque-todo-se-resuelve-en-el-minuto-90/'
INICIO, HOY = '2026-11-13', '2026-11-16'
WURL = 'https://www.electografica.com/2026/11/encuesta-winston-261113.html'   # ficha técnica: campo del 5 al 8 de noviembre
NUM = ['cero', 'una', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve', 'diez']

_spec = importlib.util.spec_from_file_location('enc_construir', RAIZ / 'encuestas/src/construir.py')
enc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enc)
pub = lambda e: e.get('publicado') or e['fin']
TODAS = enc.carga()
V = sorted((e for e in TODAS if not e['reest'] and e['fin'] >= '2023-07-24'), key=pub, reverse=True)
K = lambda e: enc.clave(e['casa'])
nombre = lambda e: e['casa'].rstrip('.')

# ---------- Cada empresa: su última encuesta de campaña frente a la última anterior al 13 ----------
camp = {}
for e in V:
    if INICIO <= pub(e) <= HOY:
        camp.setdefault(K(e), e)
assert sorted(camp) == ['40db', 'data10', 'emanalytics', 'ncreport', 'sigmados', 'sociometrica', 'sondaxe', 'swdemoscopia', 'winston', 'yougov'], sorted(camp)
CASAS = []
for k, e in camp.items():
    ant = next((x for x in V if K(x) == k and pub(x) < INICIO), None)
    if ant is None:
        continue
    c = dict(casa=nombre(e), medio=e['medio'], pub=pub(e), fin=e['fin'], url=e['url'], n=int(e['muestra']),
             ant_pub=pub(ant), ant_fin=ant['fin'], ant_n=int(ant['muestra']), ant_url=ant['url'], e=e, ant=ant)
    for par in ('PP', 'PSOE', 'VOX'):
        c[par], c['a' + par] = e['voto'][par], ant['voto'][par]
        c['d' + par] = round(e['voto'][par] - ant['voto'][par], 1)
        # margen (2 sigmas) del cambio de un partido entre dos encuestas independientes, con muestreo aleatorio simple
        q1, q2 = ant['voto'][par] / 100, e['voto'][par] / 100
        c['m' + par] = 200 * sqrt(q1 * (1 - q1) / c['ant_n'] + q2 * (1 - q2) / c['n'])
    c['gap'], c['agap'] = round(c['PP'] - c['PSOE'], 1), round(c['aPP'] - c['aPSOE'], 1)
    CASAS.append(c)
CASAS.sort(key=lambda c: c['dPSOE'] - c['dPP'], reverse=True)   # de la que más acerca al PSOE a la que más lo aleja
SIN_ANT = [nombre(e) for k, e in camp.items() if not any(K(x) == k and pub(x) < INICIO for x in V)]
assert SIN_ANT == ['YouGov'] and camp['yougov']['fin'] == '2026-11-02', SIN_ANT
YG = camp['yougov']
NC = len(CASAS)
PSOE_SUBE = [c['casa'] for c in CASAS if c['dPSOE'] > 0]
PSOE_BAJA = [c['casa'] for c in CASAS if c['dPSOE'] < 0]
PP_BAJA = [c['casa'] for c in CASAS if c['dPP'] < 0]
PP_SUBE = [c['casa'] for c in CASAS if c['dPP'] > 0]
PP_IGUAL = [c['casa'] for c in CASAS if c['dPP'] == 0]
DOS = [c['casa'] for c in CASAS if c['dPSOE'] > 0 and c['dPP'] < 0]   # las que cumplen las dos tendencias de López
ACERCA = [c['casa'] for c in CASAS if c['gap'] < c['agap']]
ALEJA = [c['casa'] for c in CASAS if c['gap'] > c['agap']]
IGUAL = [c['casa'] for c in CASAS if c['gap'] == c['agap']]
assert (NC, len(PSOE_SUBE), PSOE_BAJA, len(PP_BAJA), PP_IGUAL, len(PP_SUBE)) == (9, 7, ['Sondaxe', 'Winston'], 4, ['SW Demoscopia'], 4), \
    (NC, PSOE_SUBE, PSOE_BAJA, PP_BAJA, PP_IGUAL, PP_SUBE)
assert sorted(DOS) == sorted(PP_BAJA) == ['40dB', 'Data10', 'NC Report', 'SocioMétrica'] and sorted(ALEJA) == ['Sondaxe', 'Winston'] and IGUAL == ['EM-Analytics'], (DOS, ALEJA, IGUAL)
C = {c['casa']: c for c in CASAS}
W, SX, D40, NCR, D10 = C['Winston'], C['Sondaxe'], C['40dB'], C['NC Report'], C['Data10']
assert min(NCR['gap'], C['Data10']['gap']) > 6 and NCR['gap'] < NCR['agap'] and C['Data10']['gap'] < C['Data10']['agap']
assert NCR['fin'] == '2026-11-12' and NCR['e']['inicio'] == '2026-11-06', NCR['fin']   # La Razón: «elaborado entre el 6 y el 12 de noviembre»
assert W['fin'] == '2026-11-08' and W['pub'] == '2026-11-13', W['fin']
# ningún cambio del PP ni del PSOE supera su margen entre dos encuestas independientes
# márgenes solo cuando las dos encuestas comparadas no comparten días de trabajo de campo
INDEP = [c['casa'] for c in CASAS if c['ant_fin'] < c['e']['inicio']]
assert sorted(INDEP) == ['40dB', 'Data10', 'NC Report', 'Sondaxe', 'Winston'], INDEP
assert all(abs(C[k]['d' + par]) < C[k]['m' + par] for k in INDEP for par in ('PP', 'PSOE')), [(k, C[k]['dPP'], C[k]['mPP']) for k in INDEP]
MAX_D = max(abs(c['d' + par]) for c in CASAS for par in ('PP', 'PSOE'))
assert MAX_D == W['dPP'] == 1.7, MAX_D

# ---------- Los cuatro trackings diarios ----------
TRACK = []
for k in ('40db', 'sigmados', 'swdemoscopia', 'emanalytics'):
    s = sorted((e for e in V if K(e) == k and ('2026-11-09' if k != '40db' else INICIO) <= pub(e) <= HOY), key=pub)   # 40dB: su tracking empieza el 13; la del 9 fue su preelectoral
    TRACK.append(dict(casa=nombre(s[-1]), medio=s[-1]['medio'], serie=[dict(pub=pub(e), PP=e['voto']['PP'], PSOE=e['voto']['PSOE'], VOX=e['voto']['VOX'], n=e['muestra'], url=e['url']) for e in s]))
for t in TRACK:
    c = [s for s in t['serie'] if s['pub'] >= INICIO]
    t['g0'], t['g1'] = round(c[0]['PP'] - c[0]['PSOE'], 1), round(c[-1]['PP'] - c[-1]['PSOE'], 1)
    t['d0'], t['d1'] = c[0]['pub'], c[-1]['pub']
T = {t['casa']: t for t in TRACK}
ABANICO = round(T['Sigma Dos']['g1'] - T['SW Demoscopia']['g1'], 1)
assert ABANICO == 8.7 and max(t['g1'] for t in TRACK) == T['Sigma Dos']['g1'], ABANICO
assert (T['40dB']['g0'], T['40dB']['g1'], T['Sigma Dos']['g0'], T['Sigma Dos']['g1'], T['SW Demoscopia']['g0'], T['SW Demoscopia']['g1'],
        T['EM-Analytics']['g0'], T['EM-Analytics']['g1']) == (2.1, 1.2, 5.6, 5.4, -3.1, -3.3, 4.3, 4.0), [(t['casa'], t['g0'], t['g1']) for t in TRACK]

# ---------- Recuento: quién gana y si PP y Vox llegan a 176 (como en /encuestas/: última de cada casa, campo en 30 días) ----------
def recuento(hasta):
    return _rec([e for e in TODAS if pub(e) <= hasta], date.fromisoformat(hasta))


def _rec(encs, hoy):
    mes = sorted((e for e in encs if date.fromisoformat(e['fin']) > hoy - timedelta(days=30) and not e['reest']), key=lambda e: e['fin'], reverse=True)
    ultimas, vistos = [], set()
    for e in mes:
        if K(e) not in vistos:
            vistos.add(K(e)); ultimas.append(e)
    con_esc = [e for e in ultimas if 'PP' in e['esc'] and 'VOX' in e['esc']]
    mayoria = sum(1 for e in con_esc if enc.rango_esc(e['esc']['PP'])[0] + enc.rango_esc(e['esc']['VOX'])[0] >= 176)
    return ultimas, con_esc, mayoria


lider = lambda e: max(e['voto'], key=e['voto'].get)
U1, E1, M1 = recuento(HOY)
U0, E0, M0 = recuento('2026-11-12')
G1, G0 = sum(lider(e) == 'PP' for e in U1), sum(lider(e) == 'PP' for e in U0)
assert (G1, len(U1), M1, len(E1)) == (17, 19, 16, 18), (G1, len(U1), M1, len(E1))
PSOE_GANA = sorted(nombre(e) for e in U1 if lider(e) == 'PSOE')
assert PSOE_GANA == ['CIS', 'SW Demoscopia'], PSOE_GANA   # «Solo el CIS y SW Demoscopia»
NO_MAY = sorted(nombre(e) for e in E1 if enc.rango_esc(e['esc']['PP'])[0] + enc.rango_esc(e['esc']['VOX'])[0] < 176)
assert NO_MAY == ['CIS', 'SW Demoscopia'], NO_MAY
# 40dB, la distancia más corta entre las encuestas de campaña que dan ganador al PP
MIN_PP = min((e for e in camp.values() if lider(e) == 'PP'), key=lambda e: e['voto']['PP'] - e['voto']['PSOE'])
assert K(MIN_PP) == '40db' and pub(MIN_PP) == HOY, nombre(MIN_PP)

# ---------- La media del modelo, al empezar la campaña y hoy ----------
H0 = json.load(open(RAIZ / 'previsiones/datos/publico/historico/2026-11-13-0038.json'))
H1 = json.load(open(RAIZ / 'previsiones/datos/publico/historico/2026-11-16-0813.json'))
MED0, MED1 = H0['meta']['media_encuestas'], H1['meta']['media_encuestas']
GAP0, GAP1 = MED0['PP'] - MED0['PSOE'], MED1['PP'] - MED1['PSOE']
assert round(GAP0, 1) == 3.2 and 3.1 <= GAP1 <= 3.2, (GAP0, GAP1)   # hoy, 3,15: con los porcentajes redondeados (30,9 y 27,7) saldría 3,2; el texto no da la cifra


def bloque(h):
    b = next(b for b in h['escenario']['bloques'] if b['bloque'] == 'PP + Vox')
    d = b['escanos_dist']
    prob = sum(v for i, v in enumerate(d['p']) if d['desde'] + i >= 176)
    hemi = h['escenario']['hemiciclo']['congreso']
    return hemi['PP'] + hemi['Vox'], prob, hemi


PV0, PR0, HE0 = bloque(H0)
PV1, PR1, HE1 = bloque(H1)
assert (PV0, PV1) == (193, 194), (PV0, PV1)
pct = lambda v: f'{round(v * 100)}'

# ---------- Gráficos ----------
def cambios():
    """Dos barras por empresa desde el cero: cambio del PP (azul) y del PSOE (rojo), en puntos."""
    Wd, alto, ml = 400, 44, 112
    lo, hi = -2, 2
    H = alto * NC + 26
    x = lambda v: ml + (v - lo) / (hi - lo) * (Wd - ml - 34)
    out = [f'<svg viewBox="0 0 {Wd} {H}" role="img" aria-label="Cambio del PP y del PSOE en cada encuesta de campaña frente a la anterior de la misma empresa">']
    for v in range(lo, hi + 1):
        out.append(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="0" y2="{H - 20}" stroke="{"var(--muted)" if v == 0 else "var(--grid)"}"/>'
                   f'<text x="{x(v):.1f}" y="{H - 5}" text-anchor="middle">{("+" if v > 0 else "−" if v < 0 else "") + str(abs(v))}</text>')
    for i, c in enumerate(CASAS):
        y = i * alto
        out.append(f'<text x="{ml - 8}" y="{y + 25}" text-anchor="end" class="lab" style="fill:var(--fg)">{esc(c["casa"])}</text>')
        for j, (par, col) in enumerate((('PP', 'var(--pp)'), ('PSOE', 'var(--psoe)'))):
            v = c['d' + par]
            yy = y + 6 + j * 16
            x0, x1 = sorted((x(0), x(v)))
            out.append(f'<rect x="{x0:.1f}" y="{yy}" width="{max(1.5, x1 - x0):.1f}" height="13" rx="2" fill="{col}">'
                       f'<title>{esc(c["casa"])}, {par}: {p(c["a" + par])} → {p(c[par])} %</title></rect>')
            t = ('+' if v > 0 else '−' if v < 0 else '') + p(abs(v))
            if v >= 0:
                out.append(f'<text x="{x(v) + 4:.1f}" y="{yy + 11}">{t}</text>')
            else:
                out.append(f'<text x="{x(v) - 4:.1f}" y="{yy + 11}" text-anchor="end">{t}</text>')
    out.append('</svg>')
    return ''.join(out)


MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
fecha = lambda s: f'{int(s[8:])} {MES[int(s[5:7]) - 1]}'


def tracking(t):
    """Líneas del PP y del PSOE en un tracking, del 9 al 16 de noviembre; la banda gris, desde el arranque de la campaña."""
    Wd, H, ml, mr, mt, mb = 400, 150, 34, 40, 12, 24
    dias = [date(2026, 11, 9) + timedelta(days=i) for i in range(8)]
    xd = lambda iso: ml + (date.fromisoformat(iso) - dias[0]).days / 7 * (Wd - ml - mr)
    vals = [s[k] for s in t['serie'] for k in ('PP', 'PSOE')]
    lo, hi = int(min(vals)) - 1, int(max(vals)) + 2
    y = lambda v: mt + (1 - (v - lo) / (hi - lo)) * (H - mt - mb)
    out = [f'<svg viewBox="0 0 {Wd} {H}" role="img" aria-label="PP y PSOE en el tracking de {esc(t["casa"])}, del 9 al 16 de noviembre">',
           f'<rect x="{xd(INICIO):.1f}" y="{mt}" width="{Wd - mr - xd(INICIO):.1f}" height="{H - mt - mb}" fill="var(--grid)" fill-opacity=".45"/>']
    for v in range(lo, hi + 1):
        if (v - lo) % 2 == 0:
            out.append(f'<line x1="{ml}" x2="{Wd - mr}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--grid)"/><text x="{ml - 5}" y="{y(v) + 4:.1f}" text-anchor="end">{v}</text>')
    for d in dias:
        out.append(f'<text x="{xd(d.isoformat()):.1f}" y="{H - 6}" text-anchor="middle">{d.day}</text>')
    for par, col in (('PP', 'var(--pp)'), ('PSOE', 'var(--psoe)')):
        pts = ' '.join(f'{xd(s["pub"]):.1f},{y(s[par]):.1f}' for s in t['serie'])
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.5"/>')
        for s in t['serie']:
            out.append(f'<circle cx="{xd(s["pub"]):.1f}" cy="{y(s[par]):.1f}" r="3" fill="{col}"><title>{fecha(s["pub"])}, {par}: {p(s[par])} %</title></circle>')
        u = t['serie'][-1]
        out.append(f'<text x="{xd(u["pub"]) + 6:.1f}" y="{y(u[par]) + 4:.1f}" class="lab" style="fill:{col}">{p(u[par])}</text>')
    out.append('</svg>')
    return ''.join(out)


_pv = lambda e: f'{esc(nombre(e))}' + (f' · {esc(e["medio"])}' if e['medio'] else '') + f' · {enc.dia(pub(e))}'
CSS_ULTIMO = '<style>' + '\n'.join(l for l in enc.ESTILOS.split('\n') if l.startswith(('.ultimo-graf', '.bu-')) or ('.bu-b i' in l and 'prefers-color-scheme' in l or l.startswith(':root[data-theme="dark"] .bu-b'))) + '</style>'
assert CSS_ULTIMO.count('.bu-') >= 8, CSS_ULTIMO
g_ultimo = (enc.graficos_ultimo([(c['e'], c['ant'], _pv(c['e'])) for c in CASAS])
            .replace('Las últimas encuestas, partido a partido', f'Las {NUM[NC]} encuestas de campaña, partido a partido')
            .replace('lo que daba la encuesta anterior de la misma encuestadora', 'lo que daba la última encuesta de la misma empresa publicada antes del 13 de noviembre'))
assert f'Las {NUM[NC]} encuestas de campaña' in g_ultimo and 'antes del 13 de noviembre' in g_ultimo

mn = lambda v: ('−' if v < 0 else '') + p(abs(v))
sg = lambda v: ('+' if v > 0 else '−' if v < 0 else '') + p(abs(v))
g_cambios = figura(f'El PSOE sube en {NUM[len(PSOE_SUBE)]} encuestas; el PP baja en {NUM[len(PP_BAJA)]}',
                   'Cambio de la estimación de voto, en puntos, en la última encuesta de cada empresa publicada entre el 13 y el 16 de noviembre frente a la anterior de la misma empresa',
                   cambios(), 'Fuente: encuestas publicadas, recogidas por Electográfica y Wikipedia (tabla de <a href="' + BASE + 'encuestas/">/encuestas/</a>). Cálculo propio.',
                   leyenda=[('PP', 'var(--pp)'), ('PSOE', 'var(--psoe)')],
                   tabla=(['Empresa (anterior)', 'PP', 'PSOE', 'Ventaja PP'],
                          [[f'{c["casa"]}, {fecha(c["pub"])} ({fecha(c["ant_pub"])})', f'{p(c["PP"])} ({sg(c["dPP"])})',
                            f'{p(c["PSOE"])} ({sg(c["dPSOE"])})', f'{mn(c["gap"])} ({mn(c["agap"])})'] for c in CASAS]))

paneles = ''.join(f'<p class="lab" style="font-family:var(--ui);font-weight:600;margin:.8rem 0 0">{esc(t["casa"])} · {esc(t["medio"])}</p>{tracking(t)}' for t in TRACK)
g_track = figura('Los cuatro trackings, día a día',
                 'Estimación de voto del PP y del PSOE (%) en cada entrega publicada del 9 al 16 de noviembre, por fecha de publicación; la de 40dB, desde el 13, cuando empezó su tracking. En gris, desde el arranque de la campaña',
                 paneles, 'Fuente: 40dB para El País y la SER; Sigma Dos para El Mundo; SW Demoscopia para La Séptima; EM-Analytics para Electomanía. Recogidas por Electográfica y Wikipedia.',
                 leyenda=[('PP', 'var(--pp)'), ('PSOE', 'var(--psoe)')],
                 tabla=(['Tracking', 'Publicada', 'PP', 'PSOE', 'Vox'],
                        [[t['casa'], fecha(s['pub']), p(s['PP']), p(s['PSOE']), p(s['VOX'])] for t in TRACK for s in t['serie']]))

PARTIDOS = [('PP', 'PP', 'var(--pp)'), ('PSOE', 'PSOE', 'var(--psoe)'), ('VOX', 'Vox', 'var(--vox)'), ('SUMAR', 'Sumar / Frente Amplio', 'var(--sumar)')]


def media():
    Wd, alto, ml = 400, 40, 104
    H = alto * len(PARTIDOS) + 8
    x = lambda v: ml + v / 35 * (Wd - ml - 70)
    out = [f'<svg viewBox="0 0 {Wd} {H}" role="img" aria-label="Media de encuestas del modelo el 13 y el 16 de noviembre">']
    for i, (k, nom, col) in enumerate(PARTIDOS):
        y = 4 + i * alto
        out.append(f'<text x="{ml - 8}" y="{y + 22}" text-anchor="end" class="lab" style="fill:var(--fg)">{esc(nom if k != "SUMAR" else "Sumar / FA")}</text>')
        for j, (v, op, et) in enumerate(((MED0[k], .38, '13 nov'), (MED1[k], 1, '16 nov'))):
            yy = y + 4 + j * 16
            out.append(f'<rect x="{ml}" y="{yy}" width="{x(v) - ml:.1f}" height="13" rx="2" fill="{col}" fill-opacity="{op}"><title>{esc(nom)}, {et}: {p(v)} %</title></rect>'
                       f'<text x="{x(v) + 5:.1f}" y="{yy + 11}">{p(v)}{" (" + et + ")" if i == 0 else ""}</text>')
    out.append('</svg>')
    return ''.join(out)


g_media = figura('La media de las encuestas apenas se mueve',
                 'Media de encuestas del modelo de Mapa Electoral (%), al empezar la campaña (00.38 del 13 de noviembre, barra de arriba) y este lunes (08.13 del 16, barra de abajo)',
                 media(), f'Fuente: <a href="{BASE}encuestas/">modelo de Mapa Electoral</a>, publicaciones del 13 y el 16 de noviembre de 2026. En la tabla, el cambio se calcula con las cifras sin redondear.',
                 leyenda=[(nom, col) for _, nom, col in PARTIDOS],
                 tabla=(['Partido', '13 nov', '16 nov', 'Cambio'], [[nom, p(MED0[k]), p(MED1[k]), sg(round(MED1[k] - MED0[k], 1))] for k, nom, _ in PARTIDOS]))

# ---------- Texto ----------
lista = lambda xs: ', '.join(xs[:-1]) + ' y ' + xs[-1] if len(xs) > 1 else xs[0]
enl = lambda c: f'<a href="{c["url"]}">{esc(c["casa"])}</a>'
rng = lambda xs: f'{p(min(xs))} y {p(max(xs))}'
sube_psoe = [c for c in CASAS if c['dPSOE'] > 0]

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">El sábado, en Zamora, el portavoz socialista en el Congreso, Patxi López, se mostró convencido de que el PSOE ganará el 29N con una lectura de las encuestas que no admitía excepciones, según la agencia EFE:</p>
<blockquote class="cita"><p>«Todas las encuestas marcan dos tendencias, el alza del Partido Socialista y el descenso del Partido Popular»</p><footer>Patxi López, portavoz del PSOE en el Congreso, según <a href="{LOPEZ}">EFE</a> (14 de noviembre de 2026).</footer></blockquote>
<p data-tipo="dato">Al cuarto día de campaña, la frase se cumple a medias. {NUM[len(camp)].capitalize()} empresas han publicado encuestas de las generales entre el viernes 13 y este lunes 16, y {NUM[NC]} de ellas tenían una anterior con la que compararse. En <strong>{NUM[len(PSOE_SUBE)]}</strong>, el PSOE sube; en {NUM[len(PSOE_BAJA)]}, {lista(PSOE_BAJA)}, baja. El PP retrocede en <strong>{NUM[len(PP_BAJA)]}</strong>, {lista(sorted(PP_BAJA))}; se queda igual en {PP_IGUAL[0]} y mejora en las otras {NUM[len(PP_SUBE)]}. Las dos tendencias a la vez, que el PSOE suba y el PP baje, solo aparecen en esas {NUM[len(DOS)]}.</p>
{g_cambios}
<p data-tipo="dato">El salto más grande va en dirección contraria a la que describía López: <a href="{W['url']}">Winston para Artículo14</a> da al PP {p(W['dPP'])} puntos más que en su encuesta de finales de octubre y amplía su ventaja hasta {p(W['gap'])} puntos. <a href="{SX['url']}">Sondaxe para La Voz de Galicia</a> también la ensancha, de {p(SX['agap'])} a {p(SX['gap'])}. Del otro lado, <a href="{D10['url']}">Data10 para OKDiario</a> y <a href="{NCR['url']}">NC Report para La Razón</a> recortan la distancia, pero la dejan por encima de los seis puntos. Varias de estas encuestas se publican ya en campaña con entrevistas anteriores: Winston <a href="{WURL}">terminó su trabajo de campo el 8 de noviembre</a> y NC Report <a href="{NCR['url']}">lo hizo entre el 6 y el 12</a>, antes del arranque. La distancia más corta entre las encuestas de esta semana que dan ganador al PP es la del <a href="{D40['url']}">tracking de 40dB para El País y la SER</a>: {p(D40['gap'])} puntos, con el PSOE en el {p(D40['PSOE'])} %.</p>
{CSS_ULTIMO}
{g_ultimo}
<h2>Décimas dentro del margen</h2>
<p data-tipo="dato">Ningún cambio llega a dos puntos: el mayor, el del PP en Winston, se queda en {p(MAX_D)}. Y ninguno supera el margen de error en las {NUM[len(INDEP)]} comparaciones en que las dos encuestas no comparten ni un día de trabajo de campo. Entre dos muestras distintas, el cambio de un partido necesita superar el error de las dos juntas para ser algo más que ruido: con las 1.200 y 1.501 entrevistas de Winston, ese margen es de ±{p(W['mPP'])} puntos para el PP; con las 1.000 y 1.000 de NC Report, de ±{p(NCR['mPSOE'])} para el PSOE, que sube {p(NCR['dPSOE'])}, y con las 1.500 y 1.500 de Data10, de ±{p(D10['mPSOE'])} para un PSOE que gana {p(D10['dPSOE'])}.</p>
<p data-tipo="dato">La campaña ha traído, sobre todo, encuestas diarias. Cuatro empresas publican un tracking casi cada mañana: 40dB, Sigma Dos, SW Demoscopia y EM-Analytics; Sondaxe se ha sumado este fin de semana. Desde su primera entrega de campaña, la ventaja del PP se estrecha en 40dB, de {p(T['40dB']['g0'])} a {p(T['40dB']['g1'])} puntos, y apenas varía en Sigma Dos, de {p(T['Sigma Dos']['g0'])} a {p(T['Sigma Dos']['g1'])}, y en EM-Analytics, de {p(T['EM-Analytics']['g0'])} a {p(T['EM-Analytics']['g1'])}. SW Demoscopia es la única que pone por delante al PSOE: su ventaja pasa de {p(-T['SW Demoscopia']['g0'])} a {p(-T['SW Demoscopia']['g1'])} puntos.</p>
{g_track}
<p data-tipo="hipotesis">Las cuatro líneas dibujan cuatro campañas distintas: la distancia entre el PP y el PSOE va de los {p(T['Sigma Dos']['g1'])} puntos de Sigma Dos a los {p(-T['SW Demoscopia']['g1'])} a favor del PSOE de SW Demoscopia. Esa diferencia entre empresas, de {p(ABANICO)} puntos, pesa mucho más que cualquier movimiento de una sola de ellas en estos cuatro días.</p>
<h2>Lo que no cambia: el PP primero y la mayoría con Vox</h2>
<p data-tipo="dato">Con la última encuesta de cada empresa de los últimos 30 días, como cuenta la página de <a href="{BASE}encuestas/">encuestas</a>, el PP es el más votado en <strong>{G1} de {len(U1)}</strong>; el jueves, antes de la campaña, lo era en {G0} de {len(U0)}. Solo el {lista(PSOE_GANA)} ponen por delante al PSOE. Y de las {len(E1)} que publican escaños, <strong>{M1}</strong> dan a PP y Vox juntos 176 o más, la mayoría absoluta; el jueves eran {M0} de {len(E0)}. Las dos que no, otra vez, el CIS y SW Demoscopia.</p>
<p data-tipo="dato">La media que usa <a href="{BASE}encuestas/">nuestro modelo</a> se ha movido todavía menos. Al empezar la campaña, en la publicación de las 00.38 del viernes 13, daba al PP el {p(MED0['PP'])} % y al PSOE el {p(MED0['PSOE'])} %; este lunes, a las 08.13, el {p(MED1['PP'])} % y el {p(MED1['PSOE'])} %. La distancia sigue algo por encima de los tres puntos. En escaños, el escenario central da a PP y Vox {PV1}, uno más que el viernes ({HE1['PP']} y {HE1['Vox']}, frente a {HE0['PP']} y {HE0['Vox']}). En el {pct(PR1)} % de las simulaciones llegan a 176; el viernes, en el {pct(PR0)} %.</p>
{g_media}
<p data-tipo="contexto">Alberto Núñez Feijóo leyó el marcador en clave de fútbol el domingo, después de ver a la selección en el Metropolitano. En El Partidazo de COPE dijo que el PP va ganando «claramente», pero pidió no relajarse, según Europa Press:</p>
<blockquote class="cita"><p>«Queda lo más importante, que son los últimos días de liga donde te juegas todo»</p><footer>Alberto Núñez Feijóo, candidato del PP, según <a href="{FEIJOO}">Europa Press</a> (15 de noviembre de 2026).</footer></blockquote>
<h2>Lo que estas encuestas no dicen</h2>
<p data-tipo="contexto">Comparar una encuesta con la anterior de la misma empresa evita mezclar métodos distintos, pero no borra el error de muestreo. Los márgenes de esta pieza suponen muestreo aleatorio simple, como las fichas técnicas, y solo se calculan cuando las dos encuestas comparadas tienen muestras distintas: los trackings suman entrevistas de varios días y una entrega comparte buena parte de ellas con la del día anterior. La <a href="{YG['url']}">encuesta de YouGov para el Ara</a>, publicada el sábado con trabajo de campo hasta el 2 de noviembre, no tiene otra anterior en la tabla y queda fuera de la comparación. La ley prohíbe publicar encuestas desde el martes 24 de noviembre.</p>
'''

preguntas = [
    ('¿Sube el PSOE en las encuestas de la campaña del 29N?',
     f'En {NUM[len(PSOE_SUBE)]} de las {NUM[NC]} empresas que han publicado una encuesta entre el 13 y el 16 de noviembre y tenían una anterior, sí, entre {rng([c["dPSOE"] for c in sube_psoe])} puntos. En {lista(PSOE_BAJA)} baja. El PP baja en {NUM[len(PP_BAJA)]}: {lista(sorted(PP_BAJA))}.'),
    ('¿Cuántas encuestas dan mayoría absoluta a PP y Vox?',
     f'{M1} de las {len(E1)} que publican escaños, con la última de cada empresa de los últimos 30 días a 16 de noviembre de 2026. No la dan el CIS ni SW Demoscopia.'),
    ('¿Qué dice la media de las encuestas al empezar la campaña?',
     f'La media del modelo de Mapa Electoral da al PP el {p(MED1["PP"])} %, al PSOE el {p(MED1["PSOE"])} % y a Vox el {p(MED1["VOX"])} % el 16 de noviembre, frente al {p(MED0["PP"])}, el {p(MED0["PSOE"])} y el {p(MED0["VOX"])} % del 13.'),
]
enlaces = (f'{L("encuestas-40db-psoe-podemos-29n", "La encuesta de El País del 9 de noviembre")} · {L("cis-preelectoral-29n", "El CIS preelectoral")} · '
           f'{L("dos-semanas-29n-la-semana-en-el-mapa", "A dos semanas del 29N")} · <a href="{BASE}encuestas/">Encuestas elecciones generales 2026</a>')
foot = ('Datos: encuestas nacionales publicadas hasta el 16 de noviembre de 2026, recogidas por Electográfica y Wikipedia; media de encuestas y escenario '
        'central de mapaelectoral.es/encuestas del 13 y el 16 de noviembre. Cálculo: actualidad/src/resumenes/semana_campana.py.')

DATOS = {'CASAS': [{k: v for k, v in c.items() if k not in ('e', 'ant')} for c in CASAS], 'TRACK': TRACK, 'MED0': MED0, 'MED1': MED1,
         'PV0': PV0, 'PV1': PV1, 'PR0': PR0, 'PR1': PR1, 'HE0': HE0, 'HE1': HE1, 'NCAMP': len(camp), 'YG': [nombre(YG), YG['fin'], pub(YG)], 'INDEP': INDEP, 'GAP1': GAP1, 'PSOE_GANA': PSOE_GANA, 'NO_MAY': NO_MAY, 'G': [G0, len(U0), G1, len(U1)], 'M': [M0, len(E0), M1, len(E1)]}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza('encuestas-primera-semana-campana-29n', 'Las encuestas, semana a semana',
      f'El PSOE sube en {NUM[len(PSOE_SUBE)]} de las {NUM[NC]} encuestas de la primera semana de campaña; el PP baja en {NUM[len(PP_BAJA)]} y sube en otras {NUM[len(PP_SUBE)]}',
      f'Patxi López dijo el sábado que todas las encuestas marcan el alza del PSOE y el descenso del PP. Desde el arranque de la campaña, los cambios son de décimas '
      f'y ninguno supera el margen de error. El PP sigue primero en {G1} de {len(U1)} encuestas y la media de nuestro modelo apenas se mueve.',
      '16 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('CASAS', [(c['casa'], c['dPP'], c['dPSOE'], round(c['mPP'], 1), round(c['mPSOE'], 1)) for c in CASAS])
print('G', G0, len(U0), G1, len(U1), 'M', M0, len(E0), M1, len(E1), 'PR', PR0, PR1, 'HE', HE0['PP'], HE0['Vox'], HE1['PP'], HE1['Vox'])
