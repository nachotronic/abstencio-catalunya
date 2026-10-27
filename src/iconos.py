"""Favicon e iconos en todas las páginas del sitio.

Hasta ahora solo la portada declaraba sus iconos; el resto dependía de que el navegador pidiera
/favicon.ico por su cuenta (16 y 32 px). Los servicios que muestran la web fuera del navegador
(avisos de Chrome al seguir el sitio, lectores de RSS, accesos directos en el móvil, Discover)
buscan los <link rel="icon">, el apple-touch-icon o el manifiesto, y sin ellos salían sin icono.

Este script pasa por todas las páginas publicadas y deja en el <head> el mismo bloque de iconos
que la portada (y el enlace a /site.webmanifest). Es idempotente; src/seo.py lo llama al terminar
cualquier regeneración y también se puede lanzar solo:

    python3 src/iconos.py
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ICONOS = '''<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-96.png" type="image/png" sizes="96x96">
<link rel="icon" href="/favicon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">'''
# líneas de iconos ya presentes (sea cual sea su orden), para no duplicarlas
VIEJOS = re.compile(r'[ \t]*<link rel="(?:icon|apple-touch-icon|manifest)"[^>]*>\n?')


def paginas():
    yield from sorted(ROOT.glob('*.html'))
    for d in ('29n', 'abstencion', 'atlas', 'actualidad', 'elecciones', 'municipio', 'temas', 'generales',
              'generales-2026', 'encuestas', 'listas-electorales-29n', 'previsiones', 'insertar'):
        if (ROOT / d).is_dir():
            yield from sorted((ROOT / d).rglob('*.html'))


def procesa(f):
    if '/src/' in f.relative_to(ROOT).as_posix():
        return False
    s0 = f.read_text(encoding='utf-8')
    fin = s0.find('</head>')
    if fin < 0:
        return False
    cab = VIEJOS.sub('', s0[:fin])
    m = re.search(r'<meta charset[^>]*>\n?', cab, re.I)
    if m:
        i = m.end()
        cab = cab[:i] + ('' if cab[i - 1] == '\n' else '\n') + ICONOS + '\n' + cab[i:]
    else:
        cab = cab.rstrip('\n') + '\n' + ICONOS + '\n'
    s = cab + s0[fin:]
    if s != s0:
        f.write_text(s, encoding='utf-8')
        return True
    return False


def main():
    n = sum(procesa(f) for f in paginas())
    print(f'iconos: {n} páginas actualizadas (favicon, apple-touch-icon y manifiesto)')


if __name__ == '__main__':
    main()
