# NEXUS-SPRINT V3 — TennisLegacy Maximum Agent Deployment
> Branch: `feat/frontend` → `main` | Modo: NEXUS-Sprint MAXIMUM (102 agents, 8 fases)
> Atualizado: 2026-03-19 | Referência: `~/.claude/agents/strategy/nexus-strategy.md`
>
> **Objetivo**: Máxima cobertura de agents para elevar TennisLegacy a produto completo,
> com qualidade de carreira, comunidade, marketing e operações sustentáveis.
>
> **Regra**: Agents marcados com ⚠️ têm aplicação criativa (não óbvia) — justificativa incluída.

---

## STATUS GLOBAL

```
[ ] pendente | [~] em progresso | [x] feito | [!] bloqueado
```

| Fase | Agents | Status |
|------|--------|--------|
| 0 — Auditoria & Inteligência | 9 | `[ ]` |
| 1 — Estratégia & Arquitetura | 12 | `[ ]` |
| 2 — Fundação | 10 | `[ ]` |
| 3 — Build (6 tracks paralelos) | 27 | `[ ]` |
| 4 — Hardening & QA | 11 | `[ ]` |
| 5 — Release & Lançamento | 13 | `[ ]` |
| 6 — Operação & Escala | 16 | `[ ]` |
| Contínuo — Governança & Conhecimento | 4 | `[ ]` |
| **TOTAL** | **102** | |

---

## FASE 0 — AUDITORIA & INTELIGÊNCIA
> Rodar em paralelo. Zero code changes. Apenas diagnóstico.

### 0-01 `Code Reviewer`
**Persona**: `~/.claude/agents/engineering/engineering-code-reviewer.md`
**Status**: `[ ]`
**Tarefa**: Auditar `src/`, `api/`, `Front/src/` — críticos (P0), importantes (P1), melhorias (P2)
**Input**: Codebase | **Output**: `docs/audit_code_quality.md`

### 0-02 `API Tester`
**Persona**: `~/.claude/agents/testing/testing-api-tester.md`
**Status**: `[ ]`
**Tarefa**: Validar todos os endpoints — status, schema, error cases (4xx vs 500)
**Input**: `localhost:8000` + `scripts/smoke_test_all_routes.py` | **Output**: `docs/audit_api_endpoints.md`

### 0-03 `Performance Benchmarker`
**Persona**: `~/.claude/agents/testing/testing-performance-benchmarker.md`
**Status**: `[ ]`
**Tarefa**: Medir p50/p95 dos endpoints críticos, tamanho de shards, `avancar_semana()` cold/warm
**Input**: API local | **Output**: `docs/audit_performance.md`

### 0-04 `UX Researcher`
**Persona**: `~/.claude/agents/design/design-ux-researcher.md`
**Status**: `[ ]`
**Tarefa**: Mapear todos os fluxos principais, identificar dead ends e friction points
**Input**: `Front/src/`, `COMPARATIVO_FUNCIONALIDADES.md` | **Output**: `docs/audit_ux_flows.md`

### 0-05 `Security Engineer`
**Persona**: `~/.claude/agents/engineering/engineering-security-engineer.md`
**Status**: `[ ]`
**Tarefa**: Auditar: path traversal em saves (nome_save usado em paths), input validation nas rotas, JSON injection, XSS em strings de jogador renderizadas no frontend
**Input**: `api/routes/`, `src/dados.py`, `Front/src/` | **Output**: `docs/audit_security.md`

### 0-06 `Model QA Specialist`
**Persona**: `~/.claude/agents/specialized/specialized-model-qa.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Auditar o modelo de simulação de partida — calibração da probabilidade de vitória vs ranking, win rate por archetype, distribuição de sets, frequência de tiebreaks. É o modelo estatisticamente saudável?
**Input**: `src/simulacao_partida.py`, `src/jogar_partida.py`, `saves/*/historico_partidas.json` | **Output**: `docs/audit_match_model.md`

### 0-07 `Trend Researcher`
**Persona**: `~/.claude/agents/product/product-trend-researcher.md`
**Status**: `[ ]`
**Tarefa**: Analisar mercado de jogos de simulação de tênis/carreira esportiva — concorrentes (Tennis Manager, Top Spin, Football Manager), tendências (roguelite, idle mechanics, mobile-first), oportunidades de diferenciação
**Input**: Web research | **Output**: `docs/market_research.md`

### 0-08 `Workflow Optimizer`
**Persona**: `~/.claude/agents/testing/testing-workflow-optimizer.md`
**Status**: `[ ]`
**Tarefa**: Mapear o workflow atual de desenvolvimento (editar Python → testar → commitar) — identificar gargalos, steps manuais desnecessários, oportunidades de automação
**Input**: `Makefile`, `CLAUDE.md`, `pyproject.toml` | **Output**: `docs/audit_dev_workflow.md`

### 0-09 `Psychologist`
**Persona**: `~/.claude/agents/academic/academic-psychologist.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Analisar os atributos psicológicos do jogo (`concentracao`, `determinacao`, `mentalidade`) — são psicologicamente coerentes com a literatura de performance esportiva? Propor ajustes no sistema de pressão e momentum baseados em psicologia do esporte real
**Input**: `src/simulacao_partida.py`, `src/constantes.py`, `db/archetypes.json` | **Output**: `docs/audit_psychology.md`

---

### GATE 0 → 1
**Critério**: 9 relatórios entregues | **Gate Keeper**: Code Reviewer + Executive Summary Generator
**Output**: `docs/gate_0_summary.md` com síntese executiva

---

## FASE 1 — ESTRATÉGIA & ARQUITETURA
> Baseado nos outputs da Fase 0. Rodar em paralelo. Sem implementação.

### 1-01 `Studio Producer`
**Persona**: `~/.claude/agents/project-management/project-management-studio-producer.md`
**Status**: `[ ]`
**Tarefa**: Definir visão estratégica de longo prazo — TennisLegacy como produto comercial? open source? mobile? Estabelecer north star metric e ROI targets por feature
**Input**: `docs/market_research.md`, `docs/gate_0_summary.md` | **Output**: `docs/strategic_vision.md`

### 1-02 `Product Manager`
**Persona**: `~/.claude/agents/product/product-manager.md`
**Status**: `[ ]`
**Tarefa**: Definir roadmap completo: o que vai para v2, v3, v4 — com justificativa de negócio por feature, métricas de sucesso, e critérios de go/no-go
**Input**: `docs/strategic_vision.md`, `docs/market_research.md` | **Output**: `docs/product_roadmap.md`

### 1-03 `Game Designer`
**Persona**: `~/.claude/agents/game-development/game-designer.md`
**Status**: `[ ]`
**Tarefa**: GDD completo para: (1) Sistema de Rival Dinâmico, (2) Circuito ITF/Challenger, (3) Eventos Especiais de Carreira, (4) Sistema de Reputação Mundial, (5) Aposentadoria e Hall da Fama interativo
**Input**: `docs/audit_match_model.md`, `docs/audit_psychology.md`, `codex.md` | **Output**: `docs/gdd_features_v2.md`

### 1-04 `Level Designer`
**Persona**: `~/.claude/agents/game-development/level-designer.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Projetar a curva de progressão da carreira como um "level design" — onde estão os picos de tensão e alívio, como o calendário de torneios cria ritmo semanal natural, como diferentes "arenas" (ITF→CH→ATP→GS) escalam em dificuldade e prestígio. Design de cada "fase" da carreira como um nível com obstáculos, recompensas e narrativa
**Input**: `docs/gdd_features_v2.md`, `db/calendario.json` | **Output**: `docs/career_progression_design.md`

### 1-05 `Narrative Designer`
**Persona**: `~/.claude/agents/game-development/narrative-designer.md`
**Status**: `[ ]`
**Tarefa**: Arquitetura narrativa completa: arcos de carreira (rookie→estrela→lenda), sistema de rivalidades com escalada dramática, 50+ eventos de imprensa contextuais, milestone scripts para conquistas únicas
**Input**: `docs/gdd_features_v2.md`, `db/imprensa_perguntas.json` | **Output**: `db/career_narrative_events.json` + `docs/narrative_architecture.md`

### 1-06 `Historian`
**Persona**: `~/.claude/agents/academic/academic-historian.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Enriquecer o `db/historico.json` com contexto histórico real — campeões de GS por era, recordes históricos de tênis, rivalidades lendárias que podem inspirar o sistema de rival do jogo. Validar que datas, superfícies e formatos do calendário são historicamente plausíveis
**Input**: `db/historico.json`, `db/calendario.json` | **Output**: `docs/tennis_history_enrichment.md`

### 1-07 `Anthropologist`
**Persona**: `~/.claude/agents/academic/academic-anthropologist.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Projetar estilos de jogo culturalmente coerentes por nacionalidade — o espanhol de saibro, o australiano agressivo, o brasileiro de ritmo, o suíço técnico. Criar um sistema de `cultural_playstyle_modifier` que influencia o estilo do NPC baseado na sua origem
**Input**: `db/nomes.json`, `src/constantes.py`, `docs/audit_psychology.md` | **Output**: `docs/cultural_playstyle_matrix.md`

### 1-08 `Software Architect`
**Persona**: `~/.claude/agents/engineering/engineering-software-architect.md`
**Status**: `[ ]`
**Tarefa**: Arquitetura técnica de todas as novas features — schemas, módulos, contratos de API, plano de migração de saves antigos, dependency graph
**Input**: `docs/gdd_features_v2.md`, `docs/audit_code_quality.md`, `CLAUDE.md` | **Output**: `docs/architecture_v2.md`

### 1-09 `Geographer`
**Persona**: `~/.claude/agents/academic/academic-geographer.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Validar e enriquecer o calendário de torneios geograficamente — a "swing sul-americana" de saibro faz sentido climaticamente? Os torneios indoor de inverno europeu estão nas cidades certas? Propor um sistema de "viagem e jet lag" que influencia performance por distância percorrida
**Input**: `db/calendario.json`, `db/calendario_wta.json` | **Output**: `docs/calendar_geography_audit.md`

### 1-10 `Brand Guardian`
**Persona**: `~/.claude/agents/design/design-brand-guardian.md`
**Status**: `[ ]`
**Tarefa**: Definir identidade visual do TennisLegacy como produto — paleta neon já existe, mas falta: tom de voz, tipografia hierarquia completa, logo concept, regras de uso da marca para assets e marketing
**Input**: `docs/DESIGN_SYSTEM.md`, `Front/src/` | **Output**: `docs/brand_guidelines.md`

### 1-11 `Sprint Prioritizer`
**Persona**: `~/.claude/agents/product/product-sprint-prioritizer.md`
**Status**: `[ ]`
**Tarefa**: RICE scoring de todas as features propostas em 1-03 e 1-04 — dividir em Sprint 1 (v2), Sprint 2 (v3), Sprint 3 (v4) com justificativa por score
**Input**: `docs/gdd_features_v2.md`, `docs/product_roadmap.md` | **Output**: `docs/backlog_rice_v2.md`

### 1-12 `Senior Project Manager`
**Persona**: `~/.claude/agents/project-management/project-manager-senior.md`
**Status**: `[ ]`
**Tarefa**: Converter Sprint 1 em tasks granulares (≤4h), com ID único, agente responsável, inputs, outputs, acceptance criteria, e dependency map
**Input**: `docs/backlog_rice_v2.md`, `docs/architecture_v2.md` | **Output**: `docs/tasks_sprint1_v2.md`

---

### GATE 1 → 2
**Critério**: GDD + Arquitetura + Backlog RICE + Task list entregues
**Gate Keeper**: Studio Producer + Sprint Prioritizer
**Output**: `docs/gate_1_summary.md`

---

## FASE 2 — FUNDAÇÃO & SCAFFOLDING
> Infraestrutura e scaffolding. Sem features completas ainda.

### 2-01 `Backend Architect` (Gemini)
**Persona**: `~/.claude/agents/engineering/engineering-backend-architect.md`
**Status**: `[ ]`
**Tarefa**: Implementar novos endpoints scaffold: `rival.py`, `itf.py`, `career_events.py`; criar `src/rival_system.py`, `src/career_events.py` com structs; corrigir P0s de `audit_api_endpoints.md`
**Input**: `docs/architecture_v2.md` | **Output**: Endpoints respondendo 200 (dados vazios ok)

### 2-02 `Frontend Developer` (Claude)
**Persona**: `~/.claude/agents/engineering/engineering-frontend-developer.md`
**Status**: `[ ]`
**Tarefa**: Criar skeletons: `RivalScreen`, `RankingHistoryScreen`, `CareerEventsScreen`, `ITFScreen`; registrar rotas; adicionar métodos ao `client.ts`; links de navegação no Hub
**Input**: `docs/architecture_v2.md` | **Output**: 4 telas skeleton acessíveis

### 2-03 `UX Architect`
**Persona**: `~/.claude/agents/design/design-ux-architect.md`
**Status**: `[ ]`
**Tarefa**: Expandir o design system — adicionar: tokens para estados (empty/loading/error), escala de espaçamento consistente, breakpoints mobile documentados, classes utilitárias para componentes recorrentes
**Input**: `docs/DESIGN_SYSTEM.md`, `docs/brand_guidelines.md` | **Output**: `docs/DESIGN_SYSTEM_V2.md` + CSS tokens adicionais

### 2-04 `Database Optimizer`
**Persona**: `~/.claude/agents/engineering/engineering-database-optimizer.md`
**Status**: `[ ]`
**Tarefa**: Propor e implementar índice leve de ranking (top 100 em memória), cache de sessão para dados frequentes, esquema de migração para novos campos de save (`rival`, `career_events`, `ranking_historico`)
**Input**: `docs/audit_performance.md`, `src/save.py` | **Output**: Melhorias em `src/dados.py` + `docs/db_migration_v2.md`

### 2-05 `Data Engineer`
**Persona**: `~/.claude/agents/engineering/engineering-data-engineer.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Criar pipeline de analytics do jogo — extrair dados de `saves/*/historico_partidas.json` + `jogador.json` de múltiplos saves para análise de balanceamento. Schema: `{semana, torneio, superficie, adversario_ovr, resultado, sets, duracao_pontos}`. Salvar como `analytics/game_events.jsonl`
**Input**: `saves/*/` | **Output**: `scripts/extract_analytics.py` + schema documentado

### 2-06 `DevOps Automator`
**Persona**: `~/.claude/agents/engineering/engineering-devops-automator.md`
**Status**: `[ ]`
**Tarefa**: Configurar `pyproject.toml` com pytest + coverage mínimo 30%; criar `Makefile` completo (test, coverage, lint, format, run-api, run-frontend); criar CI workflow GitHub Actions; criar `tests/test_smoke.py` básico
**Input**: `pyproject.toml`, `requirements.txt` | **Output**: CI verde + Makefile funcional

### 2-07 `Git Workflow Master`
**Persona**: `~/.claude/agents/engineering/engineering-git-workflow-master.md`
**Status**: `[ ]`
**Tarefa**: Definir e documentar estratégia de branches para o projeto — conventional commits obrigatórios, regras de PR, policy de squash vs merge, .gitmessage template, pre-commit hooks (black, flake8)
**Input**: `.git/`, estado atual de commits | **Output**: `docs/git_workflow.md` + `.gitmessage` + `.pre-commit-config.yaml`

### 2-08 `MCP Builder`
**Persona**: `~/.claude/agents/specialized/specialized-mcp-builder.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Construir um MCP server para TennisLegacy — permite que sessões Claude interajam diretamente com o jogo via ferramentas MCP. Tools: `get_game_state()`, `advance_week()`, `get_ranking(tour)`, `simulate_match(player1, player2)`. Isso permite que agentes testem o jogo sem UI
**Input**: `api/` (FastAPI) | **Output**: `mcp_server/tennislegacy_mcp.py` + `docs/mcp_guide.md`

### 2-09 `Terminal Integration Specialist`
**Persona**: `~/.claude/agents/spatial-computing/terminal-integration-specialist.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ O TennisLegacy nasceu como jogo de terminal. Melhorar a experiência terminal Python — rich/textual para substituir prints puros, layout de placar em tempo real com refresh, cores ANSI padronizadas, cursor positioning para placar ao vivo
**Input**: `src/interface/match_info.py`, `src/interface/menu_torneio.py` | **Output**: Experiência terminal enriquecida com `rich` library

### 2-10 `Infrastructure Maintainer`
**Persona**: `~/.claude/agents/support/support-infrastructure-maintainer.md`
**Status**: `[ ]`
**Tarefa**: Configurar ambiente de desenvolvimento recomendado — Docker Compose para API + frontend, health checks, restart policies, volume mounts para saves, logging estruturado para API
**Input**: `run.sh`, `requirements.txt`, `requirements-api.txt` | **Output**: `docker-compose.yml` + `docs/dev_setup.md`

---

### GATE 2 → 3
**Critério**: CI verde + endpoints scaffold 200 + 4 telas skeleton + Docker funcional
**Gate Keeper**: DevOps Automator verifica CI + Evidence Collector captura screenshots das 4 telas
**Output**: `docs/gate_2_summary.md`

---

## FASE 3 — BUILD (6 TRACKS PARALELOS)
> Dev↔QA loop contínuo. Cada task passa por Evidence Collector/API Tester antes de avançar.
> Maximum 3 tentativas por task antes de escalação.

---

### TRACK A — Domínio do Jogo (Codex)

#### 3-A1 `Game Designer` — Sistema de Rival
**Persona**: `~/.claude/agents/game-development/game-designer.md`
**Status**: `[ ]`
**Tarefa**: Implementar `src/rival_system.py` — `detectar_rival()`, `calcular_intensidade()`, `atualizar_apos_partida()`; integrar em `avancar_semana()`; testes unitários
**Input**: `docs/gdd_features_v2.md`, `src/match_history.py` | **Output**: `src/rival_system.py` + testes

#### 3-A2 `Software Architect` — Circuito ITF/Challenger
**Persona**: `~/.claude/agents/engineering/engineering-software-architect.md`
**Status**: `[ ]`
**Tarefa**: Criar `db/calendario_itf.json`, ampliar `torneio_profile.py` com tipos ITF/Challenger, criar `src/pontuacao_itf.py`, integrar com calendário existente sem quebrar ATP
**Input**: `docs/architecture_v2.md` | **Output**: Sistema ITF funcional

#### 3-A3 `Level Designer` — Curva de progressão ITF→GS
**Persona**: `~/.claude/agents/game-development/level-designer.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Implementar o sistema de "dificuldade progressiva" por tier — calibrar o OVR dos NPCs em torneios ITF (40-55), Challenger (55-70), 250 (65-80), GS (75-95). O jogador criado com OVR 60 deve ter ~40% win rate no ITF e ~5% no GS. Ajustar `torneio_entry_config.py` para garantir essa curva
**Input**: `docs/career_progression_design.md`, `src/torneio_entry_config.py` | **Output**: NPC distributions calibradas

#### 3-A4 `Anthropologist` — Cultural Playstyle Modifier
**Persona**: `~/.claude/agents/academic/academic-anthropologist.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Implementar `src/cultural_playstyle.py` — mapa de `{nacionalidade: {bonus_saibro, bonus_saque, estilo_preferido}}` baseado em `docs/cultural_playstyle_matrix.md`. Integrar em NPC generation para dar personalidade cultural aos jogadores
**Input**: `docs/cultural_playstyle_matrix.md`, `src/gerador_nomes.py` | **Output**: `src/cultural_playstyle.py`

---

### TRACK B — Frontend (Claude)

#### 3-B1 `Frontend Developer` — 4 novas telas completas
**Persona**: `~/.claude/agents/engineering/engineering-frontend-developer.md`
**Status**: `[ ]`
**Tarefa**: Implementar completamente: `RivalScreen` (H2H animado, próximos confrontos, badge pulsante), `RankingHistoryScreen` (gráfico de linha temporal), `CareerEventsScreen` (timeline vertical), `ITFScreen` (calendário por tier)
**Input**: `docs/tasks_sprint1_v2.md` + APIs de 2-01 | **Output**: 4 telas funcionais com dados reais

#### 3-B2 `UI Designer` — Componentes padronizados
**Persona**: `~/.claude/agents/design/design-ui-designer.md`
**Status**: `[ ]`
**Tarefa**: Criar `EmptyState`, `SkeletonLoader`, `StatBadge`, `TimelineEvent`, `ProgressRing`, `RivalBadge`, `TierBadge` (ITF/CH/ATP/GS); garantir conformidade com `DESIGN_SYSTEM_V2.md`
**Input**: `docs/DESIGN_SYSTEM_V2.md`, `docs/brand_guidelines.md` | **Output**: 7 componentes em `Front/src/app/components/`

#### 3-B3 `Whimsy Injector` — Micro-interações e deleite
**Persona**: `~/.claude/agents/design/design-whimsy-injector.md`
**Status**: `[ ]`
**Tarefa**: Confetti pixel-art em GS wins; shake screen em break points decisivos; neon pulse em level up; ticker animado de "NOVO RIVAL" ao cristalizar rivalidade; easter egg no logo; partícula de bola ao vencer set
**Input**: `docs/audit_ux_flows.md` | **Output**: Animações em `motion/react` < 2KB gzip

#### 3-B4 `Visual Storyteller`
**Persona**: `~/.claude/agents/design/design-visual-storyteller.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Projetar a linguagem visual da CareerEventsScreen e WeekAdvanceScreen — ícones por tipo de evento (🏆 titulo, ⚔️ rival, 💪 recorde, 🤕 lesão), paleta cromática por intensidade emocional (vitória GS = dourado, derrota rival = vermelho escuro), hierarquia de legibilidade para as notícias semanais
**Input**: `docs/brand_guidelines.md`, `docs/narrative_architecture.md` | **Output**: Visual language spec + implementação nas 2 telas

#### 3-B5 `Technical Artist`
**Persona**: `~/.claude/agents/game-development/technical-artist.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Projetar performance budget para todas as animações do frontend — definir: max 60fps em dispositivos médios, quais animações são skiped em low-power mode, substituição de animações complexas por CSS simples quando necessário. Implementar `prefers-reduced-motion` para acessibilidade
**Input**: `docs/audit_performance.md`, componentes de 3-B3 | **Output**: Performance audit + `prefers-reduced-motion` implementado

#### 3-B6 `Accessibility Auditor`
**Persona**: `~/.claude/agents/testing/testing-accessibility-auditor.md`
**Status**: `[ ]`
**Tarefa**: Auditoria WCAG 2.1 AA — contraste de cores neon (verde #00ff88 em fundo #0a0a0a passa? ratio 4.5:1?), keyboard navigation em todas as telas, ARIA labels em botões sem texto, focus states visíveis
**Input**: `Front/src/`, `docs/DESIGN_SYSTEM_V2.md` | **Output**: `docs/accessibility_report.md` + fixes

---

### TRACK C — Backend (Gemini)

#### 3-C1 `Backend Architect` — Career Events + Ranking Histórico
**Persona**: `~/.claude/agents/engineering/engineering-backend-architect.md`
**Status**: `[ ]`
**Tarefa**: `GET /api/jogador/career-events` + `POST /dismiss/{id}` + `GET /api/jogador/ranking-historico`; integrar career events em `avancar_semana()`; persistência no save
**Input**: `db/career_narrative_events.json`, `docs/architecture_v2.md` | **Output**: 3 endpoints funcionais

#### 3-C2 `AI Engineer` — Match Commentary Engine
**Persona**: `~/.claude/agents/engineering/engineering-ai-engineer.md`
**Status**: `[ ]`
**Tarefa**: `src/match_commentary.py` — 100+ templates de comentário por contexto (ace, winner, erro, break, match point, rival present, superfície, momentum streak). Sem API externa — templates locais com variação pseudo-aleatória contextual
**Input**: `src/simulacao_partida.py`, `docs/audit_match_model.md` | **Output**: `src/match_commentary.py` + integração no runtime

#### 3-C3 `AI Data Remediation Engineer`
**Persona**: `~/.claude/agents/engineering/engineering-ai-data-remediation-engineer.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Criar `scripts/remediate_saves.py` — detecta e corrige anomalias em saves: rankings negativos, jogadores com OVR > 100, saves com `temporada.semana` > 52, `energia` > 100, `fadiga` < 0, atributos ausentes. Auto-repair com logging de cada correção
**Input**: `src/migracoes.py`, `saves/*/` | **Output**: `scripts/remediate_saves.py` + `docs/data_anomalies_found.md`

#### 3-C4 `Autonomous Optimization Architect`
**Persona**: `~/.claude/agents/engineering/engineering-autonomous-optimization-architect.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Implementar shadow testing do endpoint `/api/partida/ponto` — executar 100 simulações em background e medir: p50/p95/p99, taxa de erro, outliers > 500ms. Gerar alert se p95 > 300ms. Implementar como `scripts/shadow_test_partida.py` com relatório automático
**Input**: `docs/audit_performance.md` | **Output**: `scripts/shadow_test_partida.py` + dashboard em `docs/performance_live.md`

---

### TRACK D — Qualidade Contínua

#### 3-D1 `API Tester` — Validação contínua
**Persona**: `~/.claude/agents/testing/testing-api-tester.md`
**Status**: `[ ]`
**Ativado por**: Cada endpoint novo/alterado | **Output**: `docs/api_test_results.md` atualizado

#### 3-D2 `Evidence Collector` — QA visual
**Persona**: `~/.claude/agents/testing/testing-evidence-collector.md`
**Status**: `[ ]`
**Ativado por**: Cada tela frontend completa
**Verifica**: normal / vazio / loading / erro / mobile (320px/768px/1280px)
**Default**: NEEDS WORK | **Output**: `docs/evidence_screenshots/`

#### 3-D3 `Performance Benchmarker` — Monitoramento
**Persona**: `~/.claude/agents/testing/testing-performance-benchmarker.md`
**Status**: `[ ]`
**Ativado por**: Cada endpoint novo
**Verifica**: p95 < 300ms, nenhuma chamada > 1s em condições normais

#### 3-D4 `Experiment Tracker`
**Persona**: `~/.claude/agents/project-management/project-management-experiment-tracker.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Configurar framework de A/B testing para mecânicas do jogo — ex: "rival badge no bracket aumenta engagement com o recurso rival?", "timer de 10s vs 15s entre sets: qual resulta em mais jogos completos?". Implementar feature flags em `src/constantes.py` para habilitar/desabilitar variantes
**Input**: `docs/gdd_features_v2.md` | **Output**: `src/feature_flags.py` + `docs/ab_tests_setup.md`

---

### TRACK E — Conteúdo & Assets

#### 3-E1 `Narrative Designer` — Implementação dos eventos
**Persona**: `~/.claude/agents/game-development/narrative-designer.md`
**Status**: `[ ]`
**Tarefa**: Implementar `src/career_events.py` — detector de triggers, avaliador de condições, formatador de texto com variáveis, integração com sistema de imprensa existente
**Input**: `db/career_narrative_events.json`, `src/imprensa.py` | **Output**: `src/career_events.py` funcional

#### 3-E2 `Narratologist`
**Persona**: `~/.claude/agents/academic/academic-narratologist.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Aplicar teoria narrativa (Propp, Campbell, três-atos) ao arco de carreira — verificar se a sequência de eventos de carreira forma uma narrativa coerente do herói. Identificar onde falta: tensão crescente (sem eventos durante semanas 20-35?), climax (GS win não tem escalada suficiente?), resolução (pós-aposentadoria)
**Input**: `db/career_narrative_events.json`, `docs/narrative_architecture.md` | **Output**: `docs/narrative_review.md` + ajustes nos eventos

#### 3-E3 `Image Prompt Engineer`
**Persona**: `~/.claude/agents/design/design-image-prompt-engineer.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Criar prompts detalhados para gerar via IA: player card art (estilo pixel neon), tournament posters (Grand Slam vs Challenger), career milestone trophy images, rival badge icons, court backgrounds por superfície (clay vermelho intenso, grass verde profundo, hard azul neon)
**Input**: `docs/brand_guidelines.md` | **Output**: `docs/asset_generation_prompts.md` com 30+ prompts prontos

#### 3-E4 `Inclusive Visuals Specialist`
**Persona**: `~/.claude/agents/design/design-inclusive-visuals-specialist.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Auditar a representação global nos NPCs — há diversidade de nationalidades no top 50? Estereótipos culturais nas habilidades (ex: NPCs brasileiros são automaticamente especialistas em saibro?)? Verificar que nomes gerados por `gerador_nomes.py` não criam combinações inadvertidamente problemáticas
**Input**: `db/ranking_atp.json`, `src/gerador_nomes.py`, `docs/cultural_playstyle_matrix.md` | **Output**: `docs/inclusivity_audit.md` + correções

#### 3-E5 `Document Generator`
**Persona**: `~/.claude/agents/specialized/specialized-document-generator.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Implementar geração de documentos PDF em-jogo — "Certificado de Campeão" ao vencer GS (com nome, torneio, data, adversário na final), "Relatório de Temporada" ao final das 52 semanas (estatísticas, gráfico de ranking, highlights). Usar `reportlab` ou `fpdf2`
**Input**: `src/jogador.py`, `src/pontuacao.py` | **Output**: `src/document_generator.py` + templates PDF

#### 3-E6 `Cultural Intelligence Strategist`
**Persona**: `~/.claude/agents/specialized/specialized-cultural-intelligence-strategist.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Revisar todos os textos de interface — nomes de torneios estão localizados corretamente? Formatos de data/hora são internacionais? Mensagens de imprensa evitam clichês culturais? O sistema de "reputação por país" (Copa Davis) não favorece implicitamente nações específicas?
**Input**: `src/interface/`, `db/imprensa_perguntas.json` | **Output**: `docs/cultural_review.md` + fixes

---

### TRACK F — Ferramentas & Infraestrutura Avançada

#### 3-F1 `LSP/Index Engineer`
**Persona**: `~/.claude/agents/specialized/lsp-index-engineer.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Criar índice semântico do codebase Python — mapa de todas as funções, suas dependências, quem chama quem. Útil para navegação em `torneio_core.py` (3685 linhas), `jogar_partida.py` (1605 linhas). Implementar como `scripts/generate_code_index.py` que produz `docs/code_index.json`
**Input**: `src/` | **Output**: `scripts/generate_code_index.py` + `docs/code_index.json`

#### 3-F2 `Blender Addon Engineer`
**Persona**: `~/.claude/agents/game-development/blender/blender-addon-engineer.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Criar um script Python para visualizar brackets de torneio como grafo — usando `networkx` + `matplotlib` (mesma abordagem que Blender add-ons usam para pipelines de dados), gera imagem PNG do bracket atual. Útil para debug e screenshots de marketing
**Input**: `src/torneio_core.py` (estrutura do bracket) | **Output**: `scripts/visualize_bracket.py`

#### 3-F3 `Game Audio Engineer`
**Persona**: `~/.claude/agents/game-development/game-audio-engineer.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Projetar sistema de áudio para o frontend web — usando Web Audio API, criar: sons para ace (crowd cheer), winner (ball hit + cheer), break point (tense music sting), GS win (crowd roar). Implementar como `Front/src/hooks/useMatchAudio.ts` com volume control e mute option. Usar Web Audio API synth (não samples externos)
**Input**: `Front/src/app/screens/MatchScreen.tsx` | **Output**: `Front/src/hooks/useMatchAudio.ts` + integração

#### 3-F4 `Rapid Prototyper`
**Persona**: `~/.claude/agents/engineering/engineering-rapid-prototyper.md`
**Status**: `[ ]`
**Tarefa**: Criar POC rápido de 3 features "maybe" do backlog — testar viabilidade antes do investimento completo. Candidatos: (1) replay de pontos em ASCII art, (2) modo "career manager" controlando NPC, (3) exportar save para CSV para análise externa
**Input**: `docs/backlog_rice_v2.md` (items com C < 0.7) | **Output**: 3 POCs em `tmp/prototypes/` com verdict viability

---

### GATE 3 → 4
**Critério**: Todas as tasks `[x]`, zero 500s, coverage ≥ 30%, Evidence Collector screenshots completos
**Gate Keeper**: Agents Orchestrator (Claude session ativa)
**Output**: `docs/gate_3_summary.md`

---

## FASE 4 — HARDENING & QA FINAL
> A Reality Checker parte de NEEDS WORK. Provar com evidências esmagadoras.

### 4-01 `Reality Checker`
**Persona**: `~/.claude/agents/testing/testing-reality-checker.md`
**Status**: `[ ]`
**Default**: NEEDS WORK
**Critérios para READY**: user journeys completos, zero 500s, coverage ≥ 30%, black passa, screenshots de todos os estados, p95 < 300ms, rival funciona, ITF funciona, career events disparam

### 4-02 `Code Reviewer` — Review final
**Persona**: `~/.claude/agents/engineering/engineering-code-reviewer.md`
**Status**: `[ ]`
**Tarefa**: Review de TODO código novo de Fase 3 — sem secrets, sem SQL/JSON injection, sem XSS, black passa, sem dead code introduzido
**Output**: `docs/review_final.md`

### 4-03 `SRE`
**Persona**: `~/.claude/agents/engineering/engineering-sre.md`
**Status**: `[ ]`
**Tarefa**: Definir SLOs informais — uptime > 99% (API local), p95 `/partida/ponto` < 300ms, zero perda de dados em `salvar_json_seguro()`. Verificar: todos os novos endpoints têm timeout, novos `useEffect` têm cleanup, sem memory leaks
**Output**: `docs/slo_definition.md`

### 4-04 `Test Results Analyzer`
**Persona**: `~/.claude/agents/testing/testing-test-results-analyzer.md`
**Status**: `[ ]`
**Tarefa**: Agregar todos os resultados: pytest coverage, API test results, performance benchmarks, accessibility report, cultural review — produzir dashboard de qualidade
**Output**: `docs/quality_dashboard.md`

### 4-05 `Security Engineer` — Revisão final
**Persona**: `~/.claude/agents/engineering/engineering-security-engineer.md`
**Status**: `[ ]`
**Tarefa**: Verificar que todos os issues de `audit_security.md` foram corrigidos; testar novos endpoints para path traversal; verificar que `nome_save` é sanitizado em TODOS os novos arquivos
**Output**: `docs/security_clearance.md`

### 4-06 `Legal Compliance Checker`
**Persona**: `~/.claude/agents/support/support-legal-compliance-checker.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Verificar: saves contêm dados que podem ser PII? (nome do jogador criado pelo usuário). Se o jogo for publicado online, GDPR implica: direito de apagar dados (delete save ✓), não exportar dados sem consentimento. Verificar licenças de todas as dependências Python e npm para uso comercial
**Output**: `docs/legal_compliance.md`

### 4-07 `Workflow Optimizer` — Processo final
**Persona**: `~/.claude/agents/testing/testing-workflow-optimizer.md`
**Status**: `[ ]`
**Tarefa**: Revisar processo de desenvolvimento pós-sprint — o que foi manual e poderia ser automatizado? Quais passos do dev workflow foram gargalo? Propor melhorias para Sprint 2
**Output**: `docs/workflow_improvements.md`

### 4-08 `Model QA Specialist` — Validação pós-features
**Persona**: `~/.claude/agents/specialized/specialized-model-qa.md`
**Status**: `[ ]`
**Tarefa**: Revalidar modelo de simulação com as novas features ativas — ITF NPCs têm distribuição correta? Cultural modifiers não criam desequilíbrio? Win rate do jogador curioso após rival system
**Output**: `docs/model_validation_post_build.md`

### 4-09 `Accessibility Auditor` — Validação final
**Persona**: `~/.claude/agents/testing/testing-accessibility-auditor.md`
**Status**: `[ ]`
**Tarefa**: Reauditar WCAG nas novas telas e componentes — verificar que todas as correções de 3-B6 foram aplicadas e que novos componentes cumprem AA
**Output**: `docs/accessibility_final.md`

### 4-10 `Automation Governance Architect`
**Persona**: `~/.claude/agents/specialized/automation-governance-architect.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Auditar o sistema de simulação NPC (`tournament_manager.py`, `torneio_core.py`) — a automação de torneios mundiais semanais é: auditável (logs suficientes?), determinística (seed fixa?), reversível (pode desfazer uma semana?)? Identificar riscos de estado corrompido em simulações longas
**Output**: `docs/automation_governance.md`

### 4-11 `Tool Evaluator`
**Persona**: `~/.claude/agents/testing/testing-tool-evaluator.md`
**Status**: `[ ]`
**Tarefa**: Avaliar ferramentas para Sprint 2 — comparar: pytest-benchmark vs locust para load testing, recharts vs d3 vs css puro para gráficos, Playwright vs Cypress para E2E frontend. Recommendation report
**Output**: `docs/tools_evaluation_sprint2.md`

---

### GATE 4 → 5
**Critério**: Reality Checker emite READY
**Gate Keeper**: Reality Checker (sole authority)

---

## FASE 5 — RELEASE & LANÇAMENTO
> Documentar, mergear, publicar, comunicar.

### 5-01 `Technical Writer`
**Persona**: `~/.claude/agents/engineering/engineering-technical-writer.md`
**Status**: `[ ]`
**Tarefa**: Atualizar `README.MD` (setup completo), `CLAUDE.md` (novos módulos), criar `docs/api_reference.md` (todos endpoints + schemas), atualizar `docs/saves.md` (novos campos)
**Output**: Documentação precisa e navegável

### 5-02 `DevOps Automator` — Deploy
**Persona**: `~/.claude/agents/engineering/engineering-devops-automator.md`
**Status**: `[ ]`
**Tarefa**: Verificar CI verde, criar PR `feat/frontend` → `main` com description completa, após merge criar tag `v2.0.0` com changelog
**Output**: PR merged + tag criada

### 5-03 `Jira Workflow Steward`
**Persona**: `~/.claude/agents/project-management/project-management-jira-workflow-steward.md`
**Status**: `[ ]`
**Tarefa**: Garantir que todos os commits seguem conventional commits, PR tem linked tasks, changelog está gerado automaticamente. Criar template de PR para o repositório
**Output**: `.github/pull_request_template.md` + changelog

### 5-04 `Executive Summary Generator`
**Persona**: `~/.claude/agents/support/support-executive-summary-generator.md`
**Status**: `[ ]`
**Tarefa**: Produzir `docs/sprint_retrospective_v2.md` — o que foi entregue, métricas de qualidade, dívida técnica restante, recomendações Sprint 3. Formato SCQA ≤ 600 palavras
**Output**: `docs/sprint_retrospective_v2.md`

### 5-05 `Developer Advocate`
**Persona**: `~/.claude/agents/specialized/specialized-developer-advocate.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Criar materiais para open source community — CONTRIBUTING.md detalhado, "good first issue" labels, roadmap público, arquitetura explicada em termos acessíveis para novos contributors. TennisLegacy como showcase de Python + FastAPI + React
**Output**: `CONTRIBUTING.md` + issue templates + `docs/ARCHITECTURE_OVERVIEW.md`

### 5-06 `Content Creator`
**Persona**: `~/.claude/agents/marketing/marketing-content-creator.md`
**Status**: `[ ]`
**Tarefa**: Criar 5 peças de conteúdo para o lançamento v2 — devlog post "Building a Tennis Career Simulator", Twitter thread com features highlights, LinkedIn post técnico, Reddit post em r/gamedev e r/indiegaming, itch.io page copy
**Output**: `docs/launch_content.md` com os 5 drafts prontos

### 5-07 `Social Media Strategist`
**Persona**: `~/.claude/agents/marketing/marketing-social-media-strategist.md`
**Status**: `[ ]`
**Tarefa**: Calendário de conteúdo de lançamento — 2 semanas de posts coordenados em Twitter/X, Reddit, LinkedIn. Timing, tom por plataforma, hashtags (#indiedev, #gamedev, #sportsim, #tennismanager)
**Output**: `docs/social_calendar.md`

### 5-08 `Reddit Community Builder`
**Persona**: `~/.claude/agents/marketing/marketing-reddit-community-builder.md`
**Status**: `[ ]`
**Tarefa**: Estratégia de lançamento em Reddit — identificar subreddits relevantes (r/gamedev, r/indiegaming, r/tennis, r/footballmanagergames), planejar posts autênticos com valor real (não spam), criar r/TennisLegacy se audience justificar
**Output**: `docs/reddit_strategy.md`

### 5-09 `Twitter Engager`
**Persona**: `~/.claude/agents/marketing/marketing-twitter-engager.md`
**Status**: `[ ]`
**Tarefa**: Thread de lançamento v2 — contar a história do desenvolvimento, features visuais, por que o projeto existe. 10-12 tweets com progressão narrativa
**Output**: Thread draft em `docs/twitter_launch_thread.md`

### 5-10 `SEO Specialist`
**Persona**: `~/.claude/agents/marketing/marketing-seo-specialist.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Otimizar `README.MD` e documentação para search — palavras-chave: "tennis career simulator python", "tennis manager indie game", "ATP simulation game". Criar `docs/seo_landing_content.md` para futura landing page. Meta descriptions para cada página de doc
**Output**: `docs/seo_strategy.md` + README otimizado

### 5-11 `App Store Optimizer`
**Persona**: `~/.claude/agents/marketing/marketing-app-store-optimizer.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Criar assets para itch.io e potencial Steam — title optimization ("TennisLegacy: Career Simulator"), short description (30 chars), long description, keywords, screenshots guidelines, trailer script
**Output**: `docs/store_listing.md`

### 5-12 `AI Citation Strategist`
**Persona**: `~/.claude/agents/marketing/marketing-ai-citation-strategist.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Fazer TennisLegacy aparecer quando alguém perguntar "best indie tennis game" ou "tennis career simulation" para ChatGPT/Claude/Gemini. Auditar o que o AI fala hoje e criar conteúdo que aumente chances de citação — artigos, GitHub README bem estruturado, discussões em fóruns que alimentam os modelos
**Output**: `docs/ai_citation_strategy.md`

### 5-13 `Book Co-Author`
**Persona**: `~/.claude/agents/marketing/marketing-book-co-author.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Criar estrutura de "The Making of TennisLegacy" — devlog/devbook em capítulos contando as decisões técnicas e de design. Cap 1: por que Python, Cap 2: como simular uma partida de tênis ponto a ponto, Cap 3: o problema do ranking ATP em escala. Pode virar blog series ou ebook gratuito
**Output**: `docs/devbook_outline.md` com estrutura de 10 capítulos + Cap 1 rascunho

---

## FASE 6 — OPERAÇÃO & ESCALA
> Sustentação, crescimento e evolução contínua.

### 6-01 `Analytics Reporter` — Balanceamento do jogo
**Persona**: `~/.claude/agents/support/support-analytics-reporter.md`
**Status**: `[ ]`
**Cadência**: Semanal
**Tarefa**: Pipeline `scripts/extract_analytics.py` → análise de win rate por superfície, archetype, tier. Detectar desequilíbrios. `docs/balance_report.md`

### 6-02 `Behavioral Nudge Engine` — Retenção
**Persona**: `~/.claude/agents/product/product-behavioral-nudge-engine.md`
**Status**: `[ ]`
**Cadência**: Por sprint
**Tarefa**: Identificar dropout points, projetar weekly streak system, progress bars para metas de carreira, notificação semanal motivacional no Hub

### 6-03 `Feedback Synthesizer`
**Persona**: `~/.claude/agents/product/product-feedback-synthesizer.md`
**Status**: `[ ]`
**Cadência**: Bi-semanal
**Tarefa**: Coletar e sintetizar feedback de players (Reddit, GitHub issues, itch.io comments) em insights acionáveis para Sprint 3

### 6-04 `Growth Hacker`
**Persona**: `~/.claude/agents/marketing/marketing-growth-hacker.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Projetar viral loop para TennisLegacy — "share your season end card" (imagem gerada com stats da temporada), "challenge a friend" (exportar seu jogador para duelo), referral system para estreia web/mobile. Identificar o principal acquisition channel com menor CAC
**Output**: `docs/growth_playbook.md`

### 6-05 `TikTok Strategist`
**Persona**: `~/.claude/agents/marketing/marketing-tiktok-strategist.md`
**Status**: `[ ]`
**Tarefa**: Estratégia de clips de gameplay — "POV: você está no match point do seu primeiro Grand Slam", "ranking 500 → top 10 em uma temporada", storytelling de carreira. Hook nos primeiros 3 segundos
**Output**: `docs/tiktok_strategy.md`

### 6-06 `Short-Video Editing Coach`
**Persona**: `~/.claude/agents/marketing/marketing-short-video-editing-coach.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Guia de edição para gameplay highlights — como capturar a MatchScreen, editar com CapCut os momentos de tensão, adicionar música de fundo, legendas de placar. Guia específico para TennisLegacy com exemplos de timing
**Output**: `docs/video_editing_guide.md`

### 6-07 `Instagram Curator`
**Persona**: `~/.claude/agents/marketing/marketing-instagram-curator.md`
**Status**: `[ ]`
**Tarefa**: Grid aesthetic para TennisLegacy no Instagram — posts de screenshots do jogo com visual neon consistente, reels de gameplay, stories com "did you know" sobre tennis history. 30-post visual calendar
**Output**: `docs/instagram_calendar.md`

### 6-08 `LinkedIn Content Creator`
**Persona**: `~/.claude/agents/marketing/marketing-linkedin-content-creator.md`
**Status**: `[ ]`
**Tarefa**: Série de posts técnicos no LinkedIn — "How I built a point-by-point tennis simulator in Python", "Why FastAPI was the right choice for a real-time game backend", "Building a 2000-player ranking system". Atrai developers e potential contributors
**Output**: `docs/linkedin_series.md`

### 6-09 `Podcast Strategist`
**Persona**: `~/.claude/agents/marketing/marketing-podcast-strategist.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Estruturar "The TennisLegacy Podcast" ou identificar podcasts existentes (gamedev, sports sim, indie dev) para pitch de participação. Episodes: "Simulating 52 weeks of professional tennis", "The hardest bug I ever fixed: ranking corruption"
**Output**: `docs/podcast_strategy.md`

### 6-10 `Mobile App Builder`
**Persona**: `~/.claude/agents/engineering/engineering-mobile-app-builder.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Avaliar viabilidade de port para React Native — quais telas se adaptam bem a mobile, quais precisam reprojeto, qual seria a estratégia de monetização (free + premium saves, one-time purchase). Produzir feasibility report sem implementar ainda
**Output**: `docs/mobile_feasibility.md`

### 6-11 `Finance Tracker`
**Persona**: `~/.claude/agents/support/support-finance-tracker.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Modelar opções de monetização — itch.io "pay what you want" baseline, Patreon para features prioritization, mobile one-time purchase. Projetar breakeven e ROI esperado por canal. Também: tracking de custos do projeto (APIs, hosting se for web)
**Output**: `docs/monetization_model.md`

### 6-12 `Sales Outbound Strategist`
**Persona**: `~/.claude/agents/sales/sales-outbound-strategist.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Identificar editoras indie e plataformas que distribuem jogos de simulação esportiva — quem publicou Football Manager, Tennis Manager, etc. Criar lista de targets com ICP, pitch angle por publisher, sequência de outreach
**Output**: `docs/publisher_outreach.md`

### 6-13 `Proposal Strategist`
**Persona**: `~/.claude/agents/sales/sales-proposal-strategist.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Criar pitch deck de 10 slides para potenciais publishers/investidores — problem (sem tennis career sim indie), solution (TennisLegacy), traction (users/downloads), tech (Python + React, extensível), ask (X para mobile port + marketing)
**Output**: `docs/pitch_deck_outline.md` + slide 1-3 rascunhados

### 6-14 `Support Responder`
**Persona**: `~/.claude/agents/support/support-support-responder.md`
**Status**: `[ ]`
**Tarefa**: Criar `docs/FAQ.md` para players — bugs frequentes (save corrompido, torneio travado), perguntas de gameplay (como funciona o rival, quando aparece ITF), troubleshooting da API local
**Output**: `docs/FAQ.md` + template de resposta para issues no GitHub

### 6-15 `Incident Response Commander`
**Persona**: `~/.claude/agents/engineering/engineering-incident-response-commander.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Criar runbook de incidentes para TennisLegacy — o que fazer quando: save corrompido mid-session, API trava no `/partida/ponto`, ranking ficou inconsistente após update, torneio em estado inválido. Severidade P0/P1/P2 com passos de recovery
**Output**: `docs/incident_runbook.md`

### 6-16 `Pipeline Analyst`
**Persona**: `~/.claude/agents/sales/sales-pipeline-analyst.md`
**Status**: `[ ]`
**Tarefa**: ⚠️ Adaptar pipeline analytics para player acquisition — funnel: descobriu o jogo → baixou → criou save → completou primeiro torneio → voltou na semana 2 → atingiu rank 100. Identificar onde o funil tem maior drop. Usar dados de analytics de 6-01
**Output**: `docs/player_funnel_analysis.md`

---

## OPERAÇÃO CONTÍNUA — GOVERNANÇA & CONHECIMENTO
> Agentes que rodam permanentemente, não vinculados a uma fase.

### C-01 `ZK Steward`
**Persona**: `~/.claude/agents/specialized/zk-steward.md`
**Status**: `[ ]`
**Cadência**: Contínua
**Tarefa**: ⚠️ Construir Zettelkasten de decisões de design do TennisLegacy — cada decisão arquitetural importante vira uma nota atômica linkada: "Por que Python e não Node?", "Por que shards e não banco de dados?", "Por que pontuação ATP e não sistema próprio?". Permite onboarding de novos contributors e evita re-debater o que já foi decidido
**Output**: `docs/zettelkasten/` com notas linkadas

### C-02 `Identity Graph Operator`
**Persona**: `~/.claude/agents/specialized/identity-graph-operator.md`
**Status**: `[ ]`
**Cadência**: Por sessão de desenvolvimento
**Tarefa**: ⚠️ Resolver identidade de jogadores NPC que aparecem com nomes levemente diferentes em arquivos diferentes — "Carlos Alcaraz", "C. Alcaraz", "Alcaraz C." deveriam ser o mesmo. Criar `scripts/resolve_npc_identity.py` que normaliza e deduplica jogadores no `db/ranking_atp.json`
**Output**: `scripts/resolve_npc_identity.py` + relatório de duplicatas resolvidas

### C-03 `Workflow Architect`
**Persona**: `~/.claude/agents/specialized/specialized-workflow-architect.md`
**Status**: `[ ]`
**Cadência**: Por sprint
**Tarefa**: ⚠️ Mapear TODOS os workflows do jogo como árvores completas — fluxo semanal (hub → inscricao → torneio → partida → resultado → progressao), fluxo de save (criar → carregar → salvar → migrar), fluxo de ranking (adicionar pontos → ordenar → expirar). Cobrir happy paths, branches, failure modes e recovery. Produzir spec que serve como referência para testes
**Output**: `docs/workflow_trees/` com 8 diagramas de workflow

### C-04 `Project Shepherd`
**Persona**: `~/.claude/agents/project-management/project-management-project-shepherd.md`
**Status**: `[ ]`
**Cadência**: Por sprint
**Tarefa**: Monitorar progresso geral do pipeline NEXUS, identificar blockers entre fases, garantir que handoffs acontecem com contexto completo, atualizar stakeholders (usuário) em cada milestone
**Output**: Weekly status report em `docs/sprint_status.md`

---

## TABELA DE TODOS OS 102 AGENTS

| # | Agent | Divisão | Fase | Status |
|---|-------|---------|------|--------|
| 1 | Code Reviewer | Engineering | F0 + F4 | `[ ]` |
| 2 | API Tester | Testing | F0 + F3-D + F4 | `[ ]` |
| 3 | Performance Benchmarker | Testing | F0 + F3-D + F4 | `[ ]` |
| 4 | UX Researcher | Design | F0 | `[ ]` |
| 5 | Security Engineer | Engineering | F0 + F4 | `[ ]` |
| 6 | Model QA Specialist | Specialized | F0 + F4 | `[ ]` |
| 7 | Trend Researcher | Product | F0 | `[ ]` |
| 8 | Workflow Optimizer | Testing | F0 | `[ ]` |
| 9 | Psychologist | Academic | F0 | `[ ]` |
| 10 | Studio Producer | PM | F1 | `[ ]` |
| 11 | Product Manager | Product | F1 | `[ ]` |
| 12 | Game Designer | Game Dev | F1 + F3-A | `[ ]` |
| 13 | Level Designer | Game Dev | F1 + F3-A | `[ ]` |
| 14 | Narrative Designer | Game Dev | F1 + F3-E | `[ ]` |
| 15 | Historian | Academic | F1 | `[ ]` |
| 16 | Anthropologist | Academic | F1 + F3-A | `[ ]` |
| 17 | Software Architect | Engineering | F1 + F3-A | `[ ]` |
| 18 | Geographer | Academic | F1 | `[ ]` |
| 19 | Brand Guardian | Design | F1 | `[ ]` |
| 20 | Sprint Prioritizer | Product | F1 | `[ ]` |
| 21 | Senior Project Manager | PM | F1 | `[ ]` |
| 22 | Backend Architect | Engineering | F2 + F3-C | `[ ]` |
| 23 | Frontend Developer | Engineering | F2 + F3-B | `[ ]` |
| 24 | UX Architect | Design | F2 | `[ ]` |
| 25 | Database Optimizer | Engineering | F2 | `[ ]` |
| 26 | Data Engineer | Engineering | F2 | `[ ]` |
| 27 | DevOps Automator | Engineering | F2 + F5 | `[ ]` |
| 28 | Git Workflow Master | Engineering | F2 | `[ ]` |
| 29 | MCP Builder | Specialized | F2 | `[ ]` |
| 30 | Terminal Integration Specialist | Spatial | F2 | `[ ]` |
| 31 | Infrastructure Maintainer | Support | F2 | `[ ]` |
| 32 | Level Designer (3-A3) | Game Dev | F3-A | `[ ]` |
| 33 | Anthropologist (3-A4) | Academic | F3-A | `[ ]` |
| 34 | AI Engineer | Engineering | F3-C | `[ ]` |
| 35 | AI Data Remediation Engineer | Engineering | F3-C | `[ ]` |
| 36 | Autonomous Optimization Architect | Engineering | F3-C | `[ ]` |
| 37 | UI Designer | Design | F3-B | `[ ]` |
| 38 | Whimsy Injector | Design | F3-B | `[ ]` |
| 39 | Visual Storyteller | Design | F3-B | `[ ]` |
| 40 | Technical Artist | Game Dev | F3-B | `[ ]` |
| 41 | Accessibility Auditor | Testing | F3-B + F4 | `[ ]` |
| 42 | Evidence Collector | Testing | F3-D | `[ ]` |
| 43 | Experiment Tracker | PM | F3-D | `[ ]` |
| 44 | Narratologist | Academic | F3-E | `[ ]` |
| 45 | Image Prompt Engineer | Design | F3-E | `[ ]` |
| 46 | Inclusive Visuals Specialist | Design | F3-E | `[ ]` |
| 47 | Document Generator | Specialized | F3-E | `[ ]` |
| 48 | Cultural Intelligence Strategist | Specialized | F3-E | `[ ]` |
| 49 | LSP/Index Engineer | Specialized | F3-F | `[ ]` |
| 50 | Blender Addon Engineer | Game Dev | F3-F | `[ ]` |
| 51 | Game Audio Engineer | Game Dev | F3-F | `[ ]` |
| 52 | Rapid Prototyper | Engineering | F3-F | `[ ]` |
| 53 | Reality Checker | Testing | F4 | `[ ]` |
| 54 | SRE | Engineering | F4 | `[ ]` |
| 55 | Test Results Analyzer | Testing | F4 | `[ ]` |
| 56 | Legal Compliance Checker | Support | F4 | `[ ]` |
| 57 | Automation Governance Architect | Specialized | F4 | `[ ]` |
| 58 | Tool Evaluator | Testing | F4 | `[ ]` |
| 59 | Technical Writer | Engineering | F5 | `[ ]` |
| 60 | Jira Workflow Steward | PM | F5 | `[ ]` |
| 61 | Executive Summary Generator | Support | F5 | `[ ]` |
| 62 | Developer Advocate | Specialized | F5 | `[ ]` |
| 63 | Content Creator | Marketing | F5 | `[ ]` |
| 64 | Social Media Strategist | Marketing | F5 | `[ ]` |
| 65 | Reddit Community Builder | Marketing | F5 | `[ ]` |
| 66 | Twitter Engager | Marketing | F5 | `[ ]` |
| 67 | SEO Specialist | Marketing | F5 | `[ ]` |
| 68 | App Store Optimizer | Marketing | F5 | `[ ]` |
| 69 | AI Citation Strategist | Marketing | F5 | `[ ]` |
| 70 | Book Co-Author | Marketing | F5 | `[ ]` |
| 71 | Analytics Reporter | Support | F6 | `[ ]` |
| 72 | Behavioral Nudge Engine | Product | F6 | `[ ]` |
| 73 | Feedback Synthesizer | Product | F6 | `[ ]` |
| 74 | Growth Hacker | Marketing | F6 | `[ ]` |
| 75 | TikTok Strategist | Marketing | F6 | `[ ]` |
| 76 | Short-Video Editing Coach | Marketing | F6 | `[ ]` |
| 77 | Instagram Curator | Marketing | F6 | `[ ]` |
| 78 | LinkedIn Content Creator | Marketing | F6 | `[ ]` |
| 79 | Podcast Strategist | Marketing | F6 | `[ ]` |
| 80 | Mobile App Builder | Engineering | F6 | `[ ]` |
| 81 | Finance Tracker | Support | F6 | `[ ]` |
| 82 | Sales Outbound Strategist | Sales | F6 | `[ ]` |
| 83 | Proposal Strategist | Sales | F6 | `[ ]` |
| 84 | Support Responder | Support | F6 | `[ ]` |
| 85 | Incident Response Commander | Engineering | F6 | `[ ]` |
| 86 | Pipeline Analyst | Sales | F6 | `[ ]` |
| 87 | ZK Steward | Specialized | Contínuo | `[ ]` |
| 88 | Identity Graph Operator | Specialized | Contínuo | `[ ]` |
| 89 | Workflow Architect | Specialized | Contínuo | `[ ]` |
| 90 | Project Shepherd | PM | Contínuo | `[ ]` |
| 91 | Studio Operations | PM | F5 suporte | `[ ]` |
| 92 | Carousel Growth Engine | Marketing | F6 | `[ ]` |
| 93 | Paid Media Auditor | Paid Media | F6 (se ads) | `[ ]` |
| 94 | Ad Creative Strategist | Paid Media | F6 (se ads) | `[ ]` |
| 95 | Paid Social Strategist | Paid Media | F6 (se ads) | `[ ]` |
| 96 | PPC Campaign Strategist | Paid Media | F6 (se ads) | `[ ]` |
| 97 | Tracking & Measurement Specialist | Paid Media | F6 (se ads) | `[ ]` |
| 98 | Sales Engineer | Sales | F6 (publishers) | `[ ]` |
| 99 | XR Immersive Developer | Spatial | F3-F (POC) | `[ ]` |
| 100 | macOS Spatial/Metal Engineer | Spatial | F6 (macOS port) | `[ ]` |
| 101 | Agentic Identity & Trust Architect | Specialized | F2 (MCP) | `[ ]` |
| 102 | Data Consolidation Agent | Specialized | F6 (analytics) | `[ ]` |

---

## AGENTS NÃO APLICADOS (e por quê)

| Agent | Razão |
|-------|-------|
| Embedded Firmware Engineer | Hardware/bare-metal — sem aplicação |
| Feishu/WeChat/Weibo/Xiaohongshu/Bilibili/Baidu/Douyin/Kuaishou | Plataformas chinesas sem relação |
| China E-Commerce / Cross-Border E-Commerce / Livestream Commerce | E-commerce chinês |
| Healthcare Marketing Compliance | Setor saúde |
| Government Digital Presales | Governo chinês |
| Salesforce Architect | CRM enterprise |
| French Consulting / Korean Business Navigator | Mercados regionais específicos |
| Study Abroad Advisor | Educação |
| Corporate Training Designer | RH enterprise |
| Recruitment Specialist | RH |
| Supply Chain Strategist | Cadeia de suprimentos |
| Accounts Payable Agent | Pagamentos automáticos |
| Blockchain Security Auditor / Solidity | Blockchain/crypto |
| Compliance Auditor (SOC2/HIPAA) | Certificações enterprise |
| Threat Detection Engineer | SIEM/SecOps |
| Godot/Unity/Unreal engines | Engines diferentes |
| Roblox (Avatar/Experience/Systems) | Plataforma Roblox |
| visionOS / XR Cockpit | Hardware Apple Vision Pro / cockpits XR |
| XR Interface Architect | AR/VR interfaces |
| Report Distribution Agent / Sales Data Extraction | Relatórios Excel de vendas |
| Private Domain Operator | Ecossistema WeChat |
| Zhihu Strategist | Plataforma chinesa Q&A |

---

*NEXUS-Sprint Maximum | TennisLegacy v2 | 102 agents, 8 fases, gate-enforced pipeline*
*Referência: `~/.claude/agents/strategy/nexus-strategy.md`*
