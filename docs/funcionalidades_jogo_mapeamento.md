# Funcionalidades do Jogo e Mapeamento Front/Backend

## Objetivo
Este documento lista as funcionalidades atuais do jogo, onde elas existem no backend e se ja estao ligadas no frontend.

## Legenda
- `Ligado`: existe backend e ha tela/fluxo consumindo a funcionalidade.
- `Parcial`: existe backend e ha uso no frontend, mas incompleto, indireto ou sem cobertura total.
- `So backend`: endpoint/fluxo existe, mas nao encontrei consumo real no frontend atual.
- `So frontend`: existe tela/comportamento no client sem persistencia/endpoint dedicado.

## Rotas principais do frontend
- `/` -> `Front/src/app/screens/HomeScreen.tsx`
- `/continue` -> `Front/src/app/screens/ContinueScreen.tsx`
- `/hub` -> `Front/src/app/screens/HubScreen.tsx`
- `/calendar` -> `Front/src/app/screens/CalendarScreen.tsx`
- `/tournament` -> `Front/src/app/screens/TournamentBracket.tsx`
- `/match` -> `Front/src/app/screens/MatchScreen.tsx`
- `/player` -> `Front/src/app/screens/PlayerScreen.tsx`
- `/rankings` -> `Front/src/app/screens/RankingsScreen.tsx`
- `/training` -> `Front/src/app/screens/TrainingScreen.tsx`
- `/progression` -> `Front/src/app/screens/ProgressionScreen.tsx`
- `/market` -> `Front/src/app/screens/MarketScreen.tsx`
- `/history` -> `Front/src/app/screens/HistoryScreen.tsx`
- `/world` -> `Front/src/app/screens/WorldScreen.tsx`
- `/davis` -> `Front/src/app/screens/DavisScreen.tsx`
- `/duplas` -> `Front/src/app/screens/DuplasScreen.tsx`
- `/settings` -> `Front/src/app/screens/SettingsScreen.tsx`

## Camada de acesso do frontend
- Cliente HTTP/WebSocket: `Front/src/api/client.ts`
- Estado global: `Front/src/store/gameStore.ts`
- Backend FastAPI principal: `api/main.py`

## 1. Saves, sessao e inicio de carreira

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| Listar saves | `api/routes/save.py` | `GET /api/saves` | `ContinueScreen` | Ligado |
| Preview de save | `api/routes/save.py` | `GET /api/save/{nome}/preview` | `ContinueScreen` | Ligado |
| Criar carreira customizada | `api/routes/save.py` | `POST /api/save/criar` | `HomeScreen` | Ligado |
| Criar preset Alexandre | `api/routes/save.py` | `POST /api/save/criar-alexandre` | `HomeScreen` | Ligado |
| Carregar save | `api/routes/save.py` | `POST /api/save/carregar` | `HomeScreen`, `ContinueScreen`, `MatchScreen` | Ligado |
| Salvar save atual | `api/routes/save.py` | `POST /api/save/salvar` | `HubScreen` | Ligado |
| Sessao ativa | `api/routes/save.py` | `GET /api/sessao` | cliente existe, nao vi uso relevante em tela | Parcial |
| Apagar save | `api/routes/save.py` | `DELETE /api/save/{nome}` | `ContinueScreen` | Ligado |
| Arquetipos e nacionalidades para criacao | `api/routes/save.py` | `GET /api/save/arquetipos`, `GET /api/save/nacionalidades` | `HomeScreen` | Ligado |

Observacoes:
- O estado global do front fica em `gameStore`, mas a verdade do dado continua no backend/save.

## 2. Jogador, perfil e carreira

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| Resumo principal do jogador | `api/routes/jogador.py` | `GET /api/jogador` | `gameStore`, `MatchScreen` pos-jogo | Ligado |
| Atributos e overall | `api/routes/jogador.py` | `GET /api/jogador/atributos` | `PlayerScreen`, `ProgressionScreen` | Ligado |
| Equipe tecnica atual | `api/routes/jogador.py` | `GET /api/jogador/equipe` | `PlayerScreen` | Ligado |
| Financeiro | `api/routes/jogador.py` | `GET /api/jogador/financeiro` | `PlayerScreen` | Ligado |
| Historico de partidas | `api/routes/jogador.py` | `GET /api/jogador/historico-partidas` | `PlayerScreen` | Ligado |
| Ranking detalhado do jogador | `api/routes/jogador.py` | `GET /api/jogador/ranking-detalhado` | `PlayerScreen` | Ligado |
| Dados de carreira | `api/routes/jogador.py` | `GET /api/jogador/carreira` | `PlayerScreen` | Ligado |
| Patrocinios do jogador | `api/routes/jogador.py` | `GET /api/jogador/patrocinios` | cliente exposto, nao vi consumo direto em tela | So backend |

Observacoes:
- `PlayerScreen` concentra varios modulos que antes seriam telas separadas.
- Patrocinio hoje parece aparecer mais por email/acao do que por tela dedicada.

## 3. Ranking e classificacoes

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| Ranking ATP simples | `api/routes/ranking.py` | `GET /api/ranking/atp` | `RankingsScreen` | Ligado |
| Ranking WTA simples | `api/routes/ranking.py` | `GET /api/ranking/wta` | `RankingsScreen` | Ligado |
| Ranking de duplas ATP/WTA | `api/routes/ranking.py` | `GET /api/ranking/duplas/{tour}` | `RankingsScreen`, `DuplasScreen` | Ligado |
| Ranking de nacoes Davis | `api/routes/ranking.py` | `GET /api/ranking/nacoes/davis` | `RankingsScreen` | Ligado |
| Ranking de nacoes geral | `api/routes/ranking.py` | `GET /api/ranking/nacoes` | nao vi uso no front | So backend |

Base principal:
- Regras e carga: `src/ranking.py`
- Seeds/caminhos: `src/dados.py`

## 4. Calendario e fluxo semanal

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| Ver calendario da semana | `api/routes/calendario.py` | `GET /api/calendario/semana/{numero}` | `CalendarScreen` | Ligado |
| Ver semana atual | `api/routes/calendario.py` | `GET /api/calendario/atual` | `CalendarScreen` | Ligado |
| Avancar semana | `api/routes/calendario.py` | `POST /api/calendario/avancar` | `CalendarScreen`, `TournamentBracket`, `MatchScreen` | Ligado |
| Campeoes/resumo da semana | mesmo endpoint acima | payload de `avancar` | `CalendarScreen` modal de campeoes | Ligado |

Base principal:
- `src/calendario.py`
- `src/torneio_core.py`

## 5. Inscricao em torneios e chave

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| Checar convocacao/entrada disponivel | `api/routes/torneio.py` | `GET /api/torneio/checar-convocacao` | `CalendarScreen` | Ligado |
| Criar/entrar em torneio | `api/routes/torneio.py` | `POST /api/torneio/criar` | `CalendarScreen` | Ligado |
| Estado do torneio ativo | `api/routes/torneio.py` | `GET /api/torneio/estado` | `TournamentBracket`, `MatchScreen` | Ligado |
| Avancar fase do torneio | `api/routes/torneio.py` | `POST /api/torneio/avancar-fase` | `TournamentBracket` | Ligado |
| Desistir do torneio | `api/routes/torneio.py` | `POST /api/torneio/desistir` | `TournamentBracket` | Ligado |
| Historico do torneio/pontos a defender | `api/routes/torneio.py` | `GET /api/torneio/historico` | cliente exposto, nao vi uso em tela | So backend |

Base principal:
- `src/torneio_core.py`
- `src/tournament_manager.py`
- `src/pontuacao.py`

## 6. Partidas

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| Preview do adversario | `api/routes/partida.py` | `GET /api/partida/preview` | `MatchScreen` | Ligado |
| Recuperar partida ativa | `api/routes/partida.py` | `GET /api/partida/ativa` | `MatchScreen` | Ligado |
| Iniciar partida | `api/routes/partida.py` | `POST /api/partida/iniciar` | `TournamentBracket`, `DavisScreen`, `MatchScreen` | Ligado |
| Jogar ponto | `api/routes/partida.py` | `POST /api/partida/ponto` | `MatchScreen` | Ligado |
| Mudar estrategia | `api/routes/partida.py` | `POST /api/partida/estrategia` | `MatchScreen` | Ligado |
| Simular set | `api/routes/partida.py` | `POST /api/partida/simular-set` | `MatchScreen` | Ligado |
| Simular partida inteira | `api/routes/partida.py` | `POST /api/partida/simular-partida` | `MatchScreen` | Ligado |
| Desistir/W.O. | `api/routes/partida.py` | `POST /api/partida/desistir` | `MatchScreen` | Ligado |
| WebSocket da partida | `api/ws/partida.py` | `/ws/partida/{partida_id}` | helper em `api/client.ts`, nao vi uso dominante na tela atual | Parcial |

Base principal:
- Runtime e persistencia: `api/routes/_match_runtime.py`
- Motor ponto a ponto: `src/simulacao_partida.py`
- Dinamica de stamina/momentum: `src/match_dynamics.py`
- Config de partida: `src/match_config.py`

Observacoes:
- A tela de partida esta bem ligada ao backend.
- O helper WebSocket existe, mas o fluxo principal ainda parece majoritariamente HTTP/polling/acoes diretas.

## 7. Treinamento, descanso e progressao

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| Listar opcoes de treino | `api/routes/treinamento.py` | `GET /api/treinamento/opcoes` | `TrainingScreen` | Ligado |
| Executar treino | `api/routes/treinamento.py` | `POST /api/treinamento/executar` | `TrainingScreen` | Ligado |
| Descansar/avancar com recuperacao | `api/routes/treinamento.py` | `POST /api/treinamento/descanso` | `TrainingScreen` | Ligado |
| Ver status de progressao | `api/routes/progressao.py` | `GET /api/progressao/status` | `ProgressionScreen` | Ligado |
| Alocar pontos de skill | `api/routes/progressao.py` | `POST /api/progressao/alocar` | `ProgressionScreen` | Ligado |

Base principal:
- `src/progressao.py`
- `src/fadiga.py`

## 8. Mercado e equipe tecnica

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| Listar profissionais | `api/routes/mercado.py` | `GET /api/mercado/profissionais` | `MarketScreen` | Ligado |
| Contratar profissional | `api/routes/mercado.py` | `POST /api/mercado/contratar` | `MarketScreen` | Ligado |
| Demitir profissional | `api/routes/mercado.py` | `POST /api/mercado/demitir` | `MarketScreen` | Ligado |
| Visualizar equipe atual | `api/routes/jogador.py` | `GET /api/jogador/equipe` | `PlayerScreen` | Ligado |

Base principal:
- `src/management.py`

## 9. Emails, convites e decisoes

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| Inbox de emails | `api/routes/email.py` | `GET /api/email/inbox` | `HubScreen`, `PlayerScreen` | Ligado |
| Acoes em email | `api/routes/email.py` | `POST /api/email/acao` | `PlayerScreen` | Ligado |

Observacoes:
- Convites de duplas e propostas de patrocinio aparecem hoje acoplados ao sistema de email.
- `HubScreen` usa inbox para contar nao lidos de forma simplificada.

## 10. Duplas

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| Sugestoes de parceiros | `api/routes/duplas.py` | `GET /api/duplas/sugestoes` | `DuplasScreen` | Ligado |
| Buscar parceiro por nome/nacionalidade | `api/routes/duplas.py` | `GET /api/duplas/buscar` | `DuplasScreen` | Ligado |
| Convidar parceiro | `api/routes/duplas.py` | `POST /api/duplas/convidar` | `DuplasScreen` | Ligado |
| Entrar em torneio de duplas | `api/routes/torneio.py` | `POST /api/torneio/criar` com modalidade/parceiro | `CalendarScreen` modal de inscricao | Ligado |
| Ranking de duplas | `api/routes/ranking.py` | `GET /api/ranking/duplas/{tour}` | `DuplasScreen`, `RankingsScreen` | Ligado |

Base principal:
- `src/duplas.py`
- `src/torneio_core.py`
- `src/tournament_manager.py`

## 11. Davis Cup / competicoes de selecoes

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| Estado do confronto | `api/routes/davis.py` | `GET /api/davis/estado` | `DavisScreen` | Ligado |
| Proximo confronto | `api/routes/davis.py` | `GET /api/davis/proximo` | cliente exposto, nao vi uso em tela | So backend |
| Simular rodada atual | `api/routes/davis.py` | `POST /api/davis/simular-atual` | `DavisScreen` | Ligado |
| Entrar na sua partida da Davis | combinacao Davis + Partida | `POST /api/partida/iniciar` | `DavisScreen` | Ligado |
| Ranking de nacoes | `api/routes/ranking.py` | `GET /api/ranking/nacoes/davis` | `RankingsScreen` | Ligado |

Base principal:
- `src/davis_cup.py`

## 12. Mundo, circuito e observacao externa

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| Proximos torneios do mundo | `api/routes/mundo.py` | `GET /api/mundo/proximos` | `WorldScreen` | Ligado |
| Noticias | `api/routes/mundo.py` | `GET /api/mundo/noticias` | `WorldScreen` | Ligado |
| Detalhe de torneio do mundo | `api/routes/mundo.py` | `GET /api/mundo/torneio/{nome}` | `WorldScreen` modal | Ligado |
| Ao vivo | `api/routes/mundo.py` | `GET /api/mundo/ao-vivo` | `WorldScreen` | Ligado |
| Race to Finals | `api/routes/mundo.py` | `GET /api/mundo/race-to-finals` | `WorldScreen` | Ligado |
| Bracket externo | `api/routes/mundo.py` | `GET /api/mundo/bracket` | `WorldScreen` modal | Ligado |

Base principal:
- `src/world_tour_sync.py`
- `src/torneio_core.py`

## 13. Historico e legado

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| GOAT / recordes / titulos do jogador | `api/routes/historico.py` | `GET /api/historico/goat` | `HistoryScreen`, `PlayerScreen` | Ligado |
| Campeoes historicos | `api/routes/historico.py` | `GET /api/historico/campeoes` | `HistoryScreen` | Ligado |

Base principal:
- `db/historico.json`
- `src/imprensa.py`
- `src/match_history.py`

## 14. Logs e observabilidade

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| Receber logs do frontend | `api/routes/logs.py` | `POST /api/logs/frontend` | `Front/src/utils/reportError.ts` | Parcial |

Observacoes:
- E uma integracao de suporte/observabilidade, nao uma feature jogavel.

## 15. Configuracoes

| Funcionalidade | Backend | API | Front | Status |
|---|---|---|---|---|
| Audio, vibracao, scanlines, tema, dificuldade | nao ha backend dedicado | localStorage/browser | `SettingsScreen` | So frontend |

Observacoes:
- `SettingsScreen` hoje persiste apenas localmente no navegador.
- O proprio texto da tela ja indica que a configuracao backend nao esta exposta.

## 16. Funcionalidades importantes que existem no backend mas nao achei ligadas diretamente

- `GET /api/jogador/patrocinios`
  - Existe em `api/routes/jogador.py`
  - Nao vi uso real no frontend atual.
- `GET /api/ranking/nacoes`
  - Existe no backend
  - Nao vi tela usando.
- `GET /api/torneio/historico`
  - Existe no backend
  - Nao vi consumo no frontend.
- `GET /api/davis/proximo`
  - Cliente exposto, mas nao vi uso direto na tela.

## 17. Telas do frontend que funcionam mais como agregadoras

- `HubScreen`
  - Resume estado do jogador.
  - Usa save manual, inbox e dados do store.
  - Serve como navegacao central.
- `PlayerScreen`
  - Funciona como painel consolidado de atleta:
    - atributos
    - ranking detalhado
    - historico
    - financeiro
    - carreira
    - equipe
    - email
- `WorldScreen`
  - Consolida mundo, proximos torneios, ao vivo, race e bracket externo.

## 18. Motores e modulos centrais do dominio

Se precisar localizar onde a regra realmente vive:

- Saves/jogador: `src/jogador.py`, `src/save.py`
- Ranking: `src/ranking.py`
- Calendario: `src/calendario.py`
- Torneios: `src/torneio_core.py`, `src/tournament_manager.py`
- Duplas: `src/duplas.py`
- Davis Cup: `src/davis_cup.py`
- Partidas: `src/simulacao_partida.py`, `src/match_dynamics.py`, `api/routes/_match_runtime.py`
- Progressao e fadiga: `src/progressao.py`, `src/fadiga.py`
- Mercado/equipe: `src/management.py`
- Mundo/circuito externo: `src/world_tour_sync.py`

## 19. Resumo executivo

### Bem ligados front + backend
- saves
- jogador/perfil
- ranking simples/duplas
- calendario
- torneios
- partidas
- treinamento
- progressao
- mercado
- email
- duplas
- Davis
- mundo
- historico

### Parciais
- sessao ativa
- WebSocket de partida
- logs frontend

### Hoje mais backend que frontend
- patrocinio dedicado
- historico especifico de torneio
- ranking de nacoes fora Davis
- endpoint `davis/proximo`

### So frontend
- configuracoes locais de cliente
