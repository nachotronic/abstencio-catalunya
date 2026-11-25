# Temporal, solo lectura: Google Trends de «mapa» en semanas electorales. No se fusiona a main.
import time,sys,json
from pytrends.request import TrendReq
pt=TrendReq(hl='es-ES',tz=-60)
A='resultados elecciones'
grupos=[['mapa electoral','mapa elecciones','mapa resultados elecciones','mapa electoral españa'],
        ['elecciones generales','escrutinio','quien ha ganado las elecciones','resultados por municipios']]
E={'23J':'2023-07-14 2023-07-31','10N':'2019-11-01 2019-11-18','28A':'2019-04-19 2019-05-06','ahora':'2026-10-25 2026-11-24'}
for e,tf in E.items():
  for g in grupos:
    kw=[A]+g
    for i in range(4):
      try:
        pt.build_payload(kw,timeframe=tf,geo='ES'); df=pt.interest_over_time(); break
      except Exception as ex: print('retry',e,ex,file=sys.stderr); time.sleep(25)
    else: continue
    print('SUM',e,{k:int(df[k].sum()) for k in kw})
    for k in kw: print('SER',e,k,' '.join(f'{d.strftime("%m-%d")}:{int(v)}' for d,v in df[k].items() if v))
    time.sleep(8)
  # relacionadas
  try:
    pt.build_payload(['mapa electoral'],timeframe=tf,geo='ES'); r=pt.related_queries()['mapa electoral']
    print('REL',e,'top',None if r['top'] is None else r['top'].head(15).values.tolist())
  except Exception as ex: print('relerr',e,ex)
  time.sleep(8)
