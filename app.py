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

RED  = "#E91D2B"
CARD = "#1A1A1A"
BORD = "#2D2D2D"
GRN  = "#1DB954"
YLW  = "#F5A623"

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
    if st.button("Sair", use_container_width=True):
        logout()

st.markdown('<div class="page-title">Inicio</div>', unsafe_allow_html=True)
st.markdown("**Loja:** " + str(loja or "—") + "  ·  **Periodo:** " + str(sd) + " → " + str(ed))
st.markdown("---")

n = len(stores) if stores else 0
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        '<div style="background:' + CARD + ';border-radius:12px;padding:20px;border-top:3px solid ' + RED + '">' +
        '<b>Visao Geral</b><br>' +
        '<span style="color:#888;font-size:13px">KPIs + comparacao mes anterior</span></div>',
        unsafe_allow_html=True
    )
with c2:
    st.markdown(
        '<div style="background:' + CARD + ';border-radius:12px;padding:20px;border-top:3px solid ' + GRN + '">' +
        '<b>' + str(n) + ' lojas ativas</b><br>' +
        '<span style="color:#888;font-size:13px">Selecione no menu lateral</span></div>',
        unsafe_allow_html=True
    )
with c3:
    st.markdown(
        '<div style="background:' + CARD + ';border-radius:12px;padding:20px;border-top:3px solid ' + YLW + '">' +
        '<b>Google Sheets</b><br>' +
        '<span style="color:#888;font-size:13px">Atualizado toda segunda-feira</span></div>',
        unsafe_allow_html=True
    )
