import json,collections,urllib.request,os
raw=os.environ.get('CF','')
tok=next((p.strip().strip('"\'') for p in raw.split() if p.strip().strip('"\'').startswith('cfut_')), raw.strip().strip('"\''))
ACC='dee996483598974c337d0777f5ef047c'; SITE='532b57a6348a4babba29020993949dd7'
EXC=['/encuestas/calculadora-escanos/','/encuestas/simulador-pactos/']
D1,D2='2026-10-31','2026-11-06'
def gql(q):
    r=urllib.request.Request('https://api.cloudflare.com/client/v4/graphql',json.dumps({'query':q}).encode(),{'Authorization':'Bearer '+tok,'Content-Type':'application/json'})
    d=json.load(urllib.request.urlopen(r))
    if d.get('errors'): print('ERR',d['errors']); return []
    return d['data']['viewer']['accounts'][0]['g']
def grp(dims,limit=5000,d1=D1,d2=D2,exc=True):
    f='{AND:[{siteTag:"%s"},{date_geq:"%s"},{date_leq:"%s"}%s]}'%(SITE,d1,d2,(',{requestPath_notin:%s}'%json.dumps(EXC)) if exc else '')
    q='{viewer{accounts(filter:{accountTag:"%s"}){g:rumPageloadEventsAdaptiveGroups(limit:%d,filter:%s,orderBy:[sum_visits_DESC]){count sum{visits} dimensions{%s}}}}}'%(ACC,limit,f,' '.join(dims))
    return gql(q)
print('SEMANA',D1,'a',D2,'(sin calculadora ni simulador)')
dia=sorted(grp(['date']),key=lambda r:r['dimensions']['date'])
for r in dia: print('DIA',r['dimensions']['date'],'visitas',r['sum']['visits'],'vistas',r['count'])
print('TOTAL visitas',sum(r['sum']['visits'] for r in dia),'vistas',sum(r['count'] for r in dia))
bruto=grp(['date'],exc=False); print('BRUTO (con calc/sim) vistas',sum(r['count'] for r in bruto),'visitas',sum(r['sum']['visits'] for r in bruto))
hoy=grp(['date'],d1='2026-11-07',d2='2026-11-07'); print('HOY 7-11 parcial',[(r['sum']['visits'],r['count']) for r in hoy])
for r in grp(['requestPath'],30): print('PATH',r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
ref=collections.Counter()
for r in grp(['refererHost']):
    h=r['dimensions']['refererHost'] or '(directo)'; h='google' if 'google' in h else h; ref[h]+=r['sum']['visits']
print('REFERERS',ref.most_common(12))
print('DISP',[(r['dimensions']['deviceType'],r['sum']['visits']) for r in grp(['deviceType'])])
print('PAIS',[(r['dimensions']['countryName'],r['sum']['visits']) for r in grp(['countryName'],6)])
