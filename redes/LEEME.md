# Redes sociales automáticas

La Action **Redes sociales** (`.github/workflows/redes.yml`) mira cada 15 minutos y en cada push a main:

1. **Piezas nuevas de Actualidad** (del `actualidad/feed.xml` publicado). Antes de anunciar una pieza comprueba que la
   página responde 200, que no es `noindex` y que su imagen de compartir existe. Publica **solo** el titular y la entradilla
   de la propia pieza (`og:title`, `og:description`), que ya pasaron la revisión del editor, más el enlace y la imagen.
   No redacta nada nuevo.
   - Para que una pieza no salga en redes: `<meta name="redes" content="no">` en su `<head>`.
   - Solo se anuncian piezas de las últimas 36 horas. Al activar una red por primera vez, todo lo que ya hay en el feed
     cuenta como publicado, así que no suelta el archivo de golpe.
2. **La cola** `redes/cola.json`: publicaciones aprobadas por Nacho con su hora (de Madrid). Si una entrada lleva más
   de 6 horas de retraso, se da por caducada y no sale.

Lo publicado queda apuntado, con el enlace a cada post, en `registro.json` de la rama `redes-registro`. El resumen de
cada pasada sale en la pestaña Actions.

## Interruptores (Settings → Secrets and variables → Actions → *Variables*)

| Variable | Qué hace |
|---|---|
| `REDES_ACTIVAS` | Redes en las que se publica, separadas por comas: `bluesky,mastodon,telegram,x,threads,instagram`. Vacía significa modo ensayo: no publica nada y solo muestra en el resumen qué habría salido. |
| `REDES_PAUSA` | Con el valor `1` lo para todo al instante. |

## Formato de la cola

```json
[
  {"id": "encuestas-2026-11-05", "cuando": "2026-11-05 13:30",
   "texto": "Texto aprobado, igual para todas las redes",
   "enlace": "https://mapaelectoral.es/encuestas/",
   "imagen": "img/compartir/encuestas.jpg",
   "redes": ["x", "bluesky", "mastodon", "telegram", "threads", "instagram"],
   "texto_x": "(opcional) versión de ≤280 caracteres con el enlace incluido",
   "texto_instagram": "(opcional) pie para Instagram",
   "alt": "(opcional) texto alternativo de la imagen"}
]
```

`id` no se puede repetir. Sin `redes` sale en todas. Instagram solo publica entradas con `imagen`.

## Claves que hay que sacar (una vez)

Todas van en **Settings → Secrets and variables → Actions → New repository secret**. Nadie más las ve.

### Bluesky (gratis, 2 minutos)
1. Crea la cuenta (p. ej. `mapaelectoral.bsky.social`). Si quieres, luego se puede usar el dominio `mapaelectoral.es` como nombre de usuario.
2. Ajustes → Privacidad y seguridad → **Contraseñas de aplicación** → Añadir.
3. Secretos: `BLUESKY_USUARIO` (el usuario, sin @) y `BLUESKY_PASSWORD_APP`.

### Mastodon (gratis, 3 minutos)
1. Crea la cuenta en un servidor, por ejemplo `mastodon.social`.
2. Preferencias → Desarrollo → **Nueva aplicación**. Deja marcados solo `write:statuses` y `write:media` y guarda.
3. Abre la aplicación y copia **Tu token de acceso**.
4. Secretos: `MASTODON_SERVIDOR` (`https://mastodon.social`) y `MASTODON_TOKEN`.

### Telegram (gratis, 3 minutos)
1. En Telegram, habla con **@BotFather** → `/newbot` → te da un token.
2. Crea un canal público (p. ej. `@mapaelectoral`) y añade el bot como **administrador** con permiso para publicar.
3. Secretos: `TELEGRAM_TOKEN` y `TELEGRAM_CANAL` (`@nombredelcanal`).

### X (de pago por uso, unos 0,01 $ por post; compruébalo en la consola)
1. Entra en **developer.x.com** con la sesión de @_mapaelectoral y crea un proyecto y una app.
2. En la app: *User authentication settings* → permisos **Read and write**, tipo *Web App/Automated App*. Como URL de
   callback y web vale `https://mapaelectoral.es/`.
3. *Keys and tokens*: genera **API Key and Secret** y, **después** de poner Read and write, **Access Token and Secret**.
4. Carga crédito (unos 10 $ dan para meses).
5. Secretos: `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN` y `X_ACCESS_SECRET`.

### Instagram (gratis, unos 15 minutos)
1. La cuenta de Instagram tiene que ser **profesional** (Configuración → Tipo de cuenta → Cambiar a cuenta profesional → Creador o Empresa).
2. En **developers.facebook.com** → Mis apps → Crear app → caso de uso **«Gestionar mensajes y contenido en Instagram»** (API de Instagram con inicio de sesión de Instagram).
3. En *Configuración de la API con inicio de sesión de Instagram* → **Generar tokens de acceso** → añade la cuenta, inicia sesión y acepta.
   Copia el **token** y el **ID de usuario de Instagram** que aparece junto a la cuenta.
4. La app puede quedarse en modo desarrollo: basta para publicar en tu propia cuenta.
5. Secretos: `INSTAGRAM_USUARIO_ID` e `INSTAGRAM_TOKEN`.

### Threads (gratis, unos 10 minutos)
1. En la misma web de Meta, crea otra app con el caso de uso **«Acceder a la API de Threads»**, con los permisos `threads_basic` y `threads_content_publish`.
2. *Roles de la app* → añade tu cuenta de Threads como **tester de Threads**, y acepta la invitación en Threads → Configuración → Cuenta → Permisos del sitio web.
3. En el **Explorador de la API de Graph** (o con el generador de tokens de la app) genera un token de usuario de larga duración y apunta tu ID de usuario de Threads.
4. Secretos: `THREADS_USUARIO_ID` y `THREADS_TOKEN`.

Los tokens de Meta duran 60 días. La Action intenta ampliarlos los días 1 y 15 de cada mes y avisa en el resumen si Meta
devuelve un token nuevo que haya que copiar al secreto.

## Activar

Cuando estén los secretos de una red, añádela a la variable `REDES_ACTIVAS`. La próxima pasada lo dice en el resumen,
y la primera pieza nueva que entre después ya sale en esa red.
