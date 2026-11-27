# Temporal, solo lectura. No se fusiona a main.
import time,sys
from pytrends.request import TrendReq
pt=TrendReq(hl='es-ES',tz=-60)
for kw in [['quien gano el debate','debate a 4','audiencia debate','debate ayer','encuestas andorra'],['voto util','donde voto','jornada de reflexion','como votar','encuestas andorra']]:
    for i in range(4):
        try: pt.build_payload(kw,timeframe='now 1-d',geo='ES'); df=pt.interest_over_time(); break
        except Exception as ex: print('retry',ex,file=sys.stderr); time.sleep(30)
    else: print('FAIL',kw); continue
    df=df.resample('3h').mean()
    for k in kw: print('SER',k,' '.join(f'{d.strftime("%d-%H")}:{int(v)}' for d,v in df[k].items()))
    time.sleep(8)
for k in ['debate','votar','elecciones']:
    try:
        pt.build_payload([k],timeframe='now 1-d',geo='ES'); r=pt.related_queries()[k]
        print('RISING',k,None if r['rising'] is None else r['rising'].head(25).values.tolist())
        print('TOP',k,None if r['top'] is None else r['top'].head(15).values.tolist())
    except Exception as ex: print('relerr',k,ex)
    time.sleep(10)
