# Tennis Legacy - O Que Falta

## Bugs Críticos

- [x] Jogadores duplicados podem aparecer no ranking/qualifying
- [ ] Arquivos JSON podem corromper (sem backup antes de salvar)

---

## Sistema de Ranking

- [ ] Implementar expiração de pontos (sistema "Best 18")
- [ ] NPCs devem ganhar/perder pontos de torneios
- [ ] Histórico de progressão de ranking por jogador
- [ ] Ranking separado por superfície (clay/grass/hard)
- [ ] Volatilidade de ranking

---

## Progressão do Jogador

- [ ] Sistema de treino para melhorar atributos
- [ ] Usar sistema de moral nos cálculos de partida
- [ ] Recuperação gradual de lesões (não binária)
- [ ] Sistema de técnico/equipe de apoio
- [ ] Equipamentos que afetam atributos
- [ ] Penalidades para atributos psicológicos baixos

---

## Simulação de Partidas

- [ ] Efeitos de clima (vento, umidade)
- [ ] Efeito de altitude
- [ ] Momentum mais complexo (swing mid-set)
- [ ] Estratégia de saque adaptativa baseada na pressão
- [ ] Ajustes táticos entre sets
- [ ] Degradação da quadra durante partida
- [ ] Platô de fadiga (não apenas decay linear)
- [ ] Vantagem de estilos (saque-e-voleio vs baseline)

---

## Torneios

- [ ] Calendário completo (muitos torneios faltando)
- [ ] Circuito ITF/Challenger
- [ ] Detalhes específicos de Wimbledon
- [ ] Corrigir transição R96 → R64 no ATP 1000

---

## Circuito WTA

- [ ] Implementar circuito feminino completo
- [ ] Geração de jogadoras femininas
- [ ] Ranking WTA separado
- [ ] Estrutura de pontos WTA

---

## Davis Cup / United Cup

- [x] ~~Corrigir finalização do torneio~~ (verificado - lógica está correta)
- [ ] Formato de equipe completo
- [ ] Integração de duplas (jogador participar das duplas)
- [ ] United Cup não implementado

---

## Interface

- [ ] Feedback claro para inputs inválidos
- [ ] Barra de progresso para simulação de torneios
- [ ] Menu de pausa no modo detalhado
- [ ] Página de estatísticas de carreira detalhadas
- [ ] Arquivo de temporadas e hall da fama
- [ ] Visualização semanal do calendário

---

## Qualidade de Dados

- [ ] Validação de IDs únicos de jogadores
- [ ] NPCs com personalidade (não apenas "Bot N")
- [ ] Ranking inicial com jogadores reais completos

---

## Código / Técnico

- [ ] Dividir `torneio.py` (1.550 linhas)
- [ ] Dividir `simulacao_partida.py` (1.035 linhas)
- [ ] Arquivo de configuração central (remover números mágicos)
- [ ] Testes automatizados
- [ ] Sistema de logging/debug
- [ ] Tratamento de erros consistente
- [ ] Backup antes de sobrescrever saves
- [ ] Otimizar carregamento/salvamento de ranking

---

## Futuras Features

- [ ] Modo multiplayer local
- [ ] Torneios de exibição
- [ ] Sistema de patrocinadores
- [ ] Conferências de imprensa
- [ ] Rivalidades entre jogadores
- [ ] Forma/confiança do jogador (além de momentum)
