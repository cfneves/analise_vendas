# Dashboard Streamlit de Vendas Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-only Streamlit dashboard (`app.py` + `dados_vendas.py`) over `dados/vendas.csv` that mirrors the findings already in `analise.ipynb`, filterable by date/categoria/regiao/canal, without touching the notebook.

**Architecture:** A pure-Python module (`dados_vendas.py`, no Streamlit imports) owns data loading, filtering, and aggregation. `app.py` is a thin Streamlit layer: reads sidebar filter widgets, calls the pure functions, renders `st.metric`/`st.pyplot`/`st.dataframe`.

**Tech Stack:** Python, pandas, matplotlib, streamlit (new dependency — add to `requirements.txt`).

**Spec:** `docs/superpowers/specs/2026-10-12-streamlit-dashboard-design.md`

## Global Constraints

- `analise.ipynb` is never modified by this plan.
- `dados_vendas.py` must contain zero `streamlit`/`st.*` references — it is plain pandas, importable and testable without Streamlit running.
- Local execution only: `streamlit run app.py`. No deploy, no auth, no persistence.
- No automated test suite in scope (spec's explicit decision) — verification steps below use disposable `python -c` checks against known totals from `analise.ipynb`, not pytest.
- This project is **not a git repository** (`git rev-parse --is-inside-work-tree` fails) — skip every "commit" step; do not run `git init` unless the user asks.
- Multiselect filters (categoria/regiao/canal) must source their options from the loaded DataFrame's unique values, never a hardcoded list.
- An empty multiselect selection means "no filter applied for this field" (show all), not "show nothing."

## Review Focus

- Empty multiselect (nothing picked) must behave as "all values," not filter the DataFrame down to zero rows.
- A filter combination that legitimately yields 0 rows must render `st.warning(...)` instead of crashing on an empty-DataFrame groupby/plot.
- `margem_pct = margem / receita` divides by zero when a filtered slice has `receita == 0` (the empty-slice case above) — must be guarded, not left to raise or silently show `inf`/`NaN`.
- `"Não informado"` (the 154 rows with missing `regiao`, already cleaned by `carregar_dados`) must appear as a selectable region, included by default like every other region.
- `st.date_input` range filter must work when the user collapses the range to a single day (`min == max`) — an off-by-one in the comparison (`<` vs `<=`) would silently exclude that day's sales.

---

### Task 1: `dados_vendas.py` — carga e métricas base

**Files:**
- Create: `dados_vendas.py`

**Interfaces:**
- Consumes: `dados/vendas.csv` (columns: `data, produto, categoria, regiao, quantidade, preco_unitario, custo_unitario, canal_venda`)
- Produces:
  - `carregar_dados(caminho: str = "dados/vendas.csv") -> pd.DataFrame` — adds `receita`, `custo`, `margem` columns; `data` is `datetime64`; `regiao` has no NaN (filled with `"Não informado"`).
  - `resumo(df: pd.DataFrame) -> dict` — keys `receita`, `custo`, `margem`, `margem_pct`, `ticket_medio`. If `df` is empty or `receita` sums to 0, `margem_pct` is `0.0` (not `NaN`/`inf`).
  - `por_dimensao(df: pd.DataFrame, coluna: str) -> pd.DataFrame` — grouped by `coluna`, columns `receita, margem, margem_pct`, sorted descending by `receita`. Empty input returns an empty DataFrame with those columns (no exception).
  - `evolucao_mensal(df: pd.DataFrame) -> pd.Series` — monthly `receita`, indexed by month-end timestamp (`resample("ME")`).

- [ ] **Step 1: Write `dados_vendas.py` with the four functions**

```python
"""Carga e métricas de vendas — sem nenhuma dependência do Streamlit."""
import pandas as pd


def carregar_dados(caminho: str = "dados/vendas.csv") -> pd.DataFrame:
    df = pd.read_csv(caminho)
    df["data"] = pd.to_datetime(df["data"])
    df["regiao"] = df["regiao"].fillna("Não informado")
    df["receita"] = df["quantidade"] * df["preco_unitario"]
    df["custo"] = df["quantidade"] * df["custo_unitario"]
    df["margem"] = df["receita"] - df["custo"]
    return df


def resumo(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"receita": 0.0, "custo": 0.0, "margem": 0.0, "margem_pct": 0.0, "ticket_medio": 0.0}
    receita = df["receita"].sum()
    custo = df["custo"].sum()
    margem = df["margem"].sum()
    return {
        "receita": receita,
        "custo": custo,
        "margem": margem,
        "margem_pct": (margem / receita) if receita else 0.0,
        "ticket_medio": df["receita"].mean(),
    }


def por_dimensao(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    colunas = ["receita", "margem", "margem_pct"]
    if df.empty:
        return pd.DataFrame(columns=colunas)
    agrupado = df.groupby(coluna)[["receita", "margem"]].sum()
    agrupado["margem_pct"] = agrupado["margem"] / agrupado["receita"]
    return agrupado.sort_values("receita", ascending=False)


def evolucao_mensal(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype="float64")
    return df.set_index("data").resample("ME")["receita"].sum()
```

- [ ] **Step 2: Verify against the known totals from `analise.ipynb`**

Run (from the project root, with `.venv` active or via `.venv/Scripts/python.exe`):

```bash
.venv/Scripts/python.exe -c "
from dados_vendas import carregar_dados, resumo, por_dimensao, evolucao_mensal

df = carregar_dados()
assert df.shape == (5000, 11), df.shape

r = resumo(df)
assert round(r['receita'], 2) == 25016139.62, r['receita']
assert round(r['margem'], 2) == 9090014.60, r['margem']
assert round(r['margem_pct'], 3) == 0.363, r['margem_pct']

cat = por_dimensao(df, 'categoria')
assert cat.index[0] == 'Eletrônicos', cat.index[0]
assert round(cat.loc['Eletrônicos', 'receita'], 2) == 17113195.00

mensal = evolucao_mensal(df)
assert len(mensal) == 12, len(mensal)
assert round(mensal.iloc[0], 2) == 1108186.68

# edge cases: empty input must not raise
vazio = df.iloc[0:0]
assert resumo(vazio)['margem_pct'] == 0.0
assert por_dimensao(vazio, 'categoria').empty
assert evolucao_mensal(vazio).empty

print('OK — todos os totais batem com analise.ipynb')
"
```

Expected: prints `OK — todos os totais batem com analise.ipynb` with no `AssertionError`/traceback. These totals come directly from the `calc-totais` and `calc-categoria` cells already executed in `analise.ipynb` — if they don't match, the bug is in this file, not the notebook.

---

### Task 2: `dados_vendas.py` — `aplicar_filtros`

**Files:**
- Modify: `dados_vendas.py` (append function)

**Interfaces:**
- Consumes: `carregar_dados()`'s output (Task 1).
- Produces: `aplicar_filtros(df: pd.DataFrame, data_inicio, data_fim, categorias: list[str], regioes: list[str], canais: list[str]) -> pd.DataFrame`. `data_inicio`/`data_fim` are `datetime.date` or `pd.Timestamp`, inclusive on both ends. An empty list for `categorias`/`regioes`/`canais` means "no filter" for that field.

- [ ] **Step 1: Append `aplicar_filtros` to `dados_vendas.py`**

```python
def aplicar_filtros(df, data_inicio, data_fim, categorias=None, regioes=None, canais=None) -> pd.DataFrame:
    recorte = df[
        (df["data"] >= pd.Timestamp(data_inicio))
        & (df["data"] <= pd.Timestamp(data_fim))
    ]
    if categorias:
        recorte = recorte[recorte["categoria"].isin(categorias)]
    if regioes:
        recorte = recorte[recorte["regiao"].isin(regioes)]
    if canais:
        recorte = recorte[recorte["canal_venda"].isin(canais)]
    return recorte
```

- [ ] **Step 2: Verify filter semantics, including the Review Focus edge cases**

```bash
.venv/Scripts/python.exe -c "
import pandas as pd
from dados_vendas import carregar_dados, aplicar_filtros

df = carregar_dados()
d_min, d_max = df['data'].min(), df['data'].max()

# sem nenhum filtro de categoria/regiao/canal -> tudo dentro do periodo
todos = aplicar_filtros(df, d_min, d_max, [], [], [])
assert len(todos) == len(df), (len(todos), len(df))

# um dia so (d_min == d_max) inclui as vendas desse dia
um_dia = aplicar_filtros(df, d_min, d_min, [], [], [])
assert len(um_dia) == (df['data'] == d_min).sum(), len(um_dia)
assert len(um_dia) > 0

# filtro de categoria restringe de verdade
so_eletronicos = aplicar_filtros(df, d_min, d_max, ['Eletrônicos'], [], [])
assert (so_eletronicos['categoria'] == 'Eletrônicos').all()
assert len(so_eletronicos) < len(df)

# combinacao impossivel -> DataFrame vazio, sem excecao
vazio = aplicar_filtros(df, d_min, d_max, ['Eletrônicos'], ['Não informado'], [])
assert len(vazio) >= 0  # so nao pode levantar excecao

# 'Não informado' e um valor de regiao filtravel normalmente
nao_informado = aplicar_filtros(df, d_min, d_max, [], ['Não informado'], [])
assert len(nao_informado) == 154, len(nao_informado)

print('OK — aplicar_filtros cobre os casos de borda')
"
```

Expected: prints `OK — aplicar_filtros cobre os casos de borda` with no errors.

---

### Task 3: `app.py` — dashboard Streamlit

**Files:**
- Create: `app.py`

**Interfaces:**
- Consumes: `dados_vendas.carregar_dados`, `aplicar_filtros`, `resumo`, `por_dimensao`, `evolucao_mensal` (Tasks 1-2).
- Produces: a runnable Streamlit entry point (`streamlit run app.py`). Nothing else depends on this file.

- [ ] **Step 1: Write `app.py`**

```python
import matplotlib.pyplot as plt
import streamlit as st

from dados_vendas import aplicar_filtros, carregar_dados, evolucao_mensal, por_dimensao, resumo

COR_PRIMARIA = "#0072B2"
COR_SECUNDARIA = "#94A3B8"

plt.rcParams.update({
    "figure.dpi": 110,
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
})


def reais(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@st.cache_data
def carregar() -> "pd.DataFrame":
    return carregar_dados()


st.set_page_config(page_title="Dashboard de Vendas", layout="wide")
st.title("Dashboard de vendas")

df = carregar()

st.sidebar.header("Filtros")
data_min, data_max = df["data"].min().date(), df["data"].max().date()
periodo = st.sidebar.date_input("Período", value=(data_min, data_max), min_value=data_min, max_value=data_max)
data_inicio, data_fim = periodo if len(periodo) == 2 else (data_min, data_max)

categorias = st.sidebar.multiselect("Categoria", sorted(df["categoria"].unique()))
regioes = st.sidebar.multiselect("Região", sorted(df["regiao"].unique()))
canais = st.sidebar.multiselect("Canal de venda", sorted(df["canal_venda"].unique()))

recorte = aplicar_filtros(df, data_inicio, data_fim, categorias, regioes, canais)

if recorte.empty:
    st.warning("Nenhuma venda para esse filtro.")
    st.stop()

m = resumo(recorte)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Faturamento", reais(m["receita"]))
col2.metric("Custo", reais(m["custo"]))
col3.metric("Margem", reais(m["margem"]))
col4.metric("Margem %", f"{m['margem_pct']:.1%}")
st.metric("Ticket médio", reais(m["ticket_medio"]))


def grafico_barra_horizontal(dados, titulo, coluna="receita"):
    ordenado = dados.sort_values(coluna)
    fig, ax = plt.subplots(figsize=(8, max(2.5, 0.4 * len(ordenado))))
    ax.barh(ordenado.index.astype(str), ordenado[coluna], color=COR_PRIMARIA)
    ax.set_title(titulo)
    ax.set_xlabel("Receita (R$)")
    ax.xaxis.set_major_formatter(lambda v, _: f"{v/1e6:,.1f}M".replace(",", "."))
    st.pyplot(fig)
    plt.close(fig)


st.subheader("Evolução mensal")
mensal = evolucao_mensal(recorte)
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(mensal.index, mensal.values, marker="o", color=COR_PRIMARIA)
ax.set_ylabel("Receita (R$)")
ax.yaxis.set_major_formatter(lambda v, _: f"{v/1000:,.0f}k".replace(",", "."))
st.pyplot(fig)
plt.close(fig)

st.subheader("Por categoria")
grafico_barra_horizontal(por_dimensao(recorte, "categoria"), "Faturamento por categoria")

st.subheader("Por região")
grafico_barra_horizontal(por_dimensao(recorte, "regiao"), "Faturamento por região")

st.subheader("Por canal de venda")
grafico_barra_horizontal(por_dimensao(recorte, "canal_venda"), "Faturamento por canal")

st.subheader("Por produto")
grafico_barra_horizontal(por_dimensao(recorte, "produto"), "Faturamento por produto")

st.subheader("Ticket médio por produto")
ticket_produto = recorte.groupby("produto")["receita"].mean().sort_values()
fig, ax = plt.subplots(figsize=(8, max(2.5, 0.4 * len(ticket_produto))))
ax.barh(ticket_produto.index, ticket_produto.values, color=COR_PRIMARIA)
ax.set_xlabel("Receita média por venda (R$)")
ax.xaxis.set_major_formatter(lambda v, _: reais(v))
st.pyplot(fig)
plt.close(fig)
```

- [ ] **Step 2: Add `streamlit` to `requirements.txt`**

Append a line to the existing `requirements.txt` (don't touch the existing `# Lado Jupyter` / `# Lado análise de dados` sections):

```
# Lado dashboard
streamlit
```

- [ ] **Step 3: Install it into the existing venv**

```bash
uv pip install --python .venv -r requirements.txt
```

Expected: `streamlit` (and its dependencies) install without error into `.venv`.

- [ ] **Step 4: Run the app and verify manually**

```bash
.venv/Scripts/streamlit.exe run app.py
```

Expected: Streamlit prints a local URL (default `http://localhost:8501`). Open it and check:
- The four KPI metrics match `analise.ipynb`'s `calc-totais` cell (`R$ 25.016.139,62` faturamento, `R$ 9.090.014,60` margem, `36,3%`) when no filters are applied.
- Each multiselect (categoria/regiao/canal), left empty, shows all data — selecting one or more values narrows every chart and KPI.
- Picking a single day in the date filter (collapsing the range) still shows that day's sales, not a blank dashboard.
- Picking an impossible combination (e.g., a categoria that has zero sales in a selected regiao) shows the "Nenhuma venda para esse filtro." warning instead of a traceback.
- `analise.ipynb` still opens and runs unmodified (open it in JupyterLab, confirm the file's mtime/content is unchanged by this plan).

---

## Self-review notes

- **Spec coverage:** every function named in the spec (`carregar_dados`, `aplicar_filtros`, `resumo`, `por_dimensao`, `evolucao_mensal`) has a task; the sidebar filters, KPI metrics, and the six chart sections from the spec's "Fluxo de dados" are all in Task 3's `app.py`; the empty-filter warning and `"Não informado"` handling from "Tratamento de erros" are both covered by Task 2's tests and Task 3's `st.stop()` branch.
- **No git steps:** confirmed the project has no `.git`; no commit steps were added.
- **No pytest added:** verification steps use disposable `python -c` scripts per the spec's explicit "no automated suite" scope — nothing adds a test framework dependency.
