"""Cifras de las páginas de entrada por territorio (src/territorios.py).

Todo sale de las descargas públicas del mapa (generales-2026/descargas/), las mismas que puede bajarse
cualquier lector: resultados al Congreso por municipio desde 1977 y por sección censal desde 2004,
con la renta del INE por sección.
"""
import pathlib, sys
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / 'generales-2026' / 'descargas'
sys.path.insert(0, str(ROOT / 'generales-2026' / 'src'))
from partidos import FAMILIAS, ALIAS  # noqa: E402

FAM = [c for c, _, _ in FAMILIAS]
NOMBRE = {c: n for c, n, _ in FAMILIAS}
COLOR = {c: col for c, _, col in FAMILIAS}
GENERALES = ['1977_06', '1979_03', '1982_10', '1986_06', '1989_10', '1993_06', '1996_03', '2000_03',
             '2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
ETIQUETA = {'2019_04': 'abr. 2019', '2019_11': 'nov. 2019'}
FECHA = {'1977_06': '15 de junio de 1977', '1979_03': '1 de marzo de 1979', '1982_10': '28 de octubre de 1982', '1986_06': '22 de junio de 1986',
         '1989_10': '29 de octubre de 1989', '1993_06': '6 de junio de 1993', '1996_03': '3 de marzo de 1996', '2000_03': '12 de marzo de 2000',
         '2004_03': '14 de marzo de 2004', '2008_03': '9 de marzo de 2008', '2011_11': '20 de noviembre de 2011', '2015_12': '20 de diciembre de 2015',
         '2016_06': '26 de junio de 2016', '2019_04': '28 de abril de 2019', '2019_11': '10 de noviembre de 2019', '2023_07': '23 de julio de 2023'}
ULTIMA = '2023_07'


def etiqueta(y):
    return ETIQUETA.get(y, y[:4])


def nombre_familia(c, y):
    """Nombre de la familia en esa elección (AP antes de 1989, PCE / PSUC antes de 1986...)."""
    for hasta, alias in ALIAS.get(c, []):
        if y[:4] < hasta:
            return alias
    return NOMBRE[c]


def _carga():
    m = pd.read_csv(D / 'municipios.csv', dtype={'mun_code': str})
    h = pd.read_csv(D / 'municipios_historico.csv', dtype={'mun_code': str})
    mun = m.merge(h.drop(columns=['municipio', 'provincia']), on='mun_code', how='left')
    mun = mun.copy()
    mun['prov'] = mun.mun_code.str[:2]
    s = pd.read_csv(D / 'secciones.csv', dtype={'tract_code': str, 'mun_code': str}, usecols=['tract_code', 'mun_code', 'renta_uc'])
    lar = pd.read_csv(D / 'resultados_secciones_largo.csv', dtype={'tract_code': str, 'mun_code': str})
    lar = lar[lar.eleccion == ULTIMA].merge(s[['tract_code', 'renta_uc']], on='tract_code', how='left')
    lar['prov'] = lar.tract_code.str[:2]
    return mun, lar


MUN, SEC = _carga()

# En 2015 y en noviembre de 2019 la familia «Sumar / Podemos / IU» reúne dos listas que fueron por separado
# (Podemos e IU-Unidad Popular; Unidas Podemos y Más País), y en 2011 y abril de 2019, en la Comunitat Valenciana
# (EUPV y Compromís-Q; Unides Podem y Compromís). generales-2026/src/listas_separadas.py guarda los
# votos de la segunda por sección: con ellos el más votado se calcula con cada lista, no con la suma.
SEPARADAS = ('2011_11', '2015_12', '2019_04', '2019_11')
FUSIONES = {'36011': '36902', '36012': '36902', '15026': '15902', '15063': '15902'}   # las de construir.py
LS = pd.read_csv(D / 'listas_separadas.csv', dtype={'tract_code': str}) if (D / 'listas_separadas.csv').exists() else None
if LS is not None:
    _m = LS.assign(mun_code=LS.tract_code.str[:5].replace(FUSIONES)).groupby(['eleccion', 'mun_code']).sumar_b.sum()
    for _y in SEPARADAS:
        MUN[f'{_y}_vSUMAR_B'] = MUN.mun_code.map(_m.loc[_y]).fillna(0) if _y in _m.index.get_level_values(0) else 0
# las familias que solo existen en 1933-1936 (Segunda República) no están en las descargas desde 1977
FAM = [c for c in FAM if f'{ULTIMA}_v{c}' in MUN.columns]


def resultado(df, y):
    """Voto por familia sobre voto válido, participación, votantes y censo de un conjunto de municipios."""
    v = df[[f'{y}_v{c}' for c in FAM]].fillna(0)
    pct = df[[f'{y}_{c}' for c in FAM]].fillna(0).sum(axis=1)
    ok = pct > 0
    validos = (v[ok].sum(axis=1) / pct[ok]).sum()   # voto válido = votos a candidaturas + blancos
    votos = {c: v[f'{y}_v{c}'][ok].sum() for c in FAM}
    con_part = df[df[f'{y}_part'].notna()]
    censo, votantes = con_part[f'{y}_censo'].sum(), con_part[f'{y}_votantes'].sum()
    b = df[f'{y}_vSUMAR_B'][ok].sum() if f'{y}_vSUMAR_B' in df else 0
    return {'pct': {c: votos[c] / validos if validos else None for c in FAM}, 'votos': votos, 'validos': validos,
            'sumar_b': b / validos if validos and b else None,
            'part': votantes / censo if censo else None, 'censo': censo, 'votantes': votantes,
            'municipios': int(ok.sum()), 'sin_dato': int((~ok & df[f'{y}_censo'].fillna(0).gt(0)).sum())}


def pct_listas(r):
    """Voto de cada familia, salvo que la de Sumar / Podemos / IU cuenta solo su lista más votada en las elecciones
    en que fue en dos (2015 y nov. 2019): así se compara lista con lista."""
    p = {c: x for c, x in r['pct'].items() if c != 'OTROS' and x}
    b = r.get('sumar_b')
    if b and 'SUMAR' in p:
        p['SUMAR'] = max(p['SUMAR'] - b, b)
    return p


def ganador(r):
    p = pct_listas(r)
    # en un empate exacto, el orden de FAM (no el del diccionario) decide, para que el resultado no cambie
    return max(sorted(p, key=FAM.index), key=p.get) if p else None


# Nombre de la lista de la familia Sumar / Podemos / IU en cada elección desde 2004, y el de la segunda lista
# cuando fue en dos. Por provincia donde la candidatura tuvo otro nombre (Cataluña, Comunitat Valenciana, Galicia).
_CAT, _VAL, _GAL = ('08', '17', '25', '43'), ('03', '12', '46'), ('15', '27', '32', '36')
LISTA_SUMAR = {
    '2004_03': ('IU', {_CAT: 'ICV-EUiA'}), '2008_03': ('IU', {_CAT: 'ICV-EUiA'}), '2011_11': ('IU', {_CAT: 'ICV-EUiA', _VAL: 'EUPV'}),
    '2015_12': ('Podemos', {_CAT: 'En Comú Podem', _VAL: 'Compromís-Podemos', _GAL: 'En Marea'}),
    '2016_06': ('Unidos Podemos', {_CAT: 'En Comú Podem', _VAL: 'A la valenciana', _GAL: 'En Marea'}),
    '2019_04': ('Unidas Podemos', {_CAT: 'En Comú Podem', _VAL: 'Unides Podem', _GAL: 'En Común-Unidas Podemos'}),
    '2019_11': ('Unidas Podemos', {_CAT: 'En Comú Podem', _VAL: 'Unides Podem', _GAL: 'En Común-Unidas Podemos'}),
    '2023_07': ('Sumar', {}),
}
SEGUNDA_SUMAR = {'2011_11': ('Compromís-Q', {}), '2015_12': ('IU-Unidad Popular', {_VAL: 'EUPV-Unitat Popular'}),
                 '2019_04': ('Compromís', {}), '2019_11': ('Más País', {_VAL: 'Més Compromís'})}


def nota_separadas(serie, ys, prov=None):
    """Nota bajo la tabla: en qué elecciones la columna «Sumar / Podemos / IU» suma dos listas, y cuáles."""
    out = []
    for y in ys:
        r = serie.get(y)
        if r and r.get('sumar_b') and y in SEGUNDA_SUMAR:
            out.append(f'en {etiqueta(y)}, {_por_prov(LISTA_SUMAR, y, prov)} y {_por_prov(SEGUNDA_SUMAR, y, prov)}')
    if not out:
        return ''
    return ('«Sumar / Podemos / IU» suma dos listas que se presentaron por separado (' + '; '.join(out)
            + '); el más votado se calcula lista a lista.')


def _por_prov(tabla, y, prov):
    if y not in tabla:
        return None
    n, reg = tabla[y]
    return next((v for ps, v in reg.items() if prov in ps), n)


def nombre_ganador(r, y, prov=None):
    """Nombre de la lista más votada en esa elección: el de la familia, salvo Sumar / Podemos / IU desde 2004, que
    lleva el de la candidatura de ese año (Podemos, En Comú Podem, Unidas Podemos, Más País...)."""
    g = ganador(r)
    if g != 'SUMAR' or y not in LISTA_SUMAR:
        return nombre_familia(g, y) if g else None
    b = r.get('sumar_b')
    if b and b > r['pct']['SUMAR'] - b:
        return _por_prov(SEGUNDA_SUMAR, y, prov)
    return _por_prov(LISTA_SUMAR, y, prov)


def serie(df):
    return {y: resultado(df, y) for y in GENERALES}


def por_renta(sec, partes=5, minimo=8):
    """Secciones ordenadas por renta y agrupadas en `partes` grupos con el mismo censo (quintiles por defecto).
    Sin resultado si no hay al menos `minimo` secciones por grupo."""
    s = sec[sec.renta_uc.notna() & (sec.censo > 0)].sort_values('renta_uc').copy()
    if len(s) < partes * minimo:
        return None
    acum = s.censo.cumsum() / s.censo.sum()
    s['q'] = (acum * partes).clip(upper=partes - 1e-9).astype(int)
    out = []
    for q, g in s.groupby('q'):
        val = (g.candidaturas + g.blancos).sum()
        out.append({'q': q + 1, 'desde': g.renta_uc.min(), 'hasta': g.renta_uc.max(), 'secciones': len(g),
                    'part': g.votantes.sum() / g.censo.sum(), 'pct': {c: g[c].sum() / val for c in FAM}})
    return out


ESPANA = resultado(MUN, ULTIMA)
