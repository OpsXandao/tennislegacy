# Divisão de trabalho v5 — Gemini CLI

> Status: documento histórico de planejamento.
> Referência atual de arquitetura e integrações: `codex.md`, `docs/funcionalidades_integracoes.md` e `docs/refactoring_log.md`.

Este documento detalha as tarefas de **limpeza de código duplicado**, **remoção de código morto** e **centralização de utilitários** identificadas na análise de 28/02/2026.

---

## GEMINI CLI — Consolidação e Limpeza

As tarefas abaixo focam em eliminar redundâncias e garantir que o projeto utilize uma única fonte de verdade para funções críticas.

### G5-N1: Centralização de `normalizar_nome`
| Arquivo | Ação |
|---------|------|
| `src/nome_utils.py` | Substituir implementação pela versão com `lru_cache` de `src/jogador.py`. |
| `src/jogador.py` | Remover a implementação local de `normalizar_nome` e importar de `src.nome_utils`. |
| `src/controller.py` | Remover `_normalizar_nome` e usar `src.nome_utils.normalizar_nome`. |
| `src/ranking.py` | Verificar se já usa `src.nome_utils` (confirmado na análise). |
| `src/duplas.py` | Garantir uso de `src.nome_utils.normalizar_nome`. |

### G5-N2: Remoção de Código Morto (Dead Code)
| Arquivo / Objeto | Ação |
|-----------------|------|
| `src/torneio_display.py` | **Remover arquivo**. É composto apenas por wrappers não utilizados. |
| `src/torneio_core.py` | Remover o método `simular_torneio_npc_lite` (não utilizado). |
| `src/torneio_npc.py` | Remover wrappers `simular_partidas_npc`, `avancar_fase` e `extrair_nome_puro`. |
| `src/torneio.py` | Limpar exports no `__all__` que não têm consumidores reais (avaliar com cautela). |

### G5-N3: Unificação de Constantes e Utilitários
| Alvo | Ação |
|------|------|
| `normalizar_superficie` | Centralizar em `src/superficie_utils.py`. Remover wrappers em `src/simulacao_partida.py` e `src/match_dynamics.py`. |
| `PONTOS_WTA` | Garantir que `src/pontuacao.py` use as constantes de `src/wta_constants.py` em vez de redefinir em `PONTOS_DUPLAS`. |

---

## Ordem de Execução

1. **G5-N1 (Nomes):** É a mudança mais perigosa pois afeta buscas em dicionários/listas. Deve ser feita primeiro e validada.
2. **G5-N3 (Superfície/Pontos):** Limpeza de redundâncias de dados.
3. **G5-N2 (Código Morto):** Remoção física de arquivos e métodos após garantir que nada quebra.

---

## Regras de Segurança para GEMINI CLI nesta Sprint

1. **Validação de Impacto:** Antes de remover qualquer função, rodar `grep` em todo o `src/` para confirmar ausência de chamadas.
2. **Compatibilidade:** Ao centralizar `normalizar_nome`, manter a assinatura idêntica para não quebrar módulos dependentes.
3. **Preservação de Dados:** Não alterar `src/migracoes.py` ou `src/save.py` de forma que invalide saves existentes.
