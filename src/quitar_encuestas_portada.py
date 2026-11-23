"""Veda de encuestas (src/veda.py): quita de la portada el bloque de encuestas y, del carrusel de Actualidad, las
piezas con encuestas. No toca title, H1, description, canonical ni URL. /encuestas/ y sus páginas se quedan como
están, congeladas (encuestas.yml no publica nada en la veda).

Uso: python3 src/quitar_encuestas_portada.py [--forzar]   (sin --forzar, fuera de la veda no hace nada; pone además el aviso
     de veda en /encuestas/, debajo de la firma)
     python3 src/quitar_encuestas_portada.py --restaurar   (después de la veda: devuelve menú y simulador)
"""
import pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from veda import en_veda, es_pieza_de_encuestas  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FICHEROS = [RAIZ / 'index.html', RAIZ / 'generales-2026/src/plantilla.html']
ENCUESTAS = RAIZ / 'encuestas/index.html'

# Aviso visible en /encuestas/ durante la veda (Nacho, 23-11-2026, «vale»). Va debajo de la firma: no toca title, H1,
# description, canonical ni URL. Marca propia (no <!--veda:…-->, que es lo que --restaurar descomenta).
AVISO = ('<!--aviso-veda--><p class="veda-aviso" role="note" style="font:15px/1.45 var(--sans);border-left:4px solid var(--ink);'
         'padding:8px 12px;margin:12px 0 18px;background:var(--bg-2,transparent)"><b>Veda electoral.</b> Desde el martes 24 de noviembre '
         'y hasta el cierre de los colegios del 29N no se publican encuestas nuevas (artículo 69.7 de la LOREG). Esta página se '
         'quedó con las publicadas hasta el lunes 23 de noviembre.</p><!--/aviso-veda-->')


def poner_aviso(t):
    if '<!--aviso-veda-->' in t:
        return t
    return re.sub(r'(<p class="firma">.*?</p>\n?)', lambda m: m.group(1) + AVISO + '\n', t, count=1, flags=re.S)


def quitar_aviso(t):
    return re.sub(r'<!--aviso-veda-->.*?<!--/aviso-veda-->\n?', '', t, flags=re.S)


CARRUSELES = ('actualidad:ultimas', 'actualidad:mapa', 'videos:portada')
CON_ENCUESTAS = re.compile(r'encuesta|sondeo', re.I)


def limpiar(t):
    """Devuelve el HTML sin el bloque de encuestas y sin las tarjetas de encuestas de los carruseles de la portada:
    piezas de encuestas por su slug (src/veda.py) y cualquier tarjeta cuyo titular o antetítulo hable de encuestas
    (p. ej. el vídeo «Encuestas» o la de La Rioja de la serie «El mapa electoral de…»)."""
    t, n_bloque = re.subn(r'<!--encuestas:portada-->.*?<!--/encuestas:portada-->\n?', '', t, flags=re.S)
    quitadas = []

    def tarjeta(x):
        li = x.group(0)
        slug = re.match(r'<li><a href="(?:\.\./)?actualidad/([^/"]+)/"', li)
        texto = ' '.join(a or b for a, b in re.findall(r'<b>([^<]*)</b>|<span class="atlas-k">([^<]*)</span>', li))
        if (slug and es_pieza_de_encuestas(slug.group(1))) or CON_ENCUESTAS.search(texto):
            quitadas.append(slug.group(1) if slug else texto[:60])
            return ''
        return li
    for mk in CARRUSELES:
        t = re.sub(rf'<!--{mk}-->.*?<!--/{mk}-->',
                   lambda m: re.sub(r'<li><a href="[^"]*"[^>]*>.*?</li>', tarjeta, m.group(0), flags=re.S), t, flags=re.S)
    # «No es legal que asomen» (Nacho, 18-11-2026): tampoco el enlace «Encuestas» del menú ni la tarjeta del simulador
    # de pactos. Se guardan como comentario <!--veda:…--> para devolverlos al acabar la veda (--restaurar).
    for patron, nombre in ((r'<a href="(?:\.\./)?encuestas/">Encuestas</a>', 'menú'),
                           (r'<a class="atlas" href="(?:\.\./)?encuestas/simulador-pactos/">.*?</a>', 'simulador de pactos')):
        t, n = re.subn(patron, lambda m: '<!--veda:' + m.group(0) + '-->', t, count=1, flags=re.S)
        if n:
            quitadas.append(nombre)
    return t, n_bloque, quitadas


def restaurar(t):
    """Fin de la veda: vuelven el enlace del menú y la tarjeta del simulador (el bloque de encuestas, no)."""
    return re.sub(r'<!--veda:(.*?)-->', lambda m: m.group(1), t, flags=re.S)


def main():
    if '--restaurar' in sys.argv:
        if en_veda():
            print('Seguimos en la veda: no se restaura nada'); return
        for f in FICHEROS:
            if f.exists():
                t = f.read_text(encoding='utf-8')
                t2 = restaurar(t)
                if t2 != t:
                    f.write_text(t2, encoding='utf-8'); print(f'{f.relative_to(RAIZ)}: restaurados el menú y el simulador')
        if ENCUESTAS.exists():
            t = ENCUESTAS.read_text(encoding='utf-8')
            if quitar_aviso(t) != t:
                ENCUESTAS.write_text(quitar_aviso(t), encoding='utf-8'); print('encuestas/index.html: fuera el aviso de veda')
        return
    if not en_veda() and '--forzar' not in sys.argv:
        print('Fuera de la veda: no se toca nada'); return
    for f in FICHEROS:
        if not f.exists():
            continue
        t = f.read_text(encoding='utf-8')
        t2, n, quitadas = limpiar(t)
        if t2 != t:
            f.write_text(t2, encoding='utf-8')
        print(f'{f.relative_to(RAIZ)}: bloque de encuestas {"quitado" if n else "no estaba"}; {len(quitadas)} tarjetas de encuestas fuera de los carruseles: {quitadas}')
    if ENCUESTAS.exists():
        t = ENCUESTAS.read_text(encoding='utf-8')
        t2 = poner_aviso(t)
        if t2 != t:
            ENCUESTAS.write_text(t2, encoding='utf-8'); print('encuestas/index.html: aviso de veda puesto')
        elif '<!--aviso-veda-->' not in t:
            print('encuestas/index.html: no encuentro la firma; el aviso de veda NO se ha puesto')


if __name__ == '__main__':
    main()
