# Vídeos para YouTube Shorts

Plantilla HTML en canvas (`plantilla/short.html`) que se graba fotograma a fotograma con Chromium y se codifica con ffmpeg.
Cada Short es un guion en `shorts/<nombre>.json`: gancho, métrica del mapa, región y etiquetas, foco, bloque final
(`stack`, `bars` o `facts`) y cierre. Los tiempos del guion van en escala de 30 s y se reproducen a SPEED (1,3): unos 23 s, 1080x1920.

```
python3 video/prep_geo.py data/catalunya_secciones_2023.geojson video/comun/secciones.json   # una vez
node video/render.js salt salida.mp4                       # vídeo completo (~1 min)
node video/render.js salt "fotos/f%t.png" 30 --stills 1,17 # fotogramas sueltos para revisar
```

Los textos y datos deben quedar por encima de y≈1500 y lejos del borde derecho: la interfaz de Shorts tapa esa zona.
Las cifras de cada guion salen de piezas publicadas o de `data/`. Los MP4 no van al repositorio (se publicaría en Pages):
se guardan en la carpeta del proyecto `videos/`.

## Plantilla de encuesta (sin mapa)

`plantilla/encuesta.html`, unos 21 s con cortes cada 2-4 s: gancho, cuadrícula de 100 puntos, barras por edad,
barras por partido (colores de cada partido) e ideología. Se elige con `"plantilla": "encuesta"` en el guion
(ejemplo: `shorts/mujeres-jovenes.json`, microdatos del CIS 3420; se descargan en https://www.cis.es/documents/d/cis/MD3420).

## Plantillas de mapa nacional y de D'Hondt

- `plantilla/timelapse.html`: mapa municipal de España elección tras elección (necesita `python3 video/prep_espana.py video/comun/espana.json`,
  que lee `generales-2026/data`). Guiones: `espana-1977-2023`, `republica-1933-1936`.
- `plantilla/dhondt.html`: reparto de escaños de una provincia con sus votos reales (`dhondt-cantabria`, votos de
  `actualidad/src/sistema/simulador.json`).

## Plantilla de las guías

`plantilla/guia.html`: una lista de escenas en el guion (`hook`, `lista`, `mapa` de provincias, `mapamun`, `zoom` de España a una
sección, `barras`, `lineas`, `numeros`, `reparto`, `cierre` con la ruta de la guía). Datos: `prep_provincias.py` →
`comun/provincias.json`, `prep_espana.py` → `comun/espana.json`, `prep_secciones.py 28` → `comun/sec28.json`.
Guiones: `guia-29n`, `guia-censo`, `guia-municipios` (timelapse), `guia-participacion`, `guia-renta`, `guia-seccion`.
