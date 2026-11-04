import os,json,re,time,base64,urllib.request,urllib.parse,collections
ACC='dee996483598974c337d0777f5ef047c'; SITE='532b57a6348a4babba29020993949dd7'
EXC=['/encuestas/calculadora-escanos/','/encuestas/simulador-pactos/']
raw=os.environ.get('CF','')
tok=next((p.strip().strip('"\'') for p in raw.split() if p.strip().strip('"\'').startswith('cfut_')), raw.strip().strip('"\''))
def gql(q):
    r=urllib.request.Request('https://api.cloudflare.com/client/v4/graphql',json.dumps({'query':q}).encode(),{'Authorization':'Bearer '+tok,'Content-Type':'application/json'})
    d=json.load(urllib.request.urlopen(r))
    if d.get('errors'): print('ERR',d['errors']); return []
    return d['data']['viewer']['accounts'][0]['g']
def grp(d1,d2,dims,limit=1000,extra=''):
    f='{AND:[{siteTag:"%s"},{date_geq:"%s"},{date_leq:"%s"},{requestPath_notin:%s}%s]}'%(SITE,d1,d2,json.dumps(EXC),extra)
    q='{viewer{accounts(filter:{accountTag:"%s"}){g:rumPageloadEventsAdaptiveGroups(limit:%d,filter:%s,orderBy:[sum_visits_DESC]){count sum{visits} dimensions{%s}}}}}'%(ACC,limit,f,' '.join(dims))
    return gql(q)
print('=== DIARIO')
for a,b in [('2026-10-08','2026-10-31'),('2026-11-01','2026-11-04')]:
    for r in sorted(grp(a,b,['date']),key=lambda r:r['dimensions']['date']): print(r['dimensions']['date'],r['sum']['visits'],r['count'])
def cat(p):
    m=re.match(r'^/([^/]+)/',p or '/')
    return m.group(1) if m else p
for d in ['2026-10-30','2026-11-01','2026-11-02','2026-11-03','2026-11-04']:
    rows=grp(d,d,['requestPath','refererHost'],5000)
    print('\n=== DIA',d)
    c=collections.Counter(); ref=collections.Counter(); pth=collections.Counter()
    for r in rows:
        p=r['dimensions']['requestPath']; v=r['sum']['visits']
        k=cat(p)
        if p.startswith('/municipio/') or p.startswith('/elecciones/'): k=p.split('/')[1]
        c[k]+=v; ref[r['dimensions']['refererHost'] or '(directo)']+=v; pth[p]+=v
    print('secciones',c.most_common(15)); print('referers',ref.most_common(12))
    for p,v in pth.most_common(30): print('  ',v,p)
for d in ['2026-11-02','2026-11-03','2026-11-04']:
    print('\n=== HORAS',d)
    for r in sorted(grp(d,d,['datetimeHour']),key=lambda r:r['dimensions']['datetimeHour']): print(r['dimensions']['datetimeHour'],r['sum']['visits'])
print('\n=== DISPOSITIVO/PAIS 2-3 nov')
print([(r['dimensions'],r['sum']['visits']) for r in grp('2026-11-02','2026-11-03',['deviceType'])])
print([(r['dimensions'],r['sum']['visits']) for r in grp('2026-11-02','2026-11-03',['countryName'],10)])
# --- GSC
em=os.environ.get('GSC_CLIENT_EMAIL','').strip().strip('"'); pk=os.environ.get('GSC_PRIVATE_KEY','').strip().strip('"').replace('\\n','\n')
if not em: print('\nGSC: sin secretos'); raise SystemExit
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
b=lambda d: base64.urlsafe_b64encode(d).rstrip(b'=')
now=int(time.time())
h=b(json.dumps({'alg':'RS256','typ':'JWT'}).encode()); cl=b(json.dumps({'iss':em,'scope':'https://www.googleapis.com/auth/webmasters.readonly','aud':'https://oauth2.googleapis.com/token','iat':now,'exp':now+3600}).encode())
key=serialization.load_pem_private_key(pk.encode(),None)
sig=b(key.sign(h+b'.'+cl,padding.PKCS1v15(),hashes.SHA256()))
gt=json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token',urllib.parse.urlencode({'grant_type':'urn:ietf:params:oauth:grant-type:jwt-bearer','assertion':(h+b'.'+cl+b'.'+sig).decode()}).encode()))['access_token']
def q(body):
    r=urllib.request.Request('https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Amapaelectoral.es/searchAnalytics/query',json.dumps(body).encode(),{'Authorization':'Bearer '+gt,'Content-Type':'application/json'})
    return json.load(urllib.request.urlopen(r)).get('rows',[])
print('\n=== GSC DIARIO')
for r in q({'startDate':'2026-10-20','endDate':'2026-11-04','dimensions':['date'],'dataState':'all'}): print(r['keys'][0],r['clicks'],r['impressions'],round(r['position'],1))
for d1,d2 in [('2026-11-02','2026-11-03')]:
    rs=q({'startDate':d1,'endDate':d2,'dimensions':['query'],'rowLimit':5000,'dataState':'all'})
    print('\n=== GSC CONSULTAS',d1,d2,len(rs),'filas, clics',sum(r['clicks'] for r in rs))
    tem=collections.Counter(); imp=collections.Counter()
    pats={'mesa':r'mesa','censo/donde voto':r'censo|d[oó]nde (me toca )?vot|colegio electoral','resultados':r'resultad','eeuu/midterms':r'ee ?uu|estados unidos|midterm|senado eeuu|trump|congreso eeuu|usa','encuesta':r'encuest|sondeo|cis','voto correo':r'correo','listas/candidatos':r'lista|candidat','mapa':r'mapa'}
    for r in rs:
        k=next((n for n,p in pats.items() if re.search(p,r['keys'][0])),'otras')
        tem[k]+=r['clicks']; imp[k]+=r['impressions']
    print({k:(tem[k],imp[k]) for k in tem})
    for r in sorted(rs,key=lambda r:-r['clicks'])[:50]: print('  ',r['clicks'],r['impressions'],round(r['position'],1),r['keys'][0])
    ps=q({'startDate':d1,'endDate':d2,'dimensions':['page'],'rowLimit':5000,'dataState':'all'})
    pc=collections.Counter()
    for r in ps: pc[r['keys'][0].split('/')[3] if r['keys'][0].count('/')>3 else '/']+=r['clicks']
    print('GSC paginas por seccion',pc.most_common(12))
# rising queries last 7d vs previous, by theme, for upcoming spikes
rs=q({'startDate':'2026-10-28','endDate':'2026-11-04','dimensions':['query'],'rowLimit':10000,'dataState':'all'})
print('\n=== GSC 28oct-4nov impresiones altas pos>5 (oportunidades)')
for r in sorted([r for r in rs if r['position']>5],key=lambda r:-r['impressions'])[:60]: print('  ',r['clicks'],r['impressions'],round(r['position'],1),r['keys'][0])
for st in ['discover','news']:
  try: r=q({'startDate':'2026-10-20','endDate':'2026-11-04','type':st,'dimensions':['date']}); print(st,[(x['keys'][0],x['clicks']) for x in r])
  except Exception as e: print(st,'ERR',e)
