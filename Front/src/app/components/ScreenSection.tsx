interface ScreenSectionProps {
  title: string
  subtitle?: string
  variant?: 'green' | 'pink' | 'yellow' | 'cyan'
  right?: React.ReactNode
  className?: string
  children: React.ReactNode
}

const SECTION_COLORS = {
  green: {
    border: 'var(--neon-green)',
    glow: 'var(--glow-green-sm)',
    title: 'var(--neon-green)',
  },
  pink: {
    border: 'var(--neon-pink)',
    glow: 'var(--glow-pink-sm)',
    title: 'var(--neon-pink)',
  },
  yellow: {
    border: 'var(--neon-yellow)',
    glow: 'var(--glow-gold-sm)',
    title: 'var(--neon-yellow)',
  },
  cyan: {
    border: 'var(--neon-cyan)',
    glow: 'var(--glow-cyan-sm)',
    title: 'var(--neon-cyan)',
  },
} as const

export function ScreenSection({
  title,
  subtitle,
  variant = 'green',
  right,
  className = '',
  children,
}: ScreenSectionProps) {
  const colors = SECTION_COLORS[variant]

  return (
    <section
      className={`border-2 app-panel-elevated p-4 ${className}`}
      style={{ borderColor: `${colors.border}99`, boxShadow: colors.glow }}
    >
      <div className="mb-4 flex items-start justify-between gap-4 border-b app-divider pb-3">
        <div className="min-w-0">
          <div className="pixel-font text-xs" style={{ color: colors.title }}>
            {title}
          </div>
          {subtitle && (
            <div className="app-muted mt-1 arcade-font text-[10px]">
              {subtitle}
            </div>
          )}
        </div>
        {right && <div className="shrink-0">{right}</div>}
      </div>
      {children}
    </section>
  )
}
