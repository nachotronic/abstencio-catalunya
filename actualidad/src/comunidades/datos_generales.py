"""Historia en generales (1977-2023) de cada comunidad autónoma: porcentajes por familia, participación,
ganador por provincia y municipios ganados. Sale de generales/datos/historico (carpeta del proyecto).
Antes de 2004 el ganador de cada municipio y provincia se calcula con todas las candidaturas (incluidas las que van
a «Otros»), como en la serie «Historia electoral»; desde 2004, con las familias."""
import json, os, sys
import pandas as pd

H = '/mnt/project-files/generales/datos/historico'
AQUI = os.path.dirname(os.path.abspath(__file__))
FAM = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'UPYD', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC', 'UCD', 'CDS', 'OTROS']
CCAA = {
 'andalucia': ('Andalucía', ['Almería', 'Cádiz', 'Córdoba', 'Granada', 'Huelva', 'Jaén', 'Málaga', 'Sevilla']),
 'aragon': ('Aragón', ['Huesca', 'Teruel', 'Zaragoza']),
 'asturias': ('Asturias', ['Asturias']),
 'baleares': ('Illes Balears', ['Illes Balears']),
 'canarias': ('Canarias', ['Las Palmas', 'Santa Cruz de Tenerife']),
 'cantabria': ('Cantabria', ['Cantabria']),
 'castilla-la-mancha': ('Castilla-La Mancha', ['Albacete', 'Ciudad Real', 'Cuenca', 'Guadalajara', 'Toledo']),
 'castilla-y-leon': ('Castilla y León', ['Ávila', 'Burgos', 'León', 'Palencia', 'Salamanca', 'Segovia', 'Soria', 'Valladolid', 'Zamora']),
 'cataluna': ('Cataluña', ['Barcelona', 'Girona', 'Lleida', 'Tarragona']),
 'comunidad-valenciana': ('Comunitat Valenciana', ['Alicante', 'Castellón/Castelló', 'Valencia/Valéncia']),
 'extremadura': ('Extremadura', ['Badajoz', 'Cáceres']),
 'galicia': ('Galicia', ['A Coruña', 'Lugo', 'Ourense', 'Pontevedra']),
 'madrid': ('Comunidad de Madrid', ['Madrid']),
 'murcia': ('Región de Murcia', ['Murcia']),
 'navarra': ('Navarra', ['Navarra']),
 'pais-vasco': ('País Vasco', ['Araba/Álava', 'Bizkaia', 'Gipuzkoa']),
 'la-rioja': ('La Rioja', ['La Rioja']),
 'ceuta': ('Ceuta', ['Ceuta']),
 'melilla': ('Melilla', ['Melilla']),
}
PROV_CCAA = {p: k for k, (_, ps) in CCAA.items() for p in ps}


def main():
    d = pd.read_csv(f'{H}/municipios_largo.csv.gz')
    d = d[d.tipo == 'generales'].copy()
    d['ccaa'] = d.provincia.map(PROV_CCAA)
    assert d.ccaa.notna().all()
    els = sorted(d.eleccion.unique())
    # provincia de cada código de la época en candidaturas (dos primeros dígitos del código INE)
    prov_cod = d.assign(pc=d.mun_code // 1000).groupby('pc').provincia.first().to_dict()
    c = pd.read_csv(f'{H}/candidaturas_municipio.csv.gz')
    c = c[c.eleccion.isin(els)].copy()
    c['provincia'] = (c.mun_code // 1000).map(prov_cod)
    # ganador por municipio antes de 2004: candidatura más votada (de todas)
    top = c.sort_values('votos', ascending=False).drop_duplicates(['eleccion', 'mun_code'])
    gana_pre = {(r.eleccion, r.mun_code): (r.familia, r.siglas) for r in top.itertuples()}

    def ganador_mun(r):
        if r.eleccion < '2004':
            g = gana_pre.get((r.eleccion, r.mun_code))
            return g[0] if g else None
        v = r[FAM].astype(float)
        return v.idxmax() if v.sum() > 0 else None
    d['gana2'] = d.apply(ganador_mun, axis=1)

    esp = d.groupby('eleccion')[FAM + ['censo', 'votantes']].sum()
    out = {'elecciones': els, 'espana': {}, 'ccaa': {}}
    for e in els:
        tot = esp.loc[e, FAM].sum()
        out['espana'][e] = {'pct': {f: round(100 * esp.loc[e, f] / tot, 2) for f in FAM}, 'part': round(100 * esp.loc[e, 'votantes'] / esp.loc[e, 'censo'], 2)}
    for k, (nombre, provs) in CCAA.items():
        s = d[d.ccaa == k]
        g = s.groupby('eleccion')[FAM + ['censo', 'votantes']].sum()
        r = {'nombre': nombre, 'provincias': provs, 'serie': {}, 'prov': {}, 'munis': {}, 'n_munis': {}}
        for e in els:
            tot = g.loc[e, FAM].sum()
            r['serie'][e] = {'pct': {f: round(100 * g.loc[e, f] / tot, 2) for f in FAM}, 'votos': {f: int(g.loc[e, f]) for f in FAM},
                             'part': round(100 * g.loc[e, 'votantes'] / g.loc[e, 'censo'], 2), 'censo': int(g.loc[e, 'censo'])}
            se = s[s.eleccion == e]
            r['munis'][e] = se.gana2.value_counts().to_dict()
            r['n_munis'][e] = int(len(se))
            for p in provs:
                sp = se[se.provincia == p]
                if e < '2004':
                    cp = c[(c.eleccion == e) & (c.provincia == p)].groupby(['siglas', 'familia']).votos.sum().sort_values(ascending=False)
                    tot_p = cp.sum()
                    (sig, fam), v = cp.index[0], cp.iloc[0]
                    seg = cp.index[1]
                    r['prov'].setdefault(p, {})[e] = {'fam': fam, 'siglas': sig, 'pct': round(100 * v / tot_p, 2),
                                                      'seg': seg[1], 'seg_siglas': seg[0], 'seg_pct': round(100 * cp.iloc[1] / tot_p, 2)}
                else:
                    v = sp[FAM].sum().sort_values(ascending=False)
                    tot_p = v.sum()
                    fam = v.index[0]
                    r['prov'].setdefault(p, {})[e] = {'fam': fam, 'pct': round(100 * v.iloc[0] / tot_p, 2),
                                                      'seg': v.index[1], 'seg_pct': round(100 * v.iloc[1] / tot_p, 2)}
                    if fam == 'OTROS':
                        print('AVISO: Otros primero en', p, e, file=sys.stderr)
        # municipios con el mismo ganador en las 16 (antes de 2004 con todas las listas)
        piv = s.pivot_table(index=['mun_code', 'municipio'], columns='eleccion', values='gana2', aggfunc='first')
        piv = piv.dropna()
        fieles = piv[piv.nunique(axis=1) == 1]
        censo23 = s[s.eleccion == els[-1]].set_index('mun_code').censo
        r['fieles'] = sorted(({'mun': m, 'fam': row.iloc[0], 'censo': int(censo23.get(code, 0))} for (code, m), row in fieles.iterrows()),
                             key=lambda x: -x['censo'])
        r['n_fieles'] = len(fieles); r['n_completos'] = len(piv)
        # mayores municipios en 2023 y su ganador
        u = s[s.eleccion == els[-1]].sort_values('censo', ascending=False).head(12)
        r['mayores'] = [{'mun': x.municipio, 'censo': int(x.censo), 'gana': x.gana2,
                         'pct': {f: round(100 * getattr(x, f) / sum(getattr(x, ff) for ff in FAM), 1) for f in FAM}} for x in u.itertuples()]
        top10 = s[s.eleccion == els[-1]].sort_values('censo', ascending=False).head(10).mun_code.tolist()
        r['mayores_hist'] = [{'mun': s[(s.mun_code == mc)].municipio.iloc[-1], 'censo': int(censo23.get(mc, 0)),
                              'g': [(lambda q: q.gana2.iloc[0] if len(q) else None)(s[(s.mun_code == mc) & (s.eleccion == e)]) for e in els]} for mc in top10]
        gm = s.pivot_table(index='mun_code', columns='eleccion', values='gana2', aggfunc='first')
        r['gana_mun'] = {f'{int(c):05d}': [(row.get(e) if isinstance(row.get(e), str) else None) for e in els] for c, row in gm.iterrows()}
        out['ccaa'][k] = r
    json.dump(out, open(os.path.join(AQUI, 'generales.json'), 'w'), ensure_ascii=False)
    print('ok', len(out['ccaa']))


if __name__ == '__main__':
    main()
