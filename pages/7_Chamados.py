import streamlit as st
import pandas as pd
import plotly.express as px
import pathlib
import base64
from datetime import date
from utils.auth import check_login, logout
from utils.data import load_all, get_stores
from utils.charts import kpi
from utils.styles import GLOBAL_CSS

st.set_page_config(page_title="Chamados · Doma", page_icon="assets/logo_doma_white.png", layout="wide")
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
    if st.button("Sair", use_container_width=True):
        logout()
if not loja:
    st.warning("Selecione uma loja no menu lateral.")
    st.stop()

df = load_all().get("chamados", pd.DataFrame())
if "loja_nome" in df.columns:
    df = df[df["loja_nome"] == loja]

st.markdown('<div class="page-title">Chamados em Aberto</div>', unsafe_allow_html=True)
st.caption(str(loja))
st.markdown("---")

if df.empty:
    st.success("Nenhum chamado registrado.")
    st.stop()

if "quantidade" in df.columns:
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce").fillna(0)

total    = int(df["quantidade"].sum()) if "quantidade" in df.columns else len(df)
abertos  = int(df[df["status"]=="Aberto"]["quantidade"].sum()) if "status" in df.columns else 0
andamento= int(df[df["status"]=="Em andamento"]["quantidade"].sum()) if "status" in df.columns else 0

c1, c2, c3 = st.columns(3)
with c1: st.markdown(kpi("Total", str(total)), unsafe_allow_html=True)
with c2: st.markdown(kpi("Em Aberto", str(abertos), None, alert=(abertos>10)), unsafe_allow_html=True)
with c3: st.markdown(kpi("Em Andamento", str(andamento)), unsafe_allow_html=True)

st.markdown("---")
cols = [c for c in ["motivo","quantidade","status","data"] if c in df.columns]
if "quantidade" in df.columns:
    st.dataframe(df[cols].sort_values("quantidade", ascending=False),
                 use_container_width=True, hide_index=True)

if "motivo" in df.columns and "quantidade" in df.columns:
    st.markdown("---")
    fig = px.bar(df.sort_values("quantidade"), x="quantidade", y="motivo",
                 orientation="h", color="status" if "status" in df.columns else None,
                 color_discrete_map={"Aberto":"#C0392B","Em andamento":"#F5A623","Fechado":"#1DB954"})
    fig.update_layout(paper_bgcolor="#1A1A1A", plot_bgcolor="#1A1A1A",
                      font=dict(color="#FFFFFF"), height=320,
                      margin=dict(l=20,r=20,t=20,b=20))
    st.plotly_chart(fig, use_container_width=True)
