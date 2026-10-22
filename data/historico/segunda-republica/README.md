# Atlas electoral de la Segunda República

Fuente: Toni Rodon, Pau Vall-Prat y Diego Martín-Álvarez, *Electoral Atlas of the Spanish Second Republic*. DOI: https://doi.org/10.34810/DATA3274. Manual versión 2.0, septiembre de 2026. ZIP recibido de Nacho el 22-10-2026.

Licencia del conjunto: **CC BY-NC-SA 4.0**, https://creativecommons.org/licenses/by-nc-sa/4.0/. Atribuir autores y fuente, indicar transformaciones y respetar uso no comercial y compartir igual. La inclusión en el repositorio no cambia esta licencia; antes de cualquier explotación comercial debe aclararse el permiso con los titulares.

## Datos incorporados

- `dataset_muni_vote_shares_wide.csv.gz`: resultados procesados por municipio, censo, participación, bloques y cobertura, 1933 y 1936.
- `dataset_district_vote_shares_wide.csv.gz`: resultados procesados por circunscripción, 1931, 1933 y 1936.
- `dataset_district_raw_long.csv.gz`: votos por candidato y circunscripción, 1931, 1933 y 1936.
- `Readme.txt` y `data_codebook.pdf`: documentación original sin modificaciones.
- `inventario.json`: todos los ficheros del ZIP, SHA-256, columnas, filas y años efectivamente presentes.

Los CSV incorporados conservan exactamente los bytes originales, comprimidos con gzip. Se leen con UTF-8 con BOM (`utf-8-sig`), separador `;`, coma decimal y `NA` como ausencia. Los códigos territoriales deben leerse como texto.

Ejemplo:

```python
import pandas as pd
from pathlib import Path
base = Path('data/historico/segunda-republica')
df = pd.read_csv(base / 'dataset_muni_vote_shares_wide.csv.gz',
                 sep=';', decimal=',', encoding='utf-8-sig',
                 dtype={'cod_mun': str, 'cod_prov': str, 'cod_ccaa': str})
```

El ZIP contiene además resultados municipales y de sección por candidato y una tabla maestra. Para evitar duplicar cerca de un gigabyte de CSV, no se versionan esas tablas en esta primera incorporación. Se recuperan sin alteración con `python3 data/historico/segunda-republica/importar.py /ruta/doi-10.34810-data3274.zip /ruta/destino`, verificando todos los SHA-256 del inventario. El ZIP fuente se conserva en el archivo adjunto del proyecto de ChatGPT y en su depósito DOI.

## Límites metodológicos

- Solo primeras vueltas en esta edición. 1931 no está disponible por municipio ni sección.
- Voto por candidato: cada elector podía votar a varias personas. No interpretar la suma de votos de candidatos como electores ni como voto actual a listas.
- Las variables `pct_original`, `pct_sumbased`, `pct_meanbased` y `pct_combined` tienen denominadores y procedimientos distintos: consultar el manual antes de elegir una.
- No convertir `NA` en cero. Consultar fuente, secciones ausentes y cobertura antes de comparar territorios. Una etiqueta de sección no garantiza un resultado desagregado real en todas las filas.
- Los totales oficiales de circunscripción pueden diferir de la suma municipal; no corregirlos automáticamente.
- Los códigos y límites históricos requieren concordancias documentadas para unirse a municipios o secciones actuales. No hay geometrías en el ZIP.
- No incluye renta, ocupación ni otras covariables socioeconómicas.
- El README original menciona abril de 1931; el manual y los registros de generales indican junio de 1931. Para fechas utilizar los registros y documentar cualquier discrepancia.

Esta fuente se incorpora para análisis históricos. No modifica el motor de previsión del 29N ni publica resultados o páginas nuevas.
