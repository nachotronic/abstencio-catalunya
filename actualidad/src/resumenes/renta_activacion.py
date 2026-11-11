"""«La renta de activación del PP y el ingreso mínimo vital» (11-11-2026). El 10 de noviembre, en la presentación del
programa del PP, Feijóo anunció que reunirá el ingreso mínimo vital (IMV) y los subsidios en una «renta de activación»
vinculada a la búsqueda de empleo (Europa Press). La pieza muestra a quién llega hoy el IMV, provincia a provincia, y
cómo votaron en 2023 las provincias donde más pesa.

IMV: Instituto Nacional de la Seguridad Social, «Dossier comunidad autónoma y provincia», nómina de octubre de 2026
(beneficiarios por provincia de la entidad gestora, con País Vasco y Navarra, que gestionan el IMV), y nómina de
octubre de 2025 para la variación anual. Población: INE, Estadística Continua de Población, 1 de enero de 2025
(tabla 56945). Copia de los datos en actualidad/src/resumenes/datos/imv_provincias_2026_10.csv.
Voto: resultados oficiales de las generales de julio de 2023 por provincia (actualidad/src/sistema/simulador.json),
porcentaje sobre votos válidos.
Uso, desde la raíz: python3 actualidad/src/resumenes/renta_activacion.py
"""
import json

import numpy as np
import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, barras, mapa_provincias, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
pr = lambda v: n(v, 2)
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
EP = 'https://www.europapress.es/nacional/noticia-feijoo-reunira-ingreso-minimo-vital-subsidios-renta-activacion-vinculada-busqueda-empleo-20261110143401.html'
SS = 'https://revista.seg-social.es/-/el-ingreso-m%C3%ADnimo-vital-protege-en-octubre-a-cerca-de-2-8-millones-de-personas-que-viven-en-911.274-hogares'
SS_XLSX = ('https://revista.seg-social.es/documents/39386/0/202610+COMPLETO+Dossier+comunidad+aut%C3%B3noma+y+provincia.xlsx/'
           'e51fe86b-d3f1-8ea2-cc5d-4f74a1d12eda?t=1794301241117')
INE = 'https://www.ine.es/jaxiT3/Tabla.htm?t=56945'

sim = json.load(open(RAIZ / 'actualidad/src/sistema/simulador.json'))
E = sim['elecciones']['2023_07']
CCAA = {c: ca for ca, cods in sim['ccaa'].items() for c in cods.split()}
d = pd.read_csv(RAIZ / 'actualidad/src/resumenes/datos/imv_provincias_2026_10.csv', dtype={'cod': str})
assert len(d) == 52
d['ben'] = d.beneficiarios_2026_10
d['pob'] = d.poblacion_2025_01_01
assert d.ben.sum() == 2781679 and d.beneficiarios_2025_10.sum() == 2363554 and d.pob.sum() == 49128297
d['tasa'] = d.ben / d.pob * 100
d['nom'] = [sim['provincias'][c] for c in d.cod]
PARTIDOS = [('PP', 'var(--pp)'), ('PSOE', 'var(--psoe)'), ('Vox', 'var(--vox)'), ('Sumar', 'var(--sumar)')]
for k, _ in PARTIDOS:
    d[k] = [E[c]['v'].get(k, 0) / E[c]['validos'] * 100 for c in d.cod]
d = d.sort_values('tasa', ascending=False).reset_index(drop=True)
D = {r.nom: r for r in d.itertuples()}

# Cifras nacionales (nota de la Seguridad Social, nómina de octubre de 2026)
HOG, BEN, CUANT, NOMINA, MEN, PMEN = 911274, 2781679, 524.6, 748.2, 1120877, 40.3
TASA_ES = d.ben.sum() / d.pob.sum() * 100
VAR_ES = (d.ben.sum() / d.beneficiarios_2025_10.sum() - 1) * 100
assert round(VAR_ES, 1) == 17.7
CAPI = int(d.imv_capi.sum())
assert CAPI == 1389715
MAS10 = d[d.tasa > 10]
assert len(MAS10) == 9 and {'Ceuta', 'Melilla'} <= set(MAS10.nom)
MAS10_PROV = len(MAS10) - 2
AND = [c for c, ca in CCAA.items() if ca == 'Andalucía']
P_AND_BEN = d[d.cod.isin(AND)].ben.sum() / d.ben.sum() * 100
P_AND_POB = d[d.cod.isin(AND)].pob.sum() / d.pob.sum() * 100
MB = d[d.cod.isin(['28', '08'])]
P_MB_BEN, P_MB_POB = MB.ben.sum() / d.ben.sum() * 100, MB.pob.sum() / d.pob.sum() * 100
JAEN, GIPU, MEL = D['Jaén'], D['Gipuzkoa'], D['Melilla']
assert d.nom[0] == 'Melilla' and d.nom.iloc[-1] == 'Gipuzkoa' and d.nom[2] == 'Jaén'
UNO_JAEN, UNO_GIPU, UNO_ES = round(100 / JAEN.tasa), round(100 / GIPU.tasa), round(100 / TASA_ES)
assert (UNO_JAEN, UNO_GIPU, UNO_ES) == (8, 40, 18)
VECES = JAEN.tasa / GIPU.tasa

# Renta y paro por provincia (media de los municipios ponderada por población; ADRH 2023 y censo de 2021)
m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str}, usecols=['mun_code', 'renta_uc', 'poblacion', 'paro_2021'])
m = m.dropna(subset=['renta_uc', 'poblacion', 'paro_2021'])
m['cod'] = m.mun_code.str[:2]
g = m.groupby('cod').apply(lambda t: pd.Series({'renta': np.average(t.renta_uc, weights=t.poblacion),
                                                  'paro': np.average(t.paro_2021, weights=t.poblacion)}), include_groups=False)
d = d.merge(g, left_on='cod', right_index=True, how='left')
assert d.renta.notna().all()
R_RENTA = np.corrcoef(d.tasa, d.renta)[0, 1]
R_PARO = np.corrcoef(d.tasa, d.paro)[0, 1]


def parcial(y):
    X = np.c_[np.ones(len(d)), d.renta]
    r1 = d.tasa - X @ np.linalg.lstsq(X, d.tasa, rcond=None)[0]
    r2 = d[y] - X @ np.linalg.lstsq(X, d[y], rcond=None)[0]
    return np.corrcoef(r1, r2)[0, 1]


R = {k: np.corrcoef(d.tasa, d[k])[0, 1] for k, _ in PARTIDOS}
RP = {k: parcial(k) for k, _ in PARTIDOS}

# Cuartos de provincias: 13 provincias cada uno, ordenadas por la tasa de IMV
CUARTOS = []
for q in range(4):
    gq = d.iloc[q * 13:(q + 1) * 13]
    val = sum(E[c]['validos'] for c in gq.cod)
    CUARTOS.append(dict(provs=list(gq.nom), tasa=gq.ben.sum() / gq.pob.sum() * 100,
                        **{k: sum(E[c]['v'].get(k, 0) for c in gq.cod) / val * 100 for k, _ in PARTIDOS}))
Q1, Q4 = CUARTOS[0], CUARTOS[3]
DER1, DER4 = Q1['PP'] + Q1['Vox'], Q4['PP'] + Q4['Vox']
IZQ1, IZQ4 = Q1['PSOE'] + Q1['Sumar'], Q4['PSOE'] + Q4['Sumar']
assert DER1 > DER4 and Q1['PP'] > Q1['PSOE']

# Variación anual por comunidad
cc = d.assign(ca=[CCAA[c] for c in d.cod]).groupby('ca')[['ben', 'beneficiarios_2025_10']].sum()
cc['var'] = (cc.ben / cc.beneficiarios_2025_10 - 1) * 100
cc = cc.sort_values('var', ascending=False)
BAJAN = list(cc[cc['var'] < 0].index)
assert BAJAN == ['País Vasco'], BAJAN

lista = lambda xs: ', '.join(xs[:-1]) + ' y ' + xs[-1]

# --- Gráficos ---
CORTES = [(10, 1.0, 'Más del 10 %'), (8, .78, 'Del 8 % al 10 %'), (6, .56, 'Del 6 % al 8 %'), (4, .36, 'Del 4 % al 6 %'), (0, .18, 'Menos del 4 %')]


def tono(v):
    return next(o for c, o, _ in CORTES if v > c or c == 0)


def mezcla(o):
    return f'color-mix(in srgb, var(--acc) {round(o * 100)}%, var(--bg))'


g_mapa = figura(f'El IMV llega a más del 10 % de la población en {MAS10_PROV} provincias andaluzas y extremeñas y en Ceuta y Melilla',
                'Beneficiarios del ingreso mínimo vital en octubre de 2026 por cada 100 habitantes, por provincia',
                mapa_provincias({r.cod: mezcla(tono(r.tasa)) for r in d.itertuples()},
                                {r.cod: f'{r.nom}: {p(r.tasa)} % ({n(r.ben)} beneficiarios)' for r in d.itertuples()},
                                'Mapa de España por provincias: beneficiarios del ingreso mínimo vital por cada 100 habitantes'),
                f'Fuente: <a href="{SS_XLSX}">Instituto Nacional de la Seguridad Social</a>, nómina de octubre de 2026; '
                f'<a href="{INE}">INE</a>, población a 1 de enero de 2025. Cálculo propio.',
                [(t, mezcla(o)) for _, o, t in CORTES])
FILAS = [(r.nom, r.tasa, mezcla(tono(r.tasa)), p(r.tasa) + ' %') for r in d.itertuples()]
TABLA = (['Provincia', 'Beneficiarios (oct. 2026)', 'Por cada 100 hab.', 'Variación anual (%)', 'PP 2023 (%)', 'PSOE 2023 (%)', 'Vox 2023 (%)'],
         [[r.nom, n(r.ben), p(r.tasa), p((r.ben / r.beneficiarios_2025_10 - 1) * 100), p(r.PP), p(r.PSOE), p(r.Vox)] for r in d.itertuples()])
g_bar = figura(f'En Jaén, {p(JAEN.tasa)} de cada 100 habitantes; en Gipuzkoa, {p(GIPU.tasa)}',
               'Beneficiarios del ingreso mínimo vital por cada 100 habitantes, de más a menos. La línea marca la media de España',
               barras(FILAS, 18, 'Beneficiarios del ingreso mínimo vital por cada 100 habitantes, por provincia', W=360, ml=132, alto=20,
                      linea=(TASA_ES, f'España: {p(TASA_ES)}'), separar=True),
               f'Fuente: <a href="{SS_XLSX}">INSS</a>, nómina de octubre de 2026; <a href="{INE}">INE</a>, población a 1 de enero de 2025.',
               None, TABLA)


def grupos():
    W, ml, alto = 360, 4, 18
    H = 4 * (len(PARTIDOS) * alto + 30)
    x = lambda v: ml + v / 45 * (W - ml - 60)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Voto en 2023 a PP, PSOE, Vox y Sumar en cada cuarto de provincias según el peso del IMV">']
    y = 0
    nombres = ['Las 13 donde más pesa el IMV', 'Las 13 siguientes', 'Las 13 siguientes', 'Las 13 donde menos pesa']
    for q, cu in enumerate(CUARTOS):
        out.append(f'<text x="{ml}" y="{y + 16}" class="lab">{nombres[q]} ({p(cu["tasa"])} por cada 100 hab.)</text>')
        y += 24
        for k, col in PARTIDOS:
            out.append(f'<rect x="{ml}" y="{y}" width="{x(cu[k]) - ml:.1f}" height="{alto - 4}" fill="{col}" rx="2"><title>{k}: {p(cu[k])} %</title></rect>'
                       f'<text x="{x(cu[k]) + 6:.1f}" y="{y + alto - 6}">{k} {p(cu[k])} %</text>')
            y += alto
        y += 6
    out.append('</svg>')
    return ''.join(out).replace(f'viewBox="0 0 {W} {H}"', f'viewBox="0 0 {W} {y}"')


g_voto = figura(f'Donde más pesa el IMV, PP y Vox sumaron el {p(DER1)} % en 2023; donde menos, el {p(DER4)} %',
                'Voto en las generales de julio de 2023 en cada cuarto de las 52 provincias, ordenadas por beneficiarios del IMV por habitante. '
                'Porcentaje sobre votos válidos',
                grupos(), f'Fuente: Ministerio del Interior, resultados de 2023 por provincia; <a href="{SS_XLSX}">INSS</a>; <a href="{INE}">INE</a>. Cálculo propio. Las sumas se calculan con los votos, antes de redondear.',
                [(k, c) for k, c in PARTIDOS],
                (['Grupo', 'IMV por cada 100 hab.', 'PP', 'PSOE', 'Vox', 'Sumar'],
                 [[str(i + 1) + 'º', p(cu['tasa']), p(cu['PP']), p(cu['PSOE']), p(cu['Vox']), p(cu['Sumar'])] for i, cu in enumerate(CUARTOS)]))
g_var = figura(f'El IMV llega a un {p(VAR_ES)} % más de personas que hace un año; en el País Vasco, a menos',
               'Variación de los beneficiarios del ingreso mínimo vital entre octubre de 2025 y octubre de 2026, por comunidad. La línea marca la media de España',
               barras([(ca, max(v, 0), 'var(--acc)' if v >= 0 else 'var(--muted)', ('+' if v >= 0 else '') + p(v) + ' %') for ca, v in cc['var'].items()],
                      30, 'Variación anual de los beneficiarios del ingreso mínimo vital por comunidad', W=360, ml=140, alto=22,
                      linea=(VAR_ES, f'España: +{p(VAR_ES)} %'), separar=True),
               f'Fuente: <a href="{SS_XLSX}">INSS</a>, nóminas de octubre de 2025 y de octubre de 2026. Cálculo propio.',
               None, (['Comunidad', 'Octubre de 2025', 'Octubre de 2026', 'Variación (%)'],
                      [[ca, n(r.beneficiarios_2025_10), n(r.ben), p(r['var'])] for ca, r in cc.iterrows()]))

PV = cc.loc['País Vasco']
cuerpo = f"""
{g_mapa}
<h2>Lo que propone el PP</h2>
<p data-tipo="contexto">Alberto Núñez Feijóo presentó el martes en Madrid el programa del PP para el 29N y anunció que, si gobierna, creará «una renta de activación que reúna el ingreso mínimo vital y los diferentes subsidios en un solo camino hacia el empleo», según <a href="{EP}">Europa Press</a>. La haría con las comunidades autónomas y sería compatible con un trabajo desde el primer día, para que aceptar un empleo siempre mejore la situación de la familia, según Europa Press.</p>
<blockquote class="cita"><p>«Cada beneficiario firmará un acuerdo de formación y búsqueda de empleo, con seguimiento verificable. Rechazar empleos adecuados de forma reiterada y sin causa justificada supondrá la pérdida graduada de las ayudas»</p><footer>Alberto Núñez Feijóo, presidente del PP, en la presentación del programa electoral, según <a href="{EP}">Europa Press</a> (10-11-2026)</footer></blockquote>
<p data-tipo="contexto">Feijóo resumió la idea en una frase: «trabajar tiene que compensar más que no hacerlo». Europa Press señala que la medida no figura en el documento de 249 propuestas que el PP difundió a los medios, y que ese programa deja huecos que el partido prevé ir llenando durante la campaña. Por eso aún no se sabe qué subsidios entrarían ni cuánto cobraría cada hogar.</p>

<h2>A quién llega hoy el ingreso mínimo vital</h2>
<p data-tipo="dato">En octubre, el ingreso mínimo vital llegó a {n(HOG)} hogares en los que viven {n(BEN)} personas, según la <a href="{SS}">Seguridad Social</a>. La cuantía media fue de {p(CUANT)} euros al mes por hogar, y la nómina del mes superó los {p(NOMINA)} millones de euros. Son {n(BEN - d.beneficiarios_2025_10.sum())} beneficiarios más que en octubre de 2025, un {p(VAR_ES)} % más. {n(MEN)} de ellos son menores, el {p(PMEN)} %.</p>
<p data-tipo="dato">No todos cobran lo mismo. La mitad de los beneficiarios, {n(CAPI)}, están en la modalidad que el INSS llama IMV-CAPI, la del complemento de ayuda para la infancia, con una cuantía media de unos 32 euros al mes por persona. Según la <a href="{SS}">Seguridad Social</a>, ese complemento puede cobrarse aparte del IMV porque tiene umbrales de renta más amplios y llega también a hogares con rentas bajas o moderadas.</p>
<p data-tipo="dato">En toda España, el IMV llega a {p(TASA_ES)} de cada 100 habitantes, uno de cada {UNO_ES}. En Jaén, a {p(JAEN.tasa)}, uno de cada {UNO_JAEN}, y en Melilla, a {p(MEL.tasa)}. En Gipuzkoa, a {p(GIPU.tasa)}, uno de cada {UNO_GIPU}: en Jaén pesa {p(VECES)} veces más. Supera el 10 % en {MAS10_PROV} provincias, todas de Andalucía y Extremadura, y en Ceuta y Melilla.</p>
{g_bar}
<p data-tipo="patron">Andalucía tiene el {p(P_AND_POB)} % de la población de España y el {p(P_AND_BEN)} % de los beneficiarios del IMV. Madrid y Barcelona, juntas, tienen el {p(P_MB_POB)} % de la población y el {p(P_MB_BEN)} % de los beneficiarios. Las provincias con menos renta por hogar tienen más beneficiarios por habitante (correlación de {pr(R_RENTA)}), y la relación con el paro del censo de 2021 es aún más estrecha ({pr(R_PARO)}).</p>
{g_var}
<p data-tipo="dato">El número de beneficiarios creció en todas las comunidades menos en el País Vasco, que gestiona el IMV desde 2022: allí bajó un {p(-PV["var"])} % en un año. La variación por comunidad es la de la nómina de cada entidad gestora, no la de los hogares que se mudan de una a otra.</p>

<h2>Cómo votaron las provincias donde más pesa</h2>
<p data-tipo="patron">Si se ordenan las 52 provincias por beneficiarios del IMV por habitante y se reparten en cuatro grupos de 13, en el grupo donde más pesa el IMV el PP sacó el {p(Q1["PP"])} % de los votos en 2023, el PSOE el {p(Q1["PSOE"])} % y Vox el {p(Q1["Vox"])} %. En el grupo donde menos pesa, el PP sacó el {p(Q4["PP"])} %, el PSOE el {p(Q4["PSOE"])} % y Vox el {p(Q4["Vox"])} %. PP y Vox suman {p(DER1)} % en el primero y {p(DER4)} % en el último; PSOE y Sumar, {p(IZQ1)} % y {p(IZQ4)} %. Las sumas se calculan con los votos, antes de redondear. El primer grupo lo forman {lista(Q1['provs'])}; el último, {lista(Q4['provs'])}.</p>
{g_voto}
<p data-tipo="hipotesis">Buena parte de esa diferencia es geografía. En el grupo donde menos pesa el IMV están Barcelona, Bizkaia y Gipuzkoa, donde el PP y Vox son débiles y votan mucho a partidos que no se presentan en el resto de España. Y las provincias con más IMV son también las de menos renta. Si se descuenta la renta de cada provincia, la relación entre el peso del IMV y el voto al PP desaparece (correlación de {pr(RP["PP"])}); con Vox se mantiene, más débil ({pr(RP["Vox"])}, frente a {pr(R["Vox"])} sin descontarla). Son datos de provincias, no de personas: no dicen qué votan quienes cobran el IMV.</p>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">Los beneficiarios incluyen a los menores, que no votan, y se cuentan en la provincia de la entidad gestora. La población es la del 1 de enero de 2025, la última del INE por provincia. El voto es sobre votos válidos en las generales de julio de 2023. La «renta de activación» no tiene aún cuantías ni requisitos publicados, así que esta pieza no puede calcular a quién afectaría. Ver también {L("pobreza-participacion-barrios", "la pobreza y la participación por barrios")} y {L("quien-vota-barrios-renta-edad-inmigracion", "quién vota en los barrios según su renta, su edad y su inmigración")}.</p>
"""

preguntas = [
    ('¿Qué es la «renta de activación» que propone el PP?', f'Una prestación que, según anunció Feijóo el 10 de noviembre, reuniría el ingreso mínimo vital y los subsidios, ligada a un acuerdo de formación y búsqueda de empleo. No figura en el programa de 249 propuestas que el PP difundió, según <a href="{EP}">Europa Press</a>.'),
    ('¿Cuántas personas cobran el ingreso mínimo vital?', f'{n(BEN)} personas en {n(HOG)} hogares en octubre de 2026, según la Seguridad Social; un {p(VAR_ES)} % más que un año antes.'),
    ('¿Dónde llega a más gente el ingreso mínimo vital?', f'En proporción a la población, en Melilla ({p(MEL.tasa)} %), Ceuta ({p(D["Ceuta"].tasa)} %) y Jaén ({p(JAEN.tasa)} %). Donde menos, en Gipuzkoa ({p(GIPU.tasa)} %).'),
]
enlaces = (f'{L("pobreza-participacion-barrios", "Pobreza y participación")} · {L("quien-vota-barrios-renta-edad-inmigracion", "Quién vota en los barrios")} · '
           f'<a href="{BASE}encuestas/">Encuestas del 29N</a>')
foot = ('Datos: Instituto Nacional de la Seguridad Social, IMV por comunidad y provincia, nóminas de octubre de 2025 y 2026; INE, Estadística Continua de '
        'Población a 1 de enero de 2025; Ministerio del Interior, generales de julio de 2023 por provincia. Cálculo: actualidad/src/resumenes/renta_activacion.py.')

DATOS = {'TASA_ES': TASA_ES, 'VAR_ES': VAR_ES, 'CAPI': CAPI, 'HOG': HOG, 'BEN': BEN, 'MEN': MEN, 'PMEN': PMEN, 'CUANT': CUANT, 'NOMINA': NOMINA,
         'MAS10_PROV': MAS10_PROV, 'P_AND_BEN': P_AND_BEN, 'P_AND_POB': P_AND_POB, 'P_MB_BEN': P_MB_BEN, 'P_MB_POB': P_MB_POB,
         'UNO_JAEN': UNO_JAEN, 'UNO_GIPU': UNO_GIPU, 'UNO_ES': UNO_ES, 'VECES': VECES, 'R_RENTA': R_RENTA, 'R_PARO': R_PARO, 'R': R, 'RP': RP,
         'NUEVOS': int(BEN - d.beneficiarios_2025_10.sum()), 'DER1': DER1, 'DER4': DER4, 'IZQ1': IZQ1, 'IZQ4': IZQ4, 'PV_VAR': float(PV['var']),
         'Q': [{k: v for k, v in cu.items() if k != 'provs'} for cu in CUARTOS],
         'PROV': {r.nom: {'tasa': r.tasa, 'ben': int(r.ben), 'PP': r.PP, 'PSOE': r.PSOE, 'Vox': r.Vox} for r in d.itertuples()},
         'CCAA': {ca: float(v) for ca, v in cc['var'].items()}}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

H1 = (f'El ingreso mínimo vital que Feijóo quiere convertir en «renta de activación» llega a uno de cada {UNO_JAEN} habitantes de Jaén '
      f'y a uno de cada {UNO_GIPU} de Gipuzkoa')
DEK = (f'En octubre lo cobraban {n(BEN)} personas, un {p(VAR_ES)} % más que hace un año. Andalucía reúne el {p(P_AND_BEN)} % de los beneficiarios '
       f'con el {p(P_AND_POB)} % de la población. En las provincias donde más pesa, PP y Vox sumaron el {p(DER1)} % de los votos en 2023; '
       f'donde menos, el {p(DER4)} %.')
pieza('renta-activacion-ingreso-minimo-vital-29n', 'La renta de activación y el IMV', H1, DEK, '11 de noviembre de 2026',
      cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('tasa', p(TASA_ES), 'var', p(VAR_ES), 'and', p(P_AND_BEN), p(P_AND_POB), 'Q1', {k: p(v) for k, v in Q1.items() if k != 'provs'},
      'Q4', {k: p(v) for k, v in Q4.items() if k != 'provs'}, 'r', pr(R_RENTA), pr(R_PARO), {k: p(v) for k, v in RP.items()}, 'PV', p(PV['var']))
