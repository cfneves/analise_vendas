# app.py
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

css_path = Path(__file__).parent / "styles" / "theme.css"
st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.sidebar.markdown(
    '<div class="marca-sidebar">'
    '<div class="titulo">Dashboard de Vendas</div>'
    '<div class="subtitulo">Receita, margem e tendências</div>'
    '</div>',
    unsafe_allow_html=True,
)

pagina = st.navigation([
    st.Page("pages/visao_geral.py", title="Visão Geral", icon=":material/dashboard:", default=True),
    st.Page("pages/exploracao.py", title="Exploração", icon=":material/query_stats:"),
    st.Page("pages/sobre.py", title="Sobre", icon=":material/info:"),
])
pagina.run()
