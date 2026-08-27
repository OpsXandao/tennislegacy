import type { Patrocinio } from '../../../types'
import { ActiveContractCard } from './ActiveContractCard'

interface ActiveSponsorListProps {
  ativos: Patrocinio[]
}

export function ActiveSponsorList({ ativos }: ActiveSponsorListProps) {
  if (ativos.length === 0) return null

  const totalSemanal = ativos.reduce((s, p) => s + p.valor, 0)
  const emRisco = ativos.filter(p => p.status === 'em_risco').length
  const sobPressao = ativos.filter(p => p.status === 'sob_pressao').length

  return (
    <section>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-[10px] text-neon-yellow flex items-center gap-2" style={{ fontFamily: 'var(--font-arcade)' }}>
          CONTRATOS ATIVOS ({ativos.length})
        </h2>
        <div className="flex items-center gap-3">
          {emRisco > 0 && (
            <span className="arcade-font text-[8px] text-neon-pink animate-pulse">
              ⚠ {emRisco} EM RISCO
            </span>
          )}
          {sobPressao > 0 && (
            <span className="arcade-font text-[8px] text-neon-yellow">
              {sobPressao} SOB PRESSÃO
            </span>
          )}
          <span className="arcade-font text-[9px] text-neon-green">
            R$ {totalSemanal.toLocaleString('pt-BR')}/sem
          </span>
        </div>
      </div>
      <div className="space-y-2">
        {ativos.map((patrocinio) => (
          <ActiveContractCard key={patrocinio.id} patrocinio={patrocinio} />
        ))}
      </div>
    </section>
  )
}
