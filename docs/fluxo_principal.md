# Fluxo principal do jogo

## Entrada e inicializacao
- `main.py` chama `menu_inicial()` em `src/interface/menu_inicial.py`.
- O jogador escolhe entre novo jogo ou carregar um save.
- Novo jogo cria o jogador, inicializa arquivos de save e adiciona ao ranking.
- Jogo carregado reidrata o jogador a partir de `saves/<save>/jogador.json`.

## Decisao de fluxo
- `fluxo_principal()` em `src/controller.py` decide o proximo menu.
- Se ha torneio ativo e o jogador esta vivo, abre `menu_torneio`.
- Se nao ha torneio ativo (ou fase finalizada/eliminacao), abre `menu_temporada`.

## Temporada
- `menu_temporada()` lista torneios da semana via `src/calendario.py`.
- O jogador pode escolher um torneio ou avancar a semana.
- Ao escolher torneio, `src/torneio.py` cria a estrutura e salva o estado.

## Torneio
- `menu_torneio()` controla partidas, confrontos e resultados.
- Partidas do jogador chamam `jogar_partida()` e atualizam o estado do torneio.
- NPCs simulam confrontos restantes e o sistema avanca fases ate a final.
- Ao terminar ou eliminar o jogador, a temporada avanca para a proxima semana.
