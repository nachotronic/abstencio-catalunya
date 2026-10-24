"""«Quién va con quién el 29N» (pieza de resumen de fin de semana, 24-10-2026).

Resume las piezas de coaliciones ya publicadas (mapa final de coaliciones, coaliciones desde 2015, Madrid, Cataluña,
Canarias, Teruel, Senado) con sus mismas cifras. Las del espacio a la izquierda del PSOE salen de
actualidad/src/coaliciones/datos.json, que reproduce los escaños oficiales de las cinco generales.
Uso, desde la raíz: python3 actualidad/src/resumenes/coaliciones.py
"""
from comun import BASE, COLOR, cuadrados, esc, figura, n, pieza

A = BASE + 'actualidad/'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'

# Escaños del espacio a la izquierda del PSOE: reales y sumando los votos de sus listas en cada provincia
# (mapa-coaliciones-izquierda-29n: 71/86, 71/71, 43/43, 38/42, 31/31)
HIST = [('Dic. 2015', 71, 86, 'Separados'), ('Jun. 2016', 71, 71, 'Juntos'), ('Abr. 2019', 43, 43, 'Separados'),
        ('Nov. 2019', 38, 42, 'Separados'), ('Jul. 2023', 31, 31, 'Juntos')]


def hist_svg():
    W, H, ml, mb, mt = 640, 260, 40, 44, 16
    y = lambda v: mt + (1 - v / 90) * (H - mt - mb)
    paso = (W - ml) / len(HIST)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Escaños de la izquierda a la izquierda del PSOE en cada elección, reales y sumando sus listas">']
    for v in (0, 30, 60, 90):
        out.append(f'<line x1="{ml}" x2="{W}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--grid)"/><text x="{ml - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{v}</text>')
    for i, (e, real, suma, modo) in enumerate(HIST):
        x0 = ml + i * paso + paso * .18
        w = paso * .3
        for k, (v, op, nom) in enumerate(((real, 1, 'Escaños reales'), (suma, .4, 'Sumando sus votos'))):
            x = x0 + k * (w + 4)
            out.append(f'<rect x="{x:.1f}" y="{y(v):.1f}" width="{w:.1f}" height="{y(0) - y(v):.1f}" fill="var(--sumar)" fill-opacity="{op}" rx="2"><title>{e}, {nom}: {v}</title></rect>'
                       f'<text x="{x + w / 2:.1f}" y="{y(v) - 5:.1f}" text-anchor="middle" class="lab">{v}</text>')
        out.append(f'<text x="{x0 + w + 2:.1f}" y="{H - 24}" text-anchor="middle" class="lab">{e}</text>'
                   f'<text x="{x0 + w + 2:.1f}" y="{H - 8}" text-anchor="middle">{modo}</text>')
    out.append('</svg>')
    return ''.join(out)


fig_hist = figura('Cuando la izquierda del PSOE fue dividida, perdió escaños; cuando se juntó, perdió votos',
                  'Diputados del espacio a la izquierda del PSOE en cada elección (tono oscuro) y los que habría sacado sumando en cada provincia los votos de sus listas (tono claro). Es un cálculo, no lo que habría pasado',
                  hist_svg(),
                  'Fuente: Ministerio del Interior, resultados por mesa con voto exterior (vía pollspaindata). Reparto D\'Hondt con la barrera del 3 %; el cálculo con los votos reales reproduce los escaños oficiales. Cálculo propio.',
                  leyenda=[('Escaños reales', 'var(--sumar)'), ('Sumando sus votos', 'color-mix(in srgb, var(--sumar) 40%, var(--bg))')],
                  tabla=(['Elección', 'Escaños', 'Sumando sus votos', 'Listas'], [(e, r, s, m) for e, r, s, m in HIST]))

fig_31 = figura('Los 31 diputados de Sumar en 2023, según cómo irá su espacio el 29N',
                'Cada cuadrado es un diputado de Sumar en las generales de 2023, agrupado por la coalición registrada este año en su provincia',
                cuadrados([('Frente Amplio y Podemos, juntos (Canarias y Comunitat Valenciana)', 5, 'var(--sumar)', 1),
                           ('Frente Amplio con partidos territoriales, sin Podemos (Baleares y Aragón)', 2, 'var(--sumar)', .7),
                           ('Cataluña: Podemos dentro de las listas de ERC', 7, 'var(--sumar)', .45),
                           ('Sin coalición entre los dos (39 provincias)', 17, 'var(--sumar)', .25)],
                          'Los 31 diputados de Sumar en 2023 agrupados según las coaliciones del 29N'),
                'Fuente: Ministerio del Interior, generales de 2023 con voto exterior; coaliciones según Público, elDiario.es, Europa Press y Efe (16 y 17 de octubre de 2026). Cálculo propio.')

SEN = [('2023, como fue', 120, 72, 'PP', 'PSOE'), ('Con la lista conjunta de PSOE y Frente Amplio', 82, 110, 'PP', 'Lista conjunta'),
       ('Con la lista conjunta y los votos de Vox sumados al PP', 120, 72, 'PP con Vox', 'Lista conjunta')]


def senado_svg():
    W, ml, alto = 640, 0, 58
    H = alto * len(SEN) + 10
    x = lambda v: v / 208 * W
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Senadores elegidos en 2023 y en dos simulaciones con los mismos votos">']
    for i, (nom, der, izq, nd, ni) in enumerate(SEN):
        y = i * alto
        otros = 208 - der - izq
        out.append(f'<text x="0" y="{y + 14}" class="lab">{esc(nom)}</text>')
        col_d = 'var(--pp)'
        out.append(f'<rect x="0" y="{y + 20}" width="{x(der):.1f}" height="24" fill="{col_d}"{" stroke=\"var(--vox)\" stroke-width=\"3\"" if "Vox" in nd else ""}><title>{nd}: {der}</title></rect>')
        out.append(f'<rect x="{x(der):.1f}" y="{y + 20}" width="{x(otros):.1f}" height="24" fill="var(--otros)"><title>Otros: {otros}</title></rect>')
        out.append(f'<rect x="{x(der + otros):.1f}" y="{y + 20}" width="{x(izq):.1f}" height="24" fill="var(--psoe)"><title>{ni}: {izq}</title></rect>')
        out.append(f'<text x="6" y="{y + 37}" style="fill:#fff;font-weight:600">{nd} {der}</text>'
                   f'<text x="{W - 6}" y="{y + 37}" text-anchor="end" style="fill:#fff;font-weight:600">{ni} {izq}</text>')
    out.append(f'<line x1="{x(104):.1f}" x2="{x(104):.1f}" y1="16" y2="{H}" stroke="var(--fg)" stroke-dasharray="3 3"/>')
    out.append('</svg>')
    return ''.join(out)


fig_sen = figura('El Senado con los votos de 2023, en tres versiones',
                 'Solo los 208 senadores que se votan; no incluye a los que designan los parlamentos autonómicos. La línea marca la mitad. Borde verde: la cifra suma los votos de Vox a los del PP',
                 senado_svg(),
                 'Fuente: Junta Electoral Central, resultados oficiales del Senado de 2023 por candidato (BOE de 1 de septiembre de 2023, con la corrección del 16 de septiembre). Simulación propia: suma mecánica de votos por candidato.',
                 leyenda=[('PP (o PP con los votos de Vox)', 'var(--pp)'), ('PSOE o lista conjunta', 'var(--psoe)'), ('Otros', 'var(--otros)')])

cuerpo = f'''<div class="resumen"><b>En corto</b><ul>
<li>Congreso: el Frente Amplio y Podemos solo irán juntos en cinco provincias, las dos canarias y las tres valencianas. En Cataluña, Podemos va dentro de las listas de ERC.</li>
<li>La última vez que ese espacio fue dividido en casi toda España, en 2015, sumando sus votos habría sacado 86 diputados y no 71. Cuando se juntó, en 2016, perdió un millón de votos.</li>
<li>Senado: el PSOE y el Frente Amplio van juntos en 43 provincias. Con los votos de 2023, el PP habría bajado de 120 a 82 senadores elegidos; con los de Vox sumados, volvería a 120.</li>
<li>PP y Vox negocian el Senado. Las listas se cierran el lunes 26 de octubre a las 23.59.</li>
</ul></div>
<p data-tipo="contexto">El plazo para registrar coaliciones se cerró a las 23.59 del viernes 16 de octubre, y a esa hora ya no quedaba nada que negociar. El Frente Amplio, que reúne a Movimiento Sumar, Izquierda Unida, Más Madrid, los comuns y otros partidos, registró su coalición sin Podemos y lo explicó en una frase: «No han querido aceptar la propuesta», según <a href="https://www.publico.es/politica/frente-amplio-podemos-concurriran-separado-29-noviembre-salvo-canarias-pais-valencia.html">Público</a>. Esa misma mañana, Gabriel Rufián había dicho en RAC1 lo que nadie más se atrevía a decir en voz alta: «He fracasado y hemos fracasado», según <a href="https://www.que.es/2026/10/16/unidad-izquierda-29n-sin-pacto/">Qué!</a>.</p>
<p data-tipo="contexto">Una semana después, el mapa de las alianzas para el 29N está casi cerrado. Falta una pieza, la de la derecha en el Senado, y se decide este fin de semana: el plazo para presentar candidaturas ante las juntas electorales empezó el 21 de octubre y acaba el lunes 26 a las 23.59, según <a href="https://rtvc.es/comienza-el-plazo-para-presentar-las-candidaturas-para-el-29n-21-octubre-2026/">RTVC</a>. Este texto reúne lo que hemos contado estas semanas sobre quién va con quién, y lo que valen esas alianzas con los votos de la última vez.</p>
<h2>El Congreso: sin papeleta común en 47 provincias</h2>
<p data-tipo="dato">El Frente Amplio y Podemos solo compartirán papeleta en cinco de las 52 circunscripciones: Las Palmas y Santa Cruz de Tenerife, con Unidad del Pueblo Canario, y Valencia, Alicante y Castellón, con Compromís-Front Valencià. En Baleares y Aragón, el Frente Amplio irá con Ara Més y con la Chunta, sin Podemos. En Cataluña, Podemos no tendrá papeleta propia y meterá a independientes en las listas de ERC. En las 39 provincias restantes no hay coalición entre los dos. Lo contamos provincia a provincia en {L("pactos-izquierda-mapa-final-29n", "el mapa que dejó el plazo")}.</p>
<p data-tipo="dato">Para medir lo que eso significa hay que volver a julio de 2023, cuando todo ese espacio iba en una sola lista, la de Sumar, con Podemos dentro. Sumar sacó 31 diputados. Cinco salieron de las provincias donde ahora habrá papeleta común; los otros 26, de provincias donde no la habrá.</p>
{fig_31}
<p data-tipo="contexto">Hay excepciones dentro de las excepciones. En Teruel, Chunta Aragonesista decidió no presentar al Congreso la coalición que encabeza, CHA-Frente Amplio Aragón, «por responsabilidad», según <a href="https://www.infobae.com/espana/agencias/2026/10/22/iu-asegura-que-el-29n-habra-papeletas-de-la-izquierda-transformadora-en-teruel/">Efe</a>, e irá al Senado con el PSOE. Izquierda Unida mantendrá su propia lista. Con los votos de 2023, como contamos en {L("teruel-cha-izquierda-escano-29n", "la pieza de Teruel")}, ni siquiera todos los votantes de Sumar pasándose al PSOE le habrían dado un segundo diputado: le habrían faltado 235 votos.</p>
<h2>Madrid, Barcelona y Canarias: lo que vale la suma</h2>
<p data-tipo="dato">En Madrid, la provincia que más diputados reparte, el Frente Amplio irá encabezado por Emilio Delgado y Podemos, por Irene Montero. Con los votos de 2023, separadas, las dos listas habrían sacado entre cinco y seis de los seis diputados que logró Sumar, y el que se pierde iría al PSOE. Para que Podemos entre en el reparto necesita pasar el 3 % de los votos válidos de la provincia: uno de cada cinco votos de lo que fue Sumar. Lo contamos en {L("frente-amplio-podemos-madrid-escanos-29n", "Delgado contra Montero")}.</p>
<p data-tipo="dato">En Cataluña, ERC y los comuns volverán a ir por separado. Juntos, con los votos de 2023, habrían sacado 15 diputados en lugar de 14. El que falta habría salido de Barcelona, a costa del PSC, y por un margen que cabe en una mesa electoral: {L("rufian-fracaso-lista-unitaria-29n", "126 votos")}.</p>
<p data-tipo="dato">Canarias es el caso contrario. Allí Nueva Canarias, Podemos, IU y Sumar sí se unen, y con los votos de 2023 la suma habría pasado de uno a tres diputados: uno quitado al PP en Las Palmas y otro al PSOE en Santa Cruz de Tenerife, este por unos 1.600 votos, como explicamos en {L("canarias-unidad-pueblo-canario-29n", "la pieza de Canarias")}.</p>
<h2>Lo que enseña 2015, y lo que enseña 2016</h2>
<p data-tipo="dato">No es la primera vez que este espacio se presenta partido. En diciembre de 2015, Podemos, sus confluencias e Izquierda Unida-Unidad Popular sumaron 6,1 millones de votos y 71 diputados por separado. Sumando sus votos en cada provincia y repitiendo el reparto, la lista conjunta habría sacado 86, quince más.</p>
<blockquote class="cita"><p>«Con apenas 40.000 votos más hubiéramos obtenido siete escaños. Esto es fruto de la ley electoral y las llamadas al voto útil»</p><footer>Alberto Garzón, candidato de Unidad Popular-IU, la noche del 20 de diciembre de 2015, según <a href="https://www.lamarea.com/2015/12/21/garzon-se-desploma-pero-mantiene-con-vida-a-iu/">La Marea</a>.</footer></blockquote>
<p data-tipo="dato">Seis meses después, en junio de 2016, fueron juntos como Unidos Podemos. Sacaron los mismos 71 diputados, pero con 1.024.642 votos menos. La suma no sumó. En noviembre de 2019, con Más País por su cuenta, la división costó cuatro escaños; en 2023, todos dentro de Sumar, 31.</p>
{fig_hist}
<p data-tipo="patron">Las dos lecciones van en direcciones opuestas, y por eso conviene leerlas juntas. Cuando el espacio fue dividido en muchas provincias, la ley D'Hondt le quitó escaños. Pero la única vez que pasó de dos papeletas a una perdió uno de cada seis votos. El sociólogo Antonio Antón, de la Universidad Autónoma de Madrid, lo formuló así hace casi cuatro años, en <a href="https://www.nuevatribuna.es/articulo/actualidad/union-division-frente-amplio-elecciones-podemos-sumar-politica/20221227165009206442.html">Nueva Tribuna</a>: ir separados «no penaliza la participación y el apoyo electoral» del conjunto, pero «lo que si penaliza ostensiblemente es su traslación a escaños».</p>
<p data-tipo="hipotesis">Lo que no se puede saber con los datos de 2023 es cuántos votos de Sumar irán ahora a cada papeleta, cuántos se quedarán en casa o se irán al PSOE. Un estudio de Víctor Gago Rivas, de la Universidad de Salamanca, recogido por <a href="https://cordopolis.eldiario.es/cordoba-hoy/sociedad/politologo-demuestra-coalicion-e-iu-provoco-perdida-votos_1_12725560.html">Cordópolis</a>, calculó que en 2016 «cerca de un 10 % de los votantes de la fuerza minoritaria» de 2015 no siguió a su partido. Las cuentas de esta pieza son techos, no previsiones.</p>
<h2>El Senado: la izquierda junta y la derecha, negociando</h2>
<p data-tipo="contexto">La paradoja está en la otra cámara. Para el Senado, el PSOE y el Frente Amplio registraron una lista conjunta, Senado de Progreso, en 43 provincias, con Compromís, la Chunta o Batzarre, y Podemos fuera salvo en Ibiza y Menorca. El PSOE encabeza todas las listas. En el Congreso, la izquierda irá en varias papeletas; en el Senado, buena parte de ella irá en la misma que el PSOE.</p>
<p data-tipo="contexto">La razón está en cómo se vota la Cámara Alta. En cada provincia peninsular se eligen cuatro senadores y cada votante marca hasta tres nombres, así que el más votado suele llevarse tres y el segundo, uno. «Se trata de que, en condiciones normales los candidatos pertenecientes al partido más votado se queden con la mayoría de los senadores, mientras que el segundo partido se quede con uno», lo explicaba el letrado de las Cortes Fabio Pascua Mateo en la <a href="https://revista.cortesgenerales.es/rcg/article/download/98/91">Revista de las Cortes Generales</a>.</p>
<p data-tipo="dato">Con los votos oficiales del Senado de 2023, la lista conjunta le habría ganado al PP en 17 provincias donde este sacó tres senadores, y el PP habría bajado de 120 senadores elegidos a 82, como contamos en {L("senado-psoe-frente-amplio-29n", "la pieza del Senado de Progreso")}. Si a los candidatos del PP se suman los votos que sacó Vox, la derecha volvería a 120. La diferencia se juega en 19 provincias, de Pontevedra y Huesca, las más justas, a Madrid y Málaga. Lo explicamos en {L("vox-pp-senado-pacto-29n", "las 19 del pacto")}.</p>
{fig_sen}
<p data-tipo="contexto">El PP y Vox ya no pueden ir en coalición: ese plazo acabó el 16. Lo que pueden hacer es que Vox no presente lista en algunas provincias. «Estamos hablando y vamos a seguir hablando con Vox, desde la discreción y desde el respeto», dijo Feijóo en la COPE, según <a href="https://www.elespanol.com/espana/politica/20261020/formulas-acuerdo-pp-vox-senado-retirada-listas-via-cesion-senadores-autonomicos/1003744427480_0.html">El Español</a>. Según <a href="https://www.moncloa.com/2026/10/22/pacto-pp-vox-senado-listas-3453557">Moncloa.com</a>, negocian Miguel Tellado y Montse Lluis, y Santiago Abascal lo despachó así: «Cuando haya noticias, se las daremos, pero no vamos a comunicar el estado de las negociaciones».</p>
<p data-tipo="contexto">El viernes, <a href="https://www.esdiario.com/nacional/261023/201078/vox-pone-nueva-condicion-feijoo-pactar-senado-pp-retire-dos-provincias.html">ESdiario</a> publicaba que Vox pide a cambio que el PP no se presente en dos provincias, que no han trascendido, y que el PP no acepta, por ahora, retirar sus listas en ninguna. Ninguno de los dos partidos ha confirmado un acuerdo.</p>
<p data-tipo="hipotesis">Las cuentas del Senado son una suma mecánica: suponen que todos los votantes de Vox votarían a los candidatos del PP donde Vox no se presente, y todos los de PSOE y Sumar a la lista conjunta. En el Senado eso no está garantizado, porque cada votante marca nombres y muchos marcan menos de tres o mezclan listas. Y no dicen nada de los senadores que eligen los parlamentos autonómicos.</p>
<p data-tipo="dato">Para el 29N, las alianzas quedan así: en el Congreso, el Frente Amplio y Podemos no compartirán papeleta en 47 provincias, que en 2023 dieron a Sumar 26 de sus 31 diputados; en el Senado, en una sola con el PSOE en 43. Y la derecha tiene hasta el lunes a medianoche para decidir si hace lo mismo.</p>
'''

preguntas = [
    ('¿Dónde irán juntos el Frente Amplio y Podemos el 29N?',
     'Solo en cinco provincias: Las Palmas y Santa Cruz de Tenerife, con Unidad del Pueblo Canario, y Valencia, Alicante y Castellón, con Compromís. En Cataluña, Podemos va dentro de las listas de ERC.'),
    ('¿Cuántos diputados sacó Sumar en 2023 en las provincias donde ahora irá dividido?',
     '26 de sus 31 diputados salieron de provincias donde el Frente Amplio y Podemos no comparten coalición el 29N.'),
    ('¿Cuántos escaños costó a la izquierda ir separada en 2015?',
     'Con los votos de diciembre de 2015 sumados en una lista por provincia, Podemos, sus confluencias e IU habrían sacado 86 diputados en lugar de 71. Es un cálculo que supone que no se pierde ningún voto.'),
    ('¿Qué es Senado de Progreso?',
     'La lista conjunta del PSOE y el Frente Amplio, con Compromís, la Chunta y otros partidos, para el Senado en 43 provincias. Con los votos de 2023, habría ganado al PP en 17 provincias donde este sacó tres senadores.'),
    ('¿Van juntos PP y Vox al Senado?',
     'No en coalición: el plazo acabó el 16 de octubre. Negocian que Vox no presente lista en algunas provincias. A 24 de octubre no hay acuerdo confirmado; las candidaturas se cierran el 26 de octubre a las 23.59.'),
    ('¿Cuándo se cierran las listas del 29N?',
     'El plazo para presentar candidaturas ante las juntas electorales provinciales va del 21 al 26 de octubre de 2026, hasta las 23.59.'),
]

enlaces = (f'<a href="{BASE}">Explora el mapa por sección</a> · {L("asi-queda-el-mapa-29n", "Así queda el mapa electoral antes del 29N")} · '
           f'{L("provincias-en-el-filo-29n", "Las provincias que deciden el 29N")} · {L("mapa-coaliciones-izquierda-29n", "Las coaliciones de la izquierda desde 2015")}')
foot = ('Datos: Ministerio del Interior, generales de 2015 a 2023 por mesa con voto exterior (vía pollspaindata); Junta Electoral Central, '
        'resultados del Senado de 2023 por candidato. Coaliciones según Público, elDiario.es, Europa Press y Efe. Cálculo propio con la ley D\'Hondt y la barrera del 3 %.')

pieza('coaliciones-quien-va-con-quien-29n', 'Quién va con quién el 29N',
      'Quién va con quién el 29N: Frente Amplio y Podemos, separados en 47 provincias; en 2015, juntos habrían sacado 15 diputados más',
      'El mapa de las alianzas, cerrado a falta del Senado: el Frente Amplio y Podemos, juntos solo en Canarias y la Comunitat Valenciana; el PSOE y el Frente Amplio, juntos al Senado; y PP y Vox, negociando hasta el lunes.',
      '24 de octubre de 2026', cuerpo, preguntas, enlaces, foot)
