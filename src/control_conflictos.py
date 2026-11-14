"""Control de marcadores de conflicto de Git en los ficheros publicados (repaso del 14-11-2026, a raíz de #581:
la portada estuvo en directo con «<<<<<<< HEAD», «=======» y «>>>>>>> origin/main» del 12-11 al 13-11 y verificar
pasó en verde). Busca en todo el repositorio líneas que empiecen por esos marcadores en HTML, JS, JSON, CSS, XML,
Python, TXT y CSV. Si encuentra alguno, sale con error y el PR queda en rojo.
Uso, desde la raíz: python3 src/control_conflictos.py [--resumen FICHERO]
"""
import argparse
import subprocess
import sys

PATRON = r'^(<{7} |={7}$|>{7} )'
TIPOS = ['*.html', '*.js', '*.mjs', '*.json', '*.css', '*.xml', '*.py', '*.txt', '*.csv']


def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument('--resumen', help='fichero Markdown donde añadir el informe (GITHUB_STEP_SUMMARY)')
    a = ap.parse_args()
    r = subprocess.run(['git', 'grep', '-nE', PATRON, '--', *TIPOS], capture_output=True, text=True)
    if r.returncode > 1:
        print(r.stderr, file=sys.stderr)
        return 2
    lineas = [l for l in r.stdout.splitlines() if l.strip()]
    if lineas:
        ficheros = sorted({l.split(':', 1)[0] for l in lineas})
        texto = (f'## Marcadores de conflicto de Git: {len(lineas)} en {len(ficheros)} ficheros\n\n'
                 + '\n'.join(f'- `{l[:200]}`' for l in lineas[:100]) + '\n')
    else:
        texto = '## Marcadores de conflicto de Git: ninguno\n'
    print(texto)
    if a.resumen:
        with open(a.resumen, 'a', encoding='utf-8') as f:
            f.write(texto + '\n')
    return 1 if lineas else 0


if __name__ == '__main__':
    sys.exit(principal())
