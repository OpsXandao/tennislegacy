import { Trophy, Users, BriefcaseBusiness, Crown } from 'lucide-react'

import type { PatrocinioContexto } from '../../../types'

interface SponsorOverviewProps {
  contexto: PatrocinioContexto
}

const CARDS = [
  {
    key: 'ranking',
    label: 'RANKING',
    color: '#ffe600',
    icon: Trophy,
    getValue: (contexto: PatrocinioContexto) =>
      contexto.ranking_atual > 0 ? `#${contexto.ranking_atual}` : 'N/A',
  },
  {
    key: 'seguidores',
    label: 'SEGUIDORES',
    color: '#00e5ff',
    icon: Users,
    getValue: (contexto: PatrocinioContexto) =>
      contexto.seguidores_atuais.toLocaleString('pt-BR'),
  },
  {
    key: 'menores',
    label: 'SLOTS MENORES',
    color: '#00ff88',
    icon: BriefcaseBusiness,
    getValue: (contexto: PatrocinioContexto) =>
      String(contexto.slots_menores_restantes),
  },
  {
    key: 'master',
    label: 'MASTER',
    color: '#ff9f1c',
    icon: Crown,
    getValue: (contexto: PatrocinioContexto) =>
      contexto.slot_master_disponivel ? 'LIVRE' : 'OCUPADO',
  },
] as const

export function SponsorOverview({ contexto }: SponsorOverviewProps) {
  return (
    <section className="grid grid-cols-2 gap-2">
      {CARDS.map(({ key, label, color, icon: Icon, getValue }) => (
        <div
          key={key}
          className="border p-3"
          style={{
            borderColor: `${color}55`,
            background: `${color}0d`,
          }}
        >
          <div
            className="flex items-center gap-1.5 text-[8px]"
            style={{ fontFamily: 'var(--font-arcade)', color }}
          >
            <Icon size={10} />
            <span>{label}</span>
          </div>
          <p
            className="mt-1 text-[11px] text-white"
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            {getValue(contexto)}
          </p>
        </div>
      ))}
    </section>
  )
}
