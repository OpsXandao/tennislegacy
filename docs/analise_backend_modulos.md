# Analise Tecnica do Backend por Modulo

Documento produzido a partir de leitura do codigo real, usando [docs/funcionalidades_jogo_mapeamento.md](/home/alexandre-paiva/Documentos/estudos/tennislegacy/docs/funcionalidades_jogo_mapeamento.md) apenas como mapa inicial. Onde houver diferenca entre documentacao e implementacao, o codigo foi tratado como fonte principal.

## Saves e sessao

### Funcionalidades
- criacao, listagem, preview, carga, exclusao e persistencia do save
- sessao global em memoria com jogador, rankings e contexto de partida

### Arquivos principais
- `api/routes/save.py`
- `api/session.py`
- `src/save.py`
- `src/dados.py`
- `src/jogador.py`

### Endpoints
- `GET /api/saves`
- `GET /api/save/{nome}/preview`
- `POST /api/save/criar`
- `POST /api/save/criar-alexandre`
- `POST /api/save/carregar`
- `POST /api/save/salvar`
- `DELETE /api/save/{nome}`
- `GET /api/sessao`
- `GET /api/save/arquetipos`
- `GET /api/save/nacionalidades`

### Fluxo real
- rota:
  `api/routes/save.py` valida entrada, cria/carrega `Jogador`, atualiza sessao e devolve payload resumido.
- servico/regra:
  `set_save_ativo()` popula singleton global; `_rebuild_rankings()` recria objetos `SistemaRanking`; `salvar_jogo()` serializa `jogador.json` e sincroniza ranking local.
- persistencia:
  `saves/<save>/jogador.json`, `saves/<save>/temporada.json`, `saves/<save>/rankings/*.json`, jogadores shard em `saves/<save>/jogadores/{atp|wta}/*.json`.

### Dependencias cruzadas
- `src/ranking.py` para preview, carga e sync de ranking.
- `src.dados.py` centraliza paths e loaders.
- `api.session.py` concentra estado global compartilhado por todas as rotas.

### Testes existentes
- `tests/test_api_shared_unittest.py` cobre helpers compartilhados ligados a carga de contexto.
- Nao encontrei teste dedicado de ciclo completo `criar -> carregar -> salvar -> reabrir`.

### Inconsistencias tecnicas
- `api/session.py` usa singleton global; nao e seguro para multiusuario, multi-save concorrente ou testes paralelos.
- `refresh_session()` retorna cedo se `jogador` e `ranking_atp` ja existem; isso favorece cache stale apos mudancas fora do objeto em memoria.
- `src/save.py` sincroniza apenas um subconjunto dos campos do jogador para o ranking; divergencias entre `jogador.json` e ranking lean podem sobreviver.

### Codigo morto / rotas sem uso / integracao parcial
- `GET /api/sessao` existe, mas o front usa pouco como fonte de verdade.
- `salvar_estado_atual_torneio()` e `atualizar_estado_jogador()` em `src/save.py` parecem legado parcial; o fluxo atual de torneio usa `torneio_core`/instancias.

### Risco de regressao
- alto
- motivo:
  quase todo backend depende do singleton de sessao e dos JSONs do save; qualquer ajuste em serializacao ou refresh afeta ranking, jogador, torneio e partida.

### Veredito
- parcial

## Jogador e carreira

### Funcionalidades
- resumo do jogador
- atributos, carreira, historico, financeiro, equipe e patrocinio

### Arquivos principais
- `api/routes/jogador.py`
- `src/jogador.py`
- `src/management.py`
- `src/patrocinios.py`

### Endpoints
- `GET /api/jogador`
- `GET /api/jogador/financeiro`
- `GET /api/jogador/historico-partidas`
- `GET /api/jogador/ranking-detalhado`
- `GET /api/jogador/carreira`
- `GET /api/jogador/atributos`
- `GET /api/jogador/equipe`
- `GET /api/jogador/patrocinios`

### Fluxo real
- rota:
  `api/routes/jogador.py` usa `refresh_session()` e le diretamente `session.jogador`.
- servico/regra:
  composicao de payload e feita na rota; ranking detalhado reconstrui `SistemaRanking` de duplas sob demanda e mistura historico de ranking com estado do jogador.
- persistencia:
  principal em `jogador.json`; equipe e patrocinio sao reidratados de campos do proprio jogador.

### Dependencias cruzadas
- `src.management` e `src.patrocinios` para migracao/serializacao.
- `src.ranking` para posicao e historico de resultados.
- `api/routes/_shared.py` para temporada atual.

### Testes existentes
- `tests/test_gestao_unittest.py` cobre migracao/comportamento de equipe.
- `tests/test_regras_negocio_unittest.py` cobre partes de regra de negocio geral.
- Nao encontrei cobertura direta das rotas de `jogador.py`.

### Inconsistencias tecnicas
- Regra de negocio concentrada nas rotas; serializacao e derivacoes de carreira/financeiro nao estao encapsuladas em um servico unico.
- `GET /api/jogador/patrocinios` existe, mas o fluxo principal de patrocinio passa por email, criando duas formas de acesso ao mesmo dominio.

### Codigo morto / rotas sem uso / integracao parcial
- `GET /api/jogador/patrocinios` esta exposto e mapeado no client, mas sem uso de tela claro no front atual.

### Risco de regressao
- medio
- motivo:
  o modulo e simples na API, mas depende de dados reidratados com muitos campos opcionais e migracoes de save.

### Veredito
- parcial

## Ranking

### Funcionalidades
- rankings ATP/WTA simples
- rankings de duplas
- ranking de nacoes Davis

### Arquivos principais
- `api/routes/ranking.py`
- `src/ranking.py`
- `src/pontuacao.py`
- `src/dados.py`

### Endpoints
- `GET /api/ranking/atp`
- `GET /api/ranking/wta`
- `GET /api/ranking/duplas/{tour}`
- `GET /api/ranking/nacoes/davis`
- `GET /api/ranking/nacoes`

### Fluxo real
- rota:
  `api/routes/ranking.py` le `SistemaRanking` da sessao para simples/duplas e ordena antes de responder.
- servico/regra:
  `SistemaRanking` normaliza entradas, remove bots invalidos, recalcula pontos de ranking e pode regenerar base minima.
- persistencia:
  indices lean em `saves/<save>/rankings/*.json`; detalhes shard por jogador em `saves/<save>/jogadores/...`; ranking de nacoes em `db/ranking_nacoes_davis.json`.

### Dependencias cruzadas
- `src.save.py` atualiza ranking humano ao salvar.
- `src.torneio_core.py` e `src.davis_cup.py` adicionam pontos e historico.
- `src.dados.py` resolve templates globais e saves.

### Testes existentes
- `tests/test_regras_negocio_unittest.py`
- `tests/test_torneio_genero_unittest.py`
- `tests/test_davis_genero_unittest.py`
- cobertura indireta via torneio/duplas; nao encontrei suite dedicada ao ciclo completo de integridade do ranking.

### Inconsistencias tecnicas
- `SistemaRanking.__init__()` muta e salva o ranking durante carga se achar base curta ou inconsistente.
- Auto-healing inclui geracao de newgens e merge com global; isso mascara corrupcao e dificulta diferenciar erro de dados de comportamento legitimo.
- `GET /api/ranking/nacoes` e alias legacy com formato diferente de `GET /api/ranking/nacoes/davis`.

### Codigo morto / rotas sem uso / integracao parcial
- `GET /api/ranking/nacoes` nao aparece no front atual; parece endpoint de compatibilidade.

### Risco de regressao
- alto
- motivo:
  ranking e usado por jogador, torneio, duplas, Davis, mundo e save; a carga com side effects aumenta o risco de regressao silenciosa.

### Veredito
- parcial

## Calendario e fluxo semanal

### Funcionalidades
- consulta de semana
- consulta da semana atual
- avanco semanal com simulacao do mundo

### Arquivos principais
- `api/routes/calendario.py`
- `src/calendario.py`
- `src/world_tour_sync.py`
- `src/torneio_core.py`

### Endpoints
- `GET /api/calendario/semana/{numero}`
- `GET /api/calendario/atual`
- `POST /api/calendario/avancar`

### Fluxo real
- rota:
  `api/routes/calendario.py` resolve contexto do jogador e delega para `src.calendario`.
- servico/regra:
  `avancar_semana(nome_save)` concentra expiracao de pontos, recuperacao, simulacao de torneios e progresso de temporada.
- persistencia:
  `temporada.json`, estado de torneio do save e possiveis shards de torneios NPC/semana.

### Dependencias cruzadas
- `src.torneio_core` para estados ativos.
- `src.world_tour_sync` para torneios NPC embarcados.
- `src.fadiga` e `src.progressao` participam do efeito semanal.

### Testes existentes
- `tests/test_torneio_api_state_unittest.py`
- `tests/test_torneio_npc_unittest.py`
- cobertura indireta de semana/torneio; nao vi teste end-to-end dedicado ao `POST /api/calendario/avancar`.

### Inconsistencias tecnicas
- `POST /api/calendario/avancar` encapsula varias responsabilidades em um unico salto; quando falha, a API devolve erro generico.
- O payload de campeoes/eventos depende de bastante logica interna nao versionada.

### Codigo morto / rotas sem uso / integracao parcial
- nao identifiquei rota sem uso claro no front.

### Risco de regressao
- alto
- motivo:
  avancar semana atravessa ranking, torneio, fadiga, equipe, patrocinio e mundo; e o maior ponto de acoplamento do backend.

### Veredito
- parcial

## Torneios

### Funcionalidades
- checagem de convocacao
- criacao/entrada em torneio
- leitura de estado
- avance de fase
- desistir
- historico de pontos a defender

### Arquivos principais
- `api/routes/torneio.py`
- `src/torneio_core.py`
- `src/tournament_manager.py`
- `src/dados.py`
- `src/pontuacao.py`

### Endpoints
- `GET /api/torneio/checar-convocacao`
- `POST /api/torneio/criar`
- `GET /api/torneio/historico`
- `GET /api/torneio/estado`
- `POST /api/torneio/avancar-fase`
- `POST /api/torneio/desistir`

### Fluxo real
- rota:
  `api/routes/torneio.py` resolve torneio da semana, define modalidade/parceiro, e cria instancia via `criar_torneio()` ou fluxo especial de Davis.
- servico/regra:
  `src/torneio_core.py` monta draw, persiste estado, simula NPCs e processa resultado do jogador.
- persistencia:
  `torneio_atp.json` ou `torneio_wta.json` no save; torneios externos/semana podem ser shardados por `WeekTournamentManager`.

### Dependencias cruzadas
- `src.duplas.py` para parceiro e regras de duplas.
- `src.ranking.py` para seeds, posicao e pontuacao.
- `src.davis_cup.py` para competicoes por selecao.
- `src.world_tour_sync.py` para sincronizacao do resto do circuito.

### Testes existentes
- `tests/test_torneio_api_state_unittest.py`
- `tests/test_torneio_genero_unittest.py`
- `tests/test_torneio_npc_unittest.py`
- `tests/test_tournament_manager_unittest.py`

### Inconsistencias tecnicas
- `api/routes/torneio.py` contem logica de negocio relevante na propria rota, principalmente selecao de torneio e tratamento de Davis.
- Existe bifurcacao grande entre fluxo de torneio comum e Davis.
- O estado do torneio depende de muitos campos livres em JSON; faltam contratos tipados.

### Codigo morto / rotas sem uso / integracao parcial
- `GET /api/torneio/historico` esta exposto, mapeado no doc e sem uso claro no frontend atual.

### Risco de regressao
- alto
- motivo:
  torneio cruza ranking, calendario, duplas, partida e mundo. Pequenas mudancas em serializacao de estado quebram varias telas.

### Veredito
- parcial

## Partidas

### Funcionalidades
- preview de adversario
- recuperacao de partida ativa
- inicio, ponto a ponto, estrategia, simulacao de set/partida e W.O.
- persistencia de runtime e snapshot

### Arquivos principais
- `api/routes/partida.py`
- `api/routes/_match_runtime.py`
- `api/routes/_match_store.py`
- `api/ws/partida.py`
- `src/simulacao_partida.py`
- `src/match_dynamics.py`
- `src/jogar_partida.py`

### Endpoints
- `GET /api/partida/ativa`
- `GET /api/partida/preview`
- `POST /api/partida/iniciar`
- `POST /api/partida/desistir`
- `POST /api/partida/ponto`
- `POST /api/partida/estrategia`
- `POST /api/partida/simular-set`
- `POST /api/partida/simular-partida`
- `WS /ws/partida/{partida_id}`

### Fluxo real
- rota:
  `api/routes/partida.py` descobre confronto pendente a partir do torneio ativo e cria/reusa runtime.
- servico/regra:
  `_match_runtime` monta `MatchRuntime`, aplica motor de ponto a ponto e persiste snapshots em disco.
- persistencia:
  snapshots em `saves/<save>/snapshots/*.json`; conclusao da partida retroalimenta estado do torneio e historico do jogador.

### Dependencias cruzadas
- `api/routes/_shared.py` para contexto e confronto do jogador.
- `src.torneio_core.py` e `src.davis_cup.py` para origem/destino do confronto.
- `src.match_dynamics.py` e `src.simulacao_partida.py` para regras de jogo.

### Testes existentes
- `tests/test_api_partida_unittest.py`
- `tests/test_match_dynamics_unittest.py`
- `tests/test_mecanica_partida_unittest.py`
- `tests/test_simulacao_effects_unittest.py`

### Inconsistencias tecnicas
- `GET /api/partida/ativa` procura snapshots no disco e tenta casar com cache em memoria; apos restart, o snapshot pode existir sem runtime valido correspondente.
- Estrategia suporta dois formatos, inclusive um adaptador `FM` que mapeia para planos antigos; isso e compatibilidade remendada, nao modelo tatico unificado.
- O WebSocket existe, mas o fluxo principal continua centrado em HTTP.

### Codigo morto / rotas sem uso / integracao parcial
- `api/ws/partida.py` e helper de WebSocket existem, mas o uso dominante no front parece parcial.

### Risco de regressao
- alto
- motivo:
  partida depende do torneio ativo, do runtime em memoria e de snapshots em disco; e a area com maior chance de bug silencioso apos restart ou mudanca de estado.

### Veredito
- parcial

## Duplas

### Funcionalidades
- sugestao de parceiros
- busca por nome/nacionalidade
- convite
- integracao com inscricao em torneio e ranking de duplas

### Arquivos principais
- `api/routes/duplas.py`
- `src/duplas.py`
- `src/torneio_core.py`
- `src/tournament_manager.py`
- `src/ranking.py`

### Endpoints
- `GET /api/duplas/sugestoes`
- `GET /api/duplas/buscar`
- `POST /api/duplas/convidar`

### Fluxo real
- rota:
  `api/routes/duplas.py` carrega ranking de duplas; se estiver vazio, faz fallback para ranking de simples.
- servico/regra:
  `src.duplas.py` calcula disponibilidade, vinculo e aceite do parceiro.
- persistencia:
  vinculos e parceiro atual ficam no `jogador.json`; torneio de duplas usa o mesmo estado base do torneio.

### Dependencias cruzadas
- `src.ranking.py` para achar NPCs e posicao.
- `src.jogador.normalizar_nome` para match tolerante.
- `api/routes/torneio.py` para efetiva inscricao em duplas.

### Testes existentes
- `tests/test_api_duplas_unittest.py`
- `tests/test_duplas_unittest.py`
- cobertura boa para aceite, busca e regras basicas.

### Inconsistencias tecnicas
- Fallback de ranking de duplas para simples ajuda UX, mas mistura dois dominos; pode sugerir parceiro sem historico real de duplas.
- O convite decide elite rules pela posicao de simples, nao de duplas.

### Codigo morto / rotas sem uso / integracao parcial
- nao identifiquei rota morta; a integracao com torneio esta espalhada entre dois modulos.

### Risco de regressao
- medio
- motivo:
  a area tem testes melhores que outras, mas depende de dados NPC completos e da serializacao de parceiro no jogador.

### Veredito
- parcial

## Davis Cup

### Funcionalidades
- estado da competicao
- proximo confronto
- simulacao da rodada atual
- integracao com a partida do jogador

### Arquivos principais
- `api/routes/davis.py`
- `src/davis_cup.py`
- `api/routes/torneio.py`
- `api/routes/partida.py`

### Endpoints
- `GET /api/davis/estado`
- `GET /api/davis/proximo`
- `POST /api/davis/simular-atual`

### Fluxo real
- rota:
  `api/routes/davis.py` carrega estado do torneio ativo e recria `DavisCup` a partir dele.
- servico/regra:
  `src.davis_cup.py` verifica convocacao, monta selecoes, controla ties e decide quando bloquear simulacao para o usuario jogar.
- persistencia:
  reaproveita `torneio_atp.json` ou `torneio_wta.json` com `tipo` especial de Davis/BJK.

### Dependencias cruzadas
- `src.ranking.py` para convocacao e selecao nacional.
- `api/routes/partida.py` para iniciar a quadra humana.
- `api/routes/ranking.py` para tabela de nacoes.

### Testes existentes
- `tests/test_davis_genero_unittest.py`
- cobertura de genero/caminho; nao encontrei suite extensa de tie completo com simulacao e retomada.

### Inconsistencias tecnicas
- Davis divide armazenamento com o modulo de torneio comum, o que simplifica infraestrutura mas aumenta a complexidade semantica do estado.
- `GET /api/davis/proximo` e redundante com campos adicionados por `GET /api/davis/estado`.

### Codigo morto / rotas sem uso / integracao parcial
- `GET /api/davis/proximo` esta exposto, mas o front atual aparentemente se apoia mais em `estado`.

### Risco de regressao
- medio
- motivo:
  tem fluxo especial bem acoplado a torneio e partida, mas escopo menor que o circuito principal.

### Veredito
- parcial

## Treinamento e progressao

### Funcionalidades
- listagem de treinos
- treino semanal
- descanso
- status de progressao
- alocacao de pontos de skill

### Arquivos principais
- `api/routes/treinamento.py`
- `api/routes/progressao.py`
- `src/progressao.py`
- `src/fadiga.py`
- `src.save.py`

### Endpoints
- `GET /api/treinamento/opcoes`
- `POST /api/treinamento/executar`
- `POST /api/treinamento/descanso`
- `GET /api/progressao/status`
- `POST /api/progressao/alocar`

### Fluxo real
- rota:
  `treinamento.py` atua direto sobre `session.jogador`; `progressao.py` modifica atributos e salva.
- servico/regra:
  `treinar_semana()` e rotinas de fadiga/lesao definem custo e ganho; `descanso` ainda faz ajuste direto de energia/fadiga antes de `avancar_semana()`.
- persistencia:
  `salvar_jogo()` grava `jogador.json` e sincroniza ranking.

### Dependencias cruzadas
- `src.fadiga.py` para lesao/recuperacao.
- `src.calendario.py` porque `descanso` avanca a semana.
- `src.save.py` para persistencia.

### Testes existentes
- `tests/test_progressao_eventos_unittest.py`
- `tests/test_regras_negocio_unittest.py`

### Inconsistencias tecnicas
- `POST /api/treinamento/descanso` mistura recuperacao local manual com `avancar_semana()`, o que pode duplicar ou conflitar com outras regras semanais.
- Parte da API ainda importa ou reexporta funcoes historicamente movidas entre `progressao.py` e `fadiga.py`, sinal de fronteira de modulo instavel.

### Codigo morto / rotas sem uso / integracao parcial
- nao identifiquei rota morta; o acoplamento entre treino, descanso e semana segue alto.

### Risco de regressao
- medio
- motivo:
  qualquer ajuste em fadiga/lesao ou progressao impacta treino, torneio e partidas, mas o escopo e mais local que ranking/calendario.

### Veredito
- parcial

## Mercado e equipe

### Funcionalidades
- listagem de profissionais
- contratacao
- demissao

### Arquivos principais
- `api/routes/mercado.py`
- `src/management.py`
- `api/routes/jogador.py`

### Endpoints
- `GET /api/mercado/profissionais`
- `POST /api/mercado/contratar`
- `POST /api/mercado/demitir`

### Fluxo real
- rota:
  `api/routes/mercado.py` consulta catalogos em memoria e grava alteracoes direto no jogador da sessao.
- servico/regra:
  `src.management.py` define disponibilidade, limite de equipe e bonus.
- persistencia:
  contratos ficam em `jogador.json`.

### Dependencias cruzadas
- `api/routes/jogador.py` serializa equipe atual.
- `src.save.py` persistencia e sync de ranking.

### Testes existentes
- `tests/test_gestao_unittest.py`

### Inconsistencias tecnicas
- `GET /api/mercado/profissionais` e praticamente um dump de catalogo; custo, lock ou rotacao de mercado nao estao modelados na rota.
- Contratacao de empresario substitui diretamente o atual, sem fluxo de confirmacao ou custo de rescisao.

### Codigo morto / rotas sem uso / integracao parcial
- nao identifiquei codigo morto relevante.

### Risco de regressao
- baixo
- motivo:
  modulo pequeno e bem isolado, com impacto mais comportamental do que estrutural.

### Veredito
- ok

## Email

### Funcionalidades
- inbox
- aceitar, recusar e deletar emails/propostas

### Arquivos principais
- `api/routes/email.py`
- `src.patrocinios.py`
- `src.save.py`

### Endpoints
- `GET /api/email/inbox`
- `POST /api/email/acao`

### Fluxo real
- rota:
  `api/routes/email.py` le `caixa_email` do jogador e processa a acao selecionada.
- servico/regra:
  aceitacao delega para `processar_acao_email_carreira()`.
- persistencia:
  estado da caixa de email e patrocinio fica no `jogador.json`.

### Dependencias cruzadas
- `src.patrocinios.py` para propostas e contratos.
- `api/routes/jogador.py` para leitura de patrocinio/equipe.

### Testes existentes
- nao encontrei suite dedicada para `email.py`.

### Inconsistencias tecnicas
- `GET /api/email/inbox` tem side effect: marca todos como lidos e salva o jogo.
- a mesma caixa mistura notificacoes e contratos acionaveis sem contrato tipado de payload.

### Codigo morto / rotas sem uso / integracao parcial
- nenhuma rota morta clara; o fluxo esta ligado ao front.

### Risco de regressao
- medio
- motivo:
  side effect em GET e alta dependência de formato flexivel do email aumentam risco de comportamento inesperado.

### Veredito
- parcial

## Mundo

### Funcionalidades
- proximos torneios
- noticias
- detalhe de torneio externo
- ao vivo
- race to finals
- bracket externo

### Arquivos principais
- `api/routes/mundo.py`
- `src/world_tour_sync.py`
- `src/tournament_manager.py`
- `src.calendario.py`

### Endpoints
- `GET /api/mundo/proximos`
- `GET /api/mundo/noticias`
- `GET /api/mundo/torneio/{nome}`
- `GET /api/mundo/ao-vivo`
- `GET /api/mundo/race-to-finals`
- `GET /api/mundo/bracket`

### Fluxo real
- rota:
  `api/routes/mundo.py` combina temporada atual, calendarios e `WeekTournamentManager`.
- servico/regra:
  noticias sao majoritariamente heuristicas e texto derivado do save; brackets e ao vivo leem estado de torneios NPC semanais.
- persistencia:
  depende dos shards/estados gerados pelos torneios semanais e do ranking do save.

### Dependencias cruzadas
- `src.tournament_manager.py` e `src.world_tour_sync.py`.
- `src.ranking.py` para race e manchetes.
- `api/routes.calendario._formatar_torneio` reutilizado na rota.

### Testes existentes
- nao encontrei suite dedicada ao modulo `mundo.py`.

### Inconsistencias tecnicas
- noticias usam texto procedural e estado derivado; baixo risco funcional, mas alto risco de divergencia narrativa em saves incompletos.
- reutilizacao de helper privado `_formatar_torneio` de outro modulo indica acoplamento entre rotas.

### Codigo morto / rotas sem uso / integracao parcial
- nao identifiquei endpoint morto; todos aparecem no mapeamento do front.

### Risco de regressao
- medio
- motivo:
  depende muito do estado semanal externo, mas falhas tendem a afetar leitura do mundo mais do que o core do jogo.

### Veredito
- parcial

## Historico e legado

### Funcionalidades
- recordes/GOAT
- campeoes por ano

### Arquivos principais
- `api/routes/historico.py`
- `src/dados.py`
- `src.match_history.py`
- `src.imprensa.py`

### Endpoints
- `GET /api/historico/goat`
- `GET /api/historico/campeoes`

### Fluxo real
- rota:
  `api/routes/historico.py` carrega historico do save e devolve recortes quase sem processamento.
- servico/regra:
  leitura de `historico.json` via `src.dados.py`.
- persistencia:
  `saves/<save>/historico.json`, com fallback para `db/historico.json`.

### Dependencias cruzadas
- `src.match_history.py` participa do historico de partidas do jogador, mas nao alimenta diretamente estas rotas.

### Testes existentes
- nao encontrei suite dedicada para `historico.py`.

### Inconsistencias tecnicas
- `GET /api/historico/goat` retorna chave `" GoatPoints"` com espaco inicial; isso parece typo/compatibilidade acidental.
- calculo de GOAT points esta explicitamente pendente.

### Codigo morto / rotas sem uso / integracao parcial
- nenhuma rota morta clara; o modulo e simples, mas parcial por design.

### Risco de regressao
- baixo
- motivo:
  leitura quase passiva de JSON; principal risco e quebra de contrato de resposta.

### Veredito
- parcial

## Logs e observabilidade

### Funcionalidades
- ingestao de erros do frontend

### Arquivos principais
- `api/routes/logs.py`
- `api/logging_utils.py`
- `Front/src/utils/reportError.ts`

### Endpoints
- `POST /api/logs/frontend`

### Fluxo real
- rota:
  `api/routes/logs.py` valida payload e delega para `log_event()`.
- servico/regra:
  agrega contexto da sessao atual quando disponivel.
- persistencia:
  via sistema de logs; nao ha API de consulta.

### Dependencias cruzadas
- `api.session.get_save_ativo()` para associar save.

### Testes existentes
- `tests/test_api_logging_unittest.py`

### Inconsistencias tecnicas
- modulo e unilateral: ingere log, mas nao oferece observabilidade operacional no proprio backend.

### Codigo morto / rotas sem uso / integracao parcial
- integracao parcial por natureza; serve mais para suporte do front que para gameplay.

### Risco de regressao
- baixo
- motivo:
  modulo isolado, efeito colateral restrito a logging.

### Veredito
- ok

## Achados transversais

### Dependencias estruturais fortes
- `api/session.py` e o principal ponto de acoplamento do backend.
- `src/dados.py` concentra toda resolucao de path e boa parte do contrato implícito de persistencia.
- `src/ranking.py` tem side effects de carga que afetam todo o jogo.
- `avancar_semana()` e o maior agregador de regras de negocio cross-modulo.

### Divergencias relevantes entre doc e codigo
- o mapeamento funcional esta majoritariamente correto, mas omite alguns riscos importantes:
  - `GET /api/email/inbox` altera estado e salva.
  - `GET /api/historico/goat` tem campo com typo no contrato.
  - `GET /api/ranking/nacoes` e `GET /api/davis/proximo` sao endpoints legacy/redundantes mais do que funcionalidades centrais.
  - o WebSocket de partida existe, mas o uso no front segue parcial.

### Endpoints expostos sem uso ou com uso fraco aparente
- `GET /api/jogador/patrocinios`
- `GET /api/torneio/historico`
- `GET /api/ranking/nacoes`
- `GET /api/davis/proximo`

### Maiores riscos de regressao
1. sessao global stale ou inconsistente entre memoria e disco
2. ranking com auto-healing alterando dados durante carga
3. avancar semana misturando muitos dominios em uma unica operacao
4. runtime de partida dependente de cache + snapshot apos restart
5. estados de torneio e Davis compartilhando o mesmo arquivo base

### Prioridade sugerida de auditoria/correcao
1. `api/session.py` e fluxos de refresh/persistencia
2. `src/ranking.py` e invariantes de carga/salvamento
3. `src.calendario.py` e `src/torneio_core.py`
4. `_match_runtime` e retomada de partidas
5. `api/routes/email.py` e demais GETs com side effect
