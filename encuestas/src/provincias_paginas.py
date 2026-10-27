"""Una página por provincia: /encuestas/<provincia>/ con los escaños que da el modelo en esa circunscripción.

La llama construir.provincias() con la salida publicable del modelo (previsiones/datos/publico/), así que se rehace
cada vez que entra una encuesta. No es una encuesta provincial: las encuestadoras casi nunca publican datos por
provincia, y cada página lo dice arriba, antes de cualquier cifra.
"""
import html


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
        listas = sorted(v['listas'], key=lambda l: (-l['escanos'][1], -l['voto'][1]))
        con = [l for l in listas if l['escanos'][2] > 0]
        primero = max(v['listas'], key=lambda l: l['p_primera'])
        segundo = sorted(v['listas'], key=lambda l: -l['p_primera'])[1]
        n = c.nombre_lista
        corto = lambda l: n(l).replace(' / Frente Amplio', '')
        art = lambda l: 'el ' if l in ('PP', 'PSOE', 'PNV', 'BNG') else ''
        pp = lambda x: f'{round(x * 100)} %' if 0.01 <= x <= 0.99 else ('menos del 1 %' if x < 0.01 else 'más del 99 %')
        titular = f'Encuesta en {nombre}: {art(primero["lista"])}{corto(primero["lista"])} saldría primero en el {pp(primero["p_primera"])} de las simulaciones'
        reparto = ', '.join(f'{corto(l["lista"])} {l["escanos"][1]}' + (f' (entre {l["escanos"][0]} y {l["escanos"][2]})' if l['escanos'][0] != l['escanos'][2] else '')
                            for l in con if l['escanos'][2] > 0)
        p1 = (f'{nombre} elige {total} diputado{"s" if total > 1 else ""} el 29 de noviembre. Con la media de las encuestas nacionales repartida por provincia, '
              f'el reparto central es {reparto}. Entre paréntesis, el intervalo del 80 % de las simulaciones.')
        p2 = (f'{art(primero["lista"]).capitalize()}{corto(primero["lista"])} queda primero en el {pp(primero["p_primera"])} de las {sims} simulaciones, '
              f'y {art(segundo["lista"])}{corto(segundo["lista"])}, en el {pp(segundo["p_primera"])}.')
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
            esc = str(l['escanos'][1]) + (f'<small>{l["escanos"][0]}-{l["escanos"][2]}</small>' if l['escanos'][0] != l['escanos'][2] else '')
            filas += (f'<tr><td><i class="pt" style="background:{c.color_lista(l["lista"])}"></i>{html.escape(corto(l["lista"]))}</td>'
                      f'<td class="n">{pc(l["voto"][1])}<small>{str(l["voto"][0]).replace(".", ",")}-{str(l["voto"][2]).replace(".", ",")}</small></td>'
                      f'<td class="n">{esc}</td><td class="n">{pp(l["p_primera"]) if l["p_primera"] >= 0.005 else "–"}</td></tr>')
        cuad, k = '', 0
        for l in con:
            m = min(l['escanos'][1], total - k); k += m
            cuad += f'<i style="background:{c.color_lista(l["lista"])}" title="{html.escape(corto(l["lista"]))}"></i>' * m
        cuad += '<i class="aire"></i>' * (total - k)
        vecinas = [(slug_provincia(p), nombres[p]) for p in meta['ccaa'][ccaa_de[cod]] if p != cod]
        faq = [(f'¿Cuántos diputados elige {nombre}?', f'{total}. Se reparten con la ley D\'Hondt entre las candidaturas que pasan del 3 % de los votos válidos de la provincia.'),
               (f'¿Quién gana en {nombre} según las encuestas?', p2 + ' ' + p1),
               (f'¿Hay encuestas de las generales en {nombre}?',
                'Casi nunca: las encuestadoras publican sus datos para toda España y muy rara vez por provincia. Estas cifras no son una encuesta, '
                f'sino el modelo de Mapa Electoral, que reparte la media de las encuestas nacionales por provincia y simula el resultado {sims} veces.'),
               ('¿Cada cuánto se actualiza?', 'Cada vez que entra una encuesta nueva. Del 24 al 28 de noviembre no cambia: la ley electoral prohíbe publicar sondeos esos días.')]
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
<p class="kicker"><a href="../">Encuestas</a> · <a href="../provincias.html">Por provincias</a> · {html.escape(ccaa_de[cod])}</p>
<h1 data-miga="{html.escape(nombre)}">{html.escape(titular)}</h1>
<p class="dek">Los {total} escaños de {html.escape(nombre)} con la media de las encuestas de las generales del 29N: reparto central, horquilla y probabilidad de quedar primero.</p>
<p class="firma">Por <a href="../../sobre-mi.html">{c.AUTOR}</a> · Actualizado el <time datetime="{meta['generado']}">{actual}</time></p>
<p class="propio"><b>Modelo propio, no es una encuesta de {html.escape(nombre)}.</b> Las encuestadoras no publican sus datos por provincia. Estas cifras salen del modelo de Mapa Electoral, que reparte por provincia la media de las <a href="../">encuestas publicadas</a> y simula el resultado {sims} veces. <a href="../metodo-modelo.html">Cómo se calcula</a>.</p>
<p data-tipo="dato">{html.escape(p1)}</p>
<figure><figcaption><span class="t">Los {total} escaños de {html.escape(nombre)} en el reparto central</span><span class="s">Un cuadrado por escaño, con el color del partido que lo saca en la mediana de las simulaciones; en gris, los que quedan en el aire.</span></figcaption>
<div class="esc grande" aria-hidden="true">{cuad}</div></figure>
<p data-tipo="dato">{html.escape(p2)}</p>
<p data-tipo="dato">{html.escape(p3)}</p>
<h2>Voto y escaños de cada partido en {html.escape(nombre)}</h2>
<div class="tbl"><table><thead><tr><th>Partido</th><th class="n">Voto (80 %)</th><th class="n">Escaños (80 %)</th><th class="n">Primero</th></tr></thead><tbody>{filas}</tbody></table></div>
<p class="src">Cifra grande: mediana de las simulaciones; debajo, el intervalo del 80 %. {html.escape(meta.get('aviso', ''))} <a href="../../{ruta_provincia(cod)}">Resultados de 2023 en {html.escape(nombre)}, sección a sección →</a></p>
<h2>Preguntas frecuentes</h2>
<div class="faq">{''.join(f'<details><summary><h3>{html.escape(q)}</h3></summary><p>{html.escape(a)}</p></details>' for q, a in faq)}</div>
{f'<h2>Otras provincias de {html.escape(ccaa_de[cod])}</h2><ul class="casas">' + ''.join(f'<li><a href="../{s}/">{html.escape(nm)}</a></li>' for s, nm in vecinas) + '</ul>' if vecinas else ''}
<h2>Sigue leyendo</h2><ul class="sigue"><li><a href="../../listas-electorales-29n/{slug}/"><span class="kicker">Listas</span><b>Los candidatos del 29N en {html.escape(nombre)}, puesto a puesto</b></a></li><li><a href="../provincias.html"><span class="kicker">Por provincias</span><b>Las 52 provincias y las más disputadas</b></a></li><li><a href="../"><span class="kicker">Encuestas</span><b>Todas las encuestas de las generales y su promedio</b></a></li><li><a href="../../actualidad/ultimo-escano-29n/"><span class="kicker">Escaños</span><b>El último escaño de cada provincia</b></a></li></ul>
<footer>Mapa Electoral · Datos con licencia <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> · <a href="../../atlas/politica-editorial/">Política editorial</a></footer>
</main>"""
        estilos = c.ESTILOS.replace('</style>', '.esc{display:flex;flex-wrap:wrap;gap:3px;margin:.6rem 0}.esc.grande i{width:18px;height:18px;border-radius:3px;display:block}'
                                    '.esc i.aire{background:var(--grid);outline:1px solid var(--rule);outline-offset:-1px}'
                                    '.casas{columns:2;font-family:var(--ui);font-size:.95rem;padding-left:1.1rem}@media (max-width:520px){.casas{columns:1}}</style>')
        pagina = (c.cabecera(f'Encuesta {nombre} elecciones generales 2026: escaños según la media de encuestas', desc, url, imagen, jsonld)
                  .replace(f'<meta property="og:title" content="Encuesta {html.escape(nombre)} elecciones generales 2026: escaños según la media de encuestas">',
                           f'<meta property="og:title" content="{html.escape(titular)}">')
                  + estilos + c.CSS_SITIO + '\n</head>\n<body>\n' + c.nav('../../', 'Encuestas') + '\n' + cuerpo + '\n</body>\n</html>\n')
        (c.SALIDA / slug).mkdir(exist_ok=True)
        (c.SALIDA / slug / 'index.html').write_text(pagina, encoding='utf-8')
    return indice
