---
name: revisao-critica
description: >-
  Passo mental rápido para confirmar que um resultado se sustenta antes de
  transformá-lo em conclusão. Use depois de executar a(s) célula(s) que respondem
  a uma pergunta da análise (um achado: taxa, ranking, comparação, padrão
  temporal) — antes de escrever a interpretação. Não se aplica a células de
  import, carregamento ou transformação. Verifica tamanho de amostra, se o número
  é share ou risco, explicações alternativas e causalidade sem base.
---

# Confirmar o resultado antes de virar conclusão

Use **só nas células que respondem a uma pergunta** da análise — um achado de
verdade (uma taxa, um ranking, uma comparação, um padrão no tempo). Em import,
carregamento ou transformação, não precisa.

Antes de escrever a interpretação, pare e percorra mentalmente:

- **O `n` está visível?** Toda taxa ou média vem com o tamanho da base do lado.
  Taxa sobre base pequena não é achado, é ruído — e num ranking por taxa, um
  único caso extremo pode liderar.
- **É share ou risco?** "X concentra 70% das mortes" mede o tamanho do grupo;
  "X tem 2,3× mais mortes por ocorrência" mede o risco. São coisas diferentes —
  se a pergunta é sobre risco, use a taxa, não o share.
- **Tem outra explicação?** Pergunte "o que mais explicaria isso?". Ex: "dias
  limpos têm mais mortes" pode ser só porque dia limpo é o mais comum — mais
  exposição, não mais risco. Quando a pergunta é risco, controle por exposição
  (use a taxa por ocorrência, não o número absoluto).
- **A janela é pequena?** Recortes curtos (um feriado de 3 dias, um único mês)
  são sensíveis a um evento extremo. Sinalize a fragilidade, não venda como
  tendência.
- **Estou afirmando causa sem base?** Os dados mostram associação, não causa.
  Não escreva que A "causa" B sem como isolar isso — e nunca cite uma variável
  que não existe no dataset.

Se algum ponto não fechar, não escreva a interpretação ingênua: ajuste a própria
célula (mostre o `n`, troque absoluto por taxa, controle por exposição) e escreva
a conclusão honesta — a que sobrevive a essas perguntas. Se o achado não se
sustenta, diga isso; é uma conclusão válida.
