# Temporal, solo lectura: Search Console 26-11 tarde. No se fusiona a main.
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
hoy=datetime.date(2026,11,26); D=datetime.timedelta
for t in ['voto util','voto útil','debate a 4','debate a cuatro','debate','extranjero','cera','exterior','aciert','plasencia','ayerbe','fall','encuestas se equivoc','ultimo escaño','último escaño','restos']:
    rows=q({'startDate':str(hoy-D(days=7)),'endDate':str(hoy),'dimensions':['query','page'],'dimensionFilterGroups':[{'filters':[{'dimension':'query','operator':'contains','expression':t}]}],'rowLimit':12,'dataState':'all'})
    print('== TERMINO',t,'impr',sum(r['impressions'] for r in rows))
    for r in rows: print('  ',f(r))
print('== PAGINAS NUEVAS hoy (hourly_all)')
for p in ['/elecciones/voto-util-29n/','/actualidad/pueblos-que-siempre-aciertan-29n/','/actualidad/debate-a-cuatro-sanchez-feijoo-abascal-colau-29n/','/actualidad/voto-exterior-cera-loreg-29n/','/actualidad/encuestas-fallos-elecciones-espana-29n/','/actualidad/plasencia-acierta-siempre/']:
    for r in q({'startDate':str(hoy-D(days=2)),'endDate':str(hoy),'dimensions':['page'],'dimensionFilterGroups':[{'filters':[{'dimension':'page','operator':'equals','expression':U+p}]}],'dataState':'all'}): print(f(r))
rows=q({'startDate':str(hoy-D(days=2)),'endDate':str(hoy),'dimensions':['page'],'dimensionFilterGroups':[{'filters':[{'dimension':'page','operator':'contains','expression':'voto-util'}]}],'rowLimit':60,'dataState':'all'})
print('== VOTO UTIL paginas',len(rows));[print(f(r)) for r in rows]
