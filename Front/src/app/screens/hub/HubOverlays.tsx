import { motion, AnimatePresence } from 'motion/react'
import { useNavigate } from 'react-router'
import { ChevronRight } from 'lucide-react'
import type { TorneioState } from '../../types'

export function AutoSavePromptModal({ onConfirm }: { onConfirm: (ativo: boolean) => void }) {
  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/82 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md border-2 border-neon-green bg-[#06110c] p-5 shadow-[0_0_24px_rgba(0,255,136,0.18)]">
        <div className="arcade-font text-[10px] tracking-[0.2em] text-neon-green">SALVAMENTO AUTOMÁTICO</div>
        <div className="pixel-font mt-3 text-lg text-white">Deseja ativar o salvamento automático?</div>
        <div className="arcade-font mt-3 text-[11px] leading-relaxed text-[#9bc7af]">
          Essa configuração é definida no hub e usada quando uma nova partida começar.
        </div>
        <div className="mt-5 grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => onConfirm(false)}
            className="min-h-[44px] border-2 border-neon-pink px-4 py-3 arcade-font text-[10px] text-[#ff7d9e]"
          >
            NÃO
          </button>
          <button
            type="button"
            onClick={() => onConfirm(true)}
            className="min-h-[44px] border-2 border-neon-green px-4 py-3 arcade-font text-[10px] text-neon-green"
          >
            SIM
          </button>
        </div>
      </div>
    </div>
  )
}

export function MilestoneOverlay({ marco }: { marco: { titulo: string; texto: string } | null }) {
  return (
    <AnimatePresence>
      {marco && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ type: 'spring', stiffness: 300, damping: 22 }}
          className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none"
        >
          <div
            className="mx-6 border-2 border-neon-yellow p-6 text-center"
            style={{ background: '#0c0900', boxShadow: '0 0 48px rgba(255,230,0,0.4)' }}
          >
            <div className="pixel-font text-xl text-neon-yellow mb-2" style={{ textShadow: '0 0 14px var(--neon-yellow)' }}>
              {marco.titulo}
            </div>
            <div className="arcade-font text-[10px] text-[#c8b86a] leading-relaxed">
              {marco.texto}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export function ActiveTournamentBanner({ torneio }: { torneio: TorneioState }) {
  const navigate = useNavigate()
  return (
    <motion.button
      initial={{ opacity: 0 }}
      animate={{
        opacity: 1,
        boxShadow: [
          '0 0 16px rgba(255,230,0,0.2)',
          '0 0 32px rgba(255,230,0,0.45)',
          '0 0 16px rgba(255,230,0,0.2)',
        ],
      }}
      transition={{ opacity: { duration: 0.3 }, boxShadow: { duration: 2, repeat: Infinity, ease: 'easeInOut' } }}
      exit={{ opacity: 0 }}
      onClick={() => navigate(torneio.davis ? '/davis' : '/tournament')}
      className="mx-4 mt-3 w-[calc(100%-2rem)] flex items-center justify-between p-3 border-2 border-neon-yellow bg-black text-left active:scale-[0.98] transition-transform"
    >
      <div>
        <div className="text-[8px] text-neon-yellow animate-pulse mb-1" style={{ fontFamily: 'var(--font-pixel)' }}>
          &gt; {torneio.davis ? 'CONFRONTO NACIONAL' : 'TORNEIO EM CURSO'}
        </div>
        <div className="text-[12px] text-white" style={{ fontFamily: 'var(--font-pixel)' }}>{torneio.nome}</div>
        <div className="text-[9px] text-[#666] mt-0.5" style={{ fontFamily: 'var(--font-arcade)' }}>
          {torneio.fase_atual?.toUpperCase()}
        </div>
      </div>
      <div
        className="flex items-center gap-1 border-2 border-neon-yellow px-3 py-1.5 text-[9px] shrink-0 ml-2 text-neon-yellow"
        style={{ fontFamily: 'var(--font-pixel)' }}
      >
        PLAY <ChevronRight size={10} />
      </div>
    </motion.button>
  )
}
