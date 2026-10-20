"""Censo electoral por municipio (INE, Oficina del Censo Electoral, censo de consulta, tabla 4)
para las generales de 2023 y de 2026. Uso: python3 src/censo_ine.py tab4_2023.xlsx tab4_2026.xlsx"""
import sys
from pathlib import Path
import pandas as pd

SALIDA = Path(__file__).resolve().parent.parent / 'data' / 'censo' / 'censo_municipios_2023_2026.csv'
FUENTE = {2023: 'https://www.ine.es/oficina_censo/elecgen2023/Elecgral_2023_cc_tab4.xlsx',
          2026: 'https://www.ine.es/oficina_censo/elecgen2026/Elecgral_2026_cc_tab4.xlsx'}


def leer(fichero, y):
    d = pd.read_excel(fichero, header=None, skiprows=8, dtype={0: str})
    d = d[d[1].notna()].copy()
    d[0] = d[0].ffill()   # en 2026 la fila de Ziortza-Bolibar (48915) viene sin código de provincia
    d = pd.DataFrame({'mun_code': d[0].str.zfill(2) + d[1].astype(int).astype(str).str.zfill(3),
                      f'cer_{y}': d[3].astype(int), f'cera_{y}': d[4].astype(int)})
    return d


if __name__ == '__main__':
    a, b = leer(sys.argv[1], 2023), leer(sys.argv[2], 2026)
    t = a.merge(b, on='mun_code', how='outer').sort_values('mun_code')
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(SALIDA, index=False, float_format='%.0f')
    print(len(t), 'municipios;', t.isna().sum().to_dict())
    print('totales', t.drop(columns='mun_code').sum().to_dict())
