"""Cifras de la pieza sobre las coaliciones de la izquierda a la izquierda del PSOE en las generales (2015-2023):
qué listas se presentaron en cada provincia, con qué votos y escaños, y el reparto D'Hondt que habría salido
sumando los votos de las listas que fueron por separado (2015 y las dos de 2019), con el resto de votos igual.

Uso, desde la raíz del repositorio: python3 actualidad/src/coaliciones/calcular.py
Escribe actualidad/src/coaliciones/datos.json. Mismas variables de entorno que actualidad/src/sistema/calcular.py.
"""
import json, pathlib, sys
import pandas as pd

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / 'sistema'))
from calcular import RAW, ESC, PROV, CCAA_DE, dhondt, familia  # noqa: E402

# 2015 y 2016: Madrid 36, Barcelona 31, Asturias 8, Valencia 16 y León 4 (en 2019: 37, 32, 7, 15 y 4)
ESC['2015_12'] = ESC['2016_06'] = {**ESC['2019_11'], '28': 36, '08': 31, '33': 8, '46': 16, '24': 4}
ESC['2019_04'] = ESC['2019_11']
ELECCIONES = ['2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
# Resto de partidos: por familia (el mismo criterio que el mapa de resultados)
FAM = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'CS': 'Cs', 'ERC': 'ERC', 'JUNTS': 'Junts', 'PNV': 'PNV', 'BILDU': 'EH Bildu',
       'BNG': 'BNG', 'CC': 'CC', 'UPYD': 'UPyD'}


def otro(abrev, nombre):
    a = abrev.strip().upper()
    if a in ('U.P.N.', 'UPN'):  # UPN sola (2023); en 2015 y 2016 iba en coalición con el PP y cuenta como PP
        return 'UPN'
    if a == 'NA+':
        return 'Navarra Suma'
    if 'TERUEL EXI' in a:
        return 'Teruel Existe'
    if a.startswith('CUP'):
        return 'CUP'
    if a == 'PRC':
        return 'PRC'
    return FAM.get(familia(abrev, nombre), abrev.strip())


def marca(abrev, nombre, e):
    """Lista de la izquierda a la izquierda del PSOE (o None si no lo es)."""
    a, n = abrev.upper(), nombre.upper()
    f = familia(abrev, nombre)
    if e == '2019_04' and a.startswith('COMPROM'):
        return 'Compromís'
    if e == '2019_04' and n == 'EN MAREA':
        return 'En Marea'
    if e == '2019_11' and ('MÁS PAÍS' in n or 'MÉS COMPROM' in n or a.startswith('M PAÍS')):
        return 'Más País'
    if f != 'SUMAR':
        return None
    if e == '2015_12':
        if 'UNIDAD POPULAR' in n or 'UNITAT POPULAR' in n:
            return 'IU-Unidad Popular'
        if 'EN COMÚ' in n:
            return 'En Comú Podem'
        if 'COMPROM' in n:
            return 'Compromís-Podemos'
        if 'MAREA' in n:
            return 'En Marea'
        return 'Podemos'
    if e == '2016_06':
        if 'EN COMÚ' in n:
            return 'En Comú Podem'
        if 'COMPROM' in n:
            return 'A la valenciana'
        if 'MAREA' in n:
            return 'En Marea'
        return 'Unidos Podemos'
    if e in ('2019_04', '2019_11'):
        return 'En Comú Podem' if 'EN COMÚ PODEM' in n else 'Unidas Podemos'
    return 'Sumar'


def main():
    out = {}
    for e in ELECCIONES:
        m = pd.read_parquet(RAW / f'raw_poll_stations_congress_{e}.parquet')
        c = pd.read_parquet(RAW / f'raw_candidacies_congress_{e}.parquet')
        v = pd.read_parquet(RAW / f'raw_candidacies_poll_congress_{e}.parquet')
        c['izq'] = [marca(a, n, e) for a, n in zip(c.abbrev_candidacies, c.name_candidacies)]
        c['partido'] = [i if isinstance(i, str) else otro(a, n) for i, a, n in zip(c.izq, c.abbrev_candidacies, c.name_candidacies)]
        vot = v.groupby(['cod_INE_prov', 'id_candidacies']).ballots.sum().reset_index().merge(
            c[['id_candidacies', 'partido', 'izq', 'name_candidacies']], on='id_candidacies')
        val = m.groupby('cod_INE_prov').apply(lambda g: int(g.party_ballots.sum() + g.blank_ballots.sum()))
        P, real, junt = {}, {}, {}
        for p, g in vot.groupby('cod_INE_prov'):
            vv = g.groupby('partido').ballots.sum().astype(int).to_dict()
            n, valido = ESC[e][p], int(val[p])
            esc, _ = dhondt(vv, n, valido)
            izq = g[g.izq.notna()].groupby(['izq', 'name_candidacies']).ballots.sum().astype(int).reset_index().sort_values('ballots', ascending=False)
            listas = [{'marca': r.izq, 'nombre': r.name_candidacies.strip('" '), 'votos': int(r.ballots), 'pct': round(100 * r.ballots / valido, 2),
                       'esc': int(esc.get(r.izq, 0))} for r in izq.itertuples()]
            # Juntos: los votos de todas las listas del espacio en una sola papeleta, el resto igual
            vj = {k: b for k, b in vv.items() if k not in set(izq.izq)}
            vj['Juntos'] = int(izq.ballots.sum())
            ej, _ = dhondt(vj, n, valido)
            P[p] = {'prov': PROV[p], 'ccaa': CCAA_DE[p], 'escanos': n, 'validos': valido, 'listas': listas,
                    'suma_pct': round(100 * izq.ballots.sum() / valido, 2), 'esc_real': sum(l['esc'] for l in listas),
                    'esc_juntos': int(ej.get('Juntos', 0)),
                    # a quién se lo quita (o a quién se lo da) la suma
                    'cambio': {k: ej.get(k, 0) - esc.get(k, 0) for k in set(esc) | set(ej) if k not in set(izq.izq) and k != 'Juntos' and ej.get(k, 0) != esc.get(k, 0)}}
            for k, s in esc.items():
                real[k] = real.get(k, 0) + s
            for k, s in ej.items():
                junt[k] = junt.get(k, 0) + s
        tot = vot.groupby('partido').ballots.sum().astype(int)
        part = round(100 * (m.party_ballots.sum() + m.blank_ballots.sum() + m.invalid_ballots.sum()) / m.census_counting.sum(), 2)  # con CERA
        out[e] = {'participacion': part, 'provincias': P, 'esc_real': real, 'esc_juntos': junt, 'votos': {k: int(b) for k, b in tot.items() if b > 20000 or k in real},
                  'validos': int(val.sum())}
        izqs = sorted(set(vot.izq.dropna()))
        print(e, {k: real.get(k, 0) for k in izqs}, 'juntos', junt.get('Juntos'), 'votos', {k: int(tot[k]) for k in izqs},
              {k: s for k, s in sorted(real.items(), key=lambda x: -x[1]) if k not in izqs})
    json.dump(out, open(AQUI / 'datos.json', 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
