"""«Cabo Verde elige presidente» (previa de las presidenciales del 15-11-2026). Serie Internacional.

Resultados de 2021 por círculo electoral: Edital n.º 01/Eleições Presidenciais/2021 de la Comissão Nacional de Eleições
(CNE), republicado en el Boletim Oficial, I Série, n.º 108, de 30-10-2021 (copia en la Direção-Geral de Apoio ao Processo
Eleitoral, dgape.cv). La tabla del edital es una imagen: se copió a mano en datos/cabo_verde_presidenciales_2021.csv y
cada fila cuadra (votantes = blancos + nulos + válidos; válidos = suma de candidatos) y la suma de los 13 círculos da los
totales del edital. Porcentajes sobre votos válidos (sin blancos ni nulos), como los da la CNE.
Inscritos de 2026: web oficial de resultados de la CNE, eleicoes.cv (/data/regions.json, versión del 11-11-2026),
copiada en datos/cabo_verde_inscritos_2026.json.
Legislativas del 17-5-2026: resultado nacional del Edital n.º 3/Eleição/2026 de la CNE según Wikipedia.
Contornos: geoBoundaries (CPV ADM1, OpenStreetMap, ODbL), 22 concelhos agrupados en los 10 círculos del país.
Uso, desde la raíz: python3 actualidad/src/resumenes/cabo_verde.py
"""
import json
import math

import pandas as pd

from comun import RAIZ, esc, figura, n, barras, pieza

p = lambda v: n(v, 1)
DAT = RAIZ / 'actualidad/src/resumenes/datos'
d = pd.read_csv(DAT / 'cabo_verde_presidenciales_2021.csv')
CAND = ['delgado', 'alves', 'neves', 'veiga', 'sanches', 'pina', 'monteiro']
NOMC = {'delgado': 'Fernando Rocha Delgado', 'alves': 'Gilson Alves', 'neves': 'José Maria Neves', 'veiga': 'Carlos Veiga',
        'sanches': 'Hélio Sanches', 'pina': 'Casimiro de Pina', 'monteiro': 'Joaquim Monteiro'}
assert (d.brancos + d.nulos + d.validos == d.votantes).all() and (d[CAND].sum(axis=1) == d.validos).all()
T = d[['inscritos', 'votantes', 'brancos', 'nulos', 'validos'] + CAND].sum()
assert T.to_dict() == {'inscritos': 398690, 'votantes': 191335, 'brancos': 4295, 'nulos': 1592, 'validos': 185448, 'delgado': 2518,
                       'alves': 1410, 'neves': 96035, 'veiga': 78603, 'sanches': 2134, 'pina': 3345, 'monteiro': 1403}
for k in CAND:
    d['%' + k] = d[k] / d.validos * 100
d['part'] = d.votantes / d.inscritos * 100
d['gana'] = d[['neves', 'veiga']].idxmax(axis=1)
PCT = {k: T[k] / T.validos * 100 for k in CAND}
PART = T.votantes / T.inscritos * 100
MITAD = T.validos / 2
MARGEN = int(T.neves - math.floor(MITAD))   # votos por encima de la mitad de los válidos
assert MARGEN == 3311 and round(PCT['neves'], 2) == 51.79 and round(PCT['veiga'], 2) == 42.39
DIASP = ['África', 'Américas', 'Europa e Resto do Mundo']
NAC = d[~d.circulo.isin(DIASP)]
DIA = d[d.circulo.isin(DIASP)]
GANA_N = sorted(d[d.gana == 'neves'].circulo)
GANA_V = sorted(d[d.gana == 'veiga'].circulo)
assert GANA_V == ['Brava', 'Maio', 'Sal', 'São Nicolau'] and len(GANA_N) == 9
PART_NAC = NAC.votantes.sum() / NAC.inscritos.sum() * 100
PART_DIA = DIA.votantes.sum() / DIA.inscritos.sum() * 100
EUR = d.set_index('circulo').loc['Europa e Resto do Mundo']
STS, STN = d.set_index('circulo').loc['Santiago Sul'], d.set_index('circulo').loc['Santiago Norte']
SANTIAGO_NEVES = STS.neves + STN.neves
SANTIAGO_VEIGA = STS.veiga + STN.veiga
VENT_TOTAL = T.neves - T.veiga
SANT_PCT = (STS.validos + STN.validos) / T.validos * 100
assert 50 < SANT_PCT < 51
VENT_SANT = SANTIAGO_NEVES - SANTIAGO_VEIGA
DIAS_NEVES = DIA.neves.sum() - DIA.veiga.sum()

# --- Inscritos de 2026 (web de la CNE) ---
R = {r['name']: r['nr_inscritos'] for r in json.load(open(DAT / 'cabo_verde_inscritos_2026.json'))}
NOMBRE26 = {'Santo Antão': 'SANTO ANTÃO', 'São Vicente': 'SÃO VICENTE', 'São Nicolau': 'SÃO NICOLAU', 'Sal': 'SAL', 'Boa Vista': 'BOA VISTA',
            'Maio': 'MAIO', 'Santiago Norte': 'SANTIAGO NORTE', 'Santiago Sul': 'SANTIAGO SUL', 'Fogo': 'FOGO', 'Brava': 'BRAVA',
            'África': 'ÁFRICA', 'Américas': 'AMÉRICAS', 'Europa e Resto do Mundo': 'EUROPA E RESTO DO MUNDO'}
d['ins26'] = d.circulo.map(lambda c: R[NOMBRE26[c]])
assert d.ins26.sum() == R['GLOBAL'] == 419448 and d[~d.circulo.isin(DIASP)].ins26.sum() == R['NACIONAL'] and d[d.circulo.isin(DIASP)].ins26.sum() == R['DIÁSPORA']
d['var_ins'] = (d.ins26 / d.inscritos - 1) * 100
INS26, DIAS26 = R['GLOBAL'], R['DIÁSPORA']
P_DIAS26 = DIAS26 / INS26 * 100
VAR_TOT = (INS26 / T.inscritos - 1) * 100
VAR_DIAS = (DIAS26 / DIA.inscritos.sum() - 1) * 100
VAR_NAC = (R['NACIONAL'] / NAC.inscritos.sum() - 1) * 100
VAR_EUR = float(d.set_index('circulo').loc['Europa e Resto do Mundo', 'var_ins'])
assert round(VAR_EUR) == 41

# --- Legislativas del 17-5-2026 (CNE, Edital n.º 3/Eleição/2026, según Wikipedia) ---
LEG = {'PAICV': (90660, 37), 'MpD': (84458, 33), 'UCID': (9812, 2), 'PTS': (3268, 0), 'Partido Popular': (529, 0)}
LEG_VAL = sum(v for v, _ in LEG.values())
LEG_PCT = {k: v / LEG_VAL * 100 for k, (v, _) in LEG.items()}
assert round(LEG_PCT['PAICV'], 2) == 48.04 and round(LEG_PCT['MpD'], 2) == 44.75 and sum(s for _, s in LEG.values()) == 72
LEG_PART = (LEG_VAL + 2709 + 1893) / 416096 * 100

# --- Colores: los de cada candidatura en la web oficial de resultados de la CNE (eleicoes.cv) ---
EST = ('<style>:root{--neves:#184690;--rosa:#14b5ea}'
       '@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--neves:#7ea3e6;--rosa:#5fd0f5}}'
       ':root[data-theme="dark"]{--neves:#7ea3e6;--rosa:#5fd0f5}</style>')
COL = {'neves': 'var(--neves)', 'veiga': 'var(--rosa)'}
CORTO = {'neves': 'Neves', 'veiga': 'Veiga'}

# --- Mapa por círculo ---
G = json.load(open(DAT / 'cabo_verde_concelhos.json'))['concelhos']
KX = math.cos(math.radians(16))
D = d.set_index('circulo')


def tono(c):
    v = D.loc[c, '%' + D.loc[c, 'gana']]
    return .5 if v < 50 else (.75 if v < 55 else 1)


def mapa(W=360):
    pts = [(x * KX, -y) for c in G for a in c['anillos'] for x, y in a]
    x0, x1 = min(x for x, _ in pts), max(x for x, _ in pts)
    y0, y1 = min(y for _, y in pts), max(y for _, y in pts)
    s = (W - 20) / (x1 - x0)
    f = lambda x, y: (10 + (x * KX - x0) * s, 10 + (-y - y0) * s)
    H = round((y1 - y0) * s) + 20
    out = []
    for c in G:
        ci = c['circulo']
        dd = ''.join('M' + 'L'.join(f'{f(x, y)[0]:.1f},{f(x, y)[1]:.1f}' for x, y in a) + 'Z' for a in c['anillos'])
        out.append(f'<path d="{dd}" fill="{COL[D.loc[ci, "gana"]]}" fill-opacity="{tono(ci)}"><title>{esc(c["concelho"])} (círculo de {esc(ci)}): '
                   f'Neves {p(D.loc[ci, "%neves"])} %, Veiga {p(D.loc[ci, "%veiga"])} %</title></path>')
    # rótulos de los círculos, en el centro de sus concelhos
    rot = []
    POS = {'Santiago Norte': (0, -6), 'Santiago Sul': (6, 20)}
    for ci in NAC.circulo:
        a = [q for c in G if c['circulo'] == ci for r in c['anillos'] for q in r]
        cx, cy = f(sum(x for x, _ in a) / len(a), sum(y for _, y in a) / len(a))
        dx, dy = POS.get(ci, (0, 0))
        ancla = 'start' if cx < W * 0.62 and ci not in ('Santiago Norte', 'Santiago Sul', 'Fogo', 'Brava', 'Maio') else 'end'
        sep = 14 if ancla == 'start' else -14
        if ci in ('Sal', 'Boa Vista'):
            ancla, sep = 'end', (-12 if ci == 'Sal' else -26)
        if ci in ('Maio', 'Santiago Sul'):
            ancla, sep = 'start', 12
        rot.append(f'<text x="{cx + sep + dx:.0f}" y="{cy + 4 + dy:.0f}" text-anchor="{ancla}" class="lab" '
                   f'style="paint-order:stroke;stroke:var(--bg);stroke-width:3px;font-size:12px">{esc(ci)} {p(D.loc[ci, "%" + D.loc[ci, "gana"]])}</text>')
    # la diáspora, en tres cuadros
    caja, by = [], H + 22
    for i, ci in enumerate(DIASP):
        bx = 10 + i * (W - 20) / 3
        caja.append(f'<rect x="{bx:.0f}" y="{by}" width="{(W - 20) / 3 - 8:.0f}" height="34" rx="3" fill="{COL[D.loc[ci, "gana"]]}" fill-opacity="{tono(ci)}">'
                    f'<title>{esc(ci)}: Neves {p(D.loc[ci, "%neves"])} %, Veiga {p(D.loc[ci, "%veiga"])} %</title></rect>'
                    f'<text x="{bx + 6:.0f}" y="{by + 15}" class="lab" style="fill:#fff;font-size:12px">{esc("Europa y resto" if ci.startswith("Europa") else ci)}</text>'
                    f'<text x="{bx + 6:.0f}" y="{by + 29}" style="fill:#fff;font-size:12px">Neves {p(D.loc[ci, "%neves"])} %</text>')
    H2 = by + 40
    return (f'<svg viewBox="0 0 {W} {H2}" role="img" aria-label="Candidato más votado en cada círculo de Cabo Verde en las presidenciales de 2021" '
            f'style="max-width:{W}px;margin:0 auto"><g stroke="var(--bg)" stroke-width=".6" stroke-linejoin="round">{"".join(out)}</g>{"".join(rot)}'
            f'<text x="10" y="{H + 14}" class="lab" style="font-size:12px">Diáspora (tres círculos)</text>{"".join(caja)}</svg>')


ORD = d.sort_values('%neves', ascending=False)
TABLA = (['Círculo', 'Neves %', 'Veiga %', 'Válidos', 'Votó %'],
         [[r.circulo, p(r['%neves']), p(r['%veiga']), n(r.validos), p(r.part)] for _, r in ORD.iterrows()])
EDITAL = 'https://dgape.cv/wp-content/uploads/2023/11/B.O_Eleicao-Presidencial-2021-R.pdf'
FUENTE = (f'Fuente: Comissão Nacional de Eleições, <a href="{EDITAL}">edital de resultados de 2021</a> (Boletim Oficial, 30-10-2021). '
          'Porcentajes sobre votos válidos. Cálculo propio.')
g_mapa = figura(f'Neves ganó en {len(GANA_N)} de los 13 círculos; Veiga, en {len(GANA_V)}: São Nicolau, Sal, Maio y Brava',
                'Candidato más votado en cada círculo electoral en las presidenciales del 17 de octubre de 2021, y su porcentaje. '
                'Tono claro: menos del 50 %; medio, del 50 % al 55 %; intenso, más del 55 %',
                mapa(), FUENTE + ' Contornos: geoBoundaries (OpenStreetMap, ODbL).',
                [('José Maria Neves (PAICV)', COL['neves']), ('Carlos Veiga (MpD)', COL['veiga'])], TABLA)


def pares(W=360, ml=118, alto=34):
    H = alto * len(ORD) + 6
    x = lambda v: ml + v / 70 * (W - ml - 50)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Voto a Neves y a Veiga por círculo en 2021">',
           f'<line x1="{x(50):.1f}" x2="{x(50):.1f}" y1="0" y2="{H}" stroke="var(--fg)" stroke-dasharray="3 3"/>']
    for i, (_, r) in enumerate(ORD.iterrows()):
        y = 4 + i * alto
        nom = 'Europa y resto' if r.circulo.startswith('Europa') else r.circulo
        out.append(f'<text x="{ml - 8}" y="{y + 18}" text-anchor="end" class="lab">{esc(nom)}</text>')
        for j, k in enumerate(('neves', 'veiga')):
            yy = y + 3 + j * 14
            out.append(f'<rect x="{ml}" y="{yy}" width="{x(r["%" + k]) - ml:.1f}" height="11" fill="{COL[k]}" rx="2"><title>{esc(r.circulo)}, {CORTO[k]}: {p(r["%" + k])} %</title></rect>'
                       f'<text x="{x(r["%" + k]) + 5:.1f}" y="{yy + 10}" style="font-size:12px;paint-order:stroke;stroke:var(--bg);stroke-width:3px">{p(r["%" + k])}</text>')
    out.append('</svg>')
    return ''.join(out)


g_pares = figura(f'En la diáspora de África y América, Neves pasó del 61 %; en Maio, Veiga sacó el {p(D.loc["Maio", "%veiga"])} %',
                 'Porcentaje de votos válidos de José Maria Neves y Carlos Veiga en cada círculo en 2021, ordenados por el voto a Neves. La línea marca el 50 %',
                 pares(), FUENTE, [('José Maria Neves (PAICV)', COL['neves']), ('Carlos Veiga (MpD)', COL['veiga'])], TABLA)

ORD_INS = d.sort_values('var_ins', ascending=False)
g_ins = figura(f'En el círculo de Europa y resto del mundo hay un {p(VAR_EUR)} % más de inscritos que en 2021; en el país, un {p(VAR_NAC)} % más',
               'Variación de los electores inscritos en cada círculo entre las presidenciales de 2021 y las de 2026',
               barras([('Europa y resto' if r.circulo.startswith('Europa') else r.circulo, max(r.var_ins, 0),
                        'var(--acc)' if r.circulo in DIASP else 'var(--muted)', ('+' if r.var_ins >= 0 else '') + p(r.var_ins) + ' %')
                       for _, r in ORD_INS.iterrows()], 45, 'Variación de los inscritos por círculo, 2021-2026', W=360, ml=118, alto=22, separar=True),
               f'Fuente: CNE, <a href="{EDITAL}">edital de 2021</a> y <a href="https://eleicoes.cv/">web oficial de resultados de 2026</a> (inscritos a 11-11-2026). Cálculo propio. '
               'Las barras de los círculos que pierden inscritos se dejan en cero; la cifra va al final.',
               [('Diáspora', 'var(--acc)'), ('Círculos del país', 'var(--muted)')],
               (['Círculo', 'Inscritos 2021', 'Inscritos 2026', 'Variación (%)'],
                [[r.circulo, n(r.inscritos), n(r.ins26), ('+' if r.var_ins >= 0 else '') + p(r.var_ins)] for _, r in ORD_INS.iterrows()]))

g_leg = figura(f'En mayo, el PAICV de Neves ganó las legislativas con el {p(LEG_PCT["PAICV"])} % y mayoría absoluta',
               'Legislativas del 17 de mayo de 2026: porcentaje de los votos a candidaturas y escaños (72 en total, mayoría con 37)',
               barras([(f'{"P. Popular" if k == "Partido Popular" else k} ({s} esc.)', LEG_PCT[k], {'PAICV': 'var(--neves)', 'MpD': 'var(--rosa)'}.get(k, 'var(--otros)'), p(LEG_PCT[k]) + ' %')
                       for k, (_, s) in LEG.items()], 60, 'Legislativas de Cabo Verde, mayo de 2026', W=360, ml=118, alto=26),
               'Fuente: CNE, Edital n.º 3/Eleição/2026, según <a href="https://en.wikipedia.org/wiki/2026_Cape_Verdean_parliamentary_election">Wikipedia</a>; '
               'mayoría absoluta del PAICV según <a href="https://www.rtp.pt/noticias/mundo/paigc-da-guine-bissau-felicita-francisco-carvalho-por-maioria-absoluta_n1742133">RTP (Lusa)</a>. Cálculo propio.',
               [('PAICV', 'var(--neves)'), ('MpD', 'var(--rosa)'), ('Otros', 'var(--otros)')],
               (['Partido', 'Votos', '%', 'Escaños'], [[k, n(v), p(LEG_PCT[k]), str(s)] for k, (v, s) in LEG.items()]))

# --- Texto ---
SLUG = 'cabo-verde-presidenciales-neves-rosa-mapa'
TC6 = 'https://e-global.pt/noticias/lusofonia/cabo-verde/cabo-verde-eleicoes-presidenciais-passam-a-ter-seis-candidaturas-aceites/'
TC5 = 'https://e-global.pt/noticias/lusofonia/cabo-verde/cabo-verde-tribunal-constitucional-admite-cinco-candidaturas-as-eleicoes-presidenciais-de-2026/'
LUSA = 'https://macaubusiness.com/cabo-verde-four-presidential-candidates-without-party-backing/'
BALAI = 'https://www.balai.cv/noticias/atualidade/presidenciais-2026-jose-maria-neves-diz-que-cabo-verde-precisa-de-um-presidente-sereno-experiente-e-com-sabedoria/'
EXP = 'https://expressodasilhas.cv/politica/2026/10/03/joana-rosa-candidata-a-presidencia-da-republica-cabo-verde-precisa-de-uma-presidente-da-republica-independente-e-util/104906'
RTP = 'https://www.rtp.pt/noticias/mundo/paigc-da-guine-bissau-felicita-francisco-carvalho-por-maioria-absoluta_n1742133'
WLEG = 'https://en.wikipedia.org/wiki/2026_Cape_Verdean_parliamentary_election'
DW = 'https://www.dw.com/pt-002/cabo-verde-mpd-assume-derrota-nas-aut%C3%A1rquicas/a-70935525'
WEB = 'https://eleicoes.cv/'

H1 = f'Neves evitó la segunda vuelta en Cabo Verde por {n(MARGEN)} votos en 2021; el domingo busca la reelección con su partido ya en el Gobierno'
DEK = (f'Seis candidatos se disputan el domingo la presidencia de Cabo Verde, entre ellos el presidente, José Maria Neves, y Joana Rosa, apoyada por el MpD. '
       f'En 2021, Neves ganó en {len(GANA_N)} de los 13 círculos. La diáspora es hoy el {p(P_DIAS26)} % del censo.')
cuerpo = f"""{EST}
{g_mapa}
<p data-tipo="dato">Cabo Verde elige presidente el domingo 15 de noviembre. Hay seis candidatos: el presidente, José Maria Neves, que busca un segundo mandato con el apoyo del PAICV; la exministra de Justicia Joana Rosa, con el del MpD, y cuatro más sin el respaldo de ninguno de los dos partidos que se turnan en el Gobierno desde 1991: el juez Antero Tavares, el jurista Casimiro de Pina, el médico Gilson Alves y el profesor Loisito Sousa, según la agencia <a href="{LUSA}">Lusa</a>. Pina y Alves ya se presentaron en 2021 y sacaron el {p(PCT["pina"])} % y el {p(PCT["alves"])} %.</p>
<p data-tipo="contexto">El Tribunal Constitucional admitió cinco candidaturas el 21 de septiembre y rechazó otras cinco, entre ellas la de Sousa, por la distribución territorial de sus firmas, según <a href="{TC5}">e-Global</a>. Tres días después, tras su recurso, el tribunal comprobó que las cinco firmas que le faltaban, las del concelho de Ribeira Brava, en São Nicolau, habían llegado a tiempo y lo admitió, según <a href="{TC6}">e-Global</a>.</p>
<p data-tipo="dato">Para ganar en la primera vuelta hace falta más de la mitad de los votos válidos; si nadie la consigue, los dos primeros van a una segunda. En 2021, Neves sacó {n(T.neves)} votos, el {p(PCT["neves"])} % de los válidos, según el edital de la <a href="{EDITAL}">Comissão Nacional de Eleições</a>. La mitad de los válidos eran {n(MITAD)}: Neves la superó por {n(MARGEN)} votos. Carlos Veiga, del MpD, se quedó en el {p(PCT["veiga"])} %. Votó el {p(PART)} % de los inscritos.</p>

<h2>El mapa de 2021: Santiago y la diáspora</h2>
<p data-tipo="dato">Cabo Verde vota en 13 círculos: diez en el país, que siguen las islas (Santiago se parte en dos, Norte y Sur), y tres en la diáspora. Neves ganó en {len(GANA_N)}, entre ellos los tres de la diáspora, y Veiga, en {len(GANA_V)}: São Nicolau, Sal, Maio y Brava. La diferencia la hizo Santiago, la isla de la capital, Praia, que dio el {p(SANT_PCT)} % de los votos válidos: allí Neves sacó {n(VENT_SANT)} votos más que Veiga, de los {n(VENT_TOTAL)} de ventaja que tuvo en todo el país. En la diáspora sacó {n(DIAS_NEVES)} más.</p>
{g_pares}
<p data-tipo="dato">En los tres círculos de la diáspora, Neves pasó del 53 %: {p(D.loc["África", "%neves"])} % en África, {p(D.loc["Américas", "%neves"])} % en América y {p(D.loc["Europa e Resto do Mundo", "%neves"])} % en Europa y el resto del mundo. Pero allí votó muy poca gente: el {p(PART_DIA)} % de los inscritos, frente al {p(PART_NAC)} % en el país. En Europa, solo el {p(EUR.part)} %.</p>

<h2>Más electores fuera</h2>
<p data-tipo="dato">Para el domingo hay {n(INS26)} inscritos, según la web oficial de resultados de la <a href="{WEB}">CNE</a>, un {p(VAR_TOT)} % más que en 2021. {n(DIAS26)} viven fuera, el {p(P_DIAS26)} %. Los de la diáspora han crecido un {p(VAR_DIAS)} % y los del país, un {p(VAR_NAC)} %. El mayor aumento está en el círculo de Europa y el resto del mundo, con un {p(VAR_EUR)} % más. La agencia <a href="{LUSA}">Lusa</a> daba en septiembre una cifra algo mayor, {n(426531)} inscritos; aquí se usa la de la web de la CNE.</p>
{g_ins}

<h2>Un presidente cuyo partido ya gobierna</h2>
<p data-tipo="contexto">En 2021, Neves llegó a la presidencia con un Gobierno del MpD. Eso cambió después: el PAICV ganó en diciembre de 2024 las municipales, en 14 concelhos, incluida Praia, según <a href="{WLEG}">Wikipedia</a>, que cita a Deutsche Welle, y en mayo de 2026 las legislativas, con mayoría absoluta: {LEG["PAICV"][1]} de los 72 diputados, según <a href="{RTP}">RTP</a>. Francisco Carvalho, exalcalde de Praia, es primer ministro.</p>
{g_leg}
<p data-tipo="dato">En las legislativas del 17 de mayo, el PAICV sacó el {p(LEG_PCT["PAICV"])} % de los votos a candidaturas y el MpD, el {p(LEG_PCT["MpD"])} %, según el edital de la CNE que recoge <a href="{WLEG}">Wikipedia</a>. Votó el {p(LEG_PART)} % de los inscritos.</p>
<p data-tipo="contexto">Joana Rosa ha hecho de esa mayoría su argumento principal.</p>
<blockquote class="cita"><p>«Neste momento temos uma força política no governo e que domina o poder local e o parlamento. [...] A ideia defendida por muitos, de que não se deve pôr os ovos todos num mesmo cesto, mostra-se perfeitamente necessária na actual conjuntura política»</p><footer>Joana Rosa, candidata apoyada por el MpD, en una entrevista con <a href="{EXP}">Expresso das Ilhas</a> (3-10-2026). «Ahora mismo tenemos una fuerza política en el Gobierno que domina el poder local y el parlamento. [...] La idea que defienden muchos de que no hay que poner todos los huevos en la misma cesta es perfectamente necesaria en la coyuntura política actual» (traducción propia)</footer></blockquote>
<blockquote class="cita"><p>«Cabo Verde precisa de um Presidente “sereno, experiente e com prestígio nacional e internacional”»</p><footer>Resumen de las palabras de José Maria Neves en un mitin en Porto Novo, según <a href="{BALAI}">Balai</a> (1-11-2026). «Cabo Verde necesita un presidente “sereno, experimentado y con prestigio nacional e internacional”» (traducción propia)</footer></blockquote>
<p data-tipo="hipotesis">El mapa de 2021 no dice cómo votará Cabo Verde el domingo: la elección es otra, con otra rival y con el PAICV en el Gobierno. Lo que sí muestra es dónde se decidió la última: en Santiago, que dio la mitad de los votos válidos, y en una diáspora que vota a Neves pero que vota poco. Con seis candidatos, la clave para evitar la segunda vuelta vuelve a estar en pasar de la mitad de los válidos.</p>
<p data-tipo="contexto">La CNE publicará los resultados provisionales en su web, <a href="{WEB}">eleicoes.cv</a>, la noche del domingo.</p>
"""
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')
preguntas = [
    ('¿Cuándo son las presidenciales de Cabo Verde?', 'El domingo 15 de noviembre de 2026. Si ningún candidato pasa de la mitad de los votos válidos, los dos primeros van a una segunda vuelta.'),
    ('¿Quiénes son los candidatos?', 'Seis: José Maria Neves (apoyado por el PAICV), Joana Rosa (apoyada por el MpD), Antero Tavares, Casimiro de Pina, Gilson Alves y Loisito Sousa.'),
    ('¿Cuánto sacó Neves en 2021?', f'El {p(PCT["neves"])} % de los votos válidos, {n(T.neves)} votos: {n(MARGEN)} más de la mitad. Ganó en {len(GANA_N)} de los 13 círculos.'),
]
enlaces = 'Más mapas electorales del mundo en <a href="../../temas/internacional/">Internacional</a>.'
foot = ('Datos: Comissão Nacional de Eleições, resultados de las presidenciales de 2021 por círculo (edital publicado en el Boletim Oficial '
        'del 30-10-2021), inscritos de 2026 de la web oficial de resultados y legislativas de 2026; contornos de geoBoundaries (OpenStreetMap). '
        'Cálculo: actualidad/src/resumenes/cabo_verde.py.')
r4 = lambda x: round(float(x), 4)
DATOS = {'CIRC': {r.circulo: {'neves': int(r.neves), 'veiga': int(r.veiga), 'validos': int(r.validos), 'inscritos': int(r.inscritos), 'ins26': int(r.ins26),
                              '%neves': r4(r['%neves']), '%veiga': r4(r['%veiga']), 'part': r4(r.part), 'var_ins': r4(r.var_ins), 'gana': r.gana}
                  for _, r in d.iterrows()},
         'T': {k: int(v) for k, v in T.items()}, 'PCT': {k: r4(v) for k, v in PCT.items()}, 'PART': r4(PART), 'MITAD': float(MITAD), 'MARGEN': MARGEN,
         'GANA_N': GANA_N, 'GANA_V': GANA_V, 'PART_NAC': r4(PART_NAC), 'PART_DIA': r4(PART_DIA), 'VENT_SANT': int(VENT_SANT), 'VENT_TOTAL': int(VENT_TOTAL),
         'DIAS_NEVES': int(DIAS_NEVES), 'SANT_PCT': r4(SANT_PCT), 'INS26': INS26, 'DIAS26': DIAS26, 'P_DIAS26': r4(P_DIAS26),
         'VAR_TOT': r4(VAR_TOT), 'VAR_DIAS': r4(VAR_DIAS), 'VAR_NAC': r4(VAR_NAC), 'VAR_EUR': r4(VAR_EUR),
         'LEG': {k: [v, s] for k, (v, s) in LEG.items()}, 'LEG_PCT': {k: r4(v) for k, v in LEG_PCT.items()}, 'LEG_PART': r4(LEG_PART)}
scripts = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
if __name__ == '__main__':
    pieza(SLUG, 'Cabo Verde elige presidente', H1, DEK, '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts)
    print(H1)
    print(DEK)
    print('margen', MARGEN, 'gana', GANA_N, GANA_V, 'part', p(PART), p(PART_NAC), p(PART_DIA), 'sant', VENT_SANT, VENT_TOTAL, DIAS_NEVES,
          'ins', INS26, p(P_DIAS26), p(VAR_TOT), p(VAR_DIAS), p(VAR_NAC), p(VAR_EUR), 'leg', {k: p(v) for k, v in LEG_PCT.items()}, p(LEG_PART))
