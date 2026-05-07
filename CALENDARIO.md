# Calendário de Implementação (Status Atual)

Última atualização: 2026-03-01.

Este arquivo agora representa o **roteiro vivo** do projeto (não mais proposta fixa de 6 semanas).

## Concluído

- Split inicial de monólitos com compatibilidade por re-export:
  - `management -> imprensa + patrocinios`
  - `progressao -> fadiga`
  - `jogar_partida -> match_config`
- Estrutura ATP/WTA com ranking e calendário separados.
- Fluxo de duplas com vínculo de parceiro salvo no jogador.
- Exibição de especialistas de duplas no ranking.

## Em progresso

- Padronização total dos calendários em `db/` (ATP e WTA) para aderência ao circuito real.
- Ajustes finos de UI vs ação real (menus, estados de fase e mensagens).
- Revisão de torneios por equipes para aderência 1:1 ao formato oficial.

## Próximos passos

1. Consolidar integridade de `db/calendario.json` e `db/calendario_wta.json`.
2. Expandir cobertura de testes para:
   - avanço de fase,
   - distribuição de pontos,
   - fluxo de duplas e vínculo.
3. Revisar sincronização mundial (`world_tour_sync`) com torneios jogáveis.
