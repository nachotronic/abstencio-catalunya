# Datos de población y vivienda por municipio y sección censal

`censo_municipios_2023_2026.csv` es el censo electoral por municipio (`src/censo_ine.py`). El resto de ficheros de esta carpeta se describen aquí. Todos usan `seccion` (código INE de 10 cifras) y `mun_code` (5 cifras).

## Ocupación, estudios y país de nacimiento (INE, Censo anual)

`censo_secciones.csv.gz` (una fila por sección y año) y `censo_municipios.csv` (una fila por municipio y año, con `municipio`). Se generan con `python3 src/censo_secciones.py <carpeta>`, que descarga las tablas a `<carpeta>` si no están. Población residente a 1 de enero, ambos sexos.

| Tabla | Columnas | Años |
|---|---|---|
| [70004](https://www.ine.es/jaxiT3/Tabla.htm?t=70004) Ocupados de 16 y más años por ocupación | `ocupados`; `ocup_alta` (directores, gerentes y profesionales y técnicos de nivel medio o alto), `ocup_media` (trabajadores cualificados y oficiales u operarios de nivel bajo), `ocup_elemental` (ocupaciones elementales), `ocup_no_consta` | 2021-2023 |
| [66592](https://www.ine.es/jaxiT3/Tabla.htm?t=66592) Población de 15 y más años por nivel de estudios | `pob15`; `est_primaria` (primaria o menos), `est_secundaria1` (ESO y similar), `est_secundaria2` (bachillerato, FP de grado medio y postsecundaria no superior), `est_superior` | 2021-2024 |
| [65035](https://www.ine.es/jaxiT3/Tabla.htm?t=65035) Población por país de nacimiento | `poblacion`; `nac_espana` y 19 columnas `nac_*` (Francia, Reino Unido, Rumanía, Ucrania, otros de Europa, Marruecos, otros de África, Cuba, República Dominicana, Argentina, Bolivia, Colombia, Ecuador, Perú, Venezuela, otros de América, China, otros de Asia, Oceanía) | 2021-2025 |

Descargadas el 22-10-2026 de `https://www.ine.es/jaxiT3/files/t/csv_bdsc/<tabla>.csv`. Las columnas de un año que la tabla no cubre quedan vacías (por ejemplo, ocupación en 2024). En cada fila, las categorías suman el total (`ocupados`, `pob15`, `poblacion`).

- Cada año usa **las secciones vigentes ese año**. Las de 2023 casan con 5.107 de las 5.115 secciones de `data/catalunya_secciones_2023.csv`.
- **Secreto estadístico**: el INE no da cifras para los municipios de menos de 50 habitantes ni para sus secciones. Por eso la suma de ocupados con ocupación alta en 2023 (6.574.534) queda un poco por debajo del total nacional (6.576.432).
- Es **país de nacimiento**, no nacionalidad: un colombiano nacionalizado cuenta en `nac_colombia`. Los nacidos en el extranjero de padres españoles también cuentan como nacidos fuera.
- Correlación con la participación en las generales de 2023, por sección, en Cataluña (5.107 secciones): ocupaciones elementales −0,69; ocupación alta +0,65; estudios superiores +0,62; nacidos en Marruecos −0,51. Es un dato descriptivo, no una explicación.

## Precio del alquiler (Ministerio de Vivienda, SERPAVI)

`alquiler_secciones.csv.gz` (sección y año) y `alquiler_municipios.csv` (municipio y año), 2011-2024. Se generan con `python3 src/alquiler_serpavi.py "<fichero.xlsx>"` a partir de `2026-03_09_bd_SERPAVI_2011-2024 - DEFINITIVO WEB_v2.xlsx` (Sistema Estatal de Referencia del Precio del Alquiler de Vivienda, versión de marzo de 2026, metadatos corregidos el 8-7-2026), que Nacho subió el 22-10-2026.

- Fuente: declaraciones del IRPF (modelo 100) de viviendas alquiladas como **vivienda habitual** (sin alquileres a parientes), cruzadas con el Catastro. No son precios de anuncio sino alquileres declarados.
- Columnas, cada una con sufijo `_pisos` (vivienda colectiva) o `_unif` (unifamiliar o rural): `n` (viviendas alquiladas con dato), `alq_m2` (alquiler mensual por m², mediana), `alq_m2_p25` y `alq_m2_p75` (percentiles 25 y 75), `alq_mes` (alquiler mensual de la vivienda, mediana) y `sup_m2` (superficie, mediana).
- Secciones del **seccionado de 2021** para todos los años. En Cataluña casan 5.056 de las 5.115 secciones de 2023.
- **Sin País Vasco ni Navarra** (régimen fiscal foral). Las secciones con pocas viviendas alquiladas no tienen dato; las filas sin ningún dato se han quitado.
- Ejemplo: en Barcelona (2024) la mediana por sección es de 13,6 €/m² y 900 € al mes en pisos.

## Viviendas turísticas (INE, estadística experimental)

`viviendas_turisticas_secciones.csv.gz`: una fila por sección y `periodo` (AAAA-MM). Columnas: `viviendas` (viviendas turísticas), `plazas` y `pct_viviendas` (porcentaje sobre el total de viviendas, en tanto por cien). Se genera con `python3 src/viviendas_turisticas.py <ficheros>` a partir de los ficheros `exp_viv_turistica_tabla5_<MES><AÑO>.xlsx` de la [estadística experimental del INE](https://ine.es/experimental/viv_turistica/exp_viv_turistica_tablas.htm), que Nacho subió el 22-10-2026: febrero y agosto de 2023, febrero, agosto y noviembre de 2024, mayo y noviembre de 2025.

- El INE las cuenta haciendo *web scraping* de las tres plataformas principales, filtrando según la normativa de cada comunidad y quitando duplicados. No es un registro oficial: el de la Generalitat tiene más del doble porque incluye licencias inactivas.
- Las fechas de referencia cambiaron a finales de 2024 (antes, febrero y agosto; ahora, mayo y noviembre). Agosto es temporada alta: no conviene comparar agosto con noviembre.
- El porcentaje usa las viviendas del censo de 2021 y su seccionado, así que puede no cuadrar con el seccionado del periodo. Para sumar por municipio, sumar `viviendas` y `plazas`; el porcentaje no se suma.
- Total de España: 376.463 viviendas en noviembre de 2024 (Madrid 17.274, Barcelona 9.750). Lloret de Mar: 1.620, de media el 4,7% de las viviendas de cada sección en noviembre de 2025 y hasta el 11,3% en una.
