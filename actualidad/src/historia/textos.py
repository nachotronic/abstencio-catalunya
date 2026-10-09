"""Textos, gráficos y ficha de cada pieza de la serie «Historia electoral».

Cada pieza: slug, titulo (titular), corto (<title> de trabajo), dek, cuerpo(figura) → HTML, js (llamadas a graficos.js
con D = datos de datos.json), datos (claves de datos.json que usa), pie, y la ficha para construir.py
(descripcion, compara, limites, fuentes, lugar, enlaces).
Todas las cifras salen de datos.json (datos.py) salvo las oficiales, que llevan su fuente.
"""

INTERIOR_HIST = ('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/',
                 'Ministerio del Interior (Infoelectoral), resultados por municipio y por mesa de las elecciones generales, municipales y europeas desde 1977; '
                 'de 1986 a 2003, vía pollspaindata. Sin voto exterior (CERA)')
CIVIO_29N = ('https://civio.es/el-boe-nuestro-de-cada-dia/2026/10/06/llega-al-boe-la-convocatoria-de-elecciones-para-el-29-de-noviembre-todas-las-fechas-y-pasos-hasta-ese-dia/',
             'Civio, la convocatoria de las elecciones del 29 de noviembre en el BOE (6-10-2026)')
WIKI_GENERALES = ('https://es.wikipedia.org/wiki/Elecciones_generales_de_Espa%C3%B1a',
                  'Wikipedia, «Elecciones generales de España», resultados oficiales de 1977 a 2023 (consultada el 8-10-2026)')
FAMILIAS = ('Familias de partidos del mapa: AP/CD/CP y PP; PCE, PSUC, IU, Podemos y confluencias, Sumar; CiU y Junts; HB, EH y EH Bildu; '
            'UCD y CDS aparte. El ganador de cada municipio se calcula con todas las listas, también las locales y regionales.')
SIN_CERA = 'Sin voto exterior (CERA): la participación sale algo por encima de la oficial.'
PIE = ('Datos: Ministerio del Interior (Infoelectoral), resultados por municipio y por mesa desde 1977, sin voto exterior. '
       'Borrador: pendiente de revisión antes de publicar.')
GANCHO_29N = ('Las generales del 29 de noviembre serán las decimoséptimas desde 1977. '
              'Con todas las elecciones de la democracia ya en el mapa, municipio a municipio, se puede mirar hacia atrás antes de votar.')

P = []

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='plasencia-acierta-siempre', lugar='España', datos=['ohio'],
    corto='Plasencia acierta siempre',
    titulo='16 de 16: Plasencia ha votado al ganador en todas las elecciones generales desde 1977',
    dek='De unos 8.000 municipios, solo 27 han dado su victoria al mismo partido que ganó en España en las 16 generales de la democracia. '
        'Plasencia, con 32.589 electores, es el más grande. Más de la mitad son pueblos de Aragón.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} Y hay una pregunta que se repite en cada campaña: ¿existe en España un pueblo que siempre acierta, como el condado de Estados Unidos que vota siempre al presidente que gana?</p>
<p>Con los resultados de Interior desde 1977, la respuesta es sí, pero son muy pocos. De los <strong>7.870 municipios</strong> con datos en las 16 elecciones generales, solo <strong>27</strong> han votado siempre como primera fuerza al mismo partido que ganó en el conjunto de España: UCD en 1977 y 1979, el PSOE de 1982 a 1993, el PP en 1996 y 2000, el PSOE en 2004 y 2008, el PP de 2011 a 2016, el PSOE en las dos de 2019 y el PP en 2023.</p>
<p>El mayor de ellos es <strong>Plasencia</strong> (Cáceres), con 32.589 electores en 2023. Le siguen Villaquilambre (León), Gines (Sevilla), Jaca (Huesca), Valencina de la Concepción (Sevilla) y Zuera (Zaragoza). El resto son pueblos pequeños; el más pequeño, Sigüés (Zaragoza), tiene 66 electores.</p>
{fig('ohio', 'Plasencia y los demás: el mismo ganador que España, elección tras elección', 'Partido más votado en cada elección general. Primera fila: el ganador en España. Los 12 municipios más grandes de los 27 que nunca han fallado', 'Fuente: Ministerio del Interior. ' + FAMILIAS, [('UCD','UCD'),('PSOE','PSOE'),('PP','AP / PP')])}
<h2>Cada elección deja a muchos por el camino</h2>
<p>Acertar una vez es fácil: en 1977, 5.792 municipios votaron como primera fuerza a UCD, igual que España. Lo difícil es seguir acertando. En 1982, cuando el PSOE ganó por primera vez, ya solo quedaban 2.357 municipios con el pleno. El cambio de 1996 al PP dejó la lista en 334. El de 2004, en 104.</p>
<p>Antes del 23J quedaban 46. En julio de 2023 el PP fue el partido más votado en España, pero en 19 de ellos ganó el PSOE, y se cayeron de la lista. Entre ellos están Ponferrada (León), Coca (Segovia) o Mendavia (Navarra), que ya fueron noticia como «pueblos que siempre aciertan» hasta 2019, como contó Público tras aquellas elecciones.</p>
{fig('superv', 'De 5.792 municipios a 27', 'Municipios que han votado al ganador nacional en todas las elecciones generales hasta cada fecha, desde 1977', 'Fuente: Ministerio del Interior. Solo municipios con dato en las 16 elecciones.')}
<h2>Más de la mitad, en Aragón</h2>
<p>Los 27 no se reparten al azar. <strong>Catorce están en Aragón</strong>: seis en Huesca (entre ellos Jaca, Biescas y Ayerbe), seis en Zaragoza (Zuera, Fuentes de Ebro, Gelsa…) y dos en Teruel. Tres están en León, dos en Zamora, dos en La Rioja y dos en Sevilla. Ninguno está en Cataluña, el País Vasco, Galicia o Canarias, donde los partidos nacionalistas y regionales ganan a menudo en los municipios.</p>
<p>Que un municipio acierte siempre no quiere decir que vote como la media de España. En Plasencia el ganador coincide, pero los porcentajes pueden estar lejos de los nacionales. Lo que muestran estos datos es que el partido más votado ha cambiado allí en los mismos momentos que en el conjunto del país.</p>
<h2>Qué no dicen estos datos</h2>
<p>Que Plasencia haya acertado 16 veces no permite saber quién ganará el 29N. Con 7.870 municipios y 16 elecciones, es normal que unos pocos coincidan siempre por pura acumulación de casualidades: cada vez que hay un cambio de Gobierno, la lista se reduce. Esta pieza no es una predicción. Es una forma de mirar cuántas veces ha cambiado España de partido ganador y cuántos pueblos han cambiado exactamente a la vez.</p>
<p>La noche del 29N, el <a href="https://mapaelectoral.es/">mapa de resultados</a> permitirá ver si Plasencia y los otros 26 siguen en la lista.</p>
""",
    js="""rejilla('ohio',EL,[{l:'España',b:true,g:D.ohio.nacional,t:'Partido más votado en el conjunto de España'}].concat(D.ohio.filas.slice(0,12).map(f=>({l:f[0],g:f[3],t:f[1]+' · '+miles(f[2])+' electores'}))),{aria:'Partido más votado en cada elección general en España y en los municipios que siempre coinciden'});
tabla('ohio',['Municipio','Provincia','Electores 2023'],D.ohio.filas.map(f=>[f[0],f[1],miles(f[2])]));
barras('superv',EL.map((e,i)=>({l:e,v:D.ohio.supervivientes[i],c:'var(--acc)',lab:i==0||i==2||i==6||i==8||i==15,t:`Hasta ${e}: <b>${miles(D.ohio.supervivientes[i])}</b> municipios`})),{ticks:[0,2000,4000,6000],fy:v=>miles(v),fl:v=>miles(v),max:6400,ml:46,aria:'Municipios que han votado siempre al ganador nacional'});
tabla('superv',['Hasta la elección de','Municipios'],EL.map((e,i)=>[e,miles(D.ohio.supervivientes[i])]));""",
    pie=PIE,
    descripcion='Solo 27 de 7.870 municipios con datos completos han votado como primera fuerza al ganador de España en las 16 generales desde 1977. El mayor es Plasencia (32.589 electores); 14 están en Aragón. Antes del 23J eran 46.',
    compara='El partido más votado en cada municipio y en el conjunto de España en las 16 elecciones generales de 1977 a 2023, con todas las listas, también las locales y regionales.',
    limites='Se mira solo quién queda primero, no los porcentajes. Acertar siempre es en buena parte azar acumulado y no sirve para predecir. Los municipios sin dato en alguna elección (segregados después de 1977 o ausentes del fichero de 1982) quedan fuera. Sin voto exterior.',
    fuentes=[INTERIOR_HIST, WIKI_GENERALES,
             ('https://www.publico.es/politica/29-50-ohios-espanoles-sobreviven-23j.html', 'Público, «29 de los 50 “Ohios” españoles sobreviven al 23J» (Emilia G. Morales, 25-7-2023)'),
             CIVIO_29N],
    enlaces=[('como contó Público tras aquellas elecciones', 'https://www.publico.es/politica/29-50-ohios-espanoles-sobreviven-23j.html')],
))

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='municipios-fieles', lugar='España', datos=['fieles'],
    corto='Municipios fieles',
    titulo='Dos Hermanas ha votado al PSOE en las 16 generales; solo 11 pueblos, ninguno grande, lo han hecho con el PP',
    dek='239 municipios han dado la victoria al mismo partido en todas las elecciones generales desde 1977: 190 al PSOE, 28 al PNV, 11 a AP/PP y 10 a CiU/Junts. '
        'Los del PSOE son sobre todo andaluces y extremeños. Los del PP suman menos de 14.000 electores.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} En una campaña se habla mucho de los votos que se mueven. Esta pieza mira lo contrario: los municipios donde, pase lo que pase en España, siempre gana el mismo.</p>
<p>De los 7.870 municipios con datos en las 16 generales, <strong>239 han tenido siempre el mismo ganador</strong>. Han atravesado la Transición, las mayorías absolutas de Felipe González y de Aznar, la crisis de 2008, la llegada de Podemos, Ciudadanos y Vox, y nunca han cambiado de partido más votado.</p>
{fig('fam', '190 del PSOE, 28 del PNV, 11 del PP y 10 de CiU/Junts', 'Municipios con el mismo partido más votado en las 16 elecciones generales de 1977 a 2023', 'Fuente: Ministerio del Interior. ' + FAMILIAS)}
<h2>Los fieles del PSOE: Sevilla, Jaén y Badajoz</h2>
<p>El PSOE se lleva casi ocho de cada diez. Y entre ellos están los únicos municipios grandes de la lista. <strong>Dos Hermanas</strong> (Sevilla), con 107.888 electores, ha votado al PSOE como primera fuerza en las 16 elecciones. También Alcalá de Guadaíra, Utrera, La Rinconada, Coria del Río, Carmona o Camas, en Sevilla; Arcos de la Frontera, en Cádiz, y Martos, en Jaén.</p>
<p>Por provincias, Sevilla tiene 30 municipios fieles al PSOE; Jaén, 24; Badajoz, 21; Granada, 17; Málaga, 15; Córdoba, 13, y Huelva y Cáceres, 10 cada una.</p>
{fig('top', 'Los 15 municipios fieles más grandes', 'Electores en 2023 de los municipios que siempre han votado al mismo partido en las generales', 'Fuente: Ministerio del Interior.', [('PSOE','PSOE'),('PNV','PNV')])}
<h2>Los del PNV y CiU</h2>
<p>El PNV ha ganado en las 16 generales en 28 municipios vascos, sobre todo de Bizkaia: los mayores son Mungia, Bermeo y Gernika-Lumo. CiU y luego Junts lo han hecho en 10 municipios catalanes.</p>
<h2>Los del PP: once pueblos, uno grande</h2>
<p>En el otro lado, solo <strong>11 municipios</strong> han votado siempre a AP y después al PP. Y son casi todos diminutos: el mayor es <strong>Vilalba</strong> (Lugo), con 11.676 electores. Le siguen Riotorto (Lugo), con 1.066, e Igea (La Rioja), con 424. Entre los demás hay pueblos de La Rioja, Ourense, Zamora, Guadalajara, Zaragoza, Teruel y Palencia, y uno, Villarroya (La Rioja), tiene siete electores. Juntos, los 11 suman menos de 14.000.</p>
<p>Parte de la diferencia es de método. En 1977 y 1979, cuando AP era un partido pequeño, la derecha ganaba con UCD en la mayor parte de la España rural. Un municipio que votó a UCD en 1977 y al PP después no cuenta como fiel, porque UCD y el PP son partidos distintos. Para estar en la lista del PP, un pueblo tenía que preferir AP a UCD ya en 1977, y eso pasó en muy pocos.</p>
<h2>Qué no dicen estos datos</h2>
<p>Ganar siempre no quiere decir ganar por lo mismo. En Dos Hermanas el PSOE ha pasado por mayorías muy amplias y por victorias ajustadas. Esta pieza solo mira quién ha quedado primero; los porcentajes de cada elección se pueden consultar en el <a href="https://mapaelectoral.es/">mapa de resultados</a>.</p>
""",
    js="""const F=D.fieles.por_familia;const ORD=['PSOE','PNV','PP','JUNTS'];
hbarras('fam',ORD.map(k=>({l:NOM[k],v:F[k],c:COL[k],b:true,t:`${NOM[k]}: <b>${F[k]}</b> municipios`})),{ticks:[0,50,100,150,200],fy:v=>v,fl:v=>v,max:200,ml:210,rh:30,aria:'Municipios fieles por partido'});
tabla('fam',['Partido','Municipios'],ORD.map(k=>[NOM[k],F[k]]));
hbarras('top',D.fieles.top.map(f=>({l:f[0],v:f[2],c:COL[f[3]],t:`<b>${f[0]}</b> (${f[1]})<br>${miles(f[2])} electores · siempre ${NOM[f[3]]}`})),{ticks:[0,50000,100000],fy:v=>miles(v),fl:v=>miles(v),max:115000,ml:180,aria:'Municipios fieles más grandes'});
tabla('top',['Municipio','Provincia','Electores 2023','Siempre gana'],D.fieles.top.map(f=>[f[0],f[1],miles(f[2]),NOM[f[3]]]).concat(D.fieles.pp.map(f=>[f[0],f[1],miles(f[2]),NOM.PP])));""",
    pie=PIE,
    descripcion='239 municipios han tenido el mismo ganador en las 16 generales desde 1977: 190 el PSOE (Dos Hermanas, 107.888 electores, es el mayor), 28 el PNV, 11 AP/PP y 10 CiU/Junts. El mayor del PP es Vilalba (11.676).',
    compara='El partido más votado en cada municipio en las 16 elecciones generales de 1977 a 2023, con todas las listas, también las locales y regionales.',
    limites='Se mira solo quién queda primero, no por cuánto. UCD y AP/PP se cuentan como partidos distintos; CiU y Junts, como el mismo espacio. Los municipios sin dato en alguna elección quedan fuera. Sin voto exterior.',
    fuentes=[INTERIOR_HIST, CIVIO_29N],
    enlaces=[],
))

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='ucd-ciudadanos-hundimiento', lugar='España', datos=['hundimiento'],
    corto='UCD y Ciudadanos',
    titulo='De 5.990 municipios a 762 en tres años: así se hundió UCD, y así cayó Ciudadanos en solo seis meses',
    dek='UCD ganó las generales de 1979 con el 35 % y fue la primera fuerza en 5.990 municipios. En 1982 se quedó en el 6,7 % y en 762. '
        'Ciudadanos pasó del 16 % y 115 municipios en abril de 2019 al 6,9 % y 5 en noviembre. Son los dos mayores hundimientos de la democracia.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} En 46 años, dos partidos que llegaron a ser decisivos se hundieron en una sola elección: la Unión de Centro Democrático de Adolfo Suárez, en 1982, y Ciudadanos, en noviembre de 2019.</p>
<h2>UCD: del Gobierno al 6,7 %</h2>
<p>UCD ganó las dos primeras generales. En 1977 sacó el 34,4 % de los votos (sin contar el voto exterior) y fue la lista más votada en <strong>5.792 municipios</strong>. En 1979 subió al 35,0 % y a <strong>5.990 municipios</strong>, tres de cada cuatro de España.</p>
<p>Tres años después, en octubre de 1982, se quedó en el <strong>6,7 %</strong> y 11 diputados, y solo ganó en <strong>762 municipios</strong>. El PSOE pasó a ser la primera fuerza en 4.055 y AP, en 2.206. Los dirigentes de UCD acordaron disolver el partido el 18 de febrero de 1983.</p>
{fig('serie', 'Las dos caídas, en la misma escala', 'Porcentaje de voto en las elecciones generales, sin voto exterior', 'Fuente: Ministerio del Interior. ' + FAMILIAS, [('UCD','UCD'),('CDS','CDS'),('CS','Ciudadanos'),('PSOE','PSOE'),('PP','AP / PP'),('VOX','Vox')])}
<p>Parte de la UCD acabó en el CDS, el partido que Suárez fundó en julio de 1982: sacó el 2,9 % aquel año y el 9,3 % en 1986, antes de desaparecer del Congreso en 1993.</p>
<h2>Ciudadanos: de 57 diputados a 10</h2>
<p>Ciudadanos llegó al Congreso en 2015 con el 14,0 % y fue la primera fuerza en 21 municipios. En abril de 2019 alcanzó su máximo: el <strong>16,0 %</strong>, 57 diputados y <strong>115 municipios</strong> ganados. Siete meses después, en la repetición electoral de noviembre, bajó al <strong>6,9 %</strong>, 10 diputados y <strong>5 municipios</strong>. En 2023 no se presentó a las generales.</p>
{fig('mun', 'Municipios donde fue la lista más votada', 'UCD (1977-1986) y Ciudadanos (2015-2023), en las elecciones generales', 'Fuente: Ministerio del Interior. Se cuentan todas las listas.')}
<h2>Dos caídas distintas</h2>
<p>Las dos caídas se parecen en el resultado, pero no en el punto de partida. UCD era el partido del Gobierno y el más votado de España; su derrumbe dio la mayoría absoluta al PSOE. Ciudadanos nunca ganó unas generales: su caída coincidió con el crecimiento de Vox, que pasó del 10,3 % al 15,2 % en esos mismos siete meses, y con la subida del PP del 17,2 % al 21,4 %.</p>
<p>Con datos de resultados no se puede saber a dónde fueron los votantes de UCD o de Ciudadanos: un municipio donde un partido cae y otro sube no demuestra que sean las mismas personas. Para eso hacen falta encuestas postelectorales, como las del CIS.</p>
""",
    js="""const S=D.hundimiento.serie;
lineas('serie',EL,[{n:'UCD',c:COL.UCD,v:S.UCD.map((v,i)=>i<=2?v:null),w:3.5},{n:'CDS',c:COL.CDS,v:S.CDS.map((v,i)=>i>=2&&i<=5?v:null)},{n:'Cs',c:COL.CS,v:S.CS.map((v,i)=>i>=11&&i<=14?v:null),w:3.5},{n:'PSOE',c:COL.PSOE,v:S.PSOE,w:1.6},{n:'AP/PP',c:COL.PP,v:S.PP,w:1.6,dy:-4},{n:'Vox',c:COL.VOX,v:S.VOX.map((v,i)=>i>=13?v:null),w:1.6}],{max:50,ticks:[0,10,20,30,40,50],aria:'Voto a UCD, CDS, Ciudadanos, PSOE, PP y Vox en las generales'});
tabla('serie',['Elección','UCD','CDS','Cs','PSOE','AP/PP','Vox'],EL.map((e,i)=>[e,pct(S.UCD[i]),pct(S.CDS[i]),pct(S.CS[i]),pct(S.PSOE[i]),pct(S.PP[i]),pct(S.VOX[i])]));
const G=D.hundimiento.ganados;const MU=[['1977_06','1977','UCD'],['1979_03','1979','UCD'],['1982_10','1982','UCD'],['1986_06','1986','UCD'],['2015_12','2015','CS'],['2016_06','2016','CS'],['2019_04','2019-A','CS'],['2019_11','2019-N','CS'],['2023_07','2023','CS']];
barras('mun',MU.map(m=>({l:m[1],v:G[m[0]][m[2]]||0,c:COL[m[2]],lab:true,t:`${NOM[m[2]]}, ${m[1]}: <b>${miles(G[m[0]][m[2]]||0)}</b> municipios`})),{ticks:[0,2000,4000,6000],fy:v=>miles(v),fl:v=>miles(v),max:6600,ml:46,aria:'Municipios ganados por UCD y Ciudadanos'});
tabla('mun',['Elección','Partido','Municipios ganados'],MU.map(m=>[m[1],NOM[m[2]],miles(G[m[0]][m[2]]||0)]));""",
    pie=PIE,
    descripcion='UCD fue la lista más votada en 5.990 municipios en 1979 y en 762 en 1982, cuando cayó del 35,0 % al 6,7 %. Ciudadanos pasó de 115 municipios y el 16,0 % en abril de 2019 a 5 y el 6,9 % en noviembre.',
    compara='El voto a UCD, CDS y Ciudadanos en las elecciones generales de 1977 a 2023 y el número de municipios donde cada uno fue la lista más votada.',
    limites='Los datos de resultados no dicen a qué partido fueron los votantes de UCD o de Ciudadanos. Porcentajes sobre votos a candidaturas y sin voto exterior, por eso difieren unas décimas de los oficiales (UCD, 34,8 % oficial en 1979; Cs, 15,9 % en abril de 2019).',
    fuentes=[INTERIOR_HIST,
             ('https://es.wikipedia.org/wiki/Uni%C3%B3n_de_Centro_Democr%C3%A1tico', 'Wikipedia, «Unión de Centro Democrático»: escaños y disolución (18-2-1983) (consultada el 8-10-2026)'),
             ('https://es.wikipedia.org/wiki/Centro_Democr%C3%A1tico_y_Social', 'Wikipedia, «Centro Democrático y Social»: fundación (29-7-1982) y resultados (consultada el 8-10-2026)'),
             ('https://es.wikipedia.org/wiki/Ciudadanos_(partido_pol%C3%ADtico)', 'Wikipedia, «Ciudadanos (partido político)»: no se presentó a las generales de 2023 (consultada el 8-10-2026)'),
             WIKI_GENERALES],
    enlaces=[],
))

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='mapa-derecha-1977-2023', lugar='España', datos=['derecha'],
    foto=dict(src='img/actualidad/fotos/mapa-derecha-1977-2023.jpg', ancho=1280, alto=720, ia=True, pie='Santiago Abascal y Vox.', origen='vox-abascal.jpg'),
    corto='El mapa de la derecha',
    titulo='Donde se votaba a UCD y AP en 1977 se vota a PP y Vox en 2023; el mapa de Vox no se parece al de AP',
    dek='Municipio a municipio, el voto a UCD y AP en 1977 y el voto a PP y Vox en 2023 dibujan mapas muy parecidos: la correlación es de 0,59. '
        'Pero el voto a Vox en 2023 no sigue al de AP en 1977: la correlación es prácticamente cero.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} Una idea vuelve en cada campaña: que el voto a Vox es el heredero del de la antigua Alianza Popular de Manuel Fraga. Con los resultados por municipio de 1977 y de 2023 se puede comprobar al menos una parte: si Vox es fuerte hoy donde AP lo era entonces.</p>
<p>La respuesta corta es no. Pero el mapa del conjunto de la derecha sí ha cambiado muy poco en 46 años.</p>
<h2>El bloque de la derecha, casi en los mismos sitios</h2>
<p>En los 1.029 municipios con más de 5.000 electores, el porcentaje de voto a UCD más AP en 1977 y el de PP más Vox en 2023 tienen una <strong>correlación de 0,59</strong> (1 sería un mapa idéntico; 0, ninguna relación). Con todos los municipios, o ponderando por electores, sale entre 0,57 y 0,67. Donde más se votaba al centro y la derecha en las primeras elecciones de la democracia, más se vota a la derecha hoy.</p>
{fig('bloque', 'La derecha de 1977 y la de 2023, municipio a municipio', 'Cada punto es un municipio de más de 5.000 electores. Voto a UCD + AP en 1977 (horizontal) y a PP + Vox en 2023 (vertical)', 'Fuente: Ministerio del Interior. Porcentajes sobre votos a candidaturas, sin voto exterior.', tabla=False)}
<p>Hay excepciones. En el País Vasco y en buena parte de Cataluña, UCD sacó en 1977 resultados que hoy no tienen ni PP ni Vox: Vitoria dio a UCD y AP el 35,8 % y en 2023 dio a PP y Vox el 24,1 %. En el sentido contrario están muchos municipios de la costa mediterránea y de Madrid, que han crecido mucho desde entonces y votan hoy más a la derecha que en 1977.</p>
<h2>Vox no está donde estaba AP</h2>
<p>Si se separan los partidos, la imagen cambia. AP sacó el 8,1 % en 1977. Entre los mismos municipios, la correlación entre el voto a AP en 1977 y el voto a Vox en 2023 es de <strong>0,03</strong>: en la práctica, ninguna. Los municipios donde AP era fuerte no son, en general, los que más votan a Vox.</p>
{fig('apvox', 'AP en 1977 y Vox en 2023: sin relación', 'Cada punto es un municipio de más de 5.000 electores. Voto a AP en 1977 (horizontal) y a Vox en 2023 (vertical)', 'Fuente: Ministerio del Interior.', tabla=False)}
<h2>Qué no dicen estos datos</h2>
<p>Una correlación entre mapas no dice nada de las personas. Entre 1977 y 2023 han muerto la mayoría de los votantes de entonces y han llegado otros, y muchos municipios han multiplicado su población. Que la derecha siga fuerte en los mismos sitios es un patrón geográfico, no la prueba de que sean los mismos votantes ni las mismas familias. Tampoco que el mapa de Vox no se parezca al de AP prueba nada sobre de dónde vienen sus votantes: eso solo lo pueden decir las encuestas.</p>
""",
    js="""const PT=D.derecha.puntos;
dispersion('bloque',PT.map(p=>[p[0],p[1],p[4],p[5]]),{max:90,ticks:[0,20,40,60,80],c:COL.PP,xl:'UCD + AP en 1977',yl:'PP + Vox en 2023',xn:'UCD + AP 1977',yn:'PP + Vox 2023',aria:'Dispersión del voto a la derecha en 1977 y 2023 por municipio'});
dispersion('apvox',PT.map(p=>[p[2],p[3],p[4],p[5]]),{max:40,ticks:[0,10,20,30,40],c:COL.VOX,xl:'AP en 1977',yl:'Vox en 2023',xn:'AP 1977',yn:'Vox 2023',aria:'Dispersión del voto a AP en 1977 y a Vox en 2023 por municipio'});""",
    pie=PIE,
    descripcion='En los municipios de más de 5.000 electores, el voto a UCD + AP en 1977 y a PP + Vox en 2023 tiene una correlación de 0,59. La de AP en 1977 con Vox en 2023 es de 0,03.',
    compara='El porcentaje de voto a UCD y AP en las generales de 1977 y a PP y Vox en las de 2023, en los 1.029 municipios con más de 5.000 electores en 2023.',
    limites='Es una comparación de mapas, no de personas: no dice que los votantes sean los mismos. La correlación cambia algo según qué municipios se incluyan o cómo se ponderen (entre 0,57 y 0,67 para el bloque). Los municipios segregados después de 1977 se comparan con el de origen o quedan fuera. Sin voto exterior.',
    fuentes=[INTERIOR_HIST, CIVIO_29N],
    enlaces=[],
))

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='pueblos-menos-votantes-que-en-1977', lugar='España', datos=['censo_pueblos'],
    corto='Menos votantes que en 1977',
    titulo='6 de cada 10 municipios tienen menos electores que en 1977; Las Rozas tiene 14 veces más',
    dek='De 6.457 municipios comparables, 4.157 votarán el 29N con menos electores que en las primeras elecciones de la democracia. Juntos han perdido 1,3 millones. '
        'En Zamora y Teruel pasa en más del 94 % de los pueblos; en Navia de Suarna (Lugo) quedan menos de un tercio.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} El censo electoral de España ha crecido un 49 % desde 1977. Pero ese crecimiento se ha concentrado en las ciudades, sus coronas y la costa. En la mayoría de los municipios el censo es hoy más pequeño que en las primeras elecciones.</p>
<p>De los 6.457 municipios que se pueden comparar, <strong>4.157 (el 64 %) tenían menos electores en 2023 que en 1977</strong>. Juntos han perdido <strong>1,3 millones</strong> de electores, y eso pese a que en 1977 se votaba a partir de los 21 años y hoy desde los 18.</p>
{fig('prov', 'En Zamora, casi todos los pueblos', 'Porcentaje de municipios de cada provincia con menos electores en 2023 que en 1977', 'Fuente: Ministerio del Interior, censo de cada elección general. Se excluyen los municipios con saltos de censo de más del 25 % entre dos elecciones, que suelen ser segregaciones o fusiones.')}
<h2>Galicia interior y la España vaciada</h2>
<p>Por provincias, la proporción es mayor en <strong>Zamora (95,7 %), Teruel (94,8 %), Palencia (93,5 %), Soria (92,6 %) y Guadalajara (92,4 %)</strong>. En el otro extremo están Baleares (3,6 %), Madrid (4,5 %), Cádiz (10,8 %), Murcia y Santa Cruz de Tenerife; en Las Palmas, Ceuta y Melilla no ha perdido electores ningún municipio.</p>
<p>Las mayores caídas, entre los municipios que tenían al menos 3.000 electores en 1977, están en el interior de Lugo y Ourense. <strong>Navia de Suarna</strong> (Lugo) ha pasado de 3.233 a 930 electores. Rubiá, Riós, Cartelle y Bande, en Ourense, o Sober, A Fonsagrada, Carballedo y Pantón, en Lugo, han perdido más de la mitad. Fuera de Galicia, Algarinejo (Granada), de 4.599 a 1.985.</p>
{fig('caidas', 'Los que más han perdido', 'Electores en 1977 y en 2023 en los municipios con más de 3.000 electores en 1977 que más han perdido', 'Fuente: Ministerio del Interior.', [('#9a9a9a','1977'),('var(--acc)','2023')])}
<h2>Las Rozas, 14 veces más</h2>
<p>En el otro extremo, <strong>Las Rozas de Madrid</strong> tenía 4.878 electores en 1977 y 70.249 en 2023: 14 veces más, con un crecimiento continuo elección tras elección. Valdemoro se ha multiplicado por 12; Rincón de la Victoria, por 9, y Mijas, Majadahonda, Benalmádena y Alhaurín de la Torre, casi por 8.</p>
<h2>Una advertencia sobre el censo de los años setenta</h2>
<p>Los censos de las primeras elecciones tenían errores, y en algunas provincias, sobre todo de Galicia, incluían a muchas personas que vivían fuera. Parte de la caída de los pueblos de Ourense y Lugo puede deberse a la limpieza de esos censos y no solo a la pérdida de población. Por eso estas cifras hablan de electores, no de habitantes.</p>
""",
    js="""const C=D.censo_pueblos;
const PR=C.por_provincia.filter(p=>!['Ceuta','Melilla'].includes(p[0]));
hbarras('prov',PR.map(p=>({l:p[0],v:p[1],c:p[1]>=50?'var(--acc)':'#9a9a9a',t:`${p[0]}: <b>${pct(p[1])}</b> de sus municipios`})),{ticks:[0,25,50,75,100],max:100,rh:17,ml:150,fl:v=>num(v,0),aria:'Porcentaje de municipios con menos electores que en 1977, por provincia'});
tabla('prov',['Provincia','% de municipios con menos electores'],C.por_provincia.map(p=>[p[0],pct(p[1])]));
const CA=C.caidas;
(function(){const [box,W,tip]=caja('caidas');const rh=26,m={l:W<500?120:150,r:60,t:4,b:22},H=m.t+m.b+rh*CA.length,max=7200,x=v=>m.l+v/max*(W-m.l-m.r);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Electores en 1977 y 2023'},box);
 [0,2000,4000,6000].forEach(v=>{el('line',{x1:x(v),x2:x(v),y1:m.t,y2:H-m.b,stroke:'var(--grid)'},svg);txt(svg,{x:x(v),y:H-5,'text-anchor':'middle'},miles(v))});
 CA.forEach((c,i)=>{const cy=m.t+i*rh+rh/2;txt(svg,{x:m.l-8,y:cy+4,'text-anchor':'end','font-size':12.5},recorta(c[0],W));
  el('line',{x1:x(c[3]),x2:x(c[2]),y1:cy,y2:cy,stroke:'#9a9a9a','stroke-width':2},svg);
  el('circle',{cx:x(c[2]),cy,r:5.5,fill:'#9a9a9a'},svg);el('circle',{cx:x(c[3]),cy,r:5.5,fill:'var(--acc)'},svg);
  txt(svg,{x:x(c[2])+9,y:cy+4,'font-size':12},'−'+num(100*(1-c[3]/c[2]),0)+'%');
  const h=el('rect',{x:0,y:cy-rh/2,width:W,height:rh,fill:'transparent'},svg);hover(h,box,tip,`<b>${c[0]}</b> (${c[1]})<br>1977: ${miles(c[2])} · 2023: ${miles(c[3])}`)});})();
tabla('caidas',['Municipio','Provincia','Electores 1977','Electores 2023'],CA.concat(C.subidas).map(c=>[c[0],c[1],miles(c[2]),miles(c[3])]));""",
    pie=PIE,
    descripcion='4.157 de 6.457 municipios comparables (el 64 %) tienen menos electores que en 1977 y han perdido 1,3 millones. En Zamora le pasa al 95,7 % de los pueblos. Las Rozas ha pasado de 4.878 a 70.249.',
    compara='El censo electoral de cada municipio en las generales de 1977 y de 2023, sin contar el censo de residentes en el extranjero.',
    limites='Se excluyen los municipios con saltos de censo de más del 25 % entre dos elecciones, que suelen ser segregaciones o fusiones (por ejemplo, Dalías y El Ejido); con ellos la proporción es parecida (62 %). Los censos de los años setenta tenían errores e incluían en algunas provincias a residentes en el extranjero. En 1977 se votaba desde los 21 años.',
    fuentes=[INTERIOR_HIST, CIVIO_29N],
    enlaces=[],
))

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='avila-suarez-cds', lugar='Ávila', datos=['cds'],
    corto='Ávila y el CDS',
    titulo='Ávila dio a Suárez el 46 % en 1986, cuando su partido sacaba el 9 % en España',
    dek='El CDS, el partido que Adolfo Suárez fundó tras dejar UCD, tuvo en Ávila un resultado que no se repitió en ninguna otra provincia: el 41,6 % en 1986 y el 46,0 % en la capital. '
        'La segunda provincia, Segovia, se quedó en el 23,8 %.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} Una de las preguntas de cada campaña es cuánto pesa un candidato concreto en el voto de su tierra. La historia electoral tiene un caso extremo: Adolfo Suárez y su provincia, Ávila.</p>
<p>Suárez, nacido en Cebreros (Ávila), dejó UCD y fundó el Centro Democrático y Social (CDS) el 29 de julio de 1982, pocos meses antes de las generales de octubre. Aquel año el CDS sacó el <strong>2,9 %</strong> en España y dos diputados. En 1986 llegó a su mejor resultado: el <strong>9,3 %</strong> y 19 diputados. En 1989 bajó al 8,0 % y en 1993, al 1,8 %, sin escaños.</p>
<h2>Ávila, muy por encima de todas</h2>
<p>En la provincia de Ávila, el CDS sacó el <strong>22,4 %</strong> en 1982, casi ocho veces su media española. En 1986 llegó al <strong>41,6 %</strong>, y en la ciudad de Ávila al <strong>46,0 %</strong>, cinco veces su resultado en el conjunto de España.</p>
{fig('prov', 'Ningún otro sitio se acercó a Ávila', 'Voto al CDS en las generales de 1986 por provincia, las 12 primeras', 'Fuente: Ministerio del Interior. Porcentajes sobre votos a candidaturas, sin voto exterior.', [('CDS','CDS')])}
<p>Detrás de Ávila, el CDS superó el 20 % solo en Segovia (23,8 %) y en Las Palmas (21,1 %). En Salamanca, Valladolid y Zamora, también en Castilla y León, sacó entre el 15 % y el 19 %. En Madrid, el 14,1 %.</p>
{fig('serie', 'El CDS en Ávila y en España', 'Voto al CDS en las generales de 1982 a 1993', 'Fuente: Ministerio del Interior.', [('CDS','Ciudad de Ávila'),('#b39ddb','Provincia de Ávila'),('#9a9a9a','España')])}
<h2>Una sola victoria</h2>
<p>Pese a ese 46,0 %, el CDS solo fue la lista más votada en la ciudad de Ávila una vez, en 1986. En 1977 y 1979 ganó UCD, en 1982 AP y desde 1989 el PP, sin interrupción. Ávila es uno de los 1.932 municipios donde el PSOE nunca ha sido la lista más votada en unas generales.</p>
<h2>Qué no dicen estos datos</h2>
<p>Que el CDS sacara en Ávila cinco veces su media es un dato. Atribuirlo solo a que Suárez era de la provincia sería una explicación que los resultados por sí solos no prueban: también pueden influir la implantación del partido, sus candidatos locales o la herencia de UCD, que en 1979 había sacado en la provincia de Ávila el 66,1 %, su mejor resultado de España.</p>
""",
    js="""const C=D.cds;
hbarras('prov',C.prov86.map(p=>({l:p[0],v:p[1],c:COL.CDS,b:p[0]=='Ávila',t:`${p[0]}: <b>${pct(p[1])}</b>`})),{ticks:[0,10,20,30,40],max:45,ml:130,aria:'Voto al CDS por provincia en 1986'});
tabla('prov',['Provincia','CDS 1986'],C.prov86.map(p=>[p[0],pct(p[1])]));
const L=['1982','1986','1989','1993'];
lineas('serie',L,[{n:'Ávila ciudad',c:COL.CDS,v:C.avila_ciudad,w:3.5},{n:'Ávila prov.',c:'#b39ddb',v:C.avila_prov,dy:12},{n:'España',c:'#9a9a9a',v:C.nac}],{max:50,ticks:[0,10,20,30,40,50],aria:'Voto al CDS en Ávila y en España'});
tabla('serie',['Elección','Ciudad de Ávila','Provincia de Ávila','España'],L.map((e,i)=>[e,pct(C.avila_ciudad[i]),pct(C.avila_prov[i]),pct(C.nac[i])]));""",
    pie=PIE,
    descripcion='El CDS de Adolfo Suárez sacó en 1986 el 9,3 % en España, el 41,6 % en la provincia de Ávila y el 46,0 % en la capital. La segunda provincia fue Segovia, con el 23,8 %.',
    compara='El voto al CDS en las elecciones generales de 1982 a 1993 en España, por provincia y en la ciudad de Ávila.',
    limites='Los resultados no permiten saber cuánto pesó el origen abulense de Suárez frente a otros factores. Porcentajes sobre votos a candidaturas y sin voto exterior; los oficiales del CDS son 2,87 %, 9,22 %, 7,89 % y 1,76 %.',
    fuentes=[INTERIOR_HIST,
             ('https://es.wikipedia.org/wiki/Centro_Democr%C3%A1tico_y_Social', 'Wikipedia, «Centro Democrático y Social»: fundación (29-7-1982) y resultados oficiales (consultada el 8-10-2026)'),
             ('https://es.wikipedia.org/wiki/Adolfo_Su%C3%A1rez', 'Wikipedia, «Adolfo Suárez» (consultada el 8-10-2026)')],
    enlaces=[],
))

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='trebujena-pce-sumar', lugar='Trebujena (Cádiz)', datos=['trebujena'],
    corto='Trebujena',
    titulo='Trebujena dio al PCE dos de cada tres votos en 1977 y aún da a Sumar uno de cada dos',
    dek='En las primeras elecciones de la democracia, el PCE sacó el 67,5 % en Trebujena (Cádiz), su mejor resultado de España. Desde entonces, la izquierda a la izquierda del PSOE '
        'ha sido primera allí en todas las generales con dato menos una. En 2023, Sumar sacó el 49,3 %, cuatro veces su media.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} Sumar, Podemos, Izquierda Unida y antes el Partido Comunista han cambiado de nombre, de líderes y de socios muchas veces. Hay un municipio donde ese espacio político ha ganado casi siempre: Trebujena, en la provincia de Cádiz, junto a las marismas del Guadalquivir.</p>
<p>En junio de 1977, el PCE sacó en Trebujena el <strong>67,5 %</strong> de los votos, su mejor resultado entre los municipios de más de 2.000 electores. En el conjunto de España sacó el 9,4 %. El PSOE se quedó allí en el 11,8 %.</p>
<h2>Casi medio siglo por encima del 40 %</h2>
<p>Desde entonces, la familia política del PCE, de IU, de Podemos y de Sumar no ha bajado del <strong>41 %</strong> en Trebujena en ninguna elección general. Ha sido la lista más votada en todas las elecciones con dato menos en 2008, cuando el PSOE la igualó en el 41,4 %. En 2015, con Podemos, volvió al 61,8 %. En julio de 2023, Sumar sacó el <strong>49,3 %</strong>, cuatro veces su 12,4 % nacional.</p>
{fig('serie', 'Trebujena, a la izquierda del PSOE desde 1977', 'Voto en Trebujena a PCE / IU / Podemos / Sumar y al PSOE en las generales, y voto a la misma familia en España', 'Fuente: Ministerio del Interior. No hay dato de 1982: el fichero oficial por municipio de ese año no incluye Trebujena. Sin voto exterior.', [('SUMAR','PCE / IU / Podemos / Sumar en Trebujena'),('PSOE','PSOE en Trebujena'),('#c98aa8','PCE / IU / Podemos / Sumar en España')])}
<h2>El resto de bastiones del PCE de 1977</h2>
<p>Trebujena no es el único municipio donde el PCE arrasó en 1977, pero sí el que mejor lo ha mantenido. De los diez municipios de más de 2.000 electores donde el PCE sacó más voto en 1977, casi todos andaluces, Trebujena es el único donde Sumar se acercó al 50 % en 2023. En Montalbán de Córdoba bajó del 60,5 % al 40,0 %. En Aguilar de la Frontera, del 48,3 % al 14,5 %, y en Madrigueras (Albacete), del 51,9 % al 18,0 %.</p>
{fig('top', 'Los bastiones del PCE en 1977 y Sumar en 2023', 'Los diez municipios de más de 2.000 electores con más voto al PCE en 1977', 'Fuente: Ministerio del Interior.', [('#c98aa8','PCE 1977'),('SUMAR','Sumar 2023')])}
<p>En el conjunto de España, el mapa del PCE de 1977 y el de Sumar en 2023 se parecen algo, pero no mucho: entre los municipios de más de 1.000 electores, la correlación es de 0,40.</p>
<h2>Qué no dicen estos datos</h2>
<p>Los resultados muestran la continuidad, no sus causas. Explicar por qué Trebujena ha votado así durante casi medio siglo exigiría fuentes locales (historia del movimiento jornalero, del sindicalismo agrario o de los gobiernos municipales), y esta pieza no las aporta.</p>
""",
    js="""const T=D.trebujena;
lineas('serie',EL,[{n:'Trebujena',c:COL.SUMAR,v:T.sumar,w:3.5},{n:'PSOE',c:COL.PSOE,v:T.psoe},{n:'España',c:'#c98aa8',v:T.nac_sumar,dash:'5 4'}],{max:70,ticks:[0,10,20,30,40,50,60,70],aria:'Voto en Trebujena a la izquierda del PSOE y al PSOE'});
tabla('serie',['Elección','PCE/IU/Podemos/Sumar Trebujena','PSOE Trebujena','PCE/IU/Podemos/Sumar España'],EL.map((e,i)=>[e,pct(T.sumar[i]),pct(T.psoe[i]),pct(T.nac_sumar[i])]));
(function(){const [box,W,tip]=caja('top');const rh=28,m={l:W<500?136:170,r:16,t:4,b:22},H=m.t+m.b+rh*T.top77.length,x=v=>m.l+v/75*(W-m.l-m.r);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Voto al PCE en 1977 y a Sumar en 2023'},box);
 [0,25,50,75].forEach(v=>{el('line',{x1:x(v),x2:x(v),y1:m.t,y2:H-m.b,stroke:'var(--grid)'},svg);txt(svg,{x:x(v),y:H-5,'text-anchor':'middle'},v+'%')});
 T.top77.forEach((c,i)=>{const cy=m.t+i*rh+rh/2;txt(svg,{x:m.l-8,y:cy+4,'text-anchor':'end','font-size':12.5,class:i==0?'lab':''},recorta(c[0],W));
  el('line',{x1:x(c[3]),x2:x(c[2]),y1:cy,y2:cy,stroke:'#c98aa8','stroke-width':2},svg);
  el('circle',{cx:x(c[2]),cy,r:5.5,fill:'#c98aa8'},svg);el('circle',{cx:x(c[3]),cy,r:5.5,fill:COL.SUMAR},svg);
  const h=el('rect',{x:0,y:cy-rh/2,width:W,height:rh,fill:'transparent'},svg);hover(h,box,tip,`<b>${c[0]}</b> (${c[1]})<br>PCE 1977: ${pct(c[2])} · Sumar 2023: ${pct(c[3])}`)});})();
tabla('top',['Municipio','Provincia','PCE 1977','Sumar 2023'],T.top77.map(c=>[c[0],c[1],pct(c[2]),pct(c[3])]));""",
    pie=PIE,
    descripcion='El PCE sacó el 67,5 % en Trebujena (Cádiz) en 1977, su mejor resultado. Su familia política no ha bajado del 41 % allí desde entonces y en 2023 Sumar sacó el 49,3 %, cuatro veces su media.',
    compara='El voto en Trebujena a la familia PCE / IU / Podemos / Sumar y al PSOE en las generales de 1977 a 2023, y el de los diez municipios de más de 2.000 electores con más voto al PCE en 1977.',
    limites='El fichero oficial de 1982 por municipio no incluye Trebujena, así que falta esa elección. La familia de partidos cambia de composición (PCE, IU, Podemos, Sumar). Los datos no explican por qué Trebujena vota así. Sin voto exterior.',
    fuentes=[INTERIOR_HIST, CIVIO_29N],
    enlaces=[],
))

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='psoe-1982-mas-del-60', lugar='España', datos=['psoe60'],
    corto='El PSOE de 1982',
    titulo='En 1982 el PSOE pasaba del 60 % en al menos 748 municipios; en 2023, en 67',
    dek='El 28 de octubre de 1982 el PSOE sacó el 48,2 % y su mayor victoria. Superó el 60 % en al menos 748 municipios. En julio de 2023 lo hizo en 67. '
        'En ciudades como Estepona, Chiclana o La Línea, ha pasado de más del 68 % a alrededor del 30 %.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} El PSOE llega al 29N con el 32,0 % que sacó en julio de 2023 (sin voto exterior). Es mucho más que en 2015 o 2016, pero lejos del techo que marcó hace 44 años.</p>
<p>En octubre de 1982, el PSOE de Felipe González sacó el <strong>48,2 %</strong> de los votos a candidaturas y 202 diputados, la mayor victoria de la democracia. En <strong>748 municipios</strong> superó el 60 %. La cifra real es algo mayor: el fichero oficial de 1982 no incluye unos 139 municipios que entonces ya existían.</p>
{fig('n60', 'Municipios donde el PSOE superó el 60 %', 'En cada elección general, de 1977 a 2023', 'Fuente: Ministerio del Interior. En 1982 faltan unos 139 municipios en el fichero oficial. Porcentajes sobre votos a candidaturas, sin voto exterior.')}
<h2>Seis elecciones por encima de 600 municipios</h2>
<p>El PSOE se mantuvo por encima de 600 municipios con más del 60 % en 1986 (718), 1989 (784, su máximo) y 1993 (659). Bajó con la victoria del PP de 1996 (494) y de 2000 (266) y volvió a subir con Zapatero en 2004 (606) y 2008 (650). Desde 2011 no ha pasado de 108: 95 en 2011, 43 en 2016, 108 en noviembre de 2019 y <strong>67 en 2023</strong>.</p>
<h2>Las ciudades que más han cambiado</h2>
<p>Entre los municipios que hoy tienen más de 20.000 electores, las mayores caídas del PSOE entre 1982 y 2023 están en Andalucía y en las coronas urbanas. En <strong>Estepona</strong> (Málaga) pasó del 68,3 % al 25,8 %; en <strong>Chiclana de la Frontera</strong> (Cádiz), del 72,5 % al 30,1 %; en <strong>La Línea de la Concepción</strong>, del 73,2 % al 32,5 %. En Alzira (Valencia), del 68,8 % al 28,5 %; en San Sebastián de los Reyes (Madrid), del 65,6 % al 28,0 %.</p>
{fig('caidas', 'Del 70 % al 30 %', 'Voto al PSOE en 1982 y en 2023 en las diez ciudades de más de 20.000 electores donde más ha caído', 'Fuente: Ministerio del Interior.', [('#f19a9e','1982'),('PSOE','2023')])}
<p>Muchas de estas ciudades se han transformado desde 1982: Mijas, por ejemplo, ha pasado de 5.942 electores en 1977 a 47.977 en 2023. Los datos no permiten separar cuánto de la caída se debe a que han cambiado los votantes y cuánto a que han cambiado de voto los mismos.</p>
""",
    js="""const P6=D.psoe60;
barras('n60',EL.map((e,i)=>({l:e,v:P6.n[i],c:COL.PSOE,lab:[2,4,15].includes(i),t:`${e}: <b>${miles(P6.n[i])}</b> municipios<br>PSOE en España: ${pct(P6.nac[i])}`})),{ticks:[0,200,400,600,800],fy:v=>miles(v),fl:v=>miles(v),max:850,ml:40,aria:'Municipios donde el PSOE superó el 60 %'});
tabla('n60',['Elección','Municipios con el PSOE por encima del 60 %','PSOE en España'],EL.map((e,i)=>[e,miles(P6.n[i]),pct(P6.nac[i])]));
(function(){const CA=P6.caidas;const [box,W,tip]=caja('caidas');const rh=28,m={l:W<500?140:190,r:16,t:4,b:22},H=m.t+m.b+rh*CA.length,x=v=>m.l+v/80*(W-m.l-m.r);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Voto al PSOE en 1982 y 2023'},box);
 [0,20,40,60,80].forEach(v=>{el('line',{x1:x(v),x2:x(v),y1:m.t,y2:H-m.b,stroke:'var(--grid)'},svg);txt(svg,{x:x(v),y:H-5,'text-anchor':'middle'},v+'%')});
 CA.forEach((c,i)=>{const cy=m.t+i*rh+rh/2;txt(svg,{x:m.l-8,y:cy+4,'text-anchor':'end','font-size':12.5},recorta(c[0],W));
  el('line',{x1:x(c[3]),x2:x(c[2]),y1:cy,y2:cy,stroke:'#f19a9e','stroke-width':2},svg);
  el('circle',{cx:x(c[2]),cy,r:5.5,fill:'#f19a9e'},svg);el('circle',{cx:x(c[3]),cy,r:5.5,fill:COL.PSOE},svg);
  const h=el('rect',{x:0,y:cy-rh/2,width:W,height:rh,fill:'transparent'},svg);hover(h,box,tip,`<b>${c[0]}</b> (${c[1]})<br>1982: ${pct(c[2])} · 2023: ${pct(c[3])}`)});})();
tabla('caidas',['Municipio','Provincia','PSOE 1982','PSOE 2023'],P6.caidas.map(c=>[c[0],c[1],pct(c[2]),pct(c[3])]));""",
    pie=PIE,
    descripcion='El PSOE superó el 60 % en al menos 748 municipios en 1982 (máximo: 784 en 1989) y en 67 en 2023. En Estepona pasó del 68,3 % al 25,8 %; en Chiclana, del 72,5 % al 30,1 %.',
    compara='El número de municipios donde el PSOE superó el 60 % de los votos a candidaturas en cada elección general de 1977 a 2023, y su voto en 1982 y 2023 en los municipios de más de 20.000 electores.',
    limites='El fichero oficial de 1982 por municipio no incluye unos 139 municipios que ya existían, así que la cifra de ese año es un mínimo. Los municipios han cambiado mucho de población desde 1982: los datos no dicen si cambió el voto de las mismas personas. Sin voto exterior; el 48,2 % de 1982 es sobre votos a candidaturas (el oficial sobre voto válido es del 48,1 %).',
    fuentes=[INTERIOR_HIST, WIKI_GENERALES, CIVIO_29N],
    enlaces=[],
))

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='nunca-gano-la-derecha', lugar='España', datos=['nunca_derecha'],
    corto='Donde nunca ganó la derecha',
    titulo='Barcelona, Terrassa o Dos Hermanas: 864 municipios donde la derecha estatal nunca ha ganado unas generales',
    dek='En 864 municipios, con 6,5 millones de electores, UCD, AP, el PP, el CDS, Ciudadanos y Vox nunca han sido la lista más votada en 16 elecciones generales. '
        'Casi dos tercios están en Cataluña y el País Vasco; el resto, sobre todo en Andalucía.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} Desde 1977, la derecha de ámbito estatal ha ganado ocho elecciones generales: UCD en 1977 y 1979 y el PP en 1996, 2000, 2011, 2015, 2016 y 2023. Y aun así hay municipios donde ninguno de sus partidos ha sido nunca el más votado.</p>
<p>Son <strong>864 municipios</strong> con datos en las 16 generales, y en ellos viven <strong>6,5 millones de electores</strong>, casi uno de cada cinco de España. En ninguno ha quedado primero UCD, AP o el PP, el CDS, Ciudadanos o Vox. Han ganado el PSOE, la izquierda a su izquierda, ERC, CiU y Junts, el PNV o EH Bildu.</p>
{fig('top', 'Las 15 mayores ciudades donde nunca ha ganado la derecha estatal', 'Electores en 2023 y partidos que han sido la lista más votada alguna vez en las generales de 1977 a 2023', 'Fuente: Ministerio del Interior. ' + FAMILIAS)}
<h2>Barcelona y su área metropolitana</h2>
<p>La mayor es <strong>Barcelona</strong>, con 1,08 millones de electores. En la ciudad han ganado en estas 16 elecciones el PSC, CiU, ERC y los comuns, pero nunca UCD ni el PP, tampoco en las mayorías absolutas de 2000 o 2011. Le siguen L'Hospitalet, Terrassa, Badalona, Sabadell, Mataró, Santa Coloma de Gramenet, Cornellà y Sant Boi, todas en la provincia de Barcelona.</p>
<p>La provincia de Barcelona aporta 223 de los 864 municipios; Girona, 100; Bizkaia, 87; Gipuzkoa, 79; Tarragona, 63, y Lleida, 50. Fuera de Cataluña y el País Vasco destacan Sevilla (42), Jaén (28), Granada (27) y Córdoba (24).</p>
{fig('prov', 'Dónde están', 'Municipios donde la derecha estatal nunca ha ganado unas generales, por provincia (las diez con más)', 'Fuente: Ministerio del Interior.')}
<h2>En Andalucía, el PSOE</h2>
<p>Fuera de Cataluña y el País Vasco, la lista la forman sobre todo municipios andaluces donde el PSOE ha ganado siempre o casi siempre: Dos Hermanas (Sevilla), con 107.888 electores, es el mayor, seguido de Alcalá de Guadaíra. En Barakaldo (Bizkaia) han alternado el PSOE y la izquierda a su izquierda.</p>
<h2>Qué no dicen estos datos</h2>
<p>Que la derecha estatal no haya ganado nunca no significa que tenga poco voto: en Barcelona el PP llegó al 26,8 % en 2000 y pasó del 20 % en otras tres generales. Esta pieza solo mira quién ha quedado primero. Tampoco dice nada de las elecciones municipales o autonómicas, donde algunos de estos municipios sí han tenido alcaldes del PP. CiU, Junts y el PNV no se cuentan como «derecha estatal», porque son partidos de ámbito catalán y vasco.</p>
""",
    js="""const N=D.nunca_derecha;
hbarras('top',N.top.map(f=>({l:f[0],v:f[2],c:COL[f[3].includes('PSOE')?'PSOE':f[3][0]],t:`<b>${f[0]}</b> (${f[1]})<br>${miles(f[2])} electores<br>Han ganado: ${f[3].map(g=>NOM[g]).join(', ')}`})),{ticks:[0,500000,1000000],fy:v=>miles(v),fl:v=>miles(v),max:1150000,ml:190,aria:'Mayores municipios donde nunca ha ganado la derecha estatal'});
tabla('top',['Municipio','Provincia','Electores 2023','Han ganado alguna vez'],N.top.map(f=>[f[0],f[1],miles(f[2]),f[3].map(g=>NOM[g]).join(', ')]));
const PR=Object.entries(N.por_ccaa_prov);
hbarras('prov',PR.map(p=>({l:p[0],v:p[1],c:'var(--acc)',t:`${p[0]}: <b>${p[1]}</b> municipios`})),{ticks:[0,100,200],fy:v=>v,fl:v=>v,max:240,ml:110,aria:'Municipios por provincia'});
tabla('prov',['Provincia','Municipios'],PR);""",
    pie=PIE,
    descripcion='En 864 municipios con 6,5 millones de electores nunca ha sido la lista más votada UCD, AP/PP, CDS, Ciudadanos ni Vox en 16 generales. La mayor es Barcelona; fuera de Cataluña y el País Vasco, Dos Hermanas.',
    compara='El partido más votado en cada municipio en las 16 elecciones generales de 1977 a 2023, con todas las listas.',
    limites='Se mira solo quién queda primero, no el porcentaje. «Derecha estatal» incluye UCD, AP/PP, CDS, Ciudadanos y Vox; no CiU, Junts ni el PNV. Solo elecciones generales. Los municipios sin dato en alguna elección quedan fuera. Sin voto exterior.',
    fuentes=[INTERIOR_HIST, CIVIO_29N],
    enlaces=[],
))

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='nunca-gano-el-psoe', lugar='España', datos=['nunca_psoe'],
    corto='Donde nunca ganó el PSOE',
    titulo='Pozuelo, Getxo o Ávila: 1.932 municipios donde el PSOE nunca ha ganado unas generales',
    dek='Ni con la mayoría de 202 diputados de 1982 ni con Zapatero: en 1.932 municipios, con 1,7 millones de electores, ni el PSOE ni la izquierda estatal a su izquierda han sido nunca la lista más votada. '
        'Son sobre todo pueblos pequeños de Castilla y León y ciudades ricas de Madrid.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} El PSOE ha ganado ocho de las 16 elecciones generales de la democracia, y en 1982 lo hizo con el 48 % de los votos. Pero hay casi 2.000 municipios donde nunca ha sido el partido más votado.</p>
<p>Son <strong>1.932 municipios</strong> con datos en las 16 generales, con <strong>1,7 millones de electores</strong>. En ellos no ha quedado primero nunca el PSOE, y tampoco el PCE, Izquierda Unida, Podemos o Sumar. Es una lista de pueblos más pequeños que la de los municipios donde nunca ha ganado la derecha estatal, que suman 6,5 millones de electores en 864 municipios.</p>
{fig('top', 'Los 15 mayores municipios donde el PSOE nunca ha ganado', 'Electores en 2023 y partidos que han sido la lista más votada alguna vez en las generales de 1977 a 2023', 'Fuente: Ministerio del Interior. ' + FAMILIAS)}
<h2>Las ciudades: el oeste de Madrid, Galicia y el País Vasco</h2>
<p>La mayor es <strong>Pozuelo de Alarcón</strong>, con 64.677 electores, donde solo han ganado UCD y el PP. Le siguen <strong>Getxo</strong> (Bizkaia), donde se han alternado el PNV y el PP; <strong>Ávila</strong>, con UCD, AP, el CDS y el PP; Boadilla del Monte, Orihuela, Villaviciosa de Odón, Torrelodones y Villanueva de la Cañada. En Galicia, A Estrada, Lalín y Poio. En Cataluña, <strong>Vic</strong>, donde se han repartido las victorias CiU, Junts y ERC.</p>
<p>No todos son municipios de derechas: en 224 de ellos ha ganado alguna vez ERC, y en Durango, Amorebieta o Tolosa se han alternado el PNV y EH Bildu.</p>
<h2>Los pueblos de Castilla y León</h2>
<p>Por número, la lista la dominan los pueblos pequeños de Castilla y León: Burgos aporta 170 municipios; Ávila, 133; Palencia, 124; Segovia, 98; Zamora, 86; Soria, 85, y Valladolid, 79. Lleida, Barcelona y Girona, con 90, 89 y 78, son las provincias catalanas con más.</p>
{fig('prov', 'Dónde están', 'Municipios donde ni el PSOE ni la izquierda estatal han ganado nunca unas generales, por provincia (las diez con más)', 'Fuente: Ministerio del Interior.')}
<h2>Qué no dicen estos datos</h2>
<p>Esta pieza solo mira quién ha quedado primero. En muchos de estos municipios el PSOE ha superado el 30 % y ha perdido por poco. Tampoco incluye las elecciones municipales, donde algunos sí han tenido alcaldes socialistas.</p>
""",
    js="""const N=D.nunca_psoe;
hbarras('top',N.top.map(f=>({l:f[0],v:f[2],c:COL[f[3].includes('PP')?'PP':(f[3].includes('PNV')?'PNV':f[3][0])],t:`<b>${f[0]}</b> (${f[1]})<br>${miles(f[2])} electores<br>Han ganado: ${f[3].map(g=>NOM[g]).join(', ')}`})),{ticks:[0,20000,40000,60000],fy:v=>miles(v),fl:v=>miles(v),max:70000,ml:180,aria:'Mayores municipios donde nunca ha ganado el PSOE'});
tabla('top',['Municipio','Provincia','Electores 2023','Han ganado alguna vez'],N.top.map(f=>[f[0],f[1],miles(f[2]),f[3].map(g=>NOM[g]).join(', ')]));
const PR=Object.entries(N.por_prov);
hbarras('prov',PR.map(p=>({l:p[0],v:p[1],c:'var(--acc)',t:`${p[0]}: <b>${p[1]}</b> municipios`})),{ticks:[0,50,100,150],fy:v=>v,fl:v=>v,max:180,ml:110,aria:'Municipios por provincia'});
tabla('prov',['Provincia','Municipios'],PR);""",
    pie=PIE,
    descripcion='En 1.932 municipios con 1,7 millones de electores, ni el PSOE ni la izquierda estatal han sido nunca la lista más votada en 16 generales. Los mayores: Pozuelo, Getxo y Ávila. Burgos aporta 170 pueblos.',
    compara='El partido más votado en cada municipio en las 16 elecciones generales de 1977 a 2023, con todas las listas.',
    limites='Se mira solo quién queda primero, no el porcentaje. «Izquierda estatal» es el PSOE y la familia PCE / IU / Podemos / Sumar; ERC y EH Bildu no se cuentan, y en 224 de estos municipios ha ganado ERC alguna vez. Solo elecciones generales. Sin voto exterior.',
    fuentes=[INTERIOR_HIST, CIVIO_29N],
    enlaces=[('los municipios donde nunca ha ganado la derecha estatal', 'nunca-gano-la-derecha')],
    foto=dict(src='img/actualidad/fotos/nunca-gano-el-psoe.jpg', ancho=1280, alto=720, ia=True, pie='Alberto Núñez Feijóo y el PP.', origen='pp-feijoo.jpg'),
))

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='mont-roig-municipio-cambiante', lugar='Mont-roig del Camp (Tarragona)', datos=['cambiantes'],
    corto='Mont-roig del Camp',
    titulo='Siete partidos distintos han ganado en Mont-roig del Camp: ha cambiado 11 veces de ganador en 16 generales',
    dek='UCD, PSOE, CiU, PP, Ciudadanos, En Comú y ERC han sido la lista más votada en este municipio de Tarragona. Ningún otro de más de 5.000 electores ha cambiado tantas veces. '
        'El municipio medio de ese tamaño ha cambiado 4,4 veces.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} Hay municipios que nunca cambian de ganador y otros que cambian casi cada vez. El que más lo ha hecho entre los que tienen más de 5.000 electores está en la costa de Tarragona: <strong>Mont-roig del Camp</strong>, con 8.171 electores en 2023.</p>
<p>En las 16 elecciones generales desde 1977, Mont-roig ha cambiado de partido más votado <strong>11 veces</strong> y ha tenido <strong>siete ganadores distintos</strong>: UCD (1977 y 1979), el PSC (1982, 1986, 1996, 2004, 2008, abril de 2019 y 2023), CiU (1989 y 1993), el PP (2000 y 2011), Ciudadanos (2015), En Comú Podem (2016) y ERC (noviembre de 2019).</p>
{fig('rej', 'Once cambios de ganador', 'Partido más votado en cada elección general en los municipios de más de 5.000 electores que más veces han cambiado', 'Fuente: Ministerio del Interior. ' + FAMILIAS, [('UCD','UCD'),('PSOE','PSOE / PSC'),('JUNTS','CiU / Junts'),('PP','AP / PP'),('CS','Ciudadanos'),('SUMAR','IU / Podemos / En Comú'),('ERC','ERC'),('CC','Coalición Canaria'),('CDS','CDS'),('BILDU','HB / EH Bildu'),('PNV','PNV'),('OTROS','Otras listas')])}
<h2>Los otros: Canarias y Gipuzkoa</h2>
<p>Detrás de Mont-roig, con diez cambios, están dos municipios canarios: Yaiza (Lanzarote) y Tegueste (Tenerife). Con nueve, Teguise y Agüimes, también en Canarias, Legazpi (Gipuzkoa), El Paso (La Palma) y Eivissa. Teguise y Santa Lucía de Tirajana (Gran Canaria) igualan a Mont-roig en número de ganadores distintos, siete, aunque con menos cambios.</p>
<p>En los municipios canarios de la lista, a los partidos estatales se suman los propios: Coalición Canaria ha sido la más votada alguna vez en todos ellos menos en Eivissa, que es balear, y el CDS ganó en Teguise y Agüimes en 1989. En Legazpi se han alternado el PNV, el PSOE, EH Bildu y la izquierda estatal.</p>
<p>El municipio medio de más de 5.000 electores ha cambiado de ganador 4,4 veces en estas 16 elecciones.</p>
<h2>Qué no dicen estos datos</h2>
<p>Cambiar de ganador no exige grandes movimientos de voto: basta con que el primero y el segundo se crucen. Contar cambios dice cuántas veces se ha alterado el primer puesto, no cuánto ha cambiado el voto.</p>
""",
    js="""const R=D.cambiantes.filas;
rejilla('rej',EL,R.map((f,i)=>({l:f[0],b:i==0,g:f[5],t:`${f[1]} · ${f[3]} cambios · ${f[4]} ganadores distintos`})),{aria:'Partido más votado en los municipios más cambiantes'});
tabla('rej',['Municipio','Provincia','Electores 2023','Cambios de ganador','Ganadores distintos'],R.map(f=>[f[0],f[1],miles(f[2]),f[3],f[4]]));""",
    pie=PIE,
    descripcion='Mont-roig del Camp (Tarragona) ha cambiado 11 veces de ganador en 16 generales, con siete partidos distintos: UCD, PSC, CiU, PP, Cs, En Comú y ERC. La media de los municipios de más de 5.000 electores es 4,4.',
    compara='El partido más votado en cada elección general de 1977 a 2023 en los municipios con más de 5.000 electores en 2023, y el número de veces que ha cambiado.',
    limites='Contar cambios no mide cuánto se mueve el voto: un cambio puede decidirse por pocos votos. Con todas las listas, también las locales y regionales. Sin voto exterior.',
    fuentes=[INTERIOR_HIST, CIVIO_29N],
    enlaces=[],
))

# ---------------------------------------------------------------------------------------------------------------
EL_DEBATE = 'https://www.eldebate.com/espana/20260912/cuanto-adulterado-ley-nietos-censo-electoral-municipio_457471.html'
P.append(dict(
    slug='baltar-censo-y-participacion', lugar='Ourense y Lugo', datos=['baltar'],
    corto='Baltar',
    titulo='En Baltar votó el 16 % en 1979; hoy vota el 79 %. La participación imposible del interior gallego',
    dek='En las primeras generales, en decenas de pueblos de Ourense y Lugo votaba menos de uno de cada cuatro electores. En Baltar, el 16 % en 1979. '
        'A principios de los noventa su censo se redujo a la mitad y la participación saltó al 65 %. Hoy está en la media de España.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">El censo de los españoles que viven en el extranjero está en el centro de la campaña del 29N. El Tribunal Supremo ha ordenado detener las nuevas altas en el censo exterior de quienes obtuvieron la nacionalidad por la llamada ley de nietos, y Ourense destaca entre las capitales de provincia con el 31 % de su censo en el exterior, <a href="{EL_DEBATE}">según El Debate</a>. Los resultados de las primeras elecciones muestran que la relación entre censo y emigración en Galicia viene de lejos.</p>
<h2>Uno de cada seis</h2>
<p>En las generales de marzo de 1979 votó el 67,6 % de los electores de España (sin voto exterior). En la provincia de Ourense, el <strong>41,6 %</strong>; en Lugo, el 46,2 %. Y en algunos municipios, muchísimo menos. En <strong>Baltar</strong> (Ourense), con 3.229 electores en el censo, votaron 522: el <strong>16,2 %</strong>. Trasmiras, San Xoán de Río, O Irixo, Vilardevós o Cualedro, todos en Ourense, se quedaron por debajo del 21 %. Los diez municipios con menos participación de España aquel año, entre los de más de 1.000 electores, estaban en Ourense.</p>
{fig('baltar', 'Baltar: el censo baja a la mitad y la participación se dispara', 'Electores en el censo (barras) y participación (línea) en cada elección general', 'Fuente: Ministerio del Interior. ' + SIN_CERA, [('#9a9a9a','Electores'),('var(--acc)','Participación')], tabla=True)}
<h2>El salto de los noventa</h2>
<p>Hasta 1986, Baltar tenía unos 3.150 electores y votaba uno de cada cuatro. En 1989 el censo bajó a 2.501 y en 1993 a <strong>1.477</strong>, la mitad que siete años antes. La participación pasó del 25 % al <strong>65 %</strong> y en 2000 llegó al 79 %, por encima de la media de España. Hoy Baltar tiene 751 electores y en 2023 votó el 79,5 %.</p>
<p>El mismo patrón, menos extremo, se ve en toda la provincia. Ourense tenía 349.045 electores en 1986 y 306.085 en 1993; su participación subió del 51,3 % al 68,8 %. En Paradela (Lugo) votó el 18,2 % en 1977 y el 76,2 % en 2023.</p>
{fig('prov', 'Ourense y Lugo alcanzan a España en los noventa', 'Participación en las elecciones generales', 'Fuente: Ministerio del Interior. ' + SIN_CERA, [('var(--acc)','Ourense'),('#7ab8e6','Lugo'),('#9a9a9a','España')])}
<h2>Una hipótesis: los emigrantes en el censo</h2>
<p>Los datos no explican por sí solos el cambio, pero encajan con una hipótesis: que en los primeros censos figuraran como residentes muchos vecinos que vivían fuera, en otras provincias o en el extranjero, y que no votaban. La Ley Orgánica del Régimen Electoral General de 1985 separó en dos el censo: los residentes en España y los residentes ausentes que viven en el extranjero (CERA), que no se cuentan en estos datos. La caída del censo de Baltar y de Ourense coincide con los años siguientes a esa ley.</p>
<p>Para confirmarlo harían falta los datos de altas y bajas del censo de esos años, que esta pieza no tiene. Es una hipótesis, no una conclusión.</p>
""",
    js="""const B=D.baltar.Baltar;
(function(){const [box,W,tip]=caja('baltar');const H=W<500?260:300,m={l:44,r:44,t:14,b:W<560?52:28},n=EL.length,bw=(W-m.l-m.r)/n,yc=v=>H-m.b-v/3500*(H-m.t-m.b),yp=v=>H-m.b-v/100*(H-m.t-m.b);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Censo y participación en Baltar'},box);
 [0,1000,2000,3000].forEach(v=>{el('line',{x1:m.l,x2:W-m.r,y1:yc(v),y2:yc(v),stroke:'var(--grid)'},svg);txt(svg,{x:m.l-6,y:yc(v)+4,'text-anchor':'end'},miles(v))});
 [0,25,50,75,100].forEach(v=>txt(svg,{x:W-m.r+6,y:yp(v)+4,fill:'var(--acc)'},v+'%'));
 let d='';EL.forEach((e,i)=>{const x=m.l+i*bw;el('rect',{x:x+3,y:yc(B.censo[i]),width:bw-6,height:yc(0)-yc(B.censo[i]),rx:2,fill:'#9a9a9a','fill-opacity':.55},svg);d+=(i?'L':'M')+(x+bw/2)+','+yp(B.part[i]);
  const h=el('rect',{x,y:m.t,width:bw,height:H-m.t-m.b,fill:'transparent'},svg);hover(h,box,tip,`<b>Baltar, ${e}</b><br>${miles(B.censo[i])} electores<br>Participación: <b>${pct(B.part[i])}</b>`)});
 el('path',{d,fill:'none',stroke:'var(--acc)','stroke-width':3},svg);EL.forEach((e,i)=>el('circle',{cx:m.l+i*bw+bw/2,cy:yp(B.part[i]),r:3.5,fill:'var(--acc)'},svg));
 etiquetasX(svg,EL,i=>m.l+i*bw+bw/2,H,m,W);})();
tabla('baltar',['Elección','Electores Baltar','Participación Baltar','Electores Paradela','Participación Paradela'],EL.map((e,i)=>[e,miles(B.censo[i]),pct(B.part[i]),miles(D.baltar.Paradela.censo[i]),pct(D.baltar.Paradela.part[i])]));
lineas('prov',EL,[{n:'Ourense',c:'var(--acc)',v:D.baltar.prov.Ourense,w:3.5},{n:'Lugo',c:'#7ab8e6',v:D.baltar.prov.Lugo,dy:10},{n:'España',c:'#9a9a9a',v:D.baltar.nac,dy:-6}],{min:30,max:90,ticks:[30,50,70,90],aria:'Participación en Ourense, Lugo y España'});
tabla('prov',['Elección','Ourense','Lugo','España','Electores Ourense','Electores Lugo'],EL.map((e,i)=>[e,pct(D.baltar.prov.Ourense[i]),pct(D.baltar.prov.Lugo[i]),pct(D.baltar.nac[i]),miles(D.baltar.censo_prov.Ourense[i]),miles(D.baltar.censo_prov.Lugo[i])]));""",
    pie=PIE,
    descripcion='En Baltar (Ourense) votó el 16,2 % en 1979. Su censo pasó de 3.152 electores en 1986 a 1.477 en 1993 y la participación, del 25 % al 65 %. Ourense entera votó el 41,6 % en 1979.',
    compara='El censo y la participación en las elecciones generales de 1977 a 2023 en Baltar, Paradela y las provincias de Ourense y Lugo, sin el censo de residentes en el extranjero.',
    limites='Los datos muestran que el censo bajó y la participación subió a la vez; no prueban por qué. La explicación de los emigrantes inscritos como residentes es una hipótesis: faltan los datos de altas y bajas del censo de aquellos años. Sin voto exterior.',
    fuentes=[INTERIOR_HIST,
             ('https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672', 'BOE, Ley Orgánica 5/1985, de 19 de junio, del Régimen Electoral General, artículo 31 (censo de residentes y de residentes ausentes)'),
             (EL_DEBATE, 'El Debate, «¿Cuánto ha adulterado la ley de nietos el censo electoral de tu municipio?» (12-9-2026)')],
    enlaces=[],
))

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='europeas-arona', lugar='Canarias, Ceuta y Melilla', datos=['europeas'],
    corto='Europeas en Arona',
    titulo='En Arona votó uno de cada cinco electores en las europeas de 2014',
    dek='Las europeas de 2014 dejaron el 45,8 % de participación en España. En Arona (Tenerife), el 22,3 %, el mínimo entre los municipios de más de 20.000 electores. '
        'Ceuta, Melilla y la costa canaria ocupan los últimos puestos. Pero Arona también vota poco en las generales.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">Las elecciones europeas son las que menos interesan en España, y en algunos municipios casi nadie vota. Las de mayo de 2014 son un buen ejemplo: en el conjunto del país votó el <strong>45,8 %</strong> del censo (sin voto exterior).</p>
<p>Entre los municipios de más de 20.000 electores, el que menos votó fue <strong>Arona</strong>, en el sur de Tenerife: el <strong>22,3 %</strong>, uno de cada cinco. Le siguieron Ceuta (26,8 %), Granadilla de Abona (27,6 %), Arrecife (27,9 %), Melilla (28,0 %) y Adeje (28,1 %). En el otro extremo, Tres Cantos (57,2 %), Sant Cugat (56,2 %) y Quart de Poblet (55,4 %) pasaron del 55 %.</p>
{fig('bajas', 'Los que menos votaron en las europeas de 2014', 'Participación en los municipios de más de 20.000 electores con menos participación', 'Fuente: Ministerio del Interior. El censo de las europeas incluye a los ciudadanos de otros países de la UE inscritos para votar.')}
<h2>No es solo un efecto de los residentes europeos</h2>
<p>En las europeas y en las municipales pueden votar los ciudadanos de otros países de la Unión Europea que viven en España y se inscriben. En Arona, el censo de las europeas de 2014 tenía 45.350 electores, unos 5.800 más que el de las generales de 2015 (39.553). Si muchos de esos residentes no votaron, eso rebaja la participación.</p>
<p>Pero no lo explica todo. En las generales de diciembre de 2015, con un censo solo de españoles, en Arona votó el <strong>53,5 %</strong>, muy por debajo del 73,1 % de España. En Ceuta y Melilla, donde los censos de las dos elecciones son casi iguales, la participación en las europeas también fue de las más bajas.</p>
{fig('comp', 'Bajas en las europeas y también en las generales', 'Participación en las europeas de 2014 y en las generales de 2015', 'Fuente: Ministerio del Interior. Sin voto exterior.', [('#9a9a9a','Europeas 2014'),('var(--acc)','Generales 2015')])}
<h2>Por provincias</h2>
<p>Por provincias, las que menos votaron en 2014 fueron Ceuta (26,8 %), Melilla (28,0 %), Baleares (36,4 %), Cádiz (37,6 %), Santa Cruz de Tenerife (37,7 %) y Las Palmas (37,8 %). Las que más, Valencia (53,0 %), Palencia, Cuenca, Segovia y Valladolid, todas por encima del 50 %.</p>
<p>Las europeas de 2014 se votaron solas, sin otras elecciones el mismo día. Cuando han coincidido con las municipales, como en 2019, la participación ha subido casi 20 puntos.</p>
""",
    js="""const E=D.europeas;
hbarras('bajas',E.bajas14.map(b=>({l:b[0],v:b[3],c:'var(--acc)',t:`<b>${b[0]}</b> (${b[1]})<br>${miles(b[2])} electores · participación <b>${pct(b[3])}</b>`})),{ticks:[0,15,30,45],max:50,ml:180,aria:'Municipios con menos participación en las europeas de 2014'});
tabla('bajas',['Municipio','Provincia','Electores','Participación'],E.bajas14.concat(E.altas14).map(b=>[b[0],b[1],miles(b[2]),pct(b[3])]));
(function(){const C=E.comparacion;const [box,W,tip]=caja('comp');const rh=30,m={l:W<500?130:170,r:16,t:4,b:22},H=m.t+m.b+rh*C.length,x=v=>m.l+v/80*(W-m.l-m.r);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Participación en europeas 2014 y generales 2015'},box);
 [0,20,40,60,80].forEach(v=>{el('line',{x1:x(v),x2:x(v),y1:m.t,y2:H-m.b,stroke:'var(--grid)'},svg);txt(svg,{x:x(v),y:H-5,'text-anchor':'middle'},v+'%')});
 C.forEach((c,i)=>{const cy=m.t+i*rh+rh/2;txt(svg,{x:m.l-8,y:cy+4,'text-anchor':'end','font-size':12.5},recorta(c[0],W));
  el('line',{x1:x(c[3]),x2:x(c[4]),y1:cy,y2:cy,stroke:'#9a9a9a','stroke-width':2},svg);
  el('circle',{cx:x(c[3]),cy,r:5.5,fill:'#9a9a9a'},svg);el('circle',{cx:x(c[4]),cy,r:5.5,fill:'var(--acc)'},svg);
  const h=el('rect',{x:0,y:cy-rh/2,width:W,height:rh,fill:'transparent'},svg);hover(h,box,tip,`<b>${c[0]}</b><br>Europeas 2014: ${pct(c[3])} (${miles(c[1])} electores)<br>Generales 2015: ${pct(c[4])} (${miles(c[2])} electores)`)});})();
tabla('comp',['Municipio','Electores europeas 2014','Electores generales 2015','Participación europeas','Participación generales'],E.comparacion.map(c=>[c[0],miles(c[1]),miles(c[2]),pct(c[3]),pct(c[4])]));""",
    pie=PIE,
    descripcion='En las europeas de 2014 votó el 22,3 % en Arona, el mínimo entre los municipios de más de 20.000 electores, frente al 45,8 % de España. En las generales de 2015 Arona votó el 53,5 %, también muy por debajo de la media.',
    compara='La participación en las elecciones europeas de 2014 en los municipios de más de 20.000 electores y por provincia, y la de las generales de 2015 en los que menos votaron.',
    limites='El censo de las europeas incluye a los ciudadanos de otros países de la UE inscritos para votar, que no figuran en el de las generales. Los datos no dicen quién dejó de votar ni por qué. Sin voto exterior.',
    fuentes=[INTERIOR_HIST],
    enlaces=[],
))

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='euskadi-empate-a-tres', lugar='País Vasco', datos=['euskadi'],
    corto='Euskadi, empate a tres',
    titulo='Tres partidos en 1,3 puntos: el empate a tres de Euskadi en 2023 no tiene precedentes',
    dek='En julio de 2023 el PSE sacó el 25,4 % en el País Vasco, el PNV el 24,2 % y EH Bildu el 24,1 %. En ninguna de las 16 generales desde 1977 habían quedado tres partidos tan juntos. '
        'El PSE fue el más votado, pero EH Bildu ganó en 140 municipios y el PSE en 29.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} En el País Vasco llegan con un precedente inédito: en las generales de julio de 2023, los tres primeros partidos quedaron separados por poco más de un punto.</p>
<p>El PSE-EE sacó el <strong>25,4 %</strong> de los votos a candidaturas (sin voto exterior), el PNV el <strong>24,2 %</strong> y EH Bildu el <strong>24,1 %</strong>. Entre el primero y el tercero, 1,3 puntos. En las 15 generales anteriores, la distancia más corta entre el primero y el tercero había sido de 5,9 puntos, en 1989.</p>
{fig('serie', 'Cuatro décadas de voto en Euskadi', 'Voto en las generales en Álava, Bizkaia y Gipuzkoa', 'Fuente: Ministerio del Interior. HB, EH, Amaiur y EH Bildu, en la misma familia; en 2000, 2004 y 2008 la izquierda abertzale no se presentó o sus listas fueron ilegalizadas. ' + SIN_CERA, [('PNV','PNV'),('PSOE','PSE-EE (PSOE)'),('BILDU','HB / EH Bildu'),('PP','AP / PP'),('SUMAR','IU / Podemos / Sumar')])}
<h2>El PNV, primero casi siempre</h2>
<p>El PNV fue el partido más votado en el País Vasco en 11 de las 16 generales. Las excepciones son 1993 y 2008, cuando ganó el PSE; 2015 y 2016, cuando ganó Podemos (con el 29,1 % y el 29,2 %), y 2023. Su mejor resultado fue el 34,2 % de 2004. El de 2023, el 24,2 %, es el más bajo desde 1989.</p>
<p>EH Bildu, con el 24,1 %, igualó prácticamente el 24,4 % de Amaiur en 2011, el máximo de la izquierda abertzale en unas generales.</p>
{fig('dif', 'Nunca habían estado tan cerca', 'Distancia en puntos entre el primer y el tercer partido en el País Vasco, en cada elección general', 'Fuente: Ministerio del Interior.')}
<h2>Tres territorios, tres ganadores</h2>
<p>Cada territorio votó distinto. En <strong>Gipuzkoa</strong> ganó EH Bildu, con el 31,4 %; en <strong>Bizkaia</strong>, el PNV, con el 27,1 %, por delante del PSE (26,0 %), y en <strong>Álava</strong>, el PSE, con el 27,8 %.</p>
<p>Y por municipios, el mapa es muy distinto del total: EH Bildu fue la lista más votada en <strong>140</strong> de los 251 municipios vascos, el PNV en 76, el PSE en 29 y el PP en 6. El PSE sumó más votos ganando en menos municipios, pero más poblados.</p>
""",
    js="""const K=D.euskadi;
lineas('serie',EL,[{n:'PNV',c:COL.PNV,v:K.PNV,w:3},{n:'PSE',c:COL.PSOE,v:K.PSOE,w:3,dy:-8},{n:'Bildu',c:COL.BILDU,v:K.BILDU.map(v=>v||null),w:3,dy:10},{n:'PP',c:COL.PP,v:K.PP.map(v=>v||null),w:1.6},{n:'Sumar',c:COL.SUMAR,v:K.SUMAR,w:1.6}],{max:40,ticks:[0,10,20,30,40],aria:'Voto en el País Vasco en las generales'});
tabla('serie',['Elección','PNV','PSE','HB/EH Bildu','AP/PP','IU/Podemos/Sumar'],EL.map((e,i)=>[e,pct(K.PNV[i]),pct(K.PSOE[i]),K.BILDU[i]?pct(K.BILDU[i]):'no se presentó',pct(K.PP[i]),pct(K.SUMAR[i])]));
barras('dif',EL.map((e,i)=>({l:e,v:K.dif3[i],c:i==15?'var(--acc)':'#9a9a9a',lab:i==15||i==4,t:`${e}: <b>${num(K.dif3[i])}</b> puntos entre el primero y el tercero`})),{ticks:[0,5,10,15,20],fy:v=>v,max:21,ml:30,aria:'Distancia entre el primer y el tercer partido'});
tabla('dif',['Elección','Puntos entre el 1.º y el 3.º'],EL.map((e,i)=>[e,num(K.dif3[i])]));""",
    pie=PIE,
    descripcion='En las generales de 2023, PSE (25,4 %), PNV (24,2 %) y EH Bildu (24,1 %) quedaron en 1,3 puntos en el País Vasco, la menor distancia entre tres partidos desde 1977. EH Bildu ganó en 140 municipios; el PSE, en 29.',
    compara='El voto en las elecciones generales de 1977 a 2023 en Álava, Bizkaia y Gipuzkoa, la distancia entre el primer y el tercer partido y el ganador por municipio en 2023.',
    limites='Porcentajes sobre votos a candidaturas y sin voto exterior, por eso difieren algo de los oficiales. La izquierda abertzale no concurrió con lista propia en 2000, 2004 y 2008. Navarra no se incluye.',
    fuentes=[INTERIOR_HIST, CIVIO_29N],
    enlaces=[],
))

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='voto-en-blanco', lugar='España', datos=['blanco'],
    corto='El voto en blanco',
    titulo='El voto en blanco se multiplicó por seis entre 1977 y 2000, y desde entonces se ha reducido a la mitad',
    dek='En las primeras generales votó en blanco el 0,27 % de los votantes; en 2000 y 2004, cerca del 1,6 %, con más de 400.000 papeletas en 2004. En 2023, el 0,80 %. '
        'Los nulos han ido por otro camino: altos en 1982 y en 2011.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} Cada campaña hay quien anuncia que votará en blanco o nulo. La historia muestra que son pocos, aunque menos pocos que al principio de la democracia.</p>
<p>En junio de 1977 votaron en blanco 49.827 personas, el <strong>0,27 %</strong> de los votantes (sin contar el voto exterior). El voto en blanco fue creciendo elección tras elección hasta el <strong>1,58 %</strong> de 2000 y el 1,57 % de 2004, cuando llegó a <strong>406.496 papeletas</strong>, su máximo. Desde entonces ha bajado: el 1,12 % en 2008, el 1,35 % en 2011, entre el 0,74 % y el 0,89 % de 2015 a 2019 y el <strong>0,80 %</strong> en 2023, 199.103 votos.</p>
{fig('serie', 'Blancos y nulos desde 1977', 'Porcentaje de votantes que votaron en blanco o nulo en cada elección general', 'Fuente: Ministerio del Interior, resultados por municipio (1977-2000) y por mesa (2004-2023). ' + SIN_CERA, [('var(--acc)','En blanco'),('#9a9a9a','Nulo')])}
<h2>Los nulos, otra historia</h2>
<p>El voto nulo no ha seguido al blanco. Fue alto en las primeras elecciones: el 1,44 % en 1977 y el <strong>1,93 %</strong> en 1982, su máximo. Bajó por debajo del 1 % en los noventa y volvió a subir en 2011, hasta el 1,29 %. En 2023 fue del 1,05 %, más que el blanco.</p>
<h2>Cómo se cuentan</h2>
<p>En las elecciones españolas, el voto en blanco cuenta como voto válido y entra en el cálculo del 3 % que necesita una lista para tener escaño en su provincia; el nulo no cuenta. Los porcentajes de esta pieza están calculados sobre todos los votantes, para que blancos y nulos se puedan comparar. Por eso son algo distintos de los oficiales, que calculan el blanco sobre los votos válidos.</p>
<h2>Qué no dicen estos datos</h2>
<p>Los resultados no dicen por qué alguien vota en blanco o nulo. Un voto nulo puede ser una protesta o un error, y los datos no permiten distinguirlos.</p>
""",
    js="""const B=D.blanco;
lineas('serie',EL,[{n:'En blanco',c:'var(--acc)',v:B.blancos,w:3.5},{n:'Nulo',c:'#9a9a9a',v:B.nulos}],{max:2.2,ticks:[0,0.5,1,1.5,2],fy:v=>num(v)+'%',fl:v=>pct(v,2),aria:'Voto en blanco y nulo en las generales'});
tabla('serie',['Elección','En blanco (% votantes)','Votos en blanco','Nulo (% votantes)'],EL.map((e,i)=>[e,pct(B.blancos[i],2),miles(B.blancos_abs[i]),pct(B.nulos[i],2)]));""",
    pie=PIE,
    descripcion='El voto en blanco pasó del 0,27 % de los votantes en 1977 al 1,58 % en 2000 y a 406.496 papeletas en 2004. En 2023 fue el 0,80 %. El nulo tuvo su máximo en 1982 (1,93 %).',
    compara='Los votos en blanco y nulos en las 16 elecciones generales de 1977 a 2023, como porcentaje de los votantes.',
    limites='Porcentajes sobre el total de votantes, no sobre el voto válido como en la cifra oficial. De 1977 a 2000 los datos vienen de los ficheros por municipio de Interior y de 2004 en adelante de los resultados por mesa. Sin voto exterior.',
    fuentes=[INTERIOR_HIST,
             ('https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672', 'BOE, Ley Orgánica 5/1985, del Régimen Electoral General, artículos 96 y 163 (voto nulo, voto en blanco y barrera del 3 %)')],
    enlaces=[],
))

# ---------------------------------------------------------------------------------------------------------------
WIKI_1979 = 'https://es.wikipedia.org/wiki/Elecciones_generales_de_Espa%C3%B1a_de_1979'
P.append(dict(
    slug='psa-andalucistas-1979', lugar='Andalucía', datos=['psa'],
    corto='El PSA en 1979',
    titulo='Antes de Teruel Existe: los cinco diputados andalucistas de 1979 y el 19,7 % de Cádiz',
    dek='En 1979 el Partido Socialista de Andalucía sacó 325.842 votos y cinco diputados, con el 19,7 % en la provincia de Cádiz y más del 30 % en Jerez y San Fernando. '
        'Tres años después perdió todos sus escaños.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} Los partidos de un solo territorio, como Teruel Existe, que entró en el Congreso en 2019 con un diputado, no son una novedad. En 1979 un partido andaluz consiguió cinco.</p>
<p>El Partido Socialista de Andalucía (PSA-PA), de Alejandro Rojas-Marcos, sacó en las generales de marzo de 1979 <strong>325.842 votos</strong>, el 1,8 % de España, y <strong>cinco diputados</strong>, según los resultados oficiales.</p>
<h2>Cádiz y Sevilla</h2>
<p>Su voto estuvo muy concentrado. En la provincia de <strong>Cádiz</strong> sacó el <strong>19,7 %</strong>; en Sevilla, el 14,6 %, y en Málaga, el 12,3 %. En Jaén y Almería no llegó al 4 %.</p>
{fig('prov', 'Un voto concentrado en el oeste', 'Voto al PSA-PA en las generales de 1979, por provincia andaluza', 'Fuente: Ministerio del Interior, resultados por municipio. Porcentajes sobre votos a candidaturas, sin voto exterior.', [('#2f9e5b','PSA-PA')])}
<p>Por municipios, entre los de más de 2.000 electores, sus mejores resultados fueron El Viso del Alcor (Sevilla), con el 34,5 %; Ubrique (Cádiz), con el 33,6 %; Iznájar (Córdoba), con el 31,7 %; y dos ciudades grandes de Cádiz: <strong>Jerez de la Frontera</strong> (30,6 %) y <strong>San Fernando</strong> (30,1 %).</p>
{fig('top', 'Donde más votos sacó', 'Voto al PSA-PA en 1979 en los municipios de más de 2.000 electores', 'Fuente: Ministerio del Interior.')}
<h2>De cinco escaños a ninguno</h2>
<p>En octubre de 1982 el PSA-PA bajó a 89.025 votos y perdió todos sus diputados.</p>
<h2>Qué no dicen estos datos</h2>
<p>Los resultados no explican por qué el andalucismo fue tan fuerte en 1979 en Cádiz y Sevilla ni por qué se hundió en 1982. Para eso hacen falta estudios sobre aquel periodo, que esta pieza no aporta.</p>
""",
    js="""const S=D.psa;
hbarras('prov',S.prov79.map(p=>({l:p[0],v:p[2],c:'#2f9e5b',b:p[0]=='Cádiz',t:`${p[0]}: <b>${pct(p[2])}</b> (${miles(p[1])} votos)`})),{ticks:[0,5,10,15,20],max:22,ml:90,rh:26,aria:'Voto al PSA-PA por provincia en 1979'});
tabla('prov',['Provincia','Votos','%'],S.prov79.map(p=>[p[0],miles(p[1]),pct(p[2])]));
hbarras('top',S.top79.map(p=>({l:p[0],v:p[2],c:'#2f9e5b',t:`<b>${p[0]}</b> (${p[1]}): ${pct(p[2])}`})),{ticks:[0,10,20,30],max:38,ml:170,aria:'Municipios con más voto al PSA-PA en 1979'});
tabla('top',['Municipio','Provincia','PSA-PA 1979'],S.top79.map(p=>[p[0],p[1],pct(p[2])]));""",
    pie=PIE,
    descripcion='El PSA-PA sacó en 1979 325.842 votos y cinco diputados, con el 19,7 % en Cádiz y más del 30 % en Jerez y San Fernando. En 1982 bajó a 89.025 votos y se quedó sin escaños.',
    compara='El voto al Partido Socialista de Andalucía (PSA-PA) en las generales de 1979 y 1982, por provincia y por municipio.',
    limites='Las cifras por provincia y municipio son sobre votos a candidaturas y sin voto exterior; la cifra nacional de votos y los escaños son los oficiales. En los datos por municipio el PSA-PA suma 327.713 votos, algo más que la cifra oficial. No incluye la lista PSAR-PSDA, también andalucista. El PSOE se presentaba en Andalucía como PSA-PSOE en 1982; es otra candidatura.',
    fuentes=[INTERIOR_HIST,
             (WIKI_1979, 'Wikipedia, «Elecciones generales de España de 1979»: votos y escaños oficiales del PSA-PA (consultada el 8-10-2026)'),
             ('https://es.wikipedia.org/wiki/Teruel_Existe', 'Wikipedia, «Teruel Existe» (consultada el 8-10-2026)')],
    enlaces=[('según los resultados oficiales', WIKI_1979)],
))

# ---------------------------------------------------------------------------------------------------------------
BOE_MAYORIA = 'https://www.boe.es/buscar/doc.php?id=BOE-A-1978-28627'
P.append(dict(
    slug='censo-electoral-desde-1977', lugar='España', datos=['censo'],
    corto='El censo desde 1977',
    titulo='De 23,6 a 35,1 millones: el censo electoral ha crecido un 49 % desde 1977',
    dek='En las primeras elecciones de la democracia podían votar 23,6 millones de personas residentes en España. En 1979, con la mayoría de edad rebajada a los 18 años, ya eran 26,7 millones. '
        'En 2023, 35,1 millones.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">{GANCHO_29N} Votarán más personas que nunca: el censo electoral no ha dejado de crecer desde 1977, salvo un pequeño retroceso en 2016.</p>
<p>En junio de 1977 había <strong>23,6 millones</strong> de electores residentes en España. En 2023 eran <strong>35,1 millones</strong>, un 49 % más. Son cifras sin el censo de los españoles que viven en el extranjero, que vota aparte y no se incluye en el mapa.</p>
{fig('serie', '11,5 millones de electores más', 'Electores residentes en España en cada elección general, en millones', 'Fuente: Ministerio del Interior. Sin el censo de residentes en el extranjero (CERA).')}
<h2>El salto de 1979: votar a los 18</h2>
<p>El mayor salto entre dos elecciones se produjo entre 1977 y 1979: <strong>3,2 millones de electores más</strong> en menos de dos años. En 1977 solo podían votar los mayores de 21 años. El <a href="{BOE_MAYORIA}">Real Decreto-ley 33/1978</a>, de 16 de noviembre, rebajó la mayoría de edad a los 18 años, y en las generales de marzo de 1979 votaron por primera vez los jóvenes de 18, 19 y 20 años.</p>
<h2>Después, un crecimiento lento</h2>
<p>Desde 1979, el censo ha crecido a un ritmo mucho más lento: unos 2 millones entre 1982 y 1986, 1,4 millones entre 1993 y 1996 y menos de medio millón entre cada par de elecciones desde 2004. Entre diciembre de 2015 y junio de 2016 bajó ligeramente, de 34,62 a 34,59 millones.</p>
<p>El crecimiento no ha sido igual en todas partes. En 6 de cada 10 municipios hay hoy menos electores que en 1977, mientras que en las coronas de las grandes ciudades y en la costa el censo se ha multiplicado.</p>
<h2>Lo que no está en el censo</h2>
<p>El censo electoral de las generales solo incluye a personas con nacionalidad española. Los extranjeros residentes no pueden votar en estas elecciones, aunque los ciudadanos de la UE y de algunos países con convenio sí pueden hacerlo en las municipales.</p>
""",
    js="""const C=D.censo.total;
barras('serie',EL.map((e,i)=>({l:e,v:C[i]/1e6,c:i==1?'var(--acc)':'#9a9a9a',lab:i==0||i==1||i==15,t:`${e}: <b>${miles(C[i])}</b> electores`})),{ticks:[0,10,20,30],fy:v=>v+' M',fl:v=>num(v),max:38,ml:40,aria:'Censo electoral en cada elección general'});
tabla('serie',['Elección','Electores'],EL.map((e,i)=>[e,miles(C[i])]));""",
    pie=PIE,
    descripcion='El censo de residentes en España pasó de 23,6 millones en 1977 a 35,1 en 2023, un 49 % más. El mayor salto, 3,2 millones, llegó en 1979, tras rebajarse la mayoría de edad a los 18 años en noviembre de 1978.',
    compara='El número de electores residentes en España en cada elección general de 1977 a 2023.',
    limites='Sin el censo de residentes en el extranjero (CERA). Los censos de los primeros años tenían errores; en algunas provincias incluían a emigrantes que vivían fuera. El crecimiento del censo mezcla población, edad de voto y cambios de nacionalidad.',
    fuentes=[INTERIOR_HIST,
             (BOE_MAYORIA, 'BOE, Real Decreto-ley 33/1978, de 16 de noviembre, sobre mayoría de edad (BOE núm. 275, de 17-11-1978)'),
             ('https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672', 'BOE, Ley Orgánica 5/1985, del Régimen Electoral General, artículos 2 y 176 (quién puede votar en generales y en municipales)')],
    enlaces=[('En 6 de cada 10 municipios hay hoy menos electores que en 1977', 'pueblos-menos-votantes-que-en-1977')],
))

# ---------------------------------------------------------------------------------------------------------------
P.append(dict(
    slug='europeas-solo-con-municipales', lugar='España', datos=['todas'],
    corto='Europeas y municipales',
    titulo='Las europeas solo superan el 60 % de participación cuando coinciden con las municipales',
    dek='En las 37 elecciones desde 1977, las europeas pasaron del 60 % tres veces: 1987, 1999 y 2019, las tres el mismo día que las municipales. '
        'Cuando se votaron sin ellas, se quedaron entre el 45,6 % y el 59,6 %.',
    cuerpo=lambda fig: f"""
<p style="margin-top:1.4rem">Desde 1977 se han celebrado en España 16 elecciones generales, 12 municipales y 9 europeas. Con las 37 en el mapa, se puede ver de un vistazo cuánto vota España en cada tipo de elección, y la diferencia es grande.</p>
{fig('todas', 'Las 37 elecciones de la democracia', 'Participación en cada elección general, municipal y europea, sin voto exterior', 'Fuente: Ministerio del Interior. El censo de municipales y europeas incluye a los ciudadanos de otros países de la UE inscritos para votar.', [('#e30613','Generales'),('#1d7f95','Municipales'),('#7e57c2','Europeas')])}
<h2>Generales, por encima; municipales, en medio</h2>
<p>Las generales nunca han bajado del <strong>67,6 %</strong> (marzo de 1979) y han llegado al 80,2 % (1982). Las municipales se mueven en una franja estrecha, entre el 62,6 % de 1979 y el 69,7 % de 1995.</p>
<h2>Las europeas dependen de con quién coincidan</h2>
<p>Las europeas son las que más varían, y el patrón es claro. Superaron el 60 % solo tres veces: en <strong>1987</strong> (68,9 %), en <strong>1999</strong> (64,4 %) y en <strong>2019</strong> (64,3 %). Las tres se celebraron el mismo día que las municipales.</p>
<p>Cuando no coincidieron con las municipales, no llegaron al 60 %. En 1994 se quedaron en el 59,6 %, coincidiendo con las andaluzas. En 1989, en el 54,9 %. Y cuando se votaron solas en las cuatro últimas ocasiones sin municipales, en 2004, 2009, 2014 y 2024, la participación estuvo entre el <strong>45,6 %</strong> y el <strong>49,2 %</strong>.</p>
{fig('eu', 'Con municipales y sin ellas', 'Participación en las nueve elecciones europeas', 'Fuente: Ministerio del Interior; fechas y coincidencias, Wikipedia.', [('#7e57c2','El mismo día que las municipales'),('#c4b5e6','Sin municipales')])}
<p>De 2019 a 2024 la participación en las europeas bajó 15 puntos, del 64,3 % al 49,2 %. En 2019 coincidieron el mismo día europeas, municipales y autonómicas en doce comunidades; en 2024 se votó solo para el Parlamento Europeo.</p>
<h2>Qué no dicen estos datos</h2>
<p>Con solo nueve europeas, la relación con las municipales es un patrón, no una ley. Que coincidan dos elecciones moviliza a quien va a votar en una de ellas, pero los datos no permiten saber cuántas personas votaron en las europeas solo porque ya estaban en el colegio.</p>
""",
    js="""const TD=D.todas;const COLT={generales:'#e30613',municipales:'#1d7f95',europeas:'#7e57c2'};
const ORD=TD.slice().sort((a,b)=>{const y=x=>x[0].replace(/^[EM]/,'').slice(0,4)+(x[0][0]=='E'?'b':x[0][0]=='M'?'a':'c')+x[0];return y(a)<y(b)?-1:1});
const lab=e=>e[0][0]=='E'?'Eur. '+e[0].slice(1):e[0][0]=='M'?'Mun. '+e[0].slice(1):'Gen. '+e[0].slice(0,4)+(e[0]=='2019_04'?'-A':e[0]=='2019_11'?'-N':'');
barras('todas',ORD.map(e=>({l:e[0][0]=='E'||e[0][0]=='M'?e[0].slice(1):e[0].slice(0,4),v:e[2],c:COLT[e[1]],t:`${lab(e)}: <b>${pct(e[2])}</b>`})),{ticks:[0,20,40,60,80],max:85,ml:36,aria:'Participación en las 37 elecciones'});
tabla('todas',['Elección','Tipo','Participación'],ORD.map(e=>[lab(e),e[1],pct(e[2])]));
const EU=TD.filter(e=>e[1]=='europeas');const CON=['E1987','E1999','E2019'];
barras('eu',EU.map(e=>({l:e[0].slice(1),v:e[2],c:CON.includes(e[0])?'#7e57c2':'#c4b5e6',lab:true,t:`Europeas ${e[0].slice(1)}: <b>${pct(e[2])}</b>${CON.includes(e[0])?'<br>El mismo día que las municipales':''}`})),{ticks:[0,20,40,60],max:75,ml:36,aria:'Participación en las elecciones europeas'});
tabla('eu',['Europeas','Participación','¿Con municipales?'],EU.map(e=>[e[0].slice(1),pct(e[2]),CON.includes(e[0])?'Sí':'No']));""",
    pie=PIE,
    descripcion='Las europeas pasaron del 60 % de participación solo en 1987, 1999 y 2019, las tres el mismo día que las municipales. Solas, en 2004, 2009, 2014 y 2024, se quedaron entre el 45,6 % y el 49,2 %.',
    compara='La participación en las 37 elecciones generales, municipales y europeas celebradas en España de 1977 a 2024.',
    limites='Participación sin voto exterior, algo por encima de la oficial. El censo de municipales y europeas incluye a ciudadanos de la UE inscritos. Con nueve europeas, la relación con las municipales es un patrón, no una regla.',
    fuentes=[INTERIOR_HIST,
             ('https://es.wikipedia.org/wiki/Elecciones_al_Parlamento_Europeo_de_1987_(Espa%C3%B1a)', 'Wikipedia, europeas de 1987: el 10-6-1987, a la vez que municipales y autonómicas'),
             ('https://es.wikipedia.org/wiki/Elecciones_al_Parlamento_Europeo_de_1994_(Espa%C3%B1a)', 'Wikipedia, europeas de 1994: el 12-6-1994, a la vez que las andaluzas'),
             ('https://es.wikipedia.org/wiki/Elecciones_al_Parlamento_Europeo_de_1999_(Espa%C3%B1a)', 'Wikipedia, europeas de 1999: el 13-6-1999, a la vez que municipales y autonómicas'),
             ('https://es.wikipedia.org/wiki/Elecciones_al_Parlamento_Europeo_en_Espa%C3%B1a', 'Wikipedia, «Elecciones al Parlamento Europeo en España»: 26-5-2019, europeas, municipales y autonómicas')],
    enlaces=[],
))

PIEZAS_HISTORIA = P
