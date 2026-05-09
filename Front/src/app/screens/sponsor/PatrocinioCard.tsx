import { motion } from 'motion/react'
import type { PatrocinioDisponivel } from '../../../types'

const NIVEL_COLOR: Record<string, string> = {
  bronze: '#cd7f32',
  silver: '#c0c0c0',
  prata: '#c0c0c0',
  gold: 'var(--neon-yellow)',
  ouro: 'var(--neon-yellow)',
  platinum: 'var(--neon-cyan)',
  platina: 'var(--neon-cyan)',
  diamond: 'var(--neon-pink)',
  diamante: 'var(--neon-pink)',
}

function nivelColor(nivel: string) {
  return NIVEL_COLOR[nivel?.toLowerCase()] ?? '#aaaaaa'
}

interface PatrocinioCardProps {
  p: PatrocinioDisponivel
  assinando: string | null
  onAssinar: (id: string) => void
}

export function PatrocinioCard({
  p,
  assinando,
  onAssinar,
}: PatrocinioCardProps) {
  const cor = nivelColor(p.nivel)
  const loading = assinando === p.id

  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      className={`border p-3 ${
        p.elegivel
          ? 'border-neon-yellow/50 bg-neon-yellow/5'
          : 'border-white/10 bg-white/2 opacity-60'
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className="text-[10px]"
              style={{ fontFamily: 'var(--font-arcade)', color: cor }}
            >
              {p.nome}
            </span>
            <span
              className="text-[8px] px-1.5 py-0.5 border uppercase"
              style={{
                fontFamily: 'var(--font-arcade)',
                color: cor,
                borderColor: cor + '60',
                background: cor + '15',
              }}
            >
              {p.nivel}
            </span>
          </div>

          {p.descricao && (
            <p className="text-[9px] text-white/50 mt-1 leading-relaxed">{p.descricao}</p>
          )}

          <div className="flex flex-wrap gap-x-4 gap-y-0.5 mt-1.5">
            <span className="text-[9px] text-neon-green">
              R$ {p.valor_semanal?.toLocaleString('pt-BR')}/sem
            </span>
            <span className="text-[9px] text-white/50 uppercase">{p.categoria}</span>
            {p.requisito_ranking > 0 && (
              <span className="text-[9px] text-white/40">
                Req: top {p.requisito_ranking}
              </span>
            )}
            {p.requisito_seguidores > 0 && (
              <span className="text-[9px] text-white/40">
                Seg: {p.requisito_seguidores.toLocaleString('pt-BR')}
              </span>
            )}
            {p.bonus_assinatura > 0 && (
              <span className="text-[9px] text-neon-yellow/70">
                Bônus: R$ {p.bonus_assinatura.toLocaleString('pt-BR')}
              </span>
            )}
          </div>

          {!p.elegivel && p.motivo_bloqueio && (
            <p className="text-[9px] text-neon-pink/70 mt-1">Bloqueio: {p.motivo_bloqueio}</p>
          )}
        </div>

        {p.elegivel && (
          <button
            onClick={() => onAssinar(p.id)}
            disabled={!!assinando}
            className="shrink-0 border border-neon-yellow px-3 py-1.5 text-[8px] text-neon-yellow hover:bg-neon-yellow/20 disabled:opacity-40 transition-colors"
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            {loading ? '...' : 'ASSINAR'}
          </button>
        )}
      </div>
    </motion.div>
  )
}
