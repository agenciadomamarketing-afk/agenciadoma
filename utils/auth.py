import streamlit as st
import base64, pathlib
RED="#E91D2B"; DARK="#0F0F0F"; CARD="#1A1A1A"; BORD="#2D2D2D"

def _logo():
    p = pathlib.Path("assets/logo_doma_white.png")
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""

def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True
    b64 = _logo()
    img = '<img src="data:image/png;base64,' + b64 + '" style="height:50px;margin-bottom:16px">' if b64 else '<div style="font-size:28px;color:' + RED + ';font-weight:700">DOMA food</div>'
    st.markdown(
        '<div style="display:flex;justify-content:center;min-height:70vh;align-items:center">' +
        '<div style="background:' + CARD + ';border:1px solid ' + BORD + ';border-radius:20px;padding:48px 40px;max-width:400px;width:100%;text-align:center;border-top:4px solid ' + RED + '">' +
        img + '<div style="color:#B5B5BD;font-size:13px;margin-top:8px;margin-bottom:28px">Dashboard iFood - Acesso restrito</div></div></div>',
        unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        pwd = st.text_input("Senha", type="password", placeholder="Digite a senha", label_visibility="collapsed")
        if st.button("Entrar", use_container_width=True, type="primary"):
            if pwd == st.secrets.get("APP_PASSWORD", "doma2024"):
                st.session_state.authenticated = True; st.rerun()
            else:
                st.error("Senha incorreta.")
    return False

def logout():
    st.session_state.authenticated = False; st.rerun()
