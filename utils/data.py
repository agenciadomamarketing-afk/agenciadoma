
import streamlit as st
import pandas as pd
import gspread
import random
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta, date

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(ttl=300)
def _client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def load_sheet(name):
    try:
        sh = _client().open_by_key(st.secrets["sheets"]["spreadsheet_id"])
        ws = sh.worksheet(name)
        values = ws.get_all_values()
        if len(values) < 2:
            return pd.DataFrame()
        headers = [h.strip() for h in values[0]]
        data = values[1:]
        df = pd.DataFrame(data, columns=headers)
        # Limpar espacos em strings
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].str.strip()
        # Converter numericos
        for col in df.columns:
            if col not in ["data_inicio", "data_fim", "merchant_id", "loja_id",
                           "loja_nome", "canal", "grupo", "delta_ct_class",
                           "obs", "data_repasse", "data"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except Exception:
        return _sample(name)

def load_all():
    return {s: load_sheet(s) for s in ["lojas", "semanal", "campanhas", "chamados"]}

def get_stores(d):
    df = d.get("lojas", pd.DataFrame())
    if df.empty or "loja_nome" not in df.columns:
        return []
    return sorted(df["loja_nome"].dropna().unique().tolist())

def fp(df, s, e, col="data_inicio"):
    if df.empty or col not in df.columns:
        return df
    df = df.copy()
    parsed = pd.to_datetime(df[col], errors="coerce", dayfirst=False)
    if parsed.isna().mean() > 0.5:
        parsed = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
    df[col] = parsed
    ts_s = pd.Timestamp(s)
    ts_e = pd.Timestamp(e)
    result = df[(df[col] >= ts_s) & (df[col] <= ts_e)]
    return result if not result.empty else df

def delta(c, p):
    if not p or pd.isna(p) or p == 0:
        return None
    return (c - p) / abs(p)

def prev(s, e):
    d = e - s
    pe = s - timedelta(days=1)
    return pe - d, pe

def agg(df, loja, s, e):
    if df.empty:
        return {}
    if "loja_nome" in df.columns:
        # Busca tolerante: ignora maiusculas e espacos extras
        loja_norm = loja.strip().lower()
        mask = df["loja_nome"].str.strip().str.lower() == loja_norm
        sub = df[mask]
        # Fallback: busca parcial se nome exato nao encontrar
        if sub.empty:
            mask2 = df["loja_nome"].str.strip().str.lower().str.contains(
                loja_norm[:20], regex=False, na=False)
            sub = df[mask2]
    else:
        sub = df
    if sub.empty:
        return {}
    p = fp(sub, s, e)
    if p.empty:
        p = sub
    num = ["visitas", "visualizacoes", "sacola", "revisao", "pedidos",
           "fat_bruto", "taxas", "promocoes_loja", "anuncios", "mensalidade",
           "fat_liquido", "clientes_novos", "repasse", "cancelamentos"]
    avg_cols = ["disponibilidade_pct", "mtp_minutos", "delta_ct_minutos",
                "review_score", "nre_minutos"]
    r = {}
    for c in num:
        if c in p.columns:
            vals = pd.to_numeric(p[c], errors="coerce")
            r[c] = float(vals.sum()) if not vals.isna().all() else 0.0
    for c in avg_cols:
        if c in p.columns:
            vals = pd.to_numeric(p[c], errors="coerce")
            r[c] = float(vals.mean()) if not vals.isna().all() else 0.0
    if r.get("pedidos", 0) > 0 and r.get("fat_bruto", 0) > 0:
        r["ticket_medio"] = r["fat_bruto"] / r["pedidos"]
    return r

def _sample(name):
    random.seed(42)
    if name == "lojas":
        return pd.DataFrame([
            {"merchant_id":"561946ff","loja_id":"L01","loja_nome":"Restaurante Garden Brasa Realengo","canal":"iFood","grupo":"Garden Brasa"},
            {"merchant_id":"baef5289","loja_id":"L02","loja_nome":"Pizzaria Garden Brasa Realengo","canal":"iFood","grupo":"Garden Brasa"},
            {"merchant_id":"aca37e14","loja_id":"L03","loja_nome":"Verano Grill Restaurante e Pizzaria","canal":"iFood","grupo":"Garden Brasa"},
        ])
    if name == "semanal":
        rows = []
        lojas = [("561946ff","L01","Restaurante Garden Brasa Realengo",300),
                 ("baef5289","L02","Pizzaria Garden Brasa Realengo",50),
                 ("aca37e14","L03","Verano Grill Restaurante e Pizzaria",80)]
        for m in [6,7,8,9]:
            for mid,lid,nome,base in lojas:
                fb = round(random.uniform(base*160,base*220),2)
                rows.append({"data_inicio":date(2026,m,1).strftime("%Y-%m-%d"),
                    "data_fim":date(2026,m,28).strftime("%Y-%m-%d"),
                    "merchant_id":mid,"loja_id":lid,"loja_nome":nome,
                    "visitas":random.randint(1500,6000),"visualizacoes":random.randint(1000,4500),
                    "sacola":random.randint(400,2000),"revisao":random.randint(350,1900),
                    "pedidos":base+random.randint(-30,30),"fat_bruto":fb,
                    "taxas":round(fb*random.uniform(0.13,0.38),2),
                    "promocoes_loja":round(fb*random.uniform(0.12,0.20),2),
                    "anuncios":round(random.uniform(0,1500),2),"mensalidade":110.0,
                    "fat_liquido":round(fb*random.uniform(0.28,0.55),2),
                    "clientes_novos":random.randint(20,150),
                    "repasse":round(fb*random.uniform(0.25,0.45),2),
                    "cancelamentos":random.randint(2,25),
                    "disponibilidade_pct":round(random.uniform(0.82,0.99),4),
                    "mtp_minutos":random.randint(20,45),
                    "delta_ct_minutos":round(random.uniform(-5,15),1),
                    "review_score":round(random.uniform(3.8,5.0),1),
                    "nre_minutos":round(random.uniform(3,18),1)})
        return pd.DataFrame(rows)
    if name == "campanhas":
        rows = []
        for m in [6,7,8,9]:
            for lid,nome in [("L01","Restaurante Garden Brasa Realengo"),
                             ("L02","Pizzaria Garden Brasa Realengo"),
                             ("L03","Verano Grill Restaurante e Pizzaria")]:
                for camp,tipo in [("Entrega Gratis HITS","Entrega gratis"),
                                  ("Hits R8 OFF","Hits"),("CI 30pct off","Desconto")]:
                    ped=random.randint(3,150)
                    rows.append({"data_inicio":date(2026,m,1).strftime("%Y-%m-%d"),
                        "loja_id":lid,"loja_nome":nome,"campanha":camp,"tipo":tipo,
                        "pedidos":ped,"subsidio_loja":round(ped*random.uniform(3,12),2)})
        return pd.DataFrame(rows)
    if name == "chamados":
        rows = []
        for lid,nome in [("L01","Restaurante Garden Brasa Realengo"),
                         ("L02","Pizzaria Garden Brasa Realengo"),
                         ("L03","Verano Grill Restaurante e Pizzaria")]:
            for m in ["Pedido errado","Atraso","Item faltando","Qualidade","Cancelamento"]:
                rows.append({"loja_id":lid,"loja_nome":nome,"motivo":m,
                    "quantidade":random.randint(1,15),
                    "status":random.choice(["Aberto","Em andamento","Fechado"]),"data":"2026-09-20"})
        return pd.DataFrame(rows)
    return pd.DataFrame()
