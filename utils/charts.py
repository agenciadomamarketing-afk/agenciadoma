from html import escape
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

R = "#E91D2B"
G = "#1DB954"
E = "#C0392B"
C = "#444444"
W = "#FFFFFF"
BG = "#1A1A1A"
Y = "#F5A623"
BD = "#2D2D2D"

def kpi(label, value, d=None, alert=False):
    dc, di = ("#66D795", "▲") if d is not None and d > 0 else (("#EF9187", "▼") if d is not None and d < 0 else ("#B5B5BD", "●"))
    dh = (f'<span class="doma-kpi-delta" style="color:{dc}">{di} {abs(d):.1%} '
          '<small>vs mês ant.</small></span>') if d is not None else ''
    text = str(label).lower()
    icon = '↗' if any(w in text for w in ('fat', 'repasse', 'ticket')) else ('◷' if any(w in text for w in ('tempo', 'min', 'nre', 'ct')) else ('♙' if 'client' in text else '▤'))
    return (f'<div class="doma-kpi{" is-alert" if alert else ""}">'
            f'<div class="doma-kpi-head"><span class="doma-kpi-icon" aria-hidden="true">{icon}</span>'
            f'<span class="doma-kpi-label">{escape(str(label))}</span></div>'
            f'<div class="doma-kpi-value">{escape(str(value))}</div>{dh}</div>')


def funnel(labels, values, title="Funil"):
    reds = ["#E91D2B", "#CD3849", "#AD4456", "#91475B", "#764B60"]
    fig = go.Figure(go.Funnel(
        y=labels, x=values, textinfo="value+percent initial",
        marker=dict(color=reds[:len(labels)]),
        connector=dict(line=dict(color="#333", width=1))
    ))
    fig.update_layout(title=title, paper_bgcolor=BG, plot_bgcolor=BG,
                      font=dict(color=W, size=13),
                      margin=dict(l=20, r=20, t=50, b=20), height=380)
    return style_figure(fig)

def trend(df, x, ys, ns, title=""):
    cls = [R, "#F5ADB5", "#BBC5D6", "#D8B78B"]
    fig = go.Figure()
    for i, (col, name) in enumerate(zip(ys, ns)):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df[x], y=df[col], mode="lines+markers", name=name,
                line=dict(color=cls[i % 4], width=3, dash=["solid", "dash", "dot", "dashdot"][i % 4]), marker=dict(size=6)
            ))
    fig.update_layout(
        title=title, paper_bgcolor=BG, plot_bgcolor=BG, font=dict(color=W, size=12),
        xaxis=dict(gridcolor="#2D2D2D"), yaxis=dict(gridcolor="#2D2D2D"),
        legend=dict(bgcolor=BG, bordercolor=BD),
        margin=dict(l=20, r=20, t=40, b=20), height=360
    )
    return style_figure(fig)

def waterfall(labels, values):
    measure = ["absolute"] + ["relative"] * (len(labels) - 2) + ["total"]
    fig = go.Figure(go.Waterfall(
        orientation="v", measure=measure, x=labels, y=values,
        text=["R$ " + f"{abs(v):,.0f}".replace(",", ".") for v in values], textposition="outside", textfont=dict(size=13, color=W), cliponaxis=False,
        connector={"line": {"color": "#444"}},
        increasing={"marker": {"color": "#66D795"}},
        decreasing={"marker": {"color": "#EE887E"}},
        totals={"marker": {"color": R}}
    ))
    fig.update_layout(paper_bgcolor=BG, plot_bgcolor=BG, font=dict(color=W),
                      height=450, margin=dict(l=30, r=30, t=65, b=65),
                      xaxis=dict(gridcolor="#2D2D2D"))
    return style_figure(fig)

def gauge(value, title, thresholds=(60, 80)):
    low, high = thresholds
    color = E if value < low else (Y if value < high else G)
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        title={"text": title, "font": {"color": W, "size": 14}},
        number={"suffix": "%", "font": {"color": W, "size": 36}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#72727D", "tickfont": {"size": 10, "color": "#B5B5BD"}, "tickvals": [0, 50, 100]},
            "bar": {"color": color, "thickness": 0.25}, "bgcolor": "#2D2D2D", "borderwidth": 0,
            "threshold": {"line": {"color": W, "width": 2}, "thickness": 0.8, "value": high},
            "steps": [
                {"range": [0, low], "color": "#3D1A1A"},
                {"range": [low, high], "color": "#3D3010"},
                {"range": [high, 100], "color": "#1A3D2A"}
            ]
        }
    ))
    fig.update_layout(paper_bgcolor=BG, font=dict(color=W),
                      margin=dict(l=20, r=20, t=60, b=20), height=260)
    style_figure(fig)
    fig.update_traces(title_text="")
    fig.update_layout(title=dict(text=title, x=0.5, y=0.92, font=dict(size=14)))
    return fig


def style_figure(fig):
    """Apply presentation only, leaving values and trace types unchanged."""
    fig.update_layout(
        font=dict(family="Segoe UI, Arial, sans-serif", color=W, size=13),
        title_font=dict(size=20, color=W), title_x=0.04,
        paper_bgcolor=BG, plot_bgcolor=BG,
        hoverlabel=dict(bgcolor="#27272B", font_size=13, font_color=W),
        separators=",.",
        colorway=[R, "#F5ADB5", "#BBC5D6", "#D8B78B"],
        legend=dict(orientation="h", yanchor="top", y=-0.2, x=0, font_size=12),
    )
    fig.update_xaxes(gridcolor="#303034", zeroline=False, automargin=True)
    fig.update_yaxes(gridcolor="#303034", zeroline=False, automargin=True)
    if any(trace.type == "scatter" for trace in fig.data):
        fig.update_layout(hovermode="x unified", margin=dict(b=80))
    return fig
