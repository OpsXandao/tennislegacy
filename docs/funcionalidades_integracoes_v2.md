# Funcionalidades e Integrações (V2 - Técnico por Função)

Mapa técnico das funções centrais do projeto e com o que cada uma se integra.

## 1) Bootstrap e Orquestração

### `main.py`
- **Entrada**: execução do jogo.
- **Integra com**: `src/interface/menu_inicial.py`.
- **Saída/efeito**: inicia fluxo de criação/carregamento de save.

### `src/controller.py`

#### `fluxo_principal(jogador_inst, nome_save, salvar_automaticamente=False)`
- **Papel**: orquestrador global do loop do jogo.
- **Integra com**:
  - `menu_principal` (hub)
  - `menu_torneio` (torneio ATP/WTA jogável)
  - `menu_davis` (Davis/BJK)
  - `distribuir_pontos_torneio` / `distribuir_pontos_davis`
  - `calendario.avancar_semana`
  - `torneio_core.carregar_torneio`
- **Dados lidos/escritos**:
  - `saves/<save>/torneio_atp.json` ou `torneio_wta.json`
  - `jogador.json`, `temporada.json`, `ranking_*.json`
- **Observação**: centraliza fechamento de torneio, pontuação e avanço de semana.

#### `_torneio_ativo_do_jogador(estado, jogador_nome)`
- **Papel**: valida se o estado de torneio em disco é realmente do jogador atual.
- **Integra com**: `normalizar_nome`.

#### `_aplicar_progressao_natural_pos_torneio(...)`
- **Papel**: aplica progressão natural acumulada após torneio.
- **Integra com**: `src/progressao.py`.

## 2) Interface (Menus)

### `src/interface/menu_inicial.py`
- **Função principal**: `menu_inicial()`
- **Integra com**:
  - `jogador.criar_jogador`, `jogador.carregar_jogador`
  - `dados.listar_saves`
- **Efeito**: escolhe/abre save e entrega controle ao fluxo principal.

### `src/interface/menu_principal.py`
- **Função principal**: `menu_principal(...)`
- **Integra com**:
  - `menu_temporada`
  - `menu_progressao`
  - `menu_jogador`
  - `menu_mundo`
- **Efeito**: hub de navegação do save.

### `src/interface/menu_temporada.py`

#### `menu_temporada(jogador, nome_save, salvar_automaticamente=False)`
- **Papel**: seleção de torneio, descanso, treino e visualização de calendário.
- **Integra com**:
  - `calendario.obter_torneios_da_semana`
  - `calendario.avancar_semana`
  - `torneio_core.criar_torneio`
  - `davis_cup.criar_torneio_davis`
  - `duplas.buscar_parceiros_disponiveis` / `tentar_convidar_parceiro`
  - `ranking.SistemaRanking` (Race/Finals)
- **Dados**: atualiza `jogador.modalidade_atual`, parceiro de duplas, estado de torneio.

#### `menu_escolha_modalidade(...)`
- **Papel**: define `simples`, `duplas` ou `ambos` e tipo de dupla.
- **Integra com**: `_buscar_parceiro_menu`.

#### `_buscar_parceiro_menu(...)`
- **Papel**: convite de parceiro (mesmo gênero ou mista).
- **Integra com**:
  - ranking do save/global
  - vínculos de dupla do jogador
  - regras de aceite em `duplas.py`

### `src/interface/menu_torneio.py`

#### `menu_torneio(jogador, nome_save, torneio=None, salvar_automaticamente=False)`
- **Papel**: loop de partida durante torneio do jogador.
- **Integra com**:
  - `torneio_core.Torneio` (simples e duplas)
  - `match_info` (stats/review)
  - `world_tour_sync.sincronizar_outros_torneios_com_dia`
  - `menu_mundo`
  - `save.salvar_jogo`
- **Efeito**:
  - joga partida, simula rodadas NPC, desistência, simulação restante do torneio.

#### `_exibir_outros_torneios(estado)`
- **Papel**: mostra andamento ATP/WTA paralelo durante a semana.
- **Integra com**: dados sincronizados de `outros_torneios_semana`.

### `src/interface/menu_davis.py`

#### `menu_davis(...)`
- **Papel**: loop da competição por seleções (Davis/BJK).
- **Integra com**:
  - `davis_cup.DavisCup`
  - `match_info`
  - `save.salvar_jogo`
- **Retorno**:
  - `"saiu"` quando usuário sai manualmente.
  - `"finalizado"` quando competição encerra/eliminação.

### `src/interface/menu_mundo.py`
- **Função principal**: `menu_mundo(jogador, nome_save)`
- **Integra com**: `tournament_manager.WeekTournamentManager`
- **Efeito**: visão de torneios simulados da semana (ATP/WTA).

## 3) Núcleo de Torneio

### `src/torneio_core.py` (`class Torneio`)

#### `criar_torneio(torneio_escolhido, jogador, nome_save, semana)`
- **Papel**: cria estado inicial do torneio jogável do usuário.
- **Integra com**: configuração de draw, qualy, seeds, duplas.

#### `jogar_partida_do_jogador(...)`
- **Papel**: executa partida de simples do humano.
- **Integra com**:
  - `jogar_partida.jogar_partida`
  - progressão/fadiga/lesão
  - atualização de rodada/resultados

#### `jogar_partida_duplas_do_jogador(...)`
- **Papel**: executa partida de dupla do humano/par.
- **Integra com**:
  - `duplas.fundir_dupla`
  - simulação de duplas e avanço de fase

#### `_simular_npcs_na_fase_atual` / `_simular_npcs_duplas_na_fase`
- **Papel**: fecha jogos NPC da fase corrente.
- **Integra com**: `simular_partida_npc`.

#### `_atualizar_fase_atual` / `_atualizar_fase_duplas`
- **Papel**: promove vencedores para próxima fase.

#### `_distribuir_pontos_duplas(...)`
- **Papel**: distribui pontos de duplas ao fim do draw de duplas.
- **Integra com**: `pontuacao`/ranking do save.

#### `simular_torneio_restante(...)` / `simular_duplas_restante()`
- **Papel**: concluir torneio após eliminação do jogador.

#### `desistir_do_torneio()` / `desistir_das_duplas()`
- **Papel**: trata W/O por desistência e ajusta fase/resultados.

#### `salvar_torneio(instancia)` / `carregar_torneio(nome_save)`
- **Papel**: persistência do estado corrente de torneio.

### `src/torneio.py`
- **Papel**: forwarder/compat de API para `torneio_core`.

## 4) Competições por Seleções

### `src/davis_cup.py`

#### `class SelecaoNacional`
- **Papel**: composição da seleção nacional (convocados/reservas).
- **Integra com**: ranking por nacionalidade.

#### `class DavisCup`
- **Principais métodos**:
  - `_carregar_estado` / `_salvar_estado`
  - `obter_proximo_confronto`
  - `obter_info_confronto_atual`
  - `jogar_confronto`
  - `jogador_ainda_ativo`
- **Integra com**:
  - `jogar_partida` para simples
  - simulação de duplas
  - dados de sede/superfície de ties
- **Efeito**: mantém bracket de qualifiers/final8 e resultados do tie.

#### `criar_torneio_davis(...)` / `carregar_davis_cup(...)`
- **Papel**: criação/carregamento da competição por equipes no save.

## 5) Calendário e Semana

### `src/calendario.py`

#### `avancar_semana(nome_save)`
- **Papel**: pipeline semanal.
- **Etapas integradas**:
  - simulação de torneios não jogados (`_simular_torneios_semanais_npc`)
  - avanço de semana/ano
  - expiração de pontos
  - recuperação física/doença
  - progressão e gestão financeira
  - inicialização dos torneios da nova semana

#### `_simular_torneios_semanais_npc(...)`
- **Papel**: simula ATP+WTA em paralelo para semana atual.
- **Integra com**: `WeekTournamentManager`.

#### `_selecionar_participantes_para_torneio(...)`
- **Papel**: seleção probabilística de participantes por ranking/superfície/sede.
- **Integra com**: `calendario_participacao.prob_participacao`.

#### `_processar_expiracao_ranking(...)`
- **Papel**: remove pontos vencidos de janela de 52 semanas.

#### `processar_progressao_semanal`, `processar_seguidores`, `processar_avisos_patrocinio`
- **Papel**: evolução de carreira entre semanas.
- **Integra com**: `management.py` e estado do jogador.

## 6) Ranking e Pontuação

### `src/ranking.py`

#### `class SistemaRanking`
- **Papel**: CRUD e consultas de ranking/race.
- **Integra com**:
  - normalização de nomes
  - leitura/escrita de `ranking_*.json`

### `src/pontuacao.py`

#### `distribuir_pontos_torneio(nome_save, target_save_name=None, genero="masculino")`
- **Papel**: pontua fases do torneio ATP/WTA/GS/Finals.
- **Integra com**:
  - estado do torneio
  - ranking do save
  - histórico de campeões

#### `distribuir_pontos_davis(nome_save, target_save_name=None)`
- **Papel**: pontua desempenho individual/equipe em Davis/BJK.
- **Integra com**: estado da competição por equipes + ranking.

#### `obter_pontos_map(tournament_type, genero)`
- **Papel**: tabela de pontos por categoria/fase.

## 7) Motor de Partida

### `src/jogar_partida.py`

#### `criar_config_partida(info_torneio)` (re-export de `src/match_config.py`)
- **Papel**: constrói configuração (superfície, sets, etc).

#### `jogar_partida(jogador, adversario, ...)`
- **Papel**: simulação completa de partida com UI/estratégia.
- **Integra com**:
  - `simulacao_partida` (ponto a ponto)
  - `match_dynamics` (momentum/stamina)
  - `simulacao_effects` (lesão/doença/ambiente)
  - `match_ui` (render de menus e placar)

#### `simular_partida_npc(jogador_a, jogador_b, config=None)`
- **Papel**: simulação otimizada para confrontos NPC.

## 8) Progressão e Estado do Jogador

### `src/jogador.py`

#### `class Jogador`
- **Papel**: modelo principal do atleta humano.

#### `criar_jogador`, `criar_jogador_alexandre_paiva`, `carregar_jogador`, `reidratar_jogador`
- **Papel**: ciclo de vida do jogador no save.

#### `adicionar_jogador_ao_ranking`
- **Papel**: garante presença do jogador no ranking local.

### `src/progressao.py`

#### `handle_xp_e_level_up`, `handle_fadiga_e_lesao`, `handle_progressao_natural`
- **Papel**: progressão por partida e evolução natural.
- **Observação**: `handle_fadiga_e_lesao` vem de `src/fadiga.py` via re-export compatível.

#### `treinar_semana(jogador, foco)`
- **Papel**: treino semanal com foco em atributos específicos.

#### `processar_envelhecimento_anual`
- **Papel**: ajuste de atributos por idade/curva de carreira.

## 9) Gestão de Carreira

### `src/management.py`

#### Núcleo financeiro/contratual
- `processar_gastos_equipe`
- `processar_despesas_operacionais`
- `processar_pagamentos_patrocinio` (de `src/patrocinios.py` via re-export)
- `processar_expiracoes_contratos`
- `processar_expiracoes_empresario`

#### Núcleo de oportunidades
- `gerar_propostas_carreira_email`
- `gerar_convites_midia_email`
- `gerar_proposta_patrocinio` (de `src/patrocinios.py` via re-export)
- `gerar_proposta_empresario`
- `processar_acao_email_carreira`

#### Núcleo de mídia/entrevista
- `disparar_entrevista` (de `src/imprensa.py` via re-export)
- `_montar_perguntas_imprensa` (de `src/imprensa.py`)
- `_perfil_entrevista` (de `src/imprensa.py`)

## 10) Simulação Mundial (torneios paralelos)

### `src/tournament_manager.py`

#### `class WeekTournamentManager`
- `inicializar_torneios(lista_torneios_info, jogador_nome=None)`
  - cria draw dos torneios externos da semana.
- `simular_rodada_para_todos(...)`
  - avança fase para todos os torneios ativos.
- `obter_resumo_semanal()`
  - retorna fase/campeão simples/duplas por torneio.
- `obter_torneio(nome_torneio)`
  - devolve estado completo para inspeção no menu mundo.

### `src/world_tour_sync.py`
- **Papel**: sincroniza “outros torneios” por dia de evento durante o torneio do jogador.
- **Integra com**: `menu_torneio` e estado `outros_torneios_semana`.

## 11) Persistência e Infra de dados

### `src/dados.py`
- **Caminhos**:
  - `get_caminho_ranking_save`, `get_caminho_torneio_save`, `get_caminho_temporada`, etc.
- **Loaders**:
  - `carregar_ranking`, `carregar_estado_torneio`, `carregar_calendario`, `carregar_temporada`.
- **Sanitização**:
  - `_sanitizar_nomes_urlencoded` para decodificar `%xx` ao carregar JSON.

### `src/save.py`
- `salvar_jogo`, `atualizar_jogador_no_ranking`, `salvar_estado_atual_torneio`.
- **Integra com**: `jogador`, ranking local e estado de torneio.

### `src/json_utils.py`
- `salvar_json_seguro(...)`: escrita segura (evita corrupção parcial).

### `src/log_jogo.py`
- `log_simulacao`, `log_erro`: rastreamento de execução e falhas.

## 12) Utilitários auxiliares

- `src/duplas.py`: formação/fusão de dupla, regras de convite, busca de parceiros.
- `src/nome_utils.py`: normalização robusta de nomes para matching.
- `src/gerador_nomes.py`: geração de nomes/nacionalidades para NPC.
- `src/simulacao_effects.py`: multiplicadores por lesão/doença/ambiente.
- `src/superficie_utils.py`: normalização de superfície.
- `src/math_utils.py`: utilidades numéricas.

## 13) Scripts administrativos

- `scripts/importar_ranking_atp_duplas.py`: ingestão de ranking de duplas ATP/WTA para base.
- `scripts/extrair_ranking_html.py`: extração de rankings de HTML bruto.
- `scripts/parse_ranking_texto.py`: parser de ranking em texto.
- `scripts/gerar_atributos_psicologicos.py`: apoio para atributos mentais.

---

## Fluxo de integração (resumo)

1. **UI** (`src/interface/*`) chama serviços de domínio.
2. **Domínio** (`torneio_core`, `davis_cup`, `jogar_partida`, `calendario`, `pontuacao`) processa regras.
3. **Persistência** (`dados`, `save`, `json_utils`) grava/recupera estado em `saves/` e `db/`.
4. **Gestão de carreira** (`management`) e **simulação mundial** (`tournament_manager`, `world_tour_sync`) rodam em paralelo ao loop principal.
