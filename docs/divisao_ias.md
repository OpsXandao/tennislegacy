# Divisão de trabalho — Claude / Codex / Gemini

> Status: documento histórico de planejamento.
> Referência atual de arquitetura e integrações: `codex.md`, `docs/funcionalidades_integracoes.md` e `docs/refactoring_log.md`.

Princípio: cada IA é dona de uma camada. Overlap mínimo.
Regra: não adicionar abstrações desnecessárias. Corrigir, não reescrever do zero.

---

## Claude — Camada de Interface (`src/interface/`)

**Arquivos de responsabilidade exclusiva:**
- `src/interface/menu_principal.py`
- `src/interface/menu_torneio.py`
- `src/interface/menu_jogador.py`
- `src/interface/menu_progressao.py`
- `src/interface/menu_temporada.py`
- `src/io_utils.py`

**Arquivos que pode LER mas NÃO modificar:**
- `src/controller.py` (para entender sinais de estado)
- `src/torneio.py` (para entender o que retorna)

### Tarefas

#### T1 — Numeração de opções consistente (ALTO)
- `menu_torneio.py`: opções [6] e [7] mudam conforme `jogador_em_entrada_direta`. Fixar números, desabilitar opções inacessíveis com texto "(indisponível)" em vez de remover.
- `menu_jogador.py`: opção [1] só aparece se `pontos_de_skill > 0`. Sempre exibir, com "(0 disponíveis)" quando vazio.

#### T2 — Feedback após ações (ALTO)
- `menu_progressao.py`: após gastar skill points, mostrar os novos valores do atributo antes de retornar ao menu. Sem tela extra — basta um print antes do `input("Enter para continuar")`.
- `menu_torneio.py`: após jogar partida, exibir resultado claro (vitória/derrota, quem venceu, próximo adversário ou saída do torneio).

#### T3 — Paginação do histórico de partidas (MÉDIO)
- `menu_jogador.py`: histórico ilimitado. Mostrar só as últimas 10 partidas, com opção de ver mais.

#### T4 — Mensagens de transição de estado (MÉDIO)
- `controller.py` (linha ~42-44): mensagem Davis Cup sem contexto. Adicionar frase explicativa: "Normal — retornando ao menu da temporada."
- Qualquer transição silenciosa que deixe o jogador perdido.

#### T5 — Impacto visível de fadiga/lesão (MÉDIO)
- `menu_jogador.py`: ao exibir status, mostrar modificador de performance estimado (ex: "Fadiga alta → -10% em todos os atributos").

### Restrições
- Não mover lógica de negócio para os menus.
- Não criar novas classes.
- Usar funções helper locais se necessário, mas preferir inline quando for < 5 linhas.

---

## Codex — Camada de Domínio / Torneio (`src/torneio.py`, `src/pontuacao.py`, `src/simulacao_partida.py`)

**Arquivos de responsabilidade exclusiva:**
- `src/torneio.py`
- `src/pontuacao.py`
- `src/simulacao_partida.py`
- `src/jogar_partida.py`
- `src/davis_cup.py`
- `src/calendario.py`

**Arquivos que pode LER mas NÃO modificar:**
- `src/ranking.py` (para entender estrutura de dados)
- `src/jogador.py` (para entender campos do jogador)

### Tarefas

#### T6 — Bug cálculo semana de expiração de pontos (CRÍTICO)
- `pontuacao.py` linha ~176: `(semana_atual + 51) % 52 + 1` está errado.
- Correto: `((semana_atual - 1 + 51) % 52) + 1`
- Cobrir casos borda: semana 1, semana 52.

#### T7 — Bug Davis Cup não encerra (CRÍTICO)
- `davis_cup.py`: o tie não encerra quando um país vence 2 jogos.
- Adicionar checagem após cada jogo: se `vitorias_pais_a >= 2 or vitorias_pais_b >= 2`, encerrar tie.

#### T8 — Estado do torneio carregado múltiplas vezes (ALTO)
- `menu_torneio.py` (Codex NÃO modifica este arquivo — reportar o problema no codex.md para Claude resolver).
- Em `torneio.py`: garantir que `_carregar_estado()` seja idempotente e barata (não recalcula nada pesado).

#### T9 — Extrair magic numbers de torneio.py (ALTO)
- Linhas ~95-189: `max_top20 = 2`, cutoffs `<= 80` repetidos 3x, etc.
- Mover para constantes no topo da classe (ou topo do arquivo), com nomes descritivos.
- Não refatorar a lógica em si — só nomear os valores.

#### T10 — Resumo de pontos distribuídos (MÉDIO)
- `pontuacao.py`: após distribuir pontos, retornar (ou imprimir, se já é o padrão do arquivo) um resumo: pontos ganhos pelo jogador e nova posição estimada.
- Só para o jogador humano — não para todos os NPCs.

#### T11 — Separar enums de simulação (BAIXO)
- `simulacao_partida.py` linhas 11-44: 6 enums no topo do arquivo.
- Mover para `src/match_constants.py`. Atualizar imports em `simulacao_partida.py` e `jogar_partida.py`.

### Restrições
- Não quebrar a interface de `Torneio` que `menu_torneio.py` usa.
- Não mudar assinaturas de métodos públicos sem coordenar com Claude.
- `torneio.py` é grande mas não precisa ser dividido agora — só limpar o que foi listado.

---

## Gemini — Camada de Infraestrutura / Dados (`src/ranking.py`, `src/save.py`, `src/jogador.py`, `src/progressao.py`)

**Arquivos de responsabilidade exclusiva:**
- `src/ranking.py`
- `src/save.py`
- `src/json_utils.py`
- `src/jogador.py`
- `src/progressao.py`
- `src/dados.py`
- `src/gerador_nomes.py`

**Arquivos que pode LER mas NÃO modificar:**
- `src/torneio.py` (para entender como consome ranking)
- `db/ranking_atp.json` (para entender estrutura de dados)

### Tarefas

#### T12 — Bug deduplicação de ranking (CRÍTICO)
- `ranking.py` linha ~118-132: `_remover_duplicados()` descarta o jogador com menos pontos, mesmo que sejam jogadores diferentes com o mesmo nome.
- Corrigir: deduplicar por `(nome_normalizado, nacionalidade)` ou por ID se existir, não só por nome.
- Fallback: se não há como distinguir, manter o que tem mais pontos (comportamento atual), mas logar o caso.

#### T13 — Cache de ordenação no ranking (ALTO)
- `ranking.py` linha ~169: `obter_posicao()` chama `self.ordenar()` toda vez — O(n log n) por consulta.
- Adicionar flag `_sorted = False`, invalidar no insert/update, ordenar só quando necessário.

#### T14 — Sync de campos ao salvar (ALTO)
- `save.py` linhas ~40-58: campos `fadiga`, `status_lesao`, `pontos_de_skill` não são sincronizados do `Jogador` para o ranking.
- Adicionar esses campos ao bloco de sync.

#### T15 — DEFAULT_ATRIBUTOS em três lugares (MÉDIO)
- `ranking.py` linhas 8-19 e 99, `jogador.py` linhas ~46-57: mesma estrutura de atributos duplicada.
- Criar `src/constantes.py` com `DEFAULT_ATRIBUTOS` e `ARCHETYPES`.
- Importar de lá nos três arquivos.
- Não mover mais nada para esse arquivo por enquanto.

#### T16 — Mensagens de erro em save.py (BAIXO)
- `save.py` linha ~63: `print(f"❌ Erro ao salvar jogo: {e}")` — genérico demais.
- Incluir o path e o tipo de erro: `f"❌ Erro ao salvar {jogador_path}: {type(e).__name__}: {e}"`

#### T17 — Nomes de fase como constante (BAIXO)
- `menu_jogador.py` `_formatar_fase()` e `pontuacao.py` repetem os nomes de fase.
- Mover para `src/constantes.py` (já criado em T15).
- Gemini cria a constante; Claude atualiza o uso em `menu_jogador.py`.

### Restrições
- Não mudar estrutura dos JSONs de save sem documentar em `docs/saves.md`.
- Se mudar campos do `Jogador.__init__`, garantir que `from_dict` e `to_dict` sejam atualizados junto.
- Não adicionar dependências externas.

---

## Coordenação entre IAs

| Arquivo compartilhado | Quem toca | Como coordenar |
|---|---|---|
| `src/constantes.py` (novo) | Gemini cria, Claude e Codex importam | Gemini cria primeiro; os outros aguardam |
| `src/controller.py` | Claude lê, ninguém modifica (exceto mensagens triviais) | Avisar se precisar mudar |
| `src/io_utils.py` | Claude pode modificar | Avisar Codex se mudar assinatura de `safe_input` |

## O que NÃO fazer (regra de ouro)

- Não criar camadas de abstração para uso único.
- Não renomear variáveis em massa.
- Não reformatar arquivos inteiros (o Black já garante isso).
- Não mover arquivos de lugar.
- Não adicionar type hints onde não existem (a não ser que seja necessário para a correção).
- Não criar testes (há uma task separada para isso).
