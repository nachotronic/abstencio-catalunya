# Encargos para ChatGPT: previsiones (issue #157)

Encargados por Nacho el 21/10/2026. Al entregar cada uno, pasa su fila de `ENCARGOS.md` a «Hechos» con el número del PR.

Cuatro tareas independientes. Cada una es un PR propio contra `main`, en una rama `chatgpt/<tema>`, siguiendo `AGENTS.md`. Antes de empezar: `git fetch origin main` y partir de lo último. No toques `previsiones/src/motor.py` ni las páginas.

---

## 1. Revisión de las reglas y de la validación

**Rama:** `chatgpt/revision-previsiones`

Revisa, en el repositorio nachotronic/abstencio-catalunya:
- `previsiones/src/reglas.py`: reparto D'Hondt del Congreso (umbral del 3 % sobre votos válidos con el blanco incluido, art. 163 LOREG; escaños de 2026 según el Real Decreto 806/2026) y voto limitado del Senado (arts. 165-166 LOREG: 4 senadores y 3 votos por provincia; 3 y 2 en Gran Canaria, Mallorca y Tenerife; 1 en el resto de islas; 2 y 1 en Ceuta y Melilla).
- `previsiones/src/test_reglas.py`: ¿falta algún caso?
- `previsiones/src/perfiles.py`, función `valida()`: la comparación 2019 → 2023 entre la subida uniforme y el ajuste por perfil del CIS. ¿Hay fuga de información (datos de 2023 usados para predecir 2023 más allá de los totales nacionales y de sección) o algún error de planteamiento?

**Entrega:** un fichero `previsiones/revisiones/chatgpt-reglas.md` con cada hallazgo (archivo, línea, qué falla, por qué y la cita de la ley o del dato). Si un error es claro y pequeño, corrígelo en el mismo PR y añade una prueba en `test_reglas.py`. Comprueba que `python3 -m unittest discover previsiones/src` sigue en verde.

---

## 2. Tabla de nombres de partido de las encuestas

**Rama:** `chatgpt/partidos-encuestas`

Las encuestas vienen de Electográfica con los nombres tal como los publica cada encuestadora (FA, SUMAR, UP-ECP-EC, UNIDAS PODEMOS, UNIDOS PODEMOS, MÁS PAÍS, MÁS PAÍS-EQUO, Cs, CS, SALF, ALIANÇA.CAT, CCa, EAJ-PNV, EH BILDU, COMPROMÍS-FV, ADELANTE ANDALUCÍA…).

**Entrega:** `previsiones/datos/partidos_encuestas.csv` con las columnas `nombre_encuesta,partido_modelo,desde,hasta,nota`. Valores de `partido_modelo`: PP, PSOE, VOX, SUMAR (incluye FA y las confluencias del espacio de Sumar), PODEMOS, CS, SALF, ERC, JUNTS, BILDU, PNV, BNG, CC, UPN, ALIANCA, OTROS. `desde` y `hasta` (AAAA-MM) solo cuando un mismo nombre cambia de partido según la fecha (por ejemplo, Unidas Podemos antes de 2023 es SUMAR). En `nota`, el motivo de cada caso dudoso. Los nombres que aparecen en las encuestas nacionales de 2018 a 2026 son: ADELANTE ANDALUCÍA, ALIANÇA.CAT, BNG, CCa, COMPROMÍS, COMPROMÍS-FV, CS, Cs, CUP-PR, DEM, EAJ-PNV, EH BILDU, ERC, EV, FA, IE, JUNTS, MÁS PAÍS, MÁS PAÍS-EQUO, PODEMOS, PP, PSOE, SALF, SMR, SUMAR, SUMAR+PODEMOS, UNIDAS PODEMOS, UNIDOS PODEMOS, UP-ECP-EC, UPN, VOX. Si no sabes qué es una sigla (DEM, EV, IE, SMR), búscala en la encuesta original de Electográfica y explícalo en `nota`; si no se puede saber, OTROS.

---

## 3. Senadores designados por los parlamentos autonómicos

**Rama:** `chatgpt/senadores-designados`

**Entrega:** `previsiones/datos/senadores_designados.csv` con las columnas `comunidad,senadores,partido,fecha_designacion,fuente_url`. Una fila por comunidad y partido, con el número de senadores designados que tiene ese partido en la legislatura vigente. Fuente: la web del Senado (composición por grupos y procedencia «designado por el Parlamento de…») o el boletín oficial de cada parlamento. Cada fila con su enlace. El total debe cuadrar con el número oficial de senadores designados de la legislatura; si no cuadra, dilo en el PR. Nada de cifras sin fuente.

---

## 4. Comprobar que no faltan encuestas

**Rama:** `chatgpt/cobertura-encuestas`

Compara la lista de encuestas de elecciones generales de España publicadas desde el 1 de enero de 2026 en Electográfica (https://www.electografica.com, etiqueta «Generales») con otra lista pública de sondeos de 2026 (por ejemplo, el artículo de Wikipedia de sondeos para las próximas elecciones generales).

**Entrega:** `previsiones/revisiones/cobertura-encuestas-2026.md` con una tabla de las encuestas que están en una lista y no en la otra: encuestadora, medio, fechas de campo, muestra, enlace a la publicación original. Indica también el total de cada lista. No copies estimaciones que no tengan enlace a la publicación original.
