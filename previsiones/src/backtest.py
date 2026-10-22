"""Backtest del motor v1: ¿cuánto se habría equivocado en 10N-2019 y 23J-2023 con lo que se sabía antes?

Para cada elección objetivo se rehace el motor solo con datos anteriores:
- Base: voto por provincia en las generales anteriores (28A-2019 para 10N-2019; 10N-2019 para 23J-2023).
- Señal local: la de las europeas, solo si se celebraron entre las generales anteriores y la objetivo (europeas de
  mayo de 2019 para 10N-2019; ninguna para 23J-2023), igual que en el motor (α = 0,5, PP, PSOE, Vox y Sumar).
- Encuestas: la media de encuestas.py a 5 días y a 38 días de la elección (38 días es la distancia del 22/10/2026
  al 29N). Podemos va dentro de Sumar, como en 2019 y 2023.
- Error de encuesta: c·raíz(voto) con c medido solo en la OTRA elección y a la misma distancia (no se usa el
  resultado que se predice). El motor v1 usaba c a 5 días ampliado un 25 %; aquí se ve que a 38 días el error
  real es casi el doble que a 5 días.
- Los partidos sin encuesta (ERC, Junts, PNV, EH Bildu, BNG, CC) mantienen su voto de las generales anteriores.

Se compara con el resultado real agregado desde las secciones (sin CERA) y con los escaños que da el mismo reparto
D'Hondt a ese resultado, sin «Otros» (CUP, PRC, Teruel Existe o UPN no entran: su escaño se reparte entre el resto,
igual en lo predicho y en lo observado). La variante «encuesta perfecta» usa el voto nacional real, sin error, y
mide solo el reparto entre provincias.

No hay encuestas de febrero a julio de 2019 en la extracción de Electográfica: el 28A-2019 no se puede probar.

Uso:  python3 previsiones/src/backtest.py
Escribe /mnt/project-files/previsiones/backtest/backtest.json y RESUMEN.md.
"""
import json, math, pathlib, sys
from datetime import date, timedelta

import numpy as np
import pandas as pd

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import encuestas  # noqa: E402
from reglas import ESCANOS_2023, dhondt  # noqa: E402

LARGO = pathlib.Path('/mnt/project-files/generales/datos/resultados_secciones_largo.csv')
SALIDA = pathlib.Path('/mnt/project-files/previsiones/backtest')
LISTAS = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC']
CON_SENAL = ['PP', 'PSOE', 'VOX', 'SUMAR']
EN_ENCUESTA = CON_SENAL + ['CS']   # los únicos con cifra en las encuestas de 2019 y 2023
ESCANOS_2019 = {**ESCANOS_2023, '46': 15, '06': 6}   # RD 2019: Valencia 15 y Badajoz 6 (16 y 5 en 2023)
# (objetivo, generales anteriores, europeas intermedias o None, día de la elección, escaños, elección donde medir c)
PRUEBAS = [
    ('2019_11', '2019_04', 'E2019', date(2019, 11, 10), ESCANOS_2019, '2023-07-23'),
    ('2023_07', '2019_11', None, date(2023, 7, 23), ESCANOS_2023, '2019-11-10'),
]
HORIZONTES = [5, 38]
# «metas» es el motor; «tope», el motor v1; «aditivo» y «repetir», los modelos de referencia que hay que batir:
# subida uniforme en puntos (la misma suma o resta en todas las provincias) y repetir las generales anteriores.
METODOS = ['metas', 'tope', 'aditivo', 'repetir']
ALFA, SIGMA_PROV, SIGMA_MAX, N_SIM, SEMILLA = 0.5, 0.08, 0.30, 2000, 20261129


def carga():
    d = pd.read_csv(LARGO, dtype={'tract_code': str})
    d['prov'] = d.tract_code.str[:2]
    d['validos'] = d.candidaturas + d.blancos
    return {e: g.groupby('prov')[LISTAS + ['validos']].sum() for e, g in d.groupby('eleccion')}


def cuotas(x):
    return x[LISTAS].div(x.validos, axis=0)


def central(R, ant, euro, objetivo, metodo):
    """Cuotas por provincia: generales anteriores × señal de las europeas, escaladas hasta clavar la media."""
    provs = R[ant].index
    c = cuotas(R[ant]).values.copy()
    validos = R[ant].validos.values.astype(float)
    peso = validos / validos.sum()
    if metodo == 'repetir':
        return c
    if metodo == 'aditivo':   # sin señal de las europeas: la referencia más sencilla con encuestas
        for k, t in objetivo.items():
            j = LISTAS.index(k)
            c[:, j] = np.maximum(c[:, j] + t - (c[:, j] * peso).sum(), 0) if t > 0 else 0
        fila = c.sum(1, keepdims=True)
        return np.where(fila > 0.985, c / fila * 0.985, c)
    if euro:
        for k in CON_SENAL:
            rel = []
            for e in (euro, ant):
                x = R[e].reindex(provs)
                rel.append((x[k] / x.validos) / (x[k].sum() / x.validos.sum()))
            ok = (rel[0] > 0) & (rel[1] > 0)
            c[:, LISTAS.index(k)] *= np.where(ok, (rel[0] / rel[1].where(ok, 1)) ** ALFA, 1)
    if metodo == 'tope':   # motor v1: subida proporcional con tope de 98,5 % por provincia
        for _ in range(50):
            for k, t in objetivo.items():
                j = LISTAS.index(k)
                nac = (c[:, j] * peso).sum()
                c[:, j] *= t / nac if nac > 0 else 0
            fila = c.sum(1, keepdims=True)
            c = np.where(fila > 0.985, c / fila * 0.985, c)
        return c
    # «metas»: como el anterior, pero las listas sin encuesta también tienen meta (su voto nacional de las
    # generales anteriores), para que el tope no las vaya encogiendo vuelta a vuelta en las provincias donde suben
    # los grandes (EH Bildu y PNV en Euskadi).
    meta = {k: (objetivo[k] if k in objetivo else (c[:, j] * peso).sum()) for j, k in enumerate(LISTAS)}
    for _ in range(200):
        for k, t in meta.items():
            j = LISTAS.index(k)
            nac = (c[:, j] * peso).sum()
            c[:, j] *= t / nac if nac > 0 else 0
        fila = c.sum(1, keepdims=True)
        c = np.where(fila > 0.985, c / fila * 0.985, c)
    return c


def sigma_nac(objetivo, c_err, deriva):
    s = np.zeros(len(LISTAS))
    for k, t in objetivo.items():
        pts = max(t * 100, 0.3)
        s[LISTAS.index(k)] = min(deriva * c_err * math.sqrt(pts) / pts, SIGMA_MAX)
    return s


def simula(c, validos, provs, escanos, sig_nac, rng):
    n, P, L = N_SIM, len(provs), len(LISTAS)
    sims = c[None] * np.exp(rng.normal(0, 1, (n, 1, L)) * sig_nac + rng.normal(0, SIGMA_PROV, (n, P, L)))
    sims = sims / sims.sum(2, keepdims=True) * c.sum(1)[None, :, None]
    esc = np.zeros((n, P, L), int)
    for s in range(n):
        for i, p in enumerate(provs):
            r = dhondt(dict(zip(LISTAS, sims[s, i] * validos[i])), escanos[p], validos[i])
            esc[s, i] = [r[k] for k in LISTAS]
    return sims, esc


def observado(R, obj, escanos):
    real = cuotas(R[obj]).values
    esc = np.array([[dhondt(dict(zip(LISTAS, real[i] * R[obj].validos.iloc[i])), escanos[p], R[obj].validos.iloc[i])[k]
                     for k in LISTAS] for i, p in enumerate(R[obj].index)])
    return real, esc


def evalua(nombre, c, sims, esc, R, obj, escanos, objetivo):
    provs = R[obj].index
    real, esc_real = observado(R, obj, escanos)
    w = R[obj].validos.values / R[obj].validos.sum()
    nac_pred, nac_real = (c * w[:, None]).sum(0) * 100, (real * w[:, None]).sum(0) * 100
    tot, tot_real = esc.sum(1), esc_real.sum(0)
    q10, q50, q90 = np.percentile(tot, [10, 50, 90], axis=0)
    pq10, pq90 = np.percentile(esc, [10, 90], axis=0)
    presentes = [j for j, k in enumerate(LISTAS) if nac_real[j] > 0.3]
    # primera fuerza por provincia: probabilidad simulada frente a lo ocurrido (Brier)
    gana = np.stack([np.bincount(sims[:, i].argmax(1), minlength=len(LISTAS)) / N_SIM for i in range(len(provs))])
    gano = np.eye(len(LISTAS))[real.argmax(1)]
    acierto_1a = float((c.argmax(1) == real.argmax(1)).mean())
    err_prov = np.abs(c - real)[:, presentes] * 100
    return {
        'prueba': nombre, 'objetivo': obj,
        'voto_nacional': {LISTAS[j]: {'previsto': round(nac_pred[j], 2), 'real': round(nac_real[j], 2)} for j in presentes},
        'error_voto_provincia_pts': round(float(err_prov.mean()), 2),
        'error_voto_provincia_ponderado_pts': round(float((err_prov * w[:, None]).sum(0).mean()), 2),
        'escanos': {LISTAS[j]: {'mediana': int(q50[j]), 'intervalo80': [int(q10[j]), int(q90[j])], 'real': int(tot_real[j]),
                                'dentro': bool(q10[j] <= tot_real[j] <= q90[j])} for j in presentes},
        'error_escanos_total': int(np.abs(q50 - tot_real).sum() // 2),
        'escanos_mal_asignados_provincia': int(np.abs(np.round(np.median(esc, 0)) - esc_real).sum() // 2),
        'cobertura80_nacional': round(float(np.mean([q10[j] <= tot_real[j] <= q90[j] for j in presentes])), 2),
        # solo casillas provincia × lista con escaño real o previsto (las 0-0 inflarían la cobertura)
        'cobertura80_provincia': round(float(((pq10 <= esc_real) & (esc_real <= pq90))[(esc_real > 0) | (pq90 > 0)].mean()), 3),
        'primera_fuerza_acierto': round(acierto_1a, 3),
        'primera_fuerza_brier': round(float(((gana - gano) ** 2).sum(1).mean()), 3),
        # CRPS de los escaños de cada lista en España (en escaños; menor es mejor), sumado sobre las listas: premia
        # acertar la mediana y castiga tanto el intervalo demasiado estrecho como el demasiado ancho
        'crps_escanos': round(float(sum(crps(tot[:, j], tot_real[j]) for j in presentes)), 1),
    }


def crps(muestra, y):
    x = np.sort(muestra.astype(float))
    n = len(x)
    # E|X − y| − ½ E|X − X'|, con la fórmula de la muestra ordenada para E|X − X'|
    return np.abs(x - y).mean() - (2 * np.arange(1, n + 1) - n - 1).dot(x) / n ** 2


def main():
    R = carga()
    d = encuestas.carga()
    SALIDA.mkdir(parents=True, exist_ok=True)
    out = []
    for obj, ant, euro, dia, escanos, otra in PRUEBAS:
        provs = R[ant].index
        assert list(provs) == list(R[obj].index)
        validos = R[obj].validos.values.astype(float)   # el tamaño de cada provincia no se predice aquí
        real_nac = (cuotas(R[obj]) * R[obj].validos.values[:, None]).sum() / R[obj].validos.sum()
        variantes = [(f'{h} días', h) for h in HORIZONTES] + [('encuesta perfecta', None)]
        for (nombre, h), metodo in [(v, m) for m in METODOS for v in variantes]:
            if h is not None:
                e, _ = encuestas.error_historico(d, h)
                e = e[e.eleccion == otra]
                c_err = math.sqrt((e.error ** 2 / e.resultado).mean())
            else:
                c_err = 0
            if h is None:
                objetivo = {k: float(real_nac[k]) for k in EN_ENCUESTA}
                sig = np.zeros(len(LISTAS))
            else:
                m, usadas = encuestas.media(d, dia - timedelta(days=h))
                m['SUMAR'] = m.get('SUMAR', 0) + m.pop('PODEMOS', 0)
                objetivo = {k: m.get(k, 0) / 100 for k in EN_ENCUESTA}   # sin cifra en la media: no se presenta (Cs en 2023)
                sig = sigma_nac(objetivo, c_err, 1)
            c = central(R, ant, euro, objetivo, metodo)
            sims, esc = simula(c, validos, provs, escanos, sig, np.random.default_rng(SEMILLA))
            r = evalua(nombre, c, sims, esc, R, obj, escanos, objetivo)
            r.update({'metodo': metodo, 'c_error': round(c_err, 3), 'senal_europeas': euro,
                      'encuestas': None if h is None else len(usadas)})
            out.append(r)
            print(obj, nombre, metodo, {k: v for k, v in r.items() if k not in ('voto_nacional', 'escanos')})
            print('   ', {k: (v['mediana'], v['intervalo80'], v['real']) for k, v in r['escanos'].items()})
    (SALIDA / 'backtest.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
    t = pd.DataFrame(out)
    print('\nEscaños mal puestos en España y CRPS (menor es mejor):')
    print(t.pivot_table(index=['prueba', 'metodo'], columns='objetivo', values=['error_escanos_total', 'crps_escanos']).to_string())
    print('Escrito en', SALIDA)


if __name__ == '__main__':
    main()
