# El mapa de las generales

Pieza para las elecciones generales del 29 de noviembre de 2026: resultados del Congreso de 2004 a 2023 por municipio y sección censal (36.462 secciones), cruzados con renta, pobreza, edad y población extranjera (INE), con modo en directo para la noche electoral.

## Ficheros

En este repositorio, la web está en esta carpeta (`index.html`, `app.js`, `data/`, `descargas/`…) y los scripts en `src/`. Los scripts trabajan sobre su propia carpeta (generan `datos/` y `web/` a su lado): para publicar, se copia el contenido de `web/` aquí.

| Fichero | Qué es |
|---|---|
| `construir.py` | Descarga las fuentes (clones de GitHub) y genera `datos/` y `web/data/`. |
| `partidos.py` | Agrupación de candidaturas en familias comparables entre elecciones. |
| `pagina.py` | Genera `web/index.html` (con las cifras escritas en el HTML), `metodologia.html`, CSV, `llms.txt` y `sitemap.xml`. |
| `plantilla.html`, `metodologia.html` | Plantillas de las páginas. |
| `otras_elecciones.py` | Importa municipales y europeas desde los zips de Infoelectoral (`04202305_MESA.zip`, `07202406_MESA.zip`, `04200705_MUNI.zip`…). |
| `actualizar_29n.py` | Carga resultados nuevos: simulacro, JSON del directo, CSV por municipio o ficheros por mesa de Interior. |
| `directo/` | Cloudflare Worker que sirve los resultados en directo a la pieza. |
| `web/` | La web lista para publicar (GitHub Pages). |
| `datos/` | Tablas limpias (`secciones.csv`, `municipios.csv`, `resultados_secciones_largo.csv`, `resumen.json`). |

## Municipales y europeas

El selector de elección incluye municipales (2011-2023 por sección, 2007 por municipio) y europeas (2019 y 2024). Se cargan con `python3 otras_elecciones.py <zips de Infoelectoral>` y después `construir.py` y `pagina.py`. En la web van en ficheros aparte (`data/e/M2023.json`, `data/sec/28_M2023.json`…) que solo se descargan al elegir esa elección, para que la carga inicial no crezca. Para añadir otra, basta con subir su zip (por mesa si existe) y repetir.

Requisitos: Python 3 con pandas, geopandas, pyarrow. `python3 construir.py && python3 pagina.py` reconstruye todo.

## Noche electoral

1. **Antes**: cuando Interior publique la web de resultados (suele ser en el simulacro, unos días antes), escribir el adaptador `transformar()` de `directo/worker.js` y desplegar el Worker (`npx wrangler deploy`, con un KV y la URL de la fuente en `wrangler.toml`).
2. Poner la URL del Worker en `GENERALES_DIRECTO` y regenerar (`GENERALES_DIRECTO=https://…/resultados.json python3 construir.py`), o pasarla por la URL: `index.html?directo=https://…/resultados.json`.
3. Ensayo sin datos reales: `python3 actualizar_29n.py --simulacro 0.6` y abrir `index.html?directo=data/simulacro.json`.
4. En directo la pieza muestra % escrutado, reparto de escaños (D'Hondt por provincia con barrera del 3%, Madrid 38 y Cádiz 8) y el mapa por municipio, y se refresca cada minuto.
5. **Al terminar**: `python3 actualizar_29n.py --json resultados.json && python3 construir.py && python3 pagina.py` congela el provisional en la pieza. El texto sigue hablando del 23J: hay que reescribir la entradilla y los apartados a mano.
6. **Semanas después**: con `02202611_MESA.zip` de Infoelectoral, `python3 actualizar_29n.py --mir 02202611_MESA.zip` y reconstruir: el 29N pasa a estar también por sección.

## Comprobaciones hechas

- Totales nacionales por elección coherentes con los oficiales (diferencias de décimas por excluir el CERA).
- El reparto de escaños de 2023 recalculado con D'Hondt reproduce el oficial (PP 137, PSOE 121, Vox 33, Sumar 31…) al incluir el CERA, y da PP 136 y PSOE 122 sin él, que fue el resultado de la noche electoral.
- El lector de ficheros de Interior se ha probado con ficheros sintéticos en el formato de registro de `pollspaindata`, no con un fichero real de Interior (infoelectoral corta las conexiones desde este entorno).
