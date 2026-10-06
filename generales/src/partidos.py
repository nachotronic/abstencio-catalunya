"""Agrupación de candidaturas en familias comparables (Congreso 2004-2026, municipales 2007-2023, europeas 2019-2024).

Criterios (documentados en LEEME.md):
- PP incluye sus coaliciones regionales (PP-FORO, PP-PAR, UPN-PP), Navarra Suma (NA+, 2019) y UPN cuando va sola
  (2023 y municipales), para que Navarra no cambie de familia según haya o no coalición.
- PSOE incluye PSC, PSE-EE, PSdeG, PSIB, PSN.
- "Sumar/Podemos/IU" es el espacio a la izquierda del PSOE: IU y sus federaciones (2004-2011), Podemos y sus confluencias
  (En Comú, Compromís-Podemos, En Marea), IU-Unidad Popular (2015), Unidas Podemos (2016-2019)
  y Sumar (2023). Compromís y Más País / Más Madrid también, vayan solos o en coalición, porque se integraron en
  coaliciones de este espacio (2015, 2016, 2023) y si no, el cambio de coalición parecería un cambio de voto.
- BNG incluye NÓS-Candidatura Galega (2015).
- Junts agrupa CiU (2004-2011), DL (2015), CDC (2016) y JxCat-Junts (2019-2023).
- EH Bildu incluye Amaiur (2011) y Bildu (municipales 2011). UPyD va aparte (2008-2016).
- Municipales: las listas locales de cada partido (PSC, PSOE-A, ERC-AM, Junts-Compromís Municipal…) van con su
  partido, y las confluencias con Podemos o IU (Ahora Madrid, Barcelona en Comú, Zaragoza en Común, Marea
  Atlántica…), Compromís y Más Madrid con "Sumar/Podemos/IU". El PRC y el resto de regionalistas, en "Otros".
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
    ('PP', r"^(PP\b|PP-|P\.P\.|UPN-PP|UPN$|NA\+)"),
    ('PSOE', r"PSOE|^PSC\b|^PSC-|^PSE-EE|^PSDEG|^PSIB|^PSN"),
    ('VOX', r"^VOX$"),
    ('CS', r"^(C'S|C´S|CS)$|-CS$"),
    ('UPYD', r"^UPYD$"),
    ('SUMAR', r"^PODEMOS|^EN COMÚ|^ECP|SUMAR|UPEC|^UNIDAD POPULAR|^IU\b|^IULV|^UNIDA|^IU-|^EUPV-UPEC"),
    ('ERC', r"^ERC|^ESQUERRA$"),
    ('JUNTS', r"^(DL|CDC|CIU)$|^JXCAT|^JUNTS|[- ]JUNTS$|^CM$|-CM$"),
    ('PNV', r"^EAJ-PNV|^E\.A\.J\.-P\.N\.V\."),
    ('BILDU', r"^EH ?BILDU|^BILDU|^AMAIUR$"),
    ('BNG', r"^B\.?N\.?G\.?$|^BNG|^NÓS$"),
    ('CC', r"^CCA|^CC-|^NC-CCA|^CC$"),
]


# Por el nombre completo, cuando las siglas no bastan (sobre todo en municipales)
_NOMBRES = [
    ('ERC', r"ESQUERRA REPUBLICANA"),
    ('JUNTS', r"CONVERG[EÈ]NCIA I UNI[OÓ]|^JUNTS\b|JUNTS PER CATALUNYA|TRIAS PER BARCELONA"),
    ('PNV', r"PARTIDO NACIONALISTA VASCO|EUZKO ALDERDI JELTZALEA"),
    ('BILDU', r"^BILDU|EUSKAL HERRIA BILDU"),
    ('PSOE', r"PSOE"),
    ('CS', r"CIUDADANOS-PARTIDO DE LA CIUDADAN"),
    ('OTROS', r"^M[EÉ]S PER MALLORCA"),     # en las europeas de 2019 iba bajo "Compromís per Europa"
    ('SUMAR', r"PODEM|EN COM[UÚ]N?\b|AHORA MADRID|MAREA ATL[AÁ]NTICA|M[AÁ]LAGA AHORA|COMPROM[IÍÌ]S\b(?! MUNICIPAL)|M[AÁ]S MADRID|M[AÁ]S PA[IÍ]S"),
    ('PP', r"UNI[OÓ]N DEL PUEBLO NAVARRO"),
]


def familia(abrev: str, nombre: str = '') -> str:
    a = (abrev or '').strip().upper()
    for x in (a, a.replace('.', '')):
        for cod, pat in _REGLAS:
            if re.search(pat, x):
                return cod
    n = (nombre or '').upper()
    for cod, pat in _NOMBRES:
        if re.search(pat, n):
            return cod
    # IU y sus federaciones (2004-2011) se reconocen mejor por el nombre que por las siglas
    if re.search(r"IZQUIERDA UNIDA|ESQUERRA UNIDA|ESQUERDA UNIDA|EZKER BATUA|IZQUIERDA PLURAL|ESQUERRA PLURAL|ESQUERDA PLURAL|IZQUIERDA-EZKERRA", n):
        return 'SUMAR'
    if 'PARTIDO SOCIALISTA' in n or 'SOCIALISTES' in n:
        return 'PSOE'
    if n.startswith('PARTIDO POPULAR'):
        return 'PP'
    return 'OTROS'
