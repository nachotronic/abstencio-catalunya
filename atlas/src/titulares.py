"""Titulares cortos de las piezas del Atlas (portada, tarjetas, <title> y redes).

El titular largo de cada pieza (campo `titulo`) pasa a ser el subtítulo: lleva la cifra y el matiz.
Un titular corto no puede decir nada que no diga ya el largo; controles.py los revisa igual que el resto del texto.
Si una pieza no tiene titular aquí, se usa su `titulo`.
"""

TITULARES = {
    'cadiz-madrid-29n': 'El escaño que pasa de Cádiz a Madrid',
    'madrid-voto-exterior': 'El escaño de Madrid que decidió el extranjero',
    'escanos-ajustados-2023': 'Seis escaños por menos de 1.500 votos',
    'capitales-frente-a-su-provincia': 'La capital no es la isla progresista de su provincia',
    'sur-de-madrid': 'El sur de Madrid, contra su provincia',
    'a-illa-vilanova-de-arousa': 'Un puente y 23 puntos de distancia',
    'cabra-montilla': 'Cabra y Montilla votaban igual. Ya no',
    'puerto-real': 'Puerto Real no vota lo que dicen sus datos',
    'badalona': 'Badalona, la ciudad del voto doble',
    'paro-renta-participacion': 'A igual renta, donde hay más paro se vota menos',
    'cuencas-mineras-asturianas': 'Las cuencas mineras siguen votando como hace veinte años',
    'lalin-vilanova-de-arousa': 'Lalín y Vilanova, el PP por encima de lo previsto',
    'cuenca-de-pamplona': 'Cizur y Zizur: 1,4 kilómetros, 31 puntos',
    'getxo-portugalete': 'Dos orillas de la ría, dos votos',
    'aranda-miranda': 'Aranda y Miranda, las dos Burgos',
    'los-palacios-y-villafranca': 'Los Palacios y Villafranca y la caída del PSOE',
    'castro-urdiales': 'Castro-Urdiales, la excepción socialista de Cantabria',
    'vigo': 'Vigo, la gran ciudad gallega que ganó el PSOE',
    'pueblos-pequenos': 'Los pueblos votan más al alcalde que al Gobierno',
    'jodar': 'Jódar, el municipio que menos vota para su perfil',
    'sant-cugat-badia': 'Sant Cugat y Badia: 5,4 kilómetros, 23 puntos',
    'ontigola-aranjuez': 'Ontígola, uno de los 36 municipios donde ganó Vox',
    'morrazo-sanxenxo': 'Moaña y Sanxenxo, gemelos que votan distinto',
    'arahal-marchena': 'Arahal y Marchena, vecinos con la misma renta y otro voto',
    'manilva': 'Manilva, donde más ha caído la izquierda',
    'alcoi': 'Alcoi, a contracorriente en Alicante',
    'capitales-municipales': 'Las capitales votan menos para elegir alcalde',
    'europeas-2024': 'En las europeas, la brecha entre ricos y pobres se dispara',
}


def titular(p):
    return TITULARES.get(p['slug']) or p['titulo']
