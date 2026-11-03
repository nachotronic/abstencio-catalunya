"""«Bizkaia, el feudo del PNV» (3-11-2026): de 92 a 55 municipios entre 2019 y 2023, y el empate a tres de la media de encuestas.

Cifras: generales de 1977 a 2023 por municipio (generales-2026/descargas/municipios_historico.csv hasta 2000 y
municipios.csv desde 2004), porcentaje sobre votos a candidaturas y sin voto exterior (CERA). En 2015 la familia
«Sumar / Podemos / IU» suma Podemos e IU, que fueron por separado: en Bizkaia ganó el PNV (28,14 % frente al 26,30 %
de Podemos, Público con datos de Interior), así que la serie de ganadores corrige ese año. Modelo de encuestas:
previsiones/datos/publico/escenario-base.json del 3-11-2026, congelado en la pieza (const MODELO) porque cambia cada día.
Uso, desde la raíz: python3 actualidad/src/resumenes/bizkaia.py
"""
import json
import math
import sys

import pandas as pd

from comun import BASE, COLOR, RAIZ, esc, figura, n, barras, pares, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
F = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'UPYD', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC', 'UCD', 'CDS', 'OTROS']
EL = ['1977_06', '1979_03', '1982_10', '1986_06', '1989_10', '1993_06', '1996_03', '2000_03', '2004_03', '2008_03',
      '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
ANIO = {'2019_04': '2019-A', '2019_11': '2019-N'}
an = lambda e: ANIO.get(e, e[:4])
ETQ = {'PNV': 'PNV', 'PSOE': 'PSOE', 'BILDU': 'EH Bildu', 'PP': 'PP', 'SUMAR': 'Podemos'}

h = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios_historico.csv', dtype={'mun_code': str})
m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str})
h, m = h[h.mun_code.str[:2] == '48'], m[m.mun_code.str[:2] == '48'].copy()

SERIE = {}
for e in EL:
    d = h if e < '2004' else m
    v = {f: float(d[f'{e}_v{f}'].sum()) for f in F}
    t = sum(v.values())
    SERIE[an(e)] = {f: round(v[f] / t * 100, 2) for f in ('PNV', 'PSOE', 'BILDU', 'PP', 'SUMAR')}
GANA = {a: max(s, key=s.get) for a, s in SERIE.items()}
assert GANA['2015'] == 'SUMAR' and GANA['2016'] == 'SUMAR' and GANA['2008'] == 'PSOE'
GANA['2015'] = 'PNV'   # Podemos solo (26,30 %) quedó detrás del PNV (28,14 %): la familia suma IU
assert sum(g == 'PNV' for g in GANA.values()) == 14
assert round(SERIE['2023']['PNV'], 1) == 27.1 and round(SERIE['2023']['PSOE'], 1) == 26.0 and round(SERIE['2023']['BILDU'], 1) == 20.8
assert min(SERIE[a]['PNV'] for a in SERIE) == SERIE['2023']['PNV']

# Municipios: quién ganó en 2019-N y en 2023
a, b = '2019_11', '2023_07'
M19, M23 = m[f'{a}_gana'].value_counts().to_dict(), m[f'{b}_gana'].value_counts().to_dict()
assert M19 == {'PNV': 92, 'BILDU': 16, 'PSOE': 4} and M23 == {'PNV': 55, 'BILDU': 43, 'PSOE': 14}, (M19, M23)
fl = m[m[f'{a}_gana'] != m[f'{b}_gana']].sort_values('poblacion', ascending=False)
CAMBIOS = fl.groupby([f'{a}_gana', f'{b}_gana']).size().to_dict()
assert CAMBIOS == {('PNV', 'BILDU'): 27, ('PNV', 'PSOE'): 10}, CAMBIOS
POB = {k: int(v) for k, v in m.groupby(f'{b}_gana').poblacion.sum().items()}
POBT = int(m.poblacion.sum())
HIST_B = {an(e): int(((h if e < '2004' else m)[f'{e}_gana'] == 'BILDU').sum()) for e in EL}
assert max(v for k, v in HIST_B.items() if k != '2023') == 32 and HIST_B['2023'] == 43
cols = ['municipio', 'poblacion', f'{a}_gana', f'{b}_gana', f'{b}_PNV', f'{b}_PSOE', f'{b}_BILDU', f'{b}_PP', f'{b}_part']
MUN = {r[0]: {'pob': int(r[1]), 'g19': r[2], 'g23': r[3], 'PNV': round(r[4] * 100, 2), 'PSOE': round(r[5] * 100, 2),
              'BILDU': round(r[6] * 100, 2), 'PP': round(r[7] * 100, 2), 'part': round(r[8] * 100, 2)}
       for r in m[cols].itertuples(index=False)}
assert MUN['Durango']['g23'] == 'BILDU' and MUN['Amorebieta-Etxano']['g23'] == 'BILDU' and MUN['Bilbao']['g23'] == 'PSOE'
assert MUN['Getxo']['g23'] == 'PNV' and MUN['Leioa']['g23'] == 'PNV' and MUN['Galdakao']['g23'] == 'PNV'

# Modelo de encuestas del 3-11-2026 (se congela en la pieza)
esc_ = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
meta = json.load(open(RAIZ / 'previsiones/datos/publico/meta.json'))
assert meta['generado'] == '2026-11-03', meta['generado']


def reparto_provincia(v):
    """Copia de encuestas/src/construir.py: reparto central que suma los escaños de la provincia."""
    e = {l['lista']: l['escanos'][1] for l in v['listas']}
    voto = {l['lista']: l['voto'][1] for l in v['listas']}
    lo = {l['lista']: l['escanos'][0] for l in v['listas']}
    hi = {l['lista']: l['escanos'][2] for l in v['listas']}
    total = v['escanos_total']
    while sum(e.values()) < total:
        cand = [k for k in e if e[k] < hi[k]] or list(e)
        k = max(cand, key=lambda k: voto[k] / (e[k] + 1)); e[k] += 1
    while sum(e.values()) > total:
        cand = [k for k in e if 0 < e[k] and lo[k] < e[k]] or [k for k in e if e[k] > 0]
        k = min(cand, key=lambda k: voto[k] / e[k]); e[k] -= 1
    return e


v48 = esc_['provincias']['48']
RC = reparto_provincia(v48)
MODELO = {l['lista']: {'voto': l['voto'], 'esc': l['escanos'], 'central': RC[l['lista']], 'p1': round(l['p_primera'] * 100, 1)}
          for l in v48['listas'] if l['voto'][1] >= 2}
EUS = {}
for c in ('01', '20', '48'):
    for k, e in reparto_provincia(esc_['provincias'][c]).items():
        EUS[k] = EUS.get(k, 0) + e
EUS = {k: v for k, v in EUS.items() if v}
assert MODELO['EH Bildu']['central'] == 3 and MODELO['PNV']['central'] == 2 and MODELO['PSOE']['central'] == 2 and MODELO['PP']['central'] == 1, MODELO
assert MODELO['PNV']['voto'][1] == 22.4 and MODELO['EH Bildu']['voto'][1] == 22.4 and MODELO['PSOE']['voto'][1] == 22.2
assert EUS == {'EH Bildu': 7, 'PSOE': 5, 'PNV': 4, 'PP': 2}, EUS
SIMS = meta['simulaciones']


# --- Mapa de municipios (geometría de generales-2026/data/municipios.json) ---
G = json.load(open(RAIZ / 'generales-2026/data/municipios.json'))
COLM = {'PNV': COLOR['PNV'], 'BILDU': COLOR['EH Bildu'], 'PSOE': COLOR['PSOE'], 'PP': COLOR['PP']}
gan = {e: dict(zip(m.mun_code, m[f'{e}_gana'])) for e in (a, b)}
nom = dict(zip(m.mun_code, m.municipio))


def anillos():
    S, kx = G['S'], math.cos(math.radians(43.2))
    out = []
    for c, partes in zip(G['cod'], G['poly']):
        if not c.startswith('48'):
            continue
        for f in partes:
            x, y, pts = f[0], f[1], [(f[0], f[1])]
            for k in range(2, len(f), 2):
                x += f[k]; y += f[k + 1]; pts.append((x, y))
            out.append((c, [(px / S * kx, -py / S) for px, py in pts]))
    return out


AN = anillos()
XS = [x for _, r in AN for x, _ in r]; YS = [y for _, r in AN for _, y in r]


def mapa(e, W=310):
    s = W / (max(XS) - min(XS)); H = round((max(YS) - min(YS)) * s)
    camino = {}
    for c, r in AN:
        d = ''.join(('L' if i else 'M') + f'{(x - min(XS)) * s:.1f},{(y - min(YS)) * s:.1f}' for i, (x, y) in enumerate(r))
        camino[c] = camino.get(c, '') + d + 'Z'
    out = ''.join(f'<path d="{d}" fill="{COLM.get(gan[e].get(c), "var(--otros)")}"><title>{esc(nom.get(c, c))}: '
                  f'{esc(ETQ.get(gan[e].get(c), "sin datos"))}</title></path>' for c, d in camino.items())
    return W, H, out


def dos_mapas():
    W1, H, m1 = mapa(a, 640)
    _, _, m2 = mapa(b, 640)
    gap = 44
    return (f'<svg viewBox="0 -30 {W1} {2 * H + gap + 30}" role="img" aria-label="Municipios de Bizkaia por partido más votado en 2019 y en 2023">'
            f'<text x="0" y="-10" class="lab" style="font-size:20px">Noviembre de 2019 · PNV primero en {M19["PNV"]} municipios</text>'
            f'<g stroke="var(--bg)" stroke-width=".8" stroke-linejoin="round">{m1}</g>'
            f'<text x="0" y="{H + gap - 10}" class="lab" style="font-size:20px">Julio de 2023 · PNV primero en {M23["PNV"]} municipios</text>'
            f'<g transform="translate(0,{H + gap})" stroke="var(--bg)" stroke-width=".8" stroke-linejoin="round">{m2}</g></svg>')


def lineas(W=640, H=260, ml=40, mr=80, mt=12, mb=34):
    xs = list(SERIE)
    x = lambda i: ml + i * (W - ml - mr) / (len(xs) - 1)
    y = lambda v: mt + (40 - v) / 40 * (H - mt - mb)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Voto en Bizkaia en las generales de 1977 a 2023">']
    for v in (0, 10, 20, 30, 40):
        out.append(f'<line x1="{ml}" x2="{W - mr}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--grid)"/><text x="{ml - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{v} %</text>')
    for i, t in enumerate(xs):
        if t in ('1977', '1986', '1996', '2004', '2011', '2016', '2023'):
            out.append(f'<text x="{x(i):.1f}" y="{H - 10}" text-anchor="middle">{t}</text>')
    for k in ('PNV', 'PSOE', 'BILDU', 'PP'):
        col = COLOR[ETQ[k]]
        pts = [(x(i), y(SERIE[t][k])) for i, t in enumerate(xs) if SERIE[t][k] != 0]
        # la izquierda abertzale no se presentó en 2000, 2004 y 2008: la línea se corta
        tramos, cur = [], []
        for i, t in enumerate(xs):
            if SERIE[t][k] == 0:
                if cur: tramos.append(cur); cur = []
                continue
            cur.append(f'{x(i):.1f},{y(SERIE[t][k]):.1f}')
        tramos.append(cur)
        for tr in tramos:
            if tr:
                out.append(f'<polyline points="{" ".join(tr)}" fill="none" stroke="{col}" stroke-width="{3 if k == "PNV" else 2.2}"/>')
        for i, t in enumerate(xs):
            if SERIE[t][k] != 0:
                out.append(f'<circle cx="{x(i):.1f}" cy="{y(SERIE[t][k]):.1f}" r="3" fill="{col}"><title>{ETQ[k]}, {t}: {p(SERIE[t][k])} %</title></circle>')
        out.append(f'<text x="{x(len(xs) - 1) + 8:.1f}" y="{y(SERIE["2023"][k]) + (4 if k != "PSOE" else 12):.1f}" class="lab">{ETQ[k]} {p(SERIE["2023"][k])}</text>')
    out.append('</svg>')
    return ''.join(out)


LEY4 = [(ETQ[k], COLOR[ETQ[k]]) for k in ('PNV', 'PSOE', 'BILDU', 'PP')]
SIN_CERA = 'Porcentaje sobre votos a candidaturas, sin voto exterior (CERA).'
g_mapa = figura('El mapa de Bizkaia cambió de color en cuatro años',
                'Partido más votado en cada municipio en las generales de noviembre de 2019 y de julio de 2023',
                dos_mapas(), 'Fuente: Ministerio del Interior, resultados por municipio. ' + SIN_CERA,
                [('PNV', COLOR['PNV']), ('EH Bildu', COLOR['EH Bildu']), ('PSOE', COLOR['PSOE'])],
                (['Partido', 'Municipios en 2019-N', 'Municipios en 2023'],
                 [[ETQ[k], str(M19.get(k, 0)), str(M23.get(k, 0))] for k in ('PNV', 'BILDU', 'PSOE')]))
g_serie = figura('Cuatro décadas de voto en Bizkaia', '% de voto en las 16 elecciones generales desde 1977', lineas(),
                 'Fuente: Ministerio del Interior. HB, EH, Amaiur y EH Bildu, en la misma línea; en 2000, 2004 y 2008 la izquierda '
                 'abertzale no se presentó o sus listas fueron ilegalizadas; en 1979, AP no tiene dato propio en nuestra serie. ' + SIN_CERA, LEY4,
                 (['Elección', 'PNV', 'PSOE', 'EH Bildu', 'PP'], [[t, p(s['PNV']), p(s['PSOE']), p(s['BILDU']) if s['BILDU'] else '–', p(s['PP'])] for t, s in SERIE.items()]))
ORD = sorted(MODELO, key=lambda k: -MODELO[k]['voto'][1])
NOMM = lambda k: 'Frente Amplio (Sumar)' if k == 'Sumar' else k
g_modelo = figura('Bizkaia, empate a tres en la media de encuestas',
                  f'Voto estimado en Bizkaia para el 29N y escaños del reparto central (modelo de Mapa Electoral, {SIMS:,} simulaciones, 3 de noviembre)'.replace(',', '.'),
                  barras([(NOMM(k), MODELO[k]['voto'][1], COLOR.get(k, COLOR.get('Sumar')),
                           f'{p(MODELO[k]["voto"][1])} % · {MODELO[k]["central"]} esc.') for k in ORD], 30, 'Voto estimado en Bizkaia', ml=170),
                  'Fuente: modelo de Mapa Electoral con la media de las encuestas nacionales repartida por provincia. No es una encuesta de Bizkaia. '
                  'El intervalo del 80 % de cada partido está en la tabla.', None,
                  (['Lista', 'Voto', 'Intervalo 80 %', 'Escaños', 'Horquilla', 'Primero en'],
                   [[NOMM(k), p(MODELO[k]['voto'][1]), f'{p(MODELO[k]["voto"][0])}-{p(MODELO[k]["voto"][2])}', str(MODELO[k]['central']),
                     f'{MODELO[k]["esc"][0]}-{MODELO[k]["esc"][2]}', f'{n(MODELO[k]["p1"])} %'] for k in ORD]))

L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
MU = lambda path, t: f'<a href="{BASE}municipio/bizkaia/{path}/">{t}</a>'
PUB15 = 'https://www.publico.es/resultados-elecciones/generales/2015/euskadi/vizcaya'
PUB16 = 'https://www.publico.es/resultados-elecciones/generales/2016/congreso/euskadi/vizcaya'
ORAIN_PNV = 'https://orain.eus/es/politica/2026/10/17/el-pnv-ratifica-unanimidad-maribel-vaquero-idoia-sagastizabal-gorka-urtaran-candidatos-al-congreso/'
SOCIO = 'https://www.eldiario.es/euskadi/victoria-eh-bildu-votos-escanos-generales-pse-ee-segundo-pnv-tercero-euskadi-sociometro_1_13626270.html'
FORAL = 'https://orain.eus/es/politica/2026/07/01/pnv-sumaria-un-escano-en-las-elecciones-forales-en-bizkaia-eh-bildu-podria-sumar-2-segun-un-sondeo-foral/'
U = MUN
pb = lambda k: n(U[k]['pob'])
DATOS = {'SIMS': SIMS, 'SERIE': SERIE, 'M19': M19, 'M23': M23, 'POB': POB, 'POBT': POBT, 'HIST_B': HIST_B, 'MODELO': MODELO, 'EUS': EUS,
         'MUN': {k: U[k] for k in ('Bilbao', 'Barakaldo', 'Getxo', 'Durango', 'Amorebieta-Etxano', 'Lekeitio', 'Leioa', 'Galdakao',
                                   'Santurtzi', 'Basauri', 'Portugalete', 'Sestao', 'Arrigorriaga', 'Gernika-Lumo')},
         'CAMBIOS': {f'{x}-{y}': v for (x, y), v in CAMBIOS.items()}}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
nb, npnv = CAMBIOS[('PNV', 'BILDU')], CAMBIOS[('PNV', 'PSOE')]

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="dato">En las generales de noviembre de 2019, el PNV fue el partido más votado en {M19["PNV"]} de los 112 municipios de Bizkaia. Cuatro años después, en las de julio de 2023, solo en {M23["PNV"]}. Perdió {nb} pueblos frente a EH Bildu y {npnv} frente al PSOE. Fue la primera vez desde 1977 que EH Bildu y su familia política ganaban en más de cuarenta municipios vizcaínos: {M23["BILDU"]}, cuando su máximo anterior eran los {max(v for k, v in HIST_B.items() if k != "2023")} de Amaiur en 2011.</p>
{g_mapa}
<p data-tipo="dato">El PNV siguió siendo el más votado en el conjunto de la provincia, pero por poco: el {p(SERIE["2023"]["PNV"])} % de los votos a candidaturas, frente al {p(SERIE["2023"]["PSOE"])} % del PSOE y el {p(SERIE["2023"]["BILDU"])} % de EH Bildu. Es su resultado más bajo en Bizkaia en las 16 generales de la democracia. En noviembre de 2019 había sacado el {p(SERIE["2019-N"]["PNV"])} %.</p>
<p data-tipo="contexto">Bizkaia es la provincia del PNV. El partido nació en Bilbao en 1895 y tiene allí su sede, Sabin Etxea. En las generales, el PNV fue el más votado en Bizkaia en 14 de las 16 elecciones. Las dos excepciones fueron 2008, cuando ganó el PSOE, y 2016, cuando ganó Unidos Podemos por menos de un punto (el {p(29.04)} % frente al {p(28.43)} %, según los <a href="{PUB16}">resultados oficiales</a>). En 2015, Podemos ya se había quedado a menos de dos puntos: el PNV sacó el {p(28.14)} % y Podemos el {p(26.30)} % (<a href="{PUB15}">resultados de 2015</a>).</p>
{g_serie}

<h2>Una pinza con dos brazos</h2>
<p data-tipo="patron">El PNV no perdió los municipios al azar. Los {nb} que pasaron a EH Bildu son sobre todo pueblos del interior y de la costa oriental: {MU("durango", "Durango")} ({pb("Durango")} habitantes, EH Bildu {p(U["Durango"]["BILDU"])} %, PNV {p(U["Durango"]["PNV"])} %), {MU("amorebieta-etxano", "Amorebieta-Etxano")} ({p(U["Amorebieta-Etxano"]["BILDU"])} % frente a {p(U["Amorebieta-Etxano"]["PNV"])} %) y {MU("lekeitio", "Lekeitio")}, donde EH Bildu pasó de la mitad del voto ({p(U["Lekeitio"]["BILDU"])} %). Los {npnv} que pasaron al PSOE están en Bilbao y en su área metropolitana, como {MU("bilbao", "Bilbao")}, {MU("santurtzi", "Santurtzi")} o {MU("basauri", "Basauri")}.</p>
<p data-tipo="dato">Por eso los colores del mapa engañan. Los {M23["BILDU"]} municipios donde ganó EH Bildu suman {n(POB["BILDU"])} habitantes, el {n(POB["BILDU"] / POBT * 100)} % de la provincia. Los {M23["PSOE"]} del PSOE suman {n(POB["PSOE"])}, el {n(POB["PSOE"] / POBT * 100)} %: además de Bilbao, {MU("barakaldo", "Barakaldo")} ({p(U["Barakaldo"]["PSOE"])} %), {MU("portugalete", "Portugalete")} y {MU("sestao", "Sestao")}, en la margen izquierda de la ría. El PNV conserva la margen derecha, con {MU("getxo", "Getxo")} ({p(U["Getxo"]["PNV"])} %) y {MU("leioa", "Leioa")}, y municipios como {MU("galdakao", "Galdakao")} o {MU("gernika-lumo", "Gernika-Lumo")}.</p>
<p data-tipo="hipotesis">Una lectura posible es que el PNV sufrió en 2023 dos competencias a la vez. En los pueblos euskaldunes del interior, la de EH Bildu, que comparte con él buena parte del electorado nacionalista. En la Bilbao metropolitana, la del PSOE, en unas generales muy polarizadas entre Pedro Sánchez y Alberto Núñez Feijóo. Los datos por municipio describen dónde cambió el voto, no por qué cambió. Para saberlo harían falta encuestas que siguieran a los mismos votantes.</p>

<h2>El 29N: un empate a tres</h2>
<p data-tipo="dato">Nuestro modelo, que reparte la media de las encuestas nacionales por provincia y la simula {n(SIMS)} veces, deja hoy a Bizkaia en un empate a tres. El PNV y EH Bildu tienen el {p(MODELO["PNV"]["voto"][1])} % estimado cada uno, y el PSOE el {p(MODELO["PSOE"]["voto"][1])} %. EH Bildu queda primero en el {n(MODELO["EH Bildu"]["p1"])} % de las simulaciones, el PNV en el {n(MODELO["PNV"]["p1"])} % y el PSOE en el {n(MODELO["PSOE"]["p1"])} %.</p>
{g_modelo}
<p data-tipo="dato">El reparto central de los ocho escaños de Bizkaia sería {MODELO["EH Bildu"]["central"]} para EH Bildu, {MODELO["PNV"]["central"]} para el PNV, {MODELO["PSOE"]["central"]} para el PSOE y {MODELO["PP"]["central"]} para el PP. Pero las horquillas se solapan: el PNV podría sacar entre {MODELO["PNV"]["esc"][0]} y {MODELO["PNV"]["esc"][2]}, y EH Bildu y el PSOE, entre {MODELO["EH Bildu"]["esc"][0]} y {MODELO["EH Bildu"]["esc"][2]}. En el conjunto de Euskadi, el reparto central da {EUS["EH Bildu"]} escaños a EH Bildu, {EUS["PSOE"]} al PSOE, {EUS["PNV"]} al PNV y {EUS["PP"]} al PP. Los candidatos de cada lista y sus opciones de salir están en las <a href="{BASE}listas-electorales-29n/bizkaia/">listas del 29N en Bizkaia</a>.</p>
<p data-tipo="contexto">El Sociómetro del Gobierno vasco, la encuesta propia de Lehendakaritza, va más allá. Con trabajo de campo del 20 al 23 de octubre, deja al PNV como tercera fuerza en Euskadi. Según <a href="{SOCIO}">elDiario.es</a>, los jeltzales «serían incluso terceros en Bizkaia, su gran feudo». La cabeza de lista del PNV por Bizkaia, Idoia Sagastizabal, defendió el 17 de octubre que el partido tiene «claro el rumbo» en plena «marejada» y que «las etiquetas no resuelven los problemas», según <a href="{ORAIN_PNV}">EITB</a>.</p>
<p data-tipo="contexto">Las generales no son las forales. El sondeo de la Diputación de Bizkaia publicado en julio, hecho por Gizaker con 3.000 entrevistas, daba al PNV el 39,3 % en las elecciones a Juntas Generales de 2027, una décima más que en las de 2023, y a EH Bildu el 29,5 %, según <a href="{FORAL}">EITB</a>. Dos meses después de esas forales de mayo de 2023, el mismo PNV se quedó en el {p(SERIE["2023"]["PNV"])} % en las generales de julio. Ese doble voto, más nacionalista en las elecciones vascas y más repartido en las de España, es el que el PNV necesita recuperar el 29N.</p>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">Los porcentajes de esta pieza son sobre votos a candidaturas y sin el voto de los vizcaínos que viven en el extranjero, por eso difieren en unas décimas de los oficiales. En 2015, nuestra serie suma Podemos e IU, que se presentaron por separado; los resultados de ese año en el texto son los oficiales de cada lista. El modelo no es una encuesta de Bizkaia: reparte la media nacional por provincia con el resultado de 2023 y las encuestas vascas, y a 26 días de la votación su margen de error es amplio. Y el ganador de un municipio no dice nada de cuántos votos pesa: los {M23["BILDU"]} municipios de EH Bildu tienen menos habitantes que Bilbao.</p>
{datos_js}'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Bizkaia?', f'El PNV, con el {p(SERIE["2023"]["PNV"])} % de los votos a candidaturas (sin voto exterior), por delante del PSOE ({p(SERIE["2023"]["PSOE"])} %) y EH Bildu ({p(SERIE["2023"]["BILDU"])} %). Fue el peor resultado del PNV en Bizkaia en unas generales.'),
    ('¿Quién ganará en Bizkaia el 29N según las encuestas?', f'Nadie claro: en la media de encuestas de Mapa Electoral del 3 de noviembre, PNV y EH Bildu tienen el {p(MODELO["PNV"]["voto"][1])} % y el PSOE el {p(MODELO["PSOE"]["voto"][1])} %. EH Bildu queda primero en el {n(MODELO["EH Bildu"]["p1"])} % de las simulaciones y el PNV en el {n(MODELO["PNV"]["p1"])} %. Las cifras del día están en la <a href="{BASE}encuestas/bizkaia/">encuesta de Bizkaia</a>.'),
    ('¿Cuántos diputados elige Bizkaia?', 'Ocho diputados al Congreso, repartidos con la ley D\'Hondt entre las candidaturas que pasan del 3 % de los votos válidos de la provincia, y cuatro senadores.'),
]
enlaces = (f'<a href="{BASE}elecciones/pais-vasco/bizkaia/">Elecciones en Bizkaia</a> · <a href="{BASE}encuestas/bizkaia/">Encuesta de Bizkaia</a> · '
           f'{L("derbi-vasco-bilbao-donostia-29n", "El derbi en las urnas: Bilbao y Donostia")} · {L("euskadi-empate-a-tres", "Euskadi, empate a tres")} · '
           f'{L("pnv-cinco-pueblos-bermeo", "Los cinco pueblos más del PNV")}')
foot = ('Datos: Ministerio del Interior, generales de 1977 a 2023 por municipio; resultados oficiales de 2015 y 2016 en Bizkaia (Público); '
        'modelo de encuestas de Mapa Electoral del 3 de noviembre de 2026. Cálculo: actualidad/src/resumenes/bizkaia.py.')

pieza('bizkaia-pnv-bildu-encuestas-29n', 'Bizkaia, el feudo del PNV',
      f'El PNV ganó en {M19["PNV"]} municipios de Bizkaia en 2019 y en {M23["PNV"]} en 2023: su feudo llega al 29N en empate a tres',
      f'En cuatro años, EH Bildu le quitó {nb} pueblos y el PSOE {npnv}, Bilbao incluido. El PNV ganó la provincia con su peor resultado en unas generales, '
      f'el {p(SERIE["2023"]["PNV"])} %. Hoy la media de encuestas deja al PNV, EH Bildu y el PSOE entre el {p(MODELO["PSOE"]["voto"][1])} % y el {p(MODELO["PNV"]["voto"][1])} %.',
      '3 de noviembre de 2026', cuerpo, preguntas, enlaces, foot)
