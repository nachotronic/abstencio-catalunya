"""Agrupación de candidaturas del Congreso en familias comparables 2015-2026.

Criterios (documentados en LEEME.md):
- PP incluye sus coaliciones regionales (PP-FORO, PP-PAR, UPN-PP) y Navarra Suma (NA+, 2019).
- PSOE incluye PSC, PSE-EE, PSdeG, PSIB, PSN.
- "Sumar/Podemos/IU" es el espacio a la izquierda del PSOE: IU y sus federaciones (2004-2011), Podemos y sus confluencias
  (En Comú, Compromís-Podemos, En Marea), IU-Unidad Popular (2015), Unidas Podemos (2016-2019)
  y Sumar (2023). Más País y Más Compromís (2019N) quedan en "Otros".
- BNG incluye NÓS-Candidatura Galega (2015).
- Junts agrupa CiU (2004-2011), DL (2015), CDC (2016) y JxCat-Junts (2019-2023).
- EH Bildu incluye Amaiur (2011). UPyD va aparte (2008-2016).
"""
import re

FAMILIAS = [  # código, etiqueta, color
    ('PP', 'PP', '#1d84ce'),
    ('PSOE', 'PSOE', '#e30613'),
    ('VOX', 'Vox', '#5ac035'),
    ('SUMAR', 'Sumar / Podemos / IU', '#a2275f'),
    ('CS', 'Ciudadanos', '#eb6109'),
    ('UPYD', 'UPyD', '#e5007d'),
    ('ERC', 'ERC', '#f5b324'),
    ('JUNTS', 'Junts / CiU', '#20c0b2'),
    ('PNV', 'PNV', '#2b8a3e'),
    ('BILDU', 'EH Bildu / Amaiur', '#a5c400'),
    ('BNG', 'BNG', '#7ab8e6'),
    ('CC', 'Coalición Canaria', '#f7d417'),
    ('OTROS', 'Otros', '#9a9a9a'),
]
CODIGOS = [f[0] for f in FAMILIAS]

_REGLAS = [
    ('PP', r"^(PP\b|PP-|P\.P\.|UPN-PP|NA\+)"),
    ('PSOE', r"PSOE|^PSC\b|^PSC-|^PSE-EE|^PSDEG|^PSIB|^PSN"),
    ('VOX', r"^VOX$"),
    ('CS', r"^(C'S|C´S|CS)$"),
    ('UPYD', r"^UPYD$"),
    ('SUMAR', r"^PODEMOS|^EN COMÚ|^ECP|SUMAR|UPEC|^UNIDAD POPULAR|^IU\b|^IULV|^UNIDA|^IU-|^EUPV-UPEC"),
    ('ERC', r"^ERC|^ESQUERRA$"),
    ('JUNTS', r"^(DL|CDC|CIU)$|^JXCAT|^JUNTS"),
    ('PNV', r"^EAJ-PNV|^E\.A\.J\.-P\.N\.V\."),
    ('BILDU', r"^EH BILDU|^AMAIUR$"),
    ('BNG', r"^B\.?N\.?G\.?$|^BNG|^NÓS$"),
    ('CC', r"^CCA|^CC-|^NC-CCA|^CC$"),
]


def familia(abrev: str, nombre: str = '') -> str:
    a = (abrev or '').strip().upper()
    for cod, pat in _REGLAS:
        if re.search(pat, a):
            return cod
    n = (nombre or '').upper()
    # IU y sus federaciones (2004-2011) se reconocen mejor por el nombre que por las siglas
    if re.search(r"IZQUIERDA UNIDA|ESQUERRA UNIDA|ESQUERDA UNIDA|EZKER BATUA|IZQUIERDA PLURAL|ESQUERRA PLURAL|ESQUERDA PLURAL|IZQUIERDA-EZKERRA", n):
        return 'SUMAR'
    if 'PARTIDO SOCIALISTA' in n or 'SOCIALISTES' in n:
        return 'PSOE'
    if n.startswith('PARTIDO POPULAR'):
        return 'PP'
    return 'OTROS'
