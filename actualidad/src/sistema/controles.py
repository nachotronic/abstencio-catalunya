"""Controles de las piezas de sistema electoral: cada cifra del texto se recalcula desde cifras.json y el simulador.
Sale con código 1 si alguna no cuadra. Uso: python3 actualidad/src/sistema/controles.py"""
import json, pathlib, re, sys

AQUI = pathlib.Path(__file__).resolve().parent
C = json.load(open(AQUI / 'cifras.json'))
S = json.load(open(AQUI / 'simulador.json'))
P23, P19 = C['2023_07']['provincias'], C['2019_11']['provincias']
par = lambda e, k: next(q for q in C[e]['partidos'] if q['partido'] == k)
mil = lambda v: f'{round(v):,}'.replace(',', '.')
pc = lambda v: f'{v:.1f}'.replace('.', ',')


def reparto(v, n, val, bar, met):
    ok = {p: b for p, b in v.items() if p != 'Otros' and b >= bar * val}
    c = sorted(((b / (d if met == 'dh' else 2 * d - 1), p) for p, b in ok.items() for d in range(1, n + 1)), reverse=True)[:n]
    e = {}
    for _, p in c:
        e[p] = e.get(p, 0) + 1
    return e


def sim(el, modo, bar, met='dh'):
    E, ES = S['elecciones'][el], S['escanos'][el]
    grupos = [[p] for p in E] if modo == 'prov' else [ps.split() for ps in S['ccaa'].values()] if modo == 'ccaa' else [list(E)]
    tot = {}
    for ps in grupos:
        v, val, n = {}, 0, 0
        for p in ps:
            for k, b in E[p]['v'].items():
                v[k] = v.get(k, 0) + b
            val += E[p]['validos']; n += ES[p]
        for k, s in reparto(v, n, val, bar, met).items():
            tot[k] = tot.get(k, 0) + s
    return tot


u3, u0, cc = sim('2023_07', 'unica', .03), sim('2023_07', 'unica', 0), sim('2023_07', 'ccaa', .03)
peq = C['2023_07']['pequenas']
precio = [mil(P23['44']['votos_por_escano']), mil(P23['28']['votos_por_escano']), mil(P23['42']['votos_por_escano']),
          mil(P23['44']['validos']), mil(P23['44']['residentes_por_escano']), mil(P23['42']['residentes_por_escano']),
          mil(P23['28']['residentes_por_escano']), mil(P23['52']['votos_por_escano']), mil(P23['51']['votos_por_escano']),
          mil(P23['28']['validos'] / 38)] + \
         [mil(par('2023_07', k)['votos_por_escano']) for k in ['PP', 'PSOE', 'Vox', 'Sumar', 'PNV', 'EH Bildu', 'Junts', 'BNG']] + \
         [pc(par('2023_07', 'PP')['pct']) + '&nbsp;%', pc(par('2023_07', 'PP')['pct_escanos']) + '&nbsp;%',
          pc(par('2023_07', 'PSOE')['pct']) + '&nbsp;%', pc(par('2023_07', 'PSOE')['pct_escanos']) + '&nbsp;%',
          pc(par('2023_07', 'Vox')['pct_escanos']) + '&nbsp;%', pc(par('2023_07', 'Sumar')['pct_escanos']) + '&nbsp;%',
          mil(par('2019_11', 'Cs')['votos_por_escano']), mil(par('2019_11', 'Más País')['votos_por_escano']),
          mil(C['2015_12']['iu_up_votos']), f"{peq['n']} eligen", f"{peq['escanos']} escaños", pc(100 * peq['escanos'] / 350) + '&nbsp;%',
          pc(peq['pct_residentes']) + '&nbsp;%', pc(peq['partidos']['PP']['pct_voto']) + '&nbsp;%', f"llevó {peq['partidos']['PP']['escanos']} de los 108",
          pc(P23['42']['umbral_efectivo_pct']) + '&nbsp;%', pc(P23['28']['umbral_efectivo_pct']) + '&nbsp;%',
          f"PP ({u3['PP']} escaños), PSOE ({u3['PSOE']}), Vox ({u3['Vox']}) y Sumar ({u3['Sumar']})", f"sumado {u3['PP'] + u3['Vox']} diputados",
          f"escaño a {len(u0)} partidos", f"PACMA ({u0['PACMA']}) y la CUP ({u0['CUP']})", f"quedado en {u0['PP'] + u0['Vox']}",
          f"de 137 a {cc['PP']} escaños", f"de 33 a {cc['Vox']}", f"de 31 a {cc['Sumar']}", f"de 10 a {sim('2019_11', 'unica', .03)['Cs']}",
          f"{C['votos_2023_reparto_2026']['PSOE']} diputados para el PSOE y {C['votos_2023_reparto_2026']['PP']} para el PP"]
assert len(u3) == 4 and min(P23[p]['umbral_efectivo_pct'] for p in P23 if P23[p]['escanos'] == 3) == 17.51
sin = [mil(C['2023_07']['votos_sin_escano']), pc(C['2023_07']['pct_sin_escano']) + '&nbsp;%', mil(C['2023_07']['blancos']),
       mil(C['2019_11']['votos_sin_escano']), pc(C['2019_11']['pct_sin_escano']) + '&nbsp;%',
       mil(par('2023_07', 'PSOE')['votos_sin_escano']), mil(par('2023_07', 'PP')['votos_sin_escano']),
       mil(par('2023_07', 'Sumar')['votos_sin_escano']), mil(par('2023_07', 'Vox')['votos_sin_escano']),
       pc(par('2023_07', 'Sumar')['pct_propio_sin_escano']) + '&nbsp;%', pc(par('2023_07', 'Vox')['pct_propio_sin_escano']) + '&nbsp;%',
       mil(par('2023_07', 'PACMA')['votos']), mil(par('2023_07', 'CUP')['votos']), pc(par('2023_07', 'BNG')['pct_propio_sin_escano']) + '&nbsp;%',
       pc(par('2023_07', 'CC')['pct_propio_sin_escano']) + '&nbsp;%', mil(par('2019_11', 'Cs')['votos_sin_escano']),
       pc(par('2019_11', 'Cs')['pct_propio_sin_escano']) + '&nbsp;%', pc(par('2019_11', 'Más País')['pct_propio_sin_escano']) + '&nbsp;%',
       pc(par('2019_11', 'Unidas Podemos')['pct_propio_sin_escano']) + '&nbsp;%',
       pc(P23['28']['pct_sin_escano']) + '&nbsp;%', pc(P23['44']['pct_sin_escano']) + '&nbsp;%', pc(P23['25']['pct_sin_escano']) + '&nbsp;%',
       pc(P23['42']['pct_sin_escano']) + '&nbsp;%', pc(P23['51']['pct_sin_escano']) + '&nbsp;%', pc(P23['52']['pct_sin_escano']) + '&nbsp;%',
       mil(P23['44']['perdidos_por_partido']['Teruel Existe']), mil(P23['44']['perdidos_por_partido']['Vox']),
       mil(P23['42']['perdidos_por_partido']['Soria ¡Ya!']), mil(P23['24']['perdidos_por_partido']['UPL']), mil(P23['24']['perdidos_por_partido']['Vox']),
       mil(P23['25']['perdidos_por_partido']['PP']), mil(P23['25']['perdidos_por_partido']['Sumar']), mil(P23['25']['perdidos_por_partido']['Vox']),
       f"faltaron {P23['17']['votos_faltan']} para", f"{P23['39']['votos_faltan']} para quitárselo", f"faltaron {P19['21']['votos_faltan']} votos",
       f"En 17 circunscripciones"]
assert sum(r['votos_faltan'] < 1000 for r in P23.values()) == 2 and sum(r['votos_faltan'] < 1000 for r in P19.values()) == 7
assert sum(r['votos_faltan'] < 5000 for r in P23.values()) == 17 == sum(r['votos_faltan'] < 5000 for r in P19.values())
assert sim('2023_07', 'prov', 0) == sim('2023_07', 'prov', .03)   # «quitarla no habría cambiado ningún escaño»
fallos = 0
for f, lista in (('precio-del-escano-29n.html', precio), ('votos-sin-escano-29n.html', sin)):
    t = (AQUI.parent / f).read_text().split('<script>')[0]
    for x in lista:
        if x not in t:
            print('FALLO', f, x); fallos += 1
    print(f, len(lista), 'cifras comprobadas')
sys.exit(1 if fallos else 0)
