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
for r in sorted(grp(['date']),key=lambda r:r['dimensions']['date']): print('DIA',r['dimensions']['date'],r['sum']['visits'],r['count'])
H='2026-11-09'
for d in ['2026-11-09','2026-11-08','2026-11-02']:
    hh=collections.Counter()
    for r in grp(['datetimeHour'],d1=d,d2=d): hh[r['dimensions']['datetimeHour'][11:13]]+=r['sum']['visits']
    print('HORAS_UTC',d,sorted(hh.items()))
for r in grp(['requestPath'],40,d1=H,d2=H): print('PATH',r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
sec=collections.Counter()
for r in grp(['requestPath'],5000,d1=H,d2=H):
    p=r['dimensions']['requestPath']; s=p.strip('/').split('/')[0] or '(portada)'; sec[s]+=r['sum']['visits']
print('SECCIONES',sec.most_common(15))
for r in grp(['requestPath'],5000,d1=H,d2=H,extra=',{requestPath_like:"/actualidad/%"}'): print('ACT',r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
for r in grp(['requestPath'],5000,d1=H,d2=H,extra=',{requestPath_like:"/internacional/%"}'): print('INT',r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
for s in ['40db','huelga','seccion','encuestas']:
    hh=collections.Counter()
    for r in grp(['requestPath','datetimeHour'],500,d1=H,d2=H,extra=',{requestPath_like:"%%%s%%"}'%s): hh[(r['dimensions']['requestPath'],r['dimensions']['datetimeHour'][11:13])]+=r['sum']['visits']
    print('SLUGH',s,sorted(hh.items()))
for d in [H,'2026-11-08','2026-11-02']:
    ref=collections.Counter()
    for r in grp(['refererHost'],d1=d,d2=d):
        h=r['dimensions']['refererHost'] or '(directo)'; h='google' if 'google' in h else h; ref[h]+=r['sum']['visits']
    print('REF',d,ref.most_common(12))
dev=collections.Counter()
for r in grp(['deviceType'],d1=H,d2=H): dev[r['dimensions']['deviceType']]+=r['sum']['visits']
print('DEV',dev.most_common())

for r in grp(['refererHost','refererPath'],60,d1=H,d2=H,extra=',{refererHost_notlike:"%google%"}'): print('REFP',r['sum']['visits'],r['dimensions']['refererHost'],r['dimensions']['refererPath'])
