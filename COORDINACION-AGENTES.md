# Coordinación Claude ↔ ChatGPT — Mapa Electoral

**Fuente única de tareas: GitHub Issues**, salvo las ilustraciones. Este documento establece el protocolo; no es otra lista de pendientes. Las ilustraciones no llevan Issue desde el 22-10-2026 (decisión de Nacho): la lista de piezas que esperan una es [`ILUSTRACIONES.md`](ILUSTRACIONES.md), que se genera sola. No mantener estados manuales duplicados.

## Responsabilidades

- **Claude:** ingeniería web, integración, ETL, pruebas, despliegue; encarga ilustraciones o auditorías con Issue.
- **ChatGPT:** ilustraciones editoriales, revisión estadística/metodológica, análisis de fuentes y entregables específicos acordados. No modificar páginas o motor salvo encargo explícito.
- **Nacho:** prioriza, aprueba y fusiona. Ningún agente fusiona ni publica sin autorización.

## Ciclo de cada encargo

1. **Abrir Issue** con título accionable, responsable (`Claude`/`ChatGPT`), prioridad (`alta`/`media`/`baja`), tipo (`ilustración`/`auditoría`/`datos`/`web`), ruta prevista, fecha límite si existe, criterios de aceptación y dependencias. Si no hay labels, escribir los campos en el cuerpo; no crear una segunda tabla.
2. **Aceptar trabajo:** el agente comenta en la Issue «En curso», con rama `claude/<slug>` o `chatgpt/<slug>`. Revisar primero Issues abiertas y PR activas para evitar duplicar trabajo. No interpretar «En curso» como ejecución en segundo plano.
3. **Entregar:** abrir PR contra `main`, referenciar `Refs #N` (no `Closes` hasta aceptación), añadir qué cambió, pruebas ejecutadas, limitaciones y archivos. En la Issue, comentar enlace a PR y estado «En revisión».
4. **Revisión cruzada:** Claude revisa integración, rutas y pruebas de las entregas de ChatGPT; ChatGPT revisa cifras, metodología y estilo de piezas de Claude cuando se le solicite. Los hallazgos bloqueantes quedan en comentarios de PR, con evidencia.
5. **Cerrar:** solo tras revisión de Nacho, fusión y comprobación del archivo/resultado. Si falta binario o una fuente, **no** marcar «Hecho». Cerrar Issue con enlace al resultado.
6. **Bloqueos:** dejar comentario «Bloqueado» con causa concreta, información faltante y siguiente acción. El otro agente lo leerá en su próxima sesión; **GitHub no garantiza avisos ni ejecución automática entre agentes**.

## Protocolo especial: ilustraciones

- Sin Issue ni fila en `ENCARGOS.md`. La cola es `ILUSTRACIONES.md`: piezas con un gráfico (o nada) como cabecera, de la más reciente a la más antigua, con la guía de estilo. Se rehace con cada `construir.py` de Actualidad y la pieza sale de la lista en cuanto tiene ilustración.
- Claude publica las piezas con un gráfico de datos como cabecera y no las bloquea esperando ilustración.
- ChatGPT hace la ilustración que pida Nacho y la sube él mismo: rama `chatgpt/ilustracion-<slug>`, solo `img/actualidad/buzon/<slug>.jpg`, PR «Ilustración: <slug>». Nacho no la descarga ni la reenvía.
- Claude recoge esos PR (en el repaso diario o cuando Nacho le avise), la pasa a `img/actualidad/fotos/<slug>.jpg` a 1280×720 sin recortar, pone `ia=True`, enseña el resultado a Nacho y publica con su OK. Nunca reemplazar gráficos/mapas de datos dentro de la pieza por ilustraciones.

## Protocolo especial: datos y modelos

- Una PR por conjunto independiente de datos o auditoría; fuente y fecha de extracción por fila o documento.
- No usar valores sin verificar; no tratar agregados municipales como sección censal; distinguir observado, inferido y escenario.
- Las auditorías se registran como revisión, no como código corregido, salvo que la PR incluya la corrección y pruebas.
- No publicar predicciones sin aprobación explícita.

## Traspaso entre sesiones

**Al iniciar:** leer `AGENTS.md`, este documento, Issues abiertas pertinentes y PR activas. Identificar bloqueos y comprobar qué cambió desde la última sesión. **Al terminar:** dejar en la Issue un comentario de máximo cinco líneas: estado, enlace, pruebas, bloqueo y siguiente responsable.

## Estado

- Previsiones: [#157](https://github.com/nachotronic/abstencio-catalunya/issues/157).
- Ilustraciones: las Issues del flujo antiguo (#165, #171-#201) se cerraron el 23-10-2026; lo pendiente está en `ILUSTRACIONES.md`.

**Regla clave:** GitHub es el buzón compartido, no un canal de conversación instantánea. Los agentes consultan las Issues al ser activados; ninguno puede asumir que el otro recibe mensajes automáticamente.
