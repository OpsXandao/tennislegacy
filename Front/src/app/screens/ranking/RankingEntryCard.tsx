import { motion } from 'motion/react'
import { Trophy, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { PixelFlag } from '../../components'
import type { RankingEntry } from '../../../types'
import { getOverallTierLabel } from '../../utils/playerRatings'

interface RankingEntryCardProps {
  player: RankingEntry
  index: number
  isUser: boolean
  tour: string
  modalidade: string
  totalJogadores: number
  onNavigate: (nome: string) => void
}

export function RankingEntryCard({
  player,
  index,
  isUser,
  tour,
  modalidade,
  totalJogadores,
  onNavigate,
}: RankingEntryCardProps) {
  const change = 0
  const tier = getOverallTierLabel(0, player.posicao, totalJogadores)
  
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: Math.min(index * 0.03, 0.6) }}
      onClick={() => {
        if (tour === 'davis') return
        onNavigate(player.nome)
      }}
      className={`relative overflow-hidden border-2 p-3 ${
        isUser ? 'border-neon-green bg-neon-green/20' : 'border-neon-cyan/30 bg-[#1a1a2e]'
      } ${tour !== 'davis' ? 'cursor-pointer transition-transform hover:-translate-y-0.5' : ''}`}
      style={isUser ? { boxShadow: 'var(--glow-green)' } : undefined}
    >
      {isUser && <div className="absolute bottom-0 left-0 top-0 w-1 animate-pulse bg-neon-green" />}
      <div className="flex items-center justify-between gap-3">
        <div className={`w-10 text-center ${player.posicao <= 3 ? 'text-neon-yellow' : isUser ? 'text-neon-green' : 'text-neon-cyan'}`}>
          <span className="text-xl font-bold" style={{ fontFamily: 'var(--font-arcade)' }}>{player.posicao}</span>
          {player.posicao === 1 && <Trophy size={12} className="ml-1 inline animate-pulse text-neon-yellow" />}
        </div>
        <div className="flex flex-1 items-center gap-2 min-w-0">
          <PixelFlag countryCode={player.nacionalidade} size="md" />
          <div className="min-w-0">
            <div className={`truncate text-[11px] ${isUser ? 'text-neon-green' : 'text-neon-cyan'}`} style={{ fontFamily: 'var(--font-arcade)' }}>
              {player.nome}
            </div>
            <div className={`text-[7px] ${isUser ? 'text-neon-yellow' : 'text-[#6e8091]'}`}>
              {tier}
            </div>
            {tour !== 'davis' && !isUser && (
              <div className="text-[7px] text-[#6e8091]">Clique para abrir o perfil</div>
            )}
            {isUser && <div className="text-[7px] text-neon-yellow">★ VOCÊ ★</div>}
          </div>
        </div>
        <div className="w-12 text-center">
          <div className="text-[11px] text-[#d9ebf5] arcade-font">{player.idade || '—'}</div>
          <div className="text-ui-tag text-[#66798b]">IDADE</div>
        </div>
        {(player as any).overall > 0 && (
          <div className="w-16 flex flex-col gap-1">
            <div className="flex items-center justify-between">
              <span className="arcade-font text-ui-tag text-[#5a7488]">OVR</span>
              <span
                className="arcade-font text-ui-label font-bold"
                style={{
                  color: (player as any).overall >= 85 ? 'var(--neon-yellow)'
                       : (player as any).overall >= 75 ? 'var(--neon-cyan)'
                       : (player as any).overall >= 65 ? 'var(--neon-green)'
                       : '#7a8fa0'
                }}
              >
                {(player as any).overall}
              </span>
            </div>
            <div className="h-1 bg-[#0a1520] rounded-full overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{
                  width: `${Math.min(100, ((player as any).overall / 99) * 100)}%`,
                  background: (player as any).overall >= 85 ? 'var(--neon-yellow)'
                            : (player as any).overall >= 75 ? 'var(--neon-cyan)'
                            : 'var(--neon-green)',
                }}
              />
            </div>
          </div>
        )}
        <div className="w-20 text-right">
          <div className={`text-sm font-bold ${isUser ? 'text-neon-green' : 'text-white'}`}>
            {player.pontos.toLocaleString('pt-BR')}
          </div>
          <div className="text-ui-tag text-[#888]">PTS</div>
        </div>
        <div className="flex w-10 justify-center">
          {change > 0 ? (
            <div className="flex items-center gap-1 text-neon-green">
              <TrendingUp size={12} />
              <span className="text-[9px]">+{change}</span>
            </div>
          ) : change < 0 ? (
            <div className="flex items-center gap-1 text-neon-pink">
              <TrendingDown size={12} />
              <span className="text-[9px]">{change}</span>
            </div>
          ) : (
            <Minus size={12} className="text-[#888]" />
          )}
        </div>
      </div>
      {player.posicao === 4 && <div className="absolute bottom-0 left-0 right-0 h-px bg-neon-yellow opacity-50" />}
      {player.posicao === 8 && <div className="absolute bottom-0 left-0 right-0 h-px bg-neon-cyan opacity-30" />}
    </motion.div>
  )
}
