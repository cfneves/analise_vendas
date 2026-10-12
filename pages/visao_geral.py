# pages/visao_geral.py
import streamlit as st

from components import filtros, kpis
from components.graficos import grafico_evolucao_mensal
from dados_vendas import carregar_dados, evolucao_mensal, resumo

st.title("Visão geral")

df = carregar_dados()
recorte = filtros.renderizar(df)

if recorte.empty:
    st.info("Nenhuma venda para esse filtro.")
    st.stop()

kpis.renderizar(resumo(recorte))

tema = getattr(getattr(st.context, "theme", None), "type", "light") or "light"
st.plotly_chart(grafico_evolucao_mensal(evolucao_mensal(recorte), tema), width='stretch')
