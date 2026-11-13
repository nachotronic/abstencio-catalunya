"""«Los cuatro del debate de laSexta» (13-11-2026). laSexta emite el viernes 13 de noviembre a las 21.30 un debate sobre
economía, vivienda y actualidad con Carlos Cuerpo (PSOE), Juan Bravo (PP), José María Figaredo (Vox) y Pablo Bustinduy
(Frente Amplio), moderado por Ana Pastor (FormulaTV, 10-11-2026; El Independiente, 6-11-2026). La pieza cuenta por dónde
se presenta cada uno según las candidaturas proclamadas (BOE de 3-11-2026) y cómo votaron y qué dice la media de encuestas
de las dos provincias por las que se presentan Bravo (Sevilla) y Figaredo (Asturias).

Votos y escaños de 2019 y 2023: resultados oficiales por provincia (actualidad/src/sistema/simulador.json, Ministerio del
Interior); escaños con D'Hondt y barrera del 3 %. Candidaturas: listas-electorales-29n/datos/*-proclamadas.json (BOE).
Diputados de la XV legislatura: listas-electorales-29n/datos/diputados-xv.json (Congreso, datos abiertos).
Modelo: previsiones/datos/publico/historico (la última versión), escenario central por provincia.
Uso, desde la raíz: python3 actualidad/src/resumenes/debate_lasexta.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, pares, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
FTV = 'https://www.formulatv.com/noticias/ana-pastor-debate-electoral-lasexta-psoe-pp-vox-fa-138735/'
IND = 'https://www.elindependiente.com/series-y-television/2026/11/06/cuando-es-donde-ver-primer-debate-electoral-29n/'
BOE = 'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-23103'
BOE23 = 'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-15066'
CONGRESO = 'https://www.congreso.es/es/opendata/diputados'

LIS = RAIZ / 'listas-electorales-29n/datos'
C26 = json.load(open(LIS / '2026-proclamadas.json'))['candidaturas']
C23 = json.load(open(LIS / '2023-proclamadas.json'))['candidaturas']
DIP = json.load(open(LIS / 'diputados-xv.json'))['diputados']
assert len({c['prov'] for c in C26}) == 52


def busca(cands, apellido):
    """(provincia, cámara, siglas, puesto) de cada candidatura, titular o suplente, con ese apellido."""
    return [(c['prov'], c['camara'], c['siglas'], x['n'], x in c['titulares'])
            for c in cands for x in c['titulares'] + c.get('suplentes', []) if apellido.lower() in x['nombre'].lower()]


# Comprobación de que el buscador encuentra a los candidatos conocidos
assert busca(C26, 'Pérez-Castejón') == [('28', 'congreso', 'PSOE', 1, True)]
assert busca(C26, 'Núñez Feijóo') == [('28', 'congreso', 'PP', 1, True)]
B26, F26 = busca(C26, 'Bravo Baena'), busca(C26, 'Figaredo')
assert B26 == [('41', 'congreso', 'PP', 1, True)] and F26 == [('33', 'congreso', 'VOX', 1, True)], (B26, F26)
assert busca(C26, 'Cuerpo') == [] and busca(C26, 'Bustinduy') == []
assert busca(C23, 'Bravo Baena') == [('41', 'congreso', 'PP', 1, True)] and busca(C23, 'Figaredo') == [('33', 'congreso', 'VOX', 1, True)]
assert busca(C23, 'Cuerpo') == [] and busca(C23, 'Bustinduy') == []
DIPS = {d['nombre']: d for d in DIP}
assert DIPS['Juan Bravo Baena']['circ'] == 'Sevilla' and not DIPS['Juan Bravo Baena']['baja']
assert DIPS['José María Figaredo Álvarez-Sala']['circ'] == 'Asturias' and not DIPS['José María Figaredo Álvarez-Sala']['baja']
assert not [d for d in DIP if 'Cuerpo' in d['nombre'] or 'Bustinduy' in d['nombre']]


def cabeza(prov, siglas):
    c = next(c for c in C26 if c['prov'] == prov and c['camara'] == 'congreso' and c['siglas'] == siglas)
    return c['titulares'][0]['nombre'].split(' (')[0]


CAB = {pr: {s: cabeza(pr, s) for s in ('PSOE', 'PP', 'VOX', 'FA', 'PODEMOS')} for pr in ('41', '33')}
assert CAB['41']['PSOE'] == 'Alfonso Rodríguez Gómez de Celis' and CAB['33']['PSOE'] == 'Adriana Lastra Fernández'

# --- Votos y escaños oficiales ---
SIM = json.load(open(RAIZ / 'actualidad/src/sistema/simulador.json'))


def oficial(pr, e):
    v, val, k = SIM['elecciones'][e][pr]['v'], SIM['elecciones'][e][pr]['validos'], SIM['escanos'][e][pr]
    pct = {q: x / val * 100 for q, x in v.items()}
    vv = {q: x for q, x in v.items() if x >= 0.03 * val}
    cs = sorted(((x / d, q) for q, x in vv.items() for d in range(1, k + 1)), reverse=True)[:k]
    esc_ = {}
    for _, q in cs:
        esc_[q] = esc_.get(q, 0) + 1
    return {'pct': pct, 'esc': esc_, 'total': k, 'votos': v, 'validos': val}


R = {pr: {e: oficial(pr, e) for e in ('2019_11', '2023_07')} for pr in ('41', '33')}
assert R['41']['2023_07']['esc'] == {'PSOE': 5, 'PP': 4, 'Sumar': 2, 'Vox': 1}
assert R['33']['2023_07']['esc'] == {'PP': 3, 'PSOE': 2, 'Sumar': 1, 'Vox': 1}
assert 1.8 < R['41']['2023_07']['pct']['PP'] / R['41']['2019_11']['pct']['PP'] < 2  # «casi el doble»
assert R['33']['2019_11']['esc'].get('Vox') == 1 and R['33']['2019_11']['pct']['Vox'] > R['33']['2023_07']['pct']['Vox']  # «bajó… pero mantuvo su escaño»
assert not [c for c in C23 if c['prov'] == '41' and c['camara'] == 'congreso' and 'ADELANTE' in c['siglas'].upper()]  # Adelante no se presentó en 2023

# --- Modelo ---
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
VERSION = f'{int(_hm[:2])}.{_hm[2:]} del {int(_d)} de noviembre de {_a}'
M = {pr: {l['lista']: l for l in MOD['provincias'][pr]['listas']} for pr in ('41', '33')}
assert M['41']['PP']['escanos'][1] == 4 and M['41']['PSOE']['escanos'][1] == 4
P1 = {pr: {k: l['p_primera'] * 100 for k, l in M[pr].items()} for pr in M}
assert abs(P1['41']['PP'] - P1['41']['PSOE']) < 2
assert round(M['41']['PP']['voto'][1], 1) == round(M['41']['PSOE']['voto'][1], 1)  # «el mismo voto central»
assert M['41']['Adelante Andalucía']['escanos'][1] == 1 and M['33']['Vox']['escanos'][1] == 1

COL = {'PP': 'var(--pp)', 'PSOE': 'var(--psoe)', 'Vox': 'var(--vox)', 'Sumar': 'var(--sumar)', 'Adelante Andalucía': '#3c9a5f', 'Podemos': 'var(--pod)'}
ORD = {'41': ['PSOE', 'PP', 'Vox', 'Sumar', 'Adelante Andalucía'], '33': ['PP', 'PSOE', 'Vox', 'Sumar']}
NOMP = {'41': 'Sevilla', '33': 'Asturias'}


def fig_prov(pr, titulo):
    filas = [(k, R[pr]['2023_07']['pct'].get(k), M[pr][k]['voto'][1], COL[k]) for k in ORD[pr]]
    return figura(titulo,
                  f'Voto en las generales de julio de 2023 (barra clara) y voto central de la media de encuestas para el 29N en {NOMP[pr]}. Porcentaje sobre votos válidos',
                  pares(filas, 45, f'Voto en {NOMP[pr]}, 2023 y media de encuestas', ['2023', '29N, media'], W=360, ml=130),
                  f'Fuente: Ministerio del Interior (2023); <a href="{BASE}encuestas/">modelo de encuestas de mapaelectoral.es</a>, versión de las {VERSION}. '
                  + ('Adelante Andalucía no se presentó a las generales de 2023. ' if pr == '41' else '') + 'Sumar es, en el modelo, Sumar / Frente Amplio. Cálculo propio.',
                  [(k, COL[k]) for k in ORD[pr]],
                  (['Partido', 'Voto 2023 (%)', 'Escaños 2023', 'Voto 29N, media (%)', 'Escaños 29N, central', 'Intervalo del 80 %', 'Prob. de ser primero (%)'],
                   [[k, p(R[pr]['2023_07']['pct'].get(k, 0)) if k in R[pr]['2023_07']['pct'] else '–', (str(R[pr]['2023_07']['esc'].get(k, 0)) if k in R[pr]['2023_07']['pct'] else '–'),
                     p(M[pr][k]['voto'][1]), str(M[pr][k]['escanos'][1]), f'{M[pr][k]["escanos"][0]}-{M[pr][k]["escanos"][2]}', (p(P1[pr][k]) if P1[pr][k] >= 0.05 else 'menos de 0,1')] for k in ORD[pr]]))


S23, A23 = R['41']['2023_07'], R['33']['2023_07']
S19, A19 = R['41']['2019_11'], R['33']['2019_11']
g_sev = fig_prov('41', f'Sevilla: la media de encuestas da 4 escaños al PP y 4 al PSOE, con un {p(P1["41"]["PP"])} % y un {p(P1["41"]["PSOE"])} % de quedar primero')
g_ast = fig_prov('33', f'Asturias: Vox, {M["33"]["Vox"]["escanos"][1]} de 7 escaños, como en 2023; el PSOE subiría a {M["33"]["PSOE"]["escanos"][1]}')
MS, MA = M['41'], M['33']

cuerpo = f"""
<p data-tipo="contexto">laSexta emite esta noche, a las 21.30, el primer debate de la campaña, sobre economía, vivienda y actualidad. Lo modera Ana Pastor y no participan los candidatos a la Presidencia del Gobierno: el PSOE envía a Carlos Cuerpo; el PP, a Juan Bravo; Vox, a José María Figaredo, y Frente Amplio, a Pablo Bustinduy, según <a href="{FTV}">FormulaTV</a>. <a href="{IND}">El Independiente</a> presenta a Cuerpo como ministro de Economía, Comercio y Empresa; a Bustinduy, como ministro de Consumo; a Bravo, como portavoz del grupo popular, y a Figaredo, como secretario general del grupo parlamentario de Vox. Por sorteo, abre Cuerpo, y le siguen Bustinduy, Figaredo y Bravo.</p>
<p data-tipo="dato">Dos de los cuatro no se presentan el 29N. Ni Cuerpo ni Bustinduy figuran en ninguna de las candidaturas al Congreso o al Senado proclamadas en el <a href="{BOE}">BOE</a> del 3 de noviembre, ni como titulares ni como suplentes, y tampoco estuvieron en las de 2023 (<a href="{BOE23}">BOE</a>). Ninguno de los dos es diputado en la legislatura que acaba, según los <a href="{CONGRESO}">datos abiertos del Congreso</a>. Bravo y Figaredo, en cambio, son cabezas de lista, como en 2023: Bravo, del PP por Sevilla, y Figaredo, de Vox por Asturias.</p>

<h2>Bravo, en Sevilla: la provincia más igualada de las dos</h2>
<p data-tipo="dato">En julio de 2023, el PSOE ganó en Sevilla con el {p(S23["pct"]["PSOE"])} % y el PP sacó el {p(S23["pct"]["PP"])} %, casi el doble que en noviembre de 2019 ({p(S19["pct"]["PP"])} %). Los escaños quedaron en {S23["esc"]["PSOE"]} para el PSOE, {S23["esc"]["PP"]} para el PP, {S23["esc"]["Sumar"]} para Sumar y {S23["esc"]["Vox"]} para Vox. La media de encuestas da ahora {MS["PP"]["escanos"][1]} escaños al PP y {MS["PSOE"]["escanos"][1]} al PSOE, con el mismo voto central ({p(MS["PP"]["voto"][1])} %), y les da casi la misma probabilidad de quedar primeros: el {p(P1["41"]["PSOE"])} % de las simulaciones al PSOE y el {p(P1["41"]["PP"])} % al PP.</p>
<p data-tipo="contexto">Frente a Bravo, el PSOE presenta en Sevilla a {CAB["41"]["PSOE"]}; Vox, a {CAB["41"]["VOX"]}; Frente Amplio, a {CAB["41"]["FA"]}, y Podemos, a {CAB["41"]["PODEMOS"]}, según el <a href="{BOE}">BOE</a>. Adelante Andalucía, que en 2023 no se presentó a las generales, se presenta ahora con lista propia; la media le da {MS["Adelante Andalucía"]["escanos"][1]} escaño en Sevilla.</p>
{g_sev}

<h2>Figaredo, en Asturias: Vox repetiría su escaño</h2>
<p data-tipo="dato">En Asturias, el PP ganó en 2023 con el {p(A23["pct"]["PP"])} %, por delante del PSOE ({p(A23["pct"]["PSOE"])} %), y sacó {A23["esc"]["PP"]} de los 7 escaños; el PSOE, {A23["esc"]["PSOE"]}; Sumar y Vox, uno cada uno. Vox bajó del {p(A19["pct"]["Vox"])} % de noviembre de 2019 al {p(A23["pct"]["Vox"])} %, pero mantuvo su escaño. La media de encuestas sube a Vox al {p(MA["Vox"]["voto"][1])} % y le da {MA["Vox"]["escanos"][1]} escaño (entre {MA["Vox"]["escanos"][0]} y {MA["Vox"]["escanos"][2]}); al PSOE le da {MA["PSOE"]["escanos"][1]} y a Sumar, {MA["Sumar"]["escanos"][1]}.</p>
<p data-tipo="contexto">Frente a Figaredo, el PP presenta en Asturias a {CAB["33"]["PP"]}; el PSOE, a {CAB["33"]["PSOE"]}; Frente Amplio, a {CAB["33"]["FA"]}, y Podemos, a {CAB["33"]["PODEMOS"]} (<a href="{BOE}">BOE</a>).</p>
{g_ast}

<h2>Los temas del debate, en nuestras piezas</h2>
<p data-tipo="contexto">Sobre vivienda, hemos contado cómo vota cada barrio según cuánto se alquila en {L("alquiler-ciudad-a-ciudad", "las grandes ciudades")} y {L("precio-del-alquiler-y-voto", "según el precio del alquiler")}, {L("acampada-sol-alquiler-madrid-distritos-29n", "en los distritos de Madrid")}, y a quién votan quienes ponen la vivienda entre sus preocupaciones en {L("vivienda-preocupa-voto-sumar-29n", "las encuestas del CIS")}. Mañana añadiremos lo que se diga en el debate.</p>

<h2>Cómo se ha hecho</h2>
<p data-tipo="contexto">Las candidaturas son las proclamadas en el <a href="{BOE}">BOE</a> del 3 de noviembre de 2026, al Congreso y al Senado, con titulares y suplentes; las de 2023, las del <a href="{BOE23}">BOE</a> de 2023. Los votos son los oficiales del Ministerio del Interior por provincia, sobre votos válidos, y los escaños de 2019 y 2023 se calculan con la ley D'Hondt. Los del 29N son el escenario central del <a href="{BASE}encuestas/">modelo de encuestas</a> (versión de las {VERSION}); la probabilidad de quedar primero es el porcentaje de las 2.000 simulaciones en que esa lista es la más votada.</p>
"""
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

preguntas = [
    ('¿Quién participa en el debate de laSexta del 13 de noviembre?', f'Carlos Cuerpo (PSOE), Juan Bravo (PP), José María Figaredo (Vox) y Pablo Bustinduy (Frente Amplio), con Ana Pastor de moderadora, a las 21.30 (<a href="{FTV}">FormulaTV</a>).'),
    ('¿Se presentan Carlos Cuerpo y Pablo Bustinduy a las elecciones del 29N?', f'No. No figuran en ninguna candidatura proclamada al Congreso ni al Senado (<a href="{BOE}">BOE de 3-11-2026</a>).'),
    ('¿Por dónde se presentan Juan Bravo y José María Figaredo?', 'Bravo encabeza la lista del PP por Sevilla y Figaredo, la de Vox por Asturias, como en 2023.'),
]
enlaces = (f'{L("alquiler-ciudad-a-ciudad", "Alquiler y voto, ciudad a ciudad")} · '
           f'<a href="{BASE}listas-electorales-29n/">Listas del 29N</a> · <a href="{BASE}encuestas/">Encuestas del 29N</a>')
foot = ('Datos: BOE, candidaturas proclamadas de 2023 y 2026; Congreso de los Diputados, datos abiertos; Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 '
        'por provincia; modelo de encuestas de mapaelectoral.es. Cálculo: actualidad/src/resumenes/debate_lasexta.py.')

r4 = lambda x: round(float(x), 4)
DATOS = {'R': {pr: {e: {'pct': {k: r4(v) for k, v in r['pct'].items()}, 'esc': r['esc'], 'total': r['total']} for e, r in R[pr].items()} for pr in R},
         'M': {pr: {k: {'voto': l['voto'], 'escanos': l['escanos'], 'p1': r4(l['p_primera'] * 100)} for k, l in M[pr].items()} for pr in M},
         'B26': B26, 'F26': F26, 'CUERPO': busca(C26, 'Cuerpo'), 'BUSTINDUY': busca(C26, 'Bustinduy')}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

H1 = 'Dos de los cuatro del debate de laSexta no se presentan el 29N: ni Cuerpo ni Bustinduy están en ninguna lista'
DEK = (f'Bravo encabeza al PP en Sevilla, donde la media de encuestas da 4 escaños al PP y 4 al PSOE y casi la misma probabilidad de quedar primero; '
       f'Figaredo, a Vox en Asturias, donde repetiría su escaño.')
if __name__ == '__main__':
    pieza('debate-lasexta-cuerpo-bravo-figaredo-bustinduy-29n', 'Los cuatro del debate de laSexta', H1, DEK, '13 de noviembre de 2026',
          cuerpo, preguntas, enlaces, foot, scripts=datos_js)
    print(H1)
    print(DEK)
    print({pr: {k: (l['voto'][1], l['escanos'], round(l['p_primera'] * 100, 1)) for k, l in M[pr].items()} for pr in M})
    print(CAB)
