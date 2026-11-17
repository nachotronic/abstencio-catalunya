"""Las secciones que cambiaron de ganador entre las generales de noviembre de 2019 y las de julio de 2023, y las que se
decidieron por menos de dos puntos (serie «lo que no te enseñan»).

Datos: generales-2026/descargas/resultados_secciones_largo.csv (Ministerio del Interior, resultados por mesa agregados
por sección, sin voto exterior). Solo secciones con el mismo código en las dos elecciones y un censo que cambia menos
de un 15 %, para que sean el mismo territorio. Ganador: candidatura con más votos (sin «Otros», que agrupa listas).
Navarra: en 2019 Navarra Suma (UPN, PP y Cs) va en la columna PP; en 2023 se suman PP y UPN, que fueron por separado,
para comparar el mismo espacio, como la lista conjunta UPN-PP del 29N.
Margen: votos del primero menos los del segundo, sobre votos válidos (candidaturas más blanco).
Uso, desde la raíz: python3 actualidad/src/resumenes/secciones_cambian_ganador.py
"""
import json

import numpy as np
import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, barras, mapa_provincias, pieza
from mapa_ccaa import COL

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
SLUG = 'secciones-cambian-ganador-29n'
CENSO_MAX = 0.15
MARGEN = 2

d = pd.read_csv(RAIZ / 'generales-2026/descargas/resultados_secciones_largo.csv', dtype={'tract_code': str, 'mun_code': str}, low_memory=False)
NOPART = {'tract_code', 'censo', 'blancos', 'nulos', 'candidaturas', 'votantes', 'eleccion', 'mun_code', 'OTROS'}
P = [c for c in d.columns if c not in NOPART]
a = d[d.eleccion == '2019_11'].set_index('tract_code')
b = d[d.eleccion == '2023_07'].set_index('tract_code')
NA, NB = len(a), len(b)
com = a.index.intersection(b.index)
ok = com[((b.loc[com, 'censo'] / a.loc[com, 'censo'] - 1).abs() < CENSO_MAX)]
A19 = a.loc[ok, P].fillna(0)
B23 = b.loc[ok, P].fillna(0).copy()
nav = ok.str[:2] == '31'
assert A19.loc[nav, 'UPN'].sum() == 0   # Navarra Suma de 2019, en la columna PP
B23.loc[nav, 'PP'] += B23.loc[nav, 'UPN']
B23.loc[nav, 'UPN'] = 0


def ganador(t):
    """Partido con más votos; 'EMPATE' si los dos primeros tienen los mismos votos."""
    o = np.argsort(-t.values, axis=1, kind='stable')
    v1, v2 = np.take_along_axis(t.values, o[:, :1], 1)[:, 0], np.take_along_axis(t.values, o[:, 1:2], 1)[:, 0]
    return pd.Series(np.where(v1 == v2, 'EMPATE', t.columns[o[:, 0]]), index=t.index), pd.Series(t.columns[o[:, 1]], index=t.index)


W19, _ = ganador(A19)
W23, SEG = ganador(B23)
EMP = int(((W19 == 'EMPATE') | (W23 == 'EMPATE')).sum())
CH = (W19 != W23) & (W19 != 'EMPATE') & (W23 != 'EMPATE')
VAL = b.loc[ok, 'candidaturas'] + b.loc[ok, 'blancos']
s = np.sort(B23.values, axis=1)
MARG = pd.Series((s[:, -1] - s[:, -2]) / VAL.values * 100, index=ok)
CENSO = b.loc[ok, 'censo']
PROV = pd.Series(ok.str[:2], index=ok)

NS, NCH = len(ok), int(CH.sum())
PCH, PCEN = NCH / NS * 100, CENSO[CH].sum() / CENSO.sum() * 100
FLU = pd.crosstab(W19[CH], W23[CH]).stack().sort_values(ascending=False)
FLU = FLU[FLU > 0]
F = lambda x, y: int(FLU.get((x, y), 0))
PSOE_PP, PP_PSOE, ERC_PSOE, VOX_PP = F('PSOE', 'PP'), F('PP', 'PSOE'), F('ERC', 'PSOE'), F('VOX', 'PP')
CER = (MARG < MARGEN) & (W23 != 'EMPATE')
NCER, PCER = int(CER.sum()), CER.mean() * 100
CER_PP_PSOE = int((CER & (W23 == 'PP') & (SEG == 'PSOE')).sum())
CER_PSOE_PP = int((CER & (W23 == 'PSOE') & (SEG == 'PP')).sum())
CER_CH = int((CER & CH).sum())
CENSO_CER = int(CENSO[CER].sum())

CIF = json.load(open(RAIZ / 'actualidad/src/sistema/cifras.json'))['2023_07']['provincias']
NOMP = {k: v['nombre'] for k, v in CIF.items()}
TP = pd.DataFrame({'ch': CH, 'prov': PROV}).groupby('prov').ch.agg(['mean', 'sum', 'size'])
TP['dest'] = [W23[CH & (PROV == pr)].value_counts().idxmax() if TP.loc[pr, 'sum'] else None for pr in TP.index]
TP = TP.sort_values('mean', ascending=False)
MAXP, MINP = TP.index[0], TP.index[-1]
MAS_MITAD = int((TP['mean'] > .5).sum())
VP_MUR = int((CH & (W19 == 'VOX') & (W23 == 'PP') & (PROV == '30')).sum())
assert PROV[CH & (W19 == 'VOX') & (W23 == 'PP')].value_counts().index[0] == '30'
assert set(PROV[CH & (W19 == 'ERC') & (W23 == 'PSOE')]) <= {'08', '17', '25', '43'}

# Cifras que sostienen el texto
assert NB - NS < 0.07 * NB, (NB, NS)
assert 0.3 < PCH / 100 < 0.4 and PSOE_PP > 5 * PP_PSOE
assert FLU.index[0] == ('PSOE', 'PP') and FLU.index[1] == ('ERC', 'PSOE') and FLU.index[2] == ('VOX', 'PP')
assert CER_PP_PSOE > CER_PSOE_PP and EMP < 500
assert not ((W23 == SEG) & CER).any()

NOM = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'SUMAR': 'Sumar', 'ERC': 'ERC', 'JUNTS': 'Junts', 'PNV': 'PNV', 'BILDU': 'EH Bildu',
       'BNG': 'BNG', 'CC': 'CC', 'CS': 'Cs', 'TE': 'Teruel Existe', 'PRC': 'PRC', 'CUP': 'CUP', 'NC': 'NC', 'UPN': 'UPN'}
NOM19 = {**NOM, 'SUMAR': 'Unidas Podemos'}
col = lambda k: COL.get(k, 'var(--otros)')

# ---------- Gráfico 1: de quién a quién ----------
TOP = FLU.head(8)
g_flujos = figura(f'En {n(PSOE_PP)} secciones ganó el PSOE en 2019 y el PP en 2023; al revés, solo en {n(PP_PSOE)}',
                  f'Secciones que cambiaron de ganador entre las generales de noviembre de 2019 y las de julio de 2023, según quién ganó en cada una: los {len(TOP)} cambios más frecuentes',
                  barras([(f'{NOM19.get(x, x)} → {NOM.get(y, y)}', v, col(y), n(v)) for (x, y), v in TOP.items()],
                         TOP.iloc[0] * 1.15, 'Secciones que cambiaron de ganador, por partido', W=400, ml=150),
                  'Fuente: Ministerio del Interior, resultados por mesa agregados por sección censal, sin voto exterior. Cálculo propio.',
                  None,
                  (['Ganó en 2019', 'Ganó en 2023', 'Secciones'], [[NOM19.get(x, x), NOM.get(y, y), n(v)] for (x, y), v in FLU.items()]))

# ---------- Gráfico 2: mapa de provincias ----------
colores = {pr: col(r.dest) if r.dest else 'var(--otros)' for pr, r in TP.iterrows()}
opac = {pr: round(.15 + .85 * r['mean'], 2) for pr, r in TP.iterrows()}
titulos = {pr: f'{NOMP.get(pr, pr)}: {p(r["mean"] * 100)} % de las secciones cambió de ganador' for pr, r in TP.iterrows()}
g_mapa = figura(f'En {NOMP[MAXP]} cambió de ganador el {p(TP.loc[MAXP, "mean"] * 100)} % de las secciones; en {NOMP[MINP]}, el {p(TP.loc[MINP, "mean"] * 100)} %',
                'Porcentaje de secciones de cada provincia que cambiaron de ganador entre 2019 y 2023: cuanto más intenso, más cambiaron. El color es el del partido que más secciones ganó al cambiar',
                mapa_provincias(colores, titulos, 'Mapa de provincias según el porcentaje de secciones que cambiaron de ganador', opac),
                'Fuente: Ministerio del Interior. Cálculo propio.',
                [(NOM[k], COL[k]) for k in sorted(set(TP.dest.dropna()), key=lambda k: -int((TP.dest == k).sum()))],
                (['Provincia', 'Secciones', 'Cambiaron de ganador', '%'],
                 [[NOMP.get(pr, pr), n(r['size']), n(r['sum']), p(r['mean'] * 100)] for pr, r in TP.iterrows()]))

# ---------- Gráfico 3: las que se decidieron por menos de dos puntos ----------
PAR = pd.crosstab(W23[CER], SEG[CER]).stack().sort_values(ascending=False)
PAR = PAR[PAR > 0].head(6)
g_cerca = figura(f'{n(NCER)} secciones se decidieron en 2023 por menos de {MARGEN} puntos',
                 f'Secciones donde el primero sacó al segundo menos de {MARGEN} puntos en las generales de 2023, según quién quedó primero y quién segundo',
                 barras([(f'{NOM.get(x, x)} sobre {NOM.get(y, y)}', v, col(x), n(v)) for (x, y), v in PAR.items()],
                        PAR.iloc[0] * 1.15, f'Secciones decididas por menos de {MARGEN} puntos en 2023', W=400, ml=150),
                 'Fuente: Ministerio del Interior. Margen sobre votos válidos. Cálculo propio.')

cuerpo = f'''
<p data-tipo="contexto">El mapa de las elecciones generales se suele contar por provincias, que son las que reparten los escaños. Pero dentro de cada una hay barrios y pueblos que cambian de un partido a otro de una elección a la siguiente. Hemos comparado las {n(NS)} secciones censales que tenían el mismo territorio en las generales de noviembre de 2019 y en las de julio de 2023. En {n(EMP)} de ellas los dos primeros empataron en una de las dos elecciones, y no se cuentan como cambio.</p>
<p data-tipo="dato">En {n(NCH)} de ellas, el {p(PCH)} %, ganó en 2023 un partido distinto que en 2019. Viven en ellas el {p(PCEN)} % de los electores de esas secciones. El cambio más frecuente fue del PSOE al PP: {n(PSOE_PP)} secciones. Al revés, del PP al PSOE, solo {n(PP_PSOE)}.</p>
{g_flujos}
<p data-tipo="patron">Detrás del PSOE y el PP hay otros dos movimientos grandes. En Cataluña, el PSOE ganó en 2023 en {n(ERC_PSOE)} secciones donde en 2019 había ganado ERC. Y el PP recuperó {n(VOX_PP)} secciones donde en 2019 había ganado Vox; {n(VP_MUR)} de ellas, en la Región de Murcia.</p>
{g_mapa}
<p data-tipo="dato">Donde más cambió fue en {NOMP[MAXP]}, con el {p(TP.loc[MAXP, "mean"] * 100)} % de sus secciones, y donde menos, en {NOMP[MINP]}, con el {p(TP.loc[MINP, "mean"] * 100)} %. En {MAS_MITAD} provincias cambió de ganador más de la mitad de las secciones.</p>
<p data-tipo="dato">De cara al 29N importan también las que estuvieron a punto de cambiar. En 2023, {n(NCER)} secciones, el {p(PCER)} %, se decidieron por menos de {MARGEN} puntos; en ellas votan {n(CENSO_CER)} electores. En {n(CER_PP_PSOE)}, el PP quedó por delante del PSOE por menos de {MARGEN} puntos, y en {n(CER_PSOE_PP)}, al revés. {n(CER_CH)} de esas secciones ya habían cambiado de ganador desde 2019.</p>
{g_cerca}
<p data-tipo="contexto">Ganar más secciones no es ganar más escaños: una sección del centro de Madrid y otra de un pueblo de Soria cuentan igual en este recuento, aunque tengan muy distinto número de electores, y los escaños se reparten con los votos de toda la provincia. Lo que enseñan las secciones es dónde se movió el voto. El {L("abstencion-mapa-ganador-29n", "mapa de la abstención")} cuenta otra parte de la misma historia.</p>
'''

preguntas = [
    ('¿Cuántas secciones cambiaron de ganador entre 2019 y 2023?',
     f'{n(NCH)} de las {n(NS)} secciones comparables, el {p(PCH)} %. La mayoría pasaron del PSOE al PP: {n(PSOE_PP)}.'),
    ('¿Cuántas secciones se decidieron por poco en 2023?',
     f'{n(NCER)} secciones, el {p(PCER)} %, se decidieron por menos de {MARGEN} puntos.'),
]
enlaces = f'{L("encuestas-error-2023-2019-29n", "Lo que las encuestas no dicen")} · <a href="{BASE}">Busca tu sección en el mapa</a>'
foot = ('Datos: Ministerio del Interior, resultados por mesa de las generales de noviembre de 2019 y julio de 2023, agregados por sección censal. '
        'Cálculo: actualidad/src/resumenes/secciones_cambian_ganador.py.')
H1 = 'Elecciones generales: una de cada tres secciones cambió de ganador entre 2019 y 2023'
DEK = f'En {n(PSOE_PP)} secciones el ganador pasó del PSOE al PP; al revés, solo en {n(PP_PSOE)}. Otras {n(NCER)} se decidieron por menos de {MARGEN} puntos.'
pieza(SLUG, 'El mapa que nadie te enseña', H1, DEK, '18 de noviembre de 2026', cuerpo, preguntas, enlaces, foot)
print('EMP', EMP, 'NS', NS, 'NB', NB, 'NCH', NCH, round(PCH, 2), round(PCEN, 2), 'flujos', PSOE_PP, PP_PSOE, ERC_PSOE, VOX_PP, 'cerca', NCER, round(PCER, 2),
      CER_PP_PSOE, CER_PSOE_PP, CER_CH, CENSO_CER, 'prov', NOMP[MAXP], round(TP.loc[MAXP, 'mean'], 3), NOMP[MINP], round(TP.loc[MINP, 'mean'], 3), MAS_MITAD)
