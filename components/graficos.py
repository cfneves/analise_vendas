# components/graficos.py
"""Construtores de figura Plotly — sem nenhuma chamada st.* (puro)."""
import pandas as pd
import plotly.graph_objects as go

COR_PRIMARIA = "#0072B2"
PALETA = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442"]
FONTE = dict(family="Inter, -apple-system, sans-serif", size=13)


def template_para_tema(tema: str) -> str:
    return "plotly_dark" if tema == "dark" else "plotly_white"


def _layout_base(tema: str) -> dict:
    return dict(
        template=template_para_tema(tema),
        font=FONTE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
    )


def _reais_curto(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"R$ {v/1_000_000:,.1f}M".replace(",", ".")
    if abs(v) >= 1_000:
        return f"R$ {v/1_000:,.0f}k".replace(",", ".")
    return f"R$ {v:,.0f}".replace(",", ".")


def grafico_evolucao_mensal(mensal: pd.Series, tema: str = "light") -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=mensal.index, y=mensal.values, mode="lines+markers",
        line=dict(color=COR_PRIMARIA, width=2.5), marker=dict(size=7),
        hovertemplate="%{x|%b %Y}<br>R$ %{y:,.2f}<extra></extra>",
    ))
    fig.update_layout(**_layout_base(tema), yaxis_title="Receita (R$)")
    return fig


def grafico_barra_horizontal(dados: pd.DataFrame, tema: str = "light", coluna: str = "receita") -> go.Figure:
    ordenado = dados.sort_values(coluna)
    fig = go.Figure(go.Bar(
        x=ordenado[coluna], y=ordenado.index.astype(str), orientation="h",
        marker_color=COR_PRIMARIA,
        text=[_reais_curto(v) for v in ordenado[coluna]],
        textposition="outside",
        hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
    ))
    fig.update_layout(**_layout_base(tema), xaxis_title="Receita (R$)")
    fig.update_xaxes(range=[0, ordenado[coluna].max() * 1.18])
    return fig


def grafico_ticket_medio(ticket: pd.Series, tema: str = "light") -> go.Figure:
    ordenado = ticket.sort_values()
    fig = go.Figure(go.Bar(
        x=ordenado.values, y=ordenado.index.astype(str), orientation="h",
        marker_color=COR_PRIMARIA,
        text=[_reais_curto(v) for v in ordenado.values],
        textposition="outside",
        hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
    ))
    fig.update_layout(**_layout_base(tema), xaxis_title="Receita média por venda (R$)")
    fig.update_xaxes(range=[0, ordenado.max() * 1.18])
    return fig


def grafico_donut_categoria(dados: pd.DataFrame, tema: str = "light", coluna: str = "receita") -> go.Figure:
    """Distribuição percentual — só serve pra poucas categorias (aqui: 3)."""
    ordenado = dados.sort_values(coluna, ascending=False)
    fig = go.Figure(go.Pie(
        labels=ordenado.index.astype(str), values=ordenado[coluna],
        hole=0.6, marker=dict(colors=PALETA),
        textinfo="label+percent", hovertemplate="%{label}<br>R$ %{value:,.2f}<extra></extra>",
    ))
    fig.update_layout(**_layout_base(tema), showlegend=False)
    return fig
