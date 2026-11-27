# Temporal, solo lectura: 27-11. No se fusiona a main.
import json,collections,urllib.request,os,datetime
raw=os.environ.get('CF','')
tok=next((p.strip().strip('"\'') for p in raw.split() if p.strip().strip('"\'').startswith('cfut_')), raw.strip().strip('"\''))
ACC='dee996483598974c337d0777f5ef047c'; SITE='532b57a6348a4babba29020993949dd7'
EXC=['/encuestas/calculadora-escanos/','/encuestas/simulador-pactos/']
AND='/actualidad/encuestas-andorra-29n/'
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
HOY=datetime.datetime(2026,11,26,23)
corte=now-HOY
print('CORTE',Z(now),'madrid',(now+D(hours=1)).strftime('%H:%M'))
print('CORTE',Z(now),'madrid',(now+D(hours=1)).strftime('%H:%M'))
def hora(r): return (datetime.datetime.strptime(r['dimensions']['datetimeHour'][:13],'%Y-%m-%dT%H')+D(hours=1)).hour
def refn(h):
    h=h or '(directo)'
    if 'google' in h: return 'google'
    if h in ('t.co','x.com','twitter.com'): return 'x'
    if 'bing' in h: return 'bing'
    return h
def cat(p):
    if 'voto-util-29n' in p: return 'voto_util'
    if p==AND: return 'andorra'
    if p=='/encuestas/': return 'encuestas_portada'
    if p.startswith('/encuestas/'): return 'encuestas_prov'
    if p.startswith('/actualidad/verificacion-debate'): return 'verificacion'
    if p.startswith('/actualidad/como-votar'): return 'como_votar'
    if p=='/': return 'portada'
    if p.startswith('/elecciones/resultados-elecciones-generales-2026'): return 'resultados'
    if p.startswith('/actualidad/'): return 'actualidad_otras'
    if p.startswith('/elecciones/'): return 'elecciones_otras'
    return 'otras'
def informe(lab,a,b):
    hv=collections.Counter()
    for r in grp(['datetimeHour'],50,Z(a),Z(b)): hv[hora(r)]+=r['sum']['visits']
    print('TOT',lab,sum(hv.values()))
    print('HORA',lab,sorted(hv.items()))
    ref=collections.Counter(); c=collections.Counter(); cv=collections.Counter(); paths=collections.Counter(); nvu=set()
    for r in grp(['refererHost','requestPath'],10000,Z(a),Z(b)):
        p=r['dimensions']['requestPath']; v=r['sum']['visits']
        ref[refn(r['dimensions']['refererHost'])]+=v; c[cat(p)]+=v; cv[cat(p)]+=r['count']; paths[p]+=v
        if 'voto-util-29n' in p: nvu.add(p)
    print('REF',lab,sum(ref.values()),ref.most_common(8))
    print('CAT',lab,sorted(c.items(),key=lambda x:-x[1]))
    print('CATVISTAS',lab,sorted(cv.items(),key=lambda x:-x[1]))
    print('NVU',lab,len(nvu))
    print('TOP',lab,paths.most_common(20))
for lab,k in [('VIE27',0),('JUE26',1),('LUN23',4)]:
    a=HOY-D(days=k); informe('MISMAHORA_'+lab,a,a+corte)
for lab,k in [('JUE26',1),('LUN23',4)]:
    a=HOY-D(days=k); hv=sum(r['sum']['visits'] for r in grp(['date'],5,Z(a),Z(a+D(days=1))))
    print('DIA_COMPLETO',lab,hv)
    hh=collections.Counter()
    for r in grp(['datetimeHour'],50,Z(a),Z(a+D(days=1))): hh[hora(r)]+=r['sum']['visits']
    print('HORA_COMPLETA',lab,sorted(hh.items()))
