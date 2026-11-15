import json,collections,urllib.request,os,datetime
raw=os.environ.get('CF','')
tok=next((p.strip().strip('"\'') for p in raw.split() if p.strip().strip('"\'').startswith('cfut_')), raw.strip().strip('"\''))
ACC='dee996483598974c337d0777f5ef047c'; SITE='532b57a6348a4babba29020993949dd7'
EXC=['/encuestas/calculadora-escanos/','/encuestas/simulador-pactos/']
XH=["t.co","x.com","twitter.com","mobile.twitter.com","www.x.com"]
def gql(q):
    r=urllib.request.Request('https://api.cloudflare.com/client/v4/graphql',json.dumps({'query':q}).encode(),{'Authorization':'Bearer '+tok,'Content-Type':'application/json'})
    d=json.load(urllib.request.urlopen(r))
    if d.get('errors'): print('ERR',d['errors']); return []
    return d['data']['viewer']['accounts'][0]['g']
def grp(dims,limit,t1,t2,extra=''):
    f='{AND:[{siteTag:"%s"},{datetime_geq:"%s"},{datetime_lt:"%s"},{requestPath_notin:%s}%s]}'%(SITE,t1,t2,json.dumps(EXC),extra)
    q='{viewer{accounts(filter:{accountTag:"%s"}){g:rumPageloadEventsAdaptiveGroups(limit:%d,filter:%s,orderBy:[sum_visits_DESC]){count sum{visits} dimensions{%s}}}}}'%(ACC,limit,f,' '.join(dims))
    return gql(q)
Z=lambda d:d.strftime('%Y-%m-%dT%H:00:00Z')
now=datetime.datetime.utcnow().replace(minute=0,second=0,microsecond=0)
D0=datetime.datetime(2026,11,14,23)  # domingo 15-11 00h Madrid
corte=now-D0
print('CORTE',Z(now),'horas',corte)
def tot(a,b):
    g=grp(['date'],10,Z(a),Z(b)); return sum(r['sum']['visits'] for r in g),sum(r['count'] for r in g)
for k in [0,1,7,8,14,15]:
    a=D0-datetime.timedelta(days=k); print('MISMAHORA',(a+datetime.timedelta(hours=1)).date(),k,tot(a,a+corte))
for k in [1,7,8]:
    a=D0-datetime.timedelta(days=k); print('DIACOMPLETO',(a+datetime.timedelta(hours=1)).date(),tot(a,a+datetime.timedelta(days=1)))
def desglose(lab,a,b):
    A,B=Z(a),Z(b)
    print('TOT',lab,tot(a,b))
    for r in grp(['requestPath'],25,A,B): print('PATH',lab,r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
    sec=collections.Counter()
    for r in grp(['requestPath'],5000,A,B):
        p=r['dimensions']['requestPath']; s=p.strip('/').split('/')[0] or '(portada)'; sec[s]+=r['sum']['visits']
    print('SEC',lab,sec.most_common(12))
    for r in grp(['requestPath'],30,A,B,',{requestPath_like:"/actualidad/%"}'): print('ACT',lab,r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
    ref=collections.Counter()
    for r in grp(['refererHost'],5000,A,B):
        h=r['dimensions']['refererHost'] or '(directo)'; h='google' if 'google' in h else h; ref[h]+=r['sum']['visits']
    print('REF',lab,ref.most_common(20))
    for r in grp(['refererHost','requestPath'],30,A,B,',{refererHost_notlike:"%google%"},{refererHost_notlike:"%mapaelectoral%"},{refererHost_neq:""}'): print('REFL',lab,r['sum']['visits'],r['dimensions']['refererHost'],r['dimensions']['requestPath'])
    dev=collections.Counter()
    for r in grp(['deviceType'],50,A,B): dev[r['dimensions']['deviceType']]+=r['sum']['visits']
    print('DEV',lab,dev.most_common())
desglose('HOY',D0,now)
desglose('TRASTUIT',datetime.datetime(2026,11,14,18),now)
desglose('SAB14_12a18UTC',datetime.datetime(2026,11,14,12),datetime.datetime(2026,11,14,18))
for s in ['generacion-2008','seleccion-convocados','dos-semanas','debate-lasexta','cis-preelectoral']:
    for r in grp(['requestPath'],10,Z(datetime.datetime(2026,11,14,0)),Z(now),',{requestPath_like:"%%%s%%"}'%s): print('SLUG',s,r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
h=collections.Counter(); x=collections.Counter()
A,B=Z(datetime.datetime(2026,11,14,0)),Z(now)
for r in grp(['datetimeHour'],200,A,B): h[r['dimensions']['datetimeHour']]+=r['sum']['visits']
for r in grp(['datetimeHour','refererHost'],2000,A,B):
    if (r['dimensions']['refererHost'] or '') in XH: x[r['dimensions']['datetimeHour']]+=r['sum']['visits']
print('HORA (UTC; Madrid=+1)',sorted(h.items()))
print('HORA_X',sorted(x.items()))
for wk in [1,7]:
    hh=collections.Counter()
    for r in grp(['datetimeHour'],200,Z(datetime.datetime(2026,11,14,0)-datetime.timedelta(days=wk)),Z(now-datetime.timedelta(days=wk))): hh[r['dimensions']['datetimeHour']]+=r['sum']['visits']
    print('HORA_MENOS',wk,sorted(hh.items()))
for r in grp(['refererHost','refererPath','requestPath'],50,Z(datetime.datetime(2026,11,10)),B,',{refererHost_in:%s}'%json.dumps(XH)): print('XREF',r['sum']['visits'],r['count'],r['dimensions'])
for r in grp(['date','refererHost'],100,Z(datetime.datetime(2026,11,1)),B,',{refererHost_in:%s}'%json.dumps(XH)): print('XDIA',r['dimensions']['date'],r['dimensions']['refererHost'],r['sum']['visits'],r['count'])
for r in grp(['countryName'],10,Z(datetime.datetime(2026,11,14,18)),B): print('PAIS',r['dimensions']['countryName'],r['sum']['visits'])
