# Preregistro de la previsión del 29N (BORRADOR, pendiente del visto bueno de Nacho)

Qué se fija antes de la elección para poder evaluarla después sin trampas. Nada de esto se publica sin su aprobación.

## Modelo
- Motor `src/motor.py --encuestas` en la versión del commit que se etiquete como `previsiones-29n` (v1.1 o posterior).
- Media de encuestas de `src/encuestas.py` (última de cada casa en 28 días, peso por antigüedad y muestra), sin
  corregir el efecto de cada casa ni el sesgo del sector: ninguna de las dos correcciones mejoró fuera de muestra
  (§12 de PLAN.md).
- Error de encuesta c según los días que faltan, de `error_encuestas/error_por_distancia.csv` (fuente «españa»).
- Reparto por provincia: generales de 2023 con la señal de las europeas de 2024 (α = 0,5).

## Calendario
- Última actualización con encuestas cuyo trabajo de campo acabe hasta el lunes 23 de noviembre de 2026 (último día
  en que se pueden publicar encuestas: art. 69.7 LOREG, cinco días antes de la votación).
- La previsión que se evalúa es la última publicada antes de la jornada de reflexión.

## Qué se mide después del 29N (con el resultado oficial)
1. Escaños mal puestos en España (mediana frente al resultado, suma de diferencias / 2).
2. CRPS de los escaños de cada lista, sumado sobre las listas.
3. Cobertura: cuántas listas caen dentro de su intervalo del 80 % (lo esperado: 8 de cada 10).
4. Puntuación de Brier de la probabilidad de mayoría absoluta de PP + Vox.
5. Escaños mal puestos por provincia.

## Contra qué se compara
- «Repetir 2023»: el resultado de 2023 con el espacio de Sumar repartido como en el motor.
- «Aditivo»: la misma media de encuestas con la misma subida o bajada en puntos en todas las provincias.
El backtest de 2019 y 2023 (§10 y PLAN.md) da la vara de medir: a 5 días, el motor puso mal 18-19 escaños.

## Compromiso
Se publica la evaluación, salga como salga, en la misma sección y con la misma visibilidad que la previsión.
