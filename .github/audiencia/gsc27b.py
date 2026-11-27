# Temporal, solo lectura. No se fusiona a main.
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
def f(r): return '%s | %d | %d | %.1f%% | %.1f'%(' / '.join(r.get('keys',[])).replace(U,''),r['clicks'],r['impressions'],100*r['ctr'],r['position'])
for t in ['debate','audiencia','gan']:
    rows=q({'startDate':'2026-11-26','endDate':'2026-11-27','dimensions':['query','page'],'dimensionFilterGroups':[{'filters':[{'dimension':'query','operator':'contains','expression':t}]}],'rowLimit':25,'dataState':'all'})
    print('== TERMINO',t,'impr',sum(r['impressions'] for r in rows))
    for r in rows: print('  ',f(r))
print('== DEBATE PIEZA por hora')
for r in q({'startDate':'2026-11-26','endDate':'2026-11-27','dimensions':['hour'],'dimensionFilterGroups':[{'filters':[{'dimension':'page','operator':'contains','expression':'debate'}]}],'dataState':'hourly_all'}): print(f(r))
print('== SITIO por hora')
for r in q({'startDate':'2026-11-27','endDate':'2026-11-27','dimensions':['hour'],'dataState':'hourly_all'}): print(f(r))
