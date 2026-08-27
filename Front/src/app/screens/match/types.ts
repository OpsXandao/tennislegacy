export type Fase =
  | 'hype'
  | 'setup'
  | 'aguardando'
  | 'jogando'
  | 'entre-games'
  | 'entre-sets'
  | 'encerrada'
  | 'pos-stats'
  | 'pos-consequencias'

export type ModoAcomp = 'estrategista' | 'detalhado' | 'game' | 'auto'
export type PlanoValor = 'pressionar' | 'consistencia' | 'variar'
export type Faixa = 'FUNDO' | 'MEIO' | 'REDE'
export type Alvo = 'ESQUERDA' | 'CENTRO' | 'DIREITA'
export type SegundoSaqueModo = 'SEGURO' | 'FORCAR'
export type VelocidadeRapida = 'lenta' | 'normal' | 'rapida' | 'turbo'
export type MentalidadeValor = 'EQUILIBRADA' | 'OFENSIVA' | 'DEFENSIVA'
export type AbordagemValor = 'BASELINE' | 'SERVE_VOLLEY' | 'COUNTER'
export type InstrucaoValor = 'PADRAO' | 'FORCAR_BACKHAND' | 'TROCAS_LONGAS' | 'ATACAR_SAQUE'
export type Surface = 'hard' | 'clay' | 'grass'

export interface PacoteTaticoState {
  mentalidade: MentalidadeValor
  abordagem: AbordagemValor
  instrucao: InstrucaoValor
  segundoSaque: SegundoSaqueModo
  modo: ModoAcomp
}

export interface GameResult {
  quemGanhou: 'jogador' | 'adversario'
  foiBreak: boolean
  placarGames: [number, number]
}

export interface AdversarioInfo {
  nome: string
  nacionalidade?: string | null
  idade?: number | null
  altura?: number | null
  peso?: number | null
  maoDominante?: string | null
  reves?: string | null
  energia: number
  fadiga: number
  ranking: number | null
  overall?: number | null
  trofeus?: Array<Record<string, unknown>>
  atributos?: Record<string, number>
  atributosPsicologicos?: Record<string, number>
  historicoTorneios?: Array<Record<string, unknown>>
  historicoPartidas?: Array<Record<string, unknown>>
  resumoFifa?: Record<string, number>
  carta?: any
  overallBoosted?: number
  atributosBoosted?: Record<string, number>
  estilo: string
}
