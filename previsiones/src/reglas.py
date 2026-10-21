"""Reglas electorales vigentes para el Congreso y el Senado (LOREG), sin datos: solo el reparto.

- Congreso (arts. 162-163 LOREG): 52 circunscripciones, umbral del 3 % de los votos válidos (incluido el voto en
  blanco) en cada una y reparto D'Hondt. Ceuta y Melilla eligen un diputado cada una: gana la lista más votada.
- Senado (arts. 165-166): voto limitado a candidatos. Cuatro senadores por provincia peninsular y el elector marca
  hasta tres; tres en Gran Canaria, Mallorca y Tenerife (marca hasta dos); uno en cada una de las demás islas (uno);
  dos en Ceuta y dos en Melilla (marca hasta dos, art. 166.1.a). Desde la LO 2/2026, Ibiza y Formentera son
  circunscripciones distintas (art. 165.2; RD 806/2026, art. 3.2): 209 senadores elegidos en 60 circunscripciones. Los senadores de designación autonómica
  (art. 69.5 de la Constitución) no dependen de las generales y van aparte.
"""

# Diputados por provincia en 2026 (Real Decreto 806/2026: Madrid 38, Cádiz 8)
ESCANOS_2026 = {
    '01': 4, '02': 4, '03': 12, '04': 6, '05': 3, '06': 5, '07': 8, '08': 32, '09': 4, '10': 4, '11': 8, '12': 5,
    '13': 5, '14': 6, '15': 8, '16': 3, '17': 6, '18': 7, '19': 3, '20': 6, '21': 5, '22': 3, '23': 5, '24': 4,
    '25': 4, '26': 4, '27': 4, '28': 38, '29': 11, '30': 10, '31': 5, '32': 4, '33': 7, '34': 3, '35': 8, '36': 7,
    '37': 4, '38': 7, '39': 5, '40': 3, '41': 12, '42': 2, '43': 6, '44': 3, '45': 6, '46': 16, '47': 5, '48': 8,
    '49': 3, '50': 7, '51': 1, '52': 1}
# 2023: Madrid 37, Cádiz 9
ESCANOS_2023 = {**ESCANOS_2026, '28': 37, '11': 9}

# Circunscripciones del Senado: (código, nombre, provincia, senadores, votos por elector)
_ISLAS = [
    ('07M', 'Mallorca', '07', 3, 2), ('07N', 'Menorca', '07', 1, 1), ('07I', 'Eivissa', '07', 1, 1),
    ('07F', 'Formentera', '07', 1, 1),
    ('35G', 'Gran Canaria', '35', 3, 2), ('35L', 'Lanzarote', '35', 1, 1), ('35F', 'Fuerteventura', '35', 1, 1),
    ('38T', 'Tenerife', '38', 3, 2), ('38P', 'La Palma', '38', 1, 1), ('38G', 'La Gomera', '38', 1, 1),
    ('38H', 'El Hierro', '38', 1, 1),
]


def circunscripciones_senado(nombres):
    """Lista de circunscripciones del Senado. `nombres` es {código de provincia: nombre}."""
    out = []
    for p, nom in sorted(nombres.items()):
        if p in ('07', '35', '38'):
            out += [i for i in _ISLAS if i[2] == p]
        elif p in ('51', '52'):
            out.append((p, nom, p, 2, 2))
        else:
            out.append((p, nom, p, 4, 3))
    return out


def dhondt(votos, escanos, validos, umbral=3):
    """Reparto D'Hondt. `votos` es {lista: votos}; `validos` incluye el voto en blanco (cuenta para el umbral).
    Los empates de cociente se deshacen por más votos totales (art. 163.1.d LOREG; el sorteo no se modela)."""
    elegibles = {k: v for k, v in votos.items() if v * 100 >= umbral * validos and v > 0}   # umbral en %
    cocientes = sorted(((v / d, v, k) for k, v in elegibles.items() for d in range(1, escanos + 1)), reverse=True)
    out = {k: 0 for k in votos}
    for _, _, k in cocientes[:escanos]:
        out[k] += 1
    return out


def senado_limitado(votos, senadores, votos_elector):
    """APROXIMACIÓN, no el reparto oficial: la ley proclama a los candidatos más votados (art. 166.1.b), no a
    listas. Aquí se supone voto de lista (cada elector marca solo a candidatos de un partido, sin voto cruzado) y
    que cada partido presenta tantos candidatos como votos tiene el elector. Así, el primero se lleva tantos
    senadores como votos por elector (3 de 4 en una provincia, 2 de 3 en Mallorca, los 2 de Ceuta o Melilla) y
    el resto va a los siguientes. Si no hay más partidos con votos, los escaños sobrantes van al primero.
    El modelo por candidato, con voto cruzado, queda pendiente (revisión R3 de previsiones/revisiones/)."""
    orden = [k for v, k in sorted(((v, k) for k, v in votos.items() if v > 0), reverse=True)]
    out = {k: 0 for k in votos}
    if not orden:
        return out
    out[orden[0]] = min(votos_elector, senadores)
    for k in orden[1:1 + senadores - out[orden[0]]]:
        out[k] += 1
    out[orden[0]] += senadores - sum(out.values())
    return out
