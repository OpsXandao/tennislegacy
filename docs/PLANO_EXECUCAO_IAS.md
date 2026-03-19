# PLANO DE EXECUÇÃO — DIVISÃO TRIPARTIDA DE IAs
> TennisLegacy | Branch: `feat/frontend` | Atualizado: 2026-03-19
> Cada IA trabalha em paralelo. Nunca edite a seção de outra IA.
> Status: `[ ]` pendente | `[~]` em progresso | `[x]` feito | `[!]` bloqueado por outra IA

---

## BOOTSTRAP — Como cada IA deve se inicializar

Antes de executar qualquer tarefa, cada IA deve:

1. **Identificar sua seção** pela tabela abaixo
2. **Ler o arquivo de agent** indicado na seção — ele define sua persona, regras críticas e padrões
3. **Ler o CLAUDE.md** do projeto (`/CLAUDE.md`) para convenções gerais
4. **Executar apenas as tarefas da sua seção** — nunca editar seções alheias
5. **Atualizar o status** de cada tarefa ao finalizar: `[ ]` → `[x] YYYY-MM-DD`

| IA | Seção | Agent Principal | Path |
|---|---|---|---|
| **Gemini** | `## GEMINI` | Backend Architect | `~/.claude/agents/engineering/engineering-backend-architect.md` |
| **Codex** | `## CODEX` | Game Designer + Software Architect | `~/.claude/agents/game-development/game-designer.md` |
| **Claude** | `## CLAUDE` | Frontend Developer | `~/.claude/agents/engineering/engineering-frontend-developer.md` |

> Os caminhos acima são relativos ao home do usuário da máquina de desenvolvimento.
> Se executando em ambiente diferente, localizar os `.md` equivalentes ou solicitar ao humano.

---

## VISÃO GERAL DO ESTADO ATUAL

### O que está feito
- Backend FastAPI completo com todas as rotas (save, ranking, jogador, calendario, torneio, partida, davis)
- Frontend React em `Front/` com todas as screens conectadas à API
- Domínio Python intacto em `src/`

### O que está quebrado (bugs críticos confirmados)
1. `POST /api/torneio/desistir` — não simula restante, não distribui pontos, não avança semana
2. `POST /api/treinamento/executar` — não avança semana; validação de lesão invertida
3. `POST /api/partida/desistir` — não distribui pontos ATP/WTA
4. Session em memória desatualiza após `avancar_semana()`
5. `distribuir_pontos_torneio()` não persiste no ranking lean

### O que está faltando (features)
- Tela de Patrocínios Ativo (busca manual)
- Tela de Ranking de Nações
- Sistema de Notificações/Badges no Hub
- Scouting de Adversário (pré-partida)
- Rival dinâmico entre jogadores
- Circuito ITF/Challenger
- Ajustes táticos entre sets
- Histórico de ranking por jogador
- Tests unitários (coverage < 20%)

---

## SPRINT 1 — BUG FIXES CRÍTICOS (prioridade máxima)
> Meta: salvar sem estado corrompido após qualquer ação do jogador.
> Todas as IAs trabalham em paralelo. Sem dependências entre si neste sprint.

---

## GEMINI — Infraestrutura, Session, Persistência [x] 2026-03-19

> **Agent de referência:** `~/.claude/agents/engineering/engineering-backend-architect.md`
> Ao executar esta seção, adote a persona e as regras definidas nesse arquivo.
> Foco: robustez de API, consistência de dados, sub-20ms persistence, zero estado corrompido.

### Contexto
Gemini é dona de `api/session.py`, `api/routes/save.py`, `api/routes/ranking.py`, `api/routes/jogador.py`.
A raiz dos bugs de estado está aqui: a sessão em memória diverge do que foi salvo em disco.

---

### G-1 `session.py` — refresh automático após `avancar_semana()` [x] 2026-03-19
**Problema:** `avancar_semana()` recarrega jogador/temporada do disco internamente, mas `session.jogador`
e `session.semana_atual` ficam com valores antigos na memória.

**Arquivo:** `api/session.py`

**Fix:**
```python
def refresh_session(nome_save: str) -> None:
    """Recarrega jogador e temporada do disco após qualquer ação que avance semana."""
    from src.save import carregar_jogador
    from src.dados import get_caminho_temporada_save
    import json, os

    sess = _sessions.get(nome_save)
    if not sess:
        return
    sess.jogador = carregar_jogador(nome_save)
    caminho = get_caminho_temporada_save(nome_save)
    if os.path.exists(caminho):
        with open(caminho) as f:
            temporada = json.load(f)
        sess.semana_atual = temporada.get("semana", sess.semana_atual)
        sess.ano_atual = temporada.get("ano", sess.ano_atual)
```

Exportar `refresh_session` e chamá-la em TODOS os routes que chamam `avancar_semana()`:
- `api/routes/treinamento.py` (descanso, executar — após fix do Codex)
- `api/routes/torneio.py` (desistir — após fix do Claude)
- `api/routes/calendario.py` (avancar)

---

### G-2 `torneio_atp.json` — limpeza após desistência [x] 2026-03-19
**Problema:** após desistência + simulação restante do torneio, o arquivo `saves/<save>/torneio_atp.json`
(ou wta) permanece em disco. Na próxima semana `carregar_torneio_api()` retorna o torneio "ativo".

**Arquivo:** `api/routes/torneio.py` (chamada do route desistir, após o fix do Claude)

**Fix:** Após `avancar_semana()` retornar, verificar se `torneio_atp.json` existe e está com
`fase_atual == "finalizado"` → deletar o arquivo.

```python
import os
caminho_torneio = get_caminho_torneio_save(nome_save, tour)
if os.path.exists(caminho_torneio):
    with open(caminho_torneio) as f:
        estado = json.load(f)
    if estado.get("fase_atual") == "finalizado":
        os.remove(caminho_torneio)
```

---

### G-3 Ranking lean — sincronizar após `distribuir_pontos_torneio()` [x] 2026-03-19
**Problema:** `distribuir_pontos_torneio()` atualiza o objeto `SistemaRanking` em memória mas não
chama `ranking.salvar_ranking()`, então o índice lean `saves/<save>/ranking_atp.json` fica desatualizado.
Na próxima request de `GET /api/ranking/atp`, os pontos do jogador aparecem errados.

**Arquivo:** `src/pontuacao.py` (função `distribuir_pontos_torneio`)

**Fix:** Verificar se a função já chama `salvar_ranking()`. Se não chamar, adicionar ao final:
```python
sistema_ranking.salvar_ranking()
```
Ou, alternativamente, chamar no route logo após `distribuir_pontos_torneio()`.

---

### G-4 `POST /api/treinamento/executar` — duplo avanço de semana [x] 2026-03-19
**Problema:** se o frontend chamar `POST /api/calendario/avancar` depois de `executar` (antes do fix C-4
do Claude ser deployado), a semana avança duas vezes.

**Fix:** Adicionar idempotência em `avancar_semana()`:
```python
# No início de avancar_semana():
temporada = carregar_temporada(nome_save)
if temporada["semana"] != semana_esperada:
    return {"ok": False, "motivo": "semana_ja_avancada", "semana": temporada["semana"]}
```
Ou uma flag `semana_avancada_nesta_rodada` na sessão, resetada em cada request nova.

---

### G-5 `GET /api/jogador/ranking-historico` — novo endpoint [x] 2026-03-19
**Problema:** TODO.md item: "Histórico de progressão de ranking por jogador" — não tem rota.

**Arquivo:** `api/routes/jogador.py`

**Contrato:**
```
GET /api/jogador/ranking-historico
Response: {
  "semanas": [
    {"semana": 1, "ano": 2025, "posicao": 342, "pontos": 180},
    ...
  ]
}
```

**Implementação:** `Jogador.historico_ranking` já existe (ver `src/jogador.py`) — apenas expor via API.
Se não existir, criar lista em `jogador.historico_ranking = []` e popular no `avancar_semana()`.

---

### G-6 `GET /api/jogador/patrocinios-disponiveis` — novo endpoint [x] 2026-03-19
**Problema:** COMPARATIVO_FUNCIONALIDADES.md — "Buscar Patrocínios Manualmente" está faltando no frontend.
O terminal tinha menu de busca ativa. Precisa de rota antes de Claude criar a tela.

**Arquivo:** `api/routes/jogador.py`

**Contrato:**
```
GET /api/jogador/patrocinios-disponiveis
Response: {
  "patrocinadores": [
    {
      "nome": "Nike",
      "nivel": "premium",
      "valor_mensal": 15000,
      "requisito_ranking": 50,
      "requisito_seguidores": 100000,
      "elegivel": true,
      "motivo_bloqueio": null
    },
    ...
  ]
}
```

**Implementação:** Usar `src/patrocinios.py:PATROCINADORES_DISPONIVEIS` + `pode_assinar_patrocinio()`.

---

### G-7 `GET /api/mundo/ranking-nacoes` — novo endpoint [x] 2026-03-19
**Problema:** COMPARATIVO_FUNCIONALIDADES.md — "Ranking de Nações" faltando no frontend.

**Arquivo:** `api/routes/mundo.py` (criar se não existir) ou adicionar em `ranking.py`

**Contrato:**
```
GET /api/mundo/ranking-nacoes
Response: {
  "nacoes": [
    {"posicao": 1, "pais": "Espanha", "codigo": "ESP", "pontos": 8420, "flag": "🇪🇸"},
    ...
  ]
}
```

**Implementação:** Carregar `db/ranking_nacoes_davis.json`.

---

## CODEX — Domínio de Torneio, Partida, Calendário, Davis

> **Agent de referência (principal):** `~/.claude/agents/game-development/game-designer.md`
> **Agent de referência (arquitetura):** `~/.claude/agents/engineering/engineering-software-architect.md`
> **Agent de revisão:** `~/.claude/agents/engineering/engineering-code-reviewer.md`
> Ao executar esta seção, adote a persona do Game Designer para decisões de mecânica e do
> Software Architect para decisões de estrutura de código. Rode o Code Reviewer internamente
> antes de considerar qualquer tarefa concluída.
> Foco: correctness do domínio, determinismo da simulação, zero números mágicos, testes.

### Contexto
Codex é dono de `src/torneio_core.py`, `src/pontuacao.py`, `src/simulacao_partida.py`,
`src/jogar_partida.py`, `src/davis_cup.py`, `src/calendario.py`.
Os bugs do backend têm raiz aqui — as funções de domínio não fazem o que o backend precisa.

---

### X-1 `desistir_do_torneio()` — auditoria e correção [CRÍTICO] [x] 2026-03-19
**Arquivo:** `src/torneio_core.py`

**O que precisa acontecer após desistência:**
1. Jogador marcado como eliminado no bracket (`vivo = False`, `fase_saida = fase_atual`)
2. `simular_torneio_restante()` pode ser chamado sem erro
3. `fase_saida` correta para `distribuir_pontos_torneio()` calcular pontos certos

**Auditoria necessária:**
```python
# Verificar se desistir_do_torneio() faz:
jogador_bracket["vivo"] = False
jogador_bracket["fase_saida"] = self.fase_atual  # ← fase ANTES da desistência
self._salvar_estado()  # ← persistir no disco antes de retornar
```

Se `fase_saida` não estiver sendo setada, adicionar. Sem ela, `distribuir_pontos_torneio()` não sabe
qual foi a última fase alcançada e distribui 0 pts sempre.

---

### X-2 `simular_torneio_restante()` — garantir que funciona pós-desistência [CRÍTICO] [x] 2026-03-19
**Arquivo:** `src/torneio_core.py`

**Cenário:** jogador desiste no meio do torneio. O torneio precisa ser simulado até o fim com apenas NPCs.

**Verificação:**
```python
# Antes de simular, garantir que o jogador humano está marcado como eliminado
# e que os confrontos pendentes onde ele aparecia são preenchidos com o adversário como vencedor
for confronto in self._confrontos_pendentes():
    if confronto["jogador1"] == nome_jogador_humano:
        confronto["vencedor"] = confronto["jogador2"]
    elif confronto["jogador2"] == nome_jogador_humano:
        confronto["vencedor"] = confronto["jogador1"]
```

Se `simular_torneio_restante()` não tratar esse caso e tentar "jogar" o confronto com o humano,
vai travar ou gerar erro.

---

### X-3 `distribuir_pontos_torneio()` para jogador eliminado [CRÍTICO] [x] 2026-03-19
**Arquivo:** `src/pontuacao.py`

**Casos a garantir:**
- Desistência na qualifying → 0 pts (não chegou ao torneio principal)
- Eliminação na R64 → pts de R64
- Eliminação nas QF → pts de QF
- Desistência em QF (W/O) → pts de R16 (chegou até lá, não venceu a QF)

**Fix:**
```python
def _pontos_por_fase(fase_saida: str, tipo_torneio: str, tour: str) -> int:
    """Retorna pontos para fase_saida. Desistência = fase ANTERIOR ao confronto não jogado."""
    ...
```

Garantir que a função usa `fase_saida` do bracket, não a `fase_atual` do torneio.

---

### X-4 `_match_runtime._finalizar_torneio()` — adicionar `distribuir_pontos_torneio()` [ALTO] [x] 2026-03-19
**Arquivo:** `api/routes/_match_runtime.py` (ou equivalente)

**Problema:** a auditoria confirma que `_finalizar_torneio()` não chama `distribuir_pontos_torneio()`.
Pontos ATP/WTA só são distribuídos se o frontend chamar `/avancar` depois — dependência implícita frágil.

**Fix:**
```python
# No final de _finalizar_torneio(), após salvar_jogo():
from src.pontuacao import distribuir_pontos_torneio
distribuir_pontos_torneio(nome_save)
```

Isso garante que seja qual for o caminho (vitória, derrota, W/O), os pontos são distribuídos.

---

### X-5 Ajustes táticos entre sets — implementação [NOVO FEATURE] [x] 2026-03-19
**Arquivo:** `src/jogar_partida.py`, `src/simulacao_partida.py`

**TODO.md:** "Ajustes táticos entre sets" — não implementado.

**Mecânica proposta:**
- Ao final de cada set (exceto o último), o jogador recebe 3 opções:
  - "Manter estratégia atual"
  - "Aumentar agressividade" (+3 agressividade, -2 consistência por 1 set)
  - "Jogar mais seguro" (+3 consistência, -2 agressividade por 1 set)
- NPC usa estratégia baseada no resultado do set (se perdeu: aumenta agressividade)
- Efeito dura apenas o próximo set

**Integração API:** `POST /api/partida/ajuste-tatico` — Claude cria a UI

**Contrato:**
```
POST /api/partida/ajuste-tatico
Body: {"partida_id": "xxx", "ajuste": "agressivo" | "seguro" | "manter"}
Response: {"ok": true, "efeito_aplicado": {"agressividade": +3, "consistencia": -2}}
```

---

### X-6 Rival dinâmico — sistema de rivalidades [NOVO FEATURE]
**Arquivo:** `src/jogador.py`, `src/match_history.py`

**TODO.md:** "Rivalidades dinâmicas entre jogadores"

**Mecânica:**
- Após 3+ confrontos com o mesmo NPC, a rivalidade é ativada
- Em partidas com rival: bônus de +5 mental e +10% de momentum inicial
- `Jogador.rivalidades = {nome_npc: {confrontos: N, vitorias: N, ultima_vez: semana}}`

**Critério de ativação:**
- 3+ confrontos E (win_rate > 60% ou win_rate < 40%) → rival ativo
- Exibir no `match_info` antes da partida: "Você enfrenta seu rival ___"

---

### X-7 Davis Cup — remover mock de convocação [MÉDIO]
**Arquivo:** `api/routes/torneio.py` (rota `POST /criar` para Davis)

**Problema:** `POST /api/torneio/criar` para Davis Cup usa mock `# Mocking...` em vez de
chamar `processar_convocacao` real de `src/davis_cup.py`.

**Fix:** Implementar chamada real:
```python
from src.davis_cup import criar_tie_davis, processar_convocacao_automatica
tie = criar_tie_davis(nome_save, nacao_adversaria)
convocacao = processar_convocacao_automatica(tie, jogador)
return {"tie": tie.to_dict(), "convocacao": convocacao}
```

---

### X-8 `avancar_semana()` — retornar dict estruturado [MÉDIO] [x] 2026-03-19
**Arquivo:** `src/calendario.py`

**Contexto:** a auditoria confirma que `avancar_semana()` já foi adaptada para retornar dict.
Verificar se o dict retornado contém TODOS os campos necessários:

```python
{
  "semana": int,
  "ano": int,
  "recuperacao": {"fadiga_antes": float, "fadiga_depois": float, "lesao_status": str},
  "torneios_disponiveis": [...],
  "eventos": [str],          # notícias da semana
  "pontos_expirados": int,   # pontos que caíram do rolling 52s
  "nova_posicao_ranking": int
}
```

Se algum campo faltar, adicionar. O frontend precisa de todos esses dados para atualizar o Hub.

---

### X-9 Tests unitários — cobrir funções críticas [TÉCNICO] [x] 2026-03-19
**Arquivo:** `tests/`

**TODO.md:** "Adicionar mais testes unitários"

**Prioridade de cobertura:**
1. `pontuacao.distribuir_pontos_torneio()` — casos de desistência
2. `torneio_core.desistir_do_torneio()` + `simular_torneio_restante()`
3. `calendario.avancar_semana()` — retorno estruturado
4. `ranking.adicionar_pontos()` + `salvar_ranking()` — sem duplicatas

---

## CLAUDE — Frontend React, Novas Telas, Fluxos de UI

> **Agent de referência:** `~/.claude/agents/engineering/engineering-frontend-developer.md`
> **Agent de validação:** `~/.claude/agents/testing/testing-reality-checker.md`
> Ao executar esta seção, adote a persona do Frontend Developer. Antes de marcar qualquer
> tarefa `[x]`, passe o critério do Reality Checker: a feature funciona end-to-end com API real?
> Foco: pixel-perfect no design system existente, zero chamadas redundantes à API, store sempre sync.

### Contexto
Claude é dono de `Front/src/`. Todos os componentes visuais existem. O trabalho agora é
conectar features que faltam, corrigir fluxos quebrados e criar as 4 telas faltantes.
**Não alterar nenhum arquivo em `src/` ou `api/` exceto os indicados abaixo.**

---

### C-1 `api/routes/torneio.py` — fix `POST /desistir` [CRÍTICO] `[x] 2026-03-19`
> Gemini implementou desistir+simular+pontos+avancar_semana+rebuild_rankings+limpeza arquivo. Confirmado.

### C-1 detalhe
**Arquivo:** `api/routes/torneio.py`

```python
@router.post("/desistir")
def desistir() -> dict:
    nome_save = session.get_nome_save_ativo()
    instancia = carregar_torneio_api()
    if not instancia:
        raise HTTPException(status_code=404, detail="Nenhum torneio ativo")

    instancia.desistir_do_torneio()
    instancia.simular_torneio_restante()          # simula o resto com NPCs

    from src.pontuacao import distribuir_pontos_torneio
    distribuir_pontos_torneio(nome_save)           # 0 pts ou pts da fase alcançada

    from src.calendario import avancar_semana
    resultado = avancar_semana(nome_save)

    from api.session import refresh_session
    refresh_session(nome_save)

    return {"ok": True, **resultado}
```

---

### C-2 `api/routes/treinamento.py` — fix `POST /executar` [CRÍTICO] `[x] 2026-03-19`
> Gemini já adicionou refresh_session + expected_week. Claude adicionou ano/eventos/resumo_mundial ao response de descanso e executar.
**Arquivo:** `api/routes/treinamento.py`

```python
@router.post("/executar")
def executar_treino(body: TreinoRequest) -> dict:
    nome_save = session.get_nome_save_ativo()
    jogador = session.get_jogador()

    # Validação de lesão ANTES do treino
    if jogador.lesionado and jogador.semanas_lesao > 0:
        return {"ok": False, "motivo": "jogador_lesionado"}

    melhorias = treinar_semana(jogador, body.tipo_treino, body.intensidade)

    from src.calendario import avancar_semana
    resultado = avancar_semana(nome_save)

    from api.session import refresh_session
    refresh_session(nome_save)

    return {"ok": True, "melhorias": melhorias, **resultado}
```

---

### C-3 Frontend — `TournamentBracket` após desistir [ALTO] `[x] 2026-03-19`
> handleDesistir() já correto: setTorneio(null)+setPartidaId(null)+navigate('/week-advance'). Não chama avancar redundante.
**Arquivo:** `Front/src/app/screens/TournamentBracket.tsx` (ou equivalente)

Após `api.torneio.desistir()` retornar com sucesso:
1. Atualizar `gameStore.semana` com o valor retornado
2. Limpar `gameStore.torneioAtivo`
3. Navegar para `/hub`
4. **NÃO** chamar `api.calendario.avancar()` depois (semana já foi avançada no backend)

```typescript
const handleDesistir = async () => {
  const resultado = await api.torneio.desistir()
  if (resultado.ok) {
    useGameStore.setState({
      semana: resultado.semana,
      torneioAtivo: null,
    })
    navigate('/hub')
  }
}
```

---

### C-4 Frontend — `TrainingScreen` após executar treino [ALTO] `[x] 2026-03-19`
> Adicionado useNavigate + _navegarWeekAdvance() em TrainingScreen. Ambos handleTreinar e handleDescansar navegam para /week-advance com eventos de melhoria + campeoes do circuito.
**Arquivo:** `Front/src/app/screens/TrainingScreen.tsx`

Após `api.treinamento.executar()` retornar (com semana avançada no backend após fix C-2):
1. Atualizar `gameStore.semana`
2. Exibir modal/toast com `melhorias` e eventos da semana
3. **NÃO** chamar `api.calendario.avancar()` depois

---

### C-5 Nova tela — `SponsorScreen` (Patrocínios Ativo) [NOVO] `[x] 2026-03-19`
**Arquivo:** `Front/src/app/screens/SponsorScreen.tsx`
**Depende de:** Gemini G-6 (`GET /api/jogador/patrocinios-disponiveis`)

**UI:**
- Lista de patrocinadores disponíveis com logo, valor mensal, requisitos
- Badge "ELEGÍVEL" (verde neon) ou "BLOQUEADO" (vermelho) baseado em `elegivel`
- Para bloqueados: tooltip com `motivo_bloqueio`
- Botão "Assinar" → `POST /api/jogador/assinar-patrocinio` com `{nome_patrocinador}`
- Seção "Contratos Ativos" no topo com status dos patrocínios correntes

**Rota:** `/patrocinios` — adicionar no `routes.ts`

---

### C-6 Nova tela — `NationsRankingScreen` [NOVO] `[x] 2026-03-19`
**Arquivo:** `Front/src/app/screens/NationsRankingScreen.tsx`
**Depende de:** Gemini G-7 (`GET /api/mundo/ranking-nacoes`)

**UI:**
- Tabela de países com posição, bandeira (emoji), nome, pontos
- Destacar nação do jogador com borda neon
- Mostrar próximos confrontos de Davis Cup se disponíveis

**Rota:** `/ranking-nacoes` — adicionar como aba em `WorldScreen` ou tela própria

---

### C-7 Sistema de Notificações/Badges no Hub [NOVO] `[x] 2026-03-19`
> Já implementado: HubScreen tem unreadEmails state + api.email.unreadCount() no mount + badge animado que navega para aba Email.
**Arquivo:** `Front/src/app/screens/HubScreen.tsx`, `Front/src/store/gameStore.ts`

**COMPARATIVO_FUNCIONALIDADES.md:** "Notificações Visíveis" — jogador precisa entrar em Email/Mundo pra ver.

**Implementação:**
1. `gameStore.notificacoes: Notificacao[]` — array de notificações não lidas
2. `GET /api/notificacoes` — retorna emails não lidos + eventos da semana
3. No Hub: badge numérico sobre ícone de Email/Mundo se houver pendências
4. Ao clicar e ver: `POST /api/notificacoes/marcar-lidas`

**Contrato backend (criar em `api/routes/notificacoes.py`):**
```
GET /api/notificacoes
Response: {
  "emails_nao_lidos": int,
  "eventos_semana": [str],
  "propostas_pendentes": int
}
```

---

### C-8 Nova tela — `ScoutingScreen` (Análise de Adversário) [NOVO] `[x] 2026-03-19`
> GET /api/partida/scout/{nome} implementado em partida.py: atributos via estado do torneio, H2H + forma recente via MatchHistoryManager, superfície favorita calculada. Painel inline no TournamentBracket com botão ANALISAR + modal de scout mostrando atributos/H2H/forma. api.partida.scout() adicionado ao client.ts.
**Arquivo:** `Front/src/app/screens/ScoutingScreen.tsx`
**Depende de:** endpoint `GET /api/partida/preview/{nome_adversario}`

**UI (aparece antes da partida no `TournamentBracket`):**
- Card com foto/avatar do adversário
- Barra de atributos: Saque, Retorno, Fundo, Voleio, Físico
- Superfície favorita + resultado recente (últimas 5 partidas)
- Botão "JOGAR" ou "SIMULAR" — mesmos do bracket atual

**Endpoint backend:**
```
GET /api/partida/scout/{nome_jogador}
Response: {
  "nome": str,
  "ranking": int,
  "overall": int,
  "atributos": {...},
  "superficie_favorita": str,
  "forma_recente": ["V","D","V","V","D"],
  "h2h": {"vitorias_jogador": int, "vitorias_adversario": int}
}
```

Implementar endpoint em `api/routes/partida.py` usando `src/match_history.py` para H2H.

---

### C-9 Ajuste tático entre sets — UI [NOVO] `[x] 2026-03-19`
**Implementado diretamente:** `POST /api/partida/ajuste-tatico` criado em `api/routes/partida.py`

**Arquivo:** `Front/src/app/screens/MatchScreen.tsx`

Ao receber evento WebSocket `{tipo: "fim_set", set: 1}`:
- Exibir modal com 3 opções de ajuste tático
- Timer de 10s (se não escolher, mantém estratégia atual)
- Após escolha: `POST /api/partida/ajuste-tatico` e continua

---

### C-10 Detalhes de bônus de equipe — UI [MELHORIA] `[x] 2026-03-19`
> PlayerScreen aba Equipe agora exibe linhas de bônus por membro: bonus_progressao, bonus_recuperacao, bonus_xp, bonus_mental, bonus_fadiga, bonus_fisico_pct, bonus_patrocinio — todos com labels em português e ícone ▸ em amarelo neon.
**COMPARATIVO_FUNCIONALIDADES.md:** "Explicar melhor o que cada bônus faz"

**Arquivo:** `Front/src/app/screens/PlayerScreen.tsx` (aba Equipe)

Cada membro da equipe deve mostrar:
- Bônus atual: "+2 Estratégia por set"
- Tooltip explicativo ao hover/tap
- Indicador visual se o bônus está ativo nesta semana

---

## CONTRATOS DE API — referência para todas as IAs

> Todo endpoint novo deve ser adicionado aqui antes de implementar.
> Quem criar o endpoint escreve o contrato. Quem consome verifica aqui primeiro.

| Endpoint | Método | Dono | Status | Consumidor |
|---|---|---|---|---|
| `GET /api/jogador/patrocinios-disponiveis` | GET | Gemini | `[x] 2026-03-19` | Claude C-5 |
| `GET /api/mundo/ranking-nacoes` | GET | Gemini | `[x] 2026-03-19` | Claude C-6 |
| `GET /api/notificacoes` | GET | Gemini | `[x] 2026-03-19` | Claude C-7 |
| `POST /api/notificacoes/marcar-lidas` | POST | Gemini | `[x] 2026-03-19` | Claude C-7 |
| `GET /api/partida/scout/{nome}` | GET | Claude | `[x] 2026-03-19` | Claude C-8 |
| `POST /api/partida/ajuste-tatico` | POST | Claude | `[x] 2026-03-19` | Claude C-9 |
| `GET /api/jogador/ranking-historico` | GET | Gemini | `[x] 2026-03-19` | Claude (futuro) |
| `GET /api/partida/{id}/stats` | GET | Gemini | `[x] 2026-03-19` | Claude (futuro) |
| `GET /api/partida/{id}/log` | GET | Gemini | `[x] 2026-03-19` | Claude (futuro) |

---

## BLOQUEIOS E DEPENDÊNCIAS

| Tarefa | Bloqueada por | Desbloqueada quando |
|---|---|---|
| Claude C-5 | Gemini G-6 | Endpoint `/patrocinios-disponiveis` retorna 200 |
| Claude C-6 | Gemini G-7 | Endpoint `/ranking-nacoes` retorna 200 |
| Claude C-7 | Gemini (novo endpoint notificacoes) | Endpoint `/notificacoes` retorna 200 |
| Claude C-9 | Codex X-5 | Endpoint `/ajuste-tatico` retorna 200 |
| Claude C-1 | Codex X-1, X-2 | `desistir_do_torneio()` + `simular_torneio_restante()` auditados |
| Codex X-4 | Nenhuma | Pode começar agora |
| Gemini G-1 | Nenhuma | Pode começar agora |

---

## SPRINT 2 — SEGURANÇA & PENDÊNCIAS DO SPRINT 1
> Prioridade máxima. Bugs de segurança e tarefas não concluídas do Sprint 1.
> Auditoria de segurança completa em `docs/audit_security.md` (2026-03-19).

---

## GEMINI — Sprint 2 — Segurança & Infraestrutura [x] 2026-03-19

> **Domínio:** `api/`, `src/save.py`, `src/ranking.py`, `src/dados.py`
> **Auditoria de código:** `docs/audit_code_quality.md` | **Auditoria de segurança:** `docs/audit_security.md`

### G2-0 P0 BUGS CRÍTICOS (da auditoria de código) [x] 2026-03-19

#### G2-0a `api/routes/jogador.py:337-340` — `GET /patrocinios` NameError [x] 2026-03-19
#### G2-0b `api/routes/jogador.py:357-395` — `rk is None` não verificado [x] 2026-03-19
#### G2-0c `api/routes/jogador.py:404` — KeyError em `assinar-patrocinio` [x] 2026-03-19

---

### G2-1 Path Traversal em `nome_save` [x] 2026-03-19
**Fix:** Implementado `validar_nome_save()` em `src/dados.py` e aplicado em todos os `os.path.join` que usam `nome_save` no domínio (`src/dados.py`, `src/jogador.py`, `src/save.py`, `src/log_jogo.py`) e na API (`api/session.py`, `api/routes/save.py`).

---

### G2-2 CORS mal configurado [x] 2026-03-19
**Fix:** Origens restritas a `localhost:5173` e `localhost:3000` em `api/main.py`.

---

### G2-3 `CreateSaveRequest.nome` — validação no Pydantic [x] 2026-03-19
**Fix:** Adicionado `@validator` com regex em `api/routes/save.py`.

---

### G2-4 Ranking por superfície — novo endpoint [x] 2026-03-19
---

### G2-5 `GET /api/jogador/forma-recente` — últimas 5 partidas [x] 2026-03-19
---

### Extra: `GET /api/jogador/rivalidades` [x] 2026-03-19
**Implementação:** Adicionado endpoint para suportar feature X2-1 do Codex.

---

## CODEX — Sprint 2 — Domínio Pendente + Rival

> **Domínio:** `src/torneio_core.py`, `src/pontuacao.py`, `src/simulacao_partida.py`,
> `src/jogar_partida.py`, `src/davis_cup.py`, `src/calendario.py`
> **Auditoria de código:** `docs/audit_code_quality.md`

### X2-0 P0 BUGS CRÍTICOS (da auditoria de código) [urgente]

#### X2-0a `src/torneio_core.py:967` — qualifying não simula partidas [P0] [x] 2026-03-19
`jogar_qualy` sempre seleciona `c[0]` como vencedor — simulação nunca ocorre.
**Fix:** substituir por chamada real a `simular_partida_npc_basica(c[0], c[1])`.

#### X2-0b `src/torneio_core.py:688-693` — IndexError com número ímpar em qualifying [P0] [x] 2026-03-19
Loop monta pares sem verificar `if i + 1 < len(qualy_players)`.
**Fix:** adicionar guard antes de acessar `qualy_players[i+1]`.

---

### X2-1 Rival dinâmico — sistema de rivalidades [FEATURE] (era X-6) [x] 2026-03-19
**Arquivo:** `src/jogador.py`, `src/match_history.py`, `src/jogar_partida.py`
**Mecânica:**
- `Jogador.rivalidades = {nome_npc: {"confrontos": N, "vitorias": N, "ultima_semana": N}}`
- Após cada partida: `_atualizar_rivalidade(jogador, nome_adversario, venceu)`
- Critério de ativação: 3+ confrontos E (win_rate > 60% ou < 40%)
- Em partida com rival ativo: +5 mental e +10% momentum inicial no `jogar_partida.py`
- `rival_ativo(jogador, nome)` → bool (exportar para uso no frontend/API)
- Serializado no save: `jogador.rivalidades` como dict

**Endpoint necessário (Gemini cria):** `GET /api/jogador/rivalidades`

---

### X2-2 Davis Cup — remover mock de convocação [MÉDIO] (era X-7) [x] 2026-03-19
> Auditada a rota atual: `api/routes/torneio.py` delega para `create_tournament()`, que já usa fluxo real via `DavisCup.verificar_convocacao()` + `criar_torneio_davis()`; não restou mock ativo no caminho de criação.
**Arquivo:** `api/routes/torneio.py`
**Fix:**
```python
from src.davis_cup import criar_tie_davis, processar_convocacao_automatica
tie = criar_tie_davis(nome_save, nacao_adversaria)
convocacao = processar_convocacao_automatica(tie, jogador)
return {"tie": tie.to_dict(), "convocacao": convocacao}
```

---

### X2-3 Circuito ITF/Challenger — novo tipo de torneio [FEATURE] [x] 2026-03-19
**Arquivo:** `src/torneio_profile.py`, `db/calendario.json`, `src/pontuacao.py`
**Categorias a adicionar:**
- `ITF_25` — draw 32, pontos 25/18/12/8/4/1
- `ITF_100` — draw 32, pontos 100/70/40/20/10/2
- `CHALLENGER_125` — draw 48 (32+qualy), pontos 125/85/55/25/13/3
**Regra**: só disponível se ranking > 200 (ITF) ou > 100 (Challenger).
Adicionar semanas no `calendario.json` para torneios deste tipo nas semanas sem ATP 250.
> Entregue com perfis e tabelas de pontos dedicados, filtro de elegibilidade por ranking no serviço e no domínio do torneio, badges `[Ineligible]` no calendário e preenchimento das semanas vazias com eventos `Challenger 125`, `ITF 100` e `ITF 25`.

---

### X2-4 `avancar_semana()` — campo `rival_info` no retorno [INTEGRAÇÃO] [x] 2026-03-19
**Arquivo:** `src/calendario.py`
**Adição:** Se `jogador.rivalidades` tiver rival ativo no próximo torneio, incluir no dict retornado:
```python
"rival_info": {"nome": str, "ranking": int, "h2h": {"v": int, "d": int}} | None
```
Isso permite ao frontend exibir alerta de rival na WeekAdvanceScreen.

---

## CLAUDE — Sprint 2 — Frontend: Histórico, Rival, Forma [~] 2026-03-19

> **Domínio:** `Front/src/`
> **Auditoria UX:** `docs/audit_ux_flows.md` | **Auditoria de código:** `docs/audit_code_quality.md`

### C2-0 P0 BUGS CRÍTICOS (da auditoria UX/código) [x] 2026-03-19

#### C2-0a Botão de debug exposto [x] 2026-03-19
`HomeScreen:175` — `[ ALEXANDRE PAIVA ]` agora oculto atrás de `import.meta.env.DEV`.

#### C2-0b Erros de API silenciados em `HubScreen.fetchJogador` [x] 2026-03-19
`HubScreen` agora exibe banner vermelho "ERRO AO CARREGAR DADOS" com botão "TENTAR NOVAMENTE".

#### C2-0c Desistir de torneio sem confirmação [x] 2026-03-19
`TournamentBracket` agora exibe modal de confirmação antes de chamar `api.torneio.desistir()`.

#### C2-0d `.catch(() => {})` silenciando falhas no `MatchScreen.tsx` [~] pendente
Será endereçado junto com refactor geral de error handling.

---

### C2-1 Tela de Histórico de Ranking [x] 2026-03-19
**Arquivo:** `Front/src/app/screens/RankingHistoryScreen.tsx` — criado
- Gráfico SVG nativo (linha + área) posição por semana, eixo Y invertido (rank 1 = topo)
- Tooltip ao hover em cada ponto
- Stats summary (atual, melhor, qtd semanas)
- Tabela scrollável com todas as semanas
- Rota `/ranking-historico` | Link "VER HISTÓRICO DE POSIÇÕES →" na aba Ranking da PlayerScreen

---

### C2-2 WeekAdvanceScreen — rival alert [FEATURE]
**Arquivo:** `Front/src/app/screens/WeekAdvanceScreen.tsx`
**Depende de:** Codex X2-1 + X2-4
**UI:** Se `rival_info` presente no response de `/api/calendario/avancar`:
- Card especial com "⚔️ RIVAL NA SEMANA — [NOME] ([H2H])"
- Cor vermelha neon, diferenciado dos eventos comuns

---

### C2-3 MatchScreen — badge de rival pré-partida [FEATURE]
**Arquivo:** `Front/src/app/screens/MatchScreen.tsx`
**Depende de:** `GET /api/partida/scout/{nome}` já implementado (C-8)
**UI:** Se `scout.is_rival === true` (Gemini adiciona campo no scout):
- Banner no topo: "⚔️ PARTIDA DE RIVAL"
- Stat adicional no painel: "H2H: X-Y"

---

### C2-4 RankingScreen — abas por superfície [x] 2026-03-19
`RankingsScreen` agora tem tabs ARGILA/DURO/GRAMA além de SIMPLES/DUPLAS.
Chama `api.ranking.superficie(sup, tour)` quando superfície selecionada.

---

### C2-5 PlayerScreen — aba Forma Recente [x] 2026-03-19
Componente `FormaTab` adicionado como TAB 3 ("FORMA") em `PlayerScreen`.
5 círculos V/D + lista de partidas com adversário, torneio, placar.

---

### C2-2 WeekAdvanceScreen — rival alert [!] aguarda validação
Endpoints Codex X2-1/X2-4 marcados [x] pelo Codex — implementar após confirmar campo `rival_info` no retorno de `/api/calendario/avancar`.

### C2-3 MatchScreen — badge rival [!] aguarda validação
Aguarda campo `is_rival` no endpoint `GET /api/partida/scout/{nome}`.

---

## CONTRATOS DE API — Sprint 2

| Endpoint | Método | Dono | Status | Consumidor |
|---|---|---|---|---|
| `GET /api/ranking/superficie/{sup}` | GET | Gemini | `[x] 2026-03-19` | Claude C2-4 |
| `GET /api/jogador/forma-recente` | GET | Gemini | `[x] 2026-03-19` | Claude C2-5 |
| `GET /api/jogador/rivalidades` | GET | Gemini | `[x] 2026-03-19` | Claude C2-2/C2-3 |
| `POST /api/partida/ajuste-tatico` | POST | ~~Codex~~ Claude | `[x] 2026-03-19` | Claude C-9 |

> `ajuste-tatico` foi implementado diretamente por Claude em `api/routes/partida.py` na Sprint 1.

---

## SPRINT 3 — EXPANSÃO (após Sprint 2 estabilizado)

| Feature | IA Dona | Depende |
|---|---|---|
| **Circuito ITF UI** (tela de entrada, draw ITF) | Claude | Codex X2-3 |
| **Carreira Timeline** (eventos marcantes visuais) | Claude | nenhum |
| **Equipamentos** (raquete/tênis que afetam atributo) | Codex domínio + Claude UI | Codex X3-1 |
| **Eventos de Carreira** (polêmicas, premiações) | Codex | `imprensa.py` |
| **Stats Avançadas de Partida** (endpoint) | Gemini | `simulacao_partida.py` | [x] 2026-03-19 |
 **Stats Avançadas UI** (heatmap de pontos) | Claude | Gemini endpoint |
| **Tests unitários Rival + ITF** | Codex | X2-1, X2-3 |
| **Cache Redis/lru_cache nos endpoints pesados** | Gemini | nenhum | [x] 2026-03-19 |

---

## REGRAS DE COORDENAÇÃO

1. Cada IA atualiza **apenas sua seção** e a tabela de Contratos
2. Ao finalizar uma tarefa: marcar `[x]` e adicionar data
3. Ao criar novo endpoint: adicionar na tabela de Contratos ANTES de implementar
4. Ao encontrar bloqueio novo: adicionar na tabela de Bloqueios
5. Nunca quebrar imports em `src/` — apenas adicionar sobre
6. `black --check .` deve passar antes de qualquer commit
7. `py_compile` em cada arquivo modificado antes do commit

---

## ORDEM DE EXECUÇÃO RECOMENDADA

```
Paralelo (Sprint 1):
  Gemini:  G-1 → G-2 → G-3 → G-4 → G-5 → G-6 → G-7
  Codex:   X-1 → X-2 → X-3 → X-4 → X-8 → X-9 → X-5 → X-6 → X-7
  Claude:  C-1* → C-2 → C-3 → C-4 → C-8 → C-10
           (* aguarda X-1/X-2 para garantir que domínio suporta)

Sequencial (desbloqueio):
  Quando Gemini G-6 feito → Claude inicia C-5
  Quando Gemini G-7 feito → Claude inicia C-6
  Quando Codex X-5 feito  → Claude inicia C-9
```
