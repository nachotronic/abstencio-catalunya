"""«Del Calderón al Metropolitano» (pieza de domingo, 8-11-2026, día del Atlético-Barça en el Metropolitano).

Cifras: secciones (generales-2026/descargas/secciones.csv, con la renta por unidad de consumo del INE) de las generales de
2004 a 2023; barrios y distritos de data/barrios/secciones_barrio.csv. La renta del INE por sección tiene un tope (58.752 €):
no se cita la mediana de barrios que lo alcanzan. Descripción, sin regresión.
Uso, desde la raíz: python3 actualidad/src/resumenes/atletico.py
"""
import pandas as pd

from comun import BASE, COLOR, esc, figura, n, pieza, RAIZ

A = BASE + 'actualidad/'
MAD, BCN = '28079', '08019'
E = '2023_07'
NUEVAS = ['2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
FECHA = {'2004_03': '2004', '2008_03': '2008', '2011_11': '2011', '2015_12': '2015', '2016_06': '2016', '2019_04': 'abr. 2019', '2019_11': 'nov. 2019', '2023_07': '2023'}
P = ['PP', 'PSOE', 'SUMAR', 'VOX', 'ERC', 'JUNTS']
p = lambda v: n(v, 1)

d = pd.read_csv(RAIZ / 'generales-2026/descargas/secciones.csv', dtype={'tract_code': str, 'mun_code': str})
d = d[d.mun_code.isin([MAD, BCN])].copy()
bar = pd.read_csv(RAIZ / 'data/barrios/secciones_barrio.csv', dtype=str)[['tract_code', 'barrio', 'distrito']]
d = d.merge(bar, on='tract_code', how='left')
v = d.dropna(subset=[f'{E}_PP']).copy()
v['gana'] = v[[f'{E}_{k}' for k in P]].idxmax(axis=1).str[8:].where(v[f'{E}_gana'] != 'EMPATE', 'EMPATE')   # empate a votos: no gana nadie
assert v.renta_uc.max() == 58752


def cuota(s, k, e=E):
    s = s.dropna(subset=[f'{e}_PP'])
    return (s[f'{e}_{k}'] * s[f'{e}_votantes']).sum() / s[f'{e}_votantes'].sum() * 100


def part(s, e=E):
    s = s.dropna(subset=[f'{e}_PP'])
    return s[f'{e}_votantes'].sum() / s[f'{e}_censo'].sum() * 100


def res(s):
    return {**{k: cuota(s, k) for k in P}, 'part': part(s), 'renta': s.renta_uc.median(), 'n': len(s), 'gana': s.gana.value_counts().to_dict()}


mad, bcn = v[v.mun_code == MAD], v[v.mun_code == BCN]
DM = {k: res(s) for k, s in mad.groupby('distrito')}
ARG, SB, CH = DM['Arganzuela'], DM['San Blas - Canillejas'], DM['Chamartín']
assert ARG['n'] == 111 and ARG['gana'] == {'PP': 96, 'PSOE': 8, 'SUMAR': 5, 'EMPATE': 2} and round(ARG['PP'], 1) == 38.4 and round(ARG['part'], 1) == 78.4 and ARG['renta'] == 31378
assert SB['n'] == 112 and SB['gana'] == {'PSOE': 57, 'PP': 55} and round(SB['PP'], 1) == 37.9 and round(SB['PSOE'], 1) == 30.9 and round(SB['part'], 1) == 71.2 and SB['renta'] == 21376.5
assert round(ARG['SUMAR'], 1) == 22.9 and round(SB['VOX'], 1) == 11.9
REN = (1 - SB['renta'] / ARG['renta']) * 100
assert 31 < REN < 33   # «casi un tercio menos»
# San Blas-Canillejas, en el puesto de renta y participación entre los 21 distritos
ord_renta = sorted(DM, key=lambda k: DM[k]['renta'])
assert ord_renta.index('San Blas - Canillejas') == 6 and ord_renta.index('Arganzuela') == 13   # 7.º y 14.º de 21, de menos a más renta
MADC = res(mad)
assert round(MADC['PP'], 1) == 41.8 and round(MADC['part'], 1) == 73.4

BM = {k: res(s) for k, s in mad.groupby('barrio')}
IMP, ROS = BM['Imperial'], BM['Rosas']
assert IMP['n'] == 17 and IMP['gana'] == {'PP': 17} and round(IMP['PP'], 1) == 40.5 and round(IMP['part'], 1) == 80.0 and IMP['renta'] == 32591
assert ROS['n'] == 17 and ROS['gana'] == {'PP': 16, 'PSOE': 1} and round(ROS['PP'], 1) == 39.3 and round(ROS['PSOE'], 1) == 29.7 and round(ROS['part'], 1) == 79.3 and ROS['renta'] == 29392
AMP = BM['Amposta']
assert round(AMP['PSOE'], 1) == 40.0 and round(AMP['part'], 1) == 57.8 and AMP['renta'] == 14447

# Serie de los dos distritos
SER = {dist: {e: {'PP': cuota(d[d.distrito == dist], 'PP', e), 'PSOE': cuota(d[d.distrito == dist], 'PSOE', e), 'part': part(d[d.distrito == dist], e)} for e in NUEVAS}
       for dist in ('Arganzuela', 'San Blas - Canillejas')}
assert round(SER['San Blas - Canillejas']['2004_03']['PSOE'], 1) == 50.1 and round(SER['Arganzuela']['2004_03']['PP'], 1) == 49.2
assert round(SER['San Blas - Canillejas']['2019_11']['PSOE'], 1) == 30.3 and round(SER['San Blas - Canillejas']['2019_11']['PP'], 1) == 22.0
assert round(SER['Arganzuela']['2019_11']['PSOE'], 1) == 25.5 and round(SER['Arganzuela']['2019_11']['PP'], 1) == 24.9
GAN = {dist: {e: max(('PP', 'PSOE'), key=lambda k: SER[dist][e][k]) for e in NUEVAS} for dist in SER}
assert [GAN['Arganzuela'][e] for e in NUEVAS] == ['PP', 'PP', 'PP', 'PP', 'PP', 'PSOE', 'PSOE', 'PP']
assert [GAN['San Blas - Canillejas'][e] for e in NUEVAS] == ['PSOE', 'PSOE', 'PP', 'PP', 'PP', 'PSOE', 'PSOE', 'PP']

# Barcelona: les Corts
DB = {k: res(s) for k, s in bcn.groupby('distrito')}
LC = DB['les Corts']
assert LC['n'] == 57 and LC['gana'] == {'PSOE': 42, 'PP': 15} and round(LC['PSOE'], 1) == 28.0 and round(LC['PP'], 1) == 23.7 and round(LC['JUNTS'], 1) == 14.2
assert round(LC['ERC'], 1) == 11.6 and round(LC['part'], 1) == 72.4 and LC['renta'] == 35482
assert sorted(DB, key=lambda k: -DB[k]['PP'])[:2] == ['Sarrià - Sant Gervasi', 'les Corts']
BB = {k: res(s) for k, s in bcn.groupby('barrio')}
MAT, PED = BB['la Maternitat i Sant Ramon'], BB['Pedralbes']
assert MAT['n'] == 15 and MAT['gana'] == {'PSOE': 12, 'PP': 3} and round(MAT['PSOE'], 1) == 30.8 and round(MAT['PP'], 1) == 20.8
assert PED['n'] == 7 and PED['gana'] == {'PP': 7} and round(PED['PP'], 1) == 43.5
BCNC = res(bcn)
assert round(BCNC['PP'], 1) == 15.9 and round(BCNC['PSOE'], 1) == 33.2 and round(BCNC['part'], 1) == 67.4


# --- Gráficos ---
def lineas(W=640, H=260, ml=40, mr=150, mt=12, mb=34):
    x = lambda j: ml + j * (W - ml - mr) / (len(NUEVAS) - 1)
    y = lambda val: mt + (60 - val) / 60 * (H - mt - mb)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Voto al PP y al PSOE en Arganzuela y San Blas-Canillejas, 2004-2023">']
    for val in (0, 20, 40, 60):
        out.append(f'<line x1="{ml}" x2="{W - mr}" y1="{y(val):.1f}" y2="{y(val):.1f}" stroke="var(--grid)"/><text x="{ml - 6}" y="{y(val) + 4:.1f}" text-anchor="end">{val} %</text>')
    for j, e in enumerate(NUEVAS):
        if j % 2 == 0 or j == len(NUEVAS) - 1:
            out.append(f'<text x="{x(j):.1f}" y="{H - 10}" text-anchor="middle">{FECHA[e]}</text>')
    ult = []
    for dist, guion, nom in (('Arganzuela', '', 'Arganzuela'), ('San Blas - Canillejas', ' stroke-dasharray="6 4"', 'San Blas-C.')):
        for k in ('PP', 'PSOE'):
            col = COLOR[k]
            pts = ' '.join(f'{x(j):.1f},{y(SER[dist][e][k]):.1f}' for j, e in enumerate(NUEVAS))
            out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.5"{guion}/>')
            for j, e in enumerate(NUEVAS):
                out.append(f'<circle cx="{x(j):.1f}" cy="{y(SER[dist][e][k]):.1f}" r="3" fill="{col}"><title>{k}, {nom}, {FECHA[e]}: {p(SER[dist][e][k])} %</title></circle>')
            ult.append((y(SER[dist]['2023_07'][k]), f'{k} {nom} {p(SER[dist]["2023_07"][k])}'))
    prev = None
    for yy, t in sorted(ult):
        yy = yy if prev is None else max(yy, prev + 14)
        prev = yy
        out.append(f'<text x="{x(len(NUEVAS) - 1) + 8:.1f}" y="{yy + 4:.1f}" class="lab">{esc(t)}</text>')
    out.append('</svg>')
    return ''.join(out)


g_ser = figura('Dos distritos que votaban distinto y en 2023 votaron casi igual',
               '% de voto al PP y al PSOE en las generales de 2004 a 2023. Línea continua: Arganzuela (Calderón). Discontinua: San Blas-Canillejas (Metropolitano)',
               lineas(), 'Fuente: Ministerio del Interior, generales por sección censal, agregadas por distrito (OpenStreetMap). Porcentaje sobre votos a candidaturas.',
               [('PP', COLOR['PP']), ('PSOE', COLOR['PSOE'])],
               (['Generales', 'PP Arganzuela', 'PSOE Arganzuela', 'PP San Blas', 'PSOE San Blas', 'Particip. Arganzuela', 'Particip. San Blas'],
                [[FECHA[e], p(SER['Arganzuela'][e]['PP']), p(SER['Arganzuela'][e]['PSOE']), p(SER['San Blas - Canillejas'][e]['PP']), p(SER['San Blas - Canillejas'][e]['PSOE']),
                  p(SER['Arganzuela'][e]['part']), p(SER['San Blas - Canillejas'][e]['part'])] for e in NUEVAS]))

filas = [('Calderón', ARG), ('Metropolitano', SB), ('Camp Nou', LC)]
GS = lambda s: '<br>'.join(f'{({"PSOE": "PSC" if s is LC else "PSOE", "EMPATE": "Empate a votos"}).get(k, k)} {c}' for k, c in s['gana'].items()) + f'<br>de {s["n"]}'
METR = [('PP', lambda s: f'{p(s["PP"])} %'), ('PSOE / PSC', lambda s: f'{p(s["PSOE"])} %'), ('Sumar', lambda s: f'{p(s["SUMAR"])} %'), ('Vox', lambda s: f'{p(s["VOX"])} %'),
        ('Junts', lambda s: f'{p(s["JUNTS"])} %' if s is LC else '–'), ('ERC', lambda s: f'{p(s["ERC"])} %' if s is LC else '–'),
        ('Particip.', lambda s: f'{p(s["part"])} %'), ('Renta', lambda s: f'{n(s["renta"])} €'), ('Secciones', GS)]
g_tres = ('<figure>\n<figcaption><span class="t">Tres estadios, tres distritos</span><span class="s">Generales de 2023 en el distrito de cada estadio: Arganzuela (el Calderón, hasta 2017), San Blas-Canillejas (el Metropolitano) y les Corts (el Camp Nou)</span></figcaption>\n'
          '<div class="tbl"><table style="font-size:.92rem"><thead><tr><th></th>' + ''.join(f'<th class="n">{t}</th>' for t, _ in filas) + '</tr></thead><tbody>'
          + ''.join(f'<tr><td>{nom}</td>' + ''.join(f'<td class="n" style="white-space:nowrap">{fn(s)}</td>' for _, s in filas) + '</tr>' for nom, fn in METR)
          + '</tbody></table></div>\n<div class="src">Fuente: Ministerio del Interior (por sección censal) e INE (renta por unidad de consumo: mediana de las secciones del distrito). Distritos según OpenStreetMap.</div>\n</figure>\n')

L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
MM = lambda b, t: f'<a href="{BASE}municipio/madrid/madrid/{b}/">{t}</a>'
MB = lambda b, t: f'<a href="{BASE}municipio/barcelona/barcelona/{b}/">{t}</a>'
PARQUE = 'https://theobjective.com/espana/madrid/2024-12-09/almeida-madrid-rio-nuevo-parque-atletico-calderon/'
MAHOU = 'https://diario.madrid.es/blog/2023/04/03/de-estadio-a-gran-parque-historia-de-una-metamorfosis-urbana/'

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Esta noche, a las nueve, el Atlético recibe al Barça en el Metropolitano, en la jornada 12 de LaLiga, según el <a href="https://www.atleticodemadrid.com/noticias/previa-del-atletico-de-madrid-fc-barcelona-jornada-12-laliga-08-11-2026">Atlético</a> y el <a href="https://www.fcbarcelona.es/es/partidos/138391/atletico-madrid-fc-barcelona-la-liga-2026-2027">Barça</a>. Hasta 2017, el Atlético jugaba en el Vicente Calderón, junto al Manzanares, en el barrio {MM('imperial', 'Imperial')} del distrito de Arganzuela. Ese verano se mudó al Metropolitano, en el barrio de {MM('rosas', 'Rosas')}, en San Blas-Canillejas, al este de la ciudad. Sobre la M-30 cubierta, donde estaba el viejo estadio, el Ayuntamiento abrió en diciembre de 2024 el Parque del Atlético de Madrid, según <a href="{PARQUE}">The Objective</a>, y el ámbito Mahou-Calderón tendrá más de 1.300 viviendas, según el <a href="{MAHOU}">Ayuntamiento</a>; <a href="https://www.alimarket.es/construccion/noticia/323402/las-obras-de-las-1-312-viviendas-de-ribera-del-calderon-podrian-comenzar-este-ano">Alimarket</a> cifra en 1.312 las de Ribera del Calderón, el nombre del nuevo barrio.</p>
<p data-tipo="dato">El Atlético se fue a un distrito con casi un tercio menos de renta: la mediana de las secciones censales de San Blas-Canillejas es de {n(SB['renta'])} € por unidad de consumo, frente a {n(ARG['renta'])} € en Arganzuela. También se vota menos. En las generales de julio de 2023 votó el {p(SB['part'])} % del censo en San Blas-Canillejas y el {p(ARG['part'])} % en Arganzuela, siete puntos más. Y el voto se reparte de otra forma: en Arganzuela, el PP ganó en {ARG['gana']['PP']} de las {ARG['n']} secciones; en San Blas-Canillejas, el PSOE ganó en {SB['gana']['PSOE']} de {SB['n']} y el PP en {SB['gana']['PP']}.</p>
{g_tres}
<h2>Del Calderón al Metropolitano</h2>
<p data-tipo="dato">En el conjunto de los dos distritos, el PP sacó casi lo mismo en 2023: el {p(ARG['PP'])} % en Arganzuela y el {p(SB['PP'])} % en San Blas-Canillejas. La diferencia está en el resto. El PSOE sacó el {p(SB['PSOE'])} % en San Blas-Canillejas y el {p(ARG['PSOE'])} % en Arganzuela, y Sumar, el {p(ARG['SUMAR'])} % en Arganzuela y el {p(SB['SUMAR'])} % en San Blas-Canillejas. Vox sacó más en el distrito del Metropolitano ({p(SB['VOX'])} %) que en el del Calderón ({p(ARG['VOX'])} %).</p>
<p data-tipo="patron">Los dos distritos llevan veinte años cambiando de forma parecida. En 2004, Arganzuela votaba al PP ({p(SER['Arganzuela']['2004_03']['PP'])} %) y San Blas-Canillejas, al PSOE ({p(SER['San Blas - Canillejas']['2004_03']['PSOE'])} %). En las dos elecciones de 2019, con Ciudadanos y Vox repartiéndose el voto de la derecha, el PSOE fue primero en los dos. En 2023, con Ciudadanos ya fuera, el PP volvió a ganar en ambos.</p>
{g_ser}
<p data-tipo="hipotesis">El distrito, sin embargo, no es el barrio. San Blas-Canillejas mezcla barrios muy distintos: en {MM('amposta', 'Amposta')}, la renta mediana es de {n(AMP['renta'])} €, el PSOE sacó el {p(AMP['PSOE'])} % y votó el {p(AMP['part'])} %. El barrio del estadio, Rosas, se parece mucho más al del Calderón: renta mediana de {n(ROS['renta'])} €, frente a {n(IMP['renta'])} € en Imperial; participación del {p(ROS['part'])} %, frente al {p(IMP['part'])} %, y el PP primero en {ROS['gana']['PP']} de sus {ROS['n']} secciones, frente a todas las de Imperial, {IMP['gana']['PP']} de {IMP['n']}. El Atlético cambió de distrito más que de vecinos.</p>

<h2>El Camp Nou, en el segundo distrito del PP en Barcelona</h2>
<p data-tipo="dato">El Barça volvió al Camp Nou el 22 de noviembre de 2025, tras más de dos años y medio jugando fuera, según el <a href="https://www.fcbarcelona.es/es/noticias/4407735/el-estreno-en-el-spotify-camp-nou-en-cifras">propio club</a>. El estadio está en el barrio de {MB('la-maternitat-i-sant-ramon', 'la Maternitat i Sant Ramon')}, en el distrito de les Corts. En 2023, el PSC ganó allí en {LC['gana']['PSOE']} de las {LC['n']} secciones, con el {p(LC['PSOE'])} %, y el PP en {LC['gana']['PP']}, con el {p(LC['PP'])} % en el conjunto del distrito. Detrás quedaron Junts ({p(LC['JUNTS'])} %) y ERC ({p(LC['ERC'])} %).</p>
<p data-tipo="patron">El {p(LC['PP'])} % de les Corts es el segundo mejor resultado del PP entre los diez distritos de Barcelona, solo por detrás de Sarrià-Sant Gervasi, y más del doble que en el distrito donde menos sacó, Ciutat Vella. En el conjunto de la ciudad, el PP se quedó en el {p(BCNC['PP'])} %. Dentro de les Corts, el PP ganó en las {PED['n']} secciones de {MB('pedralbes', 'Pedralbes')}, con el {p(PED['PP'])} %. En el barrio del estadio, el PSC ganó en {MAT['gana']['PSOE']} de las {MAT['n']}.</p>
<p data-tipo="dato">La participación de les Corts, del {p(LC['part'])} %, empata con la de Sarrià-Sant Gervasi como la más alta de los distritos de Barcelona. En el conjunto de la ciudad votó el {p(BCNC['part'])} % del censo; en Madrid, el {p(MADC['part'])} %.</p>
<p data-tipo="contexto">Hace dos semanas, el día del Barça-Madrid, contamos que <a href="{A}barcelona-madrid-clasico-del-voto-29n/">en los barrios de renta media el PP saca el triple de votos en Madrid que en Barcelona</a>. Ayer, el día del Valencia-Real Madrid, que <a href="{A}valencia-madrid-mestalla-barrios-29n/">el distrito de Mestalla vota como el del Bernabéu</a>.</p>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">Las cifras son de las generales de 2023. Las encuestas del 29N no miden distritos ni barrios. El voto de los vecinos de un estadio no dice nada del de su afición, que viene de toda la ciudad y de fuera. Y la mudanza del Atlético no explica el voto de nadie: estas cifras describen a los vecinos de cada distrito, no lo que cambió por tener un estadio al lado. La renta del INE por sección tiene un tope, por eso no damos la mediana de barrios como Pedralbes, que lo alcanzan.</p>
'''

preguntas = [
    ('¿En qué distrito está el estadio Metropolitano?', f'En San Blas-Canillejas, en el barrio de Rosas. En las generales de 2023, el PSOE ganó en {SB["gana"]["PSOE"]} de las {SB["n"]} secciones del distrito y el PP en {SB["gana"]["PP"]}; en el barrio de Rosas, el PP ganó en {ROS["gana"]["PP"]} de {ROS["n"]}.'),
    ('¿Cómo votaba el distrito del Vicente Calderón?', f'Arganzuela votó al PP en 2023: ganó en {ARG["gana"]["PP"]} de sus {ARG["n"]} secciones, con el {p(ARG["PP"])} %. La participación fue del {p(ARG["part"])} %.'),
    ('¿Cómo vota el barrio del Camp Nou?', f'El estadio está en la Maternitat i Sant Ramon, en les Corts. En 2023, el PSC ganó en {MAT["gana"]["PSOE"]} de las {MAT["n"]} secciones del barrio y en {LC["gana"]["PSOE"]} de las {LC["n"]} del distrito.'),
]
enlaces = (f'<a href="{BASE}municipio/madrid/madrid/">Elecciones en Madrid</a> · <a href="{BASE}municipio/barcelona/barcelona/">Elecciones en Barcelona</a> · '
           f'{L("barcelona-madrid-clasico-del-voto-29n", "El otro Clásico")} · {L("valencia-madrid-mestalla-barrios-29n", "Mestalla vota como el Bernabéu")} · '
           f'{L("cinturon-rojo-madrid-29n", "Lo que queda del cinturón rojo")} · {L("tres-semanas-29n-la-semana-en-el-mapa", "La crónica del sábado")}')
foot = 'Datos: Ministerio del Interior, generales de 2004 a 2023 por sección censal; INE, renta por unidad de consumo por sección (Atlas de Distribución de Renta de los Hogares); barrios y distritos de OpenStreetMap. Cálculo: actualidad/src/resumenes/atletico.py.'

TIT = f'Del Calderón al Metropolitano: el Atlético se mudó a un distrito con casi un tercio menos de renta, siete puntos menos de participación y donde el PSOE gana en {SB["gana"]["PSOE"]} de las {SB["n"]} secciones'
DEK = f'El día del Atlético-Barça, los distritos de los tres estadios. En Arganzuela, donde estaba el Calderón, el PP ganó en {ARG["gana"]["PP"]} de {ARG["n"]} secciones en 2023. El barrio del Metropolitano, Rosas, se parece más al del Calderón que su distrito. Y el Camp Nou está en el segundo distrito del PP en Barcelona.'
import json
def r4(o):
    if isinstance(o, dict): return {str(k): r4(v) for k, v in o.items()}
    if isinstance(o, float): return round(o, 4)
    if hasattr(o, 'item'): return r4(o.item())
    return o
DATOS = r4({'ARG': ARG, 'SB': SB, 'IMP': IMP, 'ROS': ROS, 'AMP': AMP, 'LC': LC, 'MAT': MAT, 'PED': PED, 'MADC': MADC, 'BCNC': BCNC,
            'SER': SER, 'REN': REN, 'dif_part': ARG['part'] - SB['part'], 'puesto_renta': {k: ord_renta.index(k) + 1 for k in ('Arganzuela', 'San Blas - Canillejas')},
            'n_distritos_mad': len(DM), 'n_distritos_bcn': len(DB), 'DB': {k: {'PP': x['PP'], 'part': x['part']} for k, x in DB.items()}})
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
if __name__ == '__main__':
    print(TIT)
    pieza('atletico-barca-metropolitano-camp-nou-29n', 'Del Calderón al Metropolitano', TIT, DEK, '8 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, datos_js)
