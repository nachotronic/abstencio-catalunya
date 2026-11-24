"""Quita de las páginas publicadas de /listas-electorales-29n/ la probabilidad de salir elegido (sale de la media de
encuestas). Nacho, 24-11-2026: «quitar lo de las posibilidades de salir». Veda de encuestas (LOREG 69.7) hasta el 29-11 21:00.

Trabaja sobre el HTML publicado (no se regenera con construir.py: cambiaría títulos). No toca title, H1, canonical ni URL.
La meta description solo se toca con --descripcion (decisión aparte de Nacho). Idempotente.
"""
import csv, json, pathlib, re, sys

CARPETA = pathlib.Path(__file__).resolve().parents[1]
NB = '[  ]'
CAB = [re.compile(p, re.S | re.I) for p in (r'<title[^>]*>(.*?)</title>', r'<h1[^>]*>(.*?)</h1>', r'<link\s+rel="canonical"\s+href="([^"]*)"')]
DESC = re.compile(r'(<meta\s+(?:name="description"|property="og:description"|name="twitter:description")\s+content=")([^"]*)(")')


def limpia_texto(s):
    """Frases con la probabilidad dentro de una descripción."""
    s = re.sub(rf': (?:más del |menos del )?\d+{NB}% de opciones de conseguir escaño según la media de encuestas\.', '.', s)
    s = re.sub(r',? y quién tiene opciones de salir', '', s)
    s = re.sub(r' y qué candidatos tienen opciones de salir elegidos según las encuestas', '', s)
    s = re.sub(r',? con (?:el BOE y )?las opciones de salir elegido de cada uno', lambda m: ', con el BOE' if 'BOE' in m.group(0) else '', s)
    return s


def pagina(t, descripcion=False):
    # leyenda de las etiquetas
    t = re.sub(r'Cada nombre lleva la probabilidad de salir elegido.*?difícil</span>\.\s*', '', t, flags=re.S)
    # párrafos de datos del modelo
    t = re.sub(r'<p data-tipo="dato">\s*Con la media de (?:las )?encuestas.*?</p>\s*', '', t, flags=re.S)
    # etiquetas por candidato
    t = re.sub(r'\s*<span class="pr [^"]*"[^>]*>.*?</span>', '', t, flags=re.S)
    # fuente del modelo
    t = re.sub(r'<dt>(?:Probabilidad de salir elegido|Opciones de conseguir escaño)</dt>\s*<dd>.*?</dd>\s*', '', t, flags=re.S)
    # pregunta frecuente «¿Qué candidatos … tienen el escaño en el aire?»
    t = re.sub(r'<details>\s*<summary>\s*<h3>[^<]*en el aire\?</h3>\s*</summary>.*?</details>\s*', '', t, flags=re.S)
    # subtítulo de ficha y de provincia
    t = re.sub(rf'( · )?(?:más del |menos del )?\d+{NB}% de opciones de escaño(?=</p>)', '', t)
    t = re.sub(r', con las opciones de salir elegido de cada uno según la media de encuestas', '', t)
    # buscador (index.html)
    t = re.sub(r', con la probabilidad de salir elegido de cada puesto según la media de encuestas', '', t)
    t = re.sub(r'<label><input id="fsal" type="checkbox"> Solo con opciones de salir</label>\s*', '', t)
    t = t.replace('<th class="n">Opciones de salir</th>', '').replace("<td class=\"n\">${r[6]==null?'–':``}</td>", '')
    t = t.replace(', puesto a puesto, con las opciones de cada candidato.', ', puesto a puesto.')
    t = re.sub(r'<details>\s*<summary>\s*<h3>¿Qué significa (?:la probabilidad de salir elegido|«casi seguro» o «en el aire»)\?</h3>\s*</summary>.*?</details>\s*', '', t, flags=re.S)
    t = re.sub(r'<dt>Opciones de salir elegido</dt>\s*<dd>.*?</dd>\s*', '', t, flags=re.S)
    # mi diputado
    t = re.sub(r'<p class="nota">Sin probabilidad por puesto:.*?</p>\s*', '', t, flags=re.S)
    t = re.sub(r'<h4>(?:Candidatos del 29N con escaño casi seguro|Con el escaño en el aire) \(\d+\)</h4>\s*<ul class="gente">.*?</ul>\s*', '', t, flags=re.S)
    t = t.replace(' y los candidatos del 29N con opciones. La probabilidad de cada candidato, con la media de encuestas del 3 de noviembre de 2026: (90 % o más) y (10-90 %).',
                  ' y sus candidatos al 29N.')
    t = t.replace(', si vuelven a presentarse y qué candidatos del 29N tienen el escaño casi seguro o en el aire según la media de encuestas.', ' y si vuelven a presentarse.')

    def ld(m):
        s = m.group(2)
        try:
            d = json.loads(s)
        except ValueError:
            return m.group(0)
        ind = 1 if json.dumps(d, ensure_ascii=False, indent=1) == s else (None if json.dumps(d, ensure_ascii=False) == s else 2)
        if ind == 2 and json.dumps(d, ensure_ascii=False, indent=2) != s:
            return m.group(0)
        nodos = d if isinstance(d, list) else d.get('@graph', [d]) if isinstance(d, dict) else []
        for n in nodos:
            if isinstance(n, dict) and n.get('@type') == 'FAQPage':
                n['mainEntity'] = [q for q in n['mainEntity'] if not re.search(r'en el aire|probabilidad de salir|casi seguro', q.get('name', ''))]
            if descripcion and isinstance(n, dict):
                for k in ('description',):
                    if isinstance(n.get(k), str):
                        n[k] = limpia_texto(n[k])
        return m.group(1) + json.dumps(d, ensure_ascii=False, indent=ind) + m.group(3)
    t = re.sub(r'(<script type="application/ld\+json">\n?)(.*?)(\n?</script>)', ld, t, flags=re.S)
    if descripcion:
        t = DESC.sub(lambda m: m.group(1) + limpia_texto(m.group(2)) + m.group(3), t)
    return t


def datos():
    """La probabilidad también sale del buscador (candidatos.json, posición 6) y del CSV de descarga."""
    f = CARPETA / 'candidatos.json'
    t0 = f.read_text(encoding='utf-8')
    d = json.loads(t0)
    for r in d:
        r[6] = None
    t = json.dumps(d, ensure_ascii=False, separators=(',', ':')) if '\n' not in t0.strip() and ', ' not in t0[:200] else json.dumps(d, ensure_ascii=False)
    if t != t0:
        f.write_text(t, encoding='utf-8')
    f = CARPETA / 'candidatos-29n.csv'
    filas = list(csv.reader(f.read_text(encoding='utf-8').splitlines()))
    i = filas[0].index('prob_salir_modelo') if 'prob_salir_modelo' in filas[0] else None
    if i is not None:
        for r in filas:
            del r[i]
        with f.open('w', encoding='utf-8', newline='') as h:
            csv.writer(h, lineterminator='\n').writerows(filas)


def main(descripcion=None):
    descripcion = descripcion if descripcion is not None else '--descripcion' in sys.argv
    if '--comprobar' not in sys.argv:
        datos()
    n = 0
    for f in sorted(CARPETA.glob('**/index.html')):
        if 'src' in f.parts:
            continue
        t0 = f.read_text(encoding='utf-8')
        t = pagina(t0, descripcion)
        assert [p.findall(t) for p in CAB] == [p.findall(t0) for p in CAB], f'{f}: cambiaría title, H1 o canonical'
        if not descripcion:
            assert DESC.findall(t) == DESC.findall(t0), f'{f}: cambiaría la descripción'
        if t != t0:
            if '--comprobar' not in sys.argv:
                f.write_text(t, encoding='utf-8')
            n += 1
    print(f'sin_probabilidades: {n} páginas cambiadas')


if __name__ == '__main__':
    main()
