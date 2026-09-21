import streamlit as st
import base64
import pathlib
from datetime import date
from utils.auth import check_login, logout
from utils.data import load_all, get_stores
from utils.styles import GLOBAL_CSS

st.set_page_config(
    page_title="Doma Food",
    page_icon="assets/logo_doma_white.png",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not check_login():
    st.stop()

BORD = "#2D2D2D"

with st.sidebar:
    logo = pathlib.Path("assets/logo_doma_white.png")
    if logo.exists():
        b64 = base64.b64encode(logo.read_bytes()).decode()
        st.markdown(
            '<div style="text-align:center;padding:18px 0 8px">' +
            '<img src="data:image/png;base64,' + b64 + '" style="height:36px"></div>',
            unsafe_allow_html=True
        )
    st.markdown(
        '<div style="text-align:center;color:#888;font-size:11px;' +
        'padding-bottom:14px;border-bottom:1px solid ' + BORD + '">' +
        'Dashboard iFood</div>',
        unsafe_allow_html=True
    )
    data = load_all()
    stores = get_stores(data)
    loja = st.selectbox("Loja", stores, key="loja_global") if stores else None
    st.markdown("---")
    st.markdown("**Periodo**")
    c1, c2 = st.columns(2)
    with c1:
        sd = st.date_input("De", value=date(2026, 9, 1),
                           key="start_global", label_visibility="collapsed")
    with c2:
        ed = st.date_input("Ate", value=date(2026, 9, 19),
                           key="end_global", label_visibility="collapsed")
    st.caption(str(sd) + " -> " + str(ed))
    st.markdown("---")
    st.markdown('<div class="doma-nav-label">GESTAO DE DELIVERY</div>', unsafe_allow_html=True)
    st.page_link("app.py",                       label="Inicio")
    st.page_link("pages/1_Visao_Geral.py",       label="Visao Geral")
    st.page_link("pages/2_Funil.py",             label="Funil")
    st.page_link("pages/3_Financeiro.py",        label="Financeiro")
    st.page_link("pages/4_Operacional.py",       label="Operacional")
    st.page_link("pages/5_Promocoes.py",         label="Promocoes")
    st.page_link("pages/6_Clientes.py",          label="Clientes")
    st.page_link("pages/7_Chamados.py",          label="Chamados")
    st.markdown("---")
    if st.button("Sair", use_container_width=True):
        logout()

st.markdown('<div class="page-title">Inicio</div>', unsafe_allow_html=True)
st.markdown("**Loja:** " + str(loja or "—") + "  ·  **Periodo:** " + str(sd) + " → " + str(ed))
st.markdown("---")

n = len(stores) if stores else 0
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        '<div class="doma-home-card"><b>Visao Geral</b><br>' +
        '<span style="color:#888;font-size:13px">KPIs + comparacao mes anterior</span></div>',
        unsafe_allow_html=True
    )
with c2:
    st.markdown(
        '<div class="doma-home-card"><b>' + str(n) + ' lojas ativas</b><br>' +
        '<span style="color:#888;font-size:13px">Selecione no menu lateral</span></div>',
        unsafe_allow_html=True
    )
with c3:
    st.markdown(
        '<div class="doma-home-card"><b>Google Sheets</b><br>' +
        '<span style="color:#888;font-size:13px">Atualizado toda segunda-feira</span></div>',
        unsafe_allow_html=True
    )


from html import escape
import streamlit as st

def render_alert(message, kind="info"):
    icons = {"info": "i", "success": "✓", "warning": "!", "error": "!"}
    kind = kind if kind in icons else "info"
    st.markdown(
        '<div class="doma-alert doma-alert-' + kind + '">' +
        '<span class="doma-alert-icon">' + icons[kind] + '</span>' +
        '<span>' + escape(str(message)) + '</span></div>',
        unsafe_allow_html=True
    )

def render_table(data, use_container_width=True, hide_index=True):
    import pandas as pd
    if isinstance(data, pd.DataFrame) and not data.empty:
        st.dataframe(data, use_container_width=use_container_width, hide_index=hide_index)

def render_navigation(active="app"):
  st.page_link("app.py", label="Inicio")
st.page_link("pages/1_Visao_Geral.py", label="Visao Geral")
st.page_link("pages/2_Funil.py", label="Funil")
st.page_link("pages/3_Financeiro.py", label="Financeiro")
st.page_link("pages/4_Operacional.py", label="Operacional")
st.page_link("pages/5_Promocoes.py", label="Promocoes")
st.page_link("pages/6_Clientes.py", label="Clientes")
st.page_link("pages/7_Chamados.py", label="Chamados")

