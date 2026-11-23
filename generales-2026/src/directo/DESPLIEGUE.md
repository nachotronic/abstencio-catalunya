# Directo del 29N: cómo se pone en marcha

El escrutinio en directo no necesita el acceso de medios de Interior. Lo lee de la web pública de resultados: en el 23J
esa web la hizo Indra y servía JSON públicos por provincia y municipio en `<web>/backend-difu`, que es lo que lee
`worker.js`.

**Con acceso de medios** (manual «API de descargas · Elecciones Generales 29N 2026»): Interior da a cada medio un usuario
y una clave para un repositorio de ficheros CSV, `…/descargas/csv/data/getEnvio/2` (número de envío) y
`…/getEscrutinioMunicipios/2/<pp>/<envío>` (municipios por provincia). `worker.js` lo lee con MODO = `medios`: una
petición por minuto mientras no hay envío nuevo, y 53 cuando lo hay (52 provincias y el total con los escaños). Es la
fuente preferente; la web pública queda de reserva. El manual pide no usar servicios cloud gratuitos: Workers Paid lo cumple.

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
   Con acceso de medios, otros dos secretos: **`MEDIOS_USUARIO`** y **`MEDIOS_CLAVE`**, tal como vienen en el correo de
   Interior. No se pegan en el chat.
4. Decir en el hilo «ya está». No hace falta pasar el token por el chat.

## 2. Despliegue (lo lanzo yo, o Nacho con un clic)

Actions → **«Directo 29N: desplegar el Worker»** → Run workflow:

- **Ahora (ensayo):** FUENTE = `https://mapaelectoral.es/generales-2026/data/simulacro.json` (simulacro con el 23J; las
  fichas dicen «Simulacro con datos del 23J»).
- **Cuando Interior abra su web:** FUENTE = la raíz de su API, acabada en `/backend-difu` (ver punto 4).
- **Con acceso de medios (simulacro del 18-11 de 15:00 a 20:00 y la noche del 29N):**
  FUENTE = `https://prensa.29neleccionesgenerales.es/descargas/csv`, MODO = `medios`. Autenticación básica HTTP
  (comprobado el 18-11 a las 00:40 con las credenciales de prueba: UTF-8, `getEnvio/2` devuelve solo el número).

El resumen de la ejecución da la URL del Worker (`https://generales-directo.<subdominio>.workers.dev/resultados.json`).
Desplegar no cambia la web.

## 3. Encender la web (solo con «Fusiona»)

1. Probar sin publicar: abrir `https://mapaelectoral.es/?directo=<URL del Worker>` y una ficha, por ejemplo
   `https://mapaelectoral.es/municipio/madrid/madrid/?directo=<URL del Worker>`.
2. PR con `generales-2026/data/meta.json` → `"directo": {"url": "<URL del Worker>", …}`. Con eso el mapa y las fichas
   empiezan a leer el Worker cada minuto.
3. `NOCHE_29N` en `src/territorios.py` se queda en `False`. Comprobado el 23-11: con `True` no cambia ningún title,
   description, H1, canonical ni og de las 7.324 páginas, pero solo cambia una frase de las fichas y obliga a reconstruir
   todo (construir.py → territorios.py → seo.py; territorios.py solo deja las páginas sin favicons). No compensa.
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

Para la API de medios, con su imitación (CSV con el formato del manual):
`MODO=medios bash generales-2026/src/directo/ensayo/simulacro.sh`; y contra la de verdad, el 18-11:
`MODO=medios FUENTE=https://<dominio>/descargas/csv MEDIOS_USUARIO=… MEDIOS_CLAVE=… bash …/simulacro.sh`
(desde un ordenador que llegue a Interior; mi contenedor no llega). Hasta las 15:00 del 18 ya se puede comprobar el acceso
con los ficheros fijos de 2023: `…/descargas/csv/fijos/getEscrutinioTotales/ANT/2/07-23`.

Lo que el manual no dice y hay que confirmar con el correo de acceso: cómo se autentica (el Worker manda usuario y clave
como autenticación básica HTTP; si es otra cosa, se cambia en `pideTexto`), el dominio, y la codificación de los ficheros
(UTF-8 por defecto; si las tildes salen mal, variable `MEDIOS_CODIFICACION = "latin1"`).

## 6. Plan B

- Si la provincia no trae sus municipios dentro: volver a desplegar con MODO = `municipios` (por tandas).
- Si el Worker falla del todo: actualizar a mano provincias y CCAA cada 10-15 minutos desde la web pública.
- Fuente que se cita: «Ministerio del Interior, escrutinio provisional». Es información pública reutilizable
  (Ley 37/2007); una lectura por minuto no carga su web.

## 7. Secciones (ficheros por mesa, manual final del 23-11)

`/mesas/getAvances/2/<pp>.csv` (al acabar cada avance) y `/mesas/getEscrutinio/2/<pp>.csv` (al acabar el recuento
provisional). El Worker los suma por sección (código INE de 10 cifras) y los sirve en `/secciones/<pp>.json`; el mapa pinta
las secciones del 29N con ellos. Mientras no estén, el mapa sigue por municipio: no hay que hacer nada. La raíz de `/mesas`
no la da el manual: el Worker prueba varias y apunta en `/estado` («mesas.prueba») qué respondió cada una. Si ninguna
vale, se fija con la variable `MESAS`.

## 8. Noche del 29N, paso a paso

1. Antes: Nacho pide a Interior una clave nueva (la anterior se pegó en el chat) y la guarda en el secreto `MEDIOS_CLAVE`.
2. Domingo 29 por la mañana: Actions → «Directo 29N: desplegar el Worker» con FUENTE `…/descargas/csv`, MODO `medios`,
   DIA `261129`, PUBLICA `2026-11-29T20:00:00Z` y limpiar `si`. PUBLICA: antes de las 21:00 (cierre de Canarias) no se guarda
   ningún voto ni escaño aunque la API los diera; la participación sí. DIA descarta cualquier registro que no sea del 29 (si Interior aún sirve la prueba del 25,
   no entra) y limpiar borra lo guardado de la prueba.
3. Mirar `/estado`: «ok … municipios» con datos del día, o «ninguna provincia trajo municipios» si aún no hay nada del 29.
4. Con el «Fusiona» de Nacho: PR con la URL del Worker en `generales-2026/data/meta.json` → `directo.url`. GitHub Pages y
   el navegador guardan meta.json y app.js hasta 10 minutos: contar con ese margen.
5. Apagar si algo va mal: PR que vacía `directo.url` (vuelve todo a como estaba, en 10 minutos como mucho).

## 9. Sondeo a pie de urna (la noche del 29N, de las 20:00 a los primeros datos)

Nacho, 23-11: titular del sondeo a pie de urna desde el cierre de los colegios hasta los primeros datos, de cualquier medio y
citándolo; hora elegida, las 20:00 (como las teles).

1. A las 20:00, en cuanto un medio publique su sondeo: Actions → «Directo 29N: sondeo a pie de urna» → titular, medio,
   enlace https, hora y, si los da, los escaños por partido («PP 130-135; PSOE 100-105»).
2. El Worker no lo sirve antes del 29-11 a las 20:00 en Madrid (PIEURNA_DESDE; para probarlo antes, la entrada
   pieurna_desde del despliegue). La portada lo pone encima del recuadro del directo y lo quita sola cuando el escrutinio
   pasa del 30 %. Para quitarlo antes: el mismo workflow con borrar = si.
3. Desplegar con limpiar = si borra también el titular: se pone después del despliegue de la noche.
