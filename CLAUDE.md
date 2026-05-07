# CLAUDE.md

**⚠️ ATENÇÃO CLAUDE: Plano de execução tripartido ativo. Leia `docs/PLANO_EXECUCAO_IAS.md` antes de qualquer trabalho. Seção Claude = C-1 a C-10.**

Guia para Claude Code ao trabalhar neste repositório.

## Visão Geral do Projeto

TennisLegacy é um jogo de simulação de carreira de tênis em modo texto (UI em português) onde o jogador cria um atleta, entra em torneios semanais e progride ao longo de uma temporada ATP/WTA completa de 52 semanas. Suporta circuito masculino (ATP) e feminino (WTA), duplas, Copa Davis, Billie Jean King Cup e gestão de carreira completa.

Ver `codex.md` para referência rápida e `docs/funcionalidades.md` para mapa completo de features e integrações.

## Executando o Jogo

```bash
pip install -r requirements.txt
python main.py
```

Python 3.10+ obrigatório. Sem build step.

## Linting (CI obrigatório)

```bash
black .        # formata automaticamente
flake8 .       # lint check
python3 -m py_compile src/<arquivo>.py   # verifica sintaxe
```

`black --check .` roda no CI a cada push. Executar antes de commitar.

## Arquitetura

Padrão MVC solto:

**Ponto de entrada:** `main.py` → `src/interface/menu_inicial.py` → `src/controller.py`

**Controller (`src/controller.py`)** é o loop principal. Decide com base nos arquivos de save:
- Sem torneio ativo → `menu_principal.py` (hub da semana)
- Torneio ativo → `menu_torneio.py` (partidas e bracket)
- Copa Davis/BJK Cup → `menu_davis.py`

**Camada de domínio (`src/`):**

| Arquivo | Responsabilidade |
|---|---|
| `jogador.py` | Classe `Jogador`: atributos, fadiga, moral, XP, serialização |
| `torneio_core.py` | Motor de torneios: bracket, fases, draw, qualifying (~3685 linhas) |
| `simulacao_partida.py` | Simulação ponto-a-ponto (~1499 linhas) |
| `jogar_partida.py` | Orquestração de partidas: estratégia, momentum, stamina (~1605 linhas) |
| `pontuacao.py` | Distribuição de pontos ATP/WTA/Davis por categoria e fase |
| `ranking.py` | `SistemaRanking`: gerenciamento, ordenação, deduplicação |
| `progressao.py` | XP/level-up, evolução de NPCs, treino (fadiga em `fadiga.py`) |
| `fadiga.py` | Fadiga, lesões, recuperação entre rodadas; re-exportado por `progressao.py` |
| `calendario.py` | Semanas, torneios, recuperação semanal, expiração de pontos |
| `davis_cup.py` | Copa Davis e Billie Jean King Cup |
| `management.py` | Equipe técnica, empresários, gastos semanais (~831 linhas) |
| `patrocinios.py` | PATROCINADORES_DISPONIVEIS/REAIS, pode_assinar_patrocinio(); re-exportado por `management.py` |
| `imprensa.py` | Sistema de entrevistas: perguntas, opções, disparar_entrevista(); re-exportado por `management.py` |
| `duplas.py` | Fusão de duplas, sinergia, convite de parceiros (Hub de Duplas) |
| `match_history.py` | `MatchHistoryManager`: registro otimizado de confrontos globais |
| `tournament_manager.py` | Simulação de torneios NPC semanais (sistema sharded) |
| `gerador_nomes.py` | Geração procedural de nomes NPC por nacionalidade |
| `dados.py` | Path helpers, loaders, sanitização de nomes URL-encoded |
| `save.py` | Serialização/desserialização de saves |
| `json_utils.py` | `salvar_json_seguro()`: backup + tmp + atomic replace |
| `constantes.py` | DEFAULT_ATRIBUTOS, ARCHETYPES, FASES_NOMES |
| `torneio_profile.py` | TOURNAMENT_PROFILES por tipo (GS, 1000, Finals, Standard) |
| `match_dynamics.py` | Momentum, stamina, física dinâmica |
| `simulacao_effects.py` | Efeitos de lesão/doença/ambiente nos atributos |
| `migracoes.py` | Compatibilidade de saves antigos |

**Módulos utilitários e de suporte:**
- `match_constants.py` — Enums: ModoSimulacao, TipoSaque, Estrategia
- `match_config.py` — ConfigPartida (dataclass), criar_config_partida(); re-exportado por `jogar_partida.py`
- `match_ui.py` — UI de partida separada da lógica
- `match_dynamics.py` — Momentum, stamina, física dinâmica
- `simulacao_effects.py` — Efeitos de lesão/doença/ambiente nos atributos
- `entidade_utils.py` — duck typing para jogador/NPC
- `superficie_utils.py` — normalizar_superficie()
- `nome_utils.py` — normalizar_nome()
- `math_utils.py` — clamp()
- `log_jogo.py` — log_simulacao(), log_erro()
- `eventos_exibicao.py` — eventos especiais (convites duplas)
- `world_tour_sync.py` — sincronização de dados globais
- `calendario_participacao.py` — probabilidade de NPC participar

**Camada de interface (`src/interface/`):** Toda a UI. Sem regras de negócio.

| Arquivo | Responsabilidade |
|---|---|
| `menu_inicial.py` | Criar/carregar jogo |
| `menu_principal.py` | Hub semanal: calendário, ranking, mundo, jogador |
| `menu_temporada.py` | Escolha de torneios, modalidades, descanso, treino |
| `menu_torneio.py` | Bracket, partidas, resultados |
| `menu_jogador.py` | Stats, atributos, equipe, patrocínios, email (~1587 linhas) |
| `menu_davis.py` | Copa Davis / Billie Jean King Cup |
| `menu_mundo.py` | Circuito mundial: próximos torneios, estatísticas |
| `menu_progressao.py` | Pontos de skill, snapshots de carreira |
| `match_info.py` | Exibição de informações e estatísticas de partida |

**Dados (`db/`):**

| Arquivo | Conteúdo |
|---|---|
| `ranking_atp.json` | 2000+ jogadores ATP (atributos, pontos, histórico) |
| `ranking_wta.json` | 2000+ jogadoras WTA |
| `calendario.json` | 52 semanas × torneios ATP |
| `calendario_wta.json` | 52 semanas × torneios WTA |
| `nomes.json` | Nomes/sobrenomes por 200+ nacionalidades |
| `nacionalidades.json` | Códigos e nomes de ~200 países |
| `ranking_nacoes_davis.json` | Ranking de nações para Davis Cup |
| `historico.json` | Hall da Fama: campeões por torneio/ano |

**Saves (`saves/<perfil>/`):**
- `jogador.json` — estado completo do jogador (ver `docs/saves.md`)
- `ranking_atp.json` / `ranking_wta.json` — índices "Lean" (leves) dos rankings
- `ranking_atp_duplas.json` / `ranking_wta_duplas.json` — rankings dedicados de duplas
- `jogadores/atp/` / `wta/` — shards JSON com atributos completos de todos os NPCs
- `calendario/atp/` / `wta/` — shards JSON com o estado de cada torneio mundial
- `historico_partidas.json` — registro otimizado de confrontos com IDs únicos
- `temporada.json` — `{ano, semana}` atual
- `torneio_atp.json` / `torneio_wta.json` — estado do torneio ativo (só existe durante torneio)
- `log.txt` — log de eventos de simulação

## Convenções de Código

- Imports absolutos a partir de `src.*` (nunca manipular `sys.path`)
- IO (prints/inputs) separado da lógica de domínio
- Não duplicar regras de negócio entre menus e domínio
- `salvar_json_seguro` de `json_utils.py` para todo JSON persistido
- `salvar_ranking()` é responsabilidade do chamador
- Nomes de variáveis, comentários e strings de UI em português
- Black obrigatório — sem one-liners `if cond: return`

## Bugs Conhecidos

- **Davis Cup:** tie não encerra ao atingir 2 vitórias — sempre simula os 3 jogos
- **Qualifying:** Grand Slam pode ter nomes duplicados se ranking contiver duplicatas
- **Saves antigos:** pontos base inconsistentes se criados antes de fixes recentes

## Arquivos-chave por Tarefa

| Tarefa | Arquivo(s) |
|---|---|
| Lógica de simulação de partida | `src/simulacao_partida.py`, `src/jogar_partida.py` |
| Bracket/fases de torneio | `src/torneio_core.py`, `src/torneio_profile.py` |
| Pontos ATP/WTA por torneio | `src/pontuacao.py`, `src/wta_constants.py` |
| Progressão/XP/lesão/fadiga | `src/progressao.py`, `src/jogador.py` |
| Recuperação semanal (fadiga/lesão) | `src/calendario.py` — `_atualizar_recuperacao_jogador()` |
| Formato de save | `src/save.py`, `src/json_utils.py`, `docs/saves.md` |
| Calendário de torneios | `db/calendario.json`, `src/calendario.py` |
| Menus/UI | `src/interface/` |
| Fluxo de controle | `src/controller.py` |
| Gestão de carreira (equipe/patrocínios) | `src/management.py` |
| Duplas e sinergia | `src/duplas.py` |
| Torneios NPC semanais | `src/tournament_manager.py`, `src/calendario.py` |
| Copa Davis / BJK Cup | `src/davis_cup.py`, `src/interface/menu_davis.py` |
