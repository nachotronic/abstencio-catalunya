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
TER=['donde voto','donde votar','reflexi','correo','mesa electoral','debate','programa','escrutinio','resultado','pie de urna','como votar','cómo votar','tarjeta censal','dni','horario','cierran','abren','papeleta','senado','blanco','nulo','participaci','permiso','hondt','mayoria absoluta','mayoría absoluta','escaños','andorra','prohibid','puedo votar','multa','encuestas hoy','ultimas encuestas','últimas encuestas']
for t in TER:
    rows=q({'startDate':str(hoy-D(days=7)),'endDate':str(hoy),'dimensions':['query','page'],'dimensionFilterGroups':[{'filters':[{'dimension':'query','operator':'contains','expression':t}]}],'rowLimit':8,'dataState':'all'})
    tot=q({'startDate':str(hoy-D(days=7)),'endDate':str(hoy),'dimensions':['query'],'dimensionFilterGroups':[{'filters':[{'dimension':'query','operator':'contains','expression':t}]}],'rowLimit':500,'dataState':'all'})
    ti=sum(r['impressions'] for r in tot); tc=sum(r['clicks'] for r in tot)
    print('== TERMINO',t,'consultas',len(tot),'impr',ti,'clics',tc)
    for r in rows: print('   ',f(r).replace(U,''))
