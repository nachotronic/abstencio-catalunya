"""Nombre real de cada candidatura en cada municipio, para la ficha del mapa.

El mapa agrupa las candidaturas en familias (partidos.py) y las pinta con el color de la familia. Pero en Cataluña el
PSOE se presenta como PSC, en Galicia como PSdeG, en Navarra el PP iba con UPN o en Navarra Suma, y el espacio de
Sumar ha tenido una marca en cada sitio (En Comú Podem, Compromís, En Marea...). Este script saca, por elección y
municipio, cómo se llamaba la candidatura de cada familia, para que la ficha diga «PSC» y no «PSOE».

Salida: data/nombres/<elección>.json, que la pieza carga al elegir esa elección:
  {"n": ["", "PSC", ...],                 nombres (el 0 es «el de la familia»)
   "p": {"PSOE": {"08": 1, ...}},         nombre más votado de la familia en cada provincia
   "m": {"PSOE": {"08019": 1, ...}}}      municipios donde no coincide con el de su provincia
Si en un municipio una familia junta dos candidaturas con voto apreciable (UPN y PP en Pamplona en 2023, Podemos e
IU en 2015), salen las dos: «UPN + PP».

Uso:  python3 nombres.py [--out DIR]     (por defecto web/data/nombres; lee las mismas fuentes que construir.py)
"""
import glob, json, os, re, sys
import pandas as pd
from partidos import familia, FAMILIAS

AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get('GENERALES_CACHE', os.path.expanduser('~/.cache/generales'))
PS = os.path.join(CACHE, 'pollspaindata', 'inst', 'extdata')
EXTRA = os.environ.get('GENERALES_EXTRA', os.path.join(AQUI, 'datos', 'extra'))   # en el repositorio no está: apuntar a la carpeta del proyecto
GENERALES = ['2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
FUSIONES = {'15026': '15902', '15063': '15902', '36011': '36902', '36012': '36902'}   # como en construir.py
MINIMO = .10      # una segunda candidatura de la familia sale en el nombre si tiene al menos el 10 % del voto de la familia

# Nombre corto de cada candidatura. Se prueba con las siglas y el nombre completo (en mayúsculas). None = el de la
# familia («PSOE», «PP»...), que la ficha ya muestra. Orden: de lo más concreto a lo más general.
_ETIQ = [
    # PSOE y sus federaciones
    ('PSOE', r"^PSC\b|^PSC-|PARTIT DELS SOCIALISTES DE CATALUNYA", 'PSC'),
    ('PSOE', r"^PS ?D?E?G|SOCIALISTAS? DE GALICIA", 'PSdeG'),
    ('PSOE', r"^PSE\b|^PSE-|PARTIDO SOCIALISTA DE EUSKADI", 'PSE-EE'),
    ('PSOE', r"^PSIB|SOCIALISTA DE (LES ILLES|ISLAS) BALEARS?", 'PSIB'),
    ('PSOE', r"^PSN\b|^PSN-|SOCIALISTAS? DE NAVARRA", 'PSN'),
    ('PSOE', r"^PSPV|SOCIALISTA DEL PA[IÍ]S VALENCI|SOCIALISTES (DEL PA[IÍ]S )?VALENCI", 'PSPV'),
    ('PSOE', r"^PSA-PSOE|^PSOE-A\b|^PSOE DE A|OBRERO ESPA[NÑ]OL DE ANDALUC", 'PSOE-A'),
    ('PSOE', r"^PSOE-NCA|PSOE-NUEVA CANARIAS", 'PSOE-NC'),
    ('PSOE', r"^PSOE-PROG|OBRERO ESPA[NÑ]OL - PROGRESISTAS", 'PSOE-Progresistas'),
    ('PSOE', r"^PSV|^P\.S\.V\.|PARTI[DT]O? SOCIALISTA VALENCI", 'PSPV'),
    ('PSOE', r".", None),
    # PP y sus coaliciones, AP
    ('PP', r"^NA\+|NAVARRA SUMA", 'Navarra Suma'),
    ('PP', r"^UPN-PP|EN COALICION CON EL PP", 'UPN-PP'),
    ('PP', r"^UPN|^U\.P\.N|UNI[OÓ]N DEL PUEBLO NAVARRO", 'UPN'),
    ('PP', r"^PP-FORO|^PP-FAC", 'PP-Foro'),
    ('PP', r"^PP-PAR|PARTIDO ARAGON[EÉ]S", 'PP-PAR'),
    ('PP', r"^P\.?P\.?-E\.?U|EXTREMADURA UNIDA", 'PP-EU'),
    ('PP', r"^PP-C DE G|CENTRISTAS DE GALICIA", 'PP-CG'),
    ('PP', r"^CD$|^COALICI[OÓ]N DEMOCR[AÁ]TICA$", 'Coalición Democrática'),
    ('PP', r"^AP-PDP-PL|^COALICI[OÓ]N POPULAR", 'Coalición Popular'),
    ('PP', r"^AP-PDP|ALIANZA POP.*DEMOC", 'AP-PDP'),
    ('PP', r"^AP$|ALIANZA POPULAR", 'AP'),
    ('PP', r"^CC-AP|CONVIVENCIA CATALANA", 'Convivència Catalana'),
    ('PP', r".", None),
    # Sumar / Podemos / IU
    ('SUMAR', r"^SUMAR ?- ?ECP|^COMUNS SUMAR", 'Sumar-ECP'),
    ('SUMAR', r"COMPROM[IÍ]S ?- ?SUMAR|^SUMAR ?- ?COMPROM", 'Compromís-Sumar'),
    ('SUMAR', r"^M[EÉ]S PER MALLORCA.*SUMAR|^SUMAR M[EÉ]S", 'Sumar Més'),
    ('SUMAR', r"^SUMAR\b", 'Sumar'),
    ('SUMAR', r"^ECP|EN COM[UÚ] PODEM|^EN COM[UÚ]$|^\"?EN COM[UÚ] PODEM", 'En Comú Podem'),
    ('SUMAR', r"BARCELONA EN COM[UÚ]", 'Barcelona en Comú'),
    ('SUMAR', r"COMPROM[IÍ]S-PODEMOS|^PODEMOS-COM|^PODEMOS - C\b|^A LA VALENCIANA", 'Compromís-Podemos'),
    ('SUMAR', r"^PODEMOS-EN\b|EN MAREA", 'En Marea'),
    ('SUMAR', r"MAREA ATL[AÁ]NTICA", 'Marea Atlántica'),
    ('SUMAR', r"AHORA ?MADRID", 'Ahora Madrid'),
    ('SUMAR', r"M[AÁ]S MADRID", 'Más Madrid'),
    ('SUMAR', r"^M\.? ?PA[IÍ]S|M[AÁ]S PA[IÍ]S", 'Más País'),
    ('SUMAR', r"^M[EÉ]S COMPROM|COMPROM[IÍÌ]S|^C\.M\. COMPROM|^PRIMAVERA EUROPEA|^CPE$", 'Compromís'),
    ('SUMAR', r"UNID[AO]S PODEMOS|UNIDES PODEM|UNITS PODEM|XUN[IÍ]ES PODEMOS|^PODEMOS-I|^PODEMOS/AHAL DUGU-IU|^PODEMOS-EU|^PODEMOS-EUPV|^CEC-PODEMOS", 'Unidas Podemos'),
    ('SUMAR', r"EN COM[UÚ]N-UNIDAS PODEMOS", 'En Común-Unidas Podemos'),
    ('SUMAR', r"^PODEMOS|PODEMOS|AHAL DUGU|PODEM\b", 'Podemos'),
    ('SUMAR', r"^ICV|^IC-?V|^IC-EV|^IPC-VERDES|INICIATIVA PER CATALUNYA", 'ICV'),
    ('SUMAR', r"^IC$", 'IC'),
    ('SUMAR', r"^EUIA$|ESQUERRA UNIDA I ALTERNATIVA", 'EUiA'),
    ('SUMAR', r"^PSUC|PARTIT SOCIALISTA? UNIFICAT", 'PSUC'),
    ('SUMAR', r"UNI[OÓ] DE L.ESQUERRA CATALANA", 'Unió de l\'Esquerra Catalana'),
    ('SUMAR', r"^PCE|^PCA-PCE|^PCC-PCE|PARTIDO COMUNISTA", 'PCE'),
    ('SUMAR', r"ESQUERRA UNIDA DEL PA[IÍ]S VALENCI|^EUPV|^EU-PV|^ENTESA", 'EUPV'),
    ('SUMAR', r"^EB\b|^EB-|EZKER BATUA", 'EB-IU'),
    ('SUMAR', r"ESQUERDA UNIDA|^EU-IU|^EU-V|^EU-EG|^UG-EU|^EU-UG", 'Esquerda Unida'),
    ('SUMAR', r"^AGE$|ALTERNATIVA GALEGA", 'AGE'),
    ('SUMAR', r"UNIDAD POPULAR|^IU-UPEC|^UPEC|^IU-B-UPEC|^IU-CHA-UPEC|^UP-UPEC|^UP: |^UPB: |^IULV-CA, ?UP", 'Unidad Popular'),
    ('SUMAR', r"^IULV|^IU-LV-CA|^IU-CA|CONVOCATORIA POR ANDALUC", 'IULV-CA'),
    ('SUMAR', r"^I\.?U\.?|IZQUIERDA UNIDA|IZQUIERDA PLURAL|^IUC|^I-E$|IZQUIERDA - EZKERRA", 'IU'),
    ('SUMAR', r".", '*'),
    # Junts / CiU
    ('JUNTS', r"TRIAS ?(PER|X) ?BARCELONA|^TRIASXBCN", 'Trias per Barcelona'),
    ('JUNTS', r"^CIU$|CONVERG[EÈ]NCIA I UNI[OÓ]", 'CiU'),
    ('JUNTS', r"^DL$|DEMOCR[AÀ]CIA I LLIBERTAT", 'DL'),
    ('JUNTS', r"^CDC$|CONVERG[EÈ]NCIA DEMOCR[AÀ]TICA", 'CDC'),
    ('JUNTS', r"^PDPC$|PACTE DEMOCR[AÀ]TIC", 'Pacte Democràtic'),
    ('JUNTS', r"^JXCAT|^JUNTS|JUNTS PER|LLIURES PER EUROPA|^CM$|-CM$|COMPROM[IÍ]S MUNICIPAL", 'Junts'),
    ('JUNTS', r".", '*'),
    # resto: el nombre de la familia salvo coaliciones con otra marca
    ('ERC', r"^EC-FED|ESQUERRA DE CATALU", 'Esquerra de Catalunya'),
    ('ERC', r"^ERPV|REPUBLICANA DEL PA[IÍ]S VALENCI", 'ERPV'),
    ('ERC', r"ERC|ESQUERRA REPUBLICANA", None),
    ('ERC', r".", '*'),
    ('PNV', r"EAJ-PNV/EA|EUSKO ALKARTASUNA", 'PNV-EA'),
    ('PNV', r".", None),
    ('BILDU', r"^HB$|^H\.B\.$|HERRI BATASUNA", 'HB'),
    ('BILDU', r"^EH$|EUSKAL HERRITARROK", 'EH'),
    ('BILDU', r"^AMAIUR", 'Amaiur'),
    ('BILDU', r"^BILDU\b", 'Bildu'),
    ('BILDU', r"BILDU", None),
    ('BILDU', r".", '*'),
    ('BNG', r"^BN-?PG|BLOQUE NACIONAL.?POPULAR GAL", 'BN-PG'),
    ('BNG', r"^N[OÓ]S$|N[OÓ]S-CANDIDATURA", 'Nós'),
    ('BNG', r"^B\.?N\.?G|BLOQUE NACIONALISTA GAL", None),
    ('BNG', r".", '*'),
    ('CC', r"NUEVA CANARIAS", 'CC-NC'),
    ('CC', r"PARTIDO NACIONALISTA CANARIO|-PNC", 'CC-PNC'),
    ('CC', r"^C\.?C\.?A?\b|COALICI[OÓ]N CANARIA", None),
    ('CC', r".", '*'),
    ('CDS', r"^FORO Y CDS|COALICION FORO", 'Foro-CDS'),
    ('CDS', r"^UC-CDS|UNION CENTRISTA", 'UC-CDS'),
    ('CDS', r".", None),
    ('UCD', r"^CC-UCD|CENTRISTES DE CATALUNYA", 'Centristes de Catalunya'),
    ('UCD', r".", None),
]
_ETIQ = [(f, re.compile(p), e) for f, p, e in _ETIQ]
NOMBRE_FAM = {c: n for c, n, _ in FAMILIAS}


_MINUS = {'de', 'del', 'la', 'las', 'el', 'los', 'en', 'y', 'i', 'e', 'per', 'pel', 'els', 'les', 'por', 'para', 'con',
          'amb', 'a', 'o', 'da', 'do', 'das', 'dos', 'al'}


def bonito(siglas, nombre):
    """Listas locales sin regla propia (Zaragoza en Común, Enlairem Deltebre...): el nombre completo en minúsculas
    con mayúscula inicial si es corto; si no, las siglas tal cual."""
    n = re.sub(r'\s+', ' ', str(nombre or '').strip(' "'))
    if not n or len(n) > 40:
        return re.sub(r'\s+', ' ', str(siglas or '').strip()) or None
    sig = set(re.findall(r"[A-ZÀ-Ý+]{2,}", str(siglas or '').upper()))
    pal = []
    for k, w in enumerate(n.split(' ')):
        lw = w.lower()
        if k and lw in _MINUS:
            pal.append(lw)
        elif w.isupper() and (w in sig and len(w) <= 4 or not re.search(r'[AEIOUÁÉÍÓÚÀÈÒ]', w)):
            pal.append(w)                    # siglas dentro del nombre (PSOE, ZGZ)
        else:
            t = re.sub(r"^\w|(?<=[-/(])\w|(?<=\b[ld]['’])\w", lambda m: m.group(0).upper(), lw)
            pal.append(t[0].lower() + t[1:] if k and re.match(r"[ld]['’]", lw) else t)    # d'Aro, l'Escala
    return ' '.join(pal)


def etiqueta(siglas, nombre, fam):
    """Nombre corto de la candidatura, o None si es el de su familia."""
    s, n = str(siglas or '').strip().upper(), str(nombre or '').strip().upper()
    for f, pat, e in _ETIQ:
        if f == fam and (pat.search(s) or pat.search(n)):
            return bonito(siglas, nombre) if e == '*' else e
    return None


def candidaturas(y):
    """mun_code, siglas, nombre, votos de una elección."""
    def par(src, k):
        c = pd.read_parquet(f'{src}/raw_candidacies_{k}.parquet')
        v = pd.read_parquet(f'{src}/raw_candidacies_poll_{k}.parquet', columns=['cod_INE_prov', 'cod_INE_mun', 'id_candidacies', 'ballots'])
        v = v[v.cod_INE_mun != '999']                    # CERA fuera, como en el mapa
        v['mun_code'] = v.cod_INE_prov + v.cod_INE_mun
        g = v.groupby(['mun_code', 'id_candidacies'], as_index=False).ballots.sum()
        g = g.merge(c[['id_candidacies', 'abbrev_candidacies', 'name_candidacies']], on='id_candidacies')
        return pd.DataFrame({'mun_code': g.mun_code, 'siglas': g.abbrev_candidacies, 'nombre': g.name_candidacies, 'votos': g.ballots})
    if y in GENERALES and not os.path.exists(f'{EXTRA}/raw_candidacies_poll_congress_{y}.parquet'):
        return par(PS, 'congress_' + y)
    if os.path.exists(f'{EXTRA}/raw_candidacies_poll_{y}.parquet'):
        return par(EXTRA, y)
    d = pd.read_csv(f'{EXTRA}/{y}_municipios.csv', dtype={'mun_code': str, 'siglas': str, 'nombre': str}, keep_default_na=False)
    return d[['mun_code', 'siglas', 'nombre', 'votos']]


def una(y):
    d = candidaturas(y)
    d['mun_code'] = d.mun_code.str.zfill(5).replace(FUSIONES)
    claves = d[['siglas', 'nombre']].drop_duplicates()
    fam = {(s, n): familia(s, n) for s, n in claves.itertuples(index=False)}
    d['fam'] = [fam[(s, n)] for s, n in zip(d.siglas, d.nombre)]
    d = d[(d.fam != 'OTROS') & (d.votos > 0)]
    eti = {(s, n, f): etiqueta(s, n, f) or '' for s, n, f in d[['siglas', 'nombre', 'fam']].drop_duplicates().itertuples(index=False)}
    d['eti'] = [eti[k] for k in zip(d.siglas, d.nombre, d.fam)]
    g = d.groupby(['fam', 'mun_code', 'eti'], as_index=False).votos.sum()
    # nombre en cada municipio: la candidatura más votada de la familia, más la segunda si pasa del MINIMO
    nom = {}
    for (f, m), x in g.groupby(['fam', 'mun_code']):
        x = x.sort_values('votos', ascending=False)
        x = x[x.votos >= MINIMO * x.votos.sum()].head(2)
        e = [v or NOMBRE_FAM[f] for v in x.eti]
        nom[(f, m)] = '' if all(v == '' for v in x.eti) else ' + '.join(e)
    s = pd.Series(nom)
    s.index.names = ['fam', 'mun']
    s = s.reset_index(name='eti')
    s['prov'] = s.mun.str[:2]
    tot = g.groupby(['fam', 'mun_code']).votos.sum()
    s['votos'] = [tot[(f, m)] for f, m in zip(s.fam, s.mun)]
    if (s.eti == '').all():
        return None
    nombres = [''] + sorted(set(s.eti) - {''})
    ix = {v: k for k, v in enumerate(nombres)}
    out = {'n': nombres, 'p': {}, 'm': {}}
    for f, x in s.groupby('fam'):
        # por provincia, el nombre con más votos; en los municipios, solo lo que difiere de él
        pv = x.groupby(['prov', 'eti']).votos.sum().reset_index().sort_values('votos', ascending=False).drop_duplicates('prov')
        dp = dict(zip(pv.prov, pv.eti))
        p = {k: ix[v] for k, v in dp.items() if v}
        m = {mu: ix[e] for mu, e, pr in zip(x.mun, x.eti, x.prov) if e != dp[pr]}
        if p:
            out['p'][f] = dict(sorted(p.items()))
        if m:
            out['m'][f] = dict(sorted(m.items()))
    return out


def elecciones():
    ys = list(GENERALES)
    ys += sorted(os.path.basename(f)[len('raw_candidacies_poll_'):-8] for f in glob.glob(f'{EXTRA}/raw_candidacies_poll_[ME]*.parquet'))
    ys += sorted(os.path.basename(f).split('_municipios')[0] for f in glob.glob(f'{EXTRA}/*_municipios.csv'))
    return list(dict.fromkeys(ys))


if __name__ == '__main__':
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.join(AQUI, 'web', 'data', 'nombres')
    os.makedirs(out, exist_ok=True)
    hechas = []
    for y in elecciones():
        r = una(y)
        if r is None:
            continue
        with open(os.path.join(out, y + '.json'), 'w') as fh:
            json.dump(r, fh, ensure_ascii=False, separators=(',', ':'))
        hechas.append(y)
        print(y, len(r['n']) - 1, 'nombres,', sum(len(v) for v in r['m'].values()), 'municipios con nombre propio')
    with open(os.path.join(out, 'indice.json'), 'w') as fh:
        json.dump(hechas, fh)
