# Normas para agentes (ChatGPT, Codex y otros)

Este repositorio es la web [mapaelectoral.es](https://mapaelectoral.es/), publicada con GitHub Pages desde `main`. En él trabajan varios agentes de IA a la vez, así que estas normas sirven para no pisarse. El `README.md` explica qué hay en cada carpeta y cómo se genera.

## Cómo trabajar con Git

- **Nunca hagas push a `main`.** Todo cambio va en una rama propia y un pull request contra `main`. Nacho revisa y fusiona.
- Ramas: `chatgpt/<tema-corto>` (por ejemplo `chatgpt/ilustracion-sanchez`). Las ramas `claude/...` son de otro agente: no las toques.
- Antes de empezar y antes de abrir el PR, ponte al día con lo último de `main` (`git fetch origin main` y rebase). Cada push a `main` publica la web al momento.
- Un PR por tema, siempre contra `main` (nada de PR encadenados). Título en castellano que diga qué cambia; en la descripción, qué has hecho, qué has comprobado y qué falta.
- No reescribas el historial de ramas ajenas ni borres ficheros que no entiendas.
- Las páginas HTML son generadas: cambia la fuente (`src/`, `actualidad/src/`, `atlas/src/`, `generales-2026/src/`…) y vuelve a construir; no edites el HTML resultante a mano.

## Tu papel principal: ilustraciones

Lo que mejor encaja contigo son las **ilustraciones de cabecera** (collages editoriales) para las piezas de Actualidad y las series.

- Formato: JPG horizontal de **1280 × 720**, sin texto incrustado, estilo collage editorial. Una ilustración por pieza, sin repetir.
- Dónde va: `img/actualidad/fotos/<slug-de-la-pieza>.jpg`, y en `actualidad/src/construir.py` la pieza lleva `foto=dict(src='img/actualidad/fotos/<slug>.jpg', ancho=1280, alto=720, ia=True, pie='…')`. Con `ia=True` el pie añade solo «Ilustración generada con IA para Mapa Electoral» y el enlace a la política de uso de IA.
- Si la ilustración aún no tiene pieza, súbela a `img/actualidad/reserva/<tema>.jpg` y di en el PR qué representa.
- **Nunca** uses IA para mapas, gráficos ni nada que muestre datos: eso se dibuja a partir de los datos. Tampoco hagas pasar una ilustración por fotografía ni imites el logotipo o la imagen de un medio o un partido.

## Normas editoriales

- **Colores de partido**: en todo gráfico y mapa, cada partido con su color (PSOE rojo, PP azul, Vox verde, etc.), nunca escalas neutras o arbitrarias. Los colores están en `generales-2026/src/partidos.py`.
- **Verificación**: nada se publica sin revisión de Nacho. Cada afirmación es *dato*, *patrón* o *explicación* (en Actualidad, los párrafos se etiquetan con `data-tipo`: dato, patrón, hipótesis, contexto). No saques conclusiones causales automáticas: una explicación local necesita dos fuentes independientes o se presenta como hipótesis. Nunca inventes hallazgos ni cifras.
- **Citas**: reales, literales y enlazadas a su fuente, tanto académicas (estudios, expertos) como de protagonistas.
- **Fuentes**: prioriza EFE y Europa Press; si la noticia salió en otro medio, cita el original de la agencia.
- **Idiomas**: la pieza de Cataluña (`abstencion.html` / `ca.html`) y la de Girona son bilingües castellano/catalán: cualquier cambio de texto, en las dos versiones. Actualidad, solo en castellano.
- **Firma**: Nacho G. del Álamo.
- **Titulares**: abren con la cifra o el contraste más fuerte.
- **Nada de relleno SEO**: ni páginas vacías ni texto escrito para buscadores.
- Fotos reales: Wikimedia Commons, con autor y licencia.

## Construir

Requisitos: Python 3 con pandas, geopandas y pyarrow; Node con Playwright para las imágenes. Las órdenes, desde la raíz:

- Actualidad: `python3 actualidad/src/construir.py && node actualidad/src/miniaturas.mjs`
- Atlas: `python3 atlas/src/construir.py && python3 atlas/src/controles.py && python3 atlas/src/paginas.py`
- Pieza de Cataluña en catalán: `python3 src/build_ca.py`
- Portada (tras cambiar `generales-2026/`): `python3 src/portada.py`
- Páginas por territorio: `python3 src/territorios.py`
- Al final, siempre: `python3 src/seo.py` (sitemap, `llms.txt` y datos estructurados)

Algunos scripts leen datos de una carpeta de trabajo que no está en el repositorio; si te falta un fichero, dilo en el PR en vez de inventar los datos.
