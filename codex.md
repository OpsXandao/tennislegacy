# Mapeamento de Funcionalidades — TennisLegacy

**⚠️ ATENÇÃO CODEX: Existe uma nova tarefa de web scraping ativa. Leia `docs/divisao_scraping_real.md` para suas instruções.**

Descreve todas as funcionalidades implementadas e suas integrações entre módulos.
Para formato dos saves detalhado, ver `docs/saves.md`.

---

## Atualização de arquitetura (2026-03)

- **Sharding de Dados:** Grande refatoração para performance e escalabilidade:
  - `ranking_atp.json` agora é um índice "Lean". Atributos detalhados ficam em `jogadores/<tour>/<nome>.json`.
  - Calendário mundial fragmentado: torneios NPC ficam em arquivos individuais em `calendario/<tour>/`.
  - Ranking de duplas separado: `ranking_atp_duplas.json` e `ranking_wta_duplas.json`.
  - Histórico de partidas global: `historico_partidas.json` com ID único por confronto.

---

## 1. Gestão do Jogador e Vínculos

**Módulo principal:** `src/jogador.py`, `src/duplas.py`

**O que faz:**
- Classe `Jogador` com estado completo.
- **Sistema de Vínculos de Duplas:** Registro persistente de partidas jogadas com cada parceiro.
  - O campo `vinculos_dupla` rastreia total de jogos e vitórias por parceiro.
  - Vínculos altos geram bônus de sinergia reais no Overall da dupla durante a partida.
- Atributo `duplas` evolui organicamente (+1 a cada 5 partidas).

---

## 2. Motor de Partida e Simulação

**Módulos principais:** `src/jogar_partida.py`, `src/simulacao_partida.py`, `src/match_history.py`

**O que faz:**
- Simulação ponto a ponto (Estrategista, Detalhado, Rápido).
- **Match History Global:** Registro centralizado de todas as partidas em `historico_partidas.json`.
- Sincronização em tempo real: resultados do jogador humano são injetados automaticamente no circuito mundial para evitar inconsistências.

---

## 3. Sistema de Torneios e Duplas

**Módulos principais:** `src/torneio_core.py`, `src/duplas.py`

**O que faz:**
- Geração de chaves (GS 128, 1000 96, etc).
- **Hub de Convites de Duplas:**
  - Busca por Sugestões (parceiros de nível similar).
  - Busca por Ranking (convidar Top 50 de simples ou duplas).
  - Busca por Nacionalidade (encontrar compatriotas).
  - Busca por Nome (qualquer jogador do tour).
- **Suporte a Duplas Mistas:** Disponível em Grand Slams, com troca automática de ranking de gênero para convites.
- **IA de Aceite:** NPCs Top 30 recusam convites menores se não houver vínculo forte ou mesma nacionalidade.

---

## 4. Circuito Mundial e Fragmentação

**Módulo principal:** `src/tournament_manager.py`

**O que faz:**
- Gerencia torneios onde o jogador não participa usando **Fragmentação (Sharding)**.
- Carrega apenas os arquivos JSON dos torneios da semana atual da pasta `calendario/`.
- Salva resultados individualmente, reduzindo risco de corrupção massiva.
- `obter_resumo_semanal()`: Retorna campeões de simples e duplas de todos os torneios ativos.

---

## 5. Sistema de Ranking

**Módulo principal:** `src/ranking.py`

**O que faz:**
- **Lazy Loading:** O `SistemaRanking` carrega o índice leve e busca atributos em arquivos individuais apenas quando necessário.
- **Diferenciação de Modos:** Rankings de simples e duplas são carregados de arquivos distintos para manter a integridade dos dados.
- Ordenação automática por pontos ou Race to Finals (YTD).

---

## Mapa de Dependências (Arquitetura Sharded)

```
controller.py
  ├─ menu_principal.py
  │    └─ ranking.py (Lean Load) ─── jogadores/ (Lazy Load)
  ├─ menu_temporada.py
  │    ├─ duplas.py (Invite System) ─── ranking.py
  │    └─ torneio_core.py ─── match_history.py
  └─ calendario.py
       └─ tournament_manager.py (Shard Load) ─── calendario/ (JSONs individuais)
```
