"""Illes Balears: reportaje de la serie «Las comunidades en las urnas»."""
import html
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

IDP23 = 'https://www.idpbarcelona.net/docs/public/iccaa/2023/ibaleares_2023.pdf'
IDP95 = 'https://www.idpbarcelona.net/docs/public/iccaa/1995/ibaleares_1995.pdf'
IDP96 = 'https://www.idpbarcelona.net/docs/public/iccaa/1996/ibaleares_1996.pdf'
IDP15 = 'https://www.idpbarcelona.net/docs/public/iccaa/2015/ibaleares_2015.pdf'
TECHO = 'https://www.ultimahora.es/noticias/local/2025/12/02/2523791/parlament-tumba-techo-gasto-aboca-prohens-prorrogar-presupuestos-2025.html'
SOLER = wiki('Cristòfol Soler')
W07 = wiki('Elecciones al Parlamento de las Islas Baleares de 2007')
W23 = wiki('Elecciones al Parlamento de las Islas Baleares de 2023')
G23 = wiki('Elecciones generales de España de 2023')

# Escaños por elección, de las páginas de Wikipedia de cada elección (resultados oficiales del Parlamento).
# Se usa esta tabla en lugar de F.aut: la serie de Historia Electoral en datos.json no recoge las coaliciones
# de Ibiza ni varias listas pequeñas (1999-2007 sin el PSOE). Si se corrige datos.json, cambiar por F.aut(...).
ESCANOS = [
    (1983, 54, 21, 21, 6, 4, 'PDL 1, CIM 1'),
    (1987, 59, 25, 21, 4, 2, 'CDS 5, EEM 2'),
    (1991, 59, 31, 21, None, 3, 'EEM 2, UIM 1, FIEF 1'),
    (1995, 59, 30, 16, 2, 6, 'EU 3, Els Verds 1, AIPF 1'),
    (1999, 59, 28, 13, 3, 5, 'Pacte Progressista d’Eivissa 6, EU 2, EM 1, COP 1'),
    (2003, 59, 29, 15, 3, 4, 'Pacte Progressista d’Eivissa 5, EU 2, AIPF 1'),
    (2007, 59, 28, 16, 3, 5, 'PSOE-Eivissa pel Canvi 6, AIPF 1'),
    (2011, 59, 35, 14, None, 5, 'PSOE-Pacte per Eivissa 4, GxF 1'),
    (2015, 59, 20, 14, 3, 9, 'Podemos 10, Ciudadanos 2, GxF 1'),
    (2019, 59, 16, 19, 3, 6, 'Unidas Podemos 6, Ciudadanos 5, Vox 3, GxF 1'),
    (2023, 59, 25, 18, None, 6, 'Vox 8, Unidas Podemos 1, Sa Unió 1'),
]


def tabla_escanos():
    def c(v):
        return '—' if not v else str(v)
    filas = ''.join(f'<tr><td>{a}</td><td class="n">{c(pp)}</td><td class="n">{c(ps)}</td><td class="n">{c(um)}</td><td class="n">{c(na)}</td>'
                    f'<td>{html.escape(o)}</td></tr>' for a, t, pp, ps, um, na, o in ESCANOS)
    return ('<div class="tbl"><table class="presis"><thead><tr><th>Año</th><th class="n">PP</th><th class="n">PSOE</th><th class="n">UM / El Pi</th>'
            '<th class="n">PSM / Més</th><th>Otros</th></tr></thead><tbody>' + filas + '</tbody></table></div>'
            '<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Escaños en el Parlamento de las Illes Balears (54 en 1983 y 59 desde 1987). '
            'En 1991 el PP se presentó en coalición con UM. «PSM / Més» suma el PSM, el Bloc y Més de Mallorca y de Menorca; los pactos de Ibiza '
            'eran coaliciones del PSOE con otras fuerzas de izquierda en esa isla. Fuente: resultados oficiales recogidos en las páginas de '
            f'<a href="{W23}">Wikipedia</a> de cada elección.</p>')


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">El PP ha sido el partido más votado en diez de las once elecciones al Parlamento balear. Solo en 2019 le adelantó el PSOE. Y, sin embargo, el Govern ha cambiado mucho de manos: entre 1999 y 2015 pasó de la derecha a la izquierda, o al revés, en cada una de las cinco elecciones. Cuando el PP no llega a la mayoría absoluta, los socialistas y los partidos nacionalistas y de izquierda de Mallorca, Menorca e Ibiza han sumado más que él.</p>
<p>En las elecciones generales, Baleares se inclina a la derecha más que España. El PP fue la lista más votada en las islas en 1989 y 1993, cuando el país votaba a Felipe González, y en 2004, cuando ganó Zapatero. Y se vota poco: la participación en las islas quedó por debajo de la media española en 15 de las 16 generales; de media, solo Canarias, Ceuta y Melilla votan menos.</p>
<p>Este reportaje recorre esa historia con los resultados de las once autonómicas, de 1983 a 2023, y de las dieciséis generales desde 1977, municipio a municipio.</p>

<h2>Doce años de Cañellas y un relevo forzado</h2>
<p>El Estatuto de Autonomía de las Illes Balears se aprobó el 1 de marzo de 1983, y en mayo de ese año se votó el primer Parlamento, con 54 diputados elegidos en cuatro circunscripciones: Mallorca, Menorca, Ibiza y Formentera. La Coalición Popular de Gabriel Cañellas y el PSOE de Félix Pons empataron a 21 escaños; los populares sacaron algo más de votos (35,8% frente a 34,9%), y Cañellas fue investido con el apoyo de Unió Mallorquina (UM), un partido regionalista de centroderecha, y de los diputados del Partido Demócrata Liberal y de la Candidatura Independent de Menorca, según Historia Electoral.</p>
{tabla_escanos()}
<p>Cañellas gobernó doce años. En 1991 el PP concurrió en coalición con UM y logró 31 de los 59 escaños, y en 1995 repitió la mayoría absoluta con 30 diputados. Pero no terminó aquella legislatura. Un mes después de su cuarta investidura, la dirección nacional del PP le obligó a dimitir por el escándalo del túnel de Sóller, según el <a href="{IDP95}">Informe Comunidades Autónomas de 1995</a> y la <a href="{SOLER}">biografía de su sucesor</a> en Wikipedia. Le sustituyó Cristòfol Soler, hasta entonces presidente del Parlamento, que dimitió a su vez en junio de 1996, también por la presión de su propio partido, que no compartía su impulso a la normalización lingüística, según el <a href="{IDP96}">informe de 1996</a> y la misma biografía. Jaume Matas completó la legislatura.</p>
{presidentes([('1983', '1995', 'Gabriel Cañellas', 'AP / PP'), ('1995', '1996', 'Cristòfol Soler', 'PP'), ('1996', '1999', 'Jaume Matas', 'PP'),
              ('1999', '2003', 'Francesc Antich', 'PSOE'), ('2003', '2007', 'Jaume Matas', 'PP'), ('2007', '2011', 'Francesc Antich', 'PSOE'),
              ('2011', '2015', 'José Ramón Bauzá', 'PP'), ('2015', '2023', 'Francina Armengol', 'PSOE'), ('2023', 'hoy', 'Marga Prohens', 'PP')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes del Govern de les Illes Balears desde el Estatuto de 1983. Fuente: <a href="https://www.historiaelectoral.com/abalears.html">Historia Electoral</a> y Wikipedia.</p>

<h2>Cinco cambios de Gobierno seguidos</h2>
<p>En 1999 el PP volvió a ser el más votado, con el 44,8% y 28 escaños, pero se quedó a dos de la mayoría. El socialista Francesc Antich fue investido con 31 votos: los del PSOE, el PSM, UM, Esquerra Unida, Els Verds y las fuerzas de izquierda de Ibiza y Formentera. Fue el primer Gobierno balear sin el PP.</p>
<p>Desde entonces, el péndulo no paró. Matas recuperó el Govern en 2003 con 29 escaños, el de Formentera y el apoyo de UM; Antich volvió en 2007 con un nuevo pacto que incluía otra vez a UM, aunque en febrero de 2010 la expulsó del Gobierno por su relación con varios escándalos de corrupción, como recoge <a href="{W07}">Wikipedia</a>. En 2011, José Ramón Bauzá logró la mayoría absoluta más amplia de la historia del Parlamento: 35 escaños.</p>
<p>En 2015, el PP de Bauzá se desplomó al 28,5% y 20 escaños. La jurista Maria Ballester Cardell, de la Universitat de les Illes Balears, señalaba en el <a href="{IDP15}">Informe Comunidades Autónomas 2015</a> que en el electorado había pesado «la forma presidencialista de gobernar del Ejecutivo». Francina Armengol fue investida con el PSOE, Més per Mallorca, Més per Menorca y el apoyo de Podemos, que entraba en el Parlamento con 10 escaños. En 2019 el PSOE fue por primera vez el partido más votado, con 19 diputados, y Armengol fue la primera en repetir mandato seguido desde Cañellas. En su balance de los cuarenta años de autonomía, Ballester Cardell resumía así aquellas alternancias:</p>
{F.cita('Las situaciones de inestabilidad que han afectado al ejecutivo son consecuencia de las diferentes sensibilidades que han conformado los gobiernos de coalición', 'Maria Ballester Cardell', 'Universitat de les Illes Balears, en el Informe Comunidades Autónomas 2023 del Instituto de Derecho Público', IDP23, 'IDP Barcelona', '2024')}

<h2>2023: Prohens y la abstención de Vox</h2>
<p>En mayo de 2023 el PP de Marga Prohens subió de 16 a 25 escaños y Vox, de 3 a 8. La suma del PP y Sa Unió de Formentera, 26, superaba en uno a la de la izquierda. Prohens fue investida el 6 de julio, en la segunda votación, con los votos de su partido y de Sa Unió y la abstención de Vox, según la <a href="{W23}">crónica de aquellas elecciones</a>. Vox no entró en el Govern, pero se quedó con la presidencia del Parlamento.</p>
<p>Esa alianza no ha sido estable. En diciembre de 2025, el Parlament tumbó el techo de gasto del Govern, paso previo para presentar los presupuestos, porque Prohens no consiguió el apoyo de ningún otro grupo tras su ruptura con Vox, según <a href="{TECHO}">Última Hora</a>. Las islas funcionan en 2026 con los presupuestos de 2025 prorrogados. El conseller de Hacienda culpó a la vez a los socialistas y a Vox:</p>
{F.cita('Pedro Sánchez y Santiago Abascal prefieren que Baleares no tenga presupuesto que permitir que este Govern haga su trabajo', 'Antoni Costa', 'conseller de Hacienda del Govern balear, tras la votación del techo de gasto', TECHO, 'Última Hora', '2 de diciembre de 2025')}
<p>Las próximas autonómicas tocan en mayo de 2027.</p>

<h2>En las generales: más a la derecha que España</h2>
<p>En las generales, UCD arrasó en las islas en 1977, con el 51,1% de los votos, y el PSOE ganó en 1982 y 1986, con el 40,6%, por debajo de su resultado en el conjunto del país (48,2% y 44,3%). Desde 1989, el PP ha sido el más votado en Baleares en todas las generales menos tres: la de 2008, cuando el PSOE ganó por menos de una décima (44,7% frente a 44,6%), y las dos de 2019. En 2000 llegó al 54,7%, su mejor resultado en las islas.</p>
{F.gen('PSOE, PP y los demás en Baleares', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>La comparación con España muestra la diferencia: el PP balear ha superado su media española en 15 de las 16 generales, y el PSOE ha quedado por debajo de la suya en 14. Los partidos nacionalistas y regionalistas de las islas, como UM o el PSM, van en «Otras listas». En 2015, Podemos sacó en Baleares el 23,2%, a seis puntos del PP.</p>
{F.esp('PSOE y PP en Baleares y en España', 'PSOE y AP/PP en las Illes Balears y en el conjunto de España, en las generales.')}
{F.prov('Quién ganó en Baleares', 'Lista más votada en las generales de 1977 a 2023 en la circunscripción de las Illes Balears.')}
<p>Palma, con casi 300.000 electores, decide buena parte del resultado. Votó al PSOE en 1982 y 1986 y desde 1989 ha votado al PP en todas las generales menos en las dos de 2019. Santa Eulària des Riu, en Ibiza, es la más fiel al PP entre las grandes: ha votado a los populares en todas las generales desde 1979, salvo en abril de 2019. En el otro extremo, Maó fue en 2023 el único de los diez municipios más grandes donde el PSOE quedó primero.</p>
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios de las islas con más electores.')}
<p>El mapa por municipios enseña la fuerza del PP fuera de las ciudades. En 1977, UCD fue la lista más votada en los 65 municipios con datos. En 2000 y en 2011 el PP ganó en 66 de los 67; las excepciones fueron Costitx, donde quedó primera UM, y Capdepera, que votó al PSOE. En abril de 2019 el mapa se dio la vuelta: el PSOE ganó en 47 municipios, entre ellos todos los de Menorca y Formentera y cuatro de los cinco de Ibiza; el PP, en 19, casi todos en Mallorca, y Ara-Més-Esquerra, en Llubí. En 2023 el PP volvió a ganar en 54. El PSOE se quedó con 10, como Maó y Es Castell en Menorca o Artà, Capdepera y Pollença en el norte y el este de Mallorca, y Sumar con 3: Campanet, Deià y Esporles.</p>
{F.mapa('Baleares, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}
<p>Ninguno de los 65 municipios con datos en las 16 generales ha votado siempre al mismo partido.</p>

<h2>Votar menos que la media</h2>
<p>Baleares es una de las comunidades donde menos se vota en las generales. Sin contar el voto exterior, su participación quedó por debajo de la española en 15 de las 16 elecciones; la excepción fue 1977, con el 81,0% frente al 79,1%. La mayor distancia llegó en noviembre de 2019: votó el 58,7% del censo, frente al 69,9% del conjunto del país.</p>
{F.part('Participación en las generales: Baleares y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>Las Illes Balears eligen 8 diputados en una sola circunscripción. En 2023 fueron 3 para el PP, 3 para el PSOE, 1 para Vox y 1 para Sumar, según los <a href="{G23}">resultados oficiales</a>. El 29 de noviembre dirá si el PP repite como lista más votada, cuánto pesa Vox después de romper con Prohens y si la participación vuelve a quedarse lejos de la media española.</p>
"""


PIEZA = dict(
    cc='baleares', slug='baleares-historia-electoral', lugar='Illes Balears', corto='Baleares en las urnas',
    titulo='El PP ha ganado diez de las once autonómicas en Baleares, pero entre 1999 y 2015 el Govern cambió de manos en cada elección',
    dek='Cuando el PP no tiene mayoría absoluta, la izquierda y los partidos de las islas suman más que él. En las generales, Baleares vota más a la derecha que España: '
        'el PP ganó allí en 1989, 1993 y 2004, cuando el país votaba al PSOE. Y es una de las comunidades donde menos se vota.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='El PP ha sido el más votado en diez de las once autonómicas de Baleares, pero entre 1999 y 2015 el Govern cambió de manos en cada elección. En las generales, las islas votan más a la derecha y participan menos que España.',
    compara='Las 11 elecciones al Parlamento de las Illes Balears (1983-2023) y las 16 generales (1977-2023) en Baleares, por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('abalears', 'las Illes Balears'),
                               (IDP95, 'Avelino Blasco, «Islas Baleares», Informe Comunidades Autónomas 1995, Instituto de Derecho Público (IDP Barcelona)'),
                               (IDP96, '«Islas Baleares», Informe Comunidades Autónomas 1996, IDP Barcelona'),
                               (IDP15, 'Maria Ballester Cardell, «Islas Baleares», Informe Comunidades Autónomas 2015, Instituto de Derecho Público (IDP Barcelona)'),
                               (IDP23, 'Maria Ballester Cardell, «Illes Balears», Informe Comunidades Autónomas 2023, IDP Barcelona'),
                               (TECHO, 'Última Hora, «El Parlament tumba el techo de gasto y aboca a Prohens a prorrogar los presupuestos de 2025» (2-12-2025)'),
                               (SOLER, 'Wikipedia, Cristòfol Soler'),
                               (W07, 'Wikipedia, Elecciones al Parlamento de las Islas Baleares de 2007'),
                               (W23, 'Wikipedia, Elecciones al Parlamento de las Islas Baleares de 2023'),
                               (G23, 'Wikipedia, Elecciones generales de España de 2023 (escaños por circunscripción)')],
    enlaces=[],
)
