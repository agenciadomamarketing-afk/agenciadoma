import streamlit as st
import pandas as pd
import pathlib
import base64
from datetime import date, datetime
from utils.auth import check_login, logout
from utils.data import load_all, get_stores, agg, prev, delta
from utils.charts import kpi, funnel
from utils.styles import GLOBAL_CSS, render_alert, render_table, render_navigation

st.set_page_config(page_title="Funil · Doma", page_icon="assets/logo_doma_white.png", layout="wide")
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
    render_navigation("Funil")
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

st.markdown('<div class="page-title">Funil de Conversao</div>', unsafe_allow_html=True)
st.caption(str(loja) + "  ·  " + str(sd) + " → " + str(ed))
st.markdown("---")

etapas = ["Visitas", "Visualizacoes", "Sacola", "Revisao", "Pedidos"]
keys   = ["visitas", "visualizacoes", "sacola", "revisao", "pedidos"]
vals   = [int(cur.get(k, 0)) for k in keys]
pvals  = [int(pv.get(k, 0)) for k in keys]

c1, c2 = st.columns([3, 2])
with c1:
    if any(v > 0 for v in vals):
        st.plotly_chart(funnel(etapas, vals, "Funil - " + loja), use_container_width=True, theme=None)
    else:
        render_alert("Dados de funil nao disponiveis.", "info")
with c2:
    st.markdown("#### Conversao por Etapa")
    for i in range(len(etapas) - 1):
        vf, vt = vals[i], vals[i+1]
        pvf, pvt = pvals[i], pvals[i+1]
        cc = vt / vf if vf > 0 else 0
        cp = pvt / pvf if pvf > 0 else 0
        label = etapas[i] + " -> " + etapas[i+1]
        st.markdown(kpi(label, "{:.1%}".format(cc), delta(cc, cp)), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### Abandono por Etapa")
rows = []
for i in range(len(etapas) - 1):
    lost = vals[i] - vals[i+1]
    pct  = lost / vals[i] if vals[i] > 0 else 0
    rows.append({
        "Etapa": etapas[i] + " -> " + etapas[i+1],
        "Perdidos": lost,
        "Abandono": "{:.1%}".format(pct),
        "Status": "Alto" if pct > 0.5 else ("Medio" if pct > 0.3 else "Ok")
    })
render_table(pd.DataFrame(rows), use_container_width=True, hide_index=True)
