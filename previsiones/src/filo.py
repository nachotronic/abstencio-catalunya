"""Escaños en el filo: con los votos oficiales de 2023 y los escaños de 2026, ¿qué escaño de cada provincia se decide
por menos votos? Es aritmética sobre un dato, no una previsión.

Para cada provincia, el último escaño repartido (el cociente D'Hondt más bajo que entra) y la lista que se queda a las
puertas (el cociente más alto que no entra, incluidas las listas por debajo del 3 % si con esos votos lo superarían).
Tres medidas del margen:
  - «le faltan»: votos nuevos (de quien no votó o votó en blanco no cuentan igual: aquí, votos nuevos a candidatura)
    que necesitaría la aspirante para quitarle el escaño a la última, sin que nadie más cambie;
  - «le sobran»: votos que podría perder la última sin perder el escaño;
  - «cambio de voto»: votantes que tendrían que pasar de la última a la aspirante.
El empate se resuelve por más votos (art. 163.1.d LOREG); se pide superar estrictamente el cociente.
«Otros» agrupa candidaturas distintas y no compite. Votos con CERA (resultado oficial), Madrid 38 y Cádiz 8.

Uso:  python3 previsiones/src/filo.py
Escribe /mnt/project-files/previsiones/filo/filo_2023_con_escanos_2026.csv.
"""
import json, math, pathlib, sys

import pandas as pd

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
from reglas import ESCANOS_2023, ESCANOS_2026, dhondt  # noqa: E402

SIM = json.load(open(RAIZ / 'actualidad/src/sistema/simulador.json'))
SALIDA = pathlib.Path('/mnt/project-files/previsiones/filo')
UMBRAL = 3


def filo(votos, escanos, validos):
    """Último escaño y aspirante de una provincia, con los tres márgenes en votos."""
    v = {k: n for k, n in votos.items() if k != 'Otros' and n > 0}
    r = dhondt(v, escanos, validos)
    elegibles = {k for k, n in v.items() if n * 100 >= UMBRAL * validos}
    ultima = min((v[k] / r[k], k) for k in elegibles if r[k])[1]
    q = v[ultima] / r[ultima]
    _, asp = max((v[k] / (r[k] + 1), k) for k in v if k != ultima)
    s_u, s_a = r[ultima], r[asp] + 1
    falta = math.floor(q * s_a - v[asp]) + 1
    barrera = math.ceil(UMBRAL * validos / 100) - v[asp]   # si no llega al 3 %, también tiene que llegar
    falta = max(falta, barrera)
    sobra = v[ultima] - math.floor(v[asp] / s_a * s_u)   # votos que puede perder antes de quedar por debajo
    # cambio de voto: x tal que (v_a + x)/s_a > (v_u − x)/s_u
    cambio = math.floor((v[ultima] * s_a - v[asp] * s_u) / (s_u + s_a)) + 1
    return {'escanos': escanos, 'ultima': ultima, 'escano_n': s_u, 'aspirante': asp, 'aspirante_escano_n': s_a,
            'le_faltan': falta, 'le_sobran': sobra, 'cambio_de_voto': max(cambio, 1),
            'cambio_pct_validos': round(max(cambio, 1) / validos * 100, 3), 'reparto': {k: n for k, n in r.items() if n}}


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    base, nombres = SIM['elecciones']['2023_07'], SIM['provincias']
    filas = []
    for p in sorted(base):
        if ESCANOS_2026[p] == 1:   # Ceuta y Melilla: un escaño, gana la más votada
            v = sorted(((n, k) for k, n in base[p]['v'].items() if k != 'Otros'), reverse=True)
            m = v[0][0] - v[1][0]
            filas.append({'provincia': nombres[p], 'cod': p, 'escanos': 1, 'ultima': v[0][1], 'escano_n': 1,
                          'aspirante': v[1][1], 'aspirante_escano_n': 1, 'le_faltan': m + 1, 'le_sobran': m,
                          'cambio_de_voto': m // 2 + 1, 'cambio_pct_validos': round((m // 2 + 1) / base[p]['validos'] * 100, 3)})
            continue
        f = filo(base[p]['v'], ESCANOS_2026[p], base[p]['validos'])
        f23 = dhondt({k: n for k, n in base[p]['v'].items() if k != 'Otros'}, ESCANOS_2023[p], base[p]['validos'])
        filas.append({'provincia': nombres[p], 'cod': p, **{k: x for k, x in f.items() if k != 'reparto'},
                      'reparto_2026': ' '.join(f'{k} {n}' for k, n in sorted(f['reparto'].items(), key=lambda t: -t[1])),
                      'cambia_vs_2023': ' '.join(f'{k} {f["reparto"].get(k, 0) - n:+d}' for k, n in f23.items()
                                                 if f['reparto'].get(k, 0) != n)})
    t = pd.DataFrame(filas).sort_values('cambio_de_voto')
    t.to_csv(SALIDA / 'filo_2023_con_escanos_2026.csv', index=False)
    print(t[['provincia', 'escanos', 'ultima', 'escano_n', 'aspirante', 'cambio_de_voto', 'cambio_pct_validos',
             'le_faltan', 'le_sobran', 'cambia_vs_2023']].to_string(index=False))
    print('\nEscaños en juego por menos de 1.000 cambios de voto:', int((t.cambio_de_voto < 1000).sum()),
          '· menos de 5.000:', int((t.cambio_de_voto < 5000).sum()))


if __name__ == '__main__':
    main()
