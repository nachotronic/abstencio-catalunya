"""Importa municipales y europeas de Infoelectoral (Ministerio del Interior) para el mapa.

Uso:  python3 otras_elecciones.py 04202305_MESA.zip 07202406_MESA.zip 04200705_MUNI.zip ...
      python3 construir.py && python3 pagina.py

Los zips son los de infoelectoral.interior.gob.es > Área de descargas. El nombre dice qué son:
TTAAAAMM_MESA.zip (TT = 04 municipales, 07 europeas; MESA = por mesa, MUNI = por municipio).

- Con el fichero por mesa (09 y 10) la elección queda por sección censal. Los municipios de menos de
  250 habitantes votan en las municipales con listas abiertas y solo vienen por municipio (11 y 12);
  se asignan a la sección 01-001 del municipio, que en casi todos es la única.
- Con el fichero por municipio (05 y 06, y 11 y 12) queda solo por municipio.
- El censo de las municipales y europeas suma el de españoles (INE) y el de residentes de la UE con
  derecho a voto (CERE), porque los votantes incluyen a ambos.
- El CERA (código de municipio 999) se deja fuera, como en las generales.

Salida en datos/extra/: raw_*_{cod}.parquet (por mesa) o {cod}_municipios.csv (por municipio),
con cod = M2023 (municipales) o E2024 (europeas).
Posiciones de los registros según FICHEROS.doc, que viene dentro de cada zip.
"""
import io, os, re, sys, zipfile
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
EXTRA = os.path.join(AQUI, 'datos', 'extra')
TIPOS = {'04': 'M', '07': 'E'}


def _campos(lineas, pos, cols):
    return pd.DataFrame([[l[a - 1:b].strip() for a, b in pos] for l in lineas if l.strip()], columns=cols)


def _num(d, cols):
    for c in cols:
        d[c] = pd.to_numeric(d[c])
    return d


def importa(path):
    nombre = os.path.basename(path).upper()
    m = re.search(r'(0[47])(\d{4})(\d{2})_(MESA|MUNI)', nombre)
    if not m:
        sys.exit(f'{nombre}: no parece un zip de Infoelectoral (TTAAAAMM_MESA.zip o _MUNI.zip)')
    tipo, anyo, _, nivel = m.groups()
    cod = TIPOS[tipo] + anyo
    z = zipfile.ZipFile(path)
    # 0504.., 0604..: ámbito municipal; 0510.. son diputaciones y no sirven aquí
    fich = {n[:2]: n for n in z.namelist() if n.upper().endswith('.DAT') and n[2:4] == tipo}
    lee = lambda k: io.TextIOWrapper(z.open(fich[k]), encoding='latin-1').read().splitlines() if k in fich else []

    cand = _campos(lee('03'), [(9, 14), (15, 64), (65, 214)], ['id_candidacies', 'abbrev_candidacies', 'name_candidacies'])
    os.makedirs(EXTRA, exist_ok=True)

    # municipios de menos de 250 habitantes (municipales): totales (11) y votos por candidatura (12)
    p11 = [(12, 13), (14, 16), (131, 133), (137, 139), (149, 151), (152, 154), (155, 157)]
    peq = _num(_campos(lee('11'), p11, ['prov', 'mun', 'censo', 'cere', 'blancos', 'nulos', 'candidaturas']),
               ['censo', 'cere', 'blancos', 'nulos', 'candidaturas'])
    pv = _campos(lee('12'), [(10, 11), (12, 14), (15, 20), (21, 23)], ['prov', 'mun', 'id_candidacies', 'votos'])
    pv = _num(pv.drop_duplicates(['prov', 'mun', 'id_candidacies']), ['votos'])   # una fila por candidato

    if nivel == 'MESA':
        p09 = [(12, 13), (14, 16), (17, 18), (19, 22), (23, 23), (24, 30), (38, 44), (66, 72), (73, 79), (80, 86)]
        ms = _campos(lee('09'), p09, ['cod_INE_prov', 'cod_INE_mun', 'cod_mun_district', 'cod_sec', 'cod_poll_station',
                                      'census_INE', 'census_CERE', 'blank_ballots', 'invalid_ballots', 'party_ballots'])
        v = _campos(lee('10'), [(12, 13), (14, 16), (17, 18), (19, 22), (23, 23), (24, 29), (30, 36)],
                    ['cod_INE_prov', 'cod_INE_mun', 'cod_mun_district', 'cod_sec', 'cod_poll_station', 'id_candidacies', 'ballots'])
        _num(ms, ['census_INE', 'census_CERE', 'blank_ballots', 'invalid_ballots', 'party_ballots'])
        ms['census_INE'] += ms.pop('census_CERE')
        _num(v, ['ballots'])
        if len(peq):
            b = dict(cod_mun_district='01', cod_sec='0001', cod_poll_station='U')
            ms = pd.concat([ms, pd.DataFrame(dict(cod_INE_prov=peq.prov, cod_INE_mun=peq.mun, **b, census_INE=peq.censo + peq.cere,
                                                  blank_ballots=peq.blancos, invalid_ballots=peq.nulos, party_ballots=peq.candidaturas))])
            v = pd.concat([v, pd.DataFrame(dict(cod_INE_prov=pv.prov, cod_INE_mun=pv.mun, **b, id_candidacies=pv.id_candidacies, ballots=pv.votos))])
        for d in (ms, v):
            d['cod_sec'] = d.cod_sec.str.zfill(4).str[-3:]
        ms.reset_index(drop=True).to_parquet(os.path.join(EXTRA, f'raw_poll_stations_{cod}.parquet'))
        v.reset_index(drop=True).to_parquet(os.path.join(EXTRA, f'raw_candidacies_poll_{cod}.parquet'))
        cand.to_parquet(os.path.join(EXTRA, f'raw_candidacies_{cod}.parquet'))
        ms = ms[ms.cod_INE_mun != '999']
        print(f'{cod}: {len(ms):,} mesas ({len(peq):,} municipios pequeños), {len(cand):,} candidaturas, '
              f'censo {ms.census_INE.sum():,.0f}, votantes {ms[["blank_ballots", "invalid_ballots", "party_ballots"]].sum().sum():,.0f}')
    else:
        p05 = [(12, 13), (14, 16), (17, 18), (142, 149), (158, 165), (190, 197), (198, 205), (206, 213)]
        t = _campos(lee('05'), p05, ['prov', 'mun', 'dist', 'censo', 'cere', 'blancos', 'nulos', 'candidaturas'])
        t = _num(t[t.dist == '99'].drop(columns='dist'), ['censo', 'cere', 'blancos', 'nulos', 'candidaturas'])
        v = _campos(lee('06'), [(10, 11), (12, 14), (15, 16), (17, 22), (23, 30)], ['prov', 'mun', 'dist', 'id_candidacies', 'votos'])
        v = _num(v[v.dist == '99'].drop(columns='dist'), ['votos'])
        t, v = pd.concat([t, peq]), pd.concat([v, pv])
        t['censo'] += t.pop('cere')
        t['votantes'] = t.blancos + t.nulos + t.candidaturas
        t['mun_code'] = t.prov + t.mun
        v['mun_code'] = v.prov + v.mun
        d = v.merge(cand, on='id_candidacies', how='left').merge(t[['mun_code', 'censo', 'votantes', 'blancos', 'nulos']], on='mun_code')
        assert d.abbrev_candidacies.notna().all()
        d = d[(d.mun.str[-3:] != '999') & (d.votos > 0)]
        d = d.rename(columns={'abbrev_candidacies': 'siglas', 'name_candidacies': 'nombre'})
        d = d[['mun_code', 'censo', 'votantes', 'blancos', 'nulos', 'siglas', 'nombre', 'votos']]
        d.to_csv(os.path.join(EXTRA, f'{cod}_municipios.csv'), index=False)
        print(f'{cod}: {d.mun_code.nunique():,} municipios (solo por municipio), {d.siglas.nunique():,} candidaturas, '
              f'censo {t.censo.sum():,.0f}, votantes {t.votantes.sum():,.0f}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        importa(p)
