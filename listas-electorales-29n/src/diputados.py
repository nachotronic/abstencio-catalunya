"""Diputados de la legislatura que acaba (XV, elegida el 23J de 2023), del portal de datos abiertos del Congreso.

Junta los que siguen de alta (la Diputación Permanente tras la disolución) y los que causaron baja, con su
circunscripción, formación y fechas, en listas-electorales-29n/datos/diputados-xv.json. construir.py lo usa para marcar a los
candidatos que ya se sientan en el Congreso.

Uso, desde la raíz:  python3 listas-electorales-29n/src/diputados.py
"""
import json, pathlib, re, urllib.request

RAIZ = pathlib.Path(__file__).resolve().parents[2]
PORTAL = 'https://www.congreso.es/es/opendata/diputados'


def baja(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (mapaelectoral.es)'}), timeout=60).read()


def main():
    portal = baja(PORTAL).decode('utf-8', 'replace')
    out = []
    for tipo in ('DiputadosActivos', 'DiputadosDeBaja'):
        ruta = re.search(rf'href="(/webpublica/opendata/diputados/{tipo}__\d+\.json)"', portal).group(1)
        for d in json.loads(baja('https://www.congreso.es' + ruta)):
            ap, _, nom = d['NOMBRE'].partition(',')
            out.append({'nombre': f'{nom.strip()} {ap.strip()}'.strip(), 'circ': d['CIRCUNSCRIPCION'], 'formacion': d['FORMACIONELECTORAL'],
                        'alta': d.get('FECHAALTA', ''), 'baja': d.get('FECHABAJA', '')})
    fecha = re.search(r'DiputadosActivos__(\d{8})', portal).group(1)
    (RAIZ / 'listas-electorales-29n/datos/diputados-xv.json').write_text(json.dumps({'fuente': PORTAL, 'descargado': f'{fecha[:4]}-{fecha[4:6]}-{fecha[6:]}', 'diputados': out},
                                                                    ensure_ascii=False, indent=0))
    print(f'diputados: {len(out)} personas con escaño en la XV legislatura')


if __name__ == '__main__':
    main()
