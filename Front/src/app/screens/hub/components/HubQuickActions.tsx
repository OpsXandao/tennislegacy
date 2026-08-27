import { useState } from 'react'
import {
  CalendarDays, ShoppingBag, Users, Shield, History, Globe, Mic, Crown,
} from 'lucide-react'

export const QUICK = [
  { icon: CalendarDays, label: 'JOGAR',    route: '/calendar',  color: 'var(--neon-green)',  rgb: 'var(--neon-green-rgb)' },
  { icon: ShoppingBag,  label: 'MERCADO',  route: '/market',    color: 'var(--neon-pink)',   rgb: 'var(--neon-pink-rgb)' },
  { icon: Users,        label: 'DUPLAS',   route: '/duplas',    color: 'var(--neon-cyan)',   rgb: 'var(--neon-cyan-rgb)' },
  { icon: Shield,       label: 'DAVIS',    route: '/davis',     color: 'var(--neon-yellow)', rgb: 'var(--neon-yellow-rgb)' },
  { icon: History,      label: 'HISTORICO',route: '/history',   color: 'var(--neon-yellow)', rgb: 'var(--neon-yellow-rgb)' },
  { icon: Globe,        label: 'MUNDO',    route: '/world',     color: 'var(--neon-yellow)', rgb: 'var(--neon-yellow-rgb)' },
  { icon: Mic,          label: 'IMPRENSA', route: '/imprensa',  color: 'var(--neon-purple)', rgb: 'var(--neon-purple-rgb)' },
  { icon: Crown,        label: 'LIFESTYLE',route: '/lifestyle', color: '#ffb7c6',            rgb: '255,183,198' },
]

function QuickBtn({ item, onClick }: { item: typeof QUICK[number]; onClick: () => void }) {
  const [hovered, setHovered] = useState(false)
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="flex items-center gap-2 p-3 border-2 active:scale-95 transition-all text-left"
      style={{
        borderColor: hovered ? item.color : `rgba(${item.rgb},0.20)`,
        background: hovered ? `rgba(${item.rgb},0.05)` : 'var(--card)',
        boxShadow: hovered ? `0 0 10px rgba(${item.rgb},0.27)` : 'none',
        transition: 'border-color 0.15s, background 0.15s, box-shadow 0.15s',
      }}
    >
      <item.icon size={15} style={{ color: item.color, flexShrink: 0 }} />
      <span
        className="text-[9px] truncate"
        style={{ fontFamily: 'var(--font-pixel)', color: hovered ? item.color : '#444' }}
      >
        {item.label}
      </span>
    </button>
  )
}

interface HubQuickActionsProps {
  onNavigate: (route: string) => void
}

export function HubQuickActions({ onNavigate }: HubQuickActionsProps) {
  return (
    <div className="grid grid-cols-3 gap-2">
      {QUICK.map((item) => (
        <QuickBtn key={item.route} item={item} onClick={() => onNavigate(item.route)} />
      ))}
    </div>
  )
}
