"""Genera mapa-ca.html (versión en catalán) a partir de mapa.html, el mapa 2D.

mapa.html no tiene generador: se edita a mano. Este script aplica una lista de sustituciones
(castellano, catalán, cuántas veces aparece) y se para si alguna no aparece las veces esperadas,
igual que src/build_ca.py. Los párrafos compartidos con abstencion.html usan la traducción de
src/i18n/ca_body.html; los textos del JavaScript reutilizan los de build_ca.py.
Los datos incrustados (MAP, S, EL) no se tocan, salvo dos etiquetas visibles de S.compare.

También añade el selector de idioma ES/CA a mapa.html si todavía no lo tiene.

Uso: python3 src/build_mapa_ca.py   -> escribe mapa-ca.html
"""
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

NAV_ES = '<a href="mapa.html" aria-current="page">Mapa 2D</a></nav></div>'
LANG_CSS_AT = '.topbar .lang{margin-bottom:0}\n</style>'
LANG_CSS = ('.lang{display:flex;justify-content:flex-end;gap:6px;margin-bottom:14px;font-family:var(--mono);font-size:.78rem;letter-spacing:.06em}\n'
            '.lang a{padding:4px 10px;border:1px solid var(--rule);border-radius:4px;color:var(--muted);text-decoration:none}\n'
            '.lang a:hover{color:var(--fg);border-color:var(--muted)}\n'
            '.lang a[aria-current]{background:var(--accent);border-color:var(--accent);color:var(--bg)}\n')
LANG_ES = '<nav class="lang" aria-label="Idioma"><a href="mapa.html" hreflang="es" lang="es" aria-current="page">ES</a><a href="mapa-ca.html" hreflang="ca" lang="ca">CA</a></nav>'

# (castellano, catalán, cuántas veces aparece). En cadenas JS entre comillas simples el apóstrofo va escapado.
PAIRS = [
    # ---- cabecera
    ('<html lang="es">', '<html lang="ca">', 1),
    ('<title>¿Quién no vota en Cataluña?</title>', '<title>Qui no vota a Catalunya?</title>', 1),
    ('Mapa interactivo en 2D de la abstención en las 5.115 secciones censales de Cataluña, con gráficos por renta, estudios, paro y población extranjera.',
     'Mapa interactiu en 2D de l&#x27;abstenció a les 5.115 seccions censals de Catalunya, amb gràfics per renda, estudis, atur i població estrangera.', 2),
    ('<link rel="canonical" href="https://mapaelectoral.es/mapa.html">',
     '<link rel="canonical" href="https://mapaelectoral.es/mapa-ca.html">\n'
     '<link rel="alternate" hreflang="es" href="https://mapaelectoral.es/mapa.html">\n'
     '<link rel="alternate" hreflang="ca" href="https://mapaelectoral.es/mapa-ca.html">\n'
     '<link rel="alternate" hreflang="x-default" href="https://mapaelectoral.es/mapa.html">', 1),
    ('<meta property="og:title" content="¿Quién no vota en Cataluña? Mapa interactivo">', '<meta property="og:title" content="Qui no vota a Catalunya? Mapa interactiu">', 1),
    ('<meta property="og:url" content="https://mapaelectoral.es/mapa.html">', '<meta property="og:url" content="https://mapaelectoral.es/mapa-ca.html">', 1),
    ('<meta property="og:locale" content="es_ES">', '<meta property="og:locale" content="ca_ES">', 1),
    ('"name": "Participación y abstención por sección censal en Cataluña, 2015-2024"', '"name": "Participació i abstenció per secció censal a Catalunya, 2015-2024"', 1),
    ('"description": "Participación electoral de las 5.115 secciones censales de Cataluña en doce elecciones (Congreso, Parlament y municipales, 2015-2024), con adultos residentes, adultos sin derecho a voto, renta por unidad de consumo, edad, estudios, paro y población extranjera."',
     '"description": "Participació electoral de les 5.115 seccions censals de Catalunya en dotze eleccions (Congrés, Parlament i municipals, 2015-2024), amb adults residents, adults sense dret a vot, renda per unitat de consum, edat, estudis, atur i població estrangera."', 1),
    ('"inLanguage": "es"', '"inLanguage": "ca"', 1),
    ('"name": "Inicio", "item"', '"name": "Inici", "item"', 1),
    ('"name": "¿Quién no vota en Cataluña?", "item": "https://mapaelectoral.es/abstencion.html"', '"name": "Qui no vota a Catalunya?", "item": "https://mapaelectoral.es/ca.html"', 1),
    ('"name": "Mapa interactivo", "item": "https://mapaelectoral.es/mapa.html"', '"name": "Mapa interactiu", "item": "https://mapaelectoral.es/mapa-ca.html"', 1),
    # ---- navegación (la misma que ca.html) y selector de idioma
    ('<nav class="site" aria-label="Secciones del sitio"><a href="abstencion.html">Cataluña</a><a href="./">Mapa de resultados</a><a href="atlas/">Atlas</a><a href="mapa.html" aria-current="page">Mapa 2D</a></nav>'
     '<nav class="lang" aria-label="Idioma"><a href="mapa.html" hreflang="es" lang="es" aria-current="page">ES</a><a href="mapa-ca.html" hreflang="ca" lang="ca">CA</a></nav>',
     '<nav class="site" aria-label="Seccions del lloc"><a href="ca.html">Catalunya</a><a href="girona-ca.html">Girona</a><a href="./">Mapa de resultats</a><a href="atlas/">Atles</a><a href="mapa-ca.html" aria-current="page">Mapa 2D</a></nav>'
     '<nav class="lang" aria-label="Idioma"><a href="mapa.html" hreflang="es" lang="es">ES</a><a href="mapa-ca.html" hreflang="ca" lang="ca" aria-current="page">CA</a></nav>', 1),
    # ---- textos del cuerpo que difieren de abstencion.html
    ('<p class="lede">El 23 de julio de 2023, de cada 100 adultos que vivían en Cataluña, <span class="c-vote num" id="l-vote"></span> votaron. Otros <span class="c-no num" id="l-no"></span> no podían hacerlo porque no tienen la nacionalidad española. Y <span class="c-abst num" id="l-abst"></span> podían votar y no lo hicieron. Las cifras de participación solo cuentan el último grupo. Este mapa separa los tres, sección a sección, y los cruza con la renta, la edad, los estudios y la población extranjera.</p>',
     '<p class="lede">El 23 de juliol de 2023, de cada 100 adults que vivien a Catalunya, <span class="c-vote num" id="l-vote"></span> van votar. Uns altres <span class="c-no num" id="l-no"></span> no podien fer-ho perquè no tenen la nacionalitat espanyola. I <span class="c-abst num" id="l-abst"></span> podien votar i no ho van fer. Les dades de participació només compten l\'últim grup. Aquest mapa separa els tres, secció a secció, i els creua amb la renda, l\'edat, els estudis i la població estrangera.</p>', 1),
    ('<section class="mapband" aria-label="Mapa por sección censal">', '<section class="mapband" aria-label="Mapa per secció censal">', 1),
    ('<label for="elec">Elección', '<label for="elec">Elecció', 1),
    ('<option value="g2023">Congreso, julio de 2023</option><option value="m2023">Municipales, mayo de 2023</option><option value="p2024">Parlament, mayo de 2024</option>',
     '<option value="g2023">Congrés, juliol de 2023</option><option value="m2023">Municipals, maig de 2023</option><option value="p2024">Parlament, maig de 2024</option>', 1),
    ('<label for="var">Qué se pinta', '<label for="var">Què es pinta', 1),
    ('<label for="town">Acercar a', '<label for="town">Anar a', 1),
    ('<option value="">Toda Cataluña</option>', '<option value="">Tota Catalunya</option>', 1),
    ('<button id="reset" type="button">Ver Cataluña</button>', '<button id="reset" type="button">Veure Catalunya</button>', 1),
    ('aria-label="Mapa de secciones censales de Cataluña"', 'aria-label="Mapa de seccions censals de Catalunya"', 1),
    ('<p>Estas variables van juntas: las secciones pobres también tienen menos universitarios, más paro y más extranjeros. Un modelo que las considera a la vez (regresión ponderada por censo, 5.041 secciones) explica <span class="num" id="r2"></span> de las diferencias de participación entre secciones. Cada barra indica cuántos puntos cambia la participación cuando la variable sube una desviación típica y las demás se mantienen fijas.</p>',
     '<p>Aquestes variables van juntes: les seccions pobres també tenen menys universitaris, més atur i més estrangers. Un model que les considera alhora (regressió ponderada pel cens, 5.041 seccions) explica <span class="num" id="r2"></span> de les diferències de participació entre seccions. Cada barra indica quants punts canvia la participació quan la variable puja una desviació típica i les altres es mantenen fixes.</p>', 1),
    ('<p>Hay una segunda abstención, coyuntural, que no sigue la renta sino el voto. Entre noviembre de 2019 y julio de 2023 la participación cayó 6,7 puntos en Cataluña, pero mucho más donde el independentismo era más fuerte. En el cuarto de secciones con más voto a ERC, Junts y la CUP en 2019, la participación bajó <span class="num" id="d-hi"></span> puntos; en el cuarto con menos, <span class="num" id="d-lo"></span>. El voto independentista pasó del 42% al 27% de los votos emitidos.</p>',
     '<p>Hi ha una segona abstenció, conjuntural, que no segueix la renda sinó el vot. Entre el novembre de 2019 i el juliol de 2023 la participació va caure 6,7 punts a Catalunya, però molt més on l\'independentisme era més fort. En el quart de seccions amb més vot a ERC, Junts i la CUP el 2019, la participació va baixar <span class="num" id="d-hi"></span> punts; en el quart amb menys, <span class="num" id="d-lo"></span>. El vot independentista va passar del 42% al 27% dels vots emesos.</p>', 1),
    ('<h2 id="sobre-la-pieza">Sobre este mapa</h2>', '<h2 id="sobre-la-pieza">Sobre aquest mapa</h2>', 1),
    ('<li><b>Publicado:</b> 5 de octubre de 2026. <b>Actualizado:</b> 6 de octubre de 2026, con las correcciones que se indican abajo.</li>',
     '<li><b>Publicat:</b> 5 d\'octubre de 2026. <b>Actualitzat:</b> 6 d\'octubre de 2026, amb les correccions que s\'indiquen a sota.</li>', 1),
    ('<p class="note">Datos limpios: catalunya_secciones_2023.csv y .geojson, el histórico por sección y las tablas de Girona, en la carpeta abstencion del proyecto.</p>',
     '<p class="note">Dades netes: catalunya_secciones_2023.csv i .geojson, l\'històric per secció i les taules de Girona, a la carpeta abstencion del projecte.</p>', 1),
    # ---- párrafos compartidos con abstencion.html (traducción de src/i18n/ca_body.html)
    ('<div class="kicker">Cataluña · elecciones generales 2015–2023 · 5.115 secciones censales</div>',
     '<div class="kicker">Catalunya · eleccions generals 2015–2023 · 5.115 seccions censals</div>', 1),
    ('<h1>¿Quién no vota en Cataluña?</h1>',
     '<h1>Qui no vota a Catalunya?</h1>', 1),
    ('<div class="hundred" id="hundred" aria-label="100 adultos residentes en Cataluña"></div>',
     '<div class="hundred" id="hundred" aria-label="100 adults residents a Catalunya"></div>', 1),
    ('<div class="legend3"><span><b style="background:var(--vote)"></b>votó</span><span><b style="background:var(--noright)"></b>sin derecho a voto</span><span><b style="background:var(--abst)"></b>pudo votar y no votó</span></div>',
     '<div class="legend3"><span><b style="background:var(--vote)"></b>va votar</span><span><b style="background:var(--noright)"></b>sense dret a vot</span><span><b style="background:var(--abst)"></b>podia votar i no va votar</span></div>', 1),
    ('<h2>Dos maneras de no votar</h2>',
     '<h2>Dues maneres de no votar</h2>', 1),
    ('<p>Salt, Lloret de Mar, Salou y Figueres son los municipios catalanes de más de 20.000 habitantes donde menos adultos votan: entre 34 y 39 de cada 100 empadronados. El primer motivo no es el desinterés: entre el 29% y el 39% de sus adultos son extranjeros sin derecho a voto en unas generales. Pero los que sí pueden votar también votan menos: un 55% en Salt y Figueres y un 58% en Lloret, entre siete y diez puntos por debajo de la media catalana (65%). Son dos fenómenos que se suman y que la cifra oficial de participación mezcla, porque solo divide por el censo.</p>',
     '<p>Salt, Lloret de Mar, Salou i Figueres són els municipis catalans de més de 20.000 habitants on voten menys adults: entre 34 i 39 de cada 100 empadronats. El primer motiu no és el desinterès: entre el 29% i el 39% dels seus adults són estrangers sense dret a vot en unes generals. Però els qui sí que poden votar també voten menys: un 55% a Salt i Figueres i un 58% a Lloret, entre set i deu punts per sota de la mitjana catalana (65%). Són dos fenòmens que se sumen i que la xifra oficial de participació barreja, perquè només divideix pel cens.</p>', 1),
    ('<p>Guissona es el caso extremo del primer fenómeno: más de la mitad de sus adultos no puede votar, y solo 29 de cada 100 lo hicieron, aunque la participación sobre el censo (61%) es casi normal. En el otro extremo, Sant Cugat del Vallès combina renta alta, universitarios y pocos extranjeros: vota el 72% de su censo y 63 de cada 100 adultos.</p>',
     "<p>Guissona és el cas extrem del primer fenomen: més de la meitat dels seus adults no pot votar, i només 29 de cada 100 ho van fer, tot i que la participació sobre el cens (61%) és gairebé normal. A l'altre extrem, Sant Cugat del Vallès combina renda alta, universitaris i pocs estrangers: hi vota el 72% del cens i 63 de cada 100 adults.</p>", 1),
    ('<p class="note" style="margin-top:8px">Participación = votos emitidos / censo electoral residente (CER). Adultos = población de 18 años o más (Atlas de Renta del INE, 1 de enero de 2023). Sin derecho a voto ≈ adultos residentes − censo electoral. Las líneas recorren las generales de 2015, 2016, abril de 2019, noviembre de 2019 y 2023.</p>',
     '<p class="note" style="margin-top:8px">Participació = vots emesos / cens electoral resident (CER). Adults = població de 18 anys o més (Atlas de Renda de l\'INE, 1 de gener de 2023). Sense dret a vot ≈ adults residents − cens electoral. Les línies recorren les generals del 2015, el 2016, l\'abril del 2019, el novembre del 2019 i el 2023.</p>', 1),
    ('<h2>Qué separa una sección que vota de una que no</h2>',
     "<h2>Què separa una secció que vota d'una que no</h2>", 1),
    ('<p>Ordenando las 5.115 secciones de Cataluña en cinco grupos iguales según cada variable, la pauta es la misma: donde hay menos renta, menos estudios superiores, más paro, más extranjeros o población más joven, se vota menos. La barra completa (con el número encima) es la participación entre quienes pueden votar; su parte oscura, qué parte de todos los adultos residentes votó. La franja clara entre ambas crece donde hay más vecinos sin derecho a voto.</p>',
     "<p>Si s'ordenen les 5.115 seccions de Catalunya en cinc grups iguals segons cada variable, la pauta és la mateixa: on hi ha menys renda, menys estudis superiors, més atur, més estrangers o població més jove, es vota menys. La barra completa (amb el número a sobre) és la participació entre els qui poden votar; la part fosca, quina part de tots els adults residents va votar. La franja clara entre totes dues creix on hi ha més veïns sense dret a vot.</p>", 1),
    ('<h2>Lo que pesa cuando se mira todo a la vez</h2>',
     '<h2>El que pesa quan es mira tot alhora</h2>', 1),
    ('<p class="callout">Lo que más pesa es la educación, a mucha distancia de todo lo demás, seguida del paro. La renta, que por sí sola es lo que más se parece al mapa de la abstención, deja de añadir información cuando se tienen en cuenta los estudios y el empleo. El modelo describe asociaciones entre secciones, no causas.</p>',
     '<p class="callout">El que pesa més és l\'educació, a molta distància de tota la resta, seguida de l\'atur. La renda, que per si sola és el que s\'assembla més al mapa de l\'abstenció, deixa d\'afegir informació quan es tenen en compte els estudis i la feina. El model descriu associacions entre seccions, no causes.</p>', 1),
    ('<p>Hay efectos que no son económicos. Un porcentaje de extranjeros más alto sigue asociado a menos participación incluso entre quienes sí tienen derecho a voto, y las secciones con más españoles nacidos en el extranjero también votan menos. Es plausible que influyan los hogares mixtos y unas campañas que apenas se dirigen a estos vecinos, aunque los datos agregados no lo pueden demostrar. Parte del efecto puede ser inflación del padrón: personas empadronadas que ya se han ido y que cuentan como abstención. Las segundas residencias y el alquiler también se asocian a menos participación: en la costa hay empadronados que pasan buena parte del año en otro lugar, y en una elección celebrada el 23 de julio eso puede notarse. Con la edad pasa lo contrario: los barrios más envejecidos votan más.</p>',
     "<p>Hi ha efectes que no són econòmics. Un percentatge d'estrangers més alt continua associat a menys participació fins i tot entre els qui sí que tenen dret a vot, i les seccions amb més espanyols nascuts a l'estranger també voten menys. És plausible que hi influeixin les llars mixtes i unes campanyes que gairebé no s'adrecen a aquests veïns, tot i que les dades agregades no ho poden demostrar. Part de l'efecte pot ser inflació del padró: persones empadronades que ja han marxat i que compten com a abstenció. Les segones residències i el lloguer també s'associen a menys participació: a la costa hi ha empadronats que passen bona part de l'any en un altre lloc, i en unes eleccions celebrades el 23 de juliol això es pot notar. Amb l'edat passa el contrari: els barris més envellits voten més.</p>", 1),
    ('<p>Una advertencia necesaria: son datos por sección, no por persona. Dicen dónde se vota menos, no que cada extranjero nacionalizado o cada parado vote menos. Para afirmar eso hacen falta encuestas individuales.</p>',
     '<p>Un advertiment necessari: són dades per secció, no per persona. Diuen on es vota menys, no que cada estranger nacionalitzat o cada aturat voti menys. Per afirmar-ho calen enquestes individuals.</p>', 1),
    ('<h2>2023: la otra abstención</h2>',
     "<h2>2023: l'altra abstenció</h2>", 1),
    ('<p>Así, los pueblos pequeños del interior, que siguen votando más que la media, perdieron más participación que las ciudades del área metropolitana. Pero en el conjunto de Cataluña la diferencia entre campo y ciudad es pequeña: Barcelona vota más que la media (67%) porque sus barrios ricos compensan a los pobres. La diferencia más grande no es territorial, sino de renta, y pasa por dentro de cada ciudad. En Salt, Lloret o Figueres la abstención alta no es nueva: se repite elección tras elección desde 2015.</p>',
     "<p>Així, els pobles petits de l'interior, que continuen votant més que la mitjana, van perdre més participació que les ciutats de l'àrea metropolitana. Però en el conjunt de Catalunya la diferència entre camp i ciutat és petita: Barcelona vota més que la mitjana (67%) perquè els seus barris rics compensen els pobres. La diferència més gran no és territorial, sinó de renda, i passa per dins de cada ciutat. A Salt, Lloret o Figueres l'abstenció alta no és nova: es repeteix elecció rere elecció des del 2015.</p>", 1),
    ('<h2>Cuanto más cerca, menos se vota</h2>',
     '<h2>Com més a prop, menys es vota</h2>', 1),
    ('<p>Las elecciones municipales y las del Parlament, las más cercanas, son las que menos participación tienen: un 56% y un 58% del censo frente al 65% del Congreso. Y la distancia entre secciones ricas y pobres no se reduce, crece. En el Congreso, el decil de secciones más ricas votó 18 puntos más que el más pobre; en las municipales, 19; en el Parlament, 24.</p>',
     '<p>Les eleccions municipals i les del Parlament, les més properes, són les que tenen menys participació: un 56% i un 58% del cens davant del 65% del Congrés. I la distància entre seccions riques i pobres no es redueix, creix. Al Congrés, el decil de seccions més riques va votar 18 punts més que el més pobre; a les municipals, 19; al Parlament, 24.</p>', 1),
    ("<p>En el decil más pobre, además, el 31% de los adultos no tiene derecho a voto ni siquiera en las municipales, frente al 12% en el más rico. En las municipales también votan los ciudadanos de la UE y de los países con convenio inscritos en el censo, unos 68.000 en toda Cataluña, pero eso solo baja un punto el total de adultos sin derecho a voto. Donde más se nota es en la costa turística del Empordà y la Selva: Castelló d'Empúries (9% del censo municipal), Roses (8%), Platja d'Aro (7,8%) y Lloret (7,2%).</p>",
     "<p>En el decil més pobre, a més, el 31% dels adults no té dret a vot ni tan sols a les municipals, davant del 12% en el més ric. A les municipals també hi voten els ciutadans de la UE i dels països amb conveni inscrits al cens, uns 68.000 a tot Catalunya, però això només fa baixar un punt el total d'adults sense dret a vot. On més es nota és a la costa turística de l'Empordà i la Selva: Castelló d'Empúries (9% del cens municipal), Roses (8%), Platja d'Aro (7,8%) i Lloret (7,2%).</p>", 1),
    ('<p>Hay un solo lugar donde se vota más al ayuntamiento que al Congreso: los 589 municipios de menos de 2.000 habitantes (69% frente a 67%), donde además solo el 9% de los adultos no puede votar. En Salt, Lloret y Figueres pasa al revés, con un 47-48% en las municipales. Y lo que explica la participación cambia con la elección: en las generales pesan más los estudios; en las municipales, el paro, y en el Parlament, los dos por igual.</p>',
     "<p>Només hi ha un lloc on es vota més l'ajuntament que el Congrés: els 589 municipis de menys de 2.000 habitants (69% davant de 67%), on a més només el 9% dels adults no pot votar. A Salt, Lloret i Figueres passa al revés, amb un 47-48% a les municipals. I el que explica la participació canvia amb l'elecció: a les generals pesen més els estudis; a les municipals, l'atur, i al Parlament, tots dos per igual.</p>", 1),
    ('<h2>Las secciones que menos votan</h2>',
     '<h2>Les seccions que voten menys</h2>', 1),
    ('<p>Las participaciones más bajas de Cataluña no están donde hay más extranjeros. Nueve de las diez están en secciones de Figueres, El Prat, Badalona, Lleida, Sant Adrià de Besòs, Reus y Girona con paros de casi el 40% o más, rentas de entre 9.600 y 13.100 euros por unidad de consumo y menos de un 10% de adultos con estudios superiores. En ellas, la mayoría de los vecinos tiene la nacionalidad española, y aun así vota entre uno de cada cinco y uno de cada tres inscritos. La décima, en el Raval de Barcelona, tiene más renta y más vecinos sin derecho a voto. Es la abstención de los barrios con más paro y menos renta, y es la que menos aparece en las cifras de participación.</p>',
     "<p>Les participacions més baixes de Catalunya no són on hi ha més estrangers. Nou de les deu són en seccions de Figueres, el Prat, Badalona, Lleida, Sant Adrià de Besòs, Reus i Girona amb un atur de gairebé el 40% o més, rendes d'entre 9.600 i 13.100 euros per unitat de consum i menys d'un 10% d'adults amb estudis superiors. En aquestes, la majoria dels veïns té la nacionalitat espanyola, i tot i així hi vota entre un de cada cinc i un de cada tres inscrits. La desena, al Raval de Barcelona, té més renda i més veïns sense dret a vot. És l'abstenció dels barris amb més atur i menys renda, i és la que menys surt a les dades de participació.</p>", 1),
    ('<p class="note" style="margin-top:8px">Secciones con más de 300 electores. En alguna sección, como la del Raval que aparece en la lista, el censo electoral supera a los adultos estimados (habitual donde hay muchas inscripciones en domicilios de servicios sociales) y el grupo "sin derecho a voto" se pone a cero.</p>',
     '<p class="note" style="margin-top:8px">Seccions amb més de 300 electors. En alguna secció, com la del Raval que surt a la llista, el cens electoral supera els adults estimats (habitual on hi ha moltes inscripcions en domicilis de serveis socials) i el grup "sense dret a vot" es posa a zero.</p>', 1),
    ('<h2>Método y fuentes</h2>',
     '<h2>Mètode i fonts</h2>', 1),
    ('<li><b>Resultados:</b> elecciones al Congreso de 2015, 2016, abril y noviembre de 2019 y julio de 2023, por mesa, agregadas a sección censal. Microdatos del Ministerio del Interior, en la versión procesada del paquete <a href="https://github.com/dadosdelaplace/pollspain" target="_blank" rel="noopener">pollspain</a>. Se excluye el voto de residentes en el extranjero (CERA).</li>',
     '<li><b>Resultats:</b> eleccions al Congrés del 2015, el 2016, l\'abril i el novembre del 2019 i el juliol del 2023, per mesa, agregades a secció censal. Microdades del Ministeri de l\'Interior, en la versió processada del paquet <a href="https://github.com/dadosdelaplace/pollspain" target="_blank" rel="noopener">pollspain</a>. S\'exclou el vot dels residents a l\'estranger (CERA).</li>', 1),
    ('<li><b>Renta, edad y nacionalidad:</b> Atlas de Distribución de Renta de los Hogares del INE, datos de 2023 por sección (renta por unidad de consumo, edad media, % de población española), vía <a href="https://github.com/pablogguz/ineAtlas.data" target="_blank" rel="noopener">ineAtlas.data</a>.</li>',
     '<li><b>Renda, edat i nacionalitat:</b> Atlas de Distribució de Renda de les Llars de l\'INE, dades del 2023 per secció (renda per unitat de consum, edat mitjana, % de població espanyola), via <a href="https://github.com/pablogguz/ineAtlas.data" target="_blank" rel="noopener">ineAtlas.data</a>.</li>', 1),
    ('<li><b>Estudios, paro, vivienda y nacidos en el extranjero:</b> Censo de Población y Viviendas 2021 del INE por sección. Españoles nacidos fuera ≈ % nacidos en el extranjero − % extranjeros.</li>',
     "<li><b>Estudis, atur, habitatge i nascuts a l'estranger:</b> Cens de Població i Habitatges 2021 de l'INE per secció. Espanyols nascuts fora ≈ % nascuts a l'estranger − % estrangers.</li>", 1),
    ('<li><b>Por qué la serie larga es de generales:</b> son las únicas con resultados por mesa desde 2015, y tienen una ventaja: en el Congreso solo votan españoles, de modo que la frontera entre "sin derecho" y "abstención" es limpia. En las municipales votan además los ciudadanos de la UE y de algunos países con convenio, lo que reduce el grupo "sin derecho a voto" en la costa.</li>',
     '<li><b>Per què la sèrie llarga és de generals:</b> són les úniques amb resultats per mesa des del 2015, i tenen un avantatge: al Congrés només hi voten espanyols, de manera que la frontera entre "sense dret" i "abstenció" és neta. A les municipals hi voten a més els ciutadans de la UE i d\'alguns països amb conveni, cosa que redueix el grup "sense dret a vot" a la costa.</li>', 1),
    ('<li><b>Municipales 2023 y Parlament 2024:</b> participación por sección censal del Departament de Polítiques Digitals, vía <a href="https://analisi.transparenciacatalunya.cat" target="_blank" rel="noopener">Transparència Catalunya</a> (dataset irrv-2mfc). Sus cifras del Congreso 2023 coinciden sección a sección con las del Ministerio del Interior.</li>',
     '<li><b>Municipals 2023 i Parlament 2024:</b> participació per secció censal del Departament de Polítiques Digitals, via <a href="https://analisi.transparenciacatalunya.cat" target="_blank" rel="noopener">Transparència Catalunya</a> (conjunt de dades irrv-2mfc). Les seves xifres del Congrés 2023 coincideixen secció a secció amb les del Ministeri de l\'Interior.</li>', 1),
    ('<li><b>Contraste con Idescat:</b> la renta y la población extranjera del INE se han comparado con las de Idescat (<a href="https://www.idescat.cat/emex/" target="_blank" rel="noopener">EMEX</a>, renta familiar disponible por habitante y población extranjera de 2025). Por municipio correlacionan 0,94 en ambos casos, y la relación con la participación sale prácticamente igual con una fuente u otra, así que las conclusiones no dependen de usar el INE o Idescat. El mapa usa el INE porque es la única fuente con estos datos por sección censal.</li>',
     '<li><b>Contrast amb l\'Idescat:</b> la renda i la població estrangera de l\'INE s\'han comparat amb les de l\'Idescat (<a href="https://www.idescat.cat/emex/" target="_blank" rel="noopener">EMEX</a>, renda familiar disponible per habitant i població estrangera del 2025). Per municipi correlacionen 0,94 en tots dos casos, i la relació amb la participació surt pràcticament igual amb una font o l\'altra, de manera que les conclusions no depenen de fer servir l\'INE o l\'Idescat. El mapa fa servir l\'INE perquè és l\'única font amb aquestes dades per secció censal.</li>', 1),
    ('<li><b>Limitaciones:</b> la población adulta se estima con el % de menores de 18 del Atlas; el censo electoral de julio y la población de enero no son exactamente la misma foto; el Censo 2021 no cubre 73 secciones creadas después y el Atlas no da renta por unidad de consumo en 30.</li>',
     "<li><b>Limitacions:</b> la població adulta s'estima amb el % de menors de 18 anys de l'Atlas; el cens electoral de juliol i la població de gener no són exactament la mateixa foto; el Cens 2021 no cobreix 73 seccions creades després i l'Atlas no dona renda per unitat de consum en 30.</li>", 1),
    ('<li><b>Qué se compara:</b> en cada una de las 5.115 secciones censales de 2023, cuántos adultos residentes votaron, cuántos no tenían derecho a voto y cuántos pudieron votar y no lo hicieron en el Congreso del 23 de julio de 2023, junto con la renta, la edad y la nacionalidad (Atlas de Renta del INE, 2023) y los estudios, el paro y la vivienda (Censo 2021). La evolución compara doce elecciones, de 2015 a 2024, sobre esas mismas secciones.</li>',
     "<li><b>Què es compara:</b> a cadascuna de les 5.115 seccions censals de 2023, quants adults residents van votar, quants no tenien dret a vot i quants podien votar i no ho van fer al Congrés del 23 de juliol de 2023, juntament amb la renda, l'edat i la nacionalitat (Atlas de Renda de l'INE, 2023) i els estudis, l'atur i l'habitatge (Cens 2021). L'evolució compara dotze eleccions, del 2015 al 2024, sobre aquestes mateixes seccions.</li>", 1),
    ('<li><b>Límites:</b> son datos agregados por sección, no por persona. Las relaciones que se describen son asociaciones: el modelo estadístico dice qué va junto, no qué causa qué. «Sin derecho a voto» es una estimación (adultos residentes menos censo electoral), no un recuento de extranjeros. Las citas de expertos hablan de la abstención en general, no de estos datos. Detalle en la <a href="metodologia.html">metodología completa</a>.</li>',
     '<li><b>Límits:</b> són dades agregades per secció, no per persona. Les relacions que es descriuen són associacions: el model estadístic diu què va junt, no què causa què. «Sense dret a vot» és una estimació (adults residents menys cens electoral), no un recompte d\'estrangers. Les cites d\'experts parlen de l\'abstenció en general, no d\'aquestes dades. Detall a la <a href="metodologia-ca.html">metodologia completa</a>.</li>', 1),
    ('<li><b>Autoría y revisión:</b> datos, texto y gráficos de Nacho G. del Álamo, que también revisa los datos y el texto antes de publicar. Cada cifra del texto se recalcula con un script a partir de los datos publicados, y los totales se contrastan con los resultados oficiales de la Generalitat.</li>',
     '<li><b>Autoria i revisió:</b> dades, text i gràfics de Nacho G. del Álamo, que també en revisa les dades i el text abans de publicar. Cada xifra del text es recalcula amb un script a partir de les dades publicades, i els totals es contrasten amb els resultats oficials de la Generalitat.</li>', 1),
    ('<li><b>Correcciones (6 de octubre de 2026):</b> en la sección de Figueres con menos participación el paro es del 59% (58,5%), no del 58%; el voto independentista de 2023 era el 28% contando al PDeCAT, pero ERC, Junts y la CUP suman el 27%; en el Parlament de 2015 la distancia entre el 20% de secciones más ricas y el 20% más pobre era de 13 puntos, no de 14; el Censo 2021 no cubre 73 secciones (no 74) y el Atlas no da renta por unidad de consumo en 30 (no 20). Ninguna cambia las conclusiones. Además, tras revisar el texto con el estándar de verificación: los 68.000 inscritos en el censo municipal incluyen a los ciudadanos de países con convenio, no solo a europeos, y son alrededor del 13% de los extranjeros que podrían votar (no uno de cada cuatro europeos); y varias explicaciones que se daban como hechos se presentan ahora como hipótesis o atribuidas a los investigadores (el julio de Lloret, Guissona, el desgaste independentista, el círculo de las campañas, el modelo).</li>',
     "<li><b>Correccions (6 d'octubre de 2026):</b> a la secció de Figueres amb menys participació l'atur és del 59% (58,5%), no del 58%; el vot independentista del 2023 era el 28% comptant-hi el PDeCAT, però ERC, Junts i la CUP sumen el 27%; al Parlament del 2015 la distància entre el 20% de seccions més riques i el 20% més pobre era de 13 punts, no de 14; el Cens 2021 no cobreix 73 seccions (no 74) i l'Atlas no dona renda per unitat de consum en 30 (no 20). Cap no canvia les conclusions. A més, després de revisar el text amb l'estàndard de verificació: els 68.000 inscrits al cens municipal inclouen els ciutadans de països amb conveni, no només europeus, i són al voltant del 13% dels estrangers que podrien votar (no un de cada quatre europeus); i diverses explicacions que es donaven com a fets es presenten ara com a hipòtesis o atribuïdes als investigadors (el juliol de Lloret, Guissona, el desgast independentista, el cercle de les campanyes, el model).</li>", 1),
    ('<footer class="note">Análisis por sección censal. Elaboración propia con datos del Ministerio del Interior y del INE.</footer>',
     '<footer class="note">Anàlisi per secció censal. Elaboració pròpia amb dades del Ministeri de l\'Interior i de l\'INE.</footer>', 1),
    # ---- JavaScript: formatos y orden
    ("toLocaleString('es-ES')", "toLocaleString('ca-ES')", 8),
    ("localeCompare(b,'es')", "localeCompare(b,'ca')", 1),
    # elecciones
    ("const ELN = {g2023:'Congreso, julio de 2023', m2023:'municipales, mayo de 2023', p2024:'Parlament, mayo de 2024'};",
     "const ELN = {g2023:'Congrés, juliol de 2023', m2023:'municipals, maig de 2023', p2024:'Parlament, maig de 2024'};", 1),
    ("m2023:'municipales 23'", "m2023:'municipals 23'", 1),
    # variables del mapa
    ("name:'Abstención entre quienes pueden votar'", "name:'Abstenció entre els qui poden votar'", 1),
    ("'más abstención'", "'més abstenció'", 1),
    ("name:'Adultos residentes que no votaron'", "name:'Adults residents que no van votar'", 1),
    ("'más adultos sin votar'", "'més adults sense votar'", 1),
    ("name:'Adultos sin derecho a voto'", "name:'Adults sense dret a vot'", 1),
    ("'más adultos sin derecho'", "'més adults sense dret'", 1),
    ("name:'Caída de participación nov. 2019 → 2023'", "name:'Caiguda de participació nov. 2019 → 2023'", 1),
    ("'más caída'", "'més caiguda'", 1),
    ("name:'Renta por unidad de consumo (oscuro = más baja)'", "name:'Renda per unitat de consum (fosc = més baixa)'", 1),
    ("'menos renta'", "'menys renda'", 1),
    ("name:'Población extranjera (Censo 2021)'", "name:'Població estrangera (Cens 2021)'", 1),
    ("'más extranjeros'", "'més estrangers'", 1),
    ("name:'Adultos sin estudios superiores'", "name:'Adults sense estudis superiors'", 1),
    ("'menos estudios'", "'menys estudis'", 1),
    ("name:'Tasa de paro (Censo 2021)'", "name:'Taxa d\\'atur (Cens 2021)'", 1),
    ("'más paro'", "'més atur'", 1),
    ("name:'Edad media (oscuro = más joven)'", "name:'Edat mitjana (fosc = més jove)'", 1),
    ("'más joven'", "'més jove'", 1),
    ("name:'Voto independentista nov. 2019'", "name:'Vot independentista nov. 2019'", 1),
    ("'más independentista'", "'més independentista'", 1),
    ("' años'", "' anys'", 2),
    ('<span>· oscuro = ${v.hi}</span>', '<span>· fosc = ${v.hi}</span>', 1),
    ("V.name.replace(/ \\(oscuro.*\\)/,'')", "V.name.replace(/ \\(fosc.*\\)/,'')", 1),
    # selector de municipio
    ("og1.label='Destacados'", "og1.label='Destacats'", 1),
    ("og2.label='Todos los municipios'", "og2.label='Tots els municipis'", 1),
    # ficha
    ('aria-label="votó ${pct(v)}, sin derecho ${pct(n)}, no votó ${pct(a)}"', 'aria-label="va votar ${pct(v)}, sense dret ${pct(n)}, no va votar ${pct(a)}"', 1),
    ('${n(vo)} votaron</span>', '${n(vo)} van votar</span>', 1),
    ('unos ${n(si)} sin derecho a voto', 'uns ${n(si)} sense dret a vot', 1),
    ('${n(ab)} podían votar y no lo hicieron', '${n(ab)} podien votar i no ho van fer', 1),
    ('aria-label="Participación por elección"', 'aria-label="Participació per elecció"', 1),
    ('<div class="kicker">Sección ${', '<div class="kicker">Secció ${', 1),
    ('Adultos que viven en la sección, en personas', 'Adults que viuen a la secció, en persones', 1),
    ('Adultos que viven aquí, en personas', 'Adults que hi viuen, en persones', 1),
    ('Participación sobre censo, generales', 'Participació sobre el cens, generals', 2),
    ('<dt>Censo / votantes (', '<dt>Cens / votants (', 1),
    ('<dt>Renta por unidad de consumo</dt>', '<dt>Renda per unitat de consum</dt>', 1),
    ('<dt>Edad media</dt><dd>${p.mean_age?.toFixed(1).replace(\'.\',\',\')} años</dd>', '<dt>Edat mitjana</dt><dd>${p.mean_age?.toFixed(1).replace(\'.\',\',\')} anys</dd>', 1),
    ('<dt>Extranjeros</dt>', '<dt>Estrangers</dt>', 1),
    ('<dt>Españoles nacidos fuera</dt>', '<dt>Espanyols nascuts fora</dt>', 1),
    ('<dt>Con estudios superiores</dt>', '<dt>Amb estudis superiors</dt>', 1),
    ('<dt>Paro</dt>', '<dt>Atur</dt>', 1),
    ('<dt>Viviendas secundarias</dt>', '<dt>Habitatges secundaris</dt>', 1),
    ('<dt>Voto independentista N19</dt>', '<dt>Vot independentista N19</dt>', 1),
    ('<dt>Secciones</dt>', '<dt>Seccions</dt>', 1),
    ('<dt>Adultos residentes</dt>', '<dt>Adults residents</dt>', 1),
    ('<dt>Censo electoral</dt>', '<dt>Cens electoral</dt>', 1),
    ('<dt>Votantes (', '<dt>Votants (', 1),
    ('Pasa el cursor o toca una sección para ver su ficha.', 'Passa el cursor o toca una secció per veure\'n la fitxa.', 1),
    ("aggPanel('Cataluña','947 municipios',", "aggPanel('Catalunya','947 municipis',", 1),
    ("aggPanel(n,'Municipio',", "aggPanel(n,'Municipi',", 1),
    # tabla de comparación (dos etiquetas visibles de los datos S.compare)
    ('<th>Dónde</th><th>Población</th><th>De cada 100 adultos</th><th>Partic. 23J</th><th>Renta u.c.</th><th>Extranj.</th>',
     '<th>On</th><th>Població</th><th>De cada 100 adults</th><th>Partic. 23J</th><th>Renda u.c.</th><th>Estrang.</th>', 1),
    ('"name": "Pueblos de menos de 2.000 hab."', '"name": "Pobles de menys de 2.000 hab."', 1),
    ('"name": "Catalu\\u00f1a"', '"name": "Catalunya"', 1),
    # gráficos por quintil
    ("'Renta por unidad de consumo'", "'Renda per unitat de consum'", 1),
    ("'Con estudios superiores'", "'Amb estudis superiors'", 1),
    ("'Tasa de paro'", "'Taxa d\\'atur'", 1),
    ("'Población extranjera'", "'Població estrangera'", 1),
    ("'Edad media'", "'Edat mitjana'", 2),
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
]


def main():
    path = ROOT / 'mapa.html'
    s = path.read_text(encoding='utf-8')
    # selector de idioma en la versión castellana (una sola vez)
    if LANG_ES not in s:
        if s.count(NAV_ES) != 1:
            sys.exit('No encuentro la navegación de mapa.html para añadir el selector de idioma.')
        s = s.replace(NAV_ES, NAV_ES[:-len('</div>')] + LANG_ES + '</div>')
        path.write_text(s, encoding='utf-8')
        print('mapa.html: añadido el selector ES/CA')
    if LANG_CSS not in s:  # estilos del selector, copiados de abstencion.html
        if s.count(LANG_CSS_AT) != 1:
            sys.exit('No encuentro dónde añadir los estilos del selector de idioma en mapa.html.')
        s = s.replace(LANG_CSS_AT, LANG_CSS + LANG_CSS_AT)
        path.write_text(s, encoding='utf-8')
        print('mapa.html: añadidos los estilos del selector ES/CA')
    for old, new, n in PAIRS:
        c = s.count(old)
        if c != n:
            sys.exit(f'{c} apariciones (esperaba {n}): {old[:70]}')
        s = s.replace(old, new)
    (ROOT / 'mapa-ca.html').write_text(s, encoding='utf-8')
    print('mapa-ca.html escrito,', len(s), 'bytes,', len(PAIRS), 'sustituciones')


main()
