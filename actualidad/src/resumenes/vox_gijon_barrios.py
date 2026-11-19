"""Vox en Gijón, barrio a barrio, el día del mitin de Abascal en la ciudad (pieza del 19-11-2026).

Votos por sección: generales-2026/descargas/resultados_secciones_largo.csv (Ministerio del Interior, mesas agregadas por sección).
Barrios: data/barrios/secciones_barrio.csv (los de las fichas /municipio/asturias/gijon/<barrio>/). Renta: renta media por unidad
de consumo del INE (Atlas de Distribución de Renta de los Hogares), generales-2026/descargas/secciones.csv, media ponderada por población.
Porcentajes sobre voto válido (candidaturas más blanco), como en las fichas. Solo barrios con 3 secciones o más.
Uso, desde la raíz: python3 actualidad/src/resumenes/vox_gijon_barrios.py
"""
import json

import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, pieza
from mapa_ccaa import COL, grupos, p

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
SLUG = 'vox-gijon-barrios-abascal-29n'
GIJ = '33024'
ESP = 'https://www.elespanol.com/espana/20261119/elecciones-generales-directo-ultima-hora-pedro-sanchez-sondeos-actos-campana-psoe-pp-vox-partidos-voto-correo-2026-encuestas/1003744463824_10.html'
FICHA = lambda b: f'{BASE}municipio/asturias/gijon/{b}/'

d = pd.read_csv(RAIZ / 'generales-2026/descargas/resultados_secciones_largo.csv', dtype={'tract_code': str, 'mun_code': str}, low_memory=False)
g = d[d.mun_code == GIJ].copy()
g['val'] = g.candidaturas + g.blancos
bar = pd.read_csv(RAIZ / 'data/barrios/secciones_barrio.csv', dtype=str)
bar = bar[bar.mun_code == GIJ][['tract_code', 'barrio']]
sec = pd.read_csv(RAIZ / 'generales-2026/descargas/secciones.csv', dtype={'tract_code': str, 'mun_code': str}, low_memory=False)
sec = sec[sec.mun_code == GIJ][['tract_code', 'renta_uc', 'poblacion']]

CIU = {e: dict(vox=g[g.eleccion == e].VOX.sum() / g[g.eleccion == e].val.sum() * 100, votos=int(g[g.eleccion == e].VOX.sum()))
       for e in ('2019_11', '2023_07')}

B = {}
for e in ('2019_11', '2023_07'):
    x = g[g.eleccion == e].merge(bar, on='tract_code')
    a = x.groupby('barrio').agg(VOX=('VOX', 'sum'), val=('val', 'sum'), n=('tract_code', 'count'))
    B[e] = a.VOX / a.val * 100
    if e == '2023_07':
        N = a.n
        r = x.merge(sec, on='tract_code').groupby('barrio').apply(lambda t: (t.renta_uc * t.poblacion).sum() / t.poblacion.sum())
T = pd.DataFrame({'v23': B['2023_07'], 'v19': B['2019_11'], 'n': N, 'renta': r})
T = T[T.n >= 3].sort_values('v23', ascending=False)
NB = len(T)
TOP, ULT = T.index[0], T.index[-1]
RICO = T.renta.idxmax()
assert TOP == RICO == 'Somió', (TOP, RICO)
BAJAN = int((T.v23 < T.v19).sum())

# Secciones por quintil de renta, toda la ciudad (2023)
s23 = g[g.eleccion == '2023_07'].merge(sec, on='tract_code').dropna(subset=['renta_uc'])
s23['q'] = pd.qcut(s23.renta_uc, 5, labels=False) + 1
Q = s23.groupby('q').apply(lambda t: t.VOX.sum() / t.val.sum() * 100)
Q5, QRESTO = float(Q.loc[5]), (float(Q.loc[1:4].min()), float(Q.loc[1:4].max()))
NSEC = len(s23)

SLUGB = {'Somió': 'somio', 'Roces Urbano': 'roces-urbano', 'Viesques': 'viesques', 'Contrueces': 'contrueces', 'El Bibio-Parque': 'el-bibio-parque',
         'Montevil': 'montevil', 'El Centro': 'el-centro', 'Perchera-La Braña': 'perchera-la-brana', "L'Arena": 'l-arena',
         'Ceares / Ciares': 'ceares-ciares', 'La Calzada': 'la-calzada', 'Pumarín': 'pumarin', 'El Coto': 'el-coto', 'Laviada': 'laviada',
         'El Llano': 'el-llano', 'El Natahoyo': 'el-natahoyo', 'Cimavilla': 'cimavilla', 'El Polígono': 'el-poligono'}
assert set(T.index) <= set(SLUGB), set(T.index) - set(SLUGB)
for b in T.index:
    assert (RAIZ / f'municipio/asturias/gijon/{SLUGB[b]}/index.html').exists(), b
FB = lambda b: f'<a href="{FICHA(SLUGB[b])}">{esc(b)}</a>'

g_b = figura(f'Vox bajó en los {NB} barrios de Gijón entre 2019 y 2023; donde más votos saca es en Somió',
             'Voto a Vox en las elecciones generales de noviembre de 2019 y de julio de 2023 por barrio de Gijón, en % del voto válido',
             grupos([(b, [(r.v19, COL['VOX'], .45, f'2019: {p(r.v19)} %'), (r.v23, COL['VOX'], 1, f'2023: {p(r.v23)} %')]) for b, r in T.iterrows()],
                    T.v19.max() * 1.12, 'Voto a Vox por barrio de Gijón, 2019 y 2023', W=400, ml=130),
             'Fuente: Ministerio del Interior, resultados por sección censal, agregados por barrio. Barrios con tres secciones o más. Cálculo propio.',
             [('Noviembre de 2019', f"color-mix(in srgb, {COL['VOX']} 45%, transparent)"), ('Julio de 2023', COL['VOX'])],
             (['Barrio', 'Vox 2019 (%)', 'Vox 2023 (%)', 'Renta por unidad de consumo (euros)', 'Secciones'],
              [[b, p(r.v19), p(r.v23), n(r.renta), n(r.n)] for b, r in T.iterrows()]))

cuerpo = f'''
<p data-tipo="contexto">Santiago Abascal da este jueves un mitin en Gijón a las 19.30, según la agenda de la campaña de las elecciones generales del 29N que publica <a href="{ESP}">El Español</a>.</p>
<p data-tipo="dato">En Gijón, Vox sacó el <strong>{p(CIU['2023_07']['vox'])} %</strong> del voto válido en las generales de 2023, {n(CIU['2023_07']['votos'])} votos, frente al {p(CIU['2019_11']['vox'])} % de noviembre de 2019. Bajó en los {BAJAN} barrios de la ciudad con datos suficientes.</p>
<p data-tipo="dato">Donde más votó a Vox fue {FB(TOP)}, el barrio con más renta de los {NB}: el <strong>{p(T.loc[TOP, 'v23'])} %</strong> en 2023, después del {p(T.loc[TOP, 'v19'])} % de 2019. Le siguen {FB(T.index[1])} ({p(T.iloc[1].v23)} %) y {FB(T.index[2])} ({p(T.iloc[2].v23)} %). Donde menos, {FB(ULT)}, con el {p(T.loc[ULT, 'v23'])} %, y {FB(T.index[-2])}, con el {p(T.iloc[-2].v23)} %.</p>
{g_b}
<p data-tipo="patron">Sección a sección se ve lo mismo: en la quinta parte de las secciones con más renta de Gijón, Vox sacó el {p(Q5)} % en 2023; en las otras, entre el {p(QRESTO[0])} y el {p(QRESTO[1])} %. Es una relación entre secciones: no dice quién vota a Vox dentro de cada una.</p>
<p data-tipo="contexto">Cada barrio tiene su ficha, con el voto de cada sección desde 2004: {FB('Somió')}, {FB('El Centro')} o {FB('El Llano')}, entre otros. El mapa de toda Asturias, en {L("mapa-electoral-asturias-29n", "el mapa electoral de Asturias")}.</p>
'''

preguntas = [
    ('¿Cuánto votó Gijón a Vox en 2023?',
     f'El {p(CIU["2023_07"]["vox"])} % del voto válido en las generales de julio de 2023, frente al {p(CIU["2019_11"]["vox"])} % de noviembre de 2019.'),
    ('¿En qué barrio de Gijón vota más a Vox?',
     f'En {esc(TOP)}: el {p(T.loc[TOP, "v23"])} % en 2023. Es también el barrio con más renta de la ciudad.'),
]
enlaces = f'{L("mapa-electoral-asturias-29n", "El mapa electoral de Asturias")} · {L("vox-barrios-obreros-clase-29n", "Vox y los barrios obreros")}'
foot = ('Datos: Ministerio del Interior, resultados por sección censal; INE, Atlas de Distribución de Renta de los Hogares; barrios de las fichas de mapaelectoral.es. '
        'Cálculo: actualidad/src/resumenes/vox_gijon_barrios.py.')
DATOS = {'CIU': CIU, 'T': {b: {k: float(v) for k, v in r.items()} for b, r in T.iterrows()}, 'NB': NB, 'BAJAN': BAJAN, 'Q5': Q5,
         'QRESTO': QRESTO, 'NSEC': NSEC, 'TOP': TOP, 'ULT': ULT}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'Vox en Gijón',
      f'Elecciones generales: en Gijón, Vox saca su mejor resultado en Somió, el barrio más rico: {p(T.loc[TOP, "v23"])} %',
      f'Abascal da un mitin en la ciudad este jueves. Vox bajó en los {NB} barrios entre 2019 y 2023; en toda Gijón, del {p(CIU["2019_11"]["vox"])} % al {p(CIU["2023_07"]["vox"])} %.',
      '19 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(CIU, NB, BAJAN, TOP, ULT, round(Q5, 1), [round(x, 1) for x in QRESTO], NSEC)
