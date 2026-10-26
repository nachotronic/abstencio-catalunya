"""Imágenes ligeras para móvil en los carruseles de la portada.

Las tarjetas de los carruseles de index.html (Actualidad, series, guías, Atlas) usan las ilustraciones
a tamaño completo (1.280 px, ~250 KB cada una) aunque en el móvil se ven a unos 280 px de ancho.

Este script pasa por la portada ya generada y, para cada <img> local:

- crea una copia en WebP de 640 px de ancho como mucho en img/movil/<misma ruta>.webp (solo si falta
  o si la original es más nueva), y la descarta si no pesa al menos un 20 % menos que la original;
- envuelve el <img> en un <picture> con un <source> para pantallas de hasta 760 px (el corte del CSS
  del carrusel), de modo que el móvil baja la versión pequeña y el ordenador sigue bajando la original.

El <picture> lleva display:contents, así que el <img> se maqueta igual que antes. Es idempotente:
src/seo.py lo llama al terminar; también se puede lanzar solo:

    python3 src/movil.py
"""
import pathlib, re

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGINAS = ['index.html']
ANCHO = 640
CORTE = '(max-width: 760px)'
ESTILO = '<style id="movil-picture">picture.movil{display:contents}</style>'
IMG = re.compile(r'(<picture class="movil">.*?</picture>)|<img\b[^>]*?\bsrc="([^"]+)"[^>]*>', re.S)


def miniatura(src):
    """Ruta relativa de la versión móvil de src (la crea si hace falta), o None si no compensa."""
    orig = ROOT / src
    if src.startswith(('http', '/', 'data:')) or orig.suffix.lower() not in ('.jpg', '.jpeg', '.png') or not orig.exists():
        return None
    dest = ROOT / 'img' / 'movil' / pathlib.Path(src).with_suffix('.webp')
    if not dest.exists() or dest.stat().st_mtime < orig.stat().st_mtime:
        dest.parent.mkdir(parents=True, exist_ok=True)
        im = Image.open(orig)
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        if im.width > ANCHO:
            im = im.resize((ANCHO, round(im.height * ANCHO / im.width)), Image.LANCZOS)
        im.save(dest, 'WEBP', quality=78, method=6)
    if dest.stat().st_size > 0.8 * orig.stat().st_size:
        return None
    return dest.relative_to(ROOT).as_posix()


def procesa(html):
    def cambia(m):
        if m.group(1):   # ya envuelta
            return m.group(0)
        p = miniatura(m.group(2))
        if not p:
            return m.group(0)
        return f'<picture class="movil"><source media="{CORTE}" type="image/webp" srcset="{p}">{m.group(0)}</picture>'
    html = IMG.sub(cambia, html)
    if 'picture class="movil"' in html and 'id="movil-picture"' not in html:
        html = html.replace('</head>', ESTILO + '\n</head>', 1)
    return html


def main():
    for nombre in PAGINAS:
        f = ROOT / nombre
        t = f.read_text(encoding='utf-8')
        n = procesa(t)
        if n != t:
            f.write_text(n, encoding='utf-8')


if __name__ == '__main__':
    main()
