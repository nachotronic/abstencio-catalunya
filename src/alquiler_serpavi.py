"""Precio del alquiler de vivienda habitual por municipio y por sección censal, 2011-2024 (Ministerio de
Vivienda, Sistema Estatal de Referencia del Precio del Alquiler, SERPAVI, a partir del IRPF y el
Catastro). Escribe data/censo/alquiler_secciones.csv.gz y data/censo/alquiler_municipios.csv
(ver data/censo/LEEME.md).
Uso: python3 src/alquiler_serpavi.py "2026-03_09_bd_SERPAVI_2011-2024 - DEFINITIVO WEB_v2.xlsx" """
import sys
from pathlib import Path
import openpyxl
import pandas as pd

SALIDA = Path(__file__).resolve().parent.parent / 'data' / 'censo'
# prefijo de la columna original (+ _VC_AA o _VU_AA) -> nombre (+ _pisos o _unif)
MEDIDAS = {'BI_ALVHEPCO_T': 'n',              # viviendas alquiladas en la muestra
           'ALQM2_LV_M_': 'alq_m2',           # €/m² al mes, mediana
           'ALQM2_LV_25_': 'alq_m2_p25',
           'ALQM2_LV_75_': 'alq_m2_p75',
           'ALQTBID12_M_': 'alq_mes',         # alquiler mensual de la vivienda, mediana
           'SLVM2_M_': 'sup_m2'}              # superficie, mediana
TIPOS = {'VC': 'pisos', 'VU': 'unif'}


def hoja(libro, nombre, clave):
    filas = libro[nombre].iter_rows(values_only=True)
    cab = next(filas)
    d = pd.DataFrame(filas, columns=cab)
    d = d[d[clave].notna()]
    largo = []
    for anyo in range(2011, 2025):
        aa = f'{anyo % 100:02d}'
        cols = {}
        for pre, nom in MEDIDAS.items():
            for t, tn in TIPOS.items():
                c = f'{pre}{t}_{aa}'
                if c in d:
                    cols[c] = f'{nom}_{tn}'
        x = d[[clave] + list(cols)].rename(columns=cols)
        x.insert(1, 'anyo', anyo)
        largo.append(x)
    out = pd.concat(largo)
    medidas = [c for c in out.columns if c not in (clave, 'anyo')]
    out[medidas] = out[medidas].apply(pd.to_numeric, errors='coerce')
    orden = [f'{n}_{t}' for t in TIPOS.values() for n in MEDIDAS.values()]
    return out.dropna(subset=medidas, how='all')[[clave, 'anyo'] + [c for c in orden if c in out]]


def main(fichero):
    libro = openpyxl.load_workbook(fichero, read_only=True)
    s = hoja(libro, 'Secciones censales', 'CUSEC').rename(columns={'CUSEC': 'seccion'})
    s['seccion'] = s['seccion'].astype(str).str.zfill(10)
    s.insert(1, 'mun_code', s['seccion'].str[:5])
    m = hoja(libro, 'Municipios', 'CUMUN').rename(columns={'CUMUN': 'mun_code'})
    m['mun_code'] = m['mun_code'].astype(str).str.zfill(5)
    SALIDA.mkdir(parents=True, exist_ok=True)
    s.sort_values(['anyo', 'seccion']).to_csv(SALIDA / 'alquiler_secciones.csv.gz', index=False, float_format='%.2f')
    m.sort_values(['anyo', 'mun_code']).to_csv(SALIDA / 'alquiler_municipios.csv', index=False, float_format='%.2f')
    print('secciones', len(s), 'municipios', len(m))


if __name__ == '__main__':
    main(sys.argv[1])
