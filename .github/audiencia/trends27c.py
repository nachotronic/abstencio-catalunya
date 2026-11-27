# Temporal, solo lectura. No se fusiona a main.
import time,sys
from pytrends.request import TrendReq
pt=TrendReq(hl='es-ES',tz=-120)
def run(kw,tf):
    for i in range(4):
        try: pt.build_payload(kw,timeframe=tf,geo='ES'); return pt.interest_over_time()
        except Exception as ex: print('retry',ex,file=sys.stderr); time.sleep(30)
G=[['jornada de reflexion','donde voto','voto por correo','encuestas','mesa electoral'],
   ['jornada de reflexion','que se puede hacer en la jornada de reflexion','encuestas andorra','como votar','tarjeta censal'],
   ['jornada de reflexion','dni caducado','horario colegios electorales','papeleta senado','voto en blanco'],
   ['jornada de reflexion','elecciones','debate','calor','resultados elecciones']]
for tf in ['2023-07-22T00 2023-07-23T00']:
  for g in G:
    df=run(g,tf)
    if df is None: print('FAIL',g); continue
    df=df.resample('3h').mean()
    for k in g: print('SER',k,' '.join(f'{d.strftime("%d-%H")}:{int(v)}' for d,v in df[k].items()))
    time.sleep(8)
for g in [['jornada de reflexion','donde voto','encuestas','elecciones','voto por correo']]:
    df=run(g,'2023-07-19 2023-07-24')
    if df is not None:
        for k in g: print('DIA',k,' '.join(f'{d.strftime("%d")}:{int(v)}' for d,v in df[k].items()))
for k in ['elecciones','votar','jornada de reflexion','encuestas','voto','mesa electoral']:
    try:
        pt.build_payload([k],timeframe='2023-07-22 2023-07-22',geo='ES'); r=pt.related_queries()[k]
        print('RISING',k,None if r['rising'] is None else r['rising'].head(25).values.tolist())
        print('TOP',k,None if r['top'] is None else r['top'].head(20).values.tolist())
    except Exception as ex: print('relerr',k,ex)
    time.sleep(10)
