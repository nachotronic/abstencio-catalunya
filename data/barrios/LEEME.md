# Barrios de las grandes ciudades

Qué secciones censales del INE (2023) forman cada barrio de las capitales de provincia y de los municipios de más de
100.000 habitantes. Lo genera `src/barrios_osm.py`; lo usan las fichas de barrio de `src/territorios.py`
(`/municipio/<provincia>/<municipio>/<barrio>/`).

- `secciones_barrio.csv`: `tract_code`, `mun_code`, `barrio`, `distrito`, `nivel` (10 = barrio, 9 = distrito, el nivel
  administrativo de OpenStreetMap), `osm_id` (relación de OSM, u `of-N` si el límite es de fuente municipal), `solape` (parte de la superficie de la sección dentro del barrio).
- `fuentes.json`: ciudades cuyos límites no salen de OSM sino del ayuntamiento u otra recopilación (Vitoria-Gasteiz,
  A Coruña, Murcia y Alicante), con la fuente y su enlace. En Murcia, `distrito` distingue casco urbano y pedanías.
- `geo/<mun_code>.json`: secciones de cada ciudad, simplificadas (metros, ETRS89 / UTM 30N), para los mapas de las fichas.

Límites de barrio: © colaboradores de OpenStreetMap, licencia ODbL (https://www.openstreetmap.org/copyright), salvo las
ciudades de `fuentes.json`.
Cada sección va al barrio con el que comparte más superficie; si menos de la mitad cae dentro de algún barrio, se queda
sin asignar. Una ciudad solo tiene fichas si al menos el 70 % de sus secciones cae en algún barrio y tiene cuatro o más.
Donde OSM no tiene barrios (nivel 10) se usan los distritos (nivel 9). Un barrio necesita tres secciones para tener ficha.
