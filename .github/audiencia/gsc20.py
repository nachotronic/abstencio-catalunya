# Temporal, solo lectura: /encuestas/ en Google 20-11. No se fusiona a main.
import json,os
from urllib.parse import quote
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
s=AuthorizedSession(service_account.Credentials.from_service_account_info(json.loads(os.environ['GSC_CREDENTIALS']),scopes=["https://www.googleapis.com/auth/webmasters.readonly"]))
SITE="sc-domain:mapaelectoral.es"; B="https://searchconsole.googleapis.com/webmasters/v3/sites/"+quote(SITE,safe="")
def q(b):
    r=s.post(B+"/searchAnalytics/query",json=b)
    return r.json().get('rows',[]) if r.status_code==200 else print('ERR',r.text[:300]) or []
P="https://mapaelectoral.es/encuestas/"; HQ="encuestas elecciones generales 2026"
fP={"dimension":"page","operator":"equals","expression":P}; fQ={"dimension":"query","operator":"equals","expression":HQ}
fmt=lambda r:f"{r['clicks']:.0f}c {r['impressions']:.0f}i ctr {100*r['ctr']:.1f} pos {r['position']:.1f}"
for nm,fl in [('PAGE',[fP]),('PAGE_HQ',[fP,fQ]),('HQ_SITE',[fQ]),('SITE',[])]:
    for dims in (["date"],["date","device"]):
        rows=q({"startDate":"2026-11-13","endDate":"2026-11-20","dimensions":dims,"dataState":"all","rowLimit":500,"dimensionFilterGroups":[{"filters":fl}] if fl else []})
        for r in rows: print('D',nm,' '.join(r['keys']),fmt(r))
for nm,fl in [('PAGE',[fP]),('PAGE_HQ',[fP,fQ])]:
    for dims in (["hour"],["hour","device"]):
        rows=q({"startDate":"2026-11-19","endDate":"2026-11-20","dimensions":dims,"dataState":"hourly_all","rowLimit":500,"dimensionFilterGroups":[{"filters":fl}]})
        for r in rows: print('H',nm,' '.join(r['keys']),fmt(r))
rows=q({"startDate":"2026-11-19","endDate":"2026-11-20","dimensions":["query"],"dataState":"all","rowLimit":15,"dimensionFilterGroups":[{"filters":[fP]}]})
for r in rows: print('Q',r['keys'][0],fmt(r))
r=s.post("https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",json={"inspectionUrl":P,"siteUrl":SITE,"languageCode":"es"})
print('INSP',json.dumps(r.json().get('inspectionResult',{}).get('indexStatusResult',{}),ensure_ascii=False))
