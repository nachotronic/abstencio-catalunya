"""Europeas de 2024 por sección censal, con los partidos nuevos separados (Sumar, Podemos, SALF).

En las descargas de la pieza de las generales, Sumar y Podemos van juntos (familia «SUMAR») y SALF va en «Otros».
Este script vuelve a los votos por mesa de Interior (vía pollspaindata) y los agrega por sección sin juntar nada.

Uso, desde la raíz:  python3 previsiones/src/europeas2024.py
Lee  $GENERALES_EXTRA (por defecto /mnt/project-files/generales/datos/extra): raw_*_E2024.parquet
Escribe $PREVISIONES_BASE/europeas2024_secciones.csv (por defecto /mnt/project-files/previsiones/base)
"""
import os, pathlib, re
import pandas as pd

EXTRA = pathlib.Path(os.environ.get('GENERALES_EXTRA', '/mnt/project-files/generales/datos/extra'))
SALIDA = pathlib.Path(os.environ.get('PREVISIONES_BASE', '/mnt/project-files/previsiones/base'))

# Lista de 2024 -> partido. Lo que no está aquí va a OTROS.
REGLAS = [
    ('PP', r'^PP$'), ('PSOE', r'^PSOE$|^PSC$'), ('VOX', r'^VOX$'), ('SALF', r'SE ACAB[OÓ] LA FIESTA'),
    ('PODEMOS', r'^PODEMOS$'), ('SUMAR', r'SUMAR'), ('JUNTS', r'^JUNTS'), ('ERC', r'^ERC|^ERPV|^ARA M[EÉ]S'),
    ('BILDU', r'^EH BILDU'), ('PNV', r'^EAJ-PNV'), ('BNG', r'^BNG'), ('CC', r'^CCa$'), ('CS', r'^Cs$'), ('PACMA', r'^PACMA$'),
]
PARTIDOS = [p for p, _ in REGLAS] + ['OTROS']


def partido(abrev):
    for p, pat in REGLAS:
        if re.search(pat, abrev):
            return p
    return 'OTROS'


def main():
    cand = pd.read_parquet(EXTRA / 'raw_candidacies_E2024.parquet')
    cand['partido'] = cand.abbrev_candidacies.map(partido)
    v = pd.read_parquet(EXTRA / 'raw_candidacies_poll_E2024.parquet')
    v['partido'] = v.id_candidacies.map(cand.set_index('id_candidacies').partido)
    v['tract_code'] = v.cod_INE_prov + v.cod_INE_mun + v.cod_mun_district + v.cod_sec
    sec = v.pivot_table(index='tract_code', columns='partido', values='ballots', aggfunc='sum', fill_value=0)
    m = pd.read_parquet(EXTRA / 'raw_poll_stations_E2024.parquet')
    m['tract_code'] = m.cod_INE_prov + m.cod_INE_mun + m.cod_mun_district + m.cod_sec
    m = m.groupby('tract_code')[['census_INE', 'blank_ballots', 'invalid_ballots', 'party_ballots']].sum()
    out = sec.reindex(columns=PARTIDOS, fill_value=0).join(m)
    out = out.rename(columns={'census_INE': 'censo', 'blank_ballots': 'blancos', 'invalid_ballots': 'nulos', 'party_ballots': 'candidaturas'})
    out['validos'] = out.candidaturas + out.blancos
    SALIDA.mkdir(parents=True, exist_ok=True)
    out.reset_index().to_csv(SALIDA / 'europeas2024_secciones.csv', index=False)
    tot = out[PARTIDOS].sum()
    print(len(out), 'secciones;', (tot / out.validos.sum() * 100).round(2).to_dict())


if __name__ == '__main__':
    main()
