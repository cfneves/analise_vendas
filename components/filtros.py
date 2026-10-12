# components/filtros.py
import streamlit as st

from dados_vendas import aplicar_filtros


def renderizar(df) -> "pd.DataFrame":
    st.sidebar.header("Filtros")
    data_min, data_max = df["data"].min().date(), df["data"].max().date()
    periodo = st.sidebar.date_input(
        "Período", value=(data_min, data_max),
        min_value=data_min, max_value=data_max, key="filtro_periodo",
    )
    data_inicio, data_fim = periodo if len(periodo) == 2 else (data_min, data_max)

    categorias = st.sidebar.multiselect(
        "Categoria", sorted(df["categoria"].unique()), key="filtro_categorias",
    )
    regioes = st.sidebar.multiselect(
        "Região", sorted(df["regiao"].unique()), key="filtro_regioes",
    )
    canais = st.sidebar.multiselect(
        "Canal de venda", sorted(df["canal_venda"].unique()), key="filtro_canais",
    )
    return aplicar_filtros(df, data_inicio, data_fim, categorias, regioes, canais)
