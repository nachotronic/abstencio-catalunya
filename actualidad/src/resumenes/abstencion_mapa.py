"""«El mapa que nadie te enseña» (17-11-2026): dónde los que no votaron en 2023 superaron al partido más votado.

Abstención = censo de residentes en España (CER) menos votantes, por mesa: no incluye el voto exterior (CERA), que no se
asigna a ningún municipio. Se compara con los votos del partido más votado del mismo municipio o sección.
Datos: generales-2026/descargas/resultados_secciones_largo.csv (Interior, por mesa), municipios.csv (nombres),
secciones.csv (renta por unidad de consumo, Atlas de Distribución de Renta de los Hogares del INE, 2023).
Uso, desde la raíz: python3 actualidad/src/resumenes/abstencion_mapa.py
"""
import json
import os

import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import COL, NOM, caminos, grupos, p

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
SLUG = 'abstencion-mapa-ganador-29n'
ABS = 'var(--muted)'

r = pd.read_csv(RAIZ / 'generales-2026/descargas/resultados_secciones_largo.csv', dtype={'tract_code': str, 'mun_code': str})
NOMBRES = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype=str, usecols=['mun_code', 'municipio']).set_index('mun_code').municipio
FIJAS = ('tract_code', 'censo', 'blancos', 'nulos', 'candidaturas', 'votantes', 'eleccion', 'mun_code', 'OTROS')


def eleccion(y):
    x = r[r.eleccion == y].copy()
    P = [c for c in x.columns if c not in FIJAS and x[c].notna().any()]
    x[P] = x[P].fillna(0)
    x['abs'] = x.censo - x.votantes
    x['win'] = x[P].max(axis=1)
    x['wp'] = x[P].idxmax(axis=1)
    x['k'] = x['abs'] > x['win']
    m = x.groupby('mun_code')[P + ['censo', 'votantes']].sum()
    m['abs'] = m.censo - m.votantes
    m['win'] = m[P].max(axis=1)
    m['wp'] = m[P].idxmax(axis=1)
    m['k'] = m['abs'] > m['win']
    m['nom'] = NOMBRES.reindex(m.index).values
    return x, m, P


S23, M23, P23 = eleccion('2023_07')
S19, M19, P19 = eleccion('2019_11')
assert M23.nom.notna().all()

# --- España (sin voto exterior) ---
ABS23 = float(S23['abs'].sum())
VOT = {k: float(S23[k].sum()) for k in P23}
PRIMERO = max(VOT, key=VOT.get)
assert PRIMERO == 'PP'
PP23, PSOE23 = VOT['PP'], VOT['PSOE']
DIF_PP = ABS23 - PP23
PART23 = float(S23.votantes.sum() / S23.censo.sum() * 100)
assert round(ABS23 / 1e6, 1) == 10.4 and round(PP23 / 1e6, 1) == 8.1 and round(DIF_PP / 1e6, 1) == 2.3, (ABS23, PP23)

# --- Municipios ---
NMUN, KMUN = len(M23), int(M23.k.sum())
CENSO_KMUN = float(M23[M23.k].censo.sum() / M23.censo.sum() * 100)
NMUN19, KMUN19 = len(M19), int(M19.k.sum())
CENSO_KMUN19 = float(M19[M19.k].censo.sum() / M19.censo.sum() * 100)
GR = M23[M23.censo >= 100000].sort_values('censo', ascending=False)
NGR, KGR = len(GR), int(GR.k.sum())
GR19 = M19[M19.censo >= 100000]
NGR19, KGR19 = len(GR19), int(GR19.k.sum())
assert (NGR, KGR) == (46, 27) and (NGR19, KGR19) == (47, 45), (NGR, KGR, NGR19, KGR19)


def mun(nom):
    f = M23[M23.nom == nom]
    assert len(f) == 1, nom
    return f.iloc[0]


BCN, SEV, ZGZ, MLG = mun('Barcelona'), mun('Sevilla'), mun('Zaragoza'), mun('Málaga')
COR, LEG, VIG, MAD = mun('Córdoba'), mun('Leganés'), mun('Vigo'), mun('Madrid')
assert COR.k and COR.wp == 'PP' and COR['abs'] - COR.win == 44
assert LEG.k and LEG.wp == 'PSOE' and LEG['abs'] - LEG.win == 97
assert not VIG.k and VIG.wp == 'PSOE' and VIG.win - VIG['abs'] == 174
assert not MAD.k and MAD.wp == 'PP'
assert BCN.k and BCN.wp == 'PSOE' and SEV.k and ZGZ.k and MLG.k and SEV.wp == ZGZ.wp == MLG.wp == 'PP'
# Las diez grandes ciudades en que menos se vota, por abstención sobre el ganador
GR['ratio'] = GR['abs'] / GR.win

# --- Secciones ---
NSEC, KSEC = len(S23), int(S23.k.sum())
CENSO_KSEC = float(S23[S23.k].censo.sum() / S23.censo.sum() * 100)
NSEC19, KSEC19 = len(S19), int(S19.k.sum())
assert (NSEC, KSEC) == (36459, 18326), (NSEC, KSEC)

# Renta: diez grupos de secciones con el mismo número de secciones
SEC = pd.read_csv(RAIZ / 'generales-2026/descargas/secciones.csv', dtype={'tract_code': str}, usecols=['tract_code', 'renta_uc']).set_index('tract_code').renta_uc
S23['renta'] = S23.tract_code.map(SEC)
SIN_RENTA = int(S23.renta.isna().sum())
R = S23.dropna(subset=['renta']).copy()
R['dec'] = pd.qcut(R.renta, 10, labels=False) + 1
DEC = R.groupby('dec').agg(k=('k', 'mean'), vot=('votantes', 'sum'), censo=('censo', 'sum'), r0=('renta', 'min'), r1=('renta', 'max'))
DEC['k'] *= 100
DEC['part'] = DEC.vot / DEC.censo * 100
assert DEC.k.is_monotonic_decreasing and DEC.part.is_monotonic_increasing, DEC
K_POBRE, K_RICO = float(DEC.k.iloc[0]), float(DEC.k.iloc[-1])
P_POBRE, P_RICO = float(DEC.part.iloc[0]), float(DEC.part.iloc[-1])

# Provincias: dónde más y menos
NPROV = {'08': 'Barcelona', '17': 'Girona', '25': 'Lleida', '43': 'Tarragona', '52': 'Melilla', '51': 'Ceuta', '35': 'Las Palmas',
         '38': 'Santa Cruz de Tenerife', '01': 'Álava', '40': 'Segovia', '16': 'Cuenca', '05': 'Ávila', '34': 'Palencia', '07': 'Illes Balears'}
S23['prov'] = S23.tract_code.str[:2]
PROV = S23.groupby('prov').k.mean().mul(100).sort_values()
MAX4 = list(PROV.index[-4:][::-1])
MIN2 = list(PROV.index[:2])
assert PROV[MAX4].min() > 95 and M23[M23.index.str[:2].isin(['51', '52'])].k.all()
assert MAX4 == ['17', '25', '52', '43'] and MIN2 == ['40', '16'], (MAX4, MIN2)

# --- Mapas ---
PEN = [f'{i:02d}' for i in range(1, 53) if i not in (35, 38, 51, 52)]
OTRO = '#c49a3a'   # partidos sin color propio (Teruel Existe, Soria ¡Ya!, UPN...)
_CACHE = os.environ.get('CACHE_CAMINOS')   # solo para iterar en local: caminos() tarda unos 14 minutos con toda España
if _CACHE and os.path.exists(_CACHE):
    CAM, HMAP, CAMC, HMAPC = json.load(open(_CACHE))
else:
    CAM, HMAP = caminos(PEN, W=640, lat=40, umbral=3.5)
    CAMC, HMAPC = caminos(['35', '38'], W=640, lat=28.3, umbral=2)
    if _CACHE:
        json.dump([CAM, HMAP, CAMC, HMAPC], open(_CACHE, 'w'))


def relleno(k):
    if k not in M23.index:
        return 'var(--other)'
    f = M23.loc[k]
    return ABS if f.k else COL.get(f.wp, OTRO)


def mapa_colores(cam, H, etiqueta, rotulo=''):
    """Un solo trazado por color: con 8.000 municipios, un <path> o un <use> por municipio pesaría más de un mega.
    Sin texto al pasar por encima; los datos de las ciudades van en la tabla del gráfico siguiente."""
    por = {}
    for k, d in cam.items():
        por.setdefault(relleno(k), []).append(d)
    rot = f'<p style="margin:.8em 0 .2em;font-weight:700;font-size:.95em">{esc(rotulo)}</p>' if rotulo else ''
    return (f'{rot}<svg viewBox="0 0 640 {H}" role="img" aria-label="{esc(etiqueta)}" style="max-width:640px;margin:0 auto;display:block">'
            f'<g stroke="var(--bg)" stroke-width=".3" stroke-linejoin="round">'
            + ''.join(f'<path fill="{c}" d="{"".join(ds)}"/>' for c, ds in por.items()) + '</g></svg>')


PART_MAPA = {M23.loc[k].wp for k in list(CAM) + list(CAMC) if k in M23.index and not M23.loc[k].k}
LEY_MAPA = [('No votaron: más que el ganador', ABS)] + [(NOM.get(k, k), COL.get(k, 'var(--other)')) for k in ('PP', 'PSOE', 'VOX', 'SUMAR', 'BILDU', 'PNV', 'JUNTS', 'ERC', 'BNG', 'CC') if k in PART_MAPA] + ([('Otros partidos', OTRO)] if PART_MAPA - set(COL) else [])

g_mapa = figura(f'Los que no votaron superaron al partido más votado en {n(KMUN)} municipios, donde vive el {p(CENSO_KMUN)} % de los electores',
                'Generales de julio de 2023. Cada municipio lleva el color del partido más votado, salvo donde los que no votaron fueron más: esos van con el tono de «No votaron» de la leyenda',
                mapa_colores(CAM, HMAP, 'Mapa municipal de la abstención frente al partido más votado en 2023')
                + mapa_colores(CAMC, HMAPC, 'Canarias', rotulo='Canarias'),
                'Fuente: Ministerio del Interior, resultados por mesa (sin voto exterior). Abstención: electores residentes en España que no votaron. Ceuta y Melilla no se dibujan: en las dos, los que no votaron superaron al ganador. Cálculo propio.',
                LEY_MAPA)

TOP = GR.head(16)
CORTO = {'Las Palmas de Gran Canaria': 'Las Palmas', 'Alacant/Alicante': 'Alicante'}
g_ciudades = figura(f'La abstención superó al ganador en {KGR} de las {NGR} ciudades con más de 100.000 electores',
                    'Las 16 ciudades con más electores en 2023: electores que no votaron (primera barra) y votos del partido más votado (segunda barra)',
                    grupos([(CORTO.get(f.nom, f.nom.split('/')[0]), [(f['abs'], ABS, 1, 'no votaron'), (f.win, COL.get(f.wp, 'var(--other)'), 1, NOM.get(f.wp, f.wp))]) for _, f in TOP.iterrows()],
                           float(TOP[['abs', 'win']].max().max()), 'Abstención y votos del ganador en las 16 ciudades con más electores', W=400, ml=96, fmt=n),
                    'Fuente: Ministerio del Interior, resultados por mesa (sin voto exterior). Cálculo propio.',
                    [('No votaron', ABS), ('PP', COL['PP']), ('PSOE', COL['PSOE'])],
                    (['Municipio', 'Electores', 'No votaron', 'Más votado', 'Sus votos', 'Diferencia'],
                     [[f.nom, n(f.censo), n(f['abs']), NOM.get(f.wp, f.wp), n(f.win), ('+' if f['abs'] > f.win else '−') + n(abs(f['abs'] - f.win))] for _, f in GR.iterrows()]))

g_renta = figura(f'En las secciones con menos renta, la abstención superó al ganador en el {p(K_POBRE)} %; en las de más, en el {p(K_RICO)} %',
                 'Secciones censales en diez grupos del mismo tamaño, de menos a más renta por unidad de consumo: % de secciones en que los que no votaron superaron al partido más votado en 2023',
                 barras([(f'{"Menos renta" if d == 1 else "Más renta" if d == 10 else f"Grupo {d}"}', float(DEC.k[d]), ABS, p(DEC.k[d]) + ' %') for d in DEC.index],
                        100, 'Secciones donde la abstención superó al ganador, por renta', W=400, ml=96, fmt=p),
                 'Fuente: Ministerio del Interior, resultados por mesa, y Atlas de Distribución de Renta de los Hogares del INE (2023). Cálculo propio.',
                 None,
                 (['Grupo de renta', 'Renta por unidad de consumo (€)', 'Secciones donde ganó la abstención (%)', 'Participación (%)'],
                  [[str(d), f'{n(DEC.r0[d])}–{n(DEC.r1[d])}', p(DEC.k[d]), p(DEC.part[d])] for d in DEC.index]))

# --- Texto ---
cuerpo = f'''
<p data-tipo="contexto">El mapa electoral que se ve cada noche de elecciones pinta cada municipio del color del partido más votado. No enseña a los que no fueron a votar. Antes de las elecciones generales del 29N, este mapa los cuenta: en las generales de julio de 2023, {n(ABS23 / 1e6, 1)} millones de electores residentes en España no votaron, {n(DIF_PP / 1e6, 1)} millones más que los {n(PP23 / 1e6, 1)} millones que votaron al PP, el partido más votado. La participación de los residentes fue del {p(PART23)} %; el voto exterior queda fuera de esta cuenta porque no se asigna a ningún municipio.</p>
<p data-tipo="dato">Si la abstención fuera un partido, habría quedado por delante del ganador en {n(KMUN)} de los {n(NMUN)} municipios, donde vive el {p(CENSO_KMUN)} % de los electores. Pasó en {KGR} de las {NGR} ciudades con más de 100.000 electores: en Barcelona no votaron {n(BCN["abs"])}, frente a los {n(BCN.win)} votos del PSOE; en Sevilla, Zaragoza y Málaga, los que no votaron superaron al PP. En Córdoba, la diferencia fue de {n(COR["abs"] - COR.win)} personas; en Leganés, de {n(LEG["abs"] - LEG.win)} frente al PSOE. En Vigo fue al revés: el PSOE superó a la abstención por {n(VIG.win - VIG["abs"])} votos. En Madrid, el PP sacó {n(MAD.win)} votos y no votaron {n(MAD["abs"])}.</p>
{g_mapa}
{g_ciudades}
<p data-tipo="dato">Por secciones censales, el dibujo es parecido: en {n(KSEC)} de las {n(NSEC)} secciones de España, el {p(KSEC / NSEC * 100)} %, los que no votaron superaron al partido más votado. Las provincias con más secciones así fueron Girona, Lleida, Melilla y Tarragona, todas por encima del 95 %. En el otro extremo, Segovia ({p(PROV["40"])} %) y Cuenca ({p(PROV["16"])} %).</p>
<p data-tipo="patron">La abstención sigue a la renta. En el grupo de secciones con menos renta por unidad de consumo, los que no votaron superaron al ganador en el {p(K_POBRE)} % de las secciones; en el de más renta, en el {p(K_RICO)} %. La participación fue del {p(P_POBRE)} % en el primer grupo y del {p(P_RICO)} % en el último. Es una relación entre secciones, no entre personas: no dice quién dejó de votar dentro de cada barrio.</p>
{g_renta}
<p data-tipo="dato">En noviembre de 2019 fue más: la abstención superó al ganador en {n(KMUN19)} municipios, con el {p(CENSO_KMUN19)} % de los electores, y en {KGR19} de las {NGR19} ciudades con más de 100.000 electores. Entonces votó el {p(float(S19.votantes.sum() / S19.censo.sum() * 100))} % de los residentes, y el voto estaba más repartido: el PSOE ganó con menos votos que el PP en 2023.</p>
<p data-tipo="contexto">La abstención no es un bloque. Incluye a quien decide no votar y a quien no puede: enfermos, personas que trabajan ese día o que cambiaron de casa sin cambiar de censo. Por eso este mapa no dice qué votarían, solo cuántos son.</p>
'''

preguntas = [
    ('¿Cuántas personas no votaron en las elecciones generales de 2023?',
     f'{n(ABS23 / 1e6, 1)} millones de electores residentes en España, el {p(100 - PART23)} % del censo de residentes. Son más que los votos del PP, el partido más votado, que sacó {n(PP23 / 1e6, 1)} millones sin contar el voto exterior.'),
    ('¿En qué grandes ciudades superó la abstención al partido más votado?',
     f'En {KGR} de las {NGR} ciudades con más de 100.000 electores, entre ellas Barcelona, Sevilla, Zaragoza, Málaga, Palma, Las Palmas de Gran Canaria y Bilbao. En Madrid, València y Murcia, no.'),
    ('¿Dónde se vota menos?',
     f'En las secciones con menos renta: en el grupo con menos renta votó el {p(P_POBRE)} % de los electores, y en el de más renta, el {p(P_RICO)} %.'),
]
enlaces = f'{L("a-quien-beneficia-abstencion-29n", "¿A quién beneficia la abstención?")} · <a href="{BASE}elecciones/elecciones-29n-2026/">Las elecciones generales del 29N</a>'
foot = ('Datos: Ministerio del Interior, resultados por mesa de las generales de noviembre de 2019 y julio de 2023 (sin voto exterior); '
        'INE, Atlas de Distribución de Renta de los Hogares (2023). Cálculo: actualidad/src/resumenes/abstencion_mapa.py.')

DATOS = {'ABS23': ABS23, 'PP23': PP23, 'DIF_PP': DIF_PP, 'PART23': PART23, 'NMUN': NMUN, 'KMUN': KMUN, 'CENSO_KMUN': CENSO_KMUN,
         'NMUN19': NMUN19, 'KMUN19': KMUN19, 'CENSO_KMUN19': CENSO_KMUN19, 'NGR': NGR, 'KGR': KGR, 'NGR19': NGR19, 'KGR19': KGR19,
         'NSEC': NSEC, 'KSEC': KSEC, 'K_POBRE': K_POBRE, 'K_RICO': K_RICO, 'P_POBRE': P_POBRE, 'P_RICO': P_RICO,
         'PART19': float(S19.votantes.sum() / S19.censo.sum() * 100), 'PROV': {k: float(v) for k, v in PROV.items()},
         'CIUD': {f.nom: {'abs': float(f['abs']), 'win': float(f.win), 'wp': f.wp} for _, f in GR.iterrows()}}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'El mapa que nadie te enseña',
      f'Si la abstención fuera un partido, en 2023 habría quedado por delante del ganador en {KGR} de las {NGR} grandes ciudades y en la mitad de las secciones de España',
      f'El mapa que nadie te enseña antes de las elecciones generales del 29N: {n(ABS23 / 1e6, 1)} millones de residentes no votaron en 2023, '
      f'{n(DIF_PP / 1e6, 1)} millones más que los votos del PP. En Córdoba, la abstención superó al PP por {n(COR["abs"] - COR.win)}.',
      '17 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('ABS', ABS23, 'PP', PP23, 'DIF', DIF_PP, 'PART', round(PART23, 2), 'MUN', KMUN, NMUN, round(CENSO_KMUN, 1), 'GR', KGR, NGR,
      'SEC', KSEC, NSEC, 'DEC', round(K_POBRE, 1), round(K_RICO, 1), 'PROV', PROV.tail(4).round(1).to_dict(), PROV.head(2).round(1).to_dict(),
      '2019', KMUN19, round(CENSO_KMUN19, 1), KGR19, NGR19)
