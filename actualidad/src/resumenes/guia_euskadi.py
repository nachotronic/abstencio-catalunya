"""«El 29N en Euskadi: guía» (3-11-2026): qué se vota, quién se presenta, qué dicen las encuestas y todo lo que hay en el mapa.

Cifras: censo de consulta del INE para el 29N (data/censo/censo_municipios_2023_2026.csv), candidaturas proclamadas del BOE
(listas-electorales-29n/datos/2026-proclamadas.json), generales de 2023 por municipio (generales-2026/descargas/municipios.csv,
votos a candidaturas sin CERA) y modelo de encuestas del 3-11-2026 (previsiones/datos/publico/), congelado en la pieza.
Uso, desde la raíz: python3 actualidad/src/resumenes/guia_euskadi.py
"""
import sys
import json

import pandas as pd

from comun import BASE, COLOR, RAIZ, esc, figura, n, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
PROV = {'48': 'Bizkaia', '20': 'Gipuzkoa', '01': 'Araba/Álava'}
SLUG = {'48': 'bizkaia', '20': 'gipuzkoa', '01': 'alava'}
F = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'UPYD', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC', 'UCD', 'CDS', 'OTROS']
ETQ = {'PNV': 'PNV', 'PSOE': 'PSOE', 'BILDU': 'EH Bildu', 'PP': 'PP', 'SUMAR': 'Sumar'}

# Censo del 29N
c = pd.read_csv(RAIZ / 'data/censo/censo_municipios_2023_2026.csv', dtype={'mun_code': str})
c = c[c.mun_code.str[:2].isin(PROV)]
CENSO = {k: {'res': int(g.cer_2026.sum()), 'cera': int(g.cera_2026.sum()), 'total': int(g.cer_2026.sum() + g.cera_2026.sum()),
             't23': int(g.cer_2023.sum() + g.cera_2023.sum())} for k, g in c.groupby(c.mun_code.str[:2])}
CT = {k: sum(v[k] for v in CENSO.values()) for k in ('res', 'cera', 'total', 't23')}
assert CT['total'] == 1824886, CT

# Generales de 2023
m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str})
# Esta pieza suma una lista fija de familias: las listas propias de 2019-N y 2023 (mapa_listas_propias.py) vuelven a
# «Otros», como cuando se publicó (en estos municipios no gana ninguna).
sys.path.insert(0, str(RAIZ / 'generales-2026' / 'src'))
from partidos import sin_listas_propias_mun  # noqa: E402
m = sin_listas_propias_mun(m)
m = m[m.mun_code.str[:2].isin(PROV)]
R23 = {}
for k, g in list(m.groupby(m.mun_code.str[:2])) + [('PV', m)]:
    v = {f: float(g[f'2023_07_v{f}'].sum()) for f in F}
    t = sum(v.values())
    R23[k] = {f: round(v[f] / t * 100, 2) for f in ('PNV', 'PSOE', 'BILDU', 'PP', 'SUMAR')}
    R23[k]['part'] = round(g['2023_07_votantes'].sum() / g['2023_07_censo'].sum() * 100, 2)
MUN23 = m['2023_07_gana'].value_counts().to_dict()
assert MUN23 == {'BILDU': 140, 'PNV': 76, 'PSOE': 29, 'PP': 6}, MUN23
NMUN = len(m)
assert round(R23['PV']['PSOE'], 1) == 25.4 and round(R23['PV']['PNV'], 1) == 24.2 and round(R23['PV']['BILDU'], 1) == 24.1

# Cabezas de lista (BOE)
L = json.load(open(RAIZ / 'listas-electorales-29n/datos/2026-proclamadas.json'))
SIG = {'EAJ-PNV': 'PNV', 'EH Bildu': 'EH Bildu', 'EH BILDU': 'EH Bildu', 'PSOE': 'PSOE', 'PP': 'PP', 'FA': 'Frente Amplio',
       'FRENTE AMPLIO-FRONTE ZABALA': 'Frente Amplio', 'PODEMOS': 'Podemos', 'VOX': 'Vox'}
CAB = {k: {} for k in PROV}
NCAND = {k: 0 for k in PROV}
for x in L['candidaturas']:
    if x['prov'] in PROV and x['camara'] == 'congreso' and x['titulares']:
        NCAND[x['prov']] += 1
        if x['siglas'] in SIG:
            CAB[x['prov']][SIG[x['siglas']]] = x['titulares'][0]['nombre']
assert CAB['48']['PNV'].startswith('Idoia Sagastizabal') and CAB['20']['EH Bildu'].startswith('Oihana Etxebarrieta'), CAB


# Modelo de encuestas del 3-11-2026
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


MOD = {}
for k in PROV:
    v = esc_['provincias'][k]
    rc = reparto_provincia(v)
    MOD[k] = {'total': v['escanos_total'],
              'listas': {l['lista']: {'voto': l['voto'][1], 'central': rc[l['lista']], 'esc': l['escanos'], 'p1': round(l['p_primera'] * 100, 1)}
                         for l in v['listas'] if rc[l['lista']] or l['escanos'][2]}}
    MOD[k]['primero'] = max(MOD[k]['listas'], key=lambda x: MOD[k]['listas'][x]['p1'])
EUS = {}
for k in PROV:
    for lst, d in MOD[k]['listas'].items():
        if d['central']:
            EUS[lst] = EUS.get(lst, 0) + d['central']
assert EUS == {'EH Bildu': 7, 'PSOE': 5, 'PNV': 4, 'PP': 2}, EUS
ESCT = sum(MOD[k]['total'] for k in PROV)
assert ESCT == 18

# Barrios de Bilbao y páginas de municipio
BAR = sorted(p.name for p in (RAIZ / 'municipio/bizkaia/bilbao').iterdir() if p.is_dir())
NPAG = {k: sum(1 for q in (RAIZ / 'municipio' / SLUG[k]).iterdir() if q.is_dir()) for k in PROV}
assert len(BAR) == 24 and sum(NPAG.values()) == 153, (len(BAR), NPAG)

# --- Gráfico: escaños del reparto central por provincia ---
ORD = ['EH Bildu', 'PNV', 'PSOE', 'PP']


def filas_escanos(W=640, lado=38, gap=6, ml=130):
    out, y = [], 6
    for k in ('48', '20', '01'):
        out.append(f'<text x="{ml - 12}" y="{y + lado / 2 + 6}" text-anchor="end" class="lab" style="font-size:17px">{esc(PROV[k])} · {MOD[k]["total"]}</text>')
        x = ml
        for lst in ORD:
            for _ in range(MOD[k]['listas'].get(lst, {}).get('central', 0)):
                out.append(f'<rect x="{x}" y="{y}" width="{lado}" height="{lado}" rx="4" fill="{COLOR[lst]}"><title>{esc(PROV[k])}: {lst}</title></rect>')
                x += lado + gap
        y += lado + 18
    return f'<svg viewBox="0 0 {W} {y}" role="img" aria-label="Escaños de cada provincia vasca según la media de encuestas">' + ''.join(out) + '</svg>'


g_esc = figura('Los 18 escaños vascos según la media de encuestas',
               'Reparto central de cada provincia en el modelo de Mapa Electoral (3 de noviembre de 2026)',
               filas_escanos(),
               'Fuente: modelo de Mapa Electoral con la media de las encuestas nacionales repartida por provincia. No es una encuesta vasca. '
               'Cifras del día en las páginas de encuestas de cada provincia.', [(x, COLOR[x]) for x in ORD],
               (['Provincia', 'Escaños', 'EH Bildu', 'PNV', 'PSOE', 'PP', 'Primero en más simulaciones'],
                [[PROV[k], str(MOD[k]['total'])] + [str(MOD[k]['listas'].get(x, {}).get('central', 0)) for x in ORD]
                 + [f'{MOD[k]["primero"]} ({n(MOD[k]["listas"][MOD[k]["primero"]]["p1"])} %)'] for k in ('48', '20', '01')]))

tabla_cab = ('<figure>\n<figcaption><span class="t">Quién encabeza cada lista</span><span class="s">Número uno de las principales candidaturas al Congreso, según el BOE</span></figcaption>\n'
             '<div class="tbl"><table><thead><tr><th>Partido</th>' + ''.join(f'<th>{PROV[k]}</th>' for k in ('48', '20', '01')) + '</tr></thead><tbody>'
             + ''.join(f'<tr><td>{x}</td>' + ''.join(f'<td>{esc(CAB[k].get(x, "–"))}</td>' for k in ('48', '20', '01')) + '</tr>'
                       for x in ('PNV', 'EH Bildu', 'PSOE', 'PP', 'Frente Amplio', 'Podemos', 'Vox'))
             + '</tbody></table></div>\n<div class="src">Fuente: BOE, candidaturas proclamadas para las elecciones generales del 29 de noviembre de 2026. '
             'Todas las listas, puesto a puesto, en las páginas de listas de cada provincia.</div>\n</figure>\n')

LK = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
MU = lambda path, t: f'<a href="{BASE}municipio/{path}/">{t}</a>'
DATOS = {'CENSO': CENSO, 'CT': CT, 'R23': R23, 'MUN23': MUN23, 'NMUN': NMUN, 'MOD': MOD, 'EUS': EUS, 'NPAG': NPAG, 'NBAR': len(BAR), 'ESCT': ESCT}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
mb, mg, ma = MOD['48']['listas'], MOD['20']['listas'], MOD['01']['listas']

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="dato">El 29 de noviembre, Euskadi elige {ESCT} de los 350 diputados del Congreso: {MOD["48"]["total"]} por Bizkaia, {MOD["20"]["total"]} por Gipuzkoa y {MOD["01"]["total"]} por Araba/Álava. Pueden votar {n(CT["total"])} personas, {n(CT["total"] - CT["t23"])} más que en 2023: {n(CT["res"])} viven en el País Vasco y {n(CT["cera"])} en el extranjero. Esta guía reúne lo que hay en Mapa Electoral sobre las elecciones en Euskadi, de las listas y las encuestas a los resultados de cada municipio y cada barrio.</p>
<p data-tipo="contexto">Además, cada territorio elige cuatro senadores, doce en total. En el Senado cada elector marca hasta tres nombres, y los cuatro más votados de la provincia salen elegidos.</p>

<h2>Qué dicen las encuestas</h2>
<p data-tipo="dato">Con la media de las encuestas nacionales repartida por provincia, el reparto central de nuestro modelo da {EUS["EH Bildu"]} escaños a EH Bildu, {EUS["PSOE"]} al PSOE, {EUS["PNV"]} al PNV y {EUS["PP"]} al PP. Es una proyección con un margen amplio: a 26 días de la votación, el error típico de la media es de unos cuatro puntos para un partido del 30 %.</p>
{g_esc}
<p data-tipo="dato">Gipuzkoa es la provincia más clara: EH Bildu queda primero en el {n(mg["EH Bildu"]["p1"])} % de las simulaciones, con el {p(mg["EH Bildu"]["voto"])} % estimado. En Araba/Álava, el PSOE queda primero en el {n(ma["PSOE"]["p1"])} %. Bizkaia es un empate a tres: EH Bildu y el PNV tienen el {p(mb["EH Bildu"]["voto"])} % estimado cada uno y el PSOE el {p(mb["PSOE"]["voto"])} %, y lo explicamos en {LK("bizkaia-pnv-bildu-encuestas-29n", "la pieza sobre el feudo del PNV")}. Las cifras se actualizan cada día en las encuestas de <a href="{BASE}encuestas/bizkaia/">Bizkaia</a>, <a href="{BASE}encuestas/gipuzkoa/">Gipuzkoa</a> y <a href="{BASE}encuestas/alava/">Araba/Álava</a>.</p>

<h2>Quién se presenta</h2>
<p data-tipo="dato">El BOE publicó {NCAND["48"]} candidaturas al Congreso por Bizkaia, {NCAND["20"]} por Gipuzkoa y {NCAND["01"]} por Araba/Álava. Estas son las cabezas de lista de los partidos con más opciones:</p>
{tabla_cab}
<p data-tipo="contexto">Cada candidato, con su probabilidad de salir elegido según la media de encuestas, está en las listas de <a href="{BASE}listas-electorales-29n/bizkaia/">Bizkaia</a>, <a href="{BASE}listas-electorales-29n/gipuzkoa/">Gipuzkoa</a> y <a href="{BASE}listas-electorales-29n/alava/">Araba/Álava</a>. Si quieres saber quién te representa ahora, prueba <a href="{BASE}listas-electorales-29n/mi-diputado/">¿Quién es mi diputado?</a></p>

<h2>Cómo votó Euskadi en 2023</h2>
<p data-tipo="dato">En las generales de julio de 2023, el PSOE fue el más votado en el País Vasco con el {p(R23["PV"]["PSOE"])} % de los votos a candidaturas, por delante del PNV ({p(R23["PV"]["PNV"])} %) y EH Bildu ({p(R23["PV"]["BILDU"])} %). Fue el empate a tres más ajustado desde 1977, como contamos en {LK("euskadi-empate-a-tres", "Euskadi, empate a tres")}. Cada territorio votó distinto: el PNV ganó en Bizkaia ({p(R23["48"]["PNV"])} %), EH Bildu en Gipuzkoa ({p(R23["20"]["BILDU"])} %) y el PSOE en Araba/Álava ({p(R23["01"]["PSOE"])} %).</p>
<p data-tipo="dato">Municipio a municipio, el mapa es otro: EH Bildu fue el más votado en {MUN23["BILDU"]} de los {NMUN} municipios vascos, el PNV en {MUN23["PNV"]}, el PSOE en {MUN23["PSOE"]} y el PP en {MUN23["PP"]}. La historia completa, de 1977 a hoy, está en {LK("pais-vasco-historia-electoral", "¿Quién gobierna País Vasco?")}.</p>

<h2>Tu municipio y tu barrio</h2>
<p data-tipo="dato">Los {sum(NPAG.values())} municipios vascos de más de 1.000 habitantes tienen página propia, con el censo del 29N, los resultados por sección censal, el voto por renta y la serie desde 1977: {NPAG["48"]} en <a href="{BASE}municipio/bizkaia/">Bizkaia</a>, {NPAG["20"]} en <a href="{BASE}municipio/gipuzkoa/">Gipuzkoa</a> y {NPAG["01"]} en <a href="{BASE}municipio/alava/">Araba/Álava</a>. Las capitales: {MU("bizkaia/bilbao", "Bilbao")}, {MU("gipuzkoa/donostia-san-sebastian", "Donostia/San Sebastián")} y {MU("alava/vitoria-gasteiz", "Vitoria-Gasteiz")}. Bilbao tiene además una página para cada uno de sus {len(BAR)} barrios, de {MU("bizkaia/bilbao/abando", "Abando")} a {MU("bizkaia/bilbao/otxarkoaga", "Otxarkoaga")}.</p>
<p data-tipo="contexto">Para ver tu calle, el <a href="{BASE}?m=48020">mapa por sección censal</a> se abre en Bilbao y deja buscar cualquier dirección. Y para el día de la votación: <a href="{BASE}elecciones/votar-29n/">cómo y dónde votar</a>, el <a href="{BASE}elecciones/voto-por-correo-29n/">voto por correo</a> y qué hacer si te ha tocado <a href="{BASE}elecciones/mesa-electoral-29n/">formar parte de una mesa</a>.</p>

<h2>Las piezas sobre Euskadi</h2>
<ul>
<li>{LK("bizkaia-pnv-bildu-encuestas-29n", "El PNV ganó en 92 municipios de Bizkaia en 2019 y en 55 en 2023")}</li>
<li>{LK("derbi-vasco-bilbao-donostia-29n", "El derbi en las urnas: Bilbao y Donostia, sección a sección")}</li>
<li>{LK("euskadi-empate-a-tres", "Tres partidos en 1,3 puntos: el empate a tres de Euskadi en 2023")}</li>
<li>{LK("pais-vasco-historia-electoral", "Historia electoral del País Vasco desde 1977")}</li>
<li>{LK("pnv-cinco-pueblos-bermeo", "Los cinco pueblos más del PNV")}</li>
<li>{LK("bildu-cinco-pueblos-lizartza", "Los cinco pueblos más de EH Bildu")}</li>
<li>{LK("frontera-renta-pp-junts-pnv-29n", "La frontera de la renta: PP, Junts y PNV")}</li>
</ul>
<p data-tipo="contexto">Las páginas de comunidad y de provincia, con todos los datos de cada territorio: <a href="{BASE}elecciones/pais-vasco/">País Vasco (Euskadi)</a>, <a href="{BASE}elecciones/pais-vasco/bizkaia/">Bizkaia</a>, <a href="{BASE}elecciones/pais-vasco/gipuzkoa/">Gipuzkoa</a> y <a href="{BASE}elecciones/pais-vasco/alava/">Araba/Álava</a>.</p>'''

preguntas = [
    ('¿Cuántos diputados elige el País Vasco el 29N?', f'{ESCT}: {MOD["48"]["total"]} Bizkaia, {MOD["20"]["total"]} Gipuzkoa y {MOD["01"]["total"]} Araba/Álava. Además, cada territorio elige cuatro senadores.'),
    ('¿Cuántas personas pueden votar en Euskadi el 29N?', f'{n(CT["total"])} según el censo de consulta del INE: {n(CT["res"])} residentes en el País Vasco y {n(CT["cera"])} en el extranjero.'),
    ('¿Quién ganará en Euskadi según las encuestas?', f'En la media de encuestas de Mapa Electoral del 3 de noviembre, EH Bildu sería el partido con más escaños vascos ({EUS["EH Bildu"]}), por delante del PSOE ({EUS["PSOE"]}), el PNV ({EUS["PNV"]}) y el PP ({EUS["PP"]}). Bizkaia está en empate a tres.'),
]
enlaces = (f'<a href="{BASE}elecciones/pais-vasco/">Elecciones en País Vasco (Euskadi)</a> · <a href="{BASE}encuestas/">Encuestas del 29N</a> · '
           f'<a href="{BASE}listas-electorales-29n/">Listas del 29N</a> · {LK("bizkaia-pnv-bildu-encuestas-29n", "Bizkaia, el feudo del PNV")}')
foot = ('Datos: INE, censo de consulta del 29N; BOE, candidaturas proclamadas; Ministerio del Interior, generales de 2023 por municipio '
        '(votos a candidaturas, sin voto exterior); modelo de encuestas de Mapa Electoral del 3 de noviembre de 2026. Cálculo: actualidad/src/resumenes/guia_euskadi.py.')

pieza('euskadi-29n-guia', 'El 29N en Euskadi: guía',
      f'Elecciones del 29N en Euskadi: {ESCT} escaños, {n(CT["total"])} electores y una Bizkaia en empate a tres',
      f'Qué se vota, quién encabeza las listas, qué dicen las encuestas y cómo votó cada municipio en 2023. Con la media de encuestas, '
      f'EH Bildu sacaría {EUS["EH Bildu"]} de los {ESCT} escaños vascos; Bizkaia, con {MOD["48"]["total"]}, está en el aire.',
      '3 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
