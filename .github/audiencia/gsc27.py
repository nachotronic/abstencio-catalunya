# Temporal, solo lectura: Search Console 27-11. No se fusiona a main.
import json,os,requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
c=service_account.Credentials.from_service_account_info(json.loads(os.environ['GSC_CREDENTIALS']),scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
c.refresh(Request())
U='https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Amapaelectoral.es/searchAnalytics/query'
def q(body):
    r=requests.post(U,json=body,headers={'Authorization':'Bearer '+c.token}); r.raise_for_status(); return r.json().get('rows',[])
def f(r): return '%s clics=%d impr=%d pos=%.1f'%('|'.join(r.get('keys',[])),r['clicks'],r['impressions'],r['position'])
for r in q({'startDate':'2026-11-25','endDate':'2026-11-27','dimensions':['date'],'dataState':'all'}): print('DIA',f(r))
for d in ['2026-11-26','2026-11-27']:
    for r in q({'startDate':d,'endDate':d,'dimensions':['query'],'rowLimit':30,'dataState':'all'}): print('Q',d,f(r))
    for r in q({'startDate':d,'endDate':d,'dimensions':['page'],'rowLimit':15,'dataState':'all'}): print('PAG',d,f(r))
for pg in ['https://mapaelectoral.es/encuestas/','https://mapaelectoral.es/encuestas/barcelona/','https://mapaelectoral.es/encuestas/asturias/','https://mapaelectoral.es/encuestas/navarra/','https://mapaelectoral.es/']:
    flt=[{'filters':[{'dimension':'page','operator':'equals','expression':pg}]}]
    for d in ['2026-11-26','2026-11-27']:
        for r in q({'startDate':d,'endDate':d,'dimensions':['query'],'dimensionFilterGroups':flt,'rowLimit':6,'dataState':'all'}): print('PAGQ',d,pg,f(r))
for d in ['2026-11-26','2026-11-27']:
    flt=[{'filters':[{'dimension':'page','operator':'contains','expression':'voto-util-29n'}]}]
    for r in q({'startDate':d,'endDate':d,'dimensions':['query'],'dimensionFilterGroups':flt,'rowLimit':12,'dataState':'all'}): print('VUQ',d,f(r))
    tot=q({'startDate':d,'endDate':d,'dimensionFilterGroups':flt,'dataState':'all'}); print('VUTOT',d,[f(r) for r in tot])
