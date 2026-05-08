import type { AdversarioInfo, Faixa, Alvo, GameResult, PlanoValor, MentalidadeValor, AbordagemValor, InstrucaoValor, SegundoSaqueModo, ModoAcomp, VelocidadeRapida, Fase } from '../screens/match/types'
import type { MatchStrategySummary, PlacarState } from './index'

export interface MatchState {
  fase: Fase
  placar: PlacarState
  simulando: boolean
  simulacaoPausada: boolean
  velocidadeRapida: VelocidadeRapida
  ajustandoPlanoRapido: boolean
  mentalidade: MentalidadeValor
  abordagem: AbordagemValor
  instrucao: InstrucaoValor
  plano: PlanoValor
  modo: ModoAcomp
  segundoSaque: SegundoSaqueModo
  adversario: AdversarioInfo
  energiaJogadorAoVivo: number
  fadigaJogadorAoVivo: number
  energiaAdversarioAoVivo: number
  fadigaAdversarioAoVivo: number
  estrategiaJogadorAoVivo: MatchStrategySummary
  estrategiaAdversarioAoVivo: MatchStrategySummary
  partidaId: string | null
  superficie: string
  faseTorneio: string
  log: string[]
  erroEntrada: string
}
