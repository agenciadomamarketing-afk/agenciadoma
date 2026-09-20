
import streamlit as st, pandas as pd, plotly.express as px, pathlib, base64
from datetime import date, datetime
from utils.auth import check_login, logout
from utils.data import load_all, get_stores, fp
from utils.charts import kpi
from utils.styles import GLOBAL_CSS

st.set_page_config(page_title="Promoções · Doma",page_icon="📢",layout="wide")
st.markdown(GLOBAL_CSS,unsafe_allow_html=True)
if not check_login(): st.stop()


with st.sidebar:
    logo=pathlib.Path("assets/logo_doma_white.png")
    if logo.exists():
        b64=base64.b64encode(logo.read_bytes()).decode()
        st.markdown(f'<div style="text-align:center;padding:18px 0 8px"><img src="data:image/png;base64,{{b64}}" style="height:36px"></div>',unsafe_allow_html=True)
    data=load_all(); stores=get_stores(data)
    loja=st.selectbox("🏪 Loja",stores,key="loja_global") if stores else None
    st.markdown("---"); st.markdown("**📅 Período**")
    c1,c2=st.columns(2)
    with c1: sd=st.date_input("De",value=date(2026,9,1),key="start_global",label_visibility="collapsed")
    with c2: ed=st.date_input("Até",value=date(2026,9,19),key="end_global",label_visibility="collapsed")
    st.caption(f"{{sd}} → {{ed}}")
    st.markdown("---")
    if st.button("🚪 Sair",use_container_width=True): logout()

if not loja: st.warning("Selecione uma loja."); st.stop()

s=datetime.combine(sd,datetime.min.time()); e=datetime.combine(ed,datetime.min.time())
df=load_all().get("campanhas",pd.DataFrame())
if "loja_nome" in df.columns: df=df[df["loja_nome"]==loja]
df=fp(df,s,e)
def brl(v): return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

st.markdown('<div class="page-title">📢 Promoções</div>',unsafe_allow_html=True)
st.caption(f"{loja}  ·  {sd} → {ed}")
st.markdown("---")

if df.empty: st.info("Sem dados de campanha para este período."); st.stop()
for c in ["pedidos","subsidio_loja"]:
    if c in df.columns: df[c]=pd.to_numeric(df[c],errors="coerce").fillna(0)

total_ped=int(df["pedidos"].sum()) if "pedidos" in df.columns else 0
total_sub=df["subsidio_loja"].sum() if "subsidio_loja" in df.columns else 0
n_camps=df["campanha"].nunique() if "campanha" in df.columns else 0
cpp=total_sub/total_ped if total_ped>0 else 0

c1,c2,c3,c4=st.columns(4)
with c1: st.markdown(kpi("Pedidos c/ Campanha",f"{total_ped:,}"),unsafe_allow_html=True)
with c2: st.markdown(kpi("Subsídio Total",brl(total_sub)),unsafe_allow_html=True)
with c3: st.markdown(kpi("Campanhas Ativas",str(n_camps)),unsafe_allow_html=True)
with c4: st.markdown(kpi("Custo por Pedido",brl(cpp)),unsafe_allow_html=True)

st.markdown("---")
def veredito(row):
    if row.get("pedidos",0)==0: return "⏸️ Pausar"
    if row.get("subsidio_loja",0)==0: return "✅ Manter (sem custo)"
    roi=(row["pedidos"]*50-row["subsidio_loja"])/row["subsidio_loja"]
    return "✅ Manter" if roi>2 else ("⚠️ Revisar" if roi>0.5 else "⏸️ Pausar")
df["veredito"]=df.apply(veredito,axis=1)
cols=[c for c in ["campanha","tipo","pedidos","subsidio_loja","veredito"] if c in df.columns]
st.markdown("### 🏆 Ranking de Campanhas")
st.dataframe(df[cols].sort_values("pedidos",ascending=False) if "pedidos" in df.columns else df[cols],use_container_width=True,hide_index=True)

if "tipo" in df.columns:
    st.markdown("---")
    tipo_df=df.groupby("tipo")["pedidos"].sum().reset_index()
    fig=px.bar(tipo_df,x="tipo",y="pedidos",color="tipo",
        color_discrete_sequence=["#E91D2B","#C01020","#900C1A","#F5A623","#1DB954"],
        labels={"pedidos":"Pedidos","tipo":"Tipo"})
    fig.update_layout(paper_bgcolor="#1A1A1A",plot_bgcolor="#1A1A1A",
        font=dict(color="#FFFFFF"),showlegend=False,height=320,margin=dict(l=20,r=20,t=20,b=20))
    st.plotly_chart(fig,use_container_width=True)

st.markdown("---"); st.markdown("### 💡 Recomendações")
pausar=df[df["veredito"].str.contains("Pausar",na=False)]
manter=df[df["veredito"].str.contains("Manter",na=False)]
if not pausar.empty: st.error(f"⏸️ **Pausar ({len(pausar)}):** {', '.join(pausar['campanha'].tolist()[:3])}")
if not manter.empty: st.success(f"✅ **Manter ({len(manter)}):** {', '.join(manter['campanha'].tolist()[:3])}")
