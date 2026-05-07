import { useEffect, useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { useLocation, useNavigate } from 'react-router'
import { CalendarDays, Trophy, ChevronRight } from 'lucide-react'
import { NeonCard, NeonButton } from '../components'
import { useGameStore } from '../../store/gameStore'
import type { CampeaoSemana } from '../../types'

interface WeekAdvanceLocationState {
  fromSemana: number
  fromAno: number
  toSemana: number
  toAno: number
  campeoes: CampeaoSemana[]
  eventos?: string[]
  motivo?: 'withdraw' | 'tournament_end'
}

function titleFromReason(reason?: WeekAdvanceLocationState['motivo']) {
  if (reason === 'withdraw') return 'SEMANA AVANÇADA'
  return 'FIM DE SEMANA'
}

function subtitleFromReason(reason?: WeekAdvanceLocationState['motivo']) {
  if (reason === 'withdraw') return 'TORNEIO ENCERRADO APÓS DESISTÊNCIA'
  return 'RESULTADOS CONSOLIDADOS DO CIRCUITO'
}

function badgeColor(tour: string) {
  return tour.toLowerCase().includes('wta') ? '#ff5f8f' : '#00ff88'
}

export function WeekAdvanceScreen() {
  const navigate = useNavigate()
  const location = useLocation()
  const { setSemana, setTorneio, setPartidaId, fetchJogador } = useGameStore()
  const state = location.state as WeekAdvanceLocationState | null

  const [showIncrement, setShowIncrement] = useState(false)
  const [allowSkip, setAllowSkip] = useState(false)

  const campeoes = useMemo(() => state?.campeoes ?? [], [state])

  useEffect(() => {
    if (!state) {
      navigate('/hub', { replace: true })
      return
    }

    setTorneio(null)
    setPartidaId(null)

    const showTimer = window.setTimeout(() => {
      setShowIncrement(true)
      setSemana(state.toSemana, state.toAno)
    }, 1700)

    const skipTimer = window.setTimeout(() => {
      setAllowSkip(true)
    }, 2200)

    const endTimer = window.setTimeout(() => {
      fetchJogador().catch(() => {})
      navigate('/hub', { replace: true })
    }, 3600)

    return () => {
      window.clearTimeout(showTimer)
      window.clearTimeout(skipTimer)
      window.clearTimeout(endTimer)
    }
  }, [fetchJogador, navigate, setPartidaId, setSemana, setTorneio, state])

  if (!state) return null

  return (
    <div
      className="min-h-screen px-4 py-6 text-white"
      style={{
        background:
          'radial-gradient(circle at top, rgba(0,255,136,0.18), transparent 28%), linear-gradient(180deg, #061312 0%, #030909 100%)',
      }}
    >
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-4xl flex-col justify-center gap-6">
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <div
            className="mb-2 text-[11px]"
            style={{ fontFamily: 'var(--font-pixel)', color: '#00ff88', textShadow: '0 0 10px rgba(0,255,136,0.55)' }}
          >
            {titleFromReason(state.motivo)}
          </div>
          <div
            className="text-[20px] sm:text-[26px]"
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            {subtitleFromReason(state.motivo)}
          </div>
        </motion.div>

        <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
          <NeonCard variant="green" hover={false} className="overflow-hidden">
            <div className="mb-4 flex items-center gap-3">
              <CalendarDays size={18} className="text-[#00ff88]" />
              <div>
                <div className="pixel-font text-sm text-[#00ff88]">CALENDÁRIO</div>
                <div className="arcade-font text-xs text-[#9ae6c3]">Fechamento da semana atual</div>
              </div>
            </div>

            <div className="flex items-center justify-center gap-4 rounded border border-[#00ff8844] bg-[#031311] px-4 py-6">
              <motion.div
                animate={!showIncrement ? { scale: [1, 1.06, 1], opacity: [0.85, 1, 0.85] } : { scale: 0.94, opacity: 0.45 }}
                transition={{ duration: 0.9, repeat: !showIncrement ? Infinity : 0 }}
                className="text-center"
              >
                <div className="pixel-font text-[10px] text-[#88bca3]">SEMANA</div>
                <div className="pixel-font text-3xl text-[#ffe600]">{state.fromSemana}</div>
                <div className="arcade-font text-xs text-[#789186]">{state.fromAno}</div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0.2, x: -8 }}
                animate={showIncrement ? { opacity: 1, x: 0 } : { opacity: 0.2, x: -8 }}
                className="text-[#00e5ff]"
              >
                <ChevronRight size={34} />
              </motion.div>

              <AnimatePresence mode="wait">
                <motion.div
                  key={showIncrement ? 'next' : 'locked'}
                  initial={{ opacity: 0, scale: 0.9, y: 8 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9, y: -8 }}
                  className="text-center"
                >
                  <div className="pixel-font text-[10px] text-[#88bca3]">PRÓXIMA</div>
                  <div
                    className="pixel-font text-3xl"
                    style={{
                      color: showIncrement ? '#00ff88' : '#34544c',
                      textShadow: showIncrement ? '0 0 12px rgba(0,255,136,0.45)' : 'none',
                    }}
                  >
                    {state.toSemana}
                  </div>
                  <div className="arcade-font text-xs text-[#789186]">{state.toAno}</div>
                </motion.div>
              </AnimatePresence>
            </div>

            {state.eventos && state.eventos.length > 0 ? (
              <div className="mt-4 space-y-2">
                <div className="pixel-font text-[10px] text-[#00e5ff]">EVENTOS DA VIRADA</div>
                {state.eventos.slice(0, 4).map((evento, index) => (
                  <motion.div
                    key={`${evento}-${index}`}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.15 * index }}
                    className="border border-[#00e5ff33] bg-[#041318] px-3 py-2 text-[11px] text-[#b4f6ff]"
                    style={{ fontFamily: 'var(--font-arcade)' }}
                  >
                    {evento}
                  </motion.div>
                ))}
              </div>
            ) : null}
          </NeonCard>

          <NeonCard variant="yellow" hover={false}>
            <div className="mb-4 flex items-center gap-3">
              <Trophy size={18} className="text-[#ffe600]" />
              <div>
                <div className="pixel-font text-sm text-[#ffe600]">CAMPEÕES</div>
                <div className="arcade-font text-xs text-[#f8eb9a]">Quem venceu no circuito</div>
              </div>
            </div>

            <div className="space-y-3">
              {campeoes.length > 0 ? campeoes.map((campeao, index) => (
                <motion.div
                  key={`${campeao.torneio}-${campeao.tour}`}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                  className="border p-3"
                  style={{ borderColor: `${badgeColor(campeao.tour)}66`, background: '#0a0f0e' }}
                >
                  <div className="mb-1 flex items-center justify-between gap-3">
                    <div className="arcade-font text-sm text-white">{campeao.torneio}</div>
                    <div
                      className="pixel-font text-[9px]"
                      style={{ color: badgeColor(campeao.tour) }}
                    >
                      {campeao.tour.toUpperCase()}
                    </div>
                  </div>
                  <div className="arcade-font text-xs text-[#c7d4d0]">Simples: {campeao.simples}</div>
                  {campeao.duplas ? (
                    <div className="arcade-font mt-1 text-xs text-[#8db8ff]">Duplas: {campeao.duplas}</div>
                  ) : null}
                </motion.div>
              )) : (
                <div className="border border-dashed border-[#ffe60044] px-3 py-6 text-center">
                  <div className="arcade-font text-xs text-[#d7d7b0]">Sem campeões consolidados nesta virada.</div>
                </div>
              )}
            </div>
          </NeonCard>
        </div>

        <div className="flex justify-center">
          <NeonButton
            variant="cyan"
            onClick={() => navigate('/hub', { replace: true })}
            disabled={!allowSkip}
          >
            {allowSkip ? 'IR PARA O HUB' : 'PROCESSANDO...'}
          </NeonButton>
        </div>
      </div>
    </div>
  )
}
