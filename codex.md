# TennisLegacy - Codex

## Visao geral
TennisLegacy e um jogo de tenis em texto com foco em carreira, ranking ATP e torneios
semanais. O jogador cria um atleta, participa de torneios e evolui ao longo da temporada.

## Como rodar
- Requisitos: Python 3.10+
- Dependencias: ver `requirements.txt`
- Executar: `python main.py`

## Estrutura do projeto
- `main.py`: ponto de entrada
- `src/`: codigo do jogo
  - `interface/`: menus e fluxo de tela
  - `torneio.py`: logica do torneio
  - `jogador.py`: modelo do jogador e serializacao
  - `ranking.py`: ranking e pontuacao
  - `save.py`: persistencia em JSON
  - `calendario.py`: calendario de torneios
- `db/`: dados base (calendario, ranking inicial)
- `saves/`: saves gerados por usuario

## Logica do jogo (fluxo e regras)
- O jogo inicia em `main.py`, que carrega menus e decide entre novo jogo ou continuar.
- Novo jogo cria um jogador e inicia a temporada; jogo carregado restaura JSONs do `saves/`.
- A temporada e baseada em semanas com torneios do `db/calendario.json`.
- O jogador escolhe um torneio disponível; o menu do torneio controla fases, confrontos e resultados.
- Cada fase conclui partidas, avanca chaves e registra resultados; ao fim do torneio ou eliminacao, retorna ao menu da temporada.
- O ranking ATP e atualizado apos cada torneio com base na pontuacao do evento e desempenho.

## Padroes de codigo
- Preferir imports absolutos a partir de `src.*`
- Evitar `sys.path` em runtime; use o pacote `src`
- Manter funcoes pequenas e com uma unica responsabilidade
- Validar entrada de usuario com mensagens claras
- Separar IO (prints/inputs) de regras de negocio quando possivel
- Manter JSONs com estrutura estavel e chaveadas por nomes claros

## Persistencia (JSON)
- `saves/<save>/jogador.json`: estado do jogador
- `saves/<save>/ranking_atp.json`: ranking local
- `saves/<save>/torneio_atp.json`: estado do torneio em andamento
- `db/calendario.json`: torneios por semana

## Diretrizes para manutencao
- Nao duplicar logica entre menus e dominio
- Centralizar regras de torneio no `TorneioATP250`
- Criar funcoes utilitarias para validacoes repetidas
- Padronizar nomes de fases do torneio
- Documentar qualquer alteracao na estrutura dos JSONs

## Proximos passos sugeridos
- Separar a camada de simulacao (partidas) da camada de UI
- Criar testes basicos de serializacao e avancar fase
- Adicionar logs de debug opcional via flag
- Padronizar imports e estrutura do pacote
- Limpar warnings e inconsistencias de dados
- Documentar fluxo principal e arquivos de save
