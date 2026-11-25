# Temporal, solo lectura: Search Console 24-11. No se fusiona a main.
import json,os,datetime
from urllib.parse import quote
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
c=service_account.Credentials.from_service_account_info(json.loads(os.environ['GSC_CREDENTIALS']),scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
s=AuthorizedSession(c); SITE='sc-domain:mapaelectoral.es'; U='https://mapaelectoral.es'
API='https://searchconsole.googleapis.com/webmasters/v3/sites/%s/searchAnalytics/query'%quote(SITE,safe='')
def q(body):
    r=s.post(API,json=body)
    if r.status_code!=200: print('ERR',r.status_code,r.text[:300]); return []
    return r.json().get('rows',[])
def f(r): return '%s | %d | %d | %.1f%% | %.1f'%(' / '.join(r.get('keys',[])),r['clicks'],r['impressions'],100*r['ctr'],r['position'])
hoy=datetime.date(2026,11,24); D=datetime.timedelta
def pf(p): return [{'filters':[{'dimension':'page','operator':'equals','expression':U+p}]}]
hoy=datetime.date(2026,11,25)
TER=['mapa','resultados','resultado','escrutinio','quien gana','quién gana','quien ha ganado','votos por','elecciones generales 2026','elecciones 2026','elecciones 29n','como van']
for t in TER:
    rows=q({'startDate':str(hoy-D(days=28)),'endDate':str(hoy),'dimensions':['query'],'dimensionFilterGroups':[{'filters':[{'dimension':'query','operator':'contains','expression':t}]}],'rowLimit':20,'dataState':'all'})
    print('== TERMINO',t,'impr top20',sum(r['impressions'] for r in rows))
    for r in rows: print('  ',f(r))
    for r in q({'startDate':str(hoy-D(days=28)),'endDate':str(hoy),'dimensions':['query','page'],'dimensionFilterGroups':[{'filters':[{'dimension':'query','operator':'contains','expression':t}]}],'rowLimit':12,'dataState':'all'}): print('   qp',f(r).replace(U,''))
for p in ['/','/elecciones/resultados-elecciones-generales-2026/','/elecciones/','/generales-2026/','/elecciones/generales-2023/']:
    print('== PAGINA',p)
    for r in q({'startDate':str(hoy-D(days=7)),'endDate':str(hoy),'dimensions':['date'],'dimensionFilterGroups':pf(p),'dataState':'all'}): print('  dia',f(r))
    for r in q({'startDate':str(hoy-D(days=28)),'endDate':str(hoy),'dimensions':['device'],'dimensionFilterGroups':pf(p),'dataState':'all'}): print('  dev',f(r))
    for r in q({'startDate':str(hoy-D(days=28)),'endDate':str(hoy),'dimensions':['query'],'dimensionFilterGroups':pf(p),'rowLimit':25,'dataState':'all'}): print('  q',f(r))
