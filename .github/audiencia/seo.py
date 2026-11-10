import json,collections,urllib.request,urllib.parse,os
raw=os.environ.get('CF','')
tok=next((p.strip().strip('"\'') for p in raw.split() if p.strip().strip('"\'').startswith('cfut_')), raw.strip().strip('"\''))
ACC='dee996483598974c337d0777f5ef047c'; SITE='532b57a6348a4babba29020993949dd7'
EXC=['/encuestas/calculadora-escanos/','/encuestas/simulador-pactos/']
def gql(q):
    r=urllib.request.Request('https://api.cloudflare.com/client/v4/graphql',json.dumps({'query':q}).encode(),{'Authorization':'Bearer '+tok,'Content-Type':'application/json'})
    d=json.load(urllib.request.urlopen(r))
    if d.get('errors'): print('ERR',d['errors']); return []
    return d['data']['viewer']['accounts'][0]['g']
def grp(dims,limit=5000,d1='2026-10-27',d2='2026-11-09',extra=''):
    f='{AND:[{siteTag:"%s"},{date_geq:"%s"},{date_leq:"%s"},{requestPath_notin:%s}%s]}'%(SITE,d1,d2,json.dumps(EXC),extra)
    q='{viewer{accounts(filter:{accountTag:"%s"}){g:rumPageloadEventsAdaptiveGroups(limit:%d,filter:%s,orderBy:[sum_visits_DESC]){count sum{visits} dimensions{%s}}}}}'%(ACC,limit,f,' '.join(dims))
    return gql(q)
mad=collections.Counter(); otr=collections.Counter(); provs=collections.Counter()
for r in grp(['date','requestPath'],10000,extra=',{requestPath_like:"/municipio/%"}'):
    p=r['dimensions']['requestPath']; d=r['dimensions']['date']; v=r['sum']['visits']
    parts=p.strip('/').split('/')
    if len(parts)<3: continue
    (mad if parts[1]=='madrid' else otr)[d]+=v; provs[parts[1]]+=v
for d in sorted(set(mad)|set(otr)): print('MUNI',d,'madrid',mad[d],'resto',otr[d])
print('PROVS',provs.most_common(25))
for r in grp(['requestPath'],60,extra=',{requestPath_like:"/elecciones/%"}'): print('ELEC',r['sum']['visits'],r['dimensions']['requestPath'])
for r in grp(['requestPath'],40,d1='2026-11-03',d2='2026-11-09'): print('TOP7',r['sum']['visits'],r['dimensions']['requestPath'])
ref=collections.Counter()
for r in grp(['refererHost'],d1='2026-11-03',d2='2026-11-09'):
    h=r['dimensions']['refererHost'] or '(directo)'; h='google' if 'google' in h else h; ref[h]+=r['sum']['visits']
print('REF7',ref.most_common(20))
K=os.environ.get('BK','').strip()
def bing(m,**kw):
    q=urllib.parse.urlencode(dict(siteUrl='https://mapaelectoral.es/',apikey=K,**kw))
    try: return json.load(urllib.request.urlopen('https://ssl.bing.com/webmaster/api.svc/json/%s?%s'%(m,q),timeout=60)).get('d')
    except Exception as e: return 'ERR %s'%e
st=bing('GetRankAndTrafficStats'); print('BING_TRAFICO',json.dumps(st[-14:] if isinstance(st,list) else st)[:3000])
cr=bing('GetCrawlStats'); print('BING_CRAWL',json.dumps(cr[-10:] if isinstance(cr,list) else cr)[:3000])
for m in ['GetQueryStats','GetPageStats']:
    qs=bing(m)
    if isinstance(qs,list):
        qs.sort(key=lambda x:-x.get('Impressions',0))
        for x in qs[:40]: print('BING_'+m,x.get('Impressions'),x.get('Clicks'),x.get('AvgImpressionPosition'),x.get('Query'))
    else: print('BING_'+m,qs)
