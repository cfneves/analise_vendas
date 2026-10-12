# pages/sobre.py
import streamlit as st

st.title("Sobre")
st.markdown(
    "Dashboard de vendas sobre `dados/vendas.csv`: 5.000 vendas de 2025, com "
    "produto, categoria, região, canal de venda, quantidade e preço/custo "
    "unitário.\n\n"
    "Complementa (não substitui) a análise célula a célula em "
    "`analise.ipynb` — os mesmos cálculos de faturamento, margem e "
    "ticket médio vêm do módulo compartilhado `dados_vendas.py`."
)
