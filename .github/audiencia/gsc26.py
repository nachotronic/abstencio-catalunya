# Temporal, solo lectura: Search Console 25-11. No se fusiona a main.
import json,os,requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
c=service_account.Credentials.from_service_account_info(json.loads(os.environ['GSC_CREDENTIALS']),scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
c.refresh(Request())
U='https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Amapaelectoral.es/searchAnalytics/query'
def q(body):
    r=requests.post(U,json=body,headers={'Authorization':'Bearer '+c.token}); r.raise_for_status(); return r.json().get('rows',[])
def f(r): return '%s clics=%d impr=%d ctr=%.1f%% pos=%.1f'%('|'.join(r.get('keys',[])),r['clicks'],r['impressions'],100*r['ctr'],r['position'])
for r in q({'startDate':'2026-11-22','endDate':'2026-11-26','dimensions':['date'],'dataState':'all'}): print('DIA',f(r))
for r in q({'startDate':'2026-11-25','endDate':'2026-11-26','dimensions':['date','hour'],'dataState':'hourly_all'}): print('HORA',f(r))
pg='https://mapaelectoral.es/actualidad/encuestas-andorra-29n/'
flt=[{'filters':[{'dimension':'page','operator':'equals','expression':pg}]}]
for r in q({'startDate':'2026-11-23','endDate':'2026-11-26','dimensions':['date'],'dimensionFilterGroups':flt,'dataState':'all'}): print('ANDDIA',f(r))
