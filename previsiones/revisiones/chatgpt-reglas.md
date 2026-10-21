# Auditoría independiente de reglas y validación (21-10-2026)

**Alcance:** lectura de `reglas.py`, `test_reglas.py` y `perfiles.py` en `main`. No se han ejecutado los tests ni el backtesting con datos externos: esta revisión es estática. **No publicar pronósticos del Senado ni métricas de validación como definitivos** hasta corregir los hallazgos.

## Hallazgos bloqueantes

### R1 — Circunscripciones insulares desactualizadas para noviembre de 2026
- **Archivo y líneas:** `previsiones/src/reglas.py:22-26`, `test_reglas.py:43-47`.
- **Problema:** `07E` agrupa «Eivissa-Formentera» y asigna un único senador. La **LO 2/2026** reformó el art. 165.2 LOREG y el **RD 806/2026, art. 3.2**, enumera **Ibiza y Formentera separadamente**, un senador cada una. Por tanto, el modelo pierde una circunscripción y un senador de elección directa; el test que exige 59 circunscripciones y 208 elegidos congela la configuración anterior.
- **Corrección:** separar `07E` en dos identificadores distintos, comprobar la correspondencia territorial y actualizar el test y la suma de escaños conforme a la norma vigente.
- **Fuente:** https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672 ; https://www.boe.es/eli/es/rd/2026/10/05/806

### R2 — Votos permitidos en Ceuta y Melilla mal codificados
- **Archivo y líneas:** `reglas.py:36-37,54-76`, `test_reglas.py:49-54`.
- **Problema:** las circunscripciones 51 y 52 aparecen con `votos_elector=1`. **Art. 166.1.a LOREG vigente: hasta DOS votos en Ceuta y Melilla**. El algoritmo especial para `senadores==2 and votos_elector==1` no representa su papeleta.
- **Corrección:** cambiar a 2 votos y reemplazar el cálculo de dos escaños por una simulación basada en candidatos, no por la regla arbitraria de dividir entre dos el apoyo al primer partido.
- **Fuente:** https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672

### R3 — El Senado no se puede obtener mecánicamente de votos a partidos
- **Archivo y líneas:** `reglas.py:54-76`.
- **Problema:** la función asigna automáticamente 3+1, 2+1 o 2+0 escaños por ranking de partidos; presupone que los electores votan en bloque y que las candidaturas presentan exactamente `votos_elector` candidatos. Art. 166.1.b LOREG proclama **personas candidatas más votadas**, no listas. Hay voto cruzado, distinto número de candidaturas y variación individual. Además, con un único partido y 4 escaños la función devuelve solo 3: **no conserva el número de escaños**.
- **Corrección:** renombrar la función como heurística explícita, no usarla para proyección oficial; implementar un modelo por candidatura con votos personales, número real de candidatos y escenarios de voto cruzado. Test de conservación de escaños cuando existan suficientes candidatos.
- **Fuente:** https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672

### R4 — Fuga de resultados de 2023 en la «validación» 2019 → 2023
- **Archivo y líneas:** `perfiles.py:113-117,123-135`.
- **Problema:** `filas=vb.sum(axis=1)` introduce **votos reales de 2023 de cada sección** y `cols=vb.sum()` introduce **votos reales nacionales de 2023 por partido**. Ambas magnitudes se fuerzan con IPF antes de comparar con `vb`. El error mide una *desagregación condicional con márgenes observados*, **no una predicción ex ante** de participación ni de voto. Aunque usar totales nacionales 2023 podría justificarse en un ejercicio *condicionado*, los totales reales por sección son una fuga decisiva si se etiqueta como pronóstico.
- **Corrección:** dos experimentos separados y claramente etiquetados: (a) hindcast ex ante con únicamente datos disponibles antes de julio de 2023 y proyección de participación; (b) desagregación condicionada a márgenes observados, sin denominarla predicción. Comparar con baseline bajo exactamente las mismas restricciones.
- **Fuente:** lógica del propio código.

### R5 — Selección de especificación en el mismo conjunto evaluado
- **Archivo y líneas:** `perfiles.py:139-148`.
- **Problema:** se elige `CON_CCAA` por el menor error sobre 2023 y se presenta el mismo periodo como validación. Es selección sobre el conjunto de prueba; la ventaja de `perfil+ccaa` puede estar sobreajustada.
- **Corrección:** definir especificación a priori o usar periodos de entrenamiento/validación/prueba separados, más pruebas espaciales fuera de muestra.
- **Fuente:** lógica del propio código.

## Riesgos adicionales y tests

- **R6 — Empates D'Hondt:** `reglas.py:47` usa `k` como desempate lexicográfico en empates completos de cociente y votos; la LOREG prevé sorteo en empate absoluto, no orden alfabético. Crear test de empate total y declarar estrategia aleatoria/reproducible.
- **R7 — Exclusión de «Otros» en reproducción 2023:** `test_reglas.py:34-40` omite votos de «Otros» al repartir. El test puede reproducir los partidos con escaños aun sin verificar si alguna lista omitida alcanzaba el umbral; añadir comprobación por provincia de candidaturas completas y votos válidos.
- **R8 — Integridad de entrada:** `dhondt` no valida `validos>=sum(votos)`, magnitudes positivas ni ausencia de votos negativos; añadir tests para umbral exacto, voto blanco, cero votos y entrada inconsistente.
- **R9 — Riesgo de duplicación y denominadores:** `perfiles.py:113-116` usa intersección de índices de `tract_code` sin verificar unicidad de sección/elección ni homogeneidad de límites 2019-2023; comprobar duplicados y cambios de sección antes de evaluar.
- **R10 — Datos CIS:** `perfiles.py:122,128` usa el estudio 3411 para estimar cambios; documentar fecha de campo y que la intención declarada/recuerdo de voto no equivalen a resultados de 2023, además de sesgos de recuerdo y posibles diferencias de codificación.

## Comprobaciones positivas
- Umbral provincial del 3% sobre votos válidos incluyendo blancos en `reglas.py:46` concuerda con art. 163.1.a.
- Magnitudes de Congreso 2026, incluyendo Madrid 38 y Cádiz 8, concuerdan con anexo del RD 806/2026.
- Ceuta y Melilla eligen un diputado por pluralidad, según art. 163.2.

## Estado de ejecución
No se han modificado fuentes ni ejecutado `python3 -m unittest discover previsiones/src`: falta checkout local y, para la validación de perfiles, ficheros CSV/SAV externos. Esta PR aporta la auditoría reproducible por archivo/línea; **los hallazgos R1 y R2 requieren corrección antes de la siguiente publicación de previsiones**.
