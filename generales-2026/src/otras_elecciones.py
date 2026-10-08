"""Importa elecciones de Infoelectoral (Ministerio del Interior) para el mapa: municipales, europeas y generales.

Uso:  python3 otras_elecciones.py 04202305_MESA.zip 07202406_MESA.zip 04200705_MUNI.zip 02197706_MUNI.zip ...
      python3 otras_elecciones.py --pollspaindata ~/.cache/generales/pollspaindata/inst/extdata   (Congreso 1986-2000)
      python3 construir.py && python3 pagina.py

Los zips son los de infoelectoral.interior.gob.es > Área de descargas. El nombre dice qué son:
TTAAAAMM_MESA.zip (TT = 02 Congreso, 04 municipales, 07 europeas; MESA = por mesa, MUNI = por municipio).

- Elecciones anteriores a 2004: aunque haya fichero por mesa, en el mapa van solo por municipio, porque las
  secciones de entonces no se corresponden con las de 2023 aunque conserven el código. Los resultados por
  sección con el código de su época se guardan en datos/historico/secciones_{cod}.csv.gz.

- Con el fichero por mesa (09 y 10) la elección queda por sección censal. Los municipios de menos de
  250 habitantes votan en las municipales con listas abiertas y solo vienen por municipio (11 y 12);
  se asignan a la sección 01-001 del municipio, que en casi todos es la única.
- Con el fichero por municipio (05 y 06, y 11 y 12) queda solo por municipio.
- El censo de las municipales y europeas suma el de españoles (INE) y el de residentes de la UE con
  derecho a voto (CERE), porque los votantes incluyen a ambos.
- El CERA (código de municipio 999) se deja fuera, como en las generales.

Salida en datos/extra/: raw_*_{cod}.parquet (por mesa) o {cod}_municipios.csv (por municipio),
con cod = M2023 (municipales), E2024 (europeas) o 1977_06 (Congreso, año_mes).
Posiciones de los registros según FICHEROS.doc, que viene dentro de cada zip.
"""
import io, os, re, sys, zipfile
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
EXTRA = os.path.join(AQUI, 'datos', 'extra')
HIST = os.path.join(AQUI, 'datos', 'historico')
TIPOS = {'02': 'G', '04': 'M', '07': 'E'}
CORTE = 2004   # antes, solo por municipio en el mapa


def _campos(lineas, pos, cols):
    return pd.DataFrame([[l[a - 1:b].strip() for a, b in pos] for l in lineas if l.strip()], columns=cols)


def _num(d, cols):
    for c in cols:
        x = pd.to_numeric(d[c], errors='coerce')
        if x.isna().any():     # registros mal formados en el origen (p. ej. Salas de Bureba, municipales de 1991)
            print(f'  aviso: {int(x.isna().sum())} valor(es) ilegibles en {c}:', d.loc[x.isna()].iloc[:3, :3].values.tolist())
        d[c] = x
    return d


def importa(path):
    nombre = os.path.basename(path).upper()
    m = re.search(r'(0[247])(\d{4})(\d{2})_(MESA|MUNI)', nombre)
    if not m:
        sys.exit(f'{nombre}: no parece un zip de Infoelectoral (TTAAAAMM_MESA.zip o _MUNI.zip)')
    tipo, anyo, mes, nivel = m.groups()
    cod = f'{anyo}_{mes}' if tipo == '02' else TIPOS[tipo] + anyo
    viejo = int(anyo) < CORTE
    z = zipfile.ZipFile(path)
    # 0504.., 0604..: ámbito municipal; 0510.. son diputaciones y no sirven aquí
    fich = {os.path.basename(n)[:2]: n for n in z.namelist() if n.upper().endswith('.DAT') and os.path.basename(n)[2:4] == tipo}
    lee = lambda k: io.TextIOWrapper(z.open(fich[k]), encoding='latin-1').read().splitlines() if k in fich else []

    cand = _campos(lee('03'), [(9, 14), (15, 64), (65, 214)], ['id_candidacies', 'abbrev_candidacies', 'name_candidacies'])
    os.makedirs(EXTRA, exist_ok=True)

    # municipios de menos de 250 habitantes (municipales): totales (11) y votos por candidatura (12)
    p11 = [(12, 13), (14, 16), (131, 133), (137, 139), (149, 151), (152, 154), (155, 157)]
    peq = _num(_campos(lee('11'), p11, ['prov', 'mun', 'censo', 'cere', 'blancos', 'nulos', 'candidaturas']),
               ['censo', 'cere', 'blancos', 'nulos', 'candidaturas'])
    pv = _campos(lee('12'), [(10, 11), (12, 14), (15, 20), (21, 23)], ['prov', 'mun', 'id_candidacies', 'votos'])
    pv = _num(pv.drop_duplicates(['prov', 'mun', 'id_candidacies']), ['votos'])   # una fila por candidato

    if nivel == 'MESA' and not any(l.strip() for l in lee('09')):
        nivel = 'MUNI'        # zips de mesa sin mesas (Congreso 1977 y 1979): traen también los ficheros por municipio
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
        if viejo:
            return guarda_viejo(cod, ms, v, cand, set(peq.prov + peq.mun))
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


def a_municipios(ms, v, cand, peq=()):
    """Mesas -> formato largo por municipio (el de M2007_municipios.csv)."""
    for d in (ms, v):
        d['mun_code'] = d.cod_INE_prov + d.cod_INE_mun
    ms = ms[ms.cod_INE_mun != '999']
    t = ms.groupby('mun_code')[['census_INE', 'blank_ballots', 'invalid_ballots', 'party_ballots']].sum()
    t.columns = ['censo', 'blancos', 'nulos', 'candidaturas']
    t['votantes'] = t.blancos + t.nulos + t.candidaturas
    vv = v[v.cod_INE_mun != '999'].groupby(['mun_code', 'id_candidacies']).ballots.sum().rename('votos').reset_index()
    d = vv.merge(cand.drop_duplicates('id_candidacies'), on='id_candidacies', how='left').merge(t.reset_index(), on='mun_code')
    assert d.abbrev_candidacies.notna().all()
    # municipios cuyos votos por candidatura no suman lo que dice la mesa (en los ficheros de Interior de 1986-2003 falta la
    # primera mesa de algunas provincias): su reparto de voto queda sin dato en el mapa
    dif = (t.candidaturas - vv.groupby('mun_code').votos.sum().reindex(t.index).fillna(0)).abs()
    inc = (dif > (t.votantes * .01).clip(lower=5)) & ~t.index.isin(peq)   # listas abiertas (<250 hab.): votos por candidato, no suman papeletas
    if inc.any():
        print(f'  aviso: {int(inc.sum())} municipios con votos por candidatura incompletos:', ', '.join(t.index[inc][:10]))
    d['incompleto'] = d.mun_code.map(inc).fillna(False).astype(int)
    d = d[d.votos > 0].rename(columns={'abbrev_candidacies': 'siglas', 'name_candidacies': 'nombre'})
    return d[['mun_code', 'censo', 'votantes', 'blancos', 'nulos', 'siglas', 'nombre', 'votos', 'incompleto']], t


def guarda_viejo(cod, ms, v, cand, peq=()):
    """Elección anterior a 2004 con fichero por mesa: municipio para el mapa, sección (código de la época) aparte."""
    d, t = a_municipios(ms, v, cand, peq)
    d.to_csv(os.path.join(EXTRA, f'{cod}_municipios.csv'), index=False)
    os.makedirs(HIST, exist_ok=True)
    k = ['cod_INE_prov', 'cod_INE_mun', 'cod_mun_district', 'cod_sec']
    ms, v = ms[ms.cod_INE_mun != '999'], v[v.cod_INE_mun != '999']
    s = ms.groupby(k)[['census_INE', 'blank_ballots', 'invalid_ballots', 'party_ballots']].sum()
    s.columns = ['censo', 'blancos', 'nulos', 'candidaturas']
    sv = v.groupby(k + ['id_candidacies']).ballots.sum().rename('votos').reset_index()
    sv = sv[sv.votos > 0].merge(cand.drop_duplicates('id_candidacies'), on='id_candidacies', how='left').merge(s.reset_index(), on=k)
    sv['seccion'] = sv.cod_INE_prov + sv.cod_INE_mun + sv.cod_mun_district + sv.cod_sec.str.zfill(3)
    sv = sv.rename(columns={'abbrev_candidacies': 'siglas', 'name_candidacies': 'nombre'})
    sv[['seccion', 'censo', 'blancos', 'nulos', 'candidaturas', 'siglas', 'nombre', 'votos']].to_csv(
        os.path.join(HIST, f'secciones_{cod}.csv.gz'), index=False)
    print(f'{cod}: {len(ms):,} mesas, {s.shape[0]:,} secciones (código de la época), {t.shape[0]:,} municipios; '
          f'censo {t.censo.sum():,.0f}, votantes {t.votantes.sum():,.0f} (en el mapa, solo por municipio)')


def pollspaindata(E, elecciones=('1986_06', '1989_10', '1993_06', '1996_03', '2000_03')):
    """Congreso 1986-2000 por mesa desde el repositorio dadosdelaplace/pollspaindata (inst/extdata).
    1982 no: sus mesas traen mal el censo (Ciudad Real a cero, Madrid topado en 9.999); se usa 02198210_MUNI.zip."""
    for y in elecciones:
        ms = pd.read_parquet(f'{E}/raw_poll_stations_congress_{y}.parquet')
        v = pd.read_parquet(f'{E}/raw_candidacies_poll_congress_{y}.parquet')
        cand = pd.read_parquet(f'{E}/raw_candidacies_congress_{y}.parquet')[['id_candidacies', 'abbrev_candidacies', 'name_candidacies']]
        cand['abbrev_candidacies'] = cand.abbrev_candidacies.fillna(cand.name_candidacies)
        for d in (ms, v):
            d['cod_sec'] = d.cod_sec.str.zfill(4).str[-3:]
        os.makedirs(EXTRA, exist_ok=True)
        guarda_viejo(y, ms, v, cand)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == '--pollspaindata':      # python3 otras_elecciones.py --pollspaindata <clon>/inst/extdata
        pollspaindata(sys.argv[2])
    else:
        for p in sys.argv[1:]:
            importa(p)
