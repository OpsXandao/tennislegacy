import type { PartidaScout } from '../../../../types'
import type { AdversarioInfo } from '../types'
import {
  calcularOverallCardMatch,
  getScoutingMetrics,
  resumoScouting,
} from '../scouting'
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
    <div>
      {scout?.is_rival && (
        <div
          className="flex items-center gap-2 px-3 py-2 mb-2"
          style={{
            background: 'rgba(255,46,99,0.08)',
            border: '1px solid rgba(255,46,99,0.35)',
          }}
        >
          <span style={{ color: '#ff2e63', fontFamily: 'var(--font-arcade)', fontSize: 9, letterSpacing: '0.2em' }}>
            ⚔ RIVAL
          </span>
        </div>
      )}
      <ScoutingReportCard
        titulo="Scouting Report"
        overall={scout?.overall ?? calcularOverallCardMatch(fallbackMetrics)}
        metrics={metrics}
        report={report}
        accent={accent}
      />
    </div>
  )
}
