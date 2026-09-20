
import streamlit as st, pandas as pd, pathlib, base64
from datetime import date, datetime
from utils.auth import check_login, logout
from utils.data import load_all, get_stores, agg, prev, delta, fp
from utils.charts import kpi, trend, waterfall
from utils.styles import GLOBAL_CSS

st.set_page_config(page_title="Financeiro · Doma",page_icon="💰",layout="wide")
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
ps,pe=prev(s,e); df=load_all().get("semanal",pd.DataFrame())
cur=agg(df,loja,s,e); pv=agg(df,loja,ps,pe)
def brl(v): return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
def d(k): return delta(cur.get(k,0),pv.get(k,0))

st.markdown('<div class="page-title">💰 Financeiro</div>',unsafe_allow_html=True)
st.caption(f"{loja}  ·  {sd} → {ed}")
st.markdown("---")

c1,c2,c3,c4=st.columns(4)
with c1: st.markdown(kpi("Fat. Bruto",brl(cur.get("fat_bruto",0)),d("fat_bruto")),unsafe_allow_html=True)
with c2: st.markdown(kpi("Taxas e Comissões",brl(cur.get("taxas",0)),d("taxas"),alert=True),unsafe_allow_html=True)
with c3: st.markdown(kpi("Promoções (loja)",brl(cur.get("promocoes_loja",0)),d("promocoes_loja")),unsafe_allow_html=True)
with c4: st.markdown(kpi("Anúncios",brl(cur.get("anuncios",0))),unsafe_allow_html=True)
st.markdown("<br>",unsafe_allow_html=True)
c5,c6,c7,c8=st.columns(4)
with c5: st.markdown(kpi("Fat. Líquido",brl(cur.get("fat_liquido",0)),d("fat_liquido")),unsafe_allow_html=True)
with c6: st.markdown(kpi("Repasse Previsto",brl(cur.get("repasse",0))),unsafe_allow_html=True)
with c7: st.markdown(kpi("Ticket Médio",brl(cur.get("ticket_medio",0)),d("ticket_medio")),unsafe_allow_html=True)
with c8: st.markdown(kpi("Mensalidade",brl(cur.get("mensalidade",0))),unsafe_allow_html=True)

st.markdown("---"); st.markdown("### 💧 Para onde foi o dinheiro")
fb=cur.get("fat_bruto",0); tx=cur.get("taxas",0); pr=cur.get("promocoes_loja",0)
an=cur.get("anuncios",0); mn=cur.get("mensalidade",0); fl=cur.get("fat_liquido",0)
st.plotly_chart(waterfall(["Fat. Bruto","(-) Taxas","(-) Promoções","(-) Anúncios","(-) Mensalidade","Fat. Líquido"],[fb,-tx,-pr,-an,-mn,fl]),use_container_width=True)

if fb>0:
    st.markdown("---"); st.markdown("### 📊 Composição do Bruto")
    for nome,val in [("Fat. Líquido",fl/fb),("Taxas",tx/fb),("Promoções",pr/fb),("Anúncios",an/fb),("Mensalidade",mn/fb)]:
        alert_color="#C0392B" if nome=="Taxas" and val>0.25 else ("#1DB954" if nome=="Fat. Líquido" and val>=0.40 else "#E91D2B")
        st.markdown(f'<div style="display:flex;justify-content:space-between;margin-bottom:4px"><span>{nome}</span><b style="color:{alert_color}">{val:.1%}</b></div>',unsafe_allow_html=True)
        st.progress(min(val,1.0))

ldf=df[df["loja_nome"]==loja].copy() if "loja_nome" in df.columns else pd.DataFrame()
if not ldf.empty:
    ldf["data_inicio"]=pd.to_datetime(ldf["data_inicio"],errors="coerce")
    st.markdown("---"); st.plotly_chart(trend(ldf.sort_values("data_inicio"),"data_inicio",["fat_bruto","fat_liquido"],["Fat. Bruto","Fat. Líquido"],"Evolução Financeira Histórica"),use_container_width=True)
