"""Agrupación de candidaturas del Congreso en familias comparables 2015-2026.

Criterios (documentados en LEEME.md):
- PP incluye sus coaliciones regionales (PP-FORO, PP-PAR, UPN-PP) y Navarra Suma (NA+, 2019).
- PSOE incluye PSC, PSE-EE, PSdeG, PSIB, PSN.
- "Sumar/Podemos" es el espacio a la izquierda del PSOE: Podemos y sus confluencias
  (En Comú, Compromís-Podemos, En Marea), IU-Unidad Popular (2015), Unidas Podemos (2016-2019)
  y Sumar (2023). Más País y Más Compromís (2019N) quedan en "Otros".
- BNG incluye NÓS-Candidatura Galega (2015).
- Junts agrupa DL (2015), CDC (2016) y JxCat-Junts (2019-2023).
"""
import re

FAMILIAS = [  # código, etiqueta, color
    ('PP', 'PP', '#1d84ce'),
    ('PSOE', 'PSOE', '#e30613'),
    ('VOX', 'Vox', '#5ac035'),
    ('SUMAR', 'Sumar / Podemos', '#a2275f'),
    ('CS', 'Ciudadanos', '#eb6109'),
    ('ERC', 'ERC', '#f5b324'),
    ('JUNTS', 'Junts', '#20c0b2'),
    ('PNV', 'PNV', '#2b8a3e'),
    ('BILDU', 'EH Bildu', '#a5c400'),
    ('BNG', 'BNG', '#7ab8e6'),
    ('CC', 'Coalición Canaria', '#f7d417'),
    ('OTROS', 'Otros', '#9a9a9a'),
]
CODIGOS = [f[0] for f in FAMILIAS]

_REGLAS = [
    ('PP', r"^(PP\b|PP-|UPN-PP|NA\+)"),
    ('PSOE', r"PSOE|^PSC\b|^PSC-|^PSE-EE|^PSDEG|^PSIB|^PSN"),
    ('VOX', r"^VOX$"),
    ('CS', r"^(C'S|C´S|CS)$"),
    ('SUMAR', r"^PODEMOS|^EN COMÚ|^ECP|SUMAR|UPEC|^UNIDAD POPULAR|^IU\b|^IULV|^UNIDA|^IU-|^EUPV-UPEC"),
    ('ERC', r"^ERC"),
    ('JUNTS', r"^(DL|CDC)$|^JXCAT|^JUNTS"),
    ('PNV', r"^EAJ-PNV"),
    ('BILDU', r"^EH BILDU"),
    ('BNG', r"^B\.?N\.?G\.?$|^BNG|^NÓS$"),
    ('CC', r"^CCA|^CC-|^NC-CCA|^CC$"),
]


def familia(abrev: str, nombre: str = '') -> str:
    a = (abrev or '').strip().upper()
    for cod, pat in _REGLAS:
        if re.search(pat, a):
            return cod
    n = (nombre or '').upper()
    if 'PARTIDO SOCIALISTA' in n or 'SOCIALISTES' in n:
        return 'PSOE'
    if n.startswith('PARTIDO POPULAR'):
        return 'PP'
    return 'OTROS'
