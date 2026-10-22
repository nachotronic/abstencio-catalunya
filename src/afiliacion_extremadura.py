"""Afiliados a la Seguridad Social residentes en Extremadura, por municipio, sector, régimen y sexo
(Junta de Extremadura, Instituto de Estadística de Extremadura, tablas mensuales a final de mes).
Escribe data/empleo/afiliacion_extremadura_municipios.csv (ver data/empleo/LEEME.md).
Uso: python3 src/afiliacion_extremadura.py [carpeta]   (descarga los .xls a la carpeta si no están ya)"""
import re
import sys
import time
import urllib.request
from pathlib import Path
import pandas as pd

SALIDA = Path(__file__).resolve().parent.parent / 'data' / 'empleo' / 'afiliacion_extremadura_municipios.csv'
WEB = 'https://www.juntaex.es'
# fecha -> página de la Junta. Desde finales de 2025 el nombre de la página va un mes por detrás del dato
PAGINAS = {'2021-12': 'diciembre-2021', '2022-12': 'diciembre-2022', '2023-12': 'diciembre-2023',
           '2024-12': 'diciembre-2024', '2025-11': 'noviembre-2025', '2026-09': 'agosto-2026'}
# hojas por provincia: Badajoz 1-5, Cáceres 6-10 (total, sector, régimen, sexo, edad)
HOJAS = {'sector': ('2', '7'), 'regimen': ('3', '8'), 'sexo': ('4', '9')}
# cabecera de la tabla -> columna (no todos los meses traen la columna «No consta»)
NOMBRES = {'sector': {'Agricultura': 'agricultura', 'Industria': 'industria', 'Construcción': 'construccion',
                      'Servicios': 'servicios', 'No consta': 'sector_no_consta'},
           'regimen': {'R. General': 'general', 'R. G. Empleados de hogar': 'empleados_hogar',
                       'R. G. Sist. Especial Agrario': 'agrario', 'R. E. Autónomo': 'autonomos',
                       'No consta': 'regimen_no_consta'},
           'sexo': {'Hombre': 'hombres', 'Hombres': 'hombres', 'Mujer': 'mujeres', 'Mujeres': 'mujeres'}}


def abrir(url):
    for intento in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except OSError:
            if intento == 4:
                raise
            time.sleep(2 ** intento)


def descargar(carpeta, fecha, pagina):
    f = carpeta / f'afss_{fecha}.xls'
    if f.exists():
        return f
    html = abrir(f'{WEB}/w/afiliacion-a-la-seguridad-social-por-municipios-{pagina}').decode('utf-8', 'replace')
    enlace = re.search(r'href="(/documents/[^"]+Tablas_afss(\d{2})(\d{4})\.xls[^"]*)"', html)
    assert enlace and f'{enlace.group(3)}-{enlace.group(2)}' == fecha, (fecha, enlace and enlace.group(0))
    f.write_bytes(abrir(WEB + enlace.group(1).replace('&amp;', '&')))
    return f


def hoja(xls, nombre, nombres=None):
    d = pd.read_excel(xls, sheet_name=nombre, header=None)
    if nombres:
        cabecera = d.iloc[2]
        cols = {i: nombres[str(c).strip()] for i, c in cabecera.items() if i > 0 and pd.notna(c)}
    else:
        cols = {1: 'afiliados'}
    d = d[d[0].astype(str).str.match(r'^\d{5} - ')]
    d = d[[0, *cols]].rename(columns={0: 'municipio', **cols})
    d.insert(0, 'mun_code', d['municipio'].str[:5])
    d['municipio'] = d['municipio'].str[8:]
    # «(*)» = dato protegido por secreto estadístico
    v = list(cols.values())
    d[v] = d[v].apply(pd.to_numeric, errors='coerce')
    return d.set_index(['mun_code', 'municipio'])


if __name__ == '__main__':
    carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    carpeta.mkdir(parents=True, exist_ok=True)
    partes = []
    for fecha, pagina in PAGINAS.items():
        xls = descargar(carpeta, fecha, pagina)
        bloques = []
        for clave, (badajoz, caceres) in HOJAS.items():
            bloques.append(pd.concat([hoja(xls, h, NOMBRES[clave]) for h in (badajoz, caceres)]))
        total = pd.concat([hoja(xls, h) for h in ('1', '6')])
        t = total.join(bloques).reset_index()
        t.insert(1, 'fecha', fecha)
        partes.append(t)
        print(fecha, len(t), 'municipios;', int(t['afiliados'].sum()), 'afiliados')
    t = pd.concat(partes).sort_values(['fecha', 'mun_code'])
    t = t[['mun_code', 'fecha', 'municipio', 'afiliados', *dict.fromkeys(c for n in NOMBRES.values() for c in n.values())]]
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(SALIDA, index=False, float_format='%.0f')
