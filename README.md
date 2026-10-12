# Análise de dados com IA — template

Um projeto onde você joga seus dados numa pasta, roda o Claude Code e ele
**monta o ambiente sozinho** (Python, dependências, Jupyter) e conduz uma
análise guiada, uma pergunta de cada vez.

## Como usar (3 passos)

1. **Pré-requisito (uma vez só):** instale o `uv`. É a **única** coisa que você
   instala na mão — não precisa nem ter Python, o `uv` cuida disso.
   - **macOS / Linux:**
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
   - **Windows (PowerShell):**
     ```powershell
     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```
   Feche e reabra o terminal depois.

2. Coloque seus dados em **`dados/`** (já tem um `vendas_exemplo.csv` para testar).

3. Abra o Claude Code na pasta do projeto e digite:
   ```
   /analise
   ```
   O Claude faz o resto: cria o ambiente, sobe o Jupyter, conecta e começa a
   análise — fazendo algumas perguntas antes de mergulhar nos dados.

## Estrutura do projeto

Alguns arquivos começam com ponto (`.`) e ficam **ocultos** no Finder do Mac e
em gerenciadores de arquivos do Linux. Eles existem e são o que faz a mágica
funcionar. Para vê-los: no terminal use `ls -a`; no Finder, `Cmd + Shift + .`.

```
projeto/
├── dados/                      ← seus CSVs aqui
│   └── vendas_exemplo.csv
├── estilos/                    ← (opcional) identidade visual dos gráficos
│   ├── design-system.md        ← paleta e estilo padrão
│   └── (suas imagens de referência)
├── CLAUDE.md                   ← regras de casa (sempre carregadas pelo Claude)
├── requirements.txt            ← dependências Python
├── README.md                   ← este arquivo
│
├── .mcp.json          (oculto) ← registra o Jupyter MCP
├── .gitignore         (oculto)
├── .claude/           (oculto) ← configuração do Claude Code
│   ├── settings.json           ← hook que encerra o Jupyter ao fechar
│   ├── commands/
│   │   └── analise.md          ← o comando /analise
│   └── skills/
│       ├── analista-senior/
│       │   └── SKILL.md        ← o método da análise (o fluxo)
│       ├── verificacao-leitura/
│       │   └── SKILL.md        ← confere se os dados foram lidos certo (1x)
│       ├── revisao-critica/
│       │   └── SKILL.md        ← confere se o resultado se sustenta (por pergunta)
│       └── graficos/
│           └── SKILL.md        ← tipo de gráfico certo + estética + cores
│
├── scripts/
│   ├── bootstrap.py            ← cria venv, instala deps, sobe o Jupyter
│   └── stop.py                 ← encerra o Jupyter (roda sozinho ao fechar)
│
├── .venv/         (gerado, oculto)  ← ambiente virtual Python
└── .runtime/      (gerado, oculto)  ← pid/porta/token e log do Jupyter
```

### O que faz o quê

| Arquivo | Papel |
|---|---|
| `CLAUDE.md` | Regras que valem **sempre** (célula curta, sem jargão, etc.). |
| `.claude/skills/analista-senior/` | O **método**: como conduzir a análise, uma pergunta por vez. |
| `.claude/skills/verificacao-leitura/` | Confere **uma vez** se os dados foram lidos corretamente (encoding, separador, tipos). |
| `.claude/skills/revisao-critica/` | Confere, **a cada pergunta respondida**, se o resultado se sustenta (amostra, share vs. risco, causa). |
| `.claude/skills/graficos/` | Escolhe o **tipo de gráfico** certo e aplica estética, tamanho e cores consistentes. |
| `estilos/` | (Opcional) identidade visual dos gráficos: imagens de referência → `design-system.md` → cores do notebook. |
| `.claude/commands/analise.md` | O **botão**: o que `/analise` dispara. |
| `.mcp.json` | Conecta o Claude ao kernel do Jupyter ao vivo. |
| `scripts/bootstrap.py` | Monta o ambiente local — multiplataforma (Windows/macOS/Linux), idempotente. |

## Ver os gráficos e tabelas ao vivo

O terminal do Claude Code é o **painel de controle**: ele mostra o passo a passo,
e as tabelas (`.head()`, `.describe()`) aparecem ali como texto. Mas o terminal
**não desenha gráficos** — então, para ver os gráficos de verdade, abra o
notebook ao vivo no navegador.

O `/analise` mostra um link assim no início:
```
http://localhost:8888/lab?token=...
```
Abra ele numa aba e deixe lado a lado com o terminal: conforme o Claude escreve
e executa as células, os gráficos e tabelas vão aparecendo ali em tempo real.

> Se o navegador pedir para escolher um kernel, selecione
> **🤖 Análise de Dados (Claude Code)** — é o kernel deste projeto.

> O Claude **enxerga** os gráficos (config `ALLOW_IMG_OUTPUT=true` no `.mcp.json`)
> e os interpreta — por isso ele consegue comentar o que o gráfico mostra. Isso
> consome alguns tokens por imagem. Se quiser economizar, troque para `"false"`:
> o Claude passa a interpretar pelos dados, não pela imagem (um pouco menos rico,
> bem mais barato).

## Notas

- Funciona em **Windows, macOS e Linux** — só precisa do `uv` (nem Python).
- O `/analise` é o **único comando** que você digita. Ao fechar o Claude Code,
  o servidor Jupyter é encerrado automaticamente (hook `SessionEnd`).
- Se precisar derrubar o servidor na mão: `uv run --no-project scripts/stop.py`.
- O `bootstrap.py` é idempotente: pode rodar de novo sem medo.
- Para zerar tudo (inclusive reinstalar deps): rode `uv run --no-project
  scripts/stop.py` e apague as pastas `.venv` e `.runtime`, então rode `/analise`.
