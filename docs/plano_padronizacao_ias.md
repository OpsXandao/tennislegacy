# Plano Coordenado de Padronização e Refatoração (Claude, Gemini, Codex)

> Status: documento histórico de planejamento.
> Referência atual de arquitetura e integrações: `codex.md`, `docs/funcionalidades_integracoes.md` e `docs/refactoring_log.md`.

**Objetivo:** Padronizar a base de código do TennisLegacy, resolver dívidas técnicas (monólitos, mistura de tipos, acoplamento de UI) e preparar o sistema para escalabilidade, garantindo que as IAs trabalhem em paralelo sem conflitos de merge (overlap de arquivos).

---

## 🧠 Papéis e Focos das IAs

Para evitar que duas IAs tentem alterar o mesmo arquivo ao mesmo tempo, o escopo foi dividido estritamente por domínio:

*   **🤖 Claude (Arquiteto de Domínio):** Focado no coração do jogo e na quebra do maior monólito (`torneio.py`). Especialista em modelagem de dados e regras de negócio complexas.
*   **🌌 Gemini (Especialista em Integração e UI):** Focado em desacoplar a lógica de interface (prints/inputs) da lógica de negócio e gerenciar o fluxo principal (`controller.py`, menus).
*   **⚙️ Codex/Copilot (Engenheiro de Simulação e Dados):** Focado na simulação mecânica (`simulacao_partida.py`), progressão de status (`progressao.py`) e tipagem rigorosa de dados.

---

## 🛤️ Fases de Execução

As IAs devem atuar de forma paralela dentro de cada fase. Uma IA não deve avançar para a próxima fase até que todas tenham concluído a fase atual.

### Fase 1: Fundação e Tipagem (Isolamento de Entidades)
**Objetivo:** Eliminar a ambiguidade entre `dict` e `object`.

*   **Claude:**
    *   **Arquivo(s):** `src/jogador.py`
    *   **Tarefa:** Garantir que a classe `Jogador` tenha métodos `from_dict` e `to_dict` robustos. Remover toda lógica de outros arquivos que manipula atributos do jogador como se fosse um dicionário. Tudo que entra no sistema deve ser convertido para o objeto `Jogador` imediatamente após o load.
*   **Gemini:**
    *   **Arquivo(s):** `src/dados.py`, `src/save.py`
    *   **Tarefa:** Centralizar a leitura/escrita garantindo que os dados puros (JSON) sejam imediatamente reidratados para instâncias concretas antes de serem passados para os controllers.
*   **Codex:**
    *   **Arquivo(s):** `src/match_constants.py`, `src/simulacao_partida.py`
    *   **Tarefa:** Transformar os estados de partida, resultados e estatísticas em `dataclasses` com Type Hints fortes. Chega de passar dicionários soltos como "estado da partida".

### Fase 2: Desacoplamento da Interface (Remoção de Prints)
**Objetivo:** A lógica de negócio deve retornar dados, não imprimir na tela.

*   **Claude:**
    *   **Arquivo(s):** `src/torneio.py`
    *   **Tarefa:** Remover todos os `print`, `print_yellow`, etc., de dentro do core do torneio. A classe `Torneio` deve apenas retornar objetos de estado (`TorneioResult`, `FaseResult`).
*   **Gemini:**
    *   **Arquivo(s):** `src/interface/*` (Todos os menus)
    *   **Tarefa:** Criar formatadores visuais. Receber os objetos de estado retornados pelo back-end e formatá-los para o terminal. Centralizar todos os `safe_input` nestes arquivos.
*   **Codex:**
    *   **Arquivo(s):** `src/progressao.py`, `src/management.py`
    *   **Tarefa:** Remover prints de "Level Up", "Lesão", "Patrocínio". Essas funções devem retornar listas de "Eventos" (ex: `[EventoLevelUp, EventoLesao]`) que a UI consumirá para exibir na tela.

### Fase 3: Quebra de Monólitos (Refatoração Core)
**Objetivo:** Dividir os arquivos gigantes em módulos especializados.

*   **Claude:**
    *   **Arquivo(s):** `src/torneio.py`
    *   **Tarefa:** Fatiar em:
        *   `src/torneio/core.py` (Gerenciamento de estado básico)
        *   `src/torneio/draw.py` (Lógica de chaves, sorteio, seeds, byes R96)
        *   `src/torneio/npc_sim.py` (Simulação em lote de NPCs)
*   **Codex:**
    *   **Arquivo(s):** `src/simulacao_partida.py`
    *   **Tarefa:** Fatiar em:
        *   `src/match/engine.py` (Loop principal)
        *   `src/match/physics.py` (Cálculos de stamina, momento, clima)
        *   `src/match/ai.py` (Decisões de saque/retorno dos NPCs)
*   **Gemini:**
    *   **Arquivo(s):** `src/calendario.py`, `src/pontuacao.py`
    *   **Tarefa:** Limpar os imports inline (`from ... import ...` dentro das funções). Resolver dependências circulares criando um arquivo `src/types.py` para type hints genéricos ou reestruturando a ordem de injeção de dependência.

### Fase 4: Limpeza e Qualidade (Testes)
**Objetivo:** Garantir que as refatorações não quebraram o jogo.

*   **Claude:** Criar testes unitários para a nova lógica de Sorteio de Chaves (`src/torneio/draw.py`), cobrindo especificamente as transições ATP 1000 (R96 -> R64).
*   **Codex:** Criar testes para o motor de jogo (`src/match/engine.py`), garantindo que pontuação e cansaço escalam corretamente.
*   **Gemini:** Corrigir os testes quebrados atualmente por causa de dependências de interface (ex: injetar mocks de interface onde o `colorama` ou `safe_input` eram chamados).

---

## 🚦 Regras de Ouro para as IAs
1. **Não toque no arquivo do colega:** Respeite a divisão de arquivos de cada fase. Se precisar de uma funcionalidade do outro, assuma que ela existirá com a assinatura correta ou use stubs temporários.
2. **Type Hints são obrigatórios:** Todo parâmetro de função nova deve ser tipado (`def func(jogador: Jogador) -> dict:`).
3. **Mantenha os testes rodando:** Se fizer uma mudança arquitetural, rode `pytest` ou `python -m unittest` e conserte o que quebrou antes de dar a tarefa como concluída.
