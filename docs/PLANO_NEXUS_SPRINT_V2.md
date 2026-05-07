# NEXUS-SPRINT — TennisLegacy v2
> Branch: `feat/frontend` → `main` | Modo: NEXUS-Sprint (22 agents, 6 fases)
> Atualizado: 2026-03-19 | Orchestrador: Claude (session ativa)
>
> **Objetivo**: Elevar o TennisLegacy de MVP funcional a produto com profundidade
> de carreira, cobertura de testes e polish premium — usando o máximo de agents
> possíveis em paralelo, com gates de qualidade em cada fase.

---

## COMO EXECUTAR

1. Cada IA lê **sua seção** e o arquivo de agent indicado (persona + regras)
2. Executa as tarefas da sua fase atual
3. Atualiza o status `[ ]` → `[x] YYYY-MM-DD` ao concluir
4. Respeita os **contratos de handoff** — não avança para a próxima fase sem gate

```
STATUS: [ ] pendente | [~] em progresso | [x] feito | [!] bloqueado
```

---

## AGENTES ATIVOS NESTE SPRINT

| # | Agent | Divisão | Path do Persona |
|---|-------|---------|-----------------|
| 1 | **Code Reviewer** | Engineering | `~/.claude/agents/engineering/engineering-code-reviewer.md` |
| 2 | **API Tester** | Testing | `~/.claude/agents/testing/testing-api-tester.md` |
| 3 | **Performance Benchmarker** | Testing | `~/.claude/agents/testing/testing-performance-benchmarker.md` |
| 4 | **Evidence Collector** | Testing | `~/.claude/agents/testing/testing-evidence-collector.md` |
| 5 | **Game Designer** | Game Dev | `~/.claude/agents/game-development/game-designer.md` |
| 6 | **Software Architect** | Engineering | `~/.claude/agents/engineering/engineering-software-architect.md` |
| 7 | **Narrative Designer** | Game Dev | `~/.claude/agents/game-development/narrative-designer.md` |
| 8 | **Sprint Prioritizer** | Product | `~/.claude/agents/product/product-sprint-prioritizer.md` |
| 9 | **Senior Project Manager** | PM | `~/.claude/agents/project-management/project-manager-senior.md` |
| 10 | **Backend Architect** | Engineering | `~/.claude/agents/engineering/engineering-backend-architect.md` |
| 11 | **Frontend Developer** | Engineering | `~/.claude/agents/engineering/engineering-frontend-developer.md` |
| 12 | **Database Optimizer** | Engineering | `~/.claude/agents/engineering/engineering-database-optimizer.md` |
| 13 | **DevOps Automator** | Engineering | `~/.claude/agents/engineering/engineering-devops-automator.md` |
| 14 | **AI Engineer** | Engineering | `~/.claude/agents/engineering/engineering-ai-engineer.md` |
| 15 | **UI Designer** | Design | `~/.claude/agents/design/design-ui-designer.md` |
| 16 | **Whimsy Injector** | Design | `~/.claude/agents/design/design-whimsy-injector.md` |
| 17 | **UX Researcher** | Design | `~/.claude/agents/design/design-ux-researcher.md` |
| 18 | **SRE** | Engineering | `~/.claude/agents/engineering/engineering-sre.md` |
| 19 | **Reality Checker** | Testing | `~/.claude/agents/testing/testing-reality-checker.md` |
| 20 | **Technical Writer** | Engineering | `~/.claude/agents/engineering/engineering-technical-writer.md` |
| 21 | **Analytics Reporter** | Support | `~/.claude/agents/support/support-analytics-reporter.md` |
| 22 | **Behavioral Nudge Engine** | Product | `~/.claude/agents/product/product-behavioral-nudge-engine.md` |

---

## FASE 0 — AUDITORIA & DIAGNÓSTICO
> **Objetivo**: Mapear o estado real do sistema antes de qualquer alteração.
> Rodar em paralelo. Nenhum code change nesta fase.
> **Orchestrador de gate**: Code Reviewer + Evidence Collector

### F0-A `Code Reviewer` — Auditoria de qualidade do código
**Persona**: `engineering-code-reviewer.md`
**Status**: `[ ]`

**Inputs**: `src/`, `api/`, `Front/src/`
**Tarefa**:
1. Auditar `src/` — identificar: funções >200 linhas, bare excepts, prints no domínio, dead code
2. Auditar `api/routes/` — verificar: error handling, falta de validação de input, N+1 queries implícitas
3. Auditar `Front/src/` — verificar: prop drilling profundo, componentes >300 linhas, falta de error boundaries
4. Produzir relatório priorizado em `docs/audit_code_quality.md`

**Output**: `docs/audit_code_quality.md` com: críticos (P0), importantes (P1), melhorias (P2)
**Handoff para**: Software Architect (F1-B), Backend Architect (F2-A)

---

### F0-B `API Tester` — Validação completa dos endpoints
**Persona**: `testing-api-tester.md`
**Status**: `[ ]`

**Inputs**: Servidor rodando em `localhost:8000`, `scripts/smoke_test_all_routes.py`
**Tarefa**:
1. Rodar `python scripts/smoke_test_all_routes.py` com save ativo
2. Testar todos os endpoints documentados em `docs/PLANO_EXECUCAO_IAS.md` (contratos de API)
3. Verificar: respostas 200, schemas corretos, error cases retornam 4xx (não 500)
4. Documentar endpoints com falha/schema errado

**Output**: `docs/audit_api_endpoints.md` com tabela: endpoint / status / schema_ok / observações
**Handoff para**: Backend Architect (F2-A)

---

### F0-C `Performance Benchmarker` — Baseline de performance
**Persona**: `testing-performance-benchmarker.md`
**Status**: `[ ]`

**Inputs**: API rodando localmente
**Tarefa**:
1. Medir p50/p95 dos endpoints críticos: `/api/ranking/atp`, `/api/torneio/estado`, `/api/partida/ponto`, `/api/calendario/atual`
2. Medir tamanho dos arquivos de save (saves/*/jogadores/) — identificar shards >100KB
3. Medir tempo de `avancar_semana()` — cold vs warm
4. Documentar bottlenecks em `docs/audit_performance.md`

**Output**: `docs/audit_performance.md` com: métricas baseline, top 5 bottlenecks, recomendações
**Handoff para**: Database Optimizer (F2-C), Backend Architect (F2-A)

---

### F0-D `UX Researcher` — Auditoria de UX/flows atuais
**Persona**: `design-ux-researcher.md`
**Status**: `[ ]`

**Inputs**: Frontend em `Front/src/`, `COMPARATIVO_FUNCIONALIDADES.md`
**Tarefa**:
1. Mapear todos os fluxos de usuário principais (criar save → jogar torneio → ver ranking → treinar)
2. Identificar: dead ends de navegação, falta de feedback de loading, fluxos confusos
3. Listar: 3-5 friction points de maior impacto
4. Produzir `docs/audit_ux_flows.md`

**Output**: `docs/audit_ux_flows.md` com: mapa de fluxos, friction points, quick wins
**Handoff para**: UI Designer (F3-B2), Whimsy Injector (F3-B3), Frontend Developer (F3-B1)

---

### GATE 0 → 1
**Critério de avanço**: Todos os 4 relatórios de auditoria entregues
**Decisão**: Code Reviewer + Evidence Collector sign-off
**Formato de handoff**: `docs/gate_0_summary.md` com síntese dos 4 audits

---

## FASE 1 — ESTRATÉGIA & ARQUITETURA
> **Objetivo**: Definir o que construir, como arquitetar, priorizar por impacto.
> Rodar em paralelo. Sem código ainda.
> **Orchestrador de gate**: Sprint Prioritizer

### F1-A `Game Designer` — Design das features de profundidade de carreira
**Persona**: `game-development/game-designer.md`
**Status**: `[ ]`

**Inputs**: `docs/audit_ux_flows.md`, `COMPARATIVO_FUNCIONALIDADES.md`, `codex.md`
**Tarefa**: Projetar as seguintes features com GDD-level detail:

**1. Sistema de Rival Dinâmico**
- Critérios para "cristalizar" um rival (ranking próximo, confrontos frequentes, virada dramática)
- Estrutura de dados do rival: `{nome, vitorias_contra, derrotas_contra, ultimo_confronto, intensidade}`
- Eventos narrativos disparados: "X venceu você 3 vezes seguidas → aparece no próximo torneio"
- UI hint: badge "RIVAL" no bracket quando o adversário for seu rival

**2. Circuito ITF/Challenger**
- Hierarquia: ITF ($15k) → ITF ($25k) → Challenger → 250 → 500 → 1000 → GS
- Como jogadores progridem entre tiers
- Calendário semanal: como conviver com torneios ATP e Challenger
- Pontos e ranking dedicado por tier

**3. Eventos de Carreira Especiais**
- "Aniversário de carreira" com milestone pop-up a cada 52 semanas
- "Lesão mais grave" (semanas out) com recovery arc
- "Grande virada" (3ª set salvou match point) com notificação especial
- "Recordes pessoais" (primeiro GS, primeiro Top 10, etc)

**Output**: `docs/design_features_v2.md` com specs detalhadas das 3 features
**Handoff para**: Software Architect (F1-B), Narrative Designer (F1-C)

---

### F1-B `Software Architect` — Arquitetura técnica das novas features
**Persona**: `engineering-software-architect.md`
**Status**: `[ ]`

**Inputs**: `docs/design_features_v2.md`, `docs/audit_code_quality.md`, `CLAUDE.md`
**Tarefa**:
1. Projetar arquitetura do sistema de rival:
   - Onde guardar no save (`jogador.rival` vs `saves/*/rival.json`)
   - Como detectar/atualizar rival após cada partida
   - API: `GET /api/jogador/rival`, `GET /api/ranking/atp?include_rival=true`

2. Projetar circuito ITF/Challenger:
   - Novo `db/calendario_itf.json` com semanas e torneios ITF/Challenger
   - Como integrar com `torneio_profile.py` sem quebrar ATP
   - Separação de pontos ITF vs ATP no ranking
   - API: `GET /api/calendario/itf`, `GET /api/ranking/challenger`

3. Projetar eventos de carreira:
   - `src/career_events.py` — detector de eventos, banco de eventos, triggers
   - Como persistir em `jogador.career_events[]`
   - WebSocket push de eventos especiais durante partida/semana

4. Plano de refactoring baseado em `docs/audit_code_quality.md` (top P0 e P1)

**Output**: `docs/architecture_v2.md` com: diagramas de dados, contratos de API, plano de migração
**Handoff para**: Backend Architect (F2-A), Frontend Developer (F2-B)

---

### F1-C `Narrative Designer` — Sistema narrativo de carreira
**Persona**: `game-development/narrative-designer.md`
**Status**: `[ ]`

**Inputs**: `docs/design_features_v2.md`, `db/imprensa_perguntas.json`, `src/imprensa.py`
**Tarefa**:
1. Ampliar banco de eventos narrativos de carreira:
   - 20+ novos eventos de imprensa com contexto dinâmico (ex: "Após vencer o rival histórico...")
   - 10+ frases de milestone de carreira (primeiro GS, aposentadoria próxima, etc)
   - 5+ arcos narrativos de rival (tensão crescente → clímax → resolução)

2. Estruturar `db/career_narrative_events.json` com:
   - `tipo`: milestone / rival / lesao / recordes / impressa
   - `condicao`: expressão avaliável contra estado do jogador
   - `texto`: template com `{nome}`, `{rival}`, `{torneio}`, `{ranking}`
   - `impacto_moral`: -10 a +10

3. Planejar como integrar os eventos no loop semanal

**Output**: `db/career_narrative_events.json` com 35+ eventos estruturados
**Handoff para**: Backend Architect (F2-A) para implementar `src/career_events.py`

---

### F1-D `Sprint Prioritizer` — Backlog RICE-scored
**Persona**: `product/product-sprint-prioritizer.md`
**Status**: `[ ]`

**Inputs**: `docs/design_features_v2.md`, `docs/architecture_v2.md`, `docs/audit_ux_flows.md`
**Tarefa**:
Aplicar scoring RICE (Reach × Impact × Confidence / Effort) a todas as features:

| Feature | R | I | C | E | RICE |
|---------|---|---|---|---|------|
| Sistema Rival | ? | ? | ? | ? | ? |
| ITF/Challenger | ? | ? | ? | ? | ? |
| Eventos Carreira | ? | ? | ? | ? | ? |
| Ranking History Chart | ? | ? | ? | ? | ? |
| Tests unitários | ? | ? | ? | ? | ? |
| Refactoring P0/P1 | ? | ? | ? | ? | ? |
| Whimsy/polish UI | ? | ? | ? | ? | ? |

Determinar: O que vai para Sprint 1 (esta sessão) vs Sprint 2 (próxima)

**Output**: `docs/backlog_rice.md` com backlog priorizado e divisão de sprints
**Handoff para**: Senior Project Manager (F1-E)

---

### F1-E `Senior Project Manager` — Task breakdown
**Persona**: `project-management/project-manager-senior.md`
**Status**: `[ ]`

**Inputs**: `docs/backlog_rice.md`, `docs/architecture_v2.md`
**Tarefa**: Converter features do Sprint 1 em tasks granulares (≤4h cada):
- Para cada task: ID único, descrição, agente responsável, inputs, outputs, acceptance criteria
- Identificar dependências críticas (task A bloqueia task B)
- Estimar ciclos necessários (sem predições de tempo)

**Output**: `docs/tasks_sprint1.md` com task list completa e dependency map
**Handoff para**: todos os agentes de Fase 3

---

### GATE 1 → 2
**Critério de avanço**: `docs/design_features_v2.md` + `docs/architecture_v2.md` + `docs/backlog_rice.md` + `docs/tasks_sprint1.md` entregues
**Decisão**: Sprint Prioritizer confirma que backlog está RICE-scored e sequenciado
**Formato de handoff**: `docs/gate_1_summary.md`

---

## FASE 2 — FUNDAÇÃO
> **Objetivo**: Preparar infraestrutura para construção. Scaffolding, CI, schemas.
> Rodar em paralelo. Mínimo de business logic nesta fase.

### F2-A `Backend Architect` (Gemini) — Novos endpoints e schemas
**Persona**: `engineering-backend-architect.md`
**Status**: `[ ]`

**Inputs**: `docs/architecture_v2.md`, `docs/audit_api_endpoints.md`, `CLAUDE.md`
**Tarefa**:
1. Implementar `src/career_events.py` — detector/registrador de eventos de carreira
2. Criar `api/routes/rival.py` — `GET /api/jogador/rival`, `POST /api/jogador/rival/registrar`
3. Criar `api/routes/itf.py` — `GET /api/calendario/itf`, `GET /api/ranking/challenger`
4. Adicionar `GET /api/jogador/ranking-historico` (endpoint já existe, confirmar schema)
5. Corrigir todos os P0 de `docs/audit_api_endpoints.md`
6. Todos os arquivos: `black --check` + `py_compile` obrigatórios

**Output**: Endpoints funcionando com `curl` + contratos documentados em `docs/PLANO_NEXUS_SPRINT_V2.md` seção "Contratos API"
**Handoff para**: Frontend Developer (F2-B), API Tester (F3-D1)

---

### F2-B `Frontend Developer` (Claude) — Scaffold de novas telas
**Persona**: `engineering-frontend-developer.md`
**Status**: `[ ]`

**Inputs**: `docs/architecture_v2.md`, `docs/audit_ux_flows.md`
**Tarefa**:
1. Criar esqueletos (sem lógica real) de:
   - `Front/src/app/screens/RivalScreen.tsx` — tela do sistema rival
   - `Front/src/app/screens/RankingHistoryScreen.tsx` — gráfico de evolução de ranking
   - `Front/src/app/screens/CareerEventsScreen.tsx` — timeline de eventos de carreira
2. Registrar rotas: `/rival`, `/ranking-history`, `/career-events` em `routes.ts`
3. Adicionar métodos skeleton em `api/client.ts`: `api.jogador.rival()`, `api.jogador.rankingHistorico()`, `api.jogador.careerEvents()`
4. Adicionar links de navegação no HubScreen para as novas telas

**Output**: 3 telas skeleton acessíveis via browser (sem dados reais ainda)
**Handoff para**: UI Designer (F3-B2), Frontend Developer (F3-B1)

---

### F2-C `Database Optimizer` — Otimização de estruturas de dados
**Persona**: `engineering-database-optimizer.md`
**Status**: `[ ]`

**Inputs**: `docs/audit_performance.md`, `src/save.py`, `src/dados.py`
**Tarefa**:
1. Analisar shards de jogadores — propor: índice leve por posição, lazy load de atributos completos
2. Verificar `historico_partidas.json` — esquema atual tem duplicatas? IDs únicos corretos?
3. Propor e implementar: cache em memória para ranking lean (top 100) na sessão
4. Documentar em `docs/optimization_notes.md` qualquer mudança de schema para migração

**Output**: `src/dados.py` com melhorias de cache + `docs/optimization_notes.md`
**Handoff para**: Backend Architect (F3-A2)

---

### F2-D `DevOps Automator` — CI/CD com testes e coverage
**Persona**: `engineering-devops-automator.md`
**Status**: `[ ]`

**Inputs**: `pyproject.toml`, `requirements.txt`, `tests/` (existente)
**Tarefa**:
1. Verificar estado de `tests/` — quais testes existem, cobertura atual
2. Configurar `pyproject.toml` para: `pytest`, `pytest-cov`, cobertura mínima 30%
3. Criar/atualizar `Makefile` com targets: `test`, `coverage`, `lint`, `format`
4. Criar `.github/workflows/ci.yml` (ou verificar se existe) com: black, flake8, pytest
5. Criar `tests/test_smoke_api.py` — smoke test básico dos endpoints críticos

**Output**: `Makefile` + `pyproject.toml` + CI workflow + test smoke básico funcional
**Handoff para**: Code Reviewer (F4-A), Reality Checker (F4-C)

---

### GATE 2 → 3
**Critério**: Endpoints documentados funcionando + 3 telas scaffold visíveis + CI pipeline verde
**Gate Keeper**: DevOps Automator verifica CI + API Tester verifica novos endpoints
**Formato**: `docs/gate_2_summary.md`

---

## FASE 3 — BUILD (4 TRACKS PARALELOS)
> **Objetivo**: Implementar features do Sprint 1 com Dev↔QA loop contínuo.
> 4 tracks em paralelo. Cada task passa por Evidence Collector antes de avançar.

---

### TRACK A — Domínio do Jogo (Codex)

#### F3-A1 `Game Designer` — Sistema de Rival: implementação no domínio
**Persona**: `game-development/game-designer.md`
**Status**: `[ ]`

**Inputs**: `docs/design_features_v2.md`, `src/jogador.py`, `src/match_history.py`, `api/routes/rival.py` (scaffold)
**Tarefa**:
1. Implementar `src/rival_system.py`:
   - `detectar_rival(jogador, historico) → RivalInfo | None`
   - `calcular_intensidade_rival(h2h, ultimo_confronto) → int (0-100)`
   - `atualizar_rival_apos_partida(jogador, adversario, venceu) → void`
2. Integrar em `src/calendario.py::avancar_semana()` — atualizar rival semanalmente
3. Integrar em `api/routes/_match_runtime.py` — marcar se adversário é rival nos eventos
4. Testes: `tests/test_rival_system.py` com 5+ casos

**Output**: `src/rival_system.py` + integração + testes passando
**QA**: API Tester valida `GET /api/jogador/rival` após integração

---

#### F3-A2 `Software Architect` — Circuito ITF/Challenger
**Persona**: `engineering-software-architect.md`
**Status**: `[ ]`

**Inputs**: `docs/architecture_v2.md`, `src/torneio_profile.py`, `src/pontuacao.py`, `db/calendario.json`
**Tarefa**:
1. Criar `db/calendario_itf.json` — 52 semanas com torneios ITF/Challenger intercalados
2. Ampliar `src/torneio_profile.py` — novos tipos: `itf_15k`, `itf_25k`, `itf_50k`, `challenger_100`, `challenger_175`
3. Criar `src/pontuacao_itf.py` — tabelas de pontos ITF/Challenger por fase
4. Integrar: jogadores com ranking > 250 automaticamente aparecem em calendário ITF
5. Testes: verificar que pontos ITF não contaminam ranking ATP

**Output**: Sistema ITF funcional com `db/calendario_itf.json` + profile types + pontuação
**QA**: API Tester valida `GET /api/calendario/itf`

---

### TRACK B — Frontend (Claude)

#### F3-B1 `Frontend Developer` — Implementação das 3 novas telas
**Persona**: `engineering-frontend-developer.md`
**Status**: `[ ]`

**Inputs**: `docs/tasks_sprint1.md`, API endpoints de F2-A, scaffolds de F2-B
**Tarefa**:

**RivalScreen (`/rival`)**:
- Header com nome/foto do rival, H2H counter animado
- Seção "Histórico de confrontos" (últimas 5 partidas com placar)
- "Próximos torneios em comum" (onde você e seu rival estão inscritos)
- Botão "ANALISAR RIVAL" → redireciona para scout do rival
- Badge `RIVAL` com borda pulsante em neon vermelho

**RankingHistoryScreen (`/ranking-history`)**:
- Gráfico de linha (recharts ou CSS puro) mostrando evolução de posição no ranking ao longo das 52 semanas
- Destaque: pico de carreira, atual
- Tabela com pontos semana a semana
- Toggle ATP / WTA / Race

**CareerEventsScreen (`/career-events`)**:
- Timeline vertical de eventos de carreira com ícones por tipo
- Filtros: milestone / rival / lesao / recorde
- Evento destacado com animação ao hover

**Output**: 3 telas completamente funcionais com dados reais da API
**QA**: Evidence Collector screenshot cada tela

---

#### F3-B2 `UI Designer` — Polish dos componentes existentes
**Persona**: `design-ui-designer.md`
**Status**: `[ ]`

**Inputs**: `docs/audit_ux_flows.md`, `docs/DESIGN_SYSTEM.md`, telas existentes
**Tarefa**:
1. Criar `EmptyState` component padronizado (quando não há dados) — usado em RankingsScreen, WorldScreen, HistoryScreen
2. Criar `SkeletonLoader` animado para loading states — substituir textos "CARREGANDO..."
3. Corrigir inconsistências de espaçamento/fontes reportadas em `audit_ux_flows.md`
4. Unificar `PageHeader` para incluir breadcrumb de navegação opcional
5. Garantir que todos os componentes novos seguem o design system: `#0a0a0a bg`, neon palette, Press Start 2P + Share Tech Mono

**Output**: Componentes `EmptyState`, `SkeletonLoader` em `Front/src/app/components/` + correções aplicadas
**QA**: Evidence Collector screenshots de before/after

---

#### F3-B3 `Whimsy Injector` — Micro-interações e momentos de deleite
**Persona**: `design-whimsy-injector.md`
**Status**: `[ ]`

**Inputs**: `docs/audit_ux_flows.md`, `Front/src/app/screens/MatchScreen.tsx`, `WeekAdvanceScreen.tsx`
**Tarefa**:
1. Animação de confetti pixel-art ao vencer um Grand Slam (MatchScreen → pos-stats)
2. "Level up" animation ao subir de nível (ProgressionScreen)
3. Badge pulsante "NOVO" para emails não lidos (HubScreen)
4. Animação de contagem regressiva no timer entre sets (já existe, melhorar visual)
5. Efeito de "screen shake" leve ao perder um break point importante
6. Easter egg: sequência de cliques no logo → muda tema de cores

**Output**: Animações implementadas com `motion/react` sem impactar performance (< 2KB gzip adicionado)
**QA**: Evidence Collector grava GIF de cada animação

---

### TRACK C — Backend (Gemini)

#### F3-C1 `Backend Architect` — Eventos de carreira e integração
**Persona**: `engineering-backend-architect.md`
**Status**: `[ ]`

**Inputs**: `db/career_narrative_events.json`, `src/career_events.py` (F3-A1 herda), `api/session.py`
**Tarefa**:
1. Implementar endpoint `GET /api/jogador/career-events` — retorna eventos disparados
2. Implementar `POST /api/jogador/career-events/dismiss/{id}` — marcar como visto
3. Integrar career events em `avancar_semana()` — detectar e persistir novos eventos
4. Implementar `GET /api/jogador/ranking-historico` — retorna array `[{semana, posicao, pontos}]`
5. Corrigir P1s restantes de `docs/audit_api_endpoints.md`

**Output**: Endpoints funcionando + integração com save verificada
**QA**: API Tester validação completa de cada endpoint

---

#### F3-C2 `AI Engineer` — Geração de comentários dinâmicos
**Persona**: `engineering-ai-engineer.md`
**Status**: `[ ]`

**Inputs**: `src/simulacao_partida.py`, `db/career_narrative_events.json`, `src/eventos_exibicao.py`
**Tarefa**:
1. Criar `src/match_commentary.py` — gerador de comentários contextuais baseados em:
   - Estado do placar (pressão vs conforto)
   - Superfície e estilo do adversário
   - Adversário é rival? → comentários especiais
   - Momentum (sequências de 3+ pontos iguais → narrativa)
2. Templates de 50+ comentários por categoria (saque, winner, erro, break point)
3. Integrar em `_atualizar_placar()` no runtime — substituir mensagens genéricas
4. IMPORTANTE: Usar templates locais, sem chamada externa de API

**Output**: `src/match_commentary.py` + integração no runtime + variedade aumentada
**QA**: Rodar 5 partidas simuladas e verificar diversidade dos comentários

---

### TRACK D — Qualidade (Contínuo)

#### F3-D1 `API Tester` — Validação contínua de novos endpoints
**Persona**: `testing-api-tester.md`
**Status**: `[ ]`

**Ativado por cada**: F3-A1, F3-A2, F3-C1, F3-C2 ao declarar endpoint pronto
**Tarefa**: Para cada endpoint novo/alterado:
1. Testar: GET/POST com payload válido → espera 200
2. Testar: payload inválido → espera 400 (não 500)
3. Testar: sem sessão ativa → espera 401/403
4. Verificar schema de resposta contra contrato documentado

**Output**: `docs/api_test_results.md` atualizado a cada ciclo
**Escalação**: Se endpoint falha 3x → reportar para Backend Architect como bloqueador

---

#### F3-D2 `Evidence Collector` — QA visual de todas as features
**Persona**: `testing-evidence-collector.md`
**Status**: `[ ]`

**Ativado por cada**: F3-B1, F3-B2, F3-B3 ao declarar tela pronta
**Tarefa**: Para cada tela/feature frontend:
1. Screenshot: estado normal (com dados)
2. Screenshot: estado vazio (sem dados) — usa EmptyState?
3. Screenshot: estado de loading — usa SkeletonLoader?
4. Screenshot: estado de erro
5. Verificar: responsividade mobile (320px), tablet (768px), desktop (1280px)

**Default**: NEEDS WORK — só PASS com evidência visual para TODOS os 5 estados

**Output**: `docs/evidence_screenshots/` organizado por feature
**Escalação**: Falha 3x → UI Designer retoma

---

### GATE 3 → 4
**Critério**:
- Todas as tasks marcadas `[x]`
- API Tester: zero endpoints retornando 500
- Evidence Collector: todas as telas com screenshots completos
- `python -m pytest tests/ -v` passa com cobertura ≥ 30%

**Gate Keeper**: Agents Orchestrator (Claude nesta sessão)
**Formato**: `docs/gate_3_summary.md`

---

## FASE 4 — HARDENING & QA FINAL
> **Objetivo**: A Reality Checker parte de "NEEDS WORK". Provar com evidências.

### F4-A `Code Reviewer` — Review final antes do merge
**Persona**: `engineering-code-reviewer.md`
**Status**: `[ ]`

**Inputs**: Todo código novo de Fase 3 (git diff main...feat/frontend)
**Tarefa**:
1. Review de `src/rival_system.py`, `src/match_commentary.py`, `src/career_events.py`
2. Review de `api/routes/rival.py`, `api/routes/itf.py`, novos endpoints
3. Review de `Front/src/app/screens/RivalScreen.tsx`, `RankingHistoryScreen.tsx`, `CareerEventsScreen.tsx`
4. Verificar: sem secrets hardcoded, sem SQL injection equivalente (JSON injection), sem XSS no frontend
5. Verificar: black + flake8 passam em TODOS os arquivos novos

**Output**: `docs/review_final.md` com: aprovados, ajustes menores, bloqueadores
**Handoff para**: Reality Checker (F4-C)

---

### F4-B `SRE` — Revisão de confiabilidade
**Persona**: `engineering-sre.md`
**Status**: `[ ]`

**Inputs**: `docs/audit_performance.md`, código de Fase 3, `api/routes/`
**Tarefa**:
1. Verificar: todos os novos endpoints têm timeout handling (não pendurados)
2. Verificar: `salvar_json_seguro()` é usado em TODA escrita de JSON nova (não open() direto)
3. Verificar: novos `useEffect` no frontend têm cleanup (sem memory leaks)
4. Verificar: circuit breakers para chamadas que podem falhar (API Tester confirma)
5. Produzir: `docs/reliability_report.md` com SLO informais: uptime esperado, MTTR estimado

**Output**: `docs/reliability_report.md` + lista de ajustes necessários
**Handoff para**: Reality Checker (F4-C)

---

### F4-C `Reality Checker` — Gate final de produção
**Persona**: `testing-testing-reality-checker.md`
**Status**: `[ ]`

**Default**: NEEDS WORK. Só READY com evidência esmagadora.

**Inputs**: `docs/review_final.md`, `docs/reliability_report.md`, `docs/api_test_results.md`, `docs/evidence_screenshots/`
**Critérios para READY**:
- [ ] Todos os user journeys críticos: criar save → torneio → partida → treino → rival → semana
- [ ] Zero endpoints retornando 500 em operação normal
- [ ] Zero `console.error` não tratados no frontend
- [ ] Cobertura de testes ≥ 30%
- [ ] `black --check src/ api/` passa sem erros
- [ ] Telas novas: evidência para todos os 5 estados (normal/vazio/loading/erro/mobile)
- [ ] Performance: `/api/partida/ponto` p95 < 300ms
- [ ] Rival system: funciona após 3 confrontos contra mesmo adversário

**Output**: Relatório READY / NEEDS WORK / NOT READY com lista específica de itens faltando
**Se NEEDS WORK**: retornar ao Dev↔QA loop na Fase 3 com lista detalhada

---

### GATE 4 → 5
**Critério**: Reality Checker emite READY
**Gate Keeper**: Reality Checker (sole authority)

---

## FASE 5 — RELEASE
> **Objetivo**: Documentar, mergear, publicar.

### F5-A `Technical Writer` — Atualização de documentação
**Persona**: `engineering-technical-writer.md`
**Status**: `[ ]`

**Inputs**: Todo código novo de Fases 2-4, `CLAUDE.md`, `README.MD`
**Tarefa**:
1. Atualizar `README.MD` com: novos endpoints, novas telas, como rodar o frontend
2. Atualizar `CLAUDE.md` — novos módulos (`src/rival_system.py`, `src/career_events.py`, `src/match_commentary.py`)
3. Criar `docs/api_reference.md` — tabela completa de todos os endpoints com schema
4. Atualizar `docs/saves.md` — novos campos no save (`rival`, `career_events`, `ranking_historico`)

**Output**: Documentação atualizada e precisa
**Handoff para**: DevOps Automator (F5-B)

---

### F5-B `DevOps Automator` — Merge e deployment
**Persona**: `engineering-devops-automator.md`
**Status**: `[ ]`

**Inputs**: Branch `feat/frontend` aprovada pela Reality Checker
**Tarefa**:
1. Verificar CI verde: `black`, `flake8`, `pytest` passando
2. Criar PR: `feat/frontend` → `main` com description completa
3. Verificar que não há conflitos de merge
4. Após merge: tag de release `v2.0.0` com changelog

**IMPORTANTE**: NÃO fazer force push. NÃO fazer merge sem CI verde.

**Output**: PR criado + merged + tag de release
**Handoff para**: Analytics Reporter (F6-A)

---

### F5-C `Executive Summary Generator` — Retrospectiva do sprint
**Persona**: `support-executive-summary-generator.md`
**Status**: `[ ]`

**Inputs**: Todos os gates e relatórios de fases 0-4
**Tarefa**: Produzir em `docs/sprint_retrospective_v2.md`:
- O que foi construído (features entregues)
- Métricas de qualidade (% tasks first-pass, bugs encontrados/corrigidos)
- Dívida técnica restante
- Recomendações para Sprint 3

**Output**: `docs/sprint_retrospective_v2.md` (≤500 palavras, formato SCQA)

---

## FASE 6 — OPERAÇÃO & EVOLUÇÃO
> **Objetivo**: Medir, aprender, planejar Sprint 3. Ciclo contínuo.

### F6-A `Analytics Reporter` — Análise de balanceamento do jogo
**Persona**: `support-support-analytics-reporter.md`
**Status**: `[ ]`

**Cadência**: Semanal (após cada sessão de jogo)
**Inputs**: `saves/*/historico_partidas.json`, `saves/*/jogador.json`
**Tarefa**:
1. Analisar: win rate do jogador por superfície (esperado: 45-65% no mid-game)
2. Analisar: distribuição de rankings dos adversários derrotados/perdidos
3. Analisar: frequência de cada archetype no circuito
4. Detectar: anomalias (win rate > 80% = jogo fácil demais; < 30% = difícil demais)
5. Produzir: `docs/balance_report.md` com recomendações para Game Designer

**Output**: `docs/balance_report.md` atualizado

---

### F6-B `Behavioral Nudge Engine` — Melhorias de retenção e engajamento
**Persona**: `product/product-behavioral-nudge-engine.md`
**Status**: `[ ]`

**Cadência**: Por sprint
**Inputs**: `docs/audit_ux_flows.md`, `docs/balance_report.md`
**Tarefa**:
1. Identificar: em que ponto os jogadores "desistem" do jogo (dropout)
2. Propor: 3-5 nudges comportamentais concretos (ex: "weekly streak", "próximo milestone em X semanas")
3. Propor: sistema de progresso visual no HubScreen (barras de progresso para goals)
4. Design de `NotificaçãoSemanal` — resumo motivacional da semana ao voltar para o hub

**Output**: `docs/retention_improvements.md` com designs aprovados para Sprint 3

---

## CONTRATOS DE API — SPRINT 2

> Todos os novos endpoints devem ser documentados aqui antes de implementar.

| Endpoint | Método | Responsável | Fase | Status |
|----------|---------|-------------|------|--------|
| `GET /api/jogador/rival` | GET | Gemini | F2-A | `[ ]` |
| `POST /api/jogador/rival/registrar` | POST | Gemini | F2-A | `[ ]` |
| `GET /api/calendario/itf` | GET | Gemini | F2-A | `[ ]` |
| `GET /api/ranking/challenger` | GET | Gemini | F2-A | `[ ]` |
| `GET /api/jogador/career-events` | GET | Gemini | F3-C1 | `[ ]` |
| `POST /api/jogador/career-events/dismiss/{id}` | POST | Gemini | F3-C1 | `[ ]` |
| `GET /api/jogador/ranking-historico` | GET | Gemini | F3-C1 | `[ ]` |

---

## HANDOFF TEMPLATES PADRÃO

### Template: Entrega de Feature (Dev → Evidence Collector)
```
## Handoff: [Feature Name]
- **De**: [Agent] | **Para**: Evidence Collector
- **Task**: [ID] — [Descrição]
- **Arquivos alterados**: [lista]
- **Como testar**: [passos exatos]
- **Acceptance criteria**: [lista específica]
- **Estados a verificar**: normal / vazio / loading / erro / mobile
```

### Template: QA Failure (Evidence Collector → Developer)
```
## QA Failure: [Feature Name] — Tentativa [N/3]
- **Issues encontrados**: [lista com evidência]
- **Esperado**: [descrição]
- **Atual**: [descrição]
- **Screenshot**: [referência]
- **Fix necessário**: [instrução específica]
```

### Template: Gate Approval
```
## Gate [N] → [N+1]: APROVADO/REPROVADO
- **Gate Keeper**: [Agent]
- **Data**: YYYY-MM-DD
- **Critérios checados**: [lista com ✅/❌]
- **Itens pendentes**: [lista se reprovado]
- **Próxima fase**: [agent list]
```

---

## DEPENDENCY MAP

```
F0 (auditoria) ──────────────────────────────────────────→ F1 (estratégia)
  ├── F0-A Code Review ──→ F1-B Software Architect
  ├── F0-B API Tester ──→ F2-A Backend Architect
  ├── F0-C Performance ──→ F2-C Database Optimizer
  └── F0-D UX Research ──→ F3-B2 UI Designer

F1 (estratégia) ─────────────────────────────────────────→ F2 (fundação)
  ├── F1-A Game Designer ──→ F1-B Architect ──→ F2-A Backend
  ├── F1-C Narrative Designer ──→ F2-A Backend (career_events.json)
  ├── F1-D Sprint Prioritizer ──→ F1-E Senior PM
  └── F1-E Senior PM ──→ todos os agentes de F3

F2 (fundação) ───────────────────────────────────────────→ F3 (build)
  ├── F2-A Backend APIs ──→ F3-B1 Frontend + F3-D1 API Tester
  ├── F2-B Frontend scaffold ──→ F3-B1 + F3-B2 + F3-B3
  └── F2-D DevOps CI ──→ F4-A Code Review

F3 (build, paralelo) ────────────────────────────────────→ F4 (hardening)
  Todos os tracks ──→ F4-A Code Review + F4-B SRE + F4-C Reality Checker

F4 (hardening) ──────────────────────────────────────────→ F5 (release)
  Reality Checker READY ──→ F5-A Technical Writer + F5-B DevOps

F5 (release) ────────────────────────────────────────────→ F6 (operate)
  Merge to main ──→ F6-A Analytics + F6-B Behavioral Nudge
```

---

## PIPELINE STATUS

| Fase | Status | Gate | Agentes Ativos |
|------|--------|------|----------------|
| 0 — Auditoria | `[ ]` | Pending | Code Reviewer, API Tester, Performance Benchmarker, UX Researcher |
| 1 — Estratégia | `[ ]` | Pending | Game Designer, Software Architect, Narrative Designer, Sprint Prioritizer, Senior PM |
| 2 — Fundação | `[ ]` | Pending | Backend Architect, Frontend Developer, Database Optimizer, DevOps Automator |
| 3 — Build | `[ ]` | Pending | 9 agentes em 4 tracks |
| 4 — Hardening | `[ ]` | Pending | Code Reviewer, SRE, Reality Checker |
| 5 — Release | `[ ]` | Pending | Technical Writer, DevOps Automator, Executive Summary |
| 6 — Operação | `[ ]` | Ongoing | Analytics Reporter, Behavioral Nudge Engine |

---

*NEXUS-Sprint TennisLegacy v2 | 22 agents | 6 fases | Gate-enforced pipeline*
