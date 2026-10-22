"""Extrae los originales del ZIP recibido, verificando su integridad."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('zip', type=Path)
    parser.add_argument('destino', type=Path)
    args = parser.parse_args()
    inventory = json.loads(Path(__file__).with_name('inventario.json').read_text())
    with zipfile.ZipFile(args.zip) as archive:
        # Validar todo antes de escribir; no aceptar rutas del ZIP como destinos.
        for entry in inventory['archivos']:
            name = entry['archivo']
            if Path(name).name != name:
                raise ValueError(f'Ruta no permitida: {name}')
            data = archive.read(name)
            if hashlib.sha256(data).hexdigest() != entry['sha256']:
                raise ValueError(f'SHA-256 incorrecto: {name}')
        args.destino.mkdir(parents=True, exist_ok=True)
        for entry in inventory['archivos']:
            path = args.destino / entry['archivo']
            if path.exists():
                if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
                    raise FileExistsError(f'No se sobrescribe archivo distinto: {path}')
            else:
                path.write_bytes(archive.read(entry['archivo']))
    print(f"Verificados y disponibles: {len(inventory['archivos'])} archivos")


if __name__ == '__main__':
    main()
