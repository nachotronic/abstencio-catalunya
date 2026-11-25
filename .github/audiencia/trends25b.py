# Temporal, solo lectura: Google Trends 17-24 jul 2023 para búsquedas de servicio. No se fusiona a main.
import time,sys
from pytrends.request import TrendReq
pt=TrendReq(hl='es-ES',tz=-60)
TF='2023-07-17 2023-07-24'
A='encuestas andorra'
G=[['donde voto','jornada de reflexion','voto por correo','mesa electoral'],
   ['debate','programa electoral','escrutinio','resultados elecciones'],
   ['sondeo a pie de urna','como votar','tarjeta censal','dni caducado'],
   ['horario colegios electorales','a que hora cierran los colegios','papeleta senado','voto en blanco'],
   ['participacion elecciones','permiso para votar','ley d hondt','mayoria absoluta'],
   ['encuestas','encuestas hoy','electomania','encuestas prohibidas'],
   ['multa mesa electoral','voto nulo','puedo votar','cuantos escaños']]
for g in G:
    kw=[A]+g
    for i in range(4):
        try: pt.build_payload(kw,timeframe=TF,geo='ES'); df=pt.interest_over_time(); break
        except Exception as ex: print('retry',ex,file=sys.stderr); time.sleep(30)
    else: print('FAIL',g); continue
    for k in kw: print('SER',k,' '.join(f'{d.strftime("%a%d")}:{int(v)}' for d,v in df[k].items()))
    time.sleep(8)
for k in ['elecciones','votar','encuestas']:
    try:
        pt.build_payload([k],timeframe='2023-07-19 2023-07-22',geo='ES'); r=pt.related_queries()[k]
        print('RISING',k,None if r['rising'] is None else r['rising'].head(25).values.tolist())
        print('TOP',k,None if r['top'] is None else r['top'].head(25).values.tolist())
    except Exception as ex: print('relerr',k,ex)
    time.sleep(10)
