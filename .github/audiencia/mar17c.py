# Temporal, solo lectura: audiencia 17-11 a media jornada. No se fusiona a main. (2)
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
print('CORTE',Z(now),corte)
def tot(a,b,extra=''):
    g=grp(['date'],10,Z(a),Z(b),extra); return sum(r['sum']['visits'] for r in g),sum(r['count'] for r in g)
ENC=',{requestPath:"/encuestas/"}'; GO=',{refererHost_like:"%google%"}'
for k,lab in [(0,'HOY'),(1,'LUN16'),(7,'MAR10')]:
    a=D0-datetime.timedelta(days=k); b=a+corte
    print('TOT',lab,tot(a,b),'ENC',tot(a,b,ENC),'ENC_GOOGLE',tot(a,b,ENC+GO))
    for r in grp(['requestPath'],12,Z(a),Z(b)): print('PATH',lab,r['sum']['visits'],r['dimensions']['requestPath'])
    ref=collections.Counter()
    for r in grp(['refererHost'],5000,Z(a),Z(b)):
        h=r['dimensions']['refererHost'] or '(directo)'; h='google' if 'google' in h else h; ref[h]+=r['sum']['visits']
    print('REF',lab,sum(ref.values()),ref.most_common(6))
for k in [0,1,7]:
    a=D0-datetime.timedelta(days=k)
    for nm,ex in [('GOOGLE',ENC+GO),('TOTAL',ENC)]:
        h=collections.Counter()
        for r in grp(['datetimeHour'],50,Z(a),Z(a+corte),ex):
            t=datetime.datetime.strptime(r['dimensions']['datetimeHour'][:13],'%Y-%m-%dT%H')+datetime.timedelta(hours=1); h[t.hour]+=r['sum']['visits']
        print('ENC_HORA_MADRID',nm,(a+datetime.timedelta(hours=1)).date(),sorted(h.items()))
