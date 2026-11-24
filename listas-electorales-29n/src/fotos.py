"""Fotos oficiales de los candidatos que han sido diputados en la XV legislatura.

Solo la foto de la ficha de congreso.es de la XV, del mismo codParlamentario con el que bios_datos.py ata a la persona.
Se guarda el archivo tal cual lo sirve el Congreso (sin recortar ni recomprimir: su aviso legal pide no alterar la
información, citar la fuente y la fecha). Escribe datos/fotos.json, que lee biografias.py.
"""
import json, pathlib, re, time, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

RAIZ = pathlib.Path(__file__).resolve().parents[2]
CARPETA = RAIZ / 'listas-electorales-29n'
CACHE = CARPETA / 'datos/.cache-congreso'
FOTOS = CARPETA / 'fotos'
IMG = 'https://www.congreso.es/docu/imgweb/diputados/{}_15.jpg'
UA = {'User-Agent': 'Mozilla/5.0 (mapaelectoral.es)', 'Referer': 'https://www.congreso.es/'}


def main():
    of = json.loads((CARPETA / 'datos/biografias-oficiales.json').read_text())['personas']
    previo = json.loads((CARPETA / 'datos/fotos.json').read_text()) if (CARPETA / 'datos/fotos.json').exists() else {}
    FOTOS.mkdir(exist_ok=True)
    out = {}
    for clave, x in sorted(of.items()):
        url = x.get('ficha_congreso') or ''
        m = re.search(r'codParlamentario=(\d+)&idLegislatura=XV\b', url)
        if not m:
            continue
        cod = m.group(1)
        ficha = CACHE / f'{cod}.html'
        if not ficha.exists() or f'imgweb/diputados/{cod}_15.jpg' not in ficha.read_text(encoding='utf-8', errors='replace'):
            continue   # la ficha no enseña foto: no se busca otra
        f = FOTOS / f'{cod}_15.jpg'
        if not f.exists():
            datos = urllib.request.urlopen(urllib.request.Request(IMG.format(cod), headers=UA), timeout=60).read()
            assert datos[:3] == b'\xff\xd8\xff', f'{clave}: no es un JPEG'
            f.write_bytes(datos)
            time.sleep(0.3)
        out[clave] = {'archivo': f.name, 'nombre': x['nombre'], 'fuente': IMG.format(cod), 'ficha': url,
                      'consultada': previo.get(clave, {}).get('consultada') or datetime.now(ZoneInfo('Europe/Madrid')).date().isoformat()}
    (CARPETA / 'datos/fotos.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    peso = sum(p.stat().st_size for p in FOTOS.glob('*.jpg'))
    print(f'fotos: {len(out)} candidatos con foto oficial del Congreso; {peso / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
