"""«El primer día de campaña, en el mapa» (13-11-2026). Agenda del viernes 13 de noviembre según EFE (vía Infobae): Sánchez
en Arnedo y Pamplona; Abascal en Toledo; Montero y Rufián en Palma; Nogueras en Reus; Matute en Eibar; Vaquero en Bilbao;
Pontón en Lugo, Monforte de Lemos y Pontevedra; Valido en Santa Cruz de Tenerife. Feijóo y Colau, en Madrid.
La pieza cuenta quién ganó en cada uno de esos municipios en noviembre de 2019 y en julio de 2023, cómo le fue allí al
partido de cada candidato y qué le da a ese partido en su provincia la media de encuestas del 29N.

Votos: resultados al Congreso por sección censal (generales-2026/descargas/resultados_secciones_largo.csv, Ministerio del
Interior) sumados por municipio, sin el voto exterior (CERA). Porcentaje sobre votos válidos (candidaturas y blancos),
calculado con los votos. En noviembre de 2019, la familia PP de Navarra es Navarra Suma (UPN, PP y Cs), y la familia
SUMAR, Unidas Podemos (más Más País donde se presentó; en estos municipios solo en Palma no, ver MES).
Modelo: previsiones/datos/publico/historico (la última versión), escenario central por provincia.
Uso, desde la raíz: python3 actualidad/src/resumenes/primer_dia_campana.py
"""
import json

import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
EFE = 'https://www.infobae.com/espana/agencias/2026/11/13/comienza-la-campana-de-pamplona-a-madrid-pasando-por-youtube/'
EP_PALMA = 'https://www.ultimahora.es/noticias/elecciones-29n/2026/11/10/2747037/gabriel-rufian-aterriza-palma-mitin-junto-irene-montero-candidata-ara-mes-front-ampli.html'
BOE = 'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-23103'

E19, E23 = '2019_11', '2023_07'
NOM = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'SUMAR': 'Sumar', 'ERC': 'ERC', 'JUNTS': 'Junts', 'PNV': 'PNV',
       'BILDU': 'EH Bildu', 'BNG': 'BNG', 'CC': 'CC', 'UPN': 'UPN', 'NAS': 'Navarra Suma', 'UP': 'Unidas Podemos'}
COL = {'PP': 'var(--pp)', 'PSOE': 'var(--psoe)', 'VOX': 'var(--vox)', 'SUMAR': 'var(--sumar)', 'UP': 'var(--sumar)',
       'ERC': 'var(--erc)', 'JUNTS': 'var(--junts)', 'PNV': 'var(--pnv)', 'BILDU': 'var(--bildu)', 'BNG': 'var(--bng)',
       'CC': 'var(--cc)', 'UPN': '#0f4c8a', 'NAS': '#3d6fb6'}
FAMS = ['PP', 'PSOE', 'VOX', 'SUMAR', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC', 'UPN', 'NC', 'CUP', 'MES', 'OTROS']

# lugar, código INE, provincia, nombre de la provincia, quién va, partido (familia del fichero), lista del modelo
LUGARES = [
    ('Arnedo', '26018', '26', 'La Rioja', 'Pedro Sánchez', 'PSOE', 'PSOE'),
    ('Pamplona', '31201', '31', 'Navarra', 'Pedro Sánchez', 'PSOE', 'PSOE'),
    ('Toledo', '45168', '45', 'Toledo', 'Santiago Abascal', 'VOX', 'Vox'),
    ('Palma', '07040', '07', 'Illes Balears', 'Irene Montero y Gabriel Rufián', 'SUMAR', 'Sumar'),
    ('Reus', '43123', '43', 'Tarragona', 'Míriam Nogueras', 'JUNTS', 'Junts'),
    ('Eibar', '20030', '20', 'Gipuzkoa', 'Oskar Matute', 'BILDU', 'EH Bildu'),
    ('Bilbao', '48020', '48', 'Bizkaia', 'Maribel Vaquero', 'PNV', 'PNV'),
    ('Lugo', '27028', '27', 'Lugo', 'Ana Pontón', 'BNG', 'BNG'),
    ('Monforte de Lemos', '27031', '27', 'Lugo', 'Ana Pontón', 'BNG', 'BNG'),
    ('Pontevedra', '36038', '36', 'Pontevedra', 'Ana Pontón', 'BNG', 'BNG'),
    ('Santa Cruz de Tenerife', '38038', '38', 'Santa Cruz de Tenerife', 'Cristina Valido', 'CC', 'CC'),
]

lar = pd.read_csv(RAIZ / 'generales-2026/descargas/resultados_secciones_largo.csv', dtype={'tract_code': str, 'mun_code': str})
lar = lar[lar.eleccion.isin([E19, E23])].copy()
lar['prov'] = lar.tract_code.str[:2]
for c in FAMS:
    lar[c] = lar[c].fillna(0) if c in lar else 0


def res(mask, e):
    s = lar[mask & (lar.eleccion == e)]
    val = (s.candidaturas + s.blancos).sum()
    v = {k: int(s[k].sum()) for k in FAMS}
    return {'votos': v, 'validos': int(val), 'pct': {k: x / val * 100 for k, x in v.items()},
            'censo': int(s.censo.sum()), 'part': s.votantes.sum() / s.censo.sum() * 100}


def ganador(r, e, prov):
    """Lista más votada (sin «otros»). Navarra 2019: la familia PP es Navarra Suma."""
    v = {k: x for k, x in r['votos'].items() if k not in ('OTROS',)}
    top = sorted(v.items(), key=lambda kv: -kv[1])
    assert top[0][1] > top[1][1]
    g = top[0][0]
    if g == 'PP' and prov == '31' and e == E19:
        return 'NAS'
    if g == 'SUMAR' and e == E19:
        return 'UP'
    return g


U = {}
for nom, mun, pr, *_ in LUGARES:
    U[nom] = {e: res(lar.mun_code == mun, e) for e in (E19, E23)}
    U[nom]['prov'] = {e: res(lar.prov == pr, e) for e in (E19, E23)}
G = {nom: {e: ganador(U[nom][e], e, pr) for e in (E19, E23)} for nom, mun, pr, *_ in LUGARES}
assert all(G[x][E19] != G[x][E23] for x in G), G
G23 = pd.Series([G[x][E23] for x in G]).value_counts().to_dict()
G19 = pd.Series([G[x][E19] for x in G]).value_counts().to_dict()
assert G23 == {'PP': 7, 'PSOE': 4} and G19 == {'PSOE': 7, 'PNV': 2, 'NAS': 1, 'ERC': 1}, (G19, G23)


def dif(r, a, b):
    return (r['votos'][a] - r['votos'][b]) / r['validos'] * 100


AR, PA, TO, PM, RE, EI, BI, LU, MO, PO, SC = (U[x[0]][E23] for x in LUGARES)
AR19, TO19, LU19, BI19, EI19, RE19, SC19 = (U[x][E19] for x in ('Arnedo', 'Toledo', 'Lugo', 'Bilbao', 'Eibar', 'Reus', 'Santa Cruz de Tenerife'))
D_AR = dif(AR, 'PP', 'PSOE')
D_AR19 = dif(AR19, 'PSOE', 'PP')
D_BI = dif(BI, 'PSOE', 'PNV')
D_LU19 = LU19['votos']['PSOE'] - LU19['votos']['PP']   # en votos: 2019, por muy poco
assert 0 < D_LU19 < 100, D_LU19
UPNPP_PA = PA['pct']['UPN'] + PA['pct']['PP']
assert UPNPP_PA > PA['pct']['PSOE']
POS = {}   # puesto del partido de cada candidato en su municipio en 2023
for nom, mun, pr, prn, quien, fam, lista in LUGARES:
    orden = [k for k, _ in sorted(U[nom][E23]['votos'].items(), key=lambda kv: -kv[1]) if k != 'OTROS']
    POS[nom] = orden.index(fam) + 1
assert POS == {'Arnedo': 2, 'Pamplona': 1, 'Toledo': 3, 'Palma': 4, 'Reus': 6, 'Eibar': 2, 'Bilbao': 2,
               'Lugo': 3, 'Monforte de Lemos': 3, 'Pontevedra': 4, 'Santa Cruz de Tenerife': 3}, POS
PESO = {nom: U[nom][E23]['censo'] / U[nom]['prov'][E23]['censo'] * 100 for nom, *_ in LUGARES}

# --- Modelo: escenario central de la última versión ---
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
VERSION = f'{int(_hm[:2])}.{_hm[2:]} del {int(_d)} de noviembre de {_a}'


def modelo(pr, lista):
    d = MOD['provincias'][pr]
    l = next((x for x in d['listas'] if x['lista'] == lista), None)
    return {'total': d['escanos_total'], 'esc': l['escanos'] if l else [0, 0, 0], 'voto': l['voto'] if l else None,
            'p1': l['p_primera'] if l else 0}


PROVS = []   # una fila por provincia (Lugo sale una vez)
for nom, mun, pr, prn, quien, fam, lista in LUGARES:
    if pr not in [x[0] for x in PROVS]:
        PROVS.append((pr, prn, quien, fam, lista, modelo(pr, lista)))
M = {pr: m for pr, *_, m in PROVS}
SIM = json.load(open(RAIZ / 'actualidad/src/sistema/simulador.json'))


def dhondt(cod, e=E23):
    """Escaños de 2023 con los votos oficiales de la provincia (3 % de barrera)."""
    v, val, k = SIM['elecciones'][e][cod]['v'], SIM['elecciones'][e][cod]['validos'], SIM['escanos'][e][cod]
    v = {q: x for q, x in v.items() if x >= 0.03 * val}
    cs = sorted(((x / d, q) for q, x in v.items() for d in range(1, k + 1)), reverse=True)[:k]
    r = {}
    for _, q in cs:
        r[q] = r.get(q, 0) + 1
    return r


ESC23 = {pr: dhondt(pr) for pr, *_ in PROVS}

# --- Gráfico 1: ganador en 2019 y en 2023 ---


def chips(W=360, ml=150, alto=30):
    out, y = [], 26
    cw = (W - ml - 26) / 2
    out.append(f'<text x="{ml + cw / 2:.0f}" y="14" text-anchor="middle" class="lab">Nov. 2019</text>'
               f'<text x="{ml + cw + 26 + cw / 2:.0f}" y="14" text-anchor="middle" class="lab">Jul. 2023</text>')
    for nom, *_ in LUGARES:
        out.append(f'<text x="{ml - 8}" y="{y + 18}" text-anchor="end" class="lab">{esc(nom)}</text>')
        for i, e in enumerate((E19, E23)):
            g = G[nom][e]
            x = ml + i * (cw + 26)
            out.append(f'<rect x="{x:.0f}" y="{y + 3}" width="{cw:.0f}" height="{alto - 7}" rx="3" fill="{COL[g]}"><title>{esc(nom)}, {"2019" if i == 0 else "2023"}: {NOM[g]}</title></rect>'
                       f'<text x="{x + cw / 2:.0f}" y="{y + 19}" text-anchor="middle" style="fill:#fff;font-weight:600">{esc(NOM[g])}</text>')
        out.append(f'<text x="{ml + cw + 13:.0f}" y="{y + 19}" text-anchor="middle" class="lab">→</text>')
        y += alto
    return f'<svg viewBox="0 0 {W} {y + 4}" role="img" aria-label="Partido más votado en 2019 y en 2023 en los once municipios">' + ''.join(out) + '</svg>'


g_gan = figura(f'Los once cambiaron de ganador: el PSOE ganó en {G19["PSOE"]} en 2019; en 2023, el PP ganó en {G23["PP"]}',
               'Lista más votada en las generales de noviembre de 2019 y de julio de 2023 en los municipios que visitan los candidatos el primer día de campaña, fuera de Madrid y Barcelona',
               chips(), 'Fuente: Ministerio del Interior, resultados por sección censal sumados por municipio, sin voto exterior. '
               'En Navarra, Navarra Suma (UPN, PP y Cs) en 2019; UPN y PP fueron por separado en 2023. Cálculo propio.',
               [(NOM[k], COL[k]) for k in ('PSOE', 'PP', 'PNV', 'ERC', 'NAS')],
               (['Municipio', 'Quién va', 'Ganador 2019', 'Ganador 2023'],
                [[nom, quien, NOM[G[nom][E19]], NOM[G[nom][E23]]] for nom, mun, pr, prn, quien, *_ in LUGARES]))

# --- Gráfico 2: el partido de cada candidato en el municipio, 2019 y 2023 ---
SIN_PALMA = [x for x in LUGARES if x[0] != 'Palma']   # en Palma, Sumar 2023 no es la lista de Montero ni de Rufián


def dos(W=360, ml=150, alto=36, maximo=45):
    out, y = [], 4
    x = lambda v: ml + v / maximo * (W - ml - 92)
    for nom, mun, pr, prn, quien, fam, lista in SIN_PALMA:
        a, b = U[nom][E19]['pct'][fam], U[nom][E23]['pct'][fam]
        out.append(f'<text x="{ml - 8}" y="{y + 12}" text-anchor="end" class="lab">{esc(nom)}</text>'
                   f'<text x="{ml - 8}" y="{y + 27}" text-anchor="end" class="lab" style="fill:var(--muted)">{esc(NOM[fam])}</text>')
        for k, (v, op, et) in enumerate(((a, .38, '2019'), (b, 1, '2023'))):
            yy = y + 3 + k * 15
            out.append(f'<rect x="{ml}" y="{yy}" width="{max(1.5, x(v) - ml):.1f}" height="12" fill="{COL[fam]}" fill-opacity="{op}" rx="2"><title>{NOM[fam]} en {esc(nom)}, {et}: {p(v)} %</title></rect>'
                       f'<text x="{x(v) + 5:.1f}" y="{yy + 10}">{p(v)}{" % (" + et + ")" if nom == "Arnedo" else ""}</text>')
        y += alto
    return f'<svg viewBox="0 0 {W} {y}" role="img" aria-label="Voto al partido de cada candidato en el municipio que visita, 2019 y 2023">' + ''.join(out) + '</svg>'


g_par = figura(f'El PNV bajó del {p(BI19["pct"]["PNV"])} % al {p(BI["pct"]["PNV"])} % en Bilbao; EH Bildu subió en Eibar',
               'Voto al partido de cada candidato en el municipio que visita hoy, en noviembre de 2019 (barra clara) y en julio de 2023. Porcentaje sobre votos válidos, sin voto exterior',
               dos(), 'Fuente: Ministerio del Interior, resultados por sección censal sumados por municipio. Sin Palma: Podemos y ERC no presentan '
               'lista en Baleares, y Sumar de 2023 no es la candidatura que apoyan. Cálculo propio.', None,
               (['Municipio', 'Partido', 'Nov. 2019 (%)', 'Jul. 2023 (%)', 'Puesto en 2023'],
                [[nom, NOM[fam], p(U[nom][E19]['pct'][fam]), p(U[nom][E23]['pct'][fam]), f'{POS[nom]}.º'] for nom, mun, pr, prn, quien, fam, lista in SIN_PALMA]))

# --- Gráfico 3: lo que da el modelo a ese partido en la provincia ---
FILAS_M = [(pr, prn, fam, lista, m) for pr, prn, quien, fam, lista, m in PROVS if pr != '07']


CORTO = {'Santa Cruz de Tenerife': 'S. C. de Tenerife'}


def escanos(W=360, ml=150, alto=30):
    k = max(m['total'] for *_, m in FILAS_M)
    x = lambda v: ml + v / k * (W - ml - 60)
    out, y = [], 4
    for pr, prn, fam, lista, m in FILAS_M:
        lo, me, hi = m['esc']
        out.append(f'<text x="{ml - 8}" y="{y + 17}" text-anchor="end" class="lab">{esc(NOM[fam])}, {esc(CORTO.get(prn, prn))}</text>'
                   f'<rect x="{ml}" y="{y + 5}" width="{x(m["total"]) - ml:.1f}" height="16" fill="var(--rule)" rx="2"/>'
                   f'<rect x="{ml}" y="{y + 5}" width="{max(1.5, x(me) - ml):.1f}" height="16" fill="{COL[fam]}" rx="2"><title>{NOM[fam]} en {esc(prn)}: {me} de {m["total"]} (entre {lo} y {hi})</title></rect>'
                   f'<text x="{x(m["total"]) + 5:.1f}" y="{y + 17}">{me} de {m["total"]}</text>')
        y += alto
    return f'<svg viewBox="0 0 {W} {y}" role="img" aria-label="Escaños del escenario central para el partido de cada candidato en la provincia que visita">' + ''.join(out) + '</svg>'


g_mod = figura(f'La media de encuestas deja al PSOE con {M["26"]["esc"][1]} de los 4 escaños de La Rioja y da a Vox {M["45"]["esc"][1]} en Toledo',
               f'Escaños del escenario central del modelo de mapaelectoral.es para el partido de cada candidato en la provincia que visita hoy, de los que reparte la provincia (en gris). Versión de las {VERSION}',
               escanos(), f'Fuente: <a href="{BASE}encuestas/">modelo de encuestas de mapaelectoral.es</a> (media de encuestas repartida por provincia); escaños de 2023, '
               'Ministerio del Interior. Sin Baleares: Podemos y ERC no presentan lista allí. Margen amplio a 16 días de la votación.', None,
               (['Partido y provincia', 'Escaños en 2023', 'Escenario central', 'Intervalo del 80 %', 'Escaños de la provincia'],
                [[f'{NOM[fam]}, {prn}', str(ESC23[pr].get(lista, 0)),
                  str(m['esc'][1]), f'{m["esc"][0]}-{m["esc"][2]}', str(m['total'])] for pr, prn, fam, lista, m in FILAS_M]))

PSOE_RIOJA23 = ESC23['26']['PSOE']
assert PSOE_RIOJA23 == 2 and M['26']['esc'][1] == 1 and ESC23['45']['Vox'] == 1 and M['45']['esc'][1] == 2
assert ESC23['43']['Junts'] == 1 and M['43']['esc'][1] == 0 and ESC23['36'].get('BNG', 0) == 0 and M['36']['esc'][1] == 1
assert ESC23['27'].get('BNG', 0) == 0 and M['27']['esc'][1] == 0 and ESC23['20']['EH Bildu'] == 2 and M['20']['esc'][1] == 3
assert M['45']['esc'][1] == next(x for x in MOD['provincias']['45']['listas'] if x['lista'] == 'PSOE')['escanos'][1]
assert all(G[x][E19] == 'PSOE' and G[x][E23] == 'PP' for x in ('Arnedo', 'Toledo', 'Palma', 'Lugo', 'Monforte de Lemos', 'Pontevedra', 'Santa Cruz de Tenerife'))
assert all(G[x][E23] == 'PSOE' for x in ('Bilbao', 'Eibar', 'Reus', 'Pamplona'))
assert ESC23['38']['CC'] == 1 and M['38']['esc'][1] == 1 and ESC23['48']['PNV'] == 2 and M['48']['esc'][1] == 2
LEMA = 'https://www.pressdigital.es/articulo/politica/2026-11-13/6090037-sanchez-arranca-viernes-primer-dia-campana-doble-mitin-arnedo-rioja-pamplona'
PC = lambda nom, k, e=E23: p(U[nom][e]['pct'][k])
PV = lambda nom, k, e=E23: p(U[nom]['prov'][e]['pct'][k])
ME = lambda pr: M[pr]['esc']

cuerpo = f"""
<p data-tipo="contexto">La campaña del 29N empezó a medianoche, y este viernes es su primer día completo. Según la agenda que ha difundido <a href="{EFE}">EFE</a>, Pedro Sánchez va a Arnedo (La Rioja) y a Pamplona, con la presidenta navarra, María Chivite, y la candidata Elma Saiz; Alberto Núñez Feijóo hace su primer acto en Madrid, con Nuevas Generaciones e Isabel Díaz Ayuso; Santiago Abascal viaja a Toledo antes de volver a la plaza de Colón, y Ada Colau participa en Madrid en un diálogo sobre regeneración democrática. Irene Montero comparte mitin en Palma con Gabriel Rufián; Míriam Nogueras (Junts), a Barcelona por la mañana y a Reus por la tarde; Oskar Matute (EH Bildu), a Eibar; Maribel Vaquero (PNV), a Bilbao; Ana Pontón (BNG), a Lugo, Monforte de Lemos y Pontevedra, y Cristina Valido (Coalición Canaria), a Santa Cruz de Tenerife.</p>
<p data-tipo="dato">Fuera de Madrid y Barcelona son once municipios, y los once cambiaron de ganador entre las dos últimas generales. En noviembre de 2019, el PSOE fue el más votado en {G19["PSOE"]} de ellos; el PNV, en Bilbao y Eibar; ERC, en Reus, y Navarra Suma, en Pamplona. En julio de 2023, el PP ganó en {G23["PP"]} y el PSOE, en los otros {G23["PSOE"]}. En 2023, el partido del candidato que va de visita solo fue el más votado en uno: Pamplona, que ganó el PSOE.</p>
{g_gan}

<h2>Sánchez, en Arnedo y Pamplona</h2>
<p data-tipo="dato">Arnedo tiene el {p(PESO["Arnedo"])} % del censo de La Rioja. En noviembre de 2019, el PSOE ganó allí con el {PC("Arnedo", "PSOE", E19)} %, {p(D_AR19)} puntos por delante del PP. En julio de 2023 ganó el PP, con el {PC("Arnedo", "PP")} % frente al {PC("Arnedo", "PSOE")} % del PSOE: {p(D_AR)} puntos de diferencia. El PSOE sacó {PSOE_RIOJA23} de los 4 diputados riojanos en 2023; el escenario central de la media de encuestas le da {ME("26")[1]}, con un intervalo de {ME("26")[0]} a {ME("26")[2]}.</p>
<p data-tipo="dato">Pamplona es la excepción del día. En 2019 la ganó Navarra Suma, la coalición de UPN, PP y Ciudadanos, con el {PC("Pamplona", "PP", E19)} %. En 2023, con UPN y el PP por separado, el PSN fue el más votado, con el {PC("Pamplona", "PSOE")} %, y por detrás quedaron EH Bildu ({PC("Pamplona", "BILDU")} %), el PP ({PC("Pamplona", "PP")} %) y UPN ({PC("Pamplona", "UPN")} %). Sumados, UPN y el PP llegaban al {p(UPNPP_PA)} %. El 29N vuelven a ir juntos, en la lista UPN-PP, como contamos en {L("mapa-electoral-navarra-29n", "el mapa electoral de Navarra")}. La media de encuestas da al PSOE {ME("31")[1]} de los 5 escaños navarros (entre {ME("31")[0]} y {ME("31")[2]}).</p>
<p data-tipo="contexto">El PSOE ha elegido como lema «Vota con fuerza», según fuentes de Ferraz citadas por <a href="{LEMA}">Pressdigital</a>, que añade que Sánchez irá el sábado a Palma.</p>

<h2>Abascal, en Toledo: Vox, tercero en la ciudad</h2>
<p data-tipo="dato">Toledo pasó del PSOE al PP entre 2019 y 2023. Vox fue tercero en las dos: sacó el {PC("Toledo", "VOX", E19)} % en noviembre de 2019 y el {PC("Toledo", "VOX")} % en 2023, menos que en el conjunto de la provincia ({PV("Toledo", "VOX")} %). En la provincia, Vox tuvo {ESC23["45"]["Vox"]} de los 6 escaños en 2023; la media de encuestas le da {ME("45")[1]} (entre {ME("45")[0]} y {ME("45")[2]}), la misma cifra que al PSOE.</p>

<h2>Montero y Rufián, en Palma, donde no se presentan</h2>
<p data-tipo="dato">Ni Podemos ni ERC presentan lista propia al Congreso en Baleares, según las candidaturas proclamadas en el <a href="{BOE}">BOE</a>. En el mitin, a las 18.00 en el colegio Son Oliva, intervienen también la cabeza de lista de Ara Més-Front Ampli, Carme Gomila, y su número tres, Lucía Muñoz, que va como independiente por el acuerdo con Podemos, según <a href="{EP_PALMA}">Europa Press</a>. Rufián es el candidato de ERC por Barcelona. Palma, con el {p(PESO["Palma"])} % del censo de las islas, la ganó el PSOE en 2019 y el PP en 2023, con el {PC("Palma", "PP")} % frente al {PC("Palma", "PSOE")} %.</p>

<h2>Junts, EH Bildu y el PNV, en terreno ajeno</h2>
<p data-tipo="dato">Nogueras, cabeza de lista de Junts por Barcelona, va por la tarde a Reus, en la provincia de Tarragona. En 2019 ganó allí ERC; en 2023, el PSOE, con el {PC("Reus", "PSOE")} %, y Junts quedó sexto, con el {PC("Reus", "JUNTS")} %. En la provincia, Junts tuvo {ESC23["43"]["Junts"]} de los 6 escaños en 2023; el escenario central le da {ME("43")[1]} (hasta {ME("43")[2]}).</p>
<p data-tipo="dato">Los candidatos vascos van cada uno a la provincia del otro. Matute, número uno de EH Bildu por Bizkaia, abre en Eibar, en Gipuzkoa, donde su partido subió del {PC("Eibar", "BILDU", E19)} % al {PC("Eibar", "BILDU")} % y quedó segundo, detrás del PSOE ({PC("Eibar", "PSOE")} %). Vaquero, número uno del PNV por Gipuzkoa, va a Bilbao, que el PNV ganó en 2019 con el {PC("Bilbao", "PNV", E19)} % y perdió en 2023: bajó al {PC("Bilbao", "PNV")} %, {p(D_BI)} puntos por detrás del PSOE. La media de encuestas da a EH Bildu {ME("20")[1]} de los 6 escaños de Gipuzkoa (tuvo {ESC23["20"]["EH Bildu"]}) y al PNV, {ME("48")[1]} de los 8 de Bizkaia, los mismos que en 2023.</p>
{g_par}

<h2>Pontón, en tres municipios que ganó el PSOE en 2019 y el PP en 2023</h2>
<p data-tipo="dato">Lugo, Monforte de Lemos y Pontevedra pasaron del PSOE al PP. En Lugo, en noviembre de 2019, el PSOE ganó por {D_LU19} votos; en 2023, el PP sacó el {PC("Lugo", "PP")} % y el PSOE, el {PC("Lugo", "PSOE")} %. El BNG fue tercero en Lugo ({PC("Lugo", "BNG")} %) y en Monforte ({PC("Monforte de Lemos", "BNG")} %), y cuarto en Pontevedra ({PC("Pontevedra", "BNG")} %). En 2023 no sacó escaño ni en Lugo ni en Pontevedra; la media de encuestas le da {ME("36")[1]} en Pontevedra (entre {ME("36")[0]} y {ME("36")[2]}) y {ME("27")[1]} en Lugo, aunque puede llegar a {ME("27")[2]}.</p>

<h2>Valido, en Santa Cruz de Tenerife</h2>
<p data-tipo="dato">Santa Cruz pasó del PSOE al PP: en 2023, el PP sacó el {PC("Santa Cruz de Tenerife", "PP")} %, el PSOE el {PC("Santa Cruz de Tenerife", "PSOE")} % y Coalición Canaria, tercera, el {PC("Santa Cruz de Tenerife", "CC")} %, por debajo de su {PV("Santa Cruz de Tenerife", "CC")} % en la provincia. CC tuvo {ESC23["38"]["CC"]} de los 7 escaños de la provincia en 2023; el escenario central le da {ME("38")[1]} (hasta {ME("38")[2]}).</p>
{g_mod}

<p data-tipo="hipotesis">Los once cambios siguen dos caminos. Fuera del País Vasco, Navarra y Cataluña, los siete municipios pasaron del PSOE al PP. En Bilbao, Eibar, Reus y Pamplona, el PSOE pasó a ser el más votado. Lo que no dicen estos datos es por qué cada partido ha elegido cada sitio: un acto de campaña puede buscar votos, cámaras o apoyar a un candidato local.</p>

<h2>Cómo se ha hecho</h2>
<p data-tipo="contexto">La agenda es la de <a href="{EFE}">EFE</a> del 13 de noviembre; puede cambiar a lo largo del día. Los resultados son los de las generales al Congreso de noviembre de 2019 y julio de 2023 del Ministerio del Interior, por sección censal y sumados por municipio, sin el voto de los residentes en el extranjero. Los porcentajes son sobre votos válidos y las diferencias se calculan con los votos. Los escaños de 2023 se calculan con la ley D'Hondt sobre los votos oficiales de cada provincia, y los del 29N son el escenario central del <a href="{BASE}encuestas/">modelo de encuestas</a> (versión de las {VERSION}). Ver también {L("arranque-campana-sevilla-badalona-colon-vallecas-29n", "dónde abrió cada uno la campaña")}.</p>
"""
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

preguntas = [
    ('¿Dónde están los candidatos el primer día de campaña del 29N?', f'Sánchez, en Arnedo y Pamplona; Feijóo, en Madrid; Abascal, en Toledo y Madrid; Colau, en Madrid; Montero, con Rufián, en Palma; Nogueras, en Barcelona y Reus; Matute, en Eibar; Vaquero, en Bilbao; Pontón, en Lugo, Monforte de Lemos y Pontevedra, y Valido, en Santa Cruz de Tenerife. Fuente: <a href="{EFE}">EFE</a>.'),
    ('¿Quién ganó en Arnedo en las generales?', f'El PSOE en noviembre de 2019 ({PC("Arnedo", "PSOE", E19)} %) y el PP en julio de 2023 ({PC("Arnedo", "PP")} %, frente al {PC("Arnedo", "PSOE")} % del PSOE).'),
    ('¿Se presentan Podemos y ERC en Baleares?', f'No con lista propia al Congreso. Lucía Muñoz, independiente por el acuerdo con Podemos, es la número tres de Ara Més-Front Ampli (<a href="{BOE}">BOE</a>; <a href="{EP_PALMA}">Europa Press</a>).'),
]
enlaces = (f'{L("arranque-campana-sevilla-badalona-colon-vallecas-29n", "Dónde abrió cada uno la campaña")} · {L("mapa-electoral-navarra-29n", "El mapa electoral de Navarra")} · '
           f'<a href="{BASE}encuestas/">Encuestas del 29N</a>')
foot = ('Datos: Ministerio del Interior, generales al Congreso de noviembre de 2019 y julio de 2023 por sección censal y por provincia; '
        'modelo de encuestas de mapaelectoral.es. Cálculo: actualidad/src/resumenes/primer_dia_campana.py.')

r4 = lambda x: round(float(x), 4)
DATOS = {'U': {nom: {e: {'pct': {k: r4(v) for k, v in U[nom][e]['pct'].items()}, 'votos': U[nom][e]['votos'], 'validos': U[nom][e]['validos'],
                         'censo': U[nom][e]['censo'], 'part': r4(U[nom][e]['part'])} for e in (E19, E23)}
               | {'prov': {e: {'pct': {k: r4(v) for k, v in U[nom]['prov'][e]['pct'].items()}, 'censo': U[nom]['prov'][e]['censo']} for e in (E19, E23)}}
               for nom, *_ in LUGARES},
         'G': G, 'G19': G19, 'G23': G23, 'POS': POS, 'PESO': {k: r4(v) for k, v in PESO.items()},
         'D_AR': r4(D_AR), 'D_AR19': r4(D_AR19), 'D_BI': r4(D_BI), 'D_LU19': int(D_LU19), 'UPNPP_PA': r4(UPNPP_PA),
         'ESC23': ESC23, 'M': {pr: m for pr, m in M.items()}}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

H1 = 'Los once municipios que visitan los candidatos el primer día de campaña, fuera de Madrid y Barcelona, cambiaron de ganador entre 2019 y 2023'
DEK = (f'Sánchez va a Arnedo, que el PSOE ganó por {p(D_AR19)} puntos en 2019 y perdió por {p(D_AR)} en 2023; Vaquero (PNV), a Bilbao, '
       f'donde el PSOE superó al PNV por {p(D_BI)} puntos. Solo en Pamplona fue el más votado en 2023 el partido del candidato que va de visita.')
if __name__ == '__main__':
    pieza('primer-dia-campana-municipios-29n', 'El primer día de campaña, en el mapa', H1, DEK, '13 de noviembre de 2026',
          cuerpo, preguntas, enlaces, foot, scripts=datos_js)
    print(H1)
    print(DEK)
    print(G19, G23, POS, {k: p(v) for k, v in PESO.items()}, ESC23, {k: v['esc'] for k, v in M.items()})
