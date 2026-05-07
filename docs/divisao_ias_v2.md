# Divisão de trabalho v2 — Claude / Codex / Gemini

> Status: documento histórico de planejamento.
> Referência atual de arquitetura e integrações: `codex.md`, `docs/funcionalidades_integracoes.md` e `docs/refactoring_log.md`.

Princípio: cada IA é dona de uma camada. Overlap mínimo.
Regra: corrigir sem reescrever do zero. Sem abstrações para uso único.

---

## Status da v1

| Tarefa | IA | Status |
|--------|----|--------|
| T1 Numeração consistente menus | Claude | ✅ FEITO |
| T2 Feedback skill points | Claude | ✅ FEITO |
| T3 Paginação histórico | Claude | ✅ FEITO |
| T4 Mensagens controller | Claude | ✅ FEITO |
| T5 Label fadiga/lesão | Claude | ✅ FEITO |
| T6 Bug semana expiração | Codex | ⏳ PENDENTE |
| T7 Bug Davis Cup não encerra | Codex | ⏳ PENDENTE |
| T8 Estado carregado múltiplas vezes | Codex | ⏳ PENDENTE |
| T9 Magic numbers torneio.py | Codex | ⏳ PENDENTE |
| T10 Resumo pontos distribuídos | Codex | ⏳ PENDENTE |
| T11 Enums para módulo separado | Codex | ⏳ PENDENTE |
| T12 Bug deduplicação ranking | Gemini | ⏳ PENDENTE |
| T13 Cache ordenação ranking | Gemini | ⏳ PENDENTE |
| T14 Sync campos ao salvar | Gemini | ⏳ PENDENTE |
| T15 DEFAULT_ATRIBUTOS → constantes.py | Gemini | ⏳ PENDENTE |
| T16 Mensagens erro save.py | Gemini | ⏳ PENDENTE |
| T17 Nomes de fase como constante | Gemini | ⏳ PENDENTE |

---

## Claude — Interface (`src/interface/`)

**Arquivos de responsabilidade exclusiva:**
`menu_torneio.py`, `menu_jogador.py`, `menu_progressao.py`, `menu_principal.py`,
`menu_temporada.py`, `menu_davis.py`, `match_info.py`, `io_utils.py`

**Pode LER, NÃO modificar:** `controller.py`, `torneio.py`, `jogador.py`

### Tarefas novas

#### C1 — Duplicação nas opções 2 e 3 do menu_davis.py (ALTO)
- `menu_davis.py` linhas ~84-113: opções [2] (stats adversário) e [3] (review) têm 4 linhas praticamente idênticas — validação de `proximo`, obtenção de `adversario`, chamada da função.
- Extrair para função helper local `_obter_adversario_ou_avisar(proximo)` que retorna o dict do adversário ou `None` com print de aviso.
- Aplicar nas duas opções.

#### C2 — Input inválido sem mensagem educada em menu_temporada.py (MÉDIO)
- `menu_temporada.py` linha ~124: `int(escolha)` pode lançar exceção que é capturada com print genérico.
- Substituir o bloco try/except amplo por validação explícita:
  ```python
  if not escolha.isdigit() or not (1 <= int(escolha) <= len(torneios)):
      print_red("Opção inválida. Digite um número da lista.")
      continue
  ```
- Garantir que todas as entradas numéricas nos menus passem por essa validação.

#### C3 — Próximo adversário visível após jogar partida (MÉDIO)
- `menu_torneio.py`: após jogar partida com vitória, mostrar quem é o próximo adversário.
- Usar `torneio.obter_proximo_adversario(jogador.nome)` após a partida — se retornar alguém, printar: `"Próximo adversário: {nome} (Overall: {overall})"`.
- Se não retornar ninguém (eliminado ou fim de torneio), não printar nada (já há mensagem de eliminação).

---

## Codex — Domínio (`src/torneio.py`, `src/simulacao_partida.py`, `src/jogar_partida.py`, `src/pontuacao.py`, `src/davis_cup.py`, `src/calendario.py`)

**Arquivos de responsabilidade exclusiva:** os listados acima
**Pode LER, NÃO modificar:** `ranking.py`, `jogador.py`, `save.py`

### Tarefas pendentes da v1

#### T6 — Bug semana de expiração (CRÍTICO)
- `pontuacao.py` linha ~176: `(semana_atual + 51) % 52 + 1` → correto: `((semana_atual - 1 + 51) % 52) + 1`
- Verificar: semana 1 → expira semana 52; semana 52 → expira semana 51.

#### T7 — Davis Cup não encerra ao atingir 2 vitórias (CRÍTICO)
- `davis_cup.py`: após cada jogo individual, verificar se `vitorias_a >= 2 or vitorias_b >= 2`. Se sim, encerrar o tie sem disputar os jogos restantes.
- Não simular mais jogos depois do vencedor definido.

#### T9 — Magic numbers em torneio.py (ALTO)
- Linhas ~95-189: `80`, `20`, `50`, `60`, `35`, `max_top20 = 2` etc. aparecem sem nome.
- Definir constantes no topo do arquivo:
  ```python
  CORTE_ENTRADA_DIRETA = 80
  LIMITE_TOP20_NA_CHAVE = 2
  TAMANHO_TOP20 = 20
  ```
- Substituir todas as ocorrências. Sem alterar a lógica.

#### T10 — Resumo de pontos após torneio (MÉDIO)
- `pontuacao.py`: ao distribuir pontos, ao final imprimir para o jogador humano:
  `"📊 {nome}: +{pontos_ganhos} pts → Total: {total} pts"`
- Só para quem tem `"jogador_humano": True` ou se o nome do jogador for o mesmo do save.

#### T11 — Enums de simulação para módulo próprio (BAIXO)
- `simulacao_partida.py` linhas 11-44: mover `ModoSimulacao`, `TipoSaque`, `EstrategiaAtaque`, `MomentoJogo`, `PosicaoQuadra`, `EstadoPartida` para `src/match_constants.py`.
- Atualizar imports em `simulacao_partida.py` e `jogar_partida.py`.

### Tarefas novas da auditoria

#### C4 — Unificar simular_game_detalhado e simular_game_estrategista (CRÍTICO)
- `jogar_partida.py` linhas ~515-707: as duas funções são 92% idênticas. Diferença: o método de simulação de ponto chamado internamente.
- Extrair uma função `_simular_game(sacador, receptor, fn_simular_ponto, ...)` que recebe `fn_simular_ponto` como parâmetro.
- `simular_game_detalhado` e `simular_game_estrategista` viram wrappers de 3-5 linhas que chamam `_simular_game` com o método correto.
- Não mudar as assinaturas públicas dessas funções.

#### C5 — Extrair _calcular_poder em simulacao_partida.py (ALTO)
- Linhas ~514-605: `_calcular_poder_saque`, `_calcular_poder_devolucao`, `_calcular_poder_rally` repetem o mesmo padrão:
  1. pegar atributos base
  2. aplicar bônus psicológico
  3. aplicar `stamina_mod`
  4. retornar valor
- Extrair `_aplicar_modificadores(valor_base, bonus_psico, stamina_mod)` e usar nas três funções.
- Não alterar os valores nem a lógica de cálculo — só eliminar o padrão repetido.

#### C6 — Quebrar escolher_participantes em torneio.py (ALTO)
- Linhas ~460-739: função de 291 linhas com 5 responsabilidades distintas.
- Dividir em funções privadas sem mudar o comportamento:
  - `_selecionar_entrada_direta(ranking, tamanho_chave)` → retorna lista de jogadores diretos
  - `_selecionar_wildcards(pool, n)` → retorna wildcards
  - `_montar_qualifying(pool, n_vagas)` → retorna participantes do qualifying
  - `_completar_com_alternates(chave, pool, n_faltando)` → completa a chave
  - `_adicionar_bots_se_necessario(chave, tamanho_chave)` → preenche com bots
- `escolher_participantes` chama essas funções em sequência.

#### C7 — Unificar _selecionar_entrada_direta_atp250 e _atp500 (MÉDIO)
- Linhas ~130-328: os dois métodos têm 80% do código igual. Só diferem nos pesos.
- Extrair `_selecionar_entrada_direta(ranking, pesos, tamanho_chave)` e passar os pesos como parâmetro dict.
- Os dois métodos viram chamadas com pesos diferentes.

#### C8 — Edge case Davis Cup: confrontos presos (MÉDIO)
- `davis_cup.py` linhas ~854-858: `if confrontos_feitos >= 2` assume sempre 2 confrontos exatos.
- Se por algum motivo o estado ficar com `confrontos_feitos == 1` e a lógica não avançar, o jogo trava.
- Adicionar log de aviso e fallback: se `confrontos_feitos >= 1` e tie já tem vencedor definido (via verificação de vitórias), forçar avanço.

#### C9 — Lógica condicional duplicada de Davis Cup em calendario.py (BAIXO)
- Linhas ~317, 333: `if info_torneio["tipo"] in ("Davis Cup", "United Cup"): continue` aparece duas vezes.
- Extrair para `_e_torneio_especial(tipo)` e usar nas duas verificações.

---

## Gemini — Infraestrutura (`src/ranking.py`, `src/save.py`, `src/jogador.py`, `src/progressao.py`, `src/dados.py`, `src/json_utils.py`)

**Arquivos de responsabilidade exclusiva:** os listados acima
**Pode LER, NÃO modificar:** `torneio.py`, `calendario.py`, `db/ranking_atp.json`

### Tarefas pendentes da v1

#### T12 — Bug deduplicação de ranking (CRÍTICO)
- `ranking.py` `_remover_duplicados()`: deduplicar por `(nome_normalizado, nacionalidade)`, não só por nome.
- Fallback: se mesma `(nome, nacionalidade)`, manter o com mais pontos.

#### T13 — Cache de ordenação (ALTO)
- `ranking.py`: `obter_posicao()` chama `self.ordenar()` toda vez.
- Flag `_sorted = False`, invalidada em qualquer insert/update. Ordenar só se `not _sorted`.

#### T14 — Sync de campos ao salvar (ALTO)
- `save.py`: adicionar `fadiga`, `status_lesao`, `pontos_de_skill` ao bloco de sync do ranking.

#### T15 — DEFAULT_ATRIBUTOS → constantes.py (MÉDIO)
- Criar `src/constantes.py` com `DEFAULT_ATRIBUTOS` e `DEFAULT_ATRIBUTOS_PSICOLOGICOS`.
- Importar de lá em `ranking.py` e `jogador.py`. Não mover mais nada por enquanto.

#### T16 — Mensagens de erro em save.py (BAIXO)
- Incluir path e tipo: `f"❌ Erro ao salvar {path}: {type(e).__name__}: {e}"`

#### T17 — Nomes de fase como constante (BAIXO)
- Adicionar `FASES_DISPLAY` dict em `src/constantes.py` (criado em T15).
- Gemini cria; Claude atualiza `_formatar_fase()` em `menu_jogador.py`.

### Tarefas novas da auditoria

#### G1 — Lógica confusa de sync de pontos em ranking.py (ALTO)
- Linhas ~77-82: condição `if soma_detalhada > 0` não zera pontos quando deveria.
- Reescrever a condição claramente:
  ```python
  # Recalcula total a partir do detalhado sempre que detalhado existe
  if "pontos_detalhados" in jogador and jogador["pontos_detalhados"]:
      soma = sum(p.get("pontos", 0) for p in jogador["pontos_detalhados"])
      if jogador.get("pontos", 0) != soma:
          jogador["pontos"] = soma
          mudou = True
  elif "pontos" not in jogador:
      jogador["pontos"] = 0
      mudou = True
  ```

#### G2 — Fix sync de jogador errado em save.py (ALTO)
- `save.py` linhas ~40-60: `normalizar_nome(j.get("nome", ""))` pode colidir com outro jogador.
- Adicionar verificação de `nacionalidade` além do nome:
  ```python
  nome_match = normalizar_nome(j.get("nome", "")) == normalizar_nome(dados.get("nome", ""))
  nac_match = j.get("nacionalidade", "") == dados.get("nacionalidade", "")
  if nome_match and nac_match:
  ```

#### G3 — Quebrar avancar_semana em calendario.py (MÉDIO)
- Linha ~281-424: função de 144 linhas com 5+ responsabilidades.
- Extrair funções privadas (sem mudar comportamento):
  - `_simular_npcs_da_semana(jogadores, torneios_da_semana, nome_save)` → simula todos os torneios NPC
  - `_aplicar_decay_pontos(jogadores)` → aplica decay
  - `_recuperar_jogadores(jogadores)` → energia/fadiga entre semanas
- `avancar_semana` chama essas em sequência.
- **Nota**: `calendario.py` está no escopo do Codex na v1, mas essa função é infraestrutura pura (I/O, JSON, estado). Gemini assume essa tarefa específica.

#### G4 — Erro handling inconsistente em dados.py (BAIXO)
- `dados.py` linha ~44: `json.load(f)` sem tratamento de `json.JSONDecodeError`.
- Adicionar ao `carregar_ranking()` e outras funções de leitura:
  ```python
  except json.JSONDecodeError as e:
      print(f"❌ Arquivo corrompido: {caminho}: {e}")
      return []  # ou raise, dependendo do caller
  ```
- Verificar os callers antes de decidir se faz `return []` ou `raise`.

---

## Coordenação entre IAs

| Arquivo | Quem toca | Dependência |
|---------|-----------|-------------|
| `src/constantes.py` (novo) | Gemini cria | Claude e Codex importam após Gemini concluir T15/T17 |
| `src/match_constants.py` (novo) | Codex cria | jogar_partida.py atualiza imports junto |
| `calendario.py` | Gemini assume G3; Codex assume C9 | Funções diferentes, sem conflito |
| `controller.py` | Ninguém modifica | Só leitura |

## Prioridade de execução sugerida

**Rodar em paralelo (sem dependências entre si):**
- Claude: C1, C2, C3
- Codex: T6, T7, C4 (os mais críticos primeiro)
- Gemini: T12, G1, G2 (os mais críticos primeiro)

**Depois (dependem dos anteriores ou são menores):**
- Codex: T9, C5, C6, C7, C8, T10, T11, C9
- Gemini: T13, T14, T15 → T17, T16, G3, G4
- Claude: aguarda T17 para atualizar `_formatar_fase`

## Regras gerais (imutáveis)

- Não criar abstrações para uso único.
- Não renomear em massa.
- Não reformatar arquivos inteiros.
- Não mover arquivos de lugar.
- Não adicionar dependências externas.
- Não criar testes (tarefa separada futura).
- Não mudar assinaturas públicas sem avisar as outras IAs.
- Documentar qualquer mudança de esquema JSON em `docs/saves.md`.
