# Temporal, solo lectura: audiencia 25-11 tarde (18:38). No se fusiona a main.
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
HOY=datetime.datetime(2026,11,24,23)
corte=now-HOY
print('CORTE',Z(now),'madrid',(now+D(hours=1)).strftime('%H:%M'))
def hora(r): return (datetime.datetime.strptime(r['dimensions']['datetimeHour'][:13],'%Y-%m-%dT%H')+D(hours=1)).hour
def refn(h):
    h=h or '(directo)'
    if 'google' in h: return 'google'
    if h in ('t.co','x.com','twitter.com'): return 'x'
    if 'bing' in h: return 'bing'
    return h
def informe(lab,a,b):
    hv=collections.Counter(); ha=collections.Counter()
    for r in grp(['datetimeHour'],50,Z(a),Z(b)): hv[hora(r)]+=r['sum']['visits']
    for r in grp(['datetimeHour'],50,Z(a),Z(b),',{requestPath:"%s"}'%AND): ha[hora(r)]+=r['sum']['visits']
    print('TOT',lab,sum(hv.values()),'ANDORRA',sum(ha.values()),'RESTO',sum(hv.values())-sum(ha.values()))
    print('HORA',lab,sorted(hv.items()))
    print('HORA_AND',lab,sorted(ha.items()))
    ref=collections.Counter(); refa=collections.Counter()
    for r in grp(['refererHost','requestPath'],5000,Z(a),Z(b)):
        k=refn(r['dimensions']['refererHost']); ref[k]+=r['sum']['visits']
        if r['dimensions']['requestPath']==AND: refa[k]+=r['sum']['visits']
    print('REF',lab,sum(ref.values()),ref.most_common(8))
    print('REF_AND',lab,sum(refa.values()),refa.most_common(5))
    paths=collections.Counter()
    for r in grp(['requestPath'],5000,Z(a),Z(b)): paths[r['dimensions']['requestPath']]+=r['sum']['visits']
    print('TOP',lab,paths.most_common(15))
for lab,k in [('HOY25',0),('MAR24',1),('LUN23',2)]:
    a=HOY-D(days=k); informe('MISMAHORA_'+lab,a,a+corte)
for lab,k in [('MAR24',1),('LUN23',2)]:
    a=HOY-D(days=k); informe('DIA_'+lab,a,a+D(days=1))
