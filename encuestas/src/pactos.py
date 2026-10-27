"""Simulador de pactos: /encuestas/simulador-pactos/.

El lector marca qué vota cada partido en una investidura (sí, abstención o no) y la página le dice si sale en
primera votación (176 síes), en segunda (más síes que noes) o si fracasa, con el hemiciclo pintado en directo. Puede
mover los escaños de cada partido y elegir el punto de partida: la estimación del modelo, el promedio de escaños de las
encuestadoras, el resultado de 2023 o el reparto que llega desde la calculadora de escaños (en el enlace).

Debajo, las mayorías mínimas que dan los escaños elegidos (aritmética, no política) y las votaciones de investidura y
la moción de censura de 2018 que se pueden aplicar a los escaños de hoy. Cifras de los diarios de sesiones del Congreso.

La llama construir.py (main) después del modelo, así que se rehace sola con cada encuesta nueva. Si no hay salida
publicable del modelo, no escribe nada.
"""
import html, json

# resultado de las generales del 23 de julio de 2023 (Junta Electoral Central; Podemos iba dentro de Sumar)
R2023 = {'PP': 137, 'PSOE': 121, 'VOX': 33, 'SUMAR': 31, 'ERC': 7, 'JUNTS': 7, 'BILDU': 6, 'PNV': 5, 'BNG': 1, 'CC': 1, 'UPN': 1}
DS = 'https://www.congreso.es/public_oficiales/'
# votaciones que se pueden repetir con los escaños de hoy: qué votó cada partido (s, a, n). Los partidos que no estaban
# en el Congreso entonces, o que ya no están, cuentan como «no» al aplicarlas y la página lo dice.
HISTORICOS = [
    dict(f='2023-11-16', t='Sánchez, investido con siete socios', r='Investido en primera votación', si=179, no=171, ab=0,
         txt='A favor, PSOE, Sumar (con Podemos dentro), ERC, Junts, EH Bildu, PNV, BNG y Coalición Canaria. En contra, PP, Vox y UPN.',
         url=DS + 'L15/CONG/DS/PL/DSCD-15-PL-8.PDF',
         v={'PSOE': 's', 'SUMAR': 's', 'PODEMOS': 's', 'ERC': 's', 'JUNTS': 's', 'BILDU': 's', 'PNV': 's', 'BNG': 's', 'CC': 's'}),
    dict(f='2023-09-29', t='Feijóo se queda a cuatro', r='Fracasa en las dos votaciones', si=172, no=177, ab=0,
         txt='A favor, PP, Vox, UPN y Coalición Canaria: 172 síes en las dos votaciones. En la segunda hubo 177 noes y un voto nulo.',
         url=DS + 'L15/CONG/DS/PL/DSCD-15-PL-6.PDF', v={'PP': 's', 'VOX': 's', 'UPN': 's', 'CC': 's'}),
    dict(f='2020-01-07', t='Sánchez pasa por dos votos', r='Investido en segunda votación', si=167, no=165, ab=18,
         txt='A favor, PSOE, Unidas Podemos, PNV, Más País, Compromís, BNG, Nueva Canarias y Teruel Existe. Se abstuvieron ERC y EH Bildu.',
         url=DS + 'L14/CONG/DS/PL/DSCD-14-PL-4.PDF',
         v={'PSOE': 's', 'SUMAR': 's', 'PODEMOS': 's', 'PNV': 's', 'BNG': 's', 'NC': 's', 'ERC': 'a', 'BILDU': 'a'}),
    dict(f='2019-07-25', t='Sánchez, sin Podemos', r='Fracasa en las dos votaciones', si=124, no=155, ab=67,
         txt='A favor, PSOE y PRC. Unidas Podemos se abstuvo en la segunda votación, como ERC, PNV y EH Bildu.',
         url=DS + 'L13/CONG/DS/PL/DSCD-13-PL-5.PDF', v=None),
    dict(f='2018-06-01', t='La moción de censura contra Rajoy', r='Aprobada: Sánchez, presidente', si=180, no=169, ab=1,
         txt='A favor, PSOE, Unidos Podemos y sus confluencias, ERC, PDeCAT (hoy Junts), PNV, Compromís, EH Bildu y Nueva Canarias. '
             'En contra, PP, Ciudadanos, UPN y Foro. Se abstuvo Coalición Canaria. Una moción necesita 176 síes.',
         url='https://www.congreso.es/docu/MocCens/10062018_XIILegMocCen.pdf',
         v={'PSOE': 's', 'SUMAR': 's', 'PODEMOS': 's', 'ERC': 's', 'JUNTS': 's', 'PNV': 's', 'BILDU': 's', 'NC': 's', 'CC': 'a'}, mocion=True),
    dict(f='2016-10-29', t='Rajoy, con la abstención del PSOE', r='Investido en segunda votación', si=170, no=111, ab=68,
         txt='A favor, PP, Ciudadanos, Coalición Canaria, UPN y Foro. Se abstuvieron 68 diputados del PSOE; otros 15 votaron no.',
         url=DS + 'L12/CONG/DS/PL/DSCD-12-PL-14.PDF', v={'PP': 's', 'UPN': 's', 'CC': 's', 'PSOE': 'a'}),
    dict(f='2016-03-04', t='Sánchez y Rivera no llegan', r='Fracasa en las dos votaciones', si=131, no=219, ab=0,
         txt='A favor, PSOE, Ciudadanos y Coalición Canaria. En contra, todos los demás: PP, Podemos y sus confluencias, ERC, DiL, PNV, IU y EH Bildu.',
         url=DS + 'L11/CONG/DS/PL/DSCD-11-PL-4.PDF', v=None),
    dict(f='2011-12-20', t='Rajoy, con mayoría absoluta', r='Investido en primera votación', si=187, no=149, ab=14,
         txt='A favor, PP (UPN se presentaba en sus listas) y Foro Asturias.', url=DS + 'L10/CONG/DS/PL/PL_003.PDF', v=None),
    dict(f='2008-04-11', t='Zapatero, solo con el PSOE', r='Investido en segunda votación', si=169, no=158, ab=23,
         txt='Solo los diputados socialistas votaron sí. CiU, PNV y los demás grupos pequeños se abstuvieron; PP, ERC y UPyD votaron no.',
         url=DS + 'L9/CONG/DS/PL/PL_004.PDF', v=None),
    dict(f='2004-04-16', t='Zapatero, con la izquierda y CC', r='Investido en primera votación', si=183, no=148, ab=19,
         txt='A favor, PSOE, ERC, IU, Coalición Canaria, BNG y CHA. Se abstuvieron CiU, PNV, EA y Nafarroa Bai.',
         url=DS + 'L8/CONG/DS/PL/PL_003.PDF', v=None),
    dict(f='2000-04-26', t='Aznar, con mayoría absoluta', r='Investido en primera votación', si=202, no=148, ab=0,
         txt='A favor, PP, CiU y Coalición Canaria.', url=DS + 'L7/CONG/DS/PL/PL_003.PDF', v=None),
    dict(f='1996-05-04', t='Aznar y el pacto del Majestic', r='Investido en primera votación', si=181, no=166, ab=1,
         txt='A favor, PP, CiU, PNV y Coalición Canaria.', url=DS + 'L6/CONG/DS/PL/PL_003.PDF', v=None),
]
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']


def fecha(iso):
    a, m, d = iso.split('-')
    return f'{int(d)} de {MESES[int(m) - 1]} de {a}'


def genera(m, hemi_encuestas=None, n_hemi=0):
    if not (m.ESTIMACION / 'escenario-base.json').exists():
        return False
    d = json.load(open(m.ESTIMACION / 'escenario-base.json'))
    meta = json.load(open(m.ESTIMACION / 'meta.json'))
    if meta.get('interno', True) or meta.get('ficticio'):
        return False
    modelo = {m.DEL_MODELO[k]: v for k, v in d['hemiciclo']['congreso'].items() if k in m.DEL_MODELO and v}
    actual = m.fecha_larga(meta['generado'])
    puntos = [['modelo', 'Estimación de Mapa Electoral', f'Escenario central del modelo, con las encuestas hasta el {actual}', modelo]]
    if hemi_encuestas and sum(hemi_encuestas.values()) == 350:
        puntos.append(['encuestas', 'Promedio de las encuestadoras', f'Promedio de los escaños que publican {n_hemi} encuestadoras', hemi_encuestas])
    puntos.append(['2023', 'Resultado de 2023', 'Escaños de las generales del 23 de julio de 2023 (Podemos iba dentro de Sumar)', R2023])
    claves = [k for k in m.ORDEN_HEMI if any(p[3].get(k) for p in puntos) or k in ('SALF',)]
    col = {k: (n, c, o) for k, n, c, o in m.TODOS}
    partidos = [[k, col[k][0].replace(' / Frente Amplio', ''), col[k][1], col[k][2]] for k in claves]
    historicos = [{**{k: h[k] for k in ('t', 'r', 'si', 'no', 'ab', 'url')}, 'f': fecha(h['f']), 'v': h['v'], 'mocion': h.get('mocion', False)}
                  for h in HISTORICOS if h['v']]
    datos = {'partidos': partidos, 'puntos': puntos, 'historicos': historicos, 'alias': {n: k for n, k in m.DEL_MODELO.items() if n != k}}

    url = m.URL + 'simulador-pactos/'
    titulo = 'Simulador de pactos del 29N: ¿quién suma 176 escaños?'
    desc = ('Elige qué partidos votan sí, se abstienen o votan no y mira si sale la investidura en el Congreso del 29N. '
            f'Parte de la media de encuestas del {actual}, con las mayorías posibles y las investiduras reales desde 1996.')
    faq = [('¿Cuántos votos hacen falta para investir a un presidente del Gobierno?',
            'En la primera votación, mayoría absoluta: 176 síes de los 350 diputados. Si no los consigue, 48 horas después hay una segunda votación '
            'en la que basta con mayoría simple, es decir, más síes que noes. Las abstenciones no cuentan como votos en contra (artículo 99 de la Constitución).'),
           ('¿Y para una moción de censura?',
            'Siempre 176 síes, mayoría absoluta, y la moción tiene que llevar un candidato alternativo (artículo 113 de la Constitución). '
            'Así llegó Pedro Sánchez al Gobierno en 2018, con 180 votos.'),
           ('¿Qué pasa si nadie consigue la investidura?',
            'Si a los dos meses de la primera votación ningún candidato ha sido investido, el Rey disuelve las Cortes y se repiten las elecciones, '
            'como ocurrió en 2016 y en 2019 (artículo 99.5 de la Constitución).'),
           ('¿De dónde salen los escaños de partida?',
            f'De la estimación del modelo de Mapa Electoral, que reparte por provincia la media de las encuestas publicadas hasta el {actual}. '
            'Puedes cambiarlos a mano, empezar con el promedio de escaños de las encuestadoras o con el resultado de 2023, o traer el reparto de la calculadora de escaños.')]
    jsonld = [{'@context': 'https://schema.org', '@type': 'WebApplication', '@id': url + '#simulador', 'name': titulo, 'description': desc, 'url': url,
               'applicationCategory': 'EducationalApplication', 'operatingSystem': 'Todos', 'inLanguage': 'es', 'isAccessibleForFree': True,
               'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}, 'dateModified': meta['generado'],
               'author': {'@type': 'Person', 'name': m.AUTOR, 'url': m.BASE + '/sobre-mi.html'}, 'publisher': m.MEDIO},
              {'@context': 'https://schema.org', '@type': 'FAQPage', '@id': url + '#preguntas', 'inLanguage': 'es',
               'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]
    filas_hist, j = '', 0
    for h in HISTORICOS:
        ok = 'nvestido' in h['r'] or 'Aprobada' in h['r']
        filas_hist += (f'<li><span class="fh">{fecha(h["f"])}</span><b>{html.escape(h["t"])}</b> <span class="rs {"ok" if ok else "ko"}">{html.escape(h["r"])}</span>'
                       f'<span class="vt">{h["si"]} sí · {h["no"]} no · {h["ab"]} abstenciones</span><span class="tx">{html.escape(h["txt"])} '
                       f'<a href="{h["url"]}">Diario de sesiones</a></span>')
        if h['v']:   # data-j: posición en la lista de votaciones aplicables que va al script
            filas_hist += f'<button type="button" class="aplica" data-j="{j}">Aplicar a los escaños de hoy</button>'
            j += 1
        filas_hist += '</li>'
    cuerpo = f"""<main>
<p class="kicker">Simulador · Elecciones generales del 29N</p>
<h1 data-miga="Simulador de pactos">¿Quién suma 176? Haz tú los pactos del 29N</h1>
<p class="dek">Decide qué vota cada partido en la investidura y mira si sale presidente, en primera votación o en segunda, con el Congreso que dibujan las encuestas.</p>
<p class="firma">Por <a href="../../sobre-mi.html">{m.AUTOR}</a> · Escaños de partida del <time datetime="{meta['generado']}">{actual}</time></p>
<p class="propio"><b>Es un juego con las reglas reales del Congreso, no una previsión de pactos.</b> Los escaños de partida salen de la <a href="../">media de las encuestas</a>, repartida por provincia por nuestro <a href="../metodo-modelo.html">modelo</a>. Qué apoya cada partido lo decides tú.</p>

<section class="sim" aria-label="Simulador de pactos">
<div class="res">
  <div class="veredicto" id="veredicto" aria-live="polite"></div>
  <div class="barra" id="barra" role="img" aria-label="Síes, abstenciones y noes"></div>
  <div class="eje"><span id="e-si"></span><span class="mayoria">176</span><span id="e-no"></span></div>
</div>
<div class="rapidos" id="rapidos" aria-label="Pactos de ejemplo"></div>
<figure class="hemi"><div id="hemi"></div><figcaption class="ley"><span><i class="s"></i>Sí</span><span><i class="a"></i>Abstención</span><span><i class="n"></i>No</span></figcaption></figure>
<div class="mandos">
  <div class="cab"><label for="punto"><b>Escaños de partida</b></label><select id="punto"></select></div>
  <p class="nota" id="nota-punto"></p>
  <div id="filas" role="list"></div>
  <p class="suma" id="suma"></p>
  <div class="botones"><button type="button" id="todos-no">Todos en «no»</button><button type="button" id="compartir">Copiar enlace con mi pacto</button></div>
</div>
</section>

<h2>Las mayorías posibles con estos escaños</h2>
<p>Todas las combinaciones que llegan a 176 en las que ningún partido sobra: si uno se va, se pierde la mayoría. Cambian al mover los escaños de arriba. Es aritmética, no política: no tiene en cuenta los vetos entre partidos. Pulsa una para probarla.</p>
<div class="minimas" id="minimas"></div>

<h2>Las investiduras de verdad, desde 1996</h2>
<p>Desde 2015 ningún partido ha pasado de 137 escaños, y las investiduras se han decidido por pocos votos y con abstenciones. Las votaciones de los últimos años se pueden aplicar a los escaños de hoy, con cada partido votando lo mismo que entonces; los partidos que no estaban en el Congreso cuentan como «no».</p>
<ol class="hist">{filas_hist}</ol>

<h2>Preguntas frecuentes</h2>
<div class="faq">{''.join(f'<details><summary><h3>{html.escape(q)}</h3></summary><p>{html.escape(a)}</p></details>' for q, a in faq)}</div>
<p class="src">Reglas: artículos 99 y 113 de la <a href="https://www.boe.es/buscar/act.php?id=BOE-A-1978-31229">Constitución</a> y 170 a 172 del Reglamento del Congreso. Votaciones: <a href="https://www.congreso.es/es/cem/sesiones-de-investidura">sesiones de investidura del Congreso</a> y diarios de sesiones enlazados; se recoge la votación decisiva de cada investidura. Escaños de partida: escenario central del modelo de Mapa Electoral del {actual}{f', promedio de {n_hemi} encuestadoras' if len(puntos) == 3 else ''} y resultado oficial de 2023. Un partido que no llega a escaño no aparece en el hemiciclo.</p>
<h2>Sigue leyendo</h2><ul class="sigue"><li><a href="../calculadora-escanos/"><span class="kicker">Calculadora</span><b>Reparte tú los 350 escaños con tus porcentajes</b></a></li><li><a href="../"><span class="kicker">Encuestas</span><b>Todas las encuestas de las generales y su promedio</b></a></li><li><a href="../../actualidad/coaliciones-quien-va-con-quien-29n/"><span class="kicker">Coaliciones</span><b>Quién va con quién el 29N</b></a></li></ul>
<footer>Mapa Electoral · Datos con licencia <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> · <a href="../../atlas/politica-editorial/">Política editorial</a></footer>
</main>"""
    estilos = m.ESTILOS.replace('</style>', CSS + '</style>')
    pagina = (m.cabecera(titulo, desc, url, f'{m.BASE}/img/compartir/encuestas.jpg?v={meta["generado"]}', jsonld)
              + estilos + m.CSS_SITIO + '\n</head>\n<body>\n' + m.nav('../../', 'Encuestas') + '\n' + cuerpo + '\n'
              + JS.replace('__DATOS__', json.dumps(datos, ensure_ascii=False, separators=(',', ':'))) + '\n</body>\n</html>\n')
    salida = m.SALIDA / 'simulador-pactos'
    salida.mkdir(exist_ok=True)
    (salida / 'index.html').write_text(pagina, encoding='utf-8')
    return True


CSS = """
.sim{display:grid;gap:1rem;font-family:var(--ui);margin:1.6rem 0}
.res{position:sticky;top:0;z-index:2;background:var(--bg);padding:.5rem 0 .4rem;box-shadow:0 6px 8px -8px rgba(0,0,0,.35)}
.veredicto{font-size:1.05rem;line-height:1.35;text-wrap:balance;min-height:2.7em}
.veredicto .ok{color:#2b8a3e}.veredicto .ko{color:#b3261e}
.barra{display:flex;height:26px;border-radius:4px;overflow:hidden;position:relative;background:var(--grid);margin:.4rem 0 .15rem}
.barra i{display:block;height:100%;transition:flex-basis .25s ease}
.barra::after{content:"";position:absolute;left:50.29%;top:-4px;bottom:-4px;width:2px;background:var(--fg)}
.eje{display:flex;justify-content:space-between;font-size:.75rem;color:var(--muted)}
.eje .mayoria{color:var(--fg);font-weight:600}
.rapidos{display:flex;flex-wrap:wrap;gap:6px}
.sim button,.sim select{font:600 .85rem var(--ui);border:1px solid var(--rule);background:transparent;color:var(--fg);border-radius:6px;padding:6px 10px;cursor:pointer}
.sim button:hover,.sim select:hover{border-color:var(--fg)}
.hemi{margin:0}
.hemi svg{display:block;width:100%;height:auto;margin:0 auto}
.hemi circle{transition:fill .2s,fill-opacity .2s}
.ley{display:flex;justify-content:center;gap:16px;font-size:.8rem;color:var(--muted);margin-top:2px}
.ley i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px;vertical-align:-1px}
.ley .s{background:var(--fg)}.ley .a{background:var(--fg);opacity:.3}.ley .n{background:transparent;border:1.5px solid var(--muted);box-sizing:border-box}
.mandos .cab{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
.mandos select{max-width:100%}
.nota{font-size:.8rem;color:var(--muted);margin:.3rem 0 .6rem}
.fp{display:grid;grid-template-columns:minmax(5.5em,1fr) auto auto;align-items:center;gap:8px;padding:5px 0;border-top:1px solid var(--rule)}
.fp .nm{font-weight:600;font-size:.92rem;display:flex;align-items:center;gap:6px;min-width:0}
.fp .nm i{width:10px;height:10px;border-radius:50%;flex:none}
.fp .nm span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.esc{display:flex;align-items:center;border:1px solid var(--rule);border-radius:6px}
.sim .esc button{border:0;padding:4px 9px;border-radius:6px;font-size:1rem;line-height:1}
.esc output{min-width:2.2em;text-align:center;font-weight:700;font-variant-numeric:tabular-nums}
.voto{display:flex;border:1px solid var(--rule);border-radius:6px;overflow:hidden}
.sim .voto button{border:0;border-radius:0;padding:5px 9px;font-weight:500}
.sim .voto button+button{border-left:1px solid var(--rule)}
.sim .voto button[aria-pressed=true]{background:var(--c);color:#fff;font-weight:700}
.sim .voto button.a[aria-pressed=true]{background:color-mix(in srgb,var(--c) 30%,transparent);color:var(--fg);font-weight:700}
.sim .voto button.n[aria-pressed=true]{background:var(--fg);color:var(--bg)}
.fp.cero .nm{color:var(--muted);font-weight:500}
details.mas summary{cursor:pointer;font-size:.9rem;color:var(--muted);margin:.5rem 0}
.suma{font-size:.82rem;color:var(--muted);margin:.5rem 0}
.suma.aviso{color:#b3261e;font-weight:600}
.botones{display:flex;gap:8px;flex-wrap:wrap}
.minimas{display:grid;gap:6px;font-family:var(--ui);margin:.6rem 0 1rem}
.minimas button{display:flex;align-items:center;gap:10px;width:100%;text-align:left;font:500 .9rem var(--ui);border:1px solid var(--rule);background:transparent;color:var(--fg);border-radius:6px;padding:7px 10px;cursor:pointer}
.minimas button:hover{border-color:var(--fg)}
.minimas .mb{display:flex;height:10px;width:70px;flex:none;border-radius:2px;overflow:hidden;background:var(--grid)}
.minimas .mb i{display:block;height:100%}
.minimas .mn{flex:1;min-width:0}
.minimas b{font-variant-numeric:tabular-nums}
.minimas .vacio{color:var(--muted);font-size:.9rem}
.hist{list-style:none;padding:0;margin:.8rem 0;font-family:var(--ui);font-size:.9rem}
.hist li{border-top:1px solid var(--rule);padding:.7rem 0;display:grid;gap:3px}
.hist .fh{color:var(--muted);font-size:.8rem}
.hist .rs{font-size:.8rem;font-weight:600}
.hist .rs.ok{color:#2b8a3e}.hist .rs.ko{color:#b3261e}
.hist .vt{font-weight:600;font-variant-numeric:tabular-nums}
.hist .tx{color:var(--muted)}
.hist .aplica{justify-self:start;font:600 .82rem var(--ui);border:1px solid var(--rule);background:transparent;color:var(--fg);border-radius:6px;padding:5px 9px;cursor:pointer;margin-top:3px}
.hist .aplica:hover{border-color:var(--fg)}
@media (max-width:520px){.veredicto{font-size:.98rem}.fp{grid-template-columns:minmax(4.5em,1fr) auto auto;gap:5px}.sim .voto button{padding:5px 7px;font-size:.8rem}.sim .esc button{padding:4px 7px}}
"""

JS = """<script>
(()=>{
const D=__DATOS__,MAY=176;
const oscuro=()=>matchMedia('(prefers-color-scheme: dark)').matches&&document.documentElement.dataset.theme!=='light'||document.documentElement.dataset.theme==='dark';
const P={},ORD=D.partidos.map(p=>p[0]);D.partidos.forEach(([k,n,c,o])=>P[k]={k,n,c,o});
const col=k=>oscuro()?P[k].o:P[k].c;
const el=(t,a={},...h)=>{const e=document.createElement(t);for(const[k,v]of Object.entries(a)){if(k==='style')e.style.cssText=v;else if(k in e&&k!=='list')e[k]=v;else e.setAttribute(k,v)}e.append(...h);return e};
const NS='http://www.w3.org/2000/svg',sv=(t,a,p)=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);p&&p.append(e);return e};
const lista=ks=>ks.length<2?ks.join(''):ks.slice(0,-1).join(', ')+' y '+ks.at(-1);
let esc={},voto={},punto=D.puntos[0][0];
const cargaPunto=id=>{const p=D.puntos.find(p=>p[0]===id)||D.puntos[0];punto=p[0];esc={};ORD.forEach(k=>esc[k]=p[3][k]||0)};
const reset=()=>ORD.forEach(k=>voto[k]='n');
cargaPunto(punto);reset();
// lectura del enlace: #p=modelo&e=PP.128,PSOE.108&v=PP.s,VOX.a
try{const h=new URLSearchParams(location.hash.slice(1));
  if(h.get('p'))cargaPunto(h.get('p'));
  if(h.get('e')){ORD.forEach(k=>esc[k]=0);punto='';h.get('e').split(',').forEach(x=>{let[k,v]=x.split('.');k=D.alias[k]||k;if(k in esc)esc[k]=Math.max(0,Math.min(350,parseInt(v)||0))})}
  if(h.get('v'))h.get('v').split(',').forEach(x=>{const[k,v]=x.split('.');if(k in voto&&'san'.includes(v))voto[k]=v});
}catch(e){}
// selector de punto de partida
const sel=document.getElementById('punto');
D.puntos.forEach(p=>sel.append(el('option',{value:p[0]},p[1])));
const otro=el('option',{value:''},'Mi reparto');sel.append(otro);
sel.onchange=()=>{if(sel.value){cargaPunto(sel.value);pinta()}};
// filas de partidos
const filas=document.getElementById('filas'),mas=el('details',{className:'mas'},el('summary',{},'Partidos sin escaño en este reparto'));
const F={};
ORD.forEach(k=>{
  const out=el('output',{'aria-live':'off'});
  const b=(t,d,l)=>{const x=el('button',{type:'button','aria-label':l+' un escaño a '+P[k].n},t);x.onclick=()=>{esc[k]=Math.max(0,Math.min(350,esc[k]+d));punto='';pinta()};return x};
  const vb={};const vg=el('div',{className:'voto',role:'group','aria-label':'Voto de '+P[k].n});
  [['s','Sí'],['a','Abst.'],['n','No']].forEach(([v,t])=>{vb[v]=el('button',{type:'button',className:v,'aria-pressed':'false'},t);vb[v].onclick=()=>{voto[k]=v;pinta()};vg.append(vb[v])});
  const row=el('div',{className:'fp',role:'listitem',style:'--c:'+P[k].c},el('div',{className:'nm'},el('i',{style:'background:'+P[k].c}),el('span',{},P[k].n)),
    el('div',{className:'esc'},b('−',-1,'Quitar'),out,b('+',1,'Añadir')),vg);
  F[k]={row,out,vb};
});
function colocaFilas(){const con=ORD.filter(k=>esc[k]),sin=ORD.filter(k=>!esc[k]);
  filas.replaceChildren(...con.map(k=>F[k].row));mas.replaceChildren(mas.firstChild,...sin.map(k=>F[k].row));if(sin.length)filas.append(mas)}
// pactos de ejemplo
const RAP=[['PP + Vox',{PP:'s',VOX:'s'}],['PP + Vox + UPN + CC',{PP:'s',VOX:'s',UPN:'s',CC:'s'}],['Socios de 2023',D.historicos[0].v],['PP + PSOE',{PP:'s',PSOE:'s'}],['PP con abstención del PSOE',{PP:'s',PSOE:'a'}]];
const rap=document.getElementById('rapidos');
RAP.forEach(([n,v])=>{const x=el('button',{type:'button'},n);x.onclick=()=>aplica(v);rap.append(x)});
function aplica(v){reset();for(const k in v)if(k in voto)voto[k]=v[k];pinta();document.getElementById('veredicto').scrollIntoView({block:'nearest',behavior:'smooth'})}
// hemiciclo: cada partido en su sitio de izquierda a derecha; color lleno si vota sí, tenue si se abstiene, hueco si vota no
const hb=document.getElementById('hemi');let pts=[];
function geometria(){const W=Math.min(640,Math.max(300,hb.clientWidth||600)),R=W/2-4,filas=W<420?9:11,r0=R*.38,total=350;
  const radios=[...Array(filas)].map((_,i)=>r0+(R-r0)*(i+.5)/filas),s=radios.reduce((a,b)=>a+b,0);
  const n=radios.map(r=>Math.round(total*r/s));n[filas-1]+=total-n.reduce((a,b)=>a+b,0);
  pts=[];radios.forEach((r,i)=>{for(let j=0;j<n[i];j++){const a=Math.PI*(1-(n[i]>1?j/(n[i]-1):.5));pts.push({a,x:W/2+r*Math.cos(a),y:R+4-r*Math.sin(a)})}});
  pts.sort((p,q)=>q.a-p.a);return{W,R,r0,dot:Math.min(R*.5/filas,(R-r0)/filas*.42)}}
function hemiciclo(){const g=geometria();
  const svg=sv('svg',{viewBox:`0 0 ${g.W} ${g.R+10}`,role:'img','aria-label':'Hemiciclo del Congreso con el voto de cada partido'});
  let i=0;const tot=ORD.reduce((a,k)=>a+esc[k],0),f=tot>350?350/tot:1;
  for(const k of ORD){const n=Math.round(esc[k]*f);for(let j=0;j<n&&i<pts.length;j++){const q=pts[i++],c=col(k),v=voto[k];
    const a={cx:q.x.toFixed(1),cy:q.y.toFixed(1),r:(v==='n'?g.dot*.82:g.dot).toFixed(1),fill:v==='n'?'none':c,'fill-opacity':v==='a'?.3:1};
    if(v==='n'){a.stroke=c;a['stroke-width']=1.3;a['stroke-opacity']=.75}
    sv('title',{},sv('circle',a,svg)).textContent=P[k].n}}
  for(;i<pts.length;i++)sv('circle',{cx:pts[i].x.toFixed(1),cy:pts[i].y.toFixed(1),r:(g.dot*.5).toFixed(1),fill:'var(--grid)'},svg);
  sv('line',{x1:g.W/2,x2:g.W/2,y1:2,y2:g.R+6-g.r0+8,stroke:'var(--muted)','stroke-dasharray':'3 3'},svg);
  hb.replaceChildren(svg)}
// mayorías mínimas: combinaciones que suman 176 en las que todos los partidos son necesarios
function minimas(){const ks=ORD.filter(k=>esc[k]>0).sort((a,b)=>esc[b]-esc[a]).slice(0,14),out=[];
  for(let m=1;m<1<<ks.length;m++){let s=0,mn=999;const sub=[];for(let i=0;i<ks.length;i++)if(m>>i&1){sub.push(ks[i]);s+=esc[ks[i]];mn=Math.min(mn,esc[ks[i]])}
    if(s>=MAY&&s-mn<MAY)out.push([sub,s])}
  out.sort((a,b)=>a[0].length-b[0].length||a[1]-b[1]);
  const box=document.getElementById('minimas'),max=12;
  if(!out.length){box.replaceChildren(el('p',{className:'vacio'},'Con estos escaños ninguna combinación llega a 176.'));return}
  box.replaceChildren(...out.slice(0,max).map(([sub,s])=>{const o=ORD.filter(k=>sub.includes(k));
    const x=el('button',{type:'button'},el('span',{className:'mb'},...o.map(k=>el('i',{style:`flex:0 0 ${esc[k]/3.5}%;background:${col(k)}`}))),
      el('span',{className:'mn'},o.sort((a,b)=>esc[b]-esc[a]).map(k=>P[k].n).join(' + ')),el('b',{},String(s)));
    x.onclick=()=>aplica(Object.fromEntries(sub.map(k=>[k,'s'])));return x}),
    ...(out.length>max?[el('p',{className:'vacio'},`Y ${out.length-max} combinaciones más, con más partidos.`)]:[]))}
function pinta(){
  const tot=ORD.reduce((a,k)=>a+esc[k],0);
  if(!punto&&sel.value)sel.value='';else if(punto)sel.value=punto;
  const pp=D.puntos.find(p=>p[0]===punto);document.getElementById('nota-punto').textContent=pp?pp[2]+'.':'Escaños cambiados a mano o llegados de la calculadora de escaños.';
  colocaFilas();
  ORD.forEach(k=>{F[k].out.value=esc[k];F[k].out.textContent=esc[k];F[k].row.classList.toggle('cero',!esc[k]);for(const v in F[k].vb)F[k].vb[v].setAttribute('aria-pressed',String(voto[k]===v))});
  const su=document.getElementById('suma');
  su.textContent=tot===350?'Los partidos suman los 350 escaños.':`Los partidos suman ${tot} escaños: ${tot>350?'sobran '+(tot-350):'faltan '+(350-tot)} para los 350 del Congreso.`;
  su.classList.toggle('aviso',tot!==350);
  const sum=v=>ORD.filter(k=>voto[k]===v).reduce((a,k)=>a+esc[k],0),si=sum('s'),ab=sum('a'),no=sum('n');
  const barra=document.getElementById('barra'),seg=(k,w,o)=>el('i',{title:P[k].n+': '+esc[k],style:`flex:0 0 ${w/3.5}%;background:${col(k)};opacity:${o}`});
  const ks=v=>ORD.filter(k=>voto[k]===v&&esc[k]).sort((a,b)=>esc[b]-esc[a]);
  barra.replaceChildren(...ks('s').map(k=>seg(k,esc[k],1)),...ks('a').map(k=>seg(k,esc[k],.3)));
  document.getElementById('e-si').textContent=`${si} sí`+(ab?` · ${ab} abst.`:'');document.getElementById('e-no').textContent=`${no} no`;
  const ver=document.getElementById('veredicto');
  if(!si){ver.innerHTML='Marca qué partidos votan <b>sí</b> o prueba uno de estos pactos.'}
  else{const cand=ks('s')[0],quien=`Un candidato del <b>${P[cand].n}</b>`,apoyos=lista(ks('s').map(k=>P[k].n));
    if(si>=MAY)ver.innerHTML=`<span class="ok">✔</span> ${quien} saldría investido <b>en primera votación</b>: ${si} síes de ${apoyos}. También bastarían para una moción de censura.`;
    else if(si>no)ver.innerHTML=`<span class="ok">✔</span> ${quien} saldría investido <b>en segunda votación</b>: ${si} síes frente a ${no} noes. Se queda a ${MAY-si} de los 176 de la primera.`;
    else{const fa=no-si+1,fs=Math.ceil(fa/2);
      ver.innerHTML=`<span class="ko">✘</span> ${quien} <b>no saldría investido</b>: ${si} síes frente a ${no} noes. Le faltan ${fs} síes más, o que ${fa} de los que votan no se abstengan.`}}
  hemiciclo();
  minimas();
  try{const e=ORD.filter(k=>esc[k]).map(k=>k+'.'+esc[k]).join(','),v=ORD.filter(k=>voto[k]!=='n').map(k=>k+'.'+voto[k]).join(',');
    const h=(punto?'p='+punto:'e='+e)+(v?'&v='+v:'');history.replaceState(null,'',(punto===D.puntos[0][0]&&!v)?location.pathname:'#'+h)}catch(e){}
}
document.getElementById('todos-no').onclick=()=>{reset();pinta()};
document.getElementById('compartir').onclick=e=>{const b=e.target;navigator.clipboard?.writeText(location.href).then(()=>{b.textContent='Enlace copiado';setTimeout(()=>b.textContent='Copiar enlace con mi pacto',1800)})};
document.querySelectorAll('.aplica').forEach(b=>b.onclick=()=>aplica(D.historicos[+b.dataset.j].v));
let w=hb.clientWidth;addEventListener('resize',()=>{if(hb.clientWidth!==w){w=hb.clientWidth;hemiciclo()}});
matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change',pinta);
pinta();
})();
</script>"""
