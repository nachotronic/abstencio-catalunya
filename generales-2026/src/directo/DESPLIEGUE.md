# Directo del 29N: cómo se pone en marcha

El escrutinio en directo no necesita el acceso de medios de Interior. Lo lee de la web pública de resultados: en el 23J
esa web la hizo Indra y servía JSON públicos por provincia y municipio en `<web>/backend-difu`, que es lo que lee
`worker.js`. Si Interior concede el acceso de medios (las claves llegan el 17-11), se añade como segunda fuente.

Cadena: web de Interior → Worker de Cloudflare (cada minuto, 52 peticiones) → `resultados.json` (mapa) y
`provincia/<pp>.json` (fichas de municipio, unos 25 KB en vez de 2 MB) → la web.

## 1. Lo que hace Nacho una vez (en Cloudflare)

1. Contratar **Workers Paid** (5 $/mes): Cloudflare → Workers & Pages → Plans. El gratuito no llega: corta a los 10 ms de
   CPU por lectura y a las 100.000 peticiones al día, y las fichas abiertas piden datos cada minuto.
2. Crear un token: Mi perfil → API Tokens → Create Token → plantilla **«Edit Cloudflare Workers»**, con tu cuenta
   y sin zonas. Copiar el valor.
3. Guardarlo en GitHub como secreto del repositorio: Settings → Secrets and variables → Actions → New repository secret,
   nombre **`CLOUDFLARE_WORKERS_TOKEN`**. Opcional: otro secreto **`DIRECTO_CLAVE`** con una palabra cualquiera, para
   poder forzar una lectura a mano (`/actualiza?clave=…`).
4. Decir en el hilo «ya está». No hace falta pasar el token por el chat.

## 2. Despliegue (lo lanzo yo, o Nacho con un clic)

Actions → **«Directo 29N: desplegar el Worker»** → Run workflow:

- **Ahora (ensayo):** FUENTE = `https://mapaelectoral.es/generales-2026/data/simulacro.json` (simulacro con el 23J; las
  fichas dicen «Simulacro con datos del 23J»).
- **Cuando Interior abra su web:** FUENTE = la raíz de su API, acabada en `/backend-difu` (ver punto 4).

El resumen de la ejecución da la URL del Worker (`https://generales-directo.<subdominio>.workers.dev/resultados.json`).
Desplegar no cambia la web.

## 3. Encender la web (solo con «Fusiona»)

1. Probar sin publicar: abrir `https://mapaelectoral.es/?directo=<URL del Worker>` y una ficha, por ejemplo
   `https://mapaelectoral.es/municipio/madrid/madrid/?directo=<URL del Worker>`.
2. PR con `generales-2026/data/meta.json` → `"directo": {"url": "<URL del Worker>", …}`. Con eso el mapa y las fichas
   empiezan a leer el Worker cada minuto.
3. El mismo día de la noche: `NOCHE_29N = True` en `src/territorios.py` y reconstruir (construir.py → territorios.py →
   seo.py) para cambiar títulos y textos de las fichas a modo resultados.
4. Mientras FUENTE sea el simulacro, **no** se pone la URL en meta.json: la web enseñaría datos del 23J como del 29N.

## 4. Lo que tiene que mirar Nacho en su navegador

Mi conexión no llega a las webs de Interior ni de Indra (la del 23J ya ni responde), así que esto solo se puede ver
desde un navegador normal:

1. **Dominio de 2026.** En cuanto Interior lo anuncie (nota de prensa, normalmente con el simulacro, días antes), abrir la
   web de resultados.
2. Pulsar F12 → pestaña **Red (Network)** → filtro **Fetch/XHR** → recargar y pinchar en una provincia.
3. Copiar y pegar en el hilo las direcciones que aparezcan. Lo que buscamos se parece a:
   - `…/backend-difu/web/getConfig`
   - `…/backend-difu/nomenclator/getNomenclator?v=…`
   - `…/backend-difu/scope/data/getScopeData/…/1/2/1/1/90`
4. Si salen otras rutas (otra empresa, otro formato), basta con pegar una o dos respuestas (botón derecho → Copy
   response) y adapto `worker.js` en una o dos horas.

## 5. Simulacro repetible (el 18-11 o cuando sea)

Desde la raíz del repositorio, sin Cloudflare:

```
bash generales-2026/src/directo/ensayo/simulacro.sh
```

Arranca una imitación de la web de Interior con respuestas reales del 23J, pasa el escrutinio del 0 % al 30 % y al 100 %
y comprueba que el Worker sirve el total y la provincia y que cuadran. Con la web real abierta:
`FUENTE=https://…/backend-difu bash generales-2026/src/directo/ensayo/simulacro.sh`.

## 6. Plan B

- Si la provincia no trae sus municipios dentro: volver a desplegar con MODO = `municipios` (por tandas).
- Si el Worker falla del todo: actualizar a mano provincias y CCAA cada 10-15 minutos desde la web pública.
- Fuente que se cita: «Ministerio del Interior, escrutinio provisional». Es información pública reutilizable
  (Ley 37/2007); una lectura por minuto no carga su web.
