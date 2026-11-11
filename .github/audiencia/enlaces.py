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
def grp(dims,limit,t1,t2,extra=''):
    f='{AND:[{siteTag:"%s"},{datetime_geq:"%s"},{datetime_lt:"%s"},{requestPath_notin:%s}%s]}'%(SITE,t1,t2,json.dumps(EXC),extra)
    q='{viewer{accounts(filter:{accountTag:"%s"}){g:rumPageloadEventsAdaptiveGroups(limit:%d,filter:%s,orderBy:[sum_visits_DESC]){count sum{visits} dimensions{%s}}}}}'%(ACC,limit,f,' '.join(dims))
    return gql(q)
BUSC=['google','bing','yahoo','duckduckgo','ecosia','brave','yandex','baidu','qwant','startpage','mapaelectoral','localhost','127.0.0.1','msn.com','search']
host=collections.Counter(); hp=collections.Counter(); first={}
for a,b in [('2026-10-08T00:00:00Z','2026-11-07T00:00:00Z'),('2026-11-07T00:00:00Z','2026-11-11T12:00:00Z')]:
    for r in grp(['refererHost','requestPath','date'],9999,a,b,',{refererHost_neq:""}'):
        h=r['dimensions']['refererHost']
        if any(x in h for x in BUSC): continue
        v=r['sum']['visits']; host[h]+=v; hp[(h,r['dimensions']['requestPath'])]+=v
        d=r['dimensions']['date']; first[h]=min(first.get(h,d),d)
for h,v in host.most_common(): print('CFHOST',v,first[h],h)
for (h,p),v in hp.most_common(80): print('CFHP',v,h,p)
K=os.environ.get('BK1') or os.environ.get('BK2')
API='https://ssl.bing.com/webmaster/api.svc/json/'
def bing(m,**kw):
    kw.update(siteUrl='https://mapaelectoral.es/',apikey=K)
    try: return json.loads(urllib.request.urlopen(API+m+'?'+urllib.parse.urlencode(kw),timeout=60).read().decode())
    except Exception as e: return {'ERR':str(e)}
for pg in range(5):
    d=bing('GetLinkCounts',page=pg); print('BLC',pg,json.dumps(d)[:3000])
    links=(d.get('d') or {}).get('Links') or []
    if not links: break
    for l in links:
        u=l.get('Url'); print('BURL',l.get('Count'),u)
        for p2 in range(3):
            e=bing('GetUrlLinks',link=u,page=p2); dd=(e.get('d') or {}).get('Details') or []
            for x in dd: print('BSRC',u,x.get('Url'),x.get('AnchorText'))
            if not dd: 
                if p2==0: print('BSRCRAW',json.dumps(e)[:500])
                break
