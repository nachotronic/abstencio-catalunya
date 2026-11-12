"""«Los 33 escaños de la Comunitat Valenciana» (5-11-2026): PP y Vox ya sumaron 18 de 33 en 2023; con la media de
encuestas del 3-11 pasan a 20 en la mediana, y el último escaño de Castellón se lo disputan PSOE, Compromís y Vox.

Cifras de 2023: generales por municipio (generales-2026/descargas/municipios.csv), porcentaje sobre votos a
candidaturas y sin voto exterior (CERA). Escaños de 2023: diputados de la XV legislatura por circunscripción
(listas-electorales-29n/datos/diputados-xv.json, sin bajas posteriores).
Modelo: escenario base publicado del 3-11-2026 (previsiones/datos/publico/escenario-base.json) y, para la suma de la
Comunitat y los repartos más probables, datos/cv_modelo_20261103.json, que escribe
/mnt/project-files/actualidad/comunitat-valenciana-2026/analisis.py reproduciendo el escenario con sus semillas
(comprueba que el regenerado es idéntico al publicado). Probabilidad de cada puesto: listas-electorales-29n/datos/puestos-29n.json.
En la Comunitat, la lista «Sumar» del modelo es Compromís-Front Valencià (Compromís, Podem, EUPV y ERPV): el modelo le
da la cuota de Sumar más la de Podemos (previsiones/src/motor.py, PODEMOS_CON_FA).
Uso, desde la raíz: python3 actualidad/src/resumenes/comunitat_valenciana.py
"""
import sys
import collections
import json
import math

import pandas as pd

from comun import BASE, COLOR, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
COMP = '#e8850c'   # Compromís, naranja
F = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'UPYD', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC', 'UCD', 'CDS', 'OTROS']
PROV = {'46': 'Valencia', '03': 'Alicante', '12': 'Castellón'}
CIRC = {'46': 'Valencia/València', '03': 'Alicante/Alacant', '12': 'Castellón/Castelló'}
ESC = {'46': 16, '03': 12, '12': 5}

m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str})
# Esta pieza suma una lista fija de familias: las listas propias de 2019-N y 2023 (mapa_listas_propias.py) vuelven a
# «Otros», como cuando se publicó (en estos municipios no gana ninguna).
sys.path.insert(0, str(RAIZ / 'generales-2026' / 'src'))
from partidos import sin_listas_propias_mun  # noqa: E402
m = sin_listas_propias_mun(m)
m = m[m.mun_code.str[:2].isin(PROV)].copy()
m['prov'] = m.mun_code.str[:2]
NMUN = len(m)
assert NMUN == 542, NMUN

# 2023 por provincia y en la Comunitat
V23, P23 = {}, {}
for c in list(PROV) + ['CV']:
    d = m if c == 'CV' else m[m.prov == c]
    v = {f: int(d[f'2023_07_v{f}'].sum()) for f in F}
    T = sum(v.values())
    V23[c] = v
    P23[c] = {k: round(v[k] / T * 100, 2) for k in ('PP', 'PSOE', 'VOX', 'SUMAR')}
dips = json.load(open(RAIZ / 'listas-electorales-29n/datos/diputados-xv.json'))['diputados']
E23 = {}
for c in PROV:
    xs = [x for x in dips if x['circ'] == CIRC[c] and (not x['baja'] or x['baja'].startswith('06/10/2026'))]
    E23[c] = dict(collections.Counter(x['formacion'] for x in xs))
    assert sum(E23[c].values()) == ESC[c], (c, E23[c])
E23['CV'] = dict(sum((collections.Counter(E23[c]) for c in PROV), collections.Counter()))
assert E23['CV'] == {'PP': 13, 'PSOE': 11, 'VOX': 5, 'SUMAR': 4}, E23['CV']
GAN = collections.Counter(m['2023_07_gana'])
assert sum(GAN.values()) == NMUN

# Modelo del 3-11
ESCB = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))['provincias']
meta = json.load(open(RAIZ / 'previsiones/datos/publico/meta.json'))
assert meta['generado'] == '2026-11-03'
MOD = {c: {l['lista']: {'voto': l['voto'], 'esc': l['escanos'], 'p1': round(l['p_primera'] * 100)} for l in ESCB[c]['listas']} for c in PROV}
CVM = json.load(open(RAIZ / 'actualidad/src/resumenes/datos/cv_modelo_20261103.json'))
SIMS = meta['simulaciones']
PU = json.load(open(RAIZ / 'listas-electorales-29n/datos/puestos-29n.json'))
assert PU['modelo'] == '2026-11-03'
PU = {c: PU['puestos'][c] for c in PROV}
MEDIA = {c: {k: CVM[c]['media'][k] for k in ('PP', 'PSOE', 'Vox', 'Sumar')} for c in PROV}
MEDIA['CV'] = CVM['CV']['media']
PPVOX = {'med': CVM['CV']['ppvox_med'], 'izq': CVM['CV']['izq_med'], 'may': round(CVM['CV']['ppvox_mayoria_17'] * 100, 1),
         'p10': CVM['CV']['ppvox_p10_p90'][0], 'p90': CVM['CV']['ppvox_p10_p90'][1]}
REP = {c: CVM[c]['repartos'][:4] for c in PROV}
# los escaños en el aire: puestos entre el 10 % y el 90 %
AIRE = {c: sorted([(k, i + 1, round(q * 100, 1)) for k, qs in PU[c].items() for i, q in enumerate(qs) if 0.1 <= q < 0.9],
                  key=lambda t: -t[2]) for c in PROV}

# Cabezas y números de las listas proclamadas (BOE del 3-11)
pro = json.load(open(RAIZ / 'listas-electorales-29n/datos/2026-proclamadas.json'))['candidaturas']
LISTA = {}
for c in pro:
    if c['prov'] in PROV and c['camara'] == 'congreso' and c['titulares']:
        k = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'COMPROMIS-EUPV-PODEM-ERPV': 'Sumar'}.get(c['siglas'])
        if k:
            LISTA[(c['prov'], k)] = [t['nombre'] for t in c['titulares']]
assert LISTA[('12', 'Sumar')][0] == 'Ignasi García Felip' and LISTA[('12', 'PSOE')][1] == 'Sergio Bou Ayza'
assert LISTA[('12', 'Vox')][1] == 'María de los Llanos Massó Linares' and LISTA[('46', 'PP')][0] == 'María José Catalá Verdet'
NOMBRE = {'Sumar': 'Compromís', 'PP': 'PP', 'PSOE': 'PSOE', 'Vox': 'Vox'}
COLL = {'PP': COLOR['PP'], 'PSOE': COLOR['PSOE'], 'Vox': COLOR['Vox'], 'Sumar': COMP}

# --- Mapa de municipios de 2023 ---
G = json.load(open(RAIZ / 'generales-2026/data/municipios.json'))
COLM = {'PSOE': COLOR['PSOE'], 'PP': COLOR['PP'], 'VOX': COLOR['Vox'], 'SUMAR': COLOR['Sumar'], 'EMPATE': '#8a8486'}
ETQ = {'PSOE': 'PSOE', 'PP': 'PP', 'VOX': 'Vox', 'SUMAR': 'Sumar', 'EMPATE': 'Empate a votos'}   # empate: corrección del 10-11-2026
gan = dict(zip(m.mun_code, m['2023_07_gana']))
nom = dict(zip(m.mun_code, m.municipio))


def mapa(W=420):
    S, kx = G['S'], math.cos(math.radians(39.5))
    AN = []
    for c, partes in zip(G['cod'], G['poly']):
        if c[:2] not in PROV:
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
    out = ''.join(f'<path d="{d}" fill="{COLM.get(gan.get(c), "var(--otros)")}"><title>{esc(nom.get(c, c))}: '
                  f'{esc(ETQ.get(gan.get(c), "sin datos"))}</title></path>' for c, d in camino.items())
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Municipios de la Comunitat Valenciana por partido más votado en las generales de 2023" style="max-width:{W}px;margin:0 auto">'
            f'<g stroke="var(--bg)" stroke-width=".4" stroke-linejoin="round">{out}</g></svg>')


g_mapa = figura(f'El PP ganó en {GAN["PP"]} municipios valencianos en 2023 y el PSOE en {GAN["PSOE"]}',
                f'Partido más votado en cada uno de los {NMUN} municipios de la Comunitat Valenciana en las generales de julio de 2023',
                mapa(), 'Fuente: Ministerio del Interior, resultados por municipio, sin voto exterior (CERA).',
                [(ETQ[k], COLM[k]) for k in ('PP', 'PSOE', 'VOX', 'SUMAR', 'EMPATE') if GAN.get(k)],
                (['Partido', 'Municipios'], [[ETQ[k], str(GAN.get(k, 0))] for k in ('PP', 'PSOE', 'VOX', 'SUMAR', 'EMPATE') if k != 'EMPATE' or GAN.get(k)]))


def escanos_svg(W=640):
    """Escaños de 2023 y escaños medios del modelo, por provincia: una fila de cuadrados por provincia y año."""
    lado, gap, ml = 15, 3, 150
    filas = []
    for c in ('46', '03', '12', 'CV'):
        e23 = E23[c]
        filas.append((f'{PROV.get(c, "Comunitat")} · 2023', [(k, e23.get(k2, 0)) for k, k2 in (('PP', 'PP'), ('Vox', 'VOX'), ('PSOE', 'PSOE'), ('Sumar', 'SUMAR'))]))
    H = len(filas) * (lado + 14) + 4
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Escaños de 2023 por provincia">']
    for i, (t, partes) in enumerate(filas):
        y = 4 + i * (lado + 14)
        out.append(f'<text x="{ml - 8}" y="{y + lado - 3}" text-anchor="end" class="lab">{esc(t)}</text>')
        x = ml
        for k, v in partes:
            for _ in range(v):
                out.append(f'<rect x="{x}" y="{y}" width="{lado}" height="{lado}" rx="2" fill="{COLL[k] if k != "Sumar" else COLOR["Sumar"]}"><title>{esc(t)}: {NOMBRE[k] if k != "Sumar" else "Sumar"} {v}</title></rect>')
                x += lado + gap
            x += 6
    out.append('</svg>')
    return ''.join(out)


ORD = ('PP', 'PSOE', 'Vox', 'Sumar')
g_esc = figura('Cuántos escaños tendría cada uno',
               f'Escaños medios en las {n(SIMS)} simulaciones del modelo de Mapa Electoral del 3 de noviembre, frente a los de 2023',
               barras([(f'{NOMBRE[k]}', MEDIA['CV'][k], COLL[k], f'{p(MEDIA["CV"][k])} (en 2023, {E23["CV"][{"Vox": "VOX", "Sumar": "SUMAR"}.get(k, k)]})') for k in ORD],
                      14, 'Escaños medios en la Comunitat Valenciana', ml=110),
               'Fuente: modelo de Mapa Electoral con la media de las encuestas nacionales repartida por provincia; escaños de 2023 del Congreso. '
               'En 2023, la lista de la izquierda del PSOE era Sumar (con Compromís); el 29N es Compromís-Front Valencià (COMPROMIS-EUPV-PODEM-ERPV), con Podem, EUPV y ERPV.',
               None,
               (['Lista', 'Valencia', 'Alicante', 'Castellón', 'Comunitat', 'En 2023'],
                [[NOMBRE[k]] + [p(MEDIA[c][k]) for c in ('46', '03', '12', 'CV')] + [str(E23['CV'][{'Vox': 'VOX', 'Sumar': 'SUMAR'}.get(k, k)])] for k in ORD]))

ORDINAL = {1: 'primero', 2: 'segundo', 3: 'tercero', 4: 'cuarto', 5: 'quinto', 6: 'sexto', 7: 'séptimo'}
NUM = {5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve'}
DE = {'PP': 'del PP', 'PSOE': 'del PSOE', 'Vox': 'de Vox', 'Sumar': 'de Compromís'}
AIRE_FILAS = [(f'{NOMBRE[k]} n.º {i} · {PROV[c]}', v, COLL[k], f'{p(v)} %') for c in ('12', '03', '46') for k, i, v in AIRE[c]]
g_aire = figura('Los escaños que están en el aire',
                'Puestos de cada lista que salen elegidos entre el 10 % y el 90 % de las simulaciones (modelo del 3 de noviembre)',
                barras(AIRE_FILAS, 100, 'Probabilidad de los puestos en el aire', ml=210, alto=24),
                'Fuente: modelo de Mapa Electoral. Probabilidad de que la lista saque al menos tantos escaños como el puesto. '
                'Las de cada candidato están en las <a href="' + BASE + 'listas-electorales-29n/">listas del 29N</a>.', None,
                (['Provincia', 'Lista', 'Puesto', 'Candidato', 'Probabilidad'],
                 [[PROV[c], NOMBRE[k], str(i), LISTA[(c, k)][i - 1], f'{p(v)} %'] for c in ('12', '03', '46') for k, i, v in AIRE[c]]))

DATOS = {'SIMS': SIMS, 'NMUN': NMUN, 'GAN': dict(GAN), 'P23': P23, 'E23': E23, 'MEDIA': MEDIA, 'PPVOX': PPVOX, 'AIRE': AIRE,
         'REP': REP, 'MOD': MOD}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
EP_CATALA = 'https://www.pressdigital.es/articulo/politica/2026-10-26/6066501-catala-sobre-cabeza-lista-pp-congreso-ante-duda-valencia-siempre-sera-primero'
COMP_ACUERDO = 'https://actualidadcastellon.com/coalicion-compromis-front-valencia-acuerdo-historico/'
SYM = 'https://www.elperiodicodeaqui.com/politica/encuesta-elecciones-generales-comunitat-valenciana_100123203_102.html'
ESQUER = 'https://dialnet.unirioja.es/descarga/articulo/7038484.pdf'
LV = lambda c: f'<a href="{BASE}listas-electorales-29n/{ {"46": "valencia", "03": "alicante", "12": "castellon"}[c]}/">{PROV[c]}</a>'

cas = {k: next(v for kk, i, v in AIRE['12'] if kk == k) for k in ('PP', 'PSOE', 'Sumar', 'Vox')}
assert [(k, i) for k, i, _ in AIRE['12']] == [('PP', 2), ('PSOE', 2), ('Sumar', 1), ('Vox', 2)], AIRE['12']
r12 = REP['12']
assert r12[0][0] == {'PP': 2, 'PSOE': 2, 'Vox': 1} and r12[1][0] == {'PP': 2, 'PSOE': 1, 'Vox': 1, 'Sumar': 1}
ppvox23 = E23['CV']['PP'] + E23['CV']['VOX']
assert ppvox23 == 18 and PPVOX['med'] == 20

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="dato">La Comunitat Valenciana elige 33 de los 350 diputados del Congreso: 16 por Valencia, 12 por Alicante y 5 por Castellón. En las generales de julio de 2023, el PP sacó {E23["CV"]["PP"]}, el PSOE {E23["CV"]["PSOE"]}, Vox {E23["CV"]["VOX"]} y Sumar, que iba con Compromís, {E23["CV"]["SUMAR"]}. PP y Vox sumaron {ppvox23}, uno más de los 17 de la mayoría. El PP fue el más votado en {GAN["PP"]} de los {NMUN} municipios valencianos y el PSOE en {GAN["PSOE"]}; en otros cuatro, los dos empataron a votos.</p>
{g_mapa}
<p data-tipo="dato">Con la media de encuestas del 3 de noviembre, nuestro modelo, que reparte el voto nacional por provincia y simula {n(SIMS)} resultados, da a PP y Vox {PPVOX["med"]:.0f} de los 33 escaños valencianos en la mediana, dos más que en 2023, y al PSOE y a Compromís-Front Valencià {PPVOX["izq"]:.0f}. En el {p(PPVOX["may"])} % de las simulaciones, PP y Vox llegan al menos a 17, la mitad más uno. Por partidos, el PP saca de media {p(MEDIA["CV"]["PP"])} escaños, el PSOE {p(MEDIA["CV"]["PSOE"])}, Vox {p(MEDIA["CV"]["Vox"])} y Compromís {p(MEDIA["CV"]["Sumar"])}.</p>
{g_esc}
<p data-tipo="contexto">La encuesta de SyM Consulting para <a href="{SYM}">El Periódico de Aquí</a>, hecha del 6 al 16 de octubre, da 18 escaños a PP y Vox y 15 al PSOE y a Compromís: el PP, 12; el PSOE, 10; Vox, 6, y Compromís-Front Valencià, 5. El periódico advierte de que se hizo antes del accidente ferroviario de Urda (Toledo) y de los disturbios en Barcelona y Bilbao.</p>

<h2>Castellón: dos escaños para cuatro candidatos</h2>
<p data-tipo="dato">El reparto más ajustado está en {LV("12")}, que elige cinco diputados. El primero del PP, del PSOE y de Vox salen casi siempre. Los otros dos se los disputan cuatro candidatos: Óscar Clavell, número dos del PP, sale en el {p(cas["PP"])} % de las simulaciones; Sergio Bou, número dos del PSOE, en el {p(cas["PSOE"])} %; Ignasi García, cabeza de lista de Compromís, en el {p(cas["Sumar"])} %, y Llanos Massó, número dos de Vox, en el {p(cas["Vox"])} %. El reparto más probable, en el {p(r12[0][1] * 100)} % de las simulaciones, es el de 2023: dos del PP, dos del PSOE y uno de Vox. El siguiente, en el {p(r12[1][1] * 100)} %, cambia el segundo del PSOE por uno de Compromís.</p>
{g_aire}
<p data-tipo="dato">En {LV("03")} hay cinco puestos entre el 10 % y el 90 % de las simulaciones: {", ".join(f"el {ORDINAL[i]} {DE[k]} ({p(v)} %)" for k, i, v in AIRE["03"][:-1])} y el {ORDINAL[AIRE["03"][-1][1]]} {DE[AIRE["03"][-1][0]]} ({p(AIRE["03"][-1][2])} %). En {LV("46")}, la provincia que más diputados elige, hay {NUM[len(AIRE["46"])]}; los más disputados son el {ORDINAL[AIRE["46"][3][1]]} {DE[AIRE["46"][3][0]]} ({p(AIRE["46"][3][2])} %) y el {ORDINAL[AIRE["46"][4][1]]} {DE[AIRE["46"][4][0]]} ({p(AIRE["46"][4][2])} %).</p>
<p data-tipo="dato">Dentro de cada bloque, el modelo mueve más que entre bloques: Vox pasa de {E23["CV"]["VOX"]} escaños a una media de {p(MEDIA["CV"]["Vox"])} y el PP baja de {E23["CV"]["PP"]} a {p(MEDIA["CV"]["PP"])}; el PSOE baja de {E23["CV"]["PSOE"]} a {p(MEDIA["CV"]["PSOE"])} y Compromís se queda en {p(MEDIA["CV"]["Sumar"])}, como los {E23["CV"]["SUMAR"]} de Sumar en 2023.</p>
<p data-tipo="hipotesis">Es una estimación con la media nacional de encuestas repartida por provincia, no una encuesta valenciana, y no mide a Compromís por separado: le da la cuota de Sumar y Podemos. Si Compromís-Front Valencià rinde mejor que esa suma, como apunta SyM, los escaños en el aire de Castellón y Alicante serían los primeros en moverse.</p>

<h2>Las listas</h2>
<p data-tipo="contexto">La alcaldesa de València, María José Catalá, encabeza la lista del PP por Valencia. «Ante la duda, València siempre será lo primero», dijo sobre su candidatura en declaraciones a <a href="{EP_CATALA}">Europa Press Televisión</a>; añadió que «hay mucho en juego». A la izquierda del PSOE, Compromís, Podem, Esquerra Unida y Esquerra Republicana del País Valencià cerraron in extremis una coalición, Compromís-Front Valencià, que Àgueda Micó calificó de «histórico en la Comunitat Valenciana», según <a href="{COMP_ACUERDO}">Actualidad Castellón</a>.</p>
<blockquote class="cita"><p>«El conocimiento por parte de los ciudadanos de los candidatos que aparecen en las candidaturas, exceptuando quizás el cabeza de lista, es mínimo».</p><footer>Carlos Fernández Esquer, politólogo (UAM), en <a href="{ESQUER}">Apuntes Electorales</a> (2019)</footer></blockquote>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">Los porcentajes de 2023 son sobre votos a candidaturas y sin el voto exterior, como los resultados por municipio; los escaños son los oficiales. El modelo no es una encuesta de la Comunitat: aplica a cada provincia la media de las encuestas nacionales con lo que se movió en las europeas de 2024, y su margen es amplio a 24 días de la votación. Un escaño «en el aire» no quiere decir que esté empatado, sino que en las simulaciones sale unas veces sí y otras no. Las probabilidades de cada candidato, al día, están en las <a href="{BASE}listas-electorales-29n/">listas del 29N</a>.</p>'''

preguntas = [
    ('¿Cuántos diputados elige la Comunitat Valenciana el 29N?', '33: 16 por Valencia, 12 por Alicante y 5 por Castellón, los mismos que en 2023.'),
    ('¿Qué dicen las encuestas del 29N en la Comunitat Valenciana?', f'Con la media de encuestas de Mapa Electoral del 3 de noviembre, PP y Vox suman {PPVOX["med"]:.0f} de los 33 escaños en la mediana de las simulaciones, y el PSOE y Compromís, {PPVOX["izq"]:.0f}. La encuesta de SyM Consulting de octubre les da 18 y 15.'),
    ('¿Quién encabeza las listas por Valencia?', f'{esc(LISTA[("46", "PP")][0])} por el PP, {esc(LISTA[("46", "PSOE")][0])} por el PSOE, {esc(LISTA[("46", "Vox")][0])} por Vox y {esc(LISTA[("46", "Sumar")][0])} por Compromís-Front Valencià, según las candidaturas proclamadas en el BOE del 3 de noviembre.'),
]
enlaces = (f'<a href="{BASE}encuestas/valencia/">Encuesta de Valencia</a> · <a href="{BASE}encuestas/alicante/">de Alicante</a> · '
           f'<a href="{BASE}encuestas/castellon/">de Castellón</a> · {L("comunidad-valenciana-historia-electoral", "La historia electoral de la Comunitat")} · '
           f'{L("valencia-barrio-a-barrio-29n", "València, barrio a barrio")} · {L("dana-pueblos-primeras-generales-29n", "Los pueblos de la DANA")}')
foot = ('Datos: Ministerio del Interior, generales de 2023 por municipio; Congreso de los Diputados, diputados de la XV legislatura; '
        'BOE del 3 de noviembre de 2026, candidaturas proclamadas; modelo de encuestas de Mapa Electoral del 3 de noviembre de 2026. '
        'Cálculo: actualidad/src/resumenes/comunitat_valenciana.py.')

pieza('comunitat-valenciana-escanos-29n', 'Los 33 escaños valencianos',
      f'PP y Vox pasarían de {ppvox23} a {PPVOX["med"]:.0f} de los 33 escaños valencianos con la media de encuestas; en Castellón, dos se los disputan cuatro candidatos',
      f'Con la media de encuestas del 3 de noviembre, Vox subiría de {E23["CV"]["VOX"]} a {p(MEDIA["CV"]["Vox"])} escaños de media en la Comunitat Valenciana y el PSOE bajaría de {E23["CV"]["PSOE"]} a {p(MEDIA["CV"]["PSOE"])}. '
      f'En Castellón, el segundo del PSOE sale en el {p(cas["PSOE"])} % de las simulaciones y el cabeza de lista de Compromís, en el {p(cas["Sumar"])} %.',
      '5 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
