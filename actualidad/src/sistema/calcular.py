"""Cifras de las piezas sobre el sistema electoral (precio del escaño, voto perdido) con los resultados por mesa
de Interior (vía pollspaindata), voto exterior (CERA) incluido.

Uso, desde la raíz del repositorio: python3 actualidad/src/sistema/calcular.py
Escribe actualidad/src/sistema/cifras.json (lo que citan los textos) y simulador.json (los votos que usa el simulador).
Variables de entorno:
  GENERALES_CACHE  carpeta con el clon de dadosdelaplace/pollspaindata (por defecto ~/.cache/generales)
  PARTIDOS_PY      carpeta con partidos.py de la pieza de las generales (por defecto /mnt/project-files/generales)
"""
import json, os, pathlib, sys
import pandas as pd

AQUI = pathlib.Path(__file__).resolve().parent
CACHE = pathlib.Path(os.environ.get('GENERALES_CACHE', os.path.expanduser('~/.cache/generales')))
RAW = CACHE / 'pollspaindata' / 'inst' / 'extdata'
sys.path.insert(0, os.environ.get('PARTIDOS_PY', '/mnt/project-files/generales'))
from partidos import familia  # noqa: E402

ESC = {
    '2023_07': {'01': 4, '02': 4, '03': 12, '04': 6, '05': 3, '06': 5, '07': 8, '08': 32, '09': 4, '10': 4, '11': 9, '12': 5,
                '13': 5, '14': 6, '15': 8, '16': 3, '17': 6, '18': 7, '19': 3, '20': 6, '21': 5, '22': 3, '23': 5, '24': 4,
                '25': 4, '26': 4, '27': 4, '28': 37, '29': 11, '30': 10, '31': 5, '32': 4, '33': 7, '34': 3, '35': 8, '36': 7,
                '37': 4, '38': 7, '39': 5, '40': 3, '41': 12, '42': 2, '43': 6, '44': 3, '45': 6, '46': 16, '47': 5, '48': 8,
                '49': 3, '50': 7, '51': 1, '52': 1},
}
# 2019: Valencia 15 y Badajoz 6 (en 2023 Valencia ganó el escaño que perdió Badajoz); 2026: Madrid 38, Cádiz 8 (Real Decreto 806/2026)
ESC['2019_11'] = {**ESC['2023_07'], '46': 15, '06': 6}
ESC['2026'] = {**ESC['2023_07'], '28': 38, '11': 8}
PROV = {'01': 'Álava', '02': 'Albacete', '03': 'Alicante', '04': 'Almería', '05': 'Ávila', '06': 'Badajoz', '07': 'Illes Balears',
        '08': 'Barcelona', '09': 'Burgos', '10': 'Cáceres', '11': 'Cádiz', '12': 'Castellón', '13': 'Ciudad Real', '14': 'Córdoba',
        '15': 'A Coruña', '16': 'Cuenca', '17': 'Girona', '18': 'Granada', '19': 'Guadalajara', '20': 'Gipuzkoa', '21': 'Huelva',
        '22': 'Huesca', '23': 'Jaén', '24': 'León', '25': 'Lleida', '26': 'La Rioja', '27': 'Lugo', '28': 'Madrid', '29': 'Málaga',
        '30': 'Murcia', '31': 'Navarra', '32': 'Ourense', '33': 'Asturias', '34': 'Palencia', '35': 'Las Palmas', '36': 'Pontevedra',
        '37': 'Salamanca', '38': 'Santa Cruz de Tenerife', '39': 'Cantabria', '40': 'Segovia', '41': 'Sevilla', '42': 'Soria',
        '43': 'Tarragona', '44': 'Teruel', '45': 'Toledo', '46': 'Valencia', '47': 'Valladolid', '48': 'Bizkaia', '49': 'Zamora',
        '50': 'Zaragoza', '51': 'Ceuta', '52': 'Melilla'}
CCAA = {'Andalucía': '04 11 14 18 21 23 29 41', 'Aragón': '22 44 50', 'Asturias': '33', 'Illes Balears': '07', 'Canarias': '35 38',
        'Cantabria': '39', 'Castilla y León': '05 09 24 34 37 40 42 47 49', 'Castilla-La Mancha': '02 13 16 19 45',
        'Cataluña': '08 17 25 43', 'Comunitat Valenciana': '03 12 46', 'Extremadura': '06 10', 'Galicia': '15 27 32 36',
        'Madrid': '28', 'Murcia': '30', 'Navarra': '31', 'País Vasco': '01 20 48', 'La Rioja': '26', 'Ceuta': '51', 'Melilla': '52'}
CCAA_DE = {p: c for c, ps in CCAA.items() for p in ps.split()}
ETIQ = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'SUMAR': 'Sumar', 'CS': 'Cs', 'ERC': 'ERC', 'JUNTS': 'Junts', 'PNV': 'PNV',
        'BILDU': 'EH Bildu', 'BNG': 'BNG', 'CC': 'CC', 'UPYD': 'UPyD'}


# Nombre corto de las listas pequeñas que aparecen en los gráficos
NOMBRES = {'SY': 'Soria ¡Ya!', 'U.P.L.': 'UPL', 'XAV': 'Por Ávila', 'VB': 'Vía Burgalesa', 'CPM': 'Coalición por Melilla',
           'CUP-PR': 'CUP', 'FO': 'Frente Obrero', 'PDECAT-E-CIU': 'PDeCAT', 'GBAI': 'Geroa Bai', 'ESPAÑA VACIADA': 'España Vaciada',
           'JM+': 'Jaén Merece Más', 'ZSI': 'Zamora Sí', 'VP': 'Vamos Palencia', 'XH': 'Por Huelva', 'BQEX': 'Bloque Extremeño',
           'PREPAL': 'PREPAL', 'NC-BC': 'Nueva Canarias', 'NCa': 'Nueva Canarias', 'RECORTES CERO-GV': 'Recortes Cero', 'RECORTES CERO': 'Recortes Cero', 'Más País': 'Más País'}


def partido(abrev, nombre, anyo):
    p = _partido(abrev, nombre, anyo)
    return NOMBRES.get(p, p)


def _partido(abrev, nombre, anyo):
    a = abrev.strip().upper()
    if a in ('U.P.N.', 'UPN'):
        return 'UPN'
    if a in ('NA+',):
        return 'NA+'
    if 'EXISTE' in a or 'TERUEL EXI' in a:
        return 'Teruel Existe' if 'TERUEL' in nombre.upper() or 'TERUEL' in a else 'Existe'
    if anyo == '2019_11' and ('MÁS PAÍS' in nombre.upper() or 'MÁS PAÍS' in a or 'MÉS COMPROMÍS' in a or a.startswith('MÉS COMPROM')):
        return 'Más País'
    if anyo == '2019_11' and 'COMPROM' in nombre.upper():
        return 'Más País'
    f = familia(abrev, nombre)
    if f == 'SUMAR' and anyo == '2019_11':
        return 'Unidas Podemos'
    if f in ETIQ:
        return ETIQ[f]
    if 'PACMA' in a or 'ANIMALISTA' in nombre.upper():
        return 'PACMA'
    if 'BLANCO' in a or 'BLANC' in a:
        return 'Escaños en Blanco'
    if a.startswith('PUM+J'):
        return 'PUM+J'
    if a.startswith('PCTE') or a in ('PCTC', 'PCTG'):
        return 'PCTE'
    return abrev.strip()


def cargar(e):
    m = pd.read_parquet(RAW / f'raw_poll_stations_congress_{e}.parquet')
    c = pd.read_parquet(RAW / f'raw_candidacies_congress_{e}.parquet')
    v = pd.read_parquet(RAW / f'raw_candidacies_poll_congress_{e}.parquet')
    c['partido'] = [partido(a, n, e) for a, n in zip(c.abbrev_candidacies, c.name_candidacies)]
    vot = v.groupby(['cod_INE_prov', 'id_candidacies']).ballots.sum().reset_index().merge(c[['id_candidacies', 'partido']], on='id_candidacies')
    vot = vot.groupby(['cod_INE_prov', 'partido']).ballots.sum().reset_index()
    mm = m.assign(cera=m.cod_INE_mun == '999')
    prov = mm.groupby('cod_INE_prov').agg(censo=('census_counting', 'sum'), blancos=('blank_ballots', 'sum'),
                                          nulos=('invalid_ballots', 'sum'), candidaturas=('party_ballots', 'sum'))
    prov['censo_cera'] = mm[mm.cera].groupby('cod_INE_prov').census_counting.sum()
    prov['validos'] = prov.candidaturas + prov.blancos
    return vot, prov


def dhondt(votos, n, valido, barrera=0.03):
    """votos: dict partido -> votos. Devuelve escaños, último cociente y votos que faltaban a cada lista."""
    ok = {p: b for p, b in votos.items() if b >= barrera * valido}
    coc = sorted(((b / d, p) for p, b in ok.items() for d in range(1, n + 1)), reverse=True)
    esc = {}
    for _, p in coc[:n]:
        esc[p] = esc.get(p, 0) + 1
    return esc, coc[n - 1]


def margen(votos, esc, ult_coc, ult):
    """Votos que le faltaban al aspirante más cercano para quitar el último escaño, sin que nadie más cambie
    (mismo cálculo que atlas/src/construir.py y la pieza «El último escaño»)."""
    falta = {p: int(ult_coc * (esc.get(p, 0) + 1) - b) + 1 for p, b in votos.items() if p != ult}
    falta = {p: f for p, f in falta.items() if f > 0}
    asp = min(falta, key=falta.get)
    return asp, falta[asp]


def main():
    out, sim = {}, {'provincias': PROV, 'ccaa': CCAA, 'escanos': ESC, 'elecciones': {}}
    for e in ['2023_07', '2019_11']:
        vot, prov = cargar(e)
        R = {}
        nac_votos, nac_esc, perdido_p = {}, {}, {}
        for p, g in vot.groupby('cod_INE_prov'):
            vv = dict(zip(g.partido, g.ballots.astype(int)))
            valido = int(prov.loc[p, 'validos'])
            esc, (ult_coc, ult) = dhondt(vv, ESC[e][p], valido)
            sin_esc = {k: b for k, b in vv.items() if k not in esc}
            perd = sum(sin_esc.values())
            ok = {k: b for k, b in vv.items() if b >= 0.03 * valido}
            asp, falta = margen(ok, esc, ult_coc, ult)
            # votos que hacen falta para el primer escaño de cada lista sin escaño (sin que nadie más cambie)
            R[p] = {'nombre': PROV[p], 'ccaa': CCAA_DE[p], 'escanos': ESC[e][p], 'censo': int(prov.loc[p, 'censo']),
                    'censo_cera': int(prov.loc[p, 'censo_cera']), 'validos': valido,
                    'votos_candidaturas': int(prov.loc[p, 'candidaturas']), 'blancos': int(prov.loc[p, 'blancos']),
                    'censo_residentes': int(prov.loc[p, 'censo'] - prov.loc[p, 'censo_cera']),
                    'residentes_por_escano': round(int(prov.loc[p, 'censo'] - prov.loc[p, 'censo_cera']) / ESC[e][p]),
                    'esc': esc, 'ultimo': ult, 'aspirante': asp, 'votos_faltan': falta, 'ultimo_cociente': round(ult_coc, 1),
                    'votos_sin_escano': perd, 'pct_sin_escano': round(100 * perd / valido, 3),
                    'pct_sin_escano_mas_blanco': round(100 * (perd + int(prov.loc[p, 'blancos'])) / valido, 2),
                    'perdidos_por_partido': dict(sorted(sin_esc.items(), key=lambda x: -x[1])),
                    'umbral_efectivo_pct': round(100 * ult_coc / valido, 2),
                    'votos_por_escano': round(valido / ESC[e][p]), 'electores_por_escano': round(int(prov.loc[p, 'censo']) / ESC[e][p])}
            for k, b in vv.items():
                nac_votos[k] = nac_votos.get(k, 0) + b
                if k in sin_esc:
                    perdido_p[k] = perdido_p.get(k, 0) + b
            for k, s in esc.items():
                nac_esc[k] = nac_esc.get(k, 0) + s
        tot_val = sum(r['validos'] for r in R.values())
        tot_cand = sum(nac_votos.values())
        partidos = []
        for k, b in sorted(nac_votos.items(), key=lambda x: -x[1]):
            s = nac_esc.get(k, 0)
            partidos.append({'partido': k, 'votos': b, 'pct': round(100 * b / tot_val, 2), 'escanos': s,
                             'pct_escanos': round(100 * s / 350, 2), 'votos_por_escano': round(b / s) if s else None,
                             'votos_sin_escano': perdido_p.get(k, 0), 'pct_propio_sin_escano': round(100 * perdido_p.get(k, 0) / b, 1)})
        # las circunscripciones de cinco escaños o menos frente al resto
        peq = [q for q in R if R[q]['escanos'] <= 5]
        vpeq = vot[vot.cod_INE_prov.isin(peq)].groupby('partido').ballots.sum()
        valpeq = sum(R[q]['validos'] for q in peq)
        pequenas = {'n': len(peq), 'escanos': sum(R[q]['escanos'] for q in peq),
                    'pct_residentes': round(100 * sum(R[q]['censo_residentes'] for q in peq) / sum(r['censo_residentes'] for r in R.values()), 1),
                    'partidos': {k: {'pct_voto': round(100 * float(vpeq.get(k, 0)) / valpeq, 1),
                                     'escanos': sum(R[q]['esc'].get(k, 0) for q in peq)} for k in vpeq.sort_values(ascending=False).index[:8]}}
        out[e] = {'pequenas': pequenas, 'blancos': sum(r['blancos'] for r in R.values()), 'provincias': R, 'partidos': partidos, 'validos': tot_val, 'votos_candidaturas': tot_cand,
                  'votos_sin_escano': sum(perdido_p.values()), 'pct_sin_escano': round(100 * sum(perdido_p.values()) / tot_val, 2),
                  'censo': sum(r['censo'] for r in R.values())}
        # Simulador: votos por provincia de las listas con al menos 0,1 % en España o con escaño; el resto, «Otros»
        grandes = {q['partido'] for q in partidos if q['pct'] >= 0.1 or q['escanos']}
        sp = {}
        for p, g in vot.groupby('cod_INE_prov'):
            d = {}
            for k, b in zip(g.partido, g.ballots.astype(int)):
                kk = k if k in grandes else 'Otros'
                d[kk] = d.get(kk, 0) + int(b)
            sp[p] = {'v': d, 'validos': R[p]['validos']}
        sim['elecciones'][e] = sp
    # 2026: los votos de 2023 con el reparto de 2026 (Madrid 38, Cádiz 8): mecánico, no previsión
    vot, prov = cargar('2023_07')
    alt = {}
    for p, g in vot.groupby('cod_INE_prov'):
        esc, _ = dhondt(dict(zip(g.partido, g.ballots)), ESC['2026'][p], int(prov.loc[p, 'validos']))
        for k, s in esc.items():
            alt[k] = alt.get(k, 0) + s
    out['votos_2023_reparto_2026'] = alt
    # 2015: el caso de IU-Unidad Popular (2 escaños) frente al PP, para contrastar la cita de Alberto Garzón
    c = pd.read_parquet(RAW / 'raw_candidacies_congress_2015_12.parquet')
    v = pd.read_parquet(RAW / 'raw_candidacies_poll_congress_2015_12.parquet')
    iu = c[c.name_candidacies.str.contains('UNIDAD POPULAR|UNITAT POPULAR', case=False)].id_candidacies
    pp = c[[familia(a, n) == 'PP' for a, n in zip(c.abbrev_candidacies, c.name_candidacies)]].id_candidacies
    out['2015_12'] = {'iu_up_votos': int(v[v.id_candidacies.isin(iu)].ballots.sum()), 'iu_up_escanos': 2,
                      'pp_votos': int(v[v.id_candidacies.isin(pp)].ballots.sum()), 'pp_escanos': 123}
    json.dump(out, open(AQUI / 'cifras.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(sim, open(AQUI / 'simulador.json', 'w'), ensure_ascii=False, separators=(',', ':'))


if __name__ == '__main__':
    main()
