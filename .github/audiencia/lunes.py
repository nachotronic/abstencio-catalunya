import json,collections,urllib.request,os
raw=os.environ.get('CF','')
tok=next((p.strip().strip('"\'') for p in raw.split() if p.strip().strip('"\'').startswith('cfut_')), raw.strip().strip('"\''))
ACC='dee996483598974c337d0777f5ef047c'; SITE='532b57a6348a4babba29020993949dd7'
EXC=['/encuestas/calculadora-escanos/','/encuestas/simulador-pactos/']
def gql(q):
    r=urllib.request.Request('https://api.cloudflare.com/client/v4/graphql',json.dumps({'query':q}).encode(),{'Authorization':'Bearer '+tok,'Content-Type':'application/json'})
    d=json.load(urllib.request.urlopen(r))
    if d.get('errors'): print('ERR',d['errors']); return []
    return d['data']['viewer']['accounts'][0]['g']
def grp(dims,limit=5000,d1='2026-10-31',d2='2026-11-09',extra=''):
    f='{AND:[{siteTag:"%s"},{date_geq:"%s"},{date_leq:"%s"},{requestPath_notin:%s}%s]}'%(SITE,d1,d2,json.dumps(EXC),extra)
    q='{viewer{accounts(filter:{accountTag:"%s"}){g:rumPageloadEventsAdaptiveGroups(limit:%d,filter:%s,orderBy:[sum_visits_DESC]){count sum{visits} dimensions{%s}}}}}'%(ACC,limit,f,' '.join(dims))
    return gql(q)
H='2026-11-09'
for d in ['2026-11-09','2026-11-08','2026-11-07','2026-11-06']:
    for r in grp(['refererHost','requestPath','datetimeHour','deviceType'],200,d1=d,d2=d,extra=',{refererHost_like:"%facebook%"}'): print('FB',d,r['sum']['visits'],r['count'],r['dimensions'])
