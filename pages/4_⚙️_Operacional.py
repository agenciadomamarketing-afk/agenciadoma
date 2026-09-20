
import streamlit as st, pandas as pd, pathlib, base64
from datetime import date, datetime
from utils.auth import check_login, logout
from utils.data import load_all, get_stores, agg, prev, delta, fp
from utils.charts import kpi, gauge, trend
from utils.styles import GLOBAL_CSS

st.set_page_config(page_title="Operacional · Doma",page_icon="⚙️",layout="wide")
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
def d(k): return delta(cur.get(k,0),pv.get(k,0))

disp=cur.get("disponibilidade_pct",0)*100; mtp=cur.get("mtp_minutos",0)
dct=cur.get("delta_ct_minutos",0); nre=cur.get("nre_minutos",0); rev=cur.get("review_score",0)

st.markdown('<div class="page-title">⚙️ Operacional</div>',unsafe_allow_html=True)
st.caption(f"{loja}  ·  {sd} → {ed}")
st.markdown("---")

c1,c2,c3,c4=st.columns(4)
with c1: st.plotly_chart(gauge(round(disp,1),"Disponibilidade",(80,95)),use_container_width=True)
with c2: st.plotly_chart(gauge(round(rev*20,1),"Review (×20)",(70,85)),use_container_width=True)
with c3: st.plotly_chart(gauge(round(max(0,100-nre*5),1),"NRE Score",(50,75)),use_container_width=True)
with c4: st.plotly_chart(gauge(round(max(0,100-max(0,dct)*5),1),"Delta CT Score",(50,75)),use_container_width=True)

st.markdown("---")
c1,c2,c3,c4=st.columns(4)
with c1: st.markdown(kpi("Disponibilidade",f"{disp:.1f}%",d("disponibilidade_pct")),unsafe_allow_html=True)
with c2: st.markdown(kpi("Tempo Preparo (MTP)",f"{mtp:.0f} min",d("mtp_minutos")),unsafe_allow_html=True)
with c3: st.markdown(kpi("Delta CT",f"{dct:+.1f} min",alert=(dct>10)),unsafe_allow_html=True)
with c4: st.markdown(kpi("NRE (tempo na loja)",f"{nre:.1f} min",alert=(nre>12)),unsafe_allow_html=True)

st.markdown("---"); st.markdown("### 🚦 Alertas Operacionais")
alerts=[]
if disp<80: alerts.append(("🔴","CRÍTICO",f"Disponibilidade {disp:.1f}% — abaixo de 80%"))
elif disp<90: alerts.append(("🟡","ATENÇÃO",f"Disponibilidade {disp:.1f}% — meta: 90%+"))
else: alerts.append(("🟢","OK",f"Disponibilidade {disp:.1f}%"))
if dct>10: alerts.append(("🔴","CRÍTICO",f"Delta CT {dct:.1f} min acima do prometido"))
elif dct>5: alerts.append(("🟡","ATENÇÃO",f"Delta CT {dct:.1f} min — monitorar"))
if nre>12: alerts.append(("🔴","CRÍTICO",f"NRE {nre:.1f} min — entregador aguarda demais na loja"))
for icon,status,msg in alerts:
    bg={"🔴":"#3D1010","🟡":"#3D3010","🟢":"#103D20"}.get(icon,"#1A1A1A")
    st.markdown(f'<div style="background:{bg};border-radius:8px;padding:14px 18px;margin-bottom:8px"><b>{icon} {status}</b> — {msg}</div>',unsafe_allow_html=True)
