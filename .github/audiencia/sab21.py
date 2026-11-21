# Temporal, solo lectura: audiencia 21-11. No se fusiona a main.
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
HOY=datetime.datetime(2026,11,17,23); corte=now-HOY   # Madrid = UTC+1
print('CORTE',Z(now),corte)
def tipo(p):
    if p=='/': return 'portada'
    if p=='/encuestas/': return 'encuestas_portada'
    if p.startswith('/encuestas/'): return 'encuestas_resto'
    if p.startswith('/municipio/'): return 'fichas'
    if p.startswith('/listas'): return 'listas'
    if p.startswith('/actualidad/'): return 'actualidad'
    if p.startswith('/elecciones/'): return 'elecciones'
    return 'otros'
def hora(r): return (datetime.datetime.strptime(r['dimensions']['datetimeHour'][:13],'%Y-%m-%dT%H')+datetime.timedelta(hours=1)).hour
def informe(lab,a,b):
    hv=collections.Counter(); hpv=collections.Counter()
    for r in grp(['datetimeHour'],50,Z(a),Z(b)):
        hv[hora(r)]+=r['sum']['visits']; hpv[hora(r)]+=r['count']
    print('TOT',lab,sum(hv.values()),sum(hpv.values()))
    print('HORA',lab,sorted(hv.items()))
    ty=collections.Counter(); paths=collections.Counter()
    for r in grp(['requestPath'],5000,Z(a),Z(b)):
        p=r['dimensions']['requestPath']; ty[tipo(p)]+=r['sum']['visits']; paths[p]+=r['sum']['visits']
    print('TIPO',lab,sum(ty.values()),ty.most_common())
    print('TOP',lab,paths.most_common(10))
    ref=collections.Counter()
    for r in grp(['refererHost'],5000,Z(a),Z(b)):
        h=r['dimensions']['refererHost'] or '(directo)'; h='google' if 'google' in h else h; ref[h]+=r['sum']['visits']
    print('REF',lab,sum(ref.values()),ref.most_common(6))
    g=collections.Counter()
    for r in grp(['datetimeHour'],50,Z(a),Z(b),',{requestPath:"/encuestas/"},{refererHost_like:"%google%"}'): g[hora(r)]+=r['sum']['visits']
    print('ENC_GOOGLE_HORA',lab,sum(g.values()),sorted(g.items()))
D=datetime.timedelta
HOY=datetime.datetime(2026,11,18,23)  # 19-11 00:00 Madrid
corte=now-HOY
print('CORTE_HOY',corte)
def xref(lab,a,b):
    x=collections.Counter()
HOY=datetime.datetime(2026,11,20,23)  # 21-11 00:00 Madrid
corte=now-HOY
print('CORTE_HOY',corte)
def xref(lab,a,b):
    x=collections.Counter()
    for r in grp(['refererHost','requestPath'],5000,Z(a),Z(b)):
        h=r['dimensions']['refererHost'] or ''
        if h in ('t.co','x.com','twitter.com','mobile.twitter.com') or h.endswith('.x.com'): x[r['dimensions']['requestPath']]+=r['sum']['visits']
    print('X',lab,sum(x.values()),x.most_common(10))
    e=collections.Counter()
    for r in grp(['datetimeHour'],50,Z(a),Z(b),',{requestPath:"/encuestas/"}'): e[hora(r)]+=r['sum']['visits']
    print('ENC_TOTAL_HORA',lab,sum(e.values()),sorted(e.items()))
for lab,k in [('HOY21',0),('VIE20',1),('SAB14',7)]:
    a=HOY-D(days=k); informe('MISMAHORA_'+lab,a,a+corte); xref(lab,a,a+corte)
    act=collections.Counter()
    for r in grp(['requestPath'],5000,Z(a),Z(a+corte)):
        p=r['dimensions']['requestPath']
        if p.startswith('/actualidad/') or p.startswith('/internacional/') or p.startswith('/historia'): act[p]+=r['sum']['visits']
    print('ACT',lab,sum(act.values()),act.most_common(12))
for lab,k in [('VIE20',1),('SAB14',7)]:
    a=HOY-D(days=k); informe('DIA_'+lab,a,a+D(days=1))
