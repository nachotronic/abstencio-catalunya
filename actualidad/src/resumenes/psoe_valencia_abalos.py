"""«El PSOE de Valencia, el de Ábalos» (6-11-2026): el 5-11 la UCO registró la casa de José Luis Ábalos en Valencia en
una nueva pieza del caso Koldo (EFE). Ábalos fue número dos del PSOE por Valencia en 2023, detrás de Diana Morant; esa
lista sacó en la provincia su mejor resultado desde 2008. El modelo del 5-11, con encuestas anteriores al registro, le da los mismos cinco escaños.

Cifras de 2004 a 2023: generales por municipio (generales-2026/descargas/municipios.csv), porcentaje sobre votos a
candidaturas y sin voto exterior (CERA). Listas: BOE de las candidaturas proclamadas de 2023 y 2026
(listas-electorales-29n/datos/). Escaños de 2023: diputados de la XV legislatura. Modelo: escenario base publicado del
5-11-2026 (previsiones/datos/publico/escenario-base.json).
Uso, desde la raíz: python3 actualidad/src/resumenes/psoe_valencia_abalos.py
"""
import collections
import json
import math
import unicodedata

import pandas as pd

from comun import BASE, COLOR, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
F = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'UPYD', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC', 'UCD', 'CDS', 'OTROS']
EL = [('2004_03', '2004'), ('2008_03', '2008'), ('2011_11', '2011'), ('2015_12', '2015'), ('2016_06', '2016'),
      ('2019_04', 'abr. 2019'), ('2019_11', 'nov. 2019'), ('2023_07', '2023')]

m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str})
v = m[m.mun_code.str[:2] == '46'].copy()
NMUN = len(v)
assert NMUN == 266, NMUN

SERIE, GANA = {}, {}
for e, _ in EL:
    T = sum(v[f'{e}_v{f}'].sum() for f in F if f'{e}_v{f}' in v)
    SERIE[e] = {k: round(v[f'{e}_v{k}'].sum() / T * 100, 2) for k in ('PSOE', 'PP')}
    GANA[e] = {k: int((v[f'{e}_gana'] == k).sum()) for k in ('PSOE', 'PP')}
assert SERIE['2023_07']['PSOE'] == 32.35 and SERIE['2008_03']['PSOE'] == 40.42
MEJOR = max((e for e, _ in EL if e > '2008_03'), key=lambda e: SERIE[e]['PSOE'])
assert MEJOR == '2023_07'

# Porcentaje del PSOE por municipio en 2023
TOT = sum(v[f'2023_07_v{f}'] for f in F)
v['psoe'] = v['2023_07_vPSOE'] / TOT * 100
v['dif'] = v['psoe'] - v['2019_11_vPSOE'] / sum(v[f'2019_11_v{f}'] for f in F) * 100
SUBE = int((v.dif > 0).sum())
GRANDES = v[v['2023_07_censo'] >= 50000].sort_values('psoe', ascending=False)

# Listas
def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn').replace('à', 'a')


def lista(anio):
    d = json.load(open(RAIZ / f'listas-electorales-29n/datos/{anio}-proclamadas.json'))['candidaturas']
    c = next(x for x in d if x['prov'] == '46' and x['camara'] == 'congreso' and x['siglas'] == 'PSOE')
    return [t['nombre'] for t in c['titulares']]


L23, L26 = lista(2023), lista(2026)
assert L23[0] == 'Diana Morant Ripoll' and L23[1] == 'José Luis Ábalos Meco' and L26[0] == 'Pilar Bernabé García'
# Repiten de la lista de 2023 (titulares): por nombre y dos primeros apellidos, sin tildes
clave = lambda s: tuple(norm(s).split()[:3])
REPITEN = [x for x in L26 if clave(x) in {clave(y) for y in L23}]
assert len(REPITEN) == 3, REPITEN   # Carmen Martínez, Vicent Sarrià y Ana María González Herdaro

dips = json.load(open(RAIZ / 'listas-electorales-29n/datos/diputados-xv.json'))['diputados']
ABALOS = next(x for x in dips if x['nombre'] == 'José Luis Ábalos Meco')
assert ABALOS['baja'] == '28/01/2026' and ABALOS['circ'] == 'Valencia/València'
xs = [x for x in dips if x['circ'] == 'Valencia/València' and x['alta'].endswith('/08/2023')]   # los elegidos en julio de 2023
E23 = dict(collections.Counter(x['formacion'] for x in xs))
assert sum(E23.values()) == 16, E23
ESC23 = E23['PSOE']

# Modelo del 3-11
ESCB = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))['provincias']['46']
meta = json.load(open(RAIZ / 'previsiones/datos/publico/meta.json'))
assert meta['generado'] == '2026-11-05', meta['generado']
SIMS = meta['simulaciones']
MODP = next(l for l in ESCB['listas'] if l['lista'] == 'PSOE')
# --- Gráficos ---
g_serie = figura(f'El PSOE sacó en 2023 en la provincia de Valencia su mejor resultado desde 2008',
                 'Porcentaje de voto del PSOE en la provincia de Valencia en cada elección general',
                 barras([(t, SERIE[e]['PSOE'], COLOR['PSOE'], f'{p(SERIE[e]["PSOE"])} %') for e, t in EL], 50,
                        'Voto al PSOE en la provincia de Valencia', ml=90),
                 'Fuente: Ministerio del Interior, resultados por municipio; porcentaje sobre votos a candidaturas, sin voto exterior (CERA).',
                 None,
                 (['Elección', 'PSOE', 'PP', 'Municipios donde ganó el PSOE', 'Donde ganó el PP'],
                  [[t, f'{p(SERIE[e]["PSOE"])} %', f'{p(SERIE[e]["PP"])} %', str(GANA[e]['PSOE']), str(GANA[e]['PP'])] for e, t in EL]))

G = json.load(open(RAIZ / 'generales-2026/data/municipios.json'))
TRAMOS = [(20, '#fbe3e1'), (25, '#f4b6b1'), (30, '#ea827a'), (35, '#d9534a'), (40, '#b82a22'), (101, '#7f1510')]
ETQ_T = ['menos del 20 %', '20-25 %', '25-30 %', '30-35 %', '35-40 %', '40 % o más']
color = lambda x: next(c for t, c in TRAMOS if x < t)
pct = dict(zip(v.mun_code, v.psoe))
nom = dict(zip(v.mun_code, v.municipio))


def mapa(W=360):
    S, kx = G['S'], math.cos(math.radians(39.4))
    AN = []
    for c, partes in zip(G['cod'], G['poly']):
        if c[:2] != '46':
            continue
        for f in partes:
            x, y, pts = f[0], f[1], [(f[0], f[1])]
            for k in range(2, len(f), 2):
                x += f[k]; y += f[k + 1]; pts.append((x, y))
            AN.append((c, [(px / S * kx, -py / S) for px, py in pts]))
    XS = [x for _, r in AN for x, _ in r]; YS = [y for _, r in AN for _, y in r]
    s = W / (max(XS) - min(XS)); H = round((max(YS) - min(YS)) * s)
    camino = {}
    for c, r in AN:
        d = ''.join(('L' if i else 'M') + f'{(x - min(XS)) * s:.1f},{(y - min(YS)) * s:.1f}' for i, (x, y) in enumerate(r))
        camino[c] = camino.get(c, '') + d + 'Z'
    assert len(camino) == NMUN, len(camino)
    out = ''.join(f'<path d="{d}" fill="{color(pct[c]) if c in pct else "var(--otros)"}"><title>{esc(nom.get(c, c))}: '
                  f'{p(pct[c]) if c in pct else "sin datos"} %</title></path>' for c, d in camino.items())
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Voto al PSOE en cada municipio de la provincia de Valencia en 2023" style="max-width:{W}px;margin:0 auto">'
            f'<g stroke="var(--bg)" stroke-width=".4" stroke-linejoin="round">{out}</g></svg>')


g_mapa = figura(f'El PSOE fue el más votado en {GANA["2023_07"]["PSOE"]} de los {NMUN} municipios de la provincia',
                'Porcentaje de voto del PSOE en cada municipio de la provincia de Valencia en las generales de julio de 2023',
                mapa(), 'Fuente: Ministerio del Interior, resultados por municipio, sin voto exterior (CERA).',
                list(zip(ETQ_T, [c for _, c in TRAMOS])),
                (['Municipio', 'PSOE en 2023', 'Diferencia con noviembre de 2019 (puntos)'],
                 [[esc(r.municipio), f'{p(r.psoe)} %', f'{r.dif:+.1f}'.replace('.', ',')] for r in GRANDES.itertuples()]))

# --- Texto ---
EFE = 'https://www.infobae.com/espana/agencias/2026/11/05/la-uco-registra-la-casa-de-abalos-y-pide-informacion-a-adif-sobre-contratos-amanados/'
PUBLICO = 'https://www.publico.es/politica/uco-registra-casa-abalos-24-dias-elecciones-lleva-ano-prision.html'
SUPREMO = 'https://www.elespanol.com/espana/tribunales/20260622/supremo-condena-abalos-anos-prision-liderar-grupo-criminal-koldo-libra-aldama-carcel-ayudar-justicia/1003744278646_0.html'
PAPER = 'https://econpapers.repec.org/RePEc:cup:pscirm:v:4:y:2016:i:02:p:379-397_00'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
s23, s08, s19 = SERIE['2023_07']['PSOE'], SERIE['2008_03']['PSOE'], SERIE['2019_11']['PSOE']
pp23 = SERIE['2023_07']['PP']
gv = GRANDES.iloc[0]
med = MODP['escanos'][1]
assert MODP['escanos'] == [4, 5, 6] and med == 5 == ESC23

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">La UCO de la Guardia Civil registró este jueves la casa de José Luis Ábalos en Valencia y pidió información a Adif en una nueva pieza separada del caso Koldo, que instruye el juez de la Audiencia Nacional Ismael Moreno, según <a href="{EFE}">EFE</a>. Hubo seis detenidos, entre ellos la pareja del exministro, que salieron en libertad por la tarde, según <a href="{PUBLICO}">Público</a>. Ábalos lleva un año en prisión y en junio el Supremo lo condenó a 24 años por liderar una organización criminal, según <a href="{SUPREMO}">El Español</a>.</p>
<p data-tipo="dato">Ábalos fue el número dos de la lista del PSOE por Valencia en las generales de julio de 2023, detrás de Diana Morant, según las candidaturas publicadas en el BOE. Esa lista sacó en la provincia el {p(s23)} % de los votos, su mejor resultado desde 2008 ({p(s08)} %) y {p(s23 - s19)} puntos más que en noviembre de 2019. El PP sacó el {p(pp23)} %. El PSOE sacó {ESC23} de los 16 diputados de la provincia. Tras estallar el caso, en febrero de 2024, Ábalos pasó al Grupo Mixto, y dejó el escaño el 28 de enero de 2026, según el Congreso.</p>
{g_serie}
<p data-tipo="dato">El PSOE fue el más votado en {GANA["2023_07"]["PSOE"]} de los {NMUN} municipios de la provincia, menos que los {GANA["2019_11"]["PSOE"]} de noviembre de 2019, aunque subió en {SUBE} de ellos. Entre los que tienen más de 50.000 electores, donde más votos sacó fue {esc(gv.municipio)}, con el {p(gv.psoe)} %.</p>
{g_mapa}

<h2>El 29N, con otra lista</h2>
<p data-tipo="dato">La lista del PSOE por Valencia para el 29N la encabeza Pilar Bernabé, y de los 16 titulares de 2023 solo repiten {len(REPITEN)}: {", ".join(esc(x) for x in REPITEN[:-1])} y {esc(REPITEN[-1])}. El modelo de Mapa Electoral del 5 de noviembre, hecho con encuestas anteriores al registro, le da en la mediana de las {n(SIMS)} simulaciones {med} escaños, los mismos que en 2023, y entre {MODP["escanos"][0]} y {MODP["escanos"][2]} en el 80 % central. Con {med}, saldrían elegidos de Pilar Bernabé a {esc(L26[med - 1])}, la número {med}.</p>
<p data-tipo="contexto">Pedro Sánchez dijo el jueves que «ninguna de esas personas [las detenidas] tiene nada que ver conmigo», y el portavoz socialista en el Congreso, Patxi López, habló de «qué casualidad que siempre que el PSOE saca cabeza», según <a href="{PUBLICO}">Público</a>.</p>
<blockquote class="cita"><p>«We find that voters ignore corruption when there are side benefits to it, and that punishment is only administered in those cases in which they do not receive compensation» («Los votantes pasan por alto la corrupción cuando les reporta beneficios, y solo la castigan cuando no reciben compensación»).</p><footer>Pablo Fernández-Vázquez, Pablo Barberá y Gonzalo Rivero, con datos de las municipales españolas de 2011, en <a href="{PAPER}">Political Science Research and Methods</a> (2016)</footer></blockquote>
<p data-tipo="hipotesis">Los datos no dicen si el caso Koldo moverá votos en Valencia. En 2023, con Ábalos en la lista, el PSOE subió en la provincia, pero entonces el caso aún no se había conocido: estalló en febrero de 2024. Las encuestas que use el modelo a partir de ahora serán las primeras que puedan recoger el registro.</p>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">Los porcentajes son sobre votos a candidaturas y sin el voto exterior, como los resultados por municipio. El modelo no es una encuesta de Valencia: aplica a cada provincia la media de las encuestas nacionales con lo que se movió en las europeas de 2024, y su margen es amplio. Nada de esta pieza permite atribuir a un caso judicial un cambio de voto. Las probabilidades de cada candidato, al día, están en las <a href="{BASE}listas-electorales-29n/valencia/">listas de Valencia</a>.</p>'''

preguntas = [
    ('¿Qué puesto ocupaba Ábalos en la lista del PSOE por Valencia?', 'El segundo, detrás de Diana Morant, en las generales de julio de 2023, según las candidaturas proclamadas en el BOE. Dejó el escaño el 28 de enero de 2026.'),
    ('¿Cuánto votó la provincia de Valencia al PSOE en 2023?', f'El {p(s23)} % de los votos a candidaturas, su mejor resultado en unas generales desde 2008, cuando sacó el {p(s08)} %.'),
    ('¿Quién encabeza la lista del PSOE por Valencia el 29N?', f'Pilar Bernabé, según las candidaturas proclamadas en el BOE del 3 de noviembre. De los 16 titulares de 2023 repiten {len(REPITEN)}.'),
]
enlaces = (f'{L("comunitat-valenciana-escanos-29n", "Los 33 escaños valencianos")} · <a href="{BASE}encuestas/valencia/">Encuesta de Valencia</a> · '
           f'{L("comunidad-valenciana-historia-electoral", "La historia electoral de la Comunitat")} · {L("valencia-barrio-a-barrio-29n", "València, barrio a barrio")}')
foot = ('Datos: Ministerio del Interior, generales de 2004 a 2023 por municipio; BOE, candidaturas proclamadas de 2023 y 2026; '
        'Congreso de los Diputados, diputados de la XV legislatura; modelo de encuestas de Mapa Electoral del 5 de noviembre de 2026. '
        'Cálculo: actualidad/src/resumenes/psoe_valencia_abalos.py.')

DATOS = {'SERIE': SERIE, 'GANA': GANA, 'NMUN': NMUN, 'SUBE': SUBE, 'ESC23': ESC23, 'MOD': MODP, 'SIMS': SIMS,
         'REPITEN': REPITEN, 'GRANDES': [[r.municipio, round(r.psoe, 2), round(r.dif, 2)] for r in GRANDES.itertuples()]}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza('psoe-valencia-abalos-municipios-29n', 'El PSOE de Valencia',
      f'La lista del PSOE por Valencia con Ábalos de número dos sacó en 2023 el {p(s23)} %, su mejor resultado desde 2008; el 29N, con Pilar Bernabé, el modelo le da los mismos {med} escaños',
      f'La UCO registró el jueves la casa del exministro en Valencia. En la provincia, el PSOE fue el más votado en {GANA["2023_07"]["PSOE"]} de los {NMUN} municipios en 2023; '
      f'para el 29N, el modelo, con encuestas anteriores al registro, le da en la mediana los mismos {med} escaños que en 2023.',
      '6 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
