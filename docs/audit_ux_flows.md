# Auditoria UX — TennisLegacy Frontend

**Data:** 2026-03-19
**Auditor:** UX Researcher Agent
**Escopo:** Fluxos de navegacao, friction points, dead ends, cobertura de features e feedback visual
**Versao analisada:** Frontend React 18 + TypeScript + Tailwind + Zustand (branch `feat/frontend`)

---

## 1. Mapa de Rotas e Fluxos Existentes

### 1.1 Inventario de Telas

| Rota | Componente | Categoria |
|---|---|---|
| `/` | `HomeScreen` | Onboarding / Menu inicial |
| `/continue` | `ContinueScreen` | Carregar / Apagar saves |
| `/hub` | `HubScreen` | Hub central da carreira |
| `/calendar` | `CalendarScreen` | Escolha de torneios / Descanso |
| `/tournament` | `TournamentBracket` | Chave e bracket do torneio |
| `/match` | `MatchScreen` | Simulacao ponto a ponto |
| `/week-advance` | `WeekAdvanceScreen` | Transicao de semana |
| `/training` | `TrainingScreen` | Treino e descanso |
| `/player` | `PlayerScreen` | Perfil completo (7 abas) |
| `/player/:tour/:nome` | `PlayerProfileScreen` | Perfil de NPC |
| `/rankings` | `RankingsScreen` | Rankings ATP/WTA/Duplas/Davis |
| `/calendar` | `CalendarScreen` | Calendario de 52 semanas |
| `/world` | `WorldScreen` | Circuito ao vivo / Race / Noticias |
| `/market` | `MarketScreen` | Mercado de staff (5 categorias) |
| `/duplas` | `DuplasScreen` | Parceiros de duplas |
| `/davis` | `DavisScreen` | Copa Davis / BJK Cup |
| `/patrocinios` | `SponsorScreen` | Catalogo de patrocinadores |
| `/ranking-nacoes` | `NationsRankingScreen` | Ranking de nacoes |
| `/progression` | `ProgressionScreen` | XP, habilidades, radar chart |
| `/history` | `HistoryScreen` | Hall da Fama e recordes |
| `/settings` | `SettingsScreen` | Audio, visual, dificuldade |
| `*` | `NotFoundScreen` | 404 |

### 1.2 Fluxos Principais

**Fluxo A — Onboarding (Novo Jogo)**
```
HomeScreen [NOVO JOGO]
  -> Step 0: Escolha ATP / WTA
  -> Step 1: Formulario (nome, idade, pais, estilo tecnico, perfil mental, ID do save)
  -> api.saves.criar() + api.saves.carregar()
  -> HubScreen
```

**Fluxo B — Retomar Carreira**
```
HomeScreen [CARREGAR]
  -> ContinueScreen (lista de saves com preview)
  -> api.saves.carregar()
  -> HubScreen
```

**Fluxo C — Loop Semanal (sem torneio ativo)**
```
HubScreen
  -> [PROXIMO PASSO / CALENDÁRIO]  -> CalendarScreen
     -> Inscricao em torneio       -> TournamentBracket
     -> Descanso                   -> WeekAdvanceScreen -> HubScreen
  -> [TREINAR]                     -> TrainingScreen    -> WeekAdvanceScreen -> HubScreen
```

**Fluxo D — Torneio em Curso**
```
HubScreen (banner ativo amarelo)
  -> TournamentBracket
     -> [ANALISAR] scoutData modal inline
     -> [JOGAR]    MatchScreen
        -> pos-partida -> TournamentBracket (ou WeekAdvanceScreen ao final)
     -> [AVANCAR FASE] (sem partida pendente)
     -> [DESISTIR]  -> WeekAdvanceScreen -> HubScreen
     -> [SIMULAR RESTANTE] -> WeekAdvanceScreen -> HubScreen
```

**Fluxo E — Copa Davis / BJK Cup**
```
HubScreen [DAVIS] ou CalendarScreen (convocacao especial)
  -> DavisScreen
     -> [JOGAR] -> MatchScreen
     -> [SIMULAR] (NPC simula sem input)
```

**Fluxo F — Gestao de Carreira**
```
HubScreen
  -> [MERCADO]   -> MarketScreen (treinador/fisio/psicologo/marketing/empresario)
  -> [DUPLAS]    -> DuplasScreen (sugestoes / busca / ranking duplas)
  -> PlayerScreen (email, financeiro, equipe, atributos, historico, carreira)
     -> email -> proposta de patrocinio / duplas / staff
     -> [PATROCINIOS] -> SponsorScreen (catalogo com requisitos)
```

**Fluxo G — Consulta Mundial**
```
HubScreen [MUNDO] / BottomNav [RANKING]
  -> WorldScreen (ao vivo / race / proximos / noticias)
     -> BracketModal inline de torneios NPC
     -> [RANKING NACOES] -> NationsRankingScreen
  -> RankingsScreen (ATP/WTA/duplas/davis com filtros)
     -> toque em jogador -> PlayerProfileScreen
```

---

## 2. Dead Ends Identificados

### 2.1 Rotas sem retorno claro

**`/history` (HistoryScreen)**
O `PageHeader` aponta `backTo="/player"`, portanto navega para a aba de Carreira do perfil. O problema e que o usuario pode ter chegado pelo HubScreen (botao HISTORICO no grid de acesso rapido em `QUICK`), e sera redirecionado para `/player` ao invez de voltar ao hub. O historico nao tem acesso direto pelo BottomNav e o caminho logico de retorno e ambiguo.

**`/progression` (ProgressionScreen)**
Nao tem `backTo` definido no `PageHeader` nem aparece no `BottomNav`. O acesso e indireto — presumivelmente via `/player` — mas a tela usa apenas `navigate(-1)` implicito. Se o usuario chegar por navegacao deep-link ou reload, o botao voltar pode levar para fora do jogo.

**`/ranking-nacoes` (NationsRankingScreen)**
O `backTo` e `/world`, o que e coerente. Porem a tela nao esta linkada de forma obvia no `WorldScreen` — precisa verificar se ha um botao CTA visivel ali, ja que o acesso parece ser possivel apenas sabendo a rota direta.

**`/settings` (SettingsScreen)**
O `backTo="/hub"` funciona, mas a tela nao tem nenhuma forma de retorno sem salvar. O botao "SALVAR E VOLTAR" chama `navigate('/hub')` apos 250ms. Nao ha botao "CANCELAR" ou "VOLTAR SEM SALVAR" — qualquer alteracao tentativa que o usuario queira descartar exige clicar em "RESETAR CONFIG" manualmente antes de sair.

**`/duplas` (DuplasScreen)**
A tela permite convidar parceiro e buscar no ranking, mas a acao de "convidar" nao leva a nenhuma tela de confirmacao do torneio — a inscricao em duplas acontece na `CalendarScreen`. Nao ha CTA claro para "agora va para o calendario e escolha um torneio de duplas".

### 2.2 Estados sem saida explicita

**`WeekAdvanceScreen` sem `state`**
Se o usuario tentar acessar `/week-advance` diretamente (reload ou deep-link), o componente detecta `!state` e chama `navigate('/hub', { replace: true })`. O comportamento e correto tecnicamente, mas o usuario nao recebe nenhuma mensagem de erro — apenas e redirecionado silenciosamente.

**`MatchScreen` em estado `pos-consequencias`**
A fase final da partida renderiza resultados e XP ganho. Se o usuario fechar a aba e reabrir, o estado e perdido e a partida nao e recuperavel pelo frontend sem recarregar do servidor. Nao ha mensagem explicando isso.

---

## 3. Friction Points

### 3.1 Onboarding — criacao de personagem

**Problema: formulario longo em tela pequena com scroll oculto**
O formulario de novo jogo (step 1) usa `max-h-[85vh] overflow-y-auto`. Em dispositivos com viewport pequena, a secao "NOME DA CARREIRA (ID DO SAVE)" fica abaixo da dobra e pode passar despercebida. O campo tambem usa cor cinza-escura (`text-[#555]`) e label em tom ainda mais apagado (`text-[#9px] text-[#555]`), o que o torna visualmente quase invisivel — intencional ou nao, o ID e modificavel pelo usuario e afeta a pasta do save.

**Problema: feedback de erro so aparece no final do formulario**
O `erro` state e exibido acima dos botoes de acao mas abaixo de todos os campos. Em telas com scroll, o usuario pode nao ver a mensagem de erro se o scroll ja estiver no topo. Nao ha marcacao visual nos campos invalidos (bordas vermelhas, por exemplo).

**Problema: botao "ALEXANDRE PAIVA" exposto no menu principal**
O menu inicial exibe o botao `[ ALEXANDRE PAIVA ]` como opcao de jogo rapido para desenvolvimento. Esse botao e funcionalmente um atalho de debug para criar um save pre-configurado. Ele aparece para todos os usuarios com a mesma proeminencia dos botoes de producao, o que pode confundir jogadores reais.

**Problema: sem preview dos atributos iniciais**
O usuario escolhe Estilo Tecnico e Perfil Mental via `select` com descricao textual, mas nao ha nenhuma visualizacao dos atributos numericos que serao gerados. No backend Python, o usuario via os valores iniciais. Aqui, a escolha e "cega".

### 3.2 Hub — area central

**Problema: multiplos caminhos para a mesma acao de jogo**
Para comecar a jogar, o usuario tem tres opcoes equivalentes no hub:
1. Botao "PROXIMO PASSO — COMECAR A JOGAR" (so aparece sem torneio ativo)
2. Botao "JOGAR" no grid de acesso rapido `QUICK`
3. Aba "TEMPORADA" no `BottomNav`

Todos os tres levam para `/calendar`. Nao e friction exatamente, mas representa ruido de UI — muita repeticao para a mesma acao primaria.

**Problema: badge de emails sem indicacao de urgencia**
O badge de emails nao-lidos aparece sobre o FutCard (`onClick` leva para `/player` na aba Email). O badge tem `animate-bounce`, mas nao distingue entre email urgente (proposta de contrato que expira) e informativo (resultado de torneio NPC). O usuario pode adiar intencionalmente achando que nao e urgente.

**Problema: botao "SALVAR" sem confirmacao de sucesso persistente**
O feedback de save (`SALVO` ou `ERRO`) dura apenas 2500ms e desaparece. Em mobile, onde o usuario pode estar distraido, ele pode perder o feedback e nao saber se o save funcionou.

### 3.3 Calendário — inscricao em torneios

**Problema: torneios de semanas passadas parecem clicaveis**
Os cards de torneios de semanas que nao sao a semana atual sao renderizados com `opacity-60 cursor-default`, mas o seletor de semana permite navegar livremente para qualquer semana. Nao ha mensagem explicando que o usuario esta em modo de visualizacao — ele pode tentar clicar e nao receber nenhum feedback sobre por que nao funciona.

**Problema: "DESCANSAR" e "PULAR SEMANA" no mesmo botao**
O botao no `ActionDock` da `CalendarScreen` exibe texto condicional: "DESCANSAR (PULAR SEMANA)" se ha torneios, ou "PULAR SEMANA" se nao ha. A acao e identica em ambos os casos, mas o texto sugere semanticas diferentes — "descansar" implica uma acao positiva para o personagem, enquanto "pular semana" parece uma decisao neutra. Usuarios podem hesitar ao descansar achando que estao "perdendo" algo.

**Problema: modal de inscricao nao informa requisitos de qualifying**
Ao clicar em um torneio, o `TournamentEntryModal` e exibido. Ele permite escolher modalidade (simples, duplas, mistas) mas nao informa se o jogador entra diretamente na chave principal ou no qualifying com base no ranking atual. No backend isso e calculado, mas o frontend nao comunica antecipadamente.

### 3.4 Bracket e partida

**Problema: bracket e horizontalmente scrollavel mas sem indicacao visual**
O `BracketCanvas` usa `overflow-x-auto` em um container de largura calculada dinamicamente. Em mobile, nao ha nenhuma indicacao de que o conteudo pode ser scrollado horizontalmente (sem seta, sem gradiente de fade, sem scrollbar visivel por padrao). Em Grand Slams com 10 fases, o bracket e muito maior que a tela.

**Problema: botao "ANALISAR" (scout) e "JOGAR" compartilham espaco visual**
Quando ha partida disponivel, dois botoes sao exibidos: "ANALISAR" e "JOGAR". O botao JOGAR tem `blink` ativo (piscando), o que e correto para chamar atencao. Porem ao clicar em "ANALISAR", o resultado e exibido num painel inline no mesmo `ActionDock`, e o botao "JOGAR AGORA" aparece dentro desse painel. Isso cria dois CTAs concorrentes para "JOGAR" na mesma area, com hierarquia visual confusa.

**Problema: sem confirmacao ao "DESISTIR" do torneio**
`handleDesistir()` nao tem confirmacao via `window.confirm`. O jogador pode clicar acidentalmente e perder o torneio. Comparativamente, "APAGAR SAVE" usa `window.confirm`, mas desistir de um torneio (acao igualmente destrutiva para a carreira) nao tem confirmacao.

**Problema: feedback de avanco de fase nao informa o que aconteceu**
Ao clicar "AVANCAR FASE" (ou "IR PARA QF", etc.), a fase avanca silenciosamente e o bracket se atualiza. Nao ha animacao, toast ou mensagem informando quais NPCs foram eliminados ou quem avancou. O usuario precisa ler o bracket inteiro para entender o que mudou.

### 3.5 Partida (MatchScreen)

**Problema: setup inicial com muitas escolhas sem contexto de impacto**
A fase `setup` da partida apresenta: Modo de acompanhamento (MANUAL/RAPIDA/ATE O FIM), Plano tatico (PRESSIONAR/CONSISTENCIA/VARIAR), Mentalidade, Abordagem, Instrucao e Segundo Saque. Sao 6 dimensoes de escolha antes de comecar a partida. Para novos usuarios, nao e claro como cada escolha impacta a simulacao — as descricoes textuais existem mas sao concisas e tecnicas.

**Problema: modo MANUAL (estrategista) tem muitos micro-controles por ponto**
No modo manual, cada ponto exige escolher: Intencao (PRESSIONAR/CONSTRUIR/DEFENDER), Faixa (FUNDO/MEIO/REDE) e Alvo (ESQ/CTR/DIR). Isso sao 9 combinacoes por ponto, repetidas dezenas de vezes numa partida. Nao ha atalhos de teclado nem possibilidade de "usar mesma escolha anterior".

**Problema: velocidade do modo RAPIDA nao e persistida entre partidas**
A velocidade selecionada (1X/2X/4X/8X) salva em `localStorage` via chave `tennislegacy.match.tactical-package`, mas a preferencia de modo de acompanhamento nao parece persistida de forma separada. O usuario precisa reconfigurar toda vez.

### 3.6 PlayerScreen — perfil do jogador

**Problema: 7 abas sem indicacao de qual contem novidades**
O `PlayerScreen` tem as abas: ATRIBUTOS, RANKING, HISTORICO, FINANCEIRO, CARREIRA, EQUIPE, EMAIL. A aba EMAIL tem um badge no hub (contagem de nao lidos), mas dentro da tela de perfil nao ha indicacao visual de qual aba tem conteudo novo (emails, novas transacoes, novos titulos). O usuario precisa navegar por todas para verificar.

**Problema: aba EMAIL — acoes de aceitar/rejeitar proposta sem preview completo**
Os emails exibem propostas (patrocinios, duplas, staff) com um botao de aceitar/rejeitar. Nao e claro o que acontece apos aceitar — nao ha confirmacao de contrato, preview de custo semanal ou comparacao com o contrato atual antes da acao ser executada.

### 3.7 Progressao e treino

**Problema: `TrainingScreen` avanca a semana imediatamente apos o treino**
Ao escolher um foco de treino, `handleTreinar()` executa e navega para `/week-advance`. Nao ha etapa intermediaria para o usuario ver os resultados do treino antes de a semana avancar. O feedback de melhoria de atributos e visivel apenas brevemente na `WeekAdvanceScreen` (como "EVENTOS DA VIRADA"), e a transicao auto-navega para o hub em 3.6 segundos.

**Problema: pontos de skill em `ProgressionScreen` sem tutorial**
A tela de progressao exibe `pontosSkill` e botoes para alocar pontos em atributos, mas nao ha explicacao de como os pontos sao ganhos, quando sao ganhos ou qual e o impacto numerico de alocar um ponto. O radar chart e visual mas nao quantificado o suficiente para decisoes estrategicas.

---

## 4. Features do Backend Sem Representacao Completa no Frontend

| Feature | Status no Frontend | Observacoes |
|---|---|---|
| Busca ativa de patrocinios | Parcialmente implementada | `SponsorScreen` existe e esta em `/patrocinios`, porem o `backTo="/player"` sugere acesso via perfil; nao ha link direto no hub ou no BottomNav |
| Ranking de Nacoes | Implementada (`NationsRankingScreen`) | Rota `/ranking-nacoes` existe, porem acesso e indireto — nao linkado visivelmente no WorldScreen ou no menu principal |
| Scouting de adversario | Implementada inline no TournamentBracket | Exibe ranking, overall, superficie favorita, H2H e forma recente; atributos truncados em 8 campos; funcional mas compacto |
| Requisitos de patrocinio (UI) | Parcialmente visivel | `SponsorScreen` exibe `requisito_ranking` e `requisito_seguidores` e `motivo_bloqueio`, o que e adequado |
| Busca manual de patrocinios | Implementada via `SponsorScreen` | Resolvido em relacao ao `COMPARATIVO_FUNCIONALIDADES.md` — o catalogo mostra elegiveis e bloqueados |
| Notificacoes em tempo real | Ausente | Sem sistema de badges ou notificacoes no hub alem do contador de emails |
| Detalhamento de bonus de staff | Parcial | `MarketScreen` exibe os profissionais mas nao explica o impacto dos bonus durante a partida |
| Imprensa / Entrevistas | Ausente | O backend tem `imprensa.py` com sistema completo de perguntas e opcoes de resposta. Nao ha representacao no frontend |
| Relatorios de scouting detalhados | Parcial | O scout inline do `TournamentBracket` e basico. Nao ha pagina dedicada de analise de adversario |
| Historico de confrontos H2H | Presente no scout | Apenas vitorias/derrotas; nao ha lista de partidas individuais H2H |
| Atributos psicologicos NPCs | Ausente no scout | Exibidos apenas para o jogador no `PlayerScreen`, nunca para NPCs |

---

## 5. Avaliacao do Onboarding

### O que funciona bem
- O fluxo de 2 etapas (escolha de tour -> formulario) e limpo e progressivo
- A mudanca de texto ("NOVO JOGADOR" / "NOVA JOGADORA") ao selecionar ATP/WTA e um detalhe positivo de personalizacao
- A lista de nacionalidades e ordenada alfabeticamente com busca por scroll e bandeira
- O campo de ID do save e auto-preenchido a partir do nome do jogador, reduzindo atrito

### Problemas identificados

**Falta de contexto sobre os archetypes**
Os archetypes tecnicos e mentais sao apresentados apenas com nome e descricao textual em italico pequeno (9px). Nao ha visualizacao comparativa, radar chart preview ou exemplo de atributos iniciais. O usuario esta essencialmente escolhendo um estilo de jogo "as cegas".

**Ausencia de tela de confirmacao ("Resumo do Perfil")**
Apos preencher o formulario, o botao "INICIAR JOGO" chama a API diretamente. Nao ha uma tela de revisao com "Voce criou: Carlos Silva, 18 anos, Brasil, Baseliner, Competitivo". Erros de digitacao no nome so sao descobertos ja dentro do hub.

**Campo "NOME DA CARREIRA" pouco visivel**
O campo de ID do save usa `text-[#555]` (cinza apagado) e esta posicionado no final do formulario com borda discreta. Como ele afeta a pasta do save, deveria ter uma indicacao de que e editavel e qual e seu proposito.

**Sem confirmacao de que o save ja existe**
Se o usuario tentar criar um save com o mesmo ID de um ja existente, o comportamento depende da API. Nao ha validacao client-side nem mensagem preventiva.

**Estado de loading durante criacao**
O botao muda para "PROCESSANDO..." com `blink`, o que e bom. Porem nao ha indicacao de progresso — o jogo pode demorar varios segundos para gerar 2000+ NPCs no backend, e o usuario nao tem estimativa de tempo.

---

## 6. Feedback Visual para Acoes Importantes

### Salvar jogo
- Botao com icone `Save` no header do hub
- Feedback: texto "SALVO" (verde) ou "ERRO" (rosa) por 2500ms com `AnimatePresence`
- Problema: feedback nao e persistente o suficiente; nao ha indicacao de horario do ultimo save

### Avancar semana
- `WeekAdvanceScreen` dedicada com animacao de semana atual -> proxima
- Campeoes do circuito exibidos
- Auto-navega para hub em 3.6 segundos (ou manualmente apos 2.2s)
- Problemas: o timer de 3.6s pode ser curto para ler varios campeoes; o botao "IR PARA O HUB" fica disabled ate 2.2s sem razao tecnica aparente alem de forcara animacao

### Completar torneio
- Revelacao do campeao via `campeaoFinal` state com borda dourada animada
- CTA "AVANÇAR SEMANA" visivel apos revelacao
- Adequado

### Contratar / Demitir staff
- `MarketScreen` exibe mensagem de sucesso/erro via state `mensagem` com animacao
- Problema: a mensagem desaparece apenas quando o usuario interage novamente (nao ha timer). Isso e melhor que o hub (onde desaparece em 2.5s), mas inconsistente com o padrao da app.

### Aceitar email / Proposta
- Sem feedback visual alem da remocao do email da lista
- Nao ha confirmacao do que foi aceito (ex: "Voce assinou contrato com Nike por $5k/semana")

### Erros de rede / API
- `ContinueScreen` exibe erro em texto vermelho fixo na tela
- `HubScreen` silencia erros no `fetchJogador` (`.catch(() => {})`)
- Inconsistencia: alguns erros sao exibidos, outros sao silenciados silenciosamente

---

## 7. Problemas de Consistencia de Navegacao

### BottomNav ausente em telas criticas
O `BottomNav` e renderizado no `HubScreen`, `TrainingScreen`, `RankingsScreen` e `PlayerScreen`. Nao esta presente em:
- `TournamentBracket` (usuario fica "preso" com apenas o header de voltar)
- `MatchScreen` (justificavel — foco na partida)
- `CalendarScreen` (sem BottomNav, apesar de ser uma tela primaria)
- `WorldScreen`, `MarketScreen`, `DuplasScreen`, `DavisScreen`

A inconsistencia cria um padrao de navegacao fragmentado. Em metade das telas ha BottomNav; na outra metade o usuario depende do botao voltar no `PageHeader`.

### Botoes "Voltar" com destinos inconsistentes
- `HistoryScreen`: `backTo="/player"` (esperado: `/hub` se veio pelo hub)
- `SponsorScreen`: `backTo="/player"` (mas pode ser acessado pelo hub ou pelo email)
- `NationsRankingScreen`: `backTo="/world"` (correto)
- `ProgressionScreen`: sem `backTo` definido (usa `navigate(-1)`)

### Duplicidade de acesso a rankings
- `BottomNav` tem "RANKING" -> `/rankings`
- `HubScreen` QUICK grid nao tem ranking diretamente
- `WorldScreen` tem abas de circuito mas nao linka para `/rankings`
- `NationsRankingScreen` e acessivel por `/world` e por `/rankings` (aba Davis), criando dois caminhos

---

## 8. Problemas de Acessibilidade e Mobile

### Touch targets pequenos
- Os numeros do seletor de semana em `CalendarScreen` usam `w-14 h-14` (56px), adequado
- Os botoes da chave do torneio (`BracketMatchCard`) nao sao interativos (sem onclick), adequado
- Os botoes de acao no `ActionDock` usam `NeonButton` que tem `min-h` implicito — verificar se >= 44px

### Texto muito pequeno em varios contextos
- Subtitulos de header: 8px (`text-[8px]`)
- Labels de atributos no scout: 7px (`text-[7px]`)
- Badges de tour: 9-10px
- Esses tamanhos estao abaixo de 12px, que e o minimo recomendado para leitura confortavel em mobile

### Contraste em modo claro
O design e neon/dark com hardcoded colors (`#00ff88`, `#ff0055`, `#ffe600`). O `SettingsScreen` permite modo claro, mas os componentes usam CSS variables para o fundo (`app-shell`, `app-panel`) e cores fixas para o neon. Em modo claro, o contraste entre texto neon verde (`#00ff88`) e fundo claro pode ser insuficiente.

### Falta de `aria-label` em muitos controles interativos
- Botoes de acao do `ActionDock` (JOGAR, AVANCAR FASE) nao tem `aria-label`
- Cards de torneio no `CalendarScreen` usam `motion.div onClick` sem role ou aria
- Selecao de semana usa `<button>` com numero como unico conteudo — adequado

---

## 9. Bugs UX / Comportamentos Inesperados

### CalendarScreen — condicao sempre verdadeira
Linha 90: `if (r.semana === r.semana) checarConvocacao()` — essa condicao e sempre verdadeira (variavel comparada consigo mesma). A intencao era provavelmente `if (r.semana === semanaAtual)`. Isso significa que `checarConvocacao()` e chamada toda vez que o calendario carrega, independente da semana selecionada.

### HomeScreen — fallback de `nac` incorreto
Linha 58-60: se `nac` atual nao esta na lista de nacionalidades carregadas da API, o codigo define `nac` como `nacionalidadesOrdenadas[0]`. Porem o estado inicial de `nac` e `'[BR] Brasil'` — se a API retornar uma lista que nao inclui esse formato exato, a bandeira do Brasil continuara selecionada visualmente mas o valor enviado para a API sera o primeiro da lista ordenada.

### MarketScreen — `contratoAtual` calculo incorreto
A variavel `contratoAtual` para categorias que nao sao `empresario` usa `jogador?.equipe?.find((c: any) => lista.some((prof) => prof.id === c.id))`. Isso busca na equipe do jogador um membro cujo `id` apareca na lista de profissionais da categoria atual. Se a equipe tiver membros de outras categorias com IDs que coincidam, pode haver falso positivo. A logica deveria filtrar tambem pela categoria.

### SettingsScreen — "SALVAR E VOLTAR" salva antes de navegar
O `localStorage` ja e atualizado via `useEffect` a cada mudanca de setting. O botao "SALVAR E VOLTAR" apenas escreve no localStorage novamente e navega. A funcao `handleSaveAndBack` e redundante — o save ja aconteceu. Isso pode confundir o usuario que acha que precisa clicar no botao para persistir as mudancas.

---

## 10. Oportunidades de Melhoria — Prioridade Alta

### P1 — Confirmacao antes de desistir de torneio
Adicionar `window.confirm` ou um modal nativo antes de executar `handleDesistir()`. Essa e uma acao destrutiva e irreversivel sem confirmacao.

**Impacto estimado:** Prevencao de perda acidental de progresso em 100% dos casos.

### P2 — Indicador de scroll horizontal no bracket
Adicionar um fade gradiente nas bordas do `BracketCanvas` e/ou um indicador textual ("< ARRASTE PARA VER MAIS FASES >") quando o bracket nao cabe na tela.

**Impacto estimado:** Usuarios que nao descobrem o scroll horizontal perdem a visibilidade de todo o torneio.

### P3 — Preview de atributos iniciais no onboarding
Exibir os atributos numericos aproximados que cada combinacao de archetype tecnico + mental geraria, antes de confirmar a criacao. Um radar chart simples ja existe em `ProgressionScreen` e poderia ser reutilizado.

**Impacto estimado:** Reduz o numero de jogadores que criam um segundo save por insatisfacao com os atributos iniciais.

### P4 — Remover ou ocultar botao "ALEXANDRE PAIVA" do menu principal
Mover o atalho de desenvolvimento para uma sequencia de teclas oculta (konami code, duplo-toque em logo) ou remover da build de producao.

**Impacto estimado:** Elimina confusao no onboarding de novos usuarios.

### P5 — Feedback persistente de save com timestamp
Substituir o texto "SALVO" de 2500ms por um indicador mais duravel mostrando "SALVO 14:32" ou similar, que permaneca visivelmente no header ate o proximo save ou reload.

**Impacto estimado:** Reducao da ansiedade do usuario sobre perda de progresso.

### P6 — Notificacoes contextuais no hub
Adicionar badges no grid de acesso rapido do hub para indicar estados importantes sem exigir que o usuario navegue para cada tela:
- Badge "NOVO EMAIL" em JOGADOR (ja parcialmente implementado no FutCard)
- Badge "ATIVO" em DAVIS quando ha confronto ativo
- Badge "DISPONIVEL" em PATROCINIOS quando ha patrocinadores elegiveis

### P7 — Consistencia do BottomNav
Adicionar o `BottomNav` ao `CalendarScreen` e `WorldScreen`, que sao telas primarias frequentemente visitadas. Para telas de fluxo especifico (MatchScreen, WeekAdvanceScreen), manter sem BottomNav.

---

## 11. Oportunidades de Melhoria — Prioridade Media

### P8 — Tela de revisao pre-partida mais explicita
Antes de "JOGAR", exibir um resumo de "Voce vs. Adversario" com overal do adversario, superficie, superficie favorita de cada jogador e H2H — de forma mais proeminente do que o scout inline atual.

### P9 — Campo de busca no seletor de semana
O seletor de semana e uma fila horizontal de 52 itens. Adicionar um campo de input numerico "IR PARA SEMANA [___]" reduziria o atrito para usuarios que querem navegar para uma semana especifica sem arrastar.

### P10 — Historico de MatchScreen persistido por partida
Apos o modo AUTO ou RAPIDA, exibir um resumo de estatisticas da partida (aces, duplas faltas, winners, erros) em um painel de pos-partida antes de voltar ao bracket.

### P11 — Feedback de email aceito mais detalhado
Ao aceitar uma proposta de patrocinio ou staff via email, exibir um modal de confirmacao com os termos do contrato (valor semanal, duracao, beneficios).

### P12 — Corrigir condicao de convocacao no CalendarScreen
Corrigir a linha `if (r.semana === r.semana)` para a comparacao correta.

---

## 12. Resumo Executivo

O frontend do TennisLegacy tem uma base solida de telas implementadas e uma estetica neon/arcade visualmente consistente. Os fluxos principais (onboarding, loop semanal, torneio, partida) estao funcionais e conectados. As maiores oportunidades de melhoria estao concentradas em tres areas:

**1. Feedback de acoes destrutivas e importantes**
Desistir de torneio sem confirmacao, aceitar propostas sem revisao, e saves sem indicador persistente representam riscos reais de frustracao do usuario.

**2. Descobribilidade e navegacao**
O `BottomNav` inconsistente, o bracket sem indicador de scroll e as rotas de `SponsorScreen` e `NationsRankingScreen` sem links claros no hub dificultam que usuarios descubram features existentes.

**3. Onboarding sem visibilidade das escolhas**
A criacao de personagem e o ponto de maior atrito — o usuario toma decisoes estrategicas (archetype, mental) sem ver o impacto nos atributos numericos, e nao ha tela de revisao antes de confirmar.

Features do backend que ainda nao tem representacao no frontend incluem o sistema de imprensa/entrevistas e relatorios de scouting detalhados. O resto das funcionalidades principais esta mapeado no frontend, algumas parcialmente.

---

*Auditoria realizada com base em leitura estatica do codigo-fonte. Testes de usabilidade com usuarios reais e analise de metricas de uso sao recomendados como proximos passos.*
