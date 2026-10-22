# Encuestas de generales

Se actualizan solas dos veces al día (workflow `Encuestas`, 06:20 y 19:20 UTC) y solo hay commit si cambia algún CSV.

| Fichero | Qué es |
|---|---|
| `encuestas_limpias.csv` | **El que hay que usar.** Una fila por encuesta (España y por comunidad/provincia): encuestadora, medio, inicio y fin del trabajo de campo, muestra, método, una columna por partido del modelo y enlace a la fuente original. |
| `generales_espana.csv` | Formato largo tal como lo publica Electográfica (una fila por encuesta y partido). Lo lee `previsiones/src/encuestas.py`. |
| `generales_infraestatales.csv` | Lo mismo para encuestas de generales por comunidad o provincia. |
| `wikipedia_generales_espana.csv` | Encuestas nacionales desde 2023 según Wikipedia (CC BY-SA 4.0), mismo formato que la tabla limpia. |
| `faltan_en_electografica.csv` | Encuestas de Wikipedia de los últimos 120 días sin pareja en Electográfica (sobre todo ElectoPanel de Electomanía). |
| `resumen.json` | Fecha de descarga, recuentos, última encuesta y siglas sin equivalencia. |

Partidos: los nombres se unifican con `previsiones/datos/partidos_encuestas.csv`. Las siglas del mismo espacio se suman
(FA + Compromís + FV = SUMAR). En 2019 y 2023, SUMAR es el espacio de Unidas Podemos + Más País.

Citas: se cita siempre la encuestadora y el medio original (`fuente_original`), nunca el agregador. De Electográfica
solo se guardan las cifras y la ficha técnica, no sus textos ni gráficos.

Huecos conocidos: un tercio de las encuestas de 2026 de Electográfica no trae fechas de campo (entonces `encuestas.py`
usa la publicación menos 3 días). Antes de 2018 el feed tiene otro formato y no se lee.
