"""Prepara resumenes/datos/encuestas_autonomicas_2015_2026.csv para encuestas_fallos.py (26-11-2026).

Lee las encuestas autonómicas de Electográfica y las fichas de Wikipedia que descargó previsiones/src/error_encuestas.py
(en /mnt/project-files/previsiones/encuestas/autonomicas/ y /mnt/project-files/tendencias/comunidades/wiki/). Para cada
elección autonómica desde 2015, la última encuesta de cada empresa publicada entre 20 y 6 días antes de la votación (sin
sondeos internos de partidos) y el resultado de PP, PSOE, Vox y Cs sobre votos válidos de la ficha.
En algunas entradas de 2015 a 2021 la extracción de Electográfica guardó solo uno o dos partidos. Si a una encuesta le falta
un partido que sacó al menos el 3 %, se relee la estimación completa de la descripción de su página (formato «PP 9.9% (13),
PSC 12.1% (16)…») y se guarda en datos/encuestas_autonomicas_releidas.json, para que volver a ejecutar no dependa de la red.
Uso, desde la raíz: python3 actualidad/src/resumenes/encuestas_fallos_preparar.py
"""
import json, glob, re, html, pathlib, subprocess, sys, pandas as pd
from datetime import timedelta
RAIZ = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / 'previsiones/src'))
import error_encuestas as EE
R = EE.resultados()
WF = {}
for f in glob.glob(str(EE.WIKI / '*.txt')):
    nm = pathlib.Path(f).stem
    y = re.search(r'(\d{4})$', nm)
    if not y or int(y.group(1)) < 2015: continue
    cl = next((v for v in EE.CCAA.values() if v in nm), None)
    if cl: WF.setdefault((cl, int(y.group(1))), []).append(nm)
CANON = {'40dB.': '40dB', 'Data10 - Demoscopia y Servicios': 'Data10', 'Demoscopia y Servicios': 'Data10', 'SigmaDos': 'Sigma Dos', 'del CIS · Octubre 2018': 'CIS'}
def casa(e):
    c = (e['ficha'].get('Encuestadora') or '').strip()
    if not c:
        t = e['titulo']
        if re.search(r'interno', t, re.I): return None
        m = re.search(r'(?:Sondeo|Encuesta)\s+(.+?)(?:\s*\(\d+\))?(?::|\s+\d{2}/\d{2}/\d{4}|$)', t)
        c = m.group(1).strip() if m else t
    return CANON.get(c, c)
RELEIDAS = RAIZ / 'actualidad/src/resumenes/datos/encuestas_autonomicas_releidas.json'
REL = json.loads(RELEIDAS.read_text(encoding='utf-8')) if RELEIDAS.exists() else {}
def releer(url):
    """Estimación de voto completa desde la descripción de la página de Electográfica: {etiqueta: %}."""
    if url not in REL:
        s = subprocess.run(['curl', '-s', '-m', '30', url], capture_output=True, text=True).stdout
        m = re.search(r'"description":"((?:[^"\\]|\\.)*)"', s)
        t = html.unescape(json.loads('"' + m.group(1) + '"')) if m else ''
        t = t.split('Resultados de la encuesta:')[-1].split('voto (%)')[0].split('Estimación')[0]
        REL[url] = {k.strip(): float(v.replace(',', '.')) for k, v in re.findall(r"([^,%()]+?)\s+([\d]+(?:[.,]\d+)?)%", t)}
    return REL[url]
def familias(voto, cl):
    fam = {}
    for p, v in voto.items():
        k = EE.familia(p, cl)
        if k and v: fam[k] = fam.get(k, 0) + v
    return fam
raw = json.load(open(EE.ENC_AUT))
rows = []
for e in raw:
    amb = EE.norma(e['ambito'].split('(')[0].split('▪')[0].split(',')[0])
    cl = next((v for k, v in EE.CCAA.items() if EE.norma(k) == amb), None)
    if not cl or 'Generales' in e['titulo'] or 'Municip' in e['ambito']: continue
    c = casa(e)
    if not c: continue
    fam = familias(e['voto'], cl)
    rows.append(dict(ccaa=cl, pub=pd.Timestamp(e['publicado'][:10]), casa=c, cliente=e['ficha'].get('Cliente') or '', url=e['url'], **fam))
d = pd.DataFrame(rows)
NOM = {'Vasco': 'País Vasco', 'Cortes Valencianas': 'Comunitat Valenciana', 'Islas Baleares': 'Illes Balears'}
out = []
for (cl, dia), res in sorted(R.items(), key=lambda t: t[0][1]):
    D = pd.Timestamp(dia)
    x = d[(d.ccaa == cl) & (d.pub >= D - timedelta(days=20)) & (d.pub <= D - timedelta(days=6))].sort_values(['pub', 'url'], kind='stable')
    x = x.groupby('casa').tail(1).copy()
    if not len(x): continue
    deben = [k for k in ['PP', 'PSOE', 'VOX', 'CS'] if res.get(k, 0) >= 3]
    for i, r in x.iterrows():
        if any(k not in x or pd.isna(r.get(k)) for k in deben):
            for k, v in familias(releer(r.url), cl).items(): x.loc[i, k] = v
    lab = f'{NOM.get(cl, cl)} {dia.year}'
    out.append(dict(eleccion=lab, fecha=str(dia), tipo='resultado', encuestadora='', cliente='', publicado='',
                    fuente='https://es.wikipedia.org/wiki/' + WF[(cl, dia.year)][0].replace(' ', '_'),
                    **{k: round(res[k], 2) if k in res else '' for k in ['PP', 'PSOE', 'VOX', 'CS']}))
    for r in x.itertuples():
        out.append(dict(eleccion=lab, fecha=str(dia), tipo='encuesta', encuestadora=r.casa, cliente=r.cliente, publicado=str(r.pub.date()), fuente=r.url,
                        **{k: (getattr(r, k) if k in x and pd.notna(getattr(r, k)) else '') for k in ['PP', 'PSOE', 'VOX', 'CS']}))
RELEIDAS.write_text(json.dumps(REL, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')
o = pd.DataFrame(out)
o.to_csv(RAIZ / 'actualidad/src/resumenes/datos/encuestas_autonomicas_2015_2026.csv', index=False)
e = o[o.tipo == 'encuesta']
for el, g in e.groupby('eleccion', sort=False): print(el, len(g), '|', ', '.join(sorted(g.encuestadora)))
