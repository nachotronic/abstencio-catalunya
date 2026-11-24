"""Bienes declarados al Congreso en la XIV y en la XV legislatura (normalmente 2019 y 2023), con su evolución, en la
ficha de los candidatos que eran diputados en ambas (Nacho, 24-11-2026: «se podría añadir las declaraciones de bienes y los cambios que han
tenido. Incluso con gráficos»).

Los datos están en datos/bienes-congreso.json. Las declaraciones del Congreso son PDF escaneados, sin texto: las cifras
se copiaron a mano de cada PDF (el enlace va en cada entrada). Se suman en dos magnitudes que no dependen de en qué
casilla puso cada diputado sus planes o fondos:
- ahorro e inversiones: depósitos en cuentas + deuda pública, acciones y fondos + otros bienes con valor (planes de
  pensiones, etc.); no incluye el valor de los inmuebles, que el formulario no pide;
- deudas pendientes: saldo pendiente de préstamos.
Inmuebles y vehículos cuentan las líneas del formulario.

Se escribe en la ficha ya publicada, dentro de la sección «Transparencia», entre marcas <!--bienes--> … <!--/bienes-->,
sin tocar title, description, H1, canonical ni fechas. Idempotente.

Uso, desde la raíz:  python3 listas-electorales-29n/src/bienes.py [--comprobar]
"""
import html, importlib.util, json, pathlib, re, sys

sys.dont_write_bytecode = True
CARPETA = pathlib.Path(__file__).resolve().parents[1]
DATOS = CARPETA / 'datos' / 'bienes-congreso.json'
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
COPIADO = '24 de noviembre de 2026'


def _bio():
    spec = importlib.util.spec_from_file_location('biografias', CARPETA / 'src' / 'biografias.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def euros(x):
    return f'{round(x):,}'.replace(',', '.') + ' €'


def mes(f):
    return f'{MESES[int(f[4:6]) - 1]} de {f[:4]}'


def dia(f):
    return f'{int(f[6:])} de {mes(f)}'


def ahorro(d):
    return d['cuentas'] + d['valores'] + d['otros']


def quita(t, ini, fin):
    return re.sub(re.escape(ini) + '.*?' + re.escape(fin), '', t, flags=re.S)


def grafico(r):
    y1, y2 = r['xiv']['fecha'][:4], r['xv']['fecha'][:4]
    a19, a23 = ahorro(r['xiv']), ahorro(r['xv'])
    d19, d23 = r['xiv']['deudas'], r['xv']['deudas']
    tope = max(a19, a23, d19, d23, 1)
    ancho = 200
    partes = []
    y = 0
    for titulo, v19, v23 in (('Ahorro e inversiones', a19, a23), ('Deudas pendientes', d19, d23)):
        partes.append(f'<text x="0" y="{y + 13}" class="bt">{titulo}</text>')
        for anio, v, op, dy in ((y1, v19, '.4', 20), (y2, v23, '1', 40)):
            w = max(round(ancho * v / tope), 1 if v > 0 else 0)
            yy = y + dy
            partes.append(f'<text x="0" y="{yy + 12}" class="ba">{anio}</text>'
                          f'<rect x="40" y="{yy}" width="{w}" height="16" rx="2" fill="var(--c)" fill-opacity="{op}"/>'
                          f'<text x="{40 + w + 6}" y="{yy + 12}" class="bv">{euros(v)}</text>')
        y += 66
    return (f'<svg viewBox="0 0 380 {y}" width="100%" role="img" aria-label="Ahorro e inversiones y deudas declarados en {y1} y en {y2}">'
            f'{"".join(partes)}</svg>')


def bloque(r, color):
    e = html.escape
    x, v = r['xiv'], r['xv']
    y1, y2 = x['fecha'][:4], v['fecha'][:4]
    a19, a23 = ahorro(x), ahorro(v)
    cero = lambda p, q: round(p) == 0 and round(q) == 0
    ini = f'Según lo que declaró al Congreso, entre {mes(x["fecha"])} y {mes(v["fecha"])}'
    if cero(a19, a23):
        frase = f'{ini} no declaró ahorro ni inversiones, y sus deudas pendientes pasaron de {euros(x["deudas"])} a {euros(v["deudas"])}.'
    elif cero(x['deudas'], v['deudas']):
        frase = f'{ini} su ahorro e inversiones pasaron de {euros(a19)} a {euros(a23)}. No declaró deudas pendientes en ninguna de las dos.'
    else:
        frase = (f'{ini} su ahorro e inversiones pasaron de {euros(a19)} a {euros(a23)}, y sus deudas pendientes, '
                 f'de {euros(x["deudas"])} a {euros(v["deudas"])}.')
    frase += f' Declaró {v["inmuebles"]} {"inmueble" if v["inmuebles"] == 1 else "inmuebles"} en {y2} ({x["inmuebles"]} en {y1}).'
    filas = ''.join(f'<tr><th scope="row">{n}</th><td>{a}</td><td>{b}</td></tr>' for n, a, b in (
        ('Ahorro e inversiones', euros(a19), euros(a23)),
        ('Deudas pendientes', euros(x['deudas']), euros(v['deudas'])),
        ('Inmuebles', x['inmuebles'], v['inmuebles']),
        ('Vehículos', x['vehiculos'], v['vehiculos'])))
    nota = f' {e(r["nota"])}' if r['nota'] else ''
    return (f'<!--bienes--><section class="bienes" style="--c:{color}"><h3 id="bienes">Sus bienes en {y1} y en {y2}</h3>'
            f'<p data-tipo="bienes">{e(frase)}</p>'
            f'<figure>{grafico(r)}<figcaption>Declaraciones presentadas en la XIV legislatura ({dia(x["fecha"])}) y en la XV '
            f'({dia(v["fecha"])}).</figcaption></figure>'
            f'<table><thead><tr><th scope="col"></th><th scope="col">{y1}</th><th scope="col">{y2}</th></tr></thead><tbody>{filas}</tbody></table>'
            f'<p class="nota">Cifras tal como las declaró; el Congreso no las comprueba. «Ahorro e inversiones» suma cuentas, '
            f'acciones, fondos, planes de pensiones y otros bienes con valor; no incluye el valor de casas ni terrenos, que la '
            f'declaración no pide. Inmuebles y vehículos cuentan las líneas del formulario, y una línea puede agrupar varios.{nota} '
            f'Las declaraciones son PDF escaneados y las cifras se han copiado a mano: '
            f'<a href="{e(x["url"])}">declaración de {y1}</a> y <a href="{e(v["url"])}">declaración de {y2}</a> (PDF).</p>'
            f'</section><!--/bienes-->')


ESTILO = ('<!--bienes:css--><style>.bienes{margin:1.2rem 0 1.6rem}.bienes h3{font-family:var(--ui);font-size:1rem;margin:0 0 .4rem}'
          '.bienes figure{margin:.6rem 0 .4rem;max-width:520px}.bienes svg{display:block;font-family:var(--ui)}'
          '.bienes .bt{font-size:12.5px;font-weight:700;fill:var(--fg)}.bienes .ba{font-size:11.5px;fill:var(--muted)}'
          '.bienes .bv{font-size:12px;fill:var(--fg)}.bienes figcaption{font-size:.75rem;color:var(--muted)}'
          '.bienes table{font-family:var(--ui);font-size:.85rem;border-collapse:collapse;margin:.5rem 0;width:100%;max-width:520px}'
          '.bienes th,.bienes td{padding:.25rem .4rem;border-bottom:1px solid var(--rule);text-align:right}'
          '.bienes th[scope=row],.bienes thead th:first-child{text-align:left;font-weight:400}'
          '.bienes .nota{font-family:var(--ui);font-size:.78rem;color:var(--muted);line-height:1.45}</style><!--/bienes:css-->')


def en_ficha(t, r):
    t = quita(t, '<!--bienes-->', '<!--/bienes-->')
    t = quita(t, '<!--bienes:css-->', '<!--/bienes:css-->')
    t = quita(t, '<!--bienes:fuente-->', '<!--/bienes:fuente-->')
    m = re.search(r'<section class="lista" style="--c:(#[0-9a-fA-F]{3,6})', t)
    color = m.group(1) if m else 'var(--acc)'
    i = t.index('<h2 id="transparencia">')
    j = t.index('</ul>', i) + len('</ul>')
    t = t[:j] + bloque(r, color) + t[j:]
    dd = (f'<!--bienes:fuente--><dt>Bienes</dt><dd>Declaraciones de bienes y rentas al Congreso de la XIV y la XV legislatura '
          f'(<a href="https://www.congreso.es/es/busqueda-de-diputados">Congreso de los Diputados</a>), copiadas a mano el {COPIADO}.</dd>'
          f'<!--/bienes:fuente-->')
    i = t.index('<dt>Autoría</dt>')
    t = t[:i] + dd + t[i:]
    i = t.index('</head>')
    return t[:i] + ESTILO + t[i:]


def main():
    bio = _bio()
    datos = json.loads(DATOS.read_text(encoding='utf-8'))
    tocadas = 0
    sin_seccion = []  # fichas que la web aún no marca como diputado de la XV: no tienen «Transparencia»
    for clave, r in datos.items():
        assert r['xiv']['fecha'] < r['xv']['fecha'], clave
        f = CARPETA / clave / 'index.html'
        t0 = f.read_text(encoding='utf-8')
        if '<h2 id="transparencia">' not in t0:
            sin_seccion.append(clave)
            continue
        nombre = re.search(r'<h1[^>]*>(.*?)</h1>', t0, re.S).group(1)
        assert html.unescape(re.sub('<[^>]+>', '', nombre)).strip().startswith(r['nombre'].split()[0]), f'{clave}: no es {r["nombre"]}'
        t = en_ficha(t0, r)
        assert bio.cabeceras(t) == bio.cabeceras(t0), f'{clave}: cambiaría title, description, H1 o canonical'
        if t != t0 and '--comprobar' not in sys.argv:
            f.write_text(t, encoding='utf-8')
            tocadas += 1
    print(f'bienes: {len(datos) - len(sin_seccion)} fichas con bienes; {tocadas} páginas reescritas')
    if sin_seccion:
        print('  sin sección «Transparencia», no se tocan:', ', '.join(sin_seccion))


if __name__ == '__main__':
    main()
