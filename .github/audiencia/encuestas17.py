# Temporal, solo lectura: por qué baja /encuestas/ el 17-11. No se fusiona a main.
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
D0=datetime.datetime(2026,11,18,23); corte=now-D0
ENC=',{requestPath:"/encuestas/"}'
GO=',{refererHost_like:"%google%"}'
print('CORTE',Z(now))
for k in [0,1,2,8]:
    a=D0-datetime.timedelta(days=k); h=collections.Counter()
    for r in grp(['datetimeHour'],50,Z(a),Z(a+corte),ENC+GO):
        t=datetime.datetime.strptime(r['dimensions']['datetimeHour'][:13],'%Y-%m-%dT%H')+datetime.timedelta(hours=1); h[t.hour]+=r['sum']['visits']
    print('GOOGLE_HORA_MADRID',(a+datetime.timedelta(hours=1)).date(),sorted(h.items()))
    t=collections.Counter()
    for r in grp(['datetimeHour'],50,Z(a),Z(a+corte),ENC):
        x=datetime.datetime.strptime(r['dimensions']['datetimeHour'][:13],'%Y-%m-%dT%H')+datetime.timedelta(hours=1); t[x.hour]+=r['sum']['visits']
    print('TOTAL_HORA_MADRID',(a+datetime.timedelta(hours=1)).date(),sorted(t.items()))
