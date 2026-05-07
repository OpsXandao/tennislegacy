# Audit de Gargalos do Backend — TennisLegacy

> Gerado em 2026-03-08. Referência: `docs/funcionalidades_jogo_mapeamento.md`.

---

## Resumo Executivo

O backend cobre todos os 14 grupos de funcionalidades listados no mapeamento.
O problema central não é ausência de rotas, mas **fluxos incompletos**: várias ações que deveriam terminar com avanço de semana ou distribuição de pontos não o fazem, deixando o jogador preso ou com estado inconsistente.

Padrão correto (referência `descanso`):
```
ação do jogador → lógica de domínio → distribuir_pontos (se cabível) → avancar_semana → salvar
```
Vários routes quebram esse padrão.

---

## Bug Confirmado — Origem do Problema Reportado

### `POST /api/torneio/desistir` — semana não avança

**Arquivo:** `api/routes/torneio.py:361-367`

```python
@router.post("/desistir")
def desistir() -> dict:
    instancia = carregar_torneio_api()
    if not instancia:
        raise HTTPException(status_code=404, ...)
    instancia.desistir_do_torneio()   # ← só isso
    return {"ok": True}              # ← sem pontos, sem avanço de semana
```

**O que falta:**
1. `instancia.simular_torneio_restante()` — simula o torneio até o fim após W/O
2. `distribuir_pontos_torneio(nome_save)` — distribui pontos ao jogador (0 pts mas registra fase)
3. `avancar_semana(nome_save)` — avança para a próxima semana

**Referência correta:** `POST /api/treinamento/descanso` chama `avancar_semana()` corretamente.

---

## Mapa de Gargalos por Route

### 1. `api/routes/torneio.py`

| Endpoint | Status | Problema |
|---|---|---|
| `GET /checar-convocacao` | ✅ OK | — |
| `POST /criar` | ⚠️ Parcial | Davis Cup: implementação de convocação é um mock (`# Mocking...`). Não chama `processar_convocacao` real. |
| `GET /historico` | ✅ OK | — |
| `GET /estado` | ✅ OK | — |
| `POST /avancar-fase` | ✅ OK | Simula NPCs e avança fase corretamente |
| `POST /desistir` | ❌ Bug Crítico | Não simula restante, não distribui pontos, não avança semana |

---

### 2. `api/routes/partida.py` + `_match_runtime.py`

| Endpoint | Status | Problema |
|---|---|---|
| `GET /preview` | ✅ OK | — |
| `GET /ativa` | ✅ OK | — |
| `POST /iniciar` | ✅ OK | — |
| `POST /ponto` | ✅ OK | — |
| `POST /estrategia` | ✅ OK | — |
| `POST /simular-set` | ✅ OK | — |
| `POST /simular-partida` | ✅ OK | — |
| `POST /desistir` | ⚠️ Parcial | Chama `_finalizar_torneio()` (registra derrota, XP, fadiga) mas não avança semana. Após W/O em partida, jogador precisa manualmente ir ao calendário. |

**`_match_runtime._finalizar_torneio()`** — fluxo auditado:
- ✅ `processar_resultado_partida()` — registra resultado no torneio
- ✅ `handle_xp_e_level_up()` — XP
- ✅ `handle_progressao_natural()` — progressão técnica
- ✅ `handle_fadiga_e_lesao()` — fadiga/lesão
- ✅ `salvar_jogo()` — salva jogador
- ❌ Não chama `distribuir_pontos_torneio()` — pontos ATP/WTA só são distribuídos se o frontend chamar `/avancar` depois
- ❌ Não avança semana (intencional por design, mas cria dependência implícita do frontend)

**Dependência implícita crítica:** o frontend precisa chamar `POST /api/calendario/avancar` após a partida final. Se não chamar (ex: crash, navegação errada), o save fica na mesma semana para sempre.

---

### 3. `api/routes/treinamento.py`

| Endpoint | Status | Problema |
|---|---|---|
| `POST /descanso` | ✅ OK | Chama `avancar_semana()` corretamente |
| `GET /opcoes` | ✅ OK | — |
| `POST /executar` | ❌ Bug | Executa treino e salva, mas **NÃO chama `avancar_semana()`**. O jogador treina e a semana fica parada. |

**Detalhe extra em `executar`:** a validação de lesão está invertida — verifica `if not melhorias and ... lesionado` *depois* do treino ser executado. Deveria bloquear *antes* de chamar `treinar_semana()`.

---

### 4. `api/routes/davis.py`

| Endpoint | Status | Problema |
|---|---|---|
| `GET /estado` | ✅ OK | — |
| `GET /proximo` | ✅ OK (só backend, sem uso no front) | — |
| `POST /simular-atual` | ⚠️ Parcial | Simula NPCs mas não avança semana após a Davis encerrar. Sem chamada a `distribuir_pontos_davis()`. |

---

### 5. `api/routes/calendario.py`

| Endpoint | Status | Problema |
|---|---|---|
| `GET /semana/{numero}` | ✅ OK | — |
| `GET /atual` | ✅ OK | — |
| `POST /avancar` | ✅ OK | Pipeline completo em `avancar_semana()` |

---

### 6. `api/routes/progressao.py`

| Endpoint | Status | Problema |
|---|---|---|
| `GET /status` | ✅ OK | — |
| `POST /alocar` | ✅ OK | Salva corretamente após alocar ponto de skill |

---

### 7. `api/routes/mercado.py`, `ranking.py`, `jogador.py`, `email.py`, `duplas.py`, `historico.py`, `mundo.py`

Não auditados em detalhe nesta rodada. Sem relatos de bugs. Prioridade baixa.

---

## Dependências Implícitas do Frontend (Risco Estrutural)

O backend usa dois padrões misturados:

| Padrão | Routes que usam | Risco |
|---|---|---|
| **A — ação avança semana internamente** | `descanso` | Simples, sem dependência de frontend |
| **B — ação não avança, frontend chama `/avancar` depois** | `executar`, `desistir`, `_finalizar_torneio` | Frontend precisa garantir sempre chamar `/avancar` |

A mistura de padrões A e B é a raiz dos bugs. O padrão B é frágil porque:
- Se a navegação do frontend falhar após uma ação, a semana não avança
- A responsabilidade de avançar a semana vira lógica de UI, não de domínio

**Recomendação de arquitetura:** adotar padrão A para toda ação terminal de semana (desistir, fim de treino, derrota em partida). O route chama `avancar_semana()` antes de retornar.

---

## Plano de Correção por IA

---

### Claude — Interface e Fluxo Frontend/Backend

**Responsabilidade:** garantir que o frontend chama os endpoints certos na ordem certa, e que as telas refletem o estado correto após cada ação terminal.

**Tarefas:**

#### C-1. `POST /api/torneio/desistir` — fix no route (backend)
Adicionar ao route `desistir()` em `torneio.py`:
```python
instancia.desistir_do_torneio()
instancia.simular_torneio_restante()          # fecha o torneio com NPCs
from src.pontuacao import distribuir_pontos_torneio
distribuir_pontos_torneio(nome_save)          # registra 0 pts ou pts de fase alcançada
resultado = avancar_semana(nome_save)
return {"ok": True, **resultado}
```
Retornar os dados da semana nova para o frontend poder atualizar o estado.

#### C-2. Frontend — `TournamentBracket` após desistir
Verificar se após `POST /api/torneio/desistir` o frontend:
- Atualiza `semana` e `torneio` no `gameStore`
- Navega para `/hub` ou `/calendar`
- **NÃO** chama `POST /api/calendario/avancar` de forma redundante depois

#### C-3. Frontend — `TrainingScreen` após executar treino
Após `POST /api/treinamento/executar` ter a semana avançada pelo backend (fix C-4), garantir que a tela de treino:
- Atualiza semana no store
- Mostra o resultado da semana (fadiga, próximos torneios)

#### C-4. `POST /api/treinamento/executar` — fix no route (backend)
Adicionar chamada a `avancar_semana()` no final de `executar_treino()` em `treinamento.py`:
```python
resultado = avancar_semana(session.nome_save_ativo)
return {"ok": True, "melhorias": melhorias, "semana": resultado.get("semana"), ...}
```
E mover a validação de lesão para *antes* de `treinar_semana()`.

---

### Codex — Domínio de Torneio e Partida

**Responsabilidade:** garantir que as funções de domínio fazem o que o backend espera delas.

**Tarefas:**

#### X-1. `desistir_do_torneio()` em `torneio_core.py`
Auditar o que `desistir_do_torneio()` faz atualmente:
- Verifica se registra o jogador como eliminado no bracket
- Verifica se marca fase alcançada para pontuação
- Verifica se `simular_torneio_restante()` pode ser chamado logo após

Se `desistir_do_torneio()` já marcar a fase certa e `simular_torneio_restante()` funcionar após a desistência, a correção C-1 é direta. Se não, ajustar o domínio primeiro.

#### X-2. `distribuir_pontos_torneio()` em `pontuacao.py`
Verificar se funciona corretamente para um jogador eliminado (0 pts ou pts da fase alcançada antes da desistência). Casos a testar:
- Desistência na fase de qualifying → 0 pts
- Desistência nas quartas → pts de R32 ou QF conforme a fase alcançada

#### X-3. Davis Cup — `simular-atual` sem distribuição de pontos
Em `davis.py`, após `_atualizar_estado_apos_confronto()`, se `fase_atual == "finalizado"`:
- Chamar `distribuir_pontos_davis(nome_save)`
- **Não** avançar semana (isso é responsabilidade do calendário)

#### X-4. `_match_runtime._finalizar_torneio()` — garantir que `processar_resultado_partida()` atualiza bracket
Verificar se após derrota/vitória, o estado do torneio salvo em disco (`torneio_atp.json`) está marcado como:
- Jogador eliminado (vivo = False) se perdeu
- Fase correta para distribuição de pontos

---

### Gemini — Infraestrutura de Save, Sessão e Ranking

**Responsabilidade:** garantir que os dados persistidos estão corretos e consistentes após cada fluxo.

**Tarefas:**

#### G-1. Session state após `avancar_semana()`
Em `treinamento.py:descanso`, após `avancar_semana()`, o objeto `session.jogador` fica desatualizado (foi recarregado dentro de `avancar_semana` mas a sessão em memória tem o estado antigo). Verificar:
- Se `refresh_session()` precisa ser chamado após `avancar_semana()` para refletir semana nova
- O mesmo problema existe nos outros routes que chamarão `avancar_semana()` após a correção

#### G-2. `salvar_jogo()` vs `atualizar_jogador_no_ranking()`
Verificar se `salvar_jogo()` atualiza o entry do jogador no `ranking_atp.json` (lean index). Se não, o ranking exibido ficará desatualizado (pontos, YTD) até o próximo carregamento completo.

#### G-3. Estado do torneio após `desistir_do_torneio()`
Verificar se o arquivo `torneio_atp.json` (ou `wta`) é apagado ou marcado como `finalizado` após a desistência + simulação restante. Se não for apagado, `carregar_torneio_api()` continuará retornando o torneio "ativo" na semana seguinte.

Referência: `_estado_torneio_ativo()` em `calendario.py` verifica `fase_atual == "finalizado"` — se o arquivo não for limpo ou marcado, o bug persiste.

#### G-4. `POST /api/treinamento/executar` — sem `avancar_semana()` causa drift de semana
Se o jogador treinar sem avançar semana e depois chamar `GET /api/calendario/atual`, verá a mesma semana. Mas se o frontend depois chamar `POST /api/calendario/avancar`, avançará corretamente. Verificar se há salvaguarda para evitar duplo avanço (idempotência de `avancar_semana()`).

#### G-5. Ranking lean após `distribuir_pontos_torneio()`
Confirmar que `distribuir_pontos_torneio()` chama `ranking.salvar_ranking()` no final, garantindo que o índice lean reflete os novos pontos. Se não chamar, os pontos ficam apenas em memória e somem no próximo carregamento.

---

## Prioridade de Correção

| # | Fix | IA | Impacto | Esforço |
|---|---|---|---|---|
| 1 | `POST /api/torneio/desistir` — simular restante + pontos + avanço | Claude | Crítico | Baixo |
| 2 | `POST /api/treinamento/executar` — adicionar `avancar_semana()` | Claude | Alto | Baixo |
| 3 | Frontend após `desistir` — atualizar store e navegar | Claude | Alto | Baixo |
| 4 | `desistir_do_torneio()` + `simular_torneio_restante()` — auditoria | Codex | Crítico | Médio |
| 5 | `distribuir_pontos_torneio()` para jogador eliminado | Codex | Alto | Médio |
| 6 | Session state após `avancar_semana()` | Gemini | Alto | Médio |
| 7 | Estado do torneio após desistência — limpeza de arquivo | Gemini | Alto | Baixo |
| 8 | Davis: `distribuir_pontos_davis()` após `simular-atual` final | Codex | Médio | Baixo |
| 9 | Ranking lean após distribuição de pontos | Gemini | Médio | Baixo |
| 10 | Davis Cup `/criar` — remover mock de convocação | Codex | Médio | Alto |

---

## Funcionalidades do Mapeamento Não Auditadas (Prioridade Baixa)

- `mercado.py` — contratar/demitir profissionais
- `email.py` — inbox e ações
- `duplas.py` — sugestões, busca, convite
- `ranking.py` — ATP/WTA/duplas/nações
- `mundo.py` — ao vivo, race, bracket externo
- `historico.py` — GOAT, campeões
- `logs.py` — observabilidade

Nenhum desses tem relatos de bugs. Auditar somente se problemas surgirem.
