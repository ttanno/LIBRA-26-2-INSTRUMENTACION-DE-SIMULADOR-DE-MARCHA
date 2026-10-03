import glob, re, sys, pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
rows=[]
for f in sorted(glob.glob("angulos_20260929_171116_*deg_*.csv")):
    m=re.search(r"_(\d+)deg_(\d+)\.csv",f); d=pd.read_csv(f)
    r=d["roll"]; rows.append(dict(ensayo=int(m[2]),angulo_real=int(m[1]),n=len(r),media=r.mean(),std=r.std(ddof=1),error=r.mean()-int(m[1])))
EXCL=[int(v) for v in sys.argv[1:]]  # ensayos a excluir
t=pd.DataFrame(rows).sort_values("ensayo"); t=t[~t.ensayo.isin(EXCL)].reset_index(drop=True); t["pos"]=range(len(t))
suf="_sin"+"-".join(map(str,EXCL)) if EXCL else ""
t.drop(columns='pos').to_csv(f"angulos_20260929_171116_std_roll{suf}.csv",index=False,float_format="%.4f")
print(t.to_string(index=False))
g=t.groupby("angulo_real")
fig,(a,b)=plt.subplots(1,2,figsize=(11,4.5))
ink="#333";blue="#2a6fdb"
x=np.array([0,t.angulo_real.max()]); a.plot(x,x,"--",color="#999",lw=1.2,label="Ideal (medido = real)")
n0=(t.angulo_real==0).sum(); jit={0:list(np.linspace(-0.3*(n0-1),0.3*(n0-1),n0))}; cnt={}
for _,r in t.iterrows():
    k=r.angulo_real; i=cnt.get(k,0); cnt[k]=i+1; dx=jit.get(k,[0])[i] if k in jit else 0
    a.errorbar(k+dx,r.media,yerr=r["std"],fmt="o",ms=7,color=blue,ecolor=ink,elinewidth=1.2,capsize=5,
               label="Media ± std (roll)" if _==t.index[0] else None)
    b.bar(r.pos,r["std"],color=blue,width=0.6)
    b.text(r.pos,r["std"]+0.01,f"{r['std']:.3f}°",ha="center",fontsize=8,color=ink)
a.set_xlabel("Ángulo real (°)"); a.set_ylabel("Roll medido (°)"); a.set_title("Roll medido vs. ángulo conocido")
a.set_xticks(sorted(t.angulo_real.unique())); a.grid(alpha=.25); a.legend(frameon=False,loc="upper left")
b.set_xticks(t.pos); b.set_xticklabels([f"#{e}\n{k}°" for e,k in zip(t.ensayo,t.angulo_real)])
b.set_xlabel("Ensayo / ángulo real"); b.set_ylabel("Desviación estándar (°)"); b.set_title("Dispersión por ensayo (std, 30 s, n≈257)")
b.set_ylim(0,max(t["std"])*1.2+0.02); b.grid(axis="y",alpha=.25)
for ax in (a,b): [ax.spines[s].set_visible(False) for s in ("top","right")]
fig.suptitle("BNO055 – prueba de ángulos conocidos (29/09/2026)"+(f"\nexcluidos ensayos {EXCL} (a pedido)" if EXCL else ""),fontweight="bold"); fig.tight_layout()
fig.savefig(f"angulos_20260929_171116_std_roll{suf}.png",dpi=160)
