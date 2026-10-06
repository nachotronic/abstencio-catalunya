"""Metadatos para buscadores y asistentes de IA, y página de metodología.

Escribe, en las dos lenguas:
  - el bloque <!-- seo --> del <head> de index.html, ca.html y mapa.html (descripción, enlaces
    canónicos y de idioma, Open Graph y datos estructurados schema.org NewsArticle + Dataset);
  - metodologia.html y metodologia-ca.html (descarga de datos, licencia, columnas y método);
  - llms.txt, sitemap.xml y robots.txt.

Uso, siempre después de build_ca.py:  python3 src/build_ca.py && python3 src/seo.py
Si cambia una cifra o un texto de aquí, hay que cambiarlo en castellano y en catalán.
"""
import json, pathlib, re, html, datetime

CF_ANALYTICS = '''<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "d27e4ef550c94f82912044da926a3b0f"}'></script><!-- End Cloudflare Web Analytics -->'''
ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'https://nachotronic.github.io/abstencio-catalunya/'
PUBLISHED = '2026-10-05'
MODIFIED = '2026-10-06'   # cámbiala a mano cuando se actualice el contenido
# ---- Autor: página «Sobre mí» (sobre-mi.html / sobre-mi-ca.html) ----
# PENDIENTE (Nacho): enlaces (redes, web, otros trabajos).
# Mientras la biografía esté vacía, la página no la muestra. Si cambia el nombre, cámbialo también
# en la firma de src/i18n/es_body.html y ca_body.html.
AUTHOR_NAME = 'Nacho G. del Álamo'
AUTHOR_BIO = {
    'es': 'Nacho G. del Álamo es periodista de datos con amplia experiencia en diversos medios y profesor de Datos y visualizaciones en la Universitat de Girona (UdG). '
          'Ha recibido los premios Carles Rahola, Tiflos, Injuve y el Premio Nacional de Periodismo Placeat por el reportaje «Sólo el drag les hace libres».',
    'ca': 'Nacho G. del Álamo és periodista de dades amb àmplia experiència en diversos mitjans i professor de Dades i visualitzacions a la Universitat de Girona (UdG). '
          'Ha rebut els premis Carles Rahola, Tiflos, Injuve i el Premi Nacional de Periodisme Placeat pel reportatge «Sólo el drag les hace libres».',
}
AUTHOR_JOB = {'es': 'Periodista de datos', 'ca': 'Periodista de dades'}          # p. ej. «Periodista de datos»; vacío = no se muestra
AUTHOR_LINKS = [('Universitat de Girona', 'https://www.udg.edu/ca/directori/pagina-personal?ID=240543&language=es-ES'), ('LinkedIn', 'https://www.linkedin.com/in/ignacio-garc%C3%ADa-del-%C3%A1lamo-a289418/'), ('X', 'https://x.com/nachotronic'), ('GitHub', 'https://github.com/nachotronic')]   # redes sociales, web, otros trabajos
ABOUT = {'es': 'sobre-mi.html', 'ca': 'sobre-mi-ca.html'}
AUTHOR = {'@type': 'Person', '@id': BASE + 'sobre-mi.html#person', 'name': AUTHOR_NAME, 'url': BASE + 'sobre-mi.html',
          'sameAs': [u for _, u in AUTHOR_LINKS]}
LICENSE = 'https://creativecommons.org/licenses/by/4.0/'
IMAGE = BASE + 'img/portada.png'
REPO = 'https://github.com/nachotronic/abstencio-catalunya'
# Códigos de verificación de Google Search Console y Bing Webmaster Tools (solo el valor de content="...").
GOOGLE_VERIFICATION = 'M5PxiUNlQY0Orkav-c2U9AuvCfD-w7gZCWH70gfYrIQ'
BING_VERIFICATION = 'F607F994F5AE6311370EE88405916BC0'

SOURCES = [
    ('Ministerio del Interior: resultados por mesa del Congreso 2015-2023 (vía pollspain)', 'https://github.com/dadosdelaplace/pollspain'),
    ('INE: Atlas de Distribución de Renta de los Hogares 2023 (vía ineAtlas.data)', 'https://github.com/pablogguz/ineAtlas.data'),
    ('INE: Censo de Población y Viviendas 2021', 'https://www.ine.es/censos2021/'),
    ('Generalitat de Catalunya: participación por sección censal 2015-2024 (Transparència Catalunya, irrv-2mfc)', 'https://analisi.transparenciacatalunya.cat/d/irrv-2mfc'),
    ('Idescat: EMEX', 'https://www.idescat.cat/emex/'),
]

T = {
    'es': {
        'page': 'index.html', 'meth': 'metodologia.html', 'lang': 'es', 'locale': 'es_ES',
        'title': '¿Quién no vota en Cataluña? Abstención por sección censal',
        'desc': 'De cada 100 adultos que vivían en Cataluña el 23 de julio de 2023, 54 votaron, 17 no tenían derecho a voto y 29 se abstuvieron. '
                'Mapa de las 5.115 secciones censales cruzado con renta, estudios, paro, edad y población extranjera, de 2015 a 2024.',
        'keywords': ['abstención', 'participación electoral', 'Cataluña', 'sección censal', 'renta', 'población extranjera', 'Salt', 'Lloret de Mar', 'Figueres'],
        'ds_name': 'Participación y abstención por sección censal en Cataluña, 2015-2024',
        'ds_desc': 'Participación electoral de las 5.115 secciones censales de Cataluña en doce elecciones (Congreso, Parlament y municipales, 2015-2024), '
                   'con adultos residentes, adultos sin derecho a voto, renta por unidad de consumo, edad, estudios, paro y población extranjera.',
        'about': ['Abstención electoral', 'Participación electoral', 'Desigualdad'],
        'files': {
            'catalunya_secciones_2023.csv': 'Secciones censales 2023: participación, reparto de cada 100 adultos y variables sociodemográficas',
            'catalunya_municipios.csv': 'Municipios: participación y reparto de cada 100 adultos',
            'evolucion_secciones.csv': 'Participación por sección en doce elecciones, 2015-2024',
            'catalunya_secciones_historico_congreso.csv': 'Histórico del Congreso por sección (formato largo), 2015-2023',
            'catalunya_secciones_2023.geojson': 'Contornos de las secciones censales de 2023 con todas las variables',
            'girona_secciones_2023.csv': 'Secciones de la provincia de Girona',
            'girona_municipios.csv': 'Municipios de la provincia de Girona',
        },
    },
    'ca': {
        'page': 'ca.html', 'meth': 'metodologia-ca.html', 'lang': 'ca', 'locale': 'ca_ES',
        'title': 'Qui no vota a Catalunya? Abstenció per secció censal',
        'desc': 'De cada 100 adults que vivien a Catalunya el 23 de juliol de 2023, 54 van votar, 17 no tenien dret a vot i 29 es van abstenir. '
                'Mapa de les 5.115 seccions censals creuat amb la renda, els estudis, l\'atur, l\'edat i la població estrangera, del 2015 al 2024.',
        'keywords': ['abstenció', 'participació electoral', 'Catalunya', 'secció censal', 'renda', 'població estrangera', 'Salt', 'Lloret de Mar', 'Figueres'],
        'ds_name': 'Participació i abstenció per secció censal a Catalunya, 2015-2024',
        'ds_desc': 'Participació electoral de les 5.115 seccions censals de Catalunya en dotze eleccions (Congrés, Parlament i municipals, 2015-2024), '
                   'amb adults residents, adults sense dret a vot, renda per unitat de consum, edat, estudis, atur i població estrangera.',
        'about': ['Abstenció electoral', 'Participació electoral', 'Desigualtat'],
        'files': {
            'catalunya_secciones_2023.csv': 'Seccions censals 2023: participació, repartiment de cada 100 adults i variables sociodemogràfiques',
            'catalunya_municipios.csv': 'Municipis: participació i repartiment de cada 100 adults',
            'evolucion_secciones.csv': 'Participació per secció en dotze eleccions, 2015-2024',
            'catalunya_secciones_historico_congreso.csv': 'Històric del Congrés per secció (format llarg), 2015-2023',
            'catalunya_secciones_2023.geojson': 'Contorns de les seccions censals del 2023 amb totes les variables',
            'girona_secciones_2023.csv': 'Seccions de la província de Girona',
            'girona_municipios.csv': 'Municipis de la província de Girona',
        },
    },
}
MAPA = {
    'title': '¿Quién no vota en Cataluña? Mapa interactivo',
    'desc': 'Mapa interactivo en 2D de la abstención en las 5.115 secciones censales de Cataluña, con gráficos por renta, estudios, paro y población extranjera.',
}


def dataset(L):
    t = T[L]
    return {
        '@type': 'Dataset', '@id': BASE + t['meth'] + '#dataset',
        'name': t['ds_name'], 'description': t['ds_desc'], 'inLanguage': L,
        'url': BASE + t['meth'], 'sameAs': REPO,
        'creator': AUTHOR, 'license': LICENSE, 'isAccessibleForFree': True,
        'datePublished': PUBLISHED, 'dateModified': MODIFIED,
        'temporalCoverage': '2015-05-24/2024-05-12',
        'spatialCoverage': {'@type': 'Place', 'name': 'Catalunya', 'geo': {'@type': 'GeoShape', 'box': '40.52 0.15 42.86 3.33'}},
        'keywords': t['keywords'],
        'variableMeasured': ['turnout', 'pct_ad_vota', 'pct_ad_sinderecho', 'pct_ad_abst', 'net_income_equiv', 'mean_age',
                             'pct_foreign', 'pct_higher_ed_completed', 'unemployment_rate', 'indep_share19', 'drop_19_23'],
        'isBasedOn': [u for _, u in SOURCES],
        'distribution': [{'@type': 'DataDownload', 'name': f, 'description': d,
                          'encodingFormat': 'application/geo+json' if f.endswith('.geojson') else 'text/csv',
                          'contentUrl': BASE + 'data/' + f} for f, d in t['files'].items()],
    }


def article(L):
    t = T[L]
    return {
        '@type': 'NewsArticle', '@id': BASE + t['page'] + '#article',
        'headline': t['title'], 'description': t['desc'], 'inLanguage': L,
        'url': BASE + t['page'], 'mainEntityOfPage': BASE + t['page'], 'image': IMAGE,
        'datePublished': PUBLISHED, 'dateModified': MODIFIED,
        'author': AUTHOR, 'publisher': AUTHOR, 'license': LICENSE,
        'isAccessibleForFree': True, 'keywords': t['keywords'], 'about': t['about'],
        'contentLocation': {'@type': 'Place', 'name': 'Catalunya'},
        'citation': [u for _, u in SOURCES],
        'isBasedOn': {'@id': BASE + t['meth'] + '#dataset'},
        'translationOfWork' if L == 'ca' else 'workTranslation': {'@id': BASE + T['ca' if L == 'es' else 'es']['page'] + '#article'},
    }


def faq_items(page):
    """Preguntas y respuestas del <section id="faq"> de la página (h3 + p), para no duplicar el texto."""
    s = (ROOT / page).read_text(encoding='utf-8')
    sec = s[s.index('<section id="faq">'):]
    sec = sec[:sec.index('</section>')]
    strip = lambda x: html.unescape(re.sub(r'<[^>]+>', '', x)).strip()
    return [(strip(q), strip(a)) for q, a in re.findall(r'<h3>(.*?)</h3>\s*<p>(.*?)</p>', sec, re.S)]


def faqpage(L):
    t = T[L]
    return {'@type': 'FAQPage', '@id': BASE + t['page'] + '#faq', 'inLanguage': L, 'isPartOf': {'@id': BASE + t['page'] + '#article'},
            'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq_items(t['page'])]}


def ld(*items):
    s = json.dumps({'@context': 'https://schema.org', '@graph': list(items)}, ensure_ascii=False, indent=1)
    return '<script type="application/ld+json">\n' + s.replace('</', '<\\/') + '\n</script>'


def meta(title, desc, url, lang, locale, alternates, ldjson, typ='article'):
    e = html.escape
    out = [f'<meta name="description" content="{e(desc)}">',
           f'<meta name="author" content="{AUTHOR_NAME}">',
           '<meta name="robots" content="index, follow, max-image-preview:large">',
           f'<link rel="canonical" href="{url}">']
    if GOOGLE_VERIFICATION: out.append(f'<meta name="google-site-verification" content="{GOOGLE_VERIFICATION}">')
    if BING_VERIFICATION: out.append(f'<meta name="msvalidate.01" content="{BING_VERIFICATION}">')
    out += [f'<link rel="alternate" hreflang="{h}" href="{u}">' for h, u in alternates]
    out += [f'<meta property="og:type" content="{typ}">', f'<meta property="og:title" content="{e(title)}">',
            f'<meta property="og:description" content="{e(desc)}">', f'<meta property="og:url" content="{url}">',
            f'<meta property="og:image" content="{IMAGE}">', f'<meta property="og:locale" content="{locale}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<link rel="license" href="{LICENSE}">',
            '<link rel="alternate" type="text/plain" title="llms.txt" href="llms.txt">',
            ldjson, CF_ANALYTICS]
    return '<!-- seo -->\n' + '\n'.join(out) + '\n<!-- /seo -->'


def inject(path, block):
    s = path.read_text(encoding='utf-8')
    s = re.sub(r'\n<!-- seo -->.*?<!-- /seo -->', '', s, flags=re.S)
    i = s.index('</title>', s.index('<head>')) + len('</title>')
    path.write_text(s[:i] + '\n' + block + s[i:], encoding='utf-8')


ALT = [('es', BASE + 'index.html'), ('ca', BASE + 'ca.html'), ('x-default', BASE + 'index.html')]
ALT_M = [('es', BASE + 'metodologia.html'), ('ca', BASE + 'metodologia-ca.html'), ('x-default', BASE + 'metodologia.html')]

# ---------- página de metodología ----------
COLS = {
 'es': [
  ('tract_code', 'Código INE de la sección censal (10 dígitos: provincia, municipio, distrito y sección).'),
  ('mun_code, mun_name', 'Código INE (5 dígitos) y nombre del municipio.'),
  ('electorate, voters, mesas', 'Censo electoral, votantes y número de mesas en el Congreso de julio de 2023.'),
  ('turnout', 'Participación oficial en el Congreso 2023: votantes / censo (0 a 1).'),
  ('t2015_12, t2016_06, t2019_04, t2019_11, t2023_07', 'Participación en cada elección al Congreso (0 a 1). Vacía si el código de sección cambió.'),
  ('population, adults', 'Población residente (Atlas 2023) y adultos estimados con el % de menores de 18.'),
  ('sin_derecho, abst', 'Adultos sin derecho a voto (adultos − censo, mínimo 0) y censados que no votaron.'),
  ('pct_ad_vota, pct_ad_sinderecho, pct_ad_abst', 'De cada adulto residente: votó, no tenía derecho, pudo votar y no votó (0 a 1; suman 1).'),
  ('net_income_pc, net_income_equiv, median_income_equiv', 'Renta neta media por persona, por unidad de consumo y mediana por unidad de consumo, en euros (Atlas INE, 2023).'),
  ('mean_age, pct_under18, pct_over65, pct_single_hh, pct_spanish', 'Edad media y porcentajes de menores, mayores de 65, hogares unipersonales y población española (Atlas INE, de 0 a 100).'),
  ('pct_foreign, pct_foreign_born, pct_naturalized', 'Extranjeros, nacidos en el extranjero y españoles nacidos fuera (Censo 2021, de 0 a 1).'),
  ('pct_higher_ed_completed, unemployment_rate, pct_rented, pct_secondary', 'Adultos con estudios superiores, tasa de paro, viviendas de alquiler y viviendas secundarias (Censo 2021, de 0 a 1).'),
  ('ind19, voters19, ind23', 'Votos a ERC, Junts y CUP en noviembre de 2019, votantes de noviembre de 2019 y votos a esos partidos en 2023.'),
  ('indep_share19, indep_share23, drop_19_23', 'Voto independentista sobre votos emitidos en 2019 y 2023, y caída de participación entre noviembre de 2019 y julio de 2023 (0 a 1).'),
 ],
 'ca': [
  ('tract_code', 'Codi INE de la secció censal (10 xifres: província, municipi, districte i secció).'),
  ('mun_code, mun_name', 'Codi INE (5 xifres) i nom del municipi.'),
  ('electorate, voters, mesas', 'Cens electoral, votants i nombre de meses al Congrés de juliol del 2023.'),
  ('turnout', 'Participació oficial al Congrés 2023: votants / cens (de 0 a 1).'),
  ('t2015_12, t2016_06, t2019_04, t2019_11, t2023_07', 'Participació a cada elecció al Congrés (de 0 a 1). Buida si el codi de secció va canviar.'),
  ('population, adults', 'Població resident (Atlas 2023) i adults estimats amb el % de menors de 18 anys.'),
  ('sin_derecho, abst', 'Adults sense dret a vot (adults − cens, mínim 0) i censats que no van votar.'),
  ('pct_ad_vota, pct_ad_sinderecho, pct_ad_abst', 'De cada adult resident: va votar, no tenia dret, podia votar i no va votar (de 0 a 1; sumen 1).'),
  ('net_income_pc, net_income_equiv, median_income_equiv', 'Renda neta mitjana per persona, per unitat de consum i mediana per unitat de consum, en euros (Atlas INE, 2023).'),
  ('mean_age, pct_under18, pct_over65, pct_single_hh, pct_spanish', 'Edat mitjana i percentatges de menors, majors de 65 anys, llars unipersonals i població espanyola (Atlas INE, de 0 a 100).'),
  ('pct_foreign, pct_foreign_born, pct_naturalized', 'Estrangers, nascuts a l\'estranger i espanyols nascuts fora (Cens 2021, de 0 a 1).'),
  ('pct_higher_ed_completed, unemployment_rate, pct_rented, pct_secondary', 'Adults amb estudis superiors, taxa d\'atur, habitatges de lloguer i habitatges secundaris (Cens 2021, de 0 a 1).'),
  ('ind19, voters19, ind23', 'Vots a ERC, Junts i la CUP el novembre del 2019, votants del novembre del 2019 i vots a aquests partits el 2023.'),
  ('indep_share19, indep_share23, drop_19_23', 'Vot independentista sobre vots emesos el 2019 i el 2023, i caiguda de participació entre el novembre del 2019 i el juliol del 2023 (de 0 a 1).'),
 ],
}

M = {
 'es': dict(
  title='Metodología y datos · ¿Quién no vota en Cataluña?',
  desc='Datos abiertos (CSV y GeoJSON, CC BY 4.0), columnas, fuentes y método del análisis de la abstención por sección censal en Cataluña, 2015-2024.',
  h1='Metodología y datos', back='← Volver a la pieza', other='Català', kicker='¿Quién no vota en Cataluña?',
  intro='Esta página acompaña a <a href="index.html">«¿Quién no vota en Cataluña?»</a>. Aquí están los datos que usa, con licencia libre, lo que mide cada columna y cómo se ha calculado.',
  h_dl='Descargar los datos', h_lic='Licencia y cómo citar',
  lic='Los datos elaborados se publican con licencia <a href="https://creativecommons.org/licenses/by/4.0/deed.es" rel="license">Creative Commons Atribución 4.0 (CC BY 4.0)</a>: se pueden reutilizar, también con fines comerciales, citando la fuente. Los datos de origen mantienen las condiciones de sus organismos (Ministerio del Interior, INE, Generalitat de Catalunya). Las fotos de la pieza tienen su propia licencia, indicada al pie de cada una.',
  cite='Cita sugerida: ' + AUTHOR_NAME + ', «¿Quién no vota en Cataluña? Abstención por sección censal», 2026, ' + BASE + 'index.html. Datos: ' + REPO + '.',
  h_what='Qué mide', what=[
   'Para cada sección censal se reparten los adultos residentes en tres grupos: los que votaron, los que no tenían derecho a voto y los que podían votar y no lo hicieron.',
   '<b>Votó</b>: votos emitidos en el Congreso del 23 de julio de 2023, sin voto de residentes en el extranjero (CERA).',
   '<b>Sin derecho a voto</b>: adultos residentes menos censo electoral. En unas generales solo votan los españoles.',
   '<b>No votó</b>: el resto, es decir, la abstención entre quienes sí podían votar. La participación oficial (votos / censo) solo mide este grupo.',
   'Los adultos se estiman con la población y el porcentaje de menores de 18 del Atlas de Distribución de Renta del INE de 2023.'],
  h_key='Cifras clave', key=[
   'Cataluña, 23 de julio de 2023: de cada 100 adultos residentes, 54 votaron, 17 no tenían derecho a voto y 29 podían votar y no lo hicieron.',
   'Participación oficial: 65% en el Congreso 2023, 56% en las municipales 2023 y 58% en el Parlament 2024.',
   'Salt: 34 de cada 100 adultos votaron y 39 no podían votar, el valor más bajo entre los municipios catalanes de más de 20.000 habitantes.',
   'La sección con menos participación de Cataluña está en Figueres: un 22%.',
   'Diferencia de participación entre el decil de secciones más rico y el más pobre: 18 puntos en el Congreso 2023, 19 en las municipales 2023 y 24 en el Parlament 2024.',
   'Un modelo con renta, edad, estudios, paro, población extranjera y vivienda explica el 72% de las diferencias de participación entre secciones. Los estudios son la variable que más pesa, seguida del paro.'],
  h_model='Modelo', model='Regresión lineal de la participación de 2023 sobre las variables sociodemográficas de cada sección, ponderada por censo (5.041 secciones con todos los datos). Los coeficientes se expresan en puntos de participación por cada desviación típica de la variable, con intervalos de confianza del 95% por bootstrap (500 réplicas).',
  h_src='Fuentes', h_lim='Limitaciones',
  lim=['Son datos por sección, no por persona: indican dónde se vota menos, no quién.',
       'El censo electoral de julio y la población de enero no son exactamente la misma foto. Donde el censo supera a los adultos estimados, el grupo «sin derecho a voto» se pone a cero.',
       'Las secciones de otros años solo se comparan con las de 2023 si tienen el mismo código y un censo parecido (entre dos tercios y vez y media).',
       'El Censo 2021 no cubre 73 secciones creadas después y el Atlas no da renta por unidad de consumo en 30.',
       'En las municipales votan además los ciudadanos de la UE y de algunos países con convenio inscritos en el censo, lo que reduce el grupo «sin derecho a voto».'],
  h_cols='Columnas de catalunya_secciones_2023.csv', cols_note='Los mismos nombres se usan en el resto de archivos. En evolucion_secciones.csv cada columna es una elección: M = municipales, A = Parlament, G = Congreso, seguida del año y la vuelta del año (G20192 = Congreso de noviembre de 2019).',
  dates='Publicada el 5 de octubre de 2026 · Actualizada el 6 de octubre de 2026',
  h_auth='Autoría y revisión', auth='Datos, texto y gráficos de <a href="sobre-mi.html">Nacho G. del Álamo</a>, que también revisa los datos y el texto antes de publicar. Cada cifra del texto se recalcula con un script a partir de los datos publicados, y los totales se contrastan con los resultados oficiales de la Generalitat.',
  h_fix='Correcciones', fix=['<b>6 de octubre de 2026:</b> en la sección de Figueres con menos participación el paro es del 59% (58,5%), no del 58%; el voto independentista de 2023 era el 28% contando al PDeCAT, pero ERC, Junts y la CUP suman el 27%; en el Parlament de 2015 la distancia entre el 20% de secciones más ricas y el 20% más pobre era de 13 puntos, no de 14; el Censo 2021 no cubre 73 secciones (no 74) y el Atlas no da renta por unidad de consumo en 30 (no 20). Ninguna cambia las conclusiones.'],
  h_code='Código', code='Los scripts en Python con los que se han generado los datos y las páginas están en <a href="' + REPO + '">el repositorio de GitHub</a>, carpeta <code>src/</code>.',
  th=('Columna', 'Qué es')),
 'ca': dict(
  title='Metodologia i dades · Qui no vota a Catalunya?',
  desc='Dades obertes (CSV i GeoJSON, CC BY 4.0), columnes, fonts i mètode de l\'anàlisi de l\'abstenció per secció censal a Catalunya, 2015-2024.',
  h1='Metodologia i dades', back='← Tornar a la peça', other='Español', kicker='Qui no vota a Catalunya?',
  intro='Aquesta pàgina acompanya <a href="ca.html">«Qui no vota a Catalunya?»</a>. Aquí hi ha les dades que fa servir, amb llicència lliure, què mesura cada columna i com s\'ha calculat.',
  h_dl='Descarregar les dades', h_lic='Llicència i com citar',
  lic='Les dades elaborades es publiquen amb llicència <a href="https://creativecommons.org/licenses/by/4.0/deed.ca" rel="license">Creative Commons Reconeixement 4.0 (CC BY 4.0)</a>: es poden reutilitzar, també amb finalitats comercials, citant-ne la font. Les dades d\'origen mantenen les condicions dels seus organismes (Ministeri de l\'Interior, INE, Generalitat de Catalunya). Les fotos de la peça tenen la seva pròpia llicència, indicada al peu de cadascuna.',
  cite='Cita suggerida: ' + AUTHOR_NAME + ', «Qui no vota a Catalunya? Abstenció per secció censal», 2026, ' + BASE + 'ca.html. Dades: ' + REPO + '.',
  h_what='Què mesura', what=[
   'Per a cada secció censal es reparteixen els adults residents en tres grups: els que van votar, els que no tenien dret a vot i els que podien votar i no ho van fer.',
   '<b>Va votar</b>: vots emesos al Congrés del 23 de juliol de 2023, sense el vot dels residents a l\'estranger (CERA).',
   '<b>Sense dret a vot</b>: adults residents menys cens electoral. En unes generals només voten els espanyols.',
   '<b>No va votar</b>: la resta, és a dir, l\'abstenció entre els qui sí que podien votar. La participació oficial (vots / cens) només mesura aquest grup.',
   'Els adults s\'estimen amb la població i el percentatge de menors de 18 anys de l\'Atlas de Distribució de Renda de les Llars de l\'INE del 2023.'],
  h_key='Xifres clau', key=[
   'Catalunya, 23 de juliol de 2023: de cada 100 adults residents, 54 van votar, 17 no tenien dret a vot i 29 podien votar i no ho van fer.',
   'Participació oficial: 65% al Congrés 2023, 56% a les municipals 2023 i 58% al Parlament 2024.',
   'Salt: 34 de cada 100 adults van votar i 39 no podien votar, el valor més baix entre els municipis catalans de més de 20.000 habitants.',
   'La secció amb menys participació de Catalunya és a Figueres: un 22%.',
   'Diferència de participació entre el decil de seccions més ric i el més pobre: 18 punts al Congrés 2023, 19 a les municipals 2023 i 24 al Parlament 2024.',
   'Un model amb renda, edat, estudis, atur, població estrangera i habitatge explica el 72% de les diferències de participació entre seccions. Els estudis són la variable que més pesa, seguida de l\'atur.'],
  h_model='Model', model='Regressió lineal de la participació del 2023 sobre les variables sociodemogràfiques de cada secció, ponderada pel cens (5.041 seccions amb totes les dades). Els coeficients s\'expressen en punts de participació per cada desviació típica de la variable, amb intervals de confiança del 95% per bootstrap (500 rèpliques).',
  h_src='Fonts', h_lim='Limitacions',
  lim=['Són dades per secció, no per persona: indiquen on es vota menys, no qui.',
       'El cens electoral de juliol i la població de gener no són exactament la mateixa foto. On el cens supera els adults estimats, el grup «sense dret a vot» es posa a zero.',
       'Les seccions d\'altres anys només es comparen amb les del 2023 si tenen el mateix codi i un cens semblant (entre dos terços i una vegada i mitja).',
       'El Cens 2021 no cobreix 73 seccions creades després i l\'Atlas no dona renda per unitat de consum en 30.',
       'A les municipals també voten els ciutadans de la UE i d\'alguns països amb conveni inscrits al cens, cosa que redueix el grup «sense dret a vot».'],
  h_cols='Columnes de catalunya_secciones_2023.csv', cols_note='Els mateixos noms es fan servir a la resta de fitxers. A evolucion_secciones.csv cada columna és una elecció: M = municipals, A = Parlament, G = Congrés, seguida de l\'any i la volta de l\'any (G20192 = Congrés de novembre del 2019).',
  dates='Publicada el 5 d\'octubre de 2026 · Actualitzada el 6 d\'octubre de 2026',
  h_auth='Autoria i revisió', auth='Dades, text i gràfics de <a href="sobre-mi-ca.html">Nacho G. del Álamo</a>, que també en revisa les dades i el text abans de publicar. Cada xifra del text es recalcula amb un script a partir de les dades publicades, i els totals es contrasten amb els resultats oficials de la Generalitat.',
  h_fix='Correccions', fix=['<b>6 d\'octubre de 2026:</b> a la secció de Figueres amb menys participació l\'atur és del 59% (58,5%), no del 58%; el vot independentista del 2023 era el 28% comptant-hi el PDeCAT, però ERC, Junts i la CUP sumen el 27%; al Parlament del 2015 la distància entre el 20% de seccions més riques i el 20% més pobre era de 13 punts, no de 14; el Cens 2021 no cobreix 73 seccions (no 74) i l\'Atlas no dona renda per unitat de consum en 30 (no 20). Cap no canvia les conclusions.'],
  h_code='Codi', code='Els scripts en Python amb què s\'han generat les dades i les pàgines són al <a href="' + REPO + '">repositori de GitHub</a>, carpeta <code>src/</code>.',
  th=('Columna', 'Què és')),
}

CSS = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Newsreader:opsz,wght@6..72,400;6..72,500&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{--bg:#f4f5f8;--methbg:#e8ebf3;--surface:#fff;--fg:#161a2b;--muted:#5b6178;--rule:#d9dce6;--accent:#3846a0;
  --display:"Bricolage Grotesque","Arial Narrow",system-ui,sans-serif;--body:"Newsreader",Georgia,serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#12141d;--methbg:#1b1e2b;--surface:#1a1d29;--fg:#e8eaf2;--muted:#9aa0b8;--rule:#2c3042;--accent:#8f9cf0;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#12141d;--methbg:#1b1e2b;--surface:#1a1d29;--fg:#e8eaf2;--muted:#9aa0b8;--rule:#2c3042;--accent:#8f9cf0;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--body);font-size:1.08rem;line-height:1.6;padding:0 16px 64px}
body.meth{background:var(--methbg);font-size:1rem}
main{max-width:72ch;margin:0 auto}
nav{display:flex;justify-content:space-between;gap:12px;padding:20px 0;font-family:var(--mono);font-size:.82rem}
a{color:var(--accent)}
h1,h2{font-family:var(--display);line-height:1.1;text-wrap:balance}
h1{font-size:clamp(2rem,6vw,3.2rem);font-weight:800;margin:.4rem 0 1rem}
h2{font-size:1.4rem;margin:2.4rem 0 .6rem}
.kicker{font-family:var(--mono);font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
ul{padding-left:1.2rem}li{margin:.35rem 0}
code,td:first-child{font-family:var(--mono);font-size:.84rem}
.tbl{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.95rem}
th,td{text-align:left;vertical-align:top;padding:8px 10px 8px 0;border-bottom:1px solid var(--rule)}
th{font-family:var(--mono);font-size:.78rem;color:var(--muted);font-weight:500}
.cite{background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:12px 14px}
</style>'''


def methodology(L):
    m, t = M[L], T[L]
    e = html.escape
    other_L = 'ca' if L == 'es' else 'es'
    sizes = {f: (ROOT / 'data' / f).stat().st_size for f in t['files']}
    def sz(n): return f'{n/1e6:.1f} MB'.replace('.', ',') if n >= 1e6 else f'{round(n/1e3)} kB'
    dl = '\n'.join(f'<li><a href="data/{f}" download>{f}</a> · {d} · {sz(sizes[f])}</li>' for f, d in t['files'].items())
    cols = '\n'.join(f'<tr><td>{c}</td><td>{d}</td></tr>' for c, d in COLS[L])
    src = '\n'.join(f'<li><a href="{u}">{n}</a></li>' for n, u in SOURCES)
    li = lambda xs: '\n'.join(f'<li>{x}</li>' for x in xs)
    head = meta(m['title'], m['desc'], BASE + t['meth'], L, t['locale'], ALT_M, ld(dataset(L)), typ='website')
    return f'''<!doctype html>
<html lang="{L}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(m['title'])}</title>
{head}
{CSS}
</head>
<body class="meth">
<main>
<nav><a href="{t['page']}">{m['back']}</a><a href="{T[other_L]['meth']}" hreflang="{other_L}" lang="{other_L}">{m['other']}</a></nav>
<div class="kicker">{m['kicker']}</div>
<h1>{m['h1']}</h1>
<p class="kicker">{m['dates']}</p>
<p>{m['intro']}</p>
<h2>{m['h_dl']}</h2>
<ul>
{dl}
</ul>
<h2>{m['h_lic']}</h2>
<p>{m['lic']}</p>
<p class="cite">{e(m['cite'])}</p>
<h2>{m['h_key']}</h2>
<ul>
{li(m['key'])}
</ul>
<h2>{m['h_what']}</h2>
<ul>
{li(m['what'])}
</ul>
<h2>{m['h_model']}</h2>
<p>{m['model']}</p>
<h2>{m['h_src']}</h2>
<ul>
{src}
</ul>
<h2>{m['h_lim']}</h2>
<ul>
{li(m['lim'])}
</ul>
<h2>{m['h_cols']}</h2>
<div class="tbl"><table>
<thead><tr><th>{m['th'][0]}</th><th>{m['th'][1]}</th></tr></thead>
<tbody>
{cols}
</tbody></table></div>
<p>{m['cols_note']}</p>
<h2>{m['h_auth']}</h2>
<p>{m['auth']}</p>
<h2>{m['h_fix']}</h2>
<ul>
{li(m['fix'])}
</ul>
<h2>{m['h_code']}</h2>
<p>{m['code']}</p>
</main>
</body>
</html>
'''


AB = {
 'es': dict(title='Sobre mí', back='← Volver a la pieza', other='Català', h_work='Trabajos', h_links='Enlaces',
            works=[('index.html', '¿Quién no vota en Cataluña? Abstención por sección censal', 'Octubre de 2026'),
                   ('metodologia.html', 'Metodología y datos abiertos de la pieza', 'Octubre de 2026')]),
 'ca': dict(title='Sobre mi', back='← Tornar a la peça', other='Español', h_work='Treballs', h_links='Enllaços',
            works=[('ca.html', 'Qui no vota a Catalunya? Abstenció per secció censal', 'Octubre del 2026'),
                   ('metodologia-ca.html', 'Metodologia i dades obertes de la peça', 'Octubre del 2026')]),
}
ALT_A = [('es', BASE + 'sobre-mi.html'), ('ca', BASE + 'sobre-mi-ca.html'), ('x-default', BASE + 'sobre-mi.html')]


def about(L):
    a, t, e = AB[L], T[L], html.escape
    other_L = 'ca' if L == 'es' else 'es'
    person = dict(AUTHOR)
    if AUTHOR_JOB[L]: person['jobTitle'] = AUTHOR_JOB[L]
    if AUTHOR_BIO[L]: person['description'] = AUTHOR_BIO[L]
    page = {'@type': 'ProfilePage', '@id': BASE + ABOUT[L], 'url': BASE + ABOUT[L], 'inLanguage': L,
            'name': f"{a['title']} · {AUTHOR_NAME}", 'dateModified': MODIFIED, 'mainEntity': person}
    desc = AUTHOR_BIO[L] or f"{AUTHOR_NAME}: {a['works'][0][1]}."
    head = meta(f"{a['title']} · {AUTHOR_NAME}", desc, BASE + ABOUT[L], L, t['locale'], ALT_A, ld(page), typ='profile')
    job = f'<p class="kicker">{e(AUTHOR_JOB[L])}</p>\n' if AUTHOR_JOB[L] else ''
    bio = f'<p>{e(AUTHOR_BIO[L])}</p>\n' if AUTHOR_BIO[L] else ''
    works = '\n'.join(f'<li><a href="{u}">{e(n)}</a> · {d}</li>' for u, n, d in a['works'])
    links = '\n'.join(f'<li><a href="{e(u)}" rel="me">{e(n)}</a></li>' for n, u in AUTHOR_LINKS)
    return f'''<!doctype html>
<html lang="{L}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(a['title'])} · {e(AUTHOR_NAME)}</title>
{head}
{CSS}
</head>
<body>
<main>
<nav><a href="{t['page']}">{a['back']}</a><a href="{ABOUT[other_L]}" hreflang="{other_L}" lang="{other_L}">{a['other']}</a></nav>
{job}<h1>{e(AUTHOR_NAME)}</h1>
{bio}<h2>{a['h_work']}</h2>
<ul>
{works}
</ul>
<h2>{a['h_links']}</h2>
<ul>
{links}
</ul>
</main>
</body>
</html>
'''


def llms():
    es, ca = M['es'], M['ca']
    files = '\n'.join(f'- [{f}]({BASE}data/{f}): {d}' for f, d in T['es']['files'].items())
    src = '\n'.join(f'- [{n}]({u})' for n, u in SOURCES)
    key = '\n'.join(f'- {x}' for x in es['key'])
    faq = '\n\n'.join(f'### {q}\n\n{a}' for q, a in faq_items('index.html'))
    return f'''# ¿Quién no vota en Cataluña? / Qui no vota a Catalunya?

> {T['es']['desc']}

Pieza de datos bilingüe (castellano y catalán) sobre la abstención electoral en Cataluña por sección censal, 2015-2024. Autor: [{AUTHOR_NAME}]({AUTHOR['url']}). Publicada el {PUBLISHED}; actualizada el {MODIFIED}. Datos con licencia CC BY 4.0: se pueden citar y reutilizar indicando la fuente.

## Cifras clave

{key}

## Preguntas frecuentes

{faq}

## Páginas

- [Pieza en castellano]({BASE}index.html): texto completo con mapa 3D y gráficos.
- [Peça en català]({BASE}ca.html): el mismo texto en catalán.
- [Metodología y datos]({BASE}metodologia.html): descarga, licencia, columnas, fuentes y limitaciones.
- [Metodologia i dades]({BASE}metodologia-ca.html): la misma página en catalán.
- [Mapa interactivo 2D]({BASE}mapa.html)
- [Sobre el autor]({BASE}sobre-mi.html)

## Datos (CSV y GeoJSON)

{files}

## Fuentes

{src}

## Optional

- [Código fuente]({REPO})
'''


def sitemap():
    pages = [('index.html', '1.0'), ('ca.html', '1.0'), ('metodologia.html', '0.6'), ('metodologia-ca.html', '0.6'), ('mapa.html', '0.5'), ('sobre-mi.html', '0.3'), ('sobre-mi-ca.html', '0.3'), ('generales-2026/', '0.9'), ('generales-2026/metodologia.html', '0.5')]
    pairs = {'index.html': ALT, 'ca.html': ALT, 'metodologia.html': ALT_M, 'metodologia-ca.html': ALT_M, 'sobre-mi.html': ALT_A, 'sobre-mi-ca.html': ALT_A}
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for p, pr in pages:
        out.append(f'  <url><loc>{BASE}{p}</loc><lastmod>{MODIFIED}</lastmod><priority>{pr}</priority>')
        out += [f'    <xhtml:link rel="alternate" hreflang="{h}" href="{u}"/>' for h, u in pairs.get(p, [])]
        out.append('  </url>')
    return '\n'.join(out + ['</urlset>', ''])


ROBOTS = f'''# Se permite el acceso a buscadores y a asistentes de IA.
User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: CCBot
Allow: /

Sitemap: {BASE}sitemap.xml
Sitemap: {BASE}atlas/sitemap.xml
'''


def main():
    for L in ('es', 'ca'):
        t = T[L]
        inject(ROOT / t['page'], meta(t['title'], t['desc'], BASE + t['page'], L, t['locale'], ALT, ld(article(L), faqpage(L), dataset(L))))
        (ROOT / t['meth']).write_text(methodology(L), encoding='utf-8')
        (ROOT / ABOUT[L]).write_text(about(L), encoding='utf-8')
    inject(ROOT / 'mapa.html', meta(MAPA['title'], MAPA['desc'], BASE + 'mapa.html', 'es', 'es_ES', [], ld(dataset('es')), typ='website'))
    (ROOT / 'llms.txt').write_text(llms(), encoding='utf-8')
    (ROOT / 'sitemap.xml').write_text(sitemap(), encoding='utf-8')
    (ROOT / 'robots.txt').write_text(ROBOTS, encoding='utf-8')
    print('seo: index.html, ca.html, mapa.html, metodologia(-ca).html, sobre-mi(-ca).html, llms.txt, sitemap.xml, robots.txt')


main()
