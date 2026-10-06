"""Genera ca.html (versión en catalán) a partir de index.html.

El texto visible de la página está en src/i18n/ca_body.html; src/i18n/es_body.html guarda el bloque
castellano del que se tradujo. Si el castellano cambia, el script se para hasta que se actualicen los dos.
Los textos que genera el JavaScript (leyendas, gráficos, fichas) se traducen con la lista JS de abajo.

Uso: python3 src/build_ca.py            -> escribe ca.html
     python3 src/build_ca.py --accept   -> da por buena la traducción del castellano actual
"""
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
I18N = ROOT / 'src' / 'i18n'
START, END = '<div class="wide">\n<header class="col">', '<script src="https://unpkg.com/deck.gl'

# (castellano, catalán, cuántas veces aparece). En cadenas JS entre comillas simples el apóstrofo va escapado.
JS = [
    ('<html lang="es">', '<html lang="ca">', 1),
    ('<title>Abstención en 3D</title>', '<title>Abstenció en 3D</title>', 1),
    ("toLocaleString('es-ES')", "toLocaleString('ca-ES')", 3),
    ("localeCompare(b,'es')", "localeCompare(b,'ca')", 1),
    ('aria-label="votó ${pct(v)}, sin derecho ${pct(n)}, no votó ${pct(a)}"', 'aria-label="va votar ${pct(v)}, sense dret ${pct(n)}, no va votar ${pct(a)}"', 1),
    ('${n(vo)} votaron</span>', '${n(vo)} van votar</span>', 1),
    ('unos ${n(si)} sin derecho a voto', 'uns ${n(si)} sense dret a vot', 1),
    ('${n(ab)} podían votar y no lo hicieron', '${n(ab)} podien votar i no ho van fer', 1),
    ('aria-label="Participación por elección"', 'aria-label="Participació per elecció"', 1),
    # variables del mapa
    ("'Abstención entre quienes pueden votar'", "'Abstenció entre els qui poden votar'", 1),
    ("'más abstención'", "'més abstenció'", 1),
    ("'Adultos sin derecho a voto en las municipales 2023'", "'Adults sense dret a vot a les municipals 2023'", 1),
    ("'Adultos sin derecho a voto (municipales)'", "'Adults sense dret a vot (municipals)'", 1),
    ("'Adultos sin derecho a voto'", "'Adults sense dret a vot'", 2),
    ("'más adultos sin derecho'", "'més adults sense dret'", 2),
    ("'Adultos residentes que no votaron'", "'Adults residents que no van votar'", 1),
    ("'más adultos sin votar'", "'més adults sense votar'", 1),
    ("'Renta por unidad de consumo'", "'Renda per unitat de consum'", 2),
    ("'menos renta'", "'menys renda'", 1),
    ("'Adultos sin estudios superiores'", "'Adults sense estudis superiors'", 1),
    ("'menos estudios'", "'menys estudis'", 1),
    ("'Tasa de paro (2021)'", "'Taxa d\\'atur (2021)'", 1),
    ("'más paro'", "'més atur'", 1),
    ("'Población extranjera (2021)'", "'Població estrangera (2021)'", 1),
    ("'más extranjeros'", "'més estrangers'", 1),
    ("'Edad media'", "'Edat mitjana'", 3),
    ("' años'", "' anys'", 2),
    ("'más joven'", "'més jove'", 1),
    ("'Voto independentista nov. 2019'", "'Vot independentista nov. 2019'", 1),
    ("'más independentista'", "'més independentista'", 1),
    ("'Caída de participación 2019 → 2023'", "'Caiguda de participació 2019 → 2023'", 1),
    ("' puntos'", "' punts'", 2),
    ("'más caída'", "'més caiguda'", 1),
    ("'Municipales 2023 frente a Congreso 2023'", "'Municipals 2023 davant del Congrés 2023'", 1),
    ("'menos participación en las municipales'", "'menys participació a les municipals'", 1),
    ("'Sin altura'", "'Sense altura'", 1),
    ("'Adultos que no votaron'", "'Adults que no van votar'", 1),
    ("'Abstención (sobre censo)'", "'Abstenció (sobre el cens)'", 1),
    ("'Caída 2019 → 2023'", "'Caiguda 2019 → 2023'", 1),
    ("'Participación perdida en las municipales'", "'Participació perduda a les municipals'", 1),
    # lugares: la clave de «Área de Barcelona» también se traduce (enlaza texto, cámara y foto)
    ("'Área de Barcelona'", "'Àrea de Barcelona'", 1),
    ('"Área de Barcelona":{', '"Àrea de Barcelona":{', 1),
    ('/^Área de /', '/^Àrea de /', 1),
    # ficha de sección
    ('<span class="muted">sección ', '<span class="muted">secció ', 1),
    ('Adultos que viven aquí, en personas', 'Adults que hi viuen, en persones', 1),
    ('<div>Participación 23J:', '<div>Participació 23J:', 1),
    # tabla de municipios
    ('<th>Dónde</th><th>Población</th><th>De cada 100 adultos</th><th>Partic. 23J</th><th>Renta u.c.</th><th>Extranj.</th>',
     '<th>On</th><th>Població</th><th>De cada 100 adults</th><th>Partic. 23J</th><th>Renda u.c.</th><th>Estrang.</th>', 1),
    ('"name": "Pueblos de menos de 2.000 hab."', '"name": "Pobles de menys de 2.000 hab."', 1),
    ('"name": "Catalu\\u00f1a"', '"name": "Catalunya"', 1),
    # gráficos por quintil
    ("'Con estudios superiores'", "'Amb estudis superiors'", 1),
    ("'Tasa de paro'", "'Taxa d\\'atur'", 1),
    ("'Población extranjera'", "'Població estrangera'", 1),
    ('aria-label="Participación por quintil de ${t}"', 'aria-label="Participació per quintil de ${t}"', 1),
    ('>← menos</text>', '>← menys</text>', 1),
    ('>más →</text>', '>més →</text>', 1),
    ('Cada columna es un quintil de secciones (unas 107), con su valor mínimo debajo. Altura total y número: participación sobre el censo.',
     'Cada columna és un quintil de seccions (unes 107), amb el seu valor mínim a sota. Altura total i número: participació sobre el cens.', 1),
    ('>Parte oscura</b>: votantes sobre adultos residentes.', '>Part fosca</b>: votants sobre adults residents.', 1),
    # coeficientes
    ("pct_higher_ed_completed:'Estudios superiores',unemployment_rate:'Paro'", "pct_higher_ed_completed:'Estudis superiors',unemployment_rate:'Atur'", 1),
    ("pct_foreign:'Extranjeros',pct_secondary:'Viviendas secundarias',pct_naturalized:'Españoles nacidos fuera',pct_rented:'Viviendas de alquiler',net_income_equiv:'Renta (u.c.)'",
     "pct_foreign:'Estrangers',pct_secondary:'Habitatges secundaris',pct_naturalized:'Espanyols nascuts fora',pct_rented:'Habitatges de lloguer',net_income_equiv:'Renda (u.c.)'", 1),
    ('aria-label="Efecto de cada variable en puntos de participación"', 'aria-label="Efecte de cada variable en punts de participació"', 1),
    ('Puntos de participación por cada desviación típica de la variable (p. ej., +', 'Punts de participació per cada desviació típica de la variable (p. ex., +', 1),
    (' puntos de universitarios o +', ' punts d\'universitaris o +', 1),
    (' años de edad media). La línea fina es el intervalo de confianza del 95% (bootstrap, 500 réplicas). Si cruza el cero, el efecto no se distingue de nada.',
     ' anys d\'edat mitjana). La línia fina és l\'interval de confiança del 95% (bootstrap, 500 rèpliques). Si travessa el zero, l\'efecte no es distingeix de res.', 1),
    # independentismo
    ('aria-label="Participación 2019 y 2023 por cuartil de voto independentista"', 'aria-label="Participació 2019 i 2023 per quartil de vot independentista"', 1),
    ('</b>noviembre 2019</span>', '</b>novembre 2019</span>', 1),
    ('</b>julio 2023</span>', '</b>juliol 2023</span>', 1),
    ('Secciones agrupadas en cuartos según el voto a ERC, Junts y CUP en noviembre de 2019', 'Seccions agrupades en quarts segons el vot a ERC, Junts i la CUP el novembre de 2019', 1),
    # deciles
    ('aria-label="Participación por decil de renta en las tres elecciones"', 'aria-label="Participació per decil de renda a les tres eleccions"', 1),
    ("'1 · más pobre'", "'1 · més pobre'", 1),
    ("'10 · más rico'", "'10 · més ric'", 1),
    ('</b>Congreso 2023</span>', '</b>Congrés 2023</span>', 1),
    ('</b>municipales 2023</span>', '</b>municipals 2023</span>', 1),
    ('Secciones agrupadas en diez grupos iguales por renta', 'Seccions agrupades en deu grups iguals per renda', 1),
    # tamaño de municipio
    ('Participación por tamaño de municipio, generales 2015–2023', 'Participació per mida de municipi, generals 2015–2023', 1),
    ('aria-label="Participación por tamaño de municipio"', 'aria-label="Participació per mida de municipi"', 1),
    # secciones que menos votan
    ('<th>Sección</th><th>Partic.</th><th>Adultos que votan</th><th>Sin derecho</th><th>Renta u.c.</th><th>Extranj.</th><th>Univ.</th><th>Paro</th>',
     '<th>Secció</th><th>Partic.</th><th>Adults que voten</th><th>Sense dret</th><th>Renda u.c.</th><th>Estrang.</th><th>Univ.</th><th>Atur</th>', 1),
    # evolución 2015-2024 y buscador: todos sus textos están en el objeto TXT
    (open(I18N / 'txt_es.js', encoding='utf-8').read().strip(), open(I18N / 'txt_ca.js', encoding='utf-8').read().strip(), 1),
    # textos alternativos de las fotos
    ('"Concierto de habaneras con el público junto al mar, en Calella de Palafrugell"', '"Concert d\'havaneres amb el públic vora el mar, a Calella de Palafrugell"', 1),
    ('"Fuente y paseo con palmeras en el centro de Salou"', '"Font i passeig amb palmeres al centre de Salou"', 1),
    ('"Iglesia de Santa Maria de Guissona"', '"Església de Santa Maria de Guissona"', 1),
    ('"Gente comprando en el mercado del sábado de la plaça Major de Vic"', '"Gent comprant al mercat del dissabte de la plaça Major de Vic"', 1),
    ('"Ensayo de los Marrecs de Salt en su local"', '"Assaig dels Marrecs de Salt al seu local"', 1),
    ('"Gente paseando por una calle de Barcelona"', '"Gent passejant per un carrer de Barcelona"', 1),
    ('"Gente paseando ante el Museu del Mar de Lloret de Mar"', '"Gent passejant davant del Museu del Mar de Lloret de Mar"', 1),
    ('"Niños y vecinos junto a la escultura de Sant Jordi y el dragón, en Figueres"', '"Nens i veïns al costat de l\'escultura de Sant Jordi i el drac, a Figueres"', 1),
    ('"Paseo marítimo de Roses con puestos de excursiones en barco"', '"Passeig marítim de Roses amb parades d\'excursions en vaixell"', 1),
    ('"Terrazas con gente en una plaza de Castelló d\'Empúries"', '"Terrasses amb gent en una plaça de Castelló d\'Empúries"', 1),
    ('"Un ciclista y peatones en una calle del Raval"', '"Un ciclista i vianants en un carrer del Raval"', 1),
    ('"Paseo de la Via Júlia, en Nou Barris"', '"Passeig de la Via Júlia, a Nou Barris"', 1),
    ('"Las tres chimeneas de Sant Adrià de Besòs"', '"Les tres xemeneies de Sant Adrià de Besòs"', 1),
    ('"Castellers y público en una plaza de Badalona"', '"Castellers i públic en una plaça de Badalona"', 1),
    ('"Ayuntamiento de Santa Coloma de Gramenet y terrazas de la plaza"', '"Ajuntament de Santa Coloma de Gramenet i terrasses de la plaça"', 1),
    ('"Teatre de Salt, en la plaça de Sant Jaume"', '"Teatre de Salt, a la plaça de Sant Jaume"', 1),
    ('"Esculturas frente a la antigua fábrica Coma Cros, en Salt"', '"Escultures davant de l\'antiga fàbrica Coma Cros, a Salt"', 1),
    ('"Iglesia de Sant Romà, en Lloret de Mar"', '"Església de Sant Romà, a Lloret de Mar"', 1),
]


def block(s):
    i = s.index(START); j = s.index(END, i)
    return i, j


def main():
    es = (ROOT / 'index.html').read_text(encoding='utf-8')
    i, j = block(es)
    if '--accept' in sys.argv:
        (I18N / 'es_body.html').write_text(es[i:j], encoding='utf-8'); print('es_body.html actualizado'); return
    if es[i:j] != (I18N / 'es_body.html').read_text(encoding='utf-8'):
        sys.exit('El texto castellano ha cambiado: actualiza src/i18n/ca_body.html y ejecuta con --accept.')
    s = es[:i] + (I18N / 'ca_body.html').read_text(encoding='utf-8') + es[j:]
    for old, new, n in JS:
        c = s.count(old)
        if c != n:
            sys.exit(f'{c} apariciones (esperaba {n}): {old[:70]}')
        s = s.replace(old, new)
    (ROOT / 'ca.html').write_text(s, encoding='utf-8')
    print('ca.html escrito,', len(s), 'bytes')


main()
