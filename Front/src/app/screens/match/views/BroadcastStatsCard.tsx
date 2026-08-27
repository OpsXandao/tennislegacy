import type { MatchStatsSummary } from '../../../../types'

interface BroadcastStatsCardProps {
  nomeJogador: string
  nomeAdversario: string
  rankingJogador?: number | null
  rankingAdversario?: number | null
  statsJ: MatchStatsSummary
  statsA: MatchStatsSummary
  setAtual?: number
}

function parsePct(val: string | number | undefined): number {
  if (typeof val === 'number') return val
  if (!val) return 0
  return parseFloat(String(val).replace('%', '')) || 0
}

function breakPct(val: string | undefined): number {
  if (!val) return 0
  const [won, total] = val.split('/').map(Number)
  return total > 0 ? (won / total) * 100 : 0
}

function StatRow({
  label,
  valueJ,
  valueA,
  pctJ,
  pctA,
}: {
  label: string
  valueJ: string | number
  valueA: string | number
  pctJ: number
  pctA: number
}) {
  const total = pctJ + pctA
  const wJ = total > 0 ? Math.round((pctJ / total) * 100) : 50
  const wA = 100 - wJ

  return (
    <div className="grid grid-cols-[40px_1fr_90px_1fr_40px] items-center gap-1 py-[5px] border-b border-white/[0.04]">
      <span className="arcade-font text-[10px] text-white text-right pr-1">{valueJ}</span>

      <div className="flex justify-end">
        <div
          className="h-[2px] rounded-full transition-all duration-700"
          style={{
            width: `${wJ}%`,
            background: 'linear-gradient(to left, rgba(0,255,136,0.7), rgba(0,255,136,0.1))',
          }}
        />
      </div>

      <span className="arcade-font text-[6px] text-[#4a6070] tracking-widest uppercase text-center leading-tight">
        {label}
      </span>

      <div className="flex justify-start">
        <div
          className="h-[2px] rounded-full transition-all duration-700"
          style={{
            width: `${wA}%`,
            background: 'linear-gradient(to right, rgba(255,100,80,0.7), rgba(255,100,80,0.1))',
          }}
        />
      </div>

      <span className="arcade-font text-[10px] text-[#ff8d6d] text-left pl-1">{valueA}</span>
    </div>
  )
}

export function BroadcastStatsCard({
  nomeJogador,
  nomeAdversario,
  rankingJogador,
  rankingAdversario,
  statsJ,
  statsA,
  setAtual = 1,
}: BroadcastStatsCardProps) {
  const nomeJ = nomeJogador.toUpperCase()
  const nomeA = nomeAdversario.toUpperCase()

  const rows = [
    {
      label: 'ACES',
      valueJ: statsJ.aces,
      valueA: statsA.aces,
      pctJ: statsJ.aces,
      pctA: statsA.aces,
    },
    {
      label: '1ST SERVE %',
      valueJ: statsJ.primeiro_saque_pct,
      valueA: statsA.primeiro_saque_pct,
      pctJ: parsePct(statsJ.primeiro_saque_pct),
      pctA: parsePct(statsA.primeiro_saque_pct),
    },
    {
      label: '1ST SERVE PTS WON',
      valueJ: statsJ.pontos_saque_pct,
      valueA: statsA.pontos_saque_pct,
      pctJ: parsePct(statsJ.pontos_saque_pct),
      pctA: parsePct(statsA.pontos_saque_pct),
    },
    {
      label: 'WINNERS',
      valueJ: statsJ.winners,
      valueA: statsA.winners,
      pctJ: statsJ.winners,
      pctA: statsA.winners,
    },
    {
      label: 'UNFORCED ERRORS',
      valueJ: statsJ.erros_nao_forcados,
      valueA: statsA.erros_nao_forcados,
      // inverted: fewer is better, so the bar favors the smaller value
      pctJ: statsA.erros_nao_forcados,
      pctA: statsJ.erros_nao_forcados,
    },
    {
      label: 'BREAK POINTS WON',
      valueJ: statsJ.break_points ?? '0/0',
      valueA: statsA.break_points ?? '0/0',
      pctJ: breakPct(statsJ.break_points),
      pctA: breakPct(statsA.break_points),
    },
  ]

  return (
    <div
      className="overflow-hidden"
      style={{ background: '#04090e', border: '1px solid rgba(0,180,220,0.10)' }}
    >
      {/* Top cyan line */}
      <div
        className="h-px w-full"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(0,200,255,0.5) 40%, rgba(0,200,255,0.5) 60%, transparent 100%)',
        }}
      />

      {/* Player header */}
      <div className="grid grid-cols-[1fr_auto_1fr] items-end px-3 pt-2 pb-1.5 gap-2">
        <div>
          <div className="arcade-font text-[9px] text-white leading-tight truncate">{nomeJ}</div>
          {rankingJogador != null && (
            <div className="arcade-font text-[6px] text-[#33555e] mt-0.5">#{rankingJogador}</div>
          )}
        </div>

        <div className="arcade-font text-[6px] text-[#2a4050] tracking-[0.18em] text-center whitespace-nowrap">
          SET {setAtual} STATISTICS
        </div>

        <div className="text-right">
          <div className="arcade-font text-[9px] text-[#ff8d6d] leading-tight truncate">{nomeA}</div>
          {rankingAdversario != null && (
            <div className="arcade-font text-[6px] text-[#33555e] mt-0.5">#{rankingAdversario}</div>
          )}
        </div>
      </div>

      {/* Separator */}
      <div className="mx-3 h-px" style={{ background: 'rgba(0,180,220,0.10)' }} />

      {/* Stat rows */}
      <div className="px-3 py-1">
        {rows.map((row) => (
          <StatRow key={row.label} {...row} />
        ))}
      </div>

      {/* Bottom cyan line */}
      <div
        className="h-px w-full"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, rgba(0,200,255,0.5) 40%, rgba(0,200,255,0.5) 60%, transparent 100%)',
        }}
      />
    </div>
  )
}
