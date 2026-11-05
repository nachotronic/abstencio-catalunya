#!/usr/bin/env python3
"""Publica en redes sociales las piezas nuevas de Actualidad y la cola programada (redes/cola.json).

Lo lanza .github/workflows/redes.yml cada 15 minutos y en cada push a main. Normas:
- Solo publica en las redes que estén en la variable del repo REDES_ACTIVAS (p. ej. «bluesky,mastodon,telegram,x»)
  y que tengan sus secretos. Sin esa variable no publica nada: solo dice qué habría publicado.
- REDES_PAUSA=1 (variable del repo) lo para todo al instante.
- Piezas: lee https://mapaelectoral.es/actualidad/feed.xml, y para cada pieza de las últimas 36 horas que aún no esté
  en el registro comprueba que la página está publicada (200) y que su imagen de compartir existe. Publica SOLO el
  titular y la entradilla de la propia pieza (ya revisados antes de fusionar) y el enlace: no redacta nada nuevo.
  Una pieza con <meta name="redes" content="no"> no se anuncia nunca.
- La primera vez que se activa una red, se apuntan como ya publicadas todas las piezas que hay en el feed, para no
  soltar de golpe el archivo entero.
- Cola: redes/cola.json, entradas con «cuando» (hora de Madrid). Se publican cuando llega su hora y hasta 6 horas
  después; pasado ese plazo se dan por caducadas y no salen.
- El registro de lo publicado vive en la rama redes-registro (registro.json), fuera de main.
"""
import argparse, datetime, html, json, os, re, sys, time, urllib.parse
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

import requests

MADRID = ZoneInfo('Europe/Madrid')
FEED = 'https://mapaelectoral.es/actualidad/feed.xml'
UA = {'User-Agent': 'mapaelectoral-redes/1.0 (+https://mapaelectoral.es/)'}
VENTANA_PIEZAS = datetime.timedelta(hours=36)
VENTANA_COLA = datetime.timedelta(hours=6)
REDES = ('x', 'bluesky', 'mastodon', 'telegram', 'threads', 'instagram')
URL_X = 23  # X cuenta cualquier enlace como 23 caracteres


def ahora():
    return datetime.datetime.now(datetime.timezone.utc)


def recortar(texto, maximo):
    texto = texto.strip()
    if len(texto) <= maximo:
        return texto
    corte = texto[:maximo - 1].rsplit(' ', 1)[0].rstrip(',;:')
    return corte + '…'


def get(url, **kw):
    return requests.get(url, headers=UA, timeout=30, **kw)


# ---------------------------------------------------------------- fuentes

def piezas_del_feed():
    r = get(FEED)
    r.raise_for_status()
    raiz = ET.fromstring(r.content)
    piezas = []
    for item in raiz.iter('item'):
        fecha = datetime.datetime.strptime(item.findtext('pubDate'), '%a, %d %b %Y %H:%M:%S %z')
        piezas.append({'id': item.findtext('guid').strip(), 'enlace': item.findtext('link').strip(),
                       'titulo': html.unescape(item.findtext('title') or '').strip(),
                       'entradilla': html.unescape(item.findtext('description') or '').strip(), 'fecha': fecha})
    return piezas


def meta(pagina, nombre):
    m = re.search(r'<meta[^>]+(?:property|name)="%s"[^>]+content="([^"]*)"' % re.escape(nombre), pagina)
    return html.unescape(m.group(1)) if m else None


def comprobar_pieza(p):
    """Devuelve (lista, motivo). Solo se anuncia lo que está publicado y entero."""
    r = get(p['enlace'])
    if r.status_code != 200:
        return False, f'la página da {r.status_code}'
    pagina = r.text
    if (meta(pagina, 'redes') or '').lower() == 'no':
        return False, 'marcada con <meta name="redes" content="no">'
    if 'noindex' in (meta(pagina, 'robots') or ''):
        return False, 'la página es noindex'
    p['titulo'] = meta(pagina, 'og:title') or p['titulo']
    p['entradilla'] = meta(pagina, 'og:description') or p['entradilla']
    p['imagen'] = meta(pagina, 'og:image')
    if not p['imagen']:
        return False, 'sin og:image'
    ri = get(p['imagen'])
    if ri.status_code != 200 or not ri.headers.get('content-type', '').startswith('image/'):
        return False, f'la imagen de compartir da {ri.status_code}'
    p['imagen_bytes'], p['imagen_url'] = ri.content, p['imagen']
    p['imagen_tipo'] = ri.headers['content-type'].split(';')[0]
    if not p['titulo']:
        return False, 'sin titular'
    return True, ''


def cola(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, encoding='utf-8') as f:
        entradas = json.load(f)
    salida = []
    for e in entradas:
        cuando = datetime.datetime.strptime(e['cuando'], '%Y-%m-%d %H:%M').replace(tzinfo=MADRID)
        salida.append({**e, 'id': 'cola:' + e['id'], 'cuando_utc': cuando.astimezone(datetime.timezone.utc)})
    return salida


# ---------------------------------------------------------------- textos por red

def textos(p):
    """Mismos datos para todas las redes; cada una con su largo máximo."""
    t, d, u = p.get('titulo', ''), p.get('entradilla', ''), p.get('enlace')
    if 'texto' in p:  # entrada de la cola: el texto lo ha aprobado Nacho tal cual
        base = p['texto']
        return {
            'x': p.get('texto_x') or (recortar(base, 280 - (URL_X + 2 if u else 0)) + (f'\n\n{u}' if u else '')),
            'bluesky': recortar(p.get('texto_bluesky') or base, 300),
            'mastodon': recortar(base, 500 - (URL_X + 2 if u else 0)) + (f'\n\n{u}' if u else ''),
            'telegram': html.escape(recortar(base, 900)) + (f'\n\n<a href="{html.escape(u)}">{html.escape(u)}</a>' if u else ''),
            'threads': recortar(base, 500 - (len(u) + 2 if u else 0)) + (f'\n\n{u}' if u else ''),
            'instagram': recortar(p.get('texto_instagram') or base, 2000),
        }
    return {
        'x': recortar(t, 280 - URL_X - 2) + f'\n\n{u}',
        'bluesky': recortar(t, 300),
        'mastodon': recortar(t, 200) + '\n\n' + recortar(d, 500 - 25 - min(len(t), 200) - 4) + f'\n\n{u}',
        'telegram': f'<b>{html.escape(recortar(t, 250))}</b>\n\n{html.escape(recortar(d, 600))}\n\n'
                    f'<a href="{html.escape(u)}">Leer la pieza en mapaelectoral.es</a>',
        'threads': recortar(t, 500 - len(u) - 2) + f'\n\n{u}',
        # en Instagram los enlaces del pie no son clicables: se remite a la web por su nombre
        'instagram': recortar(t, 300) + '\n\n' + recortar(d, 1200) +
                     '\n\nLa pieza completa, en mapaelectoral.es (sección Actualidad).\n\n#elecciones #mapaelectoral #datos',
    }


# ---------------------------------------------------------------- redes

def publicar_x(texto, p):
    from requests_oauthlib import OAuth1
    auth = OAuth1(os.environ['X_API_KEY'], os.environ['X_API_SECRET'],
                  os.environ['X_ACCESS_TOKEN'], os.environ['X_ACCESS_SECRET'])
    cuerpo = {'text': texto}
    if p.get('imagen_bytes') and 'texto' in p and not p.get('enlace'):
        # solo subimos imagen en entradas de la cola sin enlace; con enlace X ya pinta la tarjeta del og:image
        m = requests.post('https://upload.twitter.com/1.1/media/upload.json', auth=auth, timeout=60,
                          files={'media': p['imagen_bytes']})
        m.raise_for_status()
        cuerpo['media'] = {'media_ids': [m.json()['media_id_string']]}
    r = requests.post('https://api.x.com/2/tweets', auth=auth, json=cuerpo, timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f'X {r.status_code}: {r.text[:300]}')
    return 'https://x.com/_mapaelectoral/status/' + r.json()['data']['id']


def publicar_bluesky(texto, p):
    pds = 'https://bsky.social/xrpc/'
    s = requests.post(pds + 'com.atproto.server.createSession', timeout=30,
                      json={'identifier': os.environ['BLUESKY_USUARIO'], 'password': os.environ['BLUESKY_PASSWORD_APP']})
    s.raise_for_status()
    s = s.json()
    h = {'Authorization': 'Bearer ' + s['accessJwt']}
    registro = {'$type': 'app.bsky.feed.post', 'text': texto, 'langs': ['es'],
                'createdAt': ahora().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'}
    blob = None
    if p.get('imagen_bytes') and len(p['imagen_bytes']) < 950_000:
        b = requests.post(pds + 'com.atproto.repo.uploadBlob', data=p['imagen_bytes'], timeout=60,
                          headers={**h, 'Content-Type': p['imagen_tipo']})
        b.raise_for_status()
        blob = b.json()['blob']
    if p.get('enlace'):
        tarjeta = {'uri': p['enlace'], 'title': p.get('titulo', '')[:300], 'description': p.get('entradilla', '')[:1000]}
        if blob:
            tarjeta['thumb'] = blob
        registro['embed'] = {'$type': 'app.bsky.embed.external', 'external': tarjeta}
    elif blob:
        registro['embed'] = {'$type': 'app.bsky.embed.images', 'images': [{'image': blob, 'alt': p.get('alt', '')}]}
    r = requests.post(pds + 'com.atproto.repo.createRecord', headers=h, timeout=30,
                      json={'repo': s['did'], 'collection': 'app.bsky.feed.post', 'record': registro})
    if r.status_code >= 300:
        raise RuntimeError(f'Bluesky {r.status_code}: {r.text[:300]}')
    rkey = r.json()['uri'].rsplit('/', 1)[1]
    return f'https://bsky.app/profile/{s["handle"]}/post/{rkey}'


def publicar_mastodon(texto, p):
    base = os.environ['MASTODON_SERVIDOR'].rstrip('/')
    h = {'Authorization': 'Bearer ' + os.environ['MASTODON_TOKEN']}
    datos = {'status': texto, 'language': 'es', 'visibility': 'public'}
    if p.get('imagen_bytes') and not p.get('enlace'):
        m = requests.post(base + '/api/v2/media', headers=h, timeout=60,
                          files={'file': ('imagen', p['imagen_bytes'], p['imagen_tipo'])}, data={'description': p.get('alt', '')})
        m.raise_for_status()
        datos['media_ids[]'] = m.json()['id']
    r = requests.post(base + '/api/v1/statuses', headers={**h, 'Idempotency-Key': p['id'][:60]}, data=datos, timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f'Mastodon {r.status_code}: {r.text[:300]}')
    return r.json()['url']


def publicar_telegram(texto, p):
    api = f'https://api.telegram.org/bot{os.environ["TELEGRAM_TOKEN"]}/'
    canal = os.environ['TELEGRAM_CANAL']
    if p.get('imagen_bytes'):
        r = requests.post(api + 'sendPhoto', timeout=60, data={'chat_id': canal, 'caption': texto[:1024], 'parse_mode': 'HTML'},
                          files={'photo': ('imagen.jpg', p['imagen_bytes'], p['imagen_tipo'])})
    else:
        r = requests.post(api + 'sendMessage', timeout=30, data={'chat_id': canal, 'text': texto, 'parse_mode': 'HTML'})
    if r.status_code >= 300 or not r.json().get('ok'):
        raise RuntimeError(f'Telegram {r.status_code}: {r.text[:300]}')
    msg = r.json()['result']
    usuario = msg['chat'].get('username')
    return f'https://t.me/{usuario}/{msg["message_id"]}' if usuario else str(msg['message_id'])


def publicar_threads(texto, p):
    base, usuario, token = 'https://graph.threads.net/v1.0', os.environ['THREADS_USUARIO_ID'], os.environ['THREADS_TOKEN']
    datos = {'text': texto, 'access_token': token}
    if p.get('imagen_url') and not p.get('enlace'):
        datos.update(media_type='IMAGE', image_url=p['imagen_url'])
    else:
        datos['media_type'] = 'TEXT'  # el enlace del texto genera la vista previa
    c = requests.post(f'{base}/{usuario}/threads', data=datos, timeout=60)
    if c.status_code >= 300:
        raise RuntimeError(f'Threads {c.status_code}: {c.text[:300]}')
    time.sleep(5)  # Meta pide esperar a que el contenedor se procese
    r = requests.post(f'{base}/{usuario}/threads_publish', data={'creation_id': c.json()['id'], 'access_token': token}, timeout=60)
    if r.status_code >= 300:
        raise RuntimeError(f'Threads {r.status_code}: {r.text[:300]}')
    l = requests.get(f'{base}/{r.json()["id"]}', params={'fields': 'permalink', 'access_token': token}, timeout=30)
    return l.json().get('permalink', r.json()['id']) if l.ok else r.json()['id']


def publicar_instagram(texto, p):
    if not p.get('imagen_url'):
        raise RuntimeError('Instagram necesita imagen y esta entrada no la tiene')
    base, usuario, token = 'https://graph.instagram.com/v21.0', os.environ['INSTAGRAM_USUARIO_ID'], os.environ['INSTAGRAM_TOKEN']
    c = requests.post(f'{base}/{usuario}/media', timeout=60,
                      data={'image_url': p['imagen_url'], 'caption': texto, 'access_token': token})
    if c.status_code >= 300:
        raise RuntimeError(f'Instagram {c.status_code}: {c.text[:300]}')
    cid = c.json()['id']
    for _ in range(12):  # esperar a que Instagram descargue y procese la imagen
        e = requests.get(f'{base}/{cid}', params={'fields': 'status_code', 'access_token': token}, timeout=30)
        if e.ok and e.json().get('status_code') == 'FINISHED':
            break
        if e.ok and e.json().get('status_code') == 'ERROR':
            raise RuntimeError(f'Instagram no pudo procesar la imagen {p["imagen_url"]}')
        time.sleep(5)
    r = requests.post(f'{base}/{usuario}/media_publish', data={'creation_id': cid, 'access_token': token}, timeout=60)
    if r.status_code >= 300:
        raise RuntimeError(f'Instagram {r.status_code}: {r.text[:300]}')
    l = requests.get(f'{base}/{r.json()["id"]}', params={'fields': 'permalink', 'access_token': token}, timeout=30)
    return l.json().get('permalink', r.json()['id']) if l.ok else r.json()['id']


def renovar_tokens_meta(di):
    """Los tokens largos de Meta duran 60 días; esta llamada amplía su validez. Se hace en cada pasada del día 1 y 15."""
    if ahora().day not in (1, 15) or ahora().hour != 3 or ahora().minute >= 15:
        return
    for nombre, url, tipo in (('INSTAGRAM_TOKEN', 'https://graph.instagram.com/refresh_access_token', 'ig_refresh_token'),
                              ('THREADS_TOKEN', 'https://graph.threads.net/refresh_access_token', 'th_refresh_token')):
        if os.environ.get(nombre):
            r = requests.get(url, params={'grant_type': tipo, 'access_token': os.environ[nombre]}, timeout=30)
            dias = r.json().get('expires_in', 0) // 86400 if r.ok else None
            nuevo = r.ok and r.json().get('access_token') != os.environ[nombre]
            di(f'{nombre}: renovación {"correcta" if r.ok else "FALLIDA " + r.text[:200]}'
               + (f', caduca en {dias} días' if dias else '')
               + ('. OJO: Meta ha devuelto un token distinto; hay que copiarlo al secreto' if nuevo else ''))


PUBLICAR = {'x': publicar_x, 'bluesky': publicar_bluesky, 'mastodon': publicar_mastodon, 'telegram': publicar_telegram,
            'threads': publicar_threads, 'instagram': publicar_instagram}
SECRETOS = {'x': ['X_API_KEY', 'X_API_SECRET', 'X_ACCESS_TOKEN', 'X_ACCESS_SECRET'],
            'bluesky': ['BLUESKY_USUARIO', 'BLUESKY_PASSWORD_APP'],
            'mastodon': ['MASTODON_SERVIDOR', 'MASTODON_TOKEN'],
            'telegram': ['TELEGRAM_TOKEN', 'TELEGRAM_CANAL'],
            'threads': ['THREADS_USUARIO_ID', 'THREADS_TOKEN'],
            'instagram': ['INSTAGRAM_USUARIO_ID', 'INSTAGRAM_TOKEN']}


# ---------------------------------------------------------------- principal

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--registro', required=True, help='ruta de registro.json (rama redes-registro)')
    ap.add_argument('--cola', default='redes/cola.json')
    ap.add_argument('--resumen', help='archivo de resumen (GITHUB_STEP_SUMMARY)')
    args = ap.parse_args()

    log = []
    def di(linea):
        print(linea)
        log.append(linea)

    if os.environ.get('REDES_PAUSA', '').strip() in ('1', 'si', 'sí', 'true'):
        di('REDES_PAUSA activada: no se publica nada.')
        return escribir_resumen(args.resumen, log)

    pedidas = [r.strip().lower() for r in os.environ.get('REDES_ACTIVAS', '').split(',') if r.strip()]
    activas = []
    for red in pedidas:
        faltan = [s for s in SECRETOS.get(red, ['?']) if not os.environ.get(s)]
        if red not in PUBLICAR:
            di(f'Red desconocida en REDES_ACTIVAS: {red}')
        elif faltan:
            di(f'{red}: faltan los secretos {", ".join(faltan)}; no se publica ahí.')
        else:
            activas.append(red)
    ensayo = not activas
    if ensayo:
        di('Ninguna red activa (variable REDES_ACTIVAS vacía o sin secretos): modo ensayo, solo se muestra lo que saldría.')

    registro = {}
    if os.path.exists(args.registro):
        with open(args.registro, encoding='utf-8') as f:
            registro = json.load(f)
    registro.setdefault('publicado', {})
    registro.setdefault('redes_sembradas', [])

    if not ensayo:
        renovar_tokens_meta(di)
    piezas = piezas_del_feed()
    t = ahora()
    # Primera vez de una red: todo lo que ya está en el feed cuenta como publicado
    for red in activas:
        if red not in registro['redes_sembradas']:
            for p in piezas:
                registro['publicado'].setdefault(p['id'], {}).setdefault(red, 'anterior a la activación')
            registro['redes_sembradas'].append(red)
            di(f'{red}: primera activación; {len(piezas)} piezas del feed marcadas como ya publicadas.')

    pendientes = []
    for p in piezas:
        if t - p['fecha'] <= VENTANA_PIEZAS and p['fecha'] <= t:
            pendientes.append(p)
    for e in cola(args.cola):
        if e['cuando_utc'] <= t:
            if t - e['cuando_utc'] > VENTANA_COLA:
                if e['id'] not in registro['publicado']:
                    di(f'Cola {e["id"]}: caducada (era para {e["cuando"]}); no sale.')
                    registro['publicado'][e['id']] = {'caducada': e['cuando']}
                continue
            pendientes.append(e)

    for p in pendientes:
        hecho = registro['publicado'].get(p['id'], {})
        if 'caducada' in hecho:
            continue
        faltan = [r for r in (p.get('redes') or REDES) if (r in activas or ensayo) and r not in hecho]
        if 'texto' in p and not p.get('imagen'):
            faltan = [r for r in faltan if r != 'instagram']  # Instagram no admite publicaciones sin imagen
        if not faltan:
            continue
        if 'texto' not in p:
            ok, motivo = comprobar_pieza(p)
            if not ok:
                di(f'Pieza {p["enlace"]}: NO se anuncia ({motivo}).')
                continue
        elif p.get('imagen'):
            img = p['imagen'] if p['imagen'].startswith('http') else 'https://mapaelectoral.es/' + p['imagen'].lstrip('/')
            ri = get(img)
            if ri.status_code != 200:
                di(f'Cola {p["id"]}: la imagen {img} da {ri.status_code}; no sale.')
                continue
            p['imagen_bytes'], p['imagen_tipo'] = ri.content, ri.headers['content-type'].split(';')[0]
            p['imagen_url'] = img
        tx = textos(p)
        for red in faltan:
            if ensayo:
                di(f'[ensayo] {red} · {p["id"]}\n{tx[red]}\n')
                continue
            try:
                url = PUBLICAR[red](tx[red], p)
                registro['publicado'].setdefault(p['id'], {})[red] = url
                di(f'{red}: publicado {p["id"]} → {url}')
            except Exception as ex:  # una red caída no frena a las demás; se reintenta en la siguiente pasada
                di(f'{red}: ERROR con {p["id"]}: {ex}')
            time.sleep(2)

    if not ensayo:
        with open(args.registro, 'w', encoding='utf-8') as f:
            json.dump(registro, f, ensure_ascii=False, indent=1, sort_keys=True)
    escribir_resumen(args.resumen, log)


def escribir_resumen(ruta, log):
    if ruta:
        with open(ruta, 'a', encoding='utf-8') as f:
            f.write('## Redes sociales\n\n```\n' + ('\n'.join(log) or 'Nada que publicar.') + '\n```\n')


if __name__ == '__main__':
    main()
