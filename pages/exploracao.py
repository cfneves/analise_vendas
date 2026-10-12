# pages/exploracao.py
import streamlit as st

from components import filtros
from components.graficos import grafico_barra_horizontal, grafico_ticket_medio
from dados_vendas import carregar_dados, por_dimensao

st.title("Exploração")

df = carregar_dados()
recorte = filtros.renderizar(df)

if recorte.empty:
    st.info("Nenhuma venda para esse filtro.")
    st.stop()

tema = getattr(getattr(st.context, "theme", None), "type", "light") or "light"

for coluna, titulo in [
    ("categoria", "Faturamento por categoria"),
    ("regiao", "Faturamento por região"),
    ("canal_venda", "Faturamento por canal"),
    ("produto", "Faturamento por produto"),
]:
    st.subheader(titulo)
    st.plotly_chart(grafico_barra_horizontal(por_dimensao(recorte, coluna), titulo, tema), width='stretch')

st.subheader("Ticket médio por produto")
ticket = recorte.groupby("produto")["receita"].mean()
st.plotly_chart(grafico_ticket_medio(ticket, tema), width='stretch')

st.subheader("Dados filtrados")
st.dataframe(recorte, width='stretch')
