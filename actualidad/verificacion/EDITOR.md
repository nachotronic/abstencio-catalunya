# Lista fija del hilo editor

Regla de Nacho (3-11-2026): ninguna pieza de Actualidad o Internacional se fusiona sin la revisión de un hilo editor separado y sin «Verificar piezas» en verde. Esta lista es lo que el editor revisa **a mano**, lo que la Action no puede comprobar. Sale de los fallos que el repaso diario encontró en piezas ya fusionadas entre el 20-10 y el 7-11-2026.

El editor copia la lista en su comentario del PR y marca cada punto. Un punto sin marcar es un «no fusionar».

```
Revisión del editor · <slug>
- [ ] 1. Informe de «Verificar piezas» leído: 0 errores y cada aviso explicado (redondeo, tablas, modelo, navegador, enlaces 403)
- [ ] 2. Cifras externas: cada una abierta en su fuente, con el mismo número, la misma fecha y el mismo ámbito
- [ ] 3. Nombres propios: personas, cargos, partidos y lugares contra la fuente primaria; cada nombre escrito igual en toda la pieza
- [ ] 4. Fechas y tiempos: día de la semana, «hace N días», «a N días de la votación», y nada en futuro que ya haya pasado
- [ ] 5. Modelo: si cita el modelo, lleva su fecha, y sus cifras coinciden con /encuestas/<provincia>/ y con las listas de ese día (o la pieza explica la diferencia)
- [ ] 6. Titular, entradilla, gráfico y tabla dicen la misma cifra con el mismo redondeo
- [ ] 7. Redacción: nada causal, nada sobre personas con datos de territorios, y ninguna palabra que diga lo contrario del dato («por delante» de quien vota menos)
- [ ] 8. Citas literales: enlazadas, con autor y fecha; las traducidas, marcadas como traducción propia
- [ ] 9. Internacional: ningún dato, color, plantilla ni fuente española; nombres de países, estados y regiones en su forma española
- [ ] 10. En móvil: la pieza abierta a 390 px, con los gráficos y el mapa montados y la ilustración y su pie correctos
```

## Cómo revisar cada punto

1. **Informe de la Action.** Está en la pestaña «Checks» del PR, en «Verificar piezas». Los avisos no bloquean, pero cada uno necesita una línea del editor: «es correcto porque…» o «corregido». Los enlaces con 403 (NYT, Cook, infoelectoral…) se abren a mano una vez.
2. **Cifras externas.** El informe las lista aparte («cifras externas para el editor»). Se comprueba que la fuente diga ese número, de esa fecha y de ese ámbito (provincia frente a comunidad, residentes frente a censo con CERA, porcentaje sobre votos válidos frente a votos a candidaturas).
3. **Nombres propios.** Hay que buscar cada persona en la fuente primaria: el BOE para candidatos, la web oficial para cargos. En piezas internacionales, el nombre del estado o país se escribe igual en toda la pieza: Nuevo Hampshire siempre, nunca New Hampshire en una frase y Nuevo Hampshire en otra.
4. **Fechas.** Hay que comprobar el día de la semana de cada fecha. En las previas («vota el sábado», «mañana se sabrá») hay que decidir qué pasará con el texto cuando llegue el día: o se actualiza esa noche o se escribe sin tiempo relativo.
5. **Modelo.** Se abren /encuestas/<provincia>/ y /listas-electorales-29n/<provincia>/ y se comparan con la pieza. Si la pieza usa el modelo de otro día, lo dice en el texto. Desde el PR #504, los cálculos de la declaración pueden usar `provincia_modelo('AAAA-MM-DD', cod, lista)`.
6. **La misma cifra en todas partes.** El control de redondeo avisa cuando el texto y una tabla redondean distinto, pero solo cuando la tabla nombra la misma fila. El gráfico y el titular se miran a mano.
7. **Redacción.** Se leen los párrafos con la etiqueta «patrón» e «hipótesis» buscando verbos causales («provoca», «hace que», «por eso») y frases sobre personas («quien vive…», «los votantes de…») cuando el dato es de municipios o secciones.
8. **Citas.** Cada cita lleva enlace a donde se publicó. Si está traducida, se marca como «(traducción propia)».
9. **Internacional.** La Action ya bloquea partidos y fuentes españolas. El editor mira además los colores, la leyenda del mapa y los textos de plantilla («provincia», «sección censal», «escaños del Congreso»).
10. **Móvil.** La Action abre la pieza a 390 px y busca errores. El editor la mira de verdad: el mapa se ve, la tabla se puede desplazar y la ilustración tiene su pie y la marca de IA si la lleva.
