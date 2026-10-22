"""¿Mejora otra elección intermedia el reparto por sección? Prueba con generales pasadas.

Pregunta: conocido el voto de cada partido en cada provincia (como si la encuesta acertara), ¿se reparte mejor
entre secciones subiendo cada sección en proporción desde las generales anteriores (método actual), o
corrigiendo con lo que cambió en esa sección en una elección intermedia (europeas, municipales)?

Predicción de la cuota del partido k en la sección s:  base_sk · señal_sk^α, escalada en cada provincia para
que el partido sume su voto real. Con α = 0 es la subida proporcional. Dos formas de señal:
  - «cambio»: fuerza relativa de la sección en la elección intermedia nueva frente a la anterior del mismo tipo
    (europeas 2014 / europeas 2009), aplicada a las generales anteriores.
  - «cruce»: fuerza relativa en la intermedia frente a las generales anteriores (europeas 2014 / generales 2011).
Fuerza relativa = cuota de la sección / cuota de su provincia, encogida hacia 1 con k pseudovotos.

Se elige α en una pareja de elecciones y se mide en las otras (fuera de muestra). Error: media de |predicho −
real| en puntos, por sección y partido, en secciones con el mismo código en todas las elecciones de la prueba.

Uso:  python3 previsiones/src/senal_local.py
"""
import json, pathlib

import numpy as np
import pandas as pd

LARGO = pathlib.Path('/mnt/project-files/generales/datos/resultados_secciones_largo.csv')
SALIDA = pathlib.Path('/mnt/project-files/previsiones/base/senal_local.json')
PARTIDOS = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS']
K = 50   # pseudovotos para encoger la fuerza relativa de secciones pequeñas
ALFAS = [0, .25, .5, .75, 1]
# (generales anteriores, generales objetivo, intermedia nueva, intermedia anterior del mismo tipo)
PRUEBAS = [
    ('2011_11', '2015_12', 'E2014', 'E2009'),   # irrupción de Podemos y Cs
    ('2016_06', '2019_11', 'E2019', 'E2014'),   # irrupción de Vox, caída de Cs
    ('2019_11', '2023_07', 'M2023', 'M2019'),   # municipales dos meses antes; caída de Cs
]


def carga():
    d = pd.read_csv(LARGO, dtype={'tract_code': str})
    d['validos'] = d.candidaturas + d.blancos
    d['prov'] = d.tract_code.str[:2]
    return {e: g.set_index('tract_code') for e, g in d.groupby('eleccion')}


def fuerza(e, secs):
    """Cuota de cada sección dividida por la de su provincia, encogida hacia 1 con K pseudovotos."""
    x = e.loc[secs]
    prov = e.groupby('prov')[PARTIDOS + ['validos']].sum()
    cuota_prov = prov[PARTIDOS].div(prov.validos, axis=0)
    cp = cuota_prov.loc[x.prov].values
    return (x[PARTIDOS].values + K * cp) / (x.validos.values[:, None] + K) / np.maximum(cp, 1e-6)


def predice(E, ant, obj, senal, alfa, secs, nuevo, f_nueva):
    a, o = E[ant].loc[secs], E[obj].loc[secs]
    base = a[PARTIDOS].values / a.validos.values[:, None]
    p = base * senal ** alfa
    # partido nuevo en la provincia (menos del 1 % en las generales anteriores: Cs en 2011, Vox en 2016):
    # sin base que subir, se reparte según su fuerza relativa en la intermedia (con α = 0, por igual)
    p = np.where(nuevo, 0.01 * f_nueva ** alfa, p)
    votos = p * o.validos.values[:, None]
    real = o[PARTIDOS].values
    prov = o.prov.values
    for pr in np.unique(prov):
        m = prov == pr
        objetivo, suma = real[m].sum(0), votos[m].sum(0)
        votos[m] *= np.where(suma > 0, objetivo / np.maximum(suma, 1e-9), 0)
    pred = votos / o.validos.values[:, None] * 100
    return np.abs(pred - real / o.validos.values[:, None] * 100)


def a_provincias(E):
    """Las mismas elecciones agregadas por provincia, con España como único «ámbito»: prueba el reparto entre
    provincias conocido el voto nacional (lo que decide los escaños)."""
    out = {}
    for e, g in E.items():
        x = g.groupby('prov')[PARTIDOS + ['validos']].sum()
        x.index.name = 'tract_code'
        x['prov'] = 'ES'
        out[e] = x
    return out


def main():
    E = carga()
    res = prueba(E, 'sección')
    res += prueba(a_provincias(E), 'provincia', k=0)
    r = pd.DataFrame(res)
    print('\n', r.pivot_table(index=['nivel', 'senal', 'alfa'], columns='prueba', values='media').to_string())
    SALIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1))


def prueba(E, nivel, k=K):
    global K
    K = k
    res = []
    for ant, obj, nueva, vieja in PRUEBAS:
        secs = sorted(set.intersection(*(set(E[e].index) for e in (ant, obj, nueva, vieja))))
        secs = [s for s in secs if all(E[e].loc[s, 'validos'] > 0 for e in (ant, obj))]
        prov_ant = E[ant].groupby('prov')[PARTIDOS + ['validos']].sum()
        nuevo = (prov_ant[PARTIDOS].div(prov_ant.validos, axis=0) < 0.01).loc[E[ant].loc[secs].prov].values
        f_nueva = fuerza(E[nueva], secs)
        senales = {'cambio': f_nueva / fuerza(E[vieja], secs), 'cruce': f_nueva / fuerza(E[ant], secs)}
        for nom, s in senales.items():
            s = np.clip(s, 0.2, 5)
            for alfa in ALFAS:
                err = predice(E, ant, obj, s, alfa, secs, nuevo, np.clip(f_nueva, 0.2, 5))
                presentes = E[obj][PARTIDOS].sum() > 0
                fila = {'nivel': nivel, 'prueba': f'{ant}→{obj} con {nueva}', 'senal': nom, 'alfa': alfa, 'secciones': len(secs),
                        **{k: round(float(err[:, j].mean()), 3) for j, k in enumerate(PARTIDOS) if presentes[k]}}
                fila['media'] = round(float(np.mean([fila[k] for k in PARTIDOS if k in fila])), 3)
                res.append(fila)
    return res


if __name__ == '__main__':
    main()
