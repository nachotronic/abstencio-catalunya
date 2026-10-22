# Empleo por sector de actividad, por municipio y sección censal

Población **ocupada de 16 y más años** según la actividad económica del establecimiento donde trabaja, contada **por lugar de residencia** (no por lugar de trabajo). Años 2021, 2022 y 2023 (a 1 de enero).

Se genera con `python3 src/empleo_ine.py <carpeta>`, que descarga las tablas del INE a `<carpeta>` si no están y escribe los tres ficheros de esta carpeta.

## Fuente

INE, **Censo anual de población 2021-2023** (Censos de Población y Viviendas, resultados de ocupados). Tablas en CSV (`https://www.ine.es/jaxiT3/files/t/csv_bdsc/<tabla>.csv`):

| Tabla | Contenido | Página |
|---|---|---|
| 70005 | Ocupados por sexo y actividad (4 sectores), total nacional, provincias, municipios y secciones | [t=70005](https://www.ine.es/jaxiT3/Tabla.htm?t=70005) |
| 69992 | Ocupados por sexo y actividad (secciones A–U de la CNAE-2009), municipios de 500 habitantes o más | [t=69992](https://www.ine.es/jaxiT3/Tabla.htm?t=69992) |
| 69987 | Ocupados por lugar de trabajo, sexo, actividad y situación profesional, capitales de provincia y principales ciudades | [t=69987](https://www.ine.es/jaxiT3/Tabla.htm?t=69987) |

Descargadas el 22-10-2026. Solo se guardan los totales de ambos sexos; las tablas originales traen también hombres y mujeres (y la 69987, cuenta propia / ajena).

## Ficheros

- `empleo_sector_municipios.csv`: una fila por municipio y año. `mun_code` (código INE de 5 cifras), `municipio`, `anyo`, `ocupados`, `agricultura`, `industria`, `construccion`, `servicios`, `no_consta`, y `cnae_A` … `cnae_U` (secciones de la CNAE-2009: G comercio, I hostelería, O Administración pública, P educación, Q sanidad y servicios sociales, etc.). Las columnas `cnae_*` solo existen para los 4.144 municipios de 500 habitantes o más; en el resto quedan vacías. En cada fila, los cuatro sectores más `no_consta` suman `ocupados`, y lo mismo las secciones A–U más `no_consta`.
- `empleo_sector_secciones.csv.gz`: una fila por sección censal y año. `seccion` (código INE de 10 cifras), `mun_code`, `anyo` y las mismas columnas de 4 sectores. Cada año usa **las secciones vigentes ese año**: las filas de 2023 cruzan directamente con las secciones de 2023 (en Cataluña casan 5.099 de las 5.115 de `data/catalunya_secciones_2023.csv`; las 16 que faltan son secciones divididas o renumeradas). Para comparar años hay que tener en cuenta los cambios de seccionado.
- `lugar_trabajo_ciudades.csv`: 151 capitales y principales ciudades. De sus ocupados residentes, cuántos trabajan en el mismo municipio, en otro de la provincia, en otra provincia de la comunidad o en otra comunidad.

## Empleo público por provincia

- `empleo_publico_provincias.csv`: efectivos de las Administraciones públicas por semestre, de enero de 2023 a enero de 2026 (7 cortes, `fecha` AAAA-MM). Una fila por fecha, provincia (`prov_code` INE; `99` = extranjero), administración (`estado`, `ccaa`, `local`), sector y sexo. Sectores: administración general, justicia, fuerzas armadas y seguridad (Estado), policía autonómica, docencia no universitaria, sanidad, universidades, ayuntamientos, diputaciones y cabildos. Columnas de personal: `funcionario_carrera` (incluye el estatutario de la sanidad), `funcionario_interino`, `en_practicas`, `laboral_fijo` (con fijos discontinuos), `laboral_temporal` y `otro` (eventuales, indefinidos no fijos, varios); `efectivos` es su suma. Se genera con `python3 src/empleo_publico.py <carpeta>`.
- Fuente: Registro Central de Personal, [Estadística del personal al servicio de las Administraciones públicas (EPSAP)](https://digital.gob.es/funcion-publica/dgfp/registro-central-personal/boletin.html), microdatos semestrales (hoja de totales; los cortes de julio de 2023 a julio de 2025 son la revisión de agosto de 2026), descargados el 22-10-2026. Enero de 2026: 3.071.725 efectivos.
- Cuenta **por lugar de trabajo** y su nivel más fino es la provincia. **No hay en abierto un recuento de funcionarios por municipio ni por sección**: ni la EPSAP, ni el censo (su «situación profesional» no separa público de privado), ni la EPA (provincial). Por municipio, lo más cercano son las ramas `cnae_O` (Administración pública), `cnae_P` (educación) y `cnae_Q` (sanidad) del censo, que mezclan empleo público y privado.
- Los microdatos existen desde julio de 2019, pero **no se usan los anteriores a 2023**: hasta enero de 2021 recogen 1,1 millones de efectivos y de julio de 2021 a julio de 2022, 2,7 millones (la cobertura de comunidades y entidades locales era incompleta), frente a 3,0 desde 2023.
- La asignación a provincias tiene ruido: algunos saltos de un semestre a otro son de registro, no de plantilla (en Cáceres, sanidad pasa de 8.106 a 6.459 efectivos entre enero de 2025 y enero de 2026), y algunas universidades constan en una sola provincia (Cáceres no tiene fila de universidades). Para comparar provincias conviene usar varios cortes.
- El grupo de titulación (A1…E) y la edad no se incluyen: el grupo tiene un 20% «N/D» y la edad solo viene sin provincia.

## Límites

- **Residencia, no puesto de trabajo.** Mide a qué se dedican los vecinos, no cuántos empleos hay en el municipio. Una «ciudad de servicios» que atrae trabajadores de la comarca no se ve aquí; para eso haría falta afiliación a la Seguridad Social por municipio de la cuenta de cotización, que la Seguridad Social no publica en abierto para toda España (solo algunas comunidades, como Idescat en Cataluña, la dan por municipio y siempre por residencia).
- **Secreto estadístico.** El INE no da cifras (`.`) para los municipios de menos de 50 habitantes ni para sus secciones: 568 municipios sin dato, unos 8.000 ocupados de 19,9 millones.
- El censo anual se construye a partir de registros administrativos (padrón, Seguridad Social, AEAT…), no de cuestionario; la actividad es la del establecimiento según esos registros.
- Son datos, no explicaciones: que un municipio tenga mucho empleo público o sanitario no explica por sí solo cómo vota.
