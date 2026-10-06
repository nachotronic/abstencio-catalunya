"""Genera las páginas estáticas de la pieza (index.html, metodologia.html), los CSV de descarga,
llms.txt y sitemap.xml a partir de ./datos. Las cifras del texto salen de los datos, así que
basta con volver a ejecutarlo tras actualizar resultados.

Uso:  python3 pagina.py
"""
import datetime as dt, html, json, os, re, shutil
import pandas as pd
from partidos import FAMILIAS

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS, WEB = os.path.join(AQUI, 'datos'), os.path.join(AQUI, 'web')
URL = os.environ.get('GENERALES_URL', 'https://nachotronic.github.io/abstencio-catalunya/generales/')
AUTOR = os.environ.get('GENERALES_AUTOR', 'Nacho')
HOY = dt.date.today().isoformat()
NOM = {c: n for c, n, _ in FAMILIAS}
COL = {c: col for c, _, col in FAMILIAS}


def p(v, d=0):
    return f"{v * 100:.{d}f}".replace('.', ',') + '%'


def n(v):
    return f"{v:,.0f}".replace(',', '.')


def lista(df, col):
    nombres = [f"{html.escape(m)} ({p(v)})" for m, v in zip(df.municipio, df[col])]
    return ', '.join(nombres[:-1]) + ' y ' + nombres[-1]


def main():
    R = json.load(open(os.path.join(DATOS, 'resumen.json')))
    sec = pd.read_csv(os.path.join(DATOS, 'secciones.csv'), dtype={'tract_code': str, 'mun_code': str})
    mun = pd.read_csv(os.path.join(DATOS, 'municipios.csv'), dtype={'mun_code': str})
    V = R['variables']
    ren, pob, eda, ext, est, par = (V[k]['deciles'] for k in ('renta_uc', 'pobreza', 'edad_media', 'extranjeros', 'estudios_sup_2021', 'paro_2021'))
    nac = R['nacional']['23J 2023']
    y = '2023_07'
    gs = sec[f'{y}_gana'].value_counts()
    gm = mun[f'{y}_gana'].value_counts()
    both = sec[sec['2019_11_gana'].notna() & sec[f'{y}_gana'].notna()]
    vox_pp = int(((both['2019_11_gana'] == 'VOX') & (both[f'{y}_gana'] == 'PP')).sum())
    vox19 = int((both['2019_11_gana'] == 'VOX').sum())
    adultos = sec.adultos.sum(); sin = (sec.adultos - sec[f'{y}_censo']).clip(lower=0).sum()
    big = mun[mun.poblacion > 50000]
    low = big.nsmallest(3, f'{y}_part'); high = big.nlargest(3, f'{y}_part')
    vox = big.nlargest(3, f'{y}_VOX')
    F = dict(
        part=p(nac['part'], 1), pp=p(nac['PP'], 1), psoe=p(nac['PSOE'], 1), vox=p(nac['VOX'], 1), sumar=p(nac['SUMAR'], 1),
        nsec=n(len(sec)), nmun=n(len(mun)),
        sec_pp=n(gs.get('PP', 0)), sec_psoe=n(gs.get('PSOE', 0)), mun_pp=n(gm.get('PP', 0)), mun_psoe=n(gm.get('PSOE', 0)),
        vox19=n(vox19), vox_pp=n(vox_pp),
        r_part1=p(ren[0]['part']), r_part10=p(ren[9]['part']), r_lo=n(ren[0]['hi']), r_hi=n(ren[9]['lo']),
        r_psoe1=p(ren[0]['PSOE']), r_psoe10=p(ren[9]['PSOE']), r_pp1=p(ren[0]['PP']), r_pp10=p(ren[9]['PP']),
        r_vox1=p(ren[0]['VOX']), r_vox5=p(ren[4]['VOX']), r_vox10=p(ren[9]['VOX']),
        pob_part1=p(pob[0]['part']), pob_part10=p(pob[9]['part']), pob10=p(pob[9]['lo']),
        e_vox1=p(eda[0]['VOX']), e_vox10=p(eda[9]['VOX']), e_pp10=p(eda[9]['PP']), e_hi1=f"{eda[0]['hi']:.0f}", e_lo10=f"{eda[9]['lo']:.0f}",
        e_part1=p(eda[0]['part']), e_part10=p(eda[9]['part']),
        x_part1=p(ext[0]['part']), x_part10=p(ext[9]['part']), x_lo10=p(ext[9]['lo']), x_vox1=p(ext[0]['VOX']), x_vox10=p(ext[9]['VOX']),
        x_psoe10=p(ext[9]['PSOE']), x_pp1=p(ext[0]['PP']), x_pp10=p(ext[9]['PP']),
        s_pp10=p(est[9]['PP']), s_psoe1=p(est[0]['PSOE']), s_psoe10=p(est[9]['PSOE']),
        sin=n(round(sin / 1e5) * 1e5), sin_pct=p(sin / adultos),
        low=lista(low, f'{y}_part'), high=lista(high, f'{y}_part'), vox_top=lista(vox, f'{y}_VOX'),
        hoy=HOY, url=URL, autor=html.escape(AUTOR),
    )
    F.update({'tablas_' + k: v for k, v in tablas(V).items()})
    F.update(historia(sec))
    F['jsonld'] = jsonld(F)
    tpl = open(os.path.join(AQUI, 'plantilla.html'), encoding='utf-8').read()
    out = tpl
    for k, v in F.items():
        out = out.replace('{{' + k + '}}', str(v))
    assert '{{' not in out, out[out.index('{{'):out.index('{{') + 40]
    open(os.path.join(WEB, 'index.html'), 'w', encoding='utf-8').write(out)
    met = open(os.path.join(AQUI, 'metodologia.html'), encoding='utf-8').read().replace('{{hoy}}', HOY).replace('{{url}}', URL)
    open(os.path.join(WEB, 'metodologia.html'), 'w', encoding='utf-8').write(met)
    descargas()
    llms(F)
    open(os.path.join(WEB, 'sitemap.xml'), 'w').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{URL}{u}</loc><lastmod>{HOY}</lastmod></url>\n' for u in ('', 'metodologia.html', 'llms.txt'))
        + '</urlset>\n')
    print('ok', os.path.join(WEB, 'index.html'))


ETQ = {'2004_03': '2004', '2008_03': '2008', '2011_11': '2011', '2015_12': '2015', '2016_06': '2016', '2019_04': 'abr. 2019',
       '2019_11': 'nov. 2019', '2023_07': '2023'}


def historia(sec):
    """Brecha de participación por renta en todas las elecciones (deciles de renta 2023 fijos, ponderados por el censo
    del 23J; las elecciones antiguas, solo en las secciones que conservan el código) y voto por renta en 2004 y 2023."""
    x = sec[sec.renta_uc.notna() & (sec['2023_07_censo'] > 0)].sort_values('renta_uc')
    cum = x['2023_07_censo'].cumsum() / x['2023_07_censo'].sum()
    dec = pd.Series((cum * 10).apply(lambda v: min(10, int(-(-v // 1)))).values, index=x.tract_code)
    y = sec.assign(dec=sec.tract_code.map(dec)).dropna(subset=['dec'])
    elecs = [c[:-5] for c in sec.columns if c.endswith('_part') and f'{c[:-5]}_votantes' in sec]
    part = {e: y[y[f'{e}_part'].notna()].groupby('dec').apply(lambda g: g[f'{e}_votantes'].sum() / g[f'{e}_censo'].sum())
            for e in elecs}
    # otras variables (23J): paro y estudios
    def part_por(v):
        z = sec[sec[v].notna() & (sec['2023_07_censo'] > 0)].sort_values(v)
        c = z['2023_07_censo'].cumsum() / z['2023_07_censo'].sum()
        z = z.assign(dec=(c * 10).apply(lambda t: min(10, int(-(-t // 1)))).values)
        g = z.groupby('dec')[['2023_07_votantes', '2023_07_censo']].sum()
        return g['2023_07_votantes'] / g['2023_07_censo']
    r = pd.read_csv(os.path.join(DATOS, 'resultados_secciones_largo.csv'), dtype={'tract_code': str})
    r = r.assign(dec=r.tract_code.map(dec)).dropna(subset=['dec'])
    g = r.groupby(['eleccion', 'dec'])[['candidaturas', 'blancos', 'PP', 'PSOE', 'VOX']].sum()
    sh = g[['PP', 'PSOE', 'VOX']].div(g.candidaturas + g.blancos, axis=0)
    gap = {e: v.loc[10] - v.loc[1] for e, v in part.items()}
    pp, pa = part_por('paro_2021'), part_por('estudios_sup_2021')
    F = dict(
        h_gap04=p(gap['2004_03'], 1).replace('%', ' puntos'), h_gap23=p(gap['2023_07'], 1).replace('%', ' puntos'),
        h_gap19=p(gap['2019_11'], 1).replace('%', ' puntos'),
        h_p04_1=p(part['2004_03'].loc[1], 1), h_p04_10=p(part['2004_03'].loc[10], 1),
        h_psoe04_1=p(sh.loc[('2004_03', 1), 'PSOE'], 1), h_psoe04_10=p(sh.loc[('2004_03', 10), 'PSOE'], 1),
        h_pp04_1=p(sh.loc[('2004_03', 1), 'PP'], 1), h_pp04_10=p(sh.loc[('2004_03', 10), 'PP'], 1),
        paro_part1=p(pp.loc[1], 1), paro_part10=p(pp.loc[10], 1), est_part1=p(pa.loc[1], 1), est_part10=p(pa.loc[10], 1),
    )
    for e, k in (('E2024', 'e24'), ('E2019', 'e19'), ('M2023', 'm23'), ('M2011', 'm11')):
        if e in part:
            F.update({f'{k}_1': p(part[e].loc[1], 1), f'{k}_10': p(part[e].loc[10], 1), f'{k}_gap': p(gap[e], 1).replace('%', ' puntos')})
    if 'M2023' in part:
        F.update(m23_vox1=p(sh.loc[('M2023', 1), 'VOX'], 1), m23_vox10=p(sh.loc[('M2023', 10), 'VOX'], 1))
    F['chart_brecha'] = svg_brecha(gap)
    return F


def svg_brecha(gap):
    """Barras: diferencia de participación entre el 10% más rico y el 10% más pobre, por elección (HTML estático)."""
    grupos = [('Generales', [e for e in ETQ if e in gap]), ('Municipales', sorted(e for e in gap if e[0] == 'M')),
              ('Europeas', sorted(e for e in gap if e[0] == 'E'))]
    filas = []
    for nom, es in grupos:
        if es:
            filas.append(('h', nom))
            filas += [('b', e) for e in es]
    W, hb, x0, mx = 420, 24, 74, max(gap.values())
    H = len(filas) * hb + 8
    out = [f'<svg class="brecha" viewBox="0 0 {W} {H}" role="img" aria-label="Diferencia de participación entre las secciones más ricas y las más pobres, por elección">']
    yy = 4
    for t, v in filas:
        if t == 'h':
            out.append(f'<text class="gh" x="0" y="{yy + 15}">{v}</text>')
        else:
            w = (W - x0 - 62) * gap[v] / mx
            lab = ETQ.get(v, v[1:])
            out.append(f'<text class="ax" x="{x0 - 8}" y="{yy + 15}" text-anchor="end">{lab}</text>'
                       f'<rect class="bar{" e" if v[0] in "ME" else ""}" x="{x0}" y="{yy + 4}" width="{w:.1f}" height="{hb - 8}" rx="2"/>'
                       f'<text class="val" x="{x0 + w + 6:.1f}" y="{yy + 15}">{p(gap[v], 1).replace("%", "")} pts</text>')
        yy += hb
    out.append('</svg>')
    return ''.join(out)


def tablas(V):
    out = []
    cols = ['PP', 'PSOE', 'VOX', 'SUMAR']
    for k, o in V.items():
        fmt = (lambda v: n(v) + ' €') if k == 'renta_uc' else ((lambda v: f"{v:.1f}".replace('.', ',')) if k == 'edad_media' else (lambda v: p(v, 1)))
        rows = ''.join(f"<tr><td>{d['d']}</td><td>{fmt(d['lo'])} – {fmt(d['hi'])}</td><td>{p(d['part'], 1)}</td>"
                       + ''.join(f"<td>{p(d[c], 1)}</td>" for c in cols) + '</tr>' for d in o['deciles'])
        out.append(f'<details class="tabla"><summary>Datos: {html.escape(o["nombre"])} por decil</summary><table><caption>Elecciones generales 23J 2023. '
                   f'Cada decil agrupa secciones censales con el 10% del censo electoral, ordenadas por {html.escape(o["nombre"].lower())}.</caption>'
                   '<thead><tr><th>Decil</th><th>Rango</th><th>Participación</th>' + ''.join(f'<th>{NOM[c]}</th>' for c in cols)
                   + f'</tr></thead><tbody>{rows}</tbody></table></details>')
    return {k: v for k, v in zip(V.keys(), out)}


def jsonld(F):
    art = {
        '@context': 'https://schema.org', '@type': 'NewsArticle',
        'headline': 'El mapa de las generales: cómo vota cada barrio de España según su renta, su edad y su población extranjera',
        'description': f"Resultados del Congreso de 2004 a 2023 en las {F['nsec']} secciones censales de España, cruzados con renta, pobreza, edad y población extranjera del INE.",
        'datePublished': F['hoy'], 'dateModified': F['hoy'], 'inLanguage': 'es', 'url': F['url'],
        'author': {'@type': 'Person', 'name': AUTOR}, 'isAccessibleForFree': True,
        'about': [{'@type': 'Event', 'name': 'Elecciones generales de España de 2026', 'startDate': '2026-11-29'}],
        'citation': ['https://infoelectoral.interior.gob.es/', 'https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'https://www.ine.es/censos2021/'],
    }
    ds = {
        '@context': 'https://schema.org', '@type': 'Dataset',
        'name': 'Elecciones generales 2004-2023 por sección censal con renta, edad y población extranjera',
        'description': 'Votos al Congreso (2004-2023), municipales (2011-2023; 2007 por municipio) y europeas (2019 y 2024) por familia política, participación y censo por sección censal (códigos INE 2023), con renta neta por unidad de consumo, población en riesgo de pobreza, edad media y población extranjera (INE ADRH 2023) y estudios y paro (Censo 2021).',
        'url': F['url'] + 'metodologia.html', 'license': 'https://creativecommons.org/licenses/by/4.0/', 'inLanguage': 'es',
        'creator': {'@type': 'Person', 'name': AUTOR}, 'dateModified': F['hoy'],
        'temporalCoverage': '2004-03-14/2024-06-09', 'spatialCoverage': {'@type': 'Place', 'name': 'España'},
        'isBasedOn': ['https://infoelectoral.interior.gob.es/', 'https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'https://github.com/dadosdelaplace/pollspaindata', 'https://github.com/pablogguz/ineAtlas.data'],
        'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'text/csv', 'contentUrl': F['url'] + 'descargas/' + f}
                         for f in ('secciones.csv', 'municipios.csv', 'resultados_secciones_largo.csv',
                                   'secciones_municipales_europeas.csv', 'resultados_secciones_largo_municipales_europeas.csv')],
    }
    return '\n'.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (art, ds))


def descargas():
    d = os.path.join(WEB, 'descargas'); os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(DATOS, 'municipios.csv'), os.path.join(d, 'municipios.csv'))
    # secciones: generales en los ficheros de siempre; municipales y europeas (M2023, E2024...) aparte, para no pasar de 50 MB
    otra = lambda c: bool(re.match(r'^[ME]\d{4}', c))
    s = pd.read_csv(os.path.join(DATOS, 'secciones.csv'), dtype={'tract_code': str, 'mun_code': str})
    s[[c for c in s if not otra(c)]].to_csv(os.path.join(d, 'secciones.csv'), index=False)
    s[['tract_code'] + [c for c in s if otra(c)]].to_csv(os.path.join(d, 'secciones_municipales_europeas.csv'), index=False)
    r = pd.read_csv(os.path.join(DATOS, 'resultados_secciones_largo.csv'), dtype={'tract_code': str, 'mun_code': str, 'eleccion': str})
    r[~r.eleccion.map(otra)].to_csv(os.path.join(d, 'resultados_secciones_largo.csv'), index=False)
    r[r.eleccion.map(otra)].to_csv(os.path.join(d, 'resultados_secciones_largo_municipales_europeas.csv'), index=False)
    open(os.path.join(d, 'LICENCIA.txt'), 'w').write(
        'Datos derivados publicados con licencia CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).\n'
        'Cita: "Elecciones generales 2004-2023 por sección censal (con municipales y europeas)", ' + AUTOR + ', ' + HOY + ', ' + URL + '\n'
        'Fuentes originales: Ministerio del Interior (resultados electorales) e INE (Atlas de Distribución de Renta de los Hogares 2023; Censo 2021), '
        'reutilizables citando la fuente.\n')


def llms(F):
    t = f"""# El mapa de las generales: cómo vota cada barrio de España

> Resultados de las elecciones al Congreso de 2004 a 2023 en las {F['nsec']} secciones censales de España, cruzados con renta, pobreza, edad y población extranjera (INE). Incluye también las municipales de 2011 a 2023 y las europeas de 2019 y 2024 por sección, y las municipales de 2007 por municipio. Preparado para las elecciones generales del 29 de noviembre de 2026.

Autor: {F['autor']}. Actualizado: {F['hoy']}. Licencia de los datos: CC BY 4.0.

## Cifras clave (23J 2023, sin voto CERA)
- Participación: {F['part']}. PP {F['pp']}, PSOE {F['psoe']}, Vox {F['vox']}, Sumar {F['sumar']} (sobre voto válido).
- En el 10% del censo que vive en las secciones más pobres (renta por unidad de consumo por debajo de {F['r_lo']} €) votó el {F['r_part1']}; en el 10% más rico (más de {F['r_hi']} €), el {F['r_part10']}.
- El PSOE obtuvo el {F['r_psoe1']} en las secciones más pobres y el {F['r_psoe10']} en las más ricas; el PP, el {F['r_pp1']} y el {F['r_pp10']}.
- Vox sacó el {F['e_vox1']} en las secciones más jóvenes (edad media inferior a {F['e_hi1']} años) y el {F['e_vox10']} en las más envejecidas.
- En las secciones con más población extranjera (más del {F['x_lo10']}) la participación fue del {F['x_part10']}, frente al {F['x_part1']} en las que menos.
- Unos {F['sin']} adultos residentes ({F['sin_pct']}) no pueden votar en unas generales por no tener la nacionalidad española.
- La diferencia de participación entre el 10% de secciones más ricas y el 10% más pobres pasó de {F['h_gap04']} en 2004 a {F['h_gap23']} en 2023 (mismas secciones, ordenadas por su renta de 2023). En las europeas de 2024 fue de {F['e24_gap']}.

## Páginas
- [Pieza interactiva]({F['url']}): mapa por municipio y sección censal y gráficos por decil.
- [Metodología y fuentes]({F['url']}metodologia.html)

## Datos descargables (CSV, UTF-8)
- [secciones.csv]({F['url']}descargas/secciones.csv): una fila por sección censal INE 2023, resultados por elección y variables sociodemográficas.
- [municipios.csv]({F['url']}descargas/municipios.csv): lo mismo por municipio.
- [resultados_secciones_largo.csv]({F['url']}descargas/resultados_secciones_largo.csv): votos por sección, elección y familia política.
"""
    open(os.path.join(WEB, 'llms.txt'), 'w', encoding='utf-8').write(t)


if __name__ == '__main__':
    main()
