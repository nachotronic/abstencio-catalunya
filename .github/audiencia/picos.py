import json,re,collections,urllib.request,sys,os
raw=os.environ.get('CF','')
tok=next((p.strip().strip('"\'') for p in raw.split() if p.strip().strip('"\'').startswith('cfut_')), raw.strip().strip('"\''))
ACC='dee996483598974c337d0777f5ef047c'; SITE='532b57a6348a4babba29020993949dd7'
EXC=['/encuestas/calculadora-escanos/','/encuestas/simulador-pactos/']
def gql(q):
    r=urllib.request.Request('https://api.cloudflare.com/client/v4/graphql',json.dumps({'query':q}).encode(),{'Authorization':'Bearer '+tok,'Content-Type':'application/json'})
    d=json.load(urllib.request.urlopen(r))
    if d.get('errors'): print('ERR',d['errors']); return []
    return d['data']['viewer']['accounts'][0]['g']
def grp(t1,t2,dims,limit=5000):
    f='{AND:[{siteTag:"%s"},{datetime_geq:"%s"},{datetime_lt:"%s"},{requestPath_notin:%s}]}'%(SITE,t1,t2,json.dumps(EXC))
    q='{viewer{accounts(filter:{accountTag:"%s"}){g:rumPageloadEventsAdaptiveGroups(limit:%d,filter:%s,orderBy:[sum_visits_DESC]){count sum{visits} dimensions{%s}}}}}'%(ACC,limit,f,' '.join(dims))
    return gql(q)
H='16' # hora UTC fin, e.g. 09
for d in ['2026-11-04','2026-11-05']:
    rows=grp(f'{d}T00:00:00Z',f'{d}T{H}:00:00Z',['requestPath','refererHost'])
    sec=collections.Counter(); ref=collections.Counter(); pth=collections.Counter(); prov=collections.Counter()
    tot=0
    for r in rows:
        p=r['dimensions']['requestPath']; v=r['sum']['visits']; tot+=v
        k=(p.split('/')[1] or '/') if p.count('/')>=2 else p
        sec[k]+=v; pth[p]+=v
        h=r['dimensions']['refererHost'] or '(directo)'
        h='google' if 'google' in h else h
        ref[h]+=v
        if p.startswith('/municipio/') and p.count('/')>=4: prov[p.split('/')[2]]+=v
    print('\n===',d,'hasta',H,'UTC total',tot)
    print('secciones',sec.most_common(12)); print('referers',ref.most_common(10)); print('provincias',prov.most_common(10))
    for p,v in pth.most_common(25): print('  ',v,p)
for d in ['2026-11-04','2026-11-05']:
    print('horas',d,[(r['dimensions']['datetimeHour'][11:13],r['sum']['visits']) for r in sorted(grp(f'{d}T00:00:00Z',f'{d}T{H}:00:00Z',['datetimeHour']),key=lambda r:r['dimensions']['datetimeHour'])])

for d in ['2026-11-04','2026-11-05']:
    print('disp',d,[(r['dimensions'],r['sum']['visits']) for r in grp(f'{d}T00:00:00Z',f'{d}T{H}:00:00Z',['deviceType'])])
    print('pais',d,[(r['dimensions'],r['sum']['visits']) for r in grp(f'{d}T00:00:00Z',f'{d}T{H}:00:00Z',['countryName'],6)])
for d1,d2 in [('2026-10-29','2026-11-05')]:
    f='{AND:[{siteTag:"%s"},{date_geq:"%s"},{date_leq:"%s"}]}'%(SITE,d1,d2)
    q='{viewer{accounts(filter:{accountTag:"%s"}){g:rumPageloadEventsAdaptiveGroups(limit:100,filter:%s){sum{visits} dimensions{date}}}}}'%(ACC,f)
    print('diario',sorted((r['dimensions']['date'],r['sum']['visits']) for r in gql(q)))

RUT=['/actualidad/voto-correo-29n/','/elecciones/tarjeta-censal-29n/','/elecciones/mesa-electoral-29n/','/elecciones/voto-por-correo-29n/','/elecciones/votar-29n/']
for d in ['2026-11-04','2026-11-05']:
    rows=grp(f'{d}T00:00:00Z',f'{d}T{H}:00:00Z',['requestPath','refererHost'],10000)
    print('\nRUTAS',d)
    for r0 in RUT:
        v=sum(r['sum']['visits'] for r in rows if r['dimensions']['requestPath']==r0)
        c=sum(r['count'] for r in rows if r['dimensions']['requestPath']==r0)
        ci=sum(r['count'] for r in rows if r['dimensions']['requestPath']==r0 and 'mapaelectoral' in (r['dimensions']['refererHost'] or ''))
        print(f'  {r0}: visitas {v}, paginas vistas {c}, desde la propia web {ci}')
    tot=sum(r['count'] for r in rows); intr=sum(r['count'] for r in rows if 'mapaelectoral' in (r['dimensions']['refererHost'] or ''))
    print('  paginas vistas totales',tot,'internas',intr)
