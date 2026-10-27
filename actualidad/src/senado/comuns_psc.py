"""Cifras de la pieza comuns-psc-senado-girona-lleida-tarragona-29n: Comuns (Frente Amplio) se retira del Senado en Girona,
Lleida y Tarragona y el PP, por su pacto con Vox, en Girona y Tarragona.
Votos por candidato del Senado de 2023 (senado_2023.csv) y esos votos movidos con el cambio de cada partido en el Congreso
entre 2023 (../sistema/simulador.json) y el modelo de encuestas (previsiones/datos/publico/escenario-base.json).
Uso: python3 actualidad/src/senado/comuns_psc.py  → escribe cifras_comuns_psc.json"""
import collections, csv, json, pathlib

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
S23 = json.loads((AQUI.parent / 'sistema' / 'simulador.json').read_text())['elecciones']['2023_07']
MOD = json.loads((RAIZ / 'previsiones/datos/publico/escenario-base.json').read_text())['provincias']
META = json.loads((RAIZ / 'previsiones/datos/publico/meta.json').read_text())
FAM = {'PSC': 'PSOE', 'JxCAT - JUNTS': 'Junts', 'ERC-ESQUERRES PER LA INDEPENDÈNCIA': 'ERC', 'PP': 'PP', 'VOX': 'Vox', 'SUMAR - ECP': 'Sumar'}
PROV = {'17': 'Girona', '25': 'Lleida', '43': 'Tarragona'}
SIN_PP = {'17', '43'}   # el PP no se presenta (pacto con Vox del 26-10-2026)

votos = collections.defaultdict(lambda: collections.defaultdict(list))
for r in csv.DictReader(open(AQUI / 'senado_2023.csv', encoding='utf-8')):
    if r['prov'] in PROV and r['siglas'] in FAM:
        votos[r['prov']][FAM[r['siglas']]].append(int(r['votos']))

def reparto(v):
    """Cuatro senadores, tres votos por elector: el primero saca tres y el segundo, uno."""
    o = sorted(v, key=lambda k: -v[k])
    return {o[0]: 3, o[1]: 1}

out = dict(modelo=META['version'], provincias={})
for p, nombre in PROV.items():
    base = {k: sum(x) / len(x) for k, x in votos[p].items()}
    c23 = {k: S23[p]['v'][k] / S23[p]['validos'] for k in base}
    m26 = {l['lista']: l['voto'][1] / 100 for l in MOD[p]['listas']}
    esc = {'2023': base, 'encuestas': {k: base[k] * m26[k] / c23[k] for k in base}}
    r = dict(nombre=nombre, sin_pp=p in SIN_PP)
    for e, v in esc.items():
        sin = dict(v)
        con = {k: x for k, x in v.items() if k != 'Sumar'}
        con['PSOE'] += v['Sumar']                      # transferencia completa de Comuns al PSC
        if p in SIN_PP:
            con['Vox'] += con.pop('PP')                # transferencia completa del PP a Vox
        solo = dict(v)                                 # solo el pacto de PP y Vox, Comuns se presenta
        if p in SIN_PP:
            solo['Vox'] += solo.pop('PP')
        r[e] = dict(votos={k: round(x) for k, x in v.items()},
                    sin_pactos=reparto(sin), solo_pp_vox=reparto(solo), con_pactos=reparto(con),
                    con_pactos_votos={k: round(x) for k, x in con.items()},
                    # Parte de los votos de Comuns que necesita el PSC para quedar primero (frente al mejor rival con los pactos)
                    umbral_comuns=round(max(0, max(x for k, x in con.items() if k != 'PSOE') - v['PSOE']) / v['Sumar'], 3))
        if p in SIN_PP:
            r[e]['umbral_pp_vox_segundo'] = round((max(v['ERC'], v['Junts']) - v['Vox']) / v['PP'], 3)
            r[e]['umbral_pp_vox_primero_sin_comuns'] = round((v['PSOE'] - v['Vox']) / v['PP'], 3)
    out['provincias'][p] = r
for e in ('2023', 'encuestas'):
    out['total_' + e] = {c: dict(sum((collections.Counter(r[e][c]) for r in out['provincias'].values()), collections.Counter()))
                         for c in ('sin_pactos', 'solo_pp_vox', 'con_pactos')}
(AQUI / 'cifras_comuns_psc.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps(out, ensure_ascii=False, indent=1))
