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
