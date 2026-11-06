"""«Moreno y Feijóo en Andalucía» (6-11-2026): en las autonómicas del 17 de mayo de 2026, el PP de Juanma Moreno sacó
casi 150.000 votos más que el PP en las generales de julio de 2023, con unos 194.000 votantes menos. Para el 29N, el
modelo da al PP en cada provincia andaluza menos voto que en 2023.

Autonómicas de 2026: resultados por municipio de la Junta de Andalucía (resultadoseleccionesandalucia.es), tabla de
/mnt/project-files/psoe-adelante/muni_22_26.csv (analisis.py, a partir de mun_202605.json), copiada en
datos/andalucia_autonomicas_2026.csv (solo las columnas usadas). Porcentajes sobre votos a candidaturas.
Generales de 2023: generales-2026/descargas/municipios.csv, sin voto exterior (CERA). Escaños de 2023: diputados de la
XV legislatura elegidos en julio de 2023. Modelo: escenario base publicado del 5-11-2026.
Uso, desde la raíz: python3 actualidad/src/resumenes/pp_andalucia_moreno.py
"""
import collections
import json
import math

import pandas as pd

from comun import BASE, COLOR, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
F = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'UPYD', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC', 'UCD', 'CDS', 'OTROS']
PROV = {'04': 'Almería', '11': 'Cádiz', '14': 'Córdoba', '18': 'Granada', '21': 'Huelva', '23': 'Jaén', '29': 'Málaga', '41': 'Sevilla'}
CIRC = {'04': 'Almería', '11': 'Cádiz', '14': 'Córdoba', '18': 'Granada', '21': 'Huelva', '23': 'Jaén', '29': 'Málaga', '41': 'Sevilla'}

aut = pd.read_csv(RAIZ / 'actualidad/src/resumenes/datos/andalucia_autonomicas_2026.csv', dtype={'mun_code': str})
m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str})
m = m[m.mun_code.str[:2].isin(PROV)].copy()
NMUN = len(m)
assert NMUN == len(aut) == 785, (NMUN, len(aut))
m['tot23'] = sum(m[f'2023_07_v{f}'] for f in F)
x = aut.merge(m[['mun_code', 'municipio', 'tot23', '2023_07_vPP', '2023_07_votantes', '2023_07_censo']], on='mun_code', how='left')
assert x['2023_07_vPP'].notna().all()
x['prov'] = x.mun_code.str[:2]
x['dif'] = x.v_PP26 - x['2023_07_vPP']

def resumen(g):
    return {'pp26': int(g.v_PP26.sum()), 'pp23': int(g['2023_07_vPP'].sum()),
            'pct26': round(g.v_PP26.sum() / g.votoscandidatura26.sum() * 100, 2),
            'pct23': round(g['2023_07_vPP'].sum() / g.tot23.sum() * 100, 2),
            'vot26': int(g.votostotales26.sum()), 'vot23': int(g['2023_07_votantes'].sum()),
            'mas': int((g.dif > 0).sum()), 'n': len(g)}

R = {c: resumen(x[x.prov == c]) for c in PROV}
R['AN'] = resumen(x)
AN = R['AN']
DIFV, DIFVOT = AN['pp26'] - AN['pp23'], AN['vot23'] - AN['vot26']
assert 149000 < DIFV < 151000 and 194000 < DIFVOT < 195000 and AN['mas'] == 603, (DIFV, DIFVOT, AN['mas'])
MENOS = [c for c in PROV if R[c]['pp26'] < R[c]['pp23']]
assert MENOS == ['04'], MENOS
MAXP = max(PROV, key=lambda c: R[c]['pp26'] - R[c]['pp23'])
assert MAXP == '41'
GRANDES = x[x['2023_07_censo'] >= 100000].sort_values('dif', ascending=False)

# Escaños del PP en 2023 y modelo del 5-11
dips = json.load(open(RAIZ / 'listas-electorales-29n/datos/diputados-xv.json'))['diputados']
E23 = {c: collections.Counter(d['formacion'] for d in dips if d['circ'] == CIRC[c] and d['alta'].endswith('/08/2023')) for c in PROV}
ESC = {'04': 6, '11': 9, '14': 6, '18': 7, '21': 5, '23': 5, '29': 11, '41': 12}
for c in PROV:
    assert sum(E23[c].values()) == ESC[c], (c, E23[c])
PP23 = sum(E23[c]['PP'] for c in PROV)
assert sum(ESC.values()) == 61
meta = json.load(open(RAIZ / 'previsiones/datos/publico/meta.json'))
assert meta['generado'] == '2026-11-05', meta['generado']
SIMS = meta['simulaciones']
ESCB = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))['provincias']
MOD = {c: next(l for l in ESCB[c]['listas'] if l['lista'] == 'PP') for c in PROV}
MEDV = {c: MOD[c]['voto'][1] for c in PROV}
MEDE = {c: MOD[c]['escanos'][1] for c in PROV}
assert all(MEDV[c] < R[c]['pct23'] < R[c]['pct26'] for c in PROV), {c: (R[c]['pct23'], MEDV[c], R[c]['pct26']) for c in PROV}

# --- Gráficos ---
CLARO = '#9fc4ea'
ORDEN = sorted(PROV, key=lambda c: -R[c]['pct26'])
filas = []
for c in ORDEN:
    filas.append((f'{PROV[c]} · mayo 2026', R[c]['pct26'], COLOR['PP'], f'{p(R[c]["pct26"])} %'))
    filas.append((f'{PROV[c]} · julio 2023', R[c]['pct23'], CLARO, f'{p(R[c]["pct23"])} %'))
g_prov = figura('El PP de Moreno sacó más porcentaje que el de Feijóo en las ocho provincias',
                'Porcentaje de voto del PP en las autonómicas de mayo de 2026 y en las generales de julio de 2023, por provincia',
                barras(filas, 50, 'Voto al PP por provincia en las autonómicas de 2026 y en las generales de 2023', ml=170, alto=22),
                'Fuente: Junta de Andalucía y Ministerio del Interior, resultados por municipio; porcentaje sobre votos a candidaturas, sin voto exterior.',
                [('Autonómicas de mayo de 2026', COLOR['PP']), ('Generales de julio de 2023', CLARO)],
                (['Provincia', 'Votos PP 2026', 'Votos PP 2023', 'Diferencia', '% 2026', '% 2023'],
                 [[PROV[c], n(R[c]['pp26']), n(R[c]['pp23']), f'{R[c]["pp26"] - R[c]["pp23"]:+,}'.replace(',', '.'), f'{p(R[c]["pct26"])} %', f'{p(R[c]["pct23"])} %'] for c in ORDEN]))

G = json.load(open(RAIZ / 'generales-2026/data/municipios.json'))
dif = dict(zip(x.mun_code, x.dif))
nom = dict(zip(x.mun_code, x.municipio))
MAS, MEN = COLOR['PP'], '#c9c9c9'


def mapa(W=640):
    S, kx = G['S'], math.cos(math.radians(37.4))
    AN_ = []
    for c, partes in zip(G['cod'], G['poly']):
        if c[:2] not in PROV:
            continue
        for f in partes:
            xx, y, pts = f[0], f[1], [(f[0], f[1])]
            for k in range(2, len(f), 2):
                xx += f[k]; y += f[k + 1]; pts.append((xx, y))
            AN_.append((c, [(px / S * kx, -py / S) for px, py in pts]))
    XS = [a for _, r in AN_ for a, _ in r]; YS = [b for _, r in AN_ for _, b in r]
    s = W / (max(XS) - min(XS)); H = round((max(YS) - min(YS)) * s)
    camino = {}
    for c, r in AN_:
        d = ''.join(('L' if i else 'M') + f'{(a - min(XS)) * s:.0f},{(b - min(YS)) * s:.0f}' for i, (a, b) in enumerate(r))
        camino[c] = camino.get(c, '') + d + 'Z'
    assert len(camino) == NMUN, len(camino)
    out = ''.join(f'<path d="{d}" fill="{(MAS if dif[c] > 0 else MEN) if c in dif else "var(--otros)"}"><title>{esc(nom.get(c, c))}: '
                  f'{f"{int(dif[c]):+,}".replace(",", ".") if c in dif else "sin datos"} votos del PP</title></path>' for c, d in camino.items())
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Municipios andaluces donde el PP sacó más votos en las autonómicas de 2026 que en las generales de 2023" style="max-width:{W}px;margin:0 auto">'
            f'<g stroke="var(--bg)" stroke-width=".3" stroke-linejoin="round">{out}</g></svg>')


g_mapa = figura(f'El PP sacó más votos en mayo que en 2023 en {AN["mas"]} de los {NMUN} municipios andaluces',
                'Municipios donde el PP sacó más votos en las autonómicas de mayo de 2026 que en las generales de julio de 2023',
                mapa(), 'Fuente: Junta de Andalucía y Ministerio del Interior, resultados por municipio, sin voto exterior.',
                [('Más votos en mayo de 2026', MAS), ('Menos votos', MEN)],
                (['Municipio', 'Votos PP 2026', 'Votos PP 2023', 'Diferencia'],
                 [[esc(r['municipio']), n(int(r['v_PP26'])), n(int(r['2023_07_vPP'])), f"{int(r['dif']):+,}".replace(',', '.')] for r in GRANDES.to_dict('records')]))

# --- Texto ---
EP_MORENO = 'https://www.ultimahora.es/noticias/comunidades/2026/11/03/2742585/moreno-critica-dimision-planificada-puente-llega-tarde-recuerda-sanchez-amparo-tras-adamuz.html'
MOSTAZA = 'https://www.cope.es/programas/la-manana-fin-de-semana/noticias/politologo-manuel-mostaza-desvela-clave-pp-consiga-absoluta-andalucia-punado-votos-20260419_3348254.html'
EUSKADI = 'https://www.cordobabn.com/andalucia/video-29n-moreno-anima-euskadi-votantes-hacer-reproche-democratico-sanchez-apoyando-pp/20261026201341272499.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
mil = lambda v: n(round(v, -3))
g0 = GRANDES.iloc[0]
rango_v = (min(MEDV.values()), max(MEDV.values()))
PPMOD = sum(MEDE.values())
assert PPMOD == PP23 == 25, (PPMOD, PP23)

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Juanma Moreno es estos días una de las voces del PP en la campaña del 29N. El martes, en una entrevista en Cuatro recogida por <a href="{EP_MORENO}">Europa Press</a>, dijo de la dimisión de Óscar Puente que Pedro Sánchez «ha visto que ahora mismo es un lastre desde el punto de vista político de cara a las elecciones del 29 de noviembre».</p>
<p data-tipo="dato">En las autonómicas del 17 de mayo, el PP de Moreno sacó en Andalucía {n(AN["pp26"])} votos, el {p(AN["pct26"])} % de los votos a candidaturas. En las generales de julio de 2023, con Alberto Núñez Feijóo de candidato, el PP había sacado en la comunidad {n(AN["pp23"])}, el {p(AN["pct23"])} %. Son {mil(DIFV)} votos más en mayo, aunque fueron a votar unas {mil(DIFVOT)} personas menos: {n(AN["vot26"])} frente a {n(AN["vot23"])}.</p>
{g_prov}
<p data-tipo="dato">El PP sacó más votos en mayo que en 2023 en {AN["mas"]} de los {NMUN} municipios andaluces y en todas las provincias salvo {PROV[MENOS[0]]}, donde sacó {n(R[MENOS[0]]["pp23"] - R[MENOS[0]]["pp26"])} menos. Donde más ganó fue en {PROV[MAXP]}: {n(R[MAXP]["pp26"] - R[MAXP]["pp23"])} votos más. Entre los municipios de más de 100.000 electores, la mayor diferencia está en la ciudad de {esc(g0.municipio)}, con {n(int(g0.dif))} votos más.</p>
{g_mapa}
<blockquote class="cita"><p>«Moreno es bien valorado por el votante de centro y de centro izquierda».</p><footer>Manuel Mostaza, politólogo y director de Asuntos Públicos de Atrevia, en <a href="{MOSTAZA}">COPE</a> (19 de abril de 2026), antes de las autonómicas</footer></blockquote>

<h2>Lo que da el modelo para el 29N</h2>
<p data-tipo="dato">El modelo de Mapa Electoral del 5 de noviembre, que reparte la media de las encuestas nacionales por provincia, da al PP en Andalucía entre el {p(rango_v[0])} % y el {p(rango_v[1])} % según la provincia, en la mediana de las {n(SIMS)} simulaciones. En las ocho provincias, esa cifra queda por debajo de lo que sacó el PP con Feijóo en 2023, y aún más lejos de lo que sacó con Moreno en mayo. En escaños, la suma de las medianas provinciales da al PP {PPMOD} de los 61 diputados andaluces, los mismos que sacó en 2023.</p>
<p data-tipo="hipotesis">Que el PP saque más en unas autonómicas que en unas generales encaja con lo que la ciencia política llama voto dual: parte del electorado vota distinto según lo que se elige. Los datos por municipio no dicen quiénes son esos votantes, ni si repetirán en noviembre. En un mitin en Euskadi, Moreno pidió el voto para el PP como un «reproche democrático» a Sánchez, según <a href="{EUSKADI}">Córdoba Buenas Noticias</a>.</p>
<p data-tipo="contexto">La misma comparación para el PSOE está en {L("psoe-andalucia-generales-autonomicas", "la pieza sobre el voto dual socialista")}: en Andalucía, el PSOE saca casi diez puntos más en las generales que en las autonómicas.</p>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">Las autonómicas son de la Junta de Andalucía y las generales, del Ministerio del Interior; en las dos, los porcentajes son sobre votos a candidaturas y sin voto exterior, así que no coinciden con los oficiales. Comparar votos absolutos entre elecciones mezcla dos cosas: lo que cambia cada partido y cuánta gente va a votar. El modelo no es una encuesta andaluza, y sumar medianas provinciales no da la mediana de Andalucía.</p>'''

preguntas = [
    ('¿Cuántos votos sacó el PP en las autonómicas andaluzas de 2026?', f'{n(AN["pp26"])}, el {p(AN["pct26"])} % de los votos a candidaturas según los resultados por municipio, sin voto exterior.'),
    ('¿Sacó Moreno más votos que Feijóo en Andalucía?', f'Sí: unos {mil(DIFV)} más que el PP en las generales de julio de 2023 ({n(AN["pp23"])}), aunque votaron unas {mil(DIFVOT)} personas menos.'),
    ('¿Qué da el modelo al PP en Andalucía el 29N?', f'Entre el {p(rango_v[0])} % y el {p(rango_v[1])} % según la provincia, en la mediana del modelo de Mapa Electoral del 5 de noviembre: por debajo de 2023 y de mayo de 2026 en todas.'),
]
enlaces = (f'{L("psoe-andalucia-generales-autonomicas", "El voto dual del PSOE andaluz")} · {L("adelante-andalucia-psoe-29n", "Adelante y el PSOE")} · '
           f'{L("andalucia-historia-electoral", "La historia electoral de Andalucía")} · <a href="{BASE}encuestas/sevilla/">Encuesta de Sevilla</a>')
foot = ('Datos: Junta de Andalucía, autonómicas de 2026 por municipio; Ministerio del Interior, generales de 2023 por municipio; '
        'Congreso de los Diputados, diputados de la XV legislatura; modelo de encuestas de Mapa Electoral del 5 de noviembre de 2026. '
        'Cálculo: actualidad/src/resumenes/pp_andalucia_moreno.py.')

DATOS = {'R': R, 'DIFV': DIFV, 'DIFVOT': DIFVOT, 'NMUN': NMUN, 'MEDV': MEDV, 'MEDE': MEDE, 'PPMOD': PPMOD, 'PP23': PP23, 'SIMS': SIMS,
         'GRANDES': [[r.municipio, int(r.dif)] for r in GRANDES.itertuples()]}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza('pp-andalucia-autonomicas-generales-29n', 'Moreno y Feijóo en Andalucía',
      f'El PP de Moreno sacó en mayo {mil(DIFV)} votos más que el PP de Feijóo en las generales de 2023 en Andalucía, con {mil(DIFVOT)} votantes menos: ganó votos en {AN["mas"]} de los {NMUN} municipios',
      f'El PP sacó el {p(AN["pct26"])} % en las autonómicas y el {p(AN["pct23"])} % en las generales. Para el 29N, el modelo le da en cada provincia menos que en 2023.',
      '6 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
