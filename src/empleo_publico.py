"""Personal al servicio de las Administraciones públicas por provincia, de enero de 2023 a enero de 2026
(Registro Central de Personal, EPSAP, microdatos agregados semestrales). Escribe
data/empleo/empleo_publico_provincias.csv. Uso: python3 src/empleo_publico.py [carpeta]
(descarga los zips a la carpeta si no están ya). Los cortes de 2019 a 2022 no se usan: cubren
menos personal (1,1 y 2,7 millones frente a 3,0) y no son comparables."""
import sys
import urllib.request
import zipfile
from pathlib import Path
import pandas as pd

SALIDA = Path(__file__).resolve().parent.parent / 'data' / 'empleo' / 'empleo_publico_provincias.csv'
WEB = 'https://digital.gob.es/content/dam/portal-mtdfp/funcion-publica/rcp/boletin/'
ZIPS = {'2023-01': '2023_01/Microdatos_Enero_2023.zip',
        '2023-07': '2023_07/revision-agosto2026/Microdatos_Julio_2023.zip',
        '2024-01': '2024_01/revision-agosto-2026/Microdatos_Enero_2024.zip',
        '2024-07': '2024_07/revision-agosto2026/Microdatos_Julio_2024.zip',
        '2025-01': '2025_01/revision-agosto-2026/Microdatos_Enero_%202025.zip',
        '2025-07': '2025_07/revision-agosto2026/Microdatos_Julio_2025.zip',
        '2026-01': '2026_01/Microdatos_Enero_2026.zip'}

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
SECTOR = {'ADMINISTRACION DEL ESTADO': 'administracion general', 'ADMINISTRACION GENERAL CCAA': 'administracion general',
          'ADMINISTRACION AL SERVICIO DE JUZGADOS Y TRIBUNALES': 'justicia',
          'ADMINISTRACION AL SERVICIO DE TRIBUNALES DE INSTANCIA': 'justicia', 'ADMINISTRACION DE JUSTICIA': 'justicia',
          'FUERZAS ARMADAS Y FUERZAS Y CUERPOS DE SEGURIDAD DEL ESTADO': 'fuerzas armadas y seguridad',
          'POLICIA': 'policia autonomica', 'DOCENCIA NO UNIVERSITARIA': 'docencia no universitaria',
          'INSTITUCIONES SANITARIAS': 'sanidad', 'UNIVERSIDADES': 'universidades',
          'AYUNTAMIENTOS Y OTRAS ENTIDADES LOCALES Y SUS OOAA': 'ayuntamientos',
          'DIPUTACIONES CABILDOS Y CONSEJOS INSULARES Y SUS OOAA': 'diputaciones y cabildos'}
PERSONAL = {'PERSONAL FUNCIONARIO DE CARRERA': 'funcionario_carrera',
            'PERSONAL FUNCIONARIO INTERINO': 'funcionario_interino',
            'PERSONAL FUNCIONARIO EN FORMACION/ PRACTICAS': 'en_practicas',
            'PERSONAL LABORAL EN FORMACION/ PRACTICAS': 'en_practicas',
            'PERSONAL LABORAL FIJO': 'laboral_fijo', 'PERSONAL LABORAL FIJO DISCONTINUO': 'laboral_fijo',
            'PERSONAL LABORAL TEMPORAL': 'laboral_temporal',
            'PERSONAL EVENTUAL': 'otro', 'PERSONAL VARIO': 'otro', 'PERSONAL FUNCIONARIO PLAZAS NO ESCALAFONADAS': 'otro',
            'PERSONAL LABORAL INDEFINIDO NO FIJO': 'otro'}
COLUMNAS = ['funcionario_carrera', 'funcionario_interino', 'en_practicas', 'laboral_fijo', 'laboral_temporal', 'otro']


def leer(z, fecha):
    with zipfile.ZipFile(z) as f:
        nombre = next(n for n in f.namelist() if 'Total' in n and n.endswith('.xlsx'))
        with f.open(nombre) as x:
            d = pd.read_excel(x, sheet_name=0)
    d = d.rename(columns={'Suma de Num_NIF': 'n'})
    d = d.assign(fecha=fecha, prov_code=d['PROVINCIA'].map(PROVINCIAS), administracion=d['TIPO_ADMINISTRACION'].map(ADMIN),
                 sector=d['SUBTIPO_ADMINISTRACION'].map(SECTOR), personal=d['SUBTIPO_PERSONAL'].map(PERSONAL),
                 sexo=d['SEXO'].map({'H': 'hombres', 'M': 'mujeres'}))
    falta = d[['prov_code', 'administracion', 'sector', 'personal', 'sexo']].isna().any(axis=1)
    assert not falta.any(), d[falta].drop_duplicates(['PROVINCIA', 'SUBTIPO_ADMINISTRACION', 'SUBTIPO_PERSONAL']).head()
    return d


if __name__ == '__main__':
    carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    carpeta.mkdir(parents=True, exist_ok=True)
    partes = []
    for fecha, ruta in ZIPS.items():
        z = carpeta / f'epsap_{fecha}.zip'
        if not z.exists():
            print('descargando', WEB + ruta)
            urllib.request.urlretrieve(WEB + ruta, z)
        partes.append(leer(z, fecha))
    d = pd.concat(partes)
    t = (d.groupby(['fecha', 'prov_code', 'administracion', 'sector', 'sexo', 'personal'])['n'].sum()
         .unstack('personal', fill_value=0).reindex(columns=COLUMNAS, fill_value=0).reset_index())
    t.insert(5, 'efectivos', t[COLUMNAS].sum(axis=1))
    t.insert(2, 'provincia', t['prov_code'].map({v: k for k, v in PROVINCIAS.items()}))
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(SALIDA, index=False)
    print(len(t), 'filas'); print(t.groupby('fecha')['efectivos'].sum().to_string())
