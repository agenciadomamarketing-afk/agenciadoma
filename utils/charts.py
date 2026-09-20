
import plotly.graph_objects as go, pandas as pd
R="#E91D2B";G="#1DB954";E="#C0392B";C="#444";W="#FFFFFF";BG="#1A1A1A";Y="#F5A623";BD="#2D2D2D"

def kpi(label,value,d=None,alert=False):
    color=R if not alert else E
    if d is not None:
        dc,di=(G,"▲") if d>0 else ((E,"▼") if d<0 else (C,"●"))
        dh=f'<span style="color:{dc};font-size:12px">{di} {abs(d):.1%} vs mês ant.</span>'
    else: dh=""
    return f'''<div style="background:#1A1A1A;border:1px solid #2D2D2D;border-radius:12px;
        padding:18px 20px;border-top:3px solid {color};height:100%">
        <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">{label}</div>
        <div style="color:#FFFFFF;font-size:23px;font-weight:700;margin-bottom:4px">{value}</div>{dh}</div>'''

def funnel(labels,values,title="Funil"):
    reds=[R,"#C01020","#900C1A","#600810","#300408"]
    fig=go.Figure(go.Funnel(y=labels,x=values,textinfo="value+percent initial",
        marker=dict(color=reds[:len(labels)]),connector=dict(line=dict(color="#333",width=1))))
    fig.update_layout(title=title,paper_bgcolor=BG,plot_bgcolor=BG,font=dict(color=W,size=13),margin=dict(l=20,r=20,t=50,b=20),height=380)
    return fig

def trend(df,x,ys,ns,title=""):
    cls=[R,G,"#3498DB","#9B59B6"]; fig=go.Figure()
    for i,(col,name) in enumerate(zip(ys,ns)):
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df[x],y=df[col],mode="lines+markers",name=name,
                line=dict(color=cls[i%4],width=2.5),marker=dict(size=7)))
    fig.update_layout(title=title,paper_bgcolor=BG,plot_bgcolor=BG,font=dict(color=W,size=12),
        xaxis=dict(gridcolor="#2D2D2D"),yaxis=dict(gridcolor="#2D2D2D"),
        legend=dict(bgcolor=BG,bordercolor=BD),margin=dict(l=20,r=20,t=40,b=20),height=360)
    return fig

def waterfall(labels,values):
    measure=["absolute"]+["relative"]*(len(labels)-2)+["total"]
    fig=go.Figure(go.Waterfall(orientation="v",measure=measure,x=labels,y=values,
        text=[f"R${abs(v):,.0f}" for v in values],textposition="outside",
        connector={"line":{"color":"#444"}},
        increasing={"marker":{"color":G}},decreasing={"marker":{"color":E}},totals={"marker":{"color":R}}))
    fig.update_layout(paper_bgcolor=BG,plot_bgcolor=BG,font=dict(color=W),
        height=400,margin=dict(l=20,r=20,t=20,b=20),xaxis=dict(gridcolor="#2D2D2D"))
    return fig

def gauge(value,title,thresholds=(60,80)):
    low,high=thresholds; color=E if value<low else (Y if value<high else G)
    fig=go.Figure(go.Indicator(mode="gauge+number",value=value,
        title={"text":title,"font":{"color":W,"size":14}},
        number={"suffix":"%","font":{"color":W,"size":28}},
        gauge={"axis":{"range":[0,100],"tickcolor":W},"bar":{"color":color},"bgcolor":"#2D2D2D",
               "steps":[{"range":[0,low],"color":"#3D1A1A"},{"range":[low,high],"color":"#3D3010"},{"range":[high,100],"color":"#1A3D2A"}]}))
    fig.update_layout(paper_bgcolor=BG,font=dict(color=W),margin=dict(l=20,r=20,t=60,b=20),height=260)
    return fig
