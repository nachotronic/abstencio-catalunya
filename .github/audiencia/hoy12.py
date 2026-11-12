import json,collections,urllib.request,os
raw=os.environ.get('CF','')
tok=next((p.strip().strip('"\'') for p in raw.split() if p.strip().strip('"\'').startswith('cfut_')), raw.strip().strip('"\''))
ACC='dee996483598974c337d0777f5ef047c'; SITE='532b57a6348a4babba29020993949dd7'
EXC=['/encuestas/calculadora-escanos/','/encuestas/simulador-pactos/']
def gql(q):
    r=urllib.request.Request('https://api.cloudflare.com/client/v4/graphql',json.dumps({'query':q}).encode(),{'Authorization':'Bearer '+tok,'Content-Type':'application/json'})
    d=json.load(urllib.request.urlopen(r))
    if d.get('errors'): print('ERR',d['errors']); return []
    return d['data']['viewer']['accounts'][0]['g']
def grp(dims,limit,t1,t2,extra=''):
    f='{AND:[{siteTag:"%s"},{datetime_geq:"%s"},{datetime_lt:"%s"},{requestPath_notin:%s}%s]}'%(SITE,t1,t2,json.dumps(EXC),extra)
    q='{viewer{accounts(filter:{accountTag:"%s"}){g:rumPageloadEventsAdaptiveGroups(limit:%d,filter:%s,orderBy:[sum_visits_DESC]){count sum{visits} dimensions{%s}}}}}'%(ACC,limit,f,' '.join(dims))
    return gql(q)
import datetime
now=datetime.datetime.utcnow().replace(minute=0,second=0,microsecond=0)
hoyfin=now.strftime('%Y-%m-%dT%H:00:00Z'); ayerfin=(now-datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:00:00Z')
print('CORTE',hoyfin)
for lab,(a,b) in [('HOY',('2026-11-11T23:00:00Z',hoyfin)),('AYER',('2026-11-10T23:00:00Z',ayerfin))]:
    tot=sum(r['sum']['visits'] for r in grp(['date'],10,a,b)); vw=sum(r['count'] for r in grp(['date'],10,a,b)); print('TOT',lab,tot,vw)
    for r in grp(['requestPath'],25,a,b): print('PATH',lab,r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
    sec=collections.Counter()
    for r in grp(['requestPath'],5000,a,b):
        p=r['dimensions']['requestPath']; s=p.strip('/').split('/')[0] or '(portada)'; sec[s]+=r['sum']['visits']
    print('SEC',lab,sec.most_common(12))
    for r in grp(['requestPath'],40,a,b,',{requestPath_like:"/actualidad/%"}'): print('ACT',lab,r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
    for s in ['mapa-electoral-','arranque-campana','cabo-verde']:
        for r in grp(['requestPath'],10,a,b,',{requestPath_like:"%%%s%%"}'%s): print('SLUG',lab,s,r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
    ref=collections.Counter()
    for r in grp(['refererHost'],5000,a,b):
        h=r['dimensions']['refererHost'] or '(directo)'; h='google' if 'google' in h else h; ref[h]+=r['sum']['visits']
    print('REF',lab,ref.most_common(15))
    for r in grp(['refererHost','requestPath'],25,a,b,',{refererHost_notlike:"%google%"},{refererHost_notlike:"%mapaelectoral%"},{refererHost_neq:""}'): print('REFL',lab,r['sum']['visits'],r['dimensions']['refererHost'],r['dimensions']['requestPath'])
    dev=collections.Counter()
    for r in grp(['deviceType'],50,a,b): dev[r['dimensions']['deviceType']]+=r['sum']['visits']
    print('DEV',lab,dev.most_common())
for lab,(a,b) in [('HOY',('2026-11-11T23:00:00Z',hoyfin))]:
    for r in grp(['requestPath'],30,a,b,',{requestPath_like:"/internacional/%"}'): print('INT',lab,r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
# corte 12-11
