# Coordinación Claude ↔ ChatGPT — Mapa Electoral

**Fuente única de tareas: GitHub Issues.** Este documento establece el protocolo; no es otra lista de pendientes. `ENCARGOS.md` queda como índice histórico/creativo hasta migrar sus entradas a Issues. No mantener estados manuales duplicados.

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

- Issue con pieza/slug, concepto, formato 1280×720 JPG, plazo y guía de estilo: tonos apagados, fondo claro, minimalismo, aire, **sin palabras ni datos inventados**.
- ChatGPT entrega JPG comprobable y, si puede, PR con archivo binario. Si la herramienta no permite subir binarios, adjunta el archivo al usuario y comenta «Pendiente de integración» con nombre/ruta: **no declarar entregado en GitHub**.
- Claude integra la imagen y configura `ia=True` en fuente; comprueba que existe el archivo en la rama antes de cerrar. Nunca reemplazar gráficos/mapas de datos por ilustraciones.

## Protocolo especial: datos y modelos

- Una PR por conjunto independiente de datos o auditoría; fuente y fecha de extracción por fila o documento.
- No usar valores sin verificar; no tratar agregados municipales como sección censal; distinguir observado, inferido y escenario.
- Las auditorías se registran como revisión, no como código corregido, salvo que la PR incluya la corrección y pruebas.
- No publicar predicciones sin aprobación explícita.

## Traspaso entre sesiones

**Al iniciar:** leer `AGENTS.md`, este documento, Issues abiertas pertinentes y PR activas. Identificar bloqueos y comprobar qué cambió desde la última sesión. **Al terminar:** dejar en la Issue un comentario de máximo cinco líneas: estado, enlace, pruebas, bloqueo y siguiente responsable.

## Estado inicial al 21-10-2026 (enlaces, no lista paralela)

- Previsiones: [#157](https://github.com/nachotronic/abstencio-catalunya/issues/157); auditoría [PR #166](https://github.com/nachotronic/abstencio-catalunya/pull/166); equivalencias [PR #167](https://github.com/nachotronic/abstencio-catalunya/pull/167) (borrador).
- Ilustración prestaciones/participación: [#165](https://github.com/nachotronic/abstencio-catalunya/issues/165) — pendiente de subir JPG al repositorio.
- Encargos creativos nuevos que aún aparezcan en `ENCARGOS.md`: migrar a Issues y enlazar, sin borrar el histórico.

**Regla clave:** GitHub es el buzón compartido, no un canal de conversación instantánea. Los agentes consultan las Issues al ser activados; ninguno puede asumir que el otro recibe mensajes automáticamente.
