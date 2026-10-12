# components/graficos.py
"""Construtores de figura Plotly — sem nenhuma chamada st.* (puro)."""
import pandas as pd
import plotly.graph_objects as go

COR_PRIMARIA = "#0072B2"


def template_para_tema(tema: str) -> str:
    return "plotly_dark" if tema == "dark" else "plotly_white"


def grafico_evolucao_mensal(mensal: pd.Series, tema: str = "light") -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=mensal.index, y=mensal.values, mode="lines+markers",
        line=dict(color=COR_PRIMARIA, width=2), marker=dict(size=7),
        hovertemplate="%{x|%b %Y}<br>R$ %{y:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        template=template_para_tema(tema),
        title="Faturamento mensal",
        yaxis_title="Receita (R$)",
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def grafico_barra_horizontal(dados: pd.DataFrame, titulo: str, tema: str = "light", coluna: str = "receita") -> go.Figure:
    ordenado = dados.sort_values(coluna)
    fig = go.Figure(go.Bar(
        x=ordenado[coluna], y=ordenado.index.astype(str), orientation="h",
        marker_color=COR_PRIMARIA,
        hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        template=template_para_tema(tema),
        title=titulo,
        xaxis_title="Receita (R$)",
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def grafico_ticket_medio(ticket: pd.Series, tema: str = "light") -> go.Figure:
    ordenado = ticket.sort_values()
    fig = go.Figure(go.Bar(
        x=ordenado.values, y=ordenado.index.astype(str), orientation="h",
        marker_color=COR_PRIMARIA,
        hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        template=template_para_tema(tema),
        title="Ticket médio por produto",
        xaxis_title="Receita média por venda (R$)",
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig
