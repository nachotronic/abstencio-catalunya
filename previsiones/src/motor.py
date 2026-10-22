"""Motor del PROTOTIPO de previsiones: genera los artefactos versionados que lee /previsiones/.

ATENCIÓN: las cifras son FICTICIAS. Parten de los votos reales de 2023 por provincia, pero el «desplazamiento»
de cada partido es un número aleatorio con semilla fija, no una estimación. Sirven para diseñar la web y probar
el reparto, no para publicar. El modelo de verdad (fases 4 y 5 del plan) sustituirá `estimacion_ficticia()`.

Uso, desde la raíz del repositorio:  python3 previsiones/src/motor.py
Estimación interna desde encuestas (v1, no se publica):  python3 previsiones/src/motor.py --encuestas <media-encuestas.json>
Escribe previsiones/datos/<VERSION>/: meta.json, base.json, provincias.json y un fichero por escenario.
"""
import json, math, pathlib, sys
from datetime import date

import numpy as np

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
from reglas import ESCANOS_2026, circunscripciones_senado, dhondt, senado_limitado  # noqa: E402

VERSION = 'v0-ficticio'
SEMILLA = 20261129
N_SIM = 2000
MAYORIA = 176
SIM = json.load(open(RAIZ / 'actualidad/src/sistema/simulador.json'))
NOMBRES = SIM['provincias']
CCAA = {c: s.split() for c, s in SIM['ccaa'].items()}
BASE = SIM['elecciones']['2023_07']
# Listas que entran en el reparto. «Otros» agrupa listas distintas y no puede ganar escaños como una sola.
LISTAS = ['PP', 'PSOE', 'Vox', 'Sumar', 'ERC', 'Junts', 'EH Bildu', 'PNV', 'BNG', 'CC', 'UPN', 'CUP', 'Nueva Canarias', 'PACMA']
# Peso (ficticio) de cada isla en el voto de su provincia, solo para repartir los senadores insulares
PESO_ISLA = {'07M': .80, '07N': .08, '07I': .11, '07F': .01, '35G': .78, '35L': .13, '35F': .09,
             '38T': .87, '38P': .08, '38G': .02, '38H': .03}
# Senadores de designación autonómica: FICTICIOS. En el modelo real, la composición vigente de cada parlamento.
DESIGNADOS = {'PP': 27, 'PSOE': 20, 'Vox': 3, 'Sumar': 1, 'ERC': 2, 'Junts': 1, 'EH Bildu': 1, 'PNV': 2}
BLOQUES = [  # sumas aritméticas, no coaliciones previstas
    ('PP + Vox', ['PP', 'Vox']),
    ('PP + Vox + UPN + CC', ['PP', 'Vox', 'UPN', 'CC']),
    ('PSOE + Sumar', ['PSOE', 'Sumar']),
    ('PSOE + Sumar + ERC + Junts + EH Bildu + PNV + BNG + CC', ['PSOE', 'Sumar', 'ERC', 'Junts', 'EH Bildu', 'PNV', 'BNG', 'CC']),
]
ESCENARIOS = [  # id, título, supuesto explícito, {lista: puntos de voto nacional}, multiplicador de incertidumbre
    ('base', 'Escenario central', 'Estimación central ficticia, sin supuestos añadidos.', {}, 1.0),
    ('pp2', 'PP +2 puntos', 'El PP gana 2 puntos de voto en toda España, restados al resto en proporción a su voto.', {'PP': 2}, 1.0),
    ('psoe2', 'PSOE +2 puntos', 'El PSOE gana 2 puntos de voto en toda España, restados al resto en proporción.', {'PSOE': 2}, 1.0),
    ('vox2', 'Vox +2 puntos', 'Vox gana 2 puntos de voto en toda España, restados al resto en proporción.', {'Vox': 2}, 1.0),
    ('sumar2', 'Sumar +2 puntos', 'Sumar gana 2 puntos de voto en toda España, restados al resto en proporción.', {'Sumar': 2}, 1.0),
    ('incierto', 'Doble incertidumbre', 'Misma estimación central, con el doble de error nacional y provincial.', {}, 2.0),
]
SIGMA_NAC, SIGMA_PROV = 0.06, 0.08   # error relativo (ficticio) del voto de cada lista, nacional y provincial
COMPOSICIONAL = False


def matriz_base():
    """Cuotas de 2023 por provincia (sobre válidos, blanco incluido) para LISTAS, más la fila de válidos."""
    provs = sorted(BASE)
    cuotas = np.array([[BASE[p]['v'].get(k, 0) / BASE[p]['validos'] for k in LISTAS] for p in provs])
    validos = np.array([BASE[p]['validos'] for p in provs], float)
    return provs, cuotas, validos


def estimacion_ficticia(cuotas, rng):
    """Desplazamiento aleatorio (±15 % relativo) de cada lista en toda España. NO es una estimación."""
    factor = np.exp(rng.normal(0, 0.12, len(LISTAS)))
    return cuotas * factor


def aplica_escenario(cuotas, validos, puntos):
    """Suma `puntos` al voto nacional de una lista restándolo al resto en proporción, igual en cada provincia."""
    c = cuotas.copy()
    for k, pts in puntos.items():
        j = LISTAS.index(k)
        nac = (c * validos[:, None]).sum(0) / validos.sum()
        objetivo = nac[j] + pts / 100
        c[:, j] *= objetivo / nac[j]
        otros = [i for i in range(len(LISTAS)) if i != j]
        resto_antes = (nac[otros]).sum()
        c[:, otros] *= (resto_antes - pts / 100) / resto_antes
    return c


def simula(cuotas, validos, provs, sigma, rng):
    """N_SIM simulaciones: error nacional común a todas las provincias y error provincial independiente."""
    n, P, L = N_SIM, len(provs), len(LISTAS)
    nac = rng.normal(0, SIGMA_NAC * sigma, (n, 1, L))
    prov = rng.normal(0, SIGMA_PROV * sigma, (n, P, L))
    sims = cuotas[None] * np.exp(nac + prov)
    tope = cuotas.sum(1)[None, :, None]
    if COMPOSICIONAL:   # v1: el error reparte voto entre listas sin cambiar el total de cada provincia
        sims = sims / sims.sum(2, keepdims=True) * tope
    else:   # el total de las listas no puede pasar del voto a candidaturas de 2023 (el blanco y «Otros» se mantienen)
        sims = np.where(sims.sum(2, keepdims=True) > tope, sims / sims.sum(2, keepdims=True) * tope, sims)
    part = rng.normal(0, 0.025 * sigma, (n, 1))     # participación: error nacional ficticio
    votos_validos = validos[None] * (1 + part)
    return sims, votos_validos


def percentiles(x, eje=0):
    q = np.percentile(x, [2.5, 10, 50, 90, 97.5], axis=eje)
    return [round(float(v), 2) for v in q] if q.ndim == 1 else q


def reparto_medio(medias, total):
    """Escaños medios redondeados por restos mayores para que sumen `total` (solo para dibujar el hemiciclo)."""
    base = np.floor(medias).astype(int)
    for j in np.argsort(-(medias - base))[:total - base.sum()]:
        base[j] += 1
    return {k: int(v) for k, v in zip(LISTAS, base) if v}


def corre(cuotas, validos, provs, sigma, rng, circ_sen):
    sims, vv = simula(cuotas, validos, provs, sigma, rng)
    n, P, L = sims.shape
    cong = np.zeros((n, P, L), int)
    sen = np.zeros((n, len(circ_sen), L), int)
    idx = {p: i for i, p in enumerate(provs)}
    for s in range(n):
        for i, p in enumerate(provs):
            votos = dict(zip(LISTAS, sims[s, i] * vv[s, i]))
            r = dhondt(votos, ESCANOS_2026[p], vv[s, i])
            cong[s, i] = [r[k] for k in LISTAS]
        for c, (cod, _, p, nsen, ve) in enumerate(circ_sen):
            ruido = rng.normal(0, 0.05, L) if cod in PESO_ISLA else 0
            votos = dict(zip(LISTAS, sims[s, idx[p]] * np.exp(ruido)))
            r = senado_limitado(votos, nsen, ve)
            sen[s, c] = [r[k] for k in LISTAS]
    # voto nacional de cada lista por simulación (%)
    pct_nac = (sims * vv[:, :, None]).sum(1) / vv.sum(1, keepdims=True) * 100
    tot_cong, tot_sen = cong.sum(1), sen.sum(1)
    out = {'hemiciclo': {'congreso': reparto_medio(tot_cong.mean(0), 350),
                         'senado': reparto_medio(tot_sen.mean(0), len(circ_sen) and int(tot_sen[0].sum()))},
           'listas': [], 'bloques': [], 'participacion': None, 'provincias': {}, 'senado_circ': {}}
    for j, k in enumerate(LISTAS):
        lo = int(tot_cong[:, j].min())
        dist = np.bincount(tot_cong[:, j] - lo)
        out['listas'].append({
            'lista': k, 'voto': percentiles(pct_nac[:, j]), 'escanos': percentiles(tot_cong[:, j]),
            'escanos_dist': {'desde': lo, 'p': [round(float(v) / n, 4) for v in dist]},
            'senado': percentiles(tot_sen[:, j]), 'designados': DESIGNADOS.get(k, 0)})
    for nom, ks in BLOQUES:
        js = [LISTAS.index(k) for k in ks]
        suma = tot_cong[:, js].sum(1)
        out['bloques'].append({'bloque': nom, 'listas': ks, 'escanos': percentiles(suma),
                               'p_mayoria': round(float((suma >= MAYORIA).mean()), 3)})
    base_part = 66.6   # participación ficticia de partida (no es la de 2023 ni una estimación)
    out['participacion'] = percentiles(base_part * vv.sum(1) / validos.sum())
    for i, p in enumerate(provs):
        pct = sims[:, i] * 100
        q = np.percentile(pct, [10, 50, 90], axis=0)
        qe = np.percentile(cong[:, i], [10, 50, 90], axis=0)
        gana = np.bincount(pct.argmax(1), minlength=L) / n
        out['provincias'][p] = {
            'escanos_total': ESCANOS_2026[p],
            'listas': [{'lista': k, 'voto': [round(float(q[t, j]), 1) for t in range(3)],
                        'escanos': [int(qe[t, j]) for t in range(3)], 'p_primera': round(float(gana[j]), 3)}
                       for j, k in enumerate(LISTAS) if q[2, j] >= 0.5]}
    for nom, ps in CCAA.items():   # agregación desde las mismas simulaciones: CCAA = suma de sus provincias
        js = [idx[p] for p in ps]
        w = vv[:, js]
        pct = (sims[:, js] * w[:, :, None]).sum(1) / w.sum(1, keepdims=True) * 100
        esc = cong[:, js].sum(1)
        q = np.percentile(pct, [10, 50, 90], axis=0)
        qe = np.percentile(esc, [10, 50, 90], axis=0)
        gana = np.bincount(pct.argmax(1), minlength=L) / n
        out.setdefault('ccaa', {})[nom] = {
            'escanos_total': sum(ESCANOS_2026[p] for p in ps),
            'listas': [{'lista': k, 'voto': [round(float(q[t, j]), 1) for t in range(3)],
                        'escanos': [int(qe[t, j]) for t in range(3)], 'p_primera': round(float(gana[j]), 3)}
                       for j, k in enumerate(LISTAS) if q[2, j] >= 0.5]}
    for c, (cod, nom, p, nsen, _) in enumerate(circ_sen):
        med = np.median(sen[:, c], axis=0)
        out['senado_circ'][cod] = {'nombre': nom, 'provincia': p, 'senadores': nsen,
                                   'mediana': {k: int(med[j]) for j, k in enumerate(LISTAS) if med[j] > 0}}
    return out


def observado_2023():
    """Dato observado: voto y escaños oficiales de 2023 por provincia, con el mismo reparto (sirve de control)."""
    from reglas import ESCANOS_2023
    out, tot = {}, {k: 0 for k in LISTAS}
    for p, r in BASE.items():
        e = dhondt({k: r['v'].get(k, 0) for k in LISTAS}, ESCANOS_2023[p], r['validos'])
        for k in LISTAS:
            tot[k] += e[k]
        out[p] = {'validos': r['validos'], 'voto': {k: round(r['v'][k] / r['validos'] * 100, 2) for k in LISTAS if k in r['v']},
                  'escanos': {k: v for k, v in e.items() if v}}
    ccaa = {}
    for nom, ps in CCAA.items():
        val = sum(BASE[p]['validos'] for p in ps)
        esc = {}
        for p in ps:
            for k, v in out[p]['escanos'].items():
                esc[k] = esc.get(k, 0) + v
        ccaa[nom] = {'validos': val, 'escanos': esc,
                     'voto': {k: round(sum(BASE[p]['v'].get(k, 0) for p in ps) / val * 100, 2) for k in LISTAS
                              if any(k in BASE[p]['v'] for p in ps)}}
    validos = sum(r['validos'] for r in BASE.values())
    voto = {k: round(sum(r['v'].get(k, 0) for r in BASE.values()) / validos * 100, 2) for k in LISTAS}
    return {'provincias': out, 'ccaa': ccaa, 'escanos': {k: v for k, v in tot.items() if v}, 'voto': voto}


# ---------------------------------------------------------------------------------------------------------
# v1: estimación desde la media de encuestas (INTERNA: no se publica sin el visto bueno de Nacho)
# ---------------------------------------------------------------------------------------------------------
LISTAS_V1 = ['PP', 'PSOE', 'Vox', 'Sumar', 'Podemos', 'SALF', 'ERC', 'Junts', 'EH Bildu', 'PNV', 'BNG', 'CC', 'UPN',
             'CUP', 'Aliança', 'Nueva Canarias', 'PACMA']
DE_ENCUESTA = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'SUMAR': 'Sumar', 'PODEMOS': 'Podemos', 'SALF': 'SALF',
               'ERC': 'ERC', 'JUNTS': 'Junts', 'BILDU': 'EH Bildu', 'PNV': 'PNV', 'BNG': 'BNG', 'CC': 'CC', 'UPN': 'UPN',
               'ALIANCA': 'Aliança'}
BLOQUES_V1 = [
    ('PP + Vox', ['PP', 'Vox']),
    ('PP + Vox + SALF + UPN + CC', ['PP', 'Vox', 'SALF', 'UPN', 'CC']),
    ('PSOE + Sumar + Podemos', ['PSOE', 'Sumar', 'Podemos']),
    ('PSOE + Sumar + Podemos + ERC + Junts + EH Bildu + PNV + BNG + CC',
     ['PSOE', 'Sumar', 'Podemos', 'ERC', 'Junts', 'EH Bildu', 'PNV', 'BNG', 'CC']),
]
# Aliança Catalana, Parlament 2024 (voto sobre válidos por provincia; Cataluña 3,77 %). Fuente: resultados oficiales.
ALIANCA_2024 = {'08': 2.87, '17': 9.03, '25': 7.78, '43': 3.51}
SIGMA_MAX = 0.30   # tope del error relativo de las listas pequeñas (con c·raíz(voto) saldría ±50-100 %)
DERIVA = 1.25   # el error histórico se mide 5 días antes; a cinco semanas de la elección se amplía un 25 %
BASE2026 = pathlib.Path('/mnt/project-files/previsiones/base/base2026_secciones.csv')
EUROPEAS2024 = pathlib.Path('/mnt/project-files/previsiones/base/europeas2024_secciones.csv')
# Señal de las europeas de 2024 (senal_local.py): en 2015 y 2019, corregir la base con la fuerza relativa de cada
# provincia en las europeas intermedias frente a las generales anteriores, elevada a 0,5, redujo un tercio el error
# del reparto entre provincias (2,9 → 1,9 y 2,8 → 1,9 puntos). Se aplica a los partidos de ámbito estatal.
ALFA_EUROPEAS = 0.5
SENAL_EUROPEAS = {'PP': ['PP'], 'PSOE': ['PSOE'], 'Vox': ['VOX'], 'Sumar': ['SUMAR', 'PODEMOS'], 'Podemos': ['SUMAR', 'PODEMOS']}


def senal_europeas(provs, alfa=ALFA_EUROPEAS):
    """Por lista y provincia: el factor (cuota provincial / nacional en europeas 2024) / (lo mismo en generales
    2023), elevado a alfa, y la fuerza relativa en las europeas sola. Sumar y Podemos usan su espacio conjunto,
    porque en 2023 fueron juntos."""
    import pandas as pd
    e = pd.read_csv(EUROPEAS2024, dtype={'tract_code': str})
    g = pd.read_csv(BASE2026, dtype={'tract_code': str})
    g['PODEMOS'] = 0   # en 2023, Podemos dentro de SUMAR
    factor, fuerza = {}, {}
    for lista, cols in SENAL_EUROPEAS.items():
        rel = []
        for d in (e, g):
            x = d.assign(v=d[cols].sum(axis=1)).groupby(d.tract_code.str[:2])[['v', 'validos']].sum()
            rel.append(((x.v / x.validos) / (x.v.sum() / x.validos.sum())).reindex(provs).fillna(0).values)
        ok = (rel[0] > 0) & (rel[1] > 0)
        factor[lista] = np.where(ok, (rel[0] / np.where(ok, rel[1], 1)) ** alfa, 1.0)
        fuerza[lista] = rel[0]
    return factor, fuerza


def base_v1():
    """Cuotas de partida por provincia para LISTAS_V1: 2023 con Sumar repartido entre Sumar (FA) y Podemos según
    las europeas de 2024 (base2026.py), e índices provinciales de dónde vota SALF (europeas 2024) y Aliança (2024)."""
    import pandas as pd
    b = pd.read_csv(BASE2026, dtype={'tract_code': str})
    b['prov'] = b.tract_code.str[:2]
    g = b.assign(salf=b.indice_salf * b.validos).groupby('prov')[['PODEMOS_2023', 'SUMAR_FA_2023', 'salf', 'validos']].sum()
    cuota_pod = g.PODEMOS_2023 / (g.PODEMOS_2023 + g.SUMAR_FA_2023)
    ind_salf = g.salf / g.validos
    provs = sorted(BASE)
    validos = np.array([BASE[p]['validos'] for p in provs], float)
    cuotas = np.zeros((len(provs), len(LISTAS_V1)))
    for i, p in enumerate(provs):
        v, val = BASE[p]['v'], BASE[p]['validos']
        for j, k in enumerate(LISTAS_V1):
            cuotas[i, j] = v.get(k, 0) / val
        s = v.get('Sumar', 0) / val
        cuotas[i, LISTAS_V1.index('Sumar')] = s * (1 - cuota_pod[p])
        cuotas[i, LISTAS_V1.index('Podemos')] = s * cuota_pod[p]
    factor, fuerza = senal_europeas(provs)
    for k, f in factor.items():
        j = LISTAS_V1.index(k)
        cuotas[:, j] *= f
        # sin lista en 2023 en la provincia (Vox en Santa Cruz de Tenerife, candidatura anulada): parte de su voto
        # nacional de 2023 por su fuerza relativa en las europeas
        nac = (cuotas[:, j] * validos).sum() / validos.sum()
        cuotas[:, j] = np.where(cuotas[:, j] > 0, cuotas[:, j], nac * fuerza[k])
    indices = {'SALF': np.array([ind_salf[p] for p in provs]),
               'Aliança': np.array([ALIANCA_2024.get(p, 0) / 3.77 for p in provs])}
    return provs, cuotas, validos, indices


def ajusta_a_encuestas(cuotas, validos, indices, objetivo, iter=50):
    """Subida o bajada proporcional de cada lista en todas las provincias hasta clavar su voto nacional de la media.
    SALF y Aliança no tienen voto en 2023: parten de su índice provincial. Las listas sin encuesta (CUP, Nueva
    Canarias, PACMA) mantienen su voto de 2023; Aliança, sin cifra en la media, su voto del Parlament 2024."""
    c = cuotas.copy()
    peso = validos / validos.sum()
    if 'Aliança' not in objetivo:   # sin cifra en la media: su 3,77 % del voto catalán, expresado sobre España
        objetivo = {**objetivo, 'Aliança': 0.0377 * peso[indices['Aliança'] > 0].sum()}
    for k, ind in indices.items():
        c[:, LISTAS_V1.index(k)] = ind * objetivo.get(k, 0)
    for _ in range(iter):
        for k, t in objetivo.items():
            j = LISTAS_V1.index(k)
            nac = (c[:, j] * peso).sum()
            if nac > 0:
                c[:, j] *= t / nac
        tope = 0.985   # blanco y listas menores ocupan al menos un 1,5 % en cada provincia
        fila = c.sum(1, keepdims=True)
        c = np.where(fila > tope, c / fila * tope, c)
    return c


def sigma_v1(cuotas_nac, c_error):
    """Error relativo nacional de cada lista: c·raíz(voto en puntos) del error histórico, ampliado por la deriva."""
    pts = np.maximum(cuotas_nac * 100, 0.3)
    return np.minimum(DERIVA * c_error * np.sqrt(pts) / pts, SIGMA_MAX)


def main_encuestas(fich_media):
    global LISTAS, BLOQUES, SIGMA_NAC, VERSION, COMPOSICIONAL
    COMPOSICIONAL = True
    m = json.load(open(fich_media))
    LISTAS, BLOQUES = LISTAS_V1, BLOQUES_V1
    VERSION = 'v1-encuestas-' + m['fecha'].replace('-', '')
    provs, cuotas, validos, indices = base_v1()
    objetivo = {DE_ENCUESTA[k]: v / 100 for k, v in m['media'].items() if k in DE_ENCUESTA}
    central = ajusta_a_encuestas(cuotas, validos, indices, objetivo)
    nac = (central * validos[:, None]).sum(0) / validos.sum()
    SIGMA_NAC = sigma_v1(nac, m['c_error'])
    circ_sen = circunscripciones_senado(NOMBRES)
    carpeta = pathlib.Path('/mnt/project-files/previsiones/salidas') / VERSION
    carpeta.mkdir(parents=True, exist_ok=True)
    escrito = lambda nom, d: (carpeta / nom).write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
    for cod, tit, sup, puntos, sigma in ESCENARIOS:
        if cod == 'base':
            sup = f"Media de encuestas a {m['fecha']} repartida por provincia con subida proporcional desde 2023."
        r = corre(aplica_escenario(central, validos, puntos), validos, provs, sigma, np.random.default_rng(SEMILLA + 1), circ_sen)
        r.update({'id': cod, 'titulo': tit, 'supuesto': sup})
        escrito(f'escenario-{cod}.json', r)
        print(cod, {l['lista']: l['escanos'][2] for l in r['listas'] if l['escanos'][2]},
              {b['bloque']: b['p_mayoria'] for b in r['bloques']})
    escrito('observado-2023.json', observado_2023())
    escrito('meta.json', {
        'version': VERSION, 'ficticio': False, 'interno': True, 'generado': date.today().isoformat(), 'semilla': SEMILLA,
        'simulaciones': N_SIM, 'aviso': 'Estimación interna sin validar. No publicar sin el visto bueno de Nacho.',
        'media_encuestas': m['media'], 'c_error': m['c_error'], 'sigma_nac': dict(zip(LISTAS, np.round(SIGMA_NAC, 3).tolist())),
        'voto_central': dict(zip(LISTAS, np.round(nac * 100, 2).tolist())),
        'listas': LISTAS, 'provincias': NOMBRES, 'ccaa': CCAA, 'escanos': ESCANOS_2026, 'mayoria': MAYORIA,
        'senado': {'elegidos': sum(c[3] for c in circ_sen), 'designados': sum(DESIGNADOS.values()),
                   'circunscripciones': [{'cod': c[0], 'nombre': c[1], 'provincia': c[2], 'senadores': c[3], 'votos_elector': c[4]}
                                         for c in circ_sen]},
        'escenarios': [{'id': e[0], 'titulo': e[1], 'supuesto': e[2]} for e in ESCENARIOS]})
    print('Escrito en', carpeta)


def main():
    rng = np.random.default_rng(SEMILLA)
    provs, cuotas, validos = matriz_base()
    central = estimacion_ficticia(cuotas, rng)
    circ_sen = circunscripciones_senado(NOMBRES)
    carpeta = RAIZ / 'previsiones' / 'datos' / VERSION
    carpeta.mkdir(parents=True, exist_ok=True)
    escrito = lambda nom, d: (carpeta / nom).write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
    for cod, tit, sup, puntos, sigma in ESCENARIOS:
        r = corre(aplica_escenario(central, validos, puntos), validos, provs, sigma, np.random.default_rng(SEMILLA + 1), circ_sen)
        r.update({'id': cod, 'titulo': tit, 'supuesto': sup})
        escrito(f'escenario-{cod}.json', r)
        print(cod, {l['lista']: l['escanos'][2] for l in r['listas'] if l['escanos'][2]})
    escrito('observado-2023.json', observado_2023())
    escrito('meta.json', {
        'version': VERSION, 'ficticio': True, 'generado': date.today().isoformat(), 'semilla': SEMILLA, 'simulaciones': N_SIM,
        'aviso': 'Datos ficticios para diseñar la web. No son una estimación ni una previsión electoral.',
        'listas': LISTAS, 'provincias': NOMBRES, 'ccaa': CCAA, 'escanos': ESCANOS_2026, 'mayoria': MAYORIA,
        'senado': {'elegidos': sum(c[3] for c in circ_sen), 'designados': sum(DESIGNADOS.values()),
                   'circunscripciones': [{'cod': c[0], 'nombre': c[1], 'provincia': c[2], 'senadores': c[3], 'votos_elector': c[4]}
                                         for c in circ_sen]},
        'escenarios': [{'id': e[0], 'titulo': e[1], 'supuesto': e[2]} for e in ESCENARIOS]})


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--encuestas':   # motor.py --encuestas salidas/media-encuestas-AAAAMMDD.json
        main_encuestas(sys.argv[2])
    else:
        main()
