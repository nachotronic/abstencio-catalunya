"""¿Mejora la media si se corrige el sesgo de cada encuestadora («efecto de la casa»)? ¿Y el sesgo de todo el sector?

Efecto de la casa (relativo): en los 365 días anteriores a la fecha de la media, cada encuesta se compara con la media
de las demás casas en su fecha de campo; el efecto de la casa h para el partido p es la suma de esas desviaciones
dividida entre (número de encuestas + K), que lo encoge hacia cero cuando la casa ha publicado poco. La media corregida
resta ese efecto a cada encuesta antes de promediar. No usa ningún resultado electoral: sirve igual para el 29N.

Sesgo del sector (absoluto): error medio de la media frente al resultado en las elecciones ANTERIORES a la que se
predice (solo las anteriores, por orden de fecha), encogido con K_SECTOR elecciones ficticias de sesgo cero.

Se prueba en las dos generales y en las autonómicas desde 2015 (mismos datos que error_encuestas.py), a 7 y a 38 días,
con la c de error ≈ c·raíz(voto) de cada variante. Si una corrección no baja c fuera de muestra, no entra en el motor.

Uso:  python3 previsiones/src/sesgo_encuestas.py
Escribe /mnt/project-files/previsiones/error_encuestas/sesgo_encuestas.csv y efectos_casa_29n.csv.
"""
import math, pathlib, sys
from datetime import date, timedelta

import numpy as np
import pandas as pd

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import encuestas  # noqa: E402
import error_encuestas as EE  # noqa: E402

SALIDA = pathlib.Path('/mnt/project-files/previsiones/error_encuestas')
K, K_SECTOR, VENTANA_CASA = 3, 5, 365
DIAS = [7, 38]


def efectos_casa(d, ref):
    """{(casa, partido): efecto en puntos} con las encuestas de los VENTANA_CASA días anteriores a `ref`."""
    x = d[(d.fecha <= ref) & (d.fecha > ref - timedelta(days=VENTANA_CASA))]
    dev = {}
    for (url, casa, f), g in x.groupby(['url_electografica', 'casa', 'fecha']):
        otros, usadas = encuestas.media(x[x.casa != casa], f)
        if len(usadas) < 2:
            continue
        for r in g.itertuples():
            if r.partido_modelo in otros:
                dev.setdefault((casa, r.partido_modelo), []).append(r.voto - otros[r.partido_modelo])
    return {k: sum(v) / (len(v) + K) for k, v in dev.items()}


def corrige(d, ef):
    return d.assign(voto=[v - ef.get((c, p), 0) for v, c, p in zip(d.voto, d.casa, d.partido_modelo)])


def errores(fuente, nombre, dia, d, res):
    """Errores de la media sin corregir y con efecto de la casa, a cada distancia."""
    filas = []
    for h in DIAS:
        ref = dia - timedelta(days=h)
        m0, usadas = encuestas.media(d, ref)
        if not len(usadas):
            continue
        m1, _ = encuestas.media(corrige(d, efectos_casa(d, ref)), ref)
        for k, v in res.items():
            if k in m0 and v >= EE.MIN_VOTO:
                filas.append({'fuente': fuente, 'eleccion': nombre, 'dia': dia, 'dias': h, 'partido': k, 'resultado': v,
                              'error_sin': m0[k] - v, 'error_casa': m1[k] - v, 'encuestas': len(usadas)})
    return filas


def main():
    filas = []
    g = encuestas.carga()
    g['partido_modelo'] = g.partido_modelo.replace({'PODEMOS': 'SUMAR'})
    g = g.groupby(['url_electografica', 'casa', 'encuestadora', 'cliente', 'fecha', 'n', 'partido_modelo'],
                  dropna=False).voto.sum().reset_index()
    for dia, res in encuestas.RESULTADOS.items():
        filas += errores('generales', dia, date.fromisoformat(dia), g, res)
    a = EE.encuestas_autonomicas()
    for (clave, dia), res in sorted(EE.resultados().items(), key=lambda t: t[0][1]):
        filas += errores('autonómicas', f'{clave} {dia}', dia, a[a.ccaa == clave], res)
    e = pd.DataFrame(filas).sort_values('dia')
    # sesgo del sector: media del error (con efecto de la casa) por partido y distancia en las elecciones anteriores
    sector = []
    for r in e.itertuples():
        prev = e[(e.dia < r.dia) & (e.partido == r.partido) & (e.dias == r.dias)]
        prev = prev.groupby('eleccion').error_casa.mean()
        sector.append(prev.sum() / (len(prev) + K_SECTOR))
    e['error_casa_sector'] = e.error_casa - np.array(sector)
    e.to_csv(SALIDA / 'sesgo_encuestas.csv', index=False)
    print('c de error ≈ c·raíz(voto) (menor es mejor):')
    for (h, fuente), x in list(e.groupby(['dias', 'fuente'])) + [((h, 'todas'), x) for h, x in e.groupby('dias')]:
        c = {v: round(math.sqrt((x[v] ** 2 / x.resultado).mean()), 3) for v in ('error_sin', 'error_casa', 'error_casa_sector')}
        print(f'  {h:>2} días, {fuente:<12} {x.eleccion.nunique():>2} elecciones:', c)
    # efectos de la casa para el 29N, con las encuestas nacionales hasta hoy
    ef = efectos_casa(g, date.today())
    t = pd.DataFrame([{'casa': c, 'partido': p, 'efecto': round(v, 2)} for (c, p), v in ef.items()])
    t = t.pivot_table(index='casa', columns='partido', values='efecto')
    n = g[g.fecha > date.today() - timedelta(days=VENTANA_CASA)].groupby('casa').url_electografica.nunique()
    t['encuestas'] = n
    t = t.sort_values('encuestas', ascending=False)
    t.to_csv(SALIDA / 'efectos_casa_29n.csv')
    print('\nEfecto de la casa en el último año (puntos sobre la media de las demás):')
    print(t[t.encuestas >= 3][['PP', 'PSOE', 'VOX', 'SUMAR', 'encuestas']].round(1).to_string())


if __name__ == '__main__':
    main()
