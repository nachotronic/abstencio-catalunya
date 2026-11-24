"""Resultados de las generales por provincia y por comunidad (1982-2023), para el selector «Ver por» del mapa.

Uso:  python3 agregados_historicos.py <carpeta con los parquet de pollspaindata (inst/extdata)>
Escribe ../data/agregados.json con el mismo formato que los ámbitos PR y CM de Interior en el directo:
  {elección: {"PR": {prov: {n, esc, el, bl, c: [[siglas, votos, escaños, familia]]}}, "CM": {...}}}
Suma los votos mesa a mesa (microdatos de Interior vía dadosdelaplace/pollspaindata), con el voto desde el
extranjero (CERA) incluido, como los resultados oficiales de cada provincia. Sin escaños (0): no salen en el mapa.
La familia de cada lista es la de partidos.familia(), la misma del mapa por municipios.
"""
import json, os, sys
import pandas as pd
from partidos import familia, SIGLAS_PROPIAS

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, '..', 'data', 'agregados.json')
# comunidades con el código de Interior (el mismo de los ámbitos CM del directo, app.js CMPR)
CMPR = {'01': ['04', '11', '14', '18', '21', '23', '29', '41'], '02': ['22', '44', '50'], '03': ['33'], '04': ['07'],
        '05': ['35', '38'], '06': ['39'], '07': ['02', '13', '16', '19', '45'],
        '08': ['05', '09', '24', '34', '37', '40', '42', '47', '49'], '09': ['08', '17', '25', '43'], '10': ['06', '10'],
        '11': ['15', '27', '32', '36'], '12': ['28'], '13': ['31'], '14': ['01', '20', '48'], '15': ['30'], '16': ['26'],
        '17': ['03', '12', '46'], '18': ['51'], '19': ['52']}
PR2CM = {p: c for c, L in CMPR.items() for p in L}
# nombres de Interior (los de los ámbitos del directo)
NOMBRE = {'PR': {'01': 'Araba/Álava', '02': 'Albacete', '03': 'Alacant/Alicante', '04': 'Almería', '05': 'Ávila', '06': 'Badajoz', '07': 'Illes Balears', '08': 'Barcelona', '09': 'Burgos', '10': 'Cáceres', '11': 'Cádiz', '12': 'Castelló/Castellón', '13': 'Ciudad Real', '14': 'Córdoba', '15': 'A Coruña', '16': 'Cuenca', '17': 'Girona', '18': 'Granada', '19': 'Guadalajara', '20': 'Gipuzkoa', '21': 'Huelva', '22': 'Huesca', '23': 'Jaén', '24': 'León', '25': 'Lleida', '26': 'La Rioja', '27': 'Lugo', '28': 'Madrid', '29': 'Málaga', '30': 'Murcia', '31': 'Navarra', '32': 'Ourense', '33': 'Asturias', '34': 'Palencia', '35': 'Las Palmas', '36': 'Pontevedra', '37': 'Salamanca', '38': 'Santa Cruz de Tenerife', '39': 'Cantabria', '40': 'Segovia', '41': 'Sevilla', '42': 'Soria', '43': 'Tarragona', '44': 'Teruel', '45': 'Toledo', '46': 'València/Valencia', '47': 'Valladolid', '48': 'Bizkaia', '49': 'Zamora', '50': 'Zaragoza', '51': 'Ceuta', '52': 'Melilla'},
          'CM': {'01': 'Andalucía', '02': 'Aragón', '03': 'Principado de Asturias', '04': 'Illes Balears', '05': 'Canarias', '06': 'Cantabria', '07': 'Castilla-La Mancha', '08': 'Castilla y León', '09': 'Catalunya', '10': 'Extremadura', '11': 'Galicia', '12': 'Comunidad de Madrid', '13': 'Comunidad Foral de Navarra', '14': 'País Vasco', '15': 'Región de Murcia', '16': 'La Rioja', '17': 'Comunitat Valenciana', '18': 'Ciudad Autónoma de Ceuta', '19': 'Ciudad Autónoma de Melilla'}}
ELECCIONES = ['1982_10', '1986_06', '1989_10', '1993_06', '1996_03', '2000_03', '2004_03', '2008_03', '2011_11',
              '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']


def una(src, y):
    k = 'congress_' + y
    m = pd.read_parquet(f'{src}/raw_poll_stations_{k}.parquet')
    v = pd.read_parquet(f'{src}/raw_candidacies_poll_{k}.parquet')
    c = pd.read_parquet(f'{src}/raw_candidacies_{k}.parquet').drop_duplicates('id_candidacies')
    c['abbrev_candidacies'] = c.abbrev_candidacies.fillna(c.name_candidacies)   # alguna lista sin siglas en el origen
    # 2015: el voto CERA trae la candidatura como 9xxxxx en vez de 0xxxxx (comprobado: cae siempre en una lista de la misma provincia)
    fuera = ~v.id_candidacies.isin(set(c.id_candidacies))
    v.loc[fuera, 'id_candidacies'] = v.loc[fuera, 'id_candidacies'].str.replace(r'^9', '0', regex=True)
    # la misma candidatura en varias provincias de una comunidad (Interior la agrupa en id_candidacies_ccaa): en la comunidad
    # va en una sola fila aunque cada provincia escriba sus siglas a su manera (EAJ-PNV / E.A.J.-P.N.V. en 2011, PP / P.P.)
    c['grp'] = [str(int(float(x))) if pd.notna(x) else 'id' + i for x, i in zip(c.id_candidacies_ccaa, c.id_candidacies)]
    v = v.merge(c[['id_candidacies', 'abbrev_candidacies', 'name_candidacies', 'grp']], on='id_candidacies', how='left')
    assert v.abbrev_candidacies.notna().all(), y
    v['fam'] = [familia(a, n) for a, n in zip(v.abbrev_candidacies, v.name_candidacies)]
    # listas propias del 10N y el 23J (Existe, UPN, CUP...), con su color, como en el mapa por municipios
    prop = SIGLAS_PROPIAS.get(y, {})
    v['fam'] = [prop.get(a.strip().upper(), f) for a, f in zip(v.abbrev_candidacies, v.fam)]
    v['cm'] = v.cod_INE_prov.map(PR2CM); m['cm'] = m.cod_INE_prov.map(PR2CM)
    assert v.cm.notna().all() and m.cm.notna().all(), y
    # una candidatura, una familia en toda la comunidad: la de su provincia más votada (UC-CDS en 2000 o UPD/UPYD en 2008
    # caían en «Otros» en alguna provincia por cómo venía escrito el nombre)
    fv = v.groupby(['cm', 'grp', 'fam']).ballots.sum().reset_index().sort_values('ballots', ascending=False).drop_duplicates(['cm', 'grp'])
    v = v.drop(columns='fam').merge(fv[['cm', 'grp', 'fam']], on=['cm', 'grp'], how='left')
    out = {}
    for niv, col in (('PR', 'cod_INE_prov'), ('CM', 'cm')):
        bl = m.groupby(col).blank_ballots.sum()
        if niv == 'PR':
            g = v.groupby([col, 'abbrev_candidacies', 'fam']).ballots.sum().reset_index()
        else:   # por candidatura de Interior; siglas y familia, las de su provincia más votada
            pv = v.groupby([col, 'grp', 'cod_INE_prov', 'abbrev_candidacies', 'fam']).ballots.sum().reset_index()
            mix = pv[pv.ballots > 0].groupby([col, 'grp']).fam.nunique()
            for (t, gr) in mix[mix > 1].index:
                print('  aviso', y, t, gr, pv[(pv[col] == t) & (pv.grp == gr)][['abbrev_candidacies', 'fam', 'ballots']].values.tolist())
            top = pv.sort_values('ballots', ascending=False).drop_duplicates([col, 'grp'])[[col, 'grp', 'abbrev_candidacies', 'fam']]
            g = pv.groupby([col, 'grp']).ballots.sum().reset_index().merge(top, on=[col, 'grp'])
        d = {}
        for t, s in g.groupby(col):
            s = s.sort_values('ballots', ascending=False)
            filas = [[a.strip(), int(n), 0, f] for a, f, n in zip(s.abbrev_candidacies, s.fam, s.ballots) if n > 0]
            d[t] = {'n': NOMBRE[niv][t], 'esc': 100, 'el': 0, 'bl': int(bl.get(t, 0)), 'c': filas}
        out[niv] = d
    tot = sum(x[1] for o in out['PR'].values() for x in o['c'])
    print(y, 'votos a candidaturas', f'{tot:,}', 'CERA en los datos:', int((m.cod_INE_mun == '999').sum()), 'mesas')
    return out


def main():
    src = sys.argv[1]
    R = {y: una(src, y) for y in ELECCIONES}
    for y, o in R.items():
        assert sorted(o['PR']) == sorted(PR2CM) and sorted(o['CM']) == sorted(CMPR), y
        for c, L in CMPR.items():   # cada comunidad, la suma exacta de sus provincias
            assert sum(x[1] for x in o['CM'][c]['c']) == sum(x[1] for p in L for x in o['PR'][p]['c']), (y, c)
    # en el mapa caben 8 filas: las 10 primeras listas y el resto sumado POR FAMILIA (una fila por familia, con las siglas
    # de su lista más votada; las de «Otros», en «Otras»), para que cada familia sume lo mismo en la comunidad que en sus
    # provincias (antes, ~1.500 votos del PSOE andaluz de 1982 caían en «Otras» al recortar)
    def fam_tot(filas):
        t = {}
        for x in filas:
            t[x[3]] = t.get(x[3], 0) + x[1]
        return t
    antes = {y: {n: {k: fam_tot(t['c']) for k, t in o[n].items()} for n in ('PR', 'CM')} for y, o in R.items()}
    for o in R.values():
        for d in (o['PR'], o['CM']):
            for t in d.values():
                if len(t['c']) > 10:
                    resto = {}
                    for x in t['c'][10:]:
                        r = resto.setdefault(x[3], ['Otras' if x[3] == 'OTROS' else x[0], 0, 0, x[3]])
                        r[1] += x[1]
                    t['c'] = t['c'][:10] + sorted(resto.values(), key=lambda r: -r[1])
    for y, o in R.items():   # comprobación: ninguna familia cambia al recortar, y cada comunidad suma sus provincias familia a familia
        for n in ('PR', 'CM'):
            for k, t in o[n].items():
                assert fam_tot(t['c']) == antes[y][n][k], (y, n, k)
        for c, L in CMPR.items():
            suma = {}
            for p in L:
                for f, v in fam_tot(o['PR'][p]['c']).items():
                    suma[f] = suma.get(f, 0) + v
            assert fam_tot(o['CM'][c]['c']) == suma, (y, c)
    with open(SALIDA, 'w') as f:
        json.dump(R, f, ensure_ascii=False, separators=(',', ':'))
    print('->', SALIDA, os.path.getsize(SALIDA) // 1024, 'KB')


if __name__ == '__main__':
    main()
