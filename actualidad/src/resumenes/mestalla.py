"""«Mestalla y el Bernabéu en las urnas» (pieza de sábado, 7-11-2026, día del Valencia-Real Madrid).

Cifras: secciones (generales-2026/descargas/secciones.csv, con la renta por unidad de consumo del INE) de las generales de
noviembre de 2019 y julio de 2023; barrios y distritos de data/barrios/secciones_barrio.csv; municipios de
generales-2026/data/municipios.json. Sumar solo se usa en 2023: en 2019 la familia SUMAR del fichero suma listas distintas
(Unidas Podemos y Más País-Compromís), así que no se compara. Quintiles de renta dentro de la ciudad, sin regresión.
Uso, desde la raíz: python3 actualidad/src/resumenes/mestalla.py
"""
import json

import pandas as pd

from comun import BASE, COLOR, RAIZ, barras, esc, figura, n, pieza

A = BASE + 'actualidad/'
VLC, MAD = '46250', '28079'
E, E0 = '2023_07', '2019_11'
P = ['PP', 'PSOE', 'SUMAR', 'VOX']
ETQ = {'PP': 'PP', 'PSOE': 'PSOE', 'SUMAR': 'Sumar', 'VOX': 'Vox'}
p = lambda v: n(v, 1)

# --- La ciudad ---
m = json.load(open(RAIZ / 'generales-2026/data/municipios.json'))
i = m['cod'].index(VLC)
pc = lambda e, k: m[f'{e}_{k}'][i] * 100
assert [round(pc(E, k), 1) for k in P] == [36.5, 29.5, 17.7, 14.1]
assert [round(pc(E0, k), 1) for k in ('PP', 'PSOE', 'VOX')] == [24.4, 24.8, 16.8]

# --- Secciones ---
d = pd.read_csv(RAIZ / 'generales-2026/descargas/secciones.csv', dtype={'tract_code': str, 'mun_code': str})
d = d[d.mun_code.isin([VLC, MAD])].dropna(subset=[f'{E}_PP']).copy()
bar = pd.read_csv(RAIZ / 'data/barrios/secciones_barrio.csv', dtype=str)[['tract_code', 'barrio', 'distrito']]
d = d.merge(bar, on='tract_code', how='left')
d['gana'] = d[[f'{E}_{k}' for k in P]].idxmax(axis=1).str[8:]
v = d[d.mun_code == VLC]
mad = d[d.mun_code == MAD]
assert len(v) == 591 and v.gana.value_counts().to_dict() == {'PP': 335, 'PSOE': 241, 'SUMAR': 15}
assert v.barrio.isna().sum() == 18


def cuota(s, k, e=E):
    return (s[f'{e}_{k}'] * s[f'{e}_votantes']).sum() / s[f'{e}_votantes'].sum() * 100


def part(s, e=E):
    return s[f'{e}_votantes'].sum() / s[f'{e}_censo'].sum() * 100


def resumen(s):
    return {**{k: cuota(s, k) for k in P}, 'part': part(s), 'renta': s.renta_uc.median(), 'n': len(s),
            'gana': s.gana.value_counts().to_dict()}


D = {k: resumen(s) for k, s in v.groupby('distrito')}
PLA, BEN, MAR = D['el Pla del Real'], D['Benicalap'], D['Poblats Marítims']
assert PLA['n'] == 23 and PLA['gana'] == {'PP': 23} and round(PLA['PP'], 1) == 55.4 and round(PLA['part'], 1) == 84.0
assert round(PLA['PSOE'], 1) == 16.2 and round(PLA['VOX'], 1) == 16.4 and round(PLA['SUMAR'], 1) == 10.3 and PLA['renta'] == 34619
assert max(D, key=lambda k: D[k]['part']) == 'el Pla del Real' and max(D, key=lambda k: D[k]['PP']) == 'el Pla del Real'
assert max(D, key=lambda k: D[k]['renta']) == 'el Pla del Real'
assert BEN['n'] == 30 and BEN['gana'] == {'PSOE': 24, 'PP': 6} and round(BEN['PSOE'], 1) == 35.0 and round(BEN['PP'], 1) == 31.8
assert round(BEN['part'], 1) == 72.3 and round(BEN['renta']) == 18032
assert MAR['n'] == 42 and MAR['gana'] == {'PSOE': 38, 'PP': 4} and round(MAR['PSOE'], 1) == 35.2 and round(MAR['part'], 1) == 70.9
assert min(D, key=lambda k: D[k]['part']) == 'Poblats Marítims'

B = {k: resumen(s) for k, s in v.groupby('barrio')}
assert B['Mestalla']['n'] == 10 and round(B['Mestalla']['PP'], 1) == 49.9 and round(B['Mestalla']['part'], 1) == 82.5
assert round(B['el Pla del Remei']['PP'], 1) == 64.5 and round(B['el Pla del Remei']['PSOE'], 1) == 8.5
assert round(B['els Orriols']['PSOE'], 1) == 37.8 and round(B['els Orriols']['part'], 1) == 65.4
assert round(B['el Carme']['SUMAR'], 1) == 31.7
assert B['Benicalap']['gana'] == {'PSOE': 21, 'PP': 6} and round(B['Benicalap']['PSOE'], 1) == 34.7 and round(B['Benicalap']['PP'], 1) == 32.3
SUMB = v[v.gana == 'SUMAR'].barrio.value_counts().to_dict()
assert SUMB == {'Russafa': 5, 'Benimaclet': 4, 'el Carme': 3, 'el Pilar': 1, 'el Mercat': 1, 'el Botànic': 1}

# 2019-2023 en las secciones comparables
c = v.dropna(subset=[f'{E0}_PP'])
N2 = len(c)
SUBE_PP = int((c[f'{E}_PP'] > c[f'{E0}_PP']).sum())
SUBE_PSOE = int((c[f'{E}_PSOE'] > c[f'{E0}_PSOE']).sum())
assert N2 == 585 and SUBE_PP == 585 and SUBE_PSOE == 561
PLA0 = v[v.distrito == 'el Pla del Real']
assert round(cuota(PLA0, 'PP', E0), 1) == 40.2 and round(cuota(PLA0, 'VOX', E0), 1) == 20.1

# Quintiles de renta
g = v.dropna(subset=['renta_uc']).copy()
g['q'] = pd.qcut(g.renta_uc.rank(method='first'), 5, labels=False)
Q = {q: resumen(s) for q, s in g.groupby('q')}
assert round(Q[0]['PSOE'], 1) == 37.5 and round(Q[0]['PP'], 1) == 28.0 and round(Q[4]['PP'], 1) == 49.6 and round(Q[4]['PSOE'], 1) == 19.5
assert round(Q[0]['part'], 1) == 66.5 and round(Q[4]['part'], 1) == 83.1

# Madrid: Chamartín, el distrito del Bernabéu
CH = resumen(mad[mad.distrito == 'Chamartín'])
assert CH['n'] == 101 and CH['gana'] == {'PP': 100, 'PSOE': 1} and round(CH['PP'], 1) == 59.0 and round(CH['part'], 1) == 81.0
assert round(CH['PSOE'], 1) == 15.4 and round(CH['VOX'], 1) == 15.3 and CH['renta'] == 42089
MADC = {k: cuota(mad, k) for k in P}
assert round(MADC['PP'], 1) == 41.8 and round(MADC['PSOE'], 1) == 27.4

# --- Gráficos ---
NOMD = {'el Pla del Real': 'El Pla del Real', "l'Eixample": "L'Eixample", 'la Saïdia': 'La Saïdia', "l'Olivereta": "L'Olivereta"}
orden = sorted(D, key=lambda k: -D[k]['PP'])
FUENTE = 'Fuente: Ministerio del Interior (generales del 23 de julio de 2023, por sección censal) e INE (renta por unidad de consumo). Distritos de València según OpenStreetMap; 18 secciones sin distrito asignado solo cuentan en el total de la ciudad.'
g_dist = figura('El PP, más fuerte en el distrito de Mestalla',
                '% de voto al PP en las generales de 2023 en cada distrito de València',
                barras([(NOMD.get(k, k), D[k]['PP'], 'var(--pp)' if k == 'el Pla del Real' else 'color-mix(in srgb, var(--pp) 55%, var(--bg))', f"{p(D[k]['PP'])} %") for k in orden],
                       60, 'Voto al PP por distrito de València', ml=150, linea=(pc(E, 'PP'), f"Ciudad: {p(pc(E, 'PP'))} %"), separar=True),
                FUENTE, None,
                (['Distrito', 'PP', 'PSOE', 'Sumar', 'Vox', 'Participación', 'Renta mediana (€)', 'Secciones'],
                 [[NOMD.get(k, k), p(D[k]['PP']), p(D[k]['PSOE']), p(D[k]['SUMAR']), p(D[k]['VOX']), p(D[k]['part']), n(D[k]['renta']), str(D[k]['n'])] for k in orden]))


def quint(W=640, H=250, ml=40, mr=105, mt=12, mb=34):
    x = lambda j: ml + j * (W - ml - mr) / 4
    y = lambda val: mt + (60 - val) / 60 * (H - mt - mb)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Voto por quintil de renta en València">']
    for val in (0, 15, 30, 45, 60):
        out.append(f'<line x1="{ml}" x2="{W - mr}" y1="{y(val):.1f}" y2="{y(val):.1f}" stroke="var(--grid)"/><text x="{ml - 6}" y="{y(val) + 4:.1f}" text-anchor="end">{val} %</text>')
    for j, t in enumerate(['Más pobre', '2.º', '3.º', '4.º', 'Más rico']):
        out.append(f'<text x="{x(j):.1f}" y="{H - 10}" text-anchor="middle">{t}</text>')
    ys, prev = {}, None   # etiquetas finales separadas al menos 15 px
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


g_q = figura('En València, el PSOE gana en los barrios pobres y el PP en los ricos',
             '% de voto en las generales de 2023 según la renta de la sección', quint(),
             'Fuente: Ministerio del Interior (generales de 2023, por sección censal) e INE (renta por unidad de consumo). Cada quintil reúne una quinta parte de las secciones de la ciudad, de la más pobre a la más rica.',
             [(ETQ[k], COLOR[ETQ[k]]) for k in P],
             (['Quintil', 'Renta mediana (€)', 'PP', 'PSOE', 'Sumar', 'Vox', 'Participación'],
              [[f'{j + 1}.º', n(Q[j]['renta']), p(Q[j]['PP']), p(Q[j]['PSOE']), p(Q[j]['SUMAR']), p(Q[j]['VOX']), p(Q[j]['part'])] for j in range(5)]))

filas = [('Mestalla', PLA), ('Bernabéu', CH), ('Nou Mestalla', BEN)]
GAN = lambda s: '<br>'.join(f'{ETQ[k]} {c}' for k, c in s['gana'].items()) + f'<br>de {s["n"]}'
METR = [('PP', lambda s: f'{p(s["PP"])} %'), ('PSOE', lambda s: f'{p(s["PSOE"])} %'), ('Vox', lambda s: f'{p(s["VOX"])} %'), ('Sumar', lambda s: f'{p(s["SUMAR"])} %'),
        ('Particip.', lambda s: f'{p(s["part"])} %'), ('Renta', lambda s: f'{n(s["renta"])} €'), ('Secciones', GAN)]
g_tres = ('<figure>\n<figcaption><span class="t">Tres estadios, tres distritos</span><span class="s">Generales de 2023 en el distrito de cada estadio: El Pla del Real (Mestalla), Chamartín (Bernabéu) y Benicalap (Nou Mestalla)</span></figcaption>\n'
          '<div class="tbl"><table style="font-size:.92rem"><thead><tr><th></th>' + ''.join(f'<th class="n">{t}</th>' for t, _ in filas) + '</tr></thead><tbody>'
          + ''.join(f'<tr><td>{nom}</td>' + ''.join(f'<td class="n" style="white-space:nowrap">{fn(s)}</td>' for _, s in filas) + '</tr>' for nom, fn in METR)
          + '</tbody></table></div>\n<div class="src">Fuente: Ministerio del Interior (por sección censal) e INE (renta por unidad de consumo, mediana de las secciones del distrito). Distritos según OpenStreetMap.</div>\n</figure>\n')

L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
MV = lambda b, t: f'<a href="{BASE}municipio/valencia/valencia/{b}/">{t}</a>'
CV = f'<a href="{BASE}municipio/valencia/valencia/">València</a>'

ABALOS = 'https://www.elidealgallego.com/actualidad/espana/2026-11-06/abalos-subraya-la-coincidencia-entre-el-registro-en-su-casa-y-las-declaraciones-de-koldo-889554.html'
BENI = 'https://www.eldiario.es/comunitat-valenciana/valencia/vecinos-benicalap-rechazan-torres-nou-mestalla-operacion-especulativa-empeorara-problemas-barrio_1_13315256.html'
DEBATE = 'https://www.eldebate.com/espana/comunidad-valenciana/20261010/psoe-presenta-elecciones-abalos-listas-primera-vez-27-anos_467367.html'

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Esta noche, a las nueve, el Valencia recibe al Real Madrid en Mestalla. El estadio está en el barrio de {MV('mestalla', 'Mestalla')}, en el distrito de El Pla del Real. El Santiago Bernabéu está en el distrito madrileño de Chamartín. Son dos estadios de dos ciudades distintas, pero sus distritos votan casi igual: en las generales de julio de 2023, el PP ganó en las {PLA['n']} secciones censales de El Pla del Real y en {CH['gana']['PP']} de las {CH['n']} de Chamartín.</p>
<p data-tipo="dato">En El Pla del Real, el PP sacó el {p(PLA['PP'])} % de los votos, casi veinte puntos más que en el conjunto de {CV} ({p(pc(E, 'PP'))} %). Detrás quedaron Vox ({p(PLA['VOX'])} %), el PSOE ({p(PLA['PSOE'])} %) y Sumar ({p(PLA['SUMAR'])} %). Es el distrito de la ciudad donde más se votó, el {p(PLA['part'])} %, y el de más renta, con una mediana de {n(PLA['renta'])} € por unidad de consumo. En Chamartín, el PP sacó el {p(CH['PP'])} %, con una participación del {p(CH['part'])} % y una renta mediana de {n(CH['renta'])} €.</p>
{g_tres}
<h2>La ciudad: el PP subió en todas las secciones</h2>
<p data-tipo="dato">En el conjunto de València, el PP fue primero en 2023 con el {p(pc(E, 'PP'))} %, por delante del PSOE ({p(pc(E, 'PSOE'))} %), Sumar ({p(pc(E, 'SUMAR'))} %) y Vox ({p(pc(E, 'VOX'))} %). En noviembre de 2019 había ganado el PSOE, con el {p(pc(E0, 'PSOE'))} % frente al {p(pc(E0, 'PP'))} % del PP. De las {N2} secciones que se pueden comparar entre las dos elecciones, el PP subió en las {SUBE_PP} y el PSOE en {SUBE_PSOE}. El PP ganó en {v.gana.value_counts()['PP']} de las {len(v)} secciones de la ciudad; el PSOE, en {v.gana.value_counts()['PSOE']}, y Sumar, en {v.gana.value_counts()['SUMAR']}.</p>
<p data-tipo="patron">El mapa de distritos ordena el voto de forma muy clara. El PP saca más de la mitad en El Pla del Real y se queda cerca de ella en L'Eixample ({p(D["l'Eixample"]['PP'])} %), los dos distritos de más renta. En el otro extremo, en los Poblats Marítims, junto al mar, el PSOE ganó en {MAR['gana']['PSOE']} de las {MAR['n']} secciones, con el {p(MAR['PSOE'])} %, y se votó menos que en ningún otro distrito: el {p(MAR['part'])} %.</p>
{g_dist}
<p data-tipo="dato">Dentro de El Pla del Real, el barrio de {MV('mestalla', 'Mestalla')} es el menos conservador: el PP sacó el {p(B['Mestalla']['PP'])} % y el PSOE, el {p(B['Mestalla']['PSOE'])} %. En el vecino {MV('exposicio', 'Exposició')}, el PP llegó al {p(B['Exposició']['PP'])} %. El máximo de la ciudad está en {MV('el-pla-del-remei', 'el Pla del Remei')}, en L'Eixample: el PP sacó el {p(B['el Pla del Remei']['PP'])} % y el PSOE, el {p(B['el Pla del Remei']['PSOE'])} %. En {MV('els-orriols', 'els Orriols')}, al norte, el PSOE sacó el {p(B['els Orriols']['PSOE'])} % y votó el {p(B['els Orriols']['part'])} %.</p>
<p data-tipo="dato">Sumar, la lista en la que iba Compromís, solo fue primera en {v.gana.value_counts()['SUMAR']} secciones, todas en barrios del centro y de la primera corona: {SUMB['Russafa']} en {MV('russafa', 'Russafa')}, {SUMB['Benimaclet']} en {MV('benimaclet', 'Benimaclet')}, {SUMB['el Carme']} en {MV('el-carme', 'el Carme')}, y una en el Pilar, el Mercat y el Botànic. En el Carme sacó el {p(B['el Carme']['SUMAR'])} %.</p>

<h2>La renta, de la grada al voto</h2>
<p data-tipo="patron">Si se ordenan las secciones de la ciudad por renta y se parten en cinco grupos iguales, el voto sube y baja como una escalera. En la quinta parte más pobre, el PSOE sacó el {p(Q[0]['PSOE'])} % y el PP, el {p(Q[0]['PP'])} %. En la quinta parte más rica, el PP sacó el {p(Q[4]['PP'])} % y el PSOE, el {p(Q[4]['PSOE'])} %. La participación va del {p(Q[0]['part'])} % al {p(Q[4]['part'])} %.</p>
{g_q}

<h2>El Nou Mestalla, en un distrito donde gana el PSOE</h2>
<p data-tipo="contexto">El Valencia lleva casi veinte años construyendo su nuevo estadio, el Nou Mestalla, en Benicalap, al noroeste de la ciudad. En junio, elDiario.es contaba que, si no había contratiempos, empezaría a acoger partidos en agosto de 2027, y recogía las quejas de la asociación de vecinos por las torres de apartamentos turísticos previstas junto al estadio:</p>
<blockquote class="cita"><p>«No es una operación pensada para mejorar un barrio en su conjunto, sino para financiar una operación urbanística»</p><footer>José Antonio Caballero, vicepresidente y portavoz de la asociación de vecinos de Benicalap, en <a href="{BENI}">elDiario.es</a> (19 de junio de 2026).</footer></blockquote>
<p data-tipo="dato">Benicalap vota casi al revés que El Pla del Real. En las generales de 2023, el PSOE ganó en {BEN['gana']['PSOE']} de las {BEN['n']} secciones del distrito, con el {p(BEN['PSOE'])} %, por delante del PP ({p(BEN['PP'])} %). Votó el {p(BEN['part'])} %, casi doce puntos menos que en El Pla del Real, y la renta mediana es de {n(BEN['renta'])} €, poco más de la mitad. En el barrio de {MV('benicalap', 'Benicalap')}, el PSOE ganó en {B['Benicalap']['gana']['PSOE']} de sus {B['Benicalap']['n']} secciones.</p>
<p data-tipo="hipotesis">Cuando el Valencia se mude, su estadio pasará de un distrito donde el PP gana en todas las secciones a uno donde el PSOE gana en cuatro de cada cinco. No dice nada de cómo vota la afición, que viene de toda la ciudad y de fuera de ella: es solo el voto de los vecinos que viven alrededor.</p>

<h2>La semana del registro a Ábalos</h2>
<p data-tipo="contexto">El partido llega dos días después de que la UCO registrara la casa del exministro José Luis Ábalos en València, como contamos en {L('psoe-valencia-abalos-municipios-29n', 'el voto del PSOE en la provincia')}. Ábalos, que está en prisión, respondió el viernes en la red social X, según la agencia EFE:</p>
<blockquote class="cita"><p>«No voy a atribuir intenciones que desconozco, pero tampoco voy a fingir que no llama poderosamente la atención»</p><footer>José Luis Ábalos, el 6 de noviembre, sobre la coincidencia del registro con las declaraciones de Koldo García. Recogido por EFE en <a href="{ABALOS}">El Ideal Gallego</a>.</footer></blockquote>
<p data-tipo="contexto">Es la primera vez desde 1999 que el PSOE se presenta a unas elecciones sin Ábalos en sus listas, según <a href="{DEBATE}">El Debate</a>. En 2023 fue el número dos de la lista por Valencia, detrás de Diana Morant.</p>
<p data-tipo="dato">Nuestro modelo, que reparte por provincia la media de las encuestas nacionales, da al PP 5 de los 16 escaños de la provincia de Valencia, al PSOE otros 5, a Vox 4 y a Sumar 2. El PP queda primero en el 67 % de las simulaciones y el PSOE en el 27 %. Las cifras, que se actualizan cada día, están en la página de <a href="{BASE}encuestas/valencia/">encuestas de Valencia</a>.</p>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">Las cifras de sección son de las generales de 2023. Las encuestas del 29N no miden ciudades ni distritos, solo provincias, y nuestro modelo no estima el voto dentro de València. En 2019 no comparamos a Sumar, porque Unidas Podemos y Más País-Compromís fueron por separado. Los quintiles comparan secciones de la misma ciudad: describen dónde se vota qué, no el efecto de la renta. En València, {int(v.barrio.isna().sum())} secciones no tienen barrio asignado en nuestro mapa y solo cuentan en los totales.</p>
<p data-tipo="contexto">Y el fútbol no vota. Esta noche, en Mestalla, se juega otra cosa. Pero el estadio está en el distrito más rico y con más participación de la ciudad, donde el PP sacó el {p(PLA['PP'])} %, igual que el Bernabéu en el suyo. Las calles de cada sección están en {L('valencia-barrio-a-barrio-29n', 'València, barrio a barrio')} y en {L('como-voto-tu-calle', 'cómo votó tu calle')}.</p>
'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en la ciudad de València?', f'El PP, con el {p(pc(E, "PP"))} % de los votos, por delante del PSOE ({p(pc(E, "PSOE"))} %), Sumar ({p(pc(E, "SUMAR"))} %) y Vox ({p(pc(E, "VOX"))} %).'),
    ('¿Cómo vota el barrio de Mestalla?', f'En las generales de 2023, el PP sacó el {p(B["Mestalla"]["PP"])} % en el barrio de Mestalla y el {p(PLA["PP"])} % en su distrito, El Pla del Real, donde ganó en las {PLA["n"]} secciones censales.'),
    ('¿Dónde gana el PSOE en València?', f'En los distritos de menos renta del norte y del mar: en los Poblats Marítims ganó en {MAR["gana"]["PSOE"]} de las {MAR["n"]} secciones y en Benicalap, donde se construye el Nou Mestalla, en {BEN["gana"]["PSOE"]} de {BEN["n"]}.'),
]
enlaces = (f'<a href="{BASE}municipio/valencia/valencia/">Elecciones en València</a> · <a href="{BASE}encuestas/valencia/">Encuesta de Valencia</a> · '
           f'{L("valencia-barrio-a-barrio-29n", "València, barrio a barrio")} · {L("psoe-valencia-abalos-municipios-29n", "El PSOE de Valencia tras el registro a Ábalos")} · '
           f'{L("derbi-vasco-bilbao-donostia-29n", "El derbi vasco en las urnas")} · {L("barcelona-madrid-clasico-del-voto-29n", "El otro Clásico")}')
foot = 'Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por municipio y sección censal; INE, renta por unidad de consumo por sección (Atlas de Distribución de Renta de los Hogares); barrios y distritos de OpenStreetMap; modelo de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mestalla.py.'

TIT = f'Mestalla vota como el Bernabéu: el PP ganó en las {PLA["n"]} secciones del distrito del Valencia y en {CH["gana"]["PP"]} de las {CH["n"]} del Real Madrid'
DEK = f'El día del Valencia-Real Madrid, València sección a sección. En El Pla del Real, el distrito de Mestalla, el PP sacó el {p(PLA["PP"])} % en 2023; en Benicalap, donde se construye el Nou Mestalla, el PSOE ganó en {BEN["gana"]["PSOE"]} de {BEN["n"]} secciones.'
if __name__ == '__main__':
    print(TIT)
    print(DEK)
    pieza('valencia-madrid-mestalla-barrios-29n', 'Mestalla y el Bernabéu en las urnas', TIT, DEK, '7 de noviembre de 2026', cuerpo, preguntas, enlaces, foot)
