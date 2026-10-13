"""Fe de errores del mapa de resultados (la portada). Se publica en atlas/correcciones/ (lo genera atlas/src/paginas.py),
no en la propia portada; la portada enlaza esa página en la firma y en el pie.
Añadir una línea (fecha ISO, texto) cada vez que cambie un dato o una conclusión publicada.
"""

CORRECCIONES = [
    ('2026-10-06', 'Agrupación de partidos revisada: UPN cuenta con el PP también cuando se presenta sola, y Compromís, Más País y Más Madrid con '
                   'Sumar / Podemos / IU también cuando van por separado. Se corrigen además una lista de Unidos Podemos de 2016 y la de C,S de 2008, '
                   'que estaban en Otros, y Esquerra Republicana del País Valencià, que pasa a ERC. El PP del 23J pasa del 33,1% al 33,3% '
                   '(con UPN) y cambian algunos recuentos de secciones y municipios.'),
    ('2026-10-06', 'Las mesas que figuran con censo y ningún voto en los ficheros de Interior (de 0 a 8 por elección, como una de La Línea de la '
                   'Concepción en 2023) se tratan como «sin dato» en lugar de como un 0% de participación.'),
    ('2026-10-06', 'Los recuentos de secciones y municipios donde gana cada partido ya no cuentan los empates.'),
    ('2026-10-06', 'Se reformulan tres frases que decían más que los datos: la entradilla hablaba de personas («quien vive en un barrio rico») '
                   'con datos por sección; «los barrios ricos votan PP» pasa a «el PP gana en ellos», y «Vox crece» pasa a «Vox saca más», porque '
                   'el dato es de una sola elección. Las cifras no cambian.'),
    ('2026-10-08', 'Al añadir todas las elecciones desde 1977, se revisa la agrupación de partidos: el Partido Socialista de Andalucía (PSA) y otros '
                   'partidos con «socialista» en el nombre que no son el PSOE pasan a Otros, Iniciativa per Catalunya pasa a Sumar / Podemos / IU '
                   'en las municipales y el CDS tiene familia propia. En 2004, el PSOE en las secciones más pobres pasa del 56,8% al 56,5%.'),
    ('2026-10-13', 'Revisión de siglas que comparten muchas listas locales con un partido grande: «CC», «CM», «CDC», «CiU», «PP» o «IU» '
                   'solo cuentan para Coalición Canaria, Junts, PP o Sumar / Podemos / IU si el nombre de la candidatura lo confirma. '
                   'Unas 90 listas locales cambian de familia, casi todas a Otros (Candidatura Comunista, Ciudadanos del Condado, '
                   'Plataforma del Pueblo Soriano, Unidad del Pueblo…); Cambiemos Murcia y Contigo Zurekin pasan a Sumar / Podemos / IU, '
                   'y Converxencia Centrista/CDS (municipales de 1991 en Ourense) al CDS. Junts / CiU en el Congreso de 2000 pasa del 4,3% '
                   'al 4,2% (Los Verdes-Comunidad de Madrid contaba como Junts) y el CDS en las municipales de 1991 del 3,5% al 3,9%. '
                   'Cambia el ganador en 82 municipios (casi todos pequeños y de municipales anteriores a 2011) y en 32 secciones. El texto de la pieza no cambia.'),
]
