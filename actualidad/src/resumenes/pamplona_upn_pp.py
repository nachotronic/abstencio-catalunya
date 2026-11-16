"""«Feijóo en Pamplona con UPN» (16-11-2026): el mitin conjunto de UPN-PP en Pamplona, la tarde del cuarto día de campaña.

Las 151 secciones censales de Pamplona en las generales de julio de 2023, cuando UPN y PP fueron por separado: ganador de
cada sección con los votos de cada lista y con los de UPN y PP sumados (cálculo, no resultado). Noviembre de 2019, con
Navarra Suma (UPN, PP y Ciudadanos; en las descargas, columna PP), con las 137 secciones de entonces. Renta por sección:
Atlas de Distribución de Renta de los Hogares del INE (2023). Reparto central del modelo de /encuestas/navarra/.
Datos: generales-2026/descargas/resultados_secciones_largo.csv (Interior por mesa, vía pollspaindata, sin voto exterior).
Contexto: EFE (agenda del 16-11), OKDiario Navarra (hora y lugar del mitin), Ayuntamiento de Pamplona (moción de censura, 28-12-2023).
Uso, desde la raíz: python3 actualidad/src/resumenes/pamplona_upn_pp.py
"""
import json
import math

import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import COL, NOM, Y19, Y23, _c, p, reparto_central

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
NW = {0: 'ninguna', 1: 'una', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'feijoo-pamplona-upn-pp-secciones-29n'
EFE = 'https://www.infobae.com/espana/agencias/2026/11/16/cuarto-dia-de-campana-sanchez-con-lula-feijoo-en-lleida-y-navarra-y-abascal-en-tenerife/'
OKN = 'https://navarra.okdiario.com/navarra/politica/upn-pp-llama-movilizarse-pamplona-visita-feijoo-senala-pactos-psoe-bildu/20261116070010667727.html'
AYTO = 'https://www.pamplona.es/node/63977'
MUN = '31201'
COLC = dict(COL, UPN='#0f4c8a', NAS='#3d6fb6', SUM='#2a5d9f', UP=COL['SUMAR'])
NOMC = dict(NOM, UPN='UPN', NAS='Navarra Suma', SUM='UPN y PP sumados', SUMAR='Sumar', UP='Unidas Podemos', BILDU='EH Bildu')

# --- Datos por sección ---
r = pd.read_csv(RAIZ / 'generales-2026/descargas/resultados_secciones_largo.csv', dtype={'tract_code': str, 'mun_code': str})
r = r[(r.mun_code == MUN) & r.eleccion.isin([Y19, Y23])].fillna(0).copy()
L19 = ['PP', 'PSOE', 'BILDU', 'SUMAR', 'VOX']            # 2019: PP es Navarra Suma; SUMAR, Unidas Podemos
L23 = ['PP', 'UPN', 'PSOE', 'BILDU', 'SUMAR', 'VOX']
R19, R23 = r[r.eleccion == Y19].copy(), r[r.eleccion == Y23].copy()
assert (len(R19), len(R23)) == (137, 151)
assert R19.UPN.sum() == 0 and R19.CS.sum() == 0 and R23.CS.sum() == 0


def gana(df, cols):
    v = df[cols]
    top = v.max(axis=1)
    assert (df.OTROS < top).all()            # Geroa Bai y los demás van en OTROS: en ninguna sección llegan al primero
    dos = v.apply(lambda x: sorted(x)[-2], axis=1)
    assert (dos < top).all()                 # sin empates
    return v.idxmax(axis=1), (top - dos).astype(int)


R19['g'], R19['m'] = gana(R19, L19)
R19['g'] = R19.g.replace({'PP': 'NAS', 'SUMAR': 'UP'})
R23['g'], R23['m'] = gana(R23, L23)
R23['SUM'] = R23.PP + R23.UPN
R23['gs'], R23['ms'] = gana(R23, ['SUM', 'PSOE', 'BILDU', 'SUMAR', 'VOX'])
G19, G23, GS = R19.g.value_counts().to_dict(), R23.g.value_counts().to_dict(), R23.gs.value_counts().to_dict()
assert G19 == {'NAS': 74, 'PSOE': 39, 'BILDU': 21, 'UP': 3}, G19
assert G23 == {'PSOE': 77, 'UPN': 28, 'BILDU': 24, 'PP': 22}, G23
assert GS == {'SUM': 80, 'PSOE': 49, 'BILDU': 22}, GS
TR = pd.crosstab(R23.g, R23.gs)
DE_PSOE, DE_BILDU = int(TR.at['PSOE', 'SUM']), int(TR.at['BILDU', 'SUM'])
assert (DE_PSOE, DE_BILDU) == (28, 2) and G23['PP'] + G23['UPN'] + DE_PSOE + DE_BILDU == GS['SUM']
SEP = G23['PP'] + G23['UPN']

# Totales de la ciudad
T = {y: {c: int(d[c].sum()) for c in ['PP', 'UPN', 'PSOE', 'BILDU', 'SUMAR', 'VOX', 'candidaturas', 'censo', 'votantes']} for y, d in ((Y19, R19), (Y23, R23))}
pc = lambda y, c: T[y][c] / T[y]['candidaturas'] * 100
assert T[Y19]['PP'] == 34638 and T[Y23]['PP'] + T[Y23]['UPN'] == 36746 and T[Y23]['PSOE'] == 26296
SUMV = T[Y23]['PP'] + T[Y23]['UPN']
assert SUMV - T[Y23]['PSOE'] == 10450 and SUMV > T[Y19]['PP']
# Las 28 secciones del PSOE que pasarían a UPN y PP sumados: por cuánto
PAS = R23[(R23.g == 'PSOE') & (R23.gs == 'SUM')]
MARG_PAS = int((PAS.SUM - PAS.PSOE).median())

# Renta (ADRH 2023): cinco grupos de secciones con el mismo número de secciones, de menos a más renta por unidad de consumo
SEC = pd.read_csv(RAIZ / 'generales-2026/descargas/secciones.csv', dtype={'tract_code': str, 'mun_code': str}, usecols=['tract_code', 'mun_code', 'renta_uc'])
SEC = SEC[SEC.mun_code == MUN].set_index('tract_code')
R23['renta'] = R23.tract_code.map(SEC.renta_uc)
assert R23.renta.notna().all()
R23['q'] = pd.qcut(R23.renta.rank(method='first'), 5, labels=False)
Q = []
for q, d in R23.groupby('q'):
    v = d.candidaturas.sum()
    Q.append(dict(q=int(q), n=len(d), rmin=int(d.renta.min()), rmax=int(d.renta.max()), sum=float(d.SUM.sum() / v * 100),
                  psoe=float(d.PSOE.sum() / v * 100), bildu=float(d.BILDU.sum() / v * 100), gs=int((d.gs == 'SUM').sum())))
assert [x['n'] for x in Q] == [31, 30, 30, 30, 30] or sum(x['n'] for x in Q) == 151
assert all(Q[i]['sum'] < Q[i + 1]['sum'] for i in range(4)) and all(Q[i]['psoe'] > Q[i + 1]['psoe'] for i in range(4)), Q
assert min(Q[i]['bildu'] for i in range(3)) > 20 and Q[3]['bildu'] < 15 and Q[4]['bildu'] < 10, Q
R23['psum'] = R23.SUM / R23.candidaturas * 100
CORR = float(R23[['renta', 'psum']].corr().iat[0, 1])
assert CORR > .7, CORR

# Modelo de /encuestas/navarra/
RC = reparto_central('navarra')
RC = {('UPNPP' if k in ('UPN-PP', 'UPNPP') else 'BILDU' if k == 'EH Bildu' else k): v for k, v in RC.items()}
assert RC['UPNPP'] == (1, 1, 2) and RC['PSOE'] == (2, 1, 2) and RC['BILDU'] == (1, 1, 2) and RC['VOX'] == (1, 0, 1) and len(RC) == 4, RC
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
_a, _m, _d, _hm = HIST.stem.split('-')
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de noviembre de {_a}'


# --- Mapas por sección ---
def caminos_sec(W_=640, umbral=.8):
    g = json.load(open(RAIZ / 'generales-2026/data/sec/31.json'))
    S, kx = g['S'], math.cos(math.radians(42.8))
    AN = []
    for cod, partes in zip(g['cod'], g['poly']):
        if not cod.startswith(MUN):
            continue
        for f in partes:
            x, y, pts = f[0], f[1], [(f[0], f[1])]
            for k in range(2, len(f), 2):
                x += f[k]; y += f[k + 1]; pts.append((x, y))
            AN.append((cod, [(px / S * kx, -py / S) for px, py in pts]))
    XS = [x for _, q in AN for x, _ in q]; YS = [y for _, q in AN for _, y in q]
    s = W_ / (max(XS) - min(XS)); H = round((max(YS) - min(YS)) * s)
    cam = {}
    for cod, q in AN:
        d, ult = '', None
        for i, (x, y) in enumerate(q):
            t = (round((x - min(XS)) * s * 10), round((y - min(YS)) * s * 10))
            if ult and i < len(q) - 1 and abs(t[0] - ult[0]) + abs(t[1] - ult[1]) < umbral * 10:
                continue
            if ult is None:
                d = f'M{t[0] / 10:g},{t[1] / 10:g}l'
            else:
                dx, dy = _c((t[0] - ult[0]) / 10), _c((t[1] - ult[1]) / 10)
                d += (dx if dx[0] == '-' or d.endswith('l') else ' ' + dx) + (dy if dy[0] == '-' else ' ' + dy)
            ult = t
        cam[cod] = cam.get(cod, '') + d + 'z'
    return cam, H


CAM, HM = caminos_sec()
assert len(CAM) == 151 and set(CAM) == set(R23.tract_code)
RI = R23.set_index('tract_code')


def mapa(col_g, col_m, rot):
    def tit(k):
        x = RI.loc[k]
        return f'Sección {k[5:7]}-{k[7:]}: {NOMC[x[col_g]]}, {n(int(x[col_m]))} votos por delante'
    out = ''.join(f'<path d="{d}" fill="{COLC[RI.at[k, col_g]]}"><title>{esc(tit(k))}</title></path>' for k, d in CAM.items())
    return (f'<p style="margin:.8em 0 .2em;font-weight:700;font-size:.95em">{esc(rot)}</p>'
            f'<svg viewBox="0 0 640 {HM}" role="img" aria-label="{esc(f"Secciones censales de Pamplona por partido más votado: {rot}")}" '
            f'style="max-width:640px;margin:0 auto;display:block"><g stroke="var(--bg)" stroke-width=".7" stroke-linejoin="round">{out}</g></svg>')


ORD = ['PSOE', 'UPN', 'PP', 'SUM', 'BILDU']
g_mapa = figura(f'Por separado, UPN y PP ganaron {SEP} de las 151 secciones de Pamplona en 2023; sumados, habrían sido {GS["SUM"]}',
                'Partido más votado en cada sección censal de Pamplona en las generales de julio de 2023: arriba, con los votos de cada lista; abajo, con los de UPN y PP sumados',
                mapa('g', 'm', 'Julio de 2023, cada lista por su cuenta') + mapa('gs', 'ms', 'Julio de 2023, con UPN y PP sumados (cálculo)'),
                'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por sección censal, sin voto exterior. Sumar los votos de dos listas es una cuenta, no un resultado. Cálculo propio.',
                [(NOMC[f], COLC[f]) for f in ORD],
                (['Ganador por separado → con UPN y PP sumados', 'Secciones'],
                 [[f'{NOMC[a]} → {NOMC[b]}', str(int(TR.at[a, b]))] for a in TR.index for b in TR.columns if TR.at[a, b]]))

g_renta = figura('Cuanta más renta tiene la sección, más votaron UPN y PP',
                 'Voto en las generales de julio de 2023 (%) en las 151 secciones de Pamplona, en cinco grupos de unas 30 secciones ordenados por renta por unidad de consumo',
                 ''.join(f'<p style="margin:.8em 0 .2em;font-weight:700;font-size:.92em">{esc(t)}</p>' + barras(
                     [(f'{n(x["rmin"])}–{n(x["rmax"])} €', x[k], c, p(x[k]) + ' %') for x in Q], 60, f'{t} por grupo de renta', W=400, ml=118, fmt=p)
                     for t, k, c in (('UPN y PP sumados', 'sum', COLC['SUM']), ('PSOE', 'psoe', COLC['PSOE']), ('EH Bildu', 'bildu', COLC['BILDU']))),
                 'Fuente: Ministerio del Interior (resultados por mesa, vía pollspaindata) y Atlas de Distribución de Renta de los Hogares del INE (2023). Cálculo propio.',
                 [('UPN y PP sumados', COLC['SUM']), ('PSOE', COLC['PSOE']), ('EH Bildu', COLC['BILDU'])],
                 (['Renta por unidad de consumo', 'Secciones', 'UPN + PP', 'PSOE', 'EH Bildu', 'Secciones de UPN + PP'],
                  [[f'{n(x["rmin"])}–{n(x["rmax"])} €', str(x['n']), p(x['sum']), p(x['psoe']), p(x['bildu']), str(x['gs'])] for x in Q]))

V = [('Navarra Suma 2019', pc(Y19, 'PP'), COLC['NAS']), ('UPN + PP 2023', SUMV / T[Y23]['candidaturas'] * 100, COLC['SUM']),
     ('PSOE 2019', pc(Y19, 'PSOE'), COLC['PSOE']), ('PSOE 2023', pc(Y23, 'PSOE'), COLC['PSOE']),
     ('EH Bildu 2019', pc(Y19, 'BILDU'), COLC['BILDU']), ('EH Bildu 2023', pc(Y23, 'BILDU'), COLC['BILDU'])]
g_ciudad = figura('En Pamplona, UPN y PP sumaron en 2023 más votos que Navarra Suma en 2019',
                  'Voto en Pamplona en las generales de noviembre de 2019 y julio de 2023, en % de los votos a candidaturas',
                  barras([(t, v, c, p(v) + ' %') for t, v, c in V], 45, 'Voto en Pamplona en 2019 y 2023', W=400, ml=130, fmt=p),
                  'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por sección, sin voto exterior. Navarra Suma: UPN, PP y Ciudadanos.',
                  [('Navarra Suma / UPN + PP', COLC['SUM']), ('PSOE', COLC['PSOE']), ('EH Bildu', COLC['BILDU'])],
                  (['Lista', 'Votos', '%'], [[t, n(T[Y19]['PP'] if t.startswith('Navarra') else SUMV if t.startswith('UPN') else T[Y19 if '2019' in t else Y23]['PSOE' if 'PSOE' in t else 'BILDU']), p(v)] for t, v, c in V]))

# --- Texto ---
cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Alberto Núñez Feijóo pasa el cuarto día de campaña entre Lleida, donde visita a mediodía una explotación agrícola y ganadera, y Pamplona, donde por la tarde protagoniza un mitin conjunto del PP y UPN con la presidenta de UPN, Cristina Ibarrola, según la agencia <a href="{EFE}">EFE</a>. El mitin empieza a las siete de la tarde en el hotel NH Iruña Park, con los dos primeros candidatos de la coalición al Congreso por Navarra, Leticia San Martín y Sergio Sayas, según <a href="{OKN}">OKDiario Navarra</a>. El 29N, UPN y PP vuelven a presentarse juntos, como en noviembre de 2019 con Navarra Suma.</p>
<p data-tipo="dato">La ciudad que los recibe ilustra lo que se juegan con esa suma. En las generales de julio de 2023, con cada partido por su cuenta, el PSOE fue el más votado en <strong>{G23["PSOE"]}</strong> de las 151 secciones censales de Pamplona; UPN, en {G23["UPN"]}; EH Bildu, en {G23["BILDU"]}, y el PP, en {G23["PP"]}. Con los votos de UPN y PP sumados, la lista conjunta habría quedado primera en <strong>{GS["SUM"]}</strong>: las {SEP} que ya ganaban por separado, {DE_PSOE} del PSOE y {NW[DE_BILDU]} de EH Bildu.</p>
{g_mapa}
<p data-tipo="dato">En toda la ciudad, UPN y PP sacaron juntos {n(SUMV)} votos, el {p(SUMV / T[Y23]['candidaturas'] * 100)} %, {n(SUMV - T[Y23]['PSOE'])} más que el PSOE, que ganó con el {p(pc(Y23, 'PSOE'))} %. Son más que los {n(T[Y19]['PP'])} de Navarra Suma en 2019, que también llevaba a Ciudadanos y ganó entonces {G19["NAS"]} de las 137 secciones que tenía Pamplona.</p>
{g_ciudad}
<p data-tipo="hipotesis">Sumar los votos de dos listas es una cuenta, no un resultado: no todos los votantes de UPN habrían votado una papeleta con el PP, ni al revés, y una lista conjunta también moviliza o aleja a otros. Las secciones que cambiarían de color son, sobre todo, las que el PSOE ganó por poco: en esas {DE_PSOE}, UPN y PP sumados le sacaban una mediana de {n(MARG_PAS)} votos.</p>
<h2>La renta dibuja el mapa</h2>
<p data-tipo="dato">El voto a UPN y PP sube con la renta de cada sección. En la quinta parte de las secciones con menos renta por unidad de consumo, de {n(Q[0]["rmin"])} a {n(Q[0]["rmax"])} euros, sumaron el {p(Q[0]["sum"])} %; en la quinta parte con más, por encima de {n(Q[4]["rmin"])} euros, el <strong>{p(Q[4]["sum"])} %</strong>. El PSOE hace el camino inverso: baja del {p(Q[0]["psoe"])} % al {p(Q[4]["psoe"])} %. EH Bildu pasa del 20 % en las tres quintas partes con menos renta y cae al {p(Q[4]["bildu"])} % en la de más.</p>
{g_renta}
<p data-tipo="hipotesis">Es una relación entre secciones, no entre personas: no dice que cada vecino con más renta vote a la derecha, sino que en las secciones con más renta UPN y PP sacan más voto.</p>
<h2>Pamplona, desde la moción de censura</h2>
<p data-tipo="contexto">El Ayuntamiento lo gobierna EH Bildu desde el 28 de diciembre de 2023. Ese día, una moción de censura de EH Bildu, el grupo socialista, Geroa Bai y el Grupo Mixto, con 15 votos a favor y 11 en contra de UPN y PP, hizo alcalde a Joseba Asiron y apartó a Ibarrola, alcaldesa desde el 17 de junio de 2023, según el <a href="{AYTO}">Ayuntamiento de Pamplona</a>. Es una decisión que UPN y PP, escribe <a href="{OKN}">OKDiario Navarra</a>, «han convertido en uno de sus principales argumentos durante la campaña electoral».</p>
<p data-tipo="dato">Para el 29N, el modelo de <a href="{BASE}encuestas/navarra/">nuestras encuestas</a>, con los datos {VERSION}, da en Navarra dos escaños al PSOE y uno a UPN-PP, otro a EH Bildu y otro a Vox en el reparto central. UPN-PP saca entre uno y dos: en 2023, UPN y PP sacaron por separado un diputado cada uno. El mapa de toda la comunidad, municipio a municipio, está en {L("mapa-electoral-navarra-29n", "El mapa electoral de Navarra")}.</p>
'''

preguntas = [
    ('¿Quién ganó en Pamplona en las generales de 2023?',
     f'El PSOE, con el {p(pc(Y23, "PSOE"))} % de los votos a candidaturas, y fue el más votado en {G23["PSOE"]} de las 151 secciones censales. UPN ganó en {G23["UPN"]}, EH Bildu en {G23["BILDU"]} y el PP en {G23["PP"]}.'),
    ('¿Habrían ganado UPN y PP juntos en Pamplona en 2023?',
     f'Con sus votos sumados, {n(SUMV)}, habrían superado al PSOE por {n(SUMV - T[Y23]["PSOE"])} y habrían quedado primeros en {GS["SUM"]} de las 151 secciones. Es una cuenta: no todos sus votantes habrían votado una lista conjunta.'),
    ('¿Dónde es el mitin de Feijóo en Pamplona?',
     'En el hotel NH Iruña Park, a las siete de la tarde del 16 de noviembre de 2026, con Cristina Ibarrola, Leticia San Martín y Sergio Sayas, según OKDiario Navarra.'),
]
enlaces = (f'{L("mapa-electoral-navarra-29n", "El mapa electoral de Navarra")} · {L("participacion-navarra-municipios-29n", "La participación en Navarra")} · '
           f'<a href="{BASE}encuestas/navarra/">Encuestas de Navarra</a>')
foot = ('Datos: Ministerio del Interior, resultados de las generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata), sumados por sección censal, '
        'sin voto exterior; Atlas de Distribución de Renta de los Hogares del INE (2023); modelo de mapaelectoral.es/encuestas. Cálculo: actualidad/src/resumenes/pamplona_upn_pp.py.')

DATOS = {'G19': G19, 'G23': G23, 'GS': GS, 'SEP': SEP, 'DE_PSOE': DE_PSOE, 'DE_BILDU': DE_BILDU, 'T': T, 'SUMV': SUMV, 'MARG_PAS': MARG_PAS,
         'Q': Q, 'CORR': CORR, 'RC': {k: list(v) for k, v in RC.items()}, 'PSUM23': SUMV / T[Y23]['candidaturas'] * 100}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'Feijóo en Pamplona',
      f'Feijóo hace campaña con UPN en Pamplona, donde el PSOE ganó {G23["PSOE"]} de las 151 secciones en 2023; con UPN y PP sumados, habría ganado {GS["PSOE"]}',
      f'Por separado, UPN y PP fueron los más votados en {SEP} secciones de la ciudad; juntos, habrían quedado primeros en {GS["SUM"]}. '
      f'Su voto sube con la renta: del {p(Q[0]["sum"])} % en las secciones con menos renta al {p(Q[4]["sum"])} % en las que más tienen.',
      '16 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('G', G19, G23, GS, 'PAS', DE_PSOE, DE_BILDU, MARG_PAS, 'Q', [(x['rmin'], x['rmax'], round(x['sum'], 1), round(x['psoe'], 1), round(x['bildu'], 1), x['gs']) for x in Q], 'CORR', round(CORR, 2), RC, VERSION)
