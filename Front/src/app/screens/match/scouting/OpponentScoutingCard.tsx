import type { PartidaScout } from '../../../../types'
import type { AdversarioInfo } from '../types'
import {
  calcularOverallCardMatch,
  getScoutingMetrics,
  resumoScouting,
} from '../model'
import { ScoutingReportCard } from './ScoutingReportCard'

interface OpponentScoutingCardProps {
  adv: AdversarioInfo
  scout: PartidaScout | null
  accent: string
  superficie: string
}

export function OpponentScoutingCard({
  adv,
  scout,
  accent,
  superficie,
}: OpponentScoutingCardProps) {
  const fallbackMetrics = getScoutingMetrics(adv)
  const fallbackReport = resumoScouting(adv, superficie)

  const metrics = scout?.metricas ?? {
    saque: fallbackMetrics.saque,
    fundo: fallbackMetrics.fundo,
    mental: fallbackMetrics.mental,
  }
  const report = scout
    ? {
        texto: scout.texto,
        dicas: scout.dicas,
        pontosFortes: scout.pontos_fortes,
        fraquezas: scout.fraquezas,
      }
    : fallbackReport

  return (
    <ScoutingReportCard
      titulo="Scouting Report"
      overall={scout?.overall ?? calcularOverallCardMatch(fallbackMetrics)}
      metrics={metrics}
      report={report}
      accent={accent}
    />
  )
}
