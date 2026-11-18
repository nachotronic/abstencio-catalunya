# Temporal, solo lectura: audiencia 18-11. No se fusiona a main.
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
for lab,k in [('HOY',0),('MISMA_MAR17',1),('MISMA_MIE11',7)]:
    a=HOY-D(days=k); informe(lab,a,a+corte)
