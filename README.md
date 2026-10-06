# ¿Quién no vota en Cataluña?

Abstención en las elecciones generales (2015–2023) por sección censal en Cataluña, cruzada con renta, edad, estudios, paro y población extranjera.

- `index.html`: pieza de scroll con mapa 3D (deck.gl + scrollama). La cámara avanza con el scroll y recorre los lugares que nombra el texto; termina en un mapa plano para explorar.
- `ca.html`: la misma pieza en catalán, con selector ES/CA arriba. Se genera desde `index.html` con `python3 src/build_ca.py` (el texto catalán está en `src/i18n/ca_body.html`; si cambia el texto castellano, el script avisa hasta que se actualice la traducción y se ejecute con `--accept`).
- `calles.json`: índice de calles del buscador «¿Y en tu calle?» (callejero del censo electoral del INE, enero de 2023), generado con `src/calles.py`. Las dos páginas lo cargan cuando alguien empieza a escribir.
- `data/evolucion_secciones.csv`: participación por sección en las doce elecciones de 2015 a 2024 (municipales, Parlament y Congreso), generada con `src/evolucion.py` desde Transparència Catalunya.
- `mapa.html`: mapa interactivo en 2D con los gráficos y la metodología.
- `metodologia.html` y `metodologia-ca.html`: descarga de los datos, licencia, columnas, fuentes y limitaciones.
- `llms.txt`, `sitemap.xml`, `robots.txt` y el bloque `<!-- seo -->` del `<head>` de cada página (descripción, idiomas alternativos y datos estructurados schema.org `NewsArticle` y `Dataset`): se generan con `python3 src/seo.py`, que hay que ejecutar siempre después de `src/build_ca.py`. Los textos de esas páginas están en castellano y catalán dentro del script.
- Preguntas frecuentes: el apartado `<section id="faq">` de `src/i18n/es_body.html` y `ca_body.html`. `src/seo.py` lo lee para el esquema `FAQPage` y para `llms.txt`, así que basta con cambiarlo en esos dos archivos.
- Página «Sobre mí» (`sobre-mi.html`, `sobre-mi-ca.html`): nombre, biografía, cargo y enlaces en `AUTHOR_*` de `src/seo.py`; la firma de la pieza está en los dos `*_body.html`.
- Verificación en Google Search Console y Bing Webmaster Tools: pega el código en `GOOGLE_VERIFICATION` y `BING_VERIFICATION` de `src/seo.py` y vuelve a ejecutarlo.
- `data/`: datos limpios por sección y municipio (CSV y GeoJSON).
- `src/`: scripts en Python y plantillas con los que se han generado los datos y las páginas.

## Generales del 29N

`generales/`: mapa de las elecciones generales por municipio y sección censal en toda España (Congreso 2015–2023) cruzado con renta, pobreza, edad y población extranjera, con modo en directo para la noche electoral. Ver `generales/README.md`.

## Atlas de las anomalías electorales

`atlas/`: piezas editoriales en series (excepciones, fronteras, gemelos, contra su provincia, ciudad y entorno, voto doble, bisagras, quién no vota). Cada pieza es HTML estático con titular, resumen, cifras en el texto, tabla accesible, gráfico SVG sin JavaScript, CSV descargable, método, fuentes, autoría, revisión y JSON-LD (NewsArticle, Dataset, FAQPage).

Construir:

```
python3 atlas/src/construir.py && python3 atlas/src/controles.py && python3 atlas/src/paginas.py
```

`construir.py` calcula todas las cifras (`atlas/src/cifras.json`) y los CSV de `atlas/datos/`; `controles.py` comprueba escaños oficiales, universo, afirmaciones con nombre propio y que cada cifra del texto salga de los datos (informe en `atlas/src/controles.txt`); `paginas.py` escribe las páginas, el sitemap y `llms.txt`. `expediente.py` genera el expediente interno y la muestra para la comprobación manual (no se publica).

Ninguna pieza se publica sola: mientras su campo `revisado` en `atlas/src/piezas.py` esté vacío, la página dice «Revisión pendiente», lleva `noindex` y queda fuera del sitemap. Se rellena con la fecha cuando el revisor ha comprobado la muestra manual y el texto.

## Publicar con GitHub Pages

Settings → Pages → *Deploy from a branch* → `main` / `(root)`. Las dos páginas son autónomas: los datos van incrustados y las librerías se cargan desde unpkg.

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
