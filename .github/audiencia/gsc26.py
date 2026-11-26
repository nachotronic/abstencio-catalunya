# Temporal, solo lectura: Search Console 26-11. No se fusiona a main.
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
hoy=datetime.date(2026,11,26); D=datetime.timedelta; ay=hoy-D(days=1)
def pf(p): return [{'filters':[{'dimension':'page','operator':'equals','expression':U+p}]}]
print('== SITIO POR DIA')
for r in q({'startDate':str(hoy-D(days=8)),'endDate':str(hoy),'dimensions':['date'],'dataState':'all'}): print(f(r))
print('== PAGINAS AYER')
for r in q({'startDate':str(ay),'endDate':str(ay),'dimensions':['page'],'rowLimit':30,'dataState':'all'}): print(f(r))
print('== QUERIES AYER top 60')
for r in q({'startDate':str(ay),'endDate':str(ay),'dimensions':['query'],'rowLimit':60,'dataState':'all'}): print(f(r))
print('== OPORTUNIDADES 23-25 (pos 3-20, impr>=40) query/page')
rows=q({'startDate':str(hoy-D(days=3)),'endDate':str(ay),'dimensions':['query','page'],'rowLimit':2000,'dataState':'all'})
for r in sorted([r for r in rows if 3<=r['position']<=20 and r['impressions']>=40],key=lambda r:-r['impressions'])[:50]: print(f(r))
P='/elecciones/resultados-elecciones-generales-2026/'
print('== RESULTADOS por dia')
for r in q({'startDate':str(hoy-D(days=8)),'endDate':str(hoy),'dimensions':['date'],'dimensionFilterGroups':pf(P),'dataState':'all'}): print(f(r))
print('== RESULTADOS queries 23-25')
for r in q({'startDate':str(hoy-D(days=3)),'endDate':str(ay),'dimensions':['query'],'dimensionFilterGroups':pf(P),'rowLimit':30,'dataState':'all'}): print(f(r))
for t in ['resultado','escrutinio','quien gan','quién gan','como van','cómo van','sondeo','pie de urna','reflexi','hora','donde voto','dónde voto','colegio','participaci','elecciones 2026','elecciones generales','debate','mesa']:
    rows=q({'startDate':str(hoy-D(days=3)),'endDate':str(ay),'dimensions':['query','page'],'dimensionFilterGroups':[{'filters':[{'dimension':'query','operator':'contains','expression':t}]}],'rowLimit':8,'dataState':'all'})
    print('== TERMINO',t,'impr',sum(r['impressions'] for r in rows))
    for r in rows: print('  ',f(r))
