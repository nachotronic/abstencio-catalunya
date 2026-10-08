# Ensayo del directo sin Cloudflare

Prueba de principio a fin con una imitación de la web de resultados de Interior:
Interior simulado → Worker (`../worker.js`) → `resultados.json` → mapa.

`muestras_23j/` guarda respuestas reales de la API de la web de resultados del 23J (`resultados.generales23j.es/backend-difu`,
recuperadas del Internet Archive): la configuración, el nomenclátor (ámbitos y sus códigos) y un municipio. El simulador
sirve las mismas rutas con los datos del simulacro.

```
cd generales-2026/src/directo/ensayo
echo 0.3 > fraccion
node interior_simulado.mjs muestras_23j ../../../data/simulacro.json fraccion &
CADA=15000 node worker_local.mjs ../worker.js http://localhost:8899/backend-difu &
# desde la raíz del repositorio:  python3 -m http.server 8811
# y abrir http://localhost:8811/?directo=http://localhost:8787/resultados.json (o /insertar/?directo=…)
echo 1 > fraccion      # el escrutinio avanza; la página se refresca sola cada minuto
```

Con `wrangler dev --test-scheduled` se prueba igual en el entorno real de Cloudflare (FUENTE en `[vars]`).
