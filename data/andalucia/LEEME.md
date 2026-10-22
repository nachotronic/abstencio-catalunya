# Andalucía: malla estadística del IECA por sección censal

`malla_ieca_secciones.csv`: una fila por sección censal de 2023 de Andalucía (6.004). `seccion` y `mun_code` son códigos INE. Se genera con `python3 src/malla_ieca.py <seccionado_2023.zip> <carpeta>`, que descarga la malla municipio a municipio.

## Fuente

Instituto de Estadística y Cartografía de Andalucía (IECA), [malla estadística de 250 × 250 m](https://www.juntadeandalucia.es/institutodeestadisticaycartografia/visores/malla-estadistica/), capa `grid:gridp_250` del servicio WFS `https://www.juntadeandalucia.es/institutodeestadisticaycartografia/geoserver-ieca/grid/wfs`. Según el visor del IECA son los datos del año 2024. Descargada el 22-10-2026. Secciones: INE, [contornos del seccionado a 1 de enero de 2023](https://www.ine.es/prodyser/cartografia/seccionado_2023.zip).

## Columnas

- `celdas`: celdas de 250 m que caen en la sección (fraccionarias, ver Método).
- Población (Registro de Población de Andalucía): `pob_tot`, `pob_m`, `pob_h`; edad `edad0015`, `edad1664`, `edad65_`; nacionalidad `esp`, `ue15`, `mag` (Magreb), `ams` (América del Sur), `otr`; lugar de nacimiento `muni` (mismo municipio), `mund` (otro de la provincia), `provd` (otra provincia andaluza), `ccaad` (fuera de Andalucía), `paisd` (fuera de España); años de residencia en la vivienda `tr_05`, `tr0610`, `tr1115`, `tr16_`; nivel de estudios `ne0` (sin estudios o no consta), `ne1` (primaria), `ne2` (secundaria 1.ª etapa), `ne3` (secundaria 2.ª etapa), `ne4` (superior).
- Afiliados a la Seguridad Social por residencia: `afil_ss`, `afil_ss_m`, `afil_ss_h`, `afil_ss_a` (cuenta ajena), `afil_ss_p` (cuenta propia). **Sin actividad económica**: la malla no la trae.
- Pensiones contributivas: `penc` (perceptores), `penc_m`, `penc_h`, por tipo `pencjub`, `pencviu`, `pencjyv` (jubilación y viudedad), `pencinc`, `pencotr`, y su importe medio `*_mi` (media ponderada por perceptores).
- Demandantes de empleo `demp`, `demp_m`, `demp_h` y paro registrado `demp_pr`, `demp_pr_m`, `demp_pr_h`.

## Método y límites

- Cada celda se reparte entre las secciones de su municipio en proporción a la superficie que comparte con ellas (en ciudades muchas secciones son más pequeñas que una celda). Supone población repartida por igual dentro de la celda, así que el dato de una sección pequeña o con mucho campo es aproximado: frente a la población del Atlas de renta del INE, la mediana de la razón es 0,98 y la mitad de las secciones están entre 0,85 y 1,10. Mejor para comparar grupos de secciones o secciones grandes que para afirmar una cifra exacta de una sección.
- El IECA aplica secreto estadístico en las celdas con pocos habitantes, por eso hombres y mujeres no siempre suman el total.
- La población viene del Registro de Población de Andalucía, no del padrón del INE: suma 8.456.373 habitantes.
- Afiliados y parados son por residencia. Para la actividad por municipio, el IECA tiene en su banco de datos BADEA las consultas 868 (por municipio de trabajo) y 882 (por residencia), que no se han podido descargar porque su servicio no respondía.
