# components/kpis.py
import streamlit as st


def reais(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _delta_pct(v: float | None) -> str | None:
    return None if v is None else f"{v:+.1%}"


def renderizar(m: dict, m_anterior: dict | None = None) -> None:
    """m_anterior=None quando não há período anterior comparável nos dados
    (ex.: o filtro já cobre a base inteira) — nesse caso não mostra variação,
    em vez de inventar uma comparação sem sentido."""
    deltas = {"receita": None, "custo": None, "margem": None, "margem_pct": None, "ticket_medio": None}
    if m_anterior:
        for chave in deltas:
            if chave == "margem_pct":
                deltas[chave] = None if m["margem_pct"] is None else m["margem_pct"] - m_anterior["margem_pct"]
            else:
                a, b = m[chave], m_anterior[chave]
                deltas[chave] = None if not b else (a - b) / b

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Faturamento", reais(m["receita"]), _delta_pct(deltas["receita"]))
    col2.metric("Custo", reais(m["custo"]), _delta_pct(deltas["custo"]), delta_color="inverse")
    col3.metric("Margem", reais(m["margem"]), _delta_pct(deltas["margem"]))
    col4.metric(
        "Margem %", f"{m['margem_pct']:.1%}",
        None if deltas["margem_pct"] is None else f"{deltas['margem_pct']*100:+.1f} p.p.",
    )
    col5.metric("Ticket médio", reais(m["ticket_medio"]), _delta_pct(deltas["ticket_medio"]))
