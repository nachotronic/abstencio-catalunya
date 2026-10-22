# Previsiones: plan técnico (issue #157)

Estado: borrador para que Nacho lo revise. Nada de esto publica cifras. El prototipo de `/previsiones/` usa datos ficticios, lleva `noindex` y queda fuera del sitemap.

## 1. Qué hay ya en el repositorio

| Pieza | Dónde | Nivel | Sirve para |
|---|---|---|---|
| Resultados del Congreso 2004-2023 por mesa y sección (Interior, vía pollspaindata) | `generales-2026/descargas/`, carpeta de trabajo `generales/datos/` | sección, municipio | base del modelo y backtesting |
| Serie histórica 1977-2023, municipales y europeas | `generales/datos/historico/` | municipio (sección desde 1986, con huecos en 1982) | tendencias largas |
| Votos de 2019 y 2023 por provincia con CERA | `actualidad/src/sistema/simulador.json` | provincia | reparto de escaños (el prototipo lo usa) |
| Renta (Atlas de Renta INE 2023), edad, extranjeros, Censo 2021 | `generales-2026/descargas/secciones.csv` | sección | covariables |
| Contornos de sección 2023 y provincias | `generales-2026/data/sec/`, `provincias.json` | sección | mapa |
| D'Hondt y simulador del precio del escaño | `actualidad/src/sistema/` | provincia | se reutiliza la lógica |

Huecos: contornos de sección de años anteriores (cambian cada año), voto CERA por sección (no existe), resultados del Senado por candidato, encuestas.

## 2. Fuentes que faltan (por evaluar licencia y periodicidad)

- **Encuestas**: CIS (microdatos abiertos, mensual); resto de institutos, solo cifras publicadas. Decidir si se agregan nosotros o se usa un agregador con licencia clara.
- **INE**: cartografía de secciones de cada año (para traducir resultados antiguos a límites actuales), padrón continuo por sección, Atlas de Renta.
- **Interior**: resultados del Senado por candidato (necesarios para el modelo de voto limitado y el voto cruzado).
- **Catastro** (INSPIRE, edificios): se puede unir a sección. **AEAT** (renta) y **SEPE** (paro): solo municipio o código postal. Se usarán como contexto municipal, nunca como si fueran dato de sección.

## 3. Arquitectura

```
fuentes ──ETL──► datos/limpios (versionados, con pruebas)
                    │
                    ▼
                 motor (Python)  ──►  previsiones/datos/<versión>/*.json  ──►  /previsiones/ (solo lee)
                 · voto por sección      meta, observado, escenario-*.json
                 · agregación arriba     (estimación y escenario separados del dato)
                 · reparto Congreso / Senado
```

- Todo se calcula en Python. La web no hace cálculos: lee artefactos con versión (`v0-ficticio`, luego `v1-AAAAMMDD`...). Los escenarios también salen del motor.
- Tres tipos de cifra que nunca se mezclan: **dato observado**, **estimación** (con intervalo) y **escenario** (con su supuesto escrito).
- La agregación sale de las mismas simulaciones: la provincia es la suma de sus secciones, la comunidad la suma de sus provincias. Así municipio, provincia y España cuadran siempre.

## 4. Fases

1. **Auditoría y plan** (este documento) y **prototipo web con datos ficticios** (hecho en este PR).
2. **ETL versionado**: tabla larga sección × elección × candidatura con límites traducidos a 2023 (pesos por población o por edificios de Catastro). Pruebas: totales por provincia iguales a los oficiales.
3. **Baseline**: swing uniforme y proporcional desde 2023 por sección, con encuestas como entrada. Mapa por municipio y sección.
4. **Backtesting**: predecir 2019 con datos hasta 2016 y 2023 con datos hasta 2019, sin usar nada posterior. Métricas por nivel (error de voto por sección, municipio y provincia; escaños por provincia; Brier para la probabilidad de primer puesto).
5. **Modelo probabilístico**: multinivel con efectos de provincia y sección y covariables (renta, edad, extranjeros), error de encuesta correlacionado entre partidos y territorios, participación modelada aparte. Senado con su propio modelo de voto limitado (incluido el voto cruzado entre candidatos).
6. **Web y metodología pública**: integrar `/previsiones/` con fecha de actualización, descargas y página de método. Solo con el visto bueno de Nacho.

## 5. Ya comprobado en el prototipo

- El reparto D'Hondt con umbral del 3 % reproduce el Congreso oficial de 2023 (PP 137, PSOE 121, Vox 33, Sumar 31...). Es una prueba automática: `python3 -m unittest discover previsiones/src`.
- El Senado tiene 209 elegidos en 60 circunscripciones (provincias, islas, Ceuta y Melilla; Ibiza y Formentera por separado desde la LO 2/2026) con voto limitado, no con D'Hondt. El reparto actual es una aproximación con voto de lista; falta el modelo por candidato (revisión de ChatGPT, R3).

## 6. Decisiones pendientes para Nacho

1. **Fuente de encuestas**: solo CIS, o agregar todas las publicadas (más trabajo legal y de mantenimiento).
2. **Nivel de sección**: ¿se publican estimaciones por sección o solo se usan para agregar? Con secciones pequeñas el error es grande y puede leerse como dato de personas.
3. **Probabilidades**: ¿mostrar «X % de simulaciones con mayoría» o solo intervalos de escaños?
4. **Senadores designados**: tomar la composición vigente de cada parlamento autonómico (dato) o dejarlos fuera.
5. **Calendario**: a cinco semanas del 29N, un modelo validado (fases 2-5) llega muy justo. Propuesta: baseline transparente (fase 3) como mucho para el 29N y el modelo completo para las siguientes.

## 7. Avances (21/10/2026)

- **Encuestas** (Electográfica, a propuesta de Nacho): 1.047 nacionales de 2018 a 2026 y 137 por comunidad o provincia. Carpeta de trabajo `previsiones/encuestas/` del proyecto. Se citan la encuestadora y el medio original.
- **Europeas de 2024 por sección** (`src/europeas2024.py`): Sumar, Podemos y SALF por separado desde los votos por mesa; los totales cuadran con el resultado oficial sin CERA.
- **Base 2026 por sección** (`src/base2026.py`): voto de 2023 con el de Sumar repartido entre Sumar (FA) y Podemos según su peso en cada sección en 2024 (41,8 % para Podemos en el conjunto de España), y un índice de dónde vota SALF. Supuesto: ese reparto se mantiene.
- **Cambio por perfil con el CIS** (`src/perfiles.py`): modelo log-lineal de intención frente a recuerdo por edad (65+), estudios superiores y tamaño de municipio. Prueba 2019 → 2023 con el preelectoral del CIS (estudio 3411, 29.201 entrevistas), como desagregación condicionada (con los votos reales de 2023 de cada sección y de cada partido en España fijados; no es una predicción ex ante): el error medio por sección baja solo de 2,89 a 2,88 puntos frente a la subida proporcional uniforme; con la comunidad autónoma empeora (3,02). Conclusión: el perfil del CIS apenas mejora el reparto por sección; el error que queda es local. Se usará como ajuste pequeño o no se usará, y se probarán como señal local las autonómicas y municipales recientes.

## 8. Encuestas en el motor (22/10/2026, estimación interna, sin publicar)

- `src/encuestas.py`: media ponderada (última encuesta de cada encuestadora en 28 días; peso por antigüedad, vida media de 10 días, y por muestra) con la tabla de equivalencias de ChatGPT. Error de la media cinco días antes de la elección: 10N-2019, Vox −2,8 y Cs +2,5 puntos; 23J-2023, PSOE −3,4. Se resume en error ≈ 0,475·raíz(voto): unos 2,6 puntos para un partido del 30 %.
- `src/motor.py --encuestas <media.json>` (v1): parte de 2023 por provincia con Sumar repartido entre Sumar (FA) y Podemos (base 2026), SALF según su índice de las europeas y Aliança según el Parlament 2024; cada lista sube o baja en proporción hasta clavar la media nacional. Error nacional por lista con esa regla, ampliado un 25 % por las semanas que faltan y acotado al 30 %; el error reparte voto entre listas sin cambiar el total. Escribe en la carpeta de trabajo `previsiones/salidas/`, no en la web.
- Límites: subida proporcional (sin señal local ni regional), errores de partido independientes entre sí, Senado con voto de lista y Aliança sin cifra en casi ninguna encuesta (se mantiene su voto de 2024).

## 9. Señal local: europeas sí, municipales no (22/10/2026)

`src/senal_local.py` prueba, con el voto real de cada partido por provincia (o en España) dado, si una elección intermedia mejora el reparto frente a la subida proporcional desde las generales anteriores. Error medio en puntos:

| Prueba | Proporcional | Con la intermedia (α = 0,5) |
|---|---|---|
| Provincias, 2011 → 2015 con europeas 2014 | 2,85 | 1,89 |
| Provincias, 2016 → 2019-N con europeas 2019 | 2,79 | 1,87 |
| Secciones, 2011 → 2015 con europeas 2014 | 3,30 | 2,37 |
| Secciones, 2016 → 2019-N con europeas 2019 | 2,52 | 1,99 |
| Secciones, 2019-N → 2023 con municipales 2023 | 2,83 | 4,23 (empeora) |

La señal que funciona es la fuerza relativa de cada territorio en las europeas frente a las generales anteriores, a media potencia (α = 0,5, el mejor valor en las dos pruebas). Las municipales empeoran el reparto (pesan los candidatos locales). Para el 29N se aplica la de las europeas de 2024 a PP, PSOE, Vox y el espacio Sumar-Podemos en el motor v1, por provincia. Corrige además a Vox en Santa Cruz de Tenerife, donde en 2023 no tuvo candidatura al Congreso y el motor lo dejaba a cero. Autonómicas: sin datos por sección en el repositorio; quedan para después.

## 10. Backtest y error según la distancia (22/10/2026)

`src/backtest.py` rehace el motor para 10N-2019 y 23J-2023 solo con datos anteriores (generales previas, europeas de 2019 si caen en medio, media de encuestas a 5 y a 38 días, error de encuesta medido en la otra elección). Escaños mal puestos en España: 6-8 con el voto nacional exacto, 18-19 con la media a 5 días y 27-34 a 38 días. El reparto por provincias funciona; el error viene de las encuestas. A 38 días el error de la media es casi el doble que a 5 (c = 0,96 frente a 0,475), así que el motor (v1.1) mide c a la misma distancia del 29N en vez de ampliarlo un 25 %. Efecto: PP + Vox, mayoría en el 86 % de las simulaciones (antes 96 %), con las mismas medianas. Los partidos sin encuesta tienen ahora meta propia y no se encogen con el tope. Aun así, los intervalos del 80 % cubrieron el resultado en el 64-73 % de los casos: falta modelar errores correlacionados entre partidos (siguiente paso). El 28A-2019 no se puede probar (no hay encuestas de febrero a julio de 2019 en la extracción).
