"""Serie «Las comunidades en las urnas»: un reportaje largo por comunidad (y Ceuta y Melilla) con su historia en las
autonómicas y en las generales. Escribe los HTML de trabajo (actualidad/src/<slug>.html), como historia/paginas.py.

Datos: datos_generales.py → generales.json; datos.py → datos.json (añade Historia Electoral). Textos: piezas/<cc>.py.
Uso, desde la raíz del repositorio:
    python3 actualidad/src/comunidades/reportajes.py && python3 actualidad/src/construir.py && node actualidad/src/miniaturas.mjs
"""
import html, importlib, importlib.util, json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(AQUI)
_spec = importlib.util.spec_from_file_location('historia_paginas', os.path.join(SRC, 'historia', 'paginas.py'))
_hp = importlib.util.module_from_spec(_spec); sys.path.insert(0, os.path.join(SRC, 'historia')); _spec.loader.exec_module(_hp)
CSS, FUENTES_TIPO, figura, leyenda = _hp.CSS, _hp.FUENTES_TIPO, _hp.figura, _hp.leyenda

ORDEN = ['andalucia', 'aragon', 'asturias', 'baleares', 'canarias', 'cantabria', 'castilla-la-mancha', 'castilla-y-leon', 'cataluna',
         'comunidad-valenciana', 'extremadura', 'galicia', 'madrid', 'murcia', 'navarra', 'pais-vasco', 'la-rioja', 'ceuta', 'melilla']
NOMF = {'PP': 'AP / PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'SUMAR': 'PCE / IU / Podemos / Sumar', 'CS': 'Ciudadanos', 'UPYD': 'UPyD',
        'ERC': 'ERC', 'JUNTS': 'CiU / Junts', 'PNV': 'PNV', 'BILDU': 'HB / EH Bildu', 'BNG': 'BNG', 'CC': 'Coalición Canaria',
        'UCD': 'UCD', 'CDS': 'CDS', 'OTROS': 'Otras listas'}
# En Navarra, UPN (con el PP o en Navarra Suma) va en la familia del PP
NOM_CC = {'navarra': {'PP': 'UPN / PP'}}
CSS_EXTRA = """<style>
blockquote.cita{margin:1.8rem 0;padding:.2rem 0 .2rem 1.1rem;border-left:3px solid var(--acc)}
blockquote.cita p{font-size:1.12rem;line-height:1.5;margin:0 0 .4rem}
blockquote.cita footer{font-family:var(--ui);font-size:.95rem;color:var(--muted)}
.presis{font-family:var(--ui);font-size:.98rem}
.mapa-el{display:flex;flex-wrap:wrap;gap:4px;margin:.2rem 0 .6rem}
.mapa-el button{font:500 .85rem var(--ui);padding:.2rem .45rem;border:1px solid var(--rule);background:var(--bg);color:var(--fg);border-radius:3px;cursor:pointer}
.mapa-el button[aria-pressed=true]{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.mapa-res{font-family:var(--ui);font-size:.95rem;color:var(--fg);margin-top:.5rem;line-height:1.7}
.mapa-res .sw{width:11px;height:11px;vertical-align:-1px}
</style>"""
INTERIOR = 'https://infoelectoral.interior.gob.es/'
HE_TXT = 'Historia Electoral (historiaelectoral.com)'


class Fig:
    """Bloques que los textos insertan en su cuerpo; cada gráfico deja su JS en self.js."""

    def __init__(self, cc, d):
        self.cc, self.d, self.js = cc, d, []
        self.nom = dict(NOMF, **NOM_CC.get(cc, {}))
        if cc in NOM_CC:  # nombres propios de la comunidad también en tooltips y tablas
            self.js.append(''.join(f"NOM.{k}={json.dumps(v)};" for k, v in NOM_CC[cc].items()))

    def cita(self, texto, quien, cargo, url, medio, fecha):
        return (f'<blockquote class="cita"><p>«{texto}»</p><footer>{quien}, {cargo}. '
                f'<a href="{url}">{medio}</a>, {fecha}.</footer></blockquote>')

    def aut(self, titulo, sub):
        a = self.d['aut']
        filas = [f for f in a['filas'] if any(a and v for v in f['v'])]
        # leyenda: un color por nombre corto
        vistos, ley = set(), []
        for f in sorted(filas, key=lambda f: -sum(f['v'])):
            if (f['n'], f['c']) not in vistos:
                vistos.add((f['n'], f['c'])); ley.append((f['c'], f['n']))
        self.js.append(f"apiladas('aut',D.aut.labs,D.aut.filas.filter(f=>f.v.some(v=>v)),D.aut.total,{{aria:{json.dumps(titulo)}}});")
        return figura('aut', titulo, sub + ' La raya marca la mayoría absoluta.',
                      f'Fuente: <a href="{a["fuente"]}">{HE_TXT}</a>, a partir de los resultados oficiales.', ley)

    def gen(self, titulo, sub, fams=None, mx=None):
        g = self.d['gen']
        fams = fams or g['fams']
        mx = mx or (int(max(max(v for v in g['pct'][f] if v) for f in fams) // 10 + 1) * 10)
        ser = ','.join(f"{{n:NOM.{f},c:COL.{f},v:D.gen.pct.{f}}}" for f in fams)
        self.js.append(f"lineas('gen',D.gen.labs,[{ser}],{{max:{mx},ticks:[{','.join(str(t) for t in range(0, mx + 1, 10))}],fin:false,mr:12}});"
                       f"tabla('gen',['Elección'].concat({json.dumps([self.nom[f] for f in fams])}),D.gen.labs.map((l,i)=>[l].concat({json.dumps(fams)}.map(f=>pct(D.gen.pct[f][i])))));")
        return figura('gen', titulo, sub, 'Fuente: Ministerio del Interior; cálculo de Mapa Electoral con los votos a candidaturas, sin el voto exterior (CERA).',
                      [(f, self.nom[f]) for f in fams])

    def esp(self, titulo, sub):
        n = self.d['nombre']
        self.js.append(f"lineas('esp',D.gen.labs,[{{n:'PSOE · {n}',c:COL.PSOE,v:D.gen.pct.PSOE||D.gen.esp.PSOE.map(_=>null)}},{{n:'PSOE · España',c:COL.PSOE,v:D.gen.esp.PSOE,dash:'5 4',w:1.6}},"
                       f"{{n:'PP · {n}',c:COL.PP,v:D.gen.pct.PP||D.gen.esp.PP.map(_=>null)}},{{n:'PP · España',c:COL.PP,v:D.gen.esp.PP,dash:'5 4',w:1.6}}],{{max:70,ticks:[0,10,20,30,40,50,60,70],fin:false,mr:12}});"
                       f"tabla('esp',['Elección','PSOE aquí','PSOE España','PP aquí','PP España'],D.gen.labs.map((l,i)=>[l,pct((D.gen.pct.PSOE||[])[i]),pct(D.gen.esp.PSOE[i]),pct((D.gen.pct.PP||[])[i]),pct(D.gen.esp.PP[i])]));")
        return figura('esp', titulo, sub + ' Línea continua: aquí; discontinua: el conjunto de España.',
                      'Fuente: Ministerio del Interior; cálculo de Mapa Electoral, sin CERA.', [('PSOE', 'PSOE'), ('PP', self.nom['PP'])])

    def prov(self, titulo, sub):
        self.js.append("rejilla('prov',D.gen.labs,D.prov.map(p=>({l:p.l,g:p.g,t:null})));"
                       "tabla('prov',['Provincia'].concat(D.gen.labs),D.prov.map(p=>[p.l].concat(p.g.map((g,i)=>(NOM[g]||g)+' ('+num(p.pct[i])+'%)'))));")
        return figura('prov', titulo, sub, 'Fuente: Ministerio del Interior; cálculo de Mapa Electoral. Hasta 2000, la candidatura más votada de todas; desde 2004, por familias de partidos.',
                      self._ley([g for p in self.d['prov'] for g in p['g']]))

    def ciu(self, titulo, sub):
        self.js.append("rejilla('ciu',D.gen.labs,D.ciu.map(p=>({l:p.mun,g:p.g})));"
                       "tabla('ciu',['Municipio'].concat(D.gen.labs),D.ciu.map(p=>[p.mun].concat(p.g.map(g=>NOM[g]||'—'))));")
        return figura('ciu', titulo, sub, 'Fuente: Ministerio del Interior; cálculo de Mapa Electoral. Hasta 2000, la candidatura más votada de todas; desde 2004, por familias.',
                      self._ley([g for p in self.d['mayores_hist'] for g in p['g']]))

    def mapa(self, titulo, sub):
        self.js.append(f"mapa('mapa',D.mapa,D.gen.labs,{{aria:{json.dumps(titulo)}}});")
        return figura('mapa', titulo, sub + ' Toca una elección para cambiar el mapa.',
                      'Fuente: Ministerio del Interior; cálculo de Mapa Electoral. Hasta 2000, la candidatura más votada de todas; desde 2004, por familias. '
                      'Límites municipales de 2023: los municipios creados después de cada elección aparecen sin dato.', tabla=False)

    def part(self, titulo, sub):
        n = self.d['nombre']
        self.js.append(f"lineas('part',D.gen.labs,[{{n:'{n}',c:'var(--acc)',v:D.gen.part,w:3}},{{n:'España',c:'var(--muted)',v:D.gen.part_esp,dash:'5 4',w:1.6}}],{{min:40,max:90,ticks:[40,50,60,70,80,90],fin:false,mr:12}});"
                       "tabla('part',['Elección','Aquí','España'],D.gen.labs.map((l,i)=>[l,pct(D.gen.part[i]),pct(D.gen.part_esp[i])]));")
        return figura('part', titulo, sub, 'Fuente: Ministerio del Interior; cálculo de Mapa Electoral sobre el censo de residentes en España (sin CERA).',
                      [('var(--acc)', n), ('#9a9a9a', 'España (discontinua)')])

    def _ley(self, gs):
        orden = [f for f in self.nom if f in set(g for g in gs if g)]
        return [(f, self.nom[f]) for f in orden]


def presidentes(filas):
    """filas: [(desde, hasta, nombre, partido)]"""
    return ('<div class="tbl"><table class="presis"><thead><tr><th>Presidente</th><th>Partido</th><th class="n">Mandato</th></tr></thead><tbody>' +
            ''.join(f'<tr><td>{html.escape(n)}</td><td>{html.escape(p)}</td><td class="n">{a if a == b else f'{a}–{b}'}</td></tr>' for a, b, n, p in filas) + '</tbody></table></div>')


def piezas():
    sys.path.insert(0, os.path.join(AQUI, 'piezas'))
    out = []
    for cc in ORDEN:
        if os.path.exists(os.path.join(AQUI, 'piezas', cc.replace('-', '_') + '.py')):
            out.append(importlib.import_module(cc.replace('-', '_')).PIEZA)
    return out


def escribir():
    datos = json.load(open(os.path.join(AQUI, 'datos.json'), encoding='utf-8'))
    lib = open(os.path.join(SRC, 'historia', 'graficos.js'), encoding='utf-8').read() + open(os.path.join(AQUI, 'graficos.js'), encoding='utf-8').read()
    ps = piezas()
    for p in ps:
        d = datos[p['cc']]
        F = Fig(p['cc'], d)
        cuerpo = p['cuerpo'](F, presidentes)
        D = {'gen': d['gen'], 'prov': d['prov'], 'aut': d['aut'], 'ciu': d['mayores_hist']}
        if 'F.mapa(' in open(os.path.join(AQUI, 'piezas', p['cc'].replace('-', '_') + '.py'), encoding='utf-8').read():
            D['mapa'] = d['mapa']
        page = (f'<title>{p["corto"]}</title>\n{FUENTES_TIPO}\n{CSS}\n{CSS_EXTRA}\n<main>\n'
                f'<span class="draft">Borrador para revisión · no publicado</span>\n'
                f'<h1>{p["titulo"]}</h1>\n<p class="dek">{p["dek"]}</p>\n'
                f'<div class="byline">Nacho G. del Álamo · {p.get("fecha_txt", "9 de octubre de 2026")}</div>\n'
                f'{cuerpo}\n<div class="foot">{p["pie"]}</div>\n</main>\n'
                f'<script>\n{lib}\nconst D={json.dumps(D, ensure_ascii=False)};\n' + '\n'.join(F.js) + '\n</script>\n')
        open(os.path.join(SRC, p['slug'] + '.html'), 'w', encoding='utf-8').write(page)
        print('escrita', p['slug'])
    return ps


if __name__ == '__main__':
    escribir()
