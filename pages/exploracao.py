# pages/exploracao.py
import streamlit as st

from components import filtros
from components.graficos import grafico_barra_horizontal, grafico_donut_categoria, grafico_ticket_medio
from dados_vendas import carregar_dados, por_dimensao

st.title("Exploração")

df = carregar_dados()
recorte = filtros.renderizar(df)

if recorte.empty:
    st.info("Nenhuma venda para esse filtro.")
    st.stop()

tema = getattr(getattr(st.context, "theme", None), "type", "light") or "light"

col_donut, col_barra = st.columns([1, 2])
with col_donut:
    with st.container(border=True):
        st.subheader("Distribuição por categoria")
        st.plotly_chart(grafico_donut_categoria(por_dimensao(recorte, "categoria"), tema), width='stretch')
with col_barra:
    with st.container(border=True):
        st.subheader("Faturamento por categoria")
        st.plotly_chart(grafico_barra_horizontal(por_dimensao(recorte, "categoria"), tema), width='stretch')

for coluna, titulo in [
    ("regiao", "Faturamento por região"),
    ("canal_venda", "Faturamento por canal"),
    ("produto", "Faturamento por produto"),
]:
    with st.container(border=True):
        st.subheader(titulo)
        st.plotly_chart(grafico_barra_horizontal(por_dimensao(recorte, coluna), tema), width='stretch')

with st.container(border=True):
    st.subheader("Ticket médio por produto")
    ticket = recorte.groupby("produto")["receita"].mean()
    st.plotly_chart(grafico_ticket_medio(ticket, tema), width='stretch')

with st.container(border=True):
    col_titulo, col_botao = st.columns([3, 1])
    col_titulo.subheader("Dados filtrados")
    col_botao.download_button(
        "Exportar CSV", recorte.to_csv(index=False).encode("utf-8"),
        file_name="vendas_filtradas.csv", mime="text/csv", width='stretch',
    )
    st.dataframe(recorte, width='stretch')
