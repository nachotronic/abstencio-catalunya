# Temporal, solo lectura: 26-11 tarde. No se fusiona a main.
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
HOY=datetime.datetime(2026,11,25,23)
corte=now-HOY
print('CORTE',Z(now),'madrid',(now+D(hours=1)).strftime('%H:%M'))
def hora(r): return (datetime.datetime.strptime(r['dimensions']['datetimeHour'][:13],'%Y-%m-%dT%H')+D(hours=1)).hour
def refn(h):
    h=h or '(directo)'
def directo(lab,a,b):
    p=collections.Counter(); dev=collections.Counter(); pa=collections.Counter(); h=collections.Counter(); tot=0
    for r in grp(['requestPath','deviceType','countryName','datetimeHour'],10000,Z(a),Z(b),',{refererHost:""}'):
        v=r['sum']['visits']; d=r['dimensions']; tot+=v
        p[d['requestPath']]+=v; dev[d['deviceType']]+=v; pa[d['countryName']]+=v; h[hora(r)]+=v
    print('DIR',lab,tot); print('DIR_TOP',lab,p.most_common(20)); print('DIR_DEV',lab,dev.most_common()); print('DIR_PAIS',lab,pa.most_common(6)); print('DIR_HORA',lab,sorted(h.items()))
directo('HOY',HOY,now)
directo('MIE25',HOY-D(days=1),HOY-D(days=1)+corte)
