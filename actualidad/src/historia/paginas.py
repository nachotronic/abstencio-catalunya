"""Serie «Historia electoral» de Actualidad: escribe los HTML de trabajo (actualidad/src/<slug>.html).

Datos: datos.py → datos.json (sale de generales/datos/historico, en la carpeta del proyecto).
Textos y gráficos: textos.py. Gráficos: graficos.js (cada partido en su color, como el mapa).
Uso, desde la raíz del repositorio:
    python3 actualidad/src/historia/paginas.py && python3 actualidad/src/construir.py && node actualidad/src/miniaturas.mjs
    node actualidad/src/historia/compartir.mjs
"""
import json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from textos import PIEZAS_HISTORIA  # noqa: E402

CSS = """<style>
:root{
  --bg:#fbfaf8; --fg:#1d1a1c; --muted:#5d585b; --rule:#e2dddf; --grid:#ebe7e8;
  --acc:#1d7f95; --other:#d9d4d6; --tipbg:#1d1a1c; --tipfg:#fbfaf8;
  --serif:"Literata",Georgia,"Times New Roman",serif;
  --ui:"Barlow Semi Condensed","Arial Narrow",Arial,sans-serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#18161a; --fg:#f1edef; --muted:#b5aeb2; --rule:#343036; --grid:#2c282e;
  --acc:#3aa6bf; --other:#3e393f; --tipbg:#f1edef; --tipfg:#18161a; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#18161a; --fg:#f1edef; --muted:#b5aeb2; --rule:#343036; --grid:#2c282e;
  --acc:#3aa6bf; --other:#3e393f; --tipbg:#f1edef; --tipfg:#18161a; color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--serif);font-size:18px;line-height:1.62}
main{max-width:46rem;margin:0 auto;padding-block:2.5rem 4rem;padding-inline:16px}
.draft{font-family:var(--ui);font-size:.85rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);border:1px solid var(--rule);display:inline-block;padding:.15rem .5rem;border-radius:3px}
h1{font-size:clamp(1.8rem,5vw,2.6rem);line-height:1.12;font-weight:800;text-wrap:balance;margin:.8rem 0 .9rem}
.dek{font-size:1.15rem;line-height:1.5;color:var(--muted);margin:0 0 1rem}
.byline{font-family:var(--ui);font-size:.95rem;color:var(--muted);border-top:1px solid var(--rule);padding-top:.6rem}
h2{font-size:1.35rem;line-height:1.25;margin:2.4rem 0 .6rem;text-wrap:balance}
p{margin:0 0 1rem}
ul{padding-left:1.2rem;margin:0 0 1rem} li{margin-bottom:.35rem}
figure{margin:1.8rem 0 2rem;font-family:var(--ui)}
figcaption .t{font-weight:600;font-size:1.1rem;display:block;line-height:1.25}
figcaption .s{color:var(--muted);font-size:.98rem;display:block;margin-top:.15rem}
.src{color:var(--muted);font-size:.85rem;margin-top:.4rem}
.chart{position:relative;margin-top:.7rem}
svg{display:block;width:100%;height:auto;overflow:visible}
svg text{font-family:var(--ui);fill:var(--muted);font-size:13px}
svg .lab{fill:var(--fg);font-weight:600}
.legend{display:flex;flex-wrap:wrap;gap:.4rem 1.1rem;font-size:.95rem;color:var(--fg);margin-top:.4rem}
.legend span{display:inline-flex;align-items:center;gap:.4rem}
.sw{width:14px;height:14px;border-radius:3px;display:inline-block}
.tip{position:absolute;pointer-events:none;background:var(--tipbg);color:var(--tipfg);font-family:var(--ui);font-size:.9rem;line-height:1.3;padding:.35rem .55rem;border-radius:4px;white-space:nowrap;z-index:5;transform:translate(-50%,-115%)}
.tbl{overflow-x:auto} table{border-collapse:collapse;font-family:var(--ui);font-size:.98rem;width:100%;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:.3rem .5rem;border-bottom:1px solid var(--rule)} td.n,th.n{text-align:right}
details{font-family:var(--ui);margin-top:.5rem} summary{cursor:pointer;color:var(--muted)}
a{color:var(--acc)} a:focus-visible,summary:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.foot{font-family:var(--ui);font-size:.95rem;color:var(--muted);border-top:1px solid var(--rule);margin-top:2.5rem;padding-top:.8rem}
@media (max-width:520px){body{font-size:17px}}
</style>"""

FUENTES_TIPO = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Literata:opsz,wght@7..72,400;7..72,600;7..72,800'
                '&family=Barlow+Semi+Condensed:wght@400;500;600&display=swap">')

COLORES = {'PP': '#1d84ce', 'PSOE': '#e30613', 'VOX': '#5ac035', 'SUMAR': '#a2275f', 'CS': '#eb6109', 'UPYD': '#e5007d', 'ERC': '#f5b324',
           'JUNTS': '#20c0b2', 'PNV': '#2b8a3e', 'BILDU': '#a5c400', 'BNG': '#7ab8e6', 'CC': '#f7d417', 'UCD': '#e07b22', 'CDS': '#7e57c2',
           'OTROS': '#9a9a9a'}


def leyenda(items):
    """items: [(familia o color, texto)]"""
    out = ''.join(f'<span><i class="sw" style="background:{COLORES.get(c, c)}"></i>{t}</span>' for c, t in items)
    return f'<div class="legend">{out}</div>'


def figura(id_, titulo, sub, fuente, ley=None, tabla=True):
    t = f'<details><summary>Ver los datos en tabla</summary><div class="tbl" id="{id_}-tbl"></div></details>' if tabla else ''
    return (f'<figure>\n<figcaption><span class="t">{titulo}</span><span class="s">{sub}</span></figcaption>\n'
            f'<div class="chart" id="{id_}"></div>\n{leyenda(ley) if ley else ""}\n<div class="src">{fuente}</div>\n{t}\n</figure>')


def escribir():
    datos = json.load(open(os.path.join(AQUI, 'datos.json'), encoding='utf-8'))
    lib = open(os.path.join(AQUI, 'graficos.js'), encoding='utf-8').read()
    for p in PIEZAS_HISTORIA:
        cuerpo = p['cuerpo'](figura)
        html = (f'<title>{p["corto"]}</title>\n{FUENTES_TIPO}\n{CSS}\n<main>\n'
                f'<span class="draft">Borrador para revisión · no publicado</span>\n'
                f'<h1>{p["titulo"]}</h1>\n<p class="dek">{p["dek"]}</p>\n'
                f'<div class="byline">Nacho G. del Álamo · 8 de octubre de 2026</div>\n'
                f'{cuerpo}\n<div class="foot">{p["pie"]}</div>\n</main>\n'
                f'<script>\n{lib}\nconst D={json.dumps({k: datos[k] for k in p["datos"]}, ensure_ascii=False)};\nconst EL={json.dumps(datos["elecciones"])};\n'
                f'{p["js"]}\n</script>\n')
        open(os.path.join(SRC, p['slug'] + '.html'), 'w', encoding='utf-8').write(html)
        print('escrita', p['slug'])
    # imágenes para redes: titular, serie, entradilla y la ilustración o la miniatura del primer gráfico
    json.dump([{'archivo': f'actualidad-{p["slug"]}.jpg', 'serie': 'Historia electoral', 'titular': p['titulo'], 'subtitulo': p['descripcion'],
                'foto': (p.get('foto') or {}).get('src') or f'img/actualidad/{p["slug"]}.jpg'} for p in PIEZAS_HISTORIA],
              open(os.path.join(AQUI, 'compartir.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    escribir()
