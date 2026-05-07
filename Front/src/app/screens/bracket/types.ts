export const FASE_ORDEM: Record<string, number> = {
  qualy_r1: -3,
  qualy_1: -3,
  qualy_r2: -2,
  qualy_2: -2,
  qualy_r3: -1,
  r96: 0,
  r128: 0,
  r64: 1,
  r32: 2,
  pre_oitavas: 3,
  oitavas: 4,
  r16: 4,
  quartas: 5,
  qf: 5,
  semis: 6,
  sf: 6,
  semifinal: 6,
  final: 7,
  f: 7,
}

export const HEADER_HEIGHT = 44
export const CARD_HEIGHT = 64
export const CARD_WIDTH = 220
export const COLUMN_GAP = 78
export const INITIAL_MATCH_GAP = 22

export interface MatchCardData {
  id: string
  player1: string
  player2: string
  player1Nationality?: string
  player2Nationality?: string
  score?: string
  winner?: 1 | 2
  isCurrentMatch?: boolean
}

export interface ParsedRowScore {
  player1?: string
  player2?: string
}

export interface Round {
  name: string
  fase: string
  matches: MatchCardData[]
}

export interface LayoutRound {
  round: Round
  x: number
  positions: number[]
}

export interface BracketSection {
  id: 'qualy' | 'main'
  title: string
  subtitle: string
  rounds: Round[]
}
