import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router'
import { CalendarDays, TrendingUp, Home, User, Dumbbell } from 'lucide-react'
import { useTheme } from '../hooks/useTheme'

function NavBtn({
  item,
  active,
  onClick,
}: {
  item: { icon: React.ElementType; label: string; route: string }
  active: boolean
  onClick: () => void
}) {
  const [hovered, setHovered] = useState(false)
  const lit = active || hovered
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="flex flex-col items-center gap-1.5 px-3 py-1 min-w-[52px] transition-colors"
      style={{ background: hovered && !active ? 'color-mix(in srgb, var(--neon-green) 6%, transparent)' : 'transparent' }}
      aria-label={item.label}
    >
      <item.icon
        size={19}
        style={{ color: lit ? 'var(--neon-green)' : 'var(--text-secondary)', transition: 'color 0.12s' }}
      />
      <span
        className="text-[8px]"
        style={{
          fontFamily: 'var(--font-pixel)',
          color: lit ? 'var(--neon-green)' : 'var(--text-secondary)',
          transition: 'color 0.12s',
        }}
      >
        {item.label}
      </span>
      <div
        className="h-[2px] transition-all duration-150"
        style={{
          width: active ? '100%' : hovered ? '60%' : '0%',
          background: 'var(--neon-green)',
          opacity: active ? 1 : 0.5,
          boxShadow: active ? 'var(--glow-green-sm)' : 'none',
        }}
      />
    </button>
  )
}

const NAV = [
  { icon: CalendarDays, label: 'TEMPORADA', route: '/calendar'  },
  { icon: TrendingUp,   label: 'RANKING',   route: '/rankings'  },
  { icon: Home,         label: 'HUB',       route: '/hub', main: true },
  { icon: User,         label: 'JOGADOR',   route: '/player'   },
  { icon: Dumbbell,     label: 'TREINAR',   route: '/training'  },
]

export function BottomNav() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const [hoverMain, setHoverMain] = useState(false)
  const { isLight } = useTheme()

  return (
    <div
      className="app-panel fixed bottom-0 left-0 right-0 z-30 border-t-2"
      style={{
        borderColor: 'var(--neon-green)',
        boxShadow: '0 -4px 24px color-mix(in srgb, var(--neon-green) 15%, transparent)',
      }}
    >
      {/* scanline — apenas modo escuro */}
      {!isLight && (
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.2) 0px, rgba(0,0,0,0.2) 1px, transparent 1px, transparent 2px)',
          }}
        />
      )}
      <div className="relative flex items-end justify-around px-2 pt-2 pb-4">
        {NAV.map((item) => {
          const active = pathname === item.route

          if (item.main) {
            return (
              <button
                key={item.route}
                onClick={() => navigate(item.route)}
                onMouseEnter={() => setHoverMain(true)}
                onMouseLeave={() => setHoverMain(false)}
                className="relative -translate-y-3 flex flex-col items-center"
                aria-label="HUB"
              >
                <div
                  className="w-14 h-14 flex items-center justify-center border-2 transition-all"
                  style={{
                    borderColor: 'var(--neon-green)',
                    background: active
                      ? 'var(--neon-green)'
                      : hoverMain
                        ? 'color-mix(in srgb, var(--neon-green) 14%, var(--surface-card))'
                        : 'var(--surface-card)',
                    boxShadow: active
                      ? `0 0 0 2px var(--bg-dark), var(--glow-green)`
                      : hoverMain
                        ? `0 0 0 2px var(--bg-dark), var(--glow-green-sm)`
                        : `0 0 0 2px var(--bg-dark)`,
                  }}
                >
                  <item.icon
                    size={22}
                    style={{ color: active ? 'var(--bg-dark)' : 'var(--neon-green)' }}
                  />
                </div>
                {active && (
                  <div
                    className="mt-1 w-2 h-2"
                    style={{ background: 'var(--neon-green)', boxShadow: 'var(--glow-green-sm)' }}
                  />
                )}
              </button>
            )
          }

          return (
            <NavBtn key={item.route} item={item} active={active} onClick={() => navigate(item.route)} />
          )
        })}
      </div>
    </div>
  )
}
