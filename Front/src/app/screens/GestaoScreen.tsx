import { useNavigate } from 'react-router'
import {
  Dumbbell, ShoppingBag, Star, Newspaper,
  Smile, Users, Globe, Award, TrendingUp, Flag
} from 'lucide-react'
import { PageHeader } from '../components'

const SECTIONS = [
  { icon: Dumbbell,    label: 'TREINO',         sub: 'Atributos & Físico',   route: '/training',       color: 'var(--neon-green)'  },
  { icon: ShoppingBag, label: 'MERCADO',         sub: 'Staff & Equipamentos', route: '/market',         color: 'var(--neon-pink)'   },
  { icon: Star,        label: 'PATROCÍNIOS',     sub: 'Contratos & Metas',    route: '/patrocinios',    color: 'var(--neon-yellow)' },
  { icon: Newspaper,   label: 'IMPRENSA',        sub: 'Entrevistas & Rep.',   route: '/imprensa',       color: 'var(--neon-purple)' },
  { icon: Smile,       label: 'LIFESTYLE',       sub: 'Vida fora da quadra',  route: '/lifestyle',      color: 'var(--neon-cyan)'   },
  { icon: Users,       label: 'DUPLAS',          sub: 'Parceiros & Sinergia', route: '/duplas',         color: 'var(--neon-cyan)'   },
  { icon: Flag,        label: 'DAVIS CUP',       sub: 'Copa das Nações',      route: '/davis',          color: 'var(--neon-yellow)' },
  { icon: Globe,       label: 'MUNDO',           sub: 'Circuito Global',      route: '/world',          color: 'var(--neon-green)'  },
  { icon: Award,       label: 'PROGRESSÃO',      sub: 'Skill Points',         route: '/progression',    color: 'var(--neon-cyan)'   },
  { icon: TrendingUp,  label: 'RANKING NAÇÕES',  sub: 'Copa Davis Ranking',   route: '/ranking-nacoes', color: 'var(--neon-yellow)' },
]

export function GestaoScreen() {
  const navigate = useNavigate()
  return (
    <div className="app-shell min-h-screen pb-28">
      <PageHeader title="GESTÃO" subtitle="CARREIRA & EQUIPE" color="cyan" backTo="/hub" />
      <div className="p-4 grid grid-cols-2 gap-3">
        {SECTIONS.map(s => (
          <button
            key={s.route}
            onClick={() => navigate(s.route)}
            className="border-2 p-4 flex flex-col gap-2 text-left transition-all active:scale-95"
            style={{
              borderColor: `${s.color}44`,
              background: `${s.color}08`,
            }}
          >
            <s.icon size={22} style={{ color: s.color }} />
            <div>
              <div className="arcade-font text-ui-label" style={{ color: s.color }}>{s.label}</div>
              <div className="arcade-font text-ui-tag text-[#6e8fa5] mt-0.5">{s.sub}</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
