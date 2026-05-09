# Tennis Legacy - O Que Falta

## Bugs Críticos

- [x] Jogadores duplicados podem aparecer no ranking/qualifying
- [x] Arquivos JSON podem corromper (implementado salvamento seguro com backups)

---

## Sistema de Ranking

- [x] Implementar expiração de pontos (sistema de rolling 52 semanas / Best 18 implementado)
- [x] NPCs devem ganhar/perder pontos de torneios
- [ ] Histórico de progressão de ranking por jogador
- [ ] Ranking separado por superfície (clay/grass/hard)
- [ ] Volatilidade de ranking

---

## Progressão do Jogador

- [x] Sistema de treino para melhorar atributos
- [x] Usar sistema de moral nos cálculos de partida
- [x] Recuperação gradual de lesões (não binária)
- [x] Sistema de técnico/equipe de apoio
- [x] Penalidades para atributos psicológicos baixos
- [ ] Atributos psicológicos dinâmicos e Traços de Personalidade (unlocked via achievements)
- [ ] Equipamentos que afetam atributos

---

## Simulação de Partidas

- [x] Efeitos de clima (vento, umidade)
- [x] Momentum mais complexo (pressão, estilo de jogo)
- [x] Estratégia de saque adaptativa baseada na pressão
- [x] Degradação de stamina / Platô de fadiga
- [x] Efeito da superfície (hard, clay, grass)
- [x] Insights táticos visíveis para o jogador (transparência de cálculo)
- [ ] Ajustes táticos entre sets
- [ ] Efeito de altitude

---

## Torneios e Calendário

- [x] Calendário ATP/WTA completo (52 semanas)
- [x] Circuito WTA (Feminino) 100% integrado
- [x] Geração de NPCs reais em vez de "Bots Externos"
- [x] Curva de progressão de XP sustentável e balanceada
- [ ] Circuito ITF/Challenger
- [ ] Integração real da United Cup

---

## Davis Cup / Equipes

- [x] Sistema de confrontos entre nações (singles e duplas)
- [x] Formato de equipe completo (convocações)
- [x] Integração API -> Front para confrontos de Davis Cup
- [ ] Lógica aprofundada de grupos da Davis Cup

---

## Gestão e Carreira

- [x] Sistema de patrocinadores
- [x] Conferências de imprensa (entrevistas pós-jogo)
- [x] Vínculo de Duplas (sinergia e parcerias)
- [x] **Hub de Duplas:** Sistema avançado de convites e parcerias (UI + API)
- [x] **Lifestyle & Investimentos:** Sinks de dinheiro para late-game com bônus mecânicos
- [x] Eventos narrativos semanais (aleatórios)
- [ ] Rivalidades dinâmicas entre jogadores
- [ ] Sistema de Traços de Personalidade (Mentalidade)

---

## Código / Técnico

- [x] CI/Qualidade: Ruff, Mypy e Coverage Gate configurados (10/10)
- [x] **Estrutura de Dados:** Pydantic Models para validação de schema (Jogador, Ranking) (8/10)
- [x] Dividir `torneio.py`
- [x] Dividir `simulacao_partida.py`
- [x] Modularização e separação de responsabilidades (`fadiga.py`, `imprensa.py`, `patrocinios.py`)
- [x] Sistema de backup (`.bak`)
- [x] **Arquitetura Sharded:** Fragmentação de saves (jogadores e calendário) para performance
- [x] **Hub de Duplas:** Sistema avançado de convites e parcerias
- [ ] Otimizar busca global de jogadores (índice por nacionalidade em memória)
- [ ] Implementar limpeza de shards de torneios antigos (>2 temporadas) para economizar espaço
- [ ] Adicionar mais testes unitários (cobrir refatorações recentes)
- [ ] Remover números mágicos restantes

