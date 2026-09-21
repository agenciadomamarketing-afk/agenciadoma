import streamlit as st
import pandas as pd
import plotly.express as px
import pathlib
import base64
from datetime import date, datetime
from utils.auth import check_login, logout
from utils.data import load_all, get_stores, fp
from utils.charts import kpi
from utils.styles import GLOBAL_CSS, render_alert, render_table, render_navigation

st.set_page_config(page_title="Promocoes · Doma", page_icon="assets/logo_doma_white.png", layout="wide")
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
    render_navigation("Promocoes")
    st.markdown("---")
    if st.button("Sair", use_container_width=True):
        logout()
if not loja:
    render_alert("Selecione uma loja no menu lateral.", "warning")
    st.stop()

s = datetime.combine(sd, datetime.min.time())
e = datetime.combine(ed, datetime.min.time())
df = load_all().get("campanhas", pd.DataFrame())
if "loja_nome" in df.columns:
    df = df[df["loja_nome"] == loja]
df = fp(df, s, e)

def brl(v): return "R$ {:,.2f}".format(v).replace(",","X").replace(".",",").replace("X",".")

st.markdown('<div class="page-title">Promocoes</div>', unsafe_allow_html=True)
st.caption(str(loja) + "  ·  " + str(sd) + " → " + str(ed))
st.markdown("---")

if df.empty:
    render_alert("Sem dados de campanha para este periodo.", "info")
    st.stop()

for c in ["pedidos","subsidio_loja"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

total_ped = int(df["pedidos"].sum()) if "pedidos" in df.columns else 0
total_sub = df["subsidio_loja"].sum() if "subsidio_loja" in df.columns else 0
n_camps   = df["campanha"].nunique() if "campanha" in df.columns else 0
cpp = total_sub / total_ped if total_ped > 0 else 0

c1,c2,c3,c4 = st.columns(4)
with c1: st.markdown(kpi("Pedidos c/ Campanha", str(total_ped)), unsafe_allow_html=True)
with c2: st.markdown(kpi("Subsidio Total", brl(total_sub)), unsafe_allow_html=True)
with c3: st.markdown(kpi("Campanhas Ativas", str(n_camps)), unsafe_allow_html=True)
with c4: st.markdown(kpi("Custo por Pedido", brl(cpp)), unsafe_allow_html=True)

def veredito(row):
    if row.get("pedidos", 0) == 0: return "Pausar"
    if row.get("subsidio_loja", 0) == 0: return "Manter (sem custo)"
    roi = (row["pedidos"] * 50 - row["subsidio_loja"]) / row["subsidio_loja"]
    return "Manter" if roi > 2 else ("Revisar" if roi > 0.5 else "Pausar")

df["veredito"] = df.apply(veredito, axis=1)
cols = [c for c in ["campanha","tipo","pedidos","subsidio_loja","veredito"] if c in df.columns]
st.markdown("---")
st.markdown("### Ranking de Campanhas")
if "pedidos" in df.columns:
    render_table(df[cols].sort_values("pedidos", ascending=False),
                 use_container_width=True, hide_index=True)

st.markdown("---")
pausar = df[df["veredito"].str.contains("Pausar", na=False)]
manter = df[df["veredito"].str.contains("Manter", na=False)]
if not pausar.empty:
    render_alert("Pausar: " + ", ".join(pausar["campanha"].tolist()[:3]), "error")
if not manter.empty:
    render_alert("Manter: " + ", ".join(manter["campanha"].tolist()[:3]), "success")
