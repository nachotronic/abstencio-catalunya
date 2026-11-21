"""«El derbi sevillano en las urnas» (pieza de sábado, 21-11-2026, día del Sevilla-Betis en el Sánchez-Pizjuán).

Cifras: secciones (generales-2026/descargas/secciones.csv, con la renta por unidad de consumo del INE) de las generales de
noviembre de 2019 y julio de 2023; barrios y distritos de data/barrios/secciones_barrio.csv; ciudad de
generales-2026/data/municipios.json. Sumar solo se usa en 2023: en 2019 la familia SUMAR del fichero suma listas distintas,
así que no se compara ni se cuentan secciones ganadas en 2019. Quintiles de renta dentro de la ciudad, sin regresión.
Uso, desde la raíz: python3 actualidad/src/resumenes/derbi_sevilla.py
"""
import json

import pandas as pd

from comun import BASE, COLOR, RAIZ, barras, figura, n, pieza

A = BASE + 'actualidad/'
SEV = '41091'
E, E0 = '2023_07', '2019_11'
P = ['PP', 'PSOE', 'SUMAR', 'VOX']
ETQ = {'PP': 'PP', 'PSOE': 'PSOE', 'SUMAR': 'Sumar', 'VOX': 'Vox', 'EMPATE': 'Empate a votos'}
p = lambda v: n(v, 1)
NERV, BELL = 'Nervión', 'Distrito Bellavista-La Palmera'

# --- La ciudad ---
m = json.load(open(RAIZ / 'generales-2026/data/municipios.json'))
i = m['cod'].index(SEV)
pc = lambda e, k: m[f'{e}_{k}'][i] * 100
assert [round(pc(E, k), 1) for k in P] == [37.3, 33.6, 14.2, 12.3]
assert [round(pc(E0, k), 1) for k in ('PP', 'PSOE', 'VOX')] == [21.8, 31.8, 17.5]

# --- Secciones ---
d = pd.read_csv(RAIZ / 'generales-2026/descargas/secciones.csv', dtype={'tract_code': str, 'mun_code': str})
d = d[d.mun_code == SEV].dropna(subset=[f'{E}_PP']).copy()
bar = pd.read_csv(RAIZ / 'data/barrios/secciones_barrio.csv', dtype=str)[['tract_code', 'barrio', 'distrito']]
d = d.merge(bar, on='tract_code', how='left')
d['gana'] = d[[f'{E}_{k}' for k in P]].idxmax(axis=1).str[8:].where(d[f'{E}_gana'] != 'EMPATE', 'EMPATE')
GANA = {k: int(c) for k, c in d.gana.value_counts().items()}
assert len(d) == 521 and GANA == {'PSOE': 286, 'PP': 234, 'SUMAR': 1}
SINB = int(d.barrio.isna().sum())
assert SINB == 21


def cuota(s, k, e=E):
    return (s[f'{e}_{k}'] * s[f'{e}_votantes']).sum() / s[f'{e}_votantes'].sum() * 100


def part(s, e=E):
    return s[f'{e}_votantes'].sum() / s[f'{e}_censo'].sum() * 100


def resumen(s):
    return {**{k: cuota(s, k) for k in P}, 'part': part(s), 'renta': s.renta_uc.median(), 'n': len(s),
            'gana': {k: int(c) for k, c in s.gana.value_counts().items()},
            'PP0': cuota(s, 'PP', E0), 'PSOE0': cuota(s, 'PSOE', E0), 'VOX0': cuota(s, 'VOX', E0)}


D = {k: resumen(s) for k, s in d.groupby('distrito')}
NE, BE = D[NERV], D[BELL]
assert NE['n'] == 41 and NE['gana'] == {'PP': 37, 'PSOE': 4} and round(NE['PP'], 1) == 55.9 and round(NE['PSOE'], 1) == 19.4
assert round(NE['part'], 1) == 80.0 and NE['renta'] == 30519 and round(NE['PP0'], 1) == 37.2 and round(NE['VOX0'], 1) == 20.3
assert BE['n'] == 28 and BE['gana'] == {'PP': 18, 'PSOE': 10} and round(BE['PP'], 1) == 43.7 and round(BE['PSOE'], 1) == 26.4
assert round(BE['part'], 1) == 76.3 and BE['renta'] == 26090 and round(BE['PP0'], 1) == 25.3 and round(BE['PSOE0'], 1) == 26.4
RE, CA, NO = D['Los Remedios'], D['Distrito Cerro-Amate'], D['Distrito Norte']
assert max(D, key=lambda k: D[k]['PP']) == 'Los Remedios' and round(RE['PP'], 1) == 65.3
assert CA['gana'] == {'PSOE': 66} and NO['gana'] == {'PSOE': 46} and round(CA['PSOE'], 1) == 49.7 and round(CA['part'], 1) == 61.4
assert sorted(D, key=lambda k: -D[k]['PP'])[1] == NERV

B = {k: resumen(s) for k, s in d.groupby('barrio')}
BN, BH, BB, BU = B['Nervión'], B['Heliópolis'], B['Bellavista'], B['La Buhaira']
assert BN['n'] == 14 and BN['gana'] == {'PP': 13, 'PSOE': 1} and round(BN['PP'], 1) == 52.9 and round(BN['PSOE'], 1) == 22.1
assert BH['n'] == 1 and round(BH['PP'], 1) == 63.4 and round(BH['VOX'], 1) == 20.9 and round(BH['PSOE'], 1) == 8.0 and BH['renta'] == 39187
assert BB['n'] == 11 and BB['gana'] == {'PSOE': 8, 'PP': 3} and round(BB['PSOE'], 1) == 38.0 and round(BB['PP'], 1) == 29.7 and BB['renta'] == 17085
assert round(BU['PP'], 1) == 65.4 and BU['gana'] == {'PP': 7}

# Quintiles de renta
g = d.dropna(subset=['renta_uc']).copy()
g['q'] = pd.qcut(g.renta_uc.rank(method='first'), 5, labels=False)
Q = {q: resumen(s) for q, s in g.groupby('q')}
assert round(Q[0]['PSOE'], 1) == 55.0 and round(Q[0]['PP'], 1) == 16.6 and Q[0]['gana'] == {'PSOE': 105}
assert round(Q[4]['PP'], 1) == 59.9 and round(Q[4]['PSOE'], 1) == 15.2 and Q[4]['gana'] == {'PP': 104}
assert round(Q[0]['part'], 1) == 56.0 and round(Q[4]['part'], 1) == 82.2

# --- Gráficos ---
NOMD = lambda k: k.replace('Distrito ', '')
orden = sorted(D, key=lambda k: -D[k]['PP'])
FUENTE = (f'Fuente: Ministerio del Interior (generales del 23 de julio de 2023, por sección censal) e INE (renta por unidad de consumo). '
          f'Distritos de Sevilla según OpenStreetMap; {SINB} secciones sin distrito asignado solo cuentan en el total de la ciudad.')
EST = lambda k: k in (NERV, BELL)
g_dist = figura('Nervión, el distrito del Sánchez-Pizjuán, es el segundo donde más vota al PP',
                '% de voto al PP en las elecciones generales de 2023 en cada distrito de Sevilla. En color fuerte, los distritos de los dos estadios',
                barras([(NOMD(k), D[k]['PP'], 'var(--pp)' if EST(k) else 'color-mix(in srgb, var(--pp) 55%, var(--bg))', f"{p(D[k]['PP'])} %") for k in orden],
                       70, 'Voto al PP por distrito de Sevilla', W=420, ml=150, linea=(pc(E, 'PP'), f"Ciudad: {p(pc(E, 'PP'))} %"), separar=True),
                FUENTE, None,
                (['Distrito', 'PP', 'PSOE', 'Sumar', 'Vox', 'Participación', 'Renta mediana (€)', 'Secciones', 'Ganadas por el PP', 'Ganadas por el PSOE'],
                 [[NOMD(k), p(D[k]['PP']), p(D[k]['PSOE']), p(D[k]['SUMAR']), p(D[k]['VOX']), p(D[k]['part']), n(D[k]['renta']), str(D[k]['n']),
                   str(D[k]['gana'].get('PP', 0)), str(D[k]['gana'].get('PSOE', 0))] for k in orden]))


def quint(W=640, H=250, ml=40, mr=105, mt=12, mb=34):
    x = lambda j: ml + j * (W - ml - mr) / 4
    y = lambda val: mt + (60 - val) / 60 * (H - mt - mb)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Voto por quintil de renta en Sevilla">']
    for val in (0, 15, 30, 45, 60):
        out.append(f'<line x1="{ml}" x2="{W - mr}" y1="{y(val):.1f}" y2="{y(val):.1f}" stroke="var(--grid)"/><text x="{ml - 6}" y="{y(val) + 4:.1f}" text-anchor="end">{val} %</text>')
    for j, t in enumerate(['Más pobre', '2.º', '3.º', '4.º', 'Más rico']):
        out.append(f'<text x="{x(j):.1f}" y="{H - 10}" text-anchor="middle">{t}</text>')
    ys, prev = {}, None
    for k in sorted(P, key=lambda k: -Q[4][k]):
        ys[k] = y(Q[4][k]) if prev is None else max(y(Q[4][k]), prev + 15)
        prev = ys[k]
    for k in P:
        col = COLOR[ETQ[k]]
        pts = ' '.join(f'{x(j):.1f},{y(Q[j][k]):.1f}' for j in range(5))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3"/>')
        for j in range(5):
            out.append(f'<circle cx="{x(j):.1f}" cy="{y(Q[j][k]):.1f}" r="4" fill="{col}"><title>{ETQ[k]}, quintil {j + 1}: {p(Q[j][k])} %</title></circle>')
        out.append(f'<text x="{x(4) + 8:.1f}" y="{ys[k] + 4:.1f}" class="lab">{ETQ[k]} {p(Q[4][k])}</text>')
    out.append('</svg>')
    return ''.join(out)


g_q = figura('En Sevilla, el PSOE gana todas las secciones pobres y el PP todas las ricas',
             '% de voto en las elecciones generales de 2023 según la renta de la sección', quint(),
             'Fuente: Ministerio del Interior (generales de 2023, por sección censal) e INE (renta por unidad de consumo). Cada quintil reúne una quinta parte de las secciones de la ciudad, de la más pobre a la más rica.',
             [(ETQ[k], COLOR[ETQ[k]]) for k in P],
             (['Quintil', 'Renta mediana (€)', 'PP', 'PSOE', 'Sumar', 'Vox', 'Participación', 'Secciones', 'Ganadas por el PP', 'Ganadas por el PSOE'],
              [[f'{j + 1}.º', n(Q[j]['renta']), p(Q[j]['PP']), p(Q[j]['PSOE']), p(Q[j]['SUMAR']), p(Q[j]['VOX']), p(Q[j]['part']), str(Q[j]['n']),
                str(Q[j]['gana'].get('PP', 0)), str(Q[j]['gana'].get('PSOE', 0))] for j in range(5)]))

g_sube = figura('El PP subió 18,7 puntos en Nervión entre 2019 y 2023',
                '% de voto en las elecciones generales de noviembre de 2019 y de julio de 2023 en los distritos de Nervión y de Bellavista-La Palmera',
                barras([(f'{nom} · {ETQ[k]}', v, COLOR[ETQ[k]] if e == E else f'color-mix(in srgb, {COLOR[ETQ[k]]} 45%, var(--bg))', f'{"2023" if e == E else "2019"}: {p(v)} %')
                        for nom, s in (('Nervión', NE), ('Bellavista', BE))
                        for k in ('PP', 'PSOE', 'VOX') for e, v in ((E0, s[f'{k}0']), (E, s[k]))],
                       70, 'Voto en 2019 y 2023 en los distritos de los dos estadios', W=420, ml=130, separar=False),
                'Fuente: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por sección censal. Sumar no se compara: en 2019, Unidas Podemos y Más País fueron por separado.',
                [('2019', 'color-mix(in srgb, var(--pp) 45%, var(--bg))'), ('2023', 'var(--pp)')],
                (['Distrito', 'PP 2019', 'PP 2023', 'PSOE 2019', 'PSOE 2023', 'Vox 2019', 'Vox 2023'],
                 [[nom, p(s['PP0']), p(s['PP']), p(s['PSOE0']), p(s['PSOE']), p(s['VOX0']), p(s['VOX'])]
                  for nom, s in (('Nervión', NE), ('Bellavista-La Palmera', BE))]
                 + [['Sevilla (ciudad)', p(pc(E0, 'PP')), p(pc(E, 'PP')), p(pc(E0, 'PSOE')), p(pc(E, 'PSOE')), p(pc(E0, 'VOX')), p(pc(E, 'VOX'))]]))
assert round(NE['PP'] - NE['PP0'], 1) == 18.7

filas = [('Sánchez-Pizjuán (Nervión)', NE), ('Villamarín (Bellavista-La Palmera)', BE)]
GAN = lambda s: '<br>'.join(f'{ETQ[k]} {c}' for k, c in s['gana'].items()) + f'<br>de {s["n"]}'
METR = [('PP', lambda s: f'{p(s["PP"])} %'), ('PSOE', lambda s: f'{p(s["PSOE"])} %'), ('Vox', lambda s: f'{p(s["VOX"])} %'), ('Sumar', lambda s: f'{p(s["SUMAR"])} %'),
        ('Particip.', lambda s: f'{p(s["part"])} %'), ('Renta', lambda s: f'{n(s["renta"])} €'), ('Secciones', GAN)]
g_dos = ('<figure>\n<figcaption><span class="t">Dos estadios, dos distritos</span><span class="s">Elecciones generales de 2023 en el distrito de cada estadio</span></figcaption>\n'
         '<div class="tbl"><table style="font-size:.92rem"><thead><tr><th></th>' + ''.join(f'<th class="n">{t}</th>' for t, _ in filas) + '</tr></thead><tbody>'
         + ''.join(f'<tr><td>{nom}</td>' + ''.join(f'<td class="n" style="white-space:nowrap">{fn(s)}</td>' for _, s in filas) + '</tr>' for nom, fn in METR)
         + '</tbody></table></div>\n<div class="src">Fuente: Ministerio del Interior (por sección censal) e INE (renta por unidad de consumo, mediana de las secciones del distrito). Distritos según OpenStreetMap.</div>\n</figure>\n')

L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
MS = lambda b, t: f'<a href="{BASE}municipio/sevilla/sevilla/{b}/">{t}</a>'
CS = f'<a href="{BASE}municipio/sevilla/sevilla/">Sevilla</a>'
MORENO = 'https://www.esdiario.com/andalucia/261113/202835/moreno-pide-castigo-severo-sanchez-tambien-sevilla-ultimo-rincon-baila-psoe.html'
GOL = 'https://www.elgoldigital.com/futbol/sevilla-fc/blocus-nervion-plaza-derbi-sevilla-betis-21-noviembre/'
LALIGA = 'https://www.laliga.com/noticias/horarios-de-la-decimotercera-jornada-de-laliga-ea-sports-2026-27'

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Esta tarde, a las 18.30, el Sevilla recibe al Betis en el Ramón Sánchez-Pizjuán, en la jornada 13 de LaLiga, según el calendario de <a href="{LALIGA}">LaLiga</a> y <a href="{GOL}">El Gol Digital</a>. El estadio sevillista está en el barrio de {MS('nervion', 'Nervión')}, en el distrito del mismo nombre. El Benito Villamarín, el del Betis, está en Heliópolis, al sur, en el distrito de Bellavista-La Palmera. A ocho días de las elecciones generales del 29N, los dos estadios están en distritos donde el PP fue el más votado en 2023, en una ciudad donde el PSOE ganó en más secciones que el PP.</p>
<p data-tipo="dato">En las generales de julio de 2023, el PSOE fue primero en {GANA['PSOE']} de las {len(d)} secciones censales de {CS}; el PP, en {GANA['PP']}, y Sumar, en {GANA['SUMAR']}. En votos ganó el PP, con el {p(pc(E, 'PP'))} %, por delante del PSOE ({p(pc(E, 'PSOE'))} %), Sumar ({p(pc(E, 'SUMAR'))} %) y Vox ({p(pc(E, 'VOX'))} %). Es lo que contamos en {L('sevilla-barrio-a-barrio-29n', 'Sevilla, barrio a barrio')}: el PP gana por mucho en menos secciones, las del centro y las de más renta, y el PSOE, por menos en más secciones, las del norte y el este.</p>
<p data-tipo="dato">En el distrito de Nervión, el PP ganó en {NE['gana']['PP']} de las {NE['n']} secciones y sacó el {p(NE['PP'])} % de los votos, {p(NE['PP'] - pc(E, 'PP'))} puntos más que en el conjunto de la ciudad. El PSOE se quedó en el {p(NE['PSOE'])} %, Vox en el {p(NE['VOX'])} % y Sumar en el {p(NE['SUMAR'])} %. Votó el {p(NE['part'])} % del censo, y la renta mediana de sus secciones es de {n(NE['renta'])} € por unidad de consumo. Solo Los Remedios, al otro lado del río, votó más al PP: el {p(RE['PP'])} %.</p>
{g_dos}
<h2>Nervión: el PP, en todas menos cuatro</h2>
<p data-tipo="dato">En el barrio de {MS('nervion', 'Nervión')}, el del estadio, el PP ganó en {BN['gana']['PP']} de las {BN['n']} secciones, con el {p(BN['PP'])} %, y el PSOE sacó el {p(BN['PSOE'])} %. En el vecino {MS('la-buhaira', 'La Buhaira')}, el PP ganó las {BU['n']} secciones con el {p(BU['PP'])} %. En noviembre de 2019, el PP ya era el primero en el distrito, pero con el {p(NE['PP0'])} %: entre una elección y otra subió {p(NE['PP'] - NE['PP0'])} puntos, mientras Vox bajaba del {p(NE['VOX0'])} % al {p(NE['VOX'])} % y el PSOE se quedaba casi igual ({p(NE['PSOE0'])} % y {p(NE['PSOE'])} %).</p>
{g_sube}
<h2>El Villamarín, entre Heliópolis y Bellavista</h2>
<p data-tipo="dato">El distrito del Villamarín vota más repartido. En Bellavista-La Palmera, el PP ganó en {BE['gana']['PP']} de las {BE['n']} secciones y el PSOE, en {BE['gana']['PSOE']}. El PP sacó el {p(BE['PP'])} % y el PSOE, el {p(BE['PSOE'])} %; votó el {p(BE['part'])} %. En noviembre de 2019, el PSOE había sacado allí el {p(BE['PSOE0'])} % y el PP, el {p(BE['PP0'])} %: el distrito pasó de un empate casi exacto a una ventaja del PP de {p(BE['PP'] - BE['PSOE'])} puntos.</p>
<p data-tipo="dato">Dentro del distrito, los dos barrios que rodean el estadio votan casi al revés. Heliópolis, el del Villamarín, es una sola sección censal: el PP sacó el {p(BH['PP'])} %, Vox el {p(BH['VOX'])} % y el PSOE el {p(BH['PSOE'])} %, con una renta mediana de {n(BH['renta'])} €. En {MS('bellavista', 'Bellavista')}, al otro lado de la avenida, el PSOE ganó en {BB['gana']['PSOE']} de las {BB['n']} secciones con el {p(BB['PSOE'])} %, frente al {p(BB['PP'])} % del PP, y la renta mediana es de {n(BB['renta'])} €, menos de la mitad.</p>

<h2>La renta, de la grada al voto</h2>
<p data-tipo="patron">Si se ordenan las secciones de Sevilla por renta y se parten en cinco grupos iguales, el reparto es casi total. El PSOE ganó en las {Q[0]['gana']['PSOE']} secciones de la quinta parte más pobre, con el {p(Q[0]['PSOE'])} %, frente al {p(Q[0]['PP'])} % del PP. El PP ganó en las {Q[4]['gana']['PP']} de la quinta parte más rica, con el {p(Q[4]['PP'])} %, frente al {p(Q[4]['PSOE'])} % del PSOE. La participación va del {p(Q[0]['part'])} % al {p(Q[4]['part'])} %.</p>
{g_q}
<p data-tipo="patron">El distrito de Nervión, con una renta mediana de {n(NE['renta'])} €, está en la parte alta de esa escalera. Los distritos donde el PSOE ganó todas las secciones, Cerro-Amate ({CA['n']}) y Norte ({NO['n']}), están en la baja. En Cerro-Amate, el PSOE sacó el {p(CA['PSOE'])} % y votó el {p(CA['part'])} %, casi veinte puntos menos que en Nervión.</p>
{g_dist}

<h2>Sevilla, en campaña</h2>
<p data-tipo="contexto">Sevilla es la provincia donde el PSOE es más fuerte en Andalucía, y los dos grandes partidos arrancaron allí la campaña el 12 de noviembre. Pedro Sánchez dio su primer mitin en el palacio de congresos Fibes, como contamos en {L('arranque-campana-sevilla-badalona-colon-vallecas-29n', 'el arranque de la campaña')}. El mismo día, en la misma ciudad, el presidente de la Junta y del PP andaluz, Juanma Moreno, pidió el voto para Alberto Núñez Feijóo:</p>
<blockquote class="cita"><p>«¿Estáis dispuestos a soportar cuatro años más de sanchismo?»</p><footer>Juanma Moreno, presidente del PP andaluz, en el acto del PP en Sevilla del 12 de noviembre, según <a href="{MORENO}">ESdiario</a> (13-11-2026).</footer></blockquote>
<p data-tipo="dato">Nuestro modelo, que reparte por provincia la media de las encuestas nacionales, deja al PSOE primero en el 56 % de las simulaciones en la provincia de Sevilla, con un reparto central de 4 de los 12 escaños para el PSOE, 4 para el PP, 2 para Vox, 1 para Adelante Andalucía y 1 para Sumar, según la página de <a href="{BASE}encuestas/sevilla/">encuestas de Sevilla</a>, que se actualiza cada día.</p>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">Las cifras de sección son de las generales de 2023. Las encuestas del 29N no miden ciudades ni distritos, solo provincias, y nuestro modelo no estima el voto dentro de Sevilla. En 2019 no comparamos a Sumar ni contamos secciones ganadas, porque Unidas Podemos y Más País fueron por separado. Los quintiles comparan secciones de la misma ciudad: describen dónde se vota qué, no el efecto de la renta. {SINB} secciones no tienen barrio asignado en nuestro mapa y solo cuentan en los totales.</p>
<p data-tipo="hipotesis">Y el fútbol no vota. La afición del Sevilla y la del Betis vienen de toda la ciudad y de toda la provincia, y nada de esto dice cómo vota cada una. Lo que sí muestra el mapa es que el derbi se juega en dos distritos donde el PP fue el más votado, en una ciudad que el PSOE gana en secciones. Las calles de cada sección están en {L('sevilla-barrio-a-barrio-29n', 'Sevilla, barrio a barrio')} y en {L('como-voto-tu-calle', 'cómo votó tu calle')}.</p>
'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en la ciudad de Sevilla?', f'El PP en votos, con el {p(pc(E, "PP"))} %, por delante del PSOE ({p(pc(E, "PSOE"))} %). Pero el PSOE fue primero en más secciones censales: {GANA["PSOE"]} de {len(d)}, frente a {GANA["PP"]} del PP.'),
    ('¿Cómo vota Nervión, el barrio del Sánchez-Pizjuán?', f'En las generales de 2023, el PP ganó en {NE["gana"]["PP"]} de las {NE["n"]} secciones del distrito de Nervión, con el {p(NE["PP"])} % de los votos.'),
    ('¿Cómo vota el distrito del Benito Villamarín?', f'En Bellavista-La Palmera, el PP ganó en {BE["gana"]["PP"]} de las {BE["n"]} secciones y el PSOE en {BE["gana"]["PSOE"]}; el PP sacó el {p(BE["PP"])} % y el PSOE, el {p(BE["PSOE"])} %.'),
]
enlaces = (f'<a href="{BASE}municipio/sevilla/sevilla/">Elecciones en Sevilla</a> · <a href="{BASE}encuestas/sevilla/">Encuesta de Sevilla</a> · '
           f'{L("sevilla-barrio-a-barrio-29n", "Sevilla, barrio a barrio")} · {L("arranque-campana-sevilla-badalona-colon-vallecas-29n", "El arranque de la campaña")} · '
           f'{L("valencia-madrid-mestalla-barrios-29n", "Mestalla y el Bernabéu en las urnas")} · {L("derbi-vasco-bilbao-donostia-29n", "El derbi vasco en las urnas")}')
foot = 'Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por municipio y sección censal; INE, renta por unidad de consumo por sección (Atlas de Distribución de Renta de los Hogares); barrios y distritos de OpenStreetMap; modelo de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/derbi_sevilla.py.'

TIT = f'El derbi sevillano se juega en barrios del PP: en Nervión, el del Sánchez-Pizjuán, ganó en {NE["gana"]["PP"]} de {NE["n"]} secciones; en la ciudad, el PSOE fue primero en {GANA["PSOE"]} de {len(d)}'
DEK = (f'El día del Sevilla-Betis, Sevilla sección a sección en las elecciones generales de 2023. En el distrito del Villamarín, el PP ganó en {BE["gana"]["PP"]} de {BE["n"]} secciones; '
       f'en la quinta parte más pobre de la ciudad, el PSOE ganó en todas.')
r1 = lambda x: round(float(x), 4)


def plano(s):
    return {**{k: r1(s[k]) for k in P + ['PP0', 'PSOE0', 'VOX0']}, 'part': r1(s['part']), 'renta': r1(s['renta']), 'n': int(s['n']), 'gana': s['gana']}


DATOS = {'CIU': {e: {k: r1(pc(e, k)) for k in P} for e in (E, E0)}, 'DIST': {NOMD(k): plano(s) for k, s in D.items()},
         'BARR': {k: plano(B[k]) for k in ('Nervión', 'Heliópolis', 'Bellavista', 'La Buhaira')},
         'Q': {str(q): plano(s) for q, s in Q.items()}, 'NSEC': len(d), 'GANA': GANA, 'SINBARRIO': SINB,
         'MODELO': {'psoe_primero': 56, 'PSOE': 4, 'PP': 4, 'VOX': 2, 'AA': 1, 'SUMAR': 1, 'escanos': 12}}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
if __name__ == '__main__':
    print(TIT)
    print(DEK)
    pieza('derbi-sevillano-nervion-heliopolis-29n', 'Sevilla-Betis en las urnas', TIT, DEK, '21 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, datos_js)
