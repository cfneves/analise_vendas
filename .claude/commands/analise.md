---
description: Prepara o ambiente e inicia uma análise de dados guiada sobre os arquivos em ./dados
argument-hint: "[caminho local ou URL dos dados — opcional]"
---

Você vai conduzir, do zero, uma análise de dados guiada. Por padrão os dados
ficam em `./dados/`, mas o aluno pode ter passado um caminho ou uma URL junto
do comando (veja o Passo 4). Siga os passos abaixo **em ordem**, mostrando ao
aluno o que está acontecendo (o objetivo é didático — ele deve enxergar o
ambiente sendo montado, não é uma caixa-preta).

O aluno passou isto junto do comando (pode estar vazio): `$ARGUMENTS`

## Passo 1 — Preflight

Verifique se `uv` está disponível: rode `uv --version`.
- Se NÃO estiver, pare aqui e diga ao aluno, de forma amigável, que precisa
  instalar o `uv` uma única vez (é o que roda o Jupyter MCP, fornece o Python e
  monta o ambiente). Dê o comando do sistema dele:
  - **macOS / Linux:** `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - **Windows (PowerShell):** `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

  Peça para ele reabrir o terminal e rodar `/analise` de novo.
- Se estiver, siga. (Não é preciso ter Python instalado — o `uv` cuida disso.)

## Passo 2 — Subir o ambiente (visível)

Rode `uv run --no-project --python 3.12 scripts/bootstrap.py`. Mostre a saída ao
aluno — ela já traz marcos com ✅ (ambiente, dependências, servidor). Resuma em
1 frase o que aconteceu.

Da saída, leia as duas últimas linhas (`JUPYTER_URL=...` e `JUPYTER_TOKEN=...`)
e também a linha com o endereço `.../lab?token=...`.

**Destaque o link ao máximo**, exatamente neste formato (cabeçalho + a URL sozinha
numa linha, para o terminal deixá-la clicável):

```
## 🔭 Abra o notebook ao vivo no navegador

http://localhost:PORTA/lab?token=SEU_TOKEN

👉 É aqui que você vê as tabelas e os gráficos surgindo em tempo real.
   Deixe esta aba lado a lado com o terminal: o terminal é o painel de
   controle, o navegador é a tela.
```

Substitua `PORTA` e `SEU_TOKEN` pelos valores reais. Mantenha a URL **sozinha
na própria linha**, sem texto antes ou depois, para o terminal conseguir
transformá-la em link clicável.

## Passo 3 — Conectar o Jupyter MCP

Chame a tool `connect_to_jupyter` passando a URL e o token. Confirme com uma
linha clara: **"✅ Jupyter conectado."**

## Passo 4 — Localizar os dados

O destino final é sempre a pasta `./dados/`. Antes de analisar, garanta que os
dados estão lá. Trate os casos nesta ordem:

**a) O aluno passou um argumento (`$ARGUMENTS`):**
- Se for um **caminho local** (ex: `~/Downloads/vendas.csv` ou uma pasta):
  confirme que existe e **copie** para `./dados/` (copie, não mova — preserve o
  original). Avise o que copiou.
- Se for uma **URL direta para um arquivo de dados** (.csv, .xlsx, .parquet,
  .json, .zip…): baixe para `./dados/`. Para funcionar em qualquer sistema
  (inclusive Windows, que não tem `unzip`), faça o download e a descompactação
  com **Python da stdlib** — `urllib.request` para baixar e `zipfile` para
  extrair — rodando via `uv run --no-project --python 3.12 python -c "..."`.
  Confirme que baixou e que abre.
- Se for uma **URL de página** (não um arquivo direto): **pergunte antes** se
  pode investigar a página em busca de um link de download de dataset. Só depois
  de o aluno confirmar, investigue, liste os links de dados que encontrou e
  deixe ele escolher qual baixar para `./dados/`.

**b) Sem argumento — confira `./dados/`:**
- Se houver arquivo(s) de dados, siga normalmente.
- Se estiver **vazia ou não existir**, não falhe. Pergunte ao aluno, de forma
  amigável, onde estão os dados, oferecendo opções:
  1. um **caminho** no computador (você copia para `./dados/`);
  2. uma **URL** (você baixa para `./dados/`);
  3. ele esqueceu mesmo — peça para colocar o arquivo em `./dados/` e avisar.

Em qualquer caminho, o estado final é: o(s) arquivo(s) em `./dados/`, confirmado(s)
com o aluno. Nunca baixe de uma página sem perguntar primeiro.

## Passo 5 — Entender o problema (interativo)

Liste os arquivos em `./dados/`. Dê uma olhada rápida no formato (colunas,
primeiras linhas) **sem ainda criar o notebook**.

Antes de qualquer análise, faça ao aluno 2-3 perguntas curtas:
- Qual é a pergunta de negócio que ele quer responder?
- Quem vai ler o resultado?
- O que significam as colunas ambíguas?

Espere a resposta. Não invente o objetivo da análise.

## Passo 6 — Criar o notebook e começar

Use `use_notebook` para criar `analise.ipynb` na raiz do projeto. Marque o
início com uma linha clara: **"🔍 Começando a análise."**

A partir daqui, conduza a análise seguindo **rigorosamente**:
- as regras do `CLAUDE.md` (células curtas, sem jargão, outputs inspecionáveis);
- o método da skill `analista-senior` (uma pergunta por vez: markdown da pergunta
  → código → executa → markdown da interpretação → próxima pergunta).

Nunca escreva várias células de uma vez para rodar depois. Reflita sobre cada
resultado antes de decidir o próximo passo.
