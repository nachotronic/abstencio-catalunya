"""Generales de la Segunda República (1933 y 1936) por municipio, del Atlas Electoral de la Segunda República.

Uso:  python3 republica.py <carpeta del atlas>          (escribe datos/extra/1933_11_municipios.csv y 1936_02_...)
      python3 republica.py <carpeta del atlas> --web    (además, web/data/e/1933_11.json, 1936_02.json, meta.json,
                                                        nombres/ y descargas/municipios_republica.csv, sin reconstruir
                                                        el resto; necesita web/data/municipios.json. Tras construir.py y
                                                        pagina.py, volver a pasarlo con --web)

Fuente: Rodon, T., Vall-Prat, P. y Martín Álvarez, D. (2026). Electoral Atlas of the Spanish Second Republic
(1931-1936), v2.0. Universitat Pompeu Fabra. https://doi.org/10.34810/data3274. Licencia CC BY-NC-SA 4.0: lo que
sale de aquí (los CSV y los JSON de esas dos elecciones) se publica con la misma licencia, citando a los autores.
Ficheros que se leen: dataset_muni_vote_shares_wide.csv y dataset_muni_raw_long.csv. El de 1931 solo existe por
circunscripción y no entra en el mapa.

- Se votaba a personas en listas abiertas y cada elector marcaba varios nombres. El peso de cada familia es la suma de
  votos de sus candidatos entre la suma de votos de todos los candidatos (sin blancos ni nulos): la medida
  pct_votes_sumbased que recomienda el atlas para bloques. No es un recuento de electores.
- En unos 3.000 municipios (Barcelona 1933, Aragón, Albacete, Asturias, Cuenca, Navarra y Valencia 1933, Cáceres y
  Pontevedra 1936) el atlas no tiene votos por candidato sino por bloque, de una fuente secundaria. Se usan esos
  votos por bloque y, donde solo hay porcentaje (Albacete, Pontevedra), el porcentaje por los votantes, solo para
  poder sumar municipios fusionados. Si a un municipio le falta un bloque que se presentó en su circunscripción, se
  queda sin reparto (en el origen es un hueco, no un cero).
- Participación: solo la real (votantes / censo, turnout_real del atlas). La estimada a partir de los votos supone que
  todos usaron todos sus votos y a veces pasa del 100 %: no se usa.
- Códigos: INE de la época. Los ~1.390 municipios que ya no existen se suman al municipio actual en el que se
  integraron, según «Alteraciones de los municipios en los Censos de Población desde 1842» del INE
  (republica_municipios_ine.csv, consultado el 22-10-2026). Si el municipio actual existía entonces pero no tiene
  datos en esa elección, queda sin dato aunque los absorbidos sí tengan.
"""
import json, os, sys
import numpy as np
import pandas as pd
from partidos import FAMILIAS, CODIGOS, ALIAS

AQUI = os.path.dirname(os.path.abspath(__file__))
EXTRA = os.path.join(AQUI, 'datos', 'extra')
ELECCIONES = {'1933': '1933_11', '1936': '1936_02'}
ETIQ = {'1933_11': '19N 1933', '1936_02': '16F 1936'}
NOMBRE = {c: n for c, n, _ in FAMILIAS}
CAT = '09'
# Circunscripciones cuyo dato municipal no reproduce el oficial del propio atlas (por circunscripción): sin reparto.
EXCLUIR = {('1933', 'Teruel'): 'la fuente municipal casi no trae la candidatura radical (34 % en la provincia)',
           ('1933', 'Barcelona_capital'): 'solo trae la Lliga y la izquierda catalanista, que sumaron el 73 %'}


def fam(year, ccaa, bloque, partido='', candidatura=''):
    """Familia del mapa para un bloque del atlas (platform_summ) en una comunidad, o None (blancos y nulos)."""
    if bloque == 'blank_and_null':
        return None
    if year == '1936':
        return {'left_coalition': 'FP', 'right_coalition': 'DER', 'centrist_platforms': 'CENTRO',
                'basque_nat_coal': 'PNV'}.get(bloque, 'OTROS')
    if bloque == 'right_wing_regionalist_platforms':
        if partido == 'CT' and candidatura == 'CT':
            return 'DER'           # tradicionalistas en candidatura propia (Álava)
        return 'LLIGA' if ccaa == CAT else 'PNV'
    if bloque == 'left_wing_regionalist_platforms':
        if ccaa == CAT:
            # candidatura con ERC; Acció Catalana y los republicanos nacionalistas, con la izquierda republicana
            return 'ERC' if 'ERC' in candidatura or not candidatura else 'IZQREP'
        return 'OTROS'             # Partido Galeguista, ANV
    return {'right_wing_platforms': 'DER', 'center_right_republican_platforms': 'CENTRO',
            'socialist_platforms': 'PSOE', 'communist_and_other_lw_platforms': 'SUMAR',
            'left_wing_republican_platforms': 'IZQREP', 'left_wing_republican_socialist_coalition': 'IZQREP',
            'republican_socialist_coalition': 'IZQREP'}.get(bloque, 'OTROS')


def num(s):
    return pd.to_numeric(s.astype(str).str.replace(',', '.'), errors='coerce')


def carga(atlas):
    lee = lambda f, **k: pd.read_csv(os.path.join(atlas, f), sep=';', dtype=str, encoding='utf-8-sig', **k)
    w = lee('dataset_muni_vote_shares_wide.csv')
    w = w[w.year.isin(list(ELECCIONES)) & (w.elect_round == '1')].copy()
    for c in ('elect', 'votant', 'elect_est', 'turnout_real'):
        w[c] = num(w[c])
    # censo y votantes: los oficiales cuando la participación real es válida; si no, censo estimado y sin votantes
    ok = w.turnout_real.notna()
    w['censo'] = np.where(ok & w.elect.notna(), w.elect, w.elect_est)
    w['votantes'] = np.where(ok, w.turnout_real / 100 * w.censo, np.nan)

    # votos por candidato (municipios con datos por candidato)
    r = lee('dataset_muni_raw_long.csv', usecols=['year', 'cod_ccaa', 'cod_mun', 'platform_summ', 'party_short',
                                                   'platform_full', 'votes'])
    r = r[r.year.isin(list(ELECCIONES))]
    r['votos'] = num(r.votes).fillna(0)
    r['fam'] = [fam(y, c, b, p, f) for y, c, b, p, f in zip(r.year, r.cod_ccaa, r.platform_summ, r.party_short.fillna(''),
                                                             r.platform_full.fillna(''))]
    v1 = r[r.fam.notna()].groupby(['year', 'cod_mun', 'fam']).votos.sum().reset_index()

    # municipios con datos por bloque de fuentes secundarias: votos por bloque si los hay; si no, porcentaje por votantes
    p = w[w.raw_data_origin == 'platform_data']
    filas = []
    for pref in ('sum_votes_', 'pct_original_'):
        cols = [c for c in w.columns if c.startswith(pref) and not c.endswith(('blank_and_null', '_other'))]
        sub = p[p[cols].notna().any(axis=1)] if pref == 'sum_votes_' else p[p[[c.replace('pct_original_', 'sum_votes_')
                                                                              for c in cols]].isna().all(axis=1)]
        x = sub[['year', 'cod_ccaa', 'circuns', 'cod_mun', 'votantes', 'elect_est', 'votant']].copy()
        x['majority_seats'] = num(sub.majority_seats)
        x['fuente_sum'] = pref == 'sum_votes_'
        for c in cols:
            x[c[len(pref):]] = num(sub[c]) if pref == 'sum_votes_' else num(sub[c]) / 100 * sub.votantes.fillna(sub.elect_est)
        x['other'] = num(sub[pref + 'other'])
        if pref == 'pct_original_':
            x['other'] = x.other / 100 * sub.votantes.fillna(sub.elect_est)
        filas.append(x)
    p = pd.concat(filas, ignore_index=True)
    bl = [c for c in p.columns if c.endswith(('_platforms', '_coalition', '_coal'))]
    # Huecos del origen: un municipio con votos por bloque está incompleto si esos votos no llegan al 85 % de los que
    # podían emitirse (votantes por número de nombres en la papeleta; en Teruel 1933 la fuente casi no trae la
    # candidatura radical, que sacó el 34 %). Sin votantes (Barcelona, Navarra, Valencia 1933): si falta un bloque que
    # aparece en otros municipios de la circunscripción y sacó al menos el 10 % en ella (en Barcelona, 111 pueblos con
    # la Lliga y sin la izquierda catalanista). Los bloques pequeños que faltan son ceros que la fuente no escribió.
    d = lee('dataset_district_raw_long.csv', usecols=['year', 'circuns', 'platform_summ', 'votes'])
    d = d[d.year.isin(list(ELECCIONES))]
    d['votos'] = num(d.votes)
    peso = d.pivot_table(index=['year', 'circuns'], columns='platform_summ', values='votos', aggfunc='sum')
    peso = peso.div(peso.sum(axis=1), axis=0).reindex(columns=bl).fillna(0)
    peso = peso.reindex(pd.MultiIndex.from_frame(p[['year', 'circuns']])).fillna(0)
    peso = peso.where(p.groupby(['year', 'circuns'])[bl].transform(lambda s: s.notna().any()).to_numpy(), 0)
    falta = ((peso.to_numpy() >= .1) & p[bl].isna().to_numpy()).any(axis=1)
    cob = p[bl + ['other']].sum(axis=1, min_count=1) / (p.votant * p.majority_seats)
    inc = np.where(cob.notna() & p.fuente_sum, cob < .85, falta & p.fuente_sum)
    p['inc'] = inc
    malos = set(zip(p[inc].year, p[inc].cod_mun))
    p = p[~inc].melt(id_vars=['year', 'cod_ccaa', 'cod_mun'], value_vars=bl + ['other'], var_name='b', value_name='votos')
    p = p[p.votos.notna()]
    p['fam'] = [fam(y, c, b) for y, c, b in zip(p.year, p.cod_ccaa, p.b)]
    v2 = p.groupby(['year', 'cod_mun', 'fam']).votos.sum().reset_index()
    assert not set(zip(v1.year, v1.cod_mun)) & set(zip(v2.year, v2.cod_mun))
    # municipios con votos por candidato que no llegan al 85 % de los posibles (falta alguna candidatura en el origen)
    c = w[w.raw_data_origin == 'candidate_data']
    tot = v1.groupby(['year', 'cod_mun']).votos.sum().reindex(pd.MultiIndex.from_frame(c[['year', 'cod_mun']])).to_numpy()
    cob = tot / (c.votant * num(c.majority_seats)).to_numpy()
    malos |= set(zip(c.year[cob < .85], c.cod_mun[cob < .85]))
    # circunscripciones en las que los datos municipales no reproducen el resultado oficial (ver LEEME)
    malos |= {(y, m) for y, ci, m in zip(w.year, w.circuns, w.cod_mun) if (y, ci) in EXCLUIR}
    print(f'  aviso: {len(malos)} municipios sin reparto por huecos en el origen:',
          pd.Series([y for y, _ in malos]).value_counts().sort_index().to_dict())
    v = pd.concat([v1, v2], ignore_index=True)
    return w, v[[k not in malos for k in zip(v.year, v.cod_mun)]]


def a_actual(w, v, actuales):
    eq = pd.read_csv(os.path.join(AQUI, 'republica_municipios_ine.csv'), dtype=str).set_index('cod_epoca').cod_actual
    # códigos que no están en el INE (Navahermosa de Corneja, «055012», 79 electores): fuera del mapa
    falta = set(w.cod_mun) - set(actuales) - set(eq.index)
    if falta:
        print('  aviso: códigos sin municipio actual, fuera:', ', '.join(sorted(falta)))
        w = w[~w.cod_mun.isin(falta)]
    epoca = set(w.cod_mun)                   # municipios que existían en 1933 o 1936
    out = {}
    for y, cod in ELECCIONES.items():
        wy = w[w.year == y].copy()
        wy['actual'] = wy.cod_mun.map(lambda c: c if c in actuales else eq[c])
        # municipio actual que existía entonces pero sin datos en esta elección: no se le atribuyen los absorbidos
        sin = {c for c in wy.actual if c in epoca and c not in set(wy.cod_mun)}
        wy = wy[~wy.actual.isin(sin)]
        g = wy.groupby('actual')
        t = pd.DataFrame({'censo': g.censo.sum(), 'votantes': g.votantes.sum(min_count=1),
                          'completo': g.votantes.apply(lambda s: s.notna().all()),
                          'n': g.size(), 'nombres': g.mun.agg(' + '.join)})
        t.loc[~t.completo, 'votantes'] = np.nan     # si a uno de los fusionados le falta, no hay participación
        vy = v[v.year == y].merge(wy[['cod_mun', 'actual']], on='cod_mun')
        pv = vy.pivot_table(index='actual', columns='fam', values='votos', aggfunc='sum', fill_value=0)
        t = t.join(pv.reindex(columns=CODIGOS, fill_value=0))
        out[cod] = t
        print(f'{cod}: {len(wy):,} municipios de la época -> {len(t):,} actuales ({(t.n > 1).sum():,} suman varios; '
              f'{len(sin)} sin dato propio), con participación {t.votantes.notna().mean():.0%}')
    return out


def tasas(t):
    val = t[CODIGOS].sum(axis=1).where(lambda x: x > 0)
    o = pd.DataFrame({'part': (t.votantes / t.censo.where(t.censo > 0)).where(lambda p: p <= 1)})
    for k in CODIGOS:
        o[k] = t[k] / val
    sub = t[[k for k in CODIGOS if k != 'OTROS']]
    o['gana'] = np.where(val.notna() & (sub.fillna(0).max(axis=1) > 0), sub.fillna(-1).idxmax(axis=1), None)
    o['censo'] = t.censo
    return o


def escribe_extra(res):
    os.makedirs(EXTRA, exist_ok=True)
    for cod, t in res.items():
        filas = []
        for m, x in t.iterrows():
            for k in CODIGOS:
                if x[k] > 0:
                    filas.append([m, round(x.censo), '' if pd.isna(x.votantes) else round(x.votantes), 0, 0,
                                  'REP:' + k, NOMBRE[k], round(x[k], 2)])
        d = pd.DataFrame(filas, columns=['mun_code', 'censo', 'votantes', 'blancos', 'nulos', 'siglas', 'nombre', 'votos'])
        d.to_csv(os.path.join(EXTRA, f'{cod}_municipios.csv'), index=False)
        t[['n', 'nombres']].rename_axis('mun_code').to_csv(os.path.join(EXTRA, f'{cod}_fusionados.csv'))


def escribe_web(res, web):
    mun = json.load(open(os.path.join(web, 'municipios.json')))
    meta = json.load(open(os.path.join(web, 'meta.json')))
    for cod, t in res.items():
        o = tasas(t).reindex(mun['cod'])
        d = {}
        vacias = {k for k in CODIGOS if k != 'OTROS' and not (t[k] > 0).any()}
        d[f'{cod}_part'] = [None if pd.isna(x) else round(float(x), 3) for x in o.part]
        d[f'{cod}_gana'] = [CODIGOS.index(x) if isinstance(x, str) else -1 for x in o.gana]
        for k in CODIGOS:
            if k not in vacias:
                d[f'{cod}_{k}'] = [None if pd.isna(x) else round(float(x), 3) for x in o[k]]
        d[f'{cod}_censo'] = [None if pd.isna(x) else int(x) for x in o.censo]
        # municipios de la época que se suman en cada municipio actual (para la ficha)
        fus = t.nombres.where(t.n > 1).reindex(mun['cod'])
        d[f'{cod}_fus'] = [None if pd.isna(x) else x for x in fus]
        json.dump(d, open(os.path.join(web, 'e', f'{cod}.json'), 'w'), separators=(',', ':'))
        print(cod, 'en el mapa:', int(o.part.notna().sum()), 'con participación,', int(o.gana.notna().sum()), 'con reparto')
    # nombre de la candidatura en Cataluña en 1936 (el mismo formato que nombres.py)
    cat = ['08', '17', '25', '43']
    json.dump({'n': ['', "Front d'Esquerres", "Front Català d'Ordre"], 'm': {},
               'p': {'FP': {p: 1 for p in cat}, 'DER': {p: 2 for p in cat}}},
              open(os.path.join(web, 'nombres', '1936_02.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump({'n': [''], 'm': {}, 'p': {}}, open(os.path.join(web, 'nombres', '1933_11.json'), 'w'), separators=(',', ':'))
    ind = os.path.join(web, 'nombres', 'indice.json')
    if os.path.exists(ind):
        i = json.load(open(ind))
        json.dump(i + [c for c in ['1933_11', '1936_02'] if c not in i], open(ind, 'w'))
    # descarga aparte, con la licencia del atlas (CC BY-NC-SA 4.0), no la CC BY del resto de los datos
    des = os.path.join(web, '..', 'descargas')
    os.makedirs(des, exist_ok=True)
    out = pd.DataFrame({'mun_code': mun['cod'], 'municipio': mun['nombre'],
                        'provincia': [mun['provs'][p] if p >= 0 else '' for p in mun['prov']]})
    for cod, t in res.items():
        o = tasas(t)
        o['votantes'] = t.votantes
        o['municipios_epoca'] = t.nombres.where(t.n > 1)
        cols = ['part', 'censo', 'votantes', 'gana'] + [k for k in CODIGOS if (t[k] > 0).any()] + ['municipios_epoca']
        o = o[cols].round({k: 4 for k in CODIGOS + ['part']}).add_prefix(cod + '_')
        out = out.merge(o, left_on='mun_code', right_index=True, how='left')
    out = out[out.filter(like='_censo').notna().any(axis=1)]
    for c in out.filter(regex='_(censo|votantes)$'):
        out[c] = out[c].round().astype('Int64')
    out.to_csv(os.path.join(des, 'municipios_republica.csv'), index=False)
    open(os.path.join(des, 'LICENCIA-republica.txt'), 'w').write(
        'municipios_republica.csv: elecciones generales de 1933 y 1936 por municipio actual.\n'
        'Datos derivados del Atlas Electoral de la Segunda República: Rodon, T., Vall-Prat, P. y Martín Álvarez, D. (2026). '
        'Electoral Atlas of the Spanish Second Republic (1931-1936), v2.0. Universitat Pompeu Fabra. '
        'https://doi.org/10.34810/data3274\n'
        'Licencia: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/), la misma del original: '
        'citar a los autores y a mapaelectoral.es, sin uso comercial y compartiendo lo derivado con la misma licencia.\n'
        'Cambios: bloques agrupados en familias, municipios desaparecidos sumados al municipio actual (INE, Alteraciones de '
        'los municipios desde 1842), porcentajes sin blancos ni nulos. Método: https://mapaelectoral.es/generales-2026/metodologia.html\n')
    # mismas familias y orden que construir.py (las de la República van antes de "Otros")
    meta['familias'] = [{'cod': c, 'nombre': n, 'color': col} for c, n, col in FAMILIAS]
    meta['alias'] = ALIAS
    ya = {e['cod'] for e in meta['elecciones']}
    nuevas = [{'cod': c, 'nombre': ETIQ[c], 'tipo': 'generales', 'secciones': False, 'aparte': True}
              for c in sorted(ELECCIONES.values()) if c not in ya]
    meta['elecciones'] = nuevas + meta['elecciones']
    json.dump(meta, open(os.path.join(web, 'meta.json'), 'w'), ensure_ascii=False, separators=(',', ':'))


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        sys.exit(__doc__)
    web = os.path.join(AQUI, 'web', 'data')
    if '--web' in sys.argv and not os.path.exists(os.path.join(web, 'municipios.json')):
        web = os.path.join(AQUI, '..', 'data')        # copia publicada en el repositorio (generales-2026/src/)
    actuales = json.load(open(os.path.join(web, 'municipios.json')))['cod']
    w, v = carga(args[0])
    res = a_actual(w, v, set(actuales))
    escribe_extra(res)
    if '--web' in sys.argv:
        escribe_web(res, web)
