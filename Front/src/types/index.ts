// Tipos alinhados com os contratos de API

export interface Transaction {
  semana: number
  valor: number
  descricao: string
  categoria: string
  saldo_pos: number
}

export interface MatchHistoryEntry {
  torneio: string
  ano: number
  semana: number
  fase: string
  adversario: string
  placar: string
  resultado: 'V' | 'D'
}

export interface JogadorState {
  nome: string
  nacionalidade: string
  idade: number
  altura?: number
  peso?: number
  mao_dominante?: string
  reves?: string
  estilo_jogo?: string
  pico_carreira: number
  tour: 'atp' | 'wta'
  ranking: number
  pontos: number
  overall: number
  resumo_fifa?: Record<string, number>
  energia: number
  fadiga: number
  status_lesao: string | null
  dinheiro: number
  seguidores: number
  nivel: number
  xp: number
  xp_para_proximo_nivel: number
  atributos: Record<string, number>
  atributos_psicologicos?: Record<string, number>
  resumo_fifa?: Record<string, number>
  historico_partidas?: Array<Record<string, unknown>>
  historico_torneios?: Array<Record<string, unknown>>
  trofeus?: Array<Record<string, unknown>>
  carta?: CartaJogador
  identity?: PlayerIdentity
}

export interface RankingEntry {
  posicao: number
  nome: string
  nacionalidade: string
  idade?: number
  pontos: number
  pontos_duplas?: number
}

export interface BracketNode {
  id: string
  jogador1: string
  jogador2: string
  jogador1_nacionalidade?: string
  jogador2_nacionalidade?: string
  vencedor?: string
  placar?: string
  fase: string
}

export interface TorneioState {
  nome: string
  tipo: string
  superficie: string
  fase_atual: string
  bracket: BracketNode[]
  jogador_ativo: boolean
  campeao_simples?: string
  davis?: boolean
  destino_click_hub?: string
  partida_disponivel?: boolean
  info_partida?: {
    jogador1: string
    jogador2: string
    fase: string
    adversario?: AdversarioInfo
  } | null
  estado?: Record<string, unknown>
}

export interface PlacarState {
  sets: [number, number]
  games: [number, number]
  pontos: [string, string]
  servindo: 'jogador' | 'adversario'
  log: string[]
  encerrado: boolean
  vencedor?: 'jogador' | 'adversario'
  placar_final?: string
  stats_j?: MatchStatsSummary
  stats_a?: MatchStatsSummary
}

export interface MatchStatsSummary {
  aces: number
  duplas_faltas: number
  primeiro_saque_pct: string
  winners: number
  erros_nao_forcados: number
  pontos_saque_pct: string
  pontos_devolucao_pct: string
  break_points: string
  rallies_curtos: number
  rallies_medios: number
  rallies_longos: number
}

export interface MatchStrategySummary {
  estilo?: string
  saque?: string
  saque_tipo?: string
  intencao?: string
  mentalidade?: string
  abordagem?: string
  instrucao?: string
}

export interface PlacarEvent extends PlacarState {
  tipo: 'ponto' | 'game' | 'set' | 'fim'
  descricao: string
  estrategia_j?: MatchStrategySummary
  estrategia_a?: MatchStrategySummary
}

export interface MatchPointRuntime extends PlacarEvent {
  last_point_stats?: {
    sacador: string
    primeiro_saque_in: boolean
    ace: boolean
    dupla_falta: boolean
    winner: boolean
    erro_nao_forcado: boolean
    intensidade: string
    insights: string[]
    origem: [number, number]
    destino: [number, number]
  }
  energia_j: number
  energia_a: number
  fadiga_j: number
  fadiga_a: number
  estrategia_j: MatchStrategySummary
  estrategia_a: MatchStrategySummary
  ajuste_tatico_j: string
  ajuste_tatico_a: string
}

export interface TorneioCalendario {
  nome: string
  tipo: string
  superficie: string
  local: string
  pais: string
  codigo_pais?: string
  semana: number
  premiacao?: string
  permite_mistas?: boolean
  quadra_nome?: string
  horario_local?: string
  sessao_label?: string
  janela_semana?: string
}

export interface MundoTorneio extends TorneioCalendario {}

export interface DavisHistoricoPartida {
  jogador_a: string
  jogador_b: string
  placar: string
  vencedor: string
}

export interface DavisConfrontoAtual {
  equipe_a: string
  equipe_b: string
  placar_tie: number[]
  partidas: DavisHistoricoPartida[]
  vencedor?: string | null
}

export interface DavisInfoPartida {
  jogador1: string
  jogador2: string
  partida_idx?: number | null
  tipo?: string | null
}

export interface DavisState {
  nome: string
  tipo: string
  fase_atual: string
  jogador_ativo: boolean
  jogador_convocado: boolean
  partida_disponivel: boolean
  info_partida?: DavisInfoPartida | null
  confronto_atual?: DavisConfrontoAtual | null
  proximo?: Record<string, unknown> | null
  estado: Record<string, unknown>
}

export interface CampeaoSemana {
  tour: string
  torneio: string
  simples: string
  duplas?: string | null
}

export interface ResumoDaSemana {
  campeoes: CampeaoSemana[]
}

export interface WeekAdvanceStep {
  id: string
  titulo: string
  resumo: string
  tom: 'neutral' | 'positive' | 'warning' | 'info'
  detalhes: string[]
}

export interface WeekAdvancePayload {
  semana: number
  ano?: number
  eventos: string[]
  processamento?: WeekAdvanceStep[]
  torneios_disponiveis?: TorneioCalendario[]
  resumo_mundial: ResumoDaSemana
}

export interface MembroEquipe {
  nome: string
  nivel: number
  custo_semanal: number
  bonus: Record<string, number>
}

export interface Patrocinio {
  id: string
  nome: string
  categoria: string
  nivel: string
  valor: number
  semanas_restantes: number
}

export interface PatrocinioDisponivel {
  id: string
  nome: string
  categoria: string
  nivel: string
  valor_mensal: number
  valor_semanal: number
  bonus_assinatura: number
  requisito_ranking: number
  requisito_seguidores: number
  elegivel: boolean
  motivo_bloqueio: string | null
  descricao: string
}

export interface PatrocinioContexto {
  ranking_atual: number
  seguidores_atuais: number
  patrocinios_ativos: number
  slots_menores_restantes: number
  slot_master_disponivel: boolean
}

export interface AssinarPatrocinioResponse {
  ok: boolean
  mensagem: string
}

export interface SavePreview {
  nome: string
  jogador_nome: string
  tour: 'atp' | 'wta'
  semana: number
  ranking?: number
}

export interface ResultadoTemporada {
  nome: string
  fase: string
  pontos: number
  obrigatorio: boolean
}

export interface RankingDetalhado {
  posicao_simples: number | null
  posicao_duplas: number | null
  pontos_simples: number
  pontos_duplas: number
  pontos_ytd: number
  resultados_simples: ResultadoTemporada[]
  resultados_duplas: ResultadoTemporada[]
}

export interface RaceEntry {
  posicao: number
  nome: string
  nacionalidade: string
  pontos_ytd: number
  e_jogador: boolean
}

export interface RaceToFinals {
  tour: string
  top8: RaceEntry[]
  posicao_jogador: number | null
  pontos_jogador: number
  faltam_para_classificar: number
}

export interface TorneioAoVivo {
  nome: string
  tipo: string
  tour: string
  fase_atual: string
  campeao_simples: string | null
  campeao_duplas: string | null
  finalizado: boolean
}

export interface NacaoRanking {
  posicao: number
  nome: string
  codigo: string
  pontos: number
}

// ---------------------------------------------------------------------------
// Interfaces de API — substituem os `any` em client.ts
// ---------------------------------------------------------------------------

export interface JogadorStatus {
  energia: number
  fadiga: number
  atributos: Record<string, number>
  atributos_psicologicos: Record<string, number>
}

export interface AdversarioInfo {
  nome: string
  nacionalidade?: string
  idade?: number
  altura?: number
  peso?: number
  mao_dominante?: string
  reves?: string
  estilo_jogo?: string
  overall?: number
  ranking?: number
  ranking_pos?: number
  energia?: number
  fadiga?: number
  pontos?: number
  pontos_ytd?: number
  pico_carreira?: number
  atributos?: Record<string, number>
  atributos_psicologicos?: Record<string, number>
  trofeus?: Array<Record<string, unknown>>
  historico_torneios?: Array<Record<string, unknown>>
  historico_partidas?: Array<Record<string, unknown>>
  resumo_fifa?: Record<string, number>
}

export interface CartaJogador {
  tipo: 'lenda' | 'gs' | 'if' | 'ds' | 'wk' | 'iconic' | 'gold' | 'silver' | 'bronze'
  label: string
  raridade: 'iconic' | 'special' | 'gold' | 'silver' | 'bronze'
  cor_primaria: string
  cor_secundaria: string
  bonus: Record<string, number>
  contexto: 'duplas' | null
}

export interface PlayerRole {
  id: string
  label: string
  fit: number
  description: string
}

export interface PlayerBodyType {
  id: string
  label: string
  description: string
}

export interface PlayerPlaystyle {
  id: string
  label: string
  description: string
  tier: 'base' | 'plus'
  focus: string[]
}

export interface PlayerDoublesProfile {
  specialist: boolean
  rating: number
  archetype: string
  best_partner?: string | null
  record?: string | null
  partnerships: number
}

export interface PlayerIdentity {
  role: PlayerRole
  body_type: PlayerBodyType
  playstyles: PlayerPlaystyle[]
  hidden_stats: Record<string, number>
  doubles_profile: PlayerDoublesProfile
  meta?: {
    ranking_anchor?: number | null
    surface_bias?: string
  }
}

export interface PlayerProfile {
  nome: string
  tour: 'atp' | 'wta'
  modalidade?: 'simples' | 'duplas'
  nacionalidade: string
  idade: number
  altura: number
  peso: number
  mao_dominante?: string
  reves?: string
  estilo_jogo?: string
  ranking: number | null
  pontos: number
  pontos_ytd: number
  overall: number
  overall_boosted?: number
  energia: number
  fadiga: number
  pico_carreira: number
  atributos: Record<string, number>
  atributos_psicologicos: Record<string, number>
  resumo_fifa: Record<string, number>
  trofeus: Array<Record<string, unknown>>
  historico_torneios: Array<Record<string, unknown>>
  historico_partidas: Array<Record<string, unknown>>
  carta?: CartaJogador
  identity?: PlayerIdentity
}

export interface RankingEntryExtended extends RankingEntry {
  overall?: number
  carta_tipo?: string
  carta_raridade?: string
}

export interface PartidaConfig {
  modo: string
  superficie: string
  melhor_de: number
  nome_torneio?: string
  tipo_torneio?: string
  tiebreak_decisivo_pontos?: number
}

export interface PartidaPreview {
  adversario: AdversarioInfo
}

export interface PartidaAtiva {
  partida_id: string
  config: PartidaConfig
  adversario: AdversarioInfo
  placar: PlacarState
}

export interface PartidaIniciar {
  partida_id: string
  config: PartidaConfig
  adversario?: AdversarioInfo
  placar?: PlacarState
}

export interface PartidaScoutH2H {
  vitorias_jogador: number
  vitorias_adversario: number
}

export interface PartidaScout {
  nome: string
  ranking: number
  overall: number
  atributos: Record<string, number>
  atributos_psicologicos: Record<string, number>
  superficie_favorita: string
  forma_recente: string[]
  h2h: PartidaScoutH2H
  nacionalidade: string
  metricas: {
    saque: number
    fundo: number
    mental: number
  }
  texto: string
  dicas: string[]
  pontos_fortes: string[]
  fraquezas: string[]
}

export interface MembroMercado {
  id: string
  nome: string
  nivel?: number
  categoria: string
  custo_semanal?: number
  salario_semanal?: number
  bonus?: Record<string, number>
  estrelas?: number
}

export interface EmailItem {
  id: string
  remetente: string
  assunto: string
  corpo: string
  lido: boolean
  tipo?: string
  acao?: string
}

export interface GoatRecordes {
  mais_titulos?: string
  mais_grand_slams?: string
  mais_semanas_no_1?: string
  [key: string]: string | number | undefined
}

export interface TituloCarreira {
  torneio: string
  ano: number
  modalidade?: string
}

export interface VinculoDupla {
  partidas: number
  vitorias: number
}

export interface ArquetipoInfo {
  nome: string
  descricao?: string
  bonus?: Record<string, number>
}

export interface MundoTorneioDetalhe {
  tournament_data?: {
    nome?: string
    tipo?: string
  }
  fase_atual?: string
  fase_atual_duplas?: string
  campeao_simples?: string | null
  campeao_duplas?: string | null
  fases?: string[]
  fases_duplas?: string[]
  rodadas?: Record<string, Array<[string | { nome: string }, string | { nome: string }]>>
  rodadas_duplas?: Record<string, Array<[string | { nome: string }, string | { nome: string }]>>
  resultados?: Record<string, Array<Record<string, string>>>
  resultados_duplas?: Record<string, Array<Record<string, string>>>
}
