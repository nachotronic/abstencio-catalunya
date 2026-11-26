# Temporal, solo lectura: Google Trends 26-11 tarde. No se fusiona a main.
import time,sys
from pytrends.request import TrendReq
pt=TrendReq(hl='es-ES',tz=-60)
A='encuestas andorra'
G=[['voto util','debate a 4','debate a cuatro','debate'],['votar desde el extranjero','voto cera','voto exterior','voto por correo'],['pueblos que siempre aciertan','plasencia','fallos encuestas','ley d hondt']]
def run(kw,tf):
    for i in range(4):
        try: pt.build_payload(kw,timeframe=tf,geo='ES'); return pt.interest_over_time()
        except Exception as ex: print('retry',ex,file=sys.stderr); time.sleep(30)
for tf in ['now 7-d','2023-07-13 2023-07-25','2019-11-01 2019-11-12']:
  for g in G:
    df=run([A]+g if tf=='now 7-d' else g,tf)
    if df is None: print('FAIL',tf,g); continue
    if tf=='now 7-d': df=df.resample('D').mean()
    for k in df.columns:
        if k!='isPartial': print('SER',tf,k,' '.join(f'{d.strftime("%d")}:{int(v)}' for d,v in df[k].items()))
    time.sleep(8)
for k,tf in [('voto util','today 1-m'),('voto util','2023-07-01 2023-07-25'),('debate','now 7-d'),('votar desde el extranjero','today 1-m'),('voto util','2019-04-01 2019-04-30')]:
    try:
        pt.build_payload([k],timeframe=tf,geo='ES'); r=pt.related_queries()[k]
        print('RISING',k,tf,None if r['rising'] is None else r['rising'].head(20).values.tolist())
        print('TOP',k,tf,None if r['top'] is None else r['top'].head(20).values.tolist())
    except Exception as ex: print('relerr',k,ex)
    time.sleep(10)
