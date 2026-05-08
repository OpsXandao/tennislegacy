import type { CampeaoSemana, TorneioCalendario } from '../../../types'

export type TierVisual = 'grandslam' | 'masters' | 'atp500' | 'atp250'

export interface CalendarCallup {
  convocado: boolean
  mensagem: string
  torneio?: TorneioCalendario
}

export interface CalendarTournamentGridProps {
  loading: boolean
  semanaAtual: number
  semanaSelecionada: number
  torneiosSemana: TorneioCalendario[]
  convocacao: CalendarCallup | null
  inscrevendo: boolean
  erroInscricao: string
  onSelectTournament: (torneio: TorneioCalendario) => void
  onConfirmCallup: () => void
  onDeclineCallup: () => void
}

export interface CalendarChampionsModalProps {
  campeoesSemana: CampeaoSemana[]
  onClose: () => void
}
