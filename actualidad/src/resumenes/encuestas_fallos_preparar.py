"""Prepara resumenes/datos/encuestas_autonomicas_2015_2026.csv para encuestas_fallos.py (26-11-2026).

Lee las encuestas autonómicas de Electográfica y las fichas de Wikipedia que descargó previsiones/src/error_encuestas.py
(en /mnt/project-files/previsiones/encuestas/autonomicas/ y /mnt/project-files/tendencias/comunidades/wiki/). Para cada
elección autonómica desde 2015, la última encuesta de cada empresa publicada entre 20 y 6 días antes de la votación (sin
sondeos internos de partidos) y el resultado de PP, PSOE, Vox y Cs sobre votos válidos de la ficha.
Uso, desde la raíz: python3 actualidad/src/resumenes/encuestas_fallos_preparar.py
"""
import json, glob, re, pathlib, sys, pandas as pd
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
raw = json.load(open(EE.ENC_AUT))
rows = []
for e in raw:
    amb = EE.norma(e['ambito'].split('(')[0].split('▪')[0].split(',')[0])
    cl = next((v for k, v in EE.CCAA.items() if EE.norma(k) == amb), None)
    if not cl or 'Generales' in e['titulo'] or 'Municip' in e['ambito']: continue
    c = casa(e)
    if not c: continue
    fam = {}
    for p, v in e['voto'].items():
        k = EE.familia(p, cl)
        if k and v: fam[k] = fam.get(k, 0) + v
    rows.append(dict(ccaa=cl, pub=pd.Timestamp(e['publicado'][:10]), casa=c, cliente=e['ficha'].get('Cliente') or '', url=e['url'], **fam))
d = pd.DataFrame(rows)
NOM = {'Vasco': 'País Vasco', 'Cortes Valencianas': 'Comunitat Valenciana', 'Islas Baleares': 'Illes Balears'}
out = []
for (cl, dia), res in sorted(R.items(), key=lambda t: t[0][1]):
    D = pd.Timestamp(dia)
    x = d[(d.ccaa == cl) & (d.pub >= D - timedelta(days=20)) & (d.pub <= D - timedelta(days=6))].sort_values(['pub', 'url'], kind='stable')
    x = x.groupby('casa').tail(1)
    if not len(x): continue
    lab = f'{NOM.get(cl, cl)} {dia.year}'
    out.append(dict(eleccion=lab, fecha=str(dia), tipo='resultado', encuestadora='', cliente='', publicado='',
                    fuente='https://es.wikipedia.org/wiki/' + WF[(cl, dia.year)][0].replace(' ', '_'),
                    **{k: round(res[k], 2) if k in res else '' for k in ['PP', 'PSOE', 'VOX', 'CS']}))
    for r in x.itertuples():
        out.append(dict(eleccion=lab, fecha=str(dia), tipo='encuesta', encuestadora=r.casa, cliente=r.cliente, publicado=str(r.pub.date()), fuente=r.url,
                        **{k: (getattr(r, k) if k in x and pd.notna(getattr(r, k)) else '') for k in ['PP', 'PSOE', 'VOX', 'CS']}))
o = pd.DataFrame(out)
o.to_csv(RAIZ / 'actualidad/src/resumenes/datos/encuestas_autonomicas_2015_2026.csv', index=False)
e = o[o.tipo == 'encuesta']
for el, g in e.groupby('eleccion', sort=False): print(el, len(g), '|', ', '.join(sorted(g.encuestadora)))
