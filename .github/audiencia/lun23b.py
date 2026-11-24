# Temporal, solo lectura: audiencia 23-11. No se fusiona a main.
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
D=datetime.timedelta
now=datetime.datetime.utcnow().replace(second=0,microsecond=0)
HOY=datetime.datetime(2026,11,23,23)  # 24-11 00:00 Madrid (UTC+1)
corte=now-HOY
print('CORTE',Z(now),'madrid',(now+D(hours=1)).strftime('%H:%M'),corte)
PIEZAS=['/actualidad/encuestas-andorra-29n/']
def tipo(p):
    if p=='/': return 'portada'
    if p=='/encuestas/': return 'encuestas_portada'
    if p.startswith('/encuestas/'): return 'encuestas_resto'
    if p.startswith('/municipio/'): return 'fichas'
    if p.startswith('/listas'): return 'listas'
    if p.startswith('/actualidad/'): return 'actualidad'
    if p.startswith('/elecciones/'): return 'elecciones'
    return 'otros'
def hora(r): return (datetime.datetime.strptime(r['dimensions']['datetimeHour'][:13],'%Y-%m-%dT%H')+D(hours=1)).hour
def refn(h):
    h=h or '(directo)'
    if 'google' in h: return 'google'
    if h in ('t.co','x.com','twitter.com','mobile.twitter.com'): return 'x'
    if 'facebook' in h: return 'facebook'
    if 'bing' in h: return 'bing'
    return h
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
    print('TOP',lab,paths.most_common(12))
    print('PIEZAS',lab,[(p,paths[p]) for p in PIEZAS])
    act=collections.Counter({p:v for p,v in paths.items() if p.startswith('/actualidad/')})
    print('ACT',lab,sum(act.values()),act.most_common(40))
    print('KEY',lab,[(p,v) for p,v in paths.items() if any(k in p for k in ('escrutinio','blanco','nulo','cifras','investidura','participacion','veda','24-nov'))])
    ref=collections.Counter()
    for r in grp(['refererHost'],5000,Z(a),Z(b)): ref[refn(r['dimensions']['refererHost'])]+=r['sum']['visits']
    print('REF',lab,sum(ref.values()),ref.most_common(8))
    pr=collections.defaultdict(collections.Counter)
    for r in grp(['refererHost','requestPath'],5000,Z(a),Z(b)):
        p=r['dimensions']['requestPath']; k=refn(r['dimensions']['refererHost'])
        if p in PIEZAS or p=='/encuestas/' or (p.startswith('/actualidad/') and any(k in p for k in ('escrutinio','blanco','cifras','investidura','veda'))): pr[p][k]+=r['sum']['visits']
        if k=='x': pr['X_por_ruta'][p]+=r['sum']['visits']
    for p,c in pr.items(): print('REFPAG',lab,p,sum(c.values()),c.most_common(6))
for lab,k in [('HOY24',0)]:
    a=HOY-D(days=k); informe('MISMAHORA_'+lab,a,a+corte)
for lab,k in []:
    a=HOY-D(days=k); informe('DIA_'+lab,a,a+D(days=1))

pa=collections.Counter()
for r in grp(['datetimeHour'],50,Z(HOY),Z(now),',{requestPath:"/actualidad/encuestas-andorra-29n/"}'): pa[hora(r)]+=r['sum']['visits']
print('ANDORRA_HORA',sorted(pa.items()))
for r in grp(['refererHost','refererPath'],30,Z(HOY),Z(now),',{requestPath:"/actualidad/encuestas-andorra-29n/"}'): print('ANDORRA_REF',r['dimensions'],r['sum']['visits'])
for r in grp(['deviceType','countryName'],10,Z(HOY),Z(now),',{requestPath:"/actualidad/encuestas-andorra-29n/"}'): print('ANDORRA_DEV',r['dimensions'],r['sum']['visits'])
