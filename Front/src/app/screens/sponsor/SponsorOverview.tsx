import { Trophy, Users, BriefcaseBusiness, Crown, TrendingUp } from 'lucide-react'
import type { PatrocinioContexto, Patrocinio } from '../../../types'

interface SponsorOverviewProps {
  contexto: PatrocinioContexto
  ativos: Patrocinio[]
}

function saúdeMedia(ativos: Patrocinio[]): { label: string; color: string } {
  if (ativos.length === 0) return { label: '—', color: '#555' }
  const avg = ativos.reduce((s, p) => s + p.confianca, 0) / ativos.length
  if (avg >= 70) return { label: `${Math.round(avg)}% BOA`, color: 'var(--neon-green)' }
  if (avg >= 40) return { label: `${Math.round(avg)}% FRACA`, color: 'var(--neon-yellow)' }
  return { label: `${Math.round(avg)}% CRÍTICA`, color: 'var(--neon-pink)' }
}

export function SponsorOverview({ contexto, ativos }: SponsorOverviewProps) {
  const totalSemanal = ativos.reduce((s, p) => s + p.valor, 0)
  const saude = saúdeMedia(ativos)

  const CARDS = [
    {
      key: 'ranking',
      label: 'RANKING',
      color: 'var(--neon-yellow)',
      icon: Trophy,
      value: contexto.ranking_atual > 0 ? `#${contexto.ranking_atual}` : 'N/A',
    },
    {
      key: 'seguidores',
      label: 'SEGUIDORES',
      color: 'var(--neon-cyan)',
      icon: Users,
      value: contexto.seguidores_atuais.toLocaleString('pt-BR'),
    },
    {
      key: 'receita',
      label: 'RECEITA/SEM',
      color: 'var(--neon-green)',
      icon: TrendingUp,
      value: ativos.length > 0 ? `R$ ${totalSemanal.toLocaleString('pt-BR')}` : '—',
    },
    {
      key: 'saude',
      label: 'CONFIANÇA',
      color: saude.color,
      icon: BriefcaseBusiness,
      value: saude.label,
    },
    {
      key: 'slots',
      label: 'SLOTS MENORES',
      color: '#ff9f1c',
      icon: Crown,
      value: String(contexto.slots_menores_restantes),
    },
    {
      key: 'master',
      label: 'MASTER',
      color: '#ff9f1c',
      icon: Crown,
      value: contexto.slot_master_disponivel ? 'LIVRE' : 'OCUPADO',
    },
  ]

  return (
    <section className="grid grid-cols-3 gap-2">
      {CARDS.map(({ key, label, color, icon: Icon, value }) => (
        <div
          key={key}
          className="border p-2.5"
          style={{ borderColor: `${color}55`, background: `${color}0d` }}
        >
          <div
            className="flex items-center gap-1 text-[7px] mb-1"
            style={{ fontFamily: 'var(--font-arcade)', color }}
          >
            <Icon size={9} />
            <span>{label}</span>
          </div>
          <p className="text-[10px] text-white" style={{ fontFamily: 'var(--font-arcade)', color: key === 'saude' ? color : undefined }}>
            {value}
          </p>
        </div>
      ))}
    </section>
  )
}
