"""Viviendas turísticas por sección censal (INE, estadística experimental «Medición del número de
viviendas turísticas en España y su capacidad», tabla 5). Escribe data/censo/viviendas_turisticas_secciones.csv.gz
(ver data/censo/LEEME.md).
Uso: python3 src/viviendas_turisticas.py exp_viv_turistica_tabla5_*.xlsx"""
import sys
from pathlib import Path
import openpyxl
import pandas as pd

SALIDA = Path(__file__).resolve().parent.parent / 'data' / 'censo'
COLS = {'CODIGO': 'seccion', 'PERIODO': 'periodo', 'vivienda turistica': 'viviendas',
        'plazas': 'plazas', 'Porcentaje vivienda turistica': 'pct_viviendas'}


def leer(f):
    filas = openpyxl.load_workbook(f, read_only=True)['Secciones'].iter_rows(values_only=True)
    cab = next(filas)
    # la primera columna se llama CODIGO, CUSEC o cusec según el fichero
    cab = ('CODIGO',) + cab[1:]
    d = pd.DataFrame(filas, columns=cab)[list(COLS)].rename(columns=COLS)
    d = d[d['seccion'].notna()]
    # «2023M02» -> «2023-02»
    d['periodo'] = d['periodo'].str.replace('M', '-')
    return d


def main(ficheros):
    d = pd.concat(leer(f) for f in ficheros)
    d.insert(1, 'mun_code', d['seccion'].str[:5])
    for c in ('viviendas', 'plazas', 'pct_viviendas'):
        d[c] = pd.to_numeric(d[c], errors='coerce')
    d = d.sort_values(['periodo', 'seccion'])
    SALIDA.mkdir(parents=True, exist_ok=True)
    d.to_csv(SALIDA / 'viviendas_turisticas_secciones.csv.gz', index=False, float_format='%.3f')
    print(d.groupby('periodo')[['viviendas', 'plazas']].sum())


if __name__ == '__main__':
    main(sys.argv[1:])
