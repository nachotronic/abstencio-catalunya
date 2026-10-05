import geopandas as gpd, pandas as pd, json, numpy as np
from shapely.geometry import Polygon
d=pd.read_csv('/mnt/project-files/abstencion/catalunya_secciones_2023.csv',dtype={'tract_code':str,'mun_code':str})
g=gpd.read_file('/mnt/project-files/abstencion/catalunya_secciones_2023.geojson')[['tract_code','geometry']]
g=g.merge(d,on='tract_code',how='left')
mn=d.groupby('mun_code').mun_name.first(); g['mun_code']=g.tract_code.str[:5]; g['mun_name']=g.mun_code.map(mn)
g=g.to_crs(25831); g['geometry']=g.geometry.simplify(15,preserve_topology=True); g=g[~g.geometry.is_empty].to_crs(4326).reset_index(drop=True)
S=10000
polys=[]  # flat list: [sectionIndex, deltaEncoded outer ring]
for i,geom in enumerate(g.geometry):
    parts=[geom] if isinstance(geom,Polygon) else list(geom.geoms)
    for p in parts:
        cs=[(round(x*S),round(y*S)) for x,y in p.exterior.coords[:-1]]
        cs=[c for k,c in enumerate(cs) if k==0 or c!=cs[k-1]]
        if len(cs)<3: continue
        flat=[cs[0][0],cs[0][1]]
        for k in range(1,len(cs)): flat+= [cs[k][0]-cs[k-1][0], cs[k][1]-cs[k-1][1]]
        polys.append([i,flat])
props=['tract_code','mun_name','electorate','voters','turnout','t2015_12','t2016_06','t2019_04','t2019_11','t2023_07','drop_19_23','population','adults','pct_ad_vota','pct_ad_sinderecho','net_income_equiv','mean_age','pct_foreign','pct_naturalized','pct_higher_ed_completed','unemployment_rate','pct_secondary','indep_share19']
cols={}
for k in props:
    v=g[k].tolist()
    if k not in ('tract_code','mun_name'):
        dig=0 if k in ('electorate','voters','population','net_income_equiv') else (1 if k in ('adults','mean_age') else 3)
        v=[None if pd.isna(x) else (int(round(x)) if dig==0 else round(float(x),dig)) for x in v]
    cols[k]=v
names=sorted(set(x for x in cols['mun_name'] if isinstance(x,str))); idx={n:i for i,n in enumerate(names)}
cols['mun_name']=[idx.get(n,-1) for n in cols['mun_name']]
# municipality centroids for flyTo / labels
cent={}
for n,sub in g.groupby('mun_name'):
    c=sub.to_crs(25831).dissolve().geometry.iloc[0].centroid; c=gpd.GeoSeries([c],crs=25831).to_crs(4326).iloc[0]; cent[n]=[round(c.x,4),round(c.y,4)]
out={'S':S,'names':names,'cols':cols,'polys':polys,'cent':cent}
s=json.dumps(out,separators=(',',':')); open('geo3d.json','w').write(s); print(len(s), len(polys), len(g))
