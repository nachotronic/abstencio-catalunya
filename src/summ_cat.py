import pandas as pd, numpy as np, json
g=pd.read_csv('/mnt/project-files/abstencion/catalunya_secciones_2023.csv',dtype={'tract_code':str,'mun_code':str})
mu=pd.read_csv('/mnt/project-files/abstencion/girona_municipios.csv',dtype={'mun_code':str})
S={}
def q(c):
    out=[]
    for k,x in g.groupby(pd.qcut(g[c],5,labels=False)):
        out.append(dict(lo=float(x[c].min()),hi=float(x[c].max()),turnout=x.voters.sum()/x.electorate.sum(),vota=x.voters.sum()/x.adults.sum(),sin=x.sin_derecho.sum()/x.adults.sum()))
    return out
S['quint']={c:q(c) for c in ['net_income_equiv','pct_foreign','pct_higher_ed_completed','unemployment_rate','mean_age']}
def grp(x,name):
    return dict(name=name,pop=float(x.population.sum()),turnout=x.voters.sum()/x.electorate.sum(),vota=x.voters.sum()/x.adults.sum(),sin=x.sin_derecho.sum()/x.adults.sum(),
      income=float(np.average(x.net_income_equiv.fillna(x.net_income_equiv.mean()),weights=x.population)),foreign=float(np.average(x.pct_foreign.fillna(x.pct_foreign.mean()),weights=x.population)),
      age=float(np.average(x.mean_age,weights=x.population)),univ=float(np.average(x.pct_higher_ed_completed.fillna(x.pct_higher_ed_completed.mean()),weights=x.population)),
      hist=[float(x.assign(v=x[c]*x.electorate).dropna(subset=[c]).v.sum()/x.dropna(subset=[c]).electorate.sum()) for c in ['t2015_12','t2016_06','t2019_04','t2019_11','t2023_07']])
popm=g.groupby('mun_code').population.sum()
rural=g[g.mun_code.map(popm)<2000]
TOWNS=['Salt','Lloret de Mar','Figueres','Guissona','Salou','Hospitalet de Llobregat, L\'','Barcelona','Sant Cugat del Vallès']
S['compare']=[grp(g[g.mun_name==m],m) for m in TOWNS]+[grp(rural,'Pueblos de menos de 2.000 hab.'),grp(g,'Cataluña')]
S['compare'][len(TOWNS)]['n']=int(rural.mun_code.nunique())
# history by mun size (use mun hist)
m=pd.read_csv('mun_hist_cat.csv',dtype={'mun_code':str}); m=m[~m.mun_code.str.endswith('999')]
m['size']=pd.cut(m.mun_code.map(popm),[0,2000,10000,30000,1e7],labels=['< 2.000','2.000–10.000','10.000–30.000','> 30.000'])
S['size_hist']={str(k):[x[x.elec==e].voters.sum()/x[x.elec==e].electorate.sum() for e in ['2015-12','2016-06','2019-04','2019-11','2023-07']] for k,x in m.groupby('size')}
# indep quartile drop
S['indep']=[dict(lo=float(x.indep_share19.min()),hi=float(x.indep_share19.max()),t19=x.voters.sum()*0+ (x.t2019_11*x.electorate).sum()/x.electorate.sum(),t23=x.voters.sum()/x.electorate.sum()) for k,x in g.dropna(subset=['indep_share19']).groupby(pd.qcut(g.indep_share19,4,labels=False))]
# regression (standardized, weighted) Girona
X=['pct_higher_ed_completed','unemployment_rate','mean_age','pct_foreign','pct_secondary','pct_naturalized','pct_rented','net_income_equiv']
d=g.dropna(subset=X+['turnout']); Z=(d[X]-d[X].mean())/d[X].std(); Z.insert(0,'c',1); W=np.sqrt(d.electorate.values)
b,*_=np.linalg.lstsq(Z.values*W[:,None],d.turnout.values*W,rcond=None)
rng=np.random.default_rng(1); bs=[np.linalg.lstsq((Z.values*W[:,None])[ix],(d.turnout.values*W)[ix],rcond=None)[0] for ix in [rng.integers(0,len(d),len(d)) for _ in range(500)]]
se=np.std(bs,axis=0); pred=Z.values@b
r2=1-((d.turnout-pred)**2*d.electorate).sum()/(((d.turnout-np.average(d.turnout,weights=d.electorate))**2)*d.electorate).sum()
S['reg']=dict(r2=float(r2),n=len(d),coef=[dict(var=v,b=float(b[i+1]*100),se=float(se[i+1]*100),sd=float(d[v].std())) for i,v in enumerate(X)])
# simple univariate r2 for income
S['corr']={v:float(g[[v,'turnout']].corr().iloc[0,1]) for v in X}
# extremes
S['low']=g[g.electorate>300].sort_values('turnout').head(10)[['tract_code','mun_name','turnout','pct_ad_vota','pct_ad_sinderecho','net_income_equiv','pct_foreign','pct_higher_ed_completed','unemployment_rate']].to_dict('records')
S['totals']=dict(adults=float(g.adults.sum()),electorate=float(g.electorate.sum()),voters=float(g.voters.sum()),sin=float(g.sin_derecho.sum()))
json.dump(S,open('summary_cat.json','w'),default=float)
print(json.dumps(S['compare'],indent=0)[:1500]); print(S['reg']); print(S['size_hist']); print(S['indep']); print(S['totals'])
