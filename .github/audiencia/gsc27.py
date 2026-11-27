# Temporal, solo lectura: Search Console 27-11. No se fusiona a main.
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
hoy=datetime.date(2026,11,27); D=datetime.timedelta; ay=hoy-D(days=1)
print('== SITIO POR DIA')
for r in q({'startDate':str(hoy-D(days=6)),'endDate':str(hoy),'dimensions':['date'],'dataState':'all'}): print(f(r))
print('== PAGINAS 26-11 top 25')
for r in q({'startDate':str(ay),'endDate':str(ay),'dimensions':['page'],'rowLimit':25,'dataState':'all'}): print(f(r))
print('== QUERIES 26-11 top 40')
for r in q({'startDate':str(ay),'endDate':str(ay),'dimensions':['query'],'rowLimit':40,'dataState':'all'}): print(f(r))
rows=q({'startDate':str(hoy-D(days=2)),'endDate':str(hoy),'dimensions':['page'],'dimensionFilterGroups':[{'filters':[{'dimension':'page','operator':'contains','expression':'voto-util'}]}],'rowLimit':60,'dataState':'all'})
print('== VOTO UTIL paginas 25-27',len(rows),'impr',sum(r['impressions'] for r in rows),'clics',sum(r['clicks'] for r in rows));[print(f(r)) for r in rows[:15]]
for p in ['/actualidad/debate-a-cuatro-sanchez-feijoo-abascal-colau-29n/','/actualidad/debate-sanchez-feijoo-29n/','/elecciones/resultados-elecciones-generales-2026/','/actualidad/voto-exterior-cera-loreg-29n/','/actualidad/como-votar-elecciones-generales-29n/','/actualidad/a-que-hora-resultados-elecciones-generales-29n/','/','/actualidad/pueblos-que-siempre-aciertan-29n/','/actualidad/encuestas-fallos-elecciones-espana-29n/']:
    print('== PAGINA',p)
    for r in q({'startDate':str(hoy-D(days=3)),'endDate':str(hoy),'dimensions':['date'],'dimensionFilterGroups':[{'filters':[{'dimension':'page','operator':'equals','expression':U+p}]}],'dataState':'all'}): print('  dia',f(r))
    for r in q({'startDate':str(hoy-D(days=2)),'endDate':str(hoy),'dimensions':['query'],'dimensionFilterGroups':[{'filters':[{'dimension':'page','operator':'equals','expression':U+p}]}],'rowLimit':8,'dataState':'all'}): print('  q',f(r))
for t in ['voto util','voto útil','debate','jornada de reflexi','reflexión','pie de urna','donde voto','dónde voto','hora','papeleta','resultados','elecciones generales 2026','elecciones 29']:
    rows=q({'startDate':str(hoy-D(days=2)),'endDate':str(hoy),'dimensions':['query','page'],'dimensionFilterGroups':[{'filters':[{'dimension':'query','operator':'contains','expression':t}]}],'rowLimit':10,'dataState':'all'})
    print('== TERMINO',t,'impr',sum(r['impressions'] for r in rows))
    for r in rows: print('  ',f(r))
