"""Imagen principal (1280x720) para las piezas sin ilustración ni foto: su primer gráfico de proporción apaisada.

Uso, con el sitio servido en http://localhost:8765 (python3 -m http.server 8765 desde la raíz):
    python3 actualidad/src/graficos_principales.py slug1 slug2 ...
Escribe img/actualidad/fotos/<slug>-grafico.jpg y añade pie (título del gráfico) y fuente a graficos_principales.json.
"""
import json, os, re, subprocess, sys, tempfile
from PIL import Image

SRC = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(SRC))
JSON = os.path.join(SRC, 'graficos_principales.json')

if __name__ == '__main__':
    tmp = tempfile.mkdtemp()
    out = subprocess.run(['node', os.path.join(SRC, 'graficos_principales.mjs')] + sys.argv[1:], capture_output=True, text=True,
                         env={**os.environ, 'DIR_GRAFICOS': tmp}, check=True).stdout
    meta = json.load(open(JSON, encoding='utf-8')) if os.path.exists(JSON) else {}
    for s, v in json.loads(out).items():
        if not v:
            continue
        r = [x['h'] / x['w'] for x in v]
        i = next((k for k, x in enumerate(r) if 0.35 <= x <= 0.8), min(range(len(r)), key=lambda k: abs(r[k] - 0.5625)))
        im = Image.open(os.path.join(tmp, f'{s}-{i}.png')).convert('RGB')
        sc = min(1248 / im.width, 688 / im.height)
        im2 = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
        c = Image.new('RGB', (1280, 720), im.getpixel((3, 3)))
        c.paste(im2, ((1280 - im2.width) // 2, (720 - im2.height) // 2))
        c.save(os.path.join(RAIZ, 'img', 'actualidad', 'fotos', f'{s}-grafico.jpg'), quality=88)
        f = re.split(r'(?<=[a-zó\)])\. ', re.sub(r'^Fuentes?:\s*', '', v[i]['fuente']).strip())[0].rstrip('.')
        meta[s] = {'pie': v[i]['titulo'].rstrip('.') + '.', 'fuente': re.sub(r';\s*cálculo propio.*$', '', f)}
    json.dump(meta, open(JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
