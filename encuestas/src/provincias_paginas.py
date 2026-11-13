"""Una página por provincia: /encuestas/<provincia>/ con los escaños que da el modelo en esa circunscripción.

La llama construir.provincias() con la salida publicable del modelo (previsiones/datos/publico/), así que se rehace
cada vez que entra una encuesta. No es una encuesta provincial: las encuestadoras casi nunca publican datos por
provincia, y cada página lo dice arriba, antes de cualquier cifra.
"""
import html

import cis_provincias

UPN_PP = {'31'}   # provincias donde el PP concurre dentro de la lista UPN-PP (previsiones/src/motor.py, UPN_PP)
NOTA_UPN_PP = ('<p data-tipo="contexto">UPN y el PP van juntos el 29N en una sola candidatura, «Unión del Pueblo Navarro en coalición con el Partido Popular (UPN-PP)», '
               'al Congreso y al Senado: la encabeza Leticia San Martín (UPN) y el número dos es Sergio Sayas (PP), según las '
               '<a href="https://www.boe.es/boe/dias/2026/11/03/pdfs/BOE-A-2026-23103.pdf">candidaturas proclamadas en el BOE del 3 de noviembre</a>. '
               'Las encuestas siguen midiendo a UPN aparte del PP; el modelo suma las dos estimaciones en Navarra y reparte los escaños como una sola lista. '
               'En 2023 fueron por separado y sacaron un diputado cada uno.</p>')


def genera(d, meta, c, ruta_provincia, slug_provincia):
    """Escribe encuestas/<slug>/index.html de cada provincia. c es el módulo construir (formato y cabecera comunes).
    Devuelve [(slug, nombre)] para enlazarlas desde provincias.html y el sitemap."""
    nombres, prov = meta['provincias'], d['provincias']
    pc = c.pc
    actual = c.fecha_larga(meta['generado'])
    sims = f"{meta['simulaciones']:,}".replace(',', '.')
    indice = []
    ccaa_de = {p: ca for ca, ps in meta['ccaa'].items() for p in ps}
    for cod, v in prov.items():
        nombre, slug = nombres[cod], slug_provincia(cod)
        indice.append((slug, nombre))
        total = v['escanos_total']
        rc = c.reparto_provincia(v)   # suma exactamente `total`
        listas = sorted(v['listas'], key=lambda l: (-rc[l['lista']], -l['voto'][1]))
        con = [l for l in listas if l['escanos'][2] > 0 or rc[l['lista']] > 0]
        primero = max(v['listas'], key=lambda l: l['p_primera'])
        segundo = sorted(v['listas'], key=lambda l: -l['p_primera'])[1]
        # en Navarra el PP va con UPN en una sola lista, UPN-PP (motor.une_upn_pp): el lector la ve con su nombre
        upn_pp = cod in UPN_PP
        n = lambda l: 'UPN-PP' if upn_pp and l == 'PP' else c.nombre_lista(l)
        corto = lambda l: n(l).replace(' / Frente Amplio', '')
        art = lambda l: 'el ' if l in ('PP', 'PSOE', 'PNV', 'BNG') and not (upn_pp and l == 'PP') else ''
        pp = lambda x: f'{round(x * 100)} %' if 0.01 <= x <= 0.99 else ('menos del 1 %' if x < 0.01 else 'más del 99 %')
        en_el = lambda x: 'en ' + pp(x) if x > 0.99 or x < 0.01 else 'en el ' + pp(x)   # «en más del 99 %», no «en el más del 99 %»
        titular = f'Encuesta en {nombre}: {art(primero["lista"])}{corto(primero["lista"])} saldría primero {en_el(primero["p_primera"])} de las simulaciones'
        cis_tit = cis_provincias.titular(cod, primero['lista'])
        if cis_tit:   # Nacho, 13-11-2026: el CIS preelectoral también en el titular
            titular += '; ' + cis_tit
        ent = cis_provincias.entrevistas(cod)
        cis_dek = ('' if not ent else
                   f' Y la horquilla del CIS preelectoral, con {"solo " if ent < 300 else ""}{cis_provincias.miles(ent)} entrevistas en {nombre}'
                   + (', una muestra muy pequeña.' if ent < 300 else '.'))
        titulo_seo = f'Encuesta {nombre} elecciones generales 2026: escaños según la media de encuestas' + (' y el CIS' if ent else '')
        reparto = ', '.join(f'{corto(l["lista"])} {rc[l["lista"]]}' + (f' (entre {l["escanos"][0]} y {l["escanos"][2]})' if l['escanos'][0] != l['escanos'][2] else '')
                            for l in con)
        p1 = (f'{nombre} elige {total} diputado{"s" if total > 1 else ""} el 29 de noviembre. Con la media de las encuestas nacionales repartida por provincia, '
              f'el reparto central es {reparto}. Entre paréntesis, el intervalo del 80 % de las simulaciones.')
        p2 = (f'{art(primero["lista"]).capitalize()}{corto(primero["lista"])} queda primero {en_el(primero["p_primera"])} de las {sims} simulaciones, '
              f'y {art(segundo["lista"])}{corto(segundo["lista"])}, {en_el(segundo["p_primera"])}.')
        en_aire = [l for l in con if l['escanos'][2] > l['escanos'][0]]
        p3 = ''
        if en_aire:
            p3 = ('Los escaños que más bailan: ' + '; '.join(f'{corto(l["lista"])} saca entre {l["escanos"][0]} y {l["escanos"][2]}' for l in en_aire[:4])
                  + '. Una diferencia de un punto en la provincia puede mover un escaño de un partido a otro.')
        else:
            p3 = 'En todas las simulaciones del intervalo del 80 % el reparto es el mismo: es una de las provincias con menos escaños en juego.'
        filas = ''
        for l in listas:
            if l['voto'][1] < 1 and l['escanos'][2] == 0:
                continue
            esc = str(rc[l['lista']]) + (f'<small>{l["escanos"][0]}-{l["escanos"][2]}</small>' if l['escanos'][0] != l['escanos'][2] else '')
            filas += (f'<tr><td><i class="pt" style="background:{c.color_lista(l["lista"])}"></i>{html.escape(corto(l["lista"]))}</td>'
                      f'<td class="n">{pc(l["voto"][1])}<small>{str(l["voto"][0]).replace(".", ",")}-{str(l["voto"][2]).replace(".", ",")}</small></td>'
                      f'<td class="n">{esc}</td><td class="n">{pp(l["p_primera"]) if l["p_primera"] >= 0.005 else "–"}</td></tr>')
        cuad = ''.join(f'<i style="background:{c.color_lista(l["lista"])}" title="{html.escape(corto(l["lista"]))}"></i>' * rc[l['lista']] for l in con)
        # Nacho, 9-11-2026: leyenda con la correspondencia color-partido debajo de los cuadrados
        ley = ''.join(f'<span><i style="background:{c.color_lista(l["lista"])}"></i>{html.escape(corto(l["lista"]))} <b>{rc[l["lista"]]}</b></span>' for l in con if rc[l['lista']] > 0)
        vecinas = [(slug_provincia(p), nombres[p]) for p in meta['ccaa'][ccaa_de[cod]] if p != cod]
        faq = [(f'¿Cuántos diputados elige {nombre}?', f'{total}. Se reparten con la ley D\'Hondt entre las candidaturas que pasan del 3 % de los votos válidos de la provincia.'),
               (f'¿Quién gana en {nombre} según las encuestas?', p2 + ' ' + p1),
               (f'¿Hay encuestas de las generales en {nombre}?',
                'Casi nunca: las encuestadoras publican sus datos para toda España y muy rara vez por provincia. Estas cifras no son una encuesta, '
                f'sino el modelo de Mapa Electoral, que reparte la media de las encuestas nacionales por provincia y simula el resultado {sims} veces.'),
               ('¿Cada cuánto se actualiza?', 'Cada vez que entra una encuesta nueva. En los cinco días anteriores a la votación del 29N no cambia: la ley electoral prohíbe publicar sondeos esos días.')]
        url = f'{c.URL}{slug}/'
        desc = (f'Escaños de {nombre} en las generales del 29N según la media de encuestas: {reparto}. Modelo de Mapa Electoral, actualizado el {actual}.')[:300]
        imagen = f'{c.BASE}/img/compartir/encuestas.jpg?v={meta["generado"]}'
        jsonld = [{'@context': 'https://schema.org', '@type': 'AnalysisNewsArticle', '@id': url + '#articulo', 'headline': titular, 'description': desc,
                   'url': url, 'mainEntityOfPage': url, 'inLanguage': 'es', 'datePublished': '2026-10-26', 'dateModified': max(meta['generado'][:10], '2026-10-26'),
                   'image': [imagen], 'about': [{'@type': 'Thing', 'name': 'Elecciones generales de España de 2026'}, {'@type': 'AdministrativeArea', 'name': nombre}],
                   'author': {'@type': 'Person', 'name': c.AUTOR, 'url': c.BASE + '/sobre-mi.html'}, 'publisher': c.MEDIO, 'isAccessibleForFree': True},
                  {'@context': 'https://schema.org', '@type': 'FAQPage', '@id': url + '#preguntas', 'inLanguage': 'es',
                   'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]
        cuerpo = f"""<main>
<p class="kicker"><a href="../">Encuestas elecciones generales 2026</a> · <a href="../provincias.html">Por provincias</a> · {html.escape(ccaa_de[cod])}</p>
<h1 data-miga="{html.escape(nombre)}">{html.escape(titular)}</h1>
<p class="dek">{"El escaño" if total == 1 else f"Los {total} escaños"} de {html.escape(nombre)} con la media de las encuestas de las generales del 29N: reparto central, horquilla y probabilidad de quedar primero.{html.escape(cis_dek)}</p>
<p class="firma">Por <a href="../../sobre-mi.html">{c.AUTOR}</a> · Actualizado el <time datetime="{meta['generado']}">{actual}</time></p>
<p class="propio"><b>Modelo propio, no es una encuesta de {html.escape(nombre)}.</b> Las encuestadoras no publican sus datos por provincia. Estas cifras salen del modelo de Mapa Electoral, que reparte por provincia la media de las <a href="../">encuestas publicadas</a> y simula el resultado {sims} veces. <a href="../metodo-modelo.html">Cómo se calcula</a>.</p>
<p data-tipo="dato">{html.escape(p1)}</p>
<figure><figcaption><span class="t">{"El escaño" if total == 1 else f"Los {total} escaños"} de {html.escape(nombre)} en el reparto central</span><span class="s">Un cuadrado por escaño, con el color del partido que lo saca en el reparto central.</span></figcaption>
<div class="esc grande" aria-hidden="true">{cuad}</div>
<div class="ley">{ley}</div></figure>
<p data-tipo="dato">{html.escape(p2)}</p>
<p data-tipo="dato">{html.escape(p3)}</p>
{NOTA_UPN_PP if upn_pp else ''}
<h2>Voto y escaños de cada partido en {html.escape(nombre)}</h2>
<div class="tbl"><table><thead><tr><th>Partido</th><th class="n">Voto (80 %)</th><th class="n">Escaños (80 %)</th><th class="n">Primero</th></tr></thead><tbody>{filas}</tbody></table></div>
<p class="src">Cifra grande: reparto central, la mediana de las simulaciones ajustada para que sume los escaños de la provincia; debajo, el intervalo del 80 %. {html.escape(meta.get('aviso', ''))} <a href="../../{ruta_provincia(cod)}">Resultados de 2023 en {html.escape(nombre)}, sección a sección →</a></p>
{cis_provincias.bloque(cod, nombre, rc, total, c, n)}<h2>Preguntas frecuentes</h2>
<div class="faq">{''.join(f'<details><summary><h3>{html.escape(q)}</h3></summary><p>{html.escape(a)}</p></details>' for q, a in faq)}</div>
{f'<h2>Otras provincias de {html.escape(ccaa_de[cod])}</h2><ul class="casas">' + ''.join(f'<li><a href="../{s}/">{html.escape(nm)}</a></li>' for s, nm in vecinas) + '</ul>' if vecinas else ''}
<h2>Sigue leyendo</h2><ul class="sigue"><li><a href="../../listas-electorales-29n/{slug}/"><span class="kicker">Listas</span><b>Los candidatos del 29N en {html.escape(nombre)}, puesto a puesto</b></a></li><li><a href="../provincias.html"><span class="kicker">Por provincias</span><b>Las 52 provincias y las más disputadas</b></a></li><li><a href="../"><span class="kicker">Encuestas</span><b>Todas las encuestas de las elecciones generales 2026 y su promedio</b></a></li><li><a href="../../actualidad/ultimo-escano-29n/"><span class="kicker">Escaños</span><b>El último escaño de cada provincia</b></a></li></ul>
<footer>Mapa Electoral · Datos con licencia <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> · <a href="../../atlas/politica-editorial/">Política editorial</a></footer>
</main>"""
        estilos = c.ESTILOS.replace('</style>', '.esc{display:flex;flex-wrap:wrap;gap:3px;margin:.6rem 0}.esc.grande i{width:18px;height:18px;border-radius:3px;display:block}'
                                    '.esc i.aire{background:var(--grid);outline:1px solid var(--rule);outline-offset:-1px}'
                                    '.ley{display:flex;flex-wrap:wrap;gap:.3rem 1rem;font-family:var(--ui);font-size:.95rem;margin:.2rem 0 0}.ley span{display:inline-flex;align-items:center;gap:.35rem}.ley i{width:14px;height:14px;border-radius:3px;display:inline-block}'
                                    '.casas{columns:2;font-family:var(--ui);font-size:.95rem;padding-left:1.1rem}@media (max-width:520px){.casas{columns:1}}</style>')
        pagina = (c.cabecera(titulo_seo, desc, url, imagen, jsonld)
                  .replace(f'<meta property="og:title" content="{html.escape(titulo_seo)}">',
                           f'<meta property="og:title" content="{html.escape(titular)}">')
                  + estilos + c.CSS_SITIO + '\n</head>\n<body>\n' + c.nav('../../', 'Encuestas') + '\n' + cuerpo + '\n</body>\n</html>\n')
        pagina = c.fechas_meta(pagina, '2026-10-26', max(meta['generado'][:10], '2026-10-26'))
        (c.SALIDA / slug).mkdir(exist_ok=True)
        (c.SALIDA / slug / 'index.html').write_text(pagina, encoding='utf-8')
    return indice
