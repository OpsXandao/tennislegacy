import { Trophy, X } from 'lucide-react'
import { motion, AnimatePresence } from 'motion/react'
import { NeonButton } from '../../../components/NeonButton'
import type { CalendarChampionsModalProps } from '../types'

export function CalendarChampionsModal({
  campeoesSemana,
  onClose,
}: CalendarChampionsModalProps) {
  return (
    <AnimatePresence>
      {campeoesSemana.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.9, y: 20, opacity: 0 }}
            animate={{ scale: 1, y: 0, opacity: 1 }}
            exit={{ scale: 0.9, y: 20, opacity: 0 }}
            className="app-panel relative w-full max-w-md border-2 border-[#ffe600] shadow-[0_0_30px_rgba(255,230,0,0.3)]"
          >
            <div className="flex items-center justify-between border-b border-[#ffe600]/30 px-4 py-3">
              <div className="flex items-center gap-2">
                <Trophy size={16} className="text-[#ffe600]" />
                <span className="pixel-font text-sm text-[#ffe600]">CAMPEÕES DA SEMANA</span>
              </div>
              <button onClick={onClose} className="text-[#ffe600] hover:scale-110 transition-transform">
                <X size={20} />
              </button>
            </div>

            <div className="max-h-[60vh] overflow-y-auto p-4 space-y-2 [scrollbar-width:thin]">
              {['ATP', 'WTA'].map((tour) => {
                const lista = campeoesSemana.filter((campeao) => campeao.tour === tour)
                if (lista.length === 0) return null

                return (
                  <div key={tour}>
                    <div className="arcade-font text-[9px] text-[#888] mb-2 tracking-widest">{tour}</div>
                    {lista.map((campeao) => (
                      <div key={campeao.torneio} className="mb-2 border border-[#333] bg-[#111] p-3">
                        <div className="arcade-font text-[8px] text-[#888] truncate mb-1">
                          {campeao.torneio.toUpperCase()}
                        </div>
                        <div className="flex items-center gap-1">
                          <Trophy size={10} className="text-[#ffe600] shrink-0" />
                          <span className="arcade-font text-[11px] text-white font-bold truncate">
                            {campeao.simples.toUpperCase()}
                          </span>
                        </div>
                        {campeao.duplas && (
                          <div className="mt-1 arcade-font text-[9px] text-[#00e5ff] truncate">
                            DUPLAS: {campeao.duplas.toUpperCase()}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )
              })}
            </div>

            <div className="p-4 border-t border-[#ffe600]/30">
              <NeonButton variant="yellow" className="w-full" onClick={onClose}>
                AVANÇAR SEMANA
              </NeonButton>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
