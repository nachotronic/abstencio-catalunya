import geopandas as gpd, pandas as pd, json, numpy as np
df=pd.read_csv('sec2023_cat.csv',dtype={'tract_code':str,'mun_code':str})
g=gpd.read_file('census_tracts_2023.gpkg',where="substr(tract_code,1,2)='17'")
gi=df[df.tract_code.str.startswith('17')].copy()
mn=gi.groupby('mun_code').mun_name.first()
gi['mun_name']=gi.mun_code.map(mn)
# municipality table (history + structure)
m=pd.read_csv('mun_hist_cat.csv',dtype={'mun_code':str}); m=m[m.mun_code.str.startswith('17')&~m.mun_code.str.endswith('999')]
mh=m.pivot_table(index='mun_code',columns='elec',values='turnout'); mh.columns=['t'+c.replace('-','_') for c in mh.columns]
agg=gi.groupby('mun_code').agg(mun_name=('mun_name','first'),secciones=('tract_code','count'),population=('population','sum'),adults=('adults','sum'),electorate=('electorate','sum'),voters=('voters','sum'),sin_derecho=('sin_derecho','sum'),ind19=('ind19','sum'),voters19=('voters19','sum'),ind23=('ind23','sum'))
def wavg(col,w='population'): return gi.groupby('mun_code').apply(lambda x: np.average(x[col].fillna(x[col].mean()) if x[col].notna().any() else [np.nan]*len(x),weights=x[w]))
for c in ['net_income_equiv','mean_age','pct_over65','pct_spanish','pct_foreign','pct_naturalized','pct_higher_ed_completed','unemployment_rate','pct_rented','pct_secondary']: agg[c]=wavg(c)
agg['turnout']=agg.voters/agg.electorate; agg['pct_ad_vota']=agg.voters/agg.adults; agg['pct_ad_sinderecho']=agg.sin_derecho/agg.adults; agg['pct_ad_abst']=1-agg.pct_ad_vota-agg.pct_ad_sinderecho
agg['indep_share19']=agg.ind19/agg.voters19; agg['indep_share23']=agg.ind23/agg.voters
agg=agg.join(mh); agg['drop_19_23']=agg.t2019_11-agg.t2023_07
agg=agg.reset_index()
OUT='/mnt/project-files/abstencion/'
cols=['tract_code','mun_code','mun_name','electorate','voters','turnout','t2015_12','t2016_06','t2019_04','t2019_11','t2023_07','drop_19_23','population','adults','sin_derecho','pct_ad_vota','pct_ad_sinderecho','pct_ad_abst','net_income_pc','net_income_equiv','median_income_equiv','mean_age','pct_under18','pct_over65','pct_spanish','pct_foreign','pct_foreign_born','pct_naturalized','pct_higher_ed_completed','unemployment_rate','pct_rented','pct_secondary','pct_single_hh','indep_share19','indep_share23']
gi[cols].round(4).to_csv(OUT+'girona_secciones_2023.csv',index=False)
agg.drop(columns=['ind19','voters19','ind23']).round(4).to_csv(OUT+'girona_municipios.csv',index=False)
df.round(4).to_csv(OUT+'catalunya_secciones_2023.csv',index=False)
sh=pd.read_csv('sec_hist_cat.csv',dtype={'tract_code':str}); sh.round(4).to_csv(OUT+'catalunya_secciones_historico_congreso.csv',index=False)
# geojson
g=g.merge(gi[cols],on='tract_code',how='left').to_crs(25831)
g['geometry']=g.geometry.simplify(25,preserve_topology=True)
gm=g.dissolve(by='mun_code',as_index=False)[['mun_code','geometry']]
gm['geometry']=gm.geometry.simplify(60,preserve_topology=True)
keep=['tract_code','mun_code','mun_name','electorate','voters','turnout','t2015_12','t2016_06','t2019_04','t2019_11','t2023_07','drop_19_23','population','adults','pct_ad_vota','pct_ad_sinderecho','pct_ad_abst','net_income_equiv','mean_age','pct_over65','pct_foreign','pct_naturalized','pct_higher_ed_completed','unemployment_rate','pct_rented','pct_secondary','indep_share19']
g=g[keep+['geometry']].to_crs(4326); gm=gm.to_crs(4326)
for c in keep[3:]: g[c]=g[c].round(4)
g.to_file('sec.geojson',driver='GeoJSON',COORDINATE_PRECISION=4); gm.to_file('mun.geojson',driver='GeoJSON',COORDINATE_PRECISION=4)
g.to_file(OUT+'girona_secciones_2023.geojson',driver='GeoJSON',COORDINATE_PRECISION=5)
agg.round(4).to_json('mun.json',orient='records')
print(agg.sort_values('pct_ad_vota')[['mun_name','population','turnout','pct_ad_vota','pct_ad_sinderecho','pct_ad_abst']].head(12).round(3).to_string())
