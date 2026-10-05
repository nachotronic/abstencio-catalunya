import pandas as pd, numpy as np, glob
P='/tmp/pollspaindata/inst/extdata/'
elecs={'2015_12':'2015-12','2016_06':'2016-06','2019_04':'2019-04','2019_11':'2019-11','2023_07':'2023-07'}
rows=[];mrows=[]
for k,lab in elecs.items():
    d=pd.read_parquet(P+f'raw_poll_stations_congress_{k}.parquet')
    d=d[d.cod_MIR_ccaa=='09'] if False else d[d.cod_INE_prov.isin(['08','17','25','43'])]
    d['voters']=d.blank_ballots+d.invalid_ballots+d.party_ballots
    d['tract_code']=d.cod_INE_prov+d.cod_INE_mun+d.cod_mun_district+d.cod_sec
    g=d.groupby('tract_code').agg(electorate=('census_counting','sum'),voters=('voters','sum'),mesas=('cod_poll_station','count')).reset_index()
    g['elec']=lab; rows.append(g)
    m=pd.read_parquet(P+f'raw_mun_data_congress_{k}.parquet'); m=m[m.cod_INE_prov.isin(['08','17','25','43'])]
    m['mun_code']=m.cod_INE_prov+m.cod_INE_mun
    mv=d.assign(mun_code=d.cod_INE_prov+d.cod_INE_mun).groupby('mun_code').agg(electorate=('census_counting','sum'),voters=('voters','sum')).reset_index()
    mv=mv.merge(m[['mun_code','mun','pop_res_mun']],on='mun_code',how='left'); mv['elec']=lab; mrows.append(mv)
sec=pd.concat(rows); mun=pd.concat(mrows)
sec['turnout']=sec.voters/sec.electorate; mun['turnout']=mun.voters/mun.electorate
sec.to_csv('/tmp/w/sec_hist_cat.csv',index=False); mun.to_csv('/tmp/w/mun_hist_cat.csv',index=False)
print(mun[mun.elec=='2023-07'].query("mun_code.str.startswith('17')").sort_values('turnout').head(10))
for lab in elecs.values():
    x=mun[(mun.elec==lab)&mun.mun_code.str.startswith('17')]; print(lab, round(x.voters.sum()/x.electorate.sum(),4), len(x))
