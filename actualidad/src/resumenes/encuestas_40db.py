"""«La encuesta de El País» (9-11-2026): el preelectoral de 40dB para El País y la SER (campo del 2 al 4 de noviembre,
2.000 entrevistas en línea) deja al PSOE a dos puntos del PP y a Podemos en el 1,2 %.

Datos de las encuestas: previsiones/datos/encuestas/encuestas_limpias.csv (lo actualiza la Action «Encuestas» desde
Electográfica y Wikipedia). Escaños y transferencias de voto: informe de 40dB publicado por El País (PDF), páginas 6 a 10.
Media de las encuestas: la del modelo de /encuestas/ de las 10.53 del 9 de noviembre
(previsiones/datos/publico/historico/2026-11-09-1053.json).
Uso, desde la raíz: python3 actualidad/src/resumenes/encuestas_40db.py
"""
import csv
import json

from comun import BASE, COLOR, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
PDF = 'https://ep00.epimg.net/infografias/encuestas40db/2026/11-preelectoral/2026_11_preelectoral_informe.pdf'
PDF_OCT = 'https://ep00.epimg.net/infografias/encuestas40db/2026/10-08-barometro-flash/2026_10_informe_voto_barometro_flash.pdf'
MAROTO = 'https://www.europapress.es/madrid/noticia-psoe-asegura-remontada-realidad-avisa-feijoo-le-van-hacer-muy-largas-semanas-20261109111930.html'
MONTERO = 'https://www.europapress.es/nacional/noticia-montero-rufian-animan-votar-memoria-conciencia-obviando-voto-util-psoe-si-puede-te-come-20261107134413.html'
GAD3 = 'https://www.abc.es/espana/accidente-urda-apenas-altera-bloques-29n-derecha-20261108023004-nt.html'
MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

filas = [r for r in csv.DictReader(open(RAIZ / 'previsiones/datos/encuestas/encuestas_limpias.csv', encoding='utf-8')) if r['ambito'] == 'ESPAÑA']
f = lambda r, k: float(r[k]) if r[k] else None

# Serie de 40dB desde enero de 2025 (barómetros mensuales y el flash de octubre)
S40 = [dict(pub=r['publicado'], campo=r['campo_fin'], PP=f(r, 'PP'), PSOE=f(r, 'PSOE'), VOX=f(r, 'VOX'), POD=f(r, 'PODEMOS'))
       for r in filas if r['encuestadora'] == '40dB.' and r['publicado'] >= '2025-01-01']
S40.sort(key=lambda s: s['pub'])
NOV, OCT = S40[-1], S40[-2]
assert NOV['pub'] == '2026-11-09' and (NOV['PP'], NOV['PSOE'], NOV['POD']) == (31.9, 29.9, 1.2), NOV
assert OCT['pub'] == '2026-10-09', OCT
for s in S40:
    s['dif'] = round(s['PP'] - s['PSOE'], 1)
# última vez que el PSOE estuvo tan alto y el PP tan cerca en 40dB
PSOE_ANT = max((s for s in filas if s['encuestadora'] == '40dB.' and s['publicado'] < '2026-11-09' and s['PSOE'] and float(s['PSOE']) >= NOV['PSOE']),
               key=lambda s: s['publicado'])['publicado']
DIF_ANT = max((s for s in S40[:-1] if s['dif'] < NOV['dif']), key=lambda s: s['pub'])
POD_MIN_ANT = min(float(r['PODEMOS']) for r in filas if r['encuestadora'] == '40dB.' and r['PODEMOS'] and r['publicado'] < '2026-11-09')
POD_DESDE = min(r['publicado'] for r in filas if r['encuestadora'] == '40dB.' and r['PODEMOS'])

# Última encuesta de cada empresa publicada en el último mes (desde el 10 de octubre)
ult = {}
for r in sorted((r for r in filas if r['publicado'] >= '2026-10-10'), key=lambda r: (r['publicado'], r['campo_fin'])):
    ult[r['encuestadora']] = r
CASAS = sorted(([k.rstrip('.'), r['cliente'] if r['cliente'] != 'n/a' else '', r['publicado'], f(r, 'PP'), f(r, 'PSOE'),
                 round(f(r, 'PP') - f(r, 'PSOE'), 1)] for k, r in ult.items()), key=lambda c: c[5])
NCASAS = len(CASAS)
MAS_CERCA = [c[0] for c in CASAS if c[5] < NOV['dif']]
HOY = [c for c in CASAS if c[2] == '2026-11-09']
assert [c[0] for c in HOY] == ['40dB', 'GAD3', 'NC Report', 'Data10'], HOY

# Media de las encuestas del modelo, 9-11-2026 10.53
URL = {k.rstrip('.'): r['url_agregador'] if 'licdn.com' in r['fuente_original'] else r['fuente_original'] for k, r in ult.items()}
MED = json.load(open(RAIZ / 'previsiones/datos/publico/historico/2026-11-09-1053.json'))['meta']['media_encuestas']
MED_DIF = MED['PP'] - MED['PSOE']

# Informe de 40dB (PDF), noviembre y octubre (flash)
ESC = {'PP': 129, 'PSOE': 119, 'Vox': 61, 'Frente Amplio': 10, 'Podemos': 0, 'Otros': 31}
ESC_OCT = {'PP': 132, 'PSOE': 112, 'Vox': 66, 'Frente Amplio': 5, 'Podemos': 2, 'Otros': 33}
assert sum(ESC.values()) == 350 and sum(ESC_OCT.values()) == 350
FA = {'FA sin Podemos': 3.4, 'Compromís': 1.1, 'UPC': 0.3, 'Ara Més': 0.2}
# A quién votarían ahora los que votaron a Sumar en julio de 2023 (pág. 10; 152 entrevistados)
TR = [('Frente Amplio', 37.4, 'var(--sumar)'), ('PSOE', 22.0, 'var(--psoe)'), ('Abstención', 19.3, 'var(--otros)'),
      ('Podemos', 7.9, 'var(--pod)'), ('PP', 2.0, 'var(--pp)')]
TR_OCT = {'PSOE': 12.2, 'Podemos': 25.6}
N_SUMAR, N_SUMAR_OCT = 152, 46

# ---------- Gráfico de «Lo último» de /encuestas/ (#517), reutilizado ----------
# Nacho, 9-11-2026: «Estos gráficos hay que hacerlos siempre en el tema de las encuestas»
import importlib.util, re
_spec = importlib.util.spec_from_file_location('enc_construir', RAIZ / 'encuestas/src/construir.py')
enc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enc)
_pub = lambda e: e.get('publicado') or e['fin']
_validas = sorted((e for e in enc.carga() if not e['reest'] and e['fin'] >= '2023-07-24'), key=_pub, reverse=True)
_hoy = [e for e in _validas if _pub(e) == '2026-11-09']
assert sorted(enc.clave(e['casa']) for e in _hoy) == ['40db', 'data10', 'gad3', 'ncreport'], [e['casa'] for e in _hoy]
_hoy.sort(key=lambda e: (enc.clave(e['casa']) != '40db', e['voto']['PP'] - e['voto']['PSOE']))   # 40dB primero, luego de menos a más distancia
_graf = []
for e in _hoy:
    ant = next((x for x in _validas if x is not e and enc.clave(x['casa']) == enc.clave(e['casa']) and _pub(x) < _pub(e)), None)
    _graf.append((e, ant, f'{esc(e["casa"])}' + (f' · {esc(e["medio"])}' if e['medio'] else '') + f' · {enc.dia(_pub(e))}'))
CSS_ULTIMO = '<style>' + '\n'.join(l for l in enc.ESTILOS.split('\n') if l.startswith(('.ultimo-graf', '.bu-')) or ('.bu-b i' in l and 'prefers-color-scheme' in l or l.startswith(':root[data-theme="dark"] .bu-b'))) + '</style>'
assert CSS_ULTIMO.count('.bu-') >= 8, CSS_ULTIMO
g_hoy = enc.graficos_ultimo(_graf).replace('Las últimas encuestas, partido a partido', 'Las cuatro encuestas de este lunes, partido a partido')

# ---------- Gráficos ----------
def serie_dif():
    """Barras verticales: ventaja del PP sobre el PSOE en cada encuesta de 40dB desde enero de 2025."""
    W, H, ml, mt, mb = 640, 230, 30, 14, 34
    N = len(S40)
    bw = (W - ml - 4) / N
    hi = 7
    y = lambda v: mt + (1 - v / hi) * (H - mt - mb)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Ventaja del PP sobre el PSOE en las encuestas de 40dB desde enero de 2025">']
    for v in range(0, hi + 1, 2):
        out.append(f'<line x1="{ml}" x2="{W}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--grid)"/>'
                   f'<text x="{ml - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{v}</text>')
    for i, s in enumerate(S40):
        x = ml + i * bw
        ultima = i == N - 1
        out.append(f'<rect x="{x + 2:.1f}" y="{y(s["dif"]):.1f}" width="{bw - 4:.1f}" height="{y(0) - y(s["dif"]):.1f}" rx="2" '
                   f'fill="var(--pp)" fill-opacity="{1 if ultima else .55}"><title>{esc(fecha(s["pub"]))}: PP {p(s["PP"])} %, PSOE {p(s["PSOE"])} %, '
                   f'ventaja del PP {p(s["dif"])} puntos</title></rect>')
        if ultima or i == 0 or s['pub'][5:7] in ('01', '07') or s['dif'] == min(t['dif'] for t in S40):
            out.append(f'<text x="{x + bw / 2:.1f}" y="{y(s["dif"]) - 5:.1f}" text-anchor="middle" class="{"lab" if ultima else ""}">{p(s["dif"])}</text>')
        if s['pub'][5:7] in ('01', '04', '07', '10') and not (s['pub'][5:7] == '10' and S40[i - 1]['pub'][5:7] == '10') or ultima:
            out.append(f'<text x="{x + bw / 2:.1f}" y="{H - 18}" text-anchor="middle">{MES[int(s["pub"][5:7]) - 1]}</text>')
        if s['pub'][5:7] == '01' or i == 0:
            out.append(f'<text x="{x + bw / 2:.1f}" y="{H - 3}" text-anchor="middle">{s["pub"][:4]}</text>')
    out.append('</svg>')
    return ''.join(out)


def casas():
    """Barras divergentes: ventaja del PP (a la derecha, azul) o del PSOE (a la izquierda, rojo) en la última encuesta de cada empresa."""
    W, alto, ml = 640, 25, 130
    lo, hi = -12, 9
    H = alto * NCASAS + 30
    x = lambda v: ml + (v - lo) / (hi - lo) * (W - ml - 40)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Ventaja del PP o del PSOE en la última encuesta de cada empresa publicada en el último mes">']
    for v in range(-12, 10, 3):
        out.append(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="0" y2="{H - 22}" stroke="{"var(--muted)" if v == 0 else "var(--grid)"}"/>'
                   f'<text x="{x(v):.1f}" y="{H - 6}" text-anchor="middle">{abs(v)}</text>')
    for i, c in enumerate(CASAS):
        yy = i * alto
        es40 = c[0] == '40dB'
        col = 'var(--pp)' if c[5] > 0 else 'var(--psoe)'
        nom = c[0]
        out.append(f'<text x="{ml - 8}" y="{yy + 17}" text-anchor="end" class="{"lab" if es40 else ""}" style="fill:var(--fg)">{esc(nom)}</text>')
        x0, x1 = sorted((x(0), x(c[5])))
        out.append(f'<rect x="{x0:.1f}" y="{yy + 5}" width="{max(1.5, x1 - x0):.1f}" height="{alto - 9}" rx="2" fill="{col}" fill-opacity="{1 if es40 else .6}">'
                   f'<title>{esc(nom)}, {esc(fecha(c[2]))}: PP {p(c[3])} %, PSOE {p(c[4])} %</title></rect>')
        if c[5] >= 0:
            out.append(f'<text x="{x(c[5]) + 6:.1f}" y="{yy + 17}" class="{"lab" if es40 else ""}">{p(c[5])}</text>')
        else:   # dentro de la barra, para no pisar el nombre
            out.append(f'<text x="{x(c[5]) + 6:.1f}" y="{yy + 17}" style="fill:#fff;font-weight:600">{p(-c[5])}</text>')
    out.append('</svg>')
    return ''.join(out)


def fecha(s):
    a, m, d = s.split('-')
    return f'{int(d)} {MES[int(m) - 1]} {a}'


g_serie = figura('El PP, en cada encuesta de 40dB, por delante del PSOE',
                 'Ventaja del PP sobre el PSOE, en puntos de estimación de voto. Una barra por encuesta, desde enero de 2025; la última, la del 9 de noviembre',
                 serie_dif(), f'Fuente: 40dB para El País y la SER (<a href="{PDF}">informe de noviembre</a>), serie recogida por Electográfica. Cálculo propio.',
                 leyenda=[('Ventaja del PP sobre el PSOE', 'var(--pp)')],
                 tabla=(['Publicada', 'PP', 'PSOE', 'Ventaja del PP'], [[fecha(s['pub']), p(s['PP']), p(s['PSOE']), p(s['dif'])] for s in reversed(S40)]))

g_casas = figura('Del PSOE 11,8 puntos por delante al PP 8 puntos por delante',
                 f'Ventaja del PP (a la derecha) o del PSOE (a la izquierda), en puntos, en la última encuesta de cada una de las {NCASAS} empresas que han publicado una desde el 10 de octubre',
                 casas(), 'Fuente: encuestas publicadas, recogidas por Electográfica y Wikipedia. Cálculo propio.',
                 leyenda=[('PP por delante', 'var(--pp)'), ('PSOE por delante', 'var(--psoe)')],
                 tabla=(['Empresa', 'Publicada', 'PP', 'PSOE', 'Ventaja'],
                        [[c[0] + (f' ({c[1]})' if c[1] else ''), fecha(c[2]), p(c[3]), p(c[4]), ('PP +' if c[5] > 0 else 'PSOE +') + p(abs(c[5]))] for c in CASAS]))

g_tr = figura('Qué votarían ahora los que votaron a Sumar en 2023',
              f'Porcentaje de quienes recuerdan haber votado a Sumar en julio de 2023 ({N_SUMAR} entrevistados). Solo se muestran las opciones por encima del 2 %',
              barras([(t, v, c, p(v) + ' %') for t, v, c in TR], 45, 'Transferencia de voto de los votantes de Sumar en 2023 según 40dB', W=420, ml=100, fmt=p),
              f'Fuente: 40dB para El País y la SER, <a href="{PDF}">informe de noviembre</a>, pág. 10.',
              leyenda=[(t, c) for t, _, c in TR])

g_esc = figura('Los escaños que da 40dB',
               'Estimación central de escaños, en noviembre y en la encuesta flash de octubre. La mayoría absoluta está en 176',
               barras([(k, ESC[k], COLOR.get(k, 'var(--sumar)' if k == 'Frente Amplio' else 'var(--otros)'), f'{ESC[k]} (oct.: {ESC_OCT[k]})') for k in ESC],
                      200, 'Escaños de cada partido según 40dB, noviembre y octubre', W=420, ml=100),
               f'Fuente: 40dB para El País y la SER, <a href="{PDF}">informe de noviembre</a>, pág. 8. «Otros»: ERC 10, EH Bildu 7, Junts 3, PNV 3, Adelante Andalucía 3, BNG 2, UPN-PP 2 y Coalición Canaria 1.',
               leyenda=[('PP', 'var(--pp)'), ('PSOE', 'var(--psoe)'), ('Vox', 'var(--vox)'), ('Frente Amplio', 'var(--sumar)'), ('Podemos', 'var(--pod)'), ('Otros', 'var(--otros)')],
               tabla=(['Partido', 'Noviembre', 'Octubre'], [[k, str(ESC[k]), str(ESC_OCT[k])] for k in ESC]))

pp_vox, pp_vox_oct = ESC['PP'] + ESC['Vox'], ESC_OCT['PP'] + ESC_OCT['Vox']
d_psoe = NOV['PSOE'] - OCT['PSOE']
d_pod = OCT['POD'] - NOV['POD']

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="dato">El PSOE se queda a dos puntos del PP en la encuesta preelectoral de 40dB para El País y la SER, publicada este lunes: <strong>{p(NOV['PSOE'])} %</strong> frente al <strong>{p(NOV['PP'])} %</strong>. Hace un mes, en la encuesta flash de octubre, el PSOE tenía el {p(OCT['PSOE'])} %: sube {p(d_psoe)} puntos, y el PP repite. Es el dato más alto del PSOE en 40dB desde diciembre de 2024, cuando también marcó el {p(NOV['PSOE'])} %, y la distancia más corta desde octubre de 2025, cuando fue de {p(DIF_ANT['dif'])} puntos. Vox baja al {p(NOV['VOX'])} %. El trabajo de campo se hizo del 2 al 4 de noviembre, con 2.000 entrevistas en línea y un error muestral de ±2,2 puntos, según el <a href="{PDF}">informe de 40dB</a>.</p>
{g_serie}
<p data-tipo="dato">En escaños, 40dB da al PP <strong>{ESC['PP']}</strong>, al PSOE <strong>{ESC['PSOE']}</strong> y a Vox <strong>{ESC['Vox']}</strong>. PP y Vox suman {pp_vox}, por encima de la mayoría absoluta de 176, pero {pp_vox_oct - pp_vox} menos que hace un mes, cuando sumaban {pp_vox_oct}. El PSOE gana siete diputados respecto a octubre.</p>
{g_esc}
<p data-tipo="contexto">La socialista Reyes Maroto, portavoz del PSOE en el Ayuntamiento de Madrid, habló este lunes de las últimas encuestas, según Europa Press:</p>
<blockquote class="cita"><p>«Hoy seguro que en Génova están preocupados, preocupados porque la remontada es una realidad»</p><footer>Reyes Maroto, portavoz del PSOE en el Ayuntamiento de Madrid, según <a href="{MAROTO}">Europa Press</a> (9 de noviembre de 2026).</footer></blockquote>
<h2>Las demás encuestas no lo ven igual</h2>
<p data-tipo="dato">Este lunes se han publicado otras tres encuestas con trabajo de campo de la misma semana, y las tres dejan al PP mucho más lejos: <a href="{GAD3}">GAD3 para ABC</a>, a {p(HOY[1][5])} puntos; <a href="{URL['NC Report']}">NC Report para La Razón</a>, a {p(HOY[2][5])}, y <a href="{URL['Data10']}">Data10 para OKDiario</a>, a {p(HOY[3][5])}. De las {NCASAS} empresas con una encuesta publicada desde el 10 de octubre, solo tres ponen al PSOE más cerca que 40dB, y dos de ellas, por delante: <a href="{URL['CIS']}">el CIS</a>, con el último barómetro del 14 de octubre, y <a href="{URL['SW Demoscopia']}">SW Demoscopia</a>. La tercera es <a href="{URL['More in Common']}">More in Common</a>, con el PP {p(CASAS[2][5])} puntos por delante.</p>
{g_casas}
{CSS_ULTIMO}
{g_hoy}
<p data-tipo="dato">La media de las encuestas que usa <a href="{BASE}encuestas/">nuestro modelo</a>, con los datos de las 10.53 del 9 de noviembre, deja al PP en el {p(MED['PP'])} % y al PSOE en el {p(MED['PSOE'])} %: {p(MED_DIF)} puntos de distancia, el doble que 40dB.</p>
<p data-tipo="hipotesis">Las encuestas no se ponen de acuerdo porque cada empresa pregunta de una forma, pondera de otra y corrige el recuerdo de voto a su manera. Que 40dB vea al PSOE más cerca no dice que las otras se equivoquen, ni al revés: la distancia entre el PP y el PSOE es la cifra que más cambia de una encuesta a otra, y la más difícil de medir a tres semanas del 29N.</p>
<h2>Podemos, en su mínimo, y el voto de Sumar</h2>
<p data-tipo="dato">El otro dato de la encuesta es el de Podemos, que concurre separado del Frente Amplio: baja al <strong>{p(NOV['POD'])} %</strong>, {p(d_pod)} puntos menos que en octubre y el dato más bajo que le ha dado 40dB desde que lo mide por separado, en 2024. Hasta ahora, su mínimo era el {p(POD_MIN_ANT)} %. Con ese porcentaje, 40dB le da cero escaños, con un margen de cero a uno; en octubre le daba dos. En Cataluña, Podemos va en las listas de ERC. El Frente Amplio, con Compromís, Ara Més y la Unidad del Pueblo Canario, saca el {p(sum(FA.values()))} % y {ESC['Frente Amplio']} escaños.</p>
<p data-tipo="dato">El informe de 40dB pregunta también a quién votarían ahora los que votaron a Sumar en julio de 2023. El {p(TR[0][1])} % iría al Frente Amplio, el <strong>{p(TR[1][1])} %</strong> al PSOE y el {p(TR[3][1])} % a Podemos; el {p(TR[2][1])} % se abstendría.</p>
{g_tr}
<p data-tipo="hipotesis">Esos 152 entrevistados son pocos, y la comparación con octubre lo es todavía más: en la encuesta flash eran 46, y entonces el {p(TR_OCT['Podemos'])} % se iba a Podemos y el {p(TR_OCT['PSOE'])} % al PSOE, según el <a href="{PDF_OCT}">informe de octubre</a>. Además, en octubre la opción se llamaba «Sumar/Frente Amplio». Con esas muestras, el cambio es un indicio de por dónde podría venir la subida del PSOE, no una medida.</p>
<p data-tipo="contexto">Es justo el voto útil contra el que hacía campaña la candidata de Podemos, Irene Montero, el sábado en Madrid, en un acto con Gabriel Rufián:</p>
<blockquote class="cita"><p>«El PSOE, si puede, te come. Pero nosotras, si queremos que nuestro país sea como soñamos, no nos podemos dejar. Por eso apelan al voto útil»</p><footer>Irene Montero, candidata de Podemos, según <a href="{MONTERO}">Europa Press</a> (7 de noviembre de 2026).</footer></blockquote>
<h2>Lo que esta encuesta no dice</h2>
<p data-tipo="contexto">Una encuesta es una foto con margen de error. El ±2,2 que declara 40dB vale para cada porcentaje por separado; la distancia entre dos partidos tiene un margen mayor, y los dos puntos entre el PP y el PSOE caben dentro. Las estimaciones de escaños de 40dB son suyas, no de nuestro modelo, que reparte la media de todas las encuestas provincia a provincia. La ley prohíbe publicar encuestas desde el martes 24 de noviembre.</p>
'''

preguntas = [
    ('¿Qué dice la encuesta de 40dB para El País de noviembre?',
     f'PP {p(NOV["PP"])} %, PSOE {p(NOV["PSOE"])} %, Vox {p(NOV["VOX"])} %, Frente Amplio {p(sum(FA.values()))} %, SALF 2,0 % y Podemos {p(NOV["POD"])} %. En escaños, PP {ESC["PP"]}, PSOE {ESC["PSOE"]} y Vox {ESC["Vox"]}. Campo del 2 al 4 de noviembre de 2026, 2.000 entrevistas en línea.'),
    ('¿Suman mayoría absoluta PP y Vox según 40dB?',
     f'Sí: {pp_vox} escaños, por encima de 176, aunque {pp_vox_oct - pp_vox} menos que en la encuesta de octubre.'),
    ('¿Entra Podemos en el Congreso según 40dB?',
     f'Con el {p(NOV["POD"])} % de los votos, 40dB le da cero escaños, con un margen de cero a uno.'),
]
enlaces = (f'{L("encuestas-antes-despues-urda-29n", "Las encuestas tras el choque de Urda")} · {L("psoe-primera-fuerza-29n", "El sorpasso que no sale")} · '
           f'{L("frente-amplio-podemos-madrid-escanos-29n", "Frente Amplio y Podemos en Madrid")} · <a href="{BASE}encuestas/">Todas las encuestas del 29N</a> · '
           f'<a href="{BASE}encuestas/40db/">Las encuestas de 40dB</a>')
foot = ('Datos: 40dB para El País y la SER, informes de noviembre y octubre de 2026; encuestas nacionales publicadas desde el 10 de octubre de 2026, '
        'recogidas por Electográfica y Wikipedia; media de encuestas de mapaelectoral.es/encuestas. Cálculo: actualidad/src/resumenes/encuestas_40db.py.')

DATOS = {'S40': S40, 'CASAS': CASAS, 'MED': MED, 'ESC': ESC, 'ESC_OCT': ESC_OCT, 'FA': FA, 'TR': {t: v for t, v, _ in TR}, 'TR_OCT': TR_OCT,
         'POD_MIN_ANT': POD_MIN_ANT, 'DIF_ANT': DIF_ANT, 'PSOE_ANT': PSOE_ANT, 'POD_DESDE': POD_DESDE, 'MAS_CERCA': MAS_CERCA}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza('encuestas-40db-psoe-podemos-29n', 'La encuesta de El País',
      f'El PSOE se queda a dos puntos del PP en la encuesta de El País, su mejor dato en 40dB desde 2024',
      f'40dB da al PSOE el {p(NOV["PSOE"])} % y al PP el {p(NOV["PP"])} %. Las otras tres encuestas publicadas este lunes ven entre seis y ocho puntos de distancia. '
      f'Podemos cae al {p(NOV["POD"])} %, su mínimo en esta serie, y se quedaría sin escaño.',
      '9 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('PSOE_ANT', PSOE_ANT, 'DIF_ANT', DIF_ANT, 'POD_MIN_ANT', POD_MIN_ANT, POD_DESDE, 'MAS_CERCA', MAS_CERCA, 'MED_DIF', MED_DIF, 'HOY', HOY)
