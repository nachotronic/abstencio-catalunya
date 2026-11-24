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
# 1. Sitio por día
print('== SITIO POR DIA')
for r in q({'startDate':str(hoy-D(days=10)),'endDate':str(hoy),'dimensions':['date'],'dataState':'all'}): print(f(r))
# 2. Por hora, sitio y Andorra (datos frescos)
print('== SITIO POR HORA (hourly_all)')
for r in q({'startDate':str(hoy-D(days=1)),'endDate':str(hoy),'dimensions':['hour'],'dataState':'hourly_all'}): print(f(r))
PIEZAS=['/actualidad/encuestas-andorra-29n/','/actualidad/veda-encuestas-29n/','/actualidad/escrutinio-elecciones-generales-29n/','/actualidad/elecciones-generales-29n-cifras/','/actualidad/despues-elecciones-generales-29n-investidura/','/actualidad/voto-blanco-nulo-elecciones-generales-29n/','/actualidad/a-que-hora-resultados-elecciones-generales-29n/','/actualidad/como-votar-elecciones-generales-29n/','/actualidad/voto-correo-plazo-jueves-29n/','/actualidad/programa-electoral-29n/','/actualidad/me-ha-tocado-mesa-electoral-29n/','/actualidad/participacion-elecciones-generales-29n-prevision/','/actualidad/debate-sanchez-feijoo-29n/','/encuestas/','/','/elecciones/resultados-elecciones-generales-2026/']
for p in PIEZAS:
    print('== PAGINA',p)
    for r in q({'startDate':str(hoy-D(days=6)),'endDate':str(hoy),'dimensions':['date'],'dimensionFilterGroups':pf(p),'dataState':'all'}): print('  dia',f(r))
    for r in q({'startDate':str(hoy-D(days=6)),'endDate':str(hoy),'dimensions':['query'],'dimensionFilterGroups':pf(p),'rowLimit':15,'dataState':'all'}): print('  q',f(r))
print('== ANDORRA POR HORA')
for r in q({'startDate':str(hoy-D(days=1)),'endDate':str(hoy),'dimensions':['hour'],'dimensionFilterGroups':pf('/actualidad/encuestas-andorra-29n/'),'dataState':'hourly_all'}): print(f(r))
# 3. Búsquedas por término (todas las páginas), últimos 3 días
TER=['andorra','prohibid','veda','encuesta','sondeo','pie de urna','reflexi','resultado','escrutinio','hora','debate','programa','correo','mesa','donde voto','dónde voto','colegio','votar','dni','blanco','nulo','investidura','participaci','elecciones generales','elecciones 2026','29n','29 de noviembre','senado','papeleta','censo','calculadora','escaños','d\'hondt','candidat','listas']
for t in TER:
    rows=q({'startDate':str(hoy-D(days=3)),'endDate':str(hoy),'dimensions':['query'],'dimensionFilterGroups':[{'filters':[{'dimension':'query','operator':'contains','expression':t}]}],'rowLimit':12,'dataState':'all'})
    ti=sum(r['impressions'] for r in rows); print('== TERMINO',t,'top12 impr',ti)
    for r in rows: print('  ',f(r))
    for r in q({'startDate':str(hoy-D(days=3)),'endDate':str(hoy),'dimensions':['query','page'],'dimensionFilterGroups':[{'filters':[{'dimension':'query','operator':'contains','expression':t}]}],'rowLimit':5,'dataState':'all'}): print('   qp',f(r).replace(U,''))
