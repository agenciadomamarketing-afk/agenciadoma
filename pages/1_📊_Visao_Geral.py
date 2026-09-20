
import streamlit as st, pandas as pd, pathlib, base64
from datetime import date, datetime
from utils.auth import check_login, logout
from utils.data import load_all, get_stores, agg, prev, delta, fp
from utils.charts import kpi, trend
from utils.styles import GLOBAL_CSS

st.set_page_config(page_title="Visão Geral · Doma",page_icon="📊",layout="wide")
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
ps,pe=prev(s,e); data=load_all(); df=data.get("semanal",pd.DataFrame())
cur=agg(df,loja,s,e); pv=agg(df,loja,ps,pe)

def brl(v): return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
def d(k): return delta(cur.get(k,0),pv.get(k,0))

st.markdown('<div class="page-title">📊 Visão Geral</div>',unsafe_allow_html=True)
st.caption(f"{loja}  ·  {sd} → {ed}  ·  comparando com {ps.date()} → {pe.date()}")
st.markdown("---")

c1,c2,c3,c4=st.columns(4)
with c1: st.markdown(kpi("Faturamento Bruto",brl(cur.get("fat_bruto",0)),d("fat_bruto")),unsafe_allow_html=True)
with c2: st.markdown(kpi("Fat. Líquido",brl(cur.get("fat_liquido",0)),d("fat_liquido")),unsafe_allow_html=True)
with c3: st.markdown(kpi("Pedidos",f"{int(cur.get('pedidos',0)):,}",d("pedidos")),unsafe_allow_html=True)
with c4: st.markdown(kpi("Ticket Médio",brl(cur.get("ticket_medio",0)),d("ticket_medio")),unsafe_allow_html=True)
st.markdown("<br>",unsafe_allow_html=True)
c5,c6,c7,c8=st.columns(4)
with c5: st.markdown(kpi("Clientes Novos",f"{int(cur.get('clientes_novos',0)):,}",d("clientes_novos")),unsafe_allow_html=True)
with c6: st.markdown(kpi("Cancelamentos",f"{int(cur.get('cancelamentos',0)):,}",d("cancelamentos"),alert=True),unsafe_allow_html=True)
with c7: st.markdown(kpi("Repasse Previsto",brl(cur.get("repasse",0))),unsafe_allow_html=True)
with c8: st.markdown(kpi("Promoções (loja)",brl(cur.get("promocoes_loja",0)),d("promocoes_loja")),unsafe_allow_html=True)

st.markdown("---")
ldf=df[df["loja_nome"]==loja].copy() if "loja_nome" in df.columns else pd.DataFrame()
if not ldf.empty:
    ldf["data_inicio"]=pd.to_datetime(ldf["data_inicio"],errors="coerce"); ldf=ldf.sort_values("data_inicio")
    for c in ["fat_bruto","fat_liquido","pedidos","clientes_novos"]:
        if c in ldf.columns: ldf[c]=pd.to_numeric(ldf[c],errors="coerce")
    t1,t2=st.tabs(["💰 Financeiro","📦 Volume"])
    with t1: st.plotly_chart(trend(ldf,"data_inicio",["fat_bruto","fat_liquido","repasse"],["Fat. Bruto","Fat. Líquido","Repasse"],"Evolução Financeira"),use_container_width=True)
    with t2: st.plotly_chart(trend(ldf,"data_inicio",["pedidos","clientes_novos","cancelamentos"],["Pedidos","Clientes Novos","Cancelamentos"],"Volume de Pedidos"),use_container_width=True)

st.markdown("---"); st.markdown("### 🚦 Alertas")
fat_b=cur.get("fat_bruto",0); fat_l=cur.get("fat_liquido",0)
alerts=[]
if fat_b>0:
    pct=fat_l/fat_b
    alerts.append(("🟢" if pct>=0.40 else ("🟡" if pct>=0.30 else "🔴"),f"Fat. líquido = {pct:.1%} do bruto"))
if d("cancelamentos") and d("cancelamentos")>0.15: alerts.append(("🔴","Cancelamentos +{:.0%} vs mês anterior".format(d("cancelamentos"))))
if d("clientes_novos") and d("clientes_novos")>0.10: alerts.append(("🟢","Clientes novos +{:.0%} vs mês anterior".format(d("clientes_novos"))))
[st.markdown(f"{i} {m}") for i,m in alerts] if alerts else st.info("Nenhum alerta crítico no período.")
