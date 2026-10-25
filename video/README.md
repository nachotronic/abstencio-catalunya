# Vídeos para YouTube Shorts

Plantilla HTML en canvas (`plantilla/short.html`) que se graba fotograma a fotograma con Chromium y se codifica con ffmpeg.
Cada Short es un guion en `shorts/<nombre>.json`: gancho, métrica del mapa, región y etiquetas, foco, bloque final
(`stack`, `bars` o `facts`) y cierre. Duración fija de 30 s, 1080x1920.

```
python3 video/prep_geo.py data/catalunya_secciones_2023.geojson video/comun/secciones.json   # una vez
node video/render.js salt salida.mp4                       # vídeo completo (~1 min)
node video/render.js salt "fotos/f%t.png" 30 --stills 1,17 # fotogramas sueltos para revisar
```

Los textos y datos deben quedar por encima de y≈1500 y lejos del borde derecho: la interfaz de Shorts tapa esa zona.
Las cifras de cada guion salen de piezas publicadas o de `data/`. Los MP4 no van al repositorio (se publicaría en Pages):
se guardan en la carpeta del proyecto `videos/`.
