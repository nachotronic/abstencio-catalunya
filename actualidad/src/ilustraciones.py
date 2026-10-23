# Lista de piezas de Actualidad que aún no tienen ilustración de cabecera (ILUSTRACIONES.md, en la raíz).
# Se rehace con cada construir.py. Nacho pide la ilustración a ChatGPT, que la sube a img/actualidad/buzon/<slug>.jpg en un PR;
# Claude la integra y la publica con el OK de Nacho (flujo acordado el 23-10-2026; sin Issues por ilustración).
import os

# Piezas que llevan un gráfico de cabecera a propósito (Nacho, 16-10-2026): no piden ilustración
CON_GRAFICO_A_PROPOSITO = {'pensiones-censo-mayores-29n'}

CABECERA = '''# Ilustraciones pendientes

**Este fichero se genera solo** (`actualidad/src/ilustraciones.py`, cada vez que se construye Actualidad). No lo edites a mano.

Son las piezas de Actualidad que aún llevan un gráfico de datos como imagen de cabecera, o ninguna, de la más reciente a la más antigua. Cuando llega su ilustración, la pieza sale sola de esta lista.

## Cómo se hace una ilustración

1. **Nacho** le dice a ChatGPT qué pieza ilustrar (por ejemplo: «haz la ilustración de `escanos-en-el-filo-29n`»).
2. **ChatGPT** la hace siguiendo la guía de estilo de abajo y **la sube él mismo** al repositorio: rama `chatgpt/ilustracion-<slug>`, un único fichero `img/actualidad/buzon/<slug>.jpg` (JPG, 16:9) y un PR contra `main` titulado «Ilustración: <slug>». Nada más: no toca `construir.py` ni ningún HTML. Si no consigue subir el binario, lo dice en el chat y no da la ilustración por entregada.
3. **Claude** recoge los PR de `chatgpt/ilustracion-*`, mueve la imagen a `img/actualidad/fotos/`, la pone de cabecera con `ia=True`, enseña a Nacho cómo queda y publica cuando Nacho da el OK. Si Nacho la rechaza, se pide otra.

El buzón (`img/actualidad/buzon/`) existe para no pisar nunca un gráfico: algunas piezas ya tienen en `img/actualidad/fotos/<slug>.jpg` su gráfico de cabecera.

## Guía de estilo

- Collage editorial horizontal, 16:9 (se publica a 1280 × 720). Tonos apagados, fondo claro, mucho aire.
- **Sin texto, cifras, gráficos ni mapas con datos** dentro de la imagen. Los datos se dibujan aparte, a partir de los datos.
- Sin logotipos de partidos ni de medios. Políticos reconocibles solo si la pieza va de esa persona; si no, objetos y lugares (urnas, papeletas, fachadas, calles).
- Nada de violencia ni de imitar una fotografía: en la web sale con el pie «Ilustración generada con IA para Mapa Electoral».
- Una ilustración por pieza, sin repetir otra ya publicada.

## Pendientes ({n})

| Fecha | Pieza (slug = nombre del fichero) | Titular | Cabecera ahora |
|---|---|---|---|
'''


def tipo_cabecera(p, series_foto):
    f = p.get('foto')
    if f:
        return 'ilustración' if f.get('ia') else ('gráfico' if f.get('grafico') else 'foto')
    return 'serie' if p.get('serie') in series_foto else 'gráfico'


def escribir(piezas, series_foto, raiz, base):
    pendientes = [p for p in sorted(piezas, key=lambda p: p['fecha'], reverse=True)
                  if tipo_cabecera(p, series_foto) == 'gráfico' and p['slug'] not in CON_GRAFICO_A_PROPOSITO]
    filas = [f"| {p['fecha']} | [`{p['slug']}`]({base}/actualidad/{p['slug']}/) | {p['titulo'].replace('|', '/')} | "
             f"{'gráfico' if p.get('foto') else 'primer gráfico de la pieza'} |" for p in pendientes]
    with open(os.path.join(raiz, 'ILUSTRACIONES.md'), 'w', encoding='utf-8') as f:
        f.write(CABECERA.replace('{n}', str(len(pendientes))) + '\n'.join(filas) + '\n')
    return len(pendientes)
