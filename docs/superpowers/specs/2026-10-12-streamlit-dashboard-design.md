# Dashboard Streamlit de vendas — design

Data: 2026-10-12

## Propósito

Oferecer um dashboard interativo dos mesmos achados de `analise.ipynb`
(faturamento, margem, evolução mensal, categoria, região, canal, produto,
ticket médio), navegável por filtros — complementar ao notebook, não um
substituto. O notebook permanece como está, intocado; o app é um artefato
novo e separado.

## Escopo

- Um app Streamlit de página única (`app.py`), rodando só localmente via
  `streamlit run app.py`. Sem deploy, sem autenticação, sem persistência.
- Lógica de carga e cálculo das métricas extraída para um módulo compartilhado
  (`dados_vendas.py`), para não duplicar às cegas o que já existe no notebook.
- Fora de escopo: Plotly/gráficos com hover (fica para uma iteração futura se
  o usuário pedir), multi-página, deploy, testes automatizados (projeto de
  curso, não tem suíte de teste hoje).

## Arquitetura

```
projeto-exemplo/
├── analise.ipynb          (inalterado)
├── app.py                 (novo — entrada do Streamlit)
├── dados_vendas.py        (novo — carga + cálculo, puro, sem Streamlit)
├── dados/vendas.csv        (inalterado)
├── estilos/design-system.md (inalterado — fonte da paleta)
└── requirements.txt        (+ streamlit)
```

`dados_vendas.py` expõe funções puras (sem nenhuma chamada `st.*`), testáveis
isoladamente e reaproveitáveis fora do Streamlit se um dia precisar:

- `carregar_dados(caminho="dados/vendas.csv") -> pd.DataFrame`: lê o CSV,
  converte `data` para datetime, preenche `regiao` faltante com
  `"Não informado"`, calcula `receita`/`custo`/`margem`. Mesma lógica das
  células `load-csv` + `clean-data-regiao` + `calc-receita-margem` do
  notebook.
- `aplicar_filtros(df, periodo, categorias, regioes, canais) -> pd.DataFrame`:
  recorte por intervalo de data + multiselects. Se um filtro vier vazio
  (nada selecionado), trata como "todos" para esse campo — não retorna
  DataFrame vazio por engano.
- `resumo(df) -> dict`: totais de receita/custo/margem/margem_pct/ticket médio
  do recorte atual.
- `por_dimensao(df, coluna) -> pd.DataFrame`: agrupa por `categoria`/`regiao`/
  `canal_venda`/`produto`, retorna receita/margem/margem_pct ordenado por
  receita.
- `evolucao_mensal(df) -> pd.Series`: receita por mês (`resample("ME")`).

`app.py` só orquestra: lê filtros da sidebar → chama as funções acima →
renderiza com `st.metric`, `st.pyplot` (matplotlib, reaproveitando as cores de
`estilos/design-system.md` como no notebook) e `st.dataframe` quando fizer
sentido mostrar a tabela.

## Fluxo de dados

1. `carregar_dados()` roda uma vez por sessão do Streamlit, cacheado com
   `@st.cache_data` (evita reler o CSV a cada interação com um filtro).
2. Sidebar: date range (min/max de `df["data"]`), multiselect de categoria,
   região, canal — todos com as opções vindas dos valores únicos do próprio
   `df` carregado (sem lista hardcoded, não desalinha se os dados mudarem).
3. `aplicar_filtros()` recorta o `df` cacheado conforme a seleção atual — essa
   parte roda a cada interação (é barata: `pandas` sobre 5 mil linhas).
4. KPIs (`st.metric` x4: Faturamento, Custo, Margem, Margem %) + ticket médio
   geral, calculados sobre o recorte filtrado.
5. Seções em sequência (mesma ordem do notebook): evolução mensal → categoria
   → região → canal → produto → ticket médio por produto. Cada seção é um
   `st.pyplot` de um gráfico de barra horizontal ordenada ou linha, estilo
   idêntico ao `graficos`/`design-system.md` (mesmas cores, sem moldura
   sup/direita, barra do zero).
6. Se o filtro resultar em 0 linhas (ex: combinação impossível), mostrar
   `st.warning("Nenhuma venda para esse filtro.")` em vez de quebrar nos
   gráficos vazios.

## Tratamento de erros / casos de borda

- CSV ausente/ilegível: deixar o `FileNotFoundError`/`pd.errors.ParserError`
  subir — é um app local de desenvolvimento, uma mensagem de erro clara do
  Streamlit já é suficiente, sem necessidade de try/except silencioso.
- Filtro de data com intervalo invertido: `st.date_input` com `value=(min,
  max)` já impede isso na UI do Streamlit (range picker).
- Região "Não informado": mantida como opção selecionável no multiselect de
  região, igual o notebook trata (não escondida, não excluída por padrão).

## Testando

Sem suíte automatizada (fora de escopo, ver acima). Verificação manual depois
de implementado: rodar `streamlit run app.py`, abrir no navegador, testar
cada filtro isoladamente e combinado, conferir que os números batem com o que
o notebook mostra quando o filtro está "tudo selecionado" (sem recorte).

---

## Revisão 2 — multi-página + Plotly (mesmo dia)

O usuário pediu, depois da v1 implementada e funcionando, uma versão mais
"premium"/SaaS a partir de um prompt-mestre externo (auth, multi-página,
services/repositories, testes `AppTest`, exportação, tema claro/escuro com
toggle próprio). Negociado com o usuário um subconjunto proporcional ao
projeto real (ver pergunta "Escopo real" — "Multi-página + design system,
sem auth/backend fictício"): **isto substitui a seção "Escopo" e
"Arquitetura" acima nos pontos abaixo; o resto do documento original
continua válido** (lógica de dados, tratamento de erro, filosofia de teste).

### O que muda

- **Multi-página**, via `st.navigation`/`st.Page` nativo do Streamlit (não
  um roteador customizado): Visão Geral, Exploração, Sobre.
- **Plotly** no lugar de matplotlib para os gráficos do app (hover com
  valores exatos). O notebook continua em matplotlib — são artefatos
  independentes, sem exigência de consistência visual entre eles.
- **Sem toggle de tema próprio** — os gráficos Plotly detectam o tema ativo
  do Streamlit (`st.context.theme.type`, `"light"`/`"dark"`) e aplicam o
  template Plotly correspondente; o usuário troca de tema pelo menu nativo
  do Streamlit, não por um controle da aplicação.
- **Continua fora de escopo**: autenticação, camadas `services/`/
  `repositories/` (não há banco de dados nem API — seria uma camada vazia
  só pra parecer "enterprise"), exportação de relatórios, testes
  automatizados, deploy.

### Arquitetura revisada

```text
projeto-exemplo/
├── analise.ipynb            (inalterado)
├── dados_vendas.py          (inalterado — já testado na v1)
├── app.py                   (reescrito — vira o shell de navegação)
├── pages/
│   ├── visao_geral.py       (KPIs + evolução mensal)
│   ├── exploracao.py        (filtros + categoria/região/canal/produto/ticket médio + tabela)
│   └── sobre.py             (conteúdo estático sobre o dataset/projeto)
├── components/
│   ├── filtros.py           (sidebar de filtros; widgets com key fixa → persistem entre páginas via session_state nativo)
│   ├── graficos.py          (construtores de figura Plotly, tema-aware)
│   └── kpis.py              (linha de st.metric)
├── styles/
│   └── theme.css            (polimento leve de espaçamento/tipografia; injetado sem interpolar dado de usuário — zero XSS)
└── requirements.txt         (+ plotly, já tem streamlit)
```

### Fluxo de dados (revisado)

1. `app.py` carrega `df` uma vez (`@st.cache_data`, mesma função
   `carregar_dados`), monta a navegação (`st.navigation`) e define o CSS
   global.
2. Cada página (`visao_geral.py`, `exploracao.py`) chama
   `components.filtros.renderizar(df) -> pd.DataFrame` no topo: essa função
   desenha os widgets da sidebar (mesma `key` nas duas páginas, por isso a
   seleção persiste ao navegar) e já devolve o recorte filtrado via
   `aplicar_filtros` — a página não manipula filtro bruto.
3. `visao_geral.py`: `resumo()` + `evolucao_mensal()` → KPIs
   (`components.kpis`) + um gráfico de linha Plotly.
4. `exploracao.py`: `por_dimensao()` para as 4 colunas + o cálculo de
   ticket médio por produto (mesma lógica da v1) → gráficos de barra
   horizontal Plotly + `st.dataframe` do recorte.
5. `sobre.py` não toca em `df` — é texto estático (fonte dos dados, o que
   cada coluna significa, link para o notebook).
6. Mesma regra de borda da v1: recorte vazio → `st.info(...)` e a página
   para aí (sem gráfico quebrado).

### Dependência nova

`plotly` adicionado ao `requirements.txt`. Instalar no mesmo venv que já
roda o Streamlit hoje (`.venv-mcp`, por causa do bloqueio de Smart App
Control documentado em
[[Jupyter MCP Server Bloqueado pelo Smart App Control do Windows]] — o
`.venv` baseado no Python do `uv` não serve pra rodar o Streamlit nesta
máquina).
