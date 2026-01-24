# Arquivos de save

Cada save fica em `saves/<save>/` e armazena o estado do jogador, ranking local e torneio.

## `jogador.json`
- Origem: `src/jogador.py` e `src/save.py`.
- Contem atributos e status do jogador.
- Campos principais:
  - `nome`, `idade`, `nacionalidade`
  - `xp`, `nivel`, `semana`
  - `energia`, `ritmo_jogo`, `moral`, `dinheiro`
  - `atributos`: dicionario de atributos tecnicos

## `ranking_atp.json`
- Origem: `src/ranking.py` e `src/save.py`.
- Ranking local do save (lista de jogadores).
- Campos principais por jogador:
  - `nome`, `nacionalidade`, `pontos`
  - `atributos` e `overall`
  - `id` pode aparecer em dados base/importados

## `torneio_atp.json`
- Origem: `src/torneio.py`.
- Estado do torneio em andamento.
- Estrutura:
  - `torneio`, `semana`, `fase_atual`
  - `jogador`, `jogador_vivo`
  - `rodadas`: confrontos por fase
  - `resultados`: resultados por fase

## Observacoes
- O ranking global base fica em `db/ranking_atp.json`.
- O calendario de torneios fica em `db/calendario.json`.
