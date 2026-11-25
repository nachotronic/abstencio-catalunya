# Temporal, solo lectura: posicion portada. No se fusiona a main.
import json,os,requests,collections
from google.oauth2 import service_account
from google.auth.transport.requests import Request
c=service_account.Credentials.from_service_account_info(json.loads(os.environ['GSC_CREDENTIALS']),scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
c.refresh(Request())
U='https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Amapaelectoral.es/searchAnalytics/query'
def q(body):
    r=requests.post(U,json=body,headers={'Authorization':'Bearer '+c.token}); r.raise_for_status(); return r.json().get('rows',[])
def f(r): return '%s clics=%d impr=%d ctr=%.1f%% pos=%.1f'%('|'.join(r.get('keys',[])),r['clicks'],r['impressions'],100*r['ctr'],r['position'])
P=[{'filters':[{'dimension':'page','operator':'equals','expression':'https://mapaelectoral.es/'}]}]
for r in q({'startDate':'2026-11-11','endDate':'2026-11-25','dimensions':['date'],'dimensionFilterGroups':P,'dataState':'all'}): print('PORTADA',f(r))
for kw in ['mapa electoral','mapa electoral españa','mapa electoral españa 2026','mapa elecciones','mapa elecciones generales 2026','mapa votos españa']:
    G=[{'filters':[{'dimension':'query','operator':'equals','expression':kw}]}]
    for r in q({'startDate':'2026-11-11','endDate':'2026-11-25','dimensions':['date'],'dimensionFilterGroups':G,'dataState':'all'}): print('KW',kw,f(r))
for a,b in [('2026-11-11','2026-11-17'),('2026-11-18','2026-11-24')]:
    for r in q({'startDate':a,'endDate':b,'dimensions':['query'],'dimensionFilterGroups':P+[{'filters':[{'dimension':'query','operator':'contains','expression':'mapa'}]}],'rowLimit':15,'dataState':'all'}): print('SEM',a,f(r))
for r in q({'startDate':'2026-11-18','endDate':'2026-11-24','dimensions':['query','page'],'dimensionFilterGroups':[{'filters':[{'dimension':'query','operator':'contains','expression':'mapa elec'}]}],'rowLimit':15,'dataState':'all'}): print('MAPAELEC_PAG',f(r))
