"""«Dónde abre cada uno la campaña, en el mapa» (12-11-2026). La campaña del 29N arranca a medianoche: Sánchez abre en
Sevilla (Fibes), Feijóo en Badalona con Albiol, Abascal en la plaza de Colón de Madrid y Colau pega carteles en Puente de
Vallecas (Europa Press, 11-11-2026). La pieza cuenta cómo votó cada lugar en las generales de 2019 y 2023.

Votos: resultados al Congreso por sección censal (generales-2026/descargas/resultados_secciones_largo.csv, Ministerio del
Interior), sin el voto exterior (CERA), que no se asigna a secciones. Porcentaje sobre votos válidos (candidaturas y
blancos), calculado con los votos, sin redondear antes. En noviembre de 2019 la familia SUMAR del fichero suma Unidas
Podemos y Más País; la segunda lista sale de generales-2026/descargas/listas_separadas.csv y aquí se separa.
Barrios y distritos: data/barrios/secciones_barrio.csv (OpenStreetMap). Mapas: data/barrios/geo/<municipio>.json.
Escaños de 2023: reparto D'Hondt con los votos oficiales por provincia (actualidad/src/sistema/simulador.json).
Uso, desde la raíz: python3 actualidad/src/resumenes/arranque_campana.py
"""
import json

import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
EP = 'https://www.diariosigloxxi.com/texto-ep/mostrar/20261111174026/sanchez-abre-campana-jueves-sevilla-feijoo-hara-badalona-mientras-abascal-colau-eligen-madrid'
DEM = 'https://www.democrata.es/politica/sanchez-inicia-hoy-la-campana-en-sevilla-feijoo-en-badalona-y-abascal-colau-y-montero-optan-por-madrid/'
ARA = 'https://es.ara.cat/politica/feijoo-elige-catalunya-albiol-inicio-campana-29-n_1_5902176.html'
ESD = 'https://www.esdiario.com/andalucia/261109/202467/sanchez-arranca-campana-sevilla-montero-psoe-esperan-desborde.html'
DEB = 'https://www.eldebate.com/espana/andalucia/20230724/sevilla-feudo-inexpugnable-psoe-victoria-socialista-80-provincia-fetiche_130224.html'
COLON = 'https://es.wikipedia.org/wiki/Plaza_de_Col%C3%B3n_(Madrid)'
DEM2 = 'https://www.democrata.es/politica/ampliacion-feijoo-apuesta-por-el-cambio-necesario-como-lema-de-su-campana-que-se-inicia-el-jueves-12-en-badalona/'

E3 = ['2019_04', '2019_11', '2023_07']
ETQ = {'2019_04': 'abril de 2019', '2019_11': 'noviembre de 2019', '2023_07': 'julio de 2023'}
CORTA = {'2019_04': 'abr. 2019', '2019_11': 'nov. 2019', '2023_07': '2023'}
PART = ['PP', 'PSOE', 'VOX', 'SUMAR']
NOM = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'SUMAR': 'Sumar', 'ERC': 'ERC', 'JUNTS': 'Junts', 'OTROS': 'Otros', 'EMPATE': 'Empate a votos'}
COL = {'PP': 'var(--pp)', 'PSOE': 'var(--psoe)', 'VOX': 'var(--vox)', 'SUMAR': 'var(--sumar)', 'ERC': 'var(--erc)',
       'JUNTS': 'var(--junts)', 'OTROS': 'var(--otros)', 'EMPATE': '#8a8486'}
SEV, BDN, MAD = '41091', '08015', '28079'

# --- Votos por sección ---
lar = pd.read_csv(RAIZ / 'generales-2026/descargas/resultados_secciones_largo.csv', dtype={'tract_code': str, 'mun_code': str})
lar = lar[lar.eleccion.isin(E3)]
ls = pd.read_csv(RAIZ / 'generales-2026/descargas/listas_separadas.csv', dtype={'tract_code': str})
lar = lar.merge(ls, on=['tract_code', 'eleccion'], how='left')
lar['sumar_b'] = lar.sumar_b.fillna(0)
lar['prov'] = lar.tract_code.str[:2]
bar = pd.read_csv(RAIZ / 'data/barrios/secciones_barrio.csv', dtype=str)


def secs(mun, col, val):
    return set(bar[(bar.mun_code == mun) & (bar[col] == val)].tract_code)


def res(mask):
    """Voto de un conjunto de secciones en cada elección: porcentaje sobre válidos, votos, censo, participación."""
    out = {}
    for e in E3:
        s = lar[mask & (lar.eleccion == e)]
        val = (s.candidaturas + s.blancos).sum()
        r = {k: s[k].sum() / val * 100 for k in PART + ['ERC', 'JUNTS', 'CS']}
        r['SUMAR_B'] = s.sumar_b.sum() / val * 100     # nov. 2019: Más País (o Más País-Equo), lista aparte de Unidas Podemos
        r['UP'] = r['SUMAR'] - r['SUMAR_B']
        r['votos'] = {k: int(s[k].sum()) for k in PART}
        r['validos'] = int(val)
        r['censo'] = int(s.censo.sum())
        r['part'] = s.votantes.sum() / s.censo.sum() * 100
        r['n'] = len(s)
        out[e] = r
    return out


S_EST = secs(SEV, 'distrito', 'Distrito Este-Alcosa-Torreblanca')
S_SAL = secs(MAD, 'distrito', 'Salamanca')
S_VAL = secs(MAD, 'distrito', 'Puente de Vallecas')
S_COL = {b: secs(MAD, 'barrio', b) for b in ('Recoletos', 'Almagro', 'Justicia')}
assert len(S_EST) == 70 and len(S_SAL) == 124 and len(S_VAL) == 174 and [len(v) for v in S_COL.values()] == [14, 18, 12]

U = {
    'sevilla': res(lar.mun_code == SEV), 'este': res(lar.tract_code.isin(S_EST)), 'p_sev': res(lar.prov == '41'),
    'badalona': res(lar.mun_code == BDN), 'p_bcn': res(lar.prov == '08'),
    'salamanca': res(lar.tract_code.isin(S_SAL)), 'vallecas': res(lar.tract_code.isin(S_VAL)), 'madrid': res(lar.mun_code == MAD),
    'p_mad': res(lar.prov == '28'), 'espana': res(lar.prov.notna()),
    **{b.lower(): res(lar.tract_code.isin(v)) for b, v in S_COL.items()},
}
Y = '2023_07'
SV, ES, BD, SA, VA, MA = (U[k][Y] for k in ('sevilla', 'este', 'badalona', 'salamanca', 'vallecas', 'madrid'))
RE, AL, JU = U['recoletos'][Y], U['almagro'][Y], U['justicia'][Y]
PSV, PBC, PMA = U['p_sev'][Y], U['p_bcn'][Y], U['p_mad'][Y]


def dif(r, a, b):
    """Diferencia en puntos entre dos partidos, con los votos (no con los porcentajes ya redondeados)."""
    return (r['votos'][a] - r['votos'][b]) / r['validos'] * 100


# Sevilla: el PP ganó la ciudad en 2023; el PSOE, la provincia y el distrito de Fibes; en 2019, el PSOE ganó la ciudad
DIF_SEV = dif(SV, 'PP', 'PSOE')
DIF_EST = dif(ES, 'PSOE', 'PP')
DIF_PSEV = dif(PSV, 'PSOE', 'PP')
assert SV['votos']['PP'] > SV['votos']['PSOE'] and ES['votos']['PSOE'] > ES['votos']['PP'] and PSV['votos']['PSOE'] > PSV['votos']['PP']
assert all(U['sevilla'][e]['PSOE'] > U['sevilla'][e]['PP'] for e in ('2019_04', '2019_11'))
# Badalona: el PSC le sacó 24 puntos al PP
DIF_BDN = dif(BD, 'PSOE', 'PP')
assert round(DIF_BDN) == 24 and BD['PP'] > PBC['PP'] and BD['VOX'] > PBC['VOX']
FUERA = res((lar.prov == '41') & (lar.mun_code != SEV))[Y]
assert FUERA['votos']['PSOE'] > FUERA['votos']['PP']
B19A_PP, BD_PP = U['badalona']['2019_04']['PP'], BD['PP']
# Puente de Vallecas: Sumar, tercera, por detrás del PP
VAL_PP_SUM = VA['votos']['PP'] - VA['votos']['SUMAR']
assert VAL_PP_SUM == 166 and VA['votos']['PSOE'] > VA['votos']['PP']
# Peso de cada lugar en el censo de su provincia (sin CERA)
PESO = {'sevilla': SV['censo'] / PSV['censo'] * 100, 'este': ES['censo'] / PSV['censo'] * 100, 'badalona': BD['censo'] / PBC['censo'] * 100,
        'salamanca': SA['censo'] / PMA['censo'] * 100, 'vallecas': VA['censo'] / PMA['censo'] * 100}

# --- Ganador por sección (empate a votos: nadie) ---
FAMS = ['PP', 'PSOE', 'VOX', 'SUMAR', 'ERC', 'JUNTS', 'OTROS']
s23 = lar[lar.eleccion == Y].copy()
_top = s23[FAMS].apply(lambda r: sorted(r.values)[-1] == sorted(r.values)[-2], axis=1)
s23['gana'] = s23[FAMS].idxmax(axis=1).where(~_top, 'EMPATE')
GANA = s23.set_index('tract_code').gana
cuenta = lambda cods: {k: int(v) for k, v in GANA[GANA.index.isin(cods)].value_counts().items()}
G_SEV = cuenta(set(s23[s23.mun_code == SEV].tract_code))
G_EST = cuenta(S_EST)
G_BDN = cuenta(set(s23[s23.mun_code == BDN].tract_code))
G_SAL, G_VAL = cuenta(S_SAL), cuenta(S_VAL)
G_COL = cuenta(set().union(*S_COL.values()))
assert G_SEV == {'PSOE': 286, 'PP': 234, 'SUMAR': 1} and G_BDN == {'PSOE': 146, 'JUNTS': 2, 'ERC': 1}
N_BDN = sum(G_BDN.values())

# --- Escaños de 2023 (D'Hondt sobre los votos oficiales por provincia, 3 % de barrera) ---
sim = json.load(open(RAIZ / 'actualidad/src/sistema/simulador.json'))


def dhondt(cod):
    v, val, k = sim['elecciones'][Y][cod]['v'], sim['elecciones'][Y][cod]['validos'], sim['escanos'][Y][cod]
    v = {p_: x for p_, x in v.items() if x >= 0.03 * val}
    q = sorted(((x / d, p_) for p_, x in v.items() for d in range(1, k + 1)), reverse=True)[:k]
    r = {}
    for _, p_ in q:
        r[p_] = r.get(p_, 0) + 1
    return r


ESC = {c: dhondt(c) for c in ('41', '08', '28')}
AND = ['04', '11', '14', '18', '21', '23', '29', '41']
assert [c for c in AND if sim['elecciones'][Y][c]['v']['PSOE'] > sim['elecciones'][Y][c]['v']['PP']] == ['41']
assert ESC['41'] == {'PSOE': 5, 'PP': 4, 'Sumar': 2, 'Vox': 1} and ESC['08']['PP'] == 5 and ESC['28']['PP'] == 16
ESC26 = {c: sim['escanos']['2026'][c] for c in ('41', '08', '28')}
assert ESC26 == {'41': 12, '08': 32, '28': 38}


# --- Mapas de secciones (mismo dibujo que las fichas de barrio) ---
def mapa(mun, cods, colores, titulo, ancho=360, todo=False, rotulos=(), punto=None):
    g = json.loads((RAIZ / 'data/barrios/geo' / f'{mun}.json').read_text())
    g = dict(zip(g['cod'], g['poly']))
    marco = list(g) if todo else cods
    pts = [q for c in marco if c in g for r in g[c] for q in r]
    x0, x1 = min(q[0] for q in pts), max(q[0] for q in pts)
    y0, y1 = min(q[1] for q in pts), max(q[1] for q in pts)
    m = max(x1 - x0, y1 - y0) * 0.04 + 40
    x0, x1, y0, y1 = x0 - m, x1 + m, y0 - m, y1 + m
    k = ancho / (x1 - x0)
    alto = int((y1 - y0) * k)
    if alto > ancho * 1.15:
        alto = int(ancho * 1.15)
        k = alto / (y1 - y0)
        dx = (ancho / k - (x1 - x0)) / 2
        x0, x1 = x0 - dx, x1 + dx
    P = lambda q: ((q[0] - x0) * k, (y1 - q[1]) * k)

    def d(rs):
        out = []
        for r in rs:
            qs = [P(q) for q in r]
            if all(not (-30 < x < ancho + 30 and -30 < y < alto + 30) for x, y in qs):
                continue
            out.append('M' + 'L'.join(f'{x:.0f},{y:.0f}' for x, y in qs) + 'Z')
        return ''.join(out)
    capas = {}
    for c in g:
        if c in colores:
            capas.setdefault(colores[c], []).append(d(g[c]))
    fondo = ''.join(d(rs) for c, rs in g.items() if c not in colores)
    trazo = ''.join(f'<path d="{"".join(v)}" fill="{col[0]}"' + (f' fill-opacity="{col[1]}"' if col[1] < 1 else '') + '/>'
                    for col, v in capas.items())
    extra = ''
    for txt, cs in rotulos:   # nombre de cada barrio en el centro de sus secciones
        qs = [q for c in cs if c in g for r in g[c] for q in r]
        x, y = P((sum(q[0] for q in qs) / len(qs), sum(q[1] for q in qs) / len(qs)))
        extra += (f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="middle" class="lab" style="paint-order:stroke;stroke:var(--bg);stroke-width:3px">{esc(txt)}</text>')
    if punto:
        x, y = P(punto[1])
        extra += (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="6" fill="var(--fg)" stroke="var(--bg)" stroke-width="2"/>'
                  f'<text x="{x + 9:.0f}" y="{y + 4:.0f}" class="lab" style="paint-order:stroke;stroke:var(--bg);stroke-width:3px">{esc(punto[0])}</text>')
    return (f'<svg viewBox="0 0 {ancho} {alto}" role="img" aria-label="{esc(titulo)}" style="overflow:hidden">'
            f'<path d="{fondo}" style="fill:var(--rule);stroke:var(--bg)" stroke-width="0.5"/>'
            f'<g style="stroke:var(--bg)" stroke-width="0.5" stroke-linejoin="round">{trazo}</g>{extra}</svg>')


def colorea(cods, fuera=()):
    """{sección: (color del ganador, opacidad)}: las de `fuera`, más claras."""
    return {c: (COL[GANA[c]], .32 if c in fuera else 1) for c in list(cods) + list(fuera) if c in GANA.index}


def ley(g):
    return [(NOM[k], COL[k]) for k in sorted(g, key=lambda k: -g[k])]


def cuenta_txt(g):
    return ', '.join(f'{NOM[k]} {v}' for k, v in sorted(g.items(), key=lambda kv: -kv[1]))


FUENTE_MAPA = ('Fuente: Ministerio del Interior, generales de julio de 2023 por sección censal; límites de barrio y distrito de '
               '<a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>. Cálculo propio.')

sev_todas = set(s23[s23.mun_code == SEV].tract_code)
m_sev = figura(f'El PSOE ganó en {G_EST.get("PSOE", 0)} de las {len(S_EST)} secciones del distrito de Fibes; el PP, en {G_EST.get("PP", 0)}',
               f'Partido más votado en cada sección censal de Sevilla en julio de 2023. En color intenso, el distrito Este-Alcosa-Torreblanca, donde está Fibes. En toda la ciudad: {cuenta_txt(G_SEV)}',
               mapa(SEV, S_EST, colorea(S_EST, sev_todas - S_EST), 'Partido más votado por sección en Sevilla, 2023', todo=True),
               FUENTE_MAPA, ley(G_SEV))
m_bdn = figura(f'Badalona: el PSC ganó en {G_BDN["PSOE"]} de las {N_BDN} secciones y el PP, en ninguna',
               f'Partido más votado en cada sección censal de Badalona en julio de 2023: {cuenta_txt(G_BDN)}. El PSC figura como PSOE',
               mapa(BDN, set(s23[s23.mun_code == BDN].tract_code), colorea(set(s23[s23.mun_code == BDN].tract_code)), 'Partido más votado por sección en Badalona, 2023', todo=True),
               FUENTE_MAPA, ley(G_BDN))
col_todas = set().union(*S_COL.values())


def _vertices(cs):
    g = json.loads((RAIZ / 'data/barrios/geo' / f'{MAD}.json').read_text())
    g = dict(zip(g['cod'], g['poly']))
    return [tuple(q) for c in cs if c in g for r in g[c] for q in r]


_vr, _va, _vj = (_vertices(S_COL[b]) for b in ('Recoletos', 'Almagro', 'Justicia'))
_d = lambda q, vs: min((q[0] - v[0]) ** 2 + (q[1] - v[1]) ** 2 for v in vs)
TRIPLE = min(_vr, key=lambda q: _d(q, _va) + _d(q, _vj))   # vértice de Recoletos más cerca de Almagro y de Justicia: la plaza de Colón
assert _d(TRIPLE, _va) < 100 ** 2 and _d(TRIPLE, _vj) < 100 ** 2
m_col = figura(f'Alrededor de Colón, el PP ganó en las {sum(G_COL.values())} secciones',
               'Partido más votado en julio de 2023 en Recoletos (Salamanca), Almagro (Chamberí) y Justicia (Centro), los tres barrios que se tocan en la plaza de Colón. En gris, las secciones vecinas',
               mapa(MAD, col_todas, colorea(col_todas), 'Partido más votado por sección en Recoletos, Almagro y Justicia, 2023',
                    rotulos=[(b, S_COL[b]) for b in S_COL], punto=('Colón', TRIPLE)),
               FUENTE_MAPA, ley(G_COL))
m_val = figura(f'Puente de Vallecas: el PSOE ganó en {G_VAL.get("PSOE", 0)} de las {len(S_VAL)} secciones y Sumar, en {G_VAL.get("SUMAR", 0)}',
               f'Partido más votado en cada sección censal del distrito de Puente de Vallecas en julio de 2023: {cuenta_txt(G_VAL)}. En gris, las secciones vecinas',
               mapa(MAD, S_VAL, colorea(S_VAL), 'Partido más votado por sección en Puente de Vallecas, 2023'),
               FUENTE_MAPA, ley(G_VAL))


# --- Barras: cada lugar frente a su provincia (2023) ---
LUGARES = [('Sevilla (ciudad)', SV, 'provincia de Sevilla', PSV), ('Badalona', BD, 'provincia de Barcelona', PBC),
           ('Recoletos (junto a Colón)', RE, 'provincia de Madrid', PMA), ('Puente de Vallecas', VA, 'provincia de Madrid', PMA)]


def paneles():
    W, ml = 360, 4
    x = lambda v: ml + v / 70 * (W - ml - 96)
    out, y = [], 0
    for nom, r, pnom, pr_ in LUGARES:
        out.append(f'<text x="{ml}" y="{y + 15}" class="lab">{esc(nom)}</text>')
        y += 22
        for k in PART:
            out.append(f'<rect x="{ml}" y="{y}" width="{max(1.5, x(r[k]) - ml):.1f}" height="11" fill="{COL[k]}" rx="2"><title>{NOM[k]}, {esc(nom)}: {p(r[k])} %</title></rect>'
                       f'<text x="{x(r[k]) + 5:.1f}" y="{y + 10}">{NOM[k]} {p(r[k])} %</text>')
            out.append(f'<rect x="{ml}" y="{y + 13}" width="{max(1.5, x(pr_[k]) - ml):.1f}" height="5" fill="{COL[k]}" fill-opacity=".35" rx="1"><title>{NOM[k]}, {esc(pnom)}: {p(pr_[k])} %</title></rect>')
            y += 24
        y += 8
    return f'<svg viewBox="0 0 {W} {y}" role="img" aria-label="Voto a PP, PSOE, Vox y Sumar en 2023 en los cuatro lugares de arranque y en su provincia">' + ''.join(out) + '</svg>'


g_lug = figura('Cuatro arranques, cuatro mapas muy distintos',
               'Voto en julio de 2023 en cada lugar (barra gruesa) y en su provincia (barra fina, más clara). Porcentaje sobre votos válidos, sin voto exterior',
               paneles(), 'Fuente: Ministerio del Interior, generales de julio de 2023 por sección censal. Cálculo propio.',
               [(NOM[k], COL[k]) for k in PART],
               (['Lugar', 'PP', 'PSOE', 'Vox', 'Sumar', 'Particip.'],
                [[nom, p(r['PP']), p(r['PSOE']), p(r['VOX']), p(r['SUMAR']), p(r['part'])] for nom, r, _, _ in LUGARES]
                + [[pn[0].upper() + pn[1:], p(pr_['PP']), p(pr_['PSOE']), p(pr_['VOX']), p(pr_['SUMAR']), p(pr_['part'])]
                   for pn, pr_ in (('provincia de Sevilla', PSV), ('provincia de Barcelona', PBC), ('provincia de Madrid', PMA))]))

# --- Barras: el partido de cada candidato en su lugar, 2019-2023 ---
SERIE = [('PSOE en Sevilla', 'PSOE', U['sevilla']), ('PP en Badalona', 'PP', U['badalona']),
         ('Vox en Recoletos', 'VOX', U['recoletos']), ('Unidas Podemos y Sumar en Puente de Vallecas', 'UP', U['vallecas'])]
filas = []
for nom, k, u in SERIE:
    for e in E3:
        clave = 'SUMAR' if (k == 'UP' and e == '2023_07') else k
        col = COL['SUMAR'] if k == 'UP' else COL[k]
        filas.append((f'{CORTA[e]}', u[e][clave], col, p(u[e][clave]) + ' %'))
g_ser = figura(f'El PP pasó del {p(B19A_PP)} % al {p(BD_PP)} % en Badalona; Vox bajó en Recoletos',
               'Voto al partido de cada candidato en el lugar donde abre la campaña, en las tres últimas generales. Porcentaje sobre votos válidos. '
               'En Puente de Vallecas, Unidas Podemos en 2019 y Sumar en 2023',
               ''.join(f'<p style="margin:.6rem 0 .1rem;font-weight:600">{esc(nom)}</p>'
                       + barras(filas[i * 3:(i + 1) * 3], 70, f'{nom}, 2019-2023', W=360, ml=70, alto=22) for i, (nom, _, _) in enumerate(SERIE)),
               'Fuente: Ministerio del Interior, generales de 2019 y 2023 por sección censal. Cálculo propio. En noviembre de 2019, Más País fue en lista aparte '
               f'({p(U["vallecas"]["2019_11"]["SUMAR_B"])} % en Puente de Vallecas) y no se suma a Unidas Podemos.',
               None,
               (['Lugar y partido', 'Abril de 2019', 'Noviembre de 2019', 'Julio de 2023'],
                [[nom] + [p(u[e]['SUMAR' if (k == 'UP' and e == '2023_07') else k]) for e in E3] for nom, k, u in SERIE]))

# --- Tabla: cuánto pesa cada lugar ---
g_peso = figura('Sevilla es un tercio del censo de su provincia; Badalona, el 4 % del de Barcelona',
                'Censo electoral de 2023 de cada lugar (sin residentes en el extranjero) y su parte en el de la provincia, que reparte los escaños',
                barras([('Sevilla (ciudad)', PESO['sevilla'], 'var(--psoe)', p(PESO['sevilla']) + ' %'),
                        ('Distrito Este (Fibes)', PESO['este'], 'var(--psoe)', p(PESO['este']) + ' %'),
                        ('Badalona', PESO['badalona'], 'var(--pp)', p(PESO['badalona']) + ' %'),
                        ('Salamanca (distrito)', PESO['salamanca'], 'var(--vox)', p(PESO['salamanca']) + ' %'),
                        ('Puente de Vallecas', PESO['vallecas'], 'var(--sumar)', p(PESO['vallecas']) + ' %')],
                       40, 'Parte del censo de su provincia', W=360, ml=140, alto=24),
                'Fuente: Ministerio del Interior, censo de las generales de julio de 2023 por sección censal. Cálculo propio. Cada barra lleva el color del partido que abre allí la campaña.',
                [('PSOE', 'var(--psoe)'), ('PP', 'var(--pp)'), ('Vox', 'var(--vox)'), ('Sumar / Frente Amplio', 'var(--sumar)')],
                (['Lugar', 'Censo 2023', '% de la provincia', 'Escaños de la provincia'],
                 [['Sevilla (ciudad)', n(SV['censo']), p(PESO['sevilla']), str(ESC26['41'])],
                  ['Distrito Este-Alcosa-Torreblanca', n(ES['censo']), p(PESO['este']), str(ESC26['41'])],
                  ['Badalona', n(BD['censo']), p(PESO['badalona']), str(ESC26['08'])],
                  ['Distrito de Salamanca', n(SA['censo']), p(PESO['salamanca']), str(ESC26['28'])],
                  ['Puente de Vallecas', n(VA['censo']), p(PESO['vallecas']), str(ESC26['28'])]]))

V19 = U['vallecas']['2019_11']
B19A = U['badalona']['2019_04']
R19 = U['recoletos']['2019_11']
cuerpo = f"""
<p data-tipo="contexto">La campaña de las generales del 29 de noviembre empieza esta medianoche, y cada candidato ha elegido dónde abrirla. Pedro Sánchez lo hace en Sevilla, con un mitin en el auditorio Fibes; Alberto Núñez Feijóo, en Badalona, junto al alcalde y cabeza de lista del PP por Barcelona, Xavier García Albiol; Santiago Abascal, en la plaza de Colón de Madrid, y Ada Colau, candidata de Frente Amplio, pega los carteles en el distrito madrileño de Puente de Vallecas, según <a href="{EP}">Europa Press</a> y <a href="{DEM}">Demócrata</a>. Irene Montero, de Podemos, también abre en Madrid.</p>
<p data-tipo="dato">Los cuatro lugares votaron de forma muy distinta en julio de 2023. Sánchez abre en una capital que ganó el PP, por {p(DIF_SEV)} puntos, aunque el PSOE ganó en el distrito de Fibes y en la provincia. Feijóo abre en una ciudad donde el PSC le sacó {p(DIF_BDN)} puntos al PP en las generales y el PP no fue el más votado en ninguna de sus {N_BDN} secciones. Abascal abre entre tres barrios donde el PP sacó entre el {p(JU["PP"])} % y el {p(RE["PP"])} %. Y Colau abre en un distrito donde Sumar quedó tercera, a {VAL_PP_SUM} votos del PP.</p>
{g_lug}

<h2>Sánchez, en Sevilla: la capital la ganó el PP; el distrito de Fibes, el PSOE</h2>
<p data-tipo="contexto">Sánchez vuelve a Sevilla para abrir la campaña, como en las dos generales de 2019; en 2023 la abrió en Madrid, recuerda <a href="{EP}">Europa Press</a>. El mitin es a las 19.00 en Fibes, el palacio de congresos de Sevilla Este, con María Jesús Montero, según <a href="{ESD}">ESdiario</a>, que recoge que el PSOE andaluz espera «un desborde» en un auditorio de unas 3.300 a 3.500 plazas. El secretario adjunto de Organización del PSOE andaluz, Alejandro Moyano, auguró «un gran mitin de arranque de campaña en Sevilla».</p>
<p data-tipo="dato">En abril y en noviembre de 2019, el PSOE fue el más votado en la ciudad de Sevilla, con el {p(U["sevilla"]["2019_04"]["PSOE"])} % y el {p(U["sevilla"]["2019_11"]["PSOE"])} %. En julio de 2023 ganó el PP: {p(SV["PP"])} % frente a {p(SV["PSOE"])} %. Aun así, el PSOE fue el más votado en más secciones: {G_SEV["PSOE"]}, frente a {G_SEV["PP"]} del PP. En el distrito Este-Alcosa-Torreblanca, donde está Fibes, el PSOE sacó el {p(ES["PSOE"])} % y el PP, el {p(ES["PP"])} %: {p(DIF_EST)} puntos de ventaja.</p>
{m_sev}
<p data-tipo="dato">La provincia la ganó el PSOE, con el {p(PSV["PSOE"])} % frente al {p(PSV["PP"])} % del PP, y se llevó {ESC["41"]["PSOE"]} de sus 12 escaños; el PP, {ESC["41"]["PP"]}. Fue la única provincia andaluza donde el PSOE superó al PP en 2023, y ganó en 84 de sus 106 municipios; el PP ganó en 18, «entre ellos la capital», según contó <a href="{DEB}">El Debate</a> tras el escrutinio. La ciudad es el {p(PESO["sevilla"])} % del censo de la provincia; fuera de la capital, el PSOE sacó el {p(FUERA["PSOE"])} % y el PP, el {p(FUERA["PP"])} %. Sánchez abrió la precampaña en octubre en uno de esos pueblos, Dos Hermanas, recuerda <a href="{ESD}">ESdiario</a>.</p>

<h2>Feijóo, en Badalona: el PP no ganó ni una sección en las generales</h2>
<p data-tipo="contexto">El PP abre en Cataluña «consciente de que es una plaza clave para llegar al Palacio de la Moncloa por el elevado número de escaños que reparte (48 de 350)», escribe <a href="{EP}">Europa Press</a>. Según el <a href="{ARA}">Ara</a>, la dirección del PP cree que los cuatro escaños que le faltaron a Feijóo en 2023 pueden salir solo del crecimiento en Cataluña, y en 2023 hizo el mismo gesto: abrió la campaña en Castelldefels, otro municipio con alcalde del PP. Su lema será «El cambio necesario», que según el director de campaña, Miguel Tellado, resume que España «necesita virar de rumbo y hacerlo hacia la gestión, el rigor y la experiencia», según recoge <a href="{DEM2}">Demócrata</a>. «Es la campaña más importante de la historia de nuestro país y del PP», dijo Tellado, según el <a href="{ARA}">Ara</a>.</p>
<p data-tipo="dato">En las generales de julio de 2023, el PSC sacó en Badalona el {p(BD["PSOE"])} % y el PP, el {p(BD["PP"])} %. El PSC fue el más votado en {G_BDN["PSOE"]} de las {N_BDN} secciones; Junts, en {G_BDN.get("JUNTS", 0)}, y ERC, en {G_BDN.get("ERC", 0)}. El PP, en ninguna. Aun así, el {p(BD["PP"])} % de Badalona supera el {p(PBC["PP"])} % del PP en toda la provincia de Barcelona, y es más del doble del {p(B19A["PP"])} % que sacó allí en abril de 2019.</p>
{m_bdn}
<p data-tipo="patron">El tirón de Albiol está en las municipales, no en las generales: en mayo de 2023 le votaron 50.163 vecinos y dos meses después el PP sacó 16.405 votos, como contamos en {L("albiol-badalona-pp-29n", "Albiol saca en Badalona tres veces los votos del PP")}. Badalona es el {p(PESO["badalona"])} % del censo de la provincia, que reparte {ESC26["08"]} escaños; el PP sacó {ESC["08"]["PP"]} en 2023. En Badalona, donde según el <a href="{ARA}">Ara</a> «la extrema derecha no tiene presencia en el ayuntamiento», Vox sacó en las generales el {p(BD["VOX"])} %, algo más que en la provincia ({p(PBC["VOX"])} %).</p>
<blockquote class="cita"><p>«No creo que por el hecho de ser extranjero seas malo»</p><footer>Xavier García Albiol, alcalde de Badalona y cabeza de lista del PP por Barcelona, sobre el discurso de Sílvia Orriols, en Catalunya Ràdio, según el <a href="{ARA}">Ara</a> (6-11-2026)</footer></blockquote>

<h2>Abascal, en Colón: el PP ganó todas las secciones de alrededor</h2>
<p data-tipo="contexto">La plaza de Colón es, para <a href="{EP}">Europa Press</a>, «un escenario de gran carga para el partido, que ha convocado allí manifestaciones y otros actos con decenas de miles de asistentes». Está donde se tocan tres distritos de Madrid, Salamanca, Chamberí y Centro (<a href="{COLON}">Wikipedia</a>), y sus barrios más cercanos son Recoletos, Almagro y Justicia.</p>
<p data-tipo="dato">En julio de 2023, el PP fue el más votado en las {sum(G_COL.values())} secciones de esos tres barrios: sacó el {p(RE["PP"])} % en Recoletos, el {p(AL["PP"])} % en Almagro y el {p(JU["PP"])} % en Justicia. Vox sacó el {p(RE["VOX"])} % en Recoletos, el {p(AL["VOX"])} % en Almagro y el {p(JU["VOX"])} % en Justicia. En todo el distrito de Salamanca, el PP sacó el {p(SA["PP"])} % y Vox el {p(SA["VOX"])} %, por encima del {p(PMA["VOX"])} % de Vox en la provincia.</p>
{m_col}
<p data-tipo="dato">En Recoletos, Vox llegó al {p(R19["VOX"])} % en noviembre de 2019 y bajó al {p(RE["VOX"])} % en 2023, mientras el PP subía del {p(R19["PP"])} % al {p(RE["PP"])} % en unas generales a las que Ciudadanos, que allí había sacado el {p(R19["CS"])} % en 2019, ya no se presentó. Es decir: Abascal abre la campaña en uno de los barrios donde más vota la derecha de Madrid, pero donde el voto de la derecha se concentró en el PP en 2023.</p>

<h2>Colau, en Puente de Vallecas: Sumar quedó tercera, a {VAL_PP_SUM} votos del PP</h2>
<p data-tipo="contexto">Frente Amplio ha elegido Puente de Vallecas, «uno de los bastiones históricos de la izquierda alternativa en Madrid, conocido por su arraigada conciencia de clase trabajadora», según <a href="{DEM}">Demócrata</a>, para la pegada de carteles. Colau abre la campaña en Madrid con el cabeza de lista por la capital, Emilio Delgado (Más Madrid), Toni Valero (IU) y Verónica Martínez (Movimiento Sumar), según <a href="{EP}">Europa Press</a>.</p>
<p data-tipo="dato">En julio de 2023, el PSOE ganó Puente de Vallecas con el {p(VA["PSOE"])} %. El PP quedó segundo, con {n(VA["votos"]["PP"])} votos ({p(VA["PP"])} %), y Sumar tercero, con {n(VA["votos"]["SUMAR"])} ({p(VA["SUMAR"])} %): {VAL_PP_SUM} votos menos. Sumar fue el más votado en {G_VAL.get("SUMAR", 0)} de las {len(S_VAL)} secciones del distrito; el PSOE, en {G_VAL.get("PSOE", 0)}. La participación fue del {p(VA["part"])} %, {n(MA["part"] - VA["part"])} puntos menos que en el conjunto de la ciudad ({p(MA["part"])} %).</p>
{m_val}
<p data-tipo="dato">En noviembre de 2019, Unidas Podemos sacó el {p(V19["UP"])} % en el distrito y Más País, que fue en lista aparte, el {p(V19["SUMAR_B"])} %. En 2023, Sumar los reunía a ambos y a Podemos en una sola candidatura, y sacó el {p(VA["SUMAR"])} %. El 29N, Podemos se presenta por su cuenta, con Irene Montero, así que el voto de Sumar en 2023 no es el punto de partida de Frente Amplio: es el techo de una coalición que ya no existe.</p>
{g_ser}

<h2>Cuánto pesa cada lugar</h2>
<p data-tipo="patron">Los escaños se reparten por provincias, no por ciudades ni barrios. La ciudad de Sevilla es el {p(PESO["sevilla"])} % del censo de su provincia y el distrito de Fibes, el {p(PESO["este"])} %. Badalona es el {p(PESO["badalona"])} % del de Barcelona. El distrito de Salamanca es el {p(PESO["salamanca"])} % del de Madrid y Puente de Vallecas, el {p(PESO["vallecas"])} %. Madrid reparte {ESC26["28"]} escaños el 29N, uno más que en 2023.</p>
{g_peso}
<p data-tipo="hipotesis">Los lugares de arranque dicen más del mensaje que de la aritmética. Sánchez abre en la única provincia andaluza que el PSOE ganó en 2023; Feijóo, en la comunidad donde cree que puede sacar los escaños que le faltaron, y con un alcalde que saca en las municipales tres veces los votos del PP en las generales; Abascal, en un escenario propio de su partido; y Colau, en un barrio obrero donde la izquierda a la izquierda del PSOE tiene el voto que se disputará con Podemos. Son decisiones de campaña, y los datos de 2023 no dicen si funcionarán.</p>

<h2>Cómo se ha hecho</h2>
<p data-tipo="contexto">Los resultados son los de las generales al Congreso por sección censal del Ministerio del Interior, sin el voto de los residentes en el extranjero, que no se asigna a secciones. Los porcentajes son sobre votos válidos y las diferencias se calculan con los votos, antes de redondear. Los barrios y distritos salen de OpenStreetMap; el PSC figura como PSOE. Los escaños de 2023 se calculan con la ley D'Hondt sobre los votos oficiales de cada provincia. Ver también {L("sevilla-barrio-a-barrio-29n", "Sevilla, barrio a barrio")} y {L("madrid-barrio-a-barrio-29n", "Madrid, barrio a barrio")}.</p>
"""
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

preguntas = [
    ('¿Dónde empieza cada candidato la campaña del 29N?', f'Pedro Sánchez, en Sevilla (Fibes); Alberto Núñez Feijóo, en Badalona; Santiago Abascal, en la plaza de Colón de Madrid; Ada Colau, en Madrid, con la pegada de carteles en Puente de Vallecas; Irene Montero, también en Madrid. Fuente: <a href="{EP}">Europa Press</a>.'),
    ('¿Quién ganó en Sevilla en las generales de 2023?', f'En la ciudad, el PP ({p(SV["PP"])} %, frente a {p(SV["PSOE"])} % del PSOE). En la provincia, el PSOE ({p(PSV["PSOE"])} % frente a {p(PSV["PP"])} %).'),
    ('¿Cómo votó Badalona en las generales de 2023?', f'El PSC fue el más votado, con el {p(BD["PSOE"])} %, y el PP sacó el {p(BD["PP"])} %. En las municipales de mayo de 2023, la lista de Albiol sacó 50.163 votos, tres veces los 16.405 del PP en las generales de julio.'),
]
enlaces = (f'{L("albiol-badalona-pp-29n", "Albiol en Badalona")} · {L("sevilla-barrio-a-barrio-29n", "Sevilla, barrio a barrio")} · '
           f'{L("madrid-barrio-a-barrio-29n", "Madrid, barrio a barrio")} · <a href="{BASE}encuestas/">Encuestas del 29N</a>')
foot = ('Datos: Ministerio del Interior, generales al Congreso de abril y noviembre de 2019 y de julio de 2023 por sección censal y por provincia; '
        'barrios y distritos de OpenStreetMap. Cálculo: actualidad/src/resumenes/arranque_campana.py.')

r4 = lambda x: round(float(x), 4)
plano = lambda r: {k: r4(r[k]) for k in PART + ['ERC', 'JUNTS', 'CS', 'UP', 'SUMAR_B', 'part']} | {'votos': r['votos'], 'censo': r['censo'], 'n': r['n']}
DATOS = {'U': {k: {e: plano(v) for e, v in u.items()} for k, u in U.items()},
         'DIF_SEV': r4(DIF_SEV), 'DIF_EST': r4(DIF_EST), 'DIF_PSEV': r4(DIF_PSEV), 'DIF_BDN': r4(DIF_BDN), 'VAL_PP_SUM': int(VAL_PP_SUM),
         'PESO': {k: r4(v) for k, v in PESO.items()}, 'G_SEV': G_SEV, 'G_EST': G_EST, 'G_BDN': G_BDN, 'G_SAL': G_SAL, 'G_VAL': G_VAL, 'G_COL': G_COL,
         'ESC': ESC, 'ESC26': ESC26, 'FUERA': plano(FUERA)}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

H1 = (f'Feijóo abre la campaña en Badalona, donde el PP no ganó ni una de sus {N_BDN} secciones en 2023, '
      f'y Sánchez en Sevilla, una capital que ganó el PP')
DEK = (f'Abascal arranca en Colón, entre tres barrios donde el PP sacó del {p(JU["PP"])} al {p(RE["PP"])} %; Colau pega carteles en Puente de Vallecas, '
       f'donde Sumar quedó tercera a {VAL_PP_SUM} votos del PP. Así votaron en 2019 y 2023 los cuatro lugares donde empieza la campaña.')
if __name__ == '__main__':
    pieza('arranque-campana-sevilla-badalona-colon-vallecas-29n', 'Dónde abre cada uno la campaña', H1, DEK, '12 de noviembre de 2026',
          cuerpo, preguntas, enlaces, foot, scripts=datos_js)
    print(H1)
    print(DEK)
    print('sev', p(SV['PP']), p(SV['PSOE']), p(DIF_SEV), 'este', p(ES['PSOE']), p(ES['PP']), G_EST, 'bdn', p(DIF_BDN), G_BDN,
          'col', G_COL, p(RE['PP']), p(AL['PP']), p(JU['PP']), 'val', G_VAL, p(V19['UP']), p(V19['SUMAR_B']), 'peso', {k: p(v) for k, v in PESO.items()})
