"""Proyección del escrutinio en directo: con una parte de las secciones contadas, ¿cuánto se acierta el resultado final?

No hay archivo público del orden en que entraron las mesas el 23J, así que el orden se simula: cada sección entra en un
momento que crece con su tamaño (las mesas pequeñas, sobre todo rurales, acaban antes) más ruido aleatorio. Se repite
con varias semillas. Se predice el 23J-2023 con el 10N-2019 como base, por sección, y se comparan tres métodos:
  - «tal cual»: el voto contado hasta ese momento, como hace la web de Interior;
  - «cambio proporcional»: en cada provincia, cuánto ha subido o bajado cada partido en las secciones ya contadas
    frente a 2019 (cociente), aplicado al voto de 2019 de las secciones que faltan;
  - «cambio en puntos»: lo mismo con la diferencia en puntos.
La participación de las secciones que faltan se proyecta igual (cociente frente a 2019) y el censo es el de 2023.
Métrica: escaños mal puestos en España (D'Hondt por provincia sin «Otros», sin CERA) frente al resultado final.

Uso:  python3 previsiones/src/escrutinio.py
"""
import pathlib, sys

import numpy as np
import pandas as pd

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from reglas import ESCANOS_2023, dhondt  # noqa: E402

LARGO = pathlib.Path('/mnt/project-files/generales/datos/resultados_secciones_largo.csv')
SALIDA = pathlib.Path('/mnt/project-files/previsiones/escrutinio')
L = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC']
FRACCIONES = [.05, .10, .20, .40, .60, .80]
SEMILLAS = range(5)
RUIDO = 1.0   # desviación del ruido del orden (en logaritmo del tamaño); 0 = estrictamente de menor a mayor


def carga(ant='2019_11', obj='2023_07'):
    d = pd.read_csv(LARGO, dtype={'tract_code': str})
    a, o = (d[d.eleccion == e].set_index('tract_code') for e in (ant, obj))
    secs = a.index.intersection(o.index)
    a, o = a.loc[secs], o.loc[secs]
    ok = (a.censo > 0) & (o.censo > 0) & (a.votantes > 0)
    return a[ok], o[ok]


def escanos(votos, validos, provs):
    """Escaños por partido en España a partir de votos por provincia (DataFrame provincia × partido)."""
    tot = dict.fromkeys(L, 0)
    for p in provs:
        r = dhondt(votos.loc[p].to_dict(), ESCANOS_2023[p], validos.loc[p])
        for k, n in r.items():
            tot[k] += n
    return pd.Series(tot)


def proyecta(a, o, contadas, metodo):
    prov = o.index.str[:2]
    cont = o[contadas]
    if metodo == 'tal cual':
        g = cont.groupby(cont.index.str[:2])
        ps = sorted(set(prov))
        return g[L].sum().reindex(ps).fillna(0), (g.candidaturas.sum() + g.blancos.sum()).reindex(ps).fillna(0)
    ac, oc = a[contadas], o[contadas]
    pa = ac.index.str[:2]
    # cambio en cada provincia sobre las secciones contadas (partidos y participación)
    sa = ac.groupby(pa)[L + ['votantes', 'censo']].sum()
    so = oc.groupby(pa)[L + ['votantes', 'censo']].sum()
    falta = ~contadas
    af, of = a[falta], o[falta]
    pf = af.index.str[:2]
    part_r = ((so.votantes / so.censo) / (sa.votantes / sa.censo)).reindex(pf).fillna(1).values
    votantes_f = af.votantes / af.censo * of.censo * part_r   # votantes previstos en lo que falta
    cuota_a = af[L].div(af.votantes, axis=0)
    ca, co = sa[L].div(sa.votantes, axis=0), so[L].div(so.votantes, axis=0)
    if metodo == 'cambio proporcional':
        f = (co / ca.where(ca > 0)).reindex(pf).fillna(1).values
        cuota_f = cuota_a.values * f
    else:
        cuota_f = np.maximum(cuota_a.values + (co - ca).reindex(pf).fillna(0).values, 0)
    # lista nueva en la provincia (sin voto en 2019 en lo contado): su cuota contada, igual en lo que falta
    nueva = (ca.reindex(pf).values == 0) & (co.reindex(pf).values > 0)
    cuota_f = np.where(nueva, co.reindex(pf).values, cuota_f)
    vf = pd.DataFrame(cuota_f * votantes_f.values[:, None], index=af.index, columns=L)
    val_f = votantes_f * (oc.candidaturas.sum() + oc.blancos.sum()) / oc.votantes.sum()   # válidos ≈ votantes − nulos
    votos = oc[L].groupby(pa).sum().add(vf.groupby(pf).sum(), fill_value=0)
    validos = (oc.candidaturas + oc.blancos).groupby(pa).sum().add(val_f.groupby(pf).sum(), fill_value=0)
    return votos.reindex(sorted(set(prov))).fillna(0), validos.reindex(sorted(set(prov))).fillna(0)


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    a, o = carga()
    provs = sorted(set(o.index.str[:2]))
    g = o.groupby(o.index.str[:2])
    final = escanos(g[L].sum(), g.candidaturas.sum() + g.blancos.sum(), provs)
    print('Final (secciones, sin CERA):', {k: int(v) for k, v in final.items() if v})
    filas = []
    for s in SEMILLAS:
        rng = np.random.default_rng(s)
        orden = np.log(o.censo.values) + rng.normal(0, RUIDO, len(o))   # las pequeñas antes
        rango = pd.Series(orden, index=o.index).rank(pct=True)
        for f in FRACCIONES:
            contadas = (rango <= f).values
            for metodo in ('tal cual', 'cambio proporcional', 'cambio en puntos'):
                v, val = proyecta(a, o, contadas, metodo)
                e = escanos(v, val, provs)
                filas.append({'semilla': s, 'escrutado': f, 'metodo': metodo,
                              'mal_puestos': int((e - final).abs().sum() // 2),
                              **{k: int(e[k]) for k in ('PP', 'PSOE', 'VOX', 'SUMAR')}})
    t = pd.DataFrame(filas)
    t.to_csv(SALIDA / 'backtest_escrutinio_2023.csv', index=False)
    print(t.pivot_table(index='escrutado', columns='metodo', values='mal_puestos', aggfunc='mean').round(1).to_string())
    print(t.pivot_table(index='escrutado', columns='metodo', values='mal_puestos', aggfunc='max').to_string())


if __name__ == '__main__':
    main()
