# Temporal, solo lectura: /encuestas/ en Google tras #616. No se fusiona a main.
import json,os
from urllib.parse import quote
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
s=AuthorizedSession(service_account.Credentials.from_service_account_info(json.loads(os.environ['GSC_CREDENTIALS']),scopes=["https://www.googleapis.com/auth/webmasters.readonly"]))
SITE="sc-domain:mapaelectoral.es"; B="https://searchconsole.googleapis.com/webmasters/v3/sites/"+quote(SITE,safe="")
def q(b):
    r=s.post(B+"/searchAnalytics/query",json=b)
    return r.json().get('rows',[]) if r.status_code==200 else print('ERR',r.text[:300]) or []
P="https://mapaelectoral.es/encuestas/"
for nm,fl in [('PAGE',[{"dimension":"page","operator":"equals","expression":P}]),
              ('PAGE_HEADQ',[{"dimension":"page","operator":"equals","expression":P},{"dimension":"query","operator":"equals","expression":"encuestas elecciones generales 2026"}])]:
    rows=q({"startDate":"2026-11-16","endDate":"2026-11-18","dimensions":["hour"],"dataState":"hourly_all","rowLimit":200,"dimensionFilterGroups":[{"filters":fl}]})
    for r in rows: print('H',nm,r['keys'][0],f"{r['clicks']:.0f}c {r['impressions']:.0f}i ctr {100*r['ctr']:.1f} pos {r['position']:.1f}")
r=s.post("https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",json={"inspectionUrl":P,"siteUrl":SITE,"languageCode":"es"})
print('INSP',json.dumps(r.json().get('inspectionResult',{}).get('indexStatusResult',{}),ensure_ascii=False))
