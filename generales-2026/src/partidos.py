"""Agrupación de candidaturas en familias comparables (Congreso 1977-2026, municipales 1979-2023, europeas 1987-2024).

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
- Serie histórica (1977-2003), por continuidad de partido:
  - PP: Alianza Popular (1977), Coalición Democrática (1979), AP-PDP (1982), Coalición Popular (1986) y PP.
  - "Sumar / Podemos / IU" incluye el PCE y el PSUC (1977-1982), Unió de l'Esquerra Catalana (1986), Iniciativa per
    Catalunya (IC, IC-EV, IC-V, 1986-2000) y EUiA. No incluye las escisiones comunistas (MUC, PTE-UC, PCPE, PCC).
  - UCD (1977-1982) y CDS (1982-1996) son familias propias, sin sucesor (sus votantes se repartieron).
  - Junts / CiU incluye el Pacte Democràtic per Catalunya (1977). ERC incluye Esquerra de Catalunya (1977).
  - EH Bildu: Herri Batasuna (1979-1996) y Euskal Herritarrok (1998-1999), la izquierda abertzale de la que
    viene Bildu. Euskadiko Ezkerra (se integró en el PSE) y EA van en "Otros".
  - BNG incluye el Bloque Nacional-Popular Galego (1977-1979). Partido Andalucista, PSP, PST, PAR, UV, AIC: "Otros".
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
    ('UCD', 'UCD', '#e07b22'),
    ('CDS', 'CDS', '#7e57c2'),
    ('OTROS', 'Otros', '#9a9a9a'),
]
CODIGOS = [f[0] for f in FAMILIAS]
# Nombre de la familia en las elecciones anteriores a un año (la pieza lo usa en leyenda y fichas)
ALIAS = {'PP': [['1989', 'AP']], 'SUMAR': [['1986', 'PCE / PSUC']], 'BILDU': [['2011', 'HB / EH']]}

_REGLAS = [
    ('PP', r"^(PP\b|PP-|P\.P\.|UPN-PP|UPN$|NA\+)|^AP-PDP|^AP-PL"),
    ('UCD', r"^UCD$|^UCD-|^CC-UCD$"),
    ('CDS', r"^CDS$|^CDS-|^C\.D\.S\.$"),
    ('PSOE', r"PSOE(?! ?\(?H)|^PSC\b|^PSC-|^PSE-EE|^PSDEG|^PSIB|^PSN"),
    ('VOX', r"^VOX$"),
    ('CS', r"^(C'S|C´S|CS)$|-CS$"),
    ('UPYD', r"^UPYD$"),
    ('SUMAR', r"^PODEMOS|^EN COMÚ|^ECP|SUMAR|UPEC|^UNIDAD POPULAR|^IU\b|^IULV|^UNIDA|^IU-|^EUPV-UPEC|^PCE$|^PCE-|^PCA-PCE|^PSUC|^IC-EV$|^IC-?V\b|^ICV\b|^EUIA$|^EU-PV$|^EUPV$"),
    ('ERC', r"^ERC|^ESQUERRA$"),
    ('JUNTS', r"^(DL|CDC|CIU)$|^JXCAT|^JUNTS|[- ]JUNTS$|^CM$|-CM$"),
    ('PNV', r"EAJ-PNV|^E\.A\.J\.-P\.N\.V\.|^PNV"),
    ('BILDU', r"^EH ?BILDU|^BILDU|^AMAIUR$|^HB$|^H\.B\.$|^EH$"),
    ('BNG', r"^B\.?N\.?G\.?$|^BNG|^NÓS$|^BN-?PG$"),
    ('CC', r"^CCA|^CC-(?!UCD|AP)|^NC-CCA|^CC$"),
]


# Por el nombre completo, cuando las siglas no bastan (sobre todo en municipales)
_NOMBRES = [
    ('ERC', r"ESQUERRA REPUBLICANA"),
    ('JUNTS', r"CONVERG[EÈ]NCIA I UNI[OÓ]|^JUNTS\b|JUNTS PER CATALUNYA|TRIAS PER BARCELONA"),
    ('PNV', r"PARTIDO NACIONALISTA VASCO|EUZKO ALDERDI JELTZALEA"),
    ('BILDU', r"^BILDU|EUSKAL HERRIA BILDU"),
    ('PSOE', r"PSOE|^PSC\b|^PSC PROGR[EÉ]S MUNICIPAL"),
    ('CS', r"CIUDADANOS-PARTIDO DE LA CIUDADAN"),
    ('OTROS', r"^M[EÉ]S PER MALLORCA"),     # en las europeas de 2019 iba bajo "Compromís per Europa"
    ('SUMAR', r"PODEM|EN COM[UÚ]N?\b|AHORA MADRID|MAREA ATL[AÁ]NTICA|M[AÁ]LAGA AHORA|COMPROM[IÍÌ]S\b(?! MUNICIPAL)|M[AÁ]S MADRID|M[AÁ]S PA[IÍ]S"),
    ('PP', r"UNI[OÓ]N DEL PUEBLO NAVARRO|ALIANZA POPULAR|^COALICI[OÓ]N POPULAR|^COALICI[OÓ]N DEMOCR[AÁ]TICA$|CONVIVENCIA CATALANA"),
    ('UCD', r"UNI[OÓ]N DE CENTRO DEMOCR[AÁ]TICO|UNI[OÓ] DE CENTRE DEMOCR|CENTRISTES DE CATALUNYA"),
    ('CDS', r"CENTRO DEMOCR[AÁ]TICO Y SOCIAL|^COALICION FORO Y CDS"),
    ('CC', r"^COALICI[OÓ]N CANARIA"),
    ('JUNTS', r"PACTE DEMOCR[AÀ]TIC PER CATALUNYA"),
    ('ERC', r"ESQUERRA DE CATALU(NY|Ñ)A"),
    ('SUMAR', r"^PARTIDO COMUNISTA (DE |DEL |D')?(ANDALUC|ARAG|ASTURIAS|CANARIAS|CANTABRIA|CASTILLA|EUSKADI|EXTREMADURA|GALICIA|LA RIOJA|MADRID|MURCIA|NAVARRA|PA[IÍ]S VALENCI)|^PARTIDO COMUNISTA DE ESPA[NÑ]A$|^PARTIDO COMUNISTA DE ESPA[NÑ]A[- ]|PARTIT SOCIALISTA UNIFICAT|INICIATIVA PER CATALUNYA|UNI[OÓ] DE L.ESQUERRA CATALANA"),
    ('BILDU', r"HERRI BATASUNA|EUSKAL HERRITARROK"),
    ('BNG', r"BLOQUE NACIONAL.?POPULAR GALEGO"),
]

# Siglas que en algún año son de otro partido (CC en 1982: Conservadors de Catalunya, Convergencia Canaria)
_NO_ES = re.compile(r"CONSERVADORS DE CATALUNYA|INDEPENDENTISTAK ETA EZKERTIARRAK|CIUDADANA VASCA|CONVERGENCIA CANARIA|HIST[OÓ]RICO|MARXISTA-LENINISTA|\(M-L\)|\(I\)$")


def familia(abrev: str, nombre: str = '') -> str:
    a = (abrev if isinstance(abrev, str) else '').strip().upper()
    n = (nombre if isinstance(nombre, str) else '').upper()
    if _NO_ES.search(n):
        return 'OTROS'
    for x in (a, a.replace('.', '')):
        for cod, pat in _REGLAS:
            if re.search(pat, x):
                return cod
    for cod, pat in _NOMBRES:
        if re.search(pat, n):
            return cod
    # IU y sus federaciones (2004-2011) se reconocen mejor por el nombre que por las siglas
    if re.search(r"IZQUIERDA UNIDA|ESQUERRA UNIDA|ESQUERDA UNIDA|EZKER BATUA|IZQUIERDA PLURAL|ESQUERRA PLURAL|ESQUERDA PLURAL|IZQUIERDA-EZKERRA", n):
        return 'SUMAR'
    # solo el PSOE y sus federaciones (no el PSP, el PSA, el PST ni el Partido Socialista Galego)
    # (las listas locales del PSC y del PSPV, "Socialistes de...", sí)
    if re.search(r"PARTIDO SOCIALISTA OBRERO|SOCIALISTES|PARTIDO SOCIALISTA DE EUSKADI|PARTIDO DOS SOCIALISTAS DE GALICIA|PARTIT SOCIALISTA DE LES ILLES|PARTI[TD]O? SOCIALISTA DEL PA[IÍ]S VALENCIA|SOCIALISTAS? DE NAVARRA|^PARTIDO SOCIALISTA$", n):
        return 'PSOE'
    if n.startswith('PARTIDO POPULAR'):
        return 'PP'
    return 'OTROS'
