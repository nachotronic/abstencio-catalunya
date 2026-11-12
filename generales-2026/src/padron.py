"""Población de cada municipio: cifras oficiales del padrón municipal del INE a 1 de enero de 2023.

Hasta el 12-11-2026, la columna `poblacion` de los municipios salía del Atlas de Distribución de Renta de los Hogares
(ADRH 2023), que en los pueblos muy pequeños se aparta mucho del padrón (Tresviso, 5 frente a 58). Desde entonces, la
población de cada municipio es la oficial del padrón (INE, Revisión del Padrón municipal, tablas 2854-2909, una por
provincia: «<Provincia>: Población por municipios y sexo»). Las secciones censales siguen con la población del Atlas,
porque el padrón oficial no baja a sección, y también salen del Atlas los adultos (población por el porcentaje de
menores) con los que se calculan los adultos sin derecho a voto, para que municipio y sección cuadren entre sí.

Uso:
  python3 padron.py --descargar    vuelve a bajar las cifras del INE a padron_2023_municipios.csv
  python3 padron.py                pone la población del padrón en descargas/municipios.csv, data/municipios.json
                                   y data/municipios-ligero.json (construir.py ya la usa al reconstruir)
"""
import csv, json, os, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(AQUI)
CSV = os.path.join(AQUI, 'padron_2023_municipios.csv')
FECHA = '20230101'
TABLAS = range(2854, 2910)   # una por provincia (2908 Ceuta, 2909 Melilla); algunos números del rango no existen
FUENTE = 'padrón municipal del INE (1 de enero de 2023)'


def descargar():
    filas = {}
    for t in TABLAS:
        url = f'https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{t}?date={FECHA}&tip=AM'
        try:
            d = json.load(urllib.request.urlopen(url, timeout=60))
        except Exception:
            continue
        if not isinstance(d, list):
            continue
        for s in d:
            md = {m['T3_Variable']: m for m in s.get('MetaData', [])}
            mun, sexo = md.get('Municipios'), md.get('Sexo', {}).get('Nombre')
            if not mun or sexo != 'Total' or len(mun['Codigo']) != 5:
                continue
            v = [x['Valor'] for x in s['Data'] if x['Anyo'] == 2023]
            if v:
                filas[mun['Codigo']] = (mun['Nombre'], int(v[0]))
    assert len(filas) == 8131, len(filas)
    with open(CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['mun_code', 'municipio_ine', 'poblacion_padron_2023'])
        for c in sorted(filas):
            w.writerow([c, *filas[c]])
    print('padrón 2023:', len(filas), 'municipios,', sum(v for _, v in filas.values()), 'habitantes')


def padron():
    """{código INE: habitantes a 1-1-2023}"""
    with open(CSV, newline='', encoding='utf-8') as f:
        return {r['mun_code']: int(r['poblacion_padron_2023']) for r in csv.DictReader(f)}


def main(web=os.path.join(BASE, 'data'), desc=os.path.join(BASE, 'descargas')):
    p = padron()
    # descarga de municipios
    f = os.path.join(desc, 'municipios.csv')
    with open(f, newline='', encoding='utf-8') as fh:
        r = csv.reader(fh)
        cab = next(r)
        filas = list(r)
    i, k = cab.index('poblacion'), cab.index('mun_code')
    for x in filas:
        x[i] = str(float(p[x[k]]))
    with open(f, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(cab)
        w.writerows(filas)
    # datos del mapa
    for nom in ('municipios.json', 'municipios-ligero.json'):
        f = os.path.join(web, nom)
        if not os.path.exists(f):
            continue
        d = json.load(open(f))
        d['poblacion'] = [p[c] for c in d['cod']]
        json.dump(d, open(f, 'w'), separators=(',', ':'), ensure_ascii=False)
    print('población del padrón 2023 en', len(filas), 'municipios')


if __name__ == '__main__':
    descargar() if '--descargar' in sys.argv else main()
