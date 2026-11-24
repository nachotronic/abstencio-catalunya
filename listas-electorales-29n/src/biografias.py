"""Biografías breves de los candidatos con ficha, en la ficha y en la página de su provincia (Nacho, 23-11-2026: «Por
provincia. Y con geo»).

Texto de una o dos frases, solo con hechos comprobables y su fuente enlazada:
- datos/biografias-oficiales.json (bios_datos.py): nacimiento y legislaturas en el Congreso, senadores electos en 2023.
- datos/biografias-manual.json: el cargo actual de quien no sale en esos datos, con el enlace al partido o al medio
  que lo dice. Cada entrada repite nombre, provincia, siglas y puesto del BOE; si no coinciden con la lista, no se pone.

Se escribe dentro de las páginas ya publicadas, entre marcas <!--bio--> … <!--/bio-->, sin tocar nada más: ni title, ni
meta description, ni H1, ni canonical, ni la fecha de actualización (las fichas llevan probabilidades de las encuestas
y en la veda no se vuelven a fechar). En la ficha: un párrafo arriba, la fuente en «Fuentes» y Person.description (y
birthDate y birthPlace cuando los da el Congreso) en el JSON-LD. En la provincia: el bloque «Quién es quién» antes del
Senado y una lista de Person en JSON-LD. Es idempotente: se puede ejecutar las veces que haga falta.

Uso, desde la raíz:  python3 listas-electorales-29n/src/biografias.py [--comprobar]
"""
import html, importlib.util, json, pathlib, re, sys
from datetime import date

sys.dont_write_bytecode = True
RAIZ = pathlib.Path(__file__).resolve().parents[2]
CARPETA = RAIZ / 'listas-electorales-29n'
DATOS = CARPETA / 'datos'
URL = 'https://mapaelectoral.es/listas-electorales-29n/'
ELECCION = date(2026, 11, 29)
ROMANOS = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV']
ORDINAL = {2: 'segunda', 3: 'tercera', 4: 'cuarta', 5: 'quinta', 6: 'sexta', 7: 'séptima', 8: 'octava', 9: 'novena', 10: 'décima', 11: 'undécima'}
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
DISOLUCION = '06/10/2026'
# formación electoral del Congreso → cómo se nombra cuando no es el partido de la lista de ahora
FORMACION = {'Cs': 'Ciudadanos', 'UP': 'Unidas Podemos', 'NA+': 'Navarra Suma', 'DL': 'Democràcia i Llibertat', 'CDC': 'Convergència Democràtica',
             'CD': 'Coalición Democrática', 'CP': 'Coalición Popular', 'PP': 'PP', 'CCa': 'Coalición Canaria', 'ECP': 'En Comú Podem',
             'ECP-GUANYEM EL CANVI': 'En Comú Podem', 'PODEMOS': 'Podemos', 'SUMAR': 'Sumar', 'PSOE': 'PSOE', 'Vox': 'Vox', 'VOX': 'Vox'}
SENADO_ISLA = {('07', '1'): 'Mallorca', ('07', '2'): 'Menorca', ('07', '3'): 'Eivissa y Formentera', ('35', '1'): 'Gran Canaria',
               ('35', '2'): 'Lanzarote', ('35', '3'): 'Fuerteventura', ('38', '4'): 'Tenerife', ('38', '5'): 'La Palma',
               ('38', '6'): 'La Gomera', ('38', '7'): 'El Hierro'}
INFOELECTORAL = 'https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/'
BUSCADOR_CONGRESO = 'https://www.congreso.es/es/busqueda-de-diputados'


def construir():
    spec = importlib.util.spec_from_file_location('listas_construir', CARPETA / 'src/construir.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def larga(iso):
    a, mm, d = iso.split('-')
    return f'{int(d)} de {MESES[int(mm) - 1]} de {a}'


def mes_anio(dmy):
    d, mm, a = dmy.split('/')
    return f'{MESES[int(mm) - 1]} de {a}'


def edad(iso, dia=ELECCION):
    n = date.fromisoformat(iso)
    return dia.year - n.year - ((dia.month, dia.day) < (n.month, n.day))


def lista_y(xs):
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' y ' + xs[-1]


def texto_oficial(x, m, fam_lista):
    """Frases con los datos de biografias-oficiales.json. Devuelve (frases, fuentes)."""
    f = x.get('genero') == 'f'
    o = 'a' if f else 'o'
    frases, fuentes = [], []
    if x.get('nacimiento'):
        lugar = f'en {x["lugar"]} ' if x.get('lugar') else ''
        frases.append(f'Nació {lugar}el {larga(x["nacimiento"])} y llega a las elecciones del 29N con {edad(x["nacimiento"])} años.')
    cong = x.get('congreso', [])
    if cong:
        import bios_datos
        circ = lambda c: m.PROV_NOMBRE.get(bios_datos.prov(m, c['circ']) or '', c['circ']).split('/')[0]
        forms = list(dict.fromkeys(FORMACION.get(c['formacion'], c['formacion']) for c in cong if bios_datos.familia(c['formacion']) != fam_lista))
        listas = (' en las listas ' + lista_y([('del ' if f_ in ('PP', 'PSOE') else 'de ') + f_ for f_ in forms])) if forms else ''
        legs = [c['leg'] for c in cong]
        if 15 in legs:
            c15 = next(c for c in cong if c['leg'] == 15)
            desde = '' if c15['alta'][-7:] in ('07/2023', '08/2023') else f'desde {mes_anio(c15["alta"])}'
            hasta = '' if not c15['baja'] or c15['baja'] == DISOLUCION else f'hasta {mes_anio(c15["baja"])}'
            rango = ' '.join(t_ for t_ in (desde, hasta) if t_)
            rango = f' {rango}' if rango else ''
            if len(legs) == 1:
                frases.append(f'En la XV legislatura ha sido diputad{o} por {circ(c15)}{rango}.')
            else:
                frases.append(f'Entró en el Congreso en {cong[0]["alta"][-4:]} y en la XV legislatura, su '
                              f'{ORDINAL.get(len(legs), str(len(legs)) + ".ª")}, ha sido diputad{o} por {circ(c15)}{rango}.')
                circs = list(dict.fromkeys(circ(c) for c in cong if c['leg'] != 15))
                por = f' por {lista_y(circs)}' if circs != [circ(c15)] else ''
                if por or listas:
                    frases.append(f'Antes lo fue{por}{listas}.')
        else:
            circs = list(dict.fromkeys(circ(c) for c in cong))
            ro = [ROMANOS[c['leg']] for c in cong]
            pl = 's' if len(ro) > 1 else ''
            años = cong[0]['alta'][-4:] + ('' if not cong[-1]['baja'] or cong[-1]['baja'][-4:] == cong[0]['alta'][-4:] else '-' + cong[-1]['baja'][-4:])
            cuales = f'la {ro[0]} legislatura' if len(ro) == 1 else f'las legislaturas {lista_y(ro)}'
            frases.append(f'Fue diputad{o} por {lista_y(circs)} en {cuales} ({años}){"," if listas else ""}{listas}.')
        fuentes.append(('Congreso de los Diputados', x.get('ficha_congreso') or BUSCADOR_CONGRESO))
    elif x.get('ficha_congreso'):
        fuentes.append(('Congreso de los Diputados', x['ficha_congreso']))
    s = x.get('senado_2023')
    if s:
        donde = SENADO_ISLA.get((s['prov'], s['distrito'])) or m.PROV_NOMBRE[s['prov']].split('/')[0]
        frases.append(f'En las generales del 23 de julio de 2023 salió elegid{o} senador{"a" if f else ""} por {donde}.')
        fuentes.append(('Ministerio del Interior, resultados del Senado de 2023', INFOELECTORAL))
    return frases, fuentes


def bios(m):
    """clave 'provincia/ficha' → dict(texto, fuentes, persona extra, identidad) para las fichas que hay hoy."""
    datos, avance = m.carga()
    cands = m.prepara(datos, avance)
    fichas = m.elige_fichas(cands, avance)
    of = json.loads((DATOS / 'biografias-oficiales.json').read_text())['personas']
    ma = json.loads((DATOS / 'biografias-manual.json').read_text()) if (DATOS / 'biografias-manual.json').exists() else {}
    fotos = json.loads((DATOS / 'fotos.json').read_text()) if (DATOS / 'fotos.json').exists() else {}
    out, avisos = {}, []
    for c, p in fichas:
        clave = f"{m.PROV_SLUG[c['prov']]}/{p['ficha']}"
        ident = {'nombre': p['nombre'], 'prov': c['prov'], 'siglas': c['siglas'], 'n': p['n']}
        frases, fuentes, extra, foto = [], [], {}, None
        man = ma.get(clave)
        if man:
            if all(man.get(k_) == v for k_, v in ident.items()):
                frases.append(man['texto'])
                fuentes += [(f['medio'], f['url']) for f in man['fuentes']]
            else:
                avisos.append(f'{clave}: la entrada manual no coincide con el BOE ({ {k_: man.get(k_) for k_ in ident} } ≠ {ident}); fuera')
        x = of.get(clave)
        if x:
            if all(x.get(k_) == v for k_, v in ident.items()):
                fr, fu = texto_oficial(x, m, 'IZQ' if c['fam'] in ('SUMAR', 'PODEMOS') else c['fam'])
                frases += fr
                fuentes += fu
                if x.get('nacimiento'):
                    extra['birthDate'] = x['nacimiento']
                if x.get('lugar'):
                    extra['birthPlace'] = {'@type': 'Place', 'name': x['lugar']}
                # foto de su ficha del Congreso de la XV, del mismo codParlamentario (fotos.py)
                fo = fotos.get(clave)
                if fo and fo['nombre'] == x['nombre'] and (CARPETA / 'fotos' / fo['archivo']).exists():
                    foto = fo
            else:
                avisos.append(f'{clave}: los datos oficiales no coinciden con el BOE; fuera')
        if frases:
            out[clave] = dict(texto=' '.join(frases), fuentes=fuentes, extra=extra, foto=foto, c=c, p=p)
    return out, avisos


def quita(t, ini, fin):
    return re.sub(re.escape(ini) + '.*?' + re.escape(fin), '', t, flags=re.S)


def en_ficha(t, b):
    e = html.escape
    t = quita(t, '<!--bio-->', '<!--/bio-->')
    t = quita(t, '<!--bio:fuente-->', '<!--/bio:fuente-->')
    t = quita(t, '<!--bio:css-->', '<!--/bio:css-->')
    fo = b.get('foto')
    figura = (f'<figure class="foto-oficial"><img src="../../fotos/{fo["archivo"]}" width="124" height="165" alt="{e(b["p"]["nombre"])}, foto oficial del Congreso">'
              f'<figcaption>Foto: Congreso de los Diputados</figcaption></figure>') if fo else ''
    parrafo = f'<!--bio-->{figura}<p data-tipo="bio" class="bio">{e(b["texto"])}</p><!--/bio-->'
    i = t.index('<p data-tipo="dato">')
    t = t[:i] + parrafo + t[i:]
    fu = ', '.join(f'<a href="{e(u)}">{e(n)}</a>' for n, u in dict.fromkeys(b['fuentes']))
    if fo:
        fu += (f'. Foto: <a href="{e(fo["ficha"])}">Congreso de los Diputados</a>, ficha de la XV legislatura, '
               f'sin modificar (consultada el {larga(fo["consultada"])})')
    dd = (f'<!--bio:fuente--><dt>Quién es</dt><dd>{fu}. La persona se identifica por su provincia, su lista y su puesto en el BOE; '
          f'si un dato no se puede atar a ella sin duda, no se pone.</dd><!--/bio:fuente-->')
    i = t.index('<dt>Autoría</dt>')
    t = t[:i] + dd + t[i:]
    # JSON-LD: descripción de la persona (no la de la página)
    mt = re.search(r'(<script type="application/ld\+json">\n)(.*?)(\n</script>)', t, re.S)
    ld = json.loads(mt.group(2))
    assert json.dumps(ld, ensure_ascii=False, indent=1) == mt.group(2), 'el JSON-LD no se puede reescribir idéntico'
    for nodo in ld:
        if nodo.get('@type') == 'ProfilePage':
            per = nodo['mainEntity']
            for k_ in ('description', 'birthDate', 'birthPlace', 'image'):
                per.pop(k_, None)
            per['description'] = b['texto']
            per.update(b['extra'])
            if fo:
                per['image'] = f'{URL}fotos/{fo["archivo"]}'
    t = t[:mt.start(2)] + json.dumps(ld, ensure_ascii=False, indent=1) + t[mt.end(2):]
    if fo:
        i = t.index('</head>')
        t = t[:i] + ESTILO_FICHA + t[i:]
    return t


ESTILO_FICHA = ('<!--bio:css--><style>.foto-oficial{float:right;margin:.2rem 0 .6rem 1rem;width:124px}.foto-oficial img{display:block;width:124px;height:auto;'
                'border-radius:4px}.foto-oficial figcaption{font-family:var(--ui);font-size:.7rem;color:var(--muted);margin-top:.2rem;line-height:1.2}'
                '@media (max-width:420px){.foto-oficial{width:96px}.foto-oficial img{width:96px}}</style><!--/bio:css-->')


ESTILO = ('<!--bio:css--><style>.bio{font-size:1.02rem}.quien{margin:.5rem 0 1.5rem}.quien h3{font-family:var(--ui);font-size:.95rem;margin:1.1rem 0 .3rem;'
          'border-left:4px solid var(--c);padding-left:.5rem}.quien dl{margin:0}.quien dt{font-family:var(--ui);font-weight:700;margin-top:.6rem}'
          '.quien dt small{font-weight:400;color:var(--muted)}.quien dt img{width:36px;height:48px;object-fit:cover;border-radius:3px;vertical-align:middle;margin-right:.45rem}.quien dd{margin:.1rem 0 0;font-size:.95rem;line-height:1.45}</style><!--/bio:css-->')


def mini(b):
    fo = b.get('foto')
    return (f'<img src="../fotos/{fo["archivo"]}" width="36" height="48" loading="lazy" alt="{html.escape(b["p"]["nombre"])}, foto oficial del Congreso">'
            if fo else '')


def en_provincia(t, cod, bs, m):
    e = html.escape
    for a, z in (('<!--bio-->', '<!--/bio-->'), ('<!--bio:css-->', '<!--/bio:css-->'), ('<!--bio:ld-->', '<!--/bio:ld-->')):
        t = quita(t, a, z)
    if not bs:
        return t
    corto = m.PROV_NOMBRE[cod].split('/')[0]
    orden = re.findall(r'<a href="#congreso-([^"]+)"', t)   # el orden de las listas en la página
    grupos = {}
    for b in bs:
        ancla = f'{m.slug(b["c"]["siglas"] or b["c"]["denominacion"])}-{b["c"]["orden"]}'
        grupos.setdefault(ancla, []).append(b)
    cuerpo = ''
    for ancla in sorted(grupos, key=lambda a: orden.index(a) if a in orden else 99):
        g = sorted(grupos[ancla], key=lambda b: b['p']['n'])
        c = g[0]['c']
        cuerpo += f'<h3 style="--c:{c["color"]}">{e(c["corto"] if c["fam"] != "OTROS" else (c["siglas"] or c["denominacion"]))}</h3><dl>'
        cuerpo += ''.join(f'<dt>{mini(b)}<a href="{b["p"]["ficha"]}/">{e(b["p"]["nombre"])}</a> <small>n.º {b["p"]["n"]}</small></dt><dd>{e(b["texto"])}</dd>' for b in g)
        cuerpo += '</dl>'
    seccion = (f'<!--bio--><h2 id="quien-es-quien">Quién es quién entre los candidatos al Congreso por {e(corto)}</h2>'
               f'<p>Los candidatos con ficha propia (los que tienen opciones de escaño y los diputados de la legislatura que acaba), en una o dos frases. '
               f'Fuentes: Congreso de los Diputados, Ministerio del Interior y, para los cargos, el partido o la prensa, enlazados en cada ficha. '
               f'Las fotos son las oficiales del Congreso de los diputados de la legislatura que acaba.</p>'
               f'<div class="quien">{cuerpo}</div><!--/bio-->')
    i = t.index('<h2 id="senado">')
    t = t[:i] + seccion + t[i:]
    ld = {'@context': 'https://schema.org', '@type': 'ItemList', '@id': f'{URL}{m.PROV_SLUG[cod]}/#quien-es-quien',
          'name': f'Quién es quién entre los candidatos al Congreso por {corto} el 29N', 'itemListElement': [
              {'@type': 'ListItem', 'position': i_ + 1, 'item': {'@type': 'Person', '@id': f'{URL}{m.PROV_SLUG[cod]}/{b["p"]["ficha"]}/#persona',
                                                               'name': b['p']['nombre'], 'description': b['texto'], 'url': f'{URL}{m.PROV_SLUG[cod]}/{b["p"]["ficha"]}/',
                                                               **({'image': f'{URL}fotos/{b["foto"]["archivo"]}'} if b.get('foto') else {})}}
              for i_, b in enumerate(sorted(bs, key=lambda b: (b['c']['orden'], b['p']['n'])))]}
    bloque = f'<!--bio:ld--><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script><!--/bio:ld-->'
    i = t.index('</head>')
    t = t[:i] + ESTILO + bloque + t[i:]
    return t


CABECERAS = [re.compile(p, re.S | re.I) for p in (r'<title[^>]*>(.*?)</title>', r'<meta\s+name="description"\s+content="([^"]*)"',
                                                  r'<h1[^>]*>(.*?)</h1>', r'<link\s+rel="canonical"\s+href="([^"]*)"')]


def cabeceras(t):
    return [tuple(p.findall(t)) for p in CABECERAS]


def main():
    sys.path.insert(0, str(CARPETA / 'src'))
    m = construir()
    bs, avisos = bios(m)
    for a in avisos:
        print('aviso:', a)
    tocadas = 0
    por_prov = {}
    for clave, b in bs.items():
        por_prov.setdefault(b['c']['prov'], []).append(b)
        f = CARPETA / clave / 'index.html'
        t0 = f.read_text(encoding='utf-8')
        t = en_ficha(t0, b)
        assert cabeceras(t) == cabeceras(t0), f'{clave}: cambiaría title, description, H1 o canonical'
        if t != t0 and '--comprobar' not in sys.argv:
            f.write_text(t, encoding='utf-8')
            tocadas += 1
    for cod, sl in m.PROV_SLUG.items():
        f = CARPETA / sl / 'index.html'
        t0 = f.read_text(encoding='utf-8')
        t = en_provincia(t0, cod, por_prov.get(cod, []), m)
        assert cabeceras(t) == cabeceras(t0), f'{sl}: cambiaría title, description, H1 o canonical'
        if t != t0 and '--comprobar' not in sys.argv:
            f.write_text(t, encoding='utf-8')
            tocadas += 1
    print(f'biografias: {len(bs)} fichas con biografía, {len(por_prov)} provincias; {tocadas} páginas reescritas')


if __name__ == '__main__':
    main()
