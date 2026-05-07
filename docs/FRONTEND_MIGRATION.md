# TennisLegacy — Frontend Migration

**Este arquivo é o ponto central de coordenação da migração CLI → Frontend.**
Todas as IAs leem e atualizam este arquivo. Cada IA tem sua seção e atualiza
o status conforme entrega. Nunca apague seções de outras IAs.

---

## Contexto do Projeto

TennisLegacy é um jogo de simulação de carreira de tênis em modo texto (Python CLI)
sendo migrado para uma aplicação web com suporte a Android (Play Store).

**Repositório:** `/home/alexandre-paiva/Documentos/estudos/tennislegacy`
**Branch de trabalho:** `feat/frontend` (criar a partir de `feat/temporada`)

### Stack decidida

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI + Python 3.10+ (preserva toda lógica src/) |
| Frontend | React 18 + TypeScript + Tailwind CSS + Vite |
| Mobile | Capacitor 5 (Android APK) |
| Tempo real | WebSocket nativo (FastAPI) |
| HTTP client | axios |
| Roteamento | React Router v6 |
| Estado global | Zustand |

### Estilo visual

Arcade/fliperama retro com neon. Detalhes em `docs/DESIGN_SYSTEM.md` (Gemini cria).

- Background: `#0a0a0a` com scanlines
- Neon primary: `#00ff88` (verde)
- Neon danger: `#ff0055` (pink)
- Neon gold: `#ffe600`
- Neon info: `#00e5ff`
- Cards: `#1a1a2e` com borda neon 1px
- Fontes: `Press Start 2P` (títulos), `Share Tech Mono` (stats/corpo)

### Arquitetura

```
tennislegacy/
├── src/            # dominio Python — NAO ALTERAR
├── db/             # dados base — NAO ALTERAR
├── saves/          # saves locais — NAO ALTERAR
├── api/            # NOVO: FastAPI (Gemini + Codex)
│   ├── main.py
│   ├── session.py
│   └── routes/
│       ├── save.py
│       ├── ranking.py
│       ├── jogador.py
│       ├── calendario.py
│       ├── torneio.py
│       ├── partida.py
│       └── davis.py
│   └── ws/
│       └── partida.py
└── frontend/       # NOVO: React app (Claude)
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── hooks/
    │   ├── store/
    │   └── api/
    ├── capacitor.config.ts
    └── package.json
```

### Regras de coordenação

1. Cada IA atualiza **apenas sua seção** neste arquivo
2. Status de cada tarefa: `[ ]` pendente | `[x]` feito | `[~]` em progresso | `[!]` bloqueado
3. Ao encontrar dependência de outra IA, registrar em **Bloqueios e Dependências**
4. Contratos de API (endpoints + payloads) definidos em **Contratos de API** — todas as IAs respeitam
5. Nunca quebrar imports existentes em `src/` — apenas adicionar camada `api/` por cima

---

## Prompts de Inicialização (Copie e cole para cada IA)

### 🤖 Gemini (Infraestrutura)
> "Você é o **Gemini — Infraestrutura e Data Layer**. Seu objetivo é criar a base da API para a migração do jogo TennisLegacy (Python) para Web/Mobile.
>
> **Suas tarefas no repositório:**
> 1. Manter o `api/main.py` (FastAPI) e `api/session.py` (gerenciamento de sessão/save ativo).
> 2. Criar rotas em `api/routes/save.py`, `ranking.py` e `jogador.py`.
> 3. Criar o `docs/DESIGN_SYSTEM.md` com tokens de cores neon (retro arcade), fontes pixeladas e classes Tailwind de exemplo.
>
> **Regra de Ouro:** Leia o arquivo `docs/FRONTEND_MIGRATION.md` para entender os contratos de API. Sempre que terminar uma tarefa, marque com [x] na sua seção nesse arquivo. Não altere a lógica em `src/`, apenas crie a camada de API por cima."

### 🧠 Codex (Game Logic)
> "Você é o **Codex — Game Logic API**. Seu objetivo é expor a lógica interna do TennisLegacy via API para o frontend.
>
> **Suas tarefas no repositório:**
> 1. Criar `api/routes/calendario.py` (avançar semana), `torneio.py` (chaves e inscrições) e `partida.py`.
> 2. Implementar `api/ws/partida.py` usando WebSockets para transmitir o placar ponto a ponto em tempo real.
> 3. Adaptar funções em `src/` que usam `input()` ou `print()` para que retornem dicionários/JSON compatíveis com a API.
>
> **Regra de Ouro:** Leia o arquivo `docs/FRONTEND_MIGRATION.md`. Você depende do `api/session.py` do Gemini para saber qual save está ativo. Atualize seu progresso no MD e registre dependências na tabela de bloqueios."

### 🎨 Claude (Frontend & Mobile)
> "Você é o **Claude — Frontend & Mobile**. Seu objetivo é criar uma interface React deslumbrante com estética 'Arcade Retro Neon' e preparar o app para Android via Capacitor.
>
> **Suas tarefas no repositório:**
> 1. Inicializar o projeto React (Vite + TS + Tailwind) na pasta `frontend/`.
> 2. Configurar o **Capacitor** (`npx cap init`) para suporte a Android/APK.
> 3. Criar componentes neon (botões, cards, barras de energia) baseados no `docs/DESIGN_SYSTEM.md` do Gemini.
> 4. Criar as telas: Menu Inicial, Dashboard (Hub), Rankings e a tela de Partida (conectando via WebSocket).
>
> **Regra de Ouro:** Use **Zustand** para estado global e **Axios** para a API (localhost:8000). Leia o `docs/FRONTEND_MIGRATION.md` para saber os formatos de dados esperados. Atualize seu progresso no MD."

---

## Status Geral

| IA | Fase atual | Ultima atualizacao |
|---|---|---|
| Gemini | Infraestrutura OK | 2026-03-06 |
| Codex | - | - |
| Claude | COMPLETO — telas com dados reais integradas; Settings permanece local por design | 2026-03-08 |

---

## Contratos de API

> Definidos aqui por qualquer IA. Todas as outras respeitam sem alterar.
> Formato: `METODO /caminho` — request body — response body

### Save / Sessao

```
GET  /api/saves
  response: { saves: string[] }

POST /api/save/criar
  body:    { nome: string, nome_jogador: string, nacionalidade: string, tour: "atp"|"wta", archetype_id?: string, mental_id?: string }
  response: { ok: boolean, save: string }

GET  /api/save/arquetipos
  response: { tecnicos: Record<string, any>, mentais: Record<string, any> }

POST /api/save/carregar
  body:    { nome: string }
  response: { ok: boolean, jogador: JogadorState, semana: number, ano: number }

GET  /api/sessao
  response: { save_ativo: string | null }
```

### Jogador

```
GET  /api/jogador
  response: JogadorState (ver tipo abaixo)

GET  /api/jogador/atributos
  response: { atributos: Record<string, number>, overall: number }

GET  /api/jogador/equipe
  response: { treinador, fisio, psicologo, empresario }

GET  /api/jogador/patrocinios
  response: { patrocinios: Patrocinio[] }
```

### Ranking

```
GET  /api/ranking/atp?limit=100&offset=0
  response: { ranking: RankingEntry[], total: number }

GET  /api/ranking/wta?limit=100&offset=0
  response: { ranking: RankingEntry[], total: number }

GET  /api/ranking/duplas/:tour?limit=50
  response: { ranking: RankingEntry[], total: number }
```

### Calendario

```
GET  /api/calendario/semana/:n
  response: { semana: number, torneios: Torneio[] }

GET  /api/calendario/atual
  response: { semana: number, ano: number, torneios: Torneio[] }

POST /api/calendario/avancar
  response: { semana: number, eventos: string[], resumo_mundial: ResumoDaSemana }
```

### Torneio

```
POST /api/torneio/criar
  body:    { modalidade: "simples"|"duplas"|"mistas", parceiro?: string }
  response: { ok: boolean, torneio: TorneioState }

GET  /api/torneio/estado
  response: TorneioState | null

POST /api/torneio/avancar-fase
  response: { fase: string, resultados: Resultado[], proximo: PartidaInfo | null }

POST /api/torneio/desistir
  response: { ok: boolean }
```

### Partida

```
POST /api/partida/iniciar
  body:    { modo: "detalhado"|"rapido"|"estrategista" }
  response: { partida_id: string, config: ConfigPartida }

POST /api/partida/ponto
  body:    { partida_id: string }
  response: PlacarState

POST /api/partida/estrategia
  body:    { partida_id: string, estrategia: string }
  response: { ok: boolean }

WS   /ws/partida/:partida_id
  server -> client: PlacarEvent (a cada ponto)
  client -> server: { acao: "pausar"|"continuar"|"estrategia", valor?: string }
```

### Tipos TypeScript compartilhados

```typescript
interface JogadorState {
  nome: string
  nacionalidade: string
  tour: "atp" | "wta"
  ranking: number
  pontos: number
  overall: number
  energia: number
  fadiga: number
  status_lesao: string | null
  dinheiro: number
  seguidores: number
  nivel: number
  xp: number
  atributos: Record<string, number>
}

interface RankingEntry {
  posicao: number
  nome: string
  nacionalidade: string
  pontos: number
  pontos_duplas?: number
}

interface TorneioState {
  nome: string
  tipo: string
  superficie: string
  fase_atual: string
  bracket: BracketNode[]
  jogador_ativo: boolean
}

interface PlacarState {
  sets: [number, number]
  games: [number, number]
  pontos: [string, string]
  servindo: "jogador" | "adversario"
  log: string[]
  encerrado: boolean
  vencedor?: "jogador" | "adversario"
}

interface PlacarEvent extends PlacarState {
  tipo: "ponto" | "game" | "set" | "fim"
  descricao: string
}
```

---

## Secao Gemini — Infraestrutura e Data Layer

### Responsabilidade

- Criar e manter `api/main.py` (app FastAPI, CORS, startup)
- `api/session.py` (save ativo da sessao)
- `api/routes/save.py`
- `api/routes/ranking.py`
- `api/routes/jogador.py`
- `requirements-api.txt`
- `docs/DESIGN_SYSTEM.md` (tokens de cor, fontes, componentes — para o Claude usar)

### Tarefas

- [x] Criar branch `feat/frontend` a partir de `feat/temporada`
- [x] `requirements-api.txt` com fastapi, uvicorn[standard], websockets, python-multipart
- [x] `api/__init__.py` vazio
- [x] `api/main.py` — FastAPI app, CORS, incluir todos os routers, lifespan
- [x] `api/session.py` — `get_save_ativo()`, `set_save_ativo()`, `clear_sessao()`
- [x] `api/routes/save.py` — GET /api/saves, POST /api/save/criar, POST /api/save/carregar, GET /api/sessao
- [x] `api/routes/ranking.py` — GET /api/ranking/atp, GET /api/ranking/wta, GET /api/ranking/duplas/:tour
- [x] `api/routes/jogador.py` — GET /api/jogador, /atributos, /equipe, /patrocinios
- [x] `docs/DESIGN_SYSTEM.md` — tokens CSS, classes Tailwind, exemplos de componentes

### Notas tecnicas

- Importar dominio com: `import sys; sys.path.insert(0, str(Path(__file__).parent.parent))`
- `SistemaRanking` requer path do save ativo — session.py resolve isso
- Ao carregar save: instanciar `Jogador` via `save.carregar_jogador(nome_save)`
- Manter instancias em memoria durante a sessao (nao recarregar a cada request)

### Atualizacoes de progresso

- **2026-03-06:** Setup inicial da API FastAPI com suporte a CORS.
- **2026-03-06:** Session manager implementado em `api/session.py`.
- **2026-03-06:** Rotas de Save (list, create, load) finalizadas.
- **2026-03-06:** Rotas de Ranking (atp, wta, duplas) com paginação prontas.
- **2026-03-06:** Rotas de Jogador (perfil, atributos, equipe, patrocínios) finalizadas.
- **2026-03-06:** Design System detalhado em `docs/DESIGN_SYSTEM.md`.
- **2026-03-06:** BUG #8: `refresh_session()` implementado em `api/session.py`.
- **2026-03-06:** BUG #9: Endpoint `/api/jogador/equipe` refatorado para normalização de dados (treinador, fisio, psicologo, empresario).
- **2026-03-06:** BUG #1 & #2: Mapeamento de 'superficie' e formatação de 'premiacao' no calendário.
- **2026-03-06:** BUG #3: Refatoração robusta do endpoint `/equipe` usando `PROFISSIONAIS_DISPONIVEIS`.
- **2026-03-06:** BUG #9: Inclusão de `xp_para_proximo_nivel` em jogador e carregamento de save.
- **2026-03-06:** BUG #11: Endpoint `/api/save/{nome}/preview` para visualização rápida de saves.
- **2026-03-06:** Migração do Sistema de Treinamento (API + TrainingScreen).
- **2026-03-06:** Migração do Mercado de Staff (API + MarketScreen).
- **2026-03-06:** Migração do Sistema de E-mails/Propostas (API + PlayerScreen integration).
- **2026-03-06:** Migração do Histórico/Hall da Fama (API + HistoryScreen).

---

## Secao Codex — Game Logic API

### Responsabilidade

- `api/routes/calendario.py`
- `api/routes/torneio.py`
- `api/routes/partida.py`
- `api/routes/davis.py`
- `api/ws/partida.py` (WebSocket handler)

### Tarefas

- [x] `api/routes/calendario.py` — GET /api/calendario/semana/:n, GET /api/calendario/atual, POST /api/calendario/avancar
- [x] `api/routes/torneio.py` — POST criar, GET estado, POST avancar-fase, POST desistir
- [x] `api/routes/partida.py` — POST iniciar, POST ponto, POST estrategia
- [x] `api/ws/partida.py` — WebSocket /ws/partida/:id com streaming de pontos
- [x] `api/routes/davis.py` — endpoints basicos Copa Davis / BJK Cup
- [x] Adaptar `avancar_semana` de `calendario.py` para retornar dict em vez de printar
- [x] Adaptar `torneio_core` para expor estado como dict serializavel

### Notas tecnicas

- `jogar_partida.py` usa `input()` internamente — para modo automatico, passar `modo="rapido"`
- Para WebSocket: rodar simulacao em `asyncio` com `await asyncio.sleep(0.3)` entre pontos
- Estado de partida ativa: guardar em `api/session.py` junto ao save ativo
- `torneio_core.Torneio` ja tem metodo `to_dict()` — usar como base para TorneioState
- `calendario.avancar_semana()` retorna eventos como lista de strings — encapsular em JSON

### Atualizacoes de progresso

- **2026-03-06:** Criados `api/routes/calendario.py`, `api/routes/torneio.py`, `api/routes/partida.py`, `api/routes/davis.py` e `api/ws/partida.py`.
- **2026-03-06:** Adicionado runtime de partida em memoria com suporte a ponto-a-ponto via HTTP e streaming via WebSocket.
- **2026-03-06:** `src/calendario.avancar_semana()` agora retorna payload estruturado para a API; `src/torneio_core.Torneio.to_api_state()` expõe estado serializavel.
- **2026-03-06:** Runtime de partida passou a persistir snapshots por save em `saves/<save>/api_runtime/matches/` para permitir reidratacao apos restart.
- **2026-03-06:** Corrigido contrato do bracket em `src/torneio_core._serializar_confronto_api()` para `jogador1/jogador2/vencedor/placar`, e removidos `print()`/`safe_input()` bloqueantes de `src/calendario.avancar_semana()`.
- **2026-03-06:** `src/torneio_core.to_api_state()` passou a reutilizar o `estado` ja carregado ao serializar o bracket, evitando recarregar disco para cada confronto.

---

## Secao Claude — Frontend React

### Responsabilidade

- Setup completo do projeto React em `frontend/`
- Todos os componentes base (design system)
- Todas as paginas/telas
- `frontend/src/api/client.ts` (wrapper HTTP + WS)
- `capacitor.config.ts` (config mobile)

### Decisao de projeto

O Figma AI ja gerou o projeto em `Front/` com visual, componentes e rotas completos.
Claude trabalhou APENAS na camada de integracao com a API, sem alterar UI.
Pasta `frontend/` criada erroneamente antes de ver `Front/` — pode ser deletada.

### Tarefas

**Infraestrutura de integracao**
- [x] `Front/src/types/index.ts` — tipos alinhados com contratos de API
- [x] `Front/src/api/client.ts` — fetch nativo HTTP + WebSocket helper
- [x] `Front/src/store/gameStore.ts` — Zustand: saveAtivo, jogador, semana, torneio, partidaId
- [x] `Front/package.json` — adicionado zustand, @capacitor/core, @capacitor/android, @capacitor/cli
- [x] `Front/vite.config.ts` — proxy /api → :8000 e /ws → ws://:8000
- [x] `Front/capacitor.config.ts` — appId=com.tennislegacy.app, webDir=dist

**Componentes base** (ja existiam no Figma, sem alteracao)
- [x] `NeonButton`, `NeonCard`, `PixelBar`, `ScoreBoard`, `PlayerRow`, `TierBadge`
- [x] `ArcadeTab`, `LoadingScreen`, `TronGrid`, `ArcadeNotification`
- [x] CSS: scanlines CRT, neon glow, pixel-font, arcade-font

**Screens conectadas a API real**
- [x] `HomeScreen` — formulario novo jogo inline → api.saves.criar + carregar → store
- [x] `ContinueScreen` — lista saves reais, carrega save, popula store
- [x] `HubScreen` — le do store, sincroniza com api.jogador.get() no mount
- [x] `RankingsScreen` — dados ATP/WTA reais, toggle tour, busca por nome
- [x] `CalendarScreen` — calendario real, inscricao em torneio, pular semana
- [x] `MatchScreen` — WebSocket streaming, fallback REST polling, estrategia

**Screens anteriormente bloqueadas — agora conectadas**
- [x] `TournamentBracket` — estado real via api.torneio.estado(), bracket agrupado por fase, fluxo jogar/simular/desistir
- [x] `PlayerScreen` — atributos/equipe/patrocinios reais; header do store

**Mobile**
- [x] `Front/capacitor.config.ts` — Android configurado

### Notas tecnicas

- Rodar: `cd Front && pnpm install && pnpm dev`
- Proxy Vite resolve CORS em dev sem configurar backend
- react-router v7 createBrowserRouter (nao hash) — para Capacitor ajustar se necessario
- Zustand sem persist — MVP ok; reload pede novo carregar save
- Screens degradam graciosamente se API indisponivel

### Atualizacoes de progresso

- **2026-03-06:** Integracao completa: types, client, store, proxy, 6 screens conectadas.
  Visual intacto. Aguardando Gemini (equipe/patrocinios) e Codex (torneio/WS partida).
- **2026-03-06:** TournamentBracket e PlayerScreen conectados apos Gemini e Codex finalizarem.
  api/client.ts atualizado: torneio.criar() aceita torneio_nome opcional (decisao Codex).
  CalendarScreen atualizado para passar torneio_nome na inscricao.
- **2026-03-08:** ProgressionScreen deixou de exibir a secao mockada de equipment e passou a usar checkpoints reais de carreira derivados da API (titulos, majors, masters e atributos dominantes).
  O unico fluxo que permanece local por design e a SettingsScreen.

---

## Secao Codex — Game Logic API
...
## Bloqueios e Dependencias

| IA | Bloqueio | Depende de | Status |
|---|---|---|---|
| Claude | HomeScreen sem teste | Gemini: /api/saves e /api/save/carregar | [x] pronto |
| Claude | PartidaScreen | Codex: /ws/partida | [x] pronto |
| Codex | avancar_semana | Gemini: session.py (save ativo) | [x] pronto |
| Claude | Integracao real das rotas de calendario/torneio/partida | Gemini: `api/main.py` incluir routers do Codex e WebSocket | [x] pronto |

---

## Como rodar localmente

```bash
# Backend
pip install -r requirements-api.txt
uvicorn api.main:app --reload --port 8000

# Frontend (pasta gerada pelo Figma AI)
cd Front
pnpm install   # ou: npm install
pnpm dev       # http://localhost:5173

# Mobile (depois do frontend pronto)
cd Front
pnpm build
npx cap sync android
npx cap open android
```

---

## Decisoes e historico

| Data | Decisao | Motivo |
|---|---|---|
| 2026-03-06 | Backend local (nao nuvem) | Simplicidade inicial |
| 2026-03-06 | React + Capacitor (nao Flutter) | Preservar logica Python |
| 2026-03-06 | Zustand (nao Redux) | Menor boilerplate |
| 2026-03-06 | Hash routing | Compatibilidade Capacitor |
| 2026-03-06 | `POST /api/torneio/criar` aceita `torneio_nome` opcional | O contrato original nao identificava qual torneio da semana deveria ser inscrito quando ha mais de um disponivel |
| 2026-03-06 | Runtime de partida fica em memoria e usa `api.session.Session.partida_context` | Evita persistencia parcial por ponto e respeita a observacao de manter estado ativo junto da sessao |
| 2026-03-06 | `/api/davis` ficou read-mostly na V1 | `src.davis_cup.py` ainda depende de fluxo CLI para ties com jogador humano; expus estado/proximo e simulacao apenas quando o humano nao joga |
| 2026-03-06 | Snapshot de partida fica em `saves/<save>/api_runtime/matches/` com cache em memoria | Melhor decisao possivel agora: resiliencia a restart sem introduzir banco/Redis antes da hora, preservando caminho claro para trocar o backend do store depois |
| 2026-03-06 | `api/main.py` passou a incluir todos os routers HTTP e o router WS da partida | Fecha o wiring final entre as entregas de Gemini, Codex e Claude sem mudar responsabilidades do dominio |
