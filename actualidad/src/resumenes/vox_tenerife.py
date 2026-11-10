"""«Vox vuelve a la papeleta en Santa Cruz de Tenerife» (10-11-2026).

En las generales de julio de 2023, Vox no tuvo lista al Congreso en la provincia de Santa Cruz de Tenerife: varios
candidatos renunciaron y la Junta Electoral no la proclamó (RTVC, 27-6-2023 y 5-7-2023). En 2026 sí está proclamada
(BOE-A-2026-23103, 3-11-2026; listas-electorales-29n/datos/2026-proclamadas.json). La pieza compara el voto de
noviembre de 2019 con el de julio de 2023 en las dos provincias canarias, municipio a municipio, y lo cruza con la
media de encuestas del 29N.

Voto: generales-2026/descargas/municipios.csv (Ministerio del Interior, sin voto exterior). Porcentajes sobre votos a
candidaturas; «blanco y nulo» = votantes menos votos a candidaturas, sobre votantes. Escaños: D'Hondt con barrera del
3 % sobre votantes (comprobado con el resultado oficial). Encuestas: previsiones/datos/publico/escenario-base.json y la
descripción publicada en /encuestas/<provincia>/ (reparto central).
Uso, desde la raíz: python3 actualidad/src/resumenes/vox_tenerife.py
"""
import json
import re

import numpy as np
import pandas as pd

from comun import BASE, COLOR, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
s1 = lambda v: f'{v:+.1f}'.replace('.', ',').replace('-', '−')
F = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'UPYD', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC', 'UCD', 'CDS', 'OTROS']
Y19, Y23 = '2019_11', '2023_07'
CS_COL = '#eb6109'

m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str})
m['prov'] = m.mun_code.str[:2]

# España, para comparar
ES = {}
for y in (Y19, Y23):
    val = m[[f'{y}_v{f}' for f in F]].sum().sum()
    ES[y] = {f: m[f'{y}_v{f}'].sum() / val * 100 for f in ('PP', 'VOX', 'CS')}
ES_DPP = ES[Y23]['PP'] - ES[Y19]['PP']

c = m[m.prov.isin(['35', '38'])].copy()
for y in (Y19, Y23):
    c[f'{y}_val'] = c[[f'{y}_v{f}' for f in F]].sum(axis=1)
    for f in ('PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'CC', 'OTROS'):
        c[f'{y}%{f}'] = c[f'{y}_v{f}'] / c[f'{y}_val'] * 100
c['dPP'] = c[f'{Y23}%PP'] - c[f'{Y19}%PP']
assert (c[c.prov == '38'][f'{Y23}_vVOX'] == 0).all()          # Vox no se presentó en Santa Cruz de Tenerife en 2023
assert (c[c.prov == '35'][f'{Y23}_vVOX'] > 0).all()
assert len(c[c.prov == '38']) == 54 and len(c[c.prov == '35']) == 34


def dhondt(v, k):
    q = sorted(((x / d, f) for f, x in v.items() for d in range(1, k + 1)), reverse=True)[:k]
    r = {}
    for _, f in q:
        r[f] = r.get(f, 0) + 1
    return r


PROV = {}
for pr, k in (('38', 7), ('35', 8)):
    g = c[c.prov == pr]
    d = {}
    for y in (Y19, Y23):
        val, vot = g[f'{y}_val'].sum(), g[f'{y}_votantes'].sum()
        votos = {f: int(g[f'{y}_v{f}'].sum()) for f in F}
        pct = {f: votos[f] / val * 100 for f in F}
        esc_ = dhondt({f: x for f, x in votos.items() if f != 'OTROS' and x / vot >= .03}, k)
        d[y] = {'votos': votos, 'pct': pct, 'bn': (vot - val) / vot * 100, 'part': vot / g[f'{y}_censo'].sum() * 100,
                'esc': esc_, 'votantes': int(vot)}
    PROV[pr] = d
T, LP = PROV['38'], PROV['35']
# Escaños comprobados con el resultado oficial
assert T[Y19]['esc'] == {'PSOE': 2, 'PP': 2, 'CC': 1, 'SUMAR': 1, 'VOX': 1}, T[Y19]['esc']
assert T[Y23]['esc'] == {'PP': 3, 'PSOE': 3, 'CC': 1}, T[Y23]['esc']
assert LP[Y19]['esc'] == {'PSOE': 3, 'PP': 2, 'SUMAR': 1, 'VOX': 1, 'CC': 1}, LP[Y19]['esc']
assert LP[Y23]['esc'] == {'PSOE': 3, 'PP': 3, 'VOX': 1, 'SUMAR': 1}, LP[Y23]['esc']
assert T[Y23]['votos']['PP'] > T[Y23]['votos']['PSOE'] and T[Y19]['votos']['PSOE'] > T[Y19]['votos']['PP']
DER = {pr: {Y19: PROV[pr][Y19]['pct']['PP'] + PROV[pr][Y19]['pct']['VOX'] + PROV[pr][Y19]['pct']['CS'],
            Y23: PROV[pr][Y23]['pct']['PP'] + PROV[pr][Y23]['pct']['VOX']} for pr in PROV}
DPP = {pr: PROV[pr][Y23]['pct']['PP'] - PROV[pr][Y19]['pct']['PP'] for pr in PROV}
PP_MAS = T[Y23]['votos']['PP'] - T[Y19]['votos']['PP']

# Municipios de Santa Cruz de Tenerife en tres grupos con el mismo censo, según el voto a Vox en 2019; Las Palmas, igual
W = f'{Y23}_censo'
TER = {}
for pr in ('38', '35'):
    g = c[c.prov == pr].sort_values(f'{Y19}%VOX').copy()
    g['cum'] = g[W].cumsum() / g[W].sum()
    g['ter'] = np.minimum((g.cum * 3).astype(int) + 1, 3)
    TER[pr] = {int(t): {'n': len(h), 'vox19': float(np.average(h[f'{Y19}%VOX'], weights=h[f'{Y19}_val'])),
                        'pp19': float(h[f'{Y19}_vPP'].sum() / h[f'{Y19}_val'].sum() * 100),
                        'pp23': float(h[f'{Y23}_vPP'].sum() / h[f'{Y23}_val'].sum() * 100)} for t, h in g.groupby('ter')}
    for t in TER[pr]:
        TER[pr][t]['dpp'] = TER[pr][t]['pp23'] - TER[pr][t]['pp19']
TT, TL = TER['38'], TER['35']
assert TT[3]['dpp'] > TT[2]['dpp'] > TT[1]['dpp']

# Municipios de 10.000 electores o más en Santa Cruz de Tenerife
GR = c[(c.prov == '38') & (c[W] >= 10000)].sort_values(f'{Y19}%VOX', ascending=False)
NGR = len(GR)
SUR = GR[GR.municipio.isin(['Arona', 'Adeje', 'Granadilla de Abona', 'San Miguel de Abona'])]
assert len(SUR) == 4
ARONA = GR[GR.municipio == 'Arona'].iloc[0]
CAP = GR[GR.municipio == 'Santa Cruz de Tenerife'].iloc[0]
LAG = GR[GR.municipio == 'San Cristóbal de La Laguna'].iloc[0]
assert GR.iloc[0].municipio in ('San Miguel de Abona', 'Arona')
CORR = {pr: float(np.corrcoef(c[c.prov == pr][f'{Y19}%VOX'], c[c.prov == pr]['dPP'])[0, 1]) for pr in ('38', '35')}
MIN_DPP_38 = float(c[c.prov == '38'].dPP.min())
assert MIN_DPP_38 > 0                                    # el PP subió en los 54 municipios

# Media de encuestas: modelo publicado (reparto central y voto)
MOD = json.loads((RAIZ / 'previsiones/datos/publico/escenario-base.json').read_text(encoding='utf-8'))
META = json.loads((RAIZ / 'previsiones/datos/publico/meta.json').read_text(encoding='utf-8'))
assert META['generado'] == '2026-11-10', META['generado']
LIS = {l['lista']: l for l in MOD['provincias']['38']['listas']}
LIS_LP = {l['lista']: l for l in MOD['provincias']['35']['listas']}


def central(slug):
    t = (RAIZ / f'encuestas/{slug}/index.html').read_text(encoding='utf-8')
    dsc = re.search(r'"description": "Escaños de [^:]+: ([^"]+?)\. Modelo', t).group(1)
    out = {}
    for parte in dsc.split('), '):
        mm = re.match(r'(.+?) (\d+) \(entre (\d+) y (\d+)', parte.strip())
        out[mm.group(1)] = (int(mm.group(2)), int(mm.group(3)), int(mm.group(4)))
    return out


CT, CL = central('santa-cruz-de-tenerife'), central('las-palmas')
assert sum(v[0] for v in CT.values()) == 7 and CT['Vox'] == (2, 1, 2) and CT['PP'][0] == 2, CT
VOX26 = LIS['Vox']['voto']
NW = {0: 'cero', 1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro'}
CTw = {k: tuple(NW[x] for x in v) for k, v in CT.items()}
CLw = {k: tuple(NW[x] for x in v) for k, v in CL.items()}

# --- Gráficos ---
NOM = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'SUMAR': 'Unidas Podemos / Sumar', 'CS': 'Ciudadanos', 'CC': 'CC'}
COL = {'PP': COLOR['PP'], 'PSOE': COLOR['PSOE'], 'VOX': COLOR['Vox'], 'SUMAR': COLOR['Sumar'], 'CS': CS_COL, 'CC': COLOR['CC']}


def apiladas(W_=440, ml=118):
    """Bloque de la derecha (PP, Vox, Ciudadanos) en 2019 y 2023, en las dos provincias."""
    filas = [('Sta. Cruz de Tenerife', 'nov. 2019', T[Y19]['pct']), ('Sta. Cruz de Tenerife', '2023', T[Y23]['pct']),
             ('Las Palmas', 'nov. 2019', LP[Y19]['pct']), ('Las Palmas', '2023', LP[Y23]['pct'])]
    alto, H = 34, 34 * 4 + 22
    x = lambda v: v / 50 * (W_ - ml - 44)
    out = [f'<svg viewBox="0 0 {W_} {H}" role="img" aria-label="Voto al PP, Vox y Ciudadanos en noviembre de 2019 y en 2023, por provincia">']
    for i, (prov, ano, pc) in enumerate(filas):
        y = 4 + i * alto + (10 if i >= 2 else 0)
        if i in (0, 2):
            out.append(f'<text x="0" y="{y + 11}" class="lab">{esc(prov)}</text>')
        out.append(f'<text x="{ml - 8}" y="{y + 27}" text-anchor="end">{esc(ano)}</text>')
        x0, tot = ml, 0
        for f in ('PP', 'VOX', 'CS'):
            v = pc[f]
            if v <= 0:
                continue
            out.append(f'<rect x="{x0:.1f}" y="{y + 16}" width="{x(v):.1f}" height="15" fill="{COL[f]}"><title>{esc(prov)}, {ano}, {NOM[f]}: {p(v)} %</title></rect>')
            if x(v) > 34:
                out.append(f'<text x="{x0 + x(v) / 2:.1f}" y="{y + 27.5}" text-anchor="middle" style="fill:#fff;font-size:11px">{p(v)}</text>')
            x0 += x(v)
            tot += v
        out.append(f'<text x="{x0 + 5:.1f}" y="{y + 28}" class="lab">{p(tot)} %</text>')
    out.append('</svg>')
    return ''.join(out)


g_der = figura('En Tenerife, el voto de la derecha fue casi entero al PP',
               'Porcentaje de PP, Vox y Ciudadanos en las generales de noviembre de 2019 y de julio de 2023. En 2023, Vox no tuvo lista al Congreso en Santa Cruz de Tenerife y Ciudadanos no se presentó en ninguna provincia',
               apiladas(),
               'Fuente: Ministerio del Interior, resultados por municipio, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
               [('PP', COL['PP']), ('Vox', COL['VOX']), ('Ciudadanos', CS_COL)],
               (['Provincia', 'Año', 'PP (%)', 'Vox (%)', 'Ciudadanos (%)', 'Suma (%)'],
                [[prov, ano, p(PROV[pr][y]['pct']['PP']), p(PROV[pr][y]['pct']['VOX']) if PROV[pr][y]['pct']['VOX'] else 'no se presentó',
                  p(PROV[pr][y]['pct']['CS']) if PROV[pr][y]['pct']['CS'] else 'no se presentó', p(DER[pr][y])]
                 for pr, prov in (('38', 'Santa Cruz de Tenerife'), ('35', 'Las Palmas')) for y, ano in ((Y19, 'nov. 2019'), (Y23, '2023'))]))

g_sube = figura(f'El PP subió {p(DPP["38"])} puntos en Santa Cruz de Tenerife, y {p(DPP["35"])} en Las Palmas',
                'Diferencia en puntos del voto al PP entre las generales de noviembre de 2019 y las de julio de 2023',
                barras([('Sta. Cruz de Tenerife', DPP['38'], COL['PP'], f'+{p(DPP["38"])}'), ('España', ES_DPP, 'var(--otros)', f'+{p(ES_DPP)}'),
                        ('Las Palmas', DPP['35'], COL['PP'], f'+{p(DPP["35"])}')], 20, 'Subida del PP entre 2019 y 2023', W=440, ml=140, separar=True),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                [('PP', COL['PP']), ('España (referencia)', 'var(--otros)')],
                (['Territorio', 'PP nov. 2019 (%)', 'PP 2023 (%)', 'Diferencia (puntos)'],
                 [['Santa Cruz de Tenerife', p(T[Y19]['pct']['PP']), p(T[Y23]['pct']['PP']), s1(DPP['38'])],
                  ['España', p(ES[Y19]['PP']), p(ES[Y23]['PP']), s1(ES_DPP)],
                  ['Las Palmas', p(LP[Y19]['pct']['PP']), p(LP[Y23]['pct']['PP']), s1(DPP['35'])]]))


def tercios(W_=440, ml=150):
    filas = [('Más Vox en 2019', 3), ('Intermedio', 2), ('Menos Vox en 2019', 1)]
    alto, H = 46, 46 * 3 + 6
    x = lambda v: ml + v / 22 * (W_ - ml - 50)
    out = [f'<svg viewBox="0 0 {W_} {H}" role="img" aria-label="Subida del PP según el voto a Vox en 2019, en las dos provincias">']
    for i, (nom, t) in enumerate(filas):
        y = 4 + i * alto
        out.append(f'<text x="{ml - 8}" y="{y + 22}" text-anchor="end" class="lab">{esc(nom)}</text>')
        for k, (ter, op, lab) in enumerate(((TT, 1, 'Tenerife'), (TL, .4, 'Las Palmas'))):
            v = ter[t]['dpp']
            yy = y + 4 + k * 18
            x1, x2 = sorted((x(0), x(v)))
            out.append(f'<rect x="{x1:.1f}" y="{yy}" width="{max(1.5, x2 - x1):.1f}" height="15" fill="{COL["PP"]}" fill-opacity="{op}" rx="2"><title>{lab}, {nom}: {s1(v)} puntos</title></rect>')
            out.append(f'<text x="{max(x(v), x(0)) + 5:.1f}" y="{yy + 12}">{s1(v)}</text>')
    out.append(f'<line x1="{x(0):.1f}" x2="{x(0):.1f}" y1="0" y2="{H}" stroke="var(--fg)" stroke-width=".6"/></svg>')
    return ''.join(out)


g_ter = figura('Donde Vox era más fuerte, más subió el PP; en Las Palmas, mucho menos',
               'Subida del PP entre noviembre de 2019 y 2023, en puntos, en tres grupos de municipios con el mismo censo, ordenados por el voto a Vox en 2019',
               tercios(),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
               [('Santa Cruz de Tenerife (Vox no se presentó en 2023)', COL['PP']), ('Las Palmas (Vox sí se presentó)', 'rgba(29,132,206,.4)')],
               (['Provincia', 'Grupo', 'Municipios', 'Vox nov. 2019 (%)', 'PP nov. 2019 (%)', 'PP 2023 (%)', 'Diferencia (puntos)'],
                [[prov, nom, str(ter[t]['n']), p(ter[t]['vox19']), p(ter[t]['pp19']), p(ter[t]['pp23']), s1(ter[t]['dpp'])]
                 for prov, ter in (('Santa Cruz de Tenerife', TT), ('Las Palmas', TL))
                 for nom, t in (('Más Vox en 2019', 3), ('Intermedio', 2), ('Menos Vox en 2019', 1))]))

g_mun = figura('El sur de Tenerife, donde Vox sacaba más, es donde más creció el PP',
               f'Subida del PP entre noviembre de 2019 y 2023, en puntos, en los {NGR} municipios de Santa Cruz de Tenerife con 10.000 electores o más, ordenados por el voto a Vox en 2019 (entre paréntesis)',
               barras([(f'{r.municipio.replace("San Cristóbal de La Laguna", "La Laguna").replace("Santa Cruz de Tenerife", "S. C. de Tenerife").replace("Santa Cruz de la Palma", "S. C. de La Palma").replace(" de Abona", "")} ({p(r[f"{Y19}%VOX"])})',
                        r.dPP, COL['PP'], f'+{p(r.dPP)}') for _, r in GR.iterrows()], 25,
                      'Subida del PP en cada municipio', W=440, ml=192, separar=True),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio. Entre paréntesis, el voto a Vox en noviembre de 2019.',
               [('PP', COL['PP'])],
               (['Municipio', 'Electores (2023)', 'Vox nov. 2019 (%)', 'PP nov. 2019 (%)', 'Cs nov. 2019 (%)', 'PP 2023 (%)', 'Diferencia PP (puntos)'],
                [[esc(r.municipio), n(r[W]), p(r[f'{Y19}%VOX']), p(r[f'{Y19}%PP']), p(r[f'{Y19}%CS']), p(r[f'{Y23}%PP']), s1(r.dPP)] for _, r in GR.iterrows()]))

ORD = ['PP', 'PSOE', 'VOX', 'CC', 'SUMAR']
FILAS_ESC = [('Noviembre de 2019', T[Y19]['esc']), ('Julio de 2023', T[Y23]['esc']),
             ('29N, media de encuestas', {'PP': CT['PP'][0], 'PSOE': CT['PSOE'][0], 'VOX': CT['Vox'][0], 'CC': CT['CC'][0], 'SUMAR': CT['Sumar'][0]})]


def escanos(lado=24):
    W_, H = 330, 3 * 58
    out = [f'<svg viewBox="0 0 {W_} {H}" style="max-width:{W_}px" role="img" aria-label="Escaños de Santa Cruz de Tenerife en 2019, 2023 y según la media de encuestas">']
    for i, (nom, e) in enumerate(FILAS_ESC):
        y = i * 58
        out.append(f'<text x="0" y="{y + 14}" class="lab">{esc(nom)}</text>')
        k = 0
        for f in ORD:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{k * (lado + 5)}" y="{y + 22}" width="{lado}" height="{lado}" rx="3" fill="{COL[f]}"><title>{esc(nom)}: {NOM[f]}</title></rect>')
                k += 1
        assert k == 7
    out.append('</svg>')
    return ''.join(out)


g_esc = figura('En 2023, Vox y Unidas Podemos perdieron su escaño; PP y PSOE sacaron uno más cada uno',
               'Los siete diputados de Santa Cruz de Tenerife: un cuadrado por escaño',
               escanos(),
               f'Fuente: Ministerio del Interior (2019 y 2023); <a href="{BASE}encuestas/santa-cruz-de-tenerife/">media de encuestas de Mapa Electoral</a>, reparto central actualizado a las 2.31 del 10 de noviembre de 2026. '
               f'Con las encuestas, Vox sacaría entre {CTw["Vox"][1]} y {CTw["Vox"][2]} escaños, y el PP, entre {CTw["PP"][1]} y {CTw["PP"][2]}.',
               [(NOM[f], COL[f]) for f in ORD],
               (['', 'PP', 'PSOE', 'Vox', 'CC', 'Unidas Podemos / Sumar'],
                [[nom] + [str(e.get(f, 0)) for f in ORD] for nom, e in FILAS_ESC]))

# --- Texto ---
EP_CAY = 'https://www.europapress.es/islas-canarias/noticia-arriban-11-cayucos-1158-migrantes-canarias-fin-semana-20261109092514.html'
EP_SAN = 'https://www.europapress.es/epsocial/migracion/noticia-29n-sanchez-dice-llegada-mas-6600-migrantes-canarias-bastante-habitual-momento-ano-20261109224243.html'
EFE_CLA = 'https://efe.com/canarias/2026-11-09/canarias-exige-al-estado-un-plan-extraordinario-de-contingencia-ante-el-repunte-migratorio/'
RTVC_23 = 'https://rtvc.es/vox-no-presenta-lista-electoral-por-la-provincia-de-santa-cruz-de-tenerife/'
RTVC_JEC = 'https://rtvc.es/rechazan-recursos-vox-por-candidatura-santa-cruz-de-tenerife/'
RTVC_26 = 'https://rtvc.es/diputado-alberto-rodriguez-repite-cabeza-lista-vox-congreso-palmas-21-octubre-2026/'
BOE_26 = 'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-23103'
ZAPATA = 'https://rtvc.es/observatorio-de-inmigracion-ve-espectacular-actitud-de-la-sociedad-canaria/'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
E = lambda pr, y, f: PROV[pr][y]['pct'][f]

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Once cayucos con unas 1.158 personas llegaron a Canarias el fin de semana, la mayoría a El Hierro, según los datos de Salvamento Marítimo y del 112 recogidos por <a href="{EP_CAY}">Europa Press</a>. En los nueve primeros días de noviembre ya son más de 6.665, una cifra que Pedro Sánchez considera «bastante habitual en este momento del año por la calma en el Atlántico», según la <a href="{EP_SAN}">misma agencia</a>. El presidente canario, Fernando Clavijo, lleva este martes a La Moncloa un plan de ocho puntos que apoyaron todos los grupos del Parlamento canario «salvo Vox», según <a href="{EFE_CLA}">EFE</a>.</p>
<blockquote class="cita"><p>«Este es el mandato que va a llevar mañana a La Moncloa no el presidente de la comunidad solamente, sino de la integridad de la sociedad canaria»</p><footer>Fernando Clavijo, presidente de Canarias, el 9 de noviembre de 2026, según <a href="{EFE_CLA}">EFE</a></footer></blockquote>
<p data-tipo="dato">El 29N habrá algo que no hubo en 2023: una papeleta de Vox al Congreso en la provincia de Santa Cruz de Tenerife, la de Tenerife, La Palma, La Gomera y El Hierro. Hace tres años no la hubo porque varios candidatos renunciaron días antes de la proclamación y la Junta Electoral no admitió la lista, según contaron <a href="{RTVC_23}">RTVC</a> y, tras los recursos, la <a href="{RTVC_JEC}">propia televisión canaria</a>. Ahora la encabeza el concejal de Santa Cruz Alejandro Santiago Gómez Rodríguez, según <a href="{RTVC_26}">RTVC</a>, y está proclamada en el <a href="{BOE_26}">BOE del 3 de noviembre</a>.</p>
<blockquote class="cita"><p>«(…) no se puede privar a los de esta provincia de poder votar a Vox al Congreso. Porque el Senado sí salió bien, todas las listas, pero al Congreso no»</p><footer>Nicasio Galván, entonces diputado de Vox en el Parlamento de Canarias, el 27 de junio de 2023, según <a href="{RTVC_23}">RTVC</a></footer></blockquote>
<p data-tipo="dato">En noviembre de 2019, Vox había sacado en esa provincia {n(T[Y19]["votos"]["VOX"])} votos, el {p(E("38", Y19, "VOX"))} %, y un diputado. En julio de 2023, sin Vox en la papeleta, el PP pasó del {p(E("38", Y19, "PP"))} % al {p(E("38", Y23, "PP"))} %: {n(PP_MAS)} votos más. Ganó la provincia, que no ganaba desde 2016. Vox y Unidas Podemos perdieron su escaño, y el PP y el PSOE sacaron uno más cada uno. En Las Palmas, donde Vox sí se presentó, el PP subió {p(DPP["35"])} puntos, y en el conjunto de España, {p(ES_DPP)}.</p>
{g_sube}
<p data-tipo="patron">Si se suman PP, Vox y Ciudadanos, el bloque apenas se movió. En Santa Cruz de Tenerife pasó del {p(DER["38"][Y19])} % de noviembre de 2019 al {p(DER["38"][Y23])} % del PP solo en 2023. En Las Palmas, del {p(DER["35"][Y19])} % al {p(DER["35"][Y23])} %. Lo que cambió en Tenerife es el reparto: casi todo ese voto se concentró en una sola papeleta.</p>
{g_der}
<p data-tipo="patron">El mapa lo dibuja municipio a municipio. Si se reparten los 54 municipios de la provincia en tres grupos con el mismo censo según su voto a Vox en 2019, el PP subió {p(TT[3]["dpp"])} puntos en el tercio donde Vox era más fuerte y {p(TT[1]["dpp"])} en el que menos. El PP subió en los 54 municipios. En Las Palmas, con Vox en la papeleta, la subida fue de {p(TL[3]["dpp"])} y {p(TL[1]["dpp"])} puntos.</p>
{g_ter}
<p data-tipo="dato">Los municipios con más voto a Vox en 2019 están sobre todo en el sur turístico de Tenerife. En Arona, Vox sacó el {p(ARONA[f"{Y19}%VOX"])} % en noviembre de 2019, y el PP pasó del {p(ARONA[f"{Y19}%PP"])} % al {p(ARONA[f"{Y23}%PP"])} %. En Santa Cruz de Tenerife, la capital, el PP subió {p(CAP.dPP)} puntos, y en La Laguna, donde Vox había sacado el {p(LAG[f"{Y19}%VOX"])} %, {p(LAG.dPP)}.</p>
{g_mun}
<p data-tipo="hipotesis">Estos datos no dicen qué hizo cada votante de Vox: algunos pudieron votar al PP, otros quedarse en casa, votar a otro partido o en blanco, y a la vez el PP ganó votos de Ciudadanos, que tampoco se presentó en 2023. El voto en blanco y nulo, por ejemplo, subió del {p(T[Y19]["bn"])} % al {p(T[Y23]["bn"])} % de los votantes en Santa Cruz de Tenerife, mientras en Las Palmas bajó del {p(LP[Y19]["bn"])} % al {p(LP[Y23]["bn"])} %. Además, el sur de Tenerife tiene más vecinos extranjeros y una población distinta de la del norte, así que la relación entre el voto a Vox de 2019 y la subida del PP es una correlación, no una prueba de trasvase.</p>

<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, Vox sacaría en Santa Cruz de Tenerife alrededor del {p(VOX26[1])} % (entre el {p(VOX26[0])} % y el {p(VOX26[2])} %), y entre {CTw["Vox"][1]} y {CTw["Vox"][2]} de los siete diputados. En el reparto central, el PP baja de tres escaños a {CTw["PP"][0]}, el PSOE de tres a {CTw["PSOE"][0]}, y Vox se queda con {CTw["Vox"][0]}. En Las Palmas, la media da a Vox {CLw["Vox"][0]} escaños, uno más que en 2023.</p>
{g_esc}
<p data-tipo="contexto">La inmigración llega a la campaña en las islas con un matiz que ya señalaba hace cinco años el director del Observatorio de la Inmigración de Tenerife, el profesor de la Universidad de La Laguna Vicente Zapata: que la opinión pública sobre la inmigración en Canarias se forma mirando sobre todo a los cayucos.</p>
<blockquote class="cita"><p>«Se juzga un fenómeno social complejo en base a una de sus manifestaciones», la llegada de cayucos y pateras, «que no es la mayoritaria»</p><footer>Vicente Zapata, director del Observatorio de la Inmigración de Tenerife (ULL), en abril de 2021, según <a href="{ZAPATA}">RTVC</a></footer></blockquote>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">Los porcentajes son sobre votos a candidaturas y sin el voto exterior, así que pueden diferir en décimas de los oficiales. La comparación es con noviembre de 2019, las últimas generales con Vox en las dos provincias. Las encuestas tienen un margen amplio a 19 días de la votación: en Santa Cruz de Tenerife, el último escaño se decide por pocos miles de votos. Ver también {L("canarias-unidad-pueblo-canario-29n", "la Unidad del Pueblo Canario")}, {L("inmigracion-preocupa-voto-vox-29n", "dónde preocupa más la inmigración")} y {L("canarias-historia-electoral", "la historia electoral de Canarias")}.</p>'''

preguntas = [
    ('¿Por qué Vox no se presentó al Congreso en Santa Cruz de Tenerife en 2023?',
     'Varios integrantes de su candidatura renunciaron días antes de la proclamación y la Junta Electoral no la admitió; la Junta Electoral Central rechazó después sus recursos. Sí se presentó al Senado.'),
    ('¿Se presenta Vox en Santa Cruz de Tenerife el 29N?',
     'Sí. Su lista al Congreso, encabezada por Alejandro Santiago Gómez Rodríguez, está proclamada en el BOE del 3 de noviembre de 2026.'),
    ('¿Cuánto subió el PP en Santa Cruz de Tenerife sin Vox?',
     f'Del {p(E("38", Y19, "PP"))} % de noviembre de 2019 al {p(E("38", Y23, "PP"))} % de julio de 2023, {p(DPP["38"])} puntos, frente a {p(DPP["35"])} en Las Palmas. Ganó la provincia y un tercer escaño.'),
    ('¿Cuántos escaños puede sacar Vox en Santa Cruz de Tenerife?',
     f'Con la media de encuestas de Mapa Electoral, entre {CTw["Vox"][1]} y {CTw["Vox"][2]} de los siete; en el reparto central, {CTw["Vox"][0]}.'),
]
enlaces = (f'{L("canarias-unidad-pueblo-canario-29n", "La Unidad del Pueblo Canario")} · {L("inmigracion-preocupa-voto-vox-29n", "Inmigración y voto a Vox")} · '
           f'<a href="{BASE}encuestas/santa-cruz-de-tenerife/">Encuesta en Santa Cruz de Tenerife</a> · <a href="{BASE}encuestas/las-palmas/">Encuesta en Las Palmas</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por municipio (sin voto exterior); BOE-A-2026-23103, '
        'candidaturas proclamadas; media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/vox_tenerife.py.')

DATOS = {'PROV': PROV, 'DER': DER, 'DPP': DPP, 'ES': ES, 'ES_DPP': ES_DPP, 'TER': TER, 'CT': CT, 'CL': CL, 'VOX26': VOX26, 'CORR': CORR,
         'GR': [[r.municipio, int(r[W]), float(r[f'{Y19}%VOX']), float(r[f'{Y19}%PP']), float(r[f'{Y23}%PP']), float(r.dPP)] for _, r in GR.iterrows()]}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza('vox-vuelve-tenerife-29n', 'Vox vuelve a la papeleta en Tenerife',
      f'Vox vuelve a la papeleta en Tenerife: en 2023 no se presentó y el PP subió {p(DPP["38"])} puntos, frente a {p(DPP["35"])} en Las Palmas',
      f'Hace tres años, Vox no tuvo lista al Congreso en Santa Cruz de Tenerife y el PP ganó la provincia y un tercer escaño. Donde Vox era más fuerte, en el sur de Tenerife, más subió el PP. '
      f'Con las encuestas, Vox recuperaría entre {CTw["Vox"][1]} y {CTw["Vox"][2]} de los siete diputados.',
      '10 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print({k: round(v, 2) for k, v in DPP.items()}, 'ES', round(ES_DPP, 2), 'TT', {t: round(TT[t]['dpp'], 1) for t in TT}, 'TL', {t: round(TL[t]['dpp'], 1) for t in TL}, 'NGR', NGR, 'CORR', CORR)
