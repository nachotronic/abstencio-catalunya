import pandas as pd, numpy as np, geopandas as gpd
sec=pd.read_csv('/tmp/w/sec_hist_cat.csv',dtype={'tract_code':str}); mun=pd.read_csv('/tmp/w/mun_hist_cat.csv',dtype={'mun_code':str})
sec=sec[~sec.tract_code.str[2:5].eq('999')]; mun=mun[~mun.mun_code.str.endswith('999')]
cat=['08','17','25','43']
inc=pd.read_csv('/tmp/w/income_tract.csv',dtype=str); dem=pd.read_csv('/tmp/w/demographics_tract.csv',dtype=str); cen=pd.read_csv('/tmp/w/census_2021_tract.csv',dtype=str)
inc=inc[inc.prov_code.isin(cat)]; dem=dem[dem.prov_code.isin(cat)]; cen=cen[cen.prov_code.isin(cat)]
print('years inc',sorted(inc.year.unique())[-3:],'dem',sorted(dem.year.unique())[-3:])
for c in inc.columns[7:]: inc[c]=pd.to_numeric(inc[c],errors='coerce')
for c in dem.columns[7:]: dem[c]=pd.to_numeric(dem[c],errors='coerce')
for c in cen.columns[4:-1]: cen[c]=pd.to_numeric(cen[c],errors='coerce')
i23=inc[inc.year=='2023'][['tract_code','mun_name','net_income_pc','net_income_equiv','median_income_equiv']]
d23=dem[dem.year=='2023'][['tract_code','mean_age','pct_under18','pct_over65','pct_single_hh','population','pct_spanish']]
c21=cen[['tract_code','pct_foreign','pct_foreign_born','pct_higher_ed_completed','unemployment_rate','total_dwellings','secondary_dwellings','rented_dwellings','total_households','primary_dwellings']].copy()
c21['pct_rented']=c21.rented_dwellings/c21.primary_dwellings; c21['pct_secondary']=c21.secondary_dwellings/c21.total_dwellings
c21['pct_naturalized']=(c21.pct_foreign_born-c21.pct_foreign).clip(lower=0)
c21=c21.drop(columns=['total_dwellings','secondary_dwellings','rented_dwellings','total_households','primary_dwellings'])
s23=sec[sec.elec=='2023-07'].drop(columns='elec')
hist=sec.pivot_table(index='tract_code',columns='elec',values='turnout')
hist.columns=['t'+c.replace('-','_') for c in hist.columns]
df=s23.merge(i23,on='tract_code',how='left').merge(d23,on='tract_code',how='left').merge(c21,on='tract_code',how='left').merge(hist.reset_index(),on='tract_code',how='left')
df['mun_code']=df.tract_code.str[:5]
print('rows',len(df),'missing income',df.net_income_pc.isna().sum(),'missing dem',df.population.isna().sum(),'missing census',df.pct_foreign.isna().sum())
# decomposition per 100 adult residents
df['adults']=df.population*(1-df.pct_under18/100)
df['sin_derecho']=(df.adults-df.electorate).clip(lower=0)
df['abst']=df.electorate-df.voters
df['pct_ad_vota']=df.voters/df.adults
df['pct_ad_sinderecho']=df.sin_derecho/df.adults
df['pct_ad_abst']=1-df.pct_ad_vota-df.pct_ad_sinderecho
df.to_csv('/tmp/w/sec2023_cat.csv',index=False)
print(df[df.tract_code.str.startswith('17')].describe().T[['count','mean','min','max']].round(3))
