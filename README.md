# ¿Quién no vota en Cataluña?

Abstención en las elecciones generales (2015–2023) por sección censal en Cataluña, cruzada con renta, edad, estudios, paro y población extranjera.

- `index.html`: portada del sitio, el mapa de resultados de España. Es una copia de `generales-2026/index.html` con las rutas ajustadas, generada con `python3 src/portada.py`, que hay que ejecutar cada vez que se actualice la pieza de `generales-2026/` (deja en `generales-2026/index.html` una redirección a la portada).
- `abstencion.html`: pieza de scroll con mapa 3D (deck.gl + scrollama). La cámara avanza con el scroll y recorre los lugares que nombra el texto; termina en un mapa plano para explorar.
- `ca.html`: la misma pieza en catalán, con selector ES/CA arriba. Se genera desde `abstencion.html` con `python3 src/build_ca.py` (el texto catalán está en `src/i18n/ca_body.html`; si cambia el texto castellano, el script avisa hasta que se actualice la traducción y se ejecute con `--accept`).
- `calles.json`: índice de calles del buscador «¿Y en tu calle?» (callejero del censo electoral del INE, enero de 2023), generado con `src/calles.py`. Las dos páginas lo cargan cuando alguien empieza a escribir.
- `data/evolucion_secciones.csv`: participación por sección en las doce elecciones de 2015 a 2024 (municipales, Parlament y Congreso), generada con `src/evolucion.py` desde Transparència Catalunya.
- `mapa.html`: mapa interactivo en 2D con los gráficos y la metodología.
- `metodologia.html` y `metodologia-ca.html`: descarga de los datos, licencia, columnas, fuentes y limitaciones.
- `llms.txt`, `sitemap.xml`, `sitemap_index.xml` (índice que recoge solo el `sitemap.xml` de cada carpeta, como `generales-2026/` o `atlas/`), `robots.txt` y el bloque `<!-- seo -->` del `<head>` de cada página (descripción, idiomas alternativos y datos estructurados schema.org `NewsArticle` y `Dataset`): se generan con `python3 src/seo.py`, que hay que ejecutar siempre después de `src/build_ca.py`. El `llms.txt` de la raíz resume todo el sitio e incluye los `llms.txt` de `generales-2026/` y `atlas/`, así que `src/seo.py` se ejecuta también después de `src/portada.py` y de regenerar el Atlas. Los textos de esas páginas están en castellano y catalán dentro del script.
- Datos estructurados comunes (`src/esquema.py`): el autor como una sola `Person` (con `@id`, cargo, universidad y perfiles) en todas las páginas, el `Dataset` del mapa enlazado desde la metodología y las piezas de Actualidad, y las migas de pan (`BreadcrumbList`) de cada página. Repasa todas las páginas ya generadas y es idempotente; lo llaman al terminar `src/seo.py` y `atlas/src/paginas.py`, y se puede ejecutar solo con `python3 src/esquema.py`.
- Preguntas frecuentes: el apartado `<section id="faq">` de `src/i18n/es_body.html` y `ca_body.html`. `src/seo.py` lo lee para el esquema `FAQPage` y para `llms.txt`, así que basta con cambiarlo en esos dos archivos.
- Página «Sobre mí» (`sobre-mi.html`, `sobre-mi-ca.html`): nombre, biografía, cargo y enlaces en `AUTHOR_*` de `src/seo.py`; la firma de la pieza está en los dos `*_body.html`.
- Verificación en Google Search Console y Bing Webmaster Tools: pega el código en `GOOGLE_VERIFICATION` y `BING_VERIFICATION` de `src/seo.py` y vuelve a ejecutarlo.
- `data/`: datos limpios por sección y municipio (CSV y GeoJSON).
- `data/empleo/`: ocupados por sector de actividad (4 sectores por sección censal y municipio; secciones A–U de la CNAE en municipios de 500 habitantes o más) y ocupados por cuenta propia (sección y municipio) del Censo anual de población del INE, 2021-2023, generados con `src/empleo_ine.py`. Incluye también el empleo público por provincia, administración, sector, sexo y tipo de personal, semestral de 2023 a 2026 (Registro Central de Personal, `src/empleo_publico.py`). También, la afiliación a la Seguridad Social por municipio y actividad en Cataluña, por residencia y por lugar de trabajo (Idescat, `src/afiliacion_idescat.py`) y en Extremadura, por residencia, sector, régimen y sexo, 2021-2026 (Junta de Extremadura, `src/afiliacion_extremadura.py`). Fuente y límites en `data/empleo/LEEME.md`.
- `data/andalucia/`: la malla estadística de 250 m del IECA (población, estudios, afiliados, pensiones y paro, 2024) repartida entre las secciones censales de 2023 con `src/malla_ieca.py`. Fuente y límites en `data/andalucia/LEEME.md`.
- `src/`: scripts en Python y plantillas con los que se han generado los datos y las páginas.

## Girona, sección a sección

`girona.html` y `girona-ca.html`: la misma pieza que la de Cataluña (recorrido 3D, mapa final en 2D, buscador de calle) para las 536 secciones de la provincia de Girona. Se generan a partir de `abstencion.html`, así que hay que volver a ejecutarlos si cambia la plantilla de la pieza de Cataluña:

1. `python3 src/girona/datos.py` calcula las cifras del texto y las guarda en `src/girona/resumen.json` (lee los ficheros de transparencia y de secciones 2019-2024 de la carpeta del proyecto).
2. `python3 src/girona/construir.py es` y `python3 src/girona/construir.py ca` escriben las dos páginas. El texto está en `src/girona/es_body.html` y `ca_body.html` (cualquier cambio, en los dos); las fotos de Commons, con autor y licencia, en `src/girona/fotos.json`; la comarca de cada municipio, en `src/girona/comarcas.json`.
3. `python3 src/seo.py` para el sitemap y `llms.txt`.

## Generales del 29N

`generales-2026/`: mapa de las elecciones generales por municipio y sección censal en toda España (Congreso 2004–2023, con municipales y europeas) cruzado con renta, pobreza, edad y población extranjera, con modo en directo para la noche electoral. Ver `generales-2026/README.md`.

## Elecciones por comunidad y provincia

`elecciones/`: páginas de entrada por territorio y por tema, generadas con `python3 src/territorios.py` (después de regenerar el mapa y el Atlas; luego `src/seo.py`). Una por comunidad autónoma y otra por provincia (las comunidades uniprovinciales no tienen página de provincia): resultado de las generales de 2023 con el color de cada partido, la serie de las 16 generales desde 1977, voto y participación por grupos de renta de sus secciones censales, municipios principales con enlace al mapa (`?m=<código INE>`) y las piezas del Atlas y de Actualidad sobre ese territorio. Más dos páginas temáticas: `mapa-electoral-seccion-censal/` y `voto-y-renta-por-barrios/`. Las cifras salen de las descargas de `generales-2026/descargas/` (`src/territorios_datos.py`); las rutas, en `src/territorios_rutas.py` (también las usa el Atlas para enlazar cada pieza con su provincia). Las piezas de Actualidad sobre un territorio concreto se apuntan a mano en `ACTUALIDAD_LUGAR` de `src/territorios.py`. El script también rellena en la portada la franja «Elecciones por comunidad y provincia» entre las marcas `<!--territorios-->`. Y, debajo de Actualidad, el carrusel «Guías de las elecciones» con las cinco páginas temáticas, entre las marcas `<!--elecciones:guias-->` (lista en `GUIAS`). Solo las ciudades grandes tienen página (capitales de provincia y municipios de más de 50.000 habitantes, `UMBRAL` y `CAPITALES` en `src/territorios.py`), en `elecciones/<comunidad>/<provincia>/<ciudad>/`: voto barrio a barrio, por renta, municipales frente a generales y la serie desde 1977. La lista se guarda en `src/ciudades.json` para que el Atlas enlace sus piezas a la ciudad; por eso, si cambia, se ejecuta `src/territorios.py` antes que `atlas/src/paginas.py`.

## Previsiones (prototipo, sin publicar)

`previsiones/`: prototipo de la sección de previsiones de las generales (issue #157), con **datos ficticios**, `noindex` y fuera del sitemap. `previsiones/src/motor.py` escribe los artefactos versionados de `previsiones/datos/<versión>/` (escenarios, dato de 2023, metadatos) con las reglas de `previsiones/src/reglas.py` (D'Hondt del Congreso y voto limitado del Senado); la página (`index.html` y `app.js`) solo los lee. Pruebas: `python3 -m unittest discover previsiones/src`. Plan técnico: `previsiones/PLAN.md`.

## Atlas de las anomalías electorales

`atlas/`: piezas editoriales en series (excepciones, fronteras, gemelos, contra su provincia, ciudad y entorno, voto doble, bisagras, quién no vota). Cada pieza es HTML estático con titular, resumen, cifras en el texto, tabla accesible, gráfico SVG sin JavaScript, CSV descargable, método, fuentes, autoría, revisión y JSON-LD (NewsArticle, Dataset, FAQPage).

Construir:

```
python3 atlas/src/construir.py && python3 atlas/src/controles.py && python3 atlas/src/paginas.py
```

`construir.py` calcula todas las cifras (`atlas/src/cifras.json`) y los CSV de `atlas/datos/`; `controles.py` comprueba escaños oficiales, universo, afirmaciones con nombre propio y que cada cifra del texto salga de los datos (informe en `atlas/src/controles.txt`); `paginas.py` escribe las páginas, el sitemap y `llms.txt`. `expediente.py` genera el expediente interno y la muestra para la comprobación manual (no se publica).

Después, `node atlas/src/compartir.mjs` dibuja con Playwright la imagen para redes (1200 × 630) de cada pieza y del índice en `img/compartir/` (titular, subtítulo y foto). La de la portada, `img/compartir/portada.jpg`, se hizo una vez con una captura del mapa.

Cada pieza tiene un titular corto (`atlas/src/titulares.py`, 60 caracteres como máximo) que se usa en el `<h1>`, las tarjetas, el `<title>` y las redes; el titular largo (`titulo`) pasa a ser el subtítulo. `paginas.py` escribe también `atlas/feed.xml` (RSS) y rellena en la portada del sitio (`index.html` y la plantilla de `generales-2026/`) la franja «Del Atlas» con las tres últimas piezas, entre las marcas `<!--atlas:ultimas-->`. El boletín se activa poniendo la URL del formulario de alta en `NEWSLETTER` de `paginas.py`; mientras esté vacío, el bloque «Síguelo» ofrece RSS y X.

Ninguna pieza se publica sola: mientras su campo `revisado` en `atlas/src/piezas.py` esté vacío, la página dice «Revisión pendiente», lleva `noindex` y queda fuera del sitemap. Se rellena con la fecha cuando el revisor ha comprobado la muestra manual y el texto.

## Publicar con GitHub Pages

Settings → Pages → *Deploy from a branch* → `main` / `(root)`. Dominio propio: `mapaelectoral.es` (archivo `CNAME`; las URL absolutas salen de `BASE` en `src/seo.py` y `atlas/src/paginas.py`, y de `URL` en `generales-2026/src/pagina.py`). Las dos páginas son autónomas: los datos van incrustados y las librerías se cargan desde unpkg.

## Qué mide

Para cada sección, de cada 100 adultos residentes:

- **Votó**: votos emitidos el 23J de 2023.
- **Sin derecho a voto**: adultos residentes menos censo electoral (en unas generales solo votan españoles).
- **No votó**: el resto, es decir, la abstención entre quienes sí podían votar.

La participación oficial (votos / censo) solo mide el último grupo.

## Fuentes

- Resultados por mesa del Congreso 2015, 2016, abril y noviembre de 2019 y julio de 2023 (Ministerio del Interior), vía [pollspaindata](https://github.com/dadosdelaplace/pollspaindata). Sin voto CERA.
- Atlas de Distribución de Renta de los Hogares 2023 y Censo de Población y Viviendas 2021 del INE, por sección, vía [ineAtlas.data](https://github.com/pablogguz/ineAtlas.data), incluidos los contornos de las secciones de 2023.
- Participación por sección en las municipales de 2023 y el Parlament de 2024 (Departament de Polítiques Digitals), vía [Transparència Catalunya](https://analisi.transparenciacatalunya.cat) (dataset `irrv-2mfc`).
- Contraste con [Idescat](https://www.idescat.cat/emex/) (EMEX): la renta y la población extranjera del INE correlacionan 0,94 por municipio con las de Idescat, y las conclusiones no cambian con una fuente u otra. Se usa el INE porque Idescat no las da por sección.

## Columnas principales (`data/catalunya_secciones_2023.csv`)

| columna | significado |
|---|---|
| `tract_code` | código INE de sección (10 dígitos) |
| `electorate`, `voters`, `turnout` | censo, votantes y participación del 23J de 2023 |
| `t2015_12` … `t2023_07` | participación en cada general (solo si el código de sección no cambió) |
| `adults`, `sin_derecho` | adultos residentes estimados y adultos sin derecho a voto |
| `pct_ad_vota`, `pct_ad_sinderecho`, `pct_ad_abst` | reparto de cada 100 adultos residentes |
| `net_income_equiv` | renta neta por unidad de consumo (2023) |
| `mean_age`, `pct_over65`, `pct_spanish` | edad y nacionalidad (Atlas 2023) |
| `pct_foreign`, `pct_naturalized`, `pct_higher_ed_completed`, `unemployment_rate`, `pct_rented`, `pct_secondary` | Censo 2021 |
| `indep_share19`, `indep_share23`, `drop_19_23` | voto a ERC, Junts y CUP, y caída de participación entre 2019 y 2023 |

## Licencia

Los datos elaborados de `data/` se publican con licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es). Las fotos de la pieza tienen su propia licencia, indicada al pie de cada una.

## Limitaciones

Son datos por sección, no por persona: indican dónde se vota menos, no quién. La población adulta se estima con el porcentaje de menores de 18 años del Atlas. El censo electoral de julio y la población de enero no son exactamente la misma foto. Los scripts de `src/` usan rutas locales de trabajo y sirven como documentación del proceso.
