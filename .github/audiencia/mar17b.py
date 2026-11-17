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
D0=datetime.datetime(2026,11,16,23); corte=now-D0
print('RUN',2);print('CORTE',Z(now),corte)
def tot(a,b):
    g=grp(['date'],10,Z(a),Z(b)); return sum(r['sum']['visits'] for r in g),sum(r['count'] for r in g)
for k in [0,1,7]:
    a=D0-datetime.timedelta(days=k); print('MISMAHORA',k,tot(a,a+corte))
def desglose(lab,a,b):
    A,B=Z(a),Z(b)
    for r in grp(['requestPath'],8,A,B): print('PATH',lab,r['sum']['visits'],r['dimensions']['requestPath'])
    ref=collections.Counter()
    for r in grp(['refererHost'],5000,A,B):
        h=r['dimensions']['refererHost'] or '(directo)'; h='google' if 'google' in h else h; ref[h]+=r['sum']['visits']
    print('REF',lab,sum(ref.values()),ref.most_common(8))
    dev=collections.Counter()
    for r in grp(['deviceType'],50,A,B): dev[r['dimensions']['deviceType']]+=r['sum']['visits']
    print('DEV',lab,dev.most_common())
for k,lab in [(0,'HOY'),(1,'LUN'),(7,'MAR10')]:
    a=D0-datetime.timedelta(days=k); desglose(lab,a,a+corte)
# /encuestas/ por horas, Google y total, hoy y ayer
for k,lab in [(0,'HOY'),(1,'LUN')]:
    a=D0-datetime.timedelta(days=k); b=a+corte
    g=collections.Counter(); t=collections.Counter()
    for r in grp(['datetimeHour','refererHost'],2000,Z(a),Z(b),',{requestPath:"/encuestas/"}'):
        hh=r['dimensions']['datetimeHour'][11:13]; t[hh]+=r['sum']['visits']
        if 'google' in (r['dimensions']['refererHost'] or ''): g[hh]+=r['sum']['visits']
    print('ENCH',lab,'UTC', [(h,g[h],t[h]) for h in sorted(t)])
for s in ['feijoo-gipuzkoa']:
    for r in grp(['requestPath'],10,Z(D0),Z(now),',{requestPath_like:"%%%s%%"}'%s): print('SLUG',s,r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
    for r in grp(['refererHost'],10,Z(D0),Z(now),',{requestPath_like:"%%%s%%"}'%s): print('SLUGREF',s,r['sum']['visits'],r['dimensions']['refererHost'])
h=collections.Counter()
for r in grp(['datetimeHour'],50,Z(D0),Z(now)): h[r['dimensions']['datetimeHour'][11:13]]+=r['sum']['visits']
print('HORA UTC',sorted(h.items()))
X=['t.co','x.com','twitter.com','mobile.twitter.com']
xp=collections.Counter()
for r in grp(['refererHost','requestPath'],2000,Z(D0),Z(now),',{refererHost_in:%s}'%json.dumps(X)): xp[r['dimensions']['requestPath']]+=r['sum']['visits']
print('XPATH',xp.most_common(10))
m=collections.Counter()
for r in grp(['datetimeMinute'],500,Z(D0),Z(now),',{refererHost_in:%s}'%json.dumps(X)): m[r['dimensions']['datetimeMinute'][11:16]]+=r['sum']['visits']
print('XMIN UTC',sorted(m.items()))
# Temporal: audiencia martes 17-11 mediodía. No se fusiona a main.
