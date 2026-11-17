"""«Feijóo en Gipuzkoa» (17-11-2026): Feijóo arropa al candidato del PP por Gipuzkoa, atacado en Hernani el 14-11.

El PP en Gipuzkoa en las generales de 2004 a 2023 (Interior por mesa, vía pollspaindata, sin voto exterior): voto y
diputados (D'Hondt con barrera del 3 % sobre los votos válidos; desde 2011, OTROS es menos del 2,5 % y no reparte).
Votos que le faltaron en 2023 para el sexto escaño, con voto exterior (actualidad/src/sistema/simulador.json, iguales
a los oficiales). Mapa municipal del voto al PP en 2023. Hernani por secciones. Modelo de /encuestas/gipuzkoa/.
Contexto: EFE (agenda del 17-11), COPE (la agresión y las declaraciones).
Uso, desde la raíz: python3 actualidad/src/resumenes/gipuzkoa_pp_hernani.py
"""
import json
from collections import Counter

import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import COL, Y23, caminos, mapa_svg, trazados, p, reparto_central

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
SLUG = 'feijoo-gipuzkoa-hernani-pp-29n'
EFE = 'https://www.infobae.com/espana/agencias/2026/11/17/quinto-dia-de-campana-de-la-crisis-migratoria-en-canarias-al-podcast-irreverente-y-lgtbi/'
COPE = ('https://www.cope.es/programas/la-tarde/noticias/jon-echeverria-candidato-pp-pais-vasco-centenar-violentos-abalanzo-sobre-petardos-huevos-'
        'piedras-defender-pp-implica-correr-riesgo-20261116_3476190.html')
HER = '20040'
NOMS = {'PP': 'PP', 'PSOE': 'PSOE', 'PNV': 'PNV', 'BILDU': 'EH Bildu', 'SUMAR': 'Sumar', 'VOX': 'Vox', 'CS': 'Ciudadanos'}
ANYO = {'2004_03': '2004', '2008_03': '2008', '2011_11': '2011', '2015_12': '2015', '2016_06': '2016', '2019_04': 'abr. 2019',
        '2019_11': 'nov. 2019', '2023_07': '2023'}

# --- Gipuzkoa, 2004-2023, por mesa ---
s = pd.read_csv(RAIZ / 'generales-2026/descargas/resultados_secciones_largo.csv', dtype={'tract_code': str, 'mun_code': str})
g = s[s.tract_code.str[:2] == '20'].fillna(0)
LIS = [c for c in s.columns if c not in ('tract_code', 'censo', 'blancos', 'nulos', 'candidaturas', 'votantes', 'eleccion', 'mun_code', 'OTROS')]
HIST = []
for y, d in g.groupby('eleccion'):
    v = d[LIS].sum(); v = v[v > 0]
    validos, cand = d.candidaturas.sum() + d.blancos.sum(), d.candidaturas.sum()
    fila = dict(y=y, pp=float(d.PP.sum() / cand * 100), ppv=int(d.PP.sum()), otros=float(d.OTROS.sum() / cand * 100))
    if y >= '2011':
        assert fila['otros'] < 2.5, fila     # lo que va en OTROS no llega al 3 %: el reparto con las listas con columna propia vale
        q = sorted(((x / i, k) for k, x in v.items() if x >= .03 * validos for i in range(1, 7)), reverse=True)
        fila['esc'] = dict(Counter(k for _, k in q[:6]))
        fila['pp_esc'] = fila['esc'].get('PP', 0)
    HIST.append(fila)
H = {f['y']: f for f in HIST}
assert len([f for f in HIST if f['y'] > '2011_11']) == 5 and [H[y]['pp_esc'] for y in ('2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07')] == [1, 0, 0, 0, 0, 0]
assert H['2011_11']['esc'] == {'BILDU': 3, 'PNV': 1, 'PSOE': 1, 'PP': 1}
assert H['2023_07']['esc'] == {'BILDU': 2, 'PSOE': 2, 'PNV': 2}
MAXPP = max(HIST, key=lambda f: f['pp'])
assert MAXPP['y'] == '2004_03'
MINPP = min(HIST, key=lambda f: f['pp'])
assert MINPP['y'] == '2019_04'

# --- 2023 con voto exterior: el último escaño ---
SIM = json.load(open(RAIZ / 'actualidad/src/sistema/simulador.json'))
X = SIM['elecciones'][Y23]['20']
assert SIM['escanos'][Y23]['20'] == 6
VS = {k: c for k, c in X['v'].items() if k != 'Otros' and c >= .03 * X['validos']}
QS = sorted(((c / i, k) for k, c in VS.items() for i in range(1, 7)), reverse=True)
ESC23 = dict(Counter(k for _, k in QS[:6]))
assert ESC23 == {'EH Bildu': 2, 'PSOE': 2, 'PNV': 2}, ESC23
ULT = QS[5]
assert ULT[1] == 'PNV'
ULTQ = ULT[0]
PP23 = X['v']['PP']
FALTA = int(ULTQ - PP23) + 1        # votos más que necesitaba el PP para pasar el cociente del sexto escaño
SUMAR23 = X['v']['Sumar']
assert SUMAR23 > PP23 and int(ULTQ - SUMAR23) + 1 < FALTA
PP23_PCT = PP23 / sum(X['v'].values()) * 100

# --- Municipios, 2023 ---
d23 = g[g.eleccion == Y23]
MU = d23.groupby('mun_code')[['PP', 'PSOE', 'BILDU', 'PNV', 'SUMAR', 'VOX', 'candidaturas']].sum()
MU['pp'] = MU.PP / MU.candidaturas * 100
NOMB = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str}, usecols=['mun_code', 'municipio']).set_index('mun_code').municipio.to_dict()
assert len(MU) == 88
CERO = int((MU.PP == 0).sum())
assert CERO == 7
PPT = int(MU.PP.sum())
DSS, IRUN = '20069', '20045'
SS_PCT, SS_V = float(MU.at[DSS, 'pp']), int(MU.at[DSS, 'PP'])
PESO_SS = SS_V / PPT * 100
PESO_SS_IRUN = (SS_V + int(MU.at[IRUN, 'PP'])) / PPT * 100
assert 45 < PESO_SS < 50 and 60 < PESO_SS_IRUN < 62, (PESO_SS, PESO_SS_IRUN)
assert MU.pp.idxmax() == DSS
GR = MU[MU.candidaturas >= 3000]
N_GR = len(GR)
SOBRE10 = sorted(GR[GR.pp >= 10].index, key=lambda k: -MU.at[k, 'pp'])
assert SOBRE10 == [DSS, IRUN, '20902'], SOBRE10
# Hernani
HV, HC = int(MU.at[HER, 'PP']), int(MU.at[HER, 'candidaturas'])
H_PCT, HB_PCT = HV / HC * 100, MU.at[HER, 'BILDU'] / HC * 100
assert (HV, round(H_PCT, 1)) == (486, 4.7)
HS = d23[d23.mun_code == HER].copy()
HS['pp'] = HS.PP / HS.candidaturas * 100
HS['bi'] = HS.BILDU / HS.candidaturas * 100
assert len(HS) == 16 and int((HS.PP == 0).sum()) == 1
H0 = HS[HS.PP == 0].iloc[0]
H0_BI, H0_C = float(H0.bi), int(H0.candidaturas)
HMAX = float(HS.pp.max())
H_HIST = {y: (int(dd.PP.sum()), float(dd.PP.sum() / dd.candidaturas.sum() * 100)) for y, dd in g[g.mun_code == HER].groupby('eleccion')}
assert H_HIST['2011_11'][0] == 942 and H_HIST['2019_04'][0] == 314

# --- Modelo ---
RC = reparto_central('gipuzkoa')
RC = {('BILDU' if k == 'EH Bildu' else k): v for k, v in RC.items()}
assert RC['PP'] == (0, 0, 1) and RC['BILDU'] == (3, 2, 4) and RC['PSOE'] == (2, 1, 2) and RC['PNV'] == (1, 1, 2), RC
HJ = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
MOD = json.load(open(HJ))
PPM = [x for x in MOD['escenario']['provincias']['20']['listas'] if x['lista'] == 'PP'][0]
assert PPM['escanos'] == [0, 0, 1]
PPM_V = PPM['voto']
_a, _m, _d, _hm = HJ.stem.split('-')
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de noviembre de {_a}'
RB = reparto_central('bizkaia')
assert RB['PP'] == (1, 1, 1), RB
RR = reparto_central('la-rioja')
assert RR['PP'] == (2, 2, 3), RR

# --- Gráficos ---
g_hist = figura(f'El PP sacó su último diputado por Gipuzkoa en 2011, con el {p(H["2011_11"]["pp"])} % de los votos',
                'Voto al PP en Gipuzkoa en las elecciones generales, en % de los votos a candidaturas, y diputados del PP (de seis) desde 2011',
                barras([(ANYO[f['y']], f['pp'], COL['PP'], p(f['pp']) + ' %' + (f' · {f["pp_esc"]} dip.' if 'pp_esc' in f else ''))
                        for f in HIST], 20, 'Voto al PP en Gipuzkoa por elección', W=400, ml=80, fmt=p),
                'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata), sin voto exterior. Diputados: D\'Hondt con barrera del 3 %, cálculo propio, desde 2011. Cálculo propio.',
                [('PP', COL['PP'])],
                (['Elección', 'Votos del PP', '% del PP', 'Diputados del PP'],
                 [[ANYO[f['y']], n(f['ppv']), p(f['pp']), str(f['pp_esc']) if 'pp_esc' in f else 'Sin calcular'] for f in HIST]))

FILAS_U = [('Sumar', SUMAR23, COL['SUMAR']), ('PP', PP23, COL['PP']), ('Vox', X['v']['Vox'], COL['VOX'])]
g_ult = figura(f'Al PP le faltaron {n(FALTA)} votos para el sexto diputado de Gipuzkoa en 2023',
               f'Votos de las listas que se quedaron sin escaño en Gipuzkoa en julio de 2023 y cifra que había que superar para el sexto: la del segundo escaño del PNV ({n(int(ULTQ))} votos, la mitad de los suyos)',
               barras([(t, v, c, n(v)) for t, v, c in FILAS_U], 50000, 'Votos de Sumar, PP y Vox frente a la cifra del sexto escaño', W=400, ml=60,
                      linea=(ULTQ, 'Sexto escaño'), separar=True),
               'Fuente: Ministerio del Interior, resultados definitivos con voto exterior (vía pollspaindata). Reparto con D\'Hondt, igual que el oficial: EH Bildu 2, PSOE 2 y PNV 2. Cálculo propio.',
               [('Sumar', COL['SUMAR']), ('PP', COL['PP']), ('Vox', COL['VOX'])],
               (['Lista', 'Votos', 'Le faltaban para el sexto escaño'], [[t, n(v), n(int(ULTQ - v) + 1)] for t, v, _ in FILAS_U]))

TRAMOS = [(0, 0, '#cfcfcf', 'Ningún voto'), (0, 3, '#dbe8f5', 'Menos del 3 %'), (3, 6, '#a9c9e9', 'Del 3 al 6 %'),
          (6, 9, '#6fa3d8', 'Del 6 al 9 %'), (9, 12, '#3478bd', 'Del 9 al 12 %'), (12, 100, '#174d86', '12 % o más')]


def tono(k):
    v, c = MU.at[k, 'PP'], MU.at[k, 'pp']
    if v == 0:
        return TRAMOS[0][2]
    return [t[2] for t in TRAMOS[1:] if t[0] <= c < t[1]][0]


CAM, HMAP = caminos(['20'], W=640, lat=43.1, umbral=.9)
assert set(CAM) == set(MU.index), set(MU.index) ^ set(CAM)
cuenta = Counter(tono(k) for k in MU.index)
g_mapa = figura(f'El voto al PP en Gipuzkoa: del {p(SS_PCT)} % de San Sebastián a ningún voto en {CERO} municipios',
                'Voto al PP en cada municipio de Gipuzkoa en las generales de julio de 2023, en % de los votos a candidaturas',
                trazados(CAM) + mapa_svg(CAM, HMAP, tono, lambda k: f'PP {p(MU.at[k, "pp"])} % ({n(int(MU.at[k, "PP"]))} votos)',
                                         'Mapa de los municipios de Gipuzkoa por voto al PP en 2023', NOMB),
                'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata), sin voto exterior. Cálculo propio.',
                [(t[3], t[2]) for t in TRAMOS],
                (['Municipio', 'Votos a candidaturas', 'Votos del PP', '% del PP'],
                 [[NOMB[k], n(int(r.candidaturas)), n(int(r.PP)), p(r.pp)] for k, r in MU.sort_values('pp', ascending=False).iterrows()]))

# --- Texto ---
cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Alberto Núñez Feijóo empieza el quinto día de campaña en Gipuzkoa para apoyar a su candidato «tras ser agredido» en Hernani, y sigue después con mítines en Bilbao y en Logroño, según la agencia <a href="{EFE}">EFE</a>. Echeverría, de 22 años y número uno del PP al Congreso por Gipuzkoa, intentaba montar una carpa informativa en Hernani el sábado a las once de la mañana cuando, según contó en <a href="{COPE}">COPE</a>, «un centenar de violentos» les lanzó petardos, huevos y piedras. Sus compañeros salieron de la plaza escoltados por la policía municipal.</p>
<blockquote class="cita"><p>«Defender las ideas del Partido Popular en el País Vasco es correr el riesgo de que apedreen tu vehículo».</p><footer>Alberto Núñez Feijóo, presidente del PP, según <a href="{COPE}">COPE</a></footer></blockquote>
<p data-tipo="dato">Echeverría busca un escaño que el PP no saca desde hace cinco elecciones generales. En julio de 2023, el PP sacó en Gipuzkoa {n(PP23)} votos, contando el voto exterior, y los seis diputados se repartieron a dos entre EH Bildu, el PSOE y el PNV. Para quitarle al PNV su segundo escaño, el último de los seis, el PP habría necesitado <strong>{n(FALTA)} votos más</strong>. Sumar se quedó más cerca: a {n(int(ULTQ - SUMAR23) + 1)}.</p>
{g_ult}
<p data-tipo="dato">El PP tuvo diputado guipuzcoano por última vez en 2011, cuando sacó el {p(H["2011_11"]["pp"])} % de los votos y EH Bildu, entonces Amaiur, se llevó tres de los seis escaños. En 2015 cayó al {p(H["2015_12"]["pp"])} % y lo perdió; su peor resultado fue el de abril de 2019, el {p(MINPP["pp"])} %. En 2023 subió al {p(H["2023_07"]["pp"])} %, lejos todavía del {p(MAXPP["pp"])} % de 2004.</p>
{g_hist}
<h2>Un voto concentrado en San Sebastián</h2>
<p data-tipo="dato">Casi la mitad de los votos del PP en Gipuzkoa salen de San Sebastián: {n(SS_V)} de {n(PPT)}, el {p(PESO_SS)} %, sin contar el voto exterior. Con Irun, llegan al {p(PESO_SS_IRUN)} %. De los {N_GR} municipios con más de 3.000 votos a candidaturas, solo en tres pasó del 10 %: San Sebastián ({p(SS_PCT)} %), Irun ({p(MU.at[IRUN, "pp"])} %) y Lasarte-Oria ({p(MU.at["20902", "pp"])} %). En {CERO} municipios pequeños no tuvo ni un voto.</p>
{g_mapa}
<p data-tipo="dato">En Hernani, el PP sacó {HV} votos en 2023, el {p(H_PCT)} %, frente al {p(HB_PCT)} % de EH Bildu. En una de sus 16 secciones censales, con {H0_C} votos a candidaturas y EH Bildu en el {p(H0_BI)} %, no tuvo ninguno; en la que mejor le fue, el {p(HMAX)} %. En 2011, cuando todavía tenía diputado por la provincia, el PP había sacado {n(H_HIST["2011_11"][0])} votos en el municipio.</p>
<h2>Lo que dicen las encuestas</h2>
<p data-tipo="dato">El modelo de <a href="{BASE}encuestas/gipuzkoa/">nuestras encuestas</a>, con los datos {VERSION}, da al PP en Gipuzkoa entre el {p(PPM_V[0])} % y el {p(PPM_V[2])} % de los votos, con un valor central del {p(PPM_V[1])} %, y ningún escaño en el reparto central; solo en la parte alta de la horquilla recuperaría uno. EH Bildu saca tres, el PSOE dos y el PNV uno. En Bizkaia, donde Feijóo da hoy un mitin en Bilbao, el modelo le da al PP un diputado; en La Rioja, dos de cuatro, y quizá un tercero.</p>
<p data-tipo="contexto">Echeverría, en <a href="{COPE}">COPE</a>: «El PP es la única alternativa para los vascos que quieren un cambio».</p>
'''

preguntas = [
    ('¿Tiene el PP diputado por Gipuzkoa?',
     f'No desde 2015. Lo tuvo por última vez en 2011. En julio de 2023 le faltaron {n(FALTA)} votos para el sexto escaño, que fue para el PNV.'),
    ('¿Cuántos votos sacó el PP en Hernani en 2023?',
     f'{HV}, el {p(H_PCT)} % de los votos a candidaturas. EH Bildu sacó el {p(HB_PCT)} %.'),
    ('¿Qué le pasó al candidato del PP en Hernani?',
     'El sábado 14 de noviembre, cuando intentaba montar una carpa informativa, un grupo le lanzó petardos, huevos y piedras, según contó él mismo en COPE.'),
]
enlaces = (f'{L("mapa-electoral-pais-vasco-29n", "El mapa electoral del País Vasco")} · '
           f'<a href="{BASE}encuestas/gipuzkoa/">Encuestas de Gipuzkoa</a> · <a href="{BASE}encuestas/bizkaia/">Encuestas de Bizkaia</a>')
foot = ('Datos: Ministerio del Interior, resultados de las generales de 2004 a 2023 por mesa (vía pollspaindata), sin voto exterior, y resultados '
        'definitivos de 2023 por provincia con voto exterior; modelo de mapaelectoral.es/encuestas. Cálculo: actualidad/src/resumenes/gipuzkoa_pp_hernani.py.')

DATOS = {'H': {f['y']: {k: v for k, v in f.items() if k != 'y'} for f in HIST}, 'ULTQ': ULTQ, 'PP23': PP23, 'SUMAR23': SUMAR23, 'FALTA': FALTA,
         'ESC23': ESC23, 'CERO': CERO, 'PPT': PPT, 'SS_V': SS_V, 'SS_PCT': SS_PCT, 'PESO_SS': PESO_SS, 'PESO_SS_IRUN': PESO_SS_IRUN,
         'IRUN_PCT': float(MU.at[IRUN, 'pp']), 'LAS_PCT': float(MU.at['20902', 'pp']), 'N_GR': N_GR, 'SOBRE10': len(SOBRE10),
         'HV': HV, 'H_PCT': H_PCT, 'HB_PCT': HB_PCT, 'H0_C': H0_C, 'H0_BI': H0_BI, 'HMAX': HMAX, 'HSEC': len(HS),
         'H_HIST': {k: list(v) for k, v in H_HIST.items()}, 'RC': {k: list(v) for k, v in RC.items()}, 'PPM_V': PPM_V,
         'RB_PP': list(RB['PP']), 'RR_PP': list(RR['PP'])}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'Feijóo en Gipuzkoa',
      f'Al PP le faltaron {n(FALTA)} votos en 2023 para recuperar un diputado en Gipuzkoa; Feijóo arropa hoy a su candidato, atacado en Hernani',
      f'El PP no saca diputado por Gipuzkoa desde 2011. Casi la mitad de sus votos en la provincia salen de San Sebastián; en Hernani sacó {HV}, el {p(H_PCT)} %. '
      'Las encuestas no le dan escaño en el reparto central.',
      '17 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('HIST', [(f['y'], round(f['pp'], 1), f.get('pp_esc')) for f in HIST], 'ULT', ULT, 'FALTA', FALTA, 'SUMAR', int(ULTQ - SUMAR23) + 1,
      'SS', round(PESO_SS, 1), round(PESO_SS_IRUN, 1), 'CERO', CERO, 'HER', HV, round(H_PCT, 1), round(HB_PCT, 1), H0_C, round(H0_BI, 1), round(HMAX, 1),
      'MOD', PPM_V, RC, VERSION, cuenta)
