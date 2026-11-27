# Temporal, solo lectura: top paginas 27-11. No se fusiona a main.
import json,collections,urllib.request,os,datetime
raw=os.environ.get('CF','')
tok=next((p.strip().strip('"\'') for p in raw.split() if p.strip().strip('"\'').startswith('cfut_')), raw.strip().strip('"\''))
ACC='dee996483598974c337d0777f5ef047c'; SITE='532b57a6348a4babba29020993949dd7'
EXC=['/encuestas/calculadora-escanos/','/encuestas/simulador-pactos/']
def grp(t1,t2):
    f='{AND:[{siteTag:"%s"},{datetime_geq:"%s"},{datetime_lt:"%s"},{requestPath_notin:%s}]}'%(SITE,t1,t2,json.dumps(EXC))
    q='{viewer{accounts(filter:{accountTag:"%s"}){g:rumPageloadEventsAdaptiveGroups(limit:5000,filter:%s,orderBy:[sum_visits_DESC]){sum{visits} dimensions{requestPath}}}}}'%(ACC,f)
    r=urllib.request.Request('https://api.cloudflare.com/client/v4/graphql',json.dumps({'query':q}).encode(),{'Authorization':'Bearer '+tok,'Content-Type':'application/json'})
    d=json.load(urllib.request.urlopen(r))
    if d.get('errors'): print('ERR',d['errors']); return collections.Counter()
    c=collections.Counter()
    for x in d['data']['viewer']['accounts'][0]['g']: c[x['dimensions']['requestPath']]+=x['sum']['visits']
    return c
Z=lambda d:d.strftime('%Y-%m-%dT%H:%M:00Z'); D=datetime.timedelta
now=datetime.datetime.utcnow().replace(second=0,microsecond=0); HOY=datetime.datetime(2026,11,26,23); corte=now-HOY
print('CORTE madrid',(now+D(hours=1)).strftime('%H:%M'))
h=grp(Z(HOY),Z(now)); a=grp(Z(HOY-D(days=1)),Z(HOY-D(days=1)+corte))
print('TOT',sum(h.values()),sum(a.values()))
def tipo(p):
    if p=='/': return 'portada'
    if p.startswith('/encuestas/'): return 'encuestas_portada' if p=='/encuestas/' else 'encuestas_prov'
    if p.startswith('/actualidad/encuestas-andorra'): return 'andorra'
    if p.startswith('/actualidad/'): return 'actualidad'
    if p.startswith('/elecciones/'): return 'elecciones'
    if p.startswith('/municipio') or p.count('/')>=3: return 'fichas_otras'
    return 'otras'
th=collections.Counter(); ta=collections.Counter()
for p,v in h.items(): th[tipo(p)]+=v
for p,v in a.items(): ta[tipo(p)]+=v
for k in sorted(set(th)|set(ta),key=lambda k:-th[k]): print('TIPO',k,th[k],ta[k],th[k]-ta[k])
for p,v in h.most_common(40): print('TOP',p,v,a[p],v-a[p])
dif=collections.Counter({p:h[p]-a[p] for p in set(h)|set(a)})
for p,v in dif.most_common(25): print('SUBE',p,h[p],a[p],v)
for p,v in sorted(dif.items(),key=lambda x:x[1])[:10]: print('BAJA',p,h[p],a[p],v)
