import json,urllib.request,urllib.parse
for q in ['mapaelectoral.es','mapaelectoral','"mapa electoral" 29N','"Mapa Electoral" encuestas']:
    for base in ['https://public.api.bsky.app','https://api.bsky.app']:
        try:
            u=base+'/xrpc/app.bsky.feed.searchPosts?'+urllib.parse.urlencode({'q':q,'limit':60,'sort':'latest','since':'2026-11-01T00:00:00Z'})
            d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30))
            print('Q',q,base,len(d.get('posts',[])))
            for p in d.get('posts',[]):
                r=p['record']; t=r.get('text','').replace('\n',' ')
                emb=json.dumps(p.get('embed',{}))
                hit='LINK' if 'mapaelectoral' in emb or 'mapaelectoral' in json.dumps(r) else ''
                print('BS',r.get('createdAt','')[:16],p['author']['handle'],'L%s R%s'%(p.get('likeCount'),p.get('repostCount')),hit,'|',t[:220],'| https://bsky.app/profile/%s/post/%s'%(p['author']['handle'],p['uri'].split('/')[-1]))
            break
        except Exception as e: print('ERR',q,base,e)
