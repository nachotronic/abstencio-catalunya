"""Cómo votar en las elecciones generales del 29N: horario, qué llevar y cómo saber tu colegio (pieza de servicio del 20-11-2026).

Fuentes:
- Electores: nota de prensa del INE del 9-10-2026 (EG2026), tabla por circunscripción, ya guardada en
  actualidad/src/resumenes/datos/generacion_2008.json (clave censo26: total, residentes en España, residentes en el extranjero).
- Horario, documentos, mesa, ayuda y cierre: LOREG, artículos 80, 84, 85, 86, 87 y 88. Senado: artículo 166.1.a.
- DNI caducado: Junta Electoral Central, acuerdo 785/1999, de 13 de mayo de 1999.
- Color de papeletas y sobres: Real Decreto 605/1999, artículo 4.2 y 4.5.
- Plazos de los residentes en el extranjero: calendario del INE (Oficina del Censo Electoral).
Uso, desde la raíz: python3 actualidad/src/resumenes/como_votar_29n.py
"""
import json
import sys

from comun import BASE, RAIZ, barras, figura, n, pieza

sys.path.insert(0, str(RAIZ / 'src'))
from territorios_rutas import PROV_NOMBRE  # noqa: E402

SLUG = 'como-votar-elecciones-generales-29n'
A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
INE_NOTA = 'https://www.ine.es/dyngs/Prensa/es/EG2026.htm'
INE_CAL = 'https://www.ine.es/dyngs/CEL/index.htm?cid=1702'
INE_SEDE = 'https://sede.ine.gob.es/'
LOREG = 'https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672'
L80 = LOREG + '#aochenta'
L84 = LOREG + '#aochentaycuatro'
L85 = LOREG + '#aochentaycinco'
L86 = LOREG + '#aochentayseis'
L87 = LOREG + '#aochentaysiete'
L88 = LOREG + '#aochentayocho'
L166 = LOREG + '#acientosesentayseis'
L96 = LOREG + '#anoventayseis'
PUBLICO = 'https://www.publico.es/sociedad/tengo-votar-elecciones-generales-29n-consultar-colegio-mesa-electoral.html'
JEC = ('https://www.juntaelectoralcentral.es/cs/jec/doctrina/acuerdos?anyosesion=1999&idacuerdoinstruccion=55109'
       '&idsesion=493&template=Doctrina%2FJEC_Detalle')
RD605 = 'https://www.boe.es/buscar/act.php?id=BOE-A-1999-8583'
GUIA = f'{BASE}elecciones/votar-29n/'
TARJETA = f'{BASE}elecciones/tarjeta-censal-29n/'
LISTAS = f'{BASE}listas-electorales-29n/'

# ---------- Electores (INE, 9-10-2026) ----------
CEN = json.load(open(RAIZ / 'actualidad/src/resumenes/datos/generacion_2008.json'))['censo26']
TOTAL, CER, CERA = CEN['Total general']
assert (TOTAL, CER, CERA) == (38728356, 35958711, 2769645)
PRIMEROS = 1615127          # nota de prensa del INE: residentes en España que votan por primera vez en unas generales
PROV = {c: v for c, v in CEN.items() if c.isdigit()}
assert len(PROV) == 52 and sum(v[0] for v in PROV.values()) == TOTAL and sum(v[2] for v in PROV.values()) == CERA
PCT_CERA = 100 * CERA / TOTAL
CORTO = {'Santa Cruz de Tenerife': 'S. C. de Tenerife', 'Alicante/Alacant': 'Alicante', 'Valencia/València': 'Valencia',
         'Castellón/Castelló': 'Castellón', 'Araba/Álava': 'Álava', 'Illes Balears': 'Baleares', 'Balears, Illes': 'Baleares'}
NOM = dict(PROV_NOMBRE)
nom = lambda c: CORTO.get(NOM[c], NOM[c])
SH = {c: 100 * v[2] / v[0] for c, v in PROV.items()}
ORD = sorted(PROV, key=lambda c: -SH[c])
TOP = ORD[:12]
assert ORD[0] == '32' and ORD[1] == '27'           # Ourense y Lugo
OUR, LUG = SH['32'], SH['27']
GAL = [c for c in ('15', '27', '32', '36')]
assert sorted(ORD[:4]) == sorted(GAL)
MAD = PROV['28']
assert max(PROV, key=lambda c: PROV[c][2]) == '28'
MENOS = ORD[-1]
UNO_DE = round(TOTAL / CERA)
assert UNO_DE == 14

# ---------- Senado: cuántos nombres se pueden marcar (LOREG 166.1.a) ----------
MARCAS = [('Las 47 provincias de la Península', '3'),
          ('Mallorca, Gran Canaria, Tenerife, Ceuta y Melilla', '2'),
          ('Menorca, Ibiza-Formentera, Fuerteventura, Lanzarote, La Palma, La Gomera y El Hierro', '1')]

g_cera = figura(
    f'En Ourense, casi uno de cada tres electores vive fuera de España',
    f'Porcentaje del censo de las elecciones generales del 29N que reside en el extranjero, en las 12 circunscripciones donde es mayor. En toda España, el {p(PCT_CERA)} %',
    barras([(nom(c), SH[c], 'var(--muted)', f'{p(SH[c])} %') for c in TOP], SH[TOP[0]] * 1.12,
           'Electores residentes en el extranjero por circunscripción', W=400, ml=150, fmt=lambda v: f'{p(v)} %',
           linea=(PCT_CERA, 'España'), separar=True),
    f'Fuente: <a href="{INE_NOTA}">INE, Oficina del Censo Electoral</a>, censo electoral para las elecciones generales del 29 de noviembre de 2026 (nota del 9 de octubre). Cálculo propio.',
    None,
    (['Circunscripción', 'Electores', 'Residentes en España', 'Residentes en el extranjero', '% en el extranjero'],
     [[nom(c), n(PROV[c][0]), n(PROV[c][1]), n(PROV[c][2]), p(SH[c])] for c in ORD]))

cuerpo = f'''
<p data-tipo="contexto">Las elecciones generales del 29N se votan el domingo 29 de noviembre de 2026. Los colegios abren a las 9.00 y la votación sigue sin interrupción hasta las 20.00, según el <a href="{L84}">artículo 84 de la ley electoral</a> (LOREG). Antes, a las 8.00, se reúnen el presidente y los dos vocales de cada mesa para constituirla (<a href="{L80}">artículo 80</a>). Están llamados a votar {n(TOTAL)} electores: {n(CER)} viven en España y {n(CERA)} en el extranjero, según el <a href="{INE_NOTA}">INE</a>. De los residentes en España, {n(PRIMEROS)} votarán por primera vez en unas generales, porque han cumplido 18 años desde las de julio de 2023 (los más jóvenes son {L("generacion-2008-primer-voto-29n", "la generación de 2008")}).</p>
<h2>Cómo saber tu colegio y tu mesa</h2>
<p data-tipo="dato">Viene en la tarjeta censal que la Oficina del Censo Electoral envía a cada elector del 2 al 10 de noviembre, según el <a href="{INE_CAL}">calendario del INE</a>: el colegio, la dirección, la sección y la mesa. Si no la tienes, se consulta en la <a href="{INE_SEDE}">sede electrónica del INE</a>. Cada elector solo puede votar en la sección y la mesa que le corresponden (<a href="{L86}">artículo 86</a>); el mismo domingo, cada colegio tiene un callejero con la mesa que corresponde a cada calle, según <a href="{PUBLICO}">Público</a>. Qué trae la tarjeta y cómo votó tu sección en 2023, en <a href="{TARJETA}">la tarjeta censal del 29N</a>.</p>
<h2>Qué llevar</h2>
<p data-tipo="dato">El DNI, el pasaporte o el permiso de conducir, siempre que lleven tu fotografía, en original (<a href="{L85}">artículo 85</a>). La tarjeta de residencia que también cita la ley es para los extranjeros que votan en municipales y europeas: en las generales solo votan los españoles. Un documento caducado sirve: la <a href="{JEC}">Junta Electoral Central</a> acordó en 1999 que «debe admitirse el documento identificativo aunque el mismo esté caducado», porque lo que se comprueba es la identidad. La tarjeta censal no hace falta para votar.</p>
<h2>Las dos papeletas</h2>
<p data-tipo="dato">Se votan a la vez el Congreso y el Senado, con dos papeletas, dos sobres y dos urnas. La del Congreso es blanca y lleva la lista cerrada de un partido: se mete en el sobre tal cual, porque tachar, añadir o cambiar el orden de los nombres anula el voto (<a href="{L96}">artículo 96</a>). La del Senado es de color sepia, según el <a href="{RD605}">Real Decreto 605/1999</a>, y es una sola para todos los partidos: hay que marcar con una cruz a los candidatos que quieras, de cualquier partido. Si se marcan más de los permitidos, el voto al Senado es nulo; si no se marca ninguno, cuenta como voto en blanco (<a href="{L96}">artículo 96</a>). Cada sobre es del mismo color que su papeleta. Quién va en cada lista, en <a href="{LISTAS}">las listas electorales del 29N</a>.</p>
<div class="tbl"><table><thead><tr><th>Circunscripción al Senado</th><th class="n">Nombres que se pueden marcar como máximo</th></tr></thead><tbody>
{"".join(f'<tr><td>{a}</td><td class="n">{b}</td></tr>' for a, b in MARCAS)}
</tbody></table></div>
<p data-tipo="contexto">Fuente: <a href="{L166}">artículo 166 de la LOREG</a>. Cómo se repartieron los senadores en 2023, en {L("senado-29n", "esta pieza sobre el Senado")}.</p>
<h2>En la mesa</h2>
<p data-tipo="dato">Se dice el nombre al presidente, los vocales comprueban que estás en la lista del censo y miran el documento, y le entregas los sobres cerrados; el presidente dice en voz alta tu nombre y «Vota», y tú mismo los metes en las urnas (<a href="{L86}">artículo 86</a>). Las papeletas se pueden elegir en la cabina o llevarlas de casa, siempre en el sobre oficial: el voto en un sobre o una papeleta que no sean del modelo oficial es nulo. Quien no sepa leer o tenga una discapacidad que le impida elegir la papeleta o entregarla puede ir con una persona de su confianza (<a href="{L87}">artículo 87</a>), que la ley completa con un procedimiento para personas ciegas o con discapacidad visual.</p>
<p data-tipo="dato">Si llegas justo a las 20.00, no te quedas fuera: el presidente anuncia el cierre y deja votar a los electores que estén en el local o en el acceso que todavía no lo hayan hecho, y a nadie más (<a href="{L88}">artículo 88</a>). Quien pidió el voto por correo y se lo aceptaron ya no puede votar en persona ({L("voto-correo-29n", "el voto por correo, provincia a provincia")}).</p>
<h2>Los que votan desde fuera</h2>
<p data-tipo="dato">Uno de cada {UNO_DE} electores de las generales vive en el extranjero, y no vota en un colegio en España: según el <a href="{INE_CAL}">calendario del INE</a>, envía el voto por correo al consulado hasta el 24 de noviembre o lo deposita en la urna del consulado del 21 al 26. Su peso cambia mucho de una provincia a otra. En Ourense es el {p(OUR)} % del censo, y en Lugo, el {p(LUG)} %; las cuatro primeras son las provincias gallegas. Madrid es la que más tiene en número, {n(MAD[2])}, pero son el {p(SH["28"])} % de sus electores. El porcentaje más bajo es el de {nom(MENOS)}, con el {p(SH[MENOS])} %.</p>
{g_cera}
<p data-tipo="contexto">Los permisos si trabajas ese domingo, el voto por correo paso a paso y qué hacer si te toca mesa están en <a href="{GUIA}">la guía de dónde y cómo votar el 29N</a> y en {L("me-ha-tocado-mesa-electoral-29n", "esta pieza sobre las mesas electorales")}. Desde las 21.00, <a href="{BASE}">el mapa de las elecciones generales</a> irá mostrando el recuento.</p>
'''

preguntas = [
    ('¿A qué hora abren y cierran los colegios electorales el 29N?',
     f'La votación empieza a las 9.00 y sigue sin interrupción hasta las 20.00 (<a href="{L84}">artículo 84 de la LOREG</a>). Quien esté en el local o en el acceso a las 20.00 y no haya votado todavía puede votar.'),
    ('¿Qué documento hay que llevar para votar en las elecciones generales?',
     f'El DNI, el pasaporte o el permiso de conducir, con fotografía y en original. Según la <a href="{JEC}">Junta Electoral Central</a>, se admite aunque esté caducado. La tarjeta censal no es obligatoria.'),
    ('¿Cómo sé dónde me toca votar?',
     f'En la tarjeta censal, que trae el colegio y la mesa, o en la <a href="{INE_SEDE}">sede electrónica del INE</a>. Más detalles en <a href="{TARJETA}">la tarjeta censal del 29N</a>.'),
    ('¿A cuántos candidatos puedo marcar en la papeleta del Senado?',
     f'A tres como máximo en las circunscripciones provinciales, a dos en Mallorca, Gran Canaria, Tenerife, Ceuta y Melilla, y a uno en el resto de islas (<a href="{L166}">artículo 166 de la LOREG</a>). Si se marcan más, el voto al Senado es nulo.'),
    ('¿Cuántos electores hay en las elecciones generales del 29N?',
     f'{n(TOTAL)}: {n(CER)} residentes en España y {n(CERA)} en el extranjero, según el <a href="{INE_NOTA}">INE</a>.'),
]
enlaces = (f'<a href="{GUIA}">Dónde y cómo votar el 29N</a> · <a href="{TARJETA}">Tarjeta censal del 29N</a> · '
           f'{L("voto-correo-29n", "El voto por correo")} · <a href="{LISTAS}">Listas electorales del 29N</a>')
foot = ('Datos: INE, Oficina del Censo Electoral, censo electoral de las generales del 29 de noviembre de 2026 por circunscripción (nota de prensa del 9 de octubre); '
        'Ley Orgánica del Régimen Electoral General; Junta Electoral Central, acuerdo de 13 de mayo de 1999; Real Decreto 605/1999. '
        'Cálculo: actualidad/src/resumenes/como_votar_29n.py.')

DATOS = {'TOTAL': TOTAL, 'CER': CER, 'CERA': CERA, 'PRIMEROS': PRIMEROS, 'PCT_CERA': round(PCT_CERA, 2),
         'PROV': {nom(c): [*PROV[c], round(SH[c], 2)] for c in ORD}}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'Cómo votar el 29N',
      'Cómo votar en las elecciones generales del 29N: horario, qué llevar y cómo saber tu colegio',
      f'Los colegios abren el domingo 29 de noviembre de 9.00 a 20.00. Hace falta el DNI, el pasaporte o el carné de conducir, aunque estén caducados; '
      f'la tarjeta censal, no. Están llamados a votar {n(TOTAL)} electores, {n(PRIMEROS)} por primera vez en unas generales.',
      '20 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('TOTAL', TOTAL, 'CERA', CERA, p(PCT_CERA), 'UNO_DE', UNO_DE, [(nom(c), round(SH[c], 1)) for c in TOP], nom(MENOS), round(SH[MENOS], 1), 'MAD', MAD)
