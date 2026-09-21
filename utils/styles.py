from html import escape

RED = "#E91D2B"
DARK = "#0F0F0F"
CARD = "#1A1A1A"
BORD = "#2D2D2D"
GRN = "#1DB954"
ERR = "#C0392B"
YLW = "#F5A623"
WHT = "#FFFFFF"

GLOBAL_CSS = """<style>
:root { --doma-red:#E91D2B; --doma-muted:#B5B5BD; }
.stApp { background:#0F0F0F; color:#FFFFFF; font-family:'Segoe UI',Arial,sans-serif; }
.block-container { padding-top:2.8rem; padding-bottom:3rem; max-width:1560px; }
.page-title { font-family:'Segoe UI Display','Segoe UI',sans-serif; font-size:clamp(28px,3vw,40px); font-weight:750; letter-spacing:-1.2px; line-height:1.2; padding-left:16px; border-left:4px solid #E91D2B; margin:0 0 10px; }
h1,h2,h3 { letter-spacing:-.6px; }
h3 { font-size:24px !important; }
[data-testid="stCaptionContainer"] { color:#B5B5BD; }
hr { border-color:#2D2D2D !important; margin:1.4rem 0 !important; }
[data-testid="stSidebar"] { background:#141414; border-right:1px solid #2D2D2D; }
[data-testid="stSidebarNav"] { display:none; }
[data-testid="stSidebarUserContent"] { padding-top:1rem; }
[data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] { gap:.65rem; }
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] { padding:7px 12px; margin:0; border-radius:9px; border:1px solid transparent; transition:background .16s,border-color .16s; }
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover { background:#35171C; border-color:#783039; }
[data-testid="stSidebar"] [aria-current="page"] { background:#45191F; border-left:3px solid #E91D2B; color:white; }
.doma-nav-label { color:#B5B5BD; font-size:11px; font-weight:700; letter-spacing:1.8px; margin:4px 0 10px; }
.doma-kpi { box-sizing:border-box; min-height:156px; padding:19px 20px; border:1px solid transparent; border-radius:16px; background:linear-gradient(135deg,#202022,#19191B) padding-box,linear-gradient(135deg,#E91D2B,#60303A 32%,#333336 70%) border-box; box-shadow:0 8px 24px #00000030; }
.doma-kpi.is-alert { background:linear-gradient(135deg,#251B1D,#19191B) padding-box,linear-gradient(135deg,#C0392B,#60303A 32%,#333336 70%) border-box; }
.doma-kpi-head { display:flex; gap:9px; align-items:center; min-height:34px; }
.doma-kpi-icon { flex-shrink:0; display:grid; place-items:center; width:30px; height:30px; border:1px solid #68303A; border-radius:9px; color:#FF9DA6; background:#3B1B22; font-size:16px; }
.doma-kpi-label { color:#C2C2CA; font-size:12px; line-height:1.4; font-weight:600; }
.doma-kpi-value { font-family:'Segoe UI',Arial,sans-serif; font-size:clamp(21px,1.8vw,30px); font-weight:750; letter-spacing:-.7px; line-height:1.3; margin:13px 0 9px; font-variant-numeric:tabular-nums; overflow-wrap:anywhere; }
.doma-kpi-delta { font-size:12px; line-height:1.5; }
.doma-kpi-delta small { color:#B5B5BD; font-size:11px; }
.doma-alert { display:flex; align-items:flex-start; gap:12px; padding:15px 18px; border:1px solid #384957; border-left:3px solid #92BDD5; background:#182127; border-radius:12px; color:#E6EFF4; margin:8px 0; line-height:1.5; font-size:14px; }
.doma-alert-error { background:#29191B; border-color:#713237; border-left-color:#EF8076; }
.doma-alert-warning { background:#292319; border-color:#6A5330; border-left-color:#F5C778; }
.doma-alert-success { background:#17271E; border-color:#315D43; border-left-color:#66D795; }
.doma-alert-icon { font-weight:800; flex-shrink:0; }
.doma-table-wrap { overflow:auto; max-height:520px; border:1px solid #3C3033; border-radius:12px; margin:10px 0; }
.doma-table { width:100%; border-collapse:collapse; font-size:13px; font-variant-numeric:tabular-nums; }
.doma-table thead th { position:sticky; top:0; background:#B31623; color:#FFFFFF; font-weight:650; text-align:left; padding:13px 16px; white-space:nowrap; border:0; }
.doma-table td { padding:12px 16px; border:0; border-bottom:1px solid #303033; color:#E9E9ED; }
.doma-table tbody tr:nth-child(odd) { background:#1A1A1A; }
.doma-table tbody tr:nth-child(even) { background:#232325; }
.doma-table tbody tr:hover { background:#382129; }
.doma-home-card { background:linear-gradient(120deg,#252023,#1A1A1A); border:1px solid #483036; border-radius:16px; padding:24px; min-height:130px; box-shadow:0 8px 24px #00000024; }
.doma-home-card b { font-size:21px; }
.doma-home-card span { color:#B5B5BD !important; }
[data-testid="stPlotlyChart"], .stPlotlyChart { border:1px solid #2D2D2D; border-radius:16px; overflow:hidden; }
.stTabs [data-baseweb="tab-list"] { background:#1A1A1A; padding:5px 10px; border-radius:10px; gap:20px; }
.stTabs [aria-selected="true"] { color:#FF8792; }
.stButton > button { background:#E91D2B; color:white; border:1px solid #E91D2B; border-radius:10px; font-weight:650; min-height:42px; }
.stButton > button:hover { background:#BE1723; color:white; border-color:#FF7784; }
.stTextInput input { color:#FFFFFF; }
a:focus-visible,button:focus-visible,input:focus-visible,[tabindex="0"]:focus-visible { outline:2px solid #FF98A3 !important; outline-offset:3px; }
[data-testid="stVerticalBlockBorderWrapper"]:has(.doma-login-marker):not(:has([data-testid="stVerticalBlockBorderWrapper"] .doma-login-marker)) { max-width:480px; margin:3vh auto 0; padding:24px; border:1px solid #70313A; border-radius:20px; background:radial-gradient(ellipse at top right,#491D2860,transparent 70%),#1A1A1A; box-shadow:0 24px 70px #00000050; }
.stApp:has(.doma-login-marker) [data-testid="stSidebar"], .stApp:has(.doma-login-marker) [data-testid="collapsedControl"] { display:none; }
.doma-login-head { text-align:center; padding:12px 0 20px; }
.doma-login-head img { max-width:100%; height:auto; max-height:48px; }
.doma-login-title { font-size:26px; font-weight:750; letter-spacing:-.6px; margin-top:24px; }
.doma-login-subtitle { color:#B5B5BD; font-size:14px; margin:8px 0; }
@media(max-width:950px) { [data-testid="stHorizontalBlock"]:has(.doma-kpi) { flex-wrap:wrap; gap:1rem !important; } [data-testid="stHorizontalBlock"]:has(.doma-kpi) > [data-testid="column"] { min-width:0; width:calc(50% - 1rem) !important; flex:1 1 calc(50% - 1rem) !important; } }
@media(max-width:480px) { [data-testid="stHorizontalBlock"]:has(.doma-kpi) > [data-testid="column"] { width:100% !important; flex-basis:100% !important; } }
@media(max-width:768px) { .block-container { padding:2rem 1rem; } .doma-kpi { min-height:140px; } .doma-kpi-value { font-size:26px; } .doma-table td,.doma-table th { padding:10px; } }
@media(prefers-reduced-motion:reduce) { *,*::before,*::after { transition:none !important; animation:none !important; } }
</style>"""

def render_alert(message, kind="info"):
    """Render only; callers retain all original conditions and messages."""
    import streamlit as st
    icons = {"info": "i", "success": "âœ“", "warning": "!", "error": "!"}
    kind = kind if kind in icons else "info"
    role = "alert" if kind == "error" else "status"
    st.markdown(f'<div class="doma-alert doma-alert-{kind}" role="{role}">'
                f'<span class="doma-alert-icon" aria-hidden="true">{icons[kind]}</span>'
                f'<span>{escape(str(message))}</span></div>', unsafe_allow_html=True)

def render_table(data, use_container_width=True, hide_index=True):
    """Styled read-only view plus the original interactive dataframe."""
    import streamlit as st
    # Escape sheet content before allowing HTML. Keep all rows in interactive view.
    html = data.head(200).to_html(index=not hide_index, escape=True,
                                border=0, classes="doma-table")
    st.markdown('<div class="doma-table-wrap" tabindex="0" aria-label="Tabela de dados">'
                + html + '</div>', unsafe_allow_html=True)
    if len(data) > 200:
        st.caption("PrÃ©via: primeiras 200 linhas. Consulte todos os dados abaixo.")
    with st.expander("Ordenar, pesquisar e consultar dados"):
        st.dataframe(data, use_container_width=use_container_width, hide_index=hide_index)

def render_navigation(active="app"):
    """Native links supported in Streamlit 1.35; no routing/state changes."""
    import streamlit as st
    if active in ("app", "Visao_Geral", "Funil", "Financeiro", "Operacional", "Promocoes", "Clientes", "Chamados"):
        st.markdown('<style>[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][href="'
                    + active + '"] {background:#45191F;border-left:3px solid #E91D2B;color:white;}</style>',
                    unsafe_allow_html=True)
    st.markdown('<div class="doma-nav-label">GESTÃƒO DE DELIVERY</div>', unsafe_allow_html=True)
    for path, label in [
        ("app.py", "InÃ­cio"), ("pages/1_Visao_Geral.py", "VisÃ£o Geral"),
        ("pages/2_Funil.py", "Funil"), ("pages/3_Financeiro.py", "Financeiro"),
        ("pages/4_Operacional.py", "Operacional"), ("pages/5_Promocoes.py", "PromoÃ§Ãµes"),
        ("pages/6_Clientes.py", "Clientes"), ("pages/7_Chamados.py", "Chamados")
    ]:
        st.page_link(path, label=label)
