# Temporal, solo lectura: Google Trends 26-11. No se fusiona a main.
import time,sys
from pytrends.request import TrendReq
pt=TrendReq(hl='es-ES',tz=-60)
A='elecciones generales'
G=[['resultados elecciones','encuestas andorra','jornada de reflexion','donde voto'],
   ['sondeo a pie de urna','escrutinio','voto por correo','mesa electoral'],
   ['como votar','a que hora cierran los colegios','participacion elecciones','debate'],
   ['elecciones 2026','elecciones españa','encuestas','programa electoral']]
for tf in ['now 7-d','2023-07-20 2023-07-25']:
  for g in G:
    kw=[A]+g
    for i in range(4):
        try: pt.build_payload(kw,timeframe=tf,geo='ES'); df=pt.interest_over_time(); break
        except Exception as ex: print('retry',ex,file=sys.stderr); time.sleep(30)
    else: print('FAIL',g); continue
    if tf=='now 7-d': df=df.resample('D').mean()
    for k in kw: print('SER',tf,k,' '.join(f'{d.strftime("%a%d")}:{int(v)}' for d,v in df[k].items()))
    time.sleep(8)
for k in ['elecciones','votar']:
    try:
        pt.build_payload([k],timeframe='now 7-d',geo='ES'); r=pt.related_queries()[k]
        print('RISING',k,None if r['rising'] is None else r['rising'].head(25).values.tolist())
        print('TOP',k,None if r['top'] is None else r['top'].head(25).values.tolist())
    except Exception as ex: print('relerr',k,ex)
    time.sleep(10)
