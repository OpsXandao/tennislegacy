# Auditoria de Qualidade de Código — TennisLegacy
> Data: 2026-03-19
> Auditor: Code Reviewer Agent (Claude Sonnet 4.6)
> Branch: feat/frontend

---

## Sumário Executivo

O projeto é bem estruturado para um jogo de simulação em Python com frontend React — a separação em camadas (UI / domínio / persistência) é clara e a migração para API + frontend está bem conduzida. Os problemas mais graves estão concentrados em dois pontos: (1) um endpoint da API retorna uma variável `serializados` que nunca é definida, causando crash garantido em produção; (2) o qualifying nunca simula partidas reais — o primeiro jogador de cada confronto sempre avança, tornando a fase decorativa. A camada de sessão da API carece de sincronização thread-safe e o cache em memória de matches sobrevive a restarts sem invalidação de tempo de vida. Os demais issues são de design e manutenibilidade, notáveis pelo volume de monkey-patching no módulo central de torneio.

---

## P0 — Críticos

### [api/routes/jogador.py:337-340] Endpoint `/patrocinios` quebrado — NameError garantido

```
@router.get("/patrocinios")
def get_patrocinios(session: Session = Depends(obter_sessao_ativa)):
    ...
    return {"patrocinios": serializados}
```

A função contém apenas `...` (Ellipsis) e depois referencia `serializados`, que nunca foi atribuída. Qualquer chamada a `GET /api/jogador/patrocinios` gera `NameError: name 'serializados' is not defined` com HTTP 500. A UI que depender desse endpoint ficará permanentemente quebrada. O endpoint parece ter sido criado como placeholder e nunca implementado.

---

### [src/torneio_core.py:967] Qualifying nunca simula partidas — sempre avança o lado esquerdo do confronto

```python
vencedores = [c[0] for c in confrontos]  # Simplificado: sementes passam
for _ in range(len(fases_qualy) - 1):
    random.shuffle(vencedores)
    vencedores = vencedores[: len(vencedores) // 2]
```

O método `jogar_qualy` sempre seleciona `c[0]` (o primeiro elemento do confronto) como vencedor, sem qualquer simulação probabilística. Isso garante que os jogadores com menor índice no array sempre passam pelo qualifying — quebrando completamente a competição da fase classificatória. A chance de um jogador mais fraco passar pelo qualy é zero, o que viola expectativas básicas de simulação. Esse código é chamado pela UI de texto (menu_torneio), onde o jogador humano pode estar no qualy.

---

### [api/routes/jogador.py:404] KeyError não tratado em `assinar-patrocinio`

```python
pat = PATROCINADORES_DISPONIVEIS[body.patrocinio_id]
```

A linha 400 já valida se o patrocínio existe via `pode_assinar_patrocinio`, mas um race condition (ou dado corrompido) entre a validação e o acesso ao dicionário pode resultar em `KeyError` não capturado, causando HTTP 500 em vez de um erro semântico controlado. Deveria usar `.get()` com fallback ou envolver em try/except.

---

### [api/routes/jogador.py:357-358 e 394-395] AttributeError quando ranking é None

```python
rk = session.ranking_atp if j.genero == "masculino" else session.ranking_wta
posicao = rk.obter_posicao(j.nome) or 9999
```

Nos endpoints `/patrocinios-disponiveis` e `/assinar-patrocinio`, `rk` não é verificado contra `None` antes de ser usado. Em contraste, o endpoint principal `GET /api/jogador` (linha 73-75) faz essa verificação corretamente. Se o arquivo de ranking não existir no disco (save novo ou corrompido), `rebuild_rankings()` pode retornar um `SistemaRanking` com lista vazia, mas `obter_sessao_ativa` poderia em tese retornar `None` em certas condições de falha. A inconsistência de defesa é o problema real — dois endpoints protegem, dois não protegem.

---

### [src/torneio_core.py:688-693] IndexError potencial em `_montar_qualifying` com número ímpar de jogadores

```python
for i in range(0, len(qualy_players), 2):
    confrontos.append(
        (
            self.garantir_dados_completos(qualy_players[i]),
            self.garantir_dados_completos(qualy_players[i + 1]),  # <-- crash se len impar
        )
    )
```

Se `qualy_players` tiver número ímpar de elementos após `random.shuffle`, o acesso `qualy_players[i + 1]` gera `IndexError` na última iteração. O código antes da chamada tenta garantir `num_jogadores_qualy` pares via `_get_bot_pool`, mas essa garantia pode falhar se o pool de bots retornar menos jogadores do que o solicitado. Não há guarda `if i + 1 < len(qualy_players)`.

---

## P1 — Importantes

### [src/torneio_core.py:1395-1404] Monkey-patching de métodos na classe Torneio ao final do módulo

```python
if not hasattr(Torneio, "remover_confronto_do_jogador"):
    Torneio.remover_confronto_do_jogador = _torneio_remover_confronto_do_jogador
if not hasattr(Torneio, "desistir_do_torneio"):
    Torneio.desistir_do_torneio = _torneio_desistir_do_torneio
Torneio.simular_torneio_restante = _torneio_simular_torneio_restante
if not hasattr(Torneio, "_distribuir_pontos_duplas"):
    Torneio._distribuir_pontos_duplas = _torneio_distribuir_pontos_duplas
```

Quatro métodos são atribuídos dinamicamente à classe `Torneio` após sua definição, incluindo um sem a guarda `hasattr` (`simular_torneio_restante`). Isso significa que `simular_torneio_restante` sobrescreve qualquer implementação prévia a cada import do módulo, o que pode causar comportamento inesperado se o módulo for re-importado ou recarregado. O padrão correto é definir os métodos diretamente na classe. O `_Forwarder` em `torneio.py` adiciona mais uma camada de indireção que dificulta stack traces.

---

### [api/session.py:93-103] Pool de sessões sem locking — race condition em ambiente multi-threaded

```python
_sessions_pool: Dict[str, Session] = {}

def obter_sessao_ativa(x_save_name: str = ...) -> Session:
    sessao = _sessions_pool.pop(x_save_name, None)
    ...
    _sessions_pool[x_save_name] = sessao
    return sessao
```

O pool de sessões é um dicionário global mutável compartilhado entre requests. FastAPI com Uvicorn pode processar requests concorrentes via threading (dependendo da configuração). O padrão pop/insert não é atômico no contexto de múltiplas threads, podendo resultar em sessões perdidas ou corrompidas. Para um jogo single-player isso é improvável na prática, mas o padrão é estruturalmente inseguro.

---

### [api/routes/_match_store.py:10-32] Cache em memória de partidas sem TTL ou limite de tamanho

```python
_global_matches_cache: Dict[str, Any] = {}
```

O cache de `MatchRuntime` em memória nunca expira entradas. Partidas antigas, encerradas ou de sessões abandonadas permanecem indefinidamente. Um servidor de longa duração com muitas partidas acumularia vazamentos de memória. Não há nenhum mecanismo de limpeza além de `clear_runtime_cache`, que só é chamado manualmente por `invalidate_other_snapshots`. Para múltiplos saves ou sessões longas, isso pode se tornar um problema real.

---

### [api/routes/_match_runtime.py:814-818] Exceções silenciadas em operações críticas de finalização de torneio

```python
try:
    instancia.simular_npcs_na_fase_atual(instancia.jogador_nome)
    avancar_fase(instancia)
except Exception:
    pass
```

Quando a simulação de NPCs ou o avanço de fase falha após uma partida do jogador, o erro é completamente descartado. Isso pode deixar o torneio em estado inconsistente: a partida do jogador foi registrada mas a fase não avançou, podendo bloquear o progresso do jogo. A mesma exceção silenciada aparece em `_match_runtime.py:189` e `788`. Esses blocos deveriam ao menos chamar `log_erro`.

---

### [src/save.py:115] Print de domínio em módulo de persistência

```python
print(f"📸 Snapshot de carreira registrado (Semana {jogador.semana})")
```

O módulo `save.py` é parte da camada de domínio, não da UI. Prints diretos violam a separação de responsabilidades definida nas próprias convenções do projeto ("IO separado de lógica de domínio"). Esse `print` vai aparecer em contextos de API REST onde não há terminal, poluindo logs do servidor. O mesmo ocorre nas linhas 149 e 152 (`"💾 Estado do torneio salvo com sucesso"` e o erro correspondente).

---

### [src/save.py:110-113] Deduplicação de snapshots por semana ignora ano — pode sobrescrever dados de anos diferentes

```python
if (
    not jogador.snapshots_carreira
    or jogador.snapshots_carreira[-1]["semana"] != jogador.semana
):
    jogador.snapshots_carreira.append(snapshot)
```

A comparação de duplicata verifica apenas `semana`, não o par `(ano, semana)`. Na semana 1 do ano 2027, o snapshot seria bloqueado se o último snapshot for da semana 1 do ano 2026. Após o primeiro ano completo, snapshots de início de temporada são perdidos silenciosamente.

---

### [src/ranking.py:115-118] Cache de nome indexa por objeto dict como valor — referências podem ficar desatualizadas após `update`

```python
def _get_nome_cache(self):
    if self._nome_cache is None:
        self._nome_cache = {normalizar_nome(j): j for j in self.ranking}
    return self._nome_cache
```

O cache mapeia nome normalizado para o objeto `dict` do jogador. Quando `buscar_jogador_por_nome` encontra um jogador lean e chama `j.update(detalhes)`, o objeto é atualizado in-place — isso funciona corretamente. Porém, se `_invalidate_caches` não for chamado após operações que modificam `self.ranking` (como ordenação que não cria novos objetos), o cache pode retornar referências corretas mas com dados inconsistentes. O acesso `self._nome_cache = {normalizar_nome(j): j for j in self.ranking}` reconstrói o dict mas os valores são os mesmos objetos, então modificações in-place são refletidas automaticamente. O risco real é se algum caminho substitui objetos (ex: `self.ranking[i] = novo_dict`) sem invalidar o cache.

---

### [src/torneio_core.py:542-609] `_carregar_estado` aplica sanitização e pode salvar automaticamente — efeito colateral inesperado

```python
if self._reparar_main_draw_se_necessario(estado):
    self._salvar_estado(estado)
```

O método `_carregar_estado` (leitura) pode disparar um `_salvar_estado` (escrita) se detectar inconsistência no main draw. Isso viola o princípio de menor surpresa: chamadas de leitura não devem ter efeitos colaterais de escrita. Em contextos de apenas visualização (ex: `to_api_state`), isso pode causar escritas desnecessárias em disco, criar condições de corrida e dificultar debugging.

---

### [src/torneio_core.py:711-746] Score pool com bônus acumulativos sem cap — probabilidade pode ultrapassar 1.0

```python
prob = prob_participacao(...)
prob = ajustar_prob_participacao_por_contexto(...)
bonus_home = 0.18 if is_home else 0.0
bonus_surface = 0.08 if superficie_match else 0.0
bonus_pr = 0.12 if ... else 0.0
noise = random.uniform(0.0, 0.08)
return prob + bonus_home + bonus_surface + bonus_pr + noise
```

O score final pode facilmente ultrapassar 1.0 (ex: prob=0.85 + home=0.18 + surface=0.08 + pr=0.12 + noise=0.08 = 1.31). Embora esse valor seja usado apenas para ordenação relativa (não como probabilidade direta), o nome da função e o uso de `prob_participacao` sugerem que deveria ser normalizado. O valor não é clampado antes de ser usado como peso de seleção.

---

### [Front/src/app/screens/MatchScreen.tsx] Múltiplos `.catch(() => {})` silenciando falhas de API críticas

```typescript
api.saves.salvar().catch(() => {})
fetchJogador().catch(() => {})
api.partida.ajusteTatico(...).catch(() => {})
```

Ao longo do componente, várias chamadas de API críticas (salvar jogo, buscar estado do jogador, aplicar ajuste tático) têm seus erros completamente silenciados. Se o auto-save falhar, o jogador perde progresso sem nenhuma notificação. Se `fetchJogador` falhar após uma partida, o estado local fica desatualizado. O padrão deveria ser logar ou exibir um aviso discreto para pelo menos os erros de persistência.

---

### [Front/src/app/screens/MatchScreen.tsx:1430-1440] Intervalo de contagem regressiva pode disparar callback após desmontagem

```typescript
const id = window.setInterval(() => {
    setContadorSet((c) => {
        if (c <= 1) {
            window.clearInterval(id)
            continuarSetRef.current()  // pode estar stale
            return 0
        }
        return c - 1
    })
}, 1000)
return () => window.clearInterval(id)
```

O `continuarSetRef.current()` dentro do setter de estado pode ser chamado com uma referência stale se o componente desmontar entre o último tick e a chamada. Embora o cleanup do `useEffect` limpe o intervalo, existe uma janela de race condition entre o último `setContadorSet` enqueue e o `clearInterval` do cleanup. Em React strict mode (desenvolvimento), o efeito monta/desmonta duas vezes, o que pode disparar dois intervalos simultâneos.

---

## P2 — Melhorias

### [src/torneio_core.py] Módulo de 1404 linhas com responsabilidades mistas

O arquivo ainda contém lógica de draw (`_montar_chave_principal`, `_montar_qualifying`), seleção de participantes (`escolher_participantes`, `_selecionar_pool_torneio_realista`), gerenciamento de estado (`_carregar_estado`, `_salvar_estado`), simulação (`simular_npcs_na_fase_atual`), fadiga de NPCs, e funções globais monkey-patched. A extração de `torneio_draw.py`, `torneio_logic.py`, `torneio_sim.py`, `torneio_utils.py` já começou — considerar completar a migração e reduzir `torneio_core.py` ao núcleo da classe `Torneio` e seu ciclo de vida.

---

### [src/simulacao_partida.py:442] Constante de fator de sorte hardcoded na classe

```python
FATOR_SORTE = 0.15  # 15% de variância aleatória
```

Uma constante de balanceamento crítica (que afeta a aleatoriedade de todos os pontos) está hardcoded como atributo de classe. Deveria ser configurável via `ConfigPartida` ou `constantes.py` para facilitar testes de balanceamento sem alterar o código da classe.

---

### [api/routes/partida.py:189-215 e 218-246] Duplicação completa de lógica entre `/estrategia` e `/ajuste-tatico`

Os dois endpoints têm exatamente o mesmo código de parsing de estratégia (detecção de `fm|`, split por `|`, atribuição de mentalidade/abordagem/instrucao). A única diferença é que `/ajuste-tatico` retorna `set_ajustado` no response. Extrair a lógica de parsing para uma função compartilhada eliminaria ~40 linhas de duplicação e garantiria comportamento idêntico.

---

### [src/ranking.py:294-349] `salvar_ranking` com `save_details=True` pode salvar centenas de arquivos individuais silenciosamente

O método itera por todos os jogadores do ranking e, para cada um não-lean, salva um arquivo JSON individual em `saves/<nome>/jogadores/`. Com 2000+ jogadores, isso pode gerar centenas de operações de IO em uma única chamada. Não há batching, progresso ou aviso ao chamador. Considerar uma estratégia de dirty-tracking para salvar apenas jogadores cujos dados mudaram.

---

### [src/save.py:45-96] `atualizar_jogador_no_ranking` chama `ordenar(recalculate=True)` sempre

```python
rk_obj.ordenar(recalculate=True)
rk_obj.salvar_ranking()
```

A cada salvamento do jogador (que ocorre após cada partida), o ranking inteiro é reordenado com recálculo de pontos. Para 2000+ jogadores, isso é uma operação O(n log n) + O(n) desnecessária se apenas os dados de um jogador mudaram. A ordenação só seria necessária se os pontos do jogador mudassem.

---

### [src/ranking.py:281-292] Deduplicação mantém entrada com mais pontos — pode descartar dados mais recentes

```python
if j.get("pontos_ranking", 0) > unicos[chave].get("pontos_ranking", 0):
    unicos[chave] = j
```

A deduplicação usa pontos como critério de desempate, assumindo que mais pontos = entrada mais válida. Mas em cenário de save com pontos expirados aplicados, uma entrada mais antiga com pontos maiores pode substituir a entrada atual com pontos menores. O critério deveria ser temporal (última atualização) ou a presença de dados mais completos.

---

### [api/routes/partida.py:60-148] Endpoint `/scout/{nome_adversario}` faz busca linear em até 500 entradas de ranking

```python
for entrada in ranking.ranking[:500]:
    if normalizar_nome(entrada.get("nome", "")) == nome_norm:
        adversario = entrada
        break
```

O fallback de busca no ranking faz iteração linear até 500 entradas em vez de usar `ranking.buscar_jogador_por_nome()` que tem cache O(1). A chamada correta já existe na classe `SistemaRanking`.

---

### [src/torneio_core.py:617-628] `_parametros_participacao` retorna valores iguais para ATP 500 e ATP 250

```python
if "500" in tipo:
    return {"draw_main": 23, "draw_qualy": 16, "vagas_qualy": 4}
return {"draw_main": 23, "draw_qualy": 16, "vagas_qualy": 4}
```

As categorias ATP 500 e o caso padrão (ATP 250 e outros) retornam exatamente os mesmos valores, sugerindo que os parâmetros corretos para ATP 500 ainda não foram diferenciados.

---

### [Front/src/app/screens/MatchScreen.tsx] Componente com 800+ linhas e ~30+ useState

O componente `MatchScreen` acumula toda a lógica de UI, estado de partida, lógica de estratégia, timers, animações e chamadas de API em um único arquivo. Com ~30 chamadas a `useState`, múltiplos `useEffect` interdependentes e handlers aninhados, a manutenibilidade está comprometida. A lógica de estratégia (`pacoteTatico`, `PLANOS`, aplicação de estratégia via API) e a lógica de simulação automática (intervalos, velocidade) são candidatas naturais a hooks customizados (`useMatchStrategy`, `useAutoPlay`).

---

### [src/torneio_core.py:103-106] Comentário em inglês num codebase em português

```python
# Define best_of_sets based on tournament profile and gender.
# Define number of rounds based on tournament profile.
```

As convenções do projeto estabelecem comentários e variáveis em português. Esses dois comentários em inglês são resíduos que deveriam ser padronizados para manter consistência.

---

## Métricas

- **Total de issues: 20 (P0: 5, P1: 10, P2: 8)**

| Prioridade | Quantidade | Áreas Afetadas |
|---|---|---|
| P0 | 5 | api/routes/jogador.py, src/torneio_core.py |
| P1 | 10 | api/session.py, api/routes/, src/save.py, src/ranking.py, Front/ |
| P2 | 8 | src/torneio_core.py, src/simulacao_partida.py, src/ranking.py, Front/ |

### Issues por arquivo

| Arquivo | P0 | P1 | P2 |
|---|---|---|---|
| `api/routes/jogador.py` | 3 | 0 | 0 |
| `src/torneio_core.py` | 2 | 2 | 4 |
| `api/routes/_match_runtime.py` | 0 | 1 | 0 |
| `api/routes/_match_store.py` | 0 | 1 | 0 |
| `api/routes/partida.py` | 0 | 0 | 2 |
| `api/session.py` | 0 | 1 | 0 |
| `src/save.py` | 0 | 2 | 1 |
| `src/ranking.py` | 0 | 1 | 2 |
| `src/simulacao_partida.py` | 0 | 0 | 1 |
| `Front/src/app/screens/MatchScreen.tsx` | 0 | 2 | 1 |

### Ações recomendadas por prioridade

**Imediato (P0):**
1. Implementar ou remover `GET /api/jogador/patrocinios` — endpoint está broken
2. Corrigir `jogar_qualy` para usar `simular_partida_npc_basica` em vez de selecionar sempre `c[0]`
3. Adicionar guard `if i + 1 < len(qualy_players)` ou garantir número par antes do loop de confrontos
4. Usar `.get()` em vez de acesso direto ao dict em `assinar-patrocinio`
5. Adicionar verificação `if rk is None` nos endpoints que não protegem

**Curto prazo (P1 mais impactantes):**
1. Remover monkey-patching de `Torneio` — mover métodos para dentro da classe
2. Adicionar `threading.Lock` ao `_sessions_pool`
3. Implementar TTL ou limite de tamanho no `_global_matches_cache`
4. Substituir `except Exception: pass` em `_finalizar_torneio` por `log_erro` mínimo
5. Remover prints de domínio de `save.py`
