import { motion } from 'motion/react'
import { Trophy, Zap, Users } from 'lucide-react'
import { PixelFlag } from '../../../components'

interface HypeViewProps {
  torneio: string
  fase: string
  superficie: string
  jogador: { nome: string; nacionalidade: string; ranking: number | string; overall: number }
  adversario: { nome: string; nacionalidade: string | null; ranking: number | string; overall: number | null }
  themeClass: string
  onContinue: () => void
}

export function HypeView({
  torneio,
  fase,
  superficie,
  jogador,
  adversario,
  themeClass,
  onContinue
}: HypeViewProps) {
  return (
    <div className={`app-shell match-theme-screen ${themeClass} min-h-screen flex flex-col items-center justify-center p-6 text-white overflow-hidden`}>
      {/* Background Decor */}
      <motion.div 
        initial={{ opacity: 0, scale: 1.2 }}
        animate={{ opacity: 0.1, scale: 1 }}
        className="absolute inset-0 flex items-center justify-center pointer-events-none"
      >
        <Trophy size={400} />
      </motion.div>

      {/* Header */}
      <motion.div
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="text-center mb-12 relative z-10"
      >
        <div className="arcade-font text-[10px] text-neon-yellow tracking-[0.3em] mb-2">LIVE BROADCAST</div>
        <h1 className="pixel-font text-xl mb-2">{torneio.toUpperCase()}</h1>
        <div className="arcade-font text-sm text-neon-cyan">{fase.toUpperCase()} • {superficie.toUpperCase()}</div>
      </motion.div>

      {/* Versus Grid */}
      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-8 w-full max-w-lg mb-12 relative z-10">
        {/* Player */}
        <motion.div
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-right space-y-3"
        >
          <div className="flex justify-end gap-2 items-center">
            <span className="arcade-font text-[8px] text-[#888]">RANK #{jogador.ranking}</span>
            <PixelFlag countryCode={jogador.nacionalidade} size="md" />
          </div>
          <div className="pixel-font text-sm leading-tight">{jogador.nome.toUpperCase()}</div>
          <div className="arcade-font text-2xl text-neon-green">{jogador.overall}</div>
          <div className="arcade-font text-[8px] text-neon-green/60">OVERALL</div>
        </motion.div>

        {/* VS */}
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', damping: 12, delay: 0.4 }}
          className="w-12 h-12 bg-white text-black flex items-center justify-center pixel-font text-lg shadow-[0_0_20px_white]"
        >
          VS
        </motion.div>

        {/* Opponent */}
        <motion.div
          initial={{ x: 100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-left space-y-3"
        >
          <div className="flex justify-start gap-2 items-center">
            <PixelFlag countryCode={adversario.nacionalidade || '??'} size="md" />
            <span className="arcade-font text-[8px] text-[#888]">RANK #{adversario.ranking || '???'}</span>
          </div>
          <div className="pixel-font text-sm leading-tight">{adversario.nome.toUpperCase()}</div>
          <div className="arcade-font text-2xl text-neon-pink">{adversario.overall || '??'}</div>
          <div className="arcade-font text-[8px] text-neon-pink/60">OVERALL</div>
        </motion.div>
      </div>

      {/* Tactical Teaser */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="flex gap-8 mb-12"
      >
        <div className="flex flex-col items-center gap-1">
          <Zap size={16} className="text-neon-yellow" />
          <span className="arcade-font text-[8px] text-[#888]">HIGH STAKES</span>
        </div>
        <div className="flex flex-col items-center gap-1">
          <Users size={16} className="text-neon-cyan" />
          <span className="arcade-font text-[8px] text-[#888]">CROWDED ARENA</span>
        </div>
      </motion.div>

      {/* Call to Action */}
      <motion.button
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 1 }}
        onClick={onContinue}
        className="px-8 py-4 border-2 border-white arcade-font text-xs hover:bg-white hover:text-black transition-all active:scale-95"
      >
        [ ENTER COURT ]
      </motion.button>
    </div>
  )
}
