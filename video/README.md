# Vídeos para YouTube (prototipo)

Composiciones HTML en canvas que se graban fotograma a fotograma con Chromium y se codifican con ffmpeg.

```
python3 video/prep_geo.py data/catalunya_secciones_2023.geojson video/short-salt/secciones.json
node video/render.js video/short-salt salida.mp4 30                    # vídeo completo
node video/render.js video/short-salt "fotos/f%t.png" 30 --stills 1,16  # fotogramas sueltos
```

Cada composición expone `window.render(t)` (t en segundos), `window.DUR` y `window.ready`.
Los MP4 no van al repositorio: se guardan en la carpeta del proyecto `videos/`.
