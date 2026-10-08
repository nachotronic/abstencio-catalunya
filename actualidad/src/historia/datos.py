# Datos de los gráficos de la serie «Historia electoral» (8-10-2026). Escribe datos.json.
import pandas as pd, numpy as np, json
H='/mnt/project-files/generales/datos/historico/'
d=pd.read_csv(H+'municipios_largo.csv.gz',dtype={'mun_code':str})
c=pd.read_csv(H+'candidaturas_municipio.csv.gz',dtype={'mun_code':str})
fam=['PP','PSOE','VOX','SUMAR','CS','UPYD','ERC','JUNTS','PNV','BILDU','BNG','CC','UCD','CDS','OTROS']
fams=[f for f in fam if f!='OTROS']
d['val']=d[fam].sum(axis=1)
G=d[d.tipo=='generales'].copy()
EL=sorted(G.eleccion.unique()); YR={e:e[:4] if e!='2019_04' and e!='2019_11' else ('2019-A' if e=='2019_04' else '2019-N') for e in EL}
names=G.drop_duplicates('mun_code',keep='last').set_index('mun_code')[['municipio','provincia']]
cg=c[c.eleccion.str.match(r'^\d')]
top=cg.sort_values('votos').groupby(['eleccion','mun_code']).tail(1).set_index(['eleccion','mun_code'])
G=G.set_index(['eleccion','mun_code']); G['win']=G.gana
pre=G.index.get_level_values(0)<'2004'; G.loc[pre,'win']=top.familia.reindex(G.index[pre]).values
G=G.reset_index()
W=G.pivot(index='mun_code',columns='eleccion',values='win')
nat=G.groupby('eleccion')[fam].sum(); natp=nat.div(nat.sum(axis=1),axis=0); natwin=nat[fams].idxmax(axis=1)
cen23=G[G.eleccion=='2023_07'].set_index('mun_code').censo
full=W.dropna()
D={'elecciones':[YR[e] for e in EL]}
r2=lambda x: None if pd.isna(x) else round(float(x)*100,1)
# 1 Ohios
hit=full.eq(natwin,axis=1).all(axis=1)
oh=full[hit].join(names).join(cen23).sort_values('censo',ascending=False)
D['ohio']={'n':int(hit.sum()),'n_pre23':int(W.drop(columns='2023_07').dropna().eq(natwin.drop('2023_07'),axis=1).all(axis=1).sum()),
 'nacional':natwin.tolist(),
 'filas':[[r.municipio,r.provincia,int(r.censo),[r[e] for e in EL]] for _,r in oh.iterrows()]}
# fails in 2023 among pre-23 ohios
p23=W.drop(columns='2023_07').dropna(); h23=p23.eq(natwin.drop('2023_07'),axis=1).all(axis=1)
fallan=W.loc[h23[h23].index,'2023_07'].value_counts().to_dict(); D['ohio']['fallan23']=fallan
acc=[]
for k in range(len(EL)):
    sub=W[EL[:k+1]].dropna(); acc.append(int(sub.eq(natwin[EL[:k+1]],axis=1).all(axis=1).sum()))
D['ohio']['supervivientes']=acc; D['ohio']['comparables']=int(len(full))
# 2 fieles
same=full[full.nunique(axis=1)==1]; s=same.iloc[:,0]
fz=same.join(names).join(cen23).sort_values('censo',ascending=False)
D['fieles']={'n':len(same),'por_familia':s.value_counts().to_dict(),
 'top':[[r.municipio,r.provincia,int(r.censo),r['1977_06']] for _,r in fz.head(15).iterrows()],
 'pp':[[r.municipio,r.provincia,int(r.censo)] for _,r in fz[fz['1977_06']=='PP'].iterrows()],
 'por_prov_psoe':fz[fz['1977_06']=='PSOE'].provincia.value_counts().head(8).to_dict()}
# 3 UCD/Cs
D['hundimiento']={'serie':{f:[r2(natp.loc[e,f]) for e in EL] for f in ['UCD','CDS','PP','PSOE','CS','VOX','SUMAR']},
 'ganados':{e:{f:int(v) for f,v in G[G.eleccion==e].win.value_counts().items()} for e in ['1977_06','1979_03','1982_10','1986_06','2015_12','2016_06','2019_04','2019_11','2023_07']}}
# 4 derecha
def e_(x): return G[G.eleccion==x].set_index('mun_code')
a,b=e_('1977_06'),e_('2023_07')
x=(a.PP+a.UCD)/a.val; y=(b.PP+b.VOX)/b.val; ap=a.PP/a.val; vx=b.VOX/b.val
m=pd.concat([x.rename('x'),y.rename('y'),ap.rename('ap'),vx.rename('vox'),b.censo.rename('c'),b.provincia],axis=1).dropna()
m=m[m.c>=5000]
D['derecha']={'puntos':[[round(r.x*100,1),round(r.y*100,1),round(r.ap*100,1),round(r.vox*100,1),names.municipio[i],int(r.c)] for i,r in m.iterrows()],
 'corr_xy':round(m[['x','y']].corr().iloc[0,1],2),'corr_apvox':round(m[['ap','vox']].corr().iloc[0,1],2),'n':len(m)}
# 5 censo
P=G.pivot(index='mun_code',columns='eleccion',values='censo')
jump=(P.pct_change(axis=1).abs()>0.25).any(axis=1)
cc=P[['1977_06','2023_07']].dropna(); cc=cc[~jump.reindex(cc.index).fillna(False)]
cc['r']=cc['2023_07']/cc['1977_06']; cc=cc.join(names)
grow=P[['1977_06','2023_07']].dropna(); grow=grow.join(names); grow['r']=grow['2023_07']/grow['1977_06']
prov=cc.assign(menos=cc.r<1).groupby('provincia').menos.mean().sort_values(ascending=False)
D['censo_pueblos']={'n':len(cc),'menos':int((cc.r<1).sum()),'perdidos':int((cc['1977_06']-cc['2023_07'])[cc.r<1].sum()),
 'caidas':[[r.municipio,r.provincia,int(r['1977_06']),int(r['2023_07'])] for _,r in cc[cc['1977_06']>=3000].sort_values('r').head(10).iterrows()],
 'subidas':[[r.municipio,r.provincia,int(r['1977_06']),int(r['2023_07'])] for _,r in grow[grow['1977_06']>=3000].sort_values('r',ascending=False).head(10).iterrows()],
 'por_provincia':[[k,round(v*100,1)] for k,v in prov.items()]}
# 8 CDS
cds=G[G.eleccion.isin(['1982_10','1986_06','1989_10','1993_06'])]
pv=cds.groupby(['eleccion','provincia'])[['CDS','val']].sum(); pv=(pv.CDS/pv.val).unstack(0)
D['cds']={'nac':[r2(natp.loc[e,'CDS']) for e in ['1982_10','1986_06','1989_10','1993_06']],
 'avila_prov':[r2(pv.loc['Ávila',e]) for e in ['1982_10','1986_06','1989_10','1993_06']],
 'avila_ciudad':[r2(G[(G.eleccion==e)&(G.mun_code=='05019')].eval('CDS/val').iloc[0]) for e in ['1982_10','1986_06','1989_10','1993_06']],
 'prov86':[[k,r2(v)] for k,v in pv['1986_06'].sort_values(ascending=False).head(12).items()]}
# 9 Trebujena
t=G[G.mun_code=='11037'].set_index('eleccion')
D['trebujena']={'sumar':[r2((t.SUMAR/t.val).get(e)) for e in EL],'psoe':[r2((t.PSOE/t.val).get(e)) for e in EL],'nac_sumar':[r2(natp.loc[e,'SUMAR']) for e in EL],
 'part':[r2(t.part.get(e)) for e in EL]}
pce=a.SUMAR/a.val; t77=pce[a.censo>=2000].sort_values(ascending=False).head(10)
D['trebujena']['top77']=[[names.municipio[i],names.provincia[i],r2(v),r2((b.SUMAR/b.val).get(i))] for i,v in t77.items()]
mm=pd.concat([pce.rename('x'),(b.SUMAR/b.val).rename('y'),b.censo.rename('c')],axis=1).dropna(); mm=mm[mm.c>=1000]
D['trebujena']['corr']=round(mm[['x','y']].corr().iloc[0,1],2)
# 10 PSOE >60
D['psoe60']={'n':[int(((G[G.eleccion==e].PSOE/G[G.eleccion==e].val)>.6).sum()) for e in EL],'nac':[r2(natp.loc[e,'PSOE']) for e in EL]}
c82=e_('1982_10'); lb=pd.concat([c82.PSOE/c82.val,b.PSOE/b.val,b.censo],axis=1).dropna(); lb.columns=['p82','p23','c']; lb=lb[lb.c>=20000]; lb['d']=lb.p23-lb.p82
D['psoe60']['caidas']=[[names.municipio[i],names.provincia[i],r2(r.p82),r2(r.p23)] for i,r in lb.sort_values('d').head(10).iterrows()]
# 11/12
right={'PP','UCD','VOX','CS','CDS'}; lest={'PSOE','SUMAR'}
nr=full[full.apply(lambda x: not set(x)&right,axis=1)].join(names).join(cen23).sort_values('censo',ascending=False)
nl=full[full.apply(lambda x: not set(x)&lest,axis=1)].join(names).join(cen23).sort_values('censo',ascending=False)
def ganadores(r): return sorted(set(r[e] for e in EL))
D['nunca_derecha']={'n':len(nr),'electores':int(nr.censo.sum()),'top':[[r.municipio,r.provincia,int(r.censo),ganadores(r)] for _,r in nr.head(15).iterrows()],
 'por_ccaa_prov':nr.provincia.value_counts().head(10).to_dict()}
D['nunca_psoe']={'n':len(nl),'electores':int(nl.censo.sum()),'top':[[r.municipio,r.provincia,int(r.censo),ganadores(r)] for _,r in nl.head(15).iterrows()],
 'por_prov':nl.provincia.value_counts().head(10).to_dict(),'con_erc':int(nl.apply(lambda r:'ERC' in ganadores(r),axis=1).sum())}
# 13 cambiantes
chg=(full.ne(full.shift(axis=1))).sum(axis=1)-1; nu=full.nunique(axis=1)
z=pd.concat([chg.rename('k'),nu.rename('u')],axis=1).join(names).join(cen23); z=z[z.censo>=5000].sort_values(['k','u'],ascending=False)
D['cambiantes']={'filas':[[r.municipio,r.provincia,int(r.censo),int(r.k),int(r.u),[full.loc[i,e] for e in EL]] for i,r in z.head(8).iterrows()],
 'media_cambios':round(float(chg[cen23.reindex(chg.index)>=5000].mean()),1)}
# 14 Baltar/Paradela
D['baltar']={m:{'censo':[None if pd.isna(v) else int(v) for v in G[G.mun_code==code].set_index('eleccion').censo.reindex(EL)],
 'part':[r2(v) for v in G[G.mun_code==code].set_index('eleccion').part.reindex(EL)]} for m,code in [('Baltar','32005'),('Paradela','27042')]}
og=G[G.provincia.isin(['Ourense','Lugo'])].groupby(['eleccion','provincia'])[['votantes','censo']].sum()
og=(og.votantes/og.censo).unstack(); D['baltar']['prov']={p:[r2(og.loc[e,p]) for e in EL] for p in ['Ourense','Lugo']}
D['baltar']['nac']=[r2(G[G.eleccion==e].votantes.sum()/G[G.eleccion==e].censo.sum()) for e in EL]
cprov=G[G.provincia.isin(['Ourense','Lugo'])].groupby(['eleccion','provincia']).censo.sum().unstack()
D['baltar']['censo_prov']={p:[int(cprov.loc[e,p]) for e in EL] for p in ['Ourense','Lugo']}
low=G[(G.eleccion=='1979_03')&(G.censo>=1000)].sort_values('part').head(10)
D['baltar']['bajas79']=[[r.municipio,r.provincia,r2(r.part)] for _,r in low.iterrows()]
# 15/20 europeas
eu=d[d.tipo=='europeas']; x=eu[(eu.eleccion=='E2014')&(eu.censo>=20000)].sort_values('part')
D['europeas']={'bajas14':[[r.municipio,r.provincia,int(r.censo),r2(r.part)] for _,r in x.head(10).iterrows()],
 'altas14':[[r.municipio,r.provincia,int(r.censo),r2(r.part)] for _,r in x.tail(3).iterrows()]}
tot=d.groupby(['eleccion','tipo'])[['votantes','censo']].sum().reset_index(); tot['part']=tot.votantes/tot.censo
D['todas']=[[r.eleccion,r.tipo,r2(r.part)] for _,r in tot.iterrows()]
prov_eu=eu[eu.eleccion=='E2014'].groupby('provincia')[['votantes','censo']].sum(); prov_eu=(prov_eu.votantes/prov_eu.censo).sort_values()
D['europeas']['prov14']=[[k,r2(v)] for k,v in prov_eu.items()]
cmp=[]
for m in ['Arona','Ceuta','Granadilla de Abona','Arrecife','Melilla','Adeje']:
    e14=eu[(eu.eleccion=='E2014')&(eu.municipio==m)].iloc[0]; g15=G[(G.eleccion=='2015_12')&(G.municipio==m)].iloc[0]
    cmp.append([m,int(e14.censo),int(g15.censo),r2(e14.part),r2(g15.part)])
D['europeas']['comparacion']=cmp
# 16 Euskadi
pvv=G[G.provincia.isin(['Bizkaia','Gipuzkoa','Araba/Álava'])].groupby('eleccion')[fam].sum(); s=pvv.div(pvv.sum(axis=1),axis=0)
D['euskadi']={f:[r2(s.loc[e,f]) for e in EL] for f in ['PNV','PSOE','BILDU','PP','SUMAR','UCD']}
D['euskadi']['dif3']=[round(float(np.sort(s.loc[e,fams].values)[::-1][0]-np.sort(s.loc[e,fams].values)[::-1][2])*100,1) for e in EL]
pvp=G[G.provincia.isin(['Bizkaia','Gipuzkoa','Araba/Álava'])&(G.eleccion=='2023_07')].groupby('provincia')[fam].sum(); pvp=pvp.div(pvp.sum(axis=1),axis=0)
D['euskadi']['prov23']={p:{f:r2(pvp.loc[p,f]) for f in ['PSOE','PNV','BILDU','PP','SUMAR']} for p in pvp.index}
w23=G[G.provincia.isin(['Bizkaia','Gipuzkoa','Araba/Álava'])&(G.eleccion=='2023_07')].win.value_counts().to_dict(); D['euskadi']['munis23']=w23
# 17 blanco
bl=cg.drop_duplicates(['eleccion','mun_code']).groupby('eleccion')[['votantes','blancos','nulos']].sum()
x=pd.read_csv('/mnt/project-files/generales/datos/resultados_secciones_largo.csv',usecols=['eleccion','blancos','nulos','votantes'])
x=x[x.eleccion.str.match(r'^\d')].groupby('eleccion').sum()
bb=pd.concat([bl,x]); D['blanco']={'blancos':[round(float(bb.loc[e,'blancos']/bb.loc[e,'votantes'])*100,2) for e in EL],'nulos':[round(float(bb.loc[e,'nulos']/bb.loc[e,'votantes'])*100,2) for e in EL],
 'blancos_abs':[int(bb.loc[e,'blancos']) for e in EL]}
# 18 PSA
ps=cg[(cg.eleccion.isin(['1977_06','1979_03','1982_10']))&cg.siglas.str.contains(r'^PSA|PSA-PA|^PA$',na=False)]
D['psa']={'siglas':ps.groupby(['eleccion','siglas']).votos.sum().astype(int).reset_index().values.tolist()}
ps79=cg[(cg.eleccion=='1979_03')&(cg.siglas=='PSA-PA')].merge(names.reset_index(),on='mun_code',how='left')
v79=cg[cg.eleccion=='1979_03'].groupby('mun_code').votos.sum()
ps79['val']=ps79.mun_code.map(v79)
pp=ps79.groupby('provincia')[['votos','val']].sum(); pp['p']=pp.votos/pp.val
D['psa']['prov79']=[[k,int(r.votos),r2(r.p)] for k,r in pp.sort_values('p',ascending=False).iterrows()]
ps79['p']=ps79.votos/ps79.val; tp=ps79[ps79.val>=2000].sort_values('p',ascending=False).head(10)
D['psa']['top79']=[[r.municipio,r.provincia,r2(r.p)] for _,r in tp.iterrows()]
D['psa']['otras_prov']=[k for k in pp.index if k not in ['Almería','Cádiz','Córdoba','Granada','Huelva','Jaén','Málaga','Sevilla']]
D['cds']['ucd79_avila']=r2(G[(G.eleccion=='1979_03')&(G.provincia=='Ávila')].UCD.sum()/G[(G.eleccion=='1979_03')&(G.provincia=='Ávila')].val.sum())
# 19 censo total
D['censo']={'total':[int(G[G.eleccion==e].censo.sum()) for e in EL]}
import os; json.dump(D,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos.json'),'w'),ensure_ascii=False,default=str)
print(D['ohio']['supervivientes'],D['ohio']['comparables'])
