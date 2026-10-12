# Dashboard Streamlit Multi-página (v2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the single-page Streamlit app (built in the v1 plan) into a 3-page app (Visão Geral / Exploração / Sobre) with Plotly charts, native Streamlit navigation, and filters that persist across pages — without inventing auth, services/repositories layers, or export features the project has no backend to support.

**Architecture:** `dados_vendas.py` (already built and tested) stays the single source of truth for data/metrics. New `components/` modules own UI building blocks (filters, KPIs, Plotly figures) shared by the new `pages/` modules. `app.py` becomes a thin navigation shell instead of the page content itself.

**Tech Stack:** Python, pandas (existing), streamlit (existing), plotly (new — `plotly.graph_objects`).

**Spec:** `docs/superpowers/specs/2026-10-12-streamlit-dashboard-design.md` (see "Revisão 2" section — it supersedes the v1 Escopo/Arquitetura sections; everything else in the spec still applies).

## Global Constraints

- `analise.ipynb` is never modified.
- No auth, no `services/`/`repositories/` layers, no export features, no automated test suite (`AppTest` or otherwise) — explicitly ruled out in the spec's Revisão 2.
- No custom light/dark toggle — charts read Streamlit's active theme (`st.context.theme.type`) and pick a Plotly template accordingly; the user switches theme via Streamlit's own menu.
- This project is **not a git repository** — no commit steps.
- `plotly` must be installed into `.venv-mcp` (the Anaconda-based venv), not `.venv` (the `uv`-based one) — `.venv`'s Python has its `_multiprocessing` native module blocked by Windows Smart App Control on this machine, which breaks Streamlit's server startup. See [[Jupyter MCP Server Bloqueado pelo Smart App Control do Windows]].
- Filter widgets in `components/filtros.py` must use the same `key=` string in every page that renders them, or the selection will not persist across page navigation (Streamlit's `st.navigation` re-runs each page's module fresh; only `session_state`, keyed by widget `key`, survives the switch).

## Review Focus

- Switching from "Visão Geral" to "Exploração" (or back) must keep the filter selections the user already made — the most likely bug is a page defining its own filter widget without reusing `components.filtros` (or reusing it with a different `key`), silently resetting filters on navigation.
- A filter combination with 0 rows must not crash `exploracao.py`'s Plotly bar charts (empty `x`/`y` arrays) — must show `st.info(...)` and stop, same as v1's `st.warning` + `st.stop()`.
- `visao_geral.py`'s KPIs must match `dados_vendas.resumo()` exactly for the unfiltered case — a copy-paste of the formatting logic (`reais()`) must not drift from what Task 1 of the v1 plan already validated.
- The Plotly theme switch (`st.context.theme.type`) must have a safe fallback (default to `"light"`) if that attribute is unavailable on the installed Streamlit version — do not let a missing attribute crash the whole page.
- `sobre.py` must not import or touch `dados_vendas` at all (per spec, it's static content) — an accidental `carregar_dados()` call there would silently triple the CSV reads per navigation cycle (once per page that loads it).

---

### Task 1: `components/graficos.py` — construtores de figura Plotly

**Files:**
- Create: `components/__init__.py` (empty — makes it an importable package)
- Create: `components/graficos.py`

**Interfaces:**
- Consumes: `dados_vendas.evolucao_mensal()` (`pd.Series`) and `dados_vendas.por_dimensao()` (`pd.DataFrame`) outputs — both already built and tested.
- Produces:
  - `grafico_evolucao_mensal(mensal: pd.Series, tema: str = "light") -> go.Figure`
  - `grafico_barra_horizontal(dados: pd.DataFrame, titulo: str, tema: str = "light", coluna: str = "receita") -> go.Figure`
  - `grafico_ticket_medio(ticket: pd.Series, tema: str = "light") -> go.Figure` (`ticket` indexed by produto, values = ticket médio)
  - `template_para_tema(tema: str) -> str` — `"plotly_white"` for `"light"`, `"plotly_dark"` for anything else (including `"dark"` and any unrecognized value — unrecognized input must not raise).

- [ ] **Step 1: Write `components/__init__.py` (empty) and `components/graficos.py`**

```python
# components/graficos.py
"""Construtores de figura Plotly — sem nenhuma chamada st.* (puro)."""
import pandas as pd
import plotly.graph_objects as go

COR_PRIMARIA = "#0072B2"


def template_para_tema(tema: str) -> str:
    return "plotly_dark" if tema == "dark" else "plotly_white"


def grafico_evolucao_mensal(mensal: pd.Series, tema: str = "light") -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=mensal.index, y=mensal.values, mode="lines+markers",
        line=dict(color=COR_PRIMARIA, width=2), marker=dict(size=7),
        hovertemplate="%{x|%b %Y}<br>R$ %{y:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        template=template_para_tema(tema),
        title="Faturamento mensal",
        yaxis_title="Receita (R$)",
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def grafico_barra_horizontal(dados: pd.DataFrame, titulo: str, tema: str = "light", coluna: str = "receita") -> go.Figure:
    ordenado = dados.sort_values(coluna)
    fig = go.Figure(go.Bar(
        x=ordenado[coluna], y=ordenado.index.astype(str), orientation="h",
        marker_color=COR_PRIMARIA,
        hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        template=template_para_tema(tema),
        title=titulo,
        xaxis_title="Receita (R$)",
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def grafico_ticket_medio(ticket: pd.Series, tema: str = "light") -> go.Figure:
    ordenado = ticket.sort_values()
    fig = go.Figure(go.Bar(
        x=ordenado.values, y=ordenado.index.astype(str), orientation="h",
        marker_color=COR_PRIMARIA,
        hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        template=template_para_tema(tema),
        title="Ticket médio por produto",
        xaxis_title="Receita média por venda (R$)",
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig
```

- [ ] **Step 2: Verify figure construction against known aggregates (disposable check, same style as the v1 plan)**

```bash
.venv-mcp/Scripts/python.exe -c "
from dados_vendas import carregar_dados, evolucao_mensal, por_dimensao
from components.graficos import grafico_evolucao_mensal, grafico_barra_horizontal, grafico_ticket_medio, template_para_tema

assert template_para_tema('dark') == 'plotly_dark'
assert template_para_tema('light') == 'plotly_white'
assert template_para_tema('anything-else') == 'plotly_white'  # safe fallback

df = carregar_dados()
mensal = evolucao_mensal(df)
fig1 = grafico_evolucao_mensal(mensal)
assert len(fig1.data[0].y) == 12
assert round(fig1.data[0].y[0], 2) == 1108186.68

cat = por_dimensao(df, 'categoria')
fig2 = grafico_barra_horizontal(cat, 'Faturamento por categoria')
assert 'Eletrônicos' in list(fig2.data[0].y)

ticket = df.groupby('produto')['receita'].mean()
fig3 = grafico_ticket_medio(ticket)
assert len(fig3.data[0].x) == 12

print('OK — figuras Plotly batem com os totais conhecidos')
"
```

Expected: prints `OK — figuras Plotly batem com os totais conhecidos`, no traceback. (`.venv-mcp` is used here, not `.venv` — `plotly` is not yet installed in either; install it first per Task 3 Step 2, or run this check after that step. If run before, it will fail with `ModuleNotFoundError: plotly` — that is expected until Task 3 Step 2 completes; move this verification after that step if executing tasks strictly in order.)

---

### Task 2: `components/filtros.py` e `components/kpis.py`

**Files:**
- Create: `components/filtros.py`
- Create: `components/kpis.py`

**Interfaces:**
- Consumes: `dados_vendas.aplicar_filtros` (Task 2 of the v1 plan), `dados_vendas.resumo` (v1 plan).
- Produces:
  - `filtros.renderizar(df: pd.DataFrame) -> pd.DataFrame` — draws the sidebar widgets (`key="filtro_periodo"`, `key="filtro_categorias"`, `key="filtro_regioes"`, `key="filtro_canais"` — exact strings, both pages must reuse them unchanged) and returns the filtered DataFrame.
  - `kpis.renderizar(m: dict) -> None` — draws the `st.metric` row from a `resumo()`-shaped dict.

These two modules call `st.*` (unlike `graficos.py`); they are verified manually in Task 3's browser check, not by a standalone script (no `AppTest` in scope per the spec).

- [ ] **Step 1: Write `components/filtros.py`**

```python
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
```

- [ ] **Step 2: Write `components/kpis.py`**

```python
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
```

- [ ] **Step 3: Sanity-check both modules import without error (not a behavioral test — Streamlit widgets need a running app to execute)**

```bash
.venv-mcp/Scripts/python.exe -c "
import ast
for f in ('components/filtros.py', 'components/kpis.py'):
    ast.parse(open(f, encoding='utf-8').read())
print('OK — sintaxe válida nos dois módulos')
"
```

Expected: `OK — sintaxe válida nos dois módulos`. Full behavioral verification happens in Task 3 Step 5 (manual browser check), since these modules only do anything meaningful inside a running Streamlit session.

---

### Task 3: páginas, navegação, estilo, dependência, verificação manual

**Files:**
- Create: `pages/visao_geral.py`
- Create: `pages/exploracao.py`
- Create: `pages/sobre.py`
- Create: `styles/theme.css`
- Modify: `app.py` (replace entirely — becomes the navigation shell)
- Modify: `requirements.txt` (append `plotly`)
- Delete: none (the old single-page `app.py` content is replaced in place, not kept as a separate file — the spec's Revisão 2 supersedes v1's single-page architecture)

**Interfaces:**
- Consumes: `components.filtros.renderizar`, `components.kpis.renderizar`, `components.graficos.*` (Tasks 1-2), `dados_vendas.*` (v1 plan).
- Produces: a runnable `streamlit run app.py` multi-page app. Nothing else depends on these files.

- [ ] **Step 1: Write `styles/theme.css`**

```css
/* styles/theme.css — polimento leve, sem cor fixa (deixa o tema nativo do Streamlit decidir fundo/texto) */
h1, h2, h3 { letter-spacing: -0.01em; }
[data-testid="stMetricValue"] { font-weight: 600; }
[data-testid="stSidebar"] { padding-top: 1rem; }
```

- [ ] **Step 2: Add `plotly` to `requirements.txt` and install into `.venv-mcp`**

Append to `requirements.txt` (after the `# Lado dashboard` section added in the v1 plan):

```
plotly
```

Run:

```bash
uv pip install --python .venv-mcp plotly
```

Expected: installs without touching `.venv` (the `uv`-based one stays untouched — it is not used to run Streamlit on this machine). Then re-run Task 1 Step 2's verification script — it should now pass (plotly is importable).

- [ ] **Step 3: Write `pages/visao_geral.py`**

```python
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
st.plotly_chart(grafico_evolucao_mensal(evolucao_mensal(recorte), tema), use_container_width=True)
```

- [ ] **Step 4: Write `pages/exploracao.py`**

```python
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
    st.plotly_chart(grafico_barra_horizontal(por_dimensao(recorte, coluna), titulo, tema), use_container_width=True)

st.subheader("Ticket médio por produto")
ticket = recorte.groupby("produto")["receita"].mean()
st.plotly_chart(grafico_ticket_medio(ticket, tema), use_container_width=True)

st.subheader("Dados filtrados")
st.dataframe(recorte, use_container_width=True)
```

- [ ] **Step 5: Write `pages/sobre.py`**

```python
# pages/sobre.py
import streamlit as st

st.title("Sobre")
st.markdown(
    "Dashboard do curso **Análise de dados em 10 minutos** (Assimov), sobre "
    "`dados/vendas.csv`: 5.000 vendas de 2025, com produto, categoria, "
    "região, canal de venda, quantidade e preço/custo unitário.\n\n"
    "Complementa (não substitui) a análise célula a célula em "
    "`analise.ipynb` — os mesmos cálculos de faturamento, margem e "
    "ticket médio vêm do módulo compartilhado `dados_vendas.py`."
)
```

- [ ] **Step 6: Rewrite `app.py` as the navigation shell**

```python
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
```

- [ ] **Step 7: Run the app and verify manually**

```bash
.venv-mcp/Scripts/python.exe -m streamlit run app.py --server.headless true
```

Open the printed local URL and check:
- Three pages appear in the nav (Visão Geral / Exploração / Sobre); Visão Geral is the default on load.
- On Visão Geral, the 5 KPIs with no filter applied match the v1-verified totals (`R$ 25.016.139,62` faturamento, `R$ 9.090.014,60` margem, `36,3%`).
- Pick a categoria filter on Visão Geral, then switch to Exploração: the same categoria is still selected (the Review Focus item — filters must persist across pages).
- On Exploração, hover over a bar in any chart and confirm a tooltip with the exact R$ value appears (this is the whole point of switching to Plotly).
- Pick an impossible filter combination (e.g. a categoria with 0 sales in a selected regiao): both pages show "Nenhuma venda para esse filtro." instead of a traceback.
- Switch the Streamlit theme (Settings menu → light/dark) and confirm the Plotly charts' background follows (no white chart on a dark page or vice versa).
- `Sobre` page loads without any noticeable delay or extra CSV read (per the Review Focus item — it must not call `carregar_dados()`).
- `analise.ipynb` still opens and runs unmodified.

---

## Self-review notes

- **Spec coverage:** every file in the spec's Revisão 2 "Arquitetura revisada" tree has a task; the filter-persistence requirement, the theme-aware Plotly templates, and the "no services/repositories/auth" exclusions are all addressed (Task 2 Step 1's shared `key=`s, Task 1's `template_para_tema`, and the Global Constraints list respectively).
- **No git steps:** confirmed, same as v1.
- **No pytest/AppTest added:** per spec, UI-facing modules (`filtros.py`, `kpis.py`, the `pages/*.py`) are verified manually in Task 3 Step 7; only the pure `graficos.py` gets a disposable `python -c` check, same pattern as the v1 plan's `dados_vendas.py`.
- **Venv constraint carried through every step:** every command in this plan uses `.venv-mcp`, never `.venv`, consistent with the Global Constraints entry about the Smart App Control block.
