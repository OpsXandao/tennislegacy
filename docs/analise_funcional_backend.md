# Análise Funcional do Backend — TennisLegacy

> Base: código real lido em 2026-03-08. Referência inicial: `docs/funcionalidades_jogo_mapeamento.md`.
> Cada módulo foi validado contra o código, não apenas contra o documento.

---

## Sessão (`api/session.py`)

### O que o módulo faz
Gerencia o estado global em memória do processo: jogador ativo, save ativo e quatro objetos de ranking carregados.

### Como funciona hoje
- `_session` é um singleton de processo — um objeto em RAM por worker do uvicorn.
- `set_save_ativo()` carrega o jogador e reconstrói os 4 rankings do disco.
- `refresh_session()` só recarrega se `_session.jogador` ou `_session.ranking_atp` forem `None`.

### Regras de negócio e edge cases
- **Regra:** rankings são carregados uma vez por sessão e reutilizados.
- **Edge case crítico:** `refresh_session()` tem guard `if _session.jogador and _session.ranking_atp: return _session`. Significa que **qualquer escrita em disco (avancar_semana, partida, treino) NÃO é vista pela sessão até o próximo reload explícito**. A sessão é eternamente stale após a primeira carga.
- **Edge case:** uvicorn com múltiplos workers (`--workers N`) faz cada worker ter sessão própria — save ativo em worker 1 não existe no worker 2. Sistema funciona só com `--workers 1` (padrão atual).

### Pronto para frontend?
**Parcial.** Para uso single-worker funciona. O dado do jogador que o frontend recebe pode estar desatualizado se houve escrita após o carregamento.

### Inconsistências ou sinais de fragilidade
- Após `avancar_semana()` (que salva jogador e ranking no disco), a sessão em memória ainda aponta para o estado anterior. O frontend precisa chamar `GET /api/jogador` para ver estado atualizado, mas esse endpoint também usa `refresh_session()` — que não recarrega. Resultado: o frontend pode ver dados defasados por toda a sessão.
- `session.partida_id` e `session.partida_context` existem no código mas **não são usados em nenhum route atual** — sobra de design anterior.

### Lacunas percebidas
- Nenhum endpoint de "invalidar sessão" além de logout/clear.
- Sem TTL de sessão — sessão de uma semana anterior persiste indefinidamente.

### Veredito funcional
**Frágil** — funciona para single-worker, quebra em multi-worker, e nunca atualiza estado pós-escrita.

---

## Saves (`api/routes/save.py`)

### O que o módulo faz
Criar, carregar, salvar, deletar e listar saves. Ponto de entrada da sessão.

### Funcionalidades
- Listar saves disponíveis
- Preview de save (sem carregar sessão)
- Criar carreira customizada
- Criar carreira preset (Alexandre Paiva)
- Carregar save (inicia sessão)
- Salvar save atual
- Deletar save
- Listar arquetipos e nacionalidades

### Como funciona hoje
`criar_save()` → instancia `Jogador` → `_inicializar_arquivos_save()` → `salvar_jogo()` → adiciona ao ranking → `set_save_ativo()`. `carregar_save()` → `carregar_jogador()` → `set_save_ativo()` → `refresh_session()`.

### Regras de negócio e edge cases
- Validação de nome duplicado é case-insensitive (`"Teste"` != `"teste"` em path mas == na validação).
- Arquétipo/mental têm fallback para `"3"`/`"5"` se ID inválido — silencioso.
- `_serializar_jogador()` acessa `jogador_inst.status_lesao["nivel"]` diretamente — **KeyError se `status_lesao` não tiver chave `"nivel"`** (saves antigos ou Jogador recém-criado antes do setdefault).
- `criar_save()` chama `rk.adicionar_jogador_novo(vars(jogador_inst))` — `vars()` em instância de Jogador retorna `__dict__`, que pode conter objetos não-serializáveis (ex: referências circulares).

### Pronto para frontend?
**Sim**, com ressalvas menores.

### Inconsistências ou sinais de fragilidade
- `_serializar_jogador()` retorna `"pontos": j.pontos_ytd` — a label `pontos` dá a impressão de pontos de ranking, mas é YTD. Pode confundir o frontend.
- `GET /sessao` retorna apenas `{"save_ativo": nome}` — mínimo demais. O frontend não sabe se o jogador está carregado sem chamar `GET /api/jogador`.
- `criar_jogador_alexandre_paiva()` não passa por `_inicializar_arquivos_save()` — depende do próprio helper interno fazer isso, sem garantia.

### Lacunas percebidas
- Nenhum endpoint para renomear save.
- Sem validação de integridade ao carregar (jogador.json corrompido → 500 com causa_provavel no log, mas sem recovery automático).

### Veredito funcional
**Sólido** para o fluxo principal. Fragilidades pontuais em edge cases de saves antigos.

---

## Jogador e Carreira (`api/routes/jogador.py`)

### O que o módulo faz
Expõe os dados do atleta: resumo, atributos, financeiro, histórico de partidas, ranking detalhado, dados de carreira, equipe técnica e patrocínios.

### Funcionalidades
- `GET /api/jogador` — resumo completo
- `GET /api/jogador/atributos` — atributos técnicos e psicológicos
- `GET /api/jogador/financeiro` — saldo e últimas 20 transações
- `GET /api/jogador/historico-partidas` — histórico em memória
- `GET /api/jogador/ranking-detalhado` — posição simples/duplas + top 18 resultados do ano
- `GET /api/jogador/carreira` — fase de carreira, nível, XP, títulos
- `GET /api/jogador/equipe` — equipe técnica atual
- `GET /api/jogador/patrocinios` — patrocínios ativos

### Como funciona hoje
Todos os endpoints usam `refresh_session()` e leem de `session.jogador` (in-memory). `get_ranking_detalhado()` cria um `SistemaRanking` novo (lê do disco) a cada chamada — inconsistente com os outros endpoints.

### Regras de negócio e edge cases
- **Fase de carreira** é calculada em runtime por `pico_carreira - idade`. Não é persistida.
- **Títulos** em `get_carreira()` vêm de `jogador_rk.get("trofeus", [])` — o `jogador_rk` é buscado no ranking de sessão (lean). Se lean não tiver `trofeus`, retorna lista vazia mesmo que o jogador tenha ganho torneios.
- **`pontos_detalhados_duplas`** em `_extrair_resultados()` acessa `b.get("ano_origem")` — campo pode estar ausente em pontos antigos.
- **Marketing** — a categoria `marketing` existe na equipe técnica mas `get_equipe()` não a serializa: só mapeia `treinador`, `fisio`, `psicologo`, `empresario`. Membros de marketing são silenciosamente ignorados.

### Pronto para frontend?
**Parcial.** `get_jogador()` e `get_atributos()` são sólidos. `get_carreira()` e `get_historico_partidas()` têm dados potencialmente desatualizados ou incompletos.

### Inconsistências ou sinais de fragilidade
- `get_historico_partidas()` retorna `session.jogador.historico_partidas` — esse campo é do objeto Jogador em memória. O `MatchHistoryManager` grava em `historico_partidas.json` separado. Os dois podem estar dessincronizados.
- `get_ranking_detalhado()` instancia `SistemaRanking` do disco — pode mostrar dados diferentes dos `session.ranking_atp` usados por outros endpoints.
- `" GoatPoints": 0` em `historico.py:26` — chave com espaço na frente (bug de tipagem no JSON).

### Lacunas percebidas
- Nenhum endpoint para atualizar dados do jogador (ex: mudar estratégia padrão, definir objetivos de temporada).
- `GET /api/jogador/patrocinios` existe mas o mapeamento indica "só backend" — o frontend não usa diretamente.

### Veredito funcional
**Parcial** — dados principais OK, edge cases em títulos e histórico.

---

## Ranking (`api/routes/ranking.py`)

### O que o módulo faz
Expõe os rankings ATP, WTA, duplas (ATP/WTA) e nações (Davis Cup).

### Como funciona hoje
Todos os endpoints de ranking (ATP, WTA, duplas) leem de `session.ranking_*` — objetos em memória carregados no login. O endpoint de nações lê de arquivo estático `ranking_nacoes_davis.json`.

### Regras de negócio e edge cases
- **Ranking ATP/WTA** retorna `j.get("pontos", 0)` — mas o lean index armazena `pontos_ranking`, não `pontos`. Para jogadores lean, sempre retorna 0. O campo `pontos` existe apenas no objeto completo (não lean).
- **Ranking duplas** retorna `j.get("pontos_duplas", j.get("pontos", 0))` — fallback correto.
- **Ranking de nações** é lido de arquivo estático — nunca atualizado durante o jogo. Se a Davis Cup ocorrer e pontos forem distribuídos, esse ranking não reflete.
- **Stale data:** como session.ranking nunca é recarregado, após `avancar_semana()` o ranking exibido ainda é o da semana anterior.

### Pronto para frontend?
**Parcial.** Rankings são funcionais mas podem estar stale.

### Inconsistências ou sinais de fragilidade
- `pontos` vs `pontos_ranking` — o lean index tem `pontos_ranking` mas o endpoint retorna `pontos`. Para todos os NPCs lean, o ranking exibido mostra 0 pontos.
- Sem `ordenar(recalculate=True)` nos endpoints — se pontos foram adicionados após o carregamento, a ordem pode estar errada.

### Lacunas percebidas
- Ranking de nações nunca é atualizado pelo jogo — apenas dado estático inicial.
- `GET /api/ranking/nacoes` é alias de `nacoes/davis` — duplicação sem valor.

### Veredito funcional
**Frágil** — dados stale e campo `pontos` provavelmente retorna 0 para todos.

---

## Calendário (`api/routes/calendario.py`)

### O que o módulo faz
Consultar semana/torneios e disparar o avanço semanal.

### Como funciona hoje
`GET /semana/{n}` e `GET /atual` leem o calendário estático (`db/calendario.json`). `POST /avancar` chama `avancar_semana()` — o pipeline completo de 7 etapas em `src/calendario.py`.

### Regras de negócio e edge cases
- `avancar_semana()` recalcula fadiga, processa lesões, expira pontos, simula torneios NPC, avança semana/ano, inicializa novos torneios — pipeline completo.
- O retorno de `POST /avancar` inclui dados da semana nova e eventos, mas a sessão em memória NÃO é atualizada após o retorno.
- Semana 52 → semana 1: envelhecimento anual é processado, YTD resetado.

### Pronto para frontend?
**Sim** para o fluxo principal. A sessão stale pós-avanço é o único risco.

### Inconsistências ou sinais de fragilidade
- Após `POST /avancar`, a sessão em memória ainda tem `session.jogador.semana` da semana anterior. Se o frontend chamar `GET /api/jogador` logo depois, receberá semana antiga.
- Nenhum mecanismo de idempotência: chamar `POST /avancar` duas vezes avança duas semanas.

### Lacunas percebidas
- Sem endpoint `GET /historico-semanas` para ver o que aconteceu nas semanas passadas.

### Veredito funcional
**Sólido** para o fluxo happy path.

---

## Torneios (`api/routes/torneio.py`)

### O que o módulo faz
Inscrição, estado, avanço de fases e desistência de torneios individuais e Davis Cup.

### Funcionalidades
- Checar convocação Davis
- Criar/entrar em torneio
- Ver estado do torneio ativo
- Avançar fase (simular NPCs + promover vencedores)
- Desistir do torneio
- Histórico e pontos a defender

### Como funciona hoje
`POST /criar` detecta Davis Cup e usa path separado (mock). Para torneios regulares, chama `criar_torneio()` do domínio. `POST /avancar-fase` simula NPCs e avança. `POST /desistir` chama apenas `desistir_do_torneio()`.

### Regras de negócio e edge cases
- **`_escolher_torneio()`** seleciona o maior torneio da semana por tipo se não houver nome específico — comportamento automático útil mas pode surpreender.
- **Davis Cup em `POST /criar`:** usa `estado["selecoes"][davis.pais_jogador]` diretamente após `_criar_estado_inicial()` — assume que `selecoes` existe no estado inicial. Se não existir → KeyError silencioso.
- **`desistir_do_torneio()`** não distribui pontos nem avança semana (bug documentado em `audit_backend_gargalos.md`).

### Pronto para frontend?
**Parcial.** Fluxos de criação e avanço de fase sólidos. Desistência incompleta.

### Inconsistências ou sinais de fragilidade
- `POST /desistir` retorna `{"ok": True}` sem dados de semana — o frontend não sabe para onde navegar nem que semana é a nova.
- `POST /criar` para Davis tem comentário explícito de mock: `# Mocking the interactive processar_convocacao for API`. A convocação não chama `processar_convocacao()` real.
- `GET /estado` monta `adversario_info["overall"]` em linha (cálculo inline de overall) — duplicação da lógica de `jogador.calcular_overall()`.

### Lacunas percebidas
- Sem endpoint para simular o restante do torneio após eliminação (isso é chamado implicitamente no fluxo de desistência, mas falta a camada API).
- Sem retorno de pontos ganhos ao avançar fase — o frontend não sabe quantos pontos o jogador conquistou.

### Veredito funcional
**Parcial** — criação e avanço de fase OK, desistência quebrada.

---

## Partidas (`api/routes/partida.py` + `_match_runtime.py`)

### O que o módulo faz
Motor de partida ponto-a-ponto via API. Cria, persiste e avança o estado de uma partida real do jogador.

### Funcionalidades
- Preview do adversário
- Recuperar partida ativa (de snapshot)
- Iniciar partida (cria runtime)
- Jogar ponto
- Mudar estratégia
- Simular set inteiro
- Simular partida inteira
- Desistir/W.O.

### Como funciona hoje
`POST /iniciar` cria `MatchRuntime` com estado completo do placar, adversário e config. O runtime é salvo em memória (cache por `partida_id`) e em snapshot em disco (`saves/<save>/snapshots/<id>.json`). Cada `POST /ponto` avança um ponto, atualiza placar, detecta game/set/partida. Ao encerrar, `_finalizar_torneio()` processa XP, fadiga, registra resultado no bracket.

### Regras de negócio e edge cases
- **`_finalizar_torneio()` é idempotente:** `self.finalizado_torneio` previne dupla execução.
- **Após partida encerrada:** `processar_resultado_partida()` atualiza o bracket. Os pontos ATP/WTA são distribuídos via `POST /api/calendario/avancar` posteriormente — dependência implícita.
- **`POST /desistir` (partida):** marca `encerrado=True`, `vencedor="adversario"`, chama `_finalizar_torneio()`. Não avança semana.
- **Snapshot no disco:** `GET /ativa` varre todos os `.json` em `snapshots/` — potencial lentidão com muitos arquivos.
- **Modo `estrategista`:** FM tactics (Mentalidade|Abordagem|Instrucao) é mapeado para `plano_compat` de 2 opções — detalhe tático reduzido a "agressivo" ou "consistencia".

### Pronto para frontend?
**Sim** para o fluxo de partida em si. A integração pós-partida (avanço de semana) é implícita.

### Inconsistências ou sinais de fragilidade
- `_match_runtime.py` não chama `distribuir_pontos_torneio()` — pontos só entram no ranking quando `avancar_semana()` é chamado. Se o jogador ganhar o torneio e não avançar a semana, os pontos ficam em limbo.
- `GET /ativa` pode carregar um snapshot de uma semana anterior (se não foi limpo). Um snapshot com `encerrado=False` de 2 semanas atrás seria retornado como partida ativa.
- `POST /iniciar` chama `obter_ativa()` e reutiliza partida existente — se o adversário mudou (novo torneio), pode servir dados da partida errada.

### Lacunas percebidas
- Sem limpeza automática de snapshots após encerramento da partida.
- Sem endpoint `DELETE /api/partida/{id}` para invalidar snapshots manualmente.
- Sem feedback de pontos ganhos na resposta do encerramento.

### Veredito funcional
**Sólido** para o loop de jogo. Frágil na integração pós-partida.

---

## Treinamento e Progressão (`api/routes/treinamento.py`, `api/routes/progressao.py`)

### O que o módulo faz
Treinamento semanal com foco em atributos, descanso com recuperação, e alocação de pontos de skill ao subir de nível.

### Funcionalidades
- Listar opções de treino
- Executar treino (técnico, físico, psicológico)
- Descansar com recuperação e avanço de semana
- Ver status de progressão (XP, nível, pontos de skill)
- Alocar ponto de skill em atributo

### Como funciona hoje
`POST /treinamento/descanso` → `avancar_semana()` — correto. `POST /treinamento/executar` → `treinar_semana()` + `salvar_jogo()` — sem avanço de semana (bug). `POST /progressao/alocar` → modifica atributo, decrementa `pontos_de_skill`, salva.

### Regras de negócio e edge cases
- `treinar_semana()` tem sua própria lógica de custo de energia (em `src/progressao.py`) mas o route valida `j.energia < 30` antes — pode haver dupla verificação inconsistente.
- Validação de lesão em `executar` ocorre **após** `treinar_semana()` — o treino é executado mesmo lesionado, só o retorno é diferente.
- `alocar()` chama `j._sanitizar_atributos()` e `j.calcular_overall()` se existirem — defensivo, mas correto.
- **Sem verificação de `pontos_de_skill` duplos:** dois requests simultâneos de `alocar` poderiam usar o mesmo ponto (race condition no singleton de sessão).

### Pronto para frontend?
**Parcial.** Descanso OK. Treino sem avanço de semana.

### Inconsistências ou sinais de fragilidade
- `POST /executar` não avança semana — o jogador pode treinar infinitamente sem a semana avançar.
- Custo de energia do treino (15 unidades na listagem de opções) não corresponde necessariamente ao custo real em `treinar_semana()` — pode haver divergência de UX.
- `POST /descanso` aplica bônus de energia e fadiga no objeto `j` local ANTES de `avancar_semana()`, que também processa recuperação. Pode haver dupla recuperação.

### Lacunas percebidas
- Sem retorno de `semana_nova` em `POST /executar` (quando for corrigido).
- Sem endpoint para ver histórico de treinos da temporada.

### Veredito funcional
**Parcial** — descanso sólido, executar incompleto.

---

## Mercado e Equipe Técnica (`api/routes/mercado.py`)

### O que o módulo faz
Contratar e demitir profissionais (treinador, fisio, psicólogo, marketing, empresário).

### Funcionalidades
- Listar todos os profissionais disponíveis
- Contratar profissional ou empresário
- Demitir profissional ou empresário

### Como funciona hoje
`GET /profissionais` → dicionários estáticos de `management.py`. `POST /contratar` → valida categoria, verifica existente, verifica limite, adiciona contrato com 26 semanas fixas.

### Regras de negócio e edge cases
- Contrato de 26 semanas é hardcoded — toda contratação tem exatamente meia temporada, independente do profissional.
- **Sem verificação de saldo:** jogador pode contratar mesmo sem dinheiro. A dedução ocorre semanalmente via `processar_gastos_equipe()` — o contrato existe mas o saldo pode ficar negativo sem bloqueio.
- **Marketing:** `listar_profissionais()` inclui categoria `marketing`, mas `get_equipe()` em `jogador.py` não serializa membros de marketing. O frontend não vê quem foi contratado de marketing.
- **Limite de equipe** depende do empresário via `obter_max_equipe()` — sem empresário, pode ser 0 ou 1 dependendo da implementação.

### Pronto para frontend?
**Sim** para o fluxo básico. Sem verificação de saldo é risco de produto.

### Inconsistências ou sinais de fragilidade
- Sem verificação de saldo em contratação — UX inconsistente com a realidade financeira do jogador.
- Marketing contratado não aparece em `GET /api/jogador/equipe`.

### Lacunas percebidas
- Sem endpoint de renovação de contrato.
- Sem notificação de contrato expirando (só email gerado por `processar_expiracoes_contratos` durante avanço semanal).

### Veredito funcional
**Sólido** para fluxo básico, com lacunas em saldo e visibilidade de marketing.

---

## Email e Decisões de Carreira (`api/routes/email.py`)

### O que o módulo faz
Inbox de propostas e eventos de carreira (patrocínios, empresários, convites de mídia).

### Funcionalidades
- Listar inbox (e marcar todos como lidos)
- Aceitar/recusar/deletar email

### Como funciona hoje
`GET /inbox` → retorna toda a `caixa_email` do jogador e marca **todos** como lidos imediatamente. `POST /acao` → para "aceitar", chama `processar_acao_email_carreira()` do domínio com o ranking. Para "recusar"/"deletar", apenas remove da caixa.

### Regras de negócio e edge cases
- Marcar como lido é automático ao abrir inbox — sem opção de "preview sem marcar como lido".
- `processar_acao_email_carreira()` retorna `(sucesso, msg)` — se falhar, retorna 400 com a mensagem do domínio.
- "Recusar" e "deletar" têm comportamento idêntico — apenas removem o email.
- **Sem paginação** — se o jogador tem 50+ emails, todos são retornados de uma vez.
- Emails são gerados em `avancar_semana()` por `gerar_propostas_carreira_email()` e `gerar_convites_midia_email()` — o inbox só cresce semana a semana.

### Pronto para frontend?
**Sim** para o fluxo básico.

### Inconsistências ou sinais de fragilidade
- Marcar como lido ao abrir é destrutivo — se o frontend faz polling, o contador `unread_count` retorna 0 na segunda chamada mesmo que o usuário não tenha interagido.
- Sem rastreamento de propostas recusadas — o domínio não sabe que o jogador recusou um patrocínio específico, pode reenviar na próxima semana.

### Lacunas percebidas
- Sem paginação.
- Sem endpoint de "marcar como lido" separado de "listar".

### Veredito funcional
**Sólido** para o fluxo atual, com limitações de UX.

---

## Duplas (`api/routes/duplas.py`)

### O que o módulo faz
Sugestão, busca e convite de parceiros de duplas. A inscrição efetiva em torneio de duplas é feita via `POST /api/torneio/criar`.

### Funcionalidades
- Sugestões de parceiros (top 10 por score)
- Busca por nome ou nacionalidade
- Convidar parceiro

### Como funciona hoje
`GET /sugestoes` → carrega ranking duplas (ou simples como fallback) → `buscar_parceiros_disponiveis()`. `POST /convidar` → busca NPC nos dois rankings → `tentar_convidar_parceiro()` → retorna ok/fail, mas **não persiste o parceiro no jogador**.

### Regras de negócio e edge cases
- O convite é validado por `tentar_convidar_parceiro()` que usa regras de aceitação (ranking relativo, vínculos, tipo de torneio).
- **`POST /convidar` NÃO salva o parceiro no jogador.** O frontend precisa passar o nome do parceiro em `POST /api/torneio/criar`. O convite serve apenas para validação e feedback.
- Busca por nome usa `nome_norm in normalizar_nome(p.get("nome", ""))` — substring match, pode retornar falsos positivos.

### Pronto para frontend?
**Parcial.** O fluxo de convite → criação de torneio exige dois endpoints em sequência e depende do frontend manter o estado do parceiro aceito.

### Inconsistências ou sinais de fragilidade
- Se o jogador convida, recebe `ok: True`, mas não há nada no save indicando que o parceiro foi convidado. Um restart do servidor entre convite e criação de torneio perde a informação.
- `get_equipe()` serializa apenas 4 categorias — marketing nunca aparece (já mencionado).

### Lacunas percebidas
- Sem endpoint para ver o parceiro atual antes de criar o torneio.
- Sem endpoint para cancelar convite aceito antes de criar o torneio.

### Veredito funcional
**Parcial** — convite funcional, mas fluxo completo depende de estado no frontend.

---

## Davis Cup / Competições por Seleções (`api/routes/davis.py`)

### O que o módulo faz
Estado do confronto Davis Cup/BJK Cup, simulação de NPCs e ponto de entrada para partidas da seleção.

### Funcionalidades
- Estado do confronto atual
- Próximo confronto (não usado no frontend)
- Simular rodada atual (NPCs)
- Iniciar partida do jogador (via `POST /api/partida/iniciar`)

### Como funciona hoje
`POST /simular-atual` verifica se é vez do jogador; se não, simula NPCs. `GET /estado` monta o estado completo incluindo `partida_disponivel` e `info_partida`. A partida do jogador usa o runtime padrão de partidas.

### Regras de negócio e edge cases
- `POST /criar` para Davis (em `torneio.py`) é um mock — `processar_convocacao()` real não é chamado.
- `POST /simular-atual` quando NPC vence o tie: retorna `vencedor` e `placar` mas **não distribui pontos Davis** e **não avança semana**.
- Após Davis encerrar, o jogador precisa manualmente avançar a semana via calendário — sem fluxo automático.
- A seleção do jogador é montada simplisticamente em `/criar`: `davis.selecao = davis._normalizar_pais_para_lista(jogador.nacionalidade)`.

### Pronto para frontend?
**Parcial.** Estado e simulação de NPCs funcionam. Criação de convocação e distribuição de pontos são problemas.

### Inconsistências ou sinais de fragilidade
- `_carregar_davis_ativo()` usa `DavisCup(tournament_data=estado.get("tournament_data", {}))` — se `tournament_data` não estiver no estado (saves antigos), instancia com dicionário vazio.
- A convocação via API usa lógica simplificada, não a mesma do CLI. Comportamento pode divergir.

### Lacunas percebidas
- Sem distribuição de pontos ao fim do tie via API.
- `GET /api/davis/proximo` existe mas não é usado pelo frontend.

### Veredito funcional
**Frágil** — funcional para o happy path, mas criação e encerramento são incompletos.

---

## Mundo e Circuito (`api/routes/mundo.py`)

### O que o módulo faz
Visão do circuito mundial: próximos torneios, notícias, ao vivo, race to finals e bracket de torneios externos.

### Funcionalidades
- Próximos torneios (4 semanas)
- Notícias (geradas dinamicamente)
- Detalhe de torneio do mundo
- Ao vivo (estado dos torneios da semana)
- Race to Finals (top 8 YTD)
- Bracket de torneio externo

### Como funciona hoje
`GET /ao-vivo` e `GET /torneio/{nome}` usam `WeekTournamentManager` — leem os shards de torneios NPC em disco. `GET /noticias` gera notícias em runtime com `random.choice()`. `GET /race-to-finals` usa `session.ranking_*` em memória.

### Regras de negócio e edge cases
- **Notícias são não-determinísticas** — chamadas subsequentes retornam resultados diferentes. Sem persistência.
- **Ao vivo antes de `avancar_semana()`:** se os torneios ainda não foram inicializados para a semana, `obter_resumo_semanal()` retorna lista vazia.
- **Race to Finals:** usa `pontos_ytd` — correto conceitualmente, mas `session.ranking_atp` pode estar stale.
- `GET /proximos` iterage 4 semanas com `% 52 + 1` — correto para o wrap de semana 52 → 1.

### Pronto para frontend?
**Parcial.** Bracket e ao vivo dependem de torneios já inicializados. Notícias são decorativas.

### Inconsistências ou sinais de fragilidade
- Notícias aleatórias: qualidade de produto baixa, não refletem o estado real do jogo.
- Race to Finals com ranking stale pode mostrar posições desatualizadas.

### Lacunas percebidas
- Sem cache de notícias — geradas a cada request.
- Sem endpoint para estatísticas da temporada (líderes de aces, campeões por superficie, etc).

### Veredito funcional
**Parcial** — funcional para browsing, débil em contexto de dado real.

---

## Histórico e Legado (`api/routes/historico.py`)

### O que o módulo faz
Recordes mundiais (GOAT) e histórico de campeões por torneio/ano.

### Funcionalidades
- GOAT list com recordes e títulos do jogador
- Campeões históricos por ano/torneio

### Como funciona hoje
Ambos os endpoints leem `carregar_historico(nome_save)` — provavelmente `saves/<save>/historico_partidas.json` ou `db/historico.json`.

### Regras de negócio e edge cases
- `meus_titulos = getattr(j, "trofeus", [])` — `trofeus` está no objeto `Jogador` em memória. Pode estar vazio se o jogador ganhou torneios mas o atributo não foi preenchido.
- `recordes` vem de `hist.get("recordes", {})` — estrutura do histórico não auditada aqui, pode estar vazia.
- **Bug de tipagem:** `" GoatPoints": 0` — chave com espaço inicial na resposta JSON. O frontend precisa usar `" GoatPoints"` (com espaço) para acessar esse campo.

### Pronto para frontend?
**Parcial.** Dados existem, bug de chave prejudica consumo correto.

### Inconsistências ou sinais de fragilidade
- TODO explícito na resposta da API: `" GoatPoints": 0 # TODO: Implementar cálculo`.
- O campo incorreto (`" GoatPoints"` com espaço) vai para o JSON da resposta — o frontend não consegue acessar normalmente.

### Lacunas percebidas
- Sem cálculo real de pontos GOAT.
- Sem histórico pessoal de matches (além do `historico_partidas` já em `jogador.py`).

### Veredito funcional
**Frágil** — funcional para dados básicos, bug de chave e TODO pendente.

---

## Logs e Observabilidade (`api/routes/logs.py`)

### O que o módulo faz
Recebe logs de erros do frontend para centralização no servidor.

### Como funciona hoje
Não lido em detalhe — endpoint de suporte, não gameplay.

### Veredito funcional
**Sólido** para o propósito declarado (observabilidade).

---

## Rankings Consolidados

### Módulos mais sólidos
1. **Calendário** — pipeline de avanço de semana completo e correto
2. **Partidas** — motor ponto-a-ponto funcional e bem estruturado
3. **Saves** — fluxo de criação/carregamento robusto
4. **Mercado** — CRUD simples e funcional
5. **Email** — fluxo de inbox e ações correto

### Módulos mais frágeis
1. **Sessão** — dado stale é problema estrutural que afeta todo o sistema
2. **Ranking** — campo `pontos` provavelmente retorna 0 para todos os NPCs lean
3. **Torneios (desistência)** — bug crítico confirmado
4. **Davis Cup** — convocação mock, sem distribuição de pontos
5. **Histórico** — bug de chave com espaço, TODO explícito

### Maiores lacunas entre backend e experiência esperada

1. **Sessão stale:** o jogador vê dados desatualizados após qualquer ação que escreve no disco — ranking, pontos, semana.
2. **Desistência sem avanço de semana:** bug mais visível para o usuário.
3. **Treino sem avanço de semana:** jogador pode treinar sem a semana passar.
4. **Pontos no ranking:** `pontos` retorna 0 para NPCs lean no endpoint de ranking.
5. **Davis Cup:** convocação e distribuição de pontos incompletas.
6. **Notícias:** completamente não-determinísticas e sem contexto real do jogo.
7. **Pós-partida:** distribuição de pontos ATP/WTA depende de ação explícita do usuário no calendário.

### Priorização de revisão e correção

| # | Módulo | Problema | Prioridade |
|---|---|---|---|
| 1 | Sessão | `refresh_session()` não recarrega após escrita em disco | Alta — afeta todo o sistema |
| 2 | Ranking | Campo `pontos` retorna 0 para NPCs lean | Alta — ranking quebrado visualmente |
| 3 | Torneios | `POST /desistir` sem simular restante/pontos/avanço | Alta — bug reportado |
| 4 | Treinamento | `POST /executar` sem `avancar_semana()` | Alta — semana nunca avança |
| 5 | Histórico | `" GoatPoints"` com espaço na chave | Média — bug de tipagem |
| 6 | Davis | Convocação mock, sem distribuição de pontos | Média — fluxo incompleto |
| 7 | Partidas | Snapshots não limpos após encerramento | Média — risco de partida fantasma |
| 8 | Mercado | Sem verificação de saldo na contratação | Média — UX inconsistente |
| 9 | Email | Marcar como lido ao abrir (sem endpoint separado) | Baixa — limitação de UX |
| 10 | Mundo | Notícias aleatórias e stale ao vivo antes de inicializar torneios | Baixa — qualidade de produto |
