import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pathlib
import base64
from datetime import date, datetime
from utils.auth import check_login, logout
from utils.data import load_all, get_stores, agg, prev, delta
from utils.charts import style_figure, kpi, trend
from utils.styles import GLOBAL_CSS, render_alert, render_table, render_navigation

st.set_page_config(page_title="Clientes · Doma", page_icon="assets/logo_doma_white.png", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
if not check_login():
    st.stop()

with st.sidebar:
    logo = pathlib.Path("assets/logo_doma_white.png")
    if logo.exists():
        b64 = base64.b64encode(logo.read_bytes()).decode()
        st.markdown(
            '<div style="text-align:center;padding:18px 0 8px">' +
            '<img src="data:image/png;base64,' + b64 + '" style="height:36px"></div>',
            unsafe_allow_html=True
        )
    data = load_all()
    stores = get_stores(data)
    loja = st.selectbox("Loja", stores, key="loja_global") if stores else None
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        sd = st.date_input("De", value=date(2026, 9, 1),
                           key="start_global", label_visibility="collapsed")
    with c2:
        ed = st.date_input("Ate", value=date(2026, 9, 19),
                           key="end_global", label_visibility="collapsed")
    st.caption(str(sd) + " -> " + str(ed))
    st.markdown("---")
    render_navigation("Clientes")
    st.markdown("---")
    if st.button("Sair", use_container_width=True):
        logout()
if not loja:
    render_alert("Selecione uma loja no menu lateral.", "warning")
    st.stop()

s = datetime.combine(sd, datetime.min.time())
e = datetime.combine(ed, datetime.min.time())
ps, pe = prev(s, e)
df = load_all().get("semanal", pd.DataFrame())
cur = agg(df, loja, s, e)
pv  = agg(df, loja, ps, pe)

novos = int(cur.get("clientes_novos", 0))
ped   = int(cur.get("pedidos", 0))
pct   = novos / ped if ped > 0 else 0
recorr = ped - novos

st.markdown('<div class="page-title">Clientes</div>', unsafe_allow_html=True)
st.caption(str(loja) + "  ·  " + str(sd) + " → " + str(ed))
st.markdown("---")

c1,c2,c3,c4 = st.columns(4)
with c1: st.markdown(kpi("Clientes Novos", str(novos), delta(novos, pv.get("clientes_novos",0))), unsafe_allow_html=True)
with c2: st.markdown(kpi("% Novos s/ Pedidos", "{:.1%}".format(pct), None, alert=(pct>0.60)), unsafe_allow_html=True)
with c3: st.markdown(kpi("Pedidos Recorrentes", str(recorr)), unsafe_allow_html=True)
with c4: st.markdown(kpi("Total Pedidos", str(ped), delta(ped, pv.get("pedidos",0))), unsafe_allow_html=True)

st.markdown("---")
if pct > 0.65:
    render_alert("ALERTA DE RETENCAO: {:.1%} dos pedidos sao de clientes novos. Criar estrategia de fidelizacao.".format(pct), "error")
elif pct > 0.45:
    render_alert("{:.1%} dos pedidos sao de clientes novos. Monitorar retencao.".format(pct), "warning")
else:
    render_alert("{:.1%} de pedidos novos. Base recorrente saudavel.".format(pct), "success")

c1, c2 = st.columns(2)
with c1:
    fig = go.Figure(go.Pie(
        labels=["Clientes Novos","Recorrentes"], values=[novos, recorr], hole=0.5,
        marker=dict(colors=["#E91D2B","#BBC5D6"]), textinfo="label+percent"
    ))
    fig.update_layout(paper_bgcolor="#1A1A1A", font=dict(color="#FFFFFF"),
                      height=300, margin=dict(l=0,r=0,t=20,b=0), showlegend=False)
    style_figure(fig)
    st.plotly_chart(fig, use_container_width=True, theme=None)
with c2:
    ldf = df[df["loja_nome"] == loja].copy() if "loja_nome" in df.columns else pd.DataFrame()
    if not ldf.empty:
        ldf["data_inicio"] = pd.to_datetime(ldf["data_inicio"], errors="coerce")
        ldf["clientes_novos"] = pd.to_numeric(ldf.get("clientes_novos", 0), errors="coerce")
        st.plotly_chart(trend(ldf.sort_values("data_inicio"), "data_inicio",
            ["clientes_novos"], ["Clientes Novos"], "Evolucao"), use_container_width=True, theme=None)

