# components/kpis.py
import streamlit as st


def reais(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def renderizar(m: dict) -> None:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Faturamento", reais(m["receita"]))
    col2.metric("Custo", reais(m["custo"]))
    col3.metric("Margem", reais(m["margem"]))
    col4.metric("Margem %", f"{m['margem_pct']:.1%}")
    col5.metric("Ticket médio", reais(m["ticket_medio"]))
