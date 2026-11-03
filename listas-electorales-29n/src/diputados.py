"""Diputados de la legislatura que acaba (XV, elegida el 23J de 2023), del portal de datos abiertos del Congreso.

Junta los que siguen de alta (la Diputación Permanente tras la disolución) y los que causaron baja, con su
circunscripción, formación y fechas, en listas-electorales-29n/datos/diputados-xv.json. construir.py lo usa para marcar a los
candidatos que ya se sientan en el Congreso. De la ficha de cada diputado en congreso.es toma también los enlaces a sus
declaraciones de actividades, de bienes y rentas y de intereses económicos (las fichas de candidato los enlazan).

Uso, desde la raíz:  python3 listas-electorales-29n/src/diputados.py
"""
import html, json, pathlib, re, time, urllib.parse, urllib.request

RAIZ = pathlib.Path(__file__).resolve().parents[2]
PORTAL = 'https://www.congreso.es/es/opendata/diputados'


def baja(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (mapaelectoral.es)'}), timeout=60).read()


BUSCADOR = ('https://www.congreso.es/es/busqueda-de-diputados?p_p_id=diputadomodule&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view'
            '&p_p_resource_id=searchDiputados&p_p_cacheability=cacheLevelPage')
FICHA = ('https://www.congreso.es/es/busqueda-de-diputados?p_p_id=diputadomodule&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view'
         '&_diputadomodule_mostrarFicha=true&codParlamentario={}&idLegislatura=XV&mostrarAgenda=false')


def codigos():
    """«Apellidos, Nombre» → código del diputado en el buscador del Congreso (XV legislatura, altas y bajas)."""
    datos = urllib.parse.urlencode({'_diputadomodule_idLegislatura': 15, '_diputadomodule_genero': 0, '_diputadomodule_grupo': 'all',
                                    '_diputadomodule_tipo': 2, '_diputadomodule_nombre': '', '_diputadomodule_apellidos': '',
                                    '_diputadomodule_formacion': 'all', '_diputadomodule_filtroProvincias': '[]',
                                    '_diputadomodule_nombreCircunscripcion': ''}).encode()
    r = urllib.request.Request(BUSCADOR, datos, {'User-Agent': 'Mozilla/5.0 (mapaelectoral.es)'})
    return {d['apellidosNombre']: d['codParlamentario'] for d in json.load(urllib.request.urlopen(r, timeout=60))['data']}


def declaraciones(cod):
    """Enlaces de la ficha: declaración de actividades y las últimas de bienes y rentas y de intereses económicos."""
    t = baja(FICHA.format(cod)).decode('utf-8', 'replace')
    out = {}
    for href, txt in re.findall(r'<a href="(/doc(?:inte|bienes|acteco)/[^"]+\.pdf)"[^>]*>\s*([^<]+?)\s*</a>', t):
        txt = html.unescape(txt)
        for clave, prefijo in (('actividades', 'Declaración de Actividades'), ('bienes', 'Declaración de Bienes y Rentas'), ('intereses', 'Declaración de Intereses Económicos')):
            if txt.startswith(prefijo):
                fecha = (re.findall(r'_(\d{8})\.pdf$', href) or [''])[0]   # de las varias que puede haber, la más reciente
                if clave not in out or fecha > out[clave][0]:
                    out[clave] = (fecha, 'https://www.congreso.es' + href)
    return {k: {'url': u, 'fecha': f'{f[:4]}-{f[4:6]}-{f[6:]}' if f else ''} for k, (f, u) in out.items()}


def main():
    portal = baja(PORTAL).decode('utf-8', 'replace')
    out = []
    for tipo in ('DiputadosActivos', 'DiputadosDeBaja'):
        ruta = re.search(rf'href="(/webpublica/opendata/diputados/{tipo}__\d+\.json)"', portal).group(1)
        for d in json.loads(baja('https://www.congreso.es' + ruta)):
            ap, _, nom = d['NOMBRE'].partition(',')
            out.append({'nombre': f'{nom.strip()} {ap.strip()}'.strip(), 'circ': d['CIRCUNSCRIPCION'], 'formacion': d['FORMACIONELECTORAL'],
                        'alta': d.get('FECHAALTA', ''), 'baja': d.get('FECHABAJA', ''), '_clave': d['NOMBRE']})
    cods = codigos()
    for x in out:
        cod = cods.get(x.pop('_clave'))
        if cod:
            x['ficha'] = FICHA.format(cod)
            x['declaraciones'] = declaraciones(cod)
            time.sleep(0.3)
    fecha = re.search(r'DiputadosActivos__(\d{8})', portal).group(1)
    (RAIZ / 'listas-electorales-29n/datos/diputados-xv.json').write_text(json.dumps({'fuente': PORTAL, 'descargado': f'{fecha[:4]}-{fecha[4:6]}-{fecha[6:]}', 'diputados': out},
                                                                    ensure_ascii=False, indent=0))
    print(f'diputados: {len(out)} personas con escaño en la XV legislatura')


if __name__ == '__main__':
    main()
