
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

@st.cache_data(ttl=300)
def load_sheet(name):
    try:
        sh = _client().open_by_key(st.secrets["sheets"]["spreadsheet_id"])
        ws = sh.worksheet(name)
        records = ws.get_all_records()
        if not records:
            return pd.DataFrame()
        df = pd.DataFrame(records)
        # Converter colunas numericas que vieram como string
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
        return df
    except Exception as e:
        return _sample(name)

def load_all():
    return {s: load_sheet(s) for s in ["lojas", "semanal", "campanhas", "chamados"]}

def get_stores(d):
    df = d.get("lojas", pd.DataFrame())
    if df.empty or "loja_nome" not in df.columns:
        return []
    return sorted(df["loja_nome"].unique().tolist())

def get_merchant_id(data, loja_nome):
    df = data.get("lojas", pd.DataFrame())
    if df.empty or "loja_nome" not in df.columns:
        return None
    row = df[df["loja_nome"] == loja_nome]
    if row.empty:
        return None
    return row.iloc[0].get("merchant_id")

def fp(df, s, e, col="data_inicio"):
    """Filtra por periodo — robusto para datas em varios formatos."""
    if df.empty or col not in df.columns:
        return df
    df = df.copy()
    col_raw = df[col]
    # Tentar converter de multiplos formatos
    parsed = pd.to_datetime(col_raw, errors="coerce", dayfirst=False)
    # Se muitos NaT, tentar com dayfirst
    if parsed.isna().mean() > 0.5:
        parsed = pd.to_datetime(col_raw, errors="coerce", dayfirst=True)
    # Se ainda muitos NaT, tentar interpretar como serial Excel
    if parsed.isna().mean() > 0.5:
        try:
            numeric = pd.to_numeric(col_raw, errors="coerce")
            parsed = pd.to_datetime(numeric, unit="D", origin="1899-12-30", errors="coerce")
        except Exception:
            pass
    df[col] = parsed
    ts_s = pd.Timestamp(s)
    ts_e = pd.Timestamp(e)
    mask = (df[col] >= ts_s) & (df[col] <= ts_e)
    result = df[mask]
    # Se vazio, tenta sem filtro de data (retorna tudo da loja)
    if result.empty:
        return df
    return result

def delta(c, p):
    if not p or pd.isna(p) or p == 0:
        return None
    return (c - p) / abs(p)

def prev(s, e):
    d = e - s
    pe = s - timedelta(days=1)
    return pe - d, pe

def agg(df, loja, s, e):
    """Agrega metricas do periodo para uma loja."""
    if df.empty:
        return {}
    # Filtrar por loja_nome
    if "loja_nome" in df.columns:
        sub = df[df["loja_nome"] == loja]
    else:
        sub = df
    if sub.empty:
        return {}
    # Filtrar por periodo
    p = fp(sub, s, e)
    if p.empty:
        p = sub  # fallback: usa todos os dados da loja
    # Converter colunas para numerico
    num = ["visitas", "visualizacoes", "sacola", "revisao", "pedidos",
           "fat_bruto", "taxas", "promocoes_loja", "anuncios", "mensalidade",
           "fat_liquido", "clientes_novos", "repasse", "cancelamentos"]
    avg = ["disponibilidade_pct", "mtp_minutos", "delta_ct_minutos",
           "review_score", "nre_minutos"]
    r = {}
    for c in num:
        if c in p.columns:
            vals = pd.to_numeric(p[c], errors="coerce")
            r[c] = vals.sum() if not vals.isna().all() else 0
    for c in avg:
        if c in p.columns:
            vals = pd.to_numeric(p[c], errors="coerce")
            r[c] = vals.mean() if not vals.isna().all() else 0
    if r.get("pedidos", 0) > 0 and r.get("fat_bruto", 0) > 0:
        r["ticket_medio"] = r["fat_bruto"] / r["pedidos"]
    return r

def _sample(name):
    random.seed(42)
    if name == "lojas":
        return pd.DataFrame([
            {"merchant_id": "561946ff-3da8-4794-a677-5819d083eef3", "loja_id": "L01",
             "loja_nome": "Restaurante Garden Brasa Realengo", "canal": "iFood", "grupo": "Garden Brasa"},
            {"merchant_id": "baef5289-9eba-46ec-90ec-673dc8d29e8b", "loja_id": "L02",
             "loja_nome": "Pizzaria Garden Brasa Realengo", "canal": "iFood", "grupo": "Garden Brasa"},
            {"merchant_id": "aca37e14-4089-48f4-b016-a329e6abfbea", "loja_id": "L03",
             "loja_nome": "Verano Grill Restaurante e Pizzaria", "canal": "iFood", "grupo": "Garden Brasa"},
        ])
    if name == "semanal":
        rows = []
        lojas = [
            ("561946ff", "L01", "Restaurante Garden Brasa Realengo", 300),
            ("baef5289", "L02", "Pizzaria Garden Brasa Realengo", 50),
            ("aca37e14", "L03", "Verano Grill Restaurante e Pizzaria", 80),
        ]
        for m in [6, 7, 8, 9]:
            for mid, lid, nome, base in lojas:
                fb = round(random.uniform(base * 160, base * 220), 2)
                rows.append({
                    "data_inicio": date(2026, m, 1).strftime("%Y-%m-%d"),
                    "data_fim": date(2026, m, 28).strftime("%Y-%m-%d"),
                    "merchant_id": mid, "loja_id": lid, "loja_nome": nome,
                    "visitas": random.randint(1500, 6000),
                    "visualizacoes": random.randint(1000, 4500),
                    "sacola": random.randint(400, 2000),
                    "revisao": random.randint(350, 1900),
                    "pedidos": base + random.randint(-30, 30),
                    "fat_bruto": fb,
                    "taxas": round(fb * random.uniform(0.13, 0.38), 2),
                    "promocoes_loja": round(fb * random.uniform(0.12, 0.20), 2),
                    "anuncios": round(random.uniform(0, 1500), 2),
                    "mensalidade": 110.0,
                    "fat_liquido": round(fb * random.uniform(0.28, 0.55), 2),
                    "clientes_novos": random.randint(20, 150),
                    "repasse": round(fb * random.uniform(0.25, 0.45), 2),
                    "cancelamentos": random.randint(2, 25),
                    "disponibilidade_pct": round(random.uniform(0.82, 0.99), 4),
                    "mtp_minutos": random.randint(20, 45),
                    "delta_ct_minutos": round(random.uniform(-5, 15), 1),
                    "review_score": round(random.uniform(3.8, 5.0), 1),
                    "nre_minutos": round(random.uniform(3, 18), 1),
                })
        return pd.DataFrame(rows)
    if name == "campanhas":
        rows = []
        for m in [6, 7, 8, 9]:
            for lid, nome in [("L01","Restaurante Garden Brasa Realengo"),
                              ("L02","Pizzaria Garden Brasa Realengo"),
                              ("L03","Verano Grill Restaurante e Pizzaria")]:
                for camp, tipo in [("Entrega Gratis HITS","Entrega gratis"),
                                   ("Hits R8 OFF","Hits"),("CI 30pct off","Desconto")]:
                    ped = random.randint(3, 150)
                    rows.append({"data_inicio": date(2026,m,1).strftime("%Y-%m-%d"),
                        "loja_id":lid,"loja_nome":nome,"campanha":camp,"tipo":tipo,
                        "pedidos":ped,"subsidio_loja":round(ped*random.uniform(3,12),2)})
        return pd.DataFrame(rows)
    if name == "chamados":
        rows = []
        for lid, nome in [("L01","Restaurante Garden Brasa Realengo"),
                          ("L02","Pizzaria Garden Brasa Realengo"),
                          ("L03","Verano Grill Restaurante e Pizzaria")]:
            for m in ["Pedido errado","Atraso","Item faltando","Qualidade","Cancelamento"]:
                rows.append({"loja_id":lid,"loja_nome":nome,"motivo":m,
                    "quantidade":random.randint(1,15),
                    "status":random.choice(["Aberto","Em andamento","Fechado"]),"data":"2026-09-20"})
        return pd.DataFrame(rows)
    return pd.DataFrame()
