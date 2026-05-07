// Cliente HTTP e WebSocket para o backend FastAPI (localhost:8000)
// Proxy configurado no vite.config.ts para /api e /ws

import type {
  JogadorState,
  RankingEntry,
  TorneioState,
  PlacarState,
  MatchPointRuntime,
  TorneioCalendario,
  ResumoDaSemana,
  MembroEquipe,
  Patrocinio,
  PatrocinioDisponivel,
  AssinarPatrocinioResponse,
  PlacarEvent,
  SavePreview,
  MundoTorneio,
  DavisState,
  Transaction,
  MatchHistoryEntry,
  RankingDetalhado,
  RaceToFinals,
  TorneioAoVivo,
  NacaoRanking,
  WeekAdvancePayload,
  JogadorStatus,
  AdversarioInfo,
  PartidaAtiva,
  PartidaConfig,
  PartidaIniciar,
  PartidaPreview,
  PartidaScout,
  MembroMercado,
  EmailItem,
  GoatRecordes,
  TituloCarreira,
  VinculoDupla,
  ArquetipoInfo,
  PlayerProfile,
} from '../types'

const BASE = '/api'
const TIMEOUT_MS = 15_000

let currentSaveName: string | null = null

export function setApiSaveName(saveName: string | null) {
  currentSaveName = saveName
}

export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function req<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS)
  
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (currentSaveName) {
    headers['X-Save-Name'] = currentSaveName
  }

  let res: Response
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    })
  } catch (err) {
    clearTimeout(timer)
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new ApiError(`Tempo limite excedido: ${method} ${path}`, 408)
    }
    throw new ApiError(`Sem conexão com o servidor`, 0)
  }
  clearTimeout(timer)
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    const msg = data.detail || `API ${method} ${path} → ${res.status}`
    throw new ApiError(msg, res.status)
  }
  return res.json() as Promise<T>
}

const get = <T>(path: string) => req<T>('GET', path)
const post = <T>(path: string, body?: unknown) => req<T>('POST', path, body)

// ── Save / Sessão ──────────────────────────────────────────────────────────

export const api = {
  saves: {
    listar: () => get<{ saves: string[] }>('/saves'),

    arquetipos: () => get<{ tecnicos: Record<string, ArquetipoInfo>; mentais: Record<string, ArquetipoInfo> }>('/save/arquetipos'),

    nacionalidades: () => get<{ nacionalidades: string[] }>('/save/nacionalidades'),

    criar: (payload: {
      nome: string
      nome_jogador: string
      nacionalidade: string
      tour: 'atp' | 'wta'
      idade?: number
      archetype_id?: string
      mental_id?: string
    }) => post<{ ok: boolean; save: string }>('/save/criar', payload),

    criarAlexandre: (nome: string) =>
      post<{ ok: boolean; save: string }>('/save/criar-alexandre', { nome }),

    carregar: (nome: string) =>
      post<{ ok: boolean; jogador: JogadorState; semana: number; ano: number; torneio: TorneioState | null }>(
        '/save/carregar',
        { nome }
      ),

    salvar: () => post<{ ok: boolean; save: string }>('/save/salvar'),

    preview: (nome: string) => get<SavePreview>(`/save/${nome}/preview`),

    deletar: (nome: string) => req<{ ok: boolean }>('DELETE', `/save/${nome}`),

    sessao: () => get<{ save_ativo: string | null }>('/sessao'),
  },

  // ── Jogador ───────────────────────────────────────────────────────────────

  jogador: {
    get: () => get<JogadorState>('/jogador'),

    atributos: () =>
      get<{ atributos: Record<string, number>; overall: number }>(
        '/jogador/atributos'
      ),

    equipe: () =>
      get<{
        treinador: MembroEquipe | null
        fisio: MembroEquipe | null
        psicologo: MembroEquipe | null
        empresario: MembroEquipe | null
      }>('/jogador/equipe'),

    patrocinios: () =>
      get<{ patrocinios: Patrocinio[] }>('/jogador/patrocinios'),

    patrociniosDisponiveis: () =>
      get<{ patrocinadores: PatrocinioDisponivel[] }>('/jogador/patrocinios-disponiveis'),

    assinarPatrocinio: (id: string) =>
      post<AssinarPatrocinioResponse>('/jogador/assinar-patrocinio', { patrocinio_id: id }),

    financeiro: () =>
      get<{ saldo: number; transacoes: Transaction[]; resumo_categorias: Record<string, number> }>(
        '/jogador/financeiro'
      ),

    historicoPartidas: () =>
      get<{ historico: MatchHistoryEntry[] }>('/jogador/historico-partidas'),

    rankingDetalhado: () =>
      get<RankingDetalhado>('/jogador/ranking-detalhado'),

    carreira: () =>
      get<{ fase: string; idade: number; pico_carreira: number; nivel: number; xp: number; xp_para_proximo: number; titulos: TituloCarreira[] }>(
        '/jogador/carreira'
      ),

    rankingHistorico: () =>
      get<{ semanas: { semana: number; ano: number; posicao: number; pontos: number }[] }>(
        '/jogador/ranking-historico'
      ),

    formaRecente: () =>
      get<{
        forma: ('V' | 'D')[]
        partidas: { adversario: string; resultado: string | null; torneio: string | null; semana: number | null; ano: number | null; venceu: boolean }[]
      }>('/jogador/forma-recente'),

    rivalidades: () =>
      get<{
        rivalidades: { nome: string; confrontos: number; vitorias: number; win_rate: number; ultima_semana: number; rival_ativo: boolean }[]
      }>('/jogador/rivalidades'),
  },

  // ── Ranking ───────────────────────────────────────────────────────────────

  ranking: {
    atp: (limit = 100, offset = 0) =>
      get<{ ranking: RankingEntry[]; total: number }>(
        `/ranking/atp?limit=${limit}&offset=${offset}`
      ),

    wta: (limit = 100, offset = 0) =>
      get<{ ranking: RankingEntry[]; total: number }>(
        `/ranking/wta?limit=${limit}&offset=${offset}`
      ),

    duplas: (tour: 'atp' | 'wta', limit = 50) =>
      get<{ ranking: RankingEntry[]; total: number }>(
        `/ranking/duplas/${tour}?limit=${limit}`
      ),

    nacoes: (limit = 30) =>
      get<{ ranking: NacaoRanking[]; total: number }>(`/ranking/nacoes/davis?limit=${limit}`),

    superficie: (sup: string, tour: 'atp' | 'wta' = 'atp', limit = 100) =>
      get<{
        superficie: string
        jogadores: { posicao: number; nome: string; pontos_superficie: number; overall: number; nacionalidade?: string }[]
      }>(`/ranking/superficie/${encodeURIComponent(sup)}?tour=${tour}&limit=${limit}`),

    jogador: (
      nome: string,
      tour?: 'atp' | 'wta',
      modalidade: 'simples' | 'duplas' = 'simples'
    ) =>
      get<PlayerProfile>(
        `/ranking/jogador?nome=${encodeURIComponent(nome)}${tour ? `&tour=${tour}` : ''}&modalidade=${modalidade}`
      ),
  },

  // ── Mundo ─────────────────────────────────────────────────────────────────

  mundo: {
    proximos: () =>
      get<{ semana_atual: number; torneios: MundoTorneio[] }>('/mundo/proximos'),
    noticias: () => get<{ noticias: string[] }>('/mundo/noticias'),
    torneio: (nome: string, tour?: string) =>
      get<TorneioState>(`/mundo/torneio/${nome}${tour ? `?tour=${tour}` : ''}`),
    rankingNacoes: () =>
      get<{ nacoes: { posicao: number; pais: string; codigo: string; pontos: number; flag: string }[] }>(
        '/mundo/ranking-nacoes'
      ),

    aoVivo: () =>
      get<{ semana: number; torneios: TorneioAoVivo[] }>('/mundo/ao-vivo'),
    raceToFinals: () =>
      get<RaceToFinals>('/mundo/race-to-finals'),
    bracket: (torneio: string, tour: 'atp' | 'wta') =>
      get<{ nome: string; tipo: string; fase_atual: string; rodadas: Record<string, [string, string][]>; resultados: Record<string, Record<string, string>[]>; campeao_simples: string | null }>(
        `/mundo/bracket?torneio=${encodeURIComponent(torneio)}&tour=${tour}`
      ),
  },

  // ── Calendário ────────────────────────────────────────────────────────────

  calendario: {
    semana: (n: number) =>
      get<{ semana: number; torneios: TorneioCalendario[] }>(
        `/calendario/semana/${n}`
      ),

    atual: () =>
      get<{ semana: number; ano: number; torneios: TorneioCalendario[] }>(
        '/calendario/atual'
      ),

    avancar: () =>
      post<WeekAdvancePayload>(
        '/calendario/avancar'
      ),
  },

  // ── Torneio ───────────────────────────────────────────────────────────────

  torneio: {
    criar: (
      modalidade: 'simples' | 'duplas' | 'mistas',
      parceiro?: string,
      torneio_nome?: string
    ) =>
      post<{ ok: boolean; torneio: TorneioState }>('/torneio/criar', {
        modalidade,
        parceiro,
        torneio_nome,
      }),

    checarConvocacao: () => get<{
      convocado: boolean
      posicao?: number
      mensagem: string
      torneio?: TorneioCalendario
    }>('/torneio/checar-convocacao'),

    estado: () => get<TorneioState | null>('/torneio/estado'),

    avancarFase: () =>
      post<{
        fase: string
        resultados: { jogador1: string; jogador2: string; placar: string; vencedor: string }[]
        proximo: { adversario: string; fase: string; superficie: string } | null
      }>('/torneio/avancar-fase'),

    desistir: () => post<{ ok: boolean } & WeekAdvancePayload>('/torneio/desistir'),

    historico: (nome: string) =>
      get<{ pontos_a_defender: number; ultima_colocacao: string | null }>(
        `/torneio/historico?nome=${encodeURIComponent(nome)}`
      ),
  },

  // ── Partida ───────────────────────────────────────────────────────────────

  partida: {
    preview: () =>
      get<PartidaPreview>('/partida/preview'),

    scout: (nomeAdversario: string) =>
      get<PartidaScout>(`/partida/scout/${encodeURIComponent(nomeAdversario)}`),

    ativa: () =>
      get<PartidaAtiva | null>('/partida/ativa'),

    iniciar: (modo: 'detalhado' | 'rapido' | 'estrategista') =>
      post<PartidaIniciar>(
        '/partida/iniciar',
        { modo }
      ),

    desistir: (partida_id: string) =>
      post<{ ok: boolean }>('/partida/desistir', { partida_id }),

    ponto: (partida_id: string) =>
      post<MatchPointRuntime>('/partida/ponto', { partida_id }),

    simularSet: (partida_id: string) =>
      post<MatchPointRuntime>('/partida/simular-set', { partida_id }),

    simularPartida: (partida_id: string) =>
      post<MatchPointRuntime>('/partida/simular-partida', { partida_id }),

    estrategia: (partida_id: string, estrategia: string) =>
      post<{ ok: boolean }>('/partida/estrategia', { partida_id, estrategia }),

    ajusteTatico: (partida_id: string, estrategia: string, set_numero = 0) =>
      post<{ ok: boolean; set_ajustado: number }>(
        '/partida/ajuste-tatico',
        { partida_id, estrategia, set_numero }
      ),
  },

  // ── Treinamento ───────────────────────────────────────────────────────────

  treinamento: {
    opcoes: () => get<{ opcoes: { id: string; nome: string; descricao: string; custo_energia: number }[] }>('/treinamento/opcoes'),
    descanso: () =>
      post<{ ok: boolean; energia: number; fadiga: number; mensagem: string; semana?: number }>(
        '/treinamento/descanso'
      ),
    executar: (foco: string) => post<{
      ok: boolean
      melhorias: Record<string, number>
      semana?: number
      ano?: number
      jogador_status: JogadorStatus
    }>('/treinamento/executar', { foco }),
  },

  // ── Progressao ────────────────────────────────────────────────────────────

  progressao: {
    status: () =>
      get<{
        nivel: number
        xp: number
        xp_para_proximo_nivel: number
        pontos_de_skill: number
        atributos: Record<string, number>
        atributos_psicologicos: Record<string, number>
      }>('/progressao/status'),
    alocar: (tipo: 'tecnico' | 'psicologico', atributo: string) =>
      post<{
        ok: boolean
        pontos_de_skill: number
        atributos: Record<string, number>
        atributos_psicologicos: Record<string, number>
      }>('/progressao/alocar', { tipo, atributo }),
  },

  // ── Mercado ───────────────────────────────────────────────────────────────

  mercado: {
    profissionais: () => get<Record<string, MembroMercado[]>>('/mercado/profissionais'),
    contratar: (prof_id: string) => post<{ ok: boolean; mensagem: string }>('/mercado/contratar', { prof_id }),
    demitir: (prof_id: string) => post<{ ok: boolean; mensagem: string }>('/mercado/demitir', { prof_id }),
  },

  // ── E-mail ────────────────────────────────────────────────────────────────

  email: {
    inbox: () => get<{ emails: EmailItem[]; unread_count: number }>('/email/inbox'),
    unreadCount: () => get<{ unread_count: number }>('/email/unread-count'),
    marcarLidos: () => post<{ ok: boolean }>('/email/marcar-lidos', {}),
    acao: (email_id: string, acao: 'aceitar' | 'recusar' | 'deletar') => 
      post<{ ok: boolean; mensagem: string }>('/email/acao', { email_id, acao }),
  },

  // ── Histórico ─────────────────────────────────────────────────────────────

  historico: {
    goat: () => get<{ recordes: GoatRecordes; meus_titulos: TituloCarreira[] }>('/historico/goat'),
    campeoes: () => get<{ campeoes: Record<string, TituloCarreira[]> }>('/historico/campeoes'),
  },

  // ── Davis Cup / BJK Cup ───────────────────────────────────────────────────

  davis: {
    estado: () =>
      get<DavisState>('/davis/estado'),
    proximo: () => get<Record<string, unknown> | null>('/davis/proximo'),
    simular: () => post<{ ok: boolean; placar: string; vencedor: string }>('/davis/simular-atual'),
  },

  // ── Duplas ────────────────────────────────────────────────────────────────

  duplas: {
    sugestoes: () => get<{
      parceiros: {
        nome: string
        nacionalidade: string
        overall: number
        duplas?: number
        posicao?: number
        vinculo?: VinculoDupla
      }[]
    }>('/duplas/sugestoes'),

    buscar: (params: { nome?: string; nacionalidade?: string }) => {
      let q = ''
      if (params.nome) q = `?nome=${params.nome}`
      else if (params.nacionalidade) q = `?nacionalidade=${params.nacionalidade}`
      return get<{
        parceiros: {
          nome: string
          nacionalidade: string
          overall: number
          duplas?: number
          posicao?: number
        }[]
      }>(`/duplas/buscar${q}`)
    },

    convidar: (npc_nome: string, torneio_tipo: string) =>
      post<{ ok: boolean; mensagem: string; parceiro?: { nome: string; nacionalidade: string } }>(
        '/duplas/convidar',
        { npc_nome, torneio_tipo }
      ),
  },
}

// ── WebSocket helper ──────────────────────────────────────────────────────

export interface WSConn {
  send: (data: object) => void
  close: () => void
}

export function conectarPartida(
  partida_id: string,
  onEvent: (e: PlacarEvent) => void,
  onClose?: () => void
): WSConn {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const host = window.location.host
  const ws = new WebSocket(`${proto}://${host}/ws/partida/${partida_id}`)

  ws.onmessage = (e) => {
    try {
      onEvent(JSON.parse(e.data) as PlacarEvent)
    } catch {
      // ignorar mensagens malformadas
    }
  }

  ws.onclose = () => onClose?.()

  return {
    send: (data) => {
      if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(data))
    },
    close: () => ws.close(),
  }
}
