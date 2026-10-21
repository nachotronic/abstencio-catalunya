"""Base por sección para 2026: voto de las generales de 2023 con el espacio de Sumar repartido entre Sumar (FA) y
Podemos según dónde vota cada uno en las europeas de 2024, y un índice de dónde vota SALF.

Por qué: en 2023 Sumar y Podemos fueron juntos; en 2026 las encuestas los miden por separado (FA y Podemos) y añaden
SALF. Las europeas de 2024 son las únicas elecciones con los tres por separado y resultados por sección.

- cuota_podemos: parte del voto Sumar+Podemos de 2024 que fue a Podemos, con contracción bayesiana hacia el
  municipio y la provincia cuando la sección tiene pocos votos (k = 30 votos de peso a priori).
- SUMAR_FA_2023 y PODEMOS_2023: voto Sumar de 2023 multiplicado por esa cuota y su complemento.
- indice_salf: voto de SALF en la sección en 2024 dividido por su media en España (1 = media), con la misma contracción.
  El modelo lo usa para repartir por secciones el voto nacional de SALF que den las encuestas.

Supuesto (a validar): el reparto entre Sumar y Podemos de cada sección en 2024 se mantiene en 2026.

Uso, desde la raíz:  python3 previsiones/src/base2026.py   (después de europeas2024.py)
"""
import os, pathlib
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[2]
BASE = pathlib.Path(os.environ.get('PREVISIONES_BASE', '/mnt/project-files/previsiones/base'))
K = 30
FAM23 = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC', 'OTROS']


def contrae(num, den, prior, k=K):
    return (num + k * prior) / (den + k)


def main():
    e = pd.read_csv(BASE / 'europeas2024_secciones.csv', dtype={'tract_code': str})
    e['mun'] = e.tract_code.str[:5]
    e['prov'] = e.tract_code.str[:2]
    e['izq'] = e.PODEMOS + e.SUMAR
    # cuota de Podemos: España -> provincia -> municipio -> sección
    nac = e.PODEMOS.sum() / e.izq.sum()
    p = e.groupby('prov')[['PODEMOS', 'izq']].sum()
    p['q'] = contrae(p.PODEMOS, p.izq, nac, 300)
    m = e.groupby(['prov', 'mun'])[['PODEMOS', 'izq']].sum().reset_index()
    m['q'] = contrae(m.PODEMOS, m.izq, m.prov.map(p.q), 100)
    e['q_mun'] = e.mun.map(m.set_index('mun').q)
    e['cuota_podemos'] = contrae(e.PODEMOS, e.izq, e.q_mun)
    # índice de SALF (1 = media de España), contraído hacia el municipio
    s_nac = e.SALF.sum() / e.validos.sum()
    ms = e.groupby('mun')[['SALF', 'validos']].sum()
    ms['s'] = contrae(ms.SALF, ms.validos, s_nac, 200)
    e['salf_2024'] = contrae(e.SALF, e.validos, e.mun.map(ms.s), 200)
    e['indice_salf'] = e.salf_2024 / s_nac

    g = pd.read_csv(RAIZ / 'generales-2026/descargas/resultados_secciones_largo.csv', dtype={'tract_code': str, 'mun_code': str})
    g = g[g.eleccion == '2023_07'].set_index('tract_code')
    out = g[['censo', 'votantes', 'blancos', 'nulos'] + FAM23].copy()
    out['validos'] = out[FAM23].sum(axis=1) + out.blancos
    e = e.set_index('tract_code')
    cruce = out.index.intersection(e.index)
    print(f'secciones 2023: {len(out)}, con europeas 2024: {len(cruce)} ({len(cruce) / len(out):.1%})')
    # sección sin cruce (cambió de código): municipio
    q = e.cuota_podemos.reindex(out.index)
    q = q.fillna(pd.Series(out.index.str[:5], index=out.index).map(m.set_index('mun').q)).fillna(nac)
    ind = e.indice_salf.reindex(out.index)
    ind = ind.fillna(pd.Series(out.index.str[:5], index=out.index).map(ms.s / s_nac)).fillna(1.0)
    out['cuota_podemos'] = q.round(4)
    out['PODEMOS_2023'] = (out.SUMAR * q).round(1)
    out['SUMAR_FA_2023'] = (out.SUMAR - out.PODEMOS_2023).round(1)
    out['indice_salf'] = ind.round(3)
    out['cruce_europeas'] = out.index.isin(cruce)
    out.reset_index().to_csv(BASE / 'base2026_secciones.csv', index=False)
    tot = out[['SUMAR', 'PODEMOS_2023', 'SUMAR_FA_2023']].sum()
    print('España: Sumar 2023 =', int(tot.SUMAR), '-> FA', int(tot.SUMAR_FA_2023), '+ Podemos', int(tot.PODEMOS_2023),
          f'(cuota Podemos {tot.PODEMOS_2023 / tot.SUMAR:.1%}; en las europeas {nac:.1%})')
    print('indice SALF: percentiles', out.indice_salf.quantile([.05, .25, .5, .75, .95]).round(2).to_dict())


if __name__ == '__main__':
    main()
