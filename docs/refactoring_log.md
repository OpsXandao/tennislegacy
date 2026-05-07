# Refactoring Log

## 2026-03-01 — Gemini (Duplas Enhancements & Bot Removal)

Arquivos tocados:
- `src/duplas.py`
- `src/jogador.py`
- `src/constantes.py`
- `src/ranking.py`
- `src/interface/menu_temporada.py`
- `src/tournament_manager.py`
- `src/torneio_core.py`
- `db/calendario.json` e `db/calendario_wta.json`

Entregas:
1. **Remoção de Bots Genéricos ("Bot Externo")**:
   - Ajustada a geração de talentos caso o ranking fique com menos de 300 jogadores.
   - Adicionada geração de nomes de NPCs reais para preencher qualquer buraco no bracket dos torneios, eliminando de vez "Bot Externo X".
2. **Calendário Expandido (52 semanas)**:
   - Os calendários ATP e WTA foram totalmente reconstruídos e expandidos para um formato contínuo de 52 semanas, corrigindo a posição do US Open e semanas faltantes na gira de grama.
3. **Aprimoramento de Duplas**:
   - Registros de vínculo entre parcerias de duplas implementados em `jogador.py` via `vinculos_dupla`.
   - Adicionado novo atributo `"duplas": 60` em `constantes.py` propagado na normalização.
   - Sinergia em `duplas.py` calcula bônus no overall baseado no tempo jogado junto e taxa de vitória (win rate).
   - O menu da temporada categoriza parceiros para convite em "PARCEIROS ANTERIORES" e "NOVOS CANDIDATOS".
   - `ranking.py` separa "Especialistas de Duplas" que não pontuam em simples.

## 2026-03-01 — Codex (Split por responsabilidade + compatibilidade)

Arquivos tocados:
- `src/patrocinios.py` (novo)
- `src/imprensa.py` (novo)
- `src/fadiga.py` (novo, já existente no branch)
- `src/match_config.py` (novo, já existente no branch)
- `src/management.py` (reduzido + re-exports)
- `src/progressao.py` (re-export de `fadiga`)
- `src/jogar_partida.py` (re-export de `match_config`)

Entregas:
1. `src/management.py` foi dividido por domínio:
- `src/patrocinios.py`: regras de patrocinadores, propostas, pagamento e migração.
- `src/imprensa.py`: banco de perguntas, perfil de entrevista e fluxo de mídia.
- `src/management.py` mantém equipe/staff e carreira, com:
  - `from src.imprensa import *  # backward compat`
  - `from src.patrocinios import *  # backward compat`

2. `src/progressao.py` e `src/jogar_partida.py` seguem com compatibilidade por re-export:
- `from src.fadiga import *  # backward compat`
- `from src.match_config import *  # backward compat`

3. Validação técnica (verificada 2026-03-01 — ambiente com venv ativo):
- `python3 -m py_compile` em todos os 7 arquivos ✅
- `black --check` em todos os 7 arquivos ✅ (nenhuma alteração necessária)
- smoke import `from src.management import disparar_entrevista, PROFISSIONAIS_DISPONIVEIS, pode_assinar_patrocinio` ✅
- smoke import `from src.progressao import handle_fadiga_e_lesao, treinar_semana, handle_xp_e_level_up` ✅
- smoke import `from src.jogar_partida import jogar_partida, criar_config_partida; from src.match_config import ConfigPartida` ✅
- import de módulos principais (`controller`, `calendario`, `torneio_core`, `davis_cup`, `progressao`, `ranking`, `save`) ✅

Tamanhos finais (após correção de truncamento pelo agente):
| Arquivo | Linhas |
|---------|--------|
| `management.py` | 564 (era 2890) |
| `patrocinios.py` | 1310 (novo) |
| `imprensa.py` | 2763 (novo) |
| `fadiga.py` | 380 (novo) |
| `progressao.py` | 401 (era 761) |
| `match_config.py` | 104 (novo) |
| `jogar_partida.py` | 1506 (era 1605) |

Nota: `patrocinios.py` inclui também `gerar_proposta_empresario`, `gerar_propostas_carreira_email`, `gerar_convites_midia_email`, `processar_acao_email_carreira` (movidas de management por coesão). Circular import com `EMPRESARIOS_DISPONIVEIS` resolvido com helper de lazy import `_obter_empresarios_disponiveis()`.

Observações:
- Objetivo de manter importadores existentes sem alteração foi preservado via re-exports.
- Ajustes de UI de duplas/vínculo já estavam implementados no branch e foram mantidos.

## 2026-02-28 — Codex (Fase 1, Zona Domínio de Jogo)

Arquivos tocados:
- `src/pontuacao.py`
- `src/simulacao_partida.py`
- `docs/prints_torneio.md`

Entregas:
1. `src/pontuacao.py`
- Removido `print` em `distribuir_pontos_torneio` no caso de arquivo ausente.
- A função agora retorna mensagem textual nesse cenário para o chamador decidir se exibe.

2. `src/simulacao_partida.py`
- `EstatisticasPartida.exibir()` deixou de imprimir diretamente.
- Agora retorna `str` formatada (bloco completo de estatísticas) para a camada de interface consumir.

3. `docs/prints_torneio.md`
- Inventário de chamadas de `print*` em `src/torneio.py` com linha, função e proposta de retorno ideal.

Observações:
- Mudanças feitas apenas nos arquivos da zona Codex nesta fase.
- Há uma falha de teste pré-existente fora desta zona (`test_tournament_manager_unittest`), não alterada aqui.

## 2026-02-28 — Claude (Zona Interface — Black CI + Lint)

Arquivos tocados:
- `src/interface/menu_inicial.py` — black format (linhas longas)
- `src/interface/match_info.py` — F541: 2 f-strings sem placeholder
- `src/interface/menu_davis.py` — F401: `print_magenta` não usado; F541: f-string
- `src/interface/menu_jogador.py` — F541: f-string sem placeholder
- `src/interface/menu_temporada.py` — F841: `hist` não usado; F401: `carregar_historico`
- `src/eventos_exibicao.py` — black format
- `src/gerador_nomes.py` — black format
- `src/duplas.py` — black format
- `src/torneio_npc.py` — black format

Entregas:
1. `src/interface/` — passa `black --check` ✅ e `flake8 --select=F401,F541,F811,F841` ✅
2. Arquivos neutros formatados — CI reduzido de 22 → 12 arquivos pendentes
3. `docs/divisao_ias_v5.md` criado com auditoria completa e plano por IA

Restam na fila do CI: zona Gemini (`save.py`, `ranking.py`, `progressao.py`, `dados.py`, `management.py`) e `scripts/`, `tests/`.

Bugs críticos corrigidos nesta fase:
- `menu_torneio.py:159` — `estado['fase_atual']` → `estado.get('fase_atual', '?')` (KeyError)
- `menu_torneio.py:376` — mesmo padrão (KeyError)
- `menu_torneio.py:383` — mesmo padrão (KeyError)
- `menu_jogador.py:1542` — `jogador.avisos_patrocinio.pop(...)` → `getattr(..., {}).pop(...)` (AttributeError)
- `menu_jogador.py:938` — `proposta['titulo']` → `proposta.get('titulo', '?')` (KeyError)

Bugs confirmados como falso-positivo:
- `eventos_exibicao.py:87` `random.sample(ranking_bots, 2)` — protegido pela guarda da linha 84.
- `gerador_nomes.py:70-72` `random.choice` — `or ["Doe"]` garante lista não vazia.
- `calendario.py:742` divisão por zero — `if psico` garante `len(psico) > 0`.

## 2026-02-28 — Codex (Fase 2, split inicial de torneio)

Arquivos tocados:
- `src/torneio_core.py` (novo, cópia do monólito original)
- `src/torneio.py` (agora wrapper/re-export)
- `src/torneio_npc.py` (wrappers de compatibilidade para funções externas)
- `src/torneio_display.py` (novo, wrappers de display)

Entregas:
1. Split inicial concluído sem quebra de API pública:
- `src/torneio.py` mantém os mesmos símbolos exportados (`Torneio`, `criar_torneio`, `salvar_torneio`, `carregar_torneio`, `simular_partidas_npc`, `avancar_fase`, `extrair_nome_puro`).
- Implementação principal movida para `src/torneio_core.py`.

2. Módulos auxiliares preparados para aprofundar a separação na próxima etapa:
- `src/torneio_npc.py` com wrappers de compatibilidade para chamadas externas.
- `src/torneio_display.py` com wrappers de exibição.

Observação:
- Nesta etapa foi priorizada compatibilidade e segurança de merge. A extração fina de métodos da classe para módulos especializados segue em iteração posterior.
