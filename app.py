# app.py
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

css_path = Path(__file__).parent / "styles" / "theme.css"
st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

pagina = st.navigation([
    st.Page("pages/visao_geral.py", title="Visão Geral", default=True),
    st.Page("pages/exploracao.py", title="Exploração"),
    st.Page("pages/sobre.py", title="Sobre"),
])
pagina.run()
