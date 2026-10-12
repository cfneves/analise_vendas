"""Carga e métricas de vendas — sem nenhuma dependência do Streamlit."""
import datetime as dt

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


def periodo_anterior(data_inicio: dt.date, data_fim: dt.date) -> tuple[dt.date, dt.date]:
    """Janela imediatamente anterior, com a mesma duração do período dado."""
    duracao = (data_fim - data_inicio)
    return (data_inicio - duracao - dt.timedelta(days=1), data_inicio - dt.timedelta(days=1))


def variacao_pct(atual: float, anterior: float) -> float | None:
    """None quando não há base de comparação válida (sem dado anterior)."""
    if not anterior:
        return None
    return (atual - anterior) / anterior


def destaques(df: pd.DataFrame, df_anterior: pd.DataFrame | None = None) -> list[str]:
    """Observações calculadas direto do recorte atual — sem IA, sem inventar
    nada: cada frase é um número que já está nos dados."""
    if df.empty:
        return []

    pontos = []

    cat = por_dimensao(df, "categoria")
    if not cat.empty:
        lider = cat.index[0]
        participacao = cat.loc[lider, "receita"] / df["receita"].sum()
        pontos.append(f"**{lider}** concentra {participacao:.0%} do faturamento do período.")

    produto = por_dimensao(df, "produto")
    if not produto.empty:
        lider = produto.index[0]
        participacao = produto.loc[lider, "receita"] / df["receita"].sum()
        pontos.append(f"**{lider}** é o produto líder, {participacao:.0%} do total.")

    if df_anterior is not None and not df_anterior.empty:
        var = variacao_pct(df["receita"].sum(), df_anterior["receita"].sum())
        if var is not None:
            direcao = "cresceu" if var >= 0 else "caiu"
            pontos.append(f"Faturamento {direcao} {abs(var):.1%} em relação ao período anterior equivalente.")

    return pontos


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
