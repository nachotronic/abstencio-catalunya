import pandas as pd, numpy as np
P='/tmp/pollspaindata/inst/extdata/'
IND={'2019_11':['ERC-SOBIRANISTES','JXCAT-JUNTS','CUP-PR'],'2023_07':['JXCAT - JUNTS','ERC','CUP-PR','PDECAT-E-CIU']}
out={}
for y,parts in IND.items():
    c=pd.read_parquet(P+f'raw_candidacies_poll_congress_{y}.parquet'); c=c[c.cod_INE_prov.isin(['08','17','25','43'])]
    k=pd.read_parquet(P+f'raw_candidacies_congress_{y}.parquet')
    c=c.merge(k[['id_candidacies','abbrev_candidacies']],on='id_candidacies')
    c['tract_code']=c.cod_INE_prov+c.cod_INE_mun+c.cod_mun_district+c.cod_sec
    c['ind']=c.abbrev_candidacies.isin(parts)*c.ballots
    out[y]=c.groupby('tract_code').agg(ind=('ind','sum'),cand=('ballots','sum'))
df=pd.read_csv('/tmp/w/sec2023_cat.csv',dtype={'tract_code':str,'mun_code':str})
sh=pd.read_csv('/tmp/w/sec_hist_cat.csv',dtype={'tract_code':str})
e19=sh[sh.elec=='2019-11'].set_index('tract_code')
df=df.join(out['2019_11'].ind.rename('ind19'),on='tract_code').join(e19[['voters']].rename(columns={'voters':'voters19'}),on='tract_code')
df=df.join(out['2023_07'].ind.rename('ind23'),on='tract_code')
df['indep_share19']=df.ind19/df.voters19
df['indep_share23']=df.ind23/df.voters
df['drop_19_23']=df.t2019_11-df.t2023_07
df.to_csv('/tmp/w/sec2023_cat.csv',index=False)
g=df[df.tract_code.str.startswith('17')]
print(g[['drop_19_23','indep_share19','net_income_equiv','pct_foreign','mean_age','pct_higher_ed_completed']].corr()['drop_19_23'].round(2))
print('Girona indep share 19',g.ind19.sum()/g.voters19.sum(),'23',g.ind23.sum()/g.voters.sum())
print(g.groupby(pd.qcut(g.indep_share19,4))[['drop_19_23','t2019_11','t2023_07']].mean().round(3))
