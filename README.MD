## Fluxograma de Navegação

### 1. Menu Inicial
- [1] Novo Jogo — Cria jogador, vai para Menu Temporada.
- [2] Carregar Jogo — Carrega estado salvo, direciona para o menu correto.

### 2. Menu Temporada
- Exibe semana e torneios disponíveis.
- [1] Escolher torneio — Vai para Menu Torneio.
- [2] Avançar semana — (Opcional) Próxima semana, recarrega torneios.

### 3. Menu Torneio
- Exibe informações do torneio, fase, confrontos e status.
- [1] Jogar partida (se houver)
- [2] Ver confrontos
- [3] Ver resultados
- [4] Salvar jogo
- [5] Sair
- Avança fases até final do torneio.

- Se torneio termina ou jogador é eliminado: retorna ao Menu Temporada.

#### Resumo do fluxo

Menu Inicial
|
V
Menu Temporada
|
V
Menu Torneio
|
+-- [Avança fases] --+
| |
+---------<---------+
[Fim do torneio ou eliminação]
|
V
Menu Temporada (semana seguinte)

## Documentacao
- `docs/fluxo_principal.md`: fluxo principal do jogo
- `docs/saves.md`: estrutura dos arquivos de save
