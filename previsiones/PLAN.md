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
- El Senado tiene 208 elegidos en 59 circunscripciones (provincias, islas, Ceuta y Melilla) con voto limitado, no con D'Hondt.

## 6. Decisiones pendientes para Nacho

1. **Fuente de encuestas**: solo CIS, o agregar todas las publicadas (más trabajo legal y de mantenimiento).
2. **Nivel de sección**: ¿se publican estimaciones por sección o solo se usan para agregar? Con secciones pequeñas el error es grande y puede leerse como dato de personas.
3. **Probabilidades**: ¿mostrar «X % de simulaciones con mayoría» o solo intervalos de escaños?
4. **Senadores designados**: tomar la composición vigente de cada parlamento autonómico (dato) o dejarlos fuera.
5. **Calendario**: a cinco semanas del 29N, un modelo validado (fases 2-5) llega muy justo. Propuesta: baseline transparente (fase 3) como mucho para el 29N y el modelo completo para las siguientes.
