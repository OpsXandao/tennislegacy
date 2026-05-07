# Divisão de trabalho v3 — Claude / Codex / Gemini

> Status: documento histórico de planejamento.
> Referência atual de arquitetura e integrações: `codex.md`, `docs/funcionalidades_integracoes.md` e `docs/refactoring_log.md`.

Princípio: cada IA é dona de uma camada. Overlap mínimo.
Regra: corrigir sem reescrever do zero. Sem abstrações para uso único.

---

## O que já existe (não recriar)

| Feature | Status | Arquivo principal |
|---------|--------|-------------------|
| Ranking com decay de pontos (52 semanas) | ✅ funciona | ranking.py |
| Chave de torneio com seeds e wildcards | ✅ funciona | torneio.py |
| Simulação NPC automática por semana | ✅ funciona | calendario.py |
| Motor de partida (superfície, atributos, stamina, psicológico) | ✅ funciona | simulacao_partida.py |
| Progressão (XP, níveis, skill points) | ✅ funciona | progressao.py |
| Fadiga e lesão | ✅ funciona | progressao.py |
| Calendário com 52 semanas | ✅ funciona | db/calendario.json |
| Davis Cup | ✅ funciona | davis_cup.py |
| Prize money no calendário | ⚠️ campo existe, não pago | calendario.py, save.py |
| Economia do jogador (dinheiro) | ⚠️ campo existe, não atualizado | save.py |

---

## Status da v2

| Tarefa | IA | Status |
|--------|----|--------|
| C1 Duplicação menu_davis.py | Claude | ✅ FEITO |
| C2 Input validation menu_temporada.py | Claude | ✅ FEITO |
| C3 Próximo adversário após partida | Claude | ✅ FEITO |
| Fix routing [8] menu_torneio.py | Claude | ✅ FEITO |
| T6 Bug semana expiração | Codex | ⏳ PENDENTE |
| T7 Davis Cup não encerra tie | Codex | ⏳ PENDENTE |
| T8 Estado carregado múltiplas vezes | Codex | ⏳ PENDENTE |
| T9 Magic numbers torneio.py | Codex | ⏳ PENDENTE |
| T10 Resumo pontos distribuídos | Codex | ⏳ PENDENTE |
| T11 Enums → match_constants.py | Codex | ⏳ PENDENTE |
| C4 Unificar game_detalhado/estrategista | Codex | ⏳ PENDENTE |
| C5 Extrair _calcular_poder | Codex | ⏳ PENDENTE |
| C6 Quebrar escolher_participantes | Codex | ⏳ PENDENTE |
| C7 Unificar _selecionar_entrada_direta | Codex | ⏳ PENDENTE |
| C8 Edge case Davis Cup | Codex | ⏳ PENDENTE |
| C9 Lógica especial Davis Cup duplicada | Codex | ⏳ PENDENTE |
| T12 Bug deduplicação ranking | Gemini | ⏳ PENDENTE |
| T13 Cache ordenação ranking | Gemini | ⏳ PENDENTE |
| T14 Sync campos ao salvar | Gemini | ⏳ PENDENTE |
| T15 DEFAULT_ATRIBUTOS → constantes.py | Gemini | ⏳ PENDENTE |
| T16 Mensagens erro save.py | Gemini | ⏳ PENDENTE |
| T17 Nomes de fase como constante | Gemini | ⏳ PENDENTE |
| G1 Sync de pontos ranking.py | Gemini | ⏳ PENDENTE |
| G2 Sync jogador em save.py | Gemini | ⏳ PENDENTE |
| G3 Quebrar avancar_semana | Gemini | ⏳ PENDENTE |
| G4 Error handling dados.py | Gemini | ⏳ PENDENTE |

---

## Features novas — Fase 1: Fundação (Codex + Gemini primeiro)

### Gemini — N-G1: Histórico de torneios por jogador (CRÍTICO pré-requisito)

- `ranking.py` + `jogador.py`: adicionar campo `historico_torneios` ao jogador no ranking.
- Estrutura por entrada:
  ```json
  { "nome": "Australian Open", "tipo": "Grand Slam", "fase": "semifinal",
    "pontos": 720, "prize": 360000, "semana": 3, "ano": 2025 }
  ```
- `pontuacao.py` (Codex) vai popular esse campo; Gemini cria o schema e o método de append.
- Ao expirar pontos em `_aplicar_decay_pontos`, marcar entradas correspondentes como `"expirado": true` (não apagar — histórico permanente).

### Gemini — N-G2: Race to Turin (YTD points tracking) (ALTO)

- `ranking.py`: adicionar campo `pontos_ytd` ao jogador.
- Reset em semana 1 de cada ano.
- `SistemaRanking` expõe `ranking_race(n=20)` → lista ordenada por `pontos_ytd`.
- Race inclui todos os torneios (não aplica regra best-18 — é YTD puro).

### Gemini — N-G3: Ledger de prize money (ALTO)

- `save.py`: ao sincronizar jogador, atualizar `dinheiro` somando prêmios recebidos.
- `jogador.py`: adicionar `historico_financeiro` (lista de `{torneio, valor, semana, ano}`).
- Método `adicionar_receita(valor, descricao, semana, ano)` no `Jogador`.

### Gemini — N-G4: Sistema de idade/pico/declínio (MÉDIO — não bloqueia outros)

- `jogador.py`: adicionar campo `ano_nascimento` (calculado de `idade` no save).
- `progressao.py`: função `_modificador_idade(idade)` → float entre 0.7 e 1.0:
  - < 18: 0.80 (jovem promissor, instável)
  - 18-24: 0.90 + 0.015/ano (subindo)
  - 25-30: 1.00 (pico)
  - 31-34: 0.98 - 0.015/ano (declínio leve)
  - 35+: 0.85 - 0.03/ano (declínio acelerado)
- Aplicar modificador como multiplicador de overall na simulação (não nos atributos base).
- Envelhecer jogador 1 ano a cada semana 1 da temporada.

---

### Codex — N-X1: Regra Best-18 ATP (CRÍTICO)

- `pontuacao.py`: após distribuir pontos, recalcular `pontos_ranking` do jogador como soma dos 18 melhores torneios do `historico_torneios` (campo criado por Gemini N-G1).
- Torneios obrigatórios (Grand Slams + ATP 1000): contam sempre.
- Demais: os melhores até completar 18 no total.
- Salvar `pontos_ranking` separado de `pontos` (que continua sendo soma do `pontos_detalhados`).
- `SistemaRanking.ordenar()` usa `pontos_ranking` se existir; senão usa `pontos`.

### Codex — N-X2: Distribuição de prize money (ALTO)

- `pontuacao.py`: ao distribuir pontos, calcular também o prêmio em dinheiro por fase.
- Premio por fase = `torneio.premiacao * fator_fase` onde `fator_fase`:
  - campeão: 18%, final: 10%, semi: 6%, quartas: 3%, oitavas: 1.5%, r32: 0.9%, r64: 0.45%, r128: 0.25%
- Chamar método `adicionar_receita(...)` do jogador (Gemini N-G3) para o jogador humano.
- Para NPCs: apenas atualizar `dinheiro` diretamente no registro do ranking.

### Codex — N-X3: Entry list com cutoff, PR e alternates (MÉDIO)

- `torneio.py`: antes de montar a chave, calcular `cutoff_rank` = posição do último jogador aceito.
- Implementar `protected_ranking`: jogador lesionado usa seu ranking de antes da lesão por até 52 semanas.
- Campo `status_entry` por jogador no estado do torneio: `"direct"`, `"wildcard"`, `"qualifier"`, `"lucky_loser"`, `"alternate"`.
- Lucky loser: primeiro eliminado do qualifying que avança quando um main draw player desiste.
- Alternates: lista de jogadores no ranking imediatamente abaixo do cutoff, ordenados por ranking.

### Codex — N-X4: NPC scheduling realista (BAIXO — não bloqueia outros)

- `calendario.py` em `_selecionar_participantes_para_torneio()`: incluir critério de superfície preferida.
- Cada jogador terá campo `superficie_preferida` (grass/clay/hard) derivado dos atributos:
  - clay se `topspin > 70`, grass se `saque > 70 and voleio > 60`, senão hard.
- Aumentar peso de participação em +15% quando torneio é na superfície preferida.
- Não muda o algoritmo base — só ajusta os pesos existentes.

---

## Features novas — Fase 2: UX completa (Claude — após Fase 1 estável)

### Claude — N-C1: Tela de ranking com best-18 e defesa (ALTO)

- `menu_jogador.py` ou novo `menu_ranking.py`: tela dedicada mostrando:
  - Posição atual e pontos de ranking (best-18 quando N-X1 disponível, senão total)
  - Breakdown dos 10 melhores resultados do ano (usa `historico_torneios`)
  - Pontos a defender nas próximas 4 semanas (filtro em `pontos_detalhados` por `semana_expiracao`)
  - Race to Turin: posição e pontos YTD (usa `pontos_ytd` de N-G2)
- Acessível via opção `[R] 📊 Ver Ranking` no menu do jogador.

### Claude — N-C2: Feed de resultados da semana (MÉDIO)

- `menu_temporada.py` ou função `_exibir_resultados_semana()`:
  - Após avançar semana, mostrar resultados dos torneios NPC simulados.
  - Formato: `"[Torneio] Campeão: {nome} ({pontos} pts)"` — 1 linha por torneio.
  - Mostrar apenas os top 3 torneios mais relevantes (por tipo: GS > 1000 > 500 > 250).
  - Dados disponíveis nos saves NPC temporários (`saves/temp_npc_torneio_*/`).

### Claude — N-C3: Tela financeira (MÉDIO — depende de N-G3)

- `menu_jogador.py`: nova opção `[F] 💰 Finanças`:
  - Saldo atual (`jogador.dinheiro`)
  - Últimas 5 receitas do `historico_financeiro`
  - Total ganho na temporada (YTD)

### Claude — N-C4: Status de entry list antes do torneio (MÉDIO — depende de N-X3)

- `menu_temporada.py`: ao listar torneios da semana, mostrar ao lado do nome:
  - `[DIRETO]` se jogador está no main draw por ranking
  - `[WC]` se entrou por wildcard
  - `[CUTOFF #82]` se o corte foi no rank 82 e jogador está fora
  - `[ALTERNATES]` com posição na fila de espera
- Sem nova tela — info inline na listagem existente.

### Claude — N-C5: Indicador de carreira/idade (BAIXO — depende de N-G4)

- `menu_jogador.py` no cabeçalho: adicionar fase da carreira ao lado da idade:
  - `"Idade: 22 — Ascensão 🚀"` / `"Idade: 27 — Pico 🔥"` / `"Idade: 33 — Veterano 🧓"`
- Labels: `< 21: Promessa`, `21-24: Ascensão`, `25-30: Pico`, `31-34: Veterano`, `35+: Lenda`

---

## Coordenação entre IAs

| Arquivo/Schema | Quem cria | Quem usa depois |
|---------------|-----------|-----------------|
| `historico_torneios` no ranking | Gemini (N-G1) | Codex (N-X1, N-X2), Claude (N-C1) |
| `pontos_ytd` no ranking | Gemini (N-G2) | Claude (N-C1) |
| `historico_financeiro` no jogador | Gemini (N-G3) | Codex (N-X2), Claude (N-C3) |
| `_modificador_idade()` | Gemini (N-G4) | Codex aplica na simulação |
| `pontos_ranking` (best-18) | Codex (N-X1) | Claude (N-C1) |
| `status_entry` no torneio | Codex (N-X3) | Claude (N-C4) |
| `superficie_preferida` no jogador | Codex (N-X4) | Gemini lê em N-X4 (já é Codex, sem conflito) |

---

## Ordem de execução

### Sprint 1 — Fundação (Codex + Gemini em paralelo, sem dependências entre si)

**Gemini:**
1. Bug fixes v2: T12, T13, T14, T15, T16, T17, G1, G2, G3, G4
2. N-G1 (histórico_torneios) — **pré-requisito do Sprint 2**
3. N-G2 (pontos_ytd) — em paralelo com N-G1
4. N-G3 (ledger prize money) — em paralelo

**Codex:**
1. Bug fixes v2: T6, T7, T8, T9, T10, T11, C4, C5, C6, C7, C8, C9
2. N-X2 (prize money distribution) — **depende de N-G3 estar pronto**

### Sprint 2 — Lógica avançada (após Sprint 1)

**Codex:**
- N-X1 (best-18) — **depende de N-G1**
- N-X3 (entry list)
- N-X4 (NPC scheduling)

**Gemini:**
- N-G4 (idade/pico/declínio)

### Sprint 3 — UX completa (Claude — após Sprint 2)

**Claude:**
- N-C1 (tela ranking) — depende de N-X1 + N-G2
- N-C2 (feed de resultados) — independente, pode fazer antes
- N-C3 (finanças) — depende de N-G3
- N-C4 (entry list UX) — depende de N-X3
- N-C5 (indicador carreira) — depende de N-G4

---

## Regras gerais (imutáveis)

- Não criar abstrações para uso único.
- Não renomear em massa.
- Não reformatar arquivos inteiros.
- Não mover arquivos de lugar.
- Não adicionar dependências externas.
- Não criar testes (tarefa separada futura).
- Não mudar assinaturas públicas sem avisar as outras IAs.
- Documentar qualquer mudança de esquema JSON em `docs/saves.md`.
- Claude não toca em domain logic. Codex não toca em ranking.py/save.py. Gemini não toca em interface/.
