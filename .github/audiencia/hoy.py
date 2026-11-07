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
def grp(dims,limit=5000,d1='2026-10-28',d2='2026-11-07',extra=''):
    f='{AND:[{siteTag:"%s"},{date_geq:"%s"},{date_leq:"%s"},{requestPath_notin:%s}%s]}'%(SITE,d1,d2,json.dumps(EXC),extra)
    q='{viewer{accounts(filter:{accountTag:"%s"}){g:rumPageloadEventsAdaptiveGroups(limit:%d,filter:%s,orderBy:[sum_visits_DESC]){count sum{visits} dimensions{%s}}}}}'%(ACC,limit,f,' '.join(dims))
    return gql(q)
for r in sorted(grp(['date']),key=lambda r:r['dimensions']['date']): print('DIA',r['dimensions']['date'],r['sum']['visits'],r['count'])
H='2026-11-07'
for d in ['2026-11-07','2026-11-06','2026-10-31']:
    hh=collections.Counter()
    for r in grp(['datetimeHour'],d1=d,d2=d): hh[r['dimensions']['datetimeHour'][11:13]]+=r['sum']['visits']
    print('HORAS',d,sorted(hh.items()))
for r in grp(['requestPath'],50,d1=H,d2=H): print('PATH',r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
for r in grp(['requestPath'],5000,d1=H,d2=H,extra=',{requestPath_like:"/actualidad/%"}'): print('ACT',r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
for r in grp(['requestPath'],5000,d1=H,d2=H,extra=',{requestPath_like:"/internacional/%"}'): print('INT',r['sum']['visits'],r['count'],r['dimensions']['requestPath'])
ref=collections.Counter()
for r in grp(['refererHost'],d1=H,d2=H):
    h=r['dimensions']['refererHost'] or '(directo)'; h='google' if 'google' in h else h; ref[h]+=r['sum']['visits']
print('REF',ref.most_common(10))
for s in ['mestalla','cinco-semanas','semana-en-el-mapa','eeuu','medio-mandato']:
    rs=grp(['requestPath','date'],500,d1='2026-11-06',d2=H,extra=',{requestPath_like:"%%%s%%"}'%s)
    print('SLUG',s,[(r['dimensions']['date'],r['dimensions']['requestPath'],r['sum']['visits'],r['count']) for r in rs])
for dims in (['refererPath','requestPath'],['refererPath'],['requestPath','datetimeHour']):
    rs=grp(dims,50,d1=H,d2=H,extra=',{refererHost_like:"%abc.es%"}')
    print('ABC',dims,[(r['dimensions'],r['sum']['visits']) for r in rs])
rs=grp(['refererHost','refererPath','requestPath'],2000,d1='2026-10-08',d2=H)
agg=collections.defaultdict(lambda:[0,collections.Counter(),collections.Counter(),set()])
for r in rs:
    d=r['dimensions']; h=d['refererHost'] or ''
    if not h or any(x in h for x in ['google','bing','mapaelectoral','duckduckgo','yahoo','ecosia','brave','yandex','qwant','baidu','startpage']): continue
    a=agg[h]; a[0]+=r['sum']['visits']; a[1][d['requestPath']]+=r['sum']['visits']; a[2][d['refererPath']]+=r['sum']['visits']
for h,a in sorted(agg.items(),key=lambda x:-x[1][0])[:40]: print('REFH',h,a[0],a[1].most_common(4),a[2].most_common(4))
rs=grp(['refererHost','date'],2000,d1='2026-10-08',d2=H)
for r in rs:
    h=r['dimensions']['refererHost'] or ''
    if h in [x for x,a in sorted(agg.items(),key=lambda x:-x[1][0])[:15]]: print('REFD',h,r['dimensions']['date'],r['sum']['visits'])
