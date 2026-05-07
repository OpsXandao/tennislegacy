# Divisão de trabalho v4 — Claude / Codex / Gemini

> Status: documento histórico de planejamento.
> Referência atual de arquitetura e integrações: `codex.md`, `docs/funcionalidades_integracoes.md` e `docs/refactoring_log.md`.

Baseado na v3 (consultar `divisao_ias_v3.md` para features novas N-*).
Esta versão adiciona **bug fixes novos** encontrados via flake8 + análise lógica.

Regras: sem reescritas do zero · sem abstrações para uso único · sem renomear em massa.

---

## Tarefas v3 ainda pendentes (manter)

Ver `divisao_ias_v3.md` — tarefas T6–T17, C4–C9, G1–G4 e features N-* continuam válidas.

---

## Bug fixes novos — Sprint atual

### CLAUDE — src/interface/

| ID | Arquivo | Linha(s) | Severidade | Problema |
|----|---------|----------|------------|---------|
| C-N1 | menu_temporada.py | 435–437 | CRÍTICO | Imports duplicados no meio do arquivo: `SistemaRanking` e `get_caminho_ranking_save` importados 2x (F811). `fundir_dupla` importado mas nunca usado (F401). Mover tudo pro topo e remover. |
| C-N2 | menu_temporada.py | 488 | ALTA | `import time; time.sleep(1)` inline com ponto-e-vírgula (E702, E402). Mover `import time` pro topo. |
| C-N3 | menu_temporada.py | 498 | ALTA | `candidatos.remove(npc)` sem try-except. Se `npc` não estiver na lista, lança `ValueError`. Trocar por list comprehension: `candidatos = [c for c in candidatos if c != npc]`. |
| C-N4 | menu_inicial.py | 22, 28, 44 | ALTA | Recursão `return menu_inicial()` em vez de loop `while True`. Com inputs inválidos repetidos pode causar stack overflow. |
| C-N5 | menu_inicial.py | 55–56 | MÉDIA | Uso de `builtins.nome_save` e `builtins.jogador` como estado global. Anti-pattern. Avaliar passar como parâmetros para `fluxo_principal`. (Pode ser intencional por limitação de arquitetura — verificar antes de alterar.) |
| C-N6 | menu_jogador.py | 608 | MÉDIA | `", ".join(foco[:3])` sem validar se `foco` é None. Se `foco = None`, `join` quebra. Trocar por `foco or []`. |
| C-N7 | interface/* | vários | BAIXA | Múltiplos W291/W293 (whitespace em linhas em branco) e E501 (linhas > 120 chars). Rodar `black .` resolve a maioria. |

---

### CODEX — src/torneio.py, simulacao_partida.py, davis_cup.py, pontuacao.py, calendario.py, controller.py

| ID | Arquivo | Linha(s) | Severidade | Problema |
|----|---------|----------|------------|---------|
| X-N1 | torneio.py | 1289 | CRÍTICO | `estado["resultados"][fase]` sem `.get()`. Se a fase não existir no dict, KeyError. Usar `.get(fase, [])`. |
| X-N2 | torneio.py | 1588, 1681 | CRÍTICO | Mesmo padrão: `estado["resultados"][fase].extend(...)` sem verificar se fase existe. Usar `estado["resultados"].setdefault(fase, []).extend(...)`. |
| X-N3 | torneio.py | 2422–2424 | ALTA | `jogador_dict["nome"]`, `adversario_dict["nome"]`, `vencedor_dict["nome"]` sem `.get()`. `garantir_dict_jogador()` garante que é dict mas não garante chave `"nome"`. Usar `.get("nome", "")`. |
| X-N4 | torneio.py | 2, 33 | MÉDIA | `json` importado mas não usado (F401). 14 constantes importadas de `torneio_constants` que não são usadas em torneio.py (F401). Remover imports desnecessários. |
| X-N5 | torneio.py | 1528, 1614, 2520 | BAIXA | Variáveis `fases_ordem`, `campeao`, `confronto_jogador` atribuídas mas nunca usadas (F841). Remover. |
| X-N6 | davis_cup.py | 718–780 | CRÍTICO | **Bug já listado como T7 na v3** — Partida de duplas sempre simulada mesmo quando time já tem 2 vitórias. O placar final 2-0 vira 3-0. Condição de encerramento deve ser verificada antes de simular a dupla. |
| X-N7 | davis_cup.py | 827 | ALTA | `estado["resultados_confrontos"].append(resultado)` sem `.setdefault()`. Se estado antigo não tem essa chave, KeyError. Usar `estado.setdefault("resultados_confrontos", []).append(resultado)`. |
| X-N8 | davis_cup.py | 13 | BAIXA | `json` importado mas não usado (F401). Remover. |
| X-N9 | davis_cup.py | 285, 379, 383, 384, 388, 625, 722, 794, 1036 | BAIXA | F-strings sem placeholders (F541). São 9 ocorrências — trocar `f"..."` por `"..."`. |
| X-N10 | calendario.py | 432 | ALTA | `status.setdefault("nivel", "lesionado" ...)` define nível como `"lesionado"`, mas o código compara com `"limitado"`, `"desconforto"`, `"saudavel"`. O valor `"lesionado"` nunca bate em nenhuma comparação — lesões nunca progridem. Alinhar o valor inicial com os valores usados nas comparações. |
| X-N11 | controller.py | 44, 99 | BAIXA | F-strings sem placeholders (F541). Trocar `f"..."` por `"..."`. |

---

### GEMINI — src/ranking.py, save.py, jogador.py, progressao.py, jogar_partida.py, duplas.py

| ID | Arquivo | Linha(s) | Severidade | Problema |
|----|---------|----------|------------|---------|
| G-N1 | jogar_partida.py | 1039 | CRÍTICO | `perdedor_final = jogador_b if vencedor_final is jogador_a else jogador_a` usa `is` (identidade) em vez de `==` (igualdade). Se `vencedor_final` e `jogador_a` têm o mesmo conteúdo mas são objetos diferentes, retorna o perdedor errado. Trocar `is` por comparação de nome/ID. |
| G-N2 | jogador.py | 460 | ALTA | `jogador.atributos = dados["atributos"]` sem `.get()`. Em saves antigos ou corrompidos sem essa chave, KeyError. Trocar por `dados.get("atributos", {})` com fallback de atributos padrão. |
| G-N3 | duplas.py | 107 | ALTA | `p['nome'] != jogador.nome` sem `.get()`. Se `p` for dict sem chave `'nome'`, KeyError. Trocar por `p.get('nome') != jogador.nome`. |
| G-N4 | duplas.py | 107 | MÉDIA | Mesma linha: comparação sem normalização de nome. Nomes com acentos ou case diferentes não coincidem. Trocar por `normalizar_nome(p.get('nome', '')) != normalizar_nome(jogador.nome)`. (Atenção: `normalizar_nome` já importada, mas marcada como F401 — ver G-N5.) |
| G-N5 | duplas.py | 2 | BAIXA | `normalizar_nome` importada mas (segundo flake8) não usada. Isso contradiz G-N4: se estiver realmente não usada, a correção G-N4 resolve o F401 ao mesmo tempo. |
| G-N6 | ranking.py | — | BAIXA | F811: `SistemaRanking` re-importada em `menu_temporada.py:436` (responsabilidade Claude, ver C-N1), gerando conflito de nome. Não requer mudança em ranking.py — só limpeza no menu. |

---

## Ordem de execução sugerida (sprint atual)

Corrigir bugs críticos primeiro, depois os demais em paralelo:

**Prioridade 1 — Bugs que causam crash:**
- X-N1, X-N2 (KeyError em torneio.py)
- X-N6 (Davis Cup — T7 da v3, já pendente)
- X-N7 (KeyError em davis_cup.py)
- G-N1 (comparação `is` vs `==` em jogar_partida.py)
- G-N2 (KeyError em jogador.py)

**Prioridade 2 — Lógica incorreta:**
- X-N3 (acesso sem `.get()` em torneio.py)
- X-N10 (nível de lesão inconsistente em calendario.py)
- G-N3, G-N4 (comparação de nome em duplas.py)
- C-N3 (ValueError em menu_temporada.py)
- C-N4 (recursão em menu_inicial.py)

**Prioridade 3 — Lint e style:**
- C-N1, C-N2, C-N7 (imports duplicados, inline import, whitespace)
- X-N4, X-N5, X-N8, X-N9, X-N11 (imports e f-strings)
- G-N5, G-N6 (imports não usados)

---

## Regras gerais (imutáveis — mesmas da v3)

- Não criar abstrações para uso único.
- Não renomear em massa.
- Não reformatar arquivos inteiros.
- Não mover arquivos de lugar.
- Não adicionar dependências externas.
- Não criar testes.
- Não mudar assinaturas públicas sem avisar as outras IAs.
- Documentar qualquer mudança de esquema JSON em `docs/saves.md`.
- Claude não toca em domain logic. Codex não toca em ranking.py/save.py. Gemini não toca em interface/.
