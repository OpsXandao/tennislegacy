# Comparativo de Funcionalidades: Terminal vs. Frontend

Este documento lista as funcionalidades presentes na versão original do jogo (Terminal) e o estado atual da migração para a nova interface (Frontend), destacando o que ainda falta implementar.

## 1. Gestão do Jogador e Perfil

| Funcionalidade | Terminal | Frontend | Status |
| :--- | :---: | :---: | :--- |
| **Atributos RPG** (Técnico/Físico/Mental) | ✅ | ✅ | Completo (Aba Atributos no Perfil) |
| **Painel de Carreira** (Idade, Pico, Nível) | ✅ | ✅ | Completo (Aba Carreira no Perfil) |
| **Histórico de Partidas** | ✅ | ✅ | Completo (Aba Histórico no Perfil) |
| **Títulos e Conquistas** | ✅ | ✅ | Completo (Aba Carreira no Perfil) |
| **Nacionalidade e Customização** | ✅ | ✅ | Completo (Criação/Perfil) |
| **Fadiga e Energia** | ✅ | ✅ | Completo (Meters no Hub e Academia) |
| **Sistema de Lesões** | ✅ | ✅ | Completo (Alertas no Hub/Perfil) |

## 2. Finanças e Patrocínios

| Funcionalidade | Terminal | Frontend | Status |
| :--- | :---: | :---: | :--- |
| **Saldo e Ganhos Semanais** | ✅ | ✅ | Completo (Hub/Perfil) |
| **Histórico de Transações** | ✅ | ✅ | Completo (Aba Financeiro no Perfil) |
| **Categorização de Gastos** | ✅ | ✅ | Completo (Aba Financeiro no Perfil) |
| **Receber Propostas de Patrocínio** | ✅ | ✅ | Completo (Via Aba Email) |
| **Buscar Patrocínios Manualmente** | ✅ | ❌ | **Faltando** (Menu de busca ativa) |
| **Requisitos de Patrocínio** (Seguidores/Rank) | ✅ | ⚠️ | Parcial (Lógica no Back, falta UI de requisitos) |

## 3. Staff e Mercado

| Funcionalidade | Terminal | Frontend | Status |
| :--- | :---: | :---: | :--- |
| **Mercado de Profissionais** | ✅ | ✅ | Completo (`MarketScreen`) |
| **Hiring/Firing (Técnico, Fisio, etc)** | ✅ | ✅ | Completo (`MarketScreen`) |
| **Gestão de Contratos Ativos** | ✅ | ✅ | Completo (Aba Equipe no Perfil) |
| **Empresário (Manager)** | ✅ | ✅ | Completo (`MarketScreen`) |
| **Efeitos de Bônus de Staff** | ✅ | ⚠️ | Parcial (Mostra bônus, falta detalhamento) |

## 4. Circuito Mundial (World Tour)

| Funcionalidade | Terminal | Frontend | Status |
| :--- | :---: | :---: | :--- |
| **Rankings ATP/WTA (Simples/Duplas)** | ✅ | ✅ | Completo (`RankingsScreen`) |
| **Race to Finals (YTD)** | ✅ | ✅ | Completo (Aba Race no `WorldScreen`) |
| **Calendário de Torneios** | ✅ | ✅ | Completo (`CalendarScreen`) |
| **Torneios Ao Vivo (Simultâneos)** | ✅ | ✅ | Completo (Aba Ao Vivo no `WorldScreen`) |
| **Chaves de Torneios (Brackets)** | ✅ | ✅ | Completo (`TournamentBracket` / Modais) |
| **Notícias do Circuito** | ✅ | ✅ | Completo (Aba Próximos no `WorldScreen`) |
| **Ranking de Nações** | ✅ | ❌ | **Faltando UI específica** |

## 5. Gameplay e Temporada

| Funcionalidade | Terminal | Frontend | Status |
| :--- | :---: | :---: | :--- |
| **Loop Semanal** | ✅ | ✅ | Completo |
| **Inscrição em Torneios** | ✅ | ✅ | Completo |
| **Treinamento de Atributos** | ✅ | ✅ | Completo (`TrainingScreen`) |
| **Descanso e Recuperação** | ✅ | ✅ | Completo (`TrainingScreen`) |
| **Busca de Parceiro de Duplas** | ✅ | ✅ | Completo (`DuplasScreen`) |
| **Davis Cup / Billie Jean King Cup** | ✅ | ✅ | Completo (`DavisScreen`) |
| **Simulação de Partida (Play-by-Play)** | ✅ | ✅ | Completo (`MatchScreen`) |

## 6. Comunicação e Gestão

| Funcionalidade | Terminal | Frontend | Status |
| :--- | :---: | :---: | :--- |
| **Caixa de Entrada (Emails)** | ✅ | ✅ | Completo (Aba Email no Perfil) |
| **Propostas de Duplas/Staff** | ✅ | ✅ | Completo (Via Email) |
| **Relatórios de Scouting** | ✅ | ❌ | **Faltando** (Análise detalhada do oponente) |

---

## O que ficou faltando (To-Do para o Frontend):

1.  **Menu de Patrocínios Ativo:** No terminal, o jogador podia "Procurar Patrocinadores" ativamente. No Frontend, ele depende de receber e-mails. Seria ideal uma tela para listar patrocínios disponíveis e seus requisitos (Ex: "Nike exige Top 50 e 100k seguidores").
2.  **Scouting / Análise de Adversário:** No terminal, antes de uma partida, havia uma opção de ver um relatório do adversário (pontos fortes/fracos). No Frontend, temos apenas a chave e o perfil básico.
3.  **Ranking de Nações:** Embora a Davis Cup esteja implementada, a visualização da tabela geral de países (Nations Ranking) ainda não tem uma tela dedicada como no terminal.
4.  **Notificações Visíveis:** No terminal, as notícias e e-mails eram mostrados no loop principal. No Frontend, o jogador precisa entrar na aba de Email/Mundo para ver. Um sistema de "badges" ou notificações no Hub ajudaria.
5.  **Detalhes dos Bônus de Equipe:** Explicar melhor na UI o que cada bônus (Ex: "+2 Estratégia") está fazendo na prática durante a partida ou treino.
