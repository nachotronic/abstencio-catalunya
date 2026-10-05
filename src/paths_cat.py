import geopandas as gpd, pandas as pd, json
SIMP=15
from shapely.geometry import Polygon, MultiPolygon
import pandas as pd
d=pd.read_csv('/mnt/project-files/abstencion/catalunya_secciones_2023.csv',dtype={'tract_code':str,'mun_code':str})
g0=gpd.read_file('census_tracts_2023.gpkg',where="substr(tract_code,1,2) IN ('08','17','25','43')")
g=g0[['tract_code','geometry']].merge(d,on='tract_code',how='left').to_crs(25831)
mn=d.groupby('mun_code').mun_name.first(); g['mun_code']=g.tract_code.str[:5]; g['mun_name']=g.mun_code.map(mn)
gg=g.copy(); gg.to_crs(4326).to_file('/mnt/project-files/abstencion/catalunya_secciones_2023.geojson',driver='GeoJSON',COORDINATE_PRECISION=5)
m=g.dissolve(by='mun_code',as_index=False)
g['geometry']=g.geometry.simplify(SIMP,preserve_topology=True)
g=g[~g.geometry.is_empty]
m['geometry']=m.geometry.simplify(80,preserve_topology=True)
minx,miny,maxx,maxy=g.total_bounds; W=1000; s=W/(maxx-minx); H=(maxy-miny)*s
def tp(x,y): return f"{(x-minx)*s:.1f} {(maxy-y)*s:.1f}"
def path(geom):
    polys=[geom] if isinstance(geom,Polygon) else list(geom.geoms)
    out=[]
    for p in polys:
        for ring in [p.exterior]+list(p.interiors):
            cs=[tp(x,y) for x,y in list(ring.coords)[:-1]]
            pts=[c for i,c in enumerate(cs) if i==0 or c!=cs[i-1]]
            if len(pts)>=3: out.append('M'+'L'.join(pts)+'Z')
    return ''.join(out).replace('.0 ',' ').replace('.0L','L').replace('.0Z','Z')
props=['tract_code','mun_code','mun_name','electorate','voters','turnout','t2015_12','t2016_06','t2019_04','t2019_11','t2023_07','drop_19_23','population','adults','pct_ad_vota','pct_ad_sinderecho','pct_ad_abst','net_income_equiv','mean_age','pct_over65','pct_foreign','pct_naturalized','pct_higher_ed_completed','unemployment_rate','pct_rented','pct_secondary','indep_share19']
secs=[]
for _,r in g.iterrows():
    d={k:(None if pd.isna(r[k]) else (round(float(r[k]),4) if not isinstance(r[k],str) else r[k])) for k in props}
    d['d']=path(r.geometry); c=r.geometry.representative_point(); d['cx'],d['cy']=[round(float(v),1) for v in tp(c.x,c.y).split()]
    secs.append(d)
muns=[{'c':r.mun_code,'d':path(r.geometry)} for _,r in m.iterrows()]
# labels for key towns
lab={}
for name in ['Salt','Lloret de Mar','Figueres','Girona','Barcelona','Lleida','Tarragona','Reus','Guissona','Salou','Vic','Tortosa','Puigcerdà','Manresa','Vielha e Mijaran','Olot','Igualada','Mataró','Sabadell']:
    sub=g[g.mun_name==name]
    if len(sub): c=sub.dissolve().geometry.iloc[0].representative_point(); lab[name]=[round(float(v),1) for v in tp(c.x,c.y).split()]
json.dump({'W':W,'H':round(H,1),'secs':secs,'muns':muns,'labels':lab},open('mapdata_cat.json','w'),separators=(',',':'))
import os; print(os.path.getsize('mapdata_cat.json'), H)
