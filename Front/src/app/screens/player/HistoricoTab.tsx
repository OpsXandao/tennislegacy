import type { MatchHistoryEntry } from '../../../types'

const FASE_LABEL: Record<string, string> = {
  campeao: 'CAMPEÃO', final: 'FINAL', semifinal: 'SEMIFINAL', semis: 'SEMIFINAL',
  quartas: 'QUARTAS', qf: 'QUARTAS', oitavas: 'OITAVAS', r16: 'OITAVAS',
  r32: 'R32', r64: 'R64', r128: 'R128', qualy_1: 'QUALY', qualy_2: 'QUALY',
}

function faseLabel(f: string) {
  return FASE_LABEL[f?.toLowerCase()] ?? f?.toUpperCase() ?? '?'
}

function foiVitoria(resultado: string | undefined) {
  const v = String(resultado || '').trim().toUpperCase()
  return v === 'V' || v === 'VITORIA' || v === 'VITÓRIA'
}

interface Props {
  historico: MatchHistoryEntry[]
}

export function HistoricoTab({ historico }: Props) {
  if (historico.length === 0) {
    return (
      <div className="text-center py-12 arcade-font text-[10px] text-[#444]">
        NENHUMA PARTIDA REGISTRADA
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {[...historico].reverse().map((h, i) => (
        <div
          key={i}
          className={`border-l-4 bg-[#111] px-3 py-3 ${foiVitoria(h.resultado) ? 'border-neon-green' : 'border-neon-pink'}`}
        >
          <div className="flex items-center justify-between gap-3 mb-1">
            <span className="arcade-font text-[11px] text-white truncate max-w-[220px]">{h.adversario}</span>
            <span className={`pixel-font text-[11px] font-bold ${foiVitoria(h.resultado) ? 'text-neon-green' : 'text-neon-pink'}`}>
              {foiVitoria(h.resultado) ? 'VIT' : 'DER'}
            </span>
          </div>
          <div className="flex items-center justify-between gap-3">
            <span className="arcade-font text-[10px] text-[#7a8c98]">{h.torneio} • {faseLabel(h.fase)}</span>
            <span className="arcade-font text-[10px] text-[#8f9aa3] text-right">{h.placar}</span>
          </div>
          <div className="arcade-font text-[9px] text-[#4a5a64] mt-1">SEM {h.semana} / {h.ano}</div>
        </div>
      ))}
    </div>
  )
}
