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
    border: '#00ff88',
    glow: 'var(--glow-green-sm)',
    title: '#00ff88',
  },
  pink: {
    border: '#ff0055',
    glow: 'var(--glow-pink-sm)',
    title: '#ff0055',
  },
  yellow: {
    border: '#ffe600',
    glow: 'var(--glow-gold-sm)',
    title: '#ffe600',
  },
  cyan: {
    border: '#00e5ff',
    glow: 'var(--glow-cyan-sm)',
    title: '#00e5ff',
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
