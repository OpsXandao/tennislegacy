# TennisLegacy - Codex

## Leitura rapida (para IAs)
Use este arquivo como referencia principal antes de explorar o codigo. Ele resume o que
existem em pastas, o fluxo do jogo e onde estao as regras principais.

## Visao geral
TennisLegacy e um jogo de tenis em texto com foco em carreira, ranking ATP e torneios
semanais. O jogador cria um atleta, participa de torneios e evolui ao longo da temporada.

## Como rodar
- Requisitos: Python 3.10+
- Dependencias: ver `requirements.txt`
- Executar: `python main.py`

## Mapa rapido do repositorio (arquivos e pastas)
- `main.py`: ponto de entrada, decide entre novo jogo e carregar.
- `README.MD`: README do projeto com contexto geral.
- `CALENDARIO.md`: referencia textual do calendario/temporada.
- `requirements.txt`: dependencias do projeto.
- `codex.md`: este guia rapido para IAs.
- `src/`: pacote principal do jogo.
  - `src/__init__.py`: inicializacao do pacote.
  - `src/controller.py`: coordena fluxo principal entre menus e dominio.
  - `src/dados.py`: utilitarios para carregar dados base.
  - `src/io_utils.py`: helpers de entrada/saida.
  - `src/jogador.py`: modelo do jogador e serializacao.
  - `src/ranking.py`: ranking e pontuacao.
  - `src/pontuacao.py`: regras de pontuacao de torneios.
  - `src/torneio.py`: regras do torneio, fases e resultados.
  - `src/calendario.py`: calendario de torneios.
  - `src/progressao.py`: evolucao do jogador na temporada.
  - `src/jogar_partida.py`: orquestracao de uma partida.
  - `src/simulacao_partida.py`: simulacao de pontos/partidas.
  - `src/save.py`: persistencia em JSON.
  - `src/interface/`: menus e fluxo de tela (UI/IO).
    - `src/interface/__init__.py`: inicializacao da UI.
    - `src/interface/menu_inicial.py`: menu de entrada.
    - `src/interface/menu_principal.py`: menu principal da temporada.
    - `src/interface/menu_jogador.py`: opcoes do jogador.
    - `src/interface/menu_torneio.py`: navegacao do torneio.
    - `src/interface/menu_temporada.py`: navega semanas/temporada.
    - `src/interface/menu_progressao.py`: tela de progressao/evolucao.
- `db/`: dados base usados ao iniciar uma nova temporada.
  - `db/calendario.json`: torneios por semana.
  - `db/ranking_atp.json`: ranking inicial da ATP.
  - `db/jogador.json`: modelo base de jogador.
  - `db/nacionalidades.json`: lista de nacionalidades.
- `docs/`: documentacao adicional.
  - `docs/fluxo_principal.md`: fluxo macro do jogo.
  - `docs/saves.md`: formato dos arquivos de save.
- `scripts/`: utilitarios avulsos.
  - `scripts/gerar_atributos_psicologicos.py`: gera/ajusta atributos psicologicos.
- `saves/`: saves gerados por usuario (cada pasta e um perfil).

## Fluxo principal do jogo
- Inicio em `main.py` -> menu inicial -> novo jogo ou carregar.
- Novo jogo cria jogador e inicia temporada.
- Carregar jogo restaura JSONs em `saves/<save>/`.
- Temporada baseada em semanas; torneios definidos em `db/calendario.json`.
- Menu do torneio controla confrontos, fases e resultados.
- Ao fim do torneio ou eliminacao: retorna ao menu da temporada.
- Ranking ATP atualizado apos cada torneio.

## Persistencia (JSON)
- `saves/<save>/jogador.json`: estado do jogador.
- `saves/<save>/ranking_atp.json`: ranking local.
- `saves/<save>/torneio_atp.json`: estado do torneio em andamento.
- `db/calendario.json`: torneios por semana.

## Padroes de codigo
- Preferir imports absolutos a partir de `src.*`.
- Evitar `sys.path` em runtime; use o pacote `src`.
- Manter funcoes pequenas e com uma unica responsabilidade.
- Validar entrada de usuario com mensagens claras.
- Separar IO (prints/inputs) de regras de negocio quando possivel.
- Manter JSONs com estrutura estavel e chaveadas por nomes claros.

## Diretrizes para manutencao
- Nao duplicar logica entre menus e dominio.
- Centralizar regras de torneio no `TorneioATP250`.
- Criar funcoes utilitarias para validacoes repetidas.
- Padronizar nomes de fases do torneio.
- Documentar qualquer alteracao na estrutura dos JSONs.

## Proximos passos sugeridos
- Separar a camada de simulacao (partidas) da camada de UI.
- Criar testes basicos de serializacao e avancar fase.
- Adicionar logs de debug opcional via flag.
- Padronizar imports e estrutura do pacote.
- Limpar warnings e inconsistencias de dados.
- Documentar fluxo principal e arquivos de save.

## Realismo (gap atual e melhorias para "ultra realista")
### O que falta hoje (principais lacunas)
- Calendario incompleto (poucas semanas/torneios) e sem tipos completos (250/500/1000/GS, Davis, ITF/Challenger).
- Pontuacao so cobre ATP 250; nao existe regra por categoria nem regra de "best 18".
- Chaves e classificacao simplificadas (sem seeds, byes, wildcards, protegidos, entry list real).
- Partidas sem influencia de superficie (hard/clay/grass), condicao/clima e altitude.
- Modo de partida sem BO5 em Grand Slam e sem diferencas de ritmo por fase.
- Progressao linear (XP por vitoria/derrota) sem curva por idade, teto genetico, forma, treino ou decaimento.
- Fadiga/lesao simplificadas (threshold fixo, sem carga acumulada, calendario/viagem e prevencao).
- Ranking global e de save coexistem, mas sem eventos historicos e sem atualizacao real de outros jogadores.
- Economia simplificada (premiacao unica, sem custo de viagem/treino/equipe).

### Melhorias recomendadas para ultra realismo
#### Temporada e calendario
- Calendario completo de 52 semanas com distribuicao real por superficie e giro regional.
- Tipos de torneio com regras proprias: ATP 250/500/1000, Grand Slam (BO5), Finals, Davis.
- Entry list realista: ranking cutoff, qualy, wildcards, protected ranking, alternates.
- Campeao do ano anterior tende a participar/defender o titulo (salvo lesao/calendario).
- Chaves com seeds e byes conforme categoria.

#### Ranking ATP
- Sistema "best 18" com pontos por categoria e expiracao por torneio especifico (na mesma semana do ano seguinte).
- Pontos diferentes por categoria e rodada (GS/1000/500/250/Challenger).
- Evolucao do ranking de todos os jogadores (NPCs) com resultados simulados por torneio.

#### Simulacao de partidas
- Impacto forte de superficie (modificadores nos atributos e no estilo).
- BO3/BO5 por torneio, tie-breaks por set e regras de GS.
- Stamina afeta desempenho por set/game, nao so por partida.
- Modelo de jogo com estilos (agressivo, defensivo, serve-and-volley), matchups e variancia controlada.
- Condicoes externas (clima/altitude/bola) como pequenas variacoes.

#### Progressao e carreira
- Curva por idade (pico e declinio), potencial maximo e variacao individual.
- Treinos com custo/tempo/risco e impacto em atributos e fadiga.
- Forma (momentum), confianca, pressao e lesoes recorrentes.
- Agenda realista (tempo de viagem, descanso) e impacto em escolha de torneios.

#### Economia e suporte
- Premiacoes por rodada, custos (viagem, treinador, fisioterapia) e patrocinio.
- Crescimento de equipe (treinador, preparador fisico) com buffs/efeitos.
