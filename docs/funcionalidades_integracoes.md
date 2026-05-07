# Funcionalidades do Tennis Legacy e Integrações

Este documento mapeia as funcionalidades do jogo e com o que cada uma se integra (módulos, dados e fluxos).

## 1) Fluxo principal do jogo

| Funcionalidade | Módulo principal | Integrações diretas | Persistência |
|---|---|---|---|
| Entrada do jogo | `main.py` | `src/interface/menu_inicial.py` | - |
| Orquestração de fluxo (hub/torneio/equipes) | `src/controller.py` (`fluxo_principal`) | `menu_principal`, `menu_torneio`, `menu_davis`, `pontuacao`, `calendario` | `saves/<save>/torneio_*.json`, `jogador.json`, `temporada.json` |
| Menu inicial (novo jogo/carregar) | `src/interface/menu_inicial.py` | `src/jogador.py`, `src/dados.py` | criação de pasta de save e arquivos iniciais |
| Menu principal (hub) | `src/interface/menu_principal.py` | `menu_temporada`, `menu_progressao`, `menu_jogador`, `menu_mundo` | leitura de estado do save |

## 2) Temporada e calendário

| Funcionalidade | Módulo principal | Integrações diretas | Persistência |
|---|---|---|---|
| Carregar calendário semanal ATP/WTA | `src/calendario.py` / `src/dados.py` | `db/calendario.json`, `db/calendario_wta.json` | leitura de `db` |
| Menu da temporada (inscrição, descanso, treino) | `src/interface/menu_temporada.py` | `calendario`, `torneio_core`, `duplas`, `ranking`, `save` | `temporada.json`, `jogador.json`, `torneio_*.json` |
| Avançar semana | `src/calendario.py` (`avancar_semana`) | recuperação física, progressão, expiração de pontos, simulação mundial | `temporada.json`, `ranking_*.json`, `jogador.json`, `world_tournaments_*.json` |
| Race/qualificação Finals | `menu_temporada` + `ranking` | `SistemaRanking.ranking_race`, badges de entrada | ranking local do save |
| Exibição de campeões da semana | `src/calendario.py` | `WeekTournamentManager`, calendário oficial, estado simulado | terminal/UI |

## 3) Torneios ATP/WTA (simples/duplas/mistas)

| Funcionalidade | Módulo principal | Integrações diretas | Persistência |
|---|---|---|---|
| Criação de torneio do jogador | `src/torneio_core.py` (`criar_torneio`) | `jogador`, `calendario`, `duplas` | `torneio_atp.json` / `torneio_wta.json` |
| Estado do torneio | `src/torneio_core.py` (`Torneio`) | `src/torneio.py` (forwarder), `dados`, `save` | `saves/<save>/torneio_*.json` |
| Menu do torneio | `src/interface/menu_torneio.py` | `torneio_core`, `match_info`, `menu_mundo`, `save` | salva andamento e resultados |
| Chaves e fases (qualy/main draw/final) | `src/torneio_core.py` | `torneio_entry_config`, `ranking`, `calendario` | `rodadas`, `resultados`, `fase_atual` |
| Simulação NPC de partidas/fases | `src/torneio_core.py` | `jogar_partida.simular_partida_npc`, `ranking` | resultados por fase |
| Duplas (mesmo gênero) | `src/torneio_core.py` + `src/duplas.py` | vínculo de dupla, convites, sinergia, ranking de duplas | `fase_atual_duplas`, `resultados_duplas`, `vinculos_dupla` |
| Duplas mistas (Grand Slam) | `menu_temporada` + `torneio_core` | rankings de gêneros opostos, parceiro convidado | estado de torneio e jogador |
| Desistência (simples/duplas) | `menu_torneio` + `torneio_core` | contabilização de derrota/fase | estado do torneio |

## 4) Competições por equipes

| Funcionalidade | Módulo principal | Integrações diretas | Persistência |
|---|---|---|---|
| Davis Cup e Billie Jean King Cup | `src/davis_cup.py` (`DavisCup`) | `controller`, `menu_davis`, `pontuacao`, `ranking` | `torneio_*.json` com tipo de competição |
| Menu da competição por equipes | `src/interface/menu_davis.py` | `DavisCup`, `match_info`, `save` | lê/salva estado da competição |
| Convocação e seleção nacional | `davis_cup.py` | ranking por nacionalidade, gerador de nomes | estado da competição |
| Ties (simples + duplas) | `davis_cup.py` | `jogar_partida`, configuração de superfície/sede | resultados de confrontos |
| Pontuação por equipes | `src/pontuacao.py` (`distribuir_pontos_davis`) | ranking de jogadores, bônus por fase/título | `ranking_*.json` do save |
| United Cup | calendário + sync mundial | `world_tour_sync`, `calendario` | atualmente simulado no mundo; modo jogável dedicado ainda não implementado |

## 5) Motor de partida

| Funcionalidade | Módulo principal | Integrações diretas | Persistência |
|---|---|---|---|
| Simulação detalhada de pontos/games/sets | `src/jogar_partida.py` | `simulacao_partida`, `match_dynamics`, `simulacao_effects`, `match_constants` | resultado no estado do torneio |
| Simulação rápida/NPC | `jogar_partida.py` (`simular_partida_npc`) | `ConfigPartida`, atributos e fatores contextuais | resultado resumido |
| UI de partida (placar, menus, estratégias) | `src/match_ui.py` | `io_utils`, escolha de modo/estratégia | terminal/UI |
| Ajuste por superfície/clima/saúde | `jogar_partida.py` + `simulacao_effects.py` | `superficie_utils`, status de lesão/doença | efeito no resultado/fadiga |

## 6) Ranking e pontuação

| Funcionalidade | Módulo principal | Integrações diretas | Persistência |
|---|---|---|---|
| Sistema de ranking | `src/ranking.py` (`SistemaRanking`) | busca por nome normalizado, posição, race | `ranking_atp.json`, `ranking_wta.json` |
| Distribuição de pontos de torneio | `src/pontuacao.py` (`distribuir_pontos_torneio`) | `torneio_core`, `dados`, histórico | ranking + histórico no save |
| Expiração de pontos (52 semanas) | `calendario.py` (`_processar_expiracao_ranking`) | histórico detalhado de pontos por torneio | ranking atualizado semanal |
| Ranking de duplas | `ranking.py` + `pontuacao.py` | `pontos_ranking_duplas` / `pontos_duplas` | ranking local do save |

## 7) Progressão, saúde e carreira

| Funcionalidade | Módulo principal | Integrações diretas | Persistência |
|---|---|---|---|
| XP, nível e evolução natural | `src/progressao.py` | pós-partida, pós-semana, controller | `jogador.json` |
| Fadiga, energia e lesão | `src/fadiga.py` + `calendario.py` | desgaste por partida, recuperação semanal, risco de lesão | `status_lesao`, `energia`, `fadiga` |
| Doenças e recuperação | `calendario.py` | penalidades temporárias em atributos e energia | `status_doenca` |
| Treino semanal por foco | `menu_temporada` + `progressao.py` (`treinar_semana`) | consome semana, modifica atributos | `jogador.json` |
| Envelhecimento anual | `progressao.py` | aplicado na virada de temporada | `jogador.json` |

## 8) Gestão de carreira (staff, patrocínio, mídia)

| Funcionalidade | Módulo principal | Integrações diretas | Persistência |
|---|---|---|---|
| Contratação de equipe técnica | `src/management.py` | treinador/físio/psicólogo, custos semanais | `jogador.equipe` |
| Patrocínios | `src/patrocinios.py` (re-export em `management.py`) | propostas por ranking/seguidores, pagamentos, expiração | `jogador.patrocinios` |
| Empresário | `management.py` | propostas e expiração | `jogador.empresario` |
| Entrevistas e impacto de imagem | `src/imprensa.py` (re-export em `management.py`) | contexto de torneio e resultado | impacto em seguidores/moral/finanças |
| E-mails de carreira/mídia | `management.py` | geração de propostas e convites | `jogador.emails` (quando aplicável) |

## 9) Simulação do circuito mundial (outros torneios)

| Funcionalidade | Módulo principal | Integrações diretas | Persistência |
|---|---|---|---|
| Inicialização de torneios paralelos ATP/WTA | `src/tournament_manager.py` | calendário da semana, ranking do save + global | `world_tournaments_masculino.json` / `world_tournaments_feminino.json` |
| Simulação rodada a rodada | `tournament_manager.py` | `calendario._selecionar_participantes_para_torneio` | fases/resultados/campeões no estado mundial |
| Sincronização por dia no torneio do jogador | `src/world_tour_sync.py` | `menu_torneio`, estado diário | status dos outros torneios durante a semana |
| Visualização do circuito mundial | `src/interface/menu_mundo.py` | `WeekTournamentManager` | leitura dos estados mundiais |

## 10) Persistência, migração e utilitários

| Funcionalidade | Módulo principal | Integrações diretas | Persistência |
|---|---|---|---|
| Salvar jogo e snapshots | `src/save.py` | `jogador`, ranking local, estado de torneio | `saves/<save>/*` |
| Leitura robusta e sanitização de dados | `src/dados.py` | decode de strings URL-encoded, caminhos e loaders | leitura de `db/` e `saves/` |
| Migração de dados legados | `src/migracoes.py` + `management.py` | normalização de patrocínio/equipe/empresário | aplicada ao carregar saves antigos |
| Escrita segura de JSON | `src/json_utils.py` | usado por vários módulos de persistência | evita corrupção parcial |
| Logs de simulação/erro | `src/log_jogo.py` | controller, calendário, pontuação etc. | arquivos de log do save |

## 11) Interface (menus)

| Funcionalidade | Módulo principal | Integrações diretas |
|---|---|---|
| Menu inicial | `src/interface/menu_inicial.py` | criação/carregamento de save |
| Menu principal | `src/interface/menu_principal.py` | temporada, jogador, progressão, mundo |
| Menu temporada | `src/interface/menu_temporada.py` | inscrição em torneios, treino, descanso |
| Menu torneio | `src/interface/menu_torneio.py` | simples/duplas, stats/review, resultados |
| Menu equipes (Davis/BJK) | `src/interface/menu_davis.py` | ties, tabela, resultados |
| Menu circuito mundial | `src/interface/menu_mundo.py` | chaves e resultados de torneios externos |
| Menu jogador/progressão | `src/interface/menu_jogador.py`, `menu_progressao.py` | atributos, carreira, evolução |
| Match info (scouting/review) | `src/interface/match_info.py` | comparação de atributos e tendência de confronto |

## 12) Scripts auxiliares (offline/admin)

| Script | Função | Integração |
|---|---|---|
| `scripts/importar_ranking_atp_duplas.py` | Importa ranking bruto de duplas ATP/WTA para a base | `db/ranking_atp.json`, `db/ranking_wta.json` |
| `scripts/extrair_ranking_html.py` | Extrai ranking de HTML salvo | dados brutos -> docs/db |
| `scripts/parse_ranking_texto.py` | Parse de texto de ranking | normalização de entrada |
| `scripts/gerar_atributos_psicologicos.py` | Geração auxiliar de atributos mentais | base de ranking/save |

---

## Resumo de integração por domínio

- **UI**: `src/interface/*` chama serviços de domínio (`torneio_core`, `davis_cup`, `calendario`, `ranking`, `management`).
- **Domínio de jogo**: `torneio_core`, `davis_cup`, `jogar_partida`, `progressao`, `pontuacao`.
- **Módulos extraídos (compat)**: `imprensa`, `patrocinios`, `fadiga`, `match_config` são consumidos via re-export nos módulos originais.
- **Dados e estado**: `dados.py`, `save.py`, `json_utils.py`, arquivos em `saves/` e `db/`.
- **Simulação do mundo**: `tournament_manager.py` + `world_tour_sync.py`.
- **Carreira**: `management.py` (equipe, patrocínio, empresário, mídia).
