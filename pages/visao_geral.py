# pages/visao_geral.py
import streamlit as st

from components import filtros, kpis
from components.graficos import grafico_evolucao_mensal
from dados_vendas import aplicar_filtros, carregar_dados, destaques, evolucao_mensal, periodo_anterior, resumo

st.title("Visão geral")

df = carregar_dados()
recorte = filtros.renderizar(df)

if recorte.empty:
    st.info("Nenhuma venda para esse filtro.")
    st.stop()

periodo_atual = st.session_state.get("filtro_periodo", ())
recorte_anterior = None
if len(periodo_atual) == 2:
    ant_ini, ant_fim = periodo_anterior(*periodo_atual)
    recorte_anterior = aplicar_filtros(
        df, ant_ini, ant_fim,
        st.session_state.get("filtro_categorias"),
        st.session_state.get("filtro_regioes"),
        st.session_state.get("filtro_canais"),
    )
m_anterior = resumo(recorte_anterior) if recorte_anterior is not None and not recorte_anterior.empty else None

with st.container(border=True):
    kpis.renderizar(resumo(recorte), m_anterior)

pontos = destaques(recorte, recorte_anterior)
if pontos:
    with st.container(border=True):
        st.subheader("Destaques")
        for p in pontos:
            st.markdown(f"- {p}")

tema = getattr(getattr(st.context, "theme", None), "type", "light") or "light"
with st.container(border=True):
    st.subheader("Faturamento mensal")
    st.plotly_chart(grafico_evolucao_mensal(evolucao_mensal(recorte), tema), width='stretch')
