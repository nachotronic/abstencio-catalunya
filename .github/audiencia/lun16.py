import json,collections,urllib.request,os,datetime
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
Z=lambda d:d.strftime('%Y-%m-%dT%H:%M:00Z')
now=datetime.datetime.utcnow().replace(second=0,microsecond=0)
D0=datetime.datetime(2026,11,15,23); corte=now-D0
print('RUN',3);print('CORTE',Z(now),corte)
def tot(a,b):
    g=grp(['date'],10,Z(a),Z(b)); return sum(r['sum']['visits'] for r in g),sum(r['count'] for r in g)
for k in [0,1,7,8]:
    a=D0-datetime.timedelta(days=k); print('MISMAHORA',k,tot(a,a+corte))
def desglose(lab,a,b):
    A,B=Z(a),Z(b)
    sec=collections.Counter()
    for r in grp(['requestPath'],5000,A,B):
        p=r['dimensions']['requestPath']; s=p.strip('/').split('/')[0] or '(portada)'; sec[s]+=r['sum']['visits']
    print('SEC',lab,sec.most_common(10))
    for r in grp(['requestPath'],12,A,B): print('PATH',lab,r['sum']['visits'],r['dimensions']['requestPath'])
    ref=collections.Counter()
    for r in grp(['refererHost'],5000,A,B):
        h=r['dimensions']['refererHost'] or '(directo)'; h='google' if 'google' in h else h; ref[h]+=r['sum']['visits']
    print('REF',lab,ref.most_common(15))
    dev=collections.Counter()
    for r in grp(['deviceType'],50,A,B): dev[r['dimensions']['deviceType']]+=r['sum']['visits']
    print('DEV',lab,dev.most_common())
    for r in grp(['requestPath'],15,A,B,',{requestPath_like:"/actualidad/%"}'): print('ACT',lab,r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
desglose('HOY',D0,now)
desglose('DOM',D0-datetime.timedelta(days=1),D0-datetime.timedelta(days=1)+corte)
print('AYER',tot(D0-datetime.timedelta(days=1),D0))
for s in ['encuestas-primera-semana-campana','feijoo-pamplona','cabo-verde','generacion-2008']:
    for r in grp(['requestPath'],10,Z(datetime.datetime(2026,11,15,23)),Z(now),',{requestPath_like:"%%%s%%"}'%s): print('SLUG',s,r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
    for r in grp(['refererHost'],10,Z(datetime.datetime(2026,11,15,23)),Z(now),',{requestPath_like:"%%%s%%"}'%s): print('SLUGREF',s,r['sum']['visits'],r['dimensions']['refererHost'])
h=collections.Counter()
for r in grp(['datetimeHour'],50,Z(D0),Z(now)): h[r['dimensions']['datetimeHour']]+=r['sum']['visits']
print('HORA UTC',sorted(h.items()))
