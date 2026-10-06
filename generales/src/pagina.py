"""Genera las páginas estáticas de la pieza (index.html, metodologia.html), los CSV de descarga,
llms.txt y sitemap.xml a partir de ./datos. Las cifras del texto salen de los datos, así que
basta con volver a ejecutarlo tras actualizar resultados.

Uso:  python3 pagina.py
"""
import datetime as dt, html, json, os, shutil
import pandas as pd
from partidos import FAMILIAS

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS, WEB = os.path.join(AQUI, 'datos'), os.path.join(AQUI, 'web')
URL = os.environ.get('GENERALES_URL', 'https://nachotronic.github.io/abstencio-catalunya/generales/')
AUTOR = os.environ.get('GENERALES_AUTOR', 'Nacho G. del Álamo')
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
        'author': {'@type': 'Person', 'name': AUTOR, 'url': 'https://nachotronic.github.io/abstencio-catalunya/sobre-mi.html'}, 'isAccessibleForFree': True,
        'about': [{'@type': 'Event', 'name': 'Elecciones generales de España de 2026', 'startDate': '2026-11-29'}],
        'citation': ['https://infoelectoral.interior.gob.es/', 'https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'https://www.ine.es/censos2021/'],
    }
    ds = {
        '@context': 'https://schema.org', '@type': 'Dataset',
        'name': 'Elecciones generales 2004-2023 por sección censal con renta, edad y población extranjera',
        'description': 'Votos al Congreso por familia política, participación y censo por sección censal (códigos INE 2023), con renta neta por unidad de consumo, población en riesgo de pobreza, edad media y población extranjera (INE ADRH 2023) y estudios y paro (Censo 2021).',
        'url': F['url'] + 'metodologia.html', 'license': 'https://creativecommons.org/licenses/by/4.0/', 'inLanguage': 'es',
        'creator': {'@type': 'Person', 'name': AUTOR, 'url': 'https://nachotronic.github.io/abstencio-catalunya/sobre-mi.html'}, 'dateModified': F['hoy'],
        'temporalCoverage': '2004-03-14/2023-07-23', 'spatialCoverage': {'@type': 'Place', 'name': 'España'},
        'isBasedOn': ['https://infoelectoral.interior.gob.es/', 'https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'https://github.com/dadosdelaplace/pollspaindata', 'https://github.com/pablogguz/ineAtlas.data'],
        'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'text/csv', 'contentUrl': F['url'] + 'descargas/' + f}
                         for f in ('secciones.csv', 'municipios.csv', 'resultados_secciones_largo.csv')],
    }
    return '\n'.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (art, ds))


def descargas():
    d = os.path.join(WEB, 'descargas'); os.makedirs(d, exist_ok=True)
    for f in ('secciones.csv', 'municipios.csv', 'resultados_secciones_largo.csv'):
        shutil.copy(os.path.join(DATOS, f), os.path.join(d, f))
    open(os.path.join(d, 'LICENCIA.txt'), 'w').write(
        'Datos derivados publicados con licencia CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).\n'
        'Cita: "Elecciones generales 2004-2023 por sección censal", ' + AUTOR + ', ' + HOY + ', ' + URL + '\n'
        'Fuentes originales: Ministerio del Interior (resultados electorales) e INE (Atlas de Distribución de Renta de los Hogares 2023; Censo 2021), '
        'reutilizables citando la fuente.\n')


def llms(F):
    t = f"""# El mapa de las generales: cómo vota cada barrio de España

> Resultados de las elecciones al Congreso de 2004 a 2023 en las {F['nsec']} secciones censales de España, cruzados con renta, pobreza, edad y población extranjera (INE). Preparado para las elecciones generales del 29 de noviembre de 2026.

Autor: {F['autor']}. Actualizado: {F['hoy']}. Licencia de los datos: CC BY 4.0.

## Cifras clave (23J 2023, sin voto CERA)
- Participación: {F['part']}. PP {F['pp']}, PSOE {F['psoe']}, Vox {F['vox']}, Sumar {F['sumar']} (sobre voto válido).
- En el 10% del censo que vive en las secciones más pobres (renta por unidad de consumo por debajo de {F['r_lo']} €) votó el {F['r_part1']}; en el 10% más rico (más de {F['r_hi']} €), el {F['r_part10']}.
- El PSOE obtuvo el {F['r_psoe1']} en las secciones más pobres y el {F['r_psoe10']} en las más ricas; el PP, el {F['r_pp1']} y el {F['r_pp10']}.
- Vox sacó el {F['e_vox1']} en las secciones más jóvenes (edad media inferior a {F['e_hi1']} años) y el {F['e_vox10']} en las más envejecidas.
- En las secciones con más población extranjera (más del {F['x_lo10']}) la participación fue del {F['x_part10']}, frente al {F['x_part1']} en las que menos.
- Unos {F['sin']} adultos residentes ({F['sin_pct']}) no pueden votar en unas generales por no tener la nacionalidad española.

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
