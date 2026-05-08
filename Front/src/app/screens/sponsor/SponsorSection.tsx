import { DollarSign, Lock } from 'lucide-react'

import type { PatrocinioDisponivel } from '../../../types'
import { PatrocinioCard } from './PatrocinioCard'

interface SponsorSectionProps {
  titulo: string
  colorClass: string
  icon: 'money' | 'lock'
  itens: PatrocinioDisponivel[]
  assinando: string | null
  onAssinar: (id: string) => void
}

const ICONS = {
  money: DollarSign,
  lock: Lock,
}

export function SponsorSection({
  titulo,
  colorClass,
  icon,
  itens,
  assinando,
  onAssinar,
}: SponsorSectionProps) {
  if (itens.length === 0) {
    return null
  }

  const Icon = ICONS[icon]

  return (
    <section>
      <h2
        className={`text-[10px] mb-3 flex items-center gap-2 ${colorClass}`}
        style={{ fontFamily: 'var(--font-arcade)' }}
      >
        <Icon size={12} />
        {titulo} ({itens.length})
      </h2>
      <div className="space-y-3">
        {itens.map((patrocinio) => (
          <PatrocinioCard
            key={patrocinio.id}
            p={patrocinio}
            assinando={assinando}
            onAssinar={onAssinar}
          />
        ))}
      </div>
    </section>
  )
}
