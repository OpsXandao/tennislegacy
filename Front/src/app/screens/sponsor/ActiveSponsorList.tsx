import { CheckCircle } from 'lucide-react'

import type { Patrocinio } from '../../../types'

interface ActiveSponsorListProps {
  ativos: Patrocinio[]
}

export function ActiveSponsorList({ ativos }: ActiveSponsorListProps) {
  if (ativos.length === 0) {
    return null
  }

  return (
    <section>
      <h2
        className="text-[10px] text-neon-yellow mb-3 flex items-center gap-2"
        style={{ fontFamily: 'var(--font-arcade)' }}
      >
        <CheckCircle size={12} />
        CONTRATOS ATIVOS ({ativos.length})
      </h2>
      <div className="space-y-2">
        {ativos.map((patrocinio) => (
          <div
            key={patrocinio.id}
            className="border border-neon-yellow/40 bg-neon-yellow/5 p-3 flex items-center justify-between gap-3"
          >
            <div className="min-w-0">
              <p
                className="text-[10px] text-neon-yellow"
                style={{ fontFamily: 'var(--font-arcade)' }}
              >
                {patrocinio.nome}
              </p>
              <p className="text-[9px] text-white/50 mt-0.5 uppercase">
                {patrocinio.categoria} • {patrocinio.nivel}
              </p>
              <p className="text-[9px] text-neon-yellow/50 mt-0.5">
                {patrocinio.semanas_restantes} semanas restantes
              </p>
            </div>
            <div className="text-right shrink-0">
              <p className="text-[10px] text-neon-green">
                R$ {patrocinio.valor.toLocaleString('pt-BR')}
              </p>
              <p className="text-[9px] text-white/40">/semana</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
