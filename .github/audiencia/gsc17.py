# Temporal, solo lectura (canibalización 19-11): /encuestas/ 17-19-11. No se fusiona a main.
import json,os
from urllib.parse import quote
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
s=AuthorizedSession(service_account.Credentials.from_service_account_info(json.loads(os.environ['GSC_CREDENTIALS']),scopes=["https://www.googleapis.com/auth/webmasters.readonly"]))
SITE="sc-domain:mapaelectoral.es"; B="https://searchconsole.googleapis.com/webmasters/v3/sites/"+quote(SITE,safe="")
P="https://mapaelectoral.es/encuestas/"
def q(b):
    b.setdefault('dataState','all'); r=s.post(B+"/searchAnalytics/query",json=b)
    return r.json().get('rows',[]) if r.status_code==200 else print('ERR',r.text[:200]) or []
f=lambda r:f"{r['clicks']:.0f}c {r['impressions']:.0f}i ctr {r['ctr']*100:.1f} pos {r['position']:.1f}"
pf=lambda p:{"dimension":"page","operator":"equals","expression":p}
qf=lambda e:{"dimension":"query","operator":"equals","expression":e}
Q=qf("encuestas elecciones generales 2026")
D={"dimension":"device","operator":"equals","expression":"DESKTOP"}
for lab,flt in [('QH',[Q]),('PH',[pf(P)])]:
    for r in q({"startDate":"2026-11-18","endDate":"2026-11-19","dimensions":["hour","device"],"dataState":"hourly_all","rowLimit":500,"dimensionFilterGroups":[{"filters":flt}]}):
        if r['keys'][1]!='TABLET': print(lab,*r['keys'],f(r))
for r in q({"startDate":"2026-11-19","endDate":"2026-11-19","dimensions":["hour","page"],"dataState":"hourly_all","rowLimit":300,"dimensionFilterGroups":[{"filters":[Q]}]}): print('QPAGE19',*r['keys'],f(r))
r=s.post("https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",json={"inspectionUrl":P,"siteUrl":SITE,"languageCode":"es"})
x=r.json().get('inspectionResult',{}).get('indexStatusResult',{}); print('INSP',x.get('lastCrawlTime'),x.get('coverageState'),x.get('googleCanonical'))
