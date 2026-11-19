"""Cuenta cuántas veces sale cada tema en los programas electorales del 29N (PP, PSOE, Vox, Frente Amplio).

Descarga los cuatro PDF (URL en PROGRAMAS), los pasa a texto con pdftotext y cuenta las apariciones de cada
patrón por cada 10.000 palabras. Texto normalizado: minúsculas, sin tildes, sin guiones de fin de línea.
Escribe datos/programas_29n.json, que lee programas_29n.py.
Uso, desde la raíz: python3 actualidad/src/resumenes/programas_29n_menciones.py
"""
import json
import re
import subprocess
import tempfile
import unicodedata
import urllib.request
from pathlib import Path

AQUI = Path(__file__).parent
PROGRAMAS = {
    'PP': 'https://www.pp.es/wp-content/uploads/2026/11/PROGRAMA-ELECTORAL-PP-2026-RECONSTRUCCION-NACIONAL.pdf',
    'PSOE': 'https://www.elindependiente.com/wp-content/uploads/2026/11/PROGRAMAPSOE29N26.pdf',
    'VOX': 'https://www.elindependiente.com/wp-content/uploads/2026/11/programa-elecct-vox.pdf',
    'FA': 'https://www.democrata.es/uploads/s1/35/42/91/4/programafrenteamplio.pdf',
}
TEMAS = {
    'Vivienda': r'\bvivienda',
    'Impuestos': r'\bimpuest|\bfiscal|\birpf\b|\biva\b',
    'Inmigración': r'\b(in)?migra(cion|ntes?|torio|toria)',
    'Pensiones': r'\bpension',
    'Sanidad': r'\bsanidad|\bsanitari',
    'Igualdad y violencia machista': r'\bigualdad|violencia de genero|violencia machista|feminis',
    'Clima y energía': r'\bclima|\bnuclear|\brenovabl|\benergia',
}


def norm(s):
    s = re.sub(r'-\n\s*', '', s)
    return unicodedata.normalize('NFKD', s.lower()).encode('ascii', 'ignore').decode()


def main():
    out = {'fuentes': PROGRAMAS, 'temas': TEMAS, 'palabras': {}, 'paginas': {}, 'veces': {}, 'tasa': {}}
    with tempfile.TemporaryDirectory() as d:
        for k, url in PROGRAMAS.items():
            pdf = Path(d) / f'{k}.pdf'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            pdf.write_bytes(urllib.request.urlopen(req, timeout=120).read())
            info = subprocess.run(['pdfinfo', str(pdf)], capture_output=True, text=True).stdout
            out['paginas'][k] = int(re.search(r'Pages:\s+(\d+)', info).group(1))
            t = norm(subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True).stdout)
            w = len(re.findall(r'[a-z]{2,}', t))
            out['palabras'][k] = w
            for tema, pat in TEMAS.items():
                v = len(re.findall(pat, t))
                out['veces'].setdefault(tema, {})[k] = v
                out['tasa'].setdefault(tema, {})[k] = round(v / w * 10000, 1)
    (AQUI / 'datos/programas_29n.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps(out['tasa'], ensure_ascii=False))


if __name__ == '__main__':
    main()
