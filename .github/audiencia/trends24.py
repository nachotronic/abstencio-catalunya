# Temporal, solo lectura: Google Trends de semanas electorales. No se fusiona a main.
import time,sys,json
from pytrends.request import TrendReq
pt=TrendReq(hl='es-ES',tz=-60)
ANCHOR='elecciones generales'
grupos=[
 ['jornada de reflexion','donde voto','colegio electoral','sondeo a pie de urna'],
 ['encuestas andorra','resultados elecciones','escrutinio','hora resultados'],
 ['que hay que llevar para votar','dni caducado votar','mesa electoral','voto por correo'],
 ['papeleta senado','como votar senado','calculadora escaños','ley d hondt'],
 ['participacion elecciones','debate','encuestas','programa electoral'],
 ['puedo votar','votar con dni caducado','cuando son las elecciones','elecciones domingo'],
]
eleccs={'23J':'2023-07-14 2023-07-26','10N':'2019-11-01 2019-11-13','28A':'2019-04-19 2019-05-01'}
out={}
for e,tf in eleccs.items():
  for g in grupos:
    kw=[ANCHOR]+g
    for i in range(4):
      try:
        pt.build_payload(kw,timeframe=tf,geo='ES'); df=pt.interest_over_time(); break
      except Exception as ex:
        print('retry',e,ex,file=sys.stderr); time.sleep(20)
    else: continue
    for k in kw:
      out.setdefault(e,{}).setdefault(k,{str(d.date()):int(v) for d,v in df[k].items()})
    print(e,g,{k:int(df[k].sum()) for k in kw},flush=True)
    time.sleep(6)
print('JSON',json.dumps(out))
