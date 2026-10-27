"""Publica las listas del 29N en cuanto salen en el BOE. Lo lanza .github/workflows/listas.yml cada pocos minutos
la noche y la mañana de cada publicación; los demás días no hace nada.

- 28-10-2026: candidaturas presentadas.  - 3-11-2026: candidaturas proclamadas.

Busca en el sumario del día los documentos de candidaturas al Congreso, los lee y solo sigue si están las 52 juntas
provinciales y las listas al Congreso tienen al menos tantos titulares como escaños la provincia (si no, sale sin
tocar nada y avisa: lo revisa una persona; alguna lista presentada incompleta se admite, más del 5 % no). Si todo cuadra, rehace la sección y escribe «publicar=1» para el workflow.

Uso, desde la raíz:  python3 listas-electorales-29n/src/automatico.py [AAAA-MM-DD]
"""
import json, os, pathlib, subprocess, sys
from datetime import datetime
from zoneinfo import ZoneInfo

RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import boe  # noqa: E402

FECHAS = {'2026-10-28': 'presentadas', '2026-11-03': 'proclamadas'}


def salida(clave, valor):
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f'{clave}={valor}\n')


def main():
    hoy = sys.argv[1] if len(sys.argv) > 1 else datetime.now(ZoneInfo('Europe/Madrid')).date().isoformat()
    fase = FECHAS.get(hoy)
    if not fase:
        print(f'{hoy}: no es día de listas en el BOE')
        return
    destino = boe.DESTINO / f'2026-{fase}.json'
    if destino.exists():
        print(f'Ya están las listas {fase}')
        return
    try:
        docs = boe.buscar(hoy.replace('-', ''))
    except SystemExit:   # el sumario del día aún no existe
        print(f'El BOE del {hoy} aún no está publicado')
        return
    docs = [(i, t) for i, t in docs if (fase == 'presentadas') == ('presentadas' in t.lower()) and 'correcci' not in t.lower()]
    if not docs:
        print(f'El BOE del {hoy} aún no trae las candidaturas {fase}')
        return
    print('Documentos:', docs)
    cands, falta = boe.guarda('2026', [i for i, _ in docs], fase)
    escanos = {p: v['escanos_total'] for p, v in json.loads((RAIZ / 'previsiones/datos/publico/escenario-base.json').read_text())['provincias'].items()}
    cortas = [(c['prov'], c['siglas'], len(c['titulares'])) for c in cands
              if c['camara'] == 'congreso' and not c.get('no_proclamada') and len(c['titulares']) < escanos.get(c['prov'], 0)]
    n_cong = sum(1 for c in cands if c['camara'] == 'congreso' and not c.get('no_proclamada'))
    if falta or len(cortas) > 0.05 * n_cong:   # alguna lista presentada incompleta es normal; muchas, un error de lectura
        destino.unlink()
        print(f'::error::No se publica: faltan provincias {falta}; listas incompletas {cortas[:10]}')
        salida('revisar', '1')
        return
    subprocess.run([sys.executable, 'listas-electorales-29n/src/construir.py'], check=True, cwd=RAIZ)
    subprocess.run([sys.executable, 'src/iconos.py'], check=True, cwd=RAIZ)
    salida('publicar', '1')


if __name__ == '__main__':
    main()
