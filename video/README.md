# Vídeos para YouTube Shorts y X

## Vídeos automáticos (desde el 16-11-2026)

La Action **Vídeos para X** (`.github/workflows/videos.yml`) graba sola, sin guion:

- **Cada pieza nueva de Actualidad** (al cambiar `actualidad/feed.xml` en main): `node video/auto.js /actualidad/<slug>/ x-<slug>.mp4`.
  La pieza baja en el móvil, se para 2,4 s en el titular y 2,6 s en cada mapa o gráfico (hasta cuatro) y acaba con el
  cierre de la plantilla `guia` y la ruta. Sale a 1066x1896 (el máximo vertical de X), 30 fps, sin sonido y por debajo
  de 9,5 MB. Sin voz no hacen falta subtítulos: todo el texto está en la imagen. `<meta name="redes" content="no">` la salta.
- **«Encuestas, hoy»** tras cada pasada correcta de la Action «Encuestas»: `prep_encuestas.py` + `render.js encuestas-hoy`
  → `x-encuestas-AAAA-MM-DD.mp4` (se rehace con cada actualización del día). No graba nada del 24 al 28 de noviembre (veda, LOREG 69.7).

Los MP4 se suben a la release [`videos`](https://github.com/nachotronic/abstencio-catalunya/releases/tag/videos), no a la web.
También se puede lanzar a mano (Actions → Vídeos para X → Run workflow, con una ruta o `encuestas`).
**No se publica nada**: un vídeo sale en X solo cuando Nacho lo aprueba y se apunta en `redes/cola.json` con `"video"` (ver `redes/LEEME.md`).
Después, como siempre, se añade al carrusel de la portada con `src/videos.py`.

## Shorts con guion

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

`vox` usa la misma plantilla: mapa municipal con `dato: "vox23"` y `rampa` propia (`mapamun`), y barras de un solo partido (`barrasPartidos` con `alto` y `marcar`, los deciles que llevan cifra). `vox23` lo genera `prep_espana.py`.
