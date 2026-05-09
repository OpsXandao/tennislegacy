interface ScoutingReportViewModel {
  texto: string
  dicas: string[]
  pontosFortes: string[]
  fraquezas: string[]
}

interface ScoutingReportCardProps {
  titulo: string
  overall: number | null | undefined
  metrics: { saque: number; fundo: number; mental: number }
  report: ScoutingReportViewModel
  accent: string
}

export function ScoutingReportCard({
  titulo,
  overall,
  metrics,
  report,
  accent,
}: ScoutingReportCardProps) {
  const stats = [
    { label: 'Saque', val: metrics.saque },
    { label: 'Fundo', val: metrics.fundo },
    { label: 'Mental', val: metrics.mental },
  ]

  return (
    <div
      className="space-y-4 border p-4"
      style={{ borderColor: `${accent}40`, background: `${accent}0a` }}
    >
      <div
        className="flex items-center justify-between border-b pb-2"
        style={{ borderColor: `${accent}20` }}
      >
        <div
          className="arcade-font text-[11px] tracking-widest uppercase"
          style={{ color: accent }}
        >
          {titulo}
        </div>
        <div className="pixel-font text-[14px] text-white">
          OVR {overall ?? '??'}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="border bg-black/40 p-1.5 text-center"
            style={{ borderColor: `${accent}20` }}
          >
            <div className="arcade-font mb-1 text-[9px] text-[#888]">
              {stat.label.toUpperCase()}
            </div>
            <div
              className="pixel-font text-[15px]"
              style={{
                color:
                  stat.val > 80 ? 'var(--neon-green)' : stat.val > 65 ? 'var(--neon-yellow)' : '#ff4466',
              }}
            >
              {stat.val}
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-3">
        <div className="flex flex-wrap gap-1.5">
          {report.pontosFortes.map((tag) => (
            <span
              key={tag}
              className="arcade-font border border-neon-green/20 bg-neon-green/10 px-1.5 py-0.5 text-[7px] text-neon-green"
            >
              {tag}
            </span>
          ))}
          {report.fraquezas.map((tag) => (
            <span
              key={tag}
              className="arcade-font border border-[#ff4466]/20 bg-[#ff4466]/10 px-1.5 py-0.5 text-[7px] text-[#ff4466]"
            >
              {tag}
            </span>
          ))}
        </div>

        <div className="space-y-2">
          <div className="arcade-font text-[10px] leading-relaxed text-white/80">
            {report.texto}
          </div>
          {report.dicas.length > 0 && (
            <div className="space-y-1 border-l-2 border-neon-yellow bg-neon-yellow/5 p-2">
              <div className="arcade-font text-[8px] tracking-widest text-neon-yellow">
                DICA TÁTICA
              </div>
              {report.dicas.map((dica, idx) => (
                <div
                  key={`${idx}-${dica}`}
                  className="arcade-font text-[9px] leading-snug text-[#d6f2ff]"
                >
                  • {dica}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
