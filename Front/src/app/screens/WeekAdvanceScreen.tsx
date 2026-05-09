import { useEffect, useMemo, useState } from 'react'
import { motion } from 'motion/react'
import { useLocation, useNavigate } from 'react-router'
import { CalendarDays, ChevronRight, Clock3, MapPinned, Trophy } from 'lucide-react'
import { NeonCard, NeonButton, PixelFlag } from '../components'
import { useGameStore } from '../../store/gameStore'
import type { CampeaoSemana, TorneioCalendario, WeekAdvanceStep } from '../../types'

interface WeekAdvanceLocationState {
  fromSemana: number
  fromAno: number
  toSemana: number
  toAno: number
  campeoes: CampeaoSemana[]
  eventos?: string[]
  processamento?: WeekAdvanceStep[]
  torneiosDisponiveis?: TorneioCalendario[]
  motivo?: 'withdraw' | 'tournament_end' | 'rest'
}

function titleFromReason(reason?: WeekAdvanceLocationState['motivo']) {
  if (reason === 'withdraw') return 'SEMANA AVANÇADA'
  if (reason === 'rest') return 'CONTINUE'
  return 'FIM DE SEMANA'
}

function subtitleFromReason(reason?: WeekAdvanceLocationState['motivo']) {
  if (reason === 'withdraw') return 'TORNEIO ENCERRADO APÓS DESISTÊNCIA'
  if (reason === 'rest') return 'A SEMANA ESTÁ SENDO PROCESSADA'
  return 'RESULTADOS CONSOLIDADOS DO CIRCUITO'
}

function badgeColor(tour: string) {
  return tour.toLowerCase().includes('wta') ? '#ff5f8f' : 'var(--neon-green)'
}

function toneColor(tom: WeekAdvanceStep['tom']) {
  if (tom === 'positive') return 'var(--neon-green)'
  if (tom === 'warning') return 'var(--neon-yellow)'
  if (tom === 'info') return 'var(--neon-cyan)'
  return '#c7d4d0'
}

function defaultSteps(state: WeekAdvanceLocationState | null): WeekAdvanceStep[] {
  if (!state) return []
  return [
    {
      id: 'advance_calendar',
      titulo: 'Calendário',
      resumo: `Semana ${state.fromSemana} encerrada. Preparando a semana ${state.toSemana}.`,
      tom: 'info',
      detalhes: state.eventos?.slice(0, 3) ?? [],
    },
    {
      id: 'simulate_tournaments',
      titulo: 'Circuito',
      resumo: 'Consolidando o que aconteceu nos torneios do mundo.',
      tom: 'neutral',
      detalhes: state.campeoes.slice(0, 3).map((campeao) => `${campeao.tour}: ${campeao.torneio}`),
    },
    {
      id: 'init_next_week',
      titulo: 'Nova agenda',
      resumo: 'Montando seus próximos compromissos de calendário.',
      tom: 'positive',
      detalhes: state.torneiosDisponiveis?.slice(0, 3).map((torneio) => `${torneio.nome} • ${torneio.horario_local ?? '13:00'}`) ?? [],
    },
  ]
}

export function WeekAdvanceScreen() {
  const navigate = useNavigate()
  const location = useLocation()
  const { setSemana, setTorneio, setPartidaId, fetchJogador } = useGameStore()
  const state = location.state as WeekAdvanceLocationState | null

  const [currentStep, setCurrentStep] = useState(-1)
  const [allowContinue, setAllowContinue] = useState(false)

  const campeoes = useMemo(() => state?.campeoes ?? [], [state])
  const etapas = useMemo(
    () => (state?.processamento && state.processamento.length > 0 ? state.processamento : defaultSteps(state)),
    [state]
  )
  const torneiosDisponiveis = useMemo(() => state?.torneiosDisponiveis ?? [], [state])
  const calendarStepIndex = useMemo(() => {
    const found = etapas.findIndex((etapa) => etapa.id === 'advance_calendar')
    return found >= 0 ? found : 0
  }, [etapas])
  const showIncrement = currentStep >= calendarStepIndex

  useEffect(() => {
    if (!state) {
      navigate('/hub', { replace: true })
      return
    }

    setTorneio(null)
    setPartidaId(null)

    const timers: number[] = []
    etapas.forEach((_, index) => {
      timers.push(
        window.setTimeout(() => {
          setCurrentStep(index)
          if (index === calendarStepIndex) {
            setSemana(state.toSemana, state.toAno)
          }
        }, 700 + index * 800)
      )
    })

    timers.push(
      window.setTimeout(() => {
        setAllowContinue(true)
        fetchJogador().catch(() => {})
      }, 1200 + etapas.length * 800)
    )

    return () => {
      timers.forEach((timer) => window.clearTimeout(timer))
    }
  }, [calendarStepIndex, etapas, fetchJogador, navigate, setPartidaId, setSemana, setTorneio, state])

  if (!state) return null

  return (
    <div
      className="min-h-screen px-4 py-6 text-white"
      style={{
        background:
          'radial-gradient(circle at top, rgba(0,255,136,0.18), transparent 28%), linear-gradient(180deg, #061312 0%, #030909 100%)',
      }}
    >
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-5xl flex-col justify-center gap-6">
        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="text-center">
          <div
            className="mb-2 text-[11px]"
            style={{ fontFamily: 'var(--font-pixel)', color: 'var(--neon-green)', textShadow: '0 0 10px rgba(0,255,136,0.55)' }}
          >
            {titleFromReason(state.motivo)}
          </div>
          <div className="text-[20px] sm:text-[26px]" style={{ fontFamily: 'var(--font-arcade)' }}>
            {subtitleFromReason(state.motivo)}
          </div>
        </motion.div>

        <div className="grid gap-5 xl:grid-cols-[1.1fr_1fr]">
          <NeonCard variant="green" hover={false} className="overflow-hidden">
            <div className="mb-4 flex items-center gap-3">
              <CalendarDays size={18} className="text-neon-green" />
              <div>
                <div className="pixel-font text-sm text-neon-green">PROGRESSÃO DA SEMANA</div>
                <div className="arcade-font text-xs text-[#9ae6c3]">Processamento visível do calendário</div>
              </div>
            </div>

            <div className="flex items-center justify-center gap-4 rounded border border-[#00ff8844] bg-[#031311] px-4 py-6">
              <motion.div
                animate={!showIncrement ? { scale: [1, 1.06, 1], opacity: [0.85, 1, 0.85] } : { scale: 0.94, opacity: 0.45 }}
                transition={{ duration: 0.9, repeat: !showIncrement ? Infinity : 0 }}
                className="text-center"
              >
                <div className="pixel-font text-[10px] text-[#88bca3]">SEMANA</div>
                <div className="pixel-font text-3xl text-neon-yellow">{state.fromSemana}</div>
                <div className="arcade-font text-xs text-[#789186]">{state.fromAno}</div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0.2, x: -8 }}
                animate={showIncrement ? { opacity: 1, x: 0 } : { opacity: 0.2, x: -8 }}
                className="text-neon-cyan"
              >
                <ChevronRight size={34} />
              </motion.div>

              <div className="text-center">
                <div className="pixel-font text-[10px] text-[#88bca3]">PRÓXIMA</div>
                <div
                  className="pixel-font text-3xl"
                  style={{
                    color: showIncrement ? 'var(--neon-green)' : '#34544c',
                    textShadow: showIncrement ? '0 0 12px rgba(0,255,136,0.45)' : 'none',
                  }}
                >
                  {state.toSemana}
                </div>
                <div className="arcade-font text-xs text-[#789186]">{state.toAno}</div>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              {etapas.map((etapa, index) => {
                const ativo = index === currentStep
                const concluido = index < currentStep || (allowContinue && index <= currentStep)
                const color = toneColor(etapa.tom)
                return (
                  <div
                    key={etapa.id}
                    className="border px-3 py-3"
                    style={{
                      borderColor: ativo || concluido ? `${color}88` : '#28402f',
                      background: ativo ? '#071d18' : '#091311',
                      boxShadow: ativo ? `0 0 18px ${color}22` : 'none',
                    }}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="pixel-font text-[10px]" style={{ color }}>{etapa.titulo.toUpperCase()}</div>
                        <div className="arcade-font text-[10px] text-[#c7d4d0] mt-1">{etapa.resumo}</div>
                      </div>
                      <div className="pixel-font text-[9px]" style={{ color }}>
                        {concluido ? 'OK' : ativo ? '...' : 'PEND'}
                      </div>
                    </div>
                    {etapa.detalhes.length > 0 && (ativo || concluido) ? (
                      <div className="mt-2 space-y-1">
                        {etapa.detalhes.slice(0, 3).map((detalhe) => (
                          <div key={detalhe} className="arcade-font text-[10px] text-[#9db2ab]">
                            {detalhe}
                          </div>
                        ))}
                      </div>
                    ) : null}
                  </div>
                )
              })}
            </div>
          </NeonCard>

          <div className="space-y-5">
            <NeonCard variant="yellow" hover={false}>
              <div className="mb-4 flex items-center gap-3">
                <Clock3 size={18} className="text-neon-yellow" />
                <div>
                  <div className="pixel-font text-sm text-neon-yellow">AGENDA DA NOVA SEMANA</div>
                  <div className="arcade-font text-xs text-[#f8eb9a]">Horários e quadras do circuito</div>
                </div>
              </div>

              <div className="space-y-3">
                {torneiosDisponiveis.length > 0 ? (
                  torneiosDisponiveis.slice(0, 4).map((torneio) => (
                    <div
                      key={`${torneio.nome}-${torneio.semana}`}
                      className="border p-3"
                      style={{ borderColor: '#00e5ff44', background: '#071015' }}
                    >
                      <div className="mb-2 flex items-start justify-between gap-3">
                        <div>
                          <div className="arcade-font text-sm text-white">{torneio.nome}</div>
                          <div className="arcade-font text-[10px] text-[#8fc0cf] mt-1">
                            {torneio.janela_semana ?? 'SEG-DOM'} • {torneio.tipo}
                          </div>
                        </div>
                        {torneio.codigo_pais ? <PixelFlag countryCode={torneio.codigo_pais} size="lg" /> : null}
                      </div>
                      <div className="grid gap-2 sm:grid-cols-2">
                        <div className="border border-[#1f3d49] bg-black/20 px-2 py-2">
                          <div className="pixel-font text-[8px] text-neon-cyan">HORÁRIO LOCAL</div>
                          <div className="arcade-font text-[10px] text-white mt-1">
                            {torneio.horario_local ?? '13:00'} • {torneio.sessao_label ?? 'Sessão principal'}
                          </div>
                        </div>
                        <div className="border border-[#3f3520] bg-black/20 px-2 py-2">
                          <div className="pixel-font text-[8px] text-neon-yellow">QUADRA PRINCIPAL</div>
                          <div className="arcade-font text-[10px] text-white mt-1">
                            {torneio.quadra_nome ?? 'Quadra Central'}
                          </div>
                        </div>
                      </div>
                      <div className="mt-2 flex items-center gap-2 arcade-font text-[10px] text-[#c7d4d0]">
                        <MapPinned size={12} className="text-[#ff9a5f]" />
                        <span>{torneio.local} • {torneio.superficie}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="border border-dashed border-[#ffe60044] px-3 py-6 text-center">
                    <div className="arcade-font text-xs text-[#d7d7b0]">Sem agenda nova consolidada nesta virada.</div>
                  </div>
                )}
              </div>
            </NeonCard>

            <NeonCard variant="yellow" hover={false}>
              <div className="mb-4 flex items-center gap-3">
                <Trophy size={18} className="text-neon-yellow" />
                <div>
                  <div className="pixel-font text-sm text-neon-yellow">CAMPEÕES</div>
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
                      <div className="pixel-font text-[9px]" style={{ color: badgeColor(campeao.tour) }}>
                        {campeao.tour.toUpperCase()}
                      </div>
                    </div>
                    <div className="arcade-font text-xs text-[#c7d4d0]">Simples: {campeao.simples}</div>
                    {campeao.duplas ? <div className="arcade-font mt-1 text-xs text-[#8db8ff]">Duplas: {campeao.duplas}</div> : null}
                  </motion.div>
                )) : (
                  <div className="border border-dashed border-[#ffe60044] px-3 py-6 text-center">
                    <div className="arcade-font text-xs text-[#d7d7b0]">Sem campeões consolidados nesta virada.</div>
                  </div>
                )}
              </div>
            </NeonCard>
          </div>
        </div>

        <div className="flex justify-center">
          <NeonButton
            variant="cyan"
            onClick={() => navigate('/hub', { replace: true })}
            disabled={!allowContinue}
          >
            {allowContinue ? 'CONTINUAR PARA O HUB' : 'PROCESSANDO A SEMANA...'}
          </NeonButton>
        </div>
      </div>
    </div>
  )
}
