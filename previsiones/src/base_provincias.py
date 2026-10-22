"""Agrega por provincia las bases por sección que usa el motor (base2026.py y europeas2024.py), para que el motor
pueda correr en GitHub Actions sin la carpeta del proyecto. El motor solo usa sumas provinciales.

Uso:  python3 previsiones/src/base_provincias.py
Escribe previsiones/datos/base/{base2026,europeas2024}_provincias.csv y copia error_por_distancia.csv.
"""
import pathlib, shutil

import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[2]
MNT = pathlib.Path('/mnt/project-files/previsiones')
SALIDA = RAIZ / 'previsiones/datos/base'


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    b = pd.read_csv(MNT / 'base/base2026_secciones.csv', dtype={'tract_code': str})
    b['salf'] = b.indice_salf * b.validos
    cols = ['PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS_2023', 'SUMAR_FA_2023', 'salf', 'validos']
    b.groupby(b.tract_code.str[:2].rename('prov'))[cols].sum().round(3).to_csv(SALIDA / 'base2026_provincias.csv')
    e = pd.read_csv(MNT / 'base/europeas2024_secciones.csv', dtype={'tract_code': str})
    e.groupby(e.tract_code.str[:2].rename('prov'))[['PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS', 'validos']].sum() \
     .to_csv(SALIDA / 'europeas2024_provincias.csv')
    shutil.copy(MNT / 'error_encuestas/error_por_distancia.csv', SALIDA / 'error_por_distancia.csv')


if __name__ == '__main__':
    main()
