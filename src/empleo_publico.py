"""Personal al servicio de las Administraciones públicas por provincia (Registro Central de Personal,
EPSAP de enero de 2026, microdatos agregados). Escribe data/empleo/empleo_publico_provincias.csv.
Uso: python3 src/empleo_publico.py [carpeta]   (descarga el zip a la carpeta si no está ya)"""
import sys
import urllib.request
import zipfile
from pathlib import Path
import pandas as pd

SALIDA = Path(__file__).resolve().parent.parent / 'data' / 'empleo' / 'empleo_publico_provincias.csv'
URL = 'https://digital.gob.es/content/dam/portal-mtdfp/funcion-publica/rcp/boletin/2026_01/Microdatos_Enero_2026.zip'
XLSX = 'Agrupaciones_Total_Enero_2026.xlsx'

PROVINCIAS = {
    'ARABA/ALAVA': '01', 'ALBACETE': '02', 'ALACANT/ALICANTE': '03', 'ALMERIA': '04', 'AVILA': '05',
    'BADAJOZ': '06', 'ILLES BALEARS': '07', 'BARCELONA': '08', 'BURGOS': '09', 'CACERES': '10',
    'CADIZ': '11', 'CASTELLO/CASTELLON': '12', 'CIUDAD REAL': '13', 'CORDOBA': '14', 'A CORUÑA': '15',
    'CUENCA': '16', 'GIRONA': '17', 'GRANADA': '18', 'GUADALAJARA': '19', 'GIPUZKOA': '20', 'HUELVA': '21',
    'HUESCA': '22', 'JAEN': '23', 'LEON': '24', 'LLEIDA': '25', 'LA RIOJA': '26', 'LUGO': '27', 'MADRID': '28',
    'MALAGA': '29', 'MURCIA': '30', 'NAVARRA': '31', 'OURENSE': '32', 'ASTURIAS': '33', 'PALENCIA': '34',
    'LAS PALMAS': '35', 'PONTEVEDRA': '36', 'SALAMANCA': '37', 'SANTA CRUZ DE TENERIFE': '38',
    'CANTABRIA': '39', 'SEGOVIA': '40', 'SEVILLA': '41', 'SORIA': '42', 'TARRAGONA': '43', 'TERUEL': '44',
    'TOLEDO': '45', 'VALÈNCIA/VALENCIA': '46', 'VALLADOLID': '47', 'BIZKAIA': '48', 'ZAMORA': '49',
    'ZARAGOZA': '50', 'CEUTA': '51', 'MELILLA': '52', 'EXTRANJERO': '99'}
ADMIN = {'SECTOR PUBLICO DEL ESTADO': 'estado', 'SECTOR PUBLICO DE LAS COMUNIDADES AUTONOMAS': 'ccaa',
         'SECTOR PUBLICO DE LAS ENTIDADES LOCALES': 'local'}
PERSONAL = {'PERSONAL FUNCIONARIO DE CARRERA': 'funcionario_carrera', 'PERSONAL LABORAL': 'laboral',
            'OTRO PERSONAL': 'otro'}

if __name__ == '__main__':
    carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    z = carpeta / 'Microdatos_Enero_2026.zip'
    if not z.exists():
        print('descargando', URL)
        urllib.request.urlretrieve(URL, z)
    with zipfile.ZipFile(z) as f, f.open(XLSX) as x:
        d = pd.read_excel(x, sheet_name='Datos')
    d = d.assign(prov_code=d['PROVINCIA'].map(PROVINCIAS), administracion=d['TIPO_ADMINISTRACION'].map(ADMIN),
                 sector=d['SUBTIPO_ADMINISTRACION'].str.lower(), personal=d['TIPO_PERSONAL'].map(PERSONAL))
    assert d[['prov_code', 'administracion', 'personal']].notna().all().all()
    t = (d.groupby(['prov_code', 'administracion', 'sector', 'personal'])['Suma de Num_NIF'].sum()
         .unstack('personal', fill_value=0).reset_index())
    t['efectivos'] = t[list(PERSONAL.values())].sum(axis=1)
    t.insert(1, 'provincia', t['prov_code'].map({v: k for k, v in PROVINCIAS.items()}))
    t = t[['prov_code', 'provincia', 'administracion', 'sector', 'efectivos', *PERSONAL.values()]]
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(SALIDA, index=False)
    print(len(t), 'filas; efectivos', t['efectivos'].sum())
