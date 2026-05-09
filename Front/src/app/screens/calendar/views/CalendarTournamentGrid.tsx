import { Trophy } from 'lucide-react'
import { motion } from 'motion/react'
import { NeonButton, PixelFlag } from '../../../components'
import { normalizeSurface, surfaceColors, surfaceTexture, tierConfig, toTier } from '../model'
import type { CalendarTournamentGridProps } from '../types'

export function CalendarTournamentGrid({
  loading,
  semanaAtual,
  semanaSelecionada,
  torneiosSemana,
  convocacao,
  inscrevendo,
  erroInscricao,
  onSelectTournament,
  onConfirmCallup,
  onDeclineCallup,
}: CalendarTournamentGridProps) {
  return (
    <div className="grid grid-cols-3 gap-2">
      {loading && (
        <motion.div
          animate={{ opacity: [1, 0.3, 1] }}
          transition={{ duration: 1, repeat: Infinity }}
          className="col-span-3 py-12 text-center pixel-font text-sm text-neon-green"
        >
          CARREGANDO...
        </motion.div>
      )}

      {!loading && convocacao?.torneio && (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="col-span-3 border-2 border-neon-yellow bg-neon-yellow/10 p-4 shadow-[0_0_15px_rgba(255,230,0,0.2)]"
        >
          <div className="mb-3 flex items-start justify-between">
            <div className="flex items-center gap-2">
              <Trophy size={16} className="text-neon-yellow" />
              <span className="text-[10px] text-white" style={{ fontFamily: 'var(--font-arcade)' }}>
                CONVOCAÇÃO - COPA DAVIS
              </span>
            </div>
            <span className="text-[10px] font-bold text-neon-yellow">ESPECIAL</span>
          </div>

          <div className="mb-1 text-xs text-white" style={{ fontFamily: 'var(--font-arcade)' }}>
            {convocacao.torneio.nome.toUpperCase()}
          </div>
          <p className="mb-4 text-[9px] text-neon-cyan uppercase">{convocacao.mensagem}</p>

          <NeonButton
            variant="yellow"
            className="w-full"
            onClick={onConfirmCallup}
            disabled={!convocacao.convocado || inscrevendo}
          >
            {convocacao.convocado ? 'REPRESENTAR SUA NAÇÃO' : 'NÃO CONVOCADO'}
          </NeonButton>

          {convocacao.convocado && (
            <button
              onClick={onDeclineCallup}
              disabled={inscrevendo}
              className="mt-2 w-full text-center text-[8px] text-neon-yellow/60 hover:text-neon-yellow uppercase underline decoration-[#ffe600]/30"
              style={{ fontFamily: 'var(--font-arcade)' }}
            >
              Recusar Convocação
            </button>
          )}
        </motion.div>
      )}

      {!loading && torneiosSemana.length === 0 && !convocacao?.torneio && (
        <div className="col-span-3 border-2 border-neon-green bg-[#1a1a2e] p-6 text-center" style={{ boxShadow: 'var(--glow-green)' }}>
          <div className="mb-3 text-4xl">💤</div>
          <div className="text-sm text-[#888]">SEMANA DE DESCANSO</div>
          <div className="mt-2 text-xs text-[#666]">Nenhum torneio esta semana</div>
        </div>
      )}

      {!loading &&
        torneiosSemana.map((tournament, index) => {
          const tier = toTier(tournament.tipo)
          const config = tierConfig(tier)
          const surface = normalizeSurface(tournament.superficie)
          const surfaceColor = surfaceColors[surface]
          const isPastOrFuture = semanaSelecionada !== semanaAtual

          return (
            <motion.div
              key={tournament.nome}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.08 }}
              onClick={() => !isPastOrFuture && onSelectTournament(tournament)}
              className={`relative flex flex-col h-28 overflow-hidden border-2 transition-transform ${
                isPastOrFuture ? 'cursor-default opacity-60' : 'cursor-pointer active:scale-95'
              }`}
              style={{ borderColor: config.color, boxShadow: isPastOrFuture ? 'none' : config.glow }}
            >
              <div
                className="absolute inset-0 opacity-70"
                style={{
                  backgroundColor: surfaceColor,
                  backgroundImage: surfaceTexture(surface),
                  backgroundSize: '12px 12px',
                  imageRendering: 'pixelated',
                }}
              />

              <div className="absolute inset-0 bg-gradient-to-b from-black/65 via-black/25 to-black/80" />

              <div className="relative flex-1 p-2 flex flex-col justify-between">
                <div className="flex items-start justify-between gap-1">
                  <div
                    className="text-[7px] font-bold tracking-widest leading-none"
                    style={{
                      color: config.color,
                      fontFamily: 'var(--font-arcade)',
                      textShadow: `0 0 8px ${config.color}`,
                    }}
                  >
                    {config.badge} {config.label}
                  </div>
                  {tournament.codigo_pais && (
                    <PixelFlag countryCode={tournament.codigo_pais} size="xl" />
                  )}
                </div>

                <div>
                  <div
                    className="text-[10px] leading-tight text-white font-bold line-clamp-2"
                    style={{ fontFamily: 'var(--font-arcade)', textShadow: '1px 1px 3px black' }}
                  >
                    {tournament.nome.toUpperCase()}
                  </div>
                  <div className="text-[7px] text-neon-cyan uppercase truncate mt-0.5">
                    {tournament.local}
                  </div>
                </div>
              </div>

              <div className="relative h-1.5" style={{ backgroundColor: config.color }} />
            </motion.div>
          )
        })}

      {erroInscricao && <div className="col-span-3 text-center text-xs text-neon-pink">{erroInscricao}</div>}
    </div>
  )
}
