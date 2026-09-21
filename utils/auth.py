import streamlit as st
import base64
import pathlib
from utils.styles import render_alert

RED  = "#E91D2B"
DARK = "#0F0F0F"
CARD = "#1A1A1A"
BORD = "#2D2D2D"

def _logo():
    p = pathlib.Path("assets/logo_doma_white.png")
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""

def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True

    b64 = _logo()
    if b64:
        img_html = '<img src="data:image/png;base64,' + b64 + '" style="height:50px;margin-bottom:16px">'
    else:
        img_html = '<div style="font-size:28px;color:' + RED + ';font-weight:700">DOMA food</div>'

    with st.container(border=True):
        st.markdown('<div class="doma-login-marker"></div><div class="doma-login-head">'
                    + img_html + '<div class="doma-login-title">Gestão de delivery</div>'
                    '<div class="doma-login-subtitle">Dashboard iFood · Acesso restrito</div></div>',
                    unsafe_allow_html=True)
        pwd = st.text_input("Senha", type="password",
                            placeholder="Digite a senha", label_visibility="collapsed")
        if st.button("Entrar", use_container_width=True, type="primary"):
            if pwd == st.secrets.get("APP_PASSWORD", "doma2024"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                render_alert("Senha incorreta.", "error")
    return False

def logout():
    st.session_state.authenticated = False
    st.rerun()
