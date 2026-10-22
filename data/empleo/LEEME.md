# Empleo por sector de actividad, por municipio y sección censal

Población **ocupada de 16 y más años** según la actividad económica del establecimiento donde trabaja, contada **por lugar de residencia** (no por lugar de trabajo). Años 2021, 2022 y 2023 (a 1 de enero).

Se genera con `python3 src/empleo_ine.py <carpeta>`, que descarga las tablas del INE a `<carpeta>` si no están y escribe los tres ficheros de esta carpeta.

## Fuente

INE, **Censo anual de población 2021-2023** (Censos de Población y Viviendas, resultados de ocupados). Tablas en CSV (`https://www.ine.es/jaxiT3/files/t/csv_bdsc/<tabla>.csv`):

| Tabla | Contenido | Página |
|---|---|---|
| 70005 | Ocupados por sexo y actividad (4 sectores), total nacional, provincias, municipios y secciones | [t=70005](https://www.ine.es/jaxiT3/Tabla.htm?t=70005) |
| 69992 | Ocupados por sexo y actividad (secciones A–U de la CNAE-2009), municipios de 500 habitantes o más | [t=69992](https://www.ine.es/jaxiT3/Tabla.htm?t=69992) |
| 70006 | Ocupados por sexo y situación profesional (cuenta propia / cuenta ajena y otra situación), total nacional, provincias, municipios y secciones | [t=70006](https://www.ine.es/jaxiT3/Tabla.htm?t=70006) |
| 69987 | Ocupados por lugar de trabajo, sexo, actividad y situación profesional, capitales de provincia y principales ciudades | [t=69987](https://www.ine.es/jaxiT3/Tabla.htm?t=69987) |

Descargadas el 22-10-2026. Solo se guardan los totales de ambos sexos; las tablas originales traen también hombres y mujeres (y la 69987, cuenta propia / ajena).

## Ficheros

- `empleo_sector_municipios.csv`: una fila por municipio y año. `mun_code` (código INE de 5 cifras), `municipio`, `anyo`, `ocupados`, `agricultura`, `industria`, `construccion`, `servicios`, `no_consta`, `cuenta_propia`, y `cnae_A` … `cnae_U` (secciones de la CNAE-2009: G comercio, I hostelería, O Administración pública, P educación, Q sanidad y servicios sociales, etc.). Las columnas `cnae_*` solo existen para los 4.144 municipios de 500 habitantes o más; en el resto quedan vacías. En cada fila, los cuatro sectores más `no_consta` suman `ocupados`, y lo mismo las secciones A–U más `no_consta`.
- `empleo_sector_secciones.csv.gz`: una fila por sección censal y año. `seccion` (código INE de 10 cifras), `mun_code`, `anyo` y las mismas columnas de 4 sectores, más `cuenta_propia`. Cada año usa **las secciones vigentes ese año**: las filas de 2023 cruzan directamente con las secciones de 2023 (en Cataluña casan 5.099 de las 5.115 de `data/catalunya_secciones_2023.csv`; las 16 que faltan son secciones divididas o renumeradas). Para comparar años hay que tener en cuenta los cambios de seccionado.
- `cuenta_propia` (en los dos ficheros, tabla 70006): ocupados **por cuenta propia**, lo más parecido a «autónomos» que da el censo. Incluye empresarios con y sin asalariados, miembros de cooperativas y ayudas familiares; el resto de ocupados son «cuenta ajena y otra situación». Es por residencia, como todo el censo. En 2023 son 3,28 millones (16,5% de los ocupados); por sección, la mediana es el 16% y en Madrid va del 4% (Puente de Vallecas) al 39% (Salamanca). No es lo mismo que los afiliados al RETA (régimen de autónomos de la Seguridad Social), que la Seguridad Social publica por municipio solo en la explotación de algunas comunidades (ver Extremadura, columna `autonomos`).
- `lugar_trabajo_ciudades.csv`: 151 capitales y principales ciudades. De sus ocupados residentes, cuántos trabajan en el mismo municipio, en otro de la provincia, en otra provincia de la comunidad o en otra comunidad.

## Afiliación a la Seguridad Social en Cataluña (Idescat)

- `afiliacion_catalunya_municipios.csv`: afiliaciones a la Seguridad Social a 31 de diciembre, por municipio (`mun_code` INE) y actividad. Tres bloques, que se distinguen por `enfoque` y `nivel`:
  - `residencia` / `sector`: todos los municipios (947), 2012-2025, por municipio de residencia padronal del afiliado, en cuatro sectores: `a` (agricultura), `b-e` (industria), `f` (construcción) y `g-u` (servicios).
  - `residencia` / `seccion`: municipios de 5.000 habitantes o más (unos 218), 2022-2025, por residencia, en secciones `a` … `u` de la CCAE-2009 (equivale a la CNAE-2009).
  - `trabajo` / `seccion`: los mismos municipios, 2020-2025, **por municipio de la cuenta de cotización** (donde está el centro de trabajo), solo régimen general (sin autónomos). Es el único bloque que cuenta empleos del municipio y no vecinos ocupados.
- Fuente: Idescat, [API de tablas](https://api.idescat.cat/taules/v2) (`afi/8598/8709`, `afi/13338/19722` y `afic/14987/15881`), descargadas el 22-10-2026 con `python3 src/afiliacion_idescat.py`. Desde enero de 2022 el Idescat redondea a múltiplos de 5, así que un total puede no coincidir con la suma de sus partes. Las celdas vacías son datos que el Idescat no da (secreto estadístico o municipio fuera del bloque). Desde enero de 2026 la clasificación pasa a la CCAE-2025 y no se mezcla con esta serie.
- Ejemplo de lo que añade: en Salt viven 13.525 afiliados, pero el municipio tiene 7.880 afiliaciones del régimen general, el 29% de ellas en sanidad y servicios sociales (2023).

## Afiliación a la Seguridad Social en Extremadura (Junta de Extremadura)

- `afiliacion_extremadura_municipios.csv`: afiliados a la Seguridad Social **residentes** en cada uno de los 388 municipios de Extremadura (`mun_code` INE), a fin de mes. Una fila por municipio y `fecha` (AAAA-MM): diciembre de 2021 a 2024, noviembre de 2025 y septiembre de 2026, el último publicado. Columnas: `afiliados`; por sector, `agricultura`, `industria`, `construccion`, `servicios` y `sector_no_consta`; por régimen, `general`, `empleados_hogar`, `agrario` (sistema especial agrario), `autonomos` y `regimen_no_consta`; por sexo, `hombres` y `mujeres`.
- Fuente: Junta de Extremadura, [«Afiliación a la Seguridad Social por municipios»](https://www.juntaex.es/w/afiliacion-a-la-seguridad-social-por-municipios-agosto-2026), tablas mensuales en `.xls` (`Tablas_afssMMAAAA.xls`), descargadas el 22-10-2026 con `python3 src/afiliacion_extremadura.py <carpeta>`. Desde finales de 2025 el nombre de la página va un mes por detrás del dato que contiene (la página «agosto-2026» trae septiembre); el script comprueba el mes del fichero. Para añadir meses basta con ampliar `PAGINAS`.
- Las celdas vacías son «(*)», dato protegido por secreto estadístico (valores pequeños). Por eso las partes pueden sumar menos que `afiliados`, nunca más; en los municipios grandes cuadran.
- Es **por residencia**, como el censo: no dice cuántos empleos hay en el municipio. Cuadra con el censo anual del INE (diciembre de 2023: 390.584 afiliados frente a 410.214 ocupados en el censo de 2023, correlación entre municipios 0,999). Lo que añade es la serie mensual hasta 2026 y el régimen (autónomos, agrario, hogar).
- Ejemplo: Plasencia tiene 15.084 afiliados residentes en septiembre de 2026 (14.267 en diciembre de 2021): 12.132 en servicios (80%), 1.243 en industria, 1.153 en construcción y 505 en agricultura; 2.816 son autónomos.

## Empleo público por provincia

- `empleo_publico_provincias.csv`: efectivos de las Administraciones públicas por semestre, de enero de 2023 a enero de 2026 (7 cortes, `fecha` AAAA-MM). Una fila por fecha, provincia (`prov_code` INE; `99` = extranjero), administración (`estado`, `ccaa`, `local`), sector y sexo. Sectores: administración general, justicia, fuerzas armadas y seguridad (Estado), policía autonómica, docencia no universitaria, sanidad, universidades, ayuntamientos, diputaciones y cabildos. Columnas de personal: `funcionario_carrera` (incluye el estatutario de la sanidad), `funcionario_interino`, `en_practicas`, `laboral_fijo` (con fijos discontinuos), `laboral_temporal` y `otro` (eventuales, indefinidos no fijos, varios); `efectivos` es su suma. Se genera con `python3 src/empleo_publico.py <carpeta>`.
- Fuente: Registro Central de Personal, [Estadística del personal al servicio de las Administraciones públicas (EPSAP)](https://digital.gob.es/funcion-publica/dgfp/registro-central-personal/boletin.html), microdatos semestrales (hoja de totales; los cortes de julio de 2023 a julio de 2025 son la revisión de agosto de 2026), descargados el 22-10-2026. Enero de 2026: 3.071.725 efectivos.
- Cuenta **por lugar de trabajo** y su nivel más fino es la provincia. **No hay en abierto un recuento de funcionarios por municipio ni por sección**: ni la EPSAP, ni el censo (su «situación profesional» no separa público de privado), ni la EPA (provincial). Por municipio, lo más cercano son las ramas `cnae_O` (Administración pública), `cnae_P` (educación) y `cnae_Q` (sanidad) del censo, que mezclan empleo público y privado.
- Los microdatos existen desde julio de 2019, pero **no se usan los anteriores a 2023**: hasta enero de 2021 recogen 1,1 millones de efectivos y de julio de 2021 a julio de 2022, 2,7 millones (la cobertura de comunidades y entidades locales era incompleta), frente a 3,0 desde 2023.
- La asignación a provincias tiene ruido: algunos saltos de un semestre a otro son de registro, no de plantilla (en Cáceres, sanidad pasa de 8.106 a 6.459 efectivos entre enero de 2025 y enero de 2026), y algunas universidades constan en una sola provincia (Cáceres no tiene fila de universidades). Para comparar provincias conviene usar varios cortes.
- El grupo de titulación (A1…E) y la edad no se incluyen: el grupo tiene un 20% «N/D» y la edad solo viene sin provincia.

## Límites

- **Residencia, no puesto de trabajo.** Mide a qué se dedican los vecinos, no cuántos empleos hay en el municipio. Una «ciudad de servicios» que atrae trabajadores de la comarca no se ve aquí; para eso haría falta afiliación a la Seguridad Social por municipio de la cuenta de cotización, que la Seguridad Social no publica en abierto para toda España (en abierto solo lo hemos encontrado en Cataluña, en el bloque `trabajo` del Idescat, y en Andalucía, en el IECA).
- **Secreto estadístico.** El INE no da cifras (`.`) para los municipios de menos de 50 habitantes ni para sus secciones: 568 municipios sin dato, unos 8.000 ocupados de 19,9 millones.
- El censo anual se construye a partir de registros administrativos (padrón, Seguridad Social, AEAT…), no de cuestionario; la actividad es la del establecimiento según esos registros.
- Son datos, no explicaciones: que un municipio tenga mucho empleo público o sanitario no explica por sí solo cómo vota.
