import streamlit as st
import pandas as pd
import pathlib
import base64
from datetime import date, datetime
from utils.auth import check_login, logout
from utils.data import load_all, get_stores, agg, prev, delta
from utils.charts import kpi, trend
from utils.styles import GLOBAL_CSS

st.set_page_config(page_title="Visao Geral · Doma", page_icon="assets/logo_doma_white.png", layout="wide")
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

s = datetime.combine(sd, datetime.min.time())
e = datetime.combine(ed, datetime.min.time())
ps, pe = prev(s, e)
df = load_all().get("semanal", pd.DataFrame())
cur = agg(df, loja, s, e)
pv  = agg(df, loja, ps, pe)

def brl(v):
    return "R$ {:,.2f}".format(v).replace(",", "X").replace(".", ",").replace("X", ".")
def d(k):
    return delta(cur.get(k, 0), pv.get(k, 0))

st.markdown('<div class="page-title">Visao Geral</div>', unsafe_allow_html=True)
st.caption(str(loja) + "  ·  " + str(sd) + " → " + str(ed))
st.markdown("---")

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(kpi("Faturamento Bruto",  brl(cur.get("fat_bruto",  0)), d("fat_bruto")),  unsafe_allow_html=True)
with c2: st.markdown(kpi("Fat. Liquido",        brl(cur.get("fat_liquido",0)), d("fat_liquido")),unsafe_allow_html=True)
with c3: st.markdown(kpi("Pedidos",             str(int(cur.get("pedidos",0))), d("pedidos")),   unsafe_allow_html=True)
with c4: st.markdown(kpi("Ticket Medio",        brl(cur.get("ticket_medio",0)), d("ticket_medio")), unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
c5, c6, c7, c8 = st.columns(4)
with c5: st.markdown(kpi("Clientes Novos",      str(int(cur.get("clientes_novos",0))), d("clientes_novos")), unsafe_allow_html=True)
with c6: st.markdown(kpi("Cancelamentos",       str(int(cur.get("cancelamentos",0))), d("cancelamentos"), alert=True), unsafe_allow_html=True)
with c7: st.markdown(kpi("Repasse Previsto",    brl(cur.get("repasse",0))), unsafe_allow_html=True)
with c8: st.markdown(kpi("Promocoes (loja)",    brl(cur.get("promocoes_loja",0)), d("promocoes_loja")), unsafe_allow_html=True)

st.markdown("---")
ldf = df[df["loja_nome"] == loja].copy() if "loja_nome" in df.columns else pd.DataFrame()
if not ldf.empty:
    ldf["data_inicio"] = pd.to_datetime(ldf["data_inicio"], errors="coerce")
    ldf = ldf.sort_values("data_inicio")
    for c in ["fat_bruto","fat_liquido","pedidos","clientes_novos"]:
        if c in ldf.columns:
            ldf[c] = pd.to_numeric(ldf[c], errors="coerce")
    t1, t2 = st.tabs(["Financeiro", "Volume"])
    with t1:
        st.plotly_chart(trend(ldf, "data_inicio",
            ["fat_bruto","fat_liquido","repasse"],
            ["Fat. Bruto","Fat. Liquido","Repasse"],
            "Evolucao Financeira"), use_container_width=True)
    with t2:
        st.plotly_chart(trend(ldf, "data_inicio",
            ["pedidos","clientes_novos","cancelamentos"],
            ["Pedidos","Clientes Novos","Cancelamentos"],
            "Volume de Pedidos"), use_container_width=True)

st.markdown("---")
fat_b = cur.get("fat_bruto", 0)
fat_l = cur.get("fat_liquido", 0)
pct   = fat_l / fat_b if fat_b > 0 else 0
if pct >= 0.40:
    st.success("Fat. liquido = {:.1%} do bruto. Margem saudavel.".format(pct))
elif pct >= 0.30:
    st.warning("Fat. liquido = {:.1%} do bruto. Margem apertada.".format(pct))
elif fat_b > 0:
    st.error("Fat. liquido = {:.1%} do bruto. Verificar taxas e promocoes.".format(pct))
